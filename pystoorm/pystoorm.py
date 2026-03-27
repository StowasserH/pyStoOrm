#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Select name FROM ORM where rating='best'
    pystoorm
"""
__author__ = "Harald Stowasser"

from clint.textui import puts, colored
from clint import arguments
import yaml
from pystoorm.analyzer.controller import Controller
from pystoorm.generator.coordinator import Coordinator
import json

args = arguments.Args()
project = args.last
if not project or len(project) < 1:
    project = "../tests/sampleproject/project.yml"
# for arg in args:
#    if arg == None:
#        break
#    print ( arg )

def dumpclean(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if hasattr(v, '__iter__') and not isinstance(v, str):
                print(k)
                dumpclean(v)
            else:
                print('%s : %s' % (k, v))
    elif isinstance(obj, list):
        for v in obj:
            if hasattr(v, '__iter__') and not isinstance(v, str):
                dumpclean(v)
            else:
                print(v)
    else:
        print(obj)

try:
    with open("./config/bootstrap.yml", 'r') as stream:
        config = yaml.safe_load(stream)
except FileNotFoundError:
    puts(colored.red('Error: bootstrap.yml not found'))
    exit(1)
except yaml.YAMLError as exc:
    puts(colored.red(f'Error parsing bootstrap.yml: {exc}'))
    exit(1)

try:
    with open(project, 'r') as stream:
        project_config = yaml.safe_load(stream)
except FileNotFoundError:
    puts(colored.red(f'Error: project file {project} not found'))
    exit(1)
except yaml.YAMLError as exc:
    puts(colored.red(f'Error parsing project config: {exc}'))
    exit(1)

config.update(project_config)

analyzer = Controller(config)
analyzer.walk()

#print (config['connections'][0]['parsedTable'])
#print(json.dumps(config['connections'], indent = 1))
dumpclean(config['connections'][0]['parsedSchema'].table_names)

generator= Coordinator(config)
generator.generate()

puts(colored.green('Ready'))
