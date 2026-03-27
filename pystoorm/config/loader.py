#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ConfigLoader - Hierarchical Configuration Loading System
Loads and merges configuration files in the following order:
1. bootstrap.yml (global defaults)
2. naming-conventions.yml (default naming conventions)
3. style-guides/python-pep8.yml (default style guide)
4. attribute-hints.yml (default attribute hints)
5. project.yml (project-specific settings and overrides)
"""

import os
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Hierarchically loads and merges YAML configuration files."""

    def __init__(self, base_path=None):
        """
        Initialize ConfigLoader.

        Args:
            base_path: Root path for configuration files.
                      If None, uses the directory of this file.
        """
        if base_path is None:
            base_path = os.path.dirname(os.path.abspath(__file__))

        self.base_path = base_path
        self.defaults_path = os.path.join(base_path, "defaults")
        self.projects_path = os.path.join(base_path, "projects")
        self.config = {}

    @staticmethod
    def _merge_deep(base, override):
        """
        Recursively merge override dict into base dict.
        Only overwrites keys that are present in override.

        Args:
            base: Base configuration dict
            override: Override configuration dict

        Returns:
            Merged dict
        """
        if not isinstance(override, dict):
            return override

        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                ConfigLoader._merge_deep(base[key], value)
            else:
                base[key] = value

        return base

    def _load_yaml(self, file_path):
        """
        Load a YAML file.

        Args:
            file_path: Path to YAML file

        Returns:
            Parsed YAML content as dict, or empty dict if file not found
        """
        if not os.path.exists(file_path):
            logger.debug(f"Configuration file not found (optional): {file_path}")
            return {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data is None:
                    return {}
                logger.debug(f"Loaded configuration: {file_path}")
                return data
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML in {file_path}: {e}")
        except IOError as e:
            raise IOError(f"Error reading {file_path}: {e}")

    def load_defaults(self):
        """
        Load all default configuration files in order:
        1. bootstrap.yml
        2. naming-conventions.yml
        3. style-guides/python-pep8.yml
        4. attribute-hints.yml

        Returns:
            self (for method chaining)
        """
        # 1. Bootstrap (output templates, logging)
        bootstrap_path = os.path.join(self.defaults_path, "bootstrap.yml")
        bootstrap_data = self._load_yaml(bootstrap_path)
        if bootstrap_data:
            self.config.update(bootstrap_data)

        # 2. Naming Conventions
        naming_path = os.path.join(self.defaults_path, "naming-conventions.yml")
        naming_data = self._load_yaml(naming_path)
        if naming_data:
            self._merge_deep(self.config, naming_data)

        # 3. Style Guide (Python PEP8)
        style_path = os.path.join(self.defaults_path, "style-guides", "python-pep8.yml")
        style_data = self._load_yaml(style_path)
        if style_data:
            self._merge_deep(self.config, style_data)

        # 4. Attribute Hints
        hints_path = os.path.join(self.defaults_path, "attribute-hints.yml")
        hints_data = self._load_yaml(hints_path)
        if hints_data:
            self._merge_deep(self.config, hints_data)

        return self

    def load_project(self, project_path):
        """
        Load project-specific configuration and overrides.

        Loads:
        1. project.yml (main project config with database connection)
        2. naming-conventions.yml (optional: project-specific naming)
        3. style-guide.yml (optional: project-specific style)
        4. attribute-hints.yml (optional: project-specific hints)

        Args:
            project_path: Path to project directory or project.yml file

        Returns:
            self (for method chaining)
        """
        # Handle both directory and file paths
        if os.path.isfile(project_path):
            project_dir = os.path.dirname(project_path)
            project_file = project_path
        else:
            project_dir = project_path
            project_file = os.path.join(project_dir, "project.yml")

        # 1. Main project.yml
        project_data = self._load_yaml(project_file)
        if project_data:
            self._merge_deep(self.config, project_data)

        # 2. Optional: project-specific naming conventions
        naming_override_path = os.path.join(project_dir, "naming-conventions.yml")
        naming_override = self._load_yaml(naming_override_path)
        if naming_override:
            self._merge_deep(self.config, naming_override)

        # 3. Optional: project-specific style guide
        style_override_path = os.path.join(project_dir, "style-guide.yml")
        style_override = self._load_yaml(style_override_path)
        if style_override:
            self._merge_deep(self.config, style_override)

        # 4. Optional: project-specific attribute hints
        hints_override_path = os.path.join(project_dir, "attribute-hints.yml")
        hints_override = self._load_yaml(hints_override_path)
        if hints_override:
            self._merge_deep(self.config, hints_override)

        return self

    def get_config(self):
        """
        Get the complete merged configuration.

        Returns:
            Configuration dict
        """
        return self.config

    def get(self, key, default=None):
        """
        Get a specific configuration value by key path.

        Args:
            key: Dot-separated path (e.g., "naming.primary_key.patterns")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def pretty_print(self, limit=None):
        """
        Print configuration in readable format (for debugging).

        Args:
            limit: Limit output to first N items (optional)
        """
        import json
        config_str = json.dumps(self.config, indent=2, default=str)
        if limit:
            lines = config_str.split('\n')[:limit]
            config_str = '\n'.join(lines) + '\n...'
        print(config_str)


# Convenience function for common usage
def load_config(project_path, base_path=None):
    """
    Load complete configuration (defaults + project).

    Args:
        project_path: Path to project directory or project.yml file
        base_path: Base path for configuration files (optional)

    Returns:
        Merged configuration dict
    """
    loader = ConfigLoader(base_path)
    loader.load_defaults().load_project(project_path)
    return loader.get_config()
