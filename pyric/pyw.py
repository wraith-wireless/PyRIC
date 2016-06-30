#!/usr/bin/env python

""" pyw.py: python iw

Copyright (C) 2016  Dale V. Patterson (wraith.wireless@yandex.com)

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

Redistribution and use in source and binary forms, with or without
modifications, are permitted provided that the following conditions are met:
 o Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
 o Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
 o Neither the name of the orginal author Dale V. Patterson nor the names of
    any contributors may be used to endorse or promote products derived from
    this software without specific prior written permission.

Provides a python version of a subset of the iw command & additionally, a
smaller subset of ifconfig/iwconfig.

Each command/function (excluding interfaces & isinterface which do not rely on
ioctl/netlink sockets) comes in two flavors - one-time & persistent.
 1) one-time: similar to iw. The command, creates the netlink socket
    (or ioctl), composes the message, sends the message & receives the
    response, parses the results, closes the socket & returns the results to
    the caller. At no time does the caller need to be aware of any underlying
    netlink processes or structures.
 2) persistent: communication & parsing only. The onus of socket creation and
    deletion is on the caller which allows them to create one (or more)
    socket(s). The pyw functions will only handle message construction, message
    sending and receiving & message parsing.

Callers that intend to use pyw functionality often & repeatedly may prefer to
use a persistent netlink/ioctl socket. Socket creation & deletion are
relatively fast however, if a program is repeatedly using pyw function(s)
(such as a scanner that is changing channels mulitple times per second) it
makes sense for the caller to create a socket one time only & use the same
socket. However, if the caller is only using pyw periodically and/or does not
want to bothered with socket maintenance, the one-time flavor would be better.

for one-time execution, for example use

regset('US')

for persistent execution, use

regset('US',nlsocket)

where nlsocket is created with libnl.nl_socket_alloc()

NOTE:
 1) All functions (excluding wireless core related) will use a Card object
    which encapsulates the physical index, device name and interface index
    (ifindex) under a tuple rather than a device name or physical index or
    ifindex as this will not require the caller to remember if a dev or a phy
    or a ifindex is needed. The only exception to this is devinfo which by
    necessity will accept a Card or a device name
 2) All functions allow pyric errors to pass through. Callers must catch these
  if they desire

"""

__name__ = 'pyw'
__license__ = 'GPLv3'
__version__ = '0.1.5'
__date__ = 'June 2016'
__author__ = 'Dale Patterson'
__maintainer__ = 'Dale Patterson'
__email__ = 'wraith.wireless@yandex.com'
__status__ = 'Production'

import struct                                   # ioctl unpacking
import pyric                                    # pyric exception
import re                                       # check addr validity
from pyric.nlhelp.nlsearch import cmdbynum      # get command name
from pyric.utils import channels                # channel related
from pyric.utils import rfkill                  # block/unblock
import pyric.utils.hardware as hw               # device related
from pyric.utils import ouifetch                # get oui dict
import pyric.net.netlink_h as nlh               # netlink definition
import pyric.net.genetlink_h as genlh           # genetlink definition
import pyric.net.wireless.nl80211_h as nl80211h # nl80211 definition
from pyric.net.wireless import wlan             # IEEE 802.11 Std definition
import pyric.net.sockios_h as sioch             # sockios constants
import pyric.net.if_h as ifh                    # ifreq structure
import pyric.lib.libnl as nl                    # netlink functions
import pyric.lib.libio as io                    # ioctl functions

_FAM80211ID_ = None

# redefine interface types and monitor flags
IFTYPES = nl80211h.NL80211_IFTYPES
MNTRFLAGS = nl80211h.NL80211_MNTR_FLAGS
TXPWRSETTINGS = nl80211h.NL80211_TX_POWER_SETTINGS

################################################################################
#### WIRELESS CORE                                                          ####
################################################################################

def interfaces():
    """
     retrieves all network interfaces (APX ifconfig)
     :returns: a list of device names of current network interfaces cards
    """
    fin = None
    try:
        # read in devices from /proc/net/dev. After splitting on newlines, the
        # first 2 lines are headers and the last line is empty so we remove them
        fin = open(hw.dpath, 'r')
        ds = fin.read().split('\n')[2:-1]
    except IOError:
        return []
    finally:
        if fin: fin.close()

    # the remaining lines are <dev>: p1 p2 ... p3, split on ':' & strip whitespace
    return [d.split(':')[0].strip() for d in ds]

def isinterface(dev):
    """
     determines if device name belongs to a network card (APX ifconfig <dev>)
     :param dev: device name
     :returns: {True if dev is a device|False otherwise}
    """
    return dev in interfaces()

def winterfaces(*argv):
    """
     retrieve all wireless interfaces (APX iwconfig)
     :param argv: ioctl socket at argv[0] (or empty)
     :returns: list of device names of current wireless NICs
    """
    try:
        iosock = argv[0]
    except IndexError:
        return _iostub_(winterfaces)

    wifaces = []
    for dev in interfaces():
        # no errors are caught here - but allowed to pass
        if iswireless(dev, iosock): wifaces.append(dev)
    return wifaces

def iswireless(dev, *argv):
    """
     determines if given device is wireless (APX iwconfig <dev>)
     :param dev: device name
     :param argv: ioctl socket at argv[0] (or empty)
     :returns: {True:device is wireless|False:device is not wireless/not present}
    """
    try:
        iosock = argv[0]
    except IndexError:
        return _iostub_(iswireless, dev)

    try:
        # if the call succeeds, found to be wireless
        _ = io.io_transfer(iosock, sioch.SIOCGIWNAME, ifh.ifreq(dev))
        return True
    except AttributeError as e:
        raise pyric.error(pyric.EINVAL, e)
    except io.error as e:
        # ENODEV or ENOTSUPP means not wireless, reraise any others
        if e.errno == pyric.ENODEV or e.errno == pyric.EOPNOTSUPP: return False
        else: raise pyric.error(e.errno, e.strerror)

def regget(*argv):
    """
     gets the current regulatory domain (iw reg get)
     :param argv: netlink socket at argv[0] (or empty)
     :returns: the two charactor regulatory domain
    """
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(regget)

    try:
        msg = nl.nlmsg_new(nltype=_familyid_(nlsock),
                           cmd=nl80211h.NL80211_CMD_GET_REG,
                           flags=nlh.NLM_F_REQUEST | nlh.NLM_F_ACK)
        nl.nl_sendmsg(nlsock, msg)
        rmsg = nl.nl_recvmsg(nlsock)
    except nl.error as e:
        raise pyric.error(e.errno, e.strerror)
    return nl.nla_find(rmsg, nl80211h.NL80211_ATTR_REG_ALPHA2)

def regset(rd, *argv):
    """
     REQUIRES ROOT PRIVILEGES
     sets the current regulatory domain (iw reg set <rd>)
     :param rd: regulatory domain code
     :param argv: netlink socket at argv[0] (or empty)
    """
    if len(rd) != 2:
        raise pyric.error(pyric.EINVAL, "Invalid reg. domain {0}".format(rd))
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(regset, rd)

    try:
        msg = nl.nlmsg_new(nltype=_familyid_(nlsock),
                           cmd=nl80211h.NL80211_CMD_REQ_SET_REG,
                           flags=nlh.NLM_F_REQUEST | nlh.NLM_F_ACK)
        nl.nla_put_string(msg, rd.upper(), nl80211h.NL80211_ATTR_REG_ALPHA2)
        nl.nl_sendmsg(nlsock, msg)
        nl.nl_recvmsg(nlsock)
    except nl.error as e:
        raise pyric.error(e.errno, e.strerror)

################################################################################
#### CARD RELATED ####
################################################################################

class Card(tuple):
    """
     A wireless network interface controller - Wrapper around a tuple
      t = (physical index,device name, interface index)
     Exposes the following properties: (callable by '.'):
      phy: physical index
      dev: device name
      idx: interface index (ifindex)
    """
    def __new__(cls, p, d, i):
        return super(Card, cls).__new__(cls, tuple((p, d, i)))
    def __repr__(self):
        return "Card(phy={0},dev={1},ifindex={2})".format(self.phy,
                                                          self.dev,
                                                          self.idx)
    @property
    def phy(self): return self[0]
    @property
    def dev(self): return self[1]
    @property
    def idx(self): return self[2]

def getcard(dev, *argv):
    """
     get the Card object from device name
     :param dev: device name
     :returns: a Card with device name dev
    """
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(getcard, dev)

    return devinfo(dev, nlsock)['card']

