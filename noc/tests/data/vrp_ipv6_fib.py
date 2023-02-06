from data.lib import Data


class Data1(Data):
    content = """
Route Flags: G - Gateway Route, H - Host Route,    U - Up Route
             S - Static Route,  D - Dynamic Route, B - Black Hole Route
--------------------------------------------------------------------------------
FIB Table:_public_
Total number of Routes: 9

Destination :  ::                                          PrefixLength : 0    
NHP         :  ::                                          Flag         : GSU  
Interface   :  NULL0                                       TunnelID     : -                    

Destination :  ::1                                         PrefixLength : 128  
NHP         :  ::1                                         Flag         : HU   
Interface   :  InLoopBack0                                 TunnelID     : -                    

Destination :  ::FFFF:127.0.0.0                            PrefixLength : 104  
NHP         :  ::FFFF:127.0.0.1                            Flag         : U    
Interface   :  InLoopBack0                                 TunnelID     : -                    

Destination :  ::FFFF:127.0.0.1                            PrefixLength : 128  
NHP         :  ::1                                         Flag         : HU   
Interface   :  InLoopBack0                                 TunnelID     : -                    

Destination :  64:FF9B::                                   PrefixLength : 64   
NHP         :  ::                                          Flag         : GSU  
Interface   :  NULL0                                       TunnelID     : -                    

Destination :  2A02::1                                     PrefixLength : 128  
NHP         :  ::1                                         Flag         : HU   
Interface   :  LoopBack1                                   TunnelID     : -                    

Destination :  2A02:6B8:B010:8004::                        PrefixLength : 64   
NHP         :  ::                                          Flag         : U    
Interface   :  NULL0                                       TunnelID     : -                    

Destination :  2A02:6B8:B010:8004::7850                    PrefixLength : 128  
NHP         :  ::                                          Flag         : HU   
Interface   :  MEth0/0/0                                   TunnelID     : -                    

Destination :  FE80::                                      PrefixLength : 10   
NHP         :  ::                                          Flag         : BU   
Interface   :  NULL0                                       TunnelID     : -                    
"""
    cmd = "display ipv6 fib slot 1 | no-more"
    host = "ce7850-test"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.150 (CE7850EI V200R002C50SPC800)
Copyright (C) 2012-2017 Huawei Technologies Co., Ltd.
HUAWEI CE7850-32Q-EI uptime is 389 days, 2 hours, 22 minutes

CE7850-32Q-EI(Master) 1 : uptime is  389 days, 2 hours, 21 minutes
        StartupTime 2017/08/31   10:37:59
Memory    Size    : 4096 M bytes
Flash     Size    : 1024 M bytes
NVRAM     Size    : 512  K bytes
CE7850-32Q-EI version information                              
1. PCB    Version : CEM32QP01    VER A
2. MAB    Version : 1
3. Board  Type    : CE7850-32Q-EI
4. CPLD1  Version : 101
5. CPLD2  Version : 101
6. BIOS   Version : 386
    """
    result = [
        {"Destination": "::", "PrefixLength": "0", "NHP": "::", "Flag": "GSU", "Interface": "NULL0", "TunnelID": "-"},
        {"Destination": "::1", "PrefixLength": "128", "NHP": "::1", "Flag": "HU", "Interface": "InLoopBack0",
         "TunnelID": "-"},
        {"Destination": "::FFFF:127.0.0.0", "PrefixLength": "104", "NHP": "::FFFF:127.0.0.1", "Flag": "U",
         "Interface": "InLoopBack0", "TunnelID": "-"},
        {"Destination": "::FFFF:127.0.0.1", "PrefixLength": "128", "NHP": "::1", "Flag": "HU",
         "Interface": "InLoopBack0", "TunnelID": "-"},
        {"Destination": "64:FF9B::", "PrefixLength": "64", "NHP": "::", "Flag": "GSU", "Interface": "NULL0",
         "TunnelID": "-"},
        {"Destination": "2A02::1", "PrefixLength": "128", "NHP": "::1", "Flag": "HU", "Interface": "LoopBack1",
         "TunnelID": "-"},
        {"Destination": "2A02:6B8:B010:8004::", "PrefixLength": "64", "NHP": "::", "Flag": "U", "Interface": "NULL0",
         "TunnelID": "-"},
        {"Destination": "2A02:6B8:B010:8004::7850", "PrefixLength": "128", "NHP": "::", "Flag": "HU",
         "Interface": "MEth0/0/0", "TunnelID": "-"},
        {"Destination": "FE80::", "PrefixLength": "10", "NHP": "::", "Flag": "BU", "Interface": "NULL0",
         "TunnelID": "-"}]


class Data2(Data):
    content = """
