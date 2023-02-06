from data.lib import Data


class Data1(Data):
    content = """
2020-05-25 13:30:42.447 +03:00 DST
Sequence    : 482      
AlarmId     : 0x8130059             AlarmName : hwOpticalInvalid                                               
AlarmType   : equipment             Severity  : Warning          State : active
RootKindFlag: Independent          
StartTime   : 2020-04-29 11:58:59+03:00 DST          
Description : Optical Module is invalid. (EntPhysicalIndex=17043726, EntPhysicalName=100GE4/0/13, EntityTrapFaultID=136193, Reason=Output Optical Power Too High.)

Sequence    : 481      
AlarmId     : 0x8130059             AlarmName : hwOpticalInvalid                                               
AlarmType   : equipment             Severity  : Warning          State : active
RootKindFlag: Independent          
StartTime   : 2020-04-29 11:58:59+03:00 DST          
Description : Optical Module is invalid. (EntPhysicalIndex=17043726, EntPhysicalName=100GE4/0/13, EntityTrapFaultID=136195, Reason=Input Optical Power Too High.)

Sequence    : 480      
AlarmId     : 0x8130059             AlarmName : hwOpticalInvalid                                               
AlarmType   : equipment             Severity  : Warning          State : active
RootKindFlag: Independent          
StartTime   : 2020-04-27 11:45:08+03:00 DST          
Description : Optical Module is invalid. (EntPhysicalIndex=17240336, EntPhysicalName=100GE7/0/15, EntityTrapFaultID=136193, Reason=Output Optical Power Too High.)

Sequence    : 479      
AlarmId     : 0x8130059             AlarmName : hwOpticalInvalid                                               
AlarmType   : equipment             Severity  : Warning          State : active
RootKindFlag: Independent          
StartTime   : 2020-04-27 11:45:08+03:00 DST          
Description : Optical Module is invalid. (EntPhysicalIndex=17240336, EntPhysicalName=100GE7/0/15, EntityTrapFaultID=136195, Reason=Input Optical Power Too High.)
    """
    cmd = "dis alarm active verbose"
    host = "man1-5d3.yndx.net"
    version = """
2020-05-25 13:30:41.274 +03:00 DST
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.180 (CE12800 V200R005C10SPC800)
Copyright (C) 2012-2018 Huawei Technologies Co., Ltd.
HUAWEI CE12808 uptime is 39 days, 0 hour, 14 minutes
Patch Version: V200R005SPH016

BKP  version information:
1.PCB      Version  : DE01BAK08A VER B
2.Board    Type     : CE-BAK08A 
3.MPU Slot Quantity : 2
4.LPU Slot Quantity : 8
5.SFU Slot Quantity : 6

MPU(Master) 9 : uptime is  39 days, 0 hour, 13 minutes
        StartupTime 2020/04/16   13:17:22+02:00
Memory     Size     : 8192 M bytes
Flash      Size     : 4096 M bytes
NVRAM      Size     : 512 K bytes
MPU version information:                             
1.PCB      Version  : DE01MPUA VER C
2.MAB      Version  : 1
3.Board    Type     : CE-MPUA
4.CPLD1    Version  : 105
5.BIOS     Version  : 433
 
MPU(Slave) 10 : uptime is  39 days, 0 hour, 13 minutes
        StartupTime 2020/04/16   13:17:18+02:00
Memory     Size     : 8192 M bytes
Flash      Size     : 4096 M bytes
NVRAM      Size     : 512 K bytes
MPU version information:                             
1.PCB      Version  : DE01MPUA VER C
2.MAB      Version  : 1
3.Board    Type     : CE-MPUA
4.CPLD1    Version  : 105
5.BIOS     Version  : 433
 
LPU 3 : uptime is 39 days, 0 hour, 3 minutes
        StartupTime 2020/04/16   13:27:18+02:00
Memory     Size     : 4096 M bytes
Flash      Size     : 128  M bytes
LPU version information:
1.PCB      Version  : CEL36CQFD VER A
2.MAB      Version  : 1
3.Board    Type     : CE-L36CQ-FD
4.CPLD1    Version  : 104
5.CPLD2    Version  : 104
6.BIOS     Version  : 192

LPU 4 : uptime is 39 days, 0 hour, 3 minutes
        StartupTime 2020/04/16   13:27:29+02:00
Memory     Size     : 4096 M bytes
Flash      Size     : 128  M bytes
LPU version information:
1.PCB      Version  : CEL36CQFD VER A
2.MAB      Version  : 1
3.Board    Type     : CE-L36CQ-FD
4.CPLD1    Version  : 104
5.CPLD2    Version  : 104
6.BIOS     Version  : 192

LPU 5 : uptime is 39 days, 0 hour, 1 minute
        StartupTime 2020/04/16   13:28:34+02:00
Memory     Size     : 4096 M bytes
Flash      Size     : 128  M bytes
LPU version information:
1.PCB      Version  : CEL36CQFD VER A
2.MAB      Version  : 1
3.Board    Type     : CE-L36CQ-FD
4.CPLD1    Version  : 104
5.CPLD2    Version  : 104
6.BIOS     Version  : 192

LPU 6 : uptime is 39 days, 0 hour, 3 minutes
        StartupTime 2020/04/16   13:27:20+02:00
Memory     Size     : 4096 M bytes
Flash      Size     : 128  M bytes
LPU version information:
1.PCB      Version  : CEL36CQFD VER A
2.MAB      Version  : 1
3.Board    Type     : CE-L36CQ-FD
4.CPLD1    Version  : 104
5.CPLD2    Version  : 104
6.BIOS     Version  : 192

LPU 7 : uptime is 39 days, 0 hour, 3 minutes
        StartupTime 2020/04/16   13:27:29+02:00
Memory     Size     : 4096 M bytes
Flash      Size     : 128  M bytes
LPU version information:
1.PCB      Version  : CEL36CQFD VER A
2.MAB      Version  : 1
3.Board    Type     : CE-L36CQ-FD
4.CPLD1    Version  : 104
5.CPLD2    Version  : 104
6.BIOS     Version  : 192

LPU 8 : uptime is 39 days, 0 hour, 2 minutes
        StartupTime 2020/04/16   13:27:40+02:00
Memory     Size     : 4096 M bytes
Flash      Size     : 128  M bytes
LPU version information:
1.PCB      Version  : CEL36CQFD VER A
2.MAB      Version  : 1
3.Board    Type     : CE-L36CQ-FD
4.CPLD1    Version  : 104
5.CPLD2    Version  : 104
6.BIOS     Version  : 192

SFU 13 : uptime is 39 days, 0 hour, 12 minutes
        StartupTime 2020/04/16   13:18:09+02:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU08G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU08G
4.CPLD1    Version  : 101
5.BIOS     Version  : 433

SFU 14 : uptime is 39 days, 0 hour, 12 minutes
        StartupTime 2020/04/16   13:18:11+02:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU08G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU08G
4.CPLD1    Version  : 101
5.BIOS     Version  : 433

SFU 15 : uptime is 39 days, 0 hour, 12 minutes
        StartupTime 2020/04/16   13:18:09+02:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU08G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU08G
4.CPLD1    Version  : 101
5.BIOS     Version  : 433

SFU 16 : uptime is 39 days, 0 hour, 12 minutes
        StartupTime 2020/04/16   13:18:08+02:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU08G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU08G
4.CPLD1    Version  : 101
5.BIOS     Version  : 433

SFU 17 : uptime is 39 days, 0 hour, 12 minutes
        StartupTime 2020/04/16   13:18:10+02:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU08G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU08G
4.CPLD1    Version  : 101
5.BIOS     Version  : 433

SFU 18 : uptime is 39 days, 0 hour, 12 minutes
        StartupTime 2020/04/16   13:18:10+02:00
Memory     Size     : 512 M bytes
Flash      Size     : 64  M bytes
SFU version information:
1.PCB      Version  : CESFU08G VER A
2.MAB      Version  : 1
3.Board    Type     : CE-SFU08G
4.CPLD1    Version  : 101
5.BIOS     Version  : 433

CMU(Master) 11 : uptime is 38 days, 17 hours, 28 minutes
        StartupTime 2020/04/16   16:17:36+02:00
Memory     Size     : 128 M bytes
Flash      Size     : 32  M bytes
CMU version information:
1.PCB      Version  : DE01CMUA VER B
2.MAB      Version  : 1
3.Board    Type     : CE-CMUA
4.CPLD1    Version  : 104
5.BIOS     Version  : 127

CMU(Slave) 12 : uptime is 38 days, 19 hours, 2 minutes
        StartupTime 2020/04/16   16:17:37+02:00
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
        {'Sequence': '482', 'AlarmId': '0x8130059', 'AlarmName': 'hwOpticalInvalid', 'AlarmType': 'equipment', 'Severity': 'Warning',
         'State': 'active', 'RootKindFlag': 'Independent', 'StartTime': '2020-04-29 11:58:59+03:00 DST',
         'Description': 'Optical Module is invalid. (EntPhysicalIndex=17043726, EntPhysicalName=100GE4/0/13, EntityTrapFaultID=136193, Reason=Output Optical Power Too High.)'},
        {'Sequence': '481', 'AlarmId': '0x8130059', 'AlarmName': 'hwOpticalInvalid', 'AlarmType': 'equipment', 'Severity': 'Warning',
         'State': 'active', 'RootKindFlag': 'Independent', 'StartTime': '2020-04-29 11:58:59+03:00 DST',
         'Description': 'Optical Module is invalid. (EntPhysicalIndex=17043726, EntPhysicalName=100GE4/0/13, EntityTrapFaultID=136195, Reason=Input Optical Power Too High.)'},
        {'Sequence': '480', 'AlarmId': '0x8130059', 'AlarmName': 'hwOpticalInvalid', 'AlarmType': 'equipment', 'Severity': 'Warning',
         'State': 'active', 'RootKindFlag': 'Independent', 'StartTime': '2020-04-27 11:45:08+03:00 DST',
         'Description': 'Optical Module is invalid. (EntPhysicalIndex=17240336, EntPhysicalName=100GE7/0/15, EntityTrapFaultID=136193, Reason=Output Optical Power Too High.)'},
        {'Sequence': '479', 'AlarmId': '0x8130059', 'AlarmName': 'hwOpticalInvalid', 'AlarmType': 'equipment', 'Severity': 'Warning',
         'State': 'active', 'RootKindFlag': 'Independent', 'StartTime': '2020-04-27 11:45:08+03:00 DST',
         'Description': 'Optical Module is invalid. (EntPhysicalIndex=17240336, EntPhysicalName=100GE7/0/15, EntityTrapFaultID=136195, Reason=Input Optical Power Too High.)'}]