def validcard(card, *argv):
    """
     determines if card is still valid i.e. another program has not changed it
     :param card: Card object
     :param argv: netlink socket at argv[0] (or empty)
     :returns: True if card is still valid, False otherwise
    """
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(validcard, card)

    try:
        return card == devinfo(card.dev, nlsock)['card']
    except pyric.error as e:
        if e.errno == pyric.ENODEV: return False
        else: raise

################################################################################
#### ADDRESS RELATED                                                        ####
################################################################################

def macget(card, *argv):
    """
     gets the interface's hw address (APX ifconfig <card.dev> | grep HWaddr)
     :param card: Card object
     :param argv: ioctl socket at argv[0] (or empty)
     :returns: device mac after operation
    """
    try:
        iosock = argv[0]
    except IndexError:
        return _iostub_(macget, card)

    try:
        flag = sioch.SIOCGIFHWADDR
        ret = io.io_transfer(iosock, flag, ifh.ifreq(card.dev, flag))
        fam = struct.unpack_from(ifh.sa_addr, ret, ifh.IFNAMELEN)[0]
        if fam in [ifh.ARPHRD_ETHER, ifh.AF_UNSPEC,ifh.ARPHRD_IEEE80211_RADIOTAP]:
            return _hex2mac_(ret[18:24])
        else:
            raise pyric.error(pyric.EAFNOSUPPORT,
                              "Invalid return hwaddr family {0}".format(fam))
    except AttributeError as e:
        raise pyric.error(pyric.EINVAL, e)
    except struct.error as e:
        raise pyric.error(pyric.EUNDEF, "Error parsing results: {0}".format(e))
    except io.error as e:
        raise pyric.error(e.errno, e.strerror)

def macset(card, mac, *argv):
    """
     REQUIRES ROOT PRIVILEGES/CARD DOWN
     set nic's hwaddr (ifconfig <card.dev> hw ether <mac>)
     :param card: Card object
     :param mac: macaddr to set
     :param argv: ioctl socket at argv[0] (or empty)
     :returns: mac address after operation
    """
    if  not _validmac_(mac): raise pyric.error(pyric.EINVAL, "Invalid mac address")

    try:
        iosock = argv[0]
    except IndexError:
        return _iostub_(macset, card, mac)

    try:
        flag = sioch.SIOCSIFHWADDR
        ret = io.io_transfer(iosock, flag, ifh.ifreq(card.dev, flag, [mac]))
        fam = struct.unpack_from(ifh.sa_addr, ret, ifh.IFNAMELEN)[0]
        if fam in [ifh.ARPHRD_ETHER, ifh.AF_UNSPEC, ifh.ARPHRD_IEEE80211_RADIOTAP]:
            return _hex2mac_(ret[18:24])
        else:

            raise pyric.error(pyric.EAFNOSUPPORT,
                              "Invalid return hwaddr family {0}".format(fam))
    except AttributeError as e:
        raise pyric.error(pyric.EINVAL, e)
    except struct.error as e:
        raise pyric.error(pyric.EUNDEF, "Error parsing results: {0}".format(e))
    except io.error as e:
        raise pyric.error(e.errno, e.strerror)

def inetget(card, *argv):
    """
     get nic's ip, netmask and broadcast addresses
     :param card: Card object
     :param argv: ioctl socket at argv[0] (or empty)
     :returns: the tuple t = (ip4,netmask,broadcast)
    """
    try:
        iosock = argv[0]
    except IndexError:
        return _iostub_(inetget, card)

    try:
        # ip
        flag = sioch.SIOCGIFADDR
        ret = io.io_transfer(iosock, flag, ifh.ifreq(card.dev, flag))
        fam = struct.unpack_from(ifh.sa_addr, ret, ifh.IFNAMELEN)[0]
        if fam == ifh.AF_INET:
            ip4 = _hex2ip4_(ret[20:24])
        else:
            raise pyric.error(pyric.EAFNOSUPPORT,
                              "Invalid return ip family {0}".format(fam))

        # netmask
        flag = sioch.SIOCGIFNETMASK
        ret = io.io_transfer(iosock, flag, ifh.ifreq(card.dev, flag))
        fam = struct.unpack_from(ifh.sa_addr, ret, ifh.IFNAMELEN)[0]
        if fam == ifh.AF_INET:
            netmask = _hex2ip4_(ret[20:24])
        else:
            raise pyric.error(pyric.EAFNOSUPPORT,
                              "Invalid return netmask family {0}".format(fam))

        # broadcast
        flag = sioch.SIOCGIFBRDADDR
        ret = io.io_transfer(iosock, flag, ifh.ifreq(card.dev, flag))
        fam = struct.unpack_from(ifh.sa_addr, ret, ifh.IFNAMELEN)[0]
        if fam == ifh.AF_INET:
            brdaddr = _hex2ip4_(ret[20:24])
        else:
            raise pyric.error(pyric.EAFNOSUPPORT,
                              "Invalid return broadcast family {0}".format(fam))
    except AttributeError as e:
        raise pyric.error(pyric.EINVAL, e)
    except struct.error as e:
        raise pyric.error(pyric.EUNDEF, "Error parsing results: {0}".format(e))
    except io.error as e:
        # catch address not available, which means the card currently does not
        # have any addresses set - raise others
        if e.errno == pyric.EADDRNOTAVAIL: return None, None, None
        raise pyric.error(e.errno, e.strerror)

    return ip4, netmask, brdaddr

def inetset(card, ipaddr, netmask, broadcast, *argv):
    """
     REQUIRES ROOT PRIVILEGES
     set nic's ip4 addr, netmask and/or broadcast
      (ifconfig <card.dev> <ipaddr> netmask <netmask> broadcast <broadcast>)
     can set ipaddr,netmask and/or broadcast to None but one or more of ipaddr,
     netmask, broadcast must be set
     :param card: Card object
     :param ipaddr: ip address to set
     :param netmask: netmask to set
     :param broadcast: broadcast to set
     :param argv: ioctl socket at argv[0] (or empty)
     NOTE:
      1) throws error if setting netmask or broadcast and card does not have
       an ip assigned
      2) if setting only the ip address, netmask and broadcast will be set
         accordingly by the kernel.
      3) If setting multiple or setting the netmask and/or broadcast after the ip
         is assigned, one can set them to erroneous values i.e. ip = 192.168.1.2
         and broadcast = 10.0.0.31.
    """
    # ensure one of params is set & that all set params are valid ip address
    if not ipaddr and not netmask and not broadcast:
        raise pyric.error(pyric.EINVAL,
                          "One of ipaddr/netmask/broadcast must be set")
    if ipaddr and not _validip4_(ipaddr):
        raise pyric.error(pyric.EINVAL, "Invalid ip4 address")
    if netmask and not _validip4_(netmask):
        raise pyric.error(pyric.EINVAL, "Invalid netmask")
    if broadcast and not _validip4_(broadcast):
        raise pyric.error(pyric.EINVAL, "Invalid broadcast")

    try:
        iosock = argv[0]
    except IndexError:
        return _iostub_(inetset, card, ipaddr, netmask, broadcast)

    # we have to do one at a time
    try:
        # ip address first
        if ipaddr: ip4set(card, ipaddr, iosock)
        if netmask: netmaskset(card, netmask, iosock)
        if broadcast: broadcastset(card, broadcast, iosock)
    except pyric.error as e:
        # an ambiguous error is thrown if attempting to set netmask or broadcast
        # without an ip address already set on the card
        if not ipaddr and e.errno == pyric.EADDRNOTAVAIL:
            raise pyric.error(pyric.EINVAL, "Set ip4 addr first")
        else:
            raise
    except AttributeError as e:
        raise pyric.error(pyric.EINVAL, e)
    except struct.error as e:
        raise pyric.error(pyric.EUNDEF, "Error parsing results: {0}".format(e))

def ip4set(card, ipaddr, *argv):
    """
     REQUIRES ROOT PRIVILEGES
     set nic's ip4 addr  (ifconfig <card.dev> <ipaddr>
     :param card: Card object
     :param ipaddr: ip address to set
     :param argv: ioctl socket at argv[0] (or empty)
     :returns: the new ip address
     NOTE: setting the ip will set netmask and broadcast accordingly
    """
    if not _validip4_(ipaddr): raise pyric.error(pyric.EINVAL, "Invalid ipaddr")

    try:
        iosock = argv[0]
    except IndexError:
        return _iostub_(ip4set, card, ipaddr)

    try:
        flag = sioch.SIOCSIFADDR
        ret = io.io_transfer(iosock, flag, ifh.ifreq(card.dev, flag, [ipaddr]))
        fam = struct.unpack_from(ifh.sa_addr, ret, ifh.IFNAMELEN)[0]
        if fam == ifh.AF_INET:
            return _hex2ip4_(ipaddr)
        else:
            raise pyric.error(pyric.EAFNOSUPPORT,
                              "Invalid return ip family {0}".format(fam))
    except AttributeError as e:
        raise pyric.error(pyric.EINVAL, e)
    except struct.error as e:
        raise pyric.error(pyric.EUNDEF, "Error parsing results: {0}".format(e))
    except io.error as e:
        raise pyric.error(e.errno, e.strerror)

