from data.lib import Data


class Data1(Data):
    content = """
Legend:
        * - primary entry, G - Gateway MAC, (R) - Routed MAC, O - Overlay MAC
        age - seconds since first seen,+ - primary entry using vPC Peer-Link
   VLAN     MAC Address      Type      age     Secure NTFY   Ports/SWID.SSID.LID
---------+-----------------+--------+---------+------+----+------------------
* 788      1c1b.0d83.e0a9    dynamic   20052700    F    F  Eth1/7/4
* 788      1c1b.0d83.e0b5    dynamic   13273900    F    F  Eth1/7/2
* 788      1c1b.0d83.e1bd    dynamic   3308660    F    F  Eth1/9/3
* 788      1c1b.0d83.e201    dynamic   16844650    F    F  Eth1/5/1
* 788      1c1b.0d83.e281    dynamic   20052720    F    F  Eth1/3/4
* 788      1c1b.0d83.e285    dynamic   20052710    F    F  Eth1/3/2
* 788      1c1b.0d83.e29d    dynamic   20052650    F    F  Eth1/1/4
* 788      1c1b.0d83.e2a1    dynamic   20052690    F    F  Eth1/10/3
* 788      1c1b.0d83.e2a5    dynamic   20052710    F    F  Eth1/12/1
* 788      1c1b.0d83.e2a9    dynamic   20052720    F    F  Eth1/1/1
* 788      1c1b.0d83.e2ad    dynamic   20052710    F    F  Eth1/1/3
* 788      1c1b.0d83.e2bd    dynamic   2946740    F    F  Eth1/5/3
* 788      1c1b.0d83.e2c5    dynamic   20052690    F    F  Eth1/5/4
* 788      1c1b.0d83.e2c9    dynamic   20052680    F    F  Eth1/9/4
* 788      1c1b.0d83.e2e1    dynamic   20052690    F    F  Eth1/10/4
* 788      1c1b.0d83.e2e5    dynamic   20052690    F    F  Eth1/10/2
* 788      1c1b.0d83.e2e9    dynamic   2677170    F    F  Eth1/8/3
* 788      1c1b.0d83.e365    dynamic   15041560    F    F  Eth1/10/1
* 788      1c1b.0d83.e369    dynamic   2669180    F    F  Eth1/8/4
* 788      1c1b.0d83.e3a5    dynamic   20052700    F    F  Eth1/11/1
* 788      1c1b.0d83.e3c9    dynamic   20052710    F    F  Eth1/9/2
* 788      1c1b.0d83.e3fd    dynamic   20052660    F    F  Eth1/9/1
* 788      1c1b.0d83.e491    dynamic   890540     F    F  Eth1/7/1
* 788      1c1b.0d83.e49d    dynamic   20052700    F    F  Eth1/7/3
* 788      1c1b.0d83.e5b5    dynamic   20052700    F    F  Eth1/5/2
* 788      1c1b.0d83.e679    dynamic   2096150    F    F  Eth1/3/3
* 788      1c1b.0d83.e67d    dynamic   20052690    F    F  Eth1/3/1
* 788      1c1b.0d83.e685    dynamic   20053680    F    F  Eth1/8/1
* 788      1c1b.0d83.e6f9    dynamic   20052690    F    F  Eth1/6/4
* 788      1c1b.0d83.e711    dynamic   20052660    F    F  Eth1/6/1
* 788      1c1b.0d83.e715    dynamic   5826970    F    F  Eth1/6/3
* 788      1c1b.0d83.e721    dynamic   20052690    F    F  Eth1/8/2
* 788      1c1b.0d83.e725    dynamic   8666780    F    F  Eth1/2/2
* 788      1c1b.0d83.e74d    dynamic   17966290    F    F  Eth1/2/4
* 788      1c1b.0d83.e751    dynamic   20052710    F    F  Eth1/4/2
* 788      1c1b.0d83.e75d    dynamic   20052730    F    F  Eth1/2/1
* 788      1c1b.0d83.e765    dynamic   3545710    F    F  Eth1/2/3
* 788      1c1b.0d83.e781    dynamic   20052720    F    F  Eth1/4/1
* 788      1c1b.0d83.e785    dynamic   16847400    F    F  Eth1/4/3
* 788      1c1b.0d83.e78d    dynamic   8896680    F    F  Eth1/4/4
* 788      1c1b.0d83.e791    dynamic   2669170    F    F  Eth1/6/2
* 700      1c1b.0d83.e0a9    dynamic   20052670    F    F  Eth1/7/4
* 700      1c1b.0d83.e0b5    dynamic   13273900    F    F  Eth1/7/2
* 700      1c1b.0d83.e1bd    dynamic   3308630    F    F  Eth1/9/3
* 700      1c1b.0d83.e201    dynamic   16844650    F    F  Eth1/5/1
* 700      1c1b.0d83.e281    dynamic   20052680    F    F  Eth1/3/4
* 700      1c1b.0d83.e285    dynamic   20052680    F    F  Eth1/3/2
* 700      1c1b.0d83.e29d    dynamic   20052620    F    F  Eth1/1/4
* 700      1c1b.0d83.e2a1    dynamic   20052660    F    F  Eth1/10/3
* 700      1c1b.0d83.e2a5    dynamic   20052680    F    F  Eth1/12/1
* 700      1c1b.0d83.e2a9    dynamic   20052680    F    F  Eth1/1/1
* 700      1c1b.0d83.e2ad    dynamic   20052680    F    F  Eth1/1/3
* 700      1c1b.0d83.e2bd    dynamic   2946740    F    F  Eth1/5/3
* 700      1c1b.0d83.e2c5    dynamic   20052660    F    F  Eth1/5/4
* 700      1c1b.0d83.e2c9    dynamic   20052650    F    F  Eth1/9/4
* 700      1c1b.0d83.e2e1    dynamic   20052650    F    F  Eth1/10/4
* 700      1c1b.0d83.e2e5    dynamic   20052660    F    F  Eth1/10/2
* 700      1c1b.0d83.e2e9    dynamic   2677170    F    F  Eth1/8/3
* 700      1c1b.0d83.e365    dynamic   15041560    F    F  Eth1/10/1
* 700      1c1b.0d83.e369    dynamic   2669170    F    F  Eth1/8/4
* 700      1c1b.0d83.e3a5    dynamic   20052670    F    F  Eth1/11/1
* 700      1c1b.0d83.e3c9    dynamic   20052680    F    F  Eth1/9/2
* 700      1c1b.0d83.e3fd    dynamic   20052630    F    F  Eth1/9/1
* 700      1c1b.0d83.e491    dynamic   890500     F    F  Eth1/7/1
* 700      1c1b.0d83.e49d    dynamic   20052670    F    F  Eth1/7/3
* 700      1c1b.0d83.e5b5    dynamic   20052670    F    F  Eth1/5/2
* 700      1c1b.0d83.e679    dynamic   2096140    F    F  Eth1/3/3
* 700      1c1b.0d83.e67d    dynamic   20052650    F    F  Eth1/3/1
* 700      1c1b.0d83.e685    dynamic   20053650    F    F  Eth1/8/1
* 700      1c1b.0d83.e6f9    dynamic   20052650    F    F  Eth1/6/4
* 700      1c1b.0d83.e711    dynamic   20052630    F    F  Eth1/6/1
* 700      1c1b.0d83.e715    dynamic   5826940    F    F  Eth1/6/3
* 700      1c1b.0d83.e721    dynamic   20052660    F    F  Eth1/8/2
* 700      1c1b.0d83.e725    dynamic   8666750    F    F  Eth1/2/2
* 700      1c1b.0d83.e74d    dynamic   17966280    F    F  Eth1/2/4
* 700      1c1b.0d83.e751    dynamic   20052680    F    F  Eth1/4/2
* 700      1c1b.0d83.e75d    dynamic   20052690    F    F  Eth1/2/1
* 700      1c1b.0d83.e765    dynamic   3545670    F    F  Eth1/2/3
* 700      1c1b.0d83.e781    dynamic   20052690    F    F  Eth1/4/1
* 700      1c1b.0d83.e785    dynamic   16847400    F    F  Eth1/4/3
* 700      1c1b.0d83.e78d    dynamic   8896680    F    F  Eth1/4/4
* 700      1c1b.0d83.e791    dynamic   2669170    F    F  Eth1/6/2
* 688      1c1b.0d83.e0a9    dynamic   20052730    F    F  Eth1/7/4
* 688      1c1b.0d83.e0b5    dynamic   13273900    F    F  Eth1/7/2
* 688      1c1b.0d83.e1bd    dynamic   3308690    F    F  Eth1/9/3
* 688      1c1b.0d83.e201    dynamic   16844650    F    F  Eth1/5/1
* 688      1c1b.0d83.e281    dynamic   20052750    F    F  Eth1/3/4
* 688      1c1b.0d83.e285    dynamic   20052740    F    F  Eth1/3/2
* 688      1c1b.0d83.e29d    dynamic   20052680    F    F  Eth1/1/4
* 688      1c1b.0d83.e2a1    dynamic   20052720    F    F  Eth1/10/3
* 688      1c1b.0d83.e2a5    dynamic   20052750    F    F  Eth1/12/1
* 688      1c1b.0d83.e2a9    dynamic   20052750    F    F  Eth1/1/1
* 688      1c1b.0d83.e2ad    dynamic   20052740    F    F  Eth1/1/3
* 688      1c1b.0d83.e2bd    dynamic   2943140    F    F  Eth1/5/3
* 688      1c1b.0d83.e2c5    dynamic   20052720    F    F  Eth1/5/4
* 688      1c1b.0d83.e2c9    dynamic   20052710    F    F  Eth1/9/4
* 688      1c1b.0d83.e2e1    dynamic   20052720    F    F  Eth1/10/4
* 688      1c1b.0d83.e2e5    dynamic   20052730    F    F  Eth1/10/2
* 688      1c1b.0d83.e2e9    dynamic   2677170    F    F  Eth1/8/3
* 688      1c1b.0d83.e365    dynamic   15041560    F    F  Eth1/10/1
* 688      1c1b.0d83.e369    dynamic   2669180    F    F  Eth1/8/4
* 688      1c1b.0d83.e3a5    dynamic   20052730    F    F  Eth1/11/1
* 688      1c1b.0d83.e3c9    dynamic   20052740    F    F  Eth1/9/2
* 688      1c1b.0d83.e3fd    dynamic   20052690    F    F  Eth1/9/1
* 688      1c1b.0d83.e491    dynamic   890570     F    F  Eth1/7/1
* 688      1c1b.0d83.e49d    dynamic   20052740    F    F  Eth1/7/3
* 688      1c1b.0d83.e5b5    dynamic   20052740    F    F  Eth1/5/2
* 688      1c1b.0d83.e679    dynamic   2096150    F    F  Eth1/3/3
* 688      1c1b.0d83.e67d    dynamic   20052720    F    F  Eth1/3/1
* 688      1c1b.0d83.e685    dynamic   20053710    F    F  Eth1/8/1
* 688      1c1b.0d83.e6f9    dynamic   20052720    F    F  Eth1/6/4
* 688      1c1b.0d83.e711    dynamic   20052690    F    F  Eth1/6/1
* 688      1c1b.0d83.e715    dynamic   5827000    F    F  Eth1/6/3
* 688      1c1b.0d83.e721    dynamic   20052730    F    F  Eth1/8/2
* 688      1c1b.0d83.e725    dynamic   8666820    F    F  Eth1/2/2
* 688      1c1b.0d83.e74d    dynamic   17966290    F    F  Eth1/2/4
* 688      1c1b.0d83.e751    dynamic   20052740    F    F  Eth1/4/2
* 688      1c1b.0d83.e75d    dynamic   20052760    F    F  Eth1/2/1
* 688      1c1b.0d83.e765    dynamic   3545740    F    F  Eth1/2/3
* 688      1c1b.0d83.e781    dynamic   20052750    F    F  Eth1/4/1
* 688      1c1b.0d83.e785    dynamic   16847400    F    F  Eth1/4/3
* 688      1c1b.0d83.e78d    dynamic   8896680    F    F  Eth1/4/4
* 688      1c1b.0d83.e791    dynamic   2669170    F    F  Eth1/6/2
* 333      1c1b.0d83.e0a9    dynamic   20052760    F    F  Eth1/7/4
* 333      1c1b.0d83.e0b5    dynamic   13273900    F    F  Eth1/7/2
* 333      1c1b.0d83.e1bd    dynamic   3308720    F    F  Eth1/9/3
* 333      1c1b.0d83.e201    dynamic   16844650    F    F  Eth1/5/1
* 333      1c1b.0d83.e281    dynamic   20052780    F    F  Eth1/3/4
* 333      1c1b.0d83.e285    dynamic   20052770    F    F  Eth1/3/2
* 333      1c1b.0d83.e291    dynamic   590        F    F  Eth1/1/2
* 333      1c1b.0d83.e29d    dynamic   20052710    F    F  Eth1/1/4
* 333      1c1b.0d83.e2a1    dynamic   20052750    F    F  Eth1/10/3
* 333      1c1b.0d83.e2a5    dynamic   20052780    F    F  Eth1/12/1
* 333      1c1b.0d83.e2a9    dynamic   20052780    F    F  Eth1/1/1
* 333      1c1b.0d83.e2ad    dynamic   20052770    F    F  Eth1/1/3
* 333      1c1b.0d83.e2bd    dynamic   2946750    F    F  Eth1/5/3
* 333      1c1b.0d83.e2c5    dynamic   20052750    F    F  Eth1/5/4
* 333      1c1b.0d83.e2c9    dynamic   20052740    F    F  Eth1/9/4
* 333      1c1b.0d83.e2e1    dynamic   20052750    F    F  Eth1/10/4
* 333      1c1b.0d83.e2e5    dynamic   20052760    F    F  Eth1/10/2
* 333      1c1b.0d83.e2e9    dynamic   2677170    F    F  Eth1/8/3
* 333      1c1b.0d83.e365    dynamic   15041560    F    F  Eth1/10/1
* 333      1c1b.0d83.e369    dynamic   2669180    F    F  Eth1/8/4
* 333      1c1b.0d83.e3a5    dynamic   20052760    F    F  Eth1/11/1
* 333      1c1b.0d83.e3c9    dynamic   20052770    F    F  Eth1/9/2
* 333      1c1b.0d83.e3fd    dynamic   20052720    F    F  Eth1/9/1
* 333      1c1b.0d83.e491    dynamic   890600     F    F  Eth1/7/1
* 333      1c1b.0d83.e49d    dynamic   20052770    F    F  Eth1/7/3
* 333      1c1b.0d83.e5b5    dynamic   20052760    F    F  Eth1/5/2
* 333      1c1b.0d83.e679    dynamic   2096150    F    F  Eth1/3/3
* 333      1c1b.0d83.e67d    dynamic   20052750    F    F  Eth1/3/1
* 333      1c1b.0d83.e685    dynamic   20053740    F    F  Eth1/8/1
* 333      1c1b.0d83.e6f9    dynamic   20052750    F    F  Eth1/6/4
* 333      1c1b.0d83.e711    dynamic   20052720    F    F  Eth1/6/1
* 333      1c1b.0d83.e715    dynamic   5827030    F    F  Eth1/6/3
* 333      1c1b.0d83.e721    dynamic   20052760    F    F  Eth1/8/2
* 333      1c1b.0d83.e725    dynamic   8666850    F    F  Eth1/2/2
* 333      1c1b.0d83.e74d    dynamic   17966290    F    F  Eth1/2/4
* 333      1c1b.0d83.e751    dynamic   20052770    F    F  Eth1/4/2
* 333      1c1b.0d83.e75d    dynamic   20052790    F    F  Eth1/2/1
* 333      1c1b.0d83.e765    dynamic   3545770    F    F  Eth1/2/3
* 333      1c1b.0d83.e781    dynamic   20052780    F    F  Eth1/4/1
* 333      1c1b.0d83.e785    dynamic   16847400    F    F  Eth1/4/3
* 333      1c1b.0d83.e78d    dynamic   8896680    F    F  Eth1/4/4
* 333      1c1b.0d83.e791    dynamic   2669170    F    F  Eth1/6/2
    """
    cmd = "show mac address-table"
    host = "man1-4s64"
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
  kickstart: version 6.0(2)U6(2)
  system:    version 6.0(2)U6(2)
  Power Sequencer Firmware:
             Module 1: version v1.1
  BIOS compile time:       06/23/2014
  kickstart image file is: bootflash:///n3000-uk9-kickstart.6.0.2.U6.2.bin
  kickstart compile time:  8/1/2015 0:00:00 [08/01/2015 09:57:50]
  system image file is:    bootflash:///n3000-uk9.6.0.2.U6.2.bin
  system compile time:     8/1/2015 0:00:00 [08/01/2015 10:22:35]


