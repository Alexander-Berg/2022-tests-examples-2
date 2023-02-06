from data.lib import Data


class Data1(Data):
    content = """
Flags: * - Adjacencies learnt on non-active FHRP router
       + - Adjacencies synced via CFSoE
       # - Adjacencies Throttled for Glean
       D - Static Adjacencies attached to down interface

IP ARP Table for all contexts
Total number of entries: 5
Address         Age       MAC Address     Interface
141.8.138.68    00:03:17  0080.ea42.6308  mgmt0          
141.8.138.69    00:04:28  0080.ea42.637d  mgmt0          
141.8.138.70    00:03:56  0080.ea42.5e13  mgmt0          
141.8.138.71    00:06:25  0080.ea42.5e37  mgmt0          
141.8.139.254   00:17:02  001b.21a1.1bf9  mgmt0           
    """
    cmd = "show ip arp vrf all"
    host = "man1-s305"
    version = """
Cisco Nexus Operating System (NX-OS) Software
TAC support: http://www.cisco.com/tac
Documents: http://www.cisco.com/en/US/products/ps9372/tsd_products_support_series_home.html
Copyright (c) 2002-2015, Cisco Systems, Inc. All rights reserved.
The copyrights to certain works contained herein are owned by
other third parties and are used and distributed under license.
Some parts of this software are covered under the GNU Public
License. A copy of the license is available at
http://www.gnu.org/licenses/gpl.html.

Software
  BIOS:      version 1.7.0
  loader:    version N/A
  kickstart: version 6.0(2)U6(4)
  system:    version 6.0(2)U6(4)
  Power Sequencer Firmware:
             Module 1: version v1.1
  BIOS compile time:       06/23/2014
  kickstart image file is: bootflash:///n3000-uk9-kickstart.6.0.2.U6.4.bin
  kickstart compile time:  10/2/2015 9:00:00 [10/02/2015 18:58:36]
  system image file is:    bootflash:///n3000-uk9.6.0.2.U6.4.bin
  system compile time:     10/2/2015 9:00:00 [10/02/2015 19:25:51]


Hardware
  cisco Nexus 3132 Chassis ("32x40G Supervisor")
  Intel(R) Pentium(R) CPU  @ 2.00GHz
 with 3793764 kB of memory.
  Processor Board ID FOC19023Q9L

  Device name: man1-s305
  bootflash:    4014080 kB

Kernel uptime is 670 day(s), 10 hour(s), 47 minute(s), 57 second(s)

Last reset
  Reason: Unknown
  System version: 6.0(2)U6(4)
  Service:

plugin
  Core Plugin, Ethernet Plugin
    """
    result = [{'interface': 'mgmt0', 'ip': '141.8.138.68', 'mac': '0080.ea42.6308'},
              {'interface': 'mgmt0', 'ip': '141.8.138.69', 'mac': '0080.ea42.637d'},
              {'interface': 'mgmt0', 'ip': '141.8.138.70', 'mac': '0080.ea42.5e13'},
              {'interface': 'mgmt0', 'ip': '141.8.138.71', 'mac': '0080.ea42.5e37'},
              {'interface': 'mgmt0', 'ip': '141.8.139.254', 'mac': '001b.21a1.1bf9'}]
