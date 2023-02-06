from data.lib import Data


class Data1(Data):
    content = """
Route Flags: R - relay, D - download to fib, B - black hole route
------------------------------------------------------------------------------
Routing Table : _public_
         Destinations : 11       Routes : 11       

Format :
Destination/Mask                             Protocol
Nexthop                                      Interface
------------------------------------------------------------------------------
 ::/0                                        Static                            
  2A02:6B8:B010:8004::1                      MEth0/0/0                         
 ::1/128                                     Direct                            
  ::1                                        InLoopBack0                       
 ::FFFF:127.0.0.0/104                        Direct                            
  ::FFFF:127.0.0.1                           InLoopBack0                       
 ::FFFF:127.0.0.1/128                        Direct                            
  ::1                                        InLoopBack0                       
 64:FF9B::/64                                Static                            
  2A02:6B8:B010:8004::1                      MEth0/0/0                         
 64:FF9B::/96                                Static                            
  2A02:6B8:B010:8004::1                      MEth0/0/0                         
 2A02::1/128                                 Direct                            
  ::1                                        LoopBack1                         
 2A02:6B8::/96                               Static                            
  2A02:6B8:B010:8004::1                      MEth0/0/0                         
 2A02:6B8:B010:8004::/64                     Direct                            
  2A02:6B8:B010:8004::7850                   MEth0/0/0                         
 2A02:6B8:B010:8004::7850/128                Direct                            
  ::1                                        MEth0/0/0                         
 FE80::/10                                   Direct                            
  ::                                         NULL0                              
    """
    cmd = "dis ipv6 routing brief | no-more"
    host = "ce7850-test"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.150 (CE7850EI V200R002C50SPC800)
Copyright (C) 2012-2017 Huawei Technologies Co., Ltd.
HUAWEI CE7850-32Q-EI uptime is 386 days, 6 hours, 33 minutes

CE7850-32Q-EI(Master) 1 : uptime is  386 days, 6 hours, 32 minutes
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
    result = [{"Destination/Mask": "::/0", "Protocol": "Static", "Nexthop": "2A02:6B8:B010:8004::1",
               "Interface": "MEth0/0/0"},
              {"Destination/Mask": "::1/128", "Protocol": "Direct", "Nexthop": "::1", "Interface": "InLoopBack0"},
              {"Destination/Mask": "::FFFF:127.0.0.0/104", "Protocol": "Direct", "Nexthop": "::FFFF:127.0.0.1",
               "Interface": "InLoopBack0"},
              {"Destination/Mask": "::FFFF:127.0.0.1/128", "Protocol": "Direct", "Nexthop": "::1",
               "Interface": "InLoopBack0"},
              {"Destination/Mask": "64:FF9B::/64", "Protocol": "Static", "Nexthop": "2A02:6B8:B010:8004::1",
               "Interface": "MEth0/0/0"},
              {"Destination/Mask": "64:FF9B::/96", "Protocol": "Static", "Nexthop": "2A02:6B8:B010:8004::1",
               "Interface": "MEth0/0/0"},
              {"Destination/Mask": "2A02::1/128", "Protocol": "Direct", "Nexthop": "::1", "Interface": "LoopBack1"},
              {"Destination/Mask": "2A02:6B8::/96", "Protocol": "Static", "Nexthop": "2A02:6B8:B010:8004::1",
               "Interface": "MEth0/0/0"}, {"Destination/Mask": "2A02:6B8:B010:8004::/64", "Protocol": "Direct",
                                           "Nexthop": "2A02:6B8:B010:8004::7850", "Interface": "MEth0/0/0"},
              {"Destination/Mask": "2A02:6B8:B010:8004::7850/128", "Protocol": "Direct", "Nexthop": "::1",
               "Interface": "MEth0/0/0"},
              {"Destination/Mask": "FE80::/10", "Protocol": "Direct", "Nexthop": "::",
               "Interface": "NULL0"},
              ]