def netmaskset(card, netmask, *argv):
    """
     REQUIRES ROOT PRIVILEGES
     set nic's ip4 netmask (ifconfig <card.dev> netmask <netmask>
     :param card: Card object
     :param netmask: netmask to set
     :param argv: ioctl socket at argv[0] (or empty)
     :returns: the new netmask
     NOTE:
      1) throws error if netmask is set and card does not have an ip assigned
    """
    if not _validip4_(netmask): raise pyric.error(pyric.EINVAL, "Invalid netmask")
    try:
        iosock = argv[0]
    except IndexError:
        return _iostub_(netmaskset, card, netmask)

    try:
        flag = sioch.SIOCGIFNETMASK
        ret = io.io_transfer(iosock, flag, ifh.ifreq(card.dev, flag))
        fam = struct.unpack_from(ifh.sa_addr, ret, ifh.IFNAMELEN)[0]
        if fam == ifh.AF_INET:
            return _hex2ip4_(ret[20:24])
        else:
            raise pyric.error(pyric.EAFNOSUPPORT,
                              "Invalid return netmask family {0}".format(fam))
    except AttributeError as e:
        raise pyric.error(pyric.EINVAL, e)
    except struct.error as e:
        raise pyric.error(pyric.EUNDEF, "Error parsing results: {0}".format(e))
    except io.error as e:
        # an ambiguous error is thrown if attempting to set netmask or broadcast
        # without an ip address already set on the card
        if e.errno == pyric.EADDRNOTAVAIL:
            raise pyric.error(pyric.EINVAL, "Cannot set netmask. Set ip first")
        else:
            raise pyric.error(e, e.strerror)

def broadcastset(card, broadcast, *argv):
    """
     REQUIRES ROOT PRIVILEGES
     set nic's ip4 netmask (ifconfig <card.dev> broadcast <broadcast>
     :param card: Card object
     :param broadcast: netmask to set
     :param argv: ioctl socket at argv[0] (or empty)
     :returns: the new broadcast address
     NOTE:
      1) throws error if netmask is set and card does not have an ip assigned
      2) can set broadcast to erroneous values i.e. ipaddr = 192.168.1.2 and
      broadcast = 10.0.0.31.
    """
    if not _validip4_(broadcast):  raise pyric.error(pyric.EINVAL, "Invalid bcast")

    try:
        iosock = argv[0]
    except IndexError:
        return _iostub_(broadcastset, card, broadcast)

    # we have to do one at a time
    try:
        flag = sioch.SIOCGIFBRDADDR
        ret = io.io_transfer(iosock, flag, ifh.ifreq(card.dev, flag))
        fam = struct.unpack_from(ifh.sa_addr, ret, ifh.IFNAMELEN)[0]
        if fam == ifh.AF_INET:
            return _hex2ip4_(ret[20:24])
        else:
            raise pyric.error(pyric.EAFNOSUPPORT,
                              "Invalid return broadcast family {0}".format(fam))
    except pyric.error as e:
        # an ambiguous error is thrown if attempting to set netmask or broadcast
        # without an ip address already set on the card
        if e.errno == pyric.EADDRNOTAVAIL:
            raise pyric.error(pyric.EINVAL, "Cannot set broadcast. Set ip first")
        else:
            raise
    except AttributeError as e:
        raise pyric.error(pyric.EINVAL, e)
    except struct.error as e:
        raise pyric.error(pyric.EUNDEF, "Error parsing results: {0}".format(e))
    except io.error as e:
        # an ambiguous error is thrown if attempting to set netmask or broadcast
        # without an ip address already set on the card
        if e.errno == pyric.EADDRNOTAVAIL:
            raise pyric.error(pyric.EINVAL, "Cannot set broadcast. Set ip first")
        else:
            raise pyric.error(e, e.strerror)

################################################################################
#### ON/OFF ####
################################################################################

def isup(card, *argv):
    """
     determine on/off state of card
     :param card: Card object
     :param argv: ioctl socet at argv[0] (or empty)
     :returns: True if card is up, False otherwise
    """
    try:
        iosock = argv[0]
    except IndexError:
        return _iostub_(isup, card)

    try:
        return _issetf_(_flagsget_(card.dev, iosock), ifh.IFF_UP)
    except AttributeError:
        raise pyric.error(pyric.EINVAL, "Invalid Card object")

def up(card, *argv):
    """
     REQUIRES ROOT PRIVILEGES
     turns dev on (ifconfig <card.dev> up)
     :param card: Card object
     :param argv: ioctl socket at argv[0] (or empty)
    """
    try:
        iosock = argv[0]
    except IndexError:
        return _iostub_(up, card)

    try:
        flags = _flagsget_(card.dev, iosock)
        if not _issetf_(flags, ifh.IFF_UP):
            _flagsset_(card.dev, _setf_(flags, ifh.IFF_UP), iosock)
    except AttributeError:
        raise pyric.error(pyric.EINVAL, "Invalid Card object")

def down(card, *argv):
    """
     REQUIRES ROOT PRIVILEGES
     turns def off (ifconfig <card.dev> down)
     :param card: Card object
     :param argv: ioctl socket at argv[0] (or empty)
    """
    try:
        iosock = argv[0]
    except IndexError:
        return _iostub_(down, card)

    try:
        flags = _flagsget_(card.dev, iosock)
        if _issetf_(flags, ifh.IFF_UP):
            _flagsset_(card.dev, _unsetf_(flags, ifh.IFF_UP), iosock)
    except AttributeError:
        raise pyric.error(pyric.EINVAL, "Invalid Card object")

def isblocked(card):
    """
     determines blocked state of Card
     :param card: Card object
     :returns: tuple (Soft={True if soft blocked|False otherwise},
                      Hard={True if hard blocked|False otherwise})
    """
    try:
        idx = rfkill.getidx(card.phy)
        return rfkill.soft_blocked(idx), rfkill.hard_blocked(idx)
    except AttributeError:
        raise pyric.error(pyric.ENODEV, "Device is no longer regsitered")

def block(card):
    """
     soft blocks card
     :param card: Card object
    """
    try:
        idx = rfkill.getidx(card.phy)
        rfkill.rfkill_block(idx)
    except AttributeError:
        raise pyric.error(pyric.ENODEV, "Device no longer registered")

def unblock(card):
    """
     turns off soft block
     :param card:
    """
    try:
        idx = rfkill.getidx(card.phy)
        rfkill.rfkill_unblock(idx)
    except AttributeError:
        raise pyric.error(pyric.ENODEV, "Device no longer registered")

################################################################################
#### RADIO PROPERTIES                                                       ####
################################################################################

def pwrsaveget(card, *argv):
    """
     returns card's power save state
     :param card: Card object
     :param argv: netlink socket at argv[0] (or empty)
     :returns: True if power save is on, False otherwise
    """
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(pwrsaveget, card)

    try:
        msg = nl.nlmsg_new(nltype=_familyid_(nlsock),
                           cmd=nl80211h.NL80211_CMD_GET_POWER_SAVE,
                           flags=nlh.NLM_F_REQUEST | nlh.NLM_F_ACK)
        nl.nla_put_u32(msg, card.idx, nl80211h.NL80211_ATTR_IFINDEX)
        nl.nl_sendmsg(nlsock, msg)
        rmsg = nl.nl_recvmsg(nlsock)
    except AttributeError:
        raise pyric.error(pyric.EINVAL, "Invalid Card object")
    except nl.error as e:
        raise pyric.error(e.errno, e.strerror)

    return nl.nla_find(rmsg, nl80211h.NL80211_ATTR_PS_STATE) == 1

def pwrsaveset(card, on, *argv):
    """
     REQUIRES ROOT PRIVILEGES
     sets card's power save state
     :param card: Card object
     :param on: {True = on|False = off}
     :param argv: netlink socket at argv[0] (or empty)
     sets card's power save
    """
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(pwrsaveset, card, on)

    try:
        msg = nl.nlmsg_new(nltype=_familyid_(nlsock),
                           cmd=nl80211h.NL80211_CMD_SET_POWER_SAVE,
                           flags=nlh.NLM_F_REQUEST | nlh.NLM_F_ACK)
        nl.nla_put_u32(msg, card.idx, nl80211h.NL80211_ATTR_IFINDEX)
        nl.nla_put_u32(msg, int(on), nl80211h.NL80211_ATTR_PS_STATE)
        nl.nl_sendmsg(nlsock, msg)
        _ = nl.nl_recvmsg(nlsock)
    except AttributeError:
        raise pyric.error(pyric.EINVAL, "Invalid Card object")
    except ValueError:
        raise pyric.error(pyric.EINVAL, "Invalid parameter on")
    except nl.error as e:
        raise pyric.error(e.errno, e.strerror)

