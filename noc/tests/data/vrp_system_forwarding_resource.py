from data.lib import Data


class Data1(Data):
    content = """
Global Main Common Hardware Forwarding Tables:
----------------------------------------------------------------
Name                               Total  Remain    Used[   %]
----------------------------------------------------------------
FEC                               131072  131046      26[  0%]
- IPV4 UC                         131072  131046      18[  0%]
- ARP_ND                          131072  131046       3[  0%]
- IPV6 UC                         131072  131046       2[  0%]
- TRILL                           131072  131046       0[  0%]
- MPLS                            131072  131046       2[  0%]
- VXLAN                           131072  131046       0[  0%]
- IP TUNNEL                       131072  131046       1[  0%]
- IP MC                           131072  131046       0[  0%]
- MQC                             131072  131046       0[  0%]
----------------------------------------------------------------
ECMP                                4095    4095       0[  0%]
- IPV4 UC                           4095    4095       0[  0%]
- ARP_ND                            4095    4095       0[  0%]
- IPV6 UC                           4095    4095       0[  0%]
- TRILL                             4095    4095       0[  0%]
- MPLS                              4095    4095       0[  0%]
- VXLAN                             4095    4095       0[  0%]
- IP TUNNEL                         4095    4095       0[  0%]
- MQC                               4095    4095       0[  0%]
----------------------------------------------------------------
    """
    cmd = "disp system forwarding resource"
    host = "vla1-9d4"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.180 (CE12800 V200R005C00SPC800)
Copyright (C) 2012-2018 Huawei Technologies Co., Ltd.
HUAWEI CE12804 uptime is 162 days, 0 hour, 4 minutes 
Patch Version: V200R005SPH007

BKP  version information:
1.PCB      Version  : DE01BAK04A VER C
2.Board    Type     : CE-BAK04A  
3.MPU Slot Quantity : 2
4.LPU Slot Quantity : 4
5.SFU Slot Quantity : 6

MPU(Master) 5 : uptime is  162 days, 0 hour, 3 minutes
        StartupTime 2019/09/24   16:15:56+03:00 
Memory     Size     : 8192 M bytes
Flash      Size     : 4096 M bytes
NVRAM      Size     : 512 K bytes
MPU version information:                              
1.PCB      Version  : DE01MPUA VER C
2.MAB      Version  : 1 
3.Board    Type     : CE-MPUA
4.CPLD1    Version  : 105
5.BIOS     Version  : 432
  
MPU(Slave) 6 : uptime is  162 days, 0 hour, 3 minutes
        StartupTime 2019/09/24   16:16:05+03:00 
Memory     Size     : 8192 M bytes
Flash      Size     : 4096 M bytes
NVRAM      Size     : 512 K bytes
MPU version information:                              
1.PCB      Version  : DE01MPUA VER C
2.MAB      Version  : 1 
3.Board    Type     : CE-MPUA
4.CPLD1    Version  : 105
5.BIOS     Version  : 432
  
LPU 4 : uptime is 161 days, 23 hours, 57 minutes
        StartupTime 2019/09/24   16:21:47+03:00 
Memory     Size     : 4096 M bytes
Flash      Size     : 128  M bytes
LPU version information:
1.PCB      Version  : CEL36CQFD VER A
2.MAB      Version  : 1
3.Board    Type     : CE-L36CQ-FD
4.CPLD1    Version  : 104
5.CPLD2    Version  : 104
6.BIOS     Version  : 161

SFU 9 : uptime is 162 days, 0 hour, 0 minute
        StartupTime 2019/09/24   16:18:48+03:00 
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 432

SFU 10 : uptime is 162 days, 0 hour, 0 minute
        StartupTime 2019/09/24   16:19:12+03:00 
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 432

SFU 11 : uptime is 162 days, 0 hour, 0 minute
        StartupTime 2019/09/24   16:18:47+03:00 
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 432

SFU 12 : uptime is 162 days, 0 hour, 0 minute
        StartupTime 2019/09/24   16:18:48+03:00 
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 432
                
SFU 13 : uptime is 162 days, 0 hour, 0 minute
        StartupTime 2019/09/24   16:19:08+03:00 
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 432

