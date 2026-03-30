#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""connects to a db"""
__author__ = "Harald Stowasser"


# CREATE USER 'pystoorm'@'localhost' IDENTIFIED BY 'pystoormpw';

class Connector(object):
    config = None

    def __init__(self, config=None):
        if config is not None:
            self.set_config(config)

    def set_config(self, config):
        self.config = config

    def connect(self):
        raise Exception("NotImplementedException")

    def get_schema(self):
        raise Exception("NotImplementedException")

    def get_table(self, table):
        raise Exception("NotImplementedException")

    def get_column(self, table, column):
        raise Exception("NotImplementedException")
