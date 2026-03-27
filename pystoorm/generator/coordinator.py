#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""builds all those fancy files"""
__author__ = "Harald Stowasser"
# CREATE USER 'pystoorm'@'localhost' IDENTIFIED BY 'pystoormpw';
## this is a comment.

from mako.template import Template
from mako.runtime import Context
from clint.textui import puts, colored
from io import StringIO

import re
import os

def camel_case(text):
    return ''.join(x for x in text.title() if not x.isspace())

def underscored(text):
    return text.lower().replace(" ", "_")

class Coordinator(object):
    config = None

    def __init__(self, config):
        self.config = config

    def generate(self):
        for template in self.config['output']:
            temp_from = template['from']
            if not os.path.isfile(temp_from):
                puts(colored.red('No File: '+temp_from))
                continue
            mytemplate = Template(filename=temp_from)
            modus = re.search('modus: (.+)', mytemplate.source)
            if modus:
                found = modus.group(1)
                if found == "schema":
                    for connection in self.config['connections']:
                        print(mytemplate.render(schema=connection["parsedSchema"]))
                if found == "table":
                    for connection in self.config['connections']:
                        schema=connection["parsedSchema"]
                        for table in schema.table_names:
                            buf = StringIO()
                            ctx = Context(buf, table=schema.tables[table],table_name=table, underscored = underscored,camel_case=camel_case )

                            mytemplate.render_context(ctx)
                            print(buf.getvalue())

                            #tables=["dffsd","efsdf"],forward_keys=[["dffsd","efsdf"],["dffsd","efsdf"]]))


#output:
#- from: ./templates/python/model.py.template
#to: [project]
#- from: ./templates/python/model.py
#- from: ./templates/python/repository.py.template
#- from: ./templates/[output]/graphviz..dot.template
