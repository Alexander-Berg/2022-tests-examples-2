from data.lib import Data


class Data1(Data):
    content = """
MAC Address       Address         Name                      Interface               Flags
68:cc:6e:a8:b8:71 10.1.1.1        10.1.1.1                  ae101.3666              none
2c:21:31:18:0f:00 10.2.1.1        10.2.1.1                  ae102.3666              none
2c:21:31:66:8c:b5 87.250.239.81   vla1-x7-ae11.yndx.net     ae7.0                   none
2c:21:31:66:5c:b5 87.250.239.155  vla1-x1-ae11.yndx.net     ae1.0                   none
2c:21:31:65:cc:b5 87.250.239.181  vla1-x3-ae11.yndx.net     ae3.0                   none
2c:21:31:66:4c:b7 87.250.239.183  vla1-x5-ae11.yndx.net     ae5.0                   none
02:00:01:00:00:05 128.0.0.5       128.0.0.5                 bme1.0                  permanent
02:00:01:00:00:05 128.0.0.6       128.0.0.6                 bme1.0                  permanent
02:00:00:00:00:10 128.0.0.16      128.0.0.16                bme0.0                  permanent
02:00:00:00:00:11 128.0.0.17      128.0.0.17                bme0.0                  permanent
02:00:00:00:00:12 128.0.0.18      128.0.0.18                bme0.0                  permanent
02:00:00:00:00:13 128.0.0.19      128.0.0.19                bme0.0                  permanent
02:00:00:00:00:14 128.0.0.20      128.0.0.20                bme0.0                  permanent
02:00:00:00:00:15 128.0.0.21      128.0.0.21                bme0.0                  permanent
02:00:00:00:00:16 128.0.0.22      128.0.0.22                bme0.0                  permanent
02:00:00:00:00:17 128.0.0.23      128.0.0.23                bme0.0                  permanent
02:00:00:00:00:18 128.0.0.24      128.0.0.24                bme0.0                  permanent
02:00:00:00:00:19 128.0.0.25      128.0.0.25                bme0.0                  permanent
02:00:00:00:00:1a 128.0.0.26      128.0.0.26                bme0.0                  permanent
02:00:00:00:00:1b 128.0.0.27      128.0.0.27                bme0.0                  permanent
02:00:00:00:00:1c 128.0.0.28      128.0.0.28                bme0.0                  permanent
02:00:00:00:00:30 128.0.0.48      128.0.0.48                bme2.0                  permanent
2c:21:31:bb:75:4d 192.168.1.1     192.168.1.1               em2.32768               none
Total entries: 23

{master}
    """
    cmd = "show arp"
    host = "vla1-1d1"
    version = """
Hostname: vla1-1d1
Model: qfx10016
Junos: 15.1X53-D67.5
JUNOS OS Kernel 64-bit  [20171218.adb25b3_builder_stable_10]
JUNOS OS libs [20171218.adb25b3_builder_stable_10]
JUNOS OS runtime [20171218.adb25b3_builder_stable_10]
JUNOS OS time zone information [20171218.adb25b3_builder_stable_10]
JUNOS OS libs compat32 [20171218.adb25b3_builder_stable_10]
JUNOS OS 32-bit compatibility [20171218.adb25b3_builder_stable_10]
JUNOS py extensions [20180619.213418_builder_junos_151_x53_d67]
JUNOS py base [20180619.213418_builder_junos_151_x53_d67]
JUNOS OS vmguest [20171218.adb25b3_builder_stable_10]
JUNOS OS crypto [20171218.adb25b3_builder_stable_10]
JUNOS network stack and utilities [20180619.213418_builder_junos_151_x53_d67]
JUNOS libs compat32 [20180619.213418_builder_junos_151_x53_d67]
JUNOS runtime [20180619.213418_builder_junos_151_x53_d67]
JUNOS qfx runtime [20180619.213418_builder_junos_151_x53_d67]
JUNOS qfx platform support [20180619.213418_builder_junos_151_x53_d67]
JUNOS modules [20180619.213418_builder_junos_151_x53_d67]
JUNOS qfx modules [20180619.213418_builder_junos_151_x53_d67]
JUNOS libs [20180619.213418_builder_junos_151_x53_d67]
JUNOS Data Plane Crypto Support [20180619.213418_builder_junos_151_x53_d67]
JUNOS daemons [20180619.213418_builder_junos_151_x53_d67]
JUNOS qfx daemons [20180619.213418_builder_junos_151_x53_d67]
JUNOS Voice Services Container package [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services SSL [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services Stateful Firewall [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services RPM [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services PTSP Container package [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services NAT [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services Mobile Subscriber Service Container package [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services MobileNext Software package [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services LL-PDF Container package [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services Jflow Container package [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services IPSec [20180619.213418_builder_junos_151_x53_d67]
JUNOS IDP Services [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services HTTP Content Management package [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services Crypto [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services Captive Portal and Content Delivery Container package [20180619.213418_builder_junos_151_x53_d67]
JUNOS Border Gateway Function package [20180619.213418_builder_junos_151_x53_d67]
JUNOS AppId Services [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services Application Level Gateways [20180619.213418_builder_junos_151_x53_d67]
JUNOS Services AACL Container package [20180619.213418_builder_junos_151_x53_d67]
JUNOS SDN Software Suite [20180619.213418_builder_junos_151_x53_d67]
JUNOS Packet Forwarding Engine Support (DC-PFE) [20180619.213418_builder_junos_151_x53_d67]
JUNOS Packet Forwarding Engine Support (M/T Common) [20180619.213418_builder_junos_151_x53_d67]
JUNOS Online Documentation [20180619.213418_builder_junos_151_x53_d67]
JUNOS FIPS mode utilities [20180619.213418_builder_junos_151_x53_d67]
JUNOS Host Software [3.14.52-rt50-WR7.0.0.9_ovp:3.0.2]
JUNOS Host qfx-10-m platform package [15.1X53-D67.5]
JUNOS Host qfx-10-m base package [15.1X53-D67.5]
JUNOS Host qfx-10-m data-plane package [15.1X53-D67.5]
JUNOS Host qfx-10-m fabric package [15.1X53-D67.5]
JUNOS Host qfx-10-m control-plane package [15.1X53-D67.5]

{master}
    """
    result = [{'interface': 'ae101.3666', 'ip': '10.1.1.1', 'mac': '68:cc:6e:a8:b8:71'},
              {'interface': 'ae102.3666', 'ip': '10.2.1.1', 'mac': '2c:21:31:18:0f:00'},
              {'interface': 'ae7.0', 'ip': '87.250.239.81', 'mac': '2c:21:31:66:8c:b5'},
              {'interface': 'ae1.0', 'ip': '87.250.239.155', 'mac': '2c:21:31:66:5c:b5'},
              {'interface': 'ae3.0', 'ip': '87.250.239.181', 'mac': '2c:21:31:65:cc:b5'},
              {'interface': 'ae5.0', 'ip': '87.250.239.183', 'mac': '2c:21:31:66:4c:b7'},
              {'interface': 'bme1.0', 'ip': '128.0.0.5', 'mac': '02:00:01:00:00:05'},
              {'interface': 'bme1.0', 'ip': '128.0.0.6', 'mac': '02:00:01:00:00:05'},
              {'interface': 'bme0.0', 'ip': '128.0.0.16', 'mac': '02:00:00:00:00:10'},
              {'interface': 'bme0.0', 'ip': '128.0.0.17', 'mac': '02:00:00:00:00:11'},
              {'interface': 'bme0.0', 'ip': '128.0.0.18', 'mac': '02:00:00:00:00:12'},
              {'interface': 'bme0.0', 'ip': '128.0.0.19', 'mac': '02:00:00:00:00:13'},
              {'interface': 'bme0.0', 'ip': '128.0.0.20', 'mac': '02:00:00:00:00:14'},
              {'interface': 'bme0.0', 'ip': '128.0.0.21', 'mac': '02:00:00:00:00:15'},
              {'interface': 'bme0.0', 'ip': '128.0.0.22', 'mac': '02:00:00:00:00:16'},
              {'interface': 'bme0.0', 'ip': '128.0.0.23', 'mac': '02:00:00:00:00:17'},
              {'interface': 'bme0.0', 'ip': '128.0.0.24', 'mac': '02:00:00:00:00:18'},
              {'interface': 'bme0.0', 'ip': '128.0.0.25', 'mac': '02:00:00:00:00:19'},
              {'interface': 'bme0.0', 'ip': '128.0.0.26', 'mac': '02:00:00:00:00:1a'},
              {'interface': 'bme0.0', 'ip': '128.0.0.27', 'mac': '02:00:00:00:00:1b'},
              {'interface': 'bme0.0', 'ip': '128.0.0.28', 'mac': '02:00:00:00:00:1c'},
              {'interface': 'bme2.0', 'ip': '128.0.0.48', 'mac': '02:00:00:00:00:30'},
              {'interface': 'em2.32768', 'ip': '192.168.1.1', 'mac': '2c:21:31:bb:75:4d'}]
