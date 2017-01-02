#!/usr/bin/env python

""" ouiupdate.py: get ouis data from IEEE

Copyright (C) 2016  Dale V. Patterson (wraith.wireless@yandex.com)

This program is free software:you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation,either version 3 of the License,or (at your option) any later
version.

Redistribution and use in source and binary forms,with or without modifications,
are permitted provided that the following conditions are met:
 o Redistributions of source code must retain the above copyright notice,this
   list of conditions and the following disclaimer.
 o Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
 o Neither the name of the orginal author Dale V. Patterson nor the names of any
   contributors may be used to endorse or promote products derived from this
   software without specific prior written permission.

Fetchs and stores oui data from IEEE

"""
from __future__ import print_function  # python 2to3 compability

#__name__ = 'ouiupdate'
__license__ = 'GPLv3'
__version__ = '0.0.1'
__date__ = 'January 2017'
__author__ = 'Dale Patterson'
__maintainer__ = 'Dale Patterson'
__email__ = 'wraith.wireless@yandex.com'
__status__ = 'Production'

import argparse as ap
import pyric.utils.ouifetch as ouifetch

if __name__ == '__main__':
    # create arg parser and parse command line args
    print("IEEE OUI Fetch")
    argp = ap.ArgumentParser(description="IEEE OUI fetch and parse")
    argp.add_argument('-p','--path',help="Path to write parsed file")
    argp.add_argument('-v','--verbose',action='store_true',help="Display operations to stdout")
    argp.add_argument('--version',action='version',version="OUI Fetch {0}".format(__version__))
    args = argp.parse_args()
    verbose = args.verbose
    path = args.path

    # execute
    ouifetch.fetch(path,verbose)
