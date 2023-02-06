from data.lib import Data


class Data1(Data):
    content = """
{"TABLE_vrf": {"ROW_vrf": {"vrf-name-out": "all", "cnt-total": "5", "TABLE_adj": {"ROW_adj": [{"intf-out": "mgmt0", "ip-addr-out": "141.8.138.68", "time-stamp": "00:03:33", "mac": "0080.ea42.6308"}, {"intf-out": "mgmt0", "ip-addr-out": "141.8.138.69", "time-stamp": "00:04:43", "mac": "0080.ea42.637d"}, {"intf-out": "mgmt0", "ip-addr-out": "141.8.138.70", "time-stamp": "00:04:12", "mac": "0080.ea42.5e13"}, {"intf-out": "mgmt0", "ip-addr-out": "141.8.138.71", "time-stamp": "00:06:40", "mac": "0080.ea42.5e37"}, {"intf-out": "mgmt0", "ip-addr-out": "141.8.139.254", "time-stamp": "00:17:18", "mac": "001b.21a1.1bf9"}]}}}}
    """
    cmd = "show ip arp vrf all | json"
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

Kernel uptime is 670 day(s), 5 hour(s), 10 minute(s), 42 second(s)

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