CMU(Master) 7 : uptime is 161 days, 4 hours, 42 minutes
        StartupTime 2019/09/24   19:18:49+03:00
Memory     Size     : 128 M bytes
Flash      Size     : 32  M bytes
CMU version information:
1.PCB      Version  : DE01CMUA VER B
2.MAB      Version  : 1 
3.Board    Type     : CE-CMUA
4.CPLD1    Version  : 104
5.BIOS     Version  : 127

CMU(Slave) 8 : uptime is 161 days, 8 hours, 38 minutes
        StartupTime 2019/09/24   19:18:50+03:00
Memory     Size     : 128 M bytes
Flash      Size     : 32  M bytes
CMU version information:
1.PCB      Version  : DE01CMUA VER B
2.MAB      Version  : 1 
3.Board    Type     : CE-CMUA
4.CPLD1    Version  : 104
5.BIOS     Version  : 127
    """
    result = {'FEC': {'IPV4 UC': {'total': 131072, 'remain': 131046, 'used': 18, 'used_percent': 0},
                      'ARP_ND': {'total': 131072, 'remain': 131046, 'used': 3, 'used_percent': 0},
                      'IPV6 UC': {'total': 131072, 'remain': 131046, 'used': 2, 'used_percent': 0},
                      'TRILL': {'total': 131072, 'remain': 131046, 'used': 0, 'used_percent': 0},
                      'MPLS': {'total': 131072, 'remain': 131046, 'used': 2, 'used_percent': 0},
                      'VXLAN': {'total': 131072, 'remain': 131046, 'used': 0, 'used_percent': 0},
                      'IP TUNNEL': {'total': 131072, 'remain': 131046, 'used': 1, 'used_percent': 0},
                      'IP MC': {'total': 131072, 'remain': 131046, 'used': 0, 'used_percent': 0},
                      'MQC': {'total': 131072, 'remain': 131046, 'used': 0, 'used_percent': 0},
                      'total': {'total': 131072, 'remain': 131046, 'used': 26, 'used_percent': 0}},
              'ECMP': {'IPV4 UC': {'total': 4095, 'remain': 4095, 'used': 0, 'used_percent': 0},
                       'ARP_ND': {'total': 4095, 'remain': 4095, 'used': 0, 'used_percent': 0},
                       'IPV6 UC': {'total': 4095, 'remain': 4095, 'used': 0, 'used_percent': 0},
                       'TRILL': {'total': 4095, 'remain': 4095, 'used': 0, 'used_percent': 0},
                       'MPLS': {'total': 4095, 'remain': 4095, 'used': 0, 'used_percent': 0},
                       'VXLAN': {'total': 4095, 'remain': 4095, 'used': 0, 'used_percent': 0},
                       'IP TUNNEL': {'total': 4095, 'remain': 4095, 'used': 0, 'used_percent': 0},
                       'MQC': {'total': 4095, 'remain': 4095, 'used': 0, 'used_percent': 0},
                       'total': {'total': 4095, 'remain': 4095, 'used': 0, 'used_percent': 0}}}


class Data2(Data):

    cmd = "disp system forwarding resource"
    host = "myt-e1.yndx.net"
    content = """Global Main Common Hardware Forwarding Tables:
