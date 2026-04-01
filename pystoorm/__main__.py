#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pyStoOrm - ORM Code Generator

Simple CLI entry point to generate ORM code from database schema.

Usage:
    python pyStoOrm.py <config_file>
    python pyStoOrm.py project.yml
    python pyStoOrm.py /path/to/project.yml

The config file (project.yml) should specify:
    - Database connections
    - Output templates
    - Template rendering modes
"""
import sys
import os
import logging
from pystoorm.config.loader import ConfigLoader
from pystoorm.analyzer.controller import Controller
from pystoorm.generator.coordinator import Coordinator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_header():
    """Print program header."""
    print("\n" + "="*70)
    print("  pyStoOrm - ORM Code Generator")
    print("="*70 + "\n")


def print_error(message):
    """Print error message."""
    print(f"✗ Error: {message}")


def print_success(message):
    """Print success message."""
    print(f"✓ {message}")


def _resolve_single_path(path, config_dir, variables):
    """Resolve a single path with variables and make it absolute."""
    if not isinstance(path, str):
        return path

    # Replace ${var} with actual values
    for var_name, var_value in variables.items():
        path = path.replace(f'${{{var_name}}}', var_value)

    # Make relative paths absolute (relative to config dir)
    if path and not os.path.isabs(path):
        path = os.path.normpath(os.path.join(config_dir, path))
    elif path:
        path = os.path.normpath(path)

    return path


def _resolve_config_paths(config, config_dir):
    """Resolve ${variable} placeholders in config and make all paths absolute."""
    variables = {'project_root': config_dir}

    def resolve_path(path):
        return _resolve_single_path(path, config_dir, variables)

    if 'output_dir' in config:
        config['output_dir'] = resolve_path(config['output_dir'])

    if 'output' in config:
        for template in config['output']:
            if 'from' in template:
                template['from'] = resolve_path(template['from'])
            if 'to' in template:
                template['to'] = resolve_path(template['to'])

    if 'connections' in config:
        for conn in config['connections']:
            # Only resolve 'database' as a path for SQLite (file-based databases)
            # For PostgreSQL/MySQL, 'database' is a database name, not a file path
            if 'database' in conn and 'sqliteconnector' in conn.get('connector', '').lower():
                conn['database'] = resolve_path(conn['database'])

    return config


def _validate_and_resolve_config_file(config_file):
    """Validate and resolve config file path."""
    if not os.path.isabs(config_file):
        if not os.path.exists(config_file):
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            alt_path = os.path.join(project_root, config_file)
            if os.path.exists(alt_path):
                config_file = alt_path

    if not os.path.exists(config_file):
        print_error(f"Configuration file not found: {config_file}")
        sys.exit(1)

    return os.path.abspath(config_file)


def _load_and_process_config(config_file):
    """Load configuration and resolve paths."""
    loader = ConfigLoader()
    loader.load_defaults().load_project(config_file)
    config = loader.get_config()
    config_dir = os.path.dirname(os.path.abspath(config_file))
    config = _resolve_config_paths(config, config_dir)
    return config


def _print_schema_summary(config):
    """Print database schema summary."""
    if not config['connections']:
        return
    schema = config['connections'][0].get('parsedSchema')
    if schema:
        print(f"\n  Tables found: {len(schema.table_names)}")
        for table_name in schema.table_names:
            table = schema.tables[table_name]
            col_count = len(table.columns)
            print(f"    - {table_name} ({col_count} columns)")


def main():
    """Main entry point."""
    print_header()

    if len(sys.argv) < 2:
        print_error("Missing configuration file argument")
        print("\nUsage:")
        print("  python pyStoOrm.py <config_file>")
        print("\nExample:")
        print("  python pyStoOrm.py project.yml")
        print("  python pyStoOrm.py tests/sampleproject/project.yml")
        sys.exit(1)

    config_file = _validate_and_resolve_config_file(sys.argv[1])
    print(f"Configuration: {config_file}\n")

    try:
        print("[1/3] Loading configuration...")
        config = _load_and_process_config(config_file)
        log_level = config.get('logging', {}).get('level', 'INFO')
        logging.getLogger().setLevel(getattr(logging, log_level))
        print_success("Configuration loaded")

        print("\n[2/3] Analyzing database schema...")
        analyzer = Controller(config)
        analyzer.walk()
        print_success("Schema analysis complete")
        _print_schema_summary(config)

        print("\n[3/3] Generating code from templates...")
        generator = Coordinator(config)
        generator.generate()
        print_success("Code generation complete")

        print("\n" + "="*70)
        print("✓ pyStoOrm generation successful!")
        print("="*70 + "\n")
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        sys.exit(130)

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print_error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
