from data.lib import Data


class Data1(Data):
    content = """
Route Flags: R - relay, D - download to fib, B - black hole route
------------------------------------------------------------------------------
Routing Table : _public_
         Destinations : 11       Routes : 11

Destination  : ::                                      PrefixLength : 0
NextHop      : 2A02:6B8:B010:8004::1                   Preference   : 60
Cost         : 0                                       Protocol     : Static
RelayNextHop : 2A02:6B8:B010:8004::1                   TunnelID     : 0x0
Interface    : MEth0/0/0                               Flags        : RD

Destination  : ::1                                     PrefixLength : 128
NextHop      : ::1                                     Preference   : 0
Cost         : 0                                       Protocol     : Direct
RelayNextHop : ::                                      TunnelID     : 0x0
Interface    : InLoopBack0                             Flags        : D

Destination  : ::FFFF:127.0.0.0                        PrefixLength : 104
NextHop      : ::FFFF:127.0.0.1                        Preference   : 0
Cost         : 0                                       Protocol     : Direct
RelayNextHop : ::                                      TunnelID     : 0x0
Interface    : InLoopBack0                             Flags        : D

Destination  : ::FFFF:127.0.0.1                        PrefixLength : 128
NextHop      : ::1                                     Preference   : 0
Cost         : 0                                       Protocol     : Direct
RelayNextHop : ::                                      TunnelID     : 0x0
Interface    : InLoopBack0                             Flags        : D

Destination  : 64:FF9B::                               PrefixLength : 64
NextHop      : 2A02:6B8:B010:8004::1                   Preference   : 60
Cost         : 0                                       Protocol     : Static
RelayNextHop : 2A02:6B8:B010:8004::1                   TunnelID     : 0x0
Interface    : MEth0/0/0                               Flags        : RD

Destination  : 64:FF9B::                               PrefixLength : 96
NextHop      : 2A02:6B8:B010:8004::1                   Preference   : 60
Cost         : 0                                       Protocol     : Static
RelayNextHop : 2A02:6B8:B010:8004::1                   TunnelID     : 0x0
Interface    : MEth0/0/0                               Flags        : RD

Destination  : 2A02::1                                 PrefixLength : 128
NextHop      : ::1                                     Preference   : 0
Cost         : 0                                       Protocol     : Direct
RelayNextHop : ::                                      TunnelID     : 0x0
Interface    : LoopBack1                               Flags        : D

Destination  : 2A02:6B8::                              PrefixLength : 96
NextHop      : 2A02:6B8:B010:8004::1                   Preference   : 60
Cost         : 0                                       Protocol     : Static
RelayNextHop : 2A02:6B8:B010:8004::1                   TunnelID     : 0x0
Interface    : MEth0/0/0                               Flags        : RD

Destination  : 2A02:6B8:B010:8004::                    PrefixLength : 64
NextHop      : 2A02:6B8:B010:8004::7850                Preference   : 0
Cost         : 0                                       Protocol     : Direct
RelayNextHop : ::                                      TunnelID     : 0x0
Interface    : MEth0/0/0                               Flags        : D

Destination  : 2A02:6B8:B010:8004::7850                PrefixLength : 128
NextHop      : ::1                                     Preference   : 0
Cost         : 0                                       Protocol     : Direct
RelayNextHop : ::                                      TunnelID     : 0x0
Interface    : MEth0/0/0                               Flags        : D

Destination  : FE80::                                  PrefixLength : 10
NextHop      : ::                                      Preference   : 0
Cost         : 0                                       Protocol     : Direct
RelayNextHop : ::                                      TunnelID     : 0x0
Interface    : NULL0                                   Flags        : DB
    """
    cmd = "dis ipv6 routing"
    host = "ce7850-test"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.150 (CE7850EI V200R002C50SPC800)
Copyright (C) 2012-2017 Huawei Technologies Co., Ltd.
HUAWEI CE7850-32Q-EI uptime is 386 days, 5 hours, 28 minutes