def covclassget(card, *argv):
    """
     gets the coverage class value
     :param card: Card object
     :param argv: netlink socket at argv[0] (or empty)
     :returns: coverage class value
    """
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(covclassget, card)

    return phyinfo(card, nlsock)['cov_class']

def covclassset(card, cc, *argv):
    """
     REQUIRES ROOT PRIVILEGES
     sets the coverage class. The coverage class IAW IEEE Std 802.11-2012 is
     defined as the Air propagation time & together with max tx power control
     the BSS diamter
     :param card: Card object
     :param cc: coverage class 0 to 31 IAW IEEE Std 802.11-2012 Table 8-56
     :param argv: netlink socket at argv[0] (or empty)
     sets card's coverage class
    """
    if cc < wlan.COVERAGE_CLASS_MIN or cc > wlan.COVERAGE_CLASS_MAX:
        # this can work 'incorrectly' on non-int values but these will
        # be caught later during conversion
        msg = "Coverage class must be integer {0} - {1}"
        raise pyric.error(pyric.EINVAL, msg.format(wlan.COVERAGE_CLASS_MIN,
                                                   wlan.COVERAGE_CLASS_MAX))

    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(covclassset, card, cc)

    try:
        msg = nl.nlmsg_new(nltype=_familyid_(nlsock),
                           cmd=nl80211h.NL80211_CMD_SET_WIPHY,
                           flags=nlh.NLM_F_REQUEST | nlh.NLM_F_ACK)
        nl.nla_put_u32(msg, card.phy, nl80211h.NL80211_ATTR_WIPHY)
        nl.nla_put_u8(msg, int(cc), nl80211h.NL80211_ATTR_WIPHY_COVERAGE_CLASS)
        nl.nl_sendmsg(nlsock, msg)
        _ = nl.nl_recvmsg(nlsock)
    except AttributeError:
        raise pyric.error(pyric.EINVAL, "Invalid Card object")
    except ValueError:
        raise pyric.error(pyric.EINVAL, "Invalid parameter value for cc")
    except nl.error as e:
        raise pyric.error(e.errno, e.strerror)

def retryshortget(card, *argv):
    """
     gets the short retry limit.
     :param card: Card object
     :param argv: netlink socket at argv[0] (or empty)
     gets card's short retry
    """
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(retryshortget, card)

    return phyinfo(card, nlsock)['retry_short']

def retryshortset(card, lim, *argv):
    """
     REQUIRES ROOT PRIVILEGES
     sets the short retry limit.
     :param card: Card object
     :param lim: max # of short retries 1 - 255
     :param argv: netlink socket at argv[0] (or empty)
     sets card's shorty retry
    """
    if lim < wlan.RETRY_MIN or lim > wlan.RETRY_MAX:
        # this can work 'incorrectly' on non-int values but these will
        # be caught later during conversion
        msg = "Retry short must be integer {0} - {1}".format(wlan.RETRY_MIN,
                                                             wlan.RETRY_MAX)
        raise pyric.error(pyric.EINVAL, msg)

    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(retryshortset, card, lim)

    try:
        msg = nl.nlmsg_new(nltype=_familyid_(nlsock),
                           cmd=nl80211h.NL80211_CMD_SET_WIPHY,
                           flags=nlh.NLM_F_REQUEST | nlh.NLM_F_ACK)
        nl.nla_put_u32(msg, card.phy, nl80211h.NL80211_ATTR_WIPHY)
        nl.nla_put_u8(msg, int(lim), nl80211h.NL80211_ATTR_WIPHY_RETRY_SHORT)
        nl.nl_sendmsg(nlsock, msg)
        _ = nl.nl_recvmsg(nlsock)
    except AttributeError:
        raise pyric.error(pyric.EINVAL, "Invalid Card object")
    except ValueError:
        raise pyric.error(pyric.EINVAL, "Invalid parameter value for lim")
    except nl.error as e:
        raise pyric.error(e.errno, e.strerror)

def retrylongget(card, *argv):
    """
     gets the long retry limit.
     :param card: Card object
     :param argv: netlink socket at argv[0] (or empty)
     gets card's long retry
    """
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(retrylongget, card)

    return phyinfo(card, nlsock)['retry_long']

def retrylongset(card, lim, *argv):
    """
     REQUIRES ROOT PRIVILEGES
     sets the long retry limit.
     :param card: Card object
     :param lim: max # of short retries 1 - 255
     :param argv: netlink socket at argv[0] (or empty)
     sets card's long retry
    """
    if lim < wlan.RETRY_MIN or lim > wlan.RETRY_MAX:
        # this can work 'incorrectly' on non-int values but these will
        # be caught later during conversion
        msg = "Retry long must be integer {0} - {1}"
        raise pyric.error(pyric.EINVAL, msg.format(wlan.RETRY_MIN, wlan.RETRY_MAX))

    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(retrylongset, card, lim)

    try:
        msg = nl.nlmsg_new(nltype=_familyid_(nlsock),
                           cmd=nl80211h.NL80211_CMD_SET_WIPHY,
                           flags=nlh.NLM_F_REQUEST | nlh.NLM_F_ACK)
        nl.nla_put_u32(msg, card.phy, nl80211h.NL80211_ATTR_WIPHY)
        nl.nla_put_u8(msg, int(lim), nl80211h.NL80211_ATTR_WIPHY_RETRY_LONG)
        nl.nl_sendmsg(nlsock, msg)
        _ = nl.nl_recvmsg(nlsock)
    except AttributeError:
        raise pyric.error(pyric.EINVAL, "Invalid Card object")
    except ValueError:
        raise pyric.error(pyric.EINVAL, "Invalid parameter value for lim")
    except nl.error as e:
        raise pyric.error(e.errno, e.strerror)

def rtsthreshget(card, *argv):
    """
     gets RTS Threshold
     :param card: Card Object
     :param argv: netlink socket at argv[0] (or empty)
     :returns: RTS threshold
    """
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(rtsthreshget, card)

    return phyinfo(card, nlsock)['rts_thresh']

def rtsthreshset(card, thresh, *argv):
    """
     REQUIRES ROOT PRIVILEGES
     sets the RTS threshold. If off, RTS is disabled. If an integer, sets the
     smallest packet for which card will send an RTS prior to each transmission
     :param card: Card object
     :param thresh: rts threshold limit
     :param argv: netlink socket at argv[0] (or empty)
     sets the card's RTS threshold
    """
    if thresh == 'off': thresh = wlan.RTS_THRESHOLD_OFF
    elif thresh == wlan.RTS_THRESHOLD_OFF: pass
    elif thresh < wlan.RTS_THRESHOLD_MIN or thresh > wlan.RTS_THRESHOLD_MAX:
        msg = "Threshold must be 'off' or integer {0} - {1}"
        raise pyric.error(pyric.EINVAL, msg.format(wlan.RTS_THRESHOLD_MIN,
                                                   wlan.RTS_THRESHOLD_MAX))

    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(rtsthreshset, card, thresh)

    try:
        msg = nl.nlmsg_new(nltype=_familyid_(nlsock),
                           cmd=nl80211h.NL80211_CMD_SET_WIPHY,
                           flags=nlh.NLM_F_REQUEST | nlh.NLM_F_ACK)
        nl.nla_put_u32(msg, card.phy, nl80211h.NL80211_ATTR_WIPHY)
        nl.nla_put_u32(msg, thresh, nl80211h.NL80211_ATTR_WIPHY_RTS_THRESHOLD)
        nl.nl_sendmsg(nlsock, msg)
        _ = nl.nl_recvmsg(nlsock)
    except AttributeError:
        raise pyric.error(pyric.EINVAL, "Invalid Card object")
    except ValueError:
        raise pyric.error(pyric.EINVAL, "Invalid parameter value for thresh")
    except nl.error as e:
        raise pyric.error(e.errno, e.strerror)

def fragthreshget(card, *argv):
    """
     gets Fragmentation Threshold
     :param card: Card Object
     :param argv: netlink socket at argv[0] (or empty)
     :returns: RTS threshold
    """
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(fragthreshget, card)

    return phyinfo(card, nlsock)['frag_thresh']

