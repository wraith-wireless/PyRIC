#!/usr/bin/env python
""" info.py

Example for displaying device details

"""

import argparse as ap
import sys
import pyric                           # pyric error (and ecode EUNDEF)
from pyric import pyw                  # for iw functionality
from pyric.utils.channels import rf2ch # rf to channel conversion

def execute(dev,itype):
    # ensure dev is a wireless interfaces
    wifaces = pyw.winterfaces()
    if dev not in wifaces:
        print "Device {0} is not wireless, use one of {1}".format(dev,wifaces)

    # get info dicts
    dinfo = pyw.devinfo(dev)
    card = dinfo['card']
    pinfo = pyw.phyinfo(card)
    iinfo = pyw.ifinfo(card)

    if itype == 'all' or itype == 'if':
        msg = "Interface {0}\n".format(card.idx)
        msg += "\tDriver: {0} Chipset: {1}\n".format(iinfo['driver'],iinfo['chipset'])
        msg += "\tHW Addr: {0} Manufacturer: {1}\n".format(iinfo['hwaddr'],
                                                           iinfo['manufacturer'])
        msg += "\tInet: {0} Bcast: {1} Mask: {2}\n".format(iinfo['inet'],
                                                           iinfo['bcast'],
                                                           iinfo['mask'])
        print msg

    if itype == 'all' or itype == 'dev':
        msg = "Device {0}\n".format(card.dev)
        msg += "\tifindex: {0}\n".format(card.idx)
        msg += "\twdev: {0}\n".format(dinfo['wdev'])
        msg += "\taddr: {0}\n".format(dinfo['mac'])
        msg += "\tmode: {0}\n".format(dinfo['mode'])
        msg += "\twiphy: {0}\n".format(card.phy)
        if dinfo['mode'] != 'managed': msg += "\tDevice not associated\n"
        else:
            msg += "\tchannel: {0} ({1} MHz), width: {2}, CF: {3} MHz\n".format(rf2ch(dinfo['RF']),
                                                                                dinfo['RF'],
                                                                                dinfo['CHW'],
                                                                                dinfo['CF'])
        print msg

    if itype == 'all' or itype == 'phy':
        msg = "Wiphy phy{0}\n".format(card.phy)
        msg += "\tGeneration: {0}m Coverage Class: {1}\n".format(pinfo['generation'],
                                                                 pinfo['cov_class'])
        msg += "\tMax # scan SSIDs: {0}\n".format(pinfo['scan_ssids'])
        msg += "\tRetry Short: {0}, Long: {1}\n".format(pinfo['retry_short'],
                                                        pinfo['retry_long'])
        msg += "\tThreshold Frag: {0}, RTS: {1}\n".format(pinfo['frag_thresh'],
                                                          pinfo['rts_thresh'])
        msg += "\tSupported Modes:\n"
        for mode in pinfo['modes']: msg += "\t  * {0}\n".format(mode)
        msg += "\tSupported Commands:\n"
        for cmd in pinfo['commands']: msg += "\t  * {0}\n".format(cmd)
        msg += "\tSupported Frequencies:\n"
        for rf in pinfo['freqs']: msg += "\t * {0} ({1})\n".format(rf,rf2ch(rf))
        msg += "\tSupported Ciphers:\n"
        for cipher in pinfo['ciphers']: msg += "\t  * {0}\n".format(cipher)

        print msg

if __name__ == '__main__':
    # create arg parser and parse command line args
    print "Wireless Device Info Display using PyRIC v{0}".format(pyric.__version__)
    argp = ap.ArgumentParser(description="Wireless Device Data")
    argp.add_argument('-d','--dev',help="Wireless Device")
    argp.add_argument('-t','--type',help="Info type one of {all|if|dev|phy}")
    args = argp.parse_args()
    try:
        dname = args.dev
        infotype = args.type
        if dname is None:
            print "usage: python details.py -d <dev> [-t <itype>]"
            sys.exit(0)
        if infotype is None: infotype = 'all'
        if infotype not in ['all','if','dev','phy']:
            print "usage: python details.py -d <dev> [-t one of {all|if|dev|phy}]"
            sys.exit(0)
        execute(dname,infotype)
    except pyric.error as e:
        print e