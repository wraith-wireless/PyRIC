# PyRIC: Python Radio Interface Controller
## Linux wireless library for the Python Wireless Developer and Pentester

[![License: GPLv3](https://img.shields.io/pypi/l/PyRIC.svg)](https://github.com/wraith-wireless/PyRIC/blob/master/LICENSE)
[![Current version at PyPI](https://img.shields.io/pypi/v/PyRIC.svg)](https://pypi.python.org/pypi/PyRIC)
[![Downloads per month on PyPI](https://img.shields.io/pypi/dm/PyRIC.svg)](https://pypi.python.org/pypi/PyRIC)
![Supported Python Versions](https://img.shields.io/pypi/pyversions/PyRIC.svg)
![Software status](https://img.shields.io/pypi/status/PyRIC.svg)

## 1 DESCRIPTION:
PyRIC (is a Linux only) library providing wireless developers and pentesters the
ability to identify, enumerate and manipulate their system's wireless cards
programmatically in Python. Pentesting applications and scripts written in Python
have increased dramatically in recent years. However, these tools still rely on
Linux command lines tools to setup and prepare and restore the system for use.
Until now. Why use subprocess.Popen, regular expressions and str.find to interact
with your wireless cards? PyRIC is:

1. Pythonic: no ctypes, SWIG etc. PyRIC redefines C header files as Python and
uses sockets to communicate with the kernel.
2. Self-sufficient: No third-party files used. PyRIC is completely self-contained.
3. Fast: (relatively speaking) PyRIC is faster than using command line tools
through subprocess.Popen
4. Parseless: Get the output you want without parsing output from command line
tools. Never worry about newer iw versions and having to rewrite your parsers.
5. Easy: If you can use iw, you can use PyRIC.

At it's heart, PyRIC is a Python port of (a subset of) iw and by extension, a
Python port of Netlink w.r.t nl80211 functionality. The original goal of PyRIC
was to provide a simple interface to the underlying nl80211 kernel support,
handling the complex operations of Netlink seamlessy while maintaining a minimum
of "code walking" to understand, modify and extend. But, why stop there? Since
it's initial inception, PyRIC has grown to include ioctl support to replicate
features of ifconfig such as getting or setting the mac address and has recently
implemented rkill support to soft block or unblock wireless cards.

### a. Additions to iw
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

### b. Current State
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

### c. What is PyRIC?

To avoid confusion, PyRIC is the system as a whole, including all header files
and "libraries" that are required to communicate with the kernel. pyw is a
interface to these libraries providing specific funtions.

What it does - defines programmatic access to a subset of iw, ifconfig and rkill.
In short, PyRIC provides Python wireless pentesters the ability to work with
wireless cards directly from Python without having to use command line tools
through Popen.

## 2. INSTALLING/USING:

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
import pyric          # pyric error and EUNDEF error code
from pyric import pyw  iw functionality
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

#### i. Setting Mac and IP Addresses

```python
mac = pyw.macget(w0) # get the hw addr

mac
=> 'a0:b1:c2:d3:e4:f5'

pyw.down(w0) # turn the card off to set the mac

pyw.macset(w0,'00:1F:32:00:01:00') # lets be a nintendo device

pyw.up(w0) # bring wlan0 back up

pyw.macget(w0) # see if it worked
=> '00:1F:32:00:01:00'

pyw.inetget(w0) # not associated, inet won't return an address
=> (None, None, None)

pyw.inetset(w0,'192.168.3.23','255.255.255.192','192.168.3.63')
=> True

pyw.inetget(w0)
=> ('192.168.3.23', '255.255.255.192', '192.168.3.255')
```

It is important to note that (like ifconfig), erroneous values can be set
when setting the inet addresses: for example you can set the ip address on
192.168.3.* network with a broadcast address of 10.255.255.255.

#### ii. Getting Info On Your Card

```python
pyw.devinfo(w0)
=> {'wdev': 4294967297, 'RF': None, 'CF': None, 'mac': '00:c0:ca:59:af:a6',
'mode': 'managed', 'CHW': None, 'card': Card(phy=1,dev=alfa0,ifindex=4)}

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

pinfo['freqs']
=>[2412, 2417, 2422, 2427, 2432, 2437, 2442, 2447, 2452, 2457, 2462, 2467, 2472,
2484]
```

Read the user guide, or type dir(pyw) in your console to get a full listing
of pyw functions.

c. Miscelleaneous Utilities
Several additional tools are located in the utils directory. Two of these are:
 * channels.py: defines ISM and UNII band channels/frequencies and provides
 functions to convert between channel and frequency and vice-versa
 * ouifetch.py: retrieves and parses oui.txt from the IEEE website and stores
  the oui data in a file that can be read by hardware.py functions
The others will be demonstrated in the following functions

i. hardware.py
Driver, chipset and mac address related functions can be found here:

``` python
import pyric.utils.hardware as hw

ouis = hw.parseoui() # load the oui dict
len(ouis)
=> 22128

mac = 'a0:88:b4:9e:68:58'
dev = 'wlan0'

hw.oui(mac)
=> 'a0:88:b4'

hw.ulm(mac)
=> '9e:68:58'

hw.manufacturer(ouis,mac)
=> 'Intel Corporate'

hw.randhw(ouis) # generate a random mac address
=>'00:03:f0:5a:a1:fc'

hw.manufacturer(ouis,'00:03:f0:5a:a1:fc')
=> 'Redfern Broadband Networks'

hw.ifcard('wlan0') # get driver & chipset
=> ('iwlwifi', 'Intel 4965/5xxx/6xxx/1xxx')
```

ii. rfkill.py
Sometimes, your card has a soft block (or hard block) on it and it is not
recognized by command line tools or pyw. Use rkill to list, turn on or turn
off soft blocks.

``` python
from pyric.utils import rfkill

rfkill.rfkill_list() # list rfkill devices
=> {'tpacpi_bluetooth_sw': {'soft': True, 'hard': False, 'type': 'bluetooth', 'idx': 1},
    'phy3': {'soft': False, 'hard': False, 'type': 'wlan', 'idx': 5},
    'phy0': {'soft': False, 'hard': False, 'type': 'wlan', 'idx': 0}}

idx = rfkill.getidx(3)
idx
=> 5

rfkill.getname(idx)
=> phy3

rfkill.gettype(idx)
=> 'wlan'

rfkill.soft_blocked(idx)
=> False

rfkill.hard_blocked(idx)
=> False

rfkill.rfkill_block(idx)

rfkill.list()
=> {'tpacpi_bluetooth_sw': {'soft': False, 'hard': True, 'type': 'bluetooth', 'idx': 1},
    'phy3': {'soft': True, 'hard': True, 'type': 'wlan', 'idx': 5},
    'phy0': {'soft': True, 'hard': True, 'type': 'wlan', 'idx': 0}}

rfkill.rfkill_unblock(idx)

rfkill.rfkill_list()
=> {'tpacpi_bluetooth_sw': {'soft': True, 'hard': False, 'type': 'bluetooth', 'idx': 1},
    'phy3': {'soft': False, 'hard': False, 'type': 'wlan', 'idx': 5},
    'phy0': {'soft': False, 'hard': False, 'type': 'wlan', 'idx': 0}}
```

Note that rfkill_list lists all 'wireless' devices: wlan, bluetooth, wimax, wwan,
gps, fm and nfc. Another important thing to note is that the rfkill index is not
the same as the interface index.

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

## 5. ARCHITECTURE/HEIRARCHY:
Brief Overview of the project file structure. Directories and/or files annotated
with (-) are not included in pip installs or PyPI downloads

* PyRIC                   root Distribution directory
  - \_\_init\_\_.py       initialize distrubution PyRIC module
  - examples              example folder
    + pentest.py          create wireless pentest environment example
    + device_details.py   display device information
  - tests (-)             test folder
    + pyw.unittest.py     unit test for pyw functions
  - docs                  User Guide resources
    + nlsend.png (-)      image for user guide
    + nlsock.png (-)      image for user guide
    + PyRIC.tex (-)       User tex file
    + PyRIC.bib (-)       User Guide bibliography
    + PyRIC.pdf           User Guide
  - setup.py              install file
  - setup.cfg             used by setup.py
  - MANIFEST.in           used by setup.py
  - README.md             this file
  - LICENSE               GPLv3 License
  - TODO                  todos for PyRIC
  - pyric                 package directory
    + \_\_init\_\_.py     initialize pyric module
    + pyw.py              wireless nic functionality
    + utils               utility directory
     * \_\_init\_\_.py    initialize utils module
     * channels.py        802.11 ISM/UNII freqs. & channels
     * hardware.py        device, chipset and mac address utility functions
     * rfkill.py          rfkill functions
     * ouifetch.py        retrieve and store oui dict from IEEE
     * data               data folder for ouis
      - oui.txt           oui file fetched from IEEE
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
        - rfkill_h.py     rfkill header file
    + lib                 library subpackages
      * \_\_init\_\_.py   initialize lib subpackage
      * libnl.py          netlink helper functions
      * libio.py          sockios helper functions
    + nlhelp              netlinke documentation/help
      * nsearch.py        nl80211 search
      * commands.help     nl80211 commands help data
      * attributes.help   nl80211 attributes help data