from data.lib import Data


class Data1(Data):
    content = """
Hardware inventory:
Item             Version  Part number  Serial number     Description
Chassis                                JN114C109AFC      MX240
Midplane         REV 07   760-021404   ABAA2974          MX240 Backplane
FPM Board        REV 03   760-021392   XH0679            Front Panel Display
PEM 0            Rev 10   740-029970   QCS1247U038       PS 1.4-2.52kW; 90-264V AC in
PEM 1            Rev 10   740-029970   QCS1433U15V       PS 1.4-2.52kW; 90-264V AC in
PEM 2            Rev 10   740-029970   QCS1247U0ME       PS 1.4-2.52kW; 90-264V AC in
PEM 3            Rev 10   740-029970   QCS1433U135       PS 1.4-2.52kW; 90-264V AC in
Routing Engine 0 REV 10   740-031116   9009228581        RE-S-1800x4
CB 0             REV 03   750-055976   CAEE8002          Enhanced MX SCB 2
FPC 1            REV 22   750-031089   ZT9596            MPC Type 2 3D
  CPU            REV 06   711-030884   ZS1257            MPC PMB 2G
  MIC 0          REV 27   750-028387   ZK3514            3D 4x 10GE  XFP
    PIC 0                 BUILTIN      BUILTIN           2x 10GE  XFP
      Xcvr 0              NON-JNPR     M1302180031       XFP-10G-SR
      Xcvr 1     $        NON-JNPR     S1109052223       XFP-10G-LR
    PIC 1                 BUILTIN      BUILTIN           2x 10GE  XFP
  MIC 1          REV 27   750-028387   ZK3464            3D 4x 10GE  XFP
    PIC 2                 BUILTIN      BUILTIN           2x 10GE  XFP
      Xcvr 0              NON-JNPR     M1106013253       XFP-10G-SR
    PIC 3                 BUILTIN      BUILTIN           2x 10GE  XFP
Fan Tray 0       REV 01   710-030216   YC9135            Enhanced Fan Tray
    """
    cmd = "show chassis hardware"
    host = "mx240-test"
    version = """
Model: mx240
Junos: 16.1R7.7
JUNOS OS Kernel 64-bit  [20180601.93ff995_builder_stable_10]
JUNOS OS libs [20180601.93ff995_builder_stable_10]
JUNOS OS runtime [20180601.93ff995_builder_stable_10]
JUNOS OS time zone information [20180601.93ff995_builder_stable_10]
JUNOS OS libs compat32 [20180601.93ff995_builder_stable_10]
JUNOS OS 32-bit compatibility [20180601.93ff995_builder_stable_10]
JUNOS py extensions [20180612.033802_builder_junos_161_r7]
JUNOS py base [20180612.033802_builder_junos_161_r7]
JUNOS OS crypto [20180601.93ff995_builder_stable_10]
JUNOS network stack and utilities [20180612.033802_builder_junos_161_r7]
JUNOS libs [20180612.033802_builder_junos_161_r7]
JUNOS libs compat32 [20180612.033802_builder_junos_161_r7]
JUNOS runtime [20180612.033802_builder_junos_161_r7]
JUNOS na telemetry [16.1R7.8-C1]
JUNOS mx libs compat32 [20180612.033802_builder_junos_161_r7]
JUNOS mx runtime [20180612.033802_builder_junos_161_r7]
JUNOS common platform support [20180612.033802_builder_junos_161_r7]
JUNOS Openconfig [0.0.0.10-1]
JUNOS modules [20180612.033802_builder_junos_161_r7]
JUNOS mx modules [20180612.033802_builder_junos_161_r7]
JUNOS mx libs [20180612.033802_builder_junos_161_r7]
JUNOS Data Plane Crypto Support [20180612.033802_builder_junos_161_r7]
JUNOS mtx Data Plane Crypto Support [20180612.033802_builder_junos_161_r7]
JUNOS daemons [20180612.033802_builder_junos_161_r7]
JUNOS mx daemons [20180612.033802_builder_junos_161_r7]
JUNOS Voice Services Container package [20180612.033802_builder_junos_161_r7]
JUNOS Services TLB Service PIC package [20180612.033802_builder_junos_161_r7]
JUNOS Services SSL [20180612.033802_builder_junos_161_r7]
JUNOS Services Stateful Firewall [20180612.033802_builder_junos_161_r7]
JUNOS Services RPM [20180612.033802_builder_junos_161_r7]
JUNOS Services PTSP Container package [20180612.033802_builder_junos_161_r7]
JUNOS Services PCEF package [20180612.033802_builder_junos_161_r7]
JUNOS Services NAT [20180612.033802_builder_junos_161_r7]
JUNOS Services Mobile Subscriber Service Container package [20180612.033802_builder_junos_161_r7]
JUNOS Services MobileNext Software package [20180612.033802_builder_junos_161_r7]
JUNOS Services Logging Report Framework package [20180612.033802_builder_junos_161_r7]
JUNOS Services LL-PDF Container package [20180612.033802_builder_junos_161_r7]
JUNOS Services Jflow Container package [20180612.033802_builder_junos_161_r7]
JUNOS Services Deep Packet Inspection package [20180612.033802_builder_junos_161_r7]
JUNOS Services IPSec [20180612.033802_builder_junos_161_r7]
JUNOS Services IDS [20180612.033802_builder_junos_161_r7]
JUNOS IDP Services [20180612.033802_builder_junos_161_r7]
JUNOS Services HTTP Content Management package [20180612.033802_builder_junos_161_r7]
JUNOS Services Crypto [20180612.033802_builder_junos_161_r7]
JUNOS Services Captive Portal and Content Delivery Container package [20180612.033802_builder_junos_161_r7]
JUNOS Services COS [20180612.033802_builder_junos_161_r7]
JUNOS Border Gateway Function package [20180612.033802_builder_junos_161_r7]
JUNOS AppId Services [20180612.033802_builder_junos_161_r7]
JUNOS Services Application Level Gateways [20180612.033802_builder_junos_161_r7]
JUNOS Services AACL Container package [20180612.033802_builder_junos_161_r7]
JUNOS SDN Software Suite [20180612.033802_builder_junos_161_r7]
JUNOS Extension Toolkit [20180612.033802_builder_junos_161_r7]
JUNOS Packet Forwarding Engine Support (wrlinux) [20180612.033802_builder_junos_161_r7]
JUNOS Packet Forwarding Engine Support (MX/EX92XX Common) [20180612.033802_builder_junos_161_r7]
JUNOS Packet Forwarding Engine Support (M/T Common) [20180612.033802_builder_junos_161_r7]
JUNOS Packet Forwarding Engine Support (MX Common) [20180612.033802_builder_junos_161_r7]
JUNOS Online Documentation [20180612.033802_builder_junos_161_r7]
JUNOS jail runtime [20180601.93ff995_builder_stable_10]
JUNOS FIPS mode utilities [20180612.033802_builder_junos_161_r7]
    """
    result = [{'Description': 'MX240', 'Serial number': 'JN114C109AFC', 'Part number': '', 'Version': '', 'Item': 'Chassis'},
              {'Description': 'MX240 Backplane', 'Serial number': 'ABAA2974', 'Part number': '760-021404', 'Version': 'REV 07', 'Item': 'Midplane'},
              {'Description': 'Front Panel Display', 'Serial number': 'XH0679', 'Part number': '760-021392', 'Version': 'REV 03', 'Item': 'FPM Board'},
              {'Description': 'PS 1.4-2.52kW; 90-264V AC in', 'Serial number': 'QCS1247U038', 'Part number': '740-029970', 'Version': 'Rev 10', 'Item': 'PEM 0'},
              {'Description': 'PS 1.4-2.52kW; 90-264V AC in', 'Serial number': 'QCS1433U15V', 'Part number': '740-029970', 'Version': 'Rev 10', 'Item': 'PEM 1'},
              {'Description': 'PS 1.4-2.52kW; 90-264V AC in', 'Serial number': 'QCS1247U0ME', 'Part number': '740-029970', 'Version': 'Rev 10', 'Item': 'PEM 2'},
              {'Description': 'PS 1.4-2.52kW; 90-264V AC in', 'Serial number': 'QCS1433U135', 'Part number': '740-029970', 'Version': 'Rev 10', 'Item': 'PEM 3'},
              {'Description': 'RE-S-1800x4', 'Serial number': '9009228581', 'Part number': '740-031116', 'Version': 'REV 10', 'Item': 'Routing Engine 0'},
              {'Description': 'Enhanced MX SCB 2', 'Serial number': 'CAEE8002', 'Part number': '750-055976', 'Version': 'REV 03', 'Item': 'CB 0'},
              {'Description': 'MPC Type 2 3D', 'Serial number': 'ZT9596', 'Part number': '750-031089', 'Version': 'REV 22', 'Item': 'FPC 1'},
              {'Description': 'MPC PMB 2G', 'Serial number': 'ZS1257', 'Part number': '711-030884', 'Version': 'REV 06', 'Item': 'FPC 1/CPU'},
              {'Description': '3D 4x 10GE  XFP', 'Serial number': 'ZK3514', 'Part number': '750-028387', 'Version': 'REV 27', 'Item': 'FPC 1/MIC 0'},
              {'Description': '2x 10GE  XFP', 'Serial number': 'BUILTIN', 'Part number': 'BUILTIN', 'Version': '', 'Item': 'FPC 1/MIC 0/PIC 0'},
              {'Description': 'XFP-10G-SR', 'Serial number': 'M1302180031', 'Part number': 'NON-JNPR', 'Version': '', 'Item': 'FPC 1/MIC 0/PIC 0/Xcvr 0'},
              {'Description': 'XFP-10G-LR', 'Serial number': 'S1109052223', 'Part number': 'NON-JNPR', 'Version': '$', 'Item': 'FPC 1/MIC 0/PIC 0/Xcvr 1'},
              {'Description': '2x 10GE  XFP', 'Serial number': 'BUILTIN', 'Part number': 'BUILTIN', 'Version': '', 'Item': 'FPC 1/MIC 0/PIC 1'},
              {'Description': '3D 4x 10GE  XFP', 'Serial number': 'ZK3464', 'Part number': '750-028387', 'Version': 'REV 27', 'Item': 'FPC 1/MIC 1'},
              {'Description': '2x 10GE  XFP', 'Serial number': 'BUILTIN', 'Part number': 'BUILTIN', 'Version': '', 'Item': 'FPC 1/MIC 1/PIC 2'},
              {'Description': 'XFP-10G-SR', 'Serial number': 'M1106013253', 'Part number': 'NON-JNPR', 'Version': '', 'Item': 'FPC 1/MIC 1/PIC 2/Xcvr 0'},
              {'Description': '2x 10GE  XFP', 'Serial number': 'BUILTIN', 'Part number': 'BUILTIN', 'Version': '', 'Item': 'FPC 1/MIC 1/PIC 3'},
              {'Description': 'Enhanced Fan Tray', 'Serial number': 'YC9135', 'Part number': '710-030216', 'Version': 'REV 01', 'Item': 'Fan Tray 0'}]
