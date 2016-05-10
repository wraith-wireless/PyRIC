# PyRIC: Python Radio Interface Controller
## Pythonic iw

## 1 DESCRIPTION:
BLUF: Stop using subprocess.Popen, regular expressions and str.find. PyRIC
is a python port of a subset of iw and python port of netlink (w.r.t nl80211
functions). It arose out of a need in Wraith (https://github.com/wraith-wireless/wraith)
for Python nl80211/netlink and ioctl functionality in Python. Originally, Wraith
used ifconfig, iwconfig and iw via subprocess.Popen and parsed the output. There
are obvious shortfalls with this method, especially in terms of iw that is actively
changing (revisions break the parser) and I started looking for open source
alternatives. There are several open source projects out there like pyroute, pymnl
(and the python files included in the libnl source) but they generally have either
not been maintained recently or come with warnings. I desired a simple interface
to the underlying nl80211 kernel support that handles the complex operations of
netlink seamlessy while maintaining a minimum of "code walking" to understand,
modify and add future operations. I decided to write my own because I do not need
complete netlink functionality, only that provided by generic netlink and within
the nl80221 family. Additionally, for Wraith, I do not need a full blown port of
iw (and ifconfig, iwconfig) functionality to Python but only require the ability
to turn a wireless nic on/off, get/set the hwaddr, get/set the channel, determine
some properties of the card and add/delete interfaces.

So, why did I do this? When I first started to explore the idea of moving away
from iw output parsing, I looked at the source for iw, and existing Python ports.
Just to figure out how to get the family id for nl80211 required reading through
five different source files with no comments. To that extent, I have attempted to
keep subclassing to a minimum, the total number of classes to a minimum, combine
files where possible and where it makes since and keep the number of files required
to be open simulateneously in order to understand the methodology and follow the
program to a minimum. One can understand the PyRIC program flow with only two files
open at any time namely, pyw and libnl. In fact, only an understanding of pyw is
required to add additional commands although an understanding of libnl is helpful
especially, if for example, the code is to be extended to handle multicast or
callbacks.

In addition to providing some ifconfig functionality, I have also added several
"extensions" to iw:
* Persistent sockets: PyRIC provides gives the caller with functions & ability to
pass their own netlink (or ioctl socket) to pyw functions;
* One-time request for the nl80211 family id.
While minimal, they will slightly improve the performance of any programs that
needs to access the wireless network interface repeatedly.

ATT, PyRIC accomplish my core needs but it is still a work in progress. It provides
the following:
* enumerate interfaces and wireless interfaces
* identify a cards chipset and driver
* get/set hardware address
* turn card on/off
* get supported standards
* get/set regulatory domain
* get info on a device
* add/delete interfaces
Before adding any other commands, I want to write a search program for nl80211
commands and attributes instead of having to search the header files for values
and descriptions.

### a. PyRIC Functionality

What it does - defines programmatic access to a small subset of iw and ifconfig.

What it does not do - handle multicast messages, callbacks or dumps, attributes
or non nl80211 funtionality.

### b. A word about porting

When porting the C header files to python I use constants to define the C 'enum'
and '#define' statements. For C structs I use the following:
* a format string for packing,
* a constant calculating the length of the format string, and
* a function taking the attributes of the struct as arguments and returning the
packed byte string

For example netlink.h defines the netlink message header as:

```c
struct nlmsghdr {
    __u32 nlmsg_len;
    __u16 nlmsg_type;
    __u16 nlmsg_flags;
    __u32 nlmsg_seq;
    __u32 nlmsg_pid;
};
```

whereas in netlink_h.py I define it thus:

```python
nl_nlmsghdr = "IHHII"
NLMSGHDRLEN = struct.calcsize(nl_nlmsghdr)
def nlmsghdr(mlen,nltype,flags,seq,pid):
    """ ... comments go here """
    return struct.pack(nl_nlmsghdr,NLMSGHDRLEN+mlen,nltype,flags,seq,pid)
```

## 2. INSTALLING:

The best way to install PyRIC is through PyPI:

    sudo pip install --pre PyRIC

Note the use of the '--pre' flag. Without it, pip will not install PyRIC since it
is still in the developmental stage

If, however, you just want to test it out, download the latest tarball from
https://github.com/wraith-wireless/pyric/releases/ or https://pypi.python.org/pypi/PyRIC/
untar and run from the downloaded package directory (pyric/pyric.

If you download only and try to run PyRIC outside of the local directory, you
will get errors. Just create a pyric.pth file in  /usr/lib/python2.7/dist-packages
and add the path to pyric/pyric in this file and you will be able to run it from
anywhere.

Once installed, see examples/pentest.py which covers most pyw functions.

### a. Requirements
* Python
* linux (kernel v 3.13.x)
PyRIC requires Python 2.7 and has not been tested on Python 3. It has been tested
on kernel 3.13.x but should work on kernel 4.x.x

** 3. EXTENDING:

Extending PyRIC is fun and easy too. ...documentation in progress...

## 4. ARCHITECTURE/HEIRARCHY: Brief Overview of the project file structure

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
