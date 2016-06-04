#!/usr/bin/env python

""" setup.py: install PyRIC

Copyright (C) 2016  Dale V. Patterson (wraith.wireless@yandex.com)

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

Redistribution and use in source and binary forms, with or without modifications,
are permitted provided that the following conditions are met:
 o Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
 o Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
 o Neither the name of the orginal author Dale V. Patterson nor the names of any
   contributors may be used to endorse or promote products derived from this
   software without specific prior written permission.

"""

#__name__ = 'setup'
__license__ = 'GPLv3'
__version__ = '0.0.3'
__date__ = 'June 2016'
__author__ = 'Dale Patterson'
__maintainer__ = 'Dale Patterson'
__email__ = 'wraith.wireless@yandex.com'
__status__ = 'Production'

from setuptools import setup, find_packages
import pyric

long_desc = """
 PyRIC is Linux wireless network interface card library. It provides the ability to
 manipuate, identify and enumerate your system's wireless cards. PyRIC is a pure
 python port of a subset of the functionality provided by iw, ifconfig, iwconfig
 and rfkill.

 PyRIC is:
 * Pythonic: No ctypes, SWIG etc. PyRIC redefines C header files as Python and
 uses sockets to communicate with kernel.
 * Self-sufficient: No third-party files used, PyRIC is completely self-contained
 * Fast: (relatively speaking) PyRIC is faster than using iw through subprocess.Popen
 * Parseless: Get the output you without parsing output from iw. Never worry about
 iw updates and rewriting your parsers.
 * Easy: If you can use iw, you can use PyRIC
"""

setup(name='PyRIC',
      version=pyric.__version__,
      description="Pythonic iw",
      long_description=long_desc,
      url='http://wraith-wireless.github.io/pyric',
      download_url="https://github.com/wraith-wireless/pyric/archive/"+pyric.__version__+".tar.gz",
      author=pyric.__author__,
      author_email=pyric.__email__,
      maintainer=pyric.__maintainer__,
      maintainer_email=pyric.__email__,
      license=pyric.__license__,
      classifiers=['Development Status :: 5 - Production/Stable',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                   'Intended Audience :: Developers',
                   'Intended Audience :: System Administrators',
                   'Topic :: Security',
                   'Topic :: Software Development',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Security',
                   'Topic :: System :: Networking',
                   'Topic :: Utilities',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.7'
                   ],
    keywords='Linux nl80211 iw wireless pentest',
    packages=find_packages(),
    package_data={'pyric':['docs/*.help']}
)
