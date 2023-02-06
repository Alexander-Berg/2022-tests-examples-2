from data.lib import Data


class Data1(Data):
    content = """
MAC flags (S - static MAC, D - dynamic MAC, L - locally learned, P - Persistent static, C - Control MAC
           SE - statistics enabled, NM - non configured MAC, R - remote PE MAC, O - ovsdb MAC)


Ethernet switching table : 20 entries, 20 learned
Routing instance : default-switch
    Vlan                MAC                 MAC         Age    Logical                NH        RTR
    name                address             flags              interface              Index     ID
    VLAN1601            ec:0d:9a:d9:01:a7   D             -   et-0/0/1.0             0         0      
    VLAN1601            ec:0d:9a:d9:01:c7   D             -   et-0/0/0.0             0         0      
    VLAN1601            ec:0d:9a:d9:01:d7   D             -   et-0/0/6.0             0         0      
    VLAN1601            ec:0d:9a:d9:01:ef   D             -   et-0/0/5.0             0         0      
    VLAN1601            ec:0d:9a:d9:02:47   D             -   et-0/0/2.0             0         0      
    VLAN1601            ec:0d:9a:d9:02:77   D             -   et-0/0/3.0             0         0      
    VLAN1601            ec:0d:9a:d9:03:07   D             -   et-0/0/4.0             0         0      
    VLAN2000            ec:0d:9a:d9:01:c7   D             -   et-0/0/0.0             0         0      
    VLAN2000            ec:0d:9a:d9:01:d7   D             -   et-0/0/6.0             0         0      
    VLAN2000            ec:0d:9a:d9:01:ef   D             -   et-0/0/5.0             0         0      
    VLAN2000            ec:0d:9a:d9:02:47   D             -   et-0/0/2.0             0         0      
    VLAN2000            ec:0d:9a:d9:02:77   D             -   et-0/0/3.0             0         0      
    VLAN2000            ec:0d:9a:d9:03:07   D             -   et-0/0/4.0             0         0      
    VLAN802             ec:0d:9a:d9:01:a7   D             -   et-0/0/1.0             0         0      
    VLAN802             ec:0d:9a:d9:01:c7   D             -   et-0/0/0.0             0         0      
    VLAN802             ec:0d:9a:d9:01:d7   D             -   et-0/0/6.0             0         0      
    VLAN802             ec:0d:9a:d9:01:ef   D             -   et-0/0/5.0             0         0      
    VLAN802             ec:0d:9a:d9:02:47   D             -   et-0/0/2.0             0         0      
    VLAN802             ec:0d:9a:d9:02:77   D             -   et-0/0/3.0             0         0      
    VLAN802             ec:0d:9a:d9:03:07   D             -   et-0/0/4.0             0         0      

{master:0}
    """
    cmd = "show ethernet-switching table"
    host = "vla1-5a1"
    version = """
localre:
--------------------------------------------------------------------------
Hostname: vla1-5a1
Model: qfx5200-32c-32q
Junos: 15.1X53-D234.2
JUNOS OS Kernel 64-bit FLEX [20180628.7473aae_builder_stable_10]
JUNOS OS libs [20180628.7473aae_builder_stable_10]
JUNOS OS runtime [20180628.7473aae_builder_stable_10]
JUNOS OS time zone information [20180628.7473aae_builder_stable_10]
JUNOS OS libs compat32 [20180628.7473aae_builder_stable_10]
JUNOS OS 32-bit compatibility [20180628.7473aae_builder_stable_10]
JUNOS py extensions [20180803.224531_builder_junos_151_x53_d234]
JUNOS py base [20180803.224531_builder_junos_151_x53_d234]
JUNOS OS vmguest [20180628.7473aae_builder_stable_10]
JUNOS OS crypto [20180628.7473aae_builder_stable_10]
JUNOS network stack and utilities [20180803.224531_builder_junos_151_x53_d234]
JUNOS libs compat32 [20180803.224531_builder_junos_151_x53_d234]
JUNOS runtime [20180803.224531_builder_junos_151_x53_d234]
JUNOS qfx runtime [20180803.224531_builder_junos_151_x53_d234]
JUNOS qfx platform support [20180803.224531_builder_junos_151_x53_d234]
JUNOS modules [20180803.224531_builder_junos_151_x53_d234]
JUNOS qfx modules [20180803.224531_builder_junos_151_x53_d234]
JUNOS libs [20180803.224531_builder_junos_151_x53_d234]
JUNOS Data Plane Crypto Support [20180803.224531_builder_junos_151_x53_d234]
JUNOS daemons [20180803.224531_builder_junos_151_x53_d234]
JUNOS qfx daemons [20180803.224531_builder_junos_151_x53_d234]
JUNOS Voice Services Container package [20180803.224531_builder_junos_151_x53_d234]
JUNOS Services SSL [20180803.224531_builder_junos_151_x53_d234]
JUNOS Services Stateful Firewall [20180803.224531_builder_junos_151_x53_d234]
JUNOS Services RPM [20180803.224531_builder_junos_151_x53_d234]
JUNOS Services PTSP Container package [20180803.224531_builder_junos_151_x53_d234]
JUNOS Services NAT [20180803.224531_builder_junos_151_x53_d234]
JUNOS Services Mobile Subscriber Service Container package [20180803.224531_builder_junos_151_x53_d234]
JUNOS Services MobileNext Software package [20180803.224531_builder_junos_151_x53_d234]
JUNOS Services LL-PDF Container package [20180803.224531_builder_junos_151_x53_d234]
JUNOS Services Jflow Container package [20180803.224531_builder_junos_151_x53_d234]
JUNOS Services IPSec [20180803.224531_builder_junos_151_x53_d234]
JUNOS IDP Services [20180803.224531_builder_junos_151_x53_d234]
JUNOS Services HTTP Content Management package [20180803.224531_builder_junos_151_x53_d234]
JUNOS Services Crypto [20180803.224531_builder_junos_151_x53_d234]
JUNOS Services Captive Portal and Content Delivery Container package [20180803.224531_builder_junos_151_x53_d234]
JUNOS Border Gateway Function package [20180803.224531_builder_junos_151_x53_d234]
JUNOS AppId Services [20180803.224531_builder_junos_151_x53_d234]
JUNOS Services Application Level Gateways [20180803.224531_builder_junos_151_x53_d234]
JUNOS Services AACL Container package [20180803.224531_builder_junos_151_x53_d234]
JUNOS SDN Software Suite [20180803.224531_builder_junos_151_x53_d234]
JET app jpuppet [3.6.1_3.0]
JUNOS Packet Forwarding Engine Support (DC-PFE) [20180803.224531_builder_junos_151_x53_d234]
JUNOS Packet Forwarding Engine Support (M/T Common) [20180803.224531_builder_junos_151_x53_d234]
JUNOS Online Documentation [20180803.224531_builder_junos_151_x53_d234]
JUNOS FIPS mode utilities [20180803.224531_builder_junos_151_x53_d234]
JET app chef [11.10.4_2.0]
JUNOS Host Software [3.14.52-rt50-WR7.0.0.9_ovp:3.0.3]
JUNOS Host qfx-5e platform package [15.1X53-D234.2]
JUNOS Host qfx-5e control-plane flex package [15.1X53-D234.2]
JUNOS Host qfx-5e data-plane package [15.1X53-D234.2]
JUNOS Host qfx-5e base package [15.1X53-D234.2]
Junos for Automation Enhancement

{master:0}
    """
    result = [{'interface': 'et-0/0/1', 'mac': 'ec:0d:9a:d9:01:a7', 'vlan': '1601'},
              {'interface': 'et-0/0/0', 'mac': 'ec:0d:9a:d9:01:c7', 'vlan': '1601'},
              {'interface': 'et-0/0/6', 'mac': 'ec:0d:9a:d9:01:d7', 'vlan': '1601'},
              {'interface': 'et-0/0/5', 'mac': 'ec:0d:9a:d9:01:ef', 'vlan': '1601'},
              {'interface': 'et-0/0/2', 'mac': 'ec:0d:9a:d9:02:47', 'vlan': '1601'},
              {'interface': 'et-0/0/3', 'mac': 'ec:0d:9a:d9:02:77', 'vlan': '1601'},
              {'interface': 'et-0/0/4', 'mac': 'ec:0d:9a:d9:03:07', 'vlan': '1601'},
              {'interface': 'et-0/0/0', 'mac': 'ec:0d:9a:d9:01:c7', 'vlan': '2000'},
              {'interface': 'et-0/0/6', 'mac': 'ec:0d:9a:d9:01:d7', 'vlan': '2000'},
              {'interface': 'et-0/0/5', 'mac': 'ec:0d:9a:d9:01:ef', 'vlan': '2000'},
              {'interface': 'et-0/0/2', 'mac': 'ec:0d:9a:d9:02:47', 'vlan': '2000'},
              {'interface': 'et-0/0/3', 'mac': 'ec:0d:9a:d9:02:77', 'vlan': '2000'},
              {'interface': 'et-0/0/4', 'mac': 'ec:0d:9a:d9:03:07', 'vlan': '2000'},
              {'interface': 'et-0/0/1', 'mac': 'ec:0d:9a:d9:01:a7', 'vlan': '802'},
              {'interface': 'et-0/0/0', 'mac': 'ec:0d:9a:d9:01:c7', 'vlan': '802'},
              {'interface': 'et-0/0/6', 'mac': 'ec:0d:9a:d9:01:d7', 'vlan': '802'},
              {'interface': 'et-0/0/5', 'mac': 'ec:0d:9a:d9:01:ef', 'vlan': '802'},
              {'interface': 'et-0/0/2', 'mac': 'ec:0d:9a:d9:02:47', 'vlan': '802'},
              {'interface': 'et-0/0/3', 'mac': 'ec:0d:9a:d9:02:77', 'vlan': '802'},
              {'interface': 'et-0/0/4', 'mac': 'ec:0d:9a:d9:03:07', 'vlan': '802'}]