Hardware
  cisco Nexus 3132 Chassis ("32x40G Supervisor")
  Intel(R) Pentium(R) CPU  @ 2.00GHz
 with 3793764 kB of memory.
  Processor Board ID FOC20193L7X

  Device name: man1-4s64
  bootflash:    3932160 kB

Kernel uptime is 796 day(s), 20 hour(s), 7 minute(s), 52 second(s)

Last reset at 247596 usecs after  Mon Nov  7 16:24:46 2016

  Reason: Reset Requested by CLI command reload
  System version: 6.0(2)U6(2)
  Service:

plugin
  Core Plugin, Ethernet Plugin
    """
    result = [{'interface': 'Eth1/7/4', 'mac': '1c1b.0d83.e0a9', 'vlan': '788'},
              {'interface': 'Eth1/7/2', 'mac': '1c1b.0d83.e0b5', 'vlan': '788'},
              {'interface': 'Eth1/9/3', 'mac': '1c1b.0d83.e1bd', 'vlan': '788'},
              {'interface': 'Eth1/5/1', 'mac': '1c1b.0d83.e201', 'vlan': '788'},
              {'interface': 'Eth1/3/4', 'mac': '1c1b.0d83.e281', 'vlan': '788'},
              {'interface': 'Eth1/3/2', 'mac': '1c1b.0d83.e285', 'vlan': '788'},
              {'interface': 'Eth1/1/4', 'mac': '1c1b.0d83.e29d', 'vlan': '788'},
              {'interface': 'Eth1/10/3', 'mac': '1c1b.0d83.e2a1', 'vlan': '788'},
              {'interface': 'Eth1/12/1', 'mac': '1c1b.0d83.e2a5', 'vlan': '788'},
              {'interface': 'Eth1/1/1', 'mac': '1c1b.0d83.e2a9', 'vlan': '788'},
              {'interface': 'Eth1/1/3', 'mac': '1c1b.0d83.e2ad', 'vlan': '788'},
              {'interface': 'Eth1/5/3', 'mac': '1c1b.0d83.e2bd', 'vlan': '788'},
              {'interface': 'Eth1/5/4', 'mac': '1c1b.0d83.e2c5', 'vlan': '788'},
              {'interface': 'Eth1/9/4', 'mac': '1c1b.0d83.e2c9', 'vlan': '788'},
              {'interface': 'Eth1/10/4', 'mac': '1c1b.0d83.e2e1', 'vlan': '788'},
              {'interface': 'Eth1/10/2', 'mac': '1c1b.0d83.e2e5', 'vlan': '788'},
              {'interface': 'Eth1/8/3', 'mac': '1c1b.0d83.e2e9', 'vlan': '788'},
              {'interface': 'Eth1/10/1', 'mac': '1c1b.0d83.e365', 'vlan': '788'},
              {'interface': 'Eth1/8/4', 'mac': '1c1b.0d83.e369', 'vlan': '788'},
              {'interface': 'Eth1/11/1', 'mac': '1c1b.0d83.e3a5', 'vlan': '788'},
              {'interface': 'Eth1/9/2', 'mac': '1c1b.0d83.e3c9', 'vlan': '788'},
              {'interface': 'Eth1/9/1', 'mac': '1c1b.0d83.e3fd', 'vlan': '788'},
              {'interface': 'Eth1/7/1', 'mac': '1c1b.0d83.e491', 'vlan': '788'},
              {'interface': 'Eth1/7/3', 'mac': '1c1b.0d83.e49d', 'vlan': '788'},
              {'interface': 'Eth1/5/2', 'mac': '1c1b.0d83.e5b5', 'vlan': '788'},
              {'interface': 'Eth1/3/3', 'mac': '1c1b.0d83.e679', 'vlan': '788'},
              {'interface': 'Eth1/3/1', 'mac': '1c1b.0d83.e67d', 'vlan': '788'},
              {'interface': 'Eth1/8/1', 'mac': '1c1b.0d83.e685', 'vlan': '788'},
              {'interface': 'Eth1/6/4', 'mac': '1c1b.0d83.e6f9', 'vlan': '788'},
              {'interface': 'Eth1/6/1', 'mac': '1c1b.0d83.e711', 'vlan': '788'},
              {'interface': 'Eth1/6/3', 'mac': '1c1b.0d83.e715', 'vlan': '788'},
              {'interface': 'Eth1/8/2', 'mac': '1c1b.0d83.e721', 'vlan': '788'},
              {'interface': 'Eth1/2/2', 'mac': '1c1b.0d83.e725', 'vlan': '788'},
              {'interface': 'Eth1/2/4', 'mac': '1c1b.0d83.e74d', 'vlan': '788'},
              {'interface': 'Eth1/4/2', 'mac': '1c1b.0d83.e751', 'vlan': '788'},
              {'interface': 'Eth1/2/1', 'mac': '1c1b.0d83.e75d', 'vlan': '788'},
              {'interface': 'Eth1/2/3', 'mac': '1c1b.0d83.e765', 'vlan': '788'},
              {'interface': 'Eth1/4/1', 'mac': '1c1b.0d83.e781', 'vlan': '788'},
              {'interface': 'Eth1/4/3', 'mac': '1c1b.0d83.e785', 'vlan': '788'},
              {'interface': 'Eth1/4/4', 'mac': '1c1b.0d83.e78d', 'vlan': '788'},
              {'interface': 'Eth1/6/2', 'mac': '1c1b.0d83.e791', 'vlan': '788'},
              {'interface': 'Eth1/7/4', 'mac': '1c1b.0d83.e0a9', 'vlan': '700'},
              {'interface': 'Eth1/7/2', 'mac': '1c1b.0d83.e0b5', 'vlan': '700'},
              {'interface': 'Eth1/9/3', 'mac': '1c1b.0d83.e1bd', 'vlan': '700'},
              {'interface': 'Eth1/5/1', 'mac': '1c1b.0d83.e201', 'vlan': '700'},
              {'interface': 'Eth1/3/4', 'mac': '1c1b.0d83.e281', 'vlan': '700'},
              {'interface': 'Eth1/3/2', 'mac': '1c1b.0d83.e285', 'vlan': '700'},
              {'interface': 'Eth1/1/4', 'mac': '1c1b.0d83.e29d', 'vlan': '700'},
              {'interface': 'Eth1/10/3', 'mac': '1c1b.0d83.e2a1', 'vlan': '700'},
              {'interface': 'Eth1/12/1', 'mac': '1c1b.0d83.e2a5', 'vlan': '700'},
              {'interface': 'Eth1/1/1', 'mac': '1c1b.0d83.e2a9', 'vlan': '700'},
              {'interface': 'Eth1/1/3', 'mac': '1c1b.0d83.e2ad', 'vlan': '700'},
              {'interface': 'Eth1/5/3', 'mac': '1c1b.0d83.e2bd', 'vlan': '700'},
              {'interface': 'Eth1/5/4', 'mac': '1c1b.0d83.e2c5', 'vlan': '700'},
              {'interface': 'Eth1/9/4', 'mac': '1c1b.0d83.e2c9', 'vlan': '700'},
              {'interface': 'Eth1/10/4', 'mac': '1c1b.0d83.e2e1', 'vlan': '700'},
              {'interface': 'Eth1/10/2', 'mac': '1c1b.0d83.e2e5', 'vlan': '700'},
              {'interface': 'Eth1/8/3', 'mac': '1c1b.0d83.e2e9', 'vlan': '700'},
              {'interface': 'Eth1/10/1', 'mac': '1c1b.0d83.e365', 'vlan': '700'},
              {'interface': 'Eth1/8/4', 'mac': '1c1b.0d83.e369', 'vlan': '700'},
              {'interface': 'Eth1/11/1', 'mac': '1c1b.0d83.e3a5', 'vlan': '700'},
              {'interface': 'Eth1/9/2', 'mac': '1c1b.0d83.e3c9', 'vlan': '700'},
              {'interface': 'Eth1/9/1', 'mac': '1c1b.0d83.e3fd', 'vlan': '700'},
              {'interface': 'Eth1/7/1', 'mac': '1c1b.0d83.e491', 'vlan': '700'},
              {'interface': 'Eth1/7/3', 'mac': '1c1b.0d83.e49d', 'vlan': '700'},
              {'interface': 'Eth1/5/2', 'mac': '1c1b.0d83.e5b5', 'vlan': '700'},
              {'interface': 'Eth1/3/3', 'mac': '1c1b.0d83.e679', 'vlan': '700'},
              {'interface': 'Eth1/3/1', 'mac': '1c1b.0d83.e67d', 'vlan': '700'},
              {'interface': 'Eth1/8/1', 'mac': '1c1b.0d83.e685', 'vlan': '700'},
              {'interface': 'Eth1/6/4', 'mac': '1c1b.0d83.e6f9', 'vlan': '700'},
              {'interface': 'Eth1/6/1', 'mac': '1c1b.0d83.e711', 'vlan': '700'},
              {'interface': 'Eth1/6/3', 'mac': '1c1b.0d83.e715', 'vlan': '700'},
              {'interface': 'Eth1/8/2', 'mac': '1c1b.0d83.e721', 'vlan': '700'},
              {'interface': 'Eth1/2/2', 'mac': '1c1b.0d83.e725', 'vlan': '700'},
              {'interface': 'Eth1/2/4', 'mac': '1c1b.0d83.e74d', 'vlan': '700'},
              {'interface': 'Eth1/4/2', 'mac': '1c1b.0d83.e751', 'vlan': '700'},
              {'interface': 'Eth1/2/1', 'mac': '1c1b.0d83.e75d', 'vlan': '700'},
              {'interface': 'Eth1/2/3', 'mac': '1c1b.0d83.e765', 'vlan': '700'},
              {'interface': 'Eth1/4/1', 'mac': '1c1b.0d83.e781', 'vlan': '700'},
              {'interface': 'Eth1/4/3', 'mac': '1c1b.0d83.e785', 'vlan': '700'},
              {'interface': 'Eth1/4/4', 'mac': '1c1b.0d83.e78d', 'vlan': '700'},
              {'interface': 'Eth1/6/2', 'mac': '1c1b.0d83.e791', 'vlan': '700'},
              {'interface': 'Eth1/7/4', 'mac': '1c1b.0d83.e0a9', 'vlan': '688'},
              {'interface': 'Eth1/7/2', 'mac': '1c1b.0d83.e0b5', 'vlan': '688'},
              {'interface': 'Eth1/9/3', 'mac': '1c1b.0d83.e1bd', 'vlan': '688'},
              {'interface': 'Eth1/5/1', 'mac': '1c1b.0d83.e201', 'vlan': '688'},
              {'interface': 'Eth1/3/4', 'mac': '1c1b.0d83.e281', 'vlan': '688'},
              {'interface': 'Eth1/3/2', 'mac': '1c1b.0d83.e285', 'vlan': '688'},
              {'interface': 'Eth1/1/4', 'mac': '1c1b.0d83.e29d', 'vlan': '688'},
              {'interface': 'Eth1/10/3', 'mac': '1c1b.0d83.e2a1', 'vlan': '688'},
              {'interface': 'Eth1/12/1', 'mac': '1c1b.0d83.e2a5', 'vlan': '688'},
              {'interface': 'Eth1/1/1', 'mac': '1c1b.0d83.e2a9', 'vlan': '688'},
              {'interface': 'Eth1/1/3', 'mac': '1c1b.0d83.e2ad', 'vlan': '688'},
              {'interface': 'Eth1/5/3', 'mac': '1c1b.0d83.e2bd', 'vlan': '688'},
              {'interface': 'Eth1/5/4', 'mac': '1c1b.0d83.e2c5', 'vlan': '688'},
              {'interface': 'Eth1/9/4', 'mac': '1c1b.0d83.e2c9', 'vlan': '688'},
              {'interface': 'Eth1/10/4', 'mac': '1c1b.0d83.e2e1', 'vlan': '688'},
              {'interface': 'Eth1/10/2', 'mac': '1c1b.0d83.e2e5', 'vlan': '688'},
              {'interface': 'Eth1/8/3', 'mac': '1c1b.0d83.e2e9', 'vlan': '688'},
              {'interface': 'Eth1/10/1', 'mac': '1c1b.0d83.e365', 'vlan': '688'},
              {'interface': 'Eth1/8/4', 'mac': '1c1b.0d83.e369', 'vlan': '688'},
              {'interface': 'Eth1/11/1', 'mac': '1c1b.0d83.e3a5', 'vlan': '688'},
              {'interface': 'Eth1/9/2', 'mac': '1c1b.0d83.e3c9', 'vlan': '688'},
              {'interface': 'Eth1/9/1', 'mac': '1c1b.0d83.e3fd', 'vlan': '688'},
              {'interface': 'Eth1/7/1', 'mac': '1c1b.0d83.e491', 'vlan': '688'},
              {'interface': 'Eth1/7/3', 'mac': '1c1b.0d83.e49d', 'vlan': '688'},
              {'interface': 'Eth1/5/2', 'mac': '1c1b.0d83.e5b5', 'vlan': '688'},
              {'interface': 'Eth1/3/3', 'mac': '1c1b.0d83.e679', 'vlan': '688'},
              {'interface': 'Eth1/3/1', 'mac': '1c1b.0d83.e67d', 'vlan': '688'},
              {'interface': 'Eth1/8/1', 'mac': '1c1b.0d83.e685', 'vlan': '688'},
              {'interface': 'Eth1/6/4', 'mac': '1c1b.0d83.e6f9', 'vlan': '688'},
              {'interface': 'Eth1/6/1', 'mac': '1c1b.0d83.e711', 'vlan': '688'},
              {'interface': 'Eth1/6/3', 'mac': '1c1b.0d83.e715', 'vlan': '688'},
              {'interface': 'Eth1/8/2', 'mac': '1c1b.0d83.e721', 'vlan': '688'},
              {'interface': 'Eth1/2/2', 'mac': '1c1b.0d83.e725', 'vlan': '688'},
              {'interface': 'Eth1/2/4', 'mac': '1c1b.0d83.e74d', 'vlan': '688'},
              {'interface': 'Eth1/4/2', 'mac': '1c1b.0d83.e751', 'vlan': '688'},
              {'interface': 'Eth1/2/1', 'mac': '1c1b.0d83.e75d', 'vlan': '688'},
              {'interface': 'Eth1/2/3', 'mac': '1c1b.0d83.e765', 'vlan': '688'},
              {'interface': 'Eth1/4/1', 'mac': '1c1b.0d83.e781', 'vlan': '688'},
              {'interface': 'Eth1/4/3', 'mac': '1c1b.0d83.e785', 'vlan': '688'},
              {'interface': 'Eth1/4/4', 'mac': '1c1b.0d83.e78d', 'vlan': '688'},
              {'interface': 'Eth1/6/2', 'mac': '1c1b.0d83.e791', 'vlan': '688'},
              {'interface': 'Eth1/7/4', 'mac': '1c1b.0d83.e0a9', 'vlan': '333'},
              {'interface': 'Eth1/7/2', 'mac': '1c1b.0d83.e0b5', 'vlan': '333'},
              {'interface': 'Eth1/9/3', 'mac': '1c1b.0d83.e1bd', 'vlan': '333'},
              {'interface': 'Eth1/5/1', 'mac': '1c1b.0d83.e201', 'vlan': '333'},
              {'interface': 'Eth1/3/4', 'mac': '1c1b.0d83.e281', 'vlan': '333'},
              {'interface': 'Eth1/3/2', 'mac': '1c1b.0d83.e285', 'vlan': '333'},
              {'interface': 'Eth1/1/2', 'mac': '1c1b.0d83.e291', 'vlan': '333'},
              {'interface': 'Eth1/1/4', 'mac': '1c1b.0d83.e29d', 'vlan': '333'},
              {'interface': 'Eth1/10/3', 'mac': '1c1b.0d83.e2a1', 'vlan': '333'},
              {'interface': 'Eth1/12/1', 'mac': '1c1b.0d83.e2a5', 'vlan': '333'},
              {'interface': 'Eth1/1/1', 'mac': '1c1b.0d83.e2a9', 'vlan': '333'},
              {'interface': 'Eth1/1/3', 'mac': '1c1b.0d83.e2ad', 'vlan': '333'},
              {'interface': 'Eth1/5/3', 'mac': '1c1b.0d83.e2bd', 'vlan': '333'},
              {'interface': 'Eth1/5/4', 'mac': '1c1b.0d83.e2c5', 'vlan': '333'},
              {'interface': 'Eth1/9/4', 'mac': '1c1b.0d83.e2c9', 'vlan': '333'},
              {'interface': 'Eth1/10/4', 'mac': '1c1b.0d83.e2e1', 'vlan': '333'},
              {'interface': 'Eth1/10/2', 'mac': '1c1b.0d83.e2e5', 'vlan': '333'},
              {'interface': 'Eth1/8/3', 'mac': '1c1b.0d83.e2e9', 'vlan': '333'},
              {'interface': 'Eth1/10/1', 'mac': '1c1b.0d83.e365', 'vlan': '333'},
              {'interface': 'Eth1/8/4', 'mac': '1c1b.0d83.e369', 'vlan': '333'},
              {'interface': 'Eth1/11/1', 'mac': '1c1b.0d83.e3a5', 'vlan': '333'},
              {'interface': 'Eth1/9/2', 'mac': '1c1b.0d83.e3c9', 'vlan': '333'},
              {'interface': 'Eth1/9/1', 'mac': '1c1b.0d83.e3fd', 'vlan': '333'},
              {'interface': 'Eth1/7/1', 'mac': '1c1b.0d83.e491', 'vlan': '333'},
              {'interface': 'Eth1/7/3', 'mac': '1c1b.0d83.e49d', 'vlan': '333'},
              {'interface': 'Eth1/5/2', 'mac': '1c1b.0d83.e5b5', 'vlan': '333'},
              {'interface': 'Eth1/3/3', 'mac': '1c1b.0d83.e679', 'vlan': '333'},
              {'interface': 'Eth1/3/1', 'mac': '1c1b.0d83.e67d', 'vlan': '333'},
              {'interface': 'Eth1/8/1', 'mac': '1c1b.0d83.e685', 'vlan': '333'},
              {'interface': 'Eth1/6/4', 'mac': '1c1b.0d83.e6f9', 'vlan': '333'},
              {'interface': 'Eth1/6/1', 'mac': '1c1b.0d83.e711', 'vlan': '333'},
              {'interface': 'Eth1/6/3', 'mac': '1c1b.0d83.e715', 'vlan': '333'},
              {'interface': 'Eth1/8/2', 'mac': '1c1b.0d83.e721', 'vlan': '333'},
              {'interface': 'Eth1/2/2', 'mac': '1c1b.0d83.e725', 'vlan': '333'},
              {'interface': 'Eth1/2/4', 'mac': '1c1b.0d83.e74d', 'vlan': '333'},
              {'interface': 'Eth1/4/2', 'mac': '1c1b.0d83.e751', 'vlan': '333'},
              {'interface': 'Eth1/2/1', 'mac': '1c1b.0d83.e75d', 'vlan': '333'},
              {'interface': 'Eth1/2/3', 'mac': '1c1b.0d83.e765', 'vlan': '333'},
              {'interface': 'Eth1/4/1', 'mac': '1c1b.0d83.e781', 'vlan': '333'},
              {'interface': 'Eth1/4/3', 'mac': '1c1b.0d83.e785', 'vlan': '333'},
              {'interface': 'Eth1/4/4', 'mac': '1c1b.0d83.e78d', 'vlan': '333'},
              {'interface': 'Eth1/6/2', 'mac': '1c1b.0d83.e791', 'vlan': '333'}]
