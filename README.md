# PyRIC: Python Radio Interface Controller
## Pythonic iw

## 1 DESCRIPTION:
BLUF: Stop using subprocess.Popen, regular expressions and str.find. PyRIC
is a python port of a subset of iw and python port of netlink (w.r.t nl80211
functions). 

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
not need a full blown port of iw et. al. functionality to Python but only require 
the ability to turn a wireless nic on/off, get/set the hwaddr, get/set the channel, 
determine some properties of the card and add/delete interfaces.

So, why did I do this and why is done "this" way? When I first started to explore 
the idea of moving away from iw output parsing, I looked at the source for iw, and 
existing Python ports. Just to figure out how to get the family id for nl80211 
required reading through five different source files with no comments. To that 
extent, I have attempted to keep subclassing to a minimum, the total number of 
classes to a minimum, combine files where possible and where it makes since and 
keep the number of files required to be open simulateneously in order to understand 
the methodology and follow the program to a minimum. One can understand the PyRIC 
program flow with only two files open at any time namely, pyw and libnl. In fact, 
only an understanding of pyw is required to add additional commands although an 
understanding of libnl(.py) is helpful especially, if for example, the code is to 
be extended to handle multicast or callbacks.

### b. Additions to iw
In addition to providing some ifconfig functionality, I have also added several
"extensions" to iw:
* Persistent sockets: pyw provides the caller with functions & ability to pass 
their own netlink (or ioctl socket) to pyw functions;
* One-time request for the nl80211 family id: pyw stores the family id in a 
global variable
* Consolidating different "reference" values to wireless NICs in one class 
(Cards are tuples t=(dev,phy #,ifindex)
These are minimal changes but they can improve the performance of any progams
that need to access the wireless nic repeatedly.

### c. Current State
ATT, PyRIC accomplish my core needs but it is still a work in progress. It provides
the following:
* enumerate interfaces and wireless interfaces
* identify a cards chipset and driver
* get/set hardware address
* turn card on/off
* get supported standards
* get supported commands
* get supported modes
* get dev info
* get phy info (does not currently process the bands)
* get/set regulatory domain
* add/delete interfaces

It also provides limited help functionality concerning nl80211 commands/attributes
(for those who wish to add additional commands). However, it pulls directly from 
the nl80211 header file and may be vague.

### d. What is PyRIC?

What it does - defines programmatic access to a small subset of iw and ifconfig.

What it does not do - handle multicast messages, callbacks or dumps or non nl80211 
funtionality.

## 2. INSTALLING/USING:

Starting with version 0.0.6, the structure (see Section 4) has changed to facilitate 
packaging on PyPI. This restructing has of course led to some minor difficulties 
especially when attempting to install (or even just test) outside of a pip installation.

### a. Requirements
PyRIC has only two requirements: Linux and Python. There has been very little testing
(on my side) on kernel 4.x and Python 3 but working out the small bugs continues on 
Python 2.7 and kernel 3.13.x.

### b. Install from Package Manager
Obviously, the easiest way to install PyRIC is through PyPI:

    sudo pip install --pre PyRIC

Note the use of the '--pre' flag. Without it, pip will not install PyRIC since it
is still in the developmental stage.

### c. Install from Source
The PyRIC source (tarball) can be downloaded from https://pypi.python.org/pypi/PyRIC or 
http://wraith-wireless.github.io/PyRIC. Additionally, the source, as a zip file, can be 
downloaded from https://github.com/wraith-wireless/PyRIC. Once downloaded, extract the 
files and from the PyRIC directory run:

    sudo python setup.py install

### d. Test without Installing

If you just want to test PyRIC out, download your choice from above. After extraction, move
the pyric folder (the package directory) to your location of choice and from there start Python
and import pyw. It is very important that you do not try and run it from PyRIC which is the 
distribution directory. This will break the imports pyw uses.

You will only be able to test PyRIC from the pyric directory but, if you want to, you can
add it to your Python path and run it from any program or any location. To do so, assume you
untared pyric to /home/bob/pyric. Create a text file named pyric.pth with one line

    /home/bob/pyric

and save this file to /usr/lib/python2.7/dist-packages (or /usr/lib/python3/dist-packages if 
you want to try it in Python 3). 

### e. Stability vs Latest

Keep in mind that the most stable version and easist installallation but oldest release is on 
PyPI (installed through pip). The source on http://wraith-wireless.github.io/PyRIC tends to be 
newer but may have some bugs. The most recent source but hardest to install is on
https://github.com/wraith-wireless/pyric/releases/ It is not guaranteed to be stable (as I tend 
to commit changes periodically while working on the code) and may in fact not run at all.

## 3. USING
Once installed, see examples/pentest.py which covers most pyw functions or read throuhg PyRIC.pdf. 
However, for those impatient types:

```python
import pyric               # pyric error and EUNDEF error code
from pyric import device   # driver and chipset lookup
from pyric import channels # channels, freqs, widths and conversions
from pyric import pyw      # iw functionality
```

will import the basic requirements and is assumed for the examples below. It is also assumed that 
the system is in the US and has three devices lo, eth0 and wlan0 (only wlan0 of course being 
wireless).

### a. Wireless Core Functionality
These functions do not work with a specific device rather with the system.

```python

pyw.interfaces()
=> ['lo','eth0','wlan']

pyw.isinterface()

```


** 4. EXTENDING:

Extending PyRIC is fun and easy too, see the user guide PyRIC.pdf.

## 5. ARCHITECTURE/HEIRARCHY: Brief Overview of the project file structure

* pyric                   root Distribution directory
  - \_\_init\_\_.py       initialize 'outer' pyric module
  - examples              example folder
    + pentest.py          create wireless pentest environment example
  - setup.py              install file
  - setup.cfg             used by setup.py
  - MANIFEST.in           used by setup.py
  - README.md             this file
  - LICENSE               GPLv3 License
  * PyRIC.pdf             User Guide
  - pyric                 package directory
    + \_\_init\_\_.py     initialize pyric module
    + pyw.py              wireless nic functionality
    + radio.py            consolidate pyw in a class
    + channels.py         802.11 ISM/UNII freqs. & channels
    + device.py           device/chipset utility functions
    + TODO                todos for PyRIC
    + RFI                 comments and observations
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
      * res               User Guide resources
        - PyRIC.tex       User Guide LaTex
        - PyRIC.bib       User Guide bibliography
