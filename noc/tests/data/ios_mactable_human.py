from data.lib import Data


class Data1(Data):
    content = """
          Mac Address Table
-------------------------------------------

Vlan    Mac Address       Type        Ports
----    -----------       --------    -----
 All    0100.0ccc.cccc    STATIC      CPU
 All    0100.0ccc.cccd    STATIC      CPU
 All    0100.0ccc.ccce    STATIC      CPU
 All    0180.c200.0000    STATIC      CPU
 All    0180.c200.0001    STATIC      CPU
 All    0180.c200.0002    STATIC      CPU
 All    0180.c200.0003    STATIC      CPU
 All    0180.c200.0004    STATIC      CPU
 All    0180.c200.0005    STATIC      CPU
 All    0180.c200.0006    STATIC      CPU
 All    0180.c200.0007    STATIC      CPU
 All    0180.c200.0008    STATIC      CPU
 All    0180.c200.0009    STATIC      CPU
 All    0180.c200.000a    STATIC      CPU
 All    0180.c200.000b    STATIC      CPU
 All    0180.c200.000c    STATIC      CPU
 All    0180.c200.000d    STATIC      CPU
 All    0180.c200.000e    STATIC      CPU
 All    0180.c200.000f    STATIC      CPU
 All    0180.c200.0010    STATIC      CPU
 All    ffff.ffff.ffff    STATIC      CPU
   1    0025.90eb.feec    DYNAMIC     Gi1/0/48
   1    00fc.bafb.ea33    DYNAMIC     Gi1/1/3
   1    7079.b33c.ecb3    DYNAMIC     Gi1/1/2
 400    0025.90c8.ca82    DYNAMIC     Gi1/1/3
 400    00fc.bafb.e452    STATIC      Vl400
 400    0c27.2491.f850    DYNAMIC     Gi1/0/10
 400    0c27.2493.f800    DYNAMIC     Gi1/0/10
 400    0c68.03af.e9d0    DYNAMIC     Gi1/0/14
 400    1ce6.c73f.8530    DYNAMIC     Gi1/0/4
 400    1ce6.c741.84e0    DYNAMIC     Gi1/0/4
 400    3c08.f6a2.ebf0    DYNAMIC     Gi1/0/9
 400    3c08.f6a2.ec03    DYNAMIC     Gi1/0/7
 400    3c08.f6b2.b231    DYNAMIC     Gi1/0/5
 400    501c.bfb4.efe0    DYNAMIC     Gi1/0/5
 400    501c.bfb6.efd0    DYNAMIC     Gi1/0/5
 400    580a.205a.5a50    DYNAMIC     Gi1/0/9
 400    580a.205a.5ba0    DYNAMIC     Gi1/0/7
 400    580a.2066.57d0    DYNAMIC     Gi1/0/9
 400    64e9.5032.7d30    DYNAMIC     Gi1/0/2
 400    6c20.56e6.89dd    DYNAMIC     Gi1/0/4
 400    6c41.6a29.7de4    DYNAMIC     Gi1/0/8
 400    6c41.6a29.7e6b    DYNAMIC     Gi1/0/11
 400    6c41.6aa3.8211    DYNAMIC     Gi1/0/12
 400    6c41.6ab1.fdc5    DYNAMIC     Gi1/0/10
 400    6c41.6ab2.1eb5    DYNAMIC     Gi1/0/14
 400    7079.b33c.ecd2    DYNAMIC     Gi1/1/2
 400    d0c7.8909.b720    DYNAMIC     Gi1/0/8
 400    d0c7.8909.bfe0    DYNAMIC     Gi1/0/11
 400    d0c7.890b.b700    DYNAMIC     Gi1/0/8
 400    d0c7.890b.bfc0    DYNAMIC     Gi1/0/11
 400    d0c7.8967.bfb0    DYNAMIC     Gi1/0/12
 400    d0c7.8969.bf50    DYNAMIC     Gi1/0/12
 400    e4c7.2281.30c2    DYNAMIC     Gi1/0/6
 400    e4c7.2281.314e    DYNAMIC     Gi1/0/2
 400    f872.ea60.6191    DYNAMIC     Gi1/0/1
 400    f872.ea60.61e0    DYNAMIC     Gi1/0/13
 400    f872.ea60.620e    DYNAMIC     Gi1/0/3
 814    000e.5e5f.2314    DYNAMIC     Gi1/1/4
 814    001d.7198.0080    DYNAMIC     Gi1/1/4
 814    0025.90c8.ca82    DYNAMIC     Gi1/1/3
 814    0025.90cd.e566    DYNAMIC     Gi1/1/3
 814    0025.90eb.feed    DYNAMIC     Gi1/1/1
 401    0025.90c8.ca82    DYNAMIC     Gi1/1/3
 401    0025.90eb.feec    DYNAMIC     Gi1/0/48
 410    0025.90c8.ca82    DYNAMIC     Gi1/1/3
 416    0025.90c8.ca82    DYNAMIC     Gi1/1/3
 419    0025.90c8.ca82    DYNAMIC     Gi1/1/3
 419    14dd.a9c7.096f    DYNAMIC     Gi1/0/7
 419    5427.5860.e535    DYNAMIC     Gi1/0/3
 419    5427.5860.e66b    DYNAMIC     Gi1/0/2
 419    5427.5860.e726    DYNAMIC     Gi1/0/9
 419    5427.5860.e7b7    DYNAMIC     Gi1/0/9
 419    5427.5860.e85d    DYNAMIC     Gi1/0/14
 419    5427.5860.e8d8    DYNAMIC     Gi1/0/2
 419    5427.5860.ea72    DYNAMIC     Gi1/0/12
 419    5427.5860.eb7d    DYNAMIC     Gi1/0/3
 419    5427.5860.ec48    DYNAMIC     Gi1/0/2
 419    980c.a5c7.a64e    DYNAMIC     Gi1/0/3
 419    980c.a5c8.20a4    DYNAMIC     Gi1/0/3
 419    980c.a5c8.24dd    DYNAMIC     Gi1/0/3
 419    980c.a5c8.258d    DYNAMIC     Gi1/0/3
 419    980c.a5c8.25d3    DYNAMIC     Gi1/0/3
 419    980c.a5c8.2641    DYNAMIC     Gi1/0/3
 419    980c.a5c8.2642    DYNAMIC     Gi1/0/3
 423    0025.90c8.ca82    DYNAMIC     Gi1/1/3
 423    241b.7acf.4e48    DYNAMIC     Gi1/0/11
 423    505b.c2b2.7fff    DYNAMIC     Gi1/0/10
 423    505b.c2b2.801d    DYNAMIC     Gi1/0/10
 423    505b.c2b2.8037    DYNAMIC     Gi1/0/10
 423    505b.c2b2.804b    DYNAMIC     Gi1/0/10
 423    505b.c2b2.805b    DYNAMIC     Gi1/0/11
 423    505b.c2b2.8ba7    DYNAMIC     Gi1/0/11
 423    505b.c2b2.8bab    DYNAMIC     Gi1/0/10
 423    9822.effd.a3e3    DYNAMIC     Gi1/0/10
 423    98de.d099.0915    DYNAMIC     Gi1/0/10
 423    a056.f328.bb0c    DYNAMIC     Gi1/0/5
 423    acd1.b813.0021    DYNAMIC     Gi1/0/5
 423    c025.e92d.cc5d    DYNAMIC     Gi1/0/10
 423    ec08.6b43.515d    DYNAMIC     Gi1/0/10
 423    f076.6f9f.3269    DYNAMIC     Gi1/0/10
 428    0025.90c8.ca82    DYNAMIC     Gi1/1/3
 428    00c0.eeae.272d    DYNAMIC     Gi1/1/2
 428    1062.e55f.6692    DYNAMIC     Gi1/1/3
 428    10e7.c664.49bb    DYNAMIC     Gi1/1/3
 428    b4b6.867c.3e82    DYNAMIC     Gi1/1/3
 428    b4b6.86c0.a7d3    DYNAMIC     Gi1/1/3
 428    b4b6.86c0.b78d    DYNAMIC     Gi1/1/3
 428    f430.b9ee.cb53    DYNAMIC     Gi1/1/3
 428    f430.b9f2.612c    DYNAMIC     Gi1/1/3
 429    0025.90c8.ca82    DYNAMIC     Gi1/1/3
 434    0025.90c8.ca82    DYNAMIC     Gi1/1/3
 435    0025.90c8.ca82    DYNAMIC     Gi1/1/3
 440    0025.90c8.ca82    DYNAMIC     Gi1/1/3
 441    0025.90c8.ca82    DYNAMIC     Gi1/1/3
 461    000f.e501.ad91    DYNAMIC     Gi1/1/3
 461    0025.9092.f7a8    DYNAMIC     Gi1/1/2
 461    0025.90c8.ca82    DYNAMIC     Gi1/1/3
 465    0025.90c8.ca82    DYNAMIC     Gi1/1/3
 811    0025.90eb.feec    DYNAMIC     Gi1/0/48
 811    0cc4.7a1a.8523    DYNAMIC     Gi1/0/47
 811    ac4e.9148.2826    DYNAMIC     Gi1/1/3
 462    accc.8ea9.90a2    DYNAMIC     Gi1/0/28
 462    accc.8ea9.90d4    DYNAMIC     Gi1/0/29
 462    accc.8ea9.92fa    DYNAMIC     Gi1/0/17
 462    accc.8ea9.93f5    DYNAMIC     Gi1/0/24
 462    accc.8ea9.93fe    DYNAMIC     Gi1/0/21
 462    accc.8ea9.9410    DYNAMIC     Gi1/0/26
 462    accc.8ea9.941d    STATIC      Gi1/0/16
 462    accc.8ea9.9420    DYNAMIC     Gi1/0/20
 462    accc.8ea9.9459    DYNAMIC     Gi1/0/22
 462    accc.8ea9.945b    DYNAMIC     Gi1/0/15
 462    accc.8eb5.9937    DYNAMIC     Gi1/0/31
 412    0025.909d.b819    DYNAMIC     Gi1/1/3
 412    0025.90c8.ca82    DYNAMIC     Gi1/1/3
 412    0025.90cd.b3f7    DYNAMIC     Gi1/1/3
Total Mac Addresses for this criterion: 136
    """
    cmd = "show mac address-table"
    host = "bruber-u5"
    version = """
Cisco IOS Software, IOS-XE Software, Catalyst L3 Switch Software (CAT3K_CAA-UNIVERSALK9-M), Version 03.06.08.E RELEASE SOFTWARE (fc1)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2018 by Cisco Systems, Inc.
Compiled Mon 22-Jan-18 05:56 by prod_rel_team



Cisco IOS-XE software, Copyright (c) 2005-2015 by cisco Systems, Inc.
All rights reserved.  Certain components of Cisco IOS-XE software are
licensed under the GNU General Public License ("GPL") Version 2.0.  The
software code licensed under GPL Version 2.0 is free software that comes
with ABSOLUTELY NO WARRANTY.  You can redistribute and/or modify such
GPL code under the terms of GPL Version 2.0.
(http://www.gnu.org/licenses/gpl-2.0.html) For more details, see the
documentation or "License Notice" file accompanying the IOS-XE software,
or the applicable URL provided on the flyer accompanying the IOS-XE
software.



ROM: IOS-XE ROMMON
BOOTLDR: CAT3K_CAA Boot Loader (CAT3K_CAA-HBOOT-M) Version 3.56, RELEASE SOFTWARE (P)

bruber-u5 uptime is 2 weeks, 5 days, 21 hours, 38 minutes
Uptime for this control processor is 2 weeks, 5 days, 21 hours, 42 minutes
System returned to ROM by Power Failure at 15:36:36 MSK Sat Dec 22 2018
System restarted at 15:50:00 MSK Mon Dec 24 2018
System image file is "flash:/cat3k_caa-universalk9.SPA.03.06.08.E.152-2.E8.bin"
Last reload reason: Power Failure



This product contains cryptographic features and is subject to United
States and local country laws governing import, export, transfer and
use. Delivery of Cisco cryptographic products does not imply
third-party authority to import, export, distribute or use encryption.
Importers, exporters, distributors and users are responsible for
compliance with U.S. and local country laws. By using this product you
agree to comply with applicable laws and regulations. If you are unable
to comply with U.S. and local laws, return this product immediately.

A summary of U.S. laws governing Cisco cryptographic products may be found at:
http://www.cisco.com/wwl/export/crypto/tool/stqrg.html

If you require further assistance please contact us by sending email to
export@cisco.com.

License Level: Lanbase
License Type: Permanent
Next reload license Level: Lanbase

cisco WS-C3650-48PS (MIPS) processor with 4194304K bytes of physical memory.
Processor board ID FDO2211E14B
2 Virtual Ethernet interfaces
52 Gigabit Ethernet interfaces
2048K bytes of non-volatile configuration memory.
4194304K bytes of physical memory.
250456K bytes of Crash Files at crashinfo:.
1609272K bytes of Flash at flash:.
0K bytes of Dummy USB Flash at usbflash0:.
0K bytes of  at webui:.

Base Ethernet MAC Address          : 00:fc:ba:fb:e4:00
Motherboard Assembly Number        : 73-15901-06
Motherboard Serial Number          : FDO22110GX8
Model Revision Number              : T0
Motherboard Revision Number        : B0
Model Number                       : WS-C3650-48PS
System Serial Number               : FDO2211E14B


Switch Ports Model              SW Version        SW Image              Mode  
------ ----- -----              ----------        ----------            ----  
*    1 52    WS-C3650-48PS      03.06.08.E        cat3k_caa-universalk9 BUNDLE


Configuration register is 0x102
    """
    result = [{'interface': 'Gi1/0/48', 'mac': '0025.90eb.feec', 'vlan': '1'},
              {'interface': 'Gi1/1/3', 'mac': '00fc.bafb.ea33', 'vlan': '1'},
              {'interface': 'Gi1/1/2', 'mac': '7079.b33c.ecb3', 'vlan': '1'},
              {'interface': 'Gi1/1/3', 'mac': '0025.90c8.ca82', 'vlan': '400'},
              {'interface': 'Vl400', 'mac': '00fc.bafb.e452', 'vlan': '400'},
              {'interface': 'Gi1/0/10', 'mac': '0c27.2491.f850', 'vlan': '400'},
              {'interface': 'Gi1/0/10', 'mac': '0c27.2493.f800', 'vlan': '400'},
              {'interface': 'Gi1/0/14', 'mac': '0c68.03af.e9d0', 'vlan': '400'},
              {'interface': 'Gi1/0/4', 'mac': '1ce6.c73f.8530', 'vlan': '400'},
              {'interface': 'Gi1/0/4', 'mac': '1ce6.c741.84e0', 'vlan': '400'},
              {'interface': 'Gi1/0/9', 'mac': '3c08.f6a2.ebf0', 'vlan': '400'},
              {'interface': 'Gi1/0/7', 'mac': '3c08.f6a2.ec03', 'vlan': '400'},
              {'interface': 'Gi1/0/5', 'mac': '3c08.f6b2.b231', 'vlan': '400'},
              {'interface': 'Gi1/0/5', 'mac': '501c.bfb4.efe0', 'vlan': '400'},
              {'interface': 'Gi1/0/5', 'mac': '501c.bfb6.efd0', 'vlan': '400'},
              {'interface': 'Gi1/0/9', 'mac': '580a.205a.5a50', 'vlan': '400'},
              {'interface': 'Gi1/0/7', 'mac': '580a.205a.5ba0', 'vlan': '400'},
              {'interface': 'Gi1/0/9', 'mac': '580a.2066.57d0', 'vlan': '400'},
              {'interface': 'Gi1/0/2', 'mac': '64e9.5032.7d30', 'vlan': '400'},
              {'interface': 'Gi1/0/4', 'mac': '6c20.56e6.89dd', 'vlan': '400'},
              {'interface': 'Gi1/0/8', 'mac': '6c41.6a29.7de4', 'vlan': '400'},
              {'interface': 'Gi1/0/11', 'mac': '6c41.6a29.7e6b', 'vlan': '400'},
              {'interface': 'Gi1/0/12', 'mac': '6c41.6aa3.8211', 'vlan': '400'},
              {'interface': 'Gi1/0/10', 'mac': '6c41.6ab1.fdc5', 'vlan': '400'},
              {'interface': 'Gi1/0/14', 'mac': '6c41.6ab2.1eb5', 'vlan': '400'},
              {'interface': 'Gi1/1/2', 'mac': '7079.b33c.ecd2', 'vlan': '400'},
              {'interface': 'Gi1/0/8', 'mac': 'd0c7.8909.b720', 'vlan': '400'},
              {'interface': 'Gi1/0/11', 'mac': 'd0c7.8909.bfe0', 'vlan': '400'},
              {'interface': 'Gi1/0/8', 'mac': 'd0c7.890b.b700', 'vlan': '400'},
              {'interface': 'Gi1/0/11', 'mac': 'd0c7.890b.bfc0', 'vlan': '400'},
              {'interface': 'Gi1/0/12', 'mac': 'd0c7.8967.bfb0', 'vlan': '400'},
              {'interface': 'Gi1/0/12', 'mac': 'd0c7.8969.bf50', 'vlan': '400'},
              {'interface': 'Gi1/0/6', 'mac': 'e4c7.2281.30c2', 'vlan': '400'},
              {'interface': 'Gi1/0/2', 'mac': 'e4c7.2281.314e', 'vlan': '400'},
              {'interface': 'Gi1/0/1', 'mac': 'f872.ea60.6191', 'vlan': '400'},
              {'interface': 'Gi1/0/13', 'mac': 'f872.ea60.61e0', 'vlan': '400'},
              {'interface': 'Gi1/0/3', 'mac': 'f872.ea60.620e', 'vlan': '400'},
              {'interface': 'Gi1/1/4', 'mac': '000e.5e5f.2314', 'vlan': '814'},
              {'interface': 'Gi1/1/4', 'mac': '001d.7198.0080', 'vlan': '814'},
              {'interface': 'Gi1/1/3', 'mac': '0025.90c8.ca82', 'vlan': '814'},
              {'interface': 'Gi1/1/3', 'mac': '0025.90cd.e566', 'vlan': '814'},
              {'interface': 'Gi1/1/1', 'mac': '0025.90eb.feed', 'vlan': '814'},
              {'interface': 'Gi1/1/3', 'mac': '0025.90c8.ca82', 'vlan': '401'},
              {'interface': 'Gi1/0/48', 'mac': '0025.90eb.feec', 'vlan': '401'},
              {'interface': 'Gi1/1/3', 'mac': '0025.90c8.ca82', 'vlan': '410'},
              {'interface': 'Gi1/1/3', 'mac': '0025.90c8.ca82', 'vlan': '416'},
              {'interface': 'Gi1/1/3', 'mac': '0025.90c8.ca82', 'vlan': '419'},
              {'interface': 'Gi1/0/7', 'mac': '14dd.a9c7.096f', 'vlan': '419'},
              {'interface': 'Gi1/0/3', 'mac': '5427.5860.e535', 'vlan': '419'},
              {'interface': 'Gi1/0/2', 'mac': '5427.5860.e66b', 'vlan': '419'},
              {'interface': 'Gi1/0/9', 'mac': '5427.5860.e726', 'vlan': '419'},
              {'interface': 'Gi1/0/9', 'mac': '5427.5860.e7b7', 'vlan': '419'},
              {'interface': 'Gi1/0/14', 'mac': '5427.5860.e85d', 'vlan': '419'},
              {'interface': 'Gi1/0/2', 'mac': '5427.5860.e8d8', 'vlan': '419'},
              {'interface': 'Gi1/0/12', 'mac': '5427.5860.ea72', 'vlan': '419'},
              {'interface': 'Gi1/0/3', 'mac': '5427.5860.eb7d', 'vlan': '419'},
              {'interface': 'Gi1/0/2', 'mac': '5427.5860.ec48', 'vlan': '419'},
              {'interface': 'Gi1/0/3', 'mac': '980c.a5c7.a64e', 'vlan': '419'},
              {'interface': 'Gi1/0/3', 'mac': '980c.a5c8.20a4', 'vlan': '419'},
              {'interface': 'Gi1/0/3', 'mac': '980c.a5c8.24dd', 'vlan': '419'},
              {'interface': 'Gi1/0/3', 'mac': '980c.a5c8.258d', 'vlan': '419'},
              {'interface': 'Gi1/0/3', 'mac': '980c.a5c8.25d3', 'vlan': '419'},
              {'interface': 'Gi1/0/3', 'mac': '980c.a5c8.2641', 'vlan': '419'},
              {'interface': 'Gi1/0/3', 'mac': '980c.a5c8.2642', 'vlan': '419'},
              {'interface': 'Gi1/1/3', 'mac': '0025.90c8.ca82', 'vlan': '423'},
              {'interface': 'Gi1/0/11', 'mac': '241b.7acf.4e48', 'vlan': '423'},
              {'interface': 'Gi1/0/10', 'mac': '505b.c2b2.7fff', 'vlan': '423'},
              {'interface': 'Gi1/0/10', 'mac': '505b.c2b2.801d', 'vlan': '423'},
              {'interface': 'Gi1/0/10', 'mac': '505b.c2b2.8037', 'vlan': '423'},
              {'interface': 'Gi1/0/10', 'mac': '505b.c2b2.804b', 'vlan': '423'},
              {'interface': 'Gi1/0/11', 'mac': '505b.c2b2.805b', 'vlan': '423'},
              {'interface': 'Gi1/0/11', 'mac': '505b.c2b2.8ba7', 'vlan': '423'},
              {'interface': 'Gi1/0/10', 'mac': '505b.c2b2.8bab', 'vlan': '423'},
              {'interface': 'Gi1/0/10', 'mac': '9822.effd.a3e3', 'vlan': '423'},
              {'interface': 'Gi1/0/10', 'mac': '98de.d099.0915', 'vlan': '423'},
              {'interface': 'Gi1/0/5', 'mac': 'a056.f328.bb0c', 'vlan': '423'},
              {'interface': 'Gi1/0/5', 'mac': 'acd1.b813.0021', 'vlan': '423'},
              {'interface': 'Gi1/0/10', 'mac': 'c025.e92d.cc5d', 'vlan': '423'},
              {'interface': 'Gi1/0/10', 'mac': 'ec08.6b43.515d', 'vlan': '423'},
              {'interface': 'Gi1/0/10', 'mac': 'f076.6f9f.3269', 'vlan': '423'},
              {'interface': 'Gi1/1/3', 'mac': '0025.90c8.ca82', 'vlan': '428'},
              {'interface': 'Gi1/1/2', 'mac': '00c0.eeae.272d', 'vlan': '428'},
              {'interface': 'Gi1/1/3', 'mac': '1062.e55f.6692', 'vlan': '428'},
              {'interface': 'Gi1/1/3', 'mac': '10e7.c664.49bb', 'vlan': '428'},
              {'interface': 'Gi1/1/3', 'mac': 'b4b6.867c.3e82', 'vlan': '428'},
              {'interface': 'Gi1/1/3', 'mac': 'b4b6.86c0.a7d3', 'vlan': '428'},
              {'interface': 'Gi1/1/3', 'mac': 'b4b6.86c0.b78d', 'vlan': '428'},
              {'interface': 'Gi1/1/3', 'mac': 'f430.b9ee.cb53', 'vlan': '428'},
              {'interface': 'Gi1/1/3', 'mac': 'f430.b9f2.612c', 'vlan': '428'},
              {'interface': 'Gi1/1/3', 'mac': '0025.90c8.ca82', 'vlan': '429'},
              {'interface': 'Gi1/1/3', 'mac': '0025.90c8.ca82', 'vlan': '434'},
              {'interface': 'Gi1/1/3', 'mac': '0025.90c8.ca82', 'vlan': '435'},
              {'interface': 'Gi1/1/3', 'mac': '0025.90c8.ca82', 'vlan': '440'},
              {'interface': 'Gi1/1/3', 'mac': '0025.90c8.ca82', 'vlan': '441'},
              {'interface': 'Gi1/1/3', 'mac': '000f.e501.ad91', 'vlan': '461'},
              {'interface': 'Gi1/1/2', 'mac': '0025.9092.f7a8', 'vlan': '461'},
              {'interface': 'Gi1/1/3', 'mac': '0025.90c8.ca82', 'vlan': '461'},
              {'interface': 'Gi1/1/3', 'mac': '0025.90c8.ca82', 'vlan': '465'},
              {'interface': 'Gi1/0/48', 'mac': '0025.90eb.feec', 'vlan': '811'},
              {'interface': 'Gi1/0/47', 'mac': '0cc4.7a1a.8523', 'vlan': '811'},
              {'interface': 'Gi1/1/3', 'mac': 'ac4e.9148.2826', 'vlan': '811'},
              {'interface': 'Gi1/0/28', 'mac': 'accc.8ea9.90a2', 'vlan': '462'},
              {'interface': 'Gi1/0/29', 'mac': 'accc.8ea9.90d4', 'vlan': '462'},
              {'interface': 'Gi1/0/17', 'mac': 'accc.8ea9.92fa', 'vlan': '462'},
              {'interface': 'Gi1/0/24', 'mac': 'accc.8ea9.93f5', 'vlan': '462'},
              {'interface': 'Gi1/0/21', 'mac': 'accc.8ea9.93fe', 'vlan': '462'},
              {'interface': 'Gi1/0/26', 'mac': 'accc.8ea9.9410', 'vlan': '462'},
              {'interface': 'Gi1/0/16', 'mac': 'accc.8ea9.941d', 'vlan': '462'},
              {'interface': 'Gi1/0/20', 'mac': 'accc.8ea9.9420', 'vlan': '462'},
              {'interface': 'Gi1/0/22', 'mac': 'accc.8ea9.9459', 'vlan': '462'},
              {'interface': 'Gi1/0/15', 'mac': 'accc.8ea9.945b', 'vlan': '462'},
              {'interface': 'Gi1/0/31', 'mac': 'accc.8eb5.9937', 'vlan': '462'},
              {'interface': 'Gi1/1/3', 'mac': '0025.909d.b819', 'vlan': '412'},
              {'interface': 'Gi1/1/3', 'mac': '0025.90c8.ca82', 'vlan': '412'},
              {'interface': 'Gi1/1/3', 'mac': '0025.90cd.b3f7', 'vlan': '412'}]