def fragthreshset(card, thresh, *argv):
    """
     REQUIRES ROOT PRIVILEGES
     sets the Frag threshold. If off, fragmentation is disabled. If an integer,
     sets the largest packet before the card will enable fragmentation
     :param card: Card object
     :param thresh: frag threshold limit in octets
     :param argv: netlink socket at argv[0] (or empty)
     sets the card's Fragmentation threshold
    """
    if thresh == 'off': thresh = wlan.FRAG_THRESHOLD_OFF
    elif thresh == wlan.FRAG_THRESHOLD_OFF: pass
    elif thresh < wlan.FRAG_THRESHOLD_MIN or thresh > wlan.FRAG_THRESHOLD_MAX:
        msg = "Threshold must be 'off' or an integer {0} - {1}"
        raise pyric.error(pyric.EINVAL, msg.format(wlan.FRAG_THRESHOLD_MIN,
                                                   wlan.FRAG_THRESHOLD_MAX))

    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(fragthreshset, card, thresh)

    try:
        msg = nl.nlmsg_new(nltype=_familyid_(nlsock),
                           cmd=nl80211h.NL80211_CMD_SET_WIPHY,
                           flags=nlh.NLM_F_REQUEST | nlh.NLM_F_ACK)
        nl.nla_put_u32(msg, card.phy, nl80211h.NL80211_ATTR_WIPHY)
        nl.nla_put_u32(msg, thresh, nl80211h.NL80211_ATTR_WIPHY_FRAG_THRESHOLD)
        nl.nl_sendmsg(nlsock, msg)
        _ = nl.nl_recvmsg(nlsock)
    except AttributeError:
        raise pyric.error(pyric.EINVAL, "Invalid Card object")
    except nl.error as e:
        raise pyric.error(e.errno, e.strerror)

################################################################################
#### INFO RELATED                                                           ####
################################################################################

def devfreqs(card, *argv):
    """
     returns card's supported frequencies
     :param card: Card object
     :param argv: netlink socket at argv[0] (or empty)
     :returns: list of supported frequencies
    """
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(devfreqs, card)

    return phyinfo(card, nlsock)['freqs']

def devchs(card, *argv):
    """
     returns card's supported channels
     :param card: Card object
     :param argv: netlink socket at argv[0] (or empty)
     :returns: list of supported channels
    """
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(devchs, card)

    return map(channels.rf2ch, phyinfo(card, nlsock)['freqs'])

def devstds(card, *argv):
    """
     gets card's wireless standards (iwconfig <card.dev> | grep IEEE
     :param card: Card object
     :param argv: ioctl socket at argv[0] (or empty)
     :returns: list of standards (letter designators)
    """
    try:
        iosock = argv[0]
    except IndexError:
        return _iostub_(devstds, card)

    try:
        flag = sioch.SIOCGIWNAME
        ret = io.io_transfer(iosock, flag,ifh.ifreq(card.dev, flag))
        stds = ret[ifh.IFNAMELEN:]              # get the standards
        stds = stds[:stds.find('\x00')]         # remove nulls
        stds = stds.replace('IEEE 802.11', '')  # remove IEEE 802.11
        return [std for std in stds]
    except AttributeError as e:
        raise pyric.error(pyric.EINVAL, e)
    except IndexError: return None
    except struct.error as e:
        raise pyric.error(pyric.EUNDEF, "Error parsing results: {0}".format(e))
    except io.error as e:
        raise pyric.error(e.errno, e.strerror)

def devmodes(card, *argv):
    """
     gets supported modes card can operate in
     :param card: Card object
     :param argv: netlink socket at argv[0] (or empty)
     :returns: list of card's supported modes
    """
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(devmodes, card)

    return phyinfo(card, nlsock)['modes']

def devcmds(card, *argv):
    """
     get supported commands card can execute
     :param card: Card object
     :param argv: netlink socket at argv[0] (or empty)
     :returns: supported commands
    """
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(devcmds, card)

    return phyinfo(card, nlsock)['commands']

def ifinfo(card, *argv):
    """
     get info for interface (ifconfig <dev>)
     :param card: Card object
     :param argv: ioctl socket at argv[0] (or empty)
     :returns: dict with the following key:value pairs
     driver -> card's driver
     chipset -> card's chipset
     manufacturer -> card's manufacturer
     hwaddr -> card's mac address
     inet -> card's inet address
     bcast -> card's broadcast address
     mask -> card's netmask address
    """
    try:
        iosock = argv[0]
    except IndexError:
        return _iostub_(ifinfo, card)

    # get oui dict
    ouis = {}
    try:
        ouis = ouifetch.load()
    except pyric.error:
        pass

    try:
        drvr, chips = hw.ifcard(card.dev)
        mac = macget(card, iosock)
        ip4, nmask, bcast = inetget(card, iosock)
        info = {'driver':drvr, 'chipset':chips,
                'hwaddr':mac, 'manufacturer':hw.manufacturer(ouis,mac),
                'inet':ip4, 'bcast':bcast, 'mask':nmask}
    #except pyric.error # allow pyric errors to fall through
    except AttributeError:
        raise pyric.error(pyric.EINVAL, "Invalid Card object")

    return info

def devinfo(card, *argv):
    """
     get info for device (iw dev <dev> info)
     :param card: Card object or dev
     :param argv: netlink socket at argv[0] (or empty)
     :returns: dict with the following key:value pairs
      card -> Card(phy,dev,ifindex)
      mode -> i.e. monitor or managed
      wdev -> wireless device id
      mac -> hw address
      RF (if associated) -> frequency
      CF (if assoicate) -> center frequency
      CHW -> channel width i.e. NOHT,HT40- etc
    """
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(devinfo, card)

    # if we have a Card, pull out dev name, ifindex itherwise get ifindex
    try:
        dev = card.dev
        idx = card.idx
    except AttributeError:
        dev = card
        idx = _ifindex_(dev)

    try:
        msg = nl.nlmsg_new(nltype=_familyid_(nlsock),
                           cmd=nl80211h.NL80211_CMD_GET_INTERFACE,
                           flags=nlh.NLM_F_REQUEST | nlh.NLM_F_ACK)
        nl.nla_put_u32(msg, idx, nl80211h.NL80211_ATTR_IFINDEX)
        nl.nl_sendmsg(nlsock, msg)
        rmsg = nl.nl_recvmsg(nlsock)
    except nl.error as e:
        raise pyric.error(e.errno, e.strerror)

    # pull out attributes
    info = {'card':Card(nl.nla_find(rmsg, nl80211h.NL80211_ATTR_WIPHY), dev, idx),
            'mode':IFTYPES[nl.nla_find(rmsg, nl80211h.NL80211_ATTR_IFTYPE)],
            'wdev':nl.nla_find(rmsg, nl80211h.NL80211_ATTR_WDEV),
            'mac':_hex2mac_(nl.nla_find(rmsg, nl80211h.NL80211_ATTR_MAC)),
            'RF':nl.nla_find(rmsg, nl80211h.NL80211_ATTR_WIPHY_FREQ),
            'CF':nl.nla_find(rmsg, nl80211h.NL80211_ATTR_CENTER_FREQ1),
            'CHW':None}
    chw = nl.nla_find(rmsg, nl80211h.NL80211_ATTR_CHANNEL_WIDTH)
    if chw:
        try:
            info['CHW'] = channels.CHTYPES[chw]
        except IndexError:
            info['CHW'] = chw
    return info

