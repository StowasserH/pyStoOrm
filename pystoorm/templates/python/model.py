#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
*TL;DR
Separates data in GUIs from the ways it is presented, and accepted.
"""


class Model(object):
    row = []

    def __init__(self, row=[]):
        self.row = row

    def __iter__(self):
        raise NotImplementedError

    def get(self, item):
        """Returns an object with a .items() call method
        that iterates over key,value pairs of its information."""
        raise NotImplementedError

    @property
    def item_type(self):
        raise NotImplementedError
