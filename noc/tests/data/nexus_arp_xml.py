from data.lib import Data


class Data1(Data):
    content = """
<?xml version="1.0" encoding="ISO-8859-1"?>
<nf:rpc-reply xmlns:nf="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="http://www.cisco.com/nxos:1.0:arp">
 <nf:data>
  <show>
   <ip>
    <arp>
     <__XML__OPT_Cmd_arp_show_adj_cmd_ip-address>
      <__XML__OPT_Cmd_arp_show_adj_cmd___readonly__>
       <__readonly__>
        <TABLE_vrf>
         <ROW_vrf>
          <vrf-name-out>all</vrf-name-out>
          <cnt-total>5</cnt-total>
          <TABLE_adj>
           <ROW_adj>
            <intf-out>mgmt0</intf-out>
            <ip-addr-out>141.8.138.68</ip-addr-out>
            <time-stamp>00:00:59</time-stamp>
            <mac>0080.ea42.6308</mac>
           </ROW_adj>
           <ROW_adj>
            <intf-out>mgmt0</intf-out>
            <ip-addr-out>141.8.138.69</ip-addr-out>
            <time-stamp>00:02:10</time-stamp>
            <mac>0080.ea42.637d</mac>
           </ROW_adj>
           <ROW_adj>
            <intf-out>mgmt0</intf-out>
            <ip-addr-out>141.8.138.70</ip-addr-out>
            <time-stamp>00:01:38</time-stamp>
            <mac>0080.ea42.5e13</mac>
           </ROW_adj>
           <ROW_adj>
            <intf-out>mgmt0</intf-out>
            <ip-addr-out>141.8.138.71</ip-addr-out>
            <time-stamp>00:04:07</time-stamp>
            <mac>0080.ea42.5e37</mac>
           </ROW_adj>
           <ROW_adj>
            <intf-out>mgmt0</intf-out>
            <ip-addr-out>141.8.139.254</ip-addr-out>
            <time-stamp>00:14:44</time-stamp>
            <mac>001b.21a1.1bf9</mac>
           </ROW_adj>
          </TABLE_adj>
         </ROW_vrf>
        </TABLE_vrf>
       </__readonly__>
      </__XML__OPT_Cmd_arp_show_adj_cmd___readonly__>
     </__XML__OPT_Cmd_arp_show_adj_cmd_ip-address>
    </arp>
   </ip>
  </show>
 </nf:data>
</nf:rpc-reply>
]]>]]>
    """
    cmd = "show ip arp vrf all | xml"
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

Kernel uptime is 670 day(s), 2 hour(s), 38 minute(s), 9 second(s)

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
