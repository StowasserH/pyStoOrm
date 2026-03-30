#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pyStoOrm - ORM Code Generator entry point

This script launches the pyStoOrm module as a package entry point.
It can be run as: python pyStoOrm.py <config_file>
or: python -m pystoorm <config_file>
"""
import sys
import subprocess

if __name__ == "__main__":
    # Run the pystoorm module with all arguments
    sys.exit(subprocess.call([sys.executable, "-m", "pystoorm"] + sys.argv[1:]))
