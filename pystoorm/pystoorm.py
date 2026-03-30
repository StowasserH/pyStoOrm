#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""pyStoOrm - ORM Code Generator
Select name FROM ORM where rating='best'
"""
__author__ = "Harald Stowasser"

import sys
import logging
from clint.textui import puts, colored
from clint import arguments
from pystoorm.config.loader import ConfigLoader
from pystoorm.analyzer.controller import Controller
from pystoorm.generator.coordinator import Coordinator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def dumpclean(obj, max_depth=3, depth=0):
    """Pretty-print object for debugging."""
    if depth > max_depth:
        return

    if isinstance(obj, dict):
        for k, v in obj.items():
            if hasattr(v, '__iter__') and not isinstance(v, str):
                print(f"{k}:")
                dumpclean(v, max_depth, depth + 1)
            else:
                print(f"  {k}: {v}")
    elif isinstance(obj, list):
        for v in obj:
            if hasattr(v, '__iter__') and not isinstance(v, str):
                dumpclean(v, max_depth, depth + 1)
            else:
                print(f"  {v}")
    else:
        print(obj)


def main():
    """Main entry point for pyStoOrm."""
    try:
        # Parse command line arguments
        args = arguments.Args()
        project_path = args.last

        if not project_path or len(project_path) < 1:
            project_path = "pystoorm/config/projects/example/project.yml"

        logger.info(f"Loading project configuration from: {project_path}")

        # Load configuration using ConfigLoader
        loader = ConfigLoader()
        try:
            loader.load_defaults().load_project(project_path)
            config = loader.get_config()
        except (IOError, ValueError) as e:
            puts(colored.red(f'Error loading configuration: {e}'))
            sys.exit(1)

        # Set logging level from config
        log_level = config.get('logging', {}).get('level', 'INFO')
        logging.getLogger().setLevel(getattr(logging, log_level))
        logger.info(f"Logging level set to {log_level}")

        # Run database analyzer
        logger.info("Starting database schema analysis...")
        analyzer = Controller(config)
        analyzer.walk()
        logger.info("Database analysis complete")

        # Print schema summary (debug)
        if config['connections']:
            schema = config['connections'][0].get('parsedSchema')
            if schema:
                puts(colored.cyan(f"Found {len(schema.table_names)} tables"))
                dumpclean(schema.table_names)

        # Run code generator
        logger.info("Starting code generation...")
        generator = Coordinator(config)
        generator.generate()
        logger.info("Code generation complete")

        puts(colored.green('✓ pyStoOrm generation successful'))
        sys.exit(0)

    except KeyboardInterrupt:
        puts(colored.yellow('\nInterrupted by user'))
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        puts(colored.red(f'Error: {e}'))
        sys.exit(1)


if __name__ == "__main__":
    main()
