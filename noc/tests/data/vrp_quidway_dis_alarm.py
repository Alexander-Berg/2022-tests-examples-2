from data.lib import Data


class Data1(Data):
    content = """
A/B/C/D/E/F/G/H/I/J
A=Sequence, B=RootKindFlag(Independent|RootCause|nonRootCause)
C=Generating time, D=Clearing time
E=ID, F=Name, G=Level, H=State
I=Description information for locating(Para info, Reason info)
J=RootCause alarm sequence(Only for nonRootCause alarm)

  1/Independent/2060-05-14 19:24:32+03:00/-/0x41932001/hwLldpEnabled/Warning/Start/OID: 1.3.6.1.4.1.2011.5.25.134.2.1 Global LLDP is enabled.
    """
    cmd = "dis alarm active"
    host = "vla2-i47.yndx.net"
    version = """
Huawei Versatile Routing Platform Software
VRP (R) software, Version 5.150 (S5300 V200R005C00SPC500)
Copyright (C) 2000-2015 HUAWEI TECH CO., LTD
Quidway S5352C-EI Routing Switch uptime is 1 week, 3 days, 20 hours, 33 minutes

CX22EMGE 0(Master) : uptime is 1 week, 3 days, 20 hours, 32 minutes
256M bytes DDR Memory
32M bytes FLASH
Pcb      Version :  VER.C
Basic  BOOTROM  Version :  206 Compiled at Jul  1 2015, 14:25:55
CPLD   Version : 80
Software Version : VRP (R) Software, Version 5.150 (V200R005C00SPC500)
FORECARD information
Pcb      Version : CX22E4XY VER.B
HINDCARD information
Pcb      Version : CX22ETPB VER.C
FANCARD I information
Pcb      Version : FAN VER.B
PWRCARD I information
Pcb      Version : PWR VER.A
PWRCARD II information
Pcb      Version : PWR VER.A
    """
    result = [
        {'Sequence': '1', 'RootKindFlag': 'Independent', 'StartTime': '2060-05-14 19:24:32+03:00', 'EndTime': '-', 'AlarmId': '0x41932001',
         'AlarmName': 'hwLldpEnabled', 'Severity': 'Warning', 'State': 'Start',
         'Description': 'OID: 1.3.6.1.4.1.2011.5.25.134.2.1 Global LLDP is enabled.', 'RootCause': None}]
