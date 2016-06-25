#!/usr/bin/env python
""" pyric Python Radio Interface Controller

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

Defines the Pyric error class and constants for some errors. All pyric errors
will follow the 2-tuple form of EnvironmentError

Requires:
 linux (preferred 3.x kernel)
 Python 2.7

 pyric 0.1.3
  desc: wireless nic library: wireless radio identification, manipulation, enumeration
  includes: /nlhelp /lib /net /utils pyw 0.1.4
  changes:
   See CHANGES in top-level directory

"""

__name__ = 'pyric'
__license__ = 'GPLv3'
__version__ = '0.1.3'
__date__ = 'June 2016'
__author__ = 'Dale Patterson'
__maintainer__ = 'Dale Patterson'
__email__ = 'wraith.wireless@yandex.com'
__status__ = 'Production'

from os import strerror

# all exceptions are tuples t=(error code,error message)
# we use errno.errocodes and use codes < 0 as an undefined error code
EUNDEF = -1
class error(EnvironmentError): pass

def perror(e):
    """
    :param e: error code
    :returns: string description of error code
    """
    # anything less than 0 is an unknown
    return strerror(e)