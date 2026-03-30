#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Code Generator - Renders templates with database schema

Renders Mako templates in two modes:
- schema mode: renders once per database connection
- table mode: renders once per table per database connection

Supports output file path substitution and template filtering.
"""
__author__ = "Harald Stowasser"

import logging
from mako.template import Template
from mako.runtime import Context
from clint.textui import puts, colored
from io import StringIO
import re
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def camel_case(text):
    """Convert text to CamelCase."""
    return ''.join(x for x in text.title() if not x.isspace())


def underscored(text):
    """Convert text to snake_case."""
    return text.lower().replace(" ", "_")


class Coordinator(object):
    """Coordinates code generation from database schema and templates."""

    def __init__(self, config):
        """Initialize coordinator with configuration.

        Args:
            config: Configuration dict with 'output' templates and 'connections'
        """
        self.config = config

    def _expand_output_path(self, output_path, table_name=None, connection_name=None):
        """Expand output path with variable substitutions.

        Supports:
            ${project} - project root directory
            ${output_dir} - output directory
            [table] - table name (for table-mode templates)
            [connection] - connection name (for schema-mode templates)

        Args:
            output_path: Path template string
            table_name: Current table name (for [table] substitution)
            connection_name: Current connection name (for [connection] substitution)

        Returns:
            str: Expanded path
        """
        expanded = output_path

        # Replace project variables
        if '${project}' in expanded:
            project_root = self.config.get('project_root', '.')
            expanded = expanded.replace('${project}', project_root)

        if '${output_dir}' in expanded:
            output_dir = self.config.get('output_dir', './generated')
            expanded = expanded.replace('${output_dir}', output_dir)

        # Replace table name
        if table_name and '[table]' in expanded:
            expanded = expanded.replace('[table]', table_name)

        # Replace connection name
        if connection_name and '[connection]' in expanded:
            expanded = expanded.replace('[connection]', connection_name)

        return expanded

    def _ensure_output_dir(self, file_path):
        """Ensure output directory exists.

        Args:
            file_path: Output file path

        Returns:
            bool: True if directory exists or was created
        """
        try:
            output_dir = os.path.dirname(file_path)
            if output_dir:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to create output directory {output_dir}: {e}")
            return False

    def _get_template_modus(self, template_source):
        """Extract modus from template source.

        Looks for comment like: ## modus: schema or ## modus: table

        Args:
            template_source: Template source code

        Returns:
            str: "schema", "table", or None if not found
        """
        match = re.search(r'##?\s*modus:\s*(\w+)', template_source)
        if match:
            return match.group(1)
        return None

    def _validate_template_path(self, template_from):
        """Validate and resolve template path."""
        if not template_from:
            logger.warning("Template config missing 'from' path")
            return None

        if not os.path.isabs(template_from) and os.path.isfile(template_from):
            template_from = os.path.abspath(template_from)

        if not os.path.isfile(template_from):
            puts(colored.red(f'Template file not found: {template_from}'))
            logger.error(f"Template file not found: {template_from}")
            return None

        return template_from

    def _process_template(self, template_config):
        """Process a single template configuration."""
        if not template_config.get('enabled', True):
            logger.debug(f"Template disabled: {template_config['from']}")
            return

        template_from = self._validate_template_path(template_config.get('from'))
        if not template_from:
            return

        template_to = template_config.get('to')

        try:
            mako_template = Template(filename=template_from)
            modus = self._get_template_modus(mako_template.source) or "schema"
            logger.debug(f"Rendering template {template_from} in {modus} mode")

            if modus == "schema":
                self._generate_schema_mode(mako_template, template_config, template_to)
            elif modus == "table":
                self._generate_table_mode(mako_template, template_config, template_to)
            else:
                logger.warning(f"Unknown modus '{modus}' in template {template_from}")

        except Exception as e:
            puts(colored.red(f'Error generating from template {template_from}: {e}'))
            logger.error(f"Template generation error: {e}", exc_info=True)
            raise

    def generate(self):
        """Generate code from all configured templates."""
        if 'output' not in self.config:
            logger.warning("No 'output' templates configured")
            return

        for template_config in self.config['output']:
            self._process_template(template_config)

    def _generate_schema_mode(self, template, template_config, output_path):
        """Generate code in schema mode (once per connection).

        Args:
            template: Mako template object
            template_config: Template configuration dict
            output_path: Output path template (or None)
        """
        for connection in self.config['connections']:
            schema = connection.get('parsedSchema')
            if not schema:
                logger.warning(f"No parsed schema for connection {connection.get('connection')}")
                continue

            # Render template
            rendered = template.render(schema=schema)

            # Output to file or stdout
            if output_path:
                expanded_path = self._expand_output_path(
                    output_path,
                    connection_name=connection.get('connection')
                )

                if self._ensure_output_dir(expanded_path):
                    with open(expanded_path, 'w') as f:
                        f.write(rendered)
                    puts(colored.green(f'Generated: {expanded_path}'))
                    logger.info(f"Generated: {expanded_path}")
            else:
                print(rendered)

    def _get_base_class_for_template(self, template_to, base_classes_config):
        """Determine base class configuration based on template output path.

        Args:
            template_to: Template output path pattern
            base_classes_config: Base classes configuration dict

        Returns:
            dict: Base class info for model, repository, builder
        """
        result = {}

        # Determine template type from output path
        if 'model' in template_to:
            result['model'] = base_classes_config.get('model', {})
        if 'repositor' in template_to:
            result['repository'] = base_classes_config.get('repository', {})
        if 'builder' in template_to or 'sqlbuilder' in template_to:
            result['builder'] = base_classes_config.get('builder', {})

        return result

    def _generate_table_mode(self, template, template_config, output_path):
        """Generate code in table mode (once per table per connection).

        Args:
            template: Mako template object
            template_config: Template configuration dict
            output_path: Output path template (or None)
        """
        # Load base classes configuration
        base_classes_config = self.config.get('base_classes', {})

        for connection in self.config['connections']:
            schema = connection.get('parsedSchema')
            if not schema:
                logger.warning(f"No parsed schema for connection {connection.get('connection')}")
                continue

            first_table_name = schema.table_names[0] if schema.table_names else None

            for table_idx, table_name in enumerate(schema.table_names):
                table = schema.tables[table_name]

                # Determine which base class to use based on template type
                template_to = template_config.get('to', '')
                base_class_info = self._get_base_class_for_template(template_to, base_classes_config)

                # Create context
                buf = StringIO()
                ctx = Context(
                    buf,
                    table=table,
                    table_name=table_name,
                    schema=schema,
                    underscored=underscored,
                    camel_case=camel_case,
                    _first_table=(table_idx == 0),
                    _last_table=(table_idx == len(schema.table_names) - 1),
                    _table_index=table_idx,
                    _first_table_name=first_table_name,
                    _base_model_class_name=base_class_info.get('model', {}).get('class_name', 'BaseModel'),
                    _base_model_import_from=base_class_info.get('model', {}).get('import_from'),
                    _base_repository_class_name=base_class_info.get('repository', {}).get('class_name', 'BaseRepository'),
                    _base_repository_import_from=base_class_info.get('repository', {}).get('import_from'),
                    _base_builder_class_name=base_class_info.get('builder', {}).get('class_name', 'BaseBuilder'),
                    _base_builder_import_from=base_class_info.get('builder', {}).get('import_from'),
                )

                # Render template
                template.render_context(ctx)
                rendered = buf.getvalue()

                # Output to file or stdout
                if output_path:
                    expanded_path = self._expand_output_path(
                        output_path,
                        table_name=table_name,
                        connection_name=connection.get('connection')
                    )

                    if self._ensure_output_dir(expanded_path):
                        with open(expanded_path, 'w') as f:
                            f.write(rendered)
                        puts(colored.green(f'Generated: {expanded_path}'))
                        logger.info(f"Generated: {expanded_path}")
                else:
                    print(rendered)
