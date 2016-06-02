# PyRIC: Python Radio Interface Controller
## Pythonic iw (and more) for the Wireless Pentester

[![License: GPLv3](https://img.shields.io/pypi/l/PyRIC.svg)](https://github.com/wraith-wireless/PyRIC/blob/master/LICENSE)
[![Current version at PyPI](https://img.shields.io/pypi/v/PyRIC.svg)](https://pypi.python.org/pypi/PyRIC)
[![Downloads per month on PyPI](https://img.shields.io/pypi/dm/PyRIC.svg)](https://pypi.python.org/pypi/PyRIC)
![Supported Python Versions](https://img.shields.io/pypi/pyversions/PyRIC.svg)
![Software status](https://img.shields.io/pypi/status/PyRIC.svg)

## 1 DESCRIPTION:
BLUF: Why use subprocess.Popen, regular expressions and str.find to interact
with your Wireless Network Interface Card. PyRIC provides the ability to
manipulate, identify and enumerate your system's wireless cards. It is a pure
python port of a subset of the functionality provided by iw, ifconfig and iwconfig.
PyRIC is:
* Pythonic: No ctypes, SWIG etc. PyRIC redefines C header files as Python and
uses netlink (or ioctl) sockets to communicate directly with the kernel.
* Self-sufficient: No third-party files used, PyRIC is completely self-contained
* Fast: (relatively speaking) PyRIC is faster than using iw through subprocess.Popen
* Small: PyRIC is roughly 420kB
* Parseless: Get the output you want without parsing output from iw. Never worry
about iw updates and rewriting your parsers.
* Easy: If you can use iw, you can use PyRIC

PyRIC is primarliy and originally a port of a subset of iw but has evolved in
an attempt to meet the needs of wireless pentesting as it relates to wireless
network cards. In addition to providing iw related functions, PyRIC implements:
* ifconfig functionality such as mac address, ip address, netmask and broadcast
setting and getting
* rfkill list, block and unblock

### a. Background
PyRIC arose out of a need in Wraith (https://github.com/wraith-wireless/wraith)
for Python nl80211/netlink and ioctl functionality. Originally, Wraith used
ifconfig, iwconfig and iw via subprocess.Popen and parsed the output. There
are obvious shortfalls with this method, especially in terms of iw that is
actively changing (revisions break the parser) and I started looking for an
open source alternative. There are several open source projects out there
such as pyroute, pymnl (and the python files included in the libnl source) but
they generally have either not been maintained recently or come with warnings.
I desired a simple interface to the underlying nl80211 kernel support that
handles the complex operations of netlink seamlessy while maintaining a minimum
of "code walking" to understand, modify and extend. I decided to write my own
because I do not need complete netlink functionality, only that provided by
generic netlink and within the nl80221 family. Additionally, for Wraith, I do
not need a full blown port of iw et. al. functionality to Python but only
require the ability to turn a wireless nic on/off, get/set the hwaddr, get/set
the channel, determine some properties of the card and add/delete interfaces.

So, why did I do this and why is it done "this" way? When I first started to
explore the idea of moving away from iw output parsing, I looked at the source
for iw, and existing Python ports. Just to figure out how to get the family id
for nl80211 required reading through five different source files with no
comments. To that extent, I have attempted to keep subclassing to a minimum,
the total number of classes to a minimum, combine files where possible and where
it makes since and keep the number of files required to be open simulateneously
in order to understand the methodology and follow the program to a minimum. One
can understand the PyRIC program flow with only two files open at any time namely,
pyw and libnl. In fact, only an understanding of pyw is required to add additional
commands although an understanding of libnl(.py) is helpful especially, if for
example, the code is to be extended to handle multicast or callbacks.

### b. Additions to iw
Several "extensions" have been added to iw:
* Persistent sockets: pyw provides the caller with functions & ability to pass
their own netlink (or ioctl socket) to pyw functions;
* One-time request for the nl80211 family id: pyw stores the family id in a
global variable
* Consolidating different "reference" values to wireless NICs in one class
(Cards are tuples t=(dev,phy #,ifindex)

These are minimal changes but they can improve the performance of any progams
that needs to access the wireless nic repeatedly as shown in the table below.

| chset      | Total    | Avg    | Longest   | Shortest |
|------------|----------|--------|-----------|----------|
| Popen(iw)  | 588.3059 | 0.0588 | 0.0682    | 0.0021   |
| one-time   | 560.3559 | 0.0560 | 0.0645    | 0.0003   |
| persistent | 257.8293 | 0.0257 | 0.0354    | 0.0004   |

The table shows benchmarks for hop time on a Alfa AWUS036NH 10000 times. Note that
there is no implication that PyRIC is faster than iw. Rather, the table shows that
PyRIC is faster than using Popen to execute iw. Using one-time sockets, there is
a difference of 28 seconds over Popen and iw with a small decrease in the average
hoptime. Not a big difference. However, the performance increased dramatically when
persistent netlink sockets are used with the total time and average hop time nearly
halved.

### c. Current State
ATT, PyRIC accomplishes my core needs but it is still a work in progress. It
currently provides the following:
* enumerate interfaces and wireless interfaces
* identify a cards chipset and driver
* get/set hardware address
* get/set ip4 address, netmask and or broadcast
* turn card on/off
* get supported standards
* get supported commands
* get supported modes
* get dev info
* get phy info
* get/set regulatory domain
* get/set mode
* add/delete interfaces
* enumerate ISM and UNII channels
* block/unblock rfkill devices

It also provides limited help functionality concerning nl80211 commands/attributes
(for those who wish to add additional commands). However, it pulls directly from
the nl80211 header file and may be vague.

### d. What is PyRIC?

To avoid confusion, PyRIC is the system as a whole, including all header files
and "libraries" that are required to communicate with the kernel. pyw is a
interface to these libraries providing specific funtions.

What it does - defines programmatic access to a subset of iw, ifconfig and iwconfig.
In short, PyRIC provides Python wireless pentesters the ability to work with
wireless cards directly from Python without having to use command line tools
through Popen.

## 2. INSTALLING/USING:

Starting with version 0.0.6, the structure (see Section 4) has changed to facilitate
packaging on PyPI. This restructing has of course led to some minor difficulties
especially when attempting to install (or even just test) outside of a pip
installation.

### a. Requirements
PyRIC has only two requirements: Linux and Python. There has been very little
testing (on my side) on kernel 4.x and Python 3 but unit testing confirms
functionality on Python 2.7 and kernel 3.13.x.

### b. Install from Package Manager
Obviously, the easiest way to install PyRIC is through PyPI:

    sudo pip install PyRIC

### c. Install from Source
The PyRIC source (tarball) can be downloaded from https://pypi.python.org/pypi/PyRIC
or http://wraith-wireless.github.io/PyRIC. Additionally, the source, as a zip file,
can be downloaded from https://github.com/wraith-wireless/PyRIC. Once downloaded,
extract the files and from the PyRIC directory run:

    sudo python setup.py install

### d. Test without Installing

If you just want to test PyRIC out, download your choice from above. After extraction,
move the pyric folder (the package directory) to your location of choice and from
there start Python and import pyw. It is very important that you do not try and
run it from PyRIC which is the distribution directory. This will break the imports
pyw uses.

You will only be able to test PyRIC from the pyric directory but, if you want to,
you can add it to your Python path and run it from any program or any location.
To do so, assume you untared PyRIC to /home/bob/PyRIC. Create a text file named
pyric.pth with one line

    /home/bob/PyRIC

and save this file to /usr/lib/python2.7/dist-packages (or /usr/lib/python3/dist-packages
if you want to try it in Python 3).

### e. Stability vs Latest

Keep in mind that the most stable version and easist installallation but oldest
release is on PyPI (installed through pip). The source on http://wraith-wireless.github.io/PyRIC tends to be
newer but may have some bugs. The most recent source but hardest to install is on
https://github.com/wraith-wireless/pyric/releases/ It is not guaranteed to be stable
(as I tend to commit changes periodically while working on the code) and may in
fact not run at all.

## 3. USING
Once installed, see examples/pentest.py which covers most pyw functions or read
throuhg PyRIC.pdf. However, for those impatient types:

```python
import pyric               # pyric error and EUNDEF error code
from pyric import device   # driver and chipset lookup
from pyric import channels # channels, freqs, widths and conversions
from pyric import pyw      # iw functionality
```

will import the basic requirements and is assumed for the examples below. It is also assumed
that the system is in the US and has three devices lo, eth0 and wlan0 (only wlan0 of course
being wireless). Keep in mind that these examples use one-time sockets.

### a. Wireless Core Functionality
These functions do not work with a specific device rather with the system.

```python

pyw.interfaces() # get all system interfaces
=> ['lo','eth0','wlan']

pyw.isinterface('eth0') # deterimine if eth0 is an interface
=> True

pyw.isinterface('bob0')
=> False

pyw.winterfaces() # get all system wireless interfaces
=> ['wlan0']

pyw.isinterface('eth0') # check eth0 for wireless
=> False

pyw.iswinterface('wlan0')
=> True

pyw.regget() # get the regulatory domain
=> 'US'

pyw.regset('BO') # set the regulatory domain

pyw.regget()
=> 'BO'
```

### b. Interface Specific
Recall that PyRIC utilizes a Card object - this removes the necessity of having  to
remember what to pass each function i.e. whether it is a device name, physical index
or ifindex.

```python
w0 = pyw.getcard('wlan0') # get a card for wlan0

w0
=> Card(phy=0,dev='wlan0',ifindex=2)
```

You can also use pyw.devinfo to get a Card object and pyw.devadd will return a card
object for the newly created virtual interface. The card, w0, will be used throughout
the remainder of the examples.

#### i. Setting The Mac Address

```python
mac = pyw.macget(w0) # get the hw addr

mac
=> 'a0:b1:c2:d3:e4:f5'

pyw.down(w0) # turn the card off to set the mac

pyw.macset(w0,'00:1F:32:00:01:00') # lets be a nintendo device

pyw.up(w0) # bring wlan0 back up

pyw.macget(w0) # see if it worked
=> '00:1F:32:00:01:00'
```
#### ii. Getting Info On Your Card

```python
pyw.txget(w0)
=> 20

pyw.modeget(w0)
=> 'managed'

pyw.devstds(w0)
=> ['b', 'g', 'n']

pyw.devmodes(w0)
=> ['ibss', 'managed', 'AP', 'AP VLAN', 'wds', 'monitor', 'mesh']

pyw.devcmds(w0)
=> [u'new_interface', u'set_interface', u'new_key', u'start_ap', u'new_station',
u'new_mpath', u'set_mesh_config', u'set_bss', u'authenticate', u'associate',
u'deauthenticate', u'disassociate', u'join_ibss', u'join_mesh', u'set_tx_bitrate_mask',
u'frame', u'frame_wait_cancel', u'set_wiphy_netns', u'set_channel', u'set_wds_peer',
u'probe_client', u'set_noack_map', u'register_beacons', u'start_p2p_device',
u'set_mcast_rate', u'connect', u'disconnect']

pyw.devinfo(w0)
=> {'wdev': 4294967297, 'RF': None, 'CF': None, 'mac': '00:c0:ca:59:af:a6',
'mode': 'managed', 'CHW': None, 'card': Card(phy=1,dev=alfa0,ifindex=4)}

pinfo = pyw.phyinfo(w0)

pinfo['scan_ssids']
=> 4

pinfo['retry_short']
=> 7

pinfo['retry_long']
=> 4

pinfo['frag_thresh']
=> 4294967295

pinfo['rts_thresh']
=> 4294967295

pinfo['cov_class']
=> 0

```

#### iii. Virtual Interfaces
In my experience, virtual interfaces are primarily used to recon, attack or some
other tomfoolery but can also be used to analyze your wireless network. In either
case, it is generally advised to create a virtual monitor interface and delete
all others (on the same phy) - this makes sure that some external process like
NetworkManager does not interfere with your shenanigans. In the below example,
in addition to creating an interface in monitor mode, we find all interfaces
on the same physical index and delete them. You may not need to do this.

NOTE: When creating a device in monitor mode, you can also set flags (see
NL80211_MNTR_FLAGS in nl80211_h), although some cards (usually atheros) do not
always obey these requests.

```python
'monitor' in pyw.devmodes(w0) # make sure we can set wlan0 to monitor
=> True

m0 = pyw.devadd(w0,'mon0','monitor') # create mon0 in monitor mode

for iface in pyw.ifaces(w0): # delete all interfaces
    pyw.devdel(iface[0])     # on the this phy

pyw.up(m0) # bring the new card up to use

pyw.chset(m0,6,None) # and set the card to channel 6
=> True

m0
=> Card(phy=0,dev='mon0',ifindex=3)
```

Of course, once you are done, you will probably want to restore your original set
up.

```python
w0 = pyw.devadd(m0,'wlan0','managed') # restore wlan0 in managed mode

pyw.devdel(m0) # delete the monitor interface

pyw.setmac(w0,mac) # restore the original mac address

pyw.up(w0) # and bring the card up

w0
=> Card(phy0,dev='wlan0',ifindex=4)

```

## 4. EXTENDING:

Extending PyRIC is fun and easy too, see the user guide PyRIC.pdf.

## 5. ARCHITECTURE/HEIRARCHY: Brief Overview of the project file structure

* PyRIC                   root Distribution directory
  - \_\_init\_\_.py       initialize distrubution PyRIC module
  - examples              example folder
    + pentest.py          create wireless pentest environment example
    + device_details.py   display device information
  - tests                 test folder
    + pyw.unittest.py     unit test for pyw functions
  - guide                 User Guide resources
    + PyRIC.tex           User Guide LaTex
    + PyRIC.bib           User Guide bibliography
  - setup.py              install file
  - setup.cfg             used by setup.py
  - MANIFEST.in           used by setup.py
  - README.md             this file
  - LICENSE               GPLv3 License
  + TODO                  todos for PyRIC
  + RFI                   comments and observations
  - PyRIC.pdf             User Guide
  - pyw_unittest.py       unittest for pyw
  - pyric                 package directory
    + \_\_init\_\_.py     initialize pyric module
    + pyw.py              wireless nic functionality
    + radio.py            consolidate pyw in a class
    + channels.py         802.11 ISM/UNII freqs. & channels
    + device.py           device/chipset utility functions
    + rfkill.py           rfkill port
    + net                 linux header ports
      * \_\_init\_\_.py   initialize net subpackage
      * if_h.py           inet/ifreq definition
      * sockios_h.py      socket-level I/O control calls
      * genetlink_h.py    port of genetlink.h
      * netlink_h.py      port of netlink.h
      * policy.py         defines attribute datatypes
      * wireless          wireless subpackage
        - \_\_init\_\_.py initialize wireless subpackage
        - nl80211_h.py    nl80211 constants
        - nl80211_c.py    nl80211 attribute policies
    + lib                 library subpackages
      * \_\_init\_\_.py   initialize lib subpackage
      * libnl.py          netlink helper functions
      * libio.py          sockios helper functions
    + docs                netlinke documentation/help
      * nlhelp.py         nl80211 search
      * commands.help     nl80211 commands help data
      * attributes.help   nl80211 attributes help data