----------------------------------------------------------------
Name                               Total  Remain    Used[   %]
----------------------------------------------------------------
FEC                               131072  127599    3473[  2%]
- IPV4 UC                             --      --     371[  0%]
- ARP_ND                              --      --      22[  0%]
- IPV6 UC                             --      --    2137[  1%]
- TRILL                               --      --       0[  0%]
- MPLS                                --      --     943[  0%]
- VXLAN                               --      --       0[  0%]
- IP TUNNEL                           --      --       0[  0%]
- IP MC                               --      --       0[  0%]
- MQC                                 --      --       0[  0%]
----------------------------------------------------------------
ECMP                                4095    3476     619[ 15%]
- IPV4 UC                             --      --      43[  1%]
- ARP_ND                              --      --       0[  0%]
- IPV6 UC                             --      --     230[  5%]
- TRILL                               --      --       0[  0%]
- MPLS                                --      --     346[  8%]
- VXLAN                               --      --       0[  0%]
- IP TUNNEL                           --      --       0[  0%]
- MQC                                 --      --       0[  0%]
----------------------------------------------------------------"""
    version = """
    Huawei Versatile Routing Platform Software
    VRP (R) software, Version 8.191 (CE12800 V200R019C10SPC800)
    Copyright (C) 2012-2020 Huawei Technologies Co., Ltd.
    HUAWEI CE12804 uptime is 79 days, 2 hours, 57 minutes
    Patch Version: V200R019SPH006

    BKP  version information:
    1.PCB      Version  : DE01BAK04A VER C
    2.Board    Type     : CE-BAK04A 
    3.MPU Slot Quantity : 2
    4.LPU Slot Quantity : 4
    5.SFU Slot Quantity : 6

    MPU(Master) 5 : uptime is  79 days, 2 hours, 56 minutes
            StartupTime 2020/11/10   09:54:51+03:00
    Memory     Size     : 8192 M bytes
    Flash      Size     : 4096 M bytes
    NVRAM      Size     : 512 K bytes
    MPU version information:                             
    1.PCB      Version  : DE01MPUA VER C
    2.MAB      Version  : 1
    3.Board    Type     : CE-MPUA
    4.CPLD1    Version  : 105
    5.BIOS     Version  : 439

    MPU(Slave) 6 : uptime is  79 days, 2 hours, 56 minutes
            StartupTime 2020/11/10   09:55:05+03:00
    Memory     Size     : 8192 M bytes
    Flash      Size     : 4096 M bytes
    NVRAM      Size     : 512 K bytes
    MPU version information:                             
    1.PCB      Version  : DE01MPUA VER C
    2.MAB      Version  : 1
    3.Board    Type     : CE-MPUA
    4.CPLD1    Version  : 105
    5.BIOS     Version  : 439

    LPU 2 : uptime is 48 days, 21 hours, 3 minutes
            StartupTime 2020/12/10   15:48:29+03:00
    Memory     Size     : 4096 M bytes
    Flash      Size     : 128  M bytes
    LPU version information:
    1.PCB      Version  : CEL36CQFD VER A
    2.MAB      Version  : 1
    3.Board    Type     : CE-L36CQ-FD
    4.CPLD1    Version  : 104
    5.CPLD2    Version  : 104
    6.BIOS     Version  : 205

    LPU 3 : uptime is 49 days, 1 hour, 22 minutes
            StartupTime 2020/12/10   11:29:17+03:00
    Memory     Size     : 4096 M bytes
    Flash      Size     : 128  M bytes
    LPU version information:
    1.PCB      Version  : CEL36CQFD VER A
    2.MAB      Version  : 1
    3.Board    Type     : CE-L36CQ-FD
    4.CPLD1    Version  : 104
    5.CPLD2    Version  : 104
    6.BIOS     Version  : 205

    LPU 4 : uptime is 79 days, 2 hours, 52 minutes
            StartupTime 2020/11/10   09:59:35+03:00
    Memory     Size     : 4096 M bytes
    Flash      Size     : 128  M bytes
    LPU version information:
    1.PCB      Version  : CEL36CQFD VER A
    2.MAB      Version  : 1
    3.Board    Type     : CE-L36CQ-FD
    4.CPLD1    Version  : 104
    5.CPLD2    Version  : 104
    6.BIOS     Version  : 205

    SFU 9 : uptime is 79 days, 2 hours, 56 minutes
            StartupTime 2020/11/10   09:55:34+03:00
    Memory     Size     : 512 M bytes
    Flash      Size     : 64  M bytes
    SFU version information:
    1.PCB      Version  : CESFU04G VER A
    2.MAB      Version  : 1
    3.Board    Type     : CE-SFU04G
    4.CPLD1    Version  : 101
    5.BIOS     Version  : 439

    SFU 10 : uptime is 79 days, 2 hours, 56 minutes
            StartupTime 2020/11/10   09:55:12+03:00
    Memory     Size     : 512 M bytes
    Flash      Size     : 64  M bytes
    SFU version information:
    1.PCB      Version  : CESFU04G VER A
    2.MAB      Version  : 1
    3.Board    Type     : CE-SFU04G
    4.CPLD1    Version  : 101
    5.BIOS     Version  : 439

    SFU 11 : uptime is 79 days, 2 hours, 56 minutes
            StartupTime 2020/11/10   09:55:14+03:00
    Memory     Size     : 512 M bytes
    Flash      Size     : 64  M bytes
    SFU version information:
    1.PCB      Version  : CESFU04G VER A
    2.MAB      Version  : 1
    3.Board    Type     : CE-SFU04G
    4.CPLD1    Version  : 101
    5.BIOS     Version  : 439

    SFU 12 : uptime is 79 days, 2 hours, 56 minutes
            StartupTime 2020/11/10   09:55:13+03:00
    Memory     Size     : 512 M bytes
    Flash      Size     : 64  M bytes
    SFU version information:
    1.PCB      Version  : CESFU04G VER A
    2.MAB      Version  : 1
    3.Board    Type     : CE-SFU04G
    4.CPLD1    Version  : 101
    5.BIOS     Version  : 439

    SFU 13 : uptime is 79 days, 2 hours, 56 minutes
            StartupTime 2020/11/10   09:55:36+03:00
    Memory     Size     : 512 M bytes
    Flash      Size     : 64  M bytes
    SFU version information:
    1.PCB      Version  : CESFU04G VER A
    2.MAB      Version  : 1
    3.Board    Type     : CE-SFU04G
    4.CPLD1    Version  : 101
    5.BIOS     Version  : 439

    SFU 14 : uptime is 79 days, 2 hours, 56 minutes
            StartupTime 2020/11/10   09:55:13+03:00
    Memory     Size     : 512 M bytes
    Flash      Size     : 64  M bytes
    SFU version information:
    1.PCB      Version  : CESFU04G VER A
    2.MAB      Version  : 1
    3.Board    Type     : CE-SFU04G
    4.CPLD1    Version  : 101
    5.BIOS     Version  : 439

    CMU(Master) 7 : uptime is 78 days, 16 hours, 2 minutes
            StartupTime 2020/11/10   12:55:00+03:00
    Memory     Size     : 128 M bytes
    Flash      Size     : 32  M bytes
    CMU version information:
    1.PCB      Version  : DE01CMUA VER B
    2.MAB      Version  : 1
    3.Board    Type     : CE-CMUA
    4.CPLD1    Version  : 104
    5.BIOS     Version  : 127

    CMU(Slave) 8 : uptime is 78 days, 19 hours, 1 minute
            StartupTime 2020/11/10   12:55:01+03:00
    Memory     Size     : 128 M bytes
    Flash      Size     : 32  M bytes
    CMU version information:
    1.PCB      Version  : DE01CMUA VER B
    2.MAB      Version  : 1
    3.Board    Type     : CE-CMUA
    4.CPLD1    Version  : 104
    5.BIOS     Version  : 127
        """
    result = {'ECMP': {'ARP_ND': {'used': 0, 'used_percent': 0},
                       'IP TUNNEL': {'used': 0, 'used_percent': 0},
                       'IPV4 UC': {'used': 43, 'used_percent': 1},
                       'IPV6 UC': {'used': 230, 'used_percent': 5},
                       'MPLS': {'used': 346, 'used_percent': 8},
                       'MQC': {'used': 0, 'used_percent': 0},
                       'TRILL': {'used': 0, 'used_percent': 0},
                       'VXLAN': {'used': 0, 'used_percent': 0},
                       'total': {'remain': 3476, 'total': 4095, 'used': 619, 'used_percent': 15}},
              'FEC': {'ARP_ND': {'used': 22, 'used_percent': 0},
                      'IP MC': {'used': 0, 'used_percent': 0},
                      'IP TUNNEL': {'used': 0, 'used_percent': 0},
                      'IPV4 UC': {'used': 371, 'used_percent': 0},
                      'IPV6 UC': {'used': 2137, 'used_percent': 1},
                      'MPLS': {'used': 943, 'used_percent': 0},
                      'MQC': {'used': 0, 'used_percent': 0},
                      'TRILL': {'used': 0, 'used_percent': 0},
                      'VXLAN': {'used': 0, 'used_percent': 0},
                      'total': {'remain': 127599, 'total': 131072, 'used': 3473, 'used_percent': 2}}}
