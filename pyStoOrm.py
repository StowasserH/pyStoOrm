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
from pathlib import Path

# Add pyStoOrm to path
CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))

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


def main():
    """Main entry point."""
    print_header()

    # Parse arguments
    if len(sys.argv) < 2:
        print_error("Missing configuration file argument")
        print("\nUsage:")
        print("  python pyStoOrm.py <config_file>")
        print("\nExample:")
        print("  python pyStoOrm.py project.yml")
        print("  python pyStoOrm.py tests/sampleproject/project.yml")
        sys.exit(1)

    config_file = sys.argv[1]

    # Resolve config file path
    if not os.path.isabs(config_file):
        # Try relative to current directory first
        if not os.path.exists(config_file):
            # Try relative to script directory
            script_dir = Path(__file__).parent
            alt_path = script_dir / config_file
            if alt_path.exists():
                config_file = str(alt_path)

    # Validate config file exists
    if not os.path.exists(config_file):
        print_error(f"Configuration file not found: {config_file}")
        sys.exit(1)

    config_file = os.path.abspath(config_file)
    print(f"Configuration: {config_file}\n")

    try:
        # ==========================================
        # Load Configuration
        # ==========================================
        print("[1/3] Loading configuration...")

        loader = ConfigLoader()
        loader.load_defaults().load_project(config_file)
        config = loader.get_config()

        # Set logging level from config
        log_level = config.get('logging', {}).get('level', 'INFO')
        logging.getLogger().setLevel(getattr(logging, log_level))

        print_success("Configuration loaded")

        # ==========================================
        # Analyze Database Schema
        # ==========================================
        print("\n[2/3] Analyzing database schema...")

        analyzer = Controller(config)
        analyzer.walk()

        print_success("Schema analysis complete")

        # Print schema summary
        if config['connections']:
            schema = config['connections'][0].get('parsedSchema')
            if schema:
                print(f"\n  Tables found: {len(schema.table_names)}")
                for table_name in schema.table_names:
                    table = schema.tables[table_name]
                    col_count = len(table.columns)
                    print(f"    - {table_name} ({col_count} columns)")

        # ==========================================
        # Generate Code
        # ==========================================
        print("\n[3/3] Generating code from templates...")

        generator = Coordinator(config)
        generator.generate()

        print_success("Code generation complete")

        # ==========================================
        # Summary
        # ==========================================
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
