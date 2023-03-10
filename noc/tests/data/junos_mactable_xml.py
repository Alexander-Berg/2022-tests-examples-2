from data.lib import Data


class Data1(Data):
    content = """
<rpc-reply xmlns:junos="http://xml.juniper.net/junos/15.1X53/junos">
    <l2ng-l2ald-rtb-macdb>
        <l2ng-l2ald-mac-entry-vlan junos:style="brief-rtb">
            <mac-count-global>20</mac-count-global>
            <learnt-mac-count>20</learnt-mac-count>
            <l2ng-l2-mac-routing-instance>default-switch</l2ng-l2-mac-routing-instance>
            <l2ng-l2-vlan-id>1601</l2ng-l2-vlan-id>
            <l2ng-mac-entry>
                <l2ng-l2-mac-vlan-name>VLAN1601</l2ng-l2-mac-vlan-name>
                <l2ng-l2-mac-address>ec:0d:9a:d9:01:a7</l2ng-l2-mac-address>
                <l2ng-l2-mac-flags>D</l2ng-l2-mac-flags>
                <l2ng-l2-mac-age>-</l2ng-l2-mac-age>
                <l2ng-l2-mac-logical-interface>et-0/0/1.0</l2ng-l2-mac-logical-interface>
                <l2ng-l2-mac-fwd-next-hop>0</l2ng-l2-mac-fwd-next-hop>
                <l2ng-l2-mac-rtr-id>0</l2ng-l2-mac-rtr-id>
            </l2ng-mac-entry>
            <l2ng-mac-entry>
                <l2ng-l2-mac-vlan-name>VLAN1601</l2ng-l2-mac-vlan-name>
                <l2ng-l2-mac-address>ec:0d:9a:d9:01:c7</l2ng-l2-mac-address>
                <l2ng-l2-mac-flags>D</l2ng-l2-mac-flags>
                <l2ng-l2-mac-age>-</l2ng-l2-mac-age>
                <l2ng-l2-mac-logical-interface>et-0/0/0.0</l2ng-l2-mac-logical-interface>
                <l2ng-l2-mac-fwd-next-hop>0</l2ng-l2-mac-fwd-next-hop>
                <l2ng-l2-mac-rtr-id>0</l2ng-l2-mac-rtr-id>
            </l2ng-mac-entry>
            <l2ng-mac-entry>
                <l2ng-l2-mac-vlan-name>VLAN1601</l2ng-l2-mac-vlan-name>
                <l2ng-l2-mac-address>ec:0d:9a:d9:01:d7</l2ng-l2-mac-address>
                <l2ng-l2-mac-flags>D</l2ng-l2-mac-flags>
                <l2ng-l2-mac-age>-</l2ng-l2-mac-age>
                <l2ng-l2-mac-logical-interface>et-0/0/6.0</l2ng-l2-mac-logical-interface>
                <l2ng-l2-mac-fwd-next-hop>0</l2ng-l2-mac-fwd-next-hop>
                <l2ng-l2-mac-rtr-id>0</l2ng-l2-mac-rtr-id>
            </l2ng-mac-entry>
            <l2ng-mac-entry>
                <l2ng-l2-mac-vlan-name>VLAN1601</l2ng-l2-mac-vlan-name>
                <l2ng-l2-mac-address>ec:0d:9a:d9:01:ef</l2ng-l2-mac-address>
                <l2ng-l2-mac-flags>D</l2ng-l2-mac-flags>
                <l2ng-l2-mac-age>-</l2ng-l2-mac-age>
                <l2ng-l2-mac-logical-interface>et-0/0/5.0</l2ng-l2-mac-logical-interface>
                <l2ng-l2-mac-fwd-next-hop>0</l2ng-l2-mac-fwd-next-hop>
                <l2ng-l2-mac-rtr-id>0</l2ng-l2-mac-rtr-id>
            </l2ng-mac-entry>
            <l2ng-mac-entry>
                <l2ng-l2-mac-vlan-name>VLAN1601</l2ng-l2-mac-vlan-name>
                <l2ng-l2-mac-address>ec:0d:9a:d9:02:47</l2ng-l2-mac-address>
                <l2ng-l2-mac-flags>D</l2ng-l2-mac-flags>
                <l2ng-l2-mac-age>-</l2ng-l2-mac-age>
                <l2ng-l2-mac-logical-interface>et-0/0/2.0</l2ng-l2-mac-logical-interface>
                <l2ng-l2-mac-fwd-next-hop>0</l2ng-l2-mac-fwd-next-hop>
                <l2ng-l2-mac-rtr-id>0</l2ng-l2-mac-rtr-id>
            </l2ng-mac-entry>
            <l2ng-mac-entry>
                <l2ng-l2-mac-vlan-name>VLAN1601</l2ng-l2-mac-vlan-name>
                <l2ng-l2-mac-address>ec:0d:9a:d9:02:77</l2ng-l2-mac-address>
                <l2ng-l2-mac-flags>D</l2ng-l2-mac-flags>
                <l2ng-l2-mac-age>-</l2ng-l2-mac-age>
                <l2ng-l2-mac-logical-interface>et-0/0/3.0</l2ng-l2-mac-logical-interface>
                <l2ng-l2-mac-fwd-next-hop>0</l2ng-l2-mac-fwd-next-hop>
                <l2ng-l2-mac-rtr-id>0</l2ng-l2-mac-rtr-id>
            </l2ng-mac-entry>
            <l2ng-mac-entry>
                <l2ng-l2-mac-vlan-name>VLAN1601</l2ng-l2-mac-vlan-name>
                <l2ng-l2-mac-address>ec:0d:9a:d9:03:07</l2ng-l2-mac-address>
                <l2ng-l2-mac-flags>D</l2ng-l2-mac-flags>
                <l2ng-l2-mac-age>-</l2ng-l2-mac-age>
                <l2ng-l2-mac-logical-interface>et-0/0/4.0</l2ng-l2-mac-logical-interface>
                <l2ng-l2-mac-fwd-next-hop>0</l2ng-l2-mac-fwd-next-hop>
                <l2ng-l2-mac-rtr-id>0</l2ng-l2-mac-rtr-id>
            </l2ng-mac-entry>
            <l2ng-mac-entry>
                <l2ng-l2-mac-vlan-name>VLAN2000</l2ng-l2-mac-vlan-name>
                <l2ng-l2-mac-address>ec:0d:9a:d9:01:c7</l2ng-l2-mac-address>
                <l2ng-l2-mac-flags>D</l2ng-l2-mac-flags>
                <l2ng-l2-mac-age>-</l2ng-l2-mac-age>
                <l2ng-l2-mac-logical-interface>et-0/0/0.0</l2ng-l2-mac-logical-interface>
                <l2ng-l2-mac-fwd-next-hop>0</l2ng-l2-mac-fwd-next-hop>
                <l2ng-l2-mac-rtr-id>0</l2ng-l2-mac-rtr-id>
            </l2ng-mac-entry>
            <l2ng-mac-entry>
                <l2ng-l2-mac-vlan-name>VLAN2000</l2ng-l2-mac-vlan-name>
                <l2ng-l2-mac-address>ec:0d:9a:d9:01:d7</l2ng-l2-mac-address>
                <l2ng-l2-mac-flags>D</l2ng-l2-mac-flags>
                <l2ng-l2-mac-age>-</l2ng-l2-mac-age>
                <l2ng-l2-mac-logical-interface>et-0/0/6.0</l2ng-l2-mac-logical-interface>
                <l2ng-l2-mac-fwd-next-hop>0</l2ng-l2-mac-fwd-next-hop>
                <l2ng-l2-mac-rtr-id>0</l2ng-l2-mac-rtr-id>
            </l2ng-mac-entry>
            <l2ng-mac-entry>
                <l2ng-l2-mac-vlan-name>VLAN2000</l2ng-l2-mac-vlan-name>
                <l2ng-l2-mac-address>ec:0d:9a:d9:01:ef</l2ng-l2-mac-address>
                <l2ng-l2-mac-flags>D</l2ng-l2-mac-flags>
                <l2ng-l2-mac-age>-</l2ng-l2-mac-age>
                <l2ng-l2-mac-logical-interface>et-0/0/5.0</l2ng-l2-mac-logical-interface>
                <l2ng-l2-mac-fwd-next-hop>0</l2ng-l2-mac-fwd-next-hop>
                <l2ng-l2-mac-rtr-id>0</l2ng-l2-mac-rtr-id>
            </l2ng-mac-entry>
            <l2ng-mac-entry>
                <l2ng-l2-mac-vlan-name>VLAN2000</l2ng-l2-mac-vlan-name>
                <l2ng-l2-mac-address>ec:0d:9a:d9:02:47</l2ng-l2-mac-address>
                <l2ng-l2-mac-flags>D</l2ng-l2-mac-flags>
                <l2ng-l2-mac-age>-</l2ng-l2-mac-age>
                <l2ng-l2-mac-logical-interface>et-0/0/2.0</l2ng-l2-mac-logical-interface>
                <l2ng-l2-mac-fwd-next-hop>0</l2ng-l2-mac-fwd-next-hop>
                <l2ng-l2-mac-rtr-id>0</l2ng-l2-mac-rtr-id>
            </l2ng-mac-entry>
            <l2ng-mac-entry>
                <l2ng-l2-mac-vlan-name>VLAN2000</l2ng-l2-mac-vlan-name>
                <l2ng-l2-mac-address>ec:0d:9a:d9:02:77</l2ng-l2-mac-address>
                <l2ng-l2-mac-flags>D</l2ng-l2-mac-flags>
                <l2ng-l2-mac-age>-</l2ng-l2-mac-age>
                <l2ng-l2-mac-logical-interface>et-0/0/3.0</l2ng-l2-mac-logical-interface>
                <l2ng-l2-mac-fwd-next-hop>0</l2ng-l2-mac-fwd-next-hop>
                <l2ng-l2-mac-rtr-id>0</l2ng-l2-mac-rtr-id>
            </l2ng-mac-entry>
            <l2ng-mac-entry>
                <l2ng-l2-mac-vlan-name>VLAN2000</l2ng-l2-mac-vlan-name>
                <l2ng-l2-mac-address>ec:0d:9a:d9:03:07</l2ng-l2-mac-address>
                <l2ng-l2-mac-flags>D</l2ng-l2-mac-flags>
                <l2ng-l2-mac-age>-</l2ng-l2-mac-age>
                <l2ng-l2-mac-logical-interface>et-0/0/4.0</l2ng-l2-mac-logical-interface>
                <l2ng-l2-mac-fwd-next-hop>0</l2ng-l2-mac-fwd-next-hop>
                <l2ng-l2-mac-rtr-id>0</l2ng-l2-mac-rtr-id>
            </l2ng-mac-entry>
            <l2ng-mac-entry>
                <l2ng-l2-mac-vlan-name>VLAN802</l2ng-l2-mac-vlan-name>
                <l2ng-l2-mac-address>ec:0d:9a:d9:01:a7</l2ng-l2-mac-address>
                <l2ng-l2-mac-flags>D</l2ng-l2-mac-flags>
                <l2ng-l2-mac-age>-</l2ng-l2-mac-age>
                <l2ng-l2-mac-logical-interface>et-0/0/1.0</l2ng-l2-mac-logical-interface>
                <l2ng-l2-mac-fwd-next-hop>0</l2ng-l2-mac-fwd-next-hop>
                <l2ng-l2-mac-rtr-id>0</l2ng-l2-mac-rtr-id>
            </l2ng-mac-entry>
            <l2ng-mac-entry>
                <l2ng-l2-mac-vlan-name>VLAN802</l2ng-l2-mac-vlan-name>
                <l2ng-l2-mac-address>ec:0d:9a:d9:01:c7</l2ng-l2-mac-address>
                <l2ng-l2-mac-flags>D</l2ng-l2-mac-flags>
                <l2ng-l2-mac-age>-</l2ng-l2-mac-age>
                <l2ng-l2-mac-logical-interface>et-0/0/0.0</l2ng-l2-mac-logical-interface>
                <l2ng-l2-mac-fwd-next-hop>0</l2ng-l2-mac-fwd-next-hop>
                <l2ng-l2-mac-rtr-id>0</l2ng-l2-mac-rtr-id>
            </l2ng-mac-entry>
            <l2ng-mac-entry>
                <l2ng-l2-mac-vlan-name>VLAN802</l2ng-l2-mac-vlan-name>
                <l2ng-l2-mac-address>ec:0d:9a:d9:01:d7</l2ng-l2-mac-address>
                <l2ng-l2-mac-flags>D</l2ng-l2-mac-flags>
                <l2ng-l2-mac-age>-</l2ng-l2-mac-age>
                <l2ng-l2-mac-logical-interface>et-0/0/6.0</l2ng-l2-mac-logical-interface>
                <l2ng-l2-mac-fwd-next-hop>0</l2ng-l2-mac-fwd-next-hop>
                <l2ng-l2-mac-rtr-id>0</l2ng-l2-mac-rtr-id>
            </l2ng-mac-entry>
            <l2ng-mac-entry>
                <l2ng-l2-mac-vlan-name>VLAN802</l2ng-l2-mac-vlan-name>
                <l2ng-l2-mac-address>ec:0d:9a:d9:01:ef</l2ng-l2-mac-address>
                <l2ng-l2-mac-flags>D</l2ng-l2-mac-flags>
                <l2ng-l2-mac-age>-</l2ng-l2-mac-age>
                <l2ng-l2-mac-logical-interface>et-0/0/5.0</l2ng-l2-mac-logical-interface>
                <l2ng-l2-mac-fwd-next-hop>0</l2ng-l2-mac-fwd-next-hop>
                <l2ng-l2-mac-rtr-id>0</l2ng-l2-mac-rtr-id>
            </l2ng-mac-entry>
            <l2ng-mac-entry>
                <l2ng-l2-mac-vlan-name>VLAN802</l2ng-l2-mac-vlan-name>
                <l2ng-l2-mac-address>ec:0d:9a:d9:02:47</l2ng-l2-mac-address>
                <l2ng-l2-mac-flags>D</l2ng-l2-mac-flags>
                <l2ng-l2-mac-age>-</l2ng-l2-mac-age>
                <l2ng-l2-mac-logical-interface>et-0/0/2.0</l2ng-l2-mac-logical-interface>
                <l2ng-l2-mac-fwd-next-hop>0</l2ng-l2-mac-fwd-next-hop>
                <l2ng-l2-mac-rtr-id>0</l2ng-l2-mac-rtr-id>
            </l2ng-mac-entry>
            <l2ng-mac-entry>
                <l2ng-l2-mac-vlan-name>VLAN802</l2ng-l2-mac-vlan-name>
                <l2ng-l2-mac-address>ec:0d:9a:d9:02:77</l2ng-l2-mac-address>
                <l2ng-l2-mac-flags>D</l2ng-l2-mac-flags>
                <l2ng-l2-mac-age>-</l2ng-l2-mac-age>
                <l2ng-l2-mac-logical-interface>et-0/0/3.0</l2ng-l2-mac-logical-interface>
                <l2ng-l2-mac-fwd-next-hop>0</l2ng-l2-mac-fwd-next-hop>
                <l2ng-l2-mac-rtr-id>0</l2ng-l2-mac-rtr-id>
            </l2ng-mac-entry>
            <l2ng-mac-entry>
                <l2ng-l2-mac-vlan-name>VLAN802</l2ng-l2-mac-vlan-name>
                <l2ng-l2-mac-address>ec:0d:9a:d9:03:07</l2ng-l2-mac-address>
                <l2ng-l2-mac-flags>D</l2ng-l2-mac-flags>
                <l2ng-l2-mac-age>-</l2ng-l2-mac-age>
                <l2ng-l2-mac-logical-interface>et-0/0/4.0</l2ng-l2-mac-logical-interface>
                <l2ng-l2-mac-fwd-next-hop>0</l2ng-l2-mac-fwd-next-hop>
                <l2ng-l2-mac-rtr-id>0</l2ng-l2-mac-rtr-id>
            </l2ng-mac-entry>
        </l2ng-l2ald-mac-entry-vlan>
    </l2ng-l2ald-rtb-macdb>
    <cli>
        <banner>{master:0}</banner>
    </cli>
</rpc-reply>

{master:0}
    """
    cmd = "show ethernet-switching table | display xml"
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
    result = [{'interface': 'et-0/0/1', 'mac': 'ec0d9ad901a7', 'vlan': '1601'},
              {'interface': 'et-0/0/0', 'mac': 'ec0d9ad901c7', 'vlan': '1601'},
              {'interface': 'et-0/0/6', 'mac': 'ec0d9ad901d7', 'vlan': '1601'},
              {'interface': 'et-0/0/5', 'mac': 'ec0d9ad901ef', 'vlan': '1601'},
              {'interface': 'et-0/0/2', 'mac': 'ec0d9ad90247', 'vlan': '1601'},
              {'interface': 'et-0/0/3', 'mac': 'ec0d9ad90277', 'vlan': '1601'},
              {'interface': 'et-0/0/4', 'mac': 'ec0d9ad90307', 'vlan': '1601'},
              {'interface': 'et-0/0/0', 'mac': 'ec0d9ad901c7', 'vlan': '2000'},
              {'interface': 'et-0/0/6', 'mac': 'ec0d9ad901d7', 'vlan': '2000'},
              {'interface': 'et-0/0/5', 'mac': 'ec0d9ad901ef', 'vlan': '2000'},
              {'interface': 'et-0/0/2', 'mac': 'ec0d9ad90247', 'vlan': '2000'},
              {'interface': 'et-0/0/3', 'mac': 'ec0d9ad90277', 'vlan': '2000'},
              {'interface': 'et-0/0/4', 'mac': 'ec0d9ad90307', 'vlan': '2000'},
              {'interface': 'et-0/0/1', 'mac': 'ec0d9ad901a7', 'vlan': '802'},
              {'interface': 'et-0/0/0', 'mac': 'ec0d9ad901c7', 'vlan': '802'},
              {'interface': 'et-0/0/6', 'mac': 'ec0d9ad901d7', 'vlan': '802'},
              {'interface': 'et-0/0/5', 'mac': 'ec0d9ad901ef', 'vlan': '802'},
              {'interface': 'et-0/0/2', 'mac': 'ec0d9ad90247', 'vlan': '802'},
              {'interface': 'et-0/0/3', 'mac': 'ec0d9ad90277', 'vlan': '802'},
              {'interface': 'et-0/0/4', 'mac': 'ec0d9ad90307', 'vlan': '802'}]