def phyinfo(card, *argv):
    """
     get info for phy (iw phy <phy> info)
     :param card: Card
     :param argv: netlink socket at argv[0] (or empty)
     :returns: dict with the following key:value pairs
      generation -> wiphy generation
      modes -> list of supported modes
      freqs -> list of supported freqs
      scan_ssids -> max number of scan SSIDS
      retry_short -> retry short limit
      retry_long -> retry long limit
      frag_thresh -> frag threshold
      rts_thresh -> rts threshold
      cov_class -> coverage class
      swmodes -> supported software modes
      commands -> supported commands
      ciphers -> supported ciphers
    """
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(phyinfo, card)

    # iw sends @NL80211_ATTR_SPLIT_WIPHY_DUMP, we don't & get full return at once
    try:
        msg = nl.nlmsg_new(nltype=_familyid_(nlsock),
                           cmd=nl80211h.NL80211_CMD_GET_WIPHY,
                           flags=nlh.NLM_F_REQUEST | nlh.NLM_F_ACK)
        nl.nla_put_u32(msg, card.phy, nl80211h.NL80211_ATTR_WIPHY)
        nl.nl_sendmsg(nlsock, msg)
        rmsg = nl.nl_recvmsg(nlsock)
    except AttributeError:
        raise pyric.error(pyric.EINVAL, "Invalid Card object")
    except nl.error as e:
        raise pyric.error(e.errno, e.strerror)

    # pull out attributes
    info = {'generation':nl.nla_find(rmsg, nl80211h.NL80211_ATTR_GENERATION),
            'retry_short':nl.nla_find(rmsg, nl80211h.NL80211_ATTR_WIPHY_RETRY_SHORT),
            'retry_long':nl.nla_find(rmsg, nl80211h.NL80211_ATTR_WIPHY_RETRY_LONG),
            'frag_thresh':nl.nla_find(rmsg, nl80211h.NL80211_ATTR_WIPHY_FRAG_THRESHOLD),
            'rts_thresh':nl.nla_find(rmsg, nl80211h.NL80211_ATTR_WIPHY_RTS_THRESHOLD),
            'cov_class':nl.nla_find(rmsg, nl80211h.NL80211_ATTR_WIPHY_COVERAGE_CLASS),
            'scan_ssids':nl.nla_find(rmsg, nl80211h.NL80211_ATTR_MAX_NUM_SCAN_SSIDS),
            'freqs':[],
            'modes':[],
            'swmodes':[],
            'commands':[],
            'ciphers':[]}

    # modify frag_thresh and rts_thresh as necessary
    if info['frag_thresh'] >= wlan.FRAG_THRESHOLD_MAX: info['frag_thresh'] = 'off'
    if info['rts_thresh'] > wlan.RTS_THRESHOLD_MAX: info['rts_thresh'] = 'off'

    # sets or arrays of attributes
    # get freqs
    _, bs, d = nl.nla_find(rmsg, nl80211h.NL80211_ATTR_WIPHY_BANDS, False)
    if d != nlh.NLA_ERROR: info['freqs'] = _frequencies_(bs)

    # get cipher suites
    _, cs, d = nl.nla_find(rmsg, nl80211h.NL80211_ATTR_CIPHER_SUITES, False)
    if d != nlh.NLA_ERROR: info['ciphers'] = _ciphers_(cs)

    # nested attributes require additional processing. They must be unpacked
    # beg-endian and may not be processed correctly by libnl. In the event of an
    # unparsed nested attribute leave as empty list
    # get supported modes
    _, ms, d = nl.nla_find(rmsg, nl80211h.NL80211_ATTR_SUPPORTED_IFTYPES, False)
    if d != nlh.NLA_ERROR:
        info['modes'] = [_iftypes_(struct.unpack('>H', m)[0]) for m in ms]

    # get supported sw modes
    _, ms, d = nl.nla_find(rmsg, nl80211h.NL80211_ATTR_SOFTWARE_IFTYPES, False)
    if d != nlh.NLA_ERROR:
        info['swmodes'] = [_iftypes_(struct.unpack('>H', m)[0]) for m in ms]

    # get supported commands
    _, cs, d = nl.nla_find(rmsg, nl80211h.NL80211_ATTR_SUPPORTED_COMMANDS, False)
    if d != nlh.NLA_ERROR: info['commands'] = _commands_(cs)

    return info

################################################################################
#### TX/RX RELATED ####
################################################################################

def txset(card, setting, lvl, *argv):
    """
     ROOT Required
      sets cards tx power (iw phy card.<phy> <lvl> <pwr> * 100)
     :param card: Card object
     :param setting: power level setting oneof {'auto' = automatically determine
      transmit power|'limit' = limit power by <pwr>|'fixed' = set to <pwr>}
     :param lvl: desired tx power in dBm or None. NOTE: ignored if lvl is 'auto'
     :param argv: netlink socket at argv[0] (or empty)
     :returns: True on success
     NOTE: this does not work on my card(s) (nor does the corresponding iw
      command)
    """
    # sanity check on power setting and power level
    if not setting in TXPWRSETTINGS:
        raise pyric.error(pyric.EINVAL, "Invalid power setting {0}".format(setting))
    if setting != 'auto':
        if lvl is None:
            raise pyric.error(pyric.EINVAL, "Power level must be specified")

    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(txset, card, setting, lvl)

    try:
        setting = TXPWRSETTINGS.index(setting)
        msg = nl.nlmsg_new(nltype=_familyid_(nlsock),
                           cmd=nl80211h.NL80211_CMD_SET_WIPHY,
                           flags=nlh.NLM_F_REQUEST | nlh.NLM_F_ACK)
        # neither sending the phy or ifindex works
        #nl.nla_put_u32(msg, card.phy, nl80211h.NL80211_ATTR_WIPHY)
        nl.nla_put_u32(msg, card.idx, nl80211h.NL80211_ATTR_IFINDEX)
        nl.nla_put_u32(msg, setting, nl80211h.NL80211_ATTR_WIPHY_TX_POWER_SETTING)
        if setting != nl80211h.NL80211_TX_POWER_AUTOMATIC:
            nl.nla_put_u32(msg, 100*lvl, nl80211h.NL80211_ATTR_WIPHY_TX_POWER_LEVEL)
        nl.nl_sendmsg(nlsock, msg)
        nl.nl_recvmsg(nlsock)
    except ValueError:
        # only relevent when converting to mbm
        raise pyric.error(pyric.EINVAL, "Invalid txpwr {0}".format(lvl))
    except AttributeError:
        raise pyric.error(pyric.EINVAL, "Invalid Card object")
    except nl.error as e:
        raise pyric.error(e.errno, e.strerror)

def txget(card, *argv):
    """
     gets card's transmission power (iwconfig <card.dev> | grep Tx-Power)
     :param card: Card object
     :param argv: ioctl socket at argv[0] (or empty)
     :returns: transmission power in dBm
     info can be found by cat /sys/kernel/debug/ieee80211/phy<#>/power but
     how valid is it?
    """
    try:
        iosock = argv[0]
    except IndexError:
        return _iostub_(txget, card)

    try:
        flag = sioch.SIOCGIWTXPOW
        ret = io.io_transfer(iosock, flag, ifh.ifreq(card.dev, flag))
        return struct.unpack_from(ifh.ifr_iwtxpwr, ret, ifh.IFNAMELEN)[0]
    except AttributeError as e:
        raise pyric.error(pyric.EINVAL, e)
    except IndexError:
        return None
    except struct.error as e:
        raise pyric.error(pyric.EUNDEF, "Error parsing results: {0}".format(e))
    except io.error as e:
        raise pyric.error(e.errno, e.strerror)

def chget(card, *argv):
    """
     gets the current channel for device (iw dev <card.dev> info | grep channel)
     :param card: Card object
     :param argv: netlink socket at argv[0] (or empty)
     NOTE: will only work if dev is associated w/ AP or device is in monitor mode
     and has had chset previously
    """
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(chget, card)

    return channels.rf2ch(devinfo(card, nlsock)['RF'])

def chset(card, ch, chw=None, *argv):
    """
     REQUIRES ROOT PRIVILEGES
     sets current channel on device (iw phy <card.phy> set channel <ch> <chw>)
     :param card: Card object
     :param ch: channel number
     :param chw: channel width oneof {[None|'HT20'|'HT40-'|'HT40+'}
     :param argv: netlink socket at argv[0] (or empty)
     :returns: True on success
     NOTE:
      o ATT can throw a device busy for several reason. Most likely due to
      the network manager etc.
      o On my system at least (Ubuntu), creating a new dev in monitor mode and
        deleting all other existing managed interfaces allows for the new virtual
        device's channels to be changed
    """
    if ch not in channels.channels(): raise pyric.error(pyric.EINVAL, "Invalid channel")

    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(chset, card, ch, chw)

    return freqset(card, channels.ch2rf(ch), chw, nlsock)

def freqset(card, rf, chw=None, *argv):
    """
     REQUIRES ROOT PRIVILEGES
     set the frequency and width
     :param card: Card object
     :param rf: frequency
     :param chw: channel width oneof {[None|'HT20'|'HT40-'|'HT40+'}
     :param argv: netlink socket at argv[0] (or empty)
    """
    if rf not in channels.freqs(): raise pyric.error(pyric.EINVAL, "Invalid RF")
    if chw in channels.CHTYPES: chw = channels.CHTYPES.index(chw)
    else: raise pyric.error(pyric.EINVAL, "Invalid width")

    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(freqset, card, rf, chw)

    try:
        msg = nl.nlmsg_new(nltype=_familyid_(nlsock),
                           cmd=nl80211h.NL80211_CMD_SET_WIPHY,
                           flags=nlh.NLM_F_REQUEST | nlh.NLM_F_ACK)
        nl.nla_put_u32(msg, card.phy, nl80211h.NL80211_ATTR_WIPHY)
        nl.nla_put_u32(msg, rf, nl80211h.NL80211_ATTR_WIPHY_FREQ)
        nl.nla_put_u32(msg, chw, nl80211h.NL80211_ATTR_WIPHY_CHANNEL_TYPE)
        nl.nl_sendmsg(nlsock, msg)
        nl.nl_recvmsg(nlsock)
    except AttributeError:
        raise pyric.error(pyric.EINVAL, "Invalid Card object")
    except nl.error as e:
        raise pyric.error(e.errno, e.strerror)

