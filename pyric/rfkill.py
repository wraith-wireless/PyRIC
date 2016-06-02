#!/usr/bin/env python
""" rfkill.py: rfkill port

/usr/include/linux
/*
 * Copyright (C) 2006 - 2007 Ivo van Doorn
 * Copyright (C) 2007 Dmitry Torokhov
 * Copyright 2009 Johannes Berg <johannes@sipsolutions.net>
 *
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 * ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 * OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 */

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

Implements userspace program rfkill in Python to query the state of rfkill switches

NOTE:
 o rfkill_block will block all devices regardless of index, however, the blocked
  state will only shown in device that was submitted for blocking - this is the
  same behavior seen in rfkill block <idx>
  - this may be due to bug in ubuntu and not present in other distros
 o rfkill does not do sanity checks on the index, rfkill.py will through error
  if the index does not exist
"""

"""
 rfkill writes and reads rfkill_event structures to /dev/rfkill using fcntl
 Results and useful information can be found in /sys/class/rfkill which contains
 one or more rfkill<n> directories where n is the index of each 'wireless'
 device. In each rfkill<n> are several files some of which are:
  o type: type of device i.e. wlan, bluetooth etc
  o name: in the case of 802.11 cards this is the physical name
"""
dpath = '/dev/rfkill'
spath = '/sys/class/rfkill'

__name__ = 'rfkill'
__license__ = 'GPLv3'
__version__ = '0.0.1'
__date__ = 'June 2016'
__author__ = 'Dale Patterson'
__maintainer__ = 'Dale Patterson'
__email__ = 'wraith.wireless@yandex.com'
__status__ = 'Production'

import os
import struct
import fcntl
import pyric
import errno

RFKILL_STATE_SOFT_BLOCKED = 0
RFKILL_STATE_UNBLOCKED    = 1
RFKILL_STATE_HARD_BLOCKED = 2

"""
/**
 * enum rfkill_type - type of rfkill switch.
 *
 * @RFKILL_TYPE_ALL: toggles all switches (requests only - not a switch type)
 * @RFKILL_TYPE_WLAN: switch is on a 802.11 wireless network device.
 * @RFKILL_TYPE_BLUETOOTH: switch is on a bluetooth device.
 * @RFKILL_TYPE_UWB: switch is on a ultra wideband device.
 * @RFKILL_TYPE_WIMAX: switch is on a WiMAX device.
 * @RFKILL_TYPE_WWAN: switch is on a wireless WAN device.
 * @RFKILL_TYPE_GPS: switch is on a GPS device.
 * @RFKILL_TYPE_FM: switch is on a FM radio device.
 * @RFKILL_TYPE_NFC: switch is on an NFC device.
 * @NUM_RFKILL_TYPES: number of defined rfkill types
 */
"""
RFKILL_TYPES = ['all','wlan','bluetooth','uwb','wimax','wwan','gps','fm','nfc']
RFKILL_TYPE_ALL       = 0
RFKILL_TYPE_WLAN      = 1
RFKILL_TYPE_BLUETOOTH = 2
RFKILL_TYPE_UWB       = 3
RFKILL_TYPE_WIMAX     = 4
RFKILL_TYPE_WWAN      = 5
RFKILL_TYPE_GPS       = 6
RFKILL_TYPE_FM        = 7
RFKILL_TYPE_NFC       = 8
NUM_RFKILL_TYPES      = 9

"""
/**
 * enum rfkill_operation - operation types
 * @RFKILL_OP_ADD: a device was added
 * @RFKILL_OP_DEL: a device was removed
 * @RFKILL_OP_CHANGE: a device's state changed -- userspace changes one device
 * @RFKILL_OP_CHANGE_ALL: userspace changes all devices (of a type, or all)
 */
 """
RFKILL_OP_ADD        = 0
RFKILL_OP_DEL        = 1
RFKILL_OP_CHANGE     = 2
RFKILL_OP_CHANGE_ALL = 3

"""
/**
 * struct rfkill_event - events for userspace on /dev/rfkill
 * @idx: index of dev rfkill
 * @type: type of the rfkill struct
 * @op: operation code
 * @hard: hard state (0/1)
 * @soft: soft state (0/1)
 *
 * Structure used for userspace communication on /dev/rfkill,
 * used for events from the kernel and control to the kernel.
 */
"""
rfk_rfkill_event = "IBBBB"
RFKILLEVENTLEN = struct.calcsize(rfk_rfkill_event)
def rfkill_event(idx,rtype,op,hard=0,soft=0):
    """
     create a rkfill event structure
     :param idx: index of dev rfkill i.e. 0,1
     :param rtype: type of rfkill
     :param op: op code
     :param hard: hard state one of {0=unbloacked|1=blocked}
     :param soft: soft state one of {0=unblocked|1=blocked}
     :returns: a rfkill event structure
    """
    return struct.pack(rfk_rfkill_event,idx,rtype,op,hard,soft)

def rfkill_list():
    """
     list rfkill event structures (rfkill list)
     :returns: a dict of dicts name -> {idx,type,soft,hard}
    """
    rfks = {}
    fin = open(dpath,'r')
    flags = fcntl.fcntl(fin.fileno(),fcntl.F_GETFL)
    fcntl.fcntl(fin.fileno(),fcntl.F_SETFL,flags|os.O_NONBLOCK)
    while True:
        try:
            idx,t,op,s,h = struct.unpack(rfk_rfkill_event,fin.read(RFKILLEVENTLEN))
            if op == RFKILL_OP_ADD:
                rfks[getname(idx)] = {'idx':idx,
                                      'type':RFKILL_TYPES[t],
                                      'soft':s,
                                      'hard':h}
        except IOError:
            break
    fin.close()
    return rfks

