#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test ConfigLoader - Hierarchical Configuration Loading
"""

import unittest
import os
from pystoorm.config.loader import ConfigLoader, load_config


class TestConfigLoader(unittest.TestCase):
    """Test cases for ConfigLoader"""

    def setUp(self):
        """Set up test fixtures"""
        self.loader = ConfigLoader()

    def test_load_defaults(self):
        """Test loading default configurations"""
        self.loader.load_defaults()
        config = self.loader.get_config()

        # Check that key sections are loaded
        self.assertIn('logging', config)
        self.assertIn('naming', config)
        self.assertIn('style', config)
        self.assertIn('attribute_hints', config)
        self.assertIn('output', config)

    def test_bootstrap_loaded(self):
        """Test bootstrap.yml is loaded"""
        self.loader.load_defaults()
        config = self.loader.get_config()

        # bootstrap.yml should have logging and output
        self.assertIsNotNone(config.get('logging'))
        self.assertIsNotNone(config.get('output'))

    def test_naming_conventions_loaded(self):
        """Test naming-conventions.yml is loaded"""
        self.loader.load_defaults()
        config = self.loader.get_config()

        naming = config.get('naming', {})
        self.assertIn('primary_key', naming)
        self.assertIn('foreign_key', naming)
        self.assertIn('table', naming)
        self.assertIn('column', naming)

    def test_style_guide_loaded(self):
        """Test style-guides/python-pep8.yml is loaded"""
        self.loader.load_defaults()
        config = self.loader.get_config()

        style = config.get('style', {})
        self.assertIn('class_naming', style)
        self.assertIn('method_naming', style)
        self.assertIn('formatting', style)

    def test_attribute_hints_loaded(self):
        """Test attribute-hints.yml is loaded"""
        self.loader.load_defaults()
        config = self.loader.get_config()

        hints = config.get('attribute_hints', {})
        self.assertIn('defaults', hints)
        self.assertIn('fallback', hints)

    def test_merge_deep_simple(self):
        """Test deep merge with simple values"""
        base = {'a': 1, 'b': {'c': 2}}
        override = {'b': {'d': 3}}

        result = ConfigLoader._merge_deep(base, override)

        self.assertEqual(result['a'], 1)
        self.assertEqual(result['b']['c'], 2)
        self.assertEqual(result['b']['d'], 3)

    def test_merge_deep_override(self):
        """Test deep merge overrides values"""
        base = {'a': 1, 'b': {'c': 2}}
        override = {'b': {'c': 999}}

        result = ConfigLoader._merge_deep(base, override)

        self.assertEqual(result['b']['c'], 999)

    def test_get_config_method(self):
        """Test get_config returns merged configuration"""
        self.loader.load_defaults()
        config = self.loader.get_config()

        self.assertIsInstance(config, dict)
        self.assertGreater(len(config), 0)

    def test_get_config_by_key(self):
        """Test getting values by dotted key path"""
        self.loader.load_defaults()

        # Test existing key
        log_level = self.loader.get('logging.level')
        self.assertIsNotNone(log_level)

        # Test non-existent key with default
        value = self.loader.get('nonexistent.key', 'default')
        self.assertEqual(value, 'default')

    def test_optional_files_missing(self):
        """Test loading when optional project files don't exist"""
        # Should not raise error if project files don't exist
        self.loader.load_defaults()
        self.loader.load_project('nonexistent/project.yml')  # Should not crash

        config = self.loader.get_config()
        self.assertIn('naming', config)  # Defaults should still be there

    def test_project_path_as_directory(self):
        """Test loading project from directory path"""
        project_dir = "pystoorm/config/projects/example"
        if os.path.exists(project_dir):
            loader = ConfigLoader()
            loader.load_defaults()
            loader.load_project(project_dir)
            config = loader.get_config()

            # Should have connections from project.yml
            self.assertIn('connections', config)

    def test_project_path_as_file(self):
        """Test loading project from file path"""
        project_file = "pystoorm/config/projects/example/project.yml"
        if os.path.exists(project_file):
            loader = ConfigLoader()
            loader.load_defaults()
            loader.load_project(project_file)
            config = loader.get_config()

            # Should have connections from project.yml
            self.assertIn('connections', config)

    def test_convenience_function(self):
        """Test load_config convenience function"""
        project_file = "pystoorm/config/projects/example/project.yml"
        if os.path.exists(project_file):
            config = load_config(project_file)

            self.assertIsInstance(config, dict)
            self.assertIn('naming', config)
            self.assertIn('connections', config)

    def test_logging_level_from_config(self):
        """Test reading logging level from config"""
        self.loader.load_defaults()
        config = self.loader.get_config()

        log_level = config['logging']['level']
        self.assertIn(log_level, ['DEBUG', 'INFO', 'WARN', 'ERROR'])


class TestConfigHierarchy(unittest.TestCase):
    """Test configuration hierarchy and merging"""

    def test_hierarchy_order(self):
        """Test that configurations are loaded in correct order"""
        loader = ConfigLoader()
        loader.load_defaults()
        config = loader.get_config()

        # Should have all default sections
        self.assertIn('logging', config)
        self.assertIn('naming', config)
        self.assertIn('style', config)
        self.assertIn('attribute_hints', config)

    def test_project_overrides_defaults(self):
        """Test that project config overrides defaults"""
        project_file = "pystoorm/config/projects/example/project.yml"
        if os.path.exists(project_file):
            loader = ConfigLoader()
            loader.load_defaults()
            defaults_config = loader.get_config().copy()

            loader2 = ConfigLoader()
            loader2.load_defaults().load_project(project_file)
            final_config = loader2.get_config()

            # Project-specific values should be present
            self.assertIn('connections', final_config)
            # Defaults should still be there
            self.assertIn('naming', final_config)


if __name__ == '__main__':
    unittest.main()
