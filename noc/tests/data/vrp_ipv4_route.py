from data.lib import Data


class Data1(Data):
    content = """
Route Flags: R - relay, D - download to fib, T - to vpn-instance, B - black hole route
------------------------------------------------------------------------------
Routing Table : _public_
Summary Count : 1

Destination: 213.180.213.252/31 
     Protocol: OSPF               Process ID: 1             
   Preference: 10                       Cost: 1102          
      NextHop: 213.180.213.136     Neighbour: 0.0.0.0
        State: Active Adv                Age: 6d17h42m43s        
          Tag: 0                    Priority: medium        
        Label: NULL                  QoSInfo: 0x0          
   IndirectID: 0x1000096            Instance:                                
 RelayNextHop: 0.0.0.0             Interface: Eth-Trunk81
     TunnelID: 0x0                     Flags: D              
    """
    cmd = "dis ip routing 213.180.213.252 31 verbose"
    host = "myt-e2.yndx.net"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.191 (CE12800 V200R019C10SPC800)
Copyright (C) 2012-2020 Huawei Technologies Co., Ltd.
HUAWEI CE12804 uptime is 222 days, 6 hours, 48 minutes
Patch Version: V200R019SPH007

BKP  version information:
1.PCB      Version  : DE01BAK04A VER C
2.Board    Type     : CE-BAK04A 
3.MPU Slot Quantity : 2
4.LPU Slot Quantity : 4
5.SFU Slot Quantity : 6

MPU(Master) 5 : uptime is  222 days, 6 hours, 48 minutes
        StartupTime 2021/04/02   12:16:05+03:00
Memory     Size     : 16384 M bytes
Flash      Size     : 4096 M bytes
MPU version information:                             
1.PCB      Version  : CE01MPUB VER B
2.MAB      Version  : 1
3.Board    Type     : CE-MPUB
4.CPLD1    Version  : 270
5.BIOS     Version  : 1102
 
MPU(Slave) 6 : uptime is  222 days, 6 hours, 48 minutes
        StartupTime 2021/04/02   12:16:11+03:00
Memory     Size     : 16384 M bytes
Flash      Size     : 4096 M bytes
MPU version information:                             
1.PCB      Version  : CE01MPUB VER B
2.MAB      Version  : 1
3.Board    Type     : CE-MPUB
4.CPLD1    Version  : 270
5.BIOS     Version  : 1102
 
LPU 1 : uptime is 222 days, 6 hours, 41 minutes
        StartupTime 2021/04/02   12:22:53+03:00
Memory     Size     : 4096 M bytes
Flash      Size     : 128  M bytes
LPU version information:
1.PCB      Version  : CEL36CQFD VER A
2.MAB      Version  : 1
3.Board    Type     : CE-L36CQ-FD
4.CPLD1    Version  : 104
5.CPLD2    Version  : 104
6.BIOS     Version  : 205

LPU 2 : uptime is 222 days, 6 hours, 42 minutes
        StartupTime 2021/04/02   12:22:09+03:00
Memory     Size     : 4096 M bytes
Flash      Size     : 128  M bytes
LPU version information:
1.PCB      Version  : CEL36CQFD VER A
2.MAB      Version  : 1
3.Board    Type     : CE-L36CQ-FD
4.CPLD1    Version  : 104
5.CPLD2    Version  : 104
6.BIOS     Version  : 205

SFU 9 : uptime is 222 days, 6 hours, 47 minutes
        StartupTime 2021/04/02   12:16:37+03:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 439

SFU 10 : uptime is 222 days, 6 hours, 47 minutes
        StartupTime 2021/04/02   12:16:37+03:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 439

SFU 11 : uptime is 222 days, 6 hours, 47 minutes
        StartupTime 2021/04/02   12:16:37+03:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 439

SFU 12 : uptime is 222 days, 6 hours, 47 minutes
        StartupTime 2021/04/02   12:16:37+03:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 439

SFU 13 : uptime is 222 days, 6 hours, 47 minutes
        StartupTime 2021/04/02   12:16:37+03:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 439

CMU(Master) 7 : uptime is 220 days, 23 hours, 40 minutes
        StartupTime 2021/04/02   15:16:16+03:00
Memory     Size     : 128 M bytes
Flash      Size     : 32  M bytes
CMU version information:
1.PCB      Version  : DE01CMUA VER B
2.MAB      Version  : 1
3.Board    Type     : CE-CMUA
4.CPLD1    Version  : 104
5.BIOS     Version  : 127

CMU(Slave) 8 : uptime is 221 days, 9 hours, 26 minutes
        StartupTime 2021/04/02   15:16:16+03:00
Memory     Size     : 128 M bytes
Flash      Size     : 32  M bytes
CMU version information:
1.PCB      Version  : DE01CMUA VER B
2.MAB      Version  : 1
3.Board    Type     : CE-CMUA
4.CPLD1    Version  : 104
5.BIOS     Version  : 127
    """
    result = [
        {
            "Protocol": "OSPF",
            "Process ID": "1",
            "Preference": "10",
            "Cost": "1102",
            "NextHop": "213.180.213.136",
            "Neighbour": "0.0.0.0",
            "State": "Active Adv",
            "Age": "6d17h42m43s",
            "Tag": "0",
            "Priority": "medium",
            "Label": "NULL",
            "QoSInfo": "0x0",
            "IndirectID": "0x1000096",
            "Instance": "",
            "RelayNextHop": "0.0.0.0",
            "Interface": "Eth-Trunk81",
            "TunnelID": "0x0",
            "Flags": "D",
            "Destination": "213.180.213.252/31",
        }
    ]
