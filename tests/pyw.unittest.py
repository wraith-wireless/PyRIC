#!/usr/bin/env python
""" pyw.unittest.py: unittest

Define unittest functions for pyw

Assumptions:
 o user has root privileges
 o user has set up global variables to system
 o private functions are tested via methods
 o persistent sockets are tested via one-time methods that is, one-time socket
   calls result in netlink socket creation, usage and deletion

usage:
 sudo python pyw.unittest.py -v

Results as of 31-May-15
sudo python pyw.unittest.py
.............................................................
----------------------------------------------------------------------
Ran 61 tests in 5.360s

OK

"""

#__name__ = 'pyw.unittest'
__license__ = 'GPLv3'
__version__ = '0.0.1'
__date__ = 'June 2016'
__author__ = 'Dale Patterson'
__maintainer__ = 'Dale Patterson'
__email__ = 'wraith.wireless@yandex.com'
__status__ = 'Production'

import unittest
import time
from pyric import error
from pyric.channels import ISM_24_F2C,rf2ch
from pyric import pyw

# modify below to fit your system
pri = {'dev':'alfa0',
       'mac':'00:c0:ca:59:af:a6',
       'ifindex':5,
       'phy':2,
       'mode':'managed',
       'tx':20,
       'freqs':sorted(ISM_24_F2C.keys()),
       'stds':['b','g','n'],
       'ip':'192.168.3.23',
       'bcast':'192.168.3.63',
       'mask':'255.255.255.192'}
newhw = '00:c0:ca:60:b0:a7'
newip = '192.168.3.30'
newbcast = '192.168.3.255'
newmask = '255.255.255.0'
nics = ['alfa0','rose0','eth0','lo','wlan0']
enics = ['eth0','lo']
wnics = ['alfa0','rose0','wlan0']
inics = ['foo0','bar0']
regdom = '00'
newregdom = 'BO'

# test functions interfaces and isinterface
class InterfaceTestCase(unittest.TestCase):
    def test_enuminterfaces(self):
        self.assertEqual(nics,pyw.interfaces())
    def test_isinterface(self):
        for nic in nics:
            self.assertTrue(pyw.isinterface(nic))
    def test_not_isinterface(self):
        for inic in inics:
            self.assertFalse(pyw.isinterface(inic))
    def test_ininterfaces(self):
        for nic in nics:
            self.assertIn(nic,pyw.interfaces())

# test functions winterfaces and iswireless
class WInterfaceTestCase(unittest.TestCase):
    def test_enumwinterfaces(self):
        self.assertEqual(wnics,pyw.winterfaces())
    def test_iswinterface(self):
        for wnic in wnics:
            self.assertTrue(pyw.iswireless(wnic))
    def test_not_iswinterface(self):
        for nic in inics + enics:
            self.assertFalse(pyw.iswireless(nic))
    def test_inwinterfaces(self):
        for wnic in wnics:
            self.assertIn(wnic,pyw.winterfaces())

# test regget, regset
class RegDomTestCase(unittest.TestCase):
    def test_regget(self):
        self.assertEqual(regdom,pyw.regget())
    def test_regset(self):
        self.assertTrue(pyw.regset(newregdom))
        time.sleep(0.25) # give sleep time
        self.assertEqual(newregdom,pyw.regget())
        self.assertTrue(pyw.regset(regdom))
        time.sleep(0.25) # give sleep time
        self.assertEqual(regdom, pyw.regget())

# test getcard,validcard
class GetCardTestCase(unittest.TestCase):
    def test_getcard(self):
        for wnic in wnics:
            self.assertIsNotNone(pyw.getcard(wnic))
    def test_notacard(self):
        for enic in enics:
            self.assertRaises(error,pyw.getcard,enic)
    def test_validcard(self):
        for wnic in wnics:
            self.assertTrue(pyw.validcard(pyw.getcard(wnic)))

# super class for test cases requiring a Card object
class CardTestCase(unittest.TestCase):
    def setUp(self): self.card = pyw.getcard(pri['dev'])
    def tearDown(self): pass