#### INTERFACE & MODE RELATED ####

def modeget(card, *argv):
    """
     get current mode of card
     :param card: Card object
     :param argv: netlink socket at argv[0] (or empty)
     :return:
    """
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(modeget, card)

    return devinfo(card, nlsock)['mode']

def modeset(card, mode, flags=None, *argv):
    """
     REQUIRES ROOT PRIVILEGES/CARD DOWN
     sets card to mode (with optional flags if mode is monitor)
     (APX iw dev <card.dev> set type <mode> [flags])
     NOTE: as far
     :param card: Card object
     :param mode: 'name' of mode to operate in (must be one of in {'unspecified'|
     'ibss'|'managed'|'AP'|'AP VLAN'|'wds'|'monitor'|'mesh'|'p2p'}
     :param flags: list of monitor flags (can only be used if card is being set
      to monitor mode)
     :param argv: netlink socket at argv[0] (or empty)
    """
    if mode not in IFTYPES: raise pyric.error(pyric.EINVAL, 'Invalid mode')
    if flags:
        if mode != 'monitor':
            raise pyric.error(pyric.EINVAL, 'Can only set flags in monitor mode')
        for flag in flags:
            if flag not in MNTRFLAGS:
                raise pyric.error(pyric.EINVAL, 'Invalid flag: {0}'.format(flag))
    else: flags = []

    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(modeset, card, mode, flags)

    try:
        msg = nl.nlmsg_new(nltype=_familyid_(nlsock),
                           cmd=nl80211h.NL80211_CMD_SET_INTERFACE,
                           flags=nlh.NLM_F_REQUEST | nlh.NLM_F_ACK)
        nl.nla_put_u32(msg, card.idx, nl80211h.NL80211_ATTR_IFINDEX)
        nl.nla_put_u32(msg, IFTYPES.index(mode), nl80211h.NL80211_ATTR_IFTYPE)
        for flag in flags:
            nl.nla_put_u32(msg,
                           MNTRFLAGS.index(flag),
                           nl80211h.NL80211_ATTR_MNTR_FLAGS)
        nl.nl_sendmsg(nlsock, msg)
        nl.nl_recvmsg(nlsock)
    except AttributeError:
        raise pyric.error(pyric.EINVAL, "Invalid Card object")
    except nl.error as e:
        raise pyric.error(e.errno, e.strerror)

def ifaces(card, *argv):
    """
     returns all interfaces sharing the same phy as card (APX iw dev | grep phy#)
     :param card: Card object
     :param argv: netlink socket at argv[0] (or empty)
     :returns: a list of tuples t = (Card,mode) for each device having the same
      phyiscal index as that of card
    """
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(ifaces, card)

    ifs = []
    for dev in winterfaces():
        info = devinfo(dev, nlsock)
        try:
            if info['card'].phy == card.phy:
                ifs.append((info['card'], info['mode']))
        except AttributeError:
            raise pyric.error(pyric.EINVAL, "Invalid Card object")
        except nl.error as e:
            raise pyric.error(e.errno, e.strerror)
    return ifs

def devadd(card, vdev, mode, flags=None, *argv):
    """
     REQUIRES ROOT PRIVILEGES
     adds a virtual interface on device having type mode (iw phy <card.phy>
      interface add <vnic> type <mode>
     :param card: Card object or physical index
     :param vdev: device name of new interface
     :param mode: 'name' of mode to operate in (must be one of in {'unspecified'|
     'ibss'|'managed'|'AP'|'AP VLAN'|'wds'|'monitor'|'mesh'|'p2p'}
     :param flags: list of monitor flags (can only be used if creating monitor
     mode) oneof {'invalid'|'fcsfail'|'plcpfail'|'control'|'other bss'
                  |'cook'|'active'}
     :param argv: netlink socket at argv[0] (or empty)
     :returns: the new Card
    """
    if mode not in IFTYPES: raise pyric.error(pyric.EINVAL, 'Invalid mode')
    if flags:
        if mode != 'monitor':
            raise pyric.error(pyric.EINVAL, 'Can only set flags in monitor mode')
        for flag in flags:
            if flag not in MNTRFLAGS:
                raise pyric.error(pyric.EINVAL, 'Invalid flag: {0}'.format(flag))
    else: flags = []

    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(devadd, card, vdev, mode, flags)

    # if we have a Card, pull out phy index
    try:
        phy = card.phy
    except AttributeError:
        phy = card

    try:
        msg = nl.nlmsg_new(nltype=_familyid_(nlsock),
                           cmd=nl80211h.NL80211_CMD_NEW_INTERFACE,
                           flags=nlh.NLM_F_REQUEST | nlh.NLM_F_ACK)
        nl.nla_put_u32(msg, phy, nl80211h.NL80211_ATTR_WIPHY)
        nl.nla_put_string(msg, vdev, nl80211h.NL80211_ATTR_IFNAME)
        nl.nla_put_u32(msg, IFTYPES.index(mode), nl80211h.NL80211_ATTR_IFTYPE)
        for flag in flags:
            nl.nla_put_u32(msg,
                           MNTRFLAGS.index(flag),
                           nl80211h.NL80211_ATTR_MNTR_FLAGS)
        nl.nl_sendmsg(nlsock, msg)
        rmsg = nl.nl_recvmsg(nlsock) # success returns new device attributes
    except AttributeError as e:
        raise pyric.error(pyric.EINVAL, e)
    except nl.error as e:
        raise pyric.error(e.errno, e.strerror)

    return Card(card.phy, vdev, nl.nla_find(rmsg, nl80211h.NL80211_ATTR_IFINDEX))

def devdel(card, *argv):
    """
     REQUIRES ROOT PRIVILEGES
     deletes the device (dev <card.dev> del
     :param card: Card object
     :param argv: netlink socket at argv[0] (or empty)
     NOTE: the original card is no longer valid (i.e. the phy will still be present
     but the device name and ifindex are no longer 'present' in the system
    """
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(devdel, card)

    try:
        msg = nl.nlmsg_new(nltype=_familyid_(nlsock),
                           cmd=nl80211h.NL80211_CMD_DEL_INTERFACE,
                           flags=nlh.NLM_F_REQUEST | nlh.NLM_F_ACK)
        nl.nla_put_u32(msg, card.idx, nl80211h.NL80211_ATTR_IFINDEX)
        nl.nl_sendmsg(nlsock, msg)
        nl.nl_recvmsg(nlsock)
    except AttributeError:
        raise pyric.error(pyric.EINVAL, "Invalid Card object")
    except nl.error as e:
        raise pyric.error(e.errno, e.strerror)

################################################################################
#### FILE PRIVATE                                                           ####
################################################################################

def _hex2mac_(v):
    """ :returns: a ':' separated mac address from byte stream v """
    return ":".join(['{0:02x}'.format(ord(c)) for c in v])

def _hex2ip4_(v):
    """ :returns: a '.' separated ip4 address from byte stream v """
    return '.'.join([str(ord(c)) for c in v])

IPADDR = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$") # re for ip addr
MACADDR = re.compile("^([0-9a-fA-F]{2}:){5}([0-9a-fA-F]{2})$") # re for mac addr

def _validip4_(addr):
    """
     determines validity of ip4 address
     :param addr: ip addr to check
     :returns: True if addr is valid ip, False otherwise
    """
    try:
        if re.match(IPADDR, addr): return True
    except TypeError:
        return False
    return False

def _validmac_(addr):
    """
     determines validity of hw addr
     :param addr: address to check
     :returns: True if addr is valid hw address, False otherwise
    """
    try:
        if re.match(MACADDR, addr): return True
    except TypeError:
        return False
    return False

def _issetf_(flags, flag):
    """
      determines if flag is set
      :param flags: current flag value
      :param flag: flag to check
      :return: True if flag is set
     """
    return (flags & flag) == flag

def _setf_(flags, flag):
    """
     sets flag, adding to flags
     :param flags: current flag value
     :param flag: flag to set
     :return: new flag value
    """
    return flags | flag

def _unsetf_(flags, flag):
    """
     unsets flag, adding to flags
     :param flags: current flag value
     :param flag: flag to unset
     :return: new flag value
    """
    return flags & ~flag