Route Flags: G - Gateway Route,  H - Host Route,  U - Up Route,  S - Static Route,  D - Dynamic Route,  B - Black Hole Route
-----------------------------------------------------------------------------------------------------------------------------------
 FIB Table:_public_
 Total number of Routes: 2566

 Destination/PrefixLength                     Nexthop                                  Flag  Interface                  TunnelID   
 ::/0                                         FE80::C1:D1                              DGU   Eth-Trunk1.3666             -         
                                              FE80::C1:D2                              DGU   Eth-Trunk2.3666             -         
 ::/1                                         FE80::C1:D1                              DGU   Eth-Trunk1.3666             -         
                                              FE80::C1:D2                              DGU   Eth-Trunk2.3666             -         
 ::1/128                                      ::1                                      HU    InLoopBack0                 -         
 ::FFFF:127.0.0.0/104                         ::FFFF:127.0.0.1                         U     InLoopBack0                 -         
 ::FFFF:127.0.0.1/128                         ::1                                      HU    InLoopBack0                 -         
 2A02:6B8::1/128                              2A02:6B8:0:1A6A::BA3A                    DGHU  Vlanif801                   -         
 2A02:6B8::2/128                              2A02:6B8:0:1A6A::BA7A                    DGHU  Vlanif801                   -         
 2A02:6B8::7/128                              2A02:6B8:0:1A6A::BA2A                    DGHU  Vlanif801                   -         
 2A02:6B8::8/128                              2A02:6B8:0:1A6A::BA2A                    DGHU  Vlanif801                   -         
 2A02:6B8::A/128                              2A02:6B8:0:1A6A::BA2A                    DGHU  Vlanif801                   -         
 2A02:6B8:0:3400::303/128                     2A02:6B8:0:1A6A::BA9A                    DGHU  Vlanif801                   -         
 2A02:6B8:0:3400::304/128                     2A02:6B8:0:1A6A::BA3A                    DGHU  Vlanif801                   -         
                                              2A02:6B8:0:1A6A::BA9A                    DGHU  Vlanif801                   -         
 2A02:6B8:0:3400::305/128                     2A02:6B8:0:1A6A::BA4A                    DGHU  Vlanif801                   -         
 2A02:6B8:0:3400::35F/128                     2A02:6B8:0:1A6A::BA4A                    DGHU  Vlanif801                   -         
 2A02:6B8:0:3400::366/128                     2A02:6B8:0:1A6A::BA4A                    DGHU  Vlanif801                   -                  
 2A02:6B8:B060:1100::/56                      FE80::F2                                 DGU   Vlanif802                   -         
                                              FE80::F3                                 DGU   Vlanif802                   -         
                                              FE80::F4                                 DGU   Vlanif802                   -         
                                              FE80::F5                                 DGU   Vlanif802                   -         
                                              FE80::F7                                 DGU   Vlanif802                   -         
                                              FE80::F8                                 DGU   Vlanif802                   -         
                                              FE80::F11                                DGU   Vlanif802                   -         
 FE80::/10                                    ::                                       BU    NULL0                       -          
    """
    cmd = "dis ipv6 fib slot 1 | no-more"
    host = "sas1-2a1"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.180 (CE8850EI V200R005C10SPC800)
Copyright (C) 2012-2018 Huawei Technologies Co., Ltd.
HUAWEI CE8850-32CQ-EI uptime is 0 day, 17 hours, 40 minutes
Patch Version: V200R005SPH013

CE8850-32CQ-EI(Master) 1 : uptime is  0 day, 17 hours, 39 minutes
        StartupTime 2020/01/30   18:48:31+03:00
Memory    Size    : 4096 M bytes
Flash     Size    : 1024 M bytes
CE8850-32CQ-EI version information                              
1. PCB    Version : CEM32CQP01    VER A
2. MAB    Version : 1
3. Board  Type    : CE8850-32CQ-EI
4. CPLD1  Version : 101
5. BIOS   Version : 192
    """
    result = [{'Destination/PrefixLength': '::/0', 'Flag': 'DGU', 'Interface': 'Eth-Trunk1.3666', 'Nexthop': 'FE80::C1:D1', 'TunnelID': '-'},
              {'Destination/PrefixLength': '::/0', 'Flag': 'DGU', 'Interface': 'Eth-Trunk2.3666', 'Nexthop': 'FE80::C1:D2', 'TunnelID': '-'},
              {'Destination/PrefixLength': '::/1', 'Flag': 'DGU', 'Interface': 'Eth-Trunk1.3666', 'Nexthop': 'FE80::C1:D1', 'TunnelID': '-'},
              {'Destination/PrefixLength': '::/1', 'Flag': 'DGU', 'Interface': 'Eth-Trunk2.3666', 'Nexthop': 'FE80::C1:D2', 'TunnelID': '-'},
              {'Destination/PrefixLength': '::1/128', 'Flag': 'HU', 'Interface': 'InLoopBack0', 'Nexthop': '::1', 'TunnelID': '-'},
              {'Destination/PrefixLength': '::FFFF:127.0.0.0/104', 'Flag': 'U', 'Interface': 'InLoopBack0', 'Nexthop': '::FFFF:127.0.0.1', 'TunnelID': '-'},
              {'Destination/PrefixLength': '::FFFF:127.0.0.1/128', 'Flag': 'HU', 'Interface': 'InLoopBack0', 'Nexthop': '::1', 'TunnelID': '-'},
              {'Destination/PrefixLength': '2A02:6B8::1/128', 'Flag': 'DGHU', 'Interface': 'Vlanif801', 'Nexthop': '2A02:6B8:0:1A6A::BA3A', 'TunnelID': '-'},
              {'Destination/PrefixLength': '2A02:6B8::2/128', 'Flag': 'DGHU', 'Interface': 'Vlanif801', 'Nexthop': '2A02:6B8:0:1A6A::BA7A', 'TunnelID': '-'},
              {'Destination/PrefixLength': '2A02:6B8::7/128', 'Flag': 'DGHU', 'Interface': 'Vlanif801', 'Nexthop': '2A02:6B8:0:1A6A::BA2A', 'TunnelID': '-'},
              {'Destination/PrefixLength': '2A02:6B8::8/128', 'Flag': 'DGHU', 'Interface': 'Vlanif801', 'Nexthop': '2A02:6B8:0:1A6A::BA2A', 'TunnelID': '-'},
              {'Destination/PrefixLength': '2A02:6B8::A/128', 'Flag': 'DGHU', 'Interface': 'Vlanif801', 'Nexthop': '2A02:6B8:0:1A6A::BA2A', 'TunnelID': '-'},
              {'Destination/PrefixLength': '2A02:6B8:0:3400::303/128', 'Flag': 'DGHU', 'Interface': 'Vlanif801', 'Nexthop': '2A02:6B8:0:1A6A::BA9A', 'TunnelID': '-'},
              {'Destination/PrefixLength': '2A02:6B8:0:3400::304/128', 'Flag': 'DGHU', 'Interface': 'Vlanif801', 'Nexthop': '2A02:6B8:0:1A6A::BA3A', 'TunnelID': '-'},
              {'Destination/PrefixLength': '2A02:6B8:0:3400::304/128', 'Flag': 'DGHU', 'Interface': 'Vlanif801', 'Nexthop': '2A02:6B8:0:1A6A::BA9A', 'TunnelID': '-'},
              {'Destination/PrefixLength': '2A02:6B8:0:3400::305/128', 'Flag': 'DGHU', 'Interface': 'Vlanif801', 'Nexthop': '2A02:6B8:0:1A6A::BA4A', 'TunnelID': '-'},
              {'Destination/PrefixLength': '2A02:6B8:0:3400::35F/128', 'Flag': 'DGHU', 'Interface': 'Vlanif801', 'Nexthop': '2A02:6B8:0:1A6A::BA4A', 'TunnelID': '-'},
              {'Destination/PrefixLength': '2A02:6B8:0:3400::366/128', 'Flag': 'DGHU', 'Interface': 'Vlanif801', 'Nexthop': '2A02:6B8:0:1A6A::BA4A', 'TunnelID': '-'},
              {'Destination/PrefixLength': '2A02:6B8:B060:1100::/56', 'Flag': 'DGU', 'Interface': 'Vlanif802', 'Nexthop': 'FE80::F2', 'TunnelID': '-'},
              {'Destination/PrefixLength': '2A02:6B8:B060:1100::/56', 'Flag': 'DGU', 'Interface': 'Vlanif802', 'Nexthop': 'FE80::F3', 'TunnelID': '-'},
              {'Destination/PrefixLength': '2A02:6B8:B060:1100::/56', 'Flag': 'DGU', 'Interface': 'Vlanif802', 'Nexthop': 'FE80::F4', 'TunnelID': '-'},
              {'Destination/PrefixLength': '2A02:6B8:B060:1100::/56', 'Flag': 'DGU', 'Interface': 'Vlanif802', 'Nexthop': 'FE80::F5', 'TunnelID': '-'},
              {'Destination/PrefixLength': '2A02:6B8:B060:1100::/56', 'Flag': 'DGU', 'Interface': 'Vlanif802', 'Nexthop': 'FE80::F7', 'TunnelID': '-'},
              {'Destination/PrefixLength': '2A02:6B8:B060:1100::/56', 'Flag': 'DGU', 'Interface': 'Vlanif802', 'Nexthop': 'FE80::F8', 'TunnelID': '-'},
              {'Destination/PrefixLength': '2A02:6B8:B060:1100::/56', 'Flag': 'DGU', 'Interface': 'Vlanif802', 'Nexthop': 'FE80::F11', 'TunnelID': '-'},
              {'Destination/PrefixLength': 'FE80::/10', 'Flag': 'BU', 'Interface': 'NULL0', 'Nexthop': '::', 'TunnelID': '-'}]