# test macget
class MacGetTestCase(CardTestCase):
    def test_macget(self):
        self.assertEquals(pri['mac'],pyw.macget(self.card))
    def test_invalidcardarg(self):
        self.assertRaises(error,pyw.macget,'bad0')

# test macset
class MacSetTestCase(CardTestCase):
    def setUp(self):
        CardTestCase.setUp(self)
        pyw.down(self.card)
    def tearDown(self):
        pyw.up(self.card)
    def test_macset(self):
        self.assertEqual(newhw,pyw.macset(self.card,newhw))
        self.assertEqual(pri['mac'],pyw.macset(self.card,pri['mac']))
    def test_invalidcardarg(self):
        self.assertRaises(error,pyw.macset,'bad0',newhw)
    def test_invalidmacarg(self):
        self.assertRaises(error,pyw.macset,self.card,'00:0A')

# test inetget/inetset
# testing both together as the test card alfa0 is never associated thus
# never has an ip etc
# NOTE: through inetset, we get the side-effect of testing ip4set, netmaskset,
#  broadcastset
class InetGetSetTestCase(CardTestCase):
    def test_inetgetset(self):
        self.assertTrue(pyw.inetset(self.card,pri['ip'],pri['mask'],pri['bcast']),
                        "InetGetSetTestCase.inetgetset->inetset Failed")
        self.assertEqual(pri['ip'],pyw.inetget(self.card)[0],
                         "InetGetSetTestCase.inetgetset->inetget Failed")
    def test_invalidcardarg(self):
        self.assertRaises(error,pyw.inetget,'bad0')
        self.assertRaises(error,pyw.inetset,'bad0',pri['ip'],
                                            pri['mask'],pri['bcast'])
    def test_invalidiparg(self):
        self.assertRaises(error,pyw.inetset,self.card,'192.168',pri['mask'],pri['bcast'])
    def test_invalidmaskarg(self):
        self.assertRaises(error,pyw.inetset,self.card,pri['ip'],'255.255',pri['bcast'])
    def test_invalidbcastarg(self):
        self.assertRaises(error,pyw.inetset,self.card,pri['ip'],pri['mask'],'192.168')

# test up
class UpTestCase(CardTestCase):
    def test_up(self): self.assertTrue(pyw.up(self.card))
    def test_invalidcardarg(self): self.assertRaises(error,pyw.up,'bad0')

# test down
class DownTestCase(CardTestCase):
    def test_down(self): self.assertTrue(pyw.down(self.card))
    def test_invalidcardarg(self): self.assertRaises(error,pyw.down,'bad0')

# test get freqs
class DevFreqsTestCase(CardTestCase):
    def test_devfreqs(self):
        self.assertItemsEqual(pri['freqs'],pyw.devfreqs(self.card))
    def test_invalidcardarg(self):
        self.assertRaises(error,pyw.devfreqs,'bad0')

# test get chs
class DevCHsTestCase(CardTestCase):
    def test_devchs(self):
        self.assertItemsEqual(map(rf2ch,pri['freqs']),pyw.devchs(self.card))
    def test_invalidcardarg(self):
        self.assertRaises(error,pyw.devchs,'bad0')

# test get stds
class DevSTDsTestCase(CardTestCase):
    def test_devchs(self):
        self.assertItemsEqual(pri['stds'],pyw.devstds(self.card))
    def test_invalidcardarg(self):
        self.assertRaises(error,pyw.devstds,'bad0')

# test get modes
class DevModesTestCase(CardTestCase):
    def test_devmodes(self):
        self.assertIn('managed',pyw.devmodes(self.card))
    def test_invalidcardarg(self):
        self.assertRaises(error,pyw.devmodes,'bad0')

# test get cmds
class DevCMDsTestCase(CardTestCase):
    def test_devcmds(self):
        self.assertIsInstance(pyw.devmodes(self.card),list)
    def test_invalidcardarg(self):
        self.assertRaises(error,pyw.devmodes,'bad0')

# test devinfo
class DevInfoTestCase(CardTestCase):
    def test_devinfobycard(self):
        self.assertIsInstance(pyw.devinfo(self.card),dict)
    def test_devinfobydev(self):
        self.assertIsInstance(pyw.devinfo(pri['dev']),dict)
    def test_invalidcardarg(self):
        self.assertRaises(error,pyw.devinfo,'bad0')