def _flagsget_(dev, *argv):
    """
     gets the device's flags
     :param dev: device name:
     :param argv: ioctl socket at argv[0] (or empty)
     :returns: device flags
    """
    try:
        iosock = argv[0]
    except IndexError:
        return _iostub_(_flagsget_, dev)

    try:
        flag = sioch.SIOCGIFFLAGS
        ret = io.io_transfer(iosock, flag, ifh.ifreq(dev, flag))
        return struct.unpack_from(ifh.ifr_flags, ret, ifh.IFNAMELEN)[0]
    except AttributeError as e:
        raise pyric.error(pyric.EINVAL, e)
    except struct.error as e:
        raise pyric.error(pyric.EUNDEF, "Error parsing results: {0}".format(e))
    except io.error as e:
        raise pyric.error(e.errno, e.strerror)

def _flagsset_(dev, flags, *argv):
    """
     gets the device's flags
     :param dev: device name:
     :param flags: flags to set
     :param argv: ioctl socket at argv[0] (or empty)
     :returns: device flags after operation
    """
    try:
        iosock = argv[0]
    except IndexError:
        return _iostub_(_flagsset_, dev, flags)

    try:
        flag = sioch.SIOCSIFFLAGS
        ret = io.io_transfer(iosock, flag, ifh.ifreq(dev, flag, [flags]))
        return struct.unpack_from(ifh.ifr_flags, ret, ifh.IFNAMELEN)[0]
    except AttributeError as e:
        raise pyric.error(pyric.EINVAL, e)
    except struct.error as e:
        raise pyric.error(pyric.EUNDEF, "Error parsing results: {0}".format(e))
    except io.error as e:
        raise pyric.error(e.errno, e.strerror)

#### ADDITIONAL PARSING FOR PHYINFO ####

def _iftypes_(i):
    """
     wraps the IFTYPES list to handle index errors
     :param i:
     :returns: the string IFTYPE corresponding to i
    """
    try:
        return IFTYPES[i]
    except IndexError:
        return "Unknown mode ({0})".format(i)

def _frequencies_(band):
    """
     extract list of supported freqs packed byte stream band
     :param band: packed byte string from NL80211_ATTR_WIPHY_BANDS
     :returns: list of supported frequencies
    """
    rfs = []
    for freq in channels.freqs():
        if band.find(struct.pack("I", freq)) != -1:
            rfs.append(freq)
    return rfs

def _commands_(command):
    """
     converts numeric commands to string version
     :param command: list of command constants
     :returns: list of supported commands as strings
    """
    cs = []
    for cmd in command:
        try:
            # convert the numeric command to the form @NL80211_CMD_<CMD>
            # Some numeric commands may have multiple string synonyms, in
            # that case, take the first one. Finally, strip off @NL80211_CMD_
            # to get only the command name and make it lowercase
            cmd = cmdbynum(struct.unpack_from('>HH', cmd, 0)[1])
            if type(cmd) is type([]): cmd = cmd[0]
            cs.append(cmd[13:].lower()) # skip NL80211_CMD_
        except KeyError:
            # kernel 4 added commands not found in kernel 3 nlh8022.h.
            # keep this just in case new commands pop up again
            cs.append("unknown cmd ({0})".format(cmd))
    return cs

def _ciphers_(cipher):
    """
     identifies supported ciphers
     :param cipher: the cipher suite stream
     :returns: a list of supported ciphers
    """
    ss = []
    for s in cipher:
        try:
            ss.append(wlan.WLAN_CIPHER_SUITE_SELECTORS[s])
        except KeyError as e:
            # we could do nothing, or append 'rsrv' but we'll add a little
            # for testing/future identificaion purposes
            ss.append('RSRV-{0}'.format(hex(int(e.__str__()))))
    return ss

#### NETLINK/IOCTL PARAMETERS ####

def _ifindex_(dev, *argv):
    """
     gets the ifindex for device
     :param dev: device name:
     :param argv: ioctl socket at argv[0] (or empty)
     :returns: ifindex of device
     NOTE: the ifindex can aslo be found in /sys/class/net/<nic>/ifindex
    """
    try:
        iosock = argv[0]
    except IndexError:
        return _iostub_(_ifindex_, dev)

    try:
        flag = sioch.SIOCGIFINDEX
        ret = io.io_transfer(iosock, flag, ifh.ifreq(dev, flag))
        return struct.unpack_from(ifh.ifr_ifindex, ret, ifh.IFNAMELEN)[0]
    except AttributeError as e:
        raise pyric.error(pyric.EINVAL, e)
    except struct.error as e:
        raise pyric.error(pyric.EUNDEF, "Error parsing results: {0}".format(e))
    except io.error as e:
        raise pyric.error(e.errno, e.strerror)

def _familyid_(nlsock):
    """
     extended version: get the family id
     :param nlsock: netlink socket
     :returns: the family id of nl80211
     NOTE:
      In addition to the family id, we get:
       CTRL_ATTR_FAMILY_NAME = nl80211\x00
       CTRL_ATTR_VERSION = \x01\x00\x00\x00 = 1
       CTRL_ATTR_HDRSIZE = \x00\x00\x00\x00 = 0
       CTRL_ATTR_MAXATTR = \xbf\x00\x00\x00 = 191
       CTRL_ATTR_OPS
       CTRL_ATTR_MCAST_GROUPS
      but for now, these are not used
    """
    global _FAM80211ID_
    if _FAM80211ID_ is None:
        # family id is not instantiated, do so now
        msg = nl.nlmsg_new(nltype=genlh.GENL_ID_CTRL,
                           cmd=genlh.CTRL_CMD_GETFAMILY,
                           flags=nlh.NLM_F_REQUEST | nlh.NLM_F_ACK)
        nl.nla_put_string(msg, nl80211h.NL80211_GENL_NAME,
                          genlh.CTRL_ATTR_FAMILY_NAME)
        nl.nl_sendmsg(nlsock, msg)
        rmsg = nl.nl_recvmsg(nlsock)
        _FAM80211ID_ = nl.nla_find(rmsg, genlh.CTRL_ATTR_FAMILY_ID)
    return _FAM80211ID_

#### TRANSLATION FUNCTIONS ####

def _iostub_(fct, *argv):
    """
     translates from traditional ioctl <cmd> to extended <cmd>ex
     :param fct: function to translate to
     :param argv: parameters to the function
     :returns: the results of fct
    """
    iosock = io.io_socket_alloc()
    try:
        argv = list(argv) + [iosock]
        return fct(*argv)
    except pyric.error:
        raise # catch and rethrow
    finally:
        io.io_socket_free(iosock)

def _nlstub_(fct, *argv):
    """
     translates from traditional netlink <cmd> to extended <cmd>ex
     :param fct: function to translate to
     :param argv: parameters to the function
     :returns: rresults of fucntion
    """
    nlsock = None
    try:
        nlsock = nl.nl_socket_alloc(timeout=2)
        argv = list(argv) + [nlsock]
        return fct(*argv)
    except pyric.error:
        raise
    finally:
        if nlsock: nl.nl_socket_free(nlsock)

#### PENDING ####

def _fut_chset(card, ch, chw, *argv):
    """
     set current channel on device (iw phy <card.phy> set channel <ch> <chw>
     :param card: Card object
     :param ch: channel number
     :param chw: channel width oneof {None|'HT20'|'HT40-'|'HT40+'}
     :param argv: netlink socket at argv[0] (or empty)
     uses the newer NL80211_CMD_SET_CHANNEL vice iw's depecrated version which
     uses *_SET_WIPHY however, ATT does not work raise Errno 22 Invalid Argument
     NOTE: This only works for cards in monitor mode
    """
    if ch not in channels.channels(): raise pyric.error(pyric.EINVAL, "Invalid channel")
    if chw not in channels.CHTYPES: raise pyric.error(pyric.EINVAL, "Invalid channel width")
    try:
        nlsock = argv[0]
    except IndexError:
        return _nlstub_(_fut_chset, card, ch, chw)

    msg = nl.nlmsg_new(nltype=_familyid_(nlsock),
                       cmd=nl80211h.NL80211_CMD_SET_CHANNEL,
                       flags=nlh.NLM_F_REQUEST | nlh.NLM_F_ACK)
    nl.nla_put_u32(msg, card.idx, nl80211h.NL80211_ATTR_IFINDEX)
    nl.nla_put_u32(msg, channels.ch2rf(ch), nl80211h.NL80211_ATTR_WIPHY_FREQ)
    nl.nla_put_u32(msg, channels.CHTYPES.index(chw), nl80211h.NL80211_ATTR_WIPHY_CHANNEL_TYPE)
    nl.nl_sendmsg(nlsock, msg)
    nl.nl_recvmsg(nlsock)