CE7850-32Q-EI(Master) 1 : uptime is  386 days, 5 hours, 27 minutes
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
        {"Destination": "::", "PrefixLength": "0", "NextHop": "2A02:6B8:B010:8004::1", "Preference": "60", "Cost": "0",
         "Protocol": "Static", "RelayNextHop": "2A02:6B8:B010:8004::1", "TunnelID": "0x0", "Interface": "MEth0/0/0",
         "Flags": "RD"},
        {"Destination": "::1", "PrefixLength": "128", "NextHop": "::1", "Preference": "0", "Cost": "0",
         "Protocol": "Direct", "RelayNextHop": "::", "TunnelID": "0x0", "Interface": "InLoopBack0", "Flags": "D"},
        {"Destination": "::FFFF:127.0.0.0", "PrefixLength": "104", "NextHop": "::FFFF:127.0.0.1", "Preference": "0",
         "Cost": "0", "Protocol": "Direct", "RelayNextHop": "::", "TunnelID": "0x0", "Interface": "InLoopBack0",
         "Flags": "D"},
        {"Destination": "::FFFF:127.0.0.1", "PrefixLength": "128", "NextHop": "::1", "Preference": "0", "Cost": "0",
         "Protocol": "Direct", "RelayNextHop": "::", "TunnelID": "0x0", "Interface": "InLoopBack0", "Flags": "D"},
        {"Destination": "64:FF9B::", "PrefixLength": "64", "NextHop": "2A02:6B8:B010:8004::1", "Preference": "60",
         "Cost": "0", "Protocol": "Static", "RelayNextHop": "2A02:6B8:B010:8004::1", "TunnelID": "0x0",
         "Interface": "MEth0/0/0", "Flags": "RD"},
        {"Destination": "64:FF9B::", "PrefixLength": "96", "NextHop": "2A02:6B8:B010:8004::1", "Preference": "60",
         "Cost": "0", "Protocol": "Static", "RelayNextHop": "2A02:6B8:B010:8004::1", "TunnelID": "0x0",
         "Interface": "MEth0/0/0", "Flags": "RD"},
        {"Destination": "2A02::1", "PrefixLength": "128", "NextHop": "::1", "Preference": "0", "Cost": "0",
         "Protocol": "Direct", "RelayNextHop": "::", "TunnelID": "0x0", "Interface": "LoopBack1", "Flags": "D"},
        {"Destination": "2A02:6B8::", "PrefixLength": "96", "NextHop": "2A02:6B8:B010:8004::1", "Preference": "60",
         "Cost": "0", "Protocol": "Static", "RelayNextHop": "2A02:6B8:B010:8004::1", "TunnelID": "0x0",
         "Interface": "MEth0/0/0", "Flags": "RD"},
        {"Destination": "2A02:6B8:B010:8004::", "PrefixLength": "64", "NextHop": "2A02:6B8:B010:8004::7850",
         "Preference": "0", "Cost": "0", "Protocol": "Direct", "RelayNextHop": "::", "TunnelID": "0x0",
         "Interface": "MEth0/0/0", "Flags": "D"},
        {"Destination": "2A02:6B8:B010:8004::7850", "PrefixLength": "128", "NextHop": "::1", "Preference": "0",
         "Cost": "0", "Protocol": "Direct", "RelayNextHop": "::", "TunnelID": "0x0", "Interface": "MEth0/0/0",
         "Flags": "D"},
        {"Destination": "FE80::", "PrefixLength": "10", "NextHop": "::", "Preference": "0", "Cost": "0",
         "Protocol": "Direct", "RelayNextHop": "::", "TunnelID": "0x0", "Interface": "NULL0", "Flags": "DB"},
        ]


class Data2(Data):
    content = """
Route Flags: R - relay, D - download to fib, B - black hole route
------------------------------------------------------------------------------
Routing Table : _public_
Summary Count : 1

Destination  : 2A02:6B8:0:3400::48E                    PrefixLength : 128
NextHop      : 2A02:6B8:0:1A6A::BA4A                   Preference   : 255
Neighbour    : 2A02:6B8:0:1A6A::BA4A                   ProcessID    : 0
Label        : NULL                                    Protocol     : EBGP
State        : Active Adv Relied                       Cost         : 1100
Entry ID     : 0                                       EntryFlags   : 0x00000000
Reference Cnt: 0                                       Tag          : 0
Priority     : low                                     Age          : 4sec
IndirectID   : 0x1000318                               Instance     :
RelayNextHop : 2A02:6B8:0:1A6A::BA4A                   TunnelID     : 0x0
Interface    : Vlanif801                               Flags        : RD
    """
    cmd = "dis ipv6 routing"
    host = "ce7850-test"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.150 (CE7850EI V200R002C50SPC800)
Copyright (C) 2012-2017 Huawei Technologies Co., Ltd.
HUAWEI CE7850-32Q-EI uptime is 386 days, 5 hours, 28 minutes

CE7850-32Q-EI(Master) 1 : uptime is  386 days, 5 hours, 27 minutes
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
    result = [{"Destination": "2A02:6B8:0:3400::48E", "PrefixLength": "128", "NextHop": "2A02:6B8:0:1A6A::BA4A",
               "Preference": "255", "Neighbour": "2A02:6B8:0:1A6A::BA4A", "ProcessID": "0", "Label": "NULL",
               "Protocol": "EBGP", "State": "Active Adv Relied", "Cost": "1100", "Entry ID": "0",
               "EntryFlags": "0x00000000", "Reference Cnt": "0", "Tag": "0", "Priority": "low", "Age": "4sec",
               "IndirectID": "0x1000318", "Instance": "", "RelayNextHop": "2A02:6B8:0:1A6A::BA4A", "TunnelID": "0x0",
               "Interface": "Vlanif801", "Flags": "RD"}]
