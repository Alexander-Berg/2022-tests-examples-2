from data.lib import Data


class Data1(Data):
    content = """
The current state is: Idle
    """
    cmd = "display patch-information"
    host = "ce6870ei-test"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.180 (CE6870EI V200R005C00SPC800)
Copyright (C) 2012-2018 Huawei Technologies Co., Ltd.
HUAWEI CE6870-48S6CQ-EI uptime is 9 days, 1 hour, 23 minutes

CE6870-48S6CQ-EI(Master) 1 : uptime is  9 days, 1 hour, 22 minutes
        StartupTime 2019/02/16   10:28:06
Memory    Size    : 4096 M bytes
Flash     Size    : 1024 M bytes
CE6870-48S6CQ-EI version information                              
1. PCB    Version : CEM48S6CQP01    VER B
2. MAB    Version : 1
3. Board  Type    : CE6870-48S6CQ-EI
4. CPLD1  Version : 102
5. CPLD2  Version : 102
6. BIOS   Version : 432
    """
    result = None


class Data2(Data):
    content = """
Patch Package Name    :flash:/CE12800-V200R002SPH018.PAT
Patch Package Version :V200R002SPH018
Patch Package State   :Running  
Patch Package Run Time:2019-02-14 15:09:01+03:00
    """
    cmd = "display patch-information"
    host = "m9-p2"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.150 (CE12800 V200R002C50SPC800)
Copyright (C) 2012-2017 Huawei Technologies Co., Ltd.
HUAWEI CE12804 uptime is 430 days, 15 hours, 44 minutes
Patch Version: V200R002SPH018

BKP  version information:
1.PCB      Version  : DE01BAK04A VER C
2.Board    Type     : CE-BAK04A 
3.MPU Slot Quantity : 2
4.LPU Slot Quantity : 4
5.SFU Slot Quantity : 6

MPU(Master) 5 : uptime is  430 days, 15 hours, 43 minutes
        StartupTime 2017/12/21   23:15:22+03:00
Memory     Size     : 8192 M bytes
Flash      Size     : 4096 M bytes
NVRAM      Size     : 512 K bytes
MPU version information:                             
1.PCB      Version  : DE01MPUA VER C
2.MAB      Version  : 1
3.Board    Type     : CE-MPUA
4.CPLD1    Version  : 104
5.BIOS     Version  : 386

MPU(Slave) 6 : uptime is  430 days, 15 hours, 43 minutes
        StartupTime 2017/12/21   23:15:28+03:00
Memory     Size     : 8192 M bytes
Flash      Size     : 4096 M bytes
NVRAM      Size     : 512 K bytes
MPU version information:                             
1.PCB      Version  : DE01MPUA VER C
2.MAB      Version  : 1
3.Board    Type     : CE-MPUA
4.CPLD1    Version  : 104
5.BIOS     Version  : 386

LPU 1 : uptime is 207 days, 3 hours, 48 minutes
        StartupTime 2018/08/02   11:10:12+03:00
Memory     Size     : 4096 M bytes
Flash      Size     : 128  M bytes
LPU version information:
1.PCB      Version  : CEL36CQFD VER A
2.MAB      Version  : 1
3.Board    Type     : CE-L36CQ-FD
4.CPLD1    Version  : 104
5.CPLD2    Version  : 104
6.BIOS     Version  : 105

LPU 2 : uptime is 430 days, 15 hours, 33 minutes
        StartupTime 2017/12/21   23:25:25+03:00
Memory     Size     : 4096 M bytes
Flash      Size     : 128  M bytes
NVRAM      Size     : 512  K bytes
TCAM       Size     : 40   M bytes
LPU version information:
1.PCB      Version  : CEL12CFEG VER A
2.MAB      Version  : 1
3.Board    Type     : CE-L12CF-EG
4.CPLD1    Version  : 108
5.CPLD2    Version  : 108
6.FPGA1    Version  : 3
7.FPGA2    Version  : 3
8.BIOS     Version  : 386

LPU 3 : uptime is 24 days, 22 hours, 4 minutes
        StartupTime 2019/01/31   16:52:52+03:00
Memory     Size     : 4096 M bytes
Flash      Size     : 128  M bytes
LPU version information:
1.PCB      Version  : CEL36CQFD VER A
2.MAB      Version  : 1
3.Board    Type     : CE-L36CQ-FD
4.CPLD1    Version  : 104
5.CPLD2    Version  : 104
6.BIOS     Version  : 105

LPU 4 : uptime is 430 days, 15 hours, 32 minutes
        StartupTime 2017/12/21   23:26:00+03:00
Memory     Size     : 4096 M bytes
Flash      Size     : 64   M bytes
NVRAM      Size     : 512  K bytes
TCAM       Size     : 20   M bytes
LPU version information:
1.PCB      Version  : CEL48XSEB VER B
2.MAB      Version  : 1
3.Board    Type     : CE-L48XS-ED
4.CPLD1    Version  : 104
5.CPLD2    Version  : 104
6.BIOS     Version  : 386

SFU 9 : uptime is 430 days, 15 hours, 33 minutes
        StartupTime 2017/12/21   23:25:21+03:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 386

SFU 10 : uptime is 430 days, 15 hours, 33 minutes
        StartupTime 2017/12/21   23:25:19+03:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 386

SFU 11 : uptime is 430 days, 15 hours, 33 minutes
        StartupTime 2017/12/21   23:25:18+03:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 386

SFU 12 : uptime is 430 days, 15 hours, 33 minutes
        StartupTime 2017/12/21   23:25:22+03:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 386

SFU 13 : uptime is 430 days, 15 hours, 33 minutes
        StartupTime 2017/12/21   23:25:18+03:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 386

SFU 14 : uptime is 430 days, 15 hours, 33 minutes
        StartupTime 2017/12/21   23:25:22+03:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU04G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU04G
4.CPLD1    Version  : 101
5.BIOS     Version  : 386

CMU(Slave) 7 : uptime is 428 days, 15 hours, 19 minutes
        StartupTime 2017/12/22   02:32:14+03:00
Memory     Size     : 128 M bytes
Flash      Size     : 32  M bytes
CMU version information:
1.PCB      Version  : DE01CMUA VER B
2.MAB      Version  : 1
3.Board    Type     : CE-CMUA
4.CPLD1    Version  : 104
5.BIOS     Version  : 127

CMU(Master) 8 : uptime is 428 days, 4 hours, 41 minutes
        StartupTime 2017/12/22   02:28:48+03:00
Memory     Size     : 128 M bytes
Flash      Size     : 32  M bytes
CMU version information:
1.PCB      Version  : DE01CMUA VER B
2.MAB      Version  : 1
3.Board    Type     : CE-CMUA
4.CPLD1    Version  : 104
5.BIOS     Version  : 127
    """
    result = "V200R002SPH018"
