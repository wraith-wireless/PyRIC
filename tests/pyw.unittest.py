#!/usr/bin/env python
""" pyw_unittest.py: utility functions

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

Define unittest functions for pyw
"""

#__name__ = 'pyw_unittest'
__license__ = 'GPLv3'
__version__ = '0.0.1'
__date__ = 'May 2016'
__author__ = 'Dale Patterson'
__maintainer__ = 'Dale Patterson'
__email__ = 'wraith.wireless@yandex.com'
__status__ = 'Production'

import unittest
import time
from pyric import pyw

# modify below to fit your system
nics = ['alfa0','rose0','eth0','lo','wlan0']
enics = ['eth0','lo']
wnics = ['alfa0','rose0','wlan0']
inics = ['foo0','bar0']
regdom = '00'
regdomnew = 'BO'

# test functions interfaces and isinterface
class InterfaceTestCase(unittest.TestCase):
    def testEnum(self):
        self.assertEqual(nics,pyw.interfaces())
    def testIs(self):
        for n in nics:
            self.assertTrue(pyw.isinterface(n))
    def testNotIs(self):
        for i in inics:
            self.assertFalse(pyw.isinterface(i))
    def testIn(self):
        for n in nics:
            self.assertIn(n,pyw.interfaces())

# test functions winterfaces and iswireless
class WInterfaceTestCase(unittest.TestCase):
    def testEnum(self):
        self.assertEqual(wnics,pyw.winterfaces())
    def testIs(self):
        for w in wnics:
            self.assertTrue(pyw.iswireless(w))
    def testNotIs(self):
        for i in inics + enics:
            self.assertFalse(pyw.iswireless(i))
    def testIn(self):
        for w in wnics:
            self.assertIn(w,pyw.winterfaces())

# test regget, regset
class RegDomTestCase(unittest.TestCase):
    def testIs(self):
        self.assertEqual(regdom,pyw.regget())
    def testNotIs(self):
        self.assertFalse('US'==pyw.regget())
    def testSet(self):
        self.assertTrue(pyw.regset(regdomnew))
        time.sleep(0.25) # give sleep time
        self.assertEqual(regdomnew,pyw.regget())
        self.assertTrue(pyw.regset(regdom))
        time.sleep(0.25) # give sleep time
        self.assertEqual(regdom, pyw.regget())

if __name__ == '__main__':
    unittest.main()