# test phyinfo
class PhyInfoTestCase(CardTestCase):
    def test_phyinfo(self):
        self.assertIsInstance(pyw.phyinfo(self.card),dict)
    def test_invalidcardarg(self):
        self.assertRaises(error,pyw.phyinfo,'bad0')

# test txget
class TXGetTestCase(CardTestCase):
    def test_txget(self):
        self.assertEquals(pri['tx'],pyw.txget(self.card))
    def test_invalidcardarg(self):
        self.assertRaises(error,pyw.txget,'bad0')

# test chget/chset
# since we are using a non-associated card, we will get None for chget
# testing chset simulatenously allows us to test chset then chget
# NOTE: we don't test for specific ch in chget, just in the infitesimal chance
# that somehow the ch was reset etc
class CHGetSetTestCase(CardTestCase):
    def test_chsetget(self):
        pyw.down(self.card)
        pyw.modeset(self.card,'monitor')
        pyw.up(self.card)
        self.assertTrue(pyw.chset(self.card,1))
        self.assertIsInstance(pyw.chget(self.card),int)
        pyw.down(self.card)
        pyw.modeset(self.card,'managed')
        pyw.up(self.card)
    def test_invalidcardarg(self):
        self.assertRaises(error,pyw.chset,pri['dev'],1)
        self.assertRaises(error,pyw.chget,'bad0')
    def test_invalidcharg(self):
        self.assertRaises(error,pyw.chset,self.card,0,None)
    def test_invalidchwarg(self):
        self.assertRaises(error,pyw.chget,self.card,1,'HT30+')

# test freqset
# because freqset was already tested in chgetset, we only test invalid args
class FreqSetTestCase(CardTestCase):
    def test_invalidrfarg(self):
        # we test both an invalid RF and an RF  the card does not support
        self.assertRaises(error,pyw.freqset,self.card,2410)
        self.assertRaises(error,pyw.freqset,self.card,5250)

# test modeget
class ModeGetTestCase(CardTestCase):
    def test_modeget(self):
        self.assertEquals('managed',pyw.modeget(self.card))
    def test_invalidcardarg(self):
        self.assertRaises(error,pyw.modeget,'bad0')

# test modeset
class ModeSetTestCase(CardTestCase):
    def test_modeset(self):
        pyw.down(self.card)
        self.assertTrue(pyw.modeset(self.card,'monitor'))
        self.assertTrue(pyw.modeset(self.card,'managed'))
        pyw.up(self.card)
    def test_invalidcardarg(self):
        self.assertRaises(error,pyw.modeset,'bad0','monitor')
    def test_invalidmodearg(self):
        self.assertRaises(error,pyw.modeset,self.card,'foobar')
    def test_invalidmonitorflagarg(self):
        self.assertRaises(error,pyw.modeset,self.card,'monitor','bad')
        self.assertRaises(error,pyw.modeset,self.card,'managed','fcsfail')

# test ifaces
class IfacesTestCase(CardTestCase):
    def test_ifaces(self):
        self.assertIsInstance(pyw.ifaces(self.card),list)
    def test_invalidcardarg(self):
        self.assertRaises(error,pyw.ifaces,'b0b0')

# test devadd/devdel
class DevAddDelTestCase(CardTestCase):
    def test_devadddel(self):
        card = pyw.devadd(self.card,'test0','monitor')
        self.assertTrue(pyw.devdel(card))
    def test_invalidcardarg(self):
        self.assertRaises(error,pyw.devadd,'bad0','test0','monitor')
        self.assertRaises(error,pyw.devdel,'bad0')
        card = pyw.devadd(self.card,'test0','monitor')
        pyw.devdel(card)
        self.assertRaises(error,pyw.devdel,card)
    def test_invalidmodearg(self):
        self.assertRaises(error,pyw.devadd,self.card,'test0','foobar')
    def test_invalidflagsarg(self):
        self.assertRaises(error,pyw.devadd,self.card,'test0','monitor','foobar')
        self.assertRaises(error,pyw.devadd,self.card,'test0','managed','fcsfail')

if __name__ == '__main__':
    unittest.main()
