def rfkill_block(idx):
    """
     blocks the device at index
     :param idx: rkill index
    """
    if not os.path.exists(os.path.join(spath,"rfkill{0}".format(idx))):
        raise pyric.error(errno.ENODEV,"No device at {0}".format(idx))
    fout = None
    try:
        rfke = rfkill_event(idx,RFKILL_TYPE_ALL,RFKILL_OP_CHANGE,1,0)
        fout = open(dpath, 'w')
        fout.write(rfke)
    except struct.error as e:
        raise pyric.error(pyric.EUNDEF,"Error packing rfkill event {0}".format(e))
    except IOError as e:
        raise pyric.error(e.errno,e.message)
    finally:
        if fout: fout.close()

def rfkill_blockby(rtype):
    """
     blocks the device of type
     :param rtype: rfkill type one of {'all'|'wlan'|'bluetooth'|'uwb'|'wimax'
      |'wwan'|'gps'|'fm'|'nfc'}
    """
    rfks = rfkill_list()
    for name in rfks:
        if rfks[name]['type'] == rtype:
            rfkill_block(rfks[name]['idx'])

def rfkill_unblock(idx):
    """
     unblocks the device at index
     :param idx: rkill index
    """
    if not os.path.exists(os.path.join(spath, "rfkill{0}".format(idx))):
        raise pyric.error(errno.ENODEV, "No device at {0}".format(idx))
    fout = None
    try:
        rfke = rfkill_event(idx,RFKILL_TYPE_ALL,RFKILL_OP_CHANGE,0,0)
        fout = open(dpath, 'w')
        fout.write(rfke)
    except struct.error as e:
        raise pyric.error(pyric.EUNDEF,"Error packing rfkill event {0}".format(e))
    except IOError as e:
        raise pyric.error(e.errno,e.message)
    finally:
        if fout: fout.close()

def rfkill_unblockby(rtype):
    """
     unblocks the device of type
     :param rtype: rfkill type one of {'all'|'wlan'|'bluetooth'|'uwb'|'wimax'
      |'wwan'|'gps'|'fm'|'nfc'}
    """
    if rtype not in RFKILL_TYPES:
        raise pyric.error(errno.EINVAL,"Type {0} is not valid".format(rtype))
    rfks = rfkill_list()
    for name in rfks:
        if rfks[name]['type'] == rtype:
            rfkill_unblock(rfks[name]['idx'])

def soft_blocked(idx):
    """
     determines soft block state of device
     :param idx: rkill index
     :returns: True if device at idx is soft blocked, False otherwise
    """
    if not os.path.exists(os.path.join(spath,"rfkill{0}".format(idx))):
        raise pyric.error(errno.ENODEV,"No device at {0}".format(idx))
    fin = None
    try:
        fin = open(os.path.join(spath,"rfkill{0}".format(idx),'soft'),'r')
        return int(fin.read().strip()) == 1
    except IOError:
        raise pyric.error(errno.ENODEV,"No device at {0}".format(idx))
    except ValueError:
        raise pyric.error(pyric.EUNDEF,"Unexpected error")
    finally:
        if fin: fin.close()

def hard_blocked(idx):
    """
     determines hard block state of device
     :param idx: rkill index
     :returns: True if device at idx is hard blocked, False otherwise
    """
    if not os.path.exists(os.path.join(spath,"rfkill{0}".format(idx))):
        raise pyric.error(errno.ENODEV,"No device at {0}".format(idx))
    fin = None
    try:
        fin = open(os.path.join(spath,"rfkill{0}".format(idx),'hard'),'r')
        return int(fin.read().strip()) == 1
    except IOError:
        raise pyric.error(errno.ENODEV,"No device at {0}".format(idx))
    except ValueError:
        raise pyric.error(pyric.EUNDEF,"Unexpected error")
    finally:
        if fin: fin.close()

def getidx(phy):
    """
     returns the rfkill index associated with the physical index
     :param phy: phyiscal index
     :returns: the rfkill index
    """
    phy = "phy{0}".format(phy)
    rfks = rfkill_list()
    try:
        return rfks["phy{0}".format(phy)]['idx']
    except KeyError:
        return None

def getname(idx):
    """
     returns the phyical name of the device
     :param idx: rfkill index
     :returns: the name of the device
    """
    fin = None
    try:
        fin = open(os.path.join(spath,"rfkill{0}".format(idx),'name'),'r')
        return fin.read().strip()
    except IOError:
        raise pyric.error(errno.EINVAL,"No device at {0}".format(idx))
    finally:
        if fin: fin.close()

def gettype(idx):
    """
     returns the type of the device
     :param idx: rfkill index
     :returns: the type of the device
    """
    fin = None
    try:
        fin = open(os.path.join(spath,"rfkill{0}".format(idx),'type'),'r')
        return fin.read().strip()
    except IOError:
        raise pyric.error(errno.ENODEV,"No device at {0}".format(idx))
    finally:
        if fin: fin.close()