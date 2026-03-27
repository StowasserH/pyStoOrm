#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""connects to a db"""
__author__ = "Harald Stowasser"
# CREATE USER 'pystoorm'@'localhost' IDENTIFIED BY 'pystoormpw';
import importlib
from clint.textui import puts, colored
from pystoorm.database.connector import Connector
from .parser import Parser


class Controller(object):
    config = None

    def __init__(self, config):
        self.config = config

    def build_import(self, connector):
        if len(connector) > 0:
            path = connector.split('.')
            if len(path) == 1:
                return 'pystoorm.database.' + connector.lower(), connector
            else:
                # Prepend 'pystoorm.' if not already present
                full_path = '.'.join(path[0:-1])
                if not full_path.startswith('pystoorm.'):
                    full_path = 'pystoorm.' + full_path
                return full_path, path[-1]

        return 'pystoorm.database.nullconnector', 'NullConnector'

    def conector_fabrik(self, connector):
        try:
            package, module = self.build_import(connector)
            puts(colored.green('Load : ' + package + ' -> ' + module + ''))
            lib = importlib.import_module(package)
            dbclass = getattr(lib, module)
            if not issubclass(dbclass, Connector):
                raise AttributeError("Module " + module + " is not a Connector")
            return dbclass()
        except ImportError as e:
            puts(colored.red(f'Error loading connector {connector}: {e}'))
            raise
        except AttributeError as e:
            puts(colored.red(f'Error: {e}'))
            raise

    def walk(self):
        for connection in self.config['connections']:
            try:
                connector_object = self.conector_fabrik(connection['connector'])
                connector_object.set_config(connection)
                connection["connector_object"] = connector_object
                connector_object.connect()
                parser = Parser(connector_object)
                connection["parsedSchema"] = parser.parse()
            except Exception as e:
                puts(colored.red(f'Error processing connection {connection.get("name", "unknown")}: {e}'))
                raise
