#!/usr/bin/env python
""" details.py

Example for displaying device details

"""

import argparse as ap
import pyric                           # pyric error (and ecode EUNDEF)
from pyric import pyw                  # for iw functionality
import pyric.utils.hardware as hw      # for chipset/driver
from pyric.utils.channels import rf2ch # rf to channel conversion

def execute(dev):
    # ensure dev is a wireless interfaces
    wifaces = pyw.winterfaces()
    if dev not in wifaces:
        print "Device {0} is not wireless, use one of {1}".format(dev,wifaces)

    dinfo = pyw.devinfo(dev)
    card = dinfo['card']
    pinfo = pyw.phyinfo(card)
    driver = hw.ifdriver(card.dev)
    chipset = hw.ifchipset(driver)
    manuf = hw.manufacturer(hw.parseoui(),dinfo['mac'])

    msg = "Device {0}\n".format(dev)
    msg += "\tDriver: {0} Chipset: {1}\n".format(driver,chipset)
    msg += "\tManufacturer: {0}\n".format(manuf)
    msg += "\tifindex: {0}\n".format(card.idx)
    msg += "\twdev: {0}\n".format(dinfo['wdev'])
    msg += "\taddr: {0}\n".format(dinfo['mac'])
    msg += "\tmode: {0}\n".format(dinfo['mode'])
    msg += "\twiphy: {0}\n".format(card.phy)
    if dinfo['mode'] == 'managed':
        msg += "\tchannel: {0} ({1} MHz), width: {2}, CF: {3}\n".format(rf2ch(dinfo['RF']),
                                                                      dinfo['RF'],
                                                                      dinfo['CHW'],
                                                                      dinfo['CF'])
    else:
        msg += "\tDevice not associated\n"
    print msg

    msg = "Wiphy phy{0}\n".format(card.phy)
    msg += "\tGeneration: {0}m Coverage Class: {1}\n".format(pinfo['generation'],
                                                             pinfo['cov_class'])
    msg += "\tMax # scan SSIDs: {0}\n".format(pinfo['scan_ssids'])
    msg += "\tRetry Short: {0}, Long: {1}\n".format(pinfo['retry_short'],
                                                    pinfo['retry_long'])
    msg += "\tThreshold Frag: {0}, RTS: {1}\n".format(pinfo['frag_thresh'],
                                                      pinfo['rts_thresh'])
    msg += "\tSupported Modes:\n"
    for mode in pinfo['modes']:
        msg += "\t  * {0}\n".format(mode)
    msg += "\tSupported Commands:\n"
    for cmd in pinfo['commands']:
        msg += "\t  * {0}\n".format(cmd)
    msg += "\tSupported Channels:\n"
    for ch in map(rf2ch,pinfo['freqs']):
        msg += "\t  * {0}\n".format(ch)

    print msg

if __name__ == '__main__':
    # create arg parser and parse command line args
    print "Wireless Device Info Display using PyRIC v{0}".format(pyric.__version__)
    argp = ap.ArgumentParser(description="Wireless Device Data")
    argp.add_argument('-d','--dev',help="Wireless Device")
    args = argp.parse_args()
    try:
        dev = args.dev
        if dev is None:
            print "usage: python details.py -d <dev>"
        else:
            execute(dev)
    except pyric.error as e:
        print e