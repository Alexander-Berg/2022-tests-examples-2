from data.lib import Data


class Data1(Data):
    content = """
<rpc-reply xmlns:junos="http://xml.juniper.net/junos/15.1X53/junos">
    <arp-table-information xmlns="http://xml.juniper.net/junos/15.1X53/junos-arp" junos:style="normal">
        <arp-table-entry>
            <mac-address>68:cc:6e:a8:b8:71</mac-address>
            <ip-address>10.1.1.1</ip-address>
            <hostname>10.1.1.1</hostname>
            <interface-name>ae101.3666</interface-name>
            <arp-table-entry-flags>
                <none/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>2c:21:31:18:0f:00</mac-address>
            <ip-address>10.2.1.1</ip-address>
            <hostname>10.2.1.1</hostname>
            <interface-name>ae102.3666</interface-name>
            <arp-table-entry-flags>
                <none/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>2c:21:31:66:8c:b5</mac-address>
            <ip-address>87.250.239.81</ip-address>
            <hostname>vla1-x7-ae11.yndx.net</hostname>
            <interface-name>ae7.0</interface-name>
            <arp-table-entry-flags>
                <none/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>2c:21:31:66:5c:b5</mac-address>
            <ip-address>87.250.239.155</ip-address>
            <hostname>vla1-x1-ae11.yndx.net</hostname>
            <interface-name>ae1.0</interface-name>
            <arp-table-entry-flags>
                <none/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>2c:21:31:65:cc:b5</mac-address>
            <ip-address>87.250.239.181</ip-address>
            <hostname>vla1-x3-ae11.yndx.net</hostname>
            <interface-name>ae3.0</interface-name>
            <arp-table-entry-flags>
                <none/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>2c:21:31:66:4c:b7</mac-address>
            <ip-address>87.250.239.183</ip-address>
            <hostname>vla1-x5-ae11.yndx.net</hostname>
            <interface-name>ae5.0</interface-name>
            <arp-table-entry-flags>
                <none/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>02:00:01:00:00:05</mac-address>
            <ip-address>128.0.0.5</ip-address>
            <hostname>128.0.0.5</hostname>
            <interface-name>bme1.0</interface-name>
            <arp-table-entry-flags>
                <permanent/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>02:00:01:00:00:05</mac-address>
            <ip-address>128.0.0.6</ip-address>
            <hostname>128.0.0.6</hostname>
            <interface-name>bme1.0</interface-name>
            <arp-table-entry-flags>
                <permanent/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>02:00:00:00:00:10</mac-address>
            <ip-address>128.0.0.16</ip-address>
            <hostname>128.0.0.16</hostname>
            <interface-name>bme0.0</interface-name>
            <arp-table-entry-flags>
                <permanent/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>02:00:00:00:00:11</mac-address>
            <ip-address>128.0.0.17</ip-address>
            <hostname>128.0.0.17</hostname>
            <interface-name>bme0.0</interface-name>
            <arp-table-entry-flags>
                <permanent/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>02:00:00:00:00:12</mac-address>
            <ip-address>128.0.0.18</ip-address>
            <hostname>128.0.0.18</hostname>
            <interface-name>bme0.0</interface-name>
            <arp-table-entry-flags>
                <permanent/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>02:00:00:00:00:13</mac-address>
            <ip-address>128.0.0.19</ip-address>
            <hostname>128.0.0.19</hostname>
            <interface-name>bme0.0</interface-name>
            <arp-table-entry-flags>
                <permanent/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>02:00:00:00:00:14</mac-address>
            <ip-address>128.0.0.20</ip-address>
            <hostname>128.0.0.20</hostname>
            <interface-name>bme0.0</interface-name>
            <arp-table-entry-flags>
                <permanent/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>02:00:00:00:00:15</mac-address>
            <ip-address>128.0.0.21</ip-address>
            <hostname>128.0.0.21</hostname>
            <interface-name>bme0.0</interface-name>
            <arp-table-entry-flags>
                <permanent/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>02:00:00:00:00:16</mac-address>
            <ip-address>128.0.0.22</ip-address>
            <hostname>128.0.0.22</hostname>
            <interface-name>bme0.0</interface-name>
            <arp-table-entry-flags>
                <permanent/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>02:00:00:00:00:17</mac-address>
            <ip-address>128.0.0.23</ip-address>
            <hostname>128.0.0.23</hostname>
            <interface-name>bme0.0</interface-name>
            <arp-table-entry-flags>
                <permanent/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>02:00:00:00:00:18</mac-address>
            <ip-address>128.0.0.24</ip-address>
            <hostname>128.0.0.24</hostname>
            <interface-name>bme0.0</interface-name>
            <arp-table-entry-flags>
                <permanent/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>02:00:00:00:00:19</mac-address>
            <ip-address>128.0.0.25</ip-address>
            <hostname>128.0.0.25</hostname>
            <interface-name>bme0.0</interface-name>
            <arp-table-entry-flags>
                <permanent/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>02:00:00:00:00:1a</mac-address>
            <ip-address>128.0.0.26</ip-address>
            <hostname>128.0.0.26</hostname>
            <interface-name>bme0.0</interface-name>
            <arp-table-entry-flags>
                <permanent/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>02:00:00:00:00:1b</mac-address>
            <ip-address>128.0.0.27</ip-address>
            <hostname>128.0.0.27</hostname>
            <interface-name>bme0.0</interface-name>
            <arp-table-entry-flags>
                <permanent/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>02:00:00:00:00:1c</mac-address>
            <ip-address>128.0.0.28</ip-address>
            <hostname>128.0.0.28</hostname>
            <interface-name>bme0.0</interface-name>
            <arp-table-entry-flags>
                <permanent/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>02:00:00:00:00:30</mac-address>
            <ip-address>128.0.0.48</ip-address>
            <hostname>128.0.0.48</hostname>
            <interface-name>bme2.0</interface-name>
            <arp-table-entry-flags>
                <permanent/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-table-entry>
            <mac-address>2c:21:31:bb:75:4d</mac-address>
            <ip-address>192.168.1.1</ip-address>
            <hostname>192.168.1.1</hostname>
            <interface-name>em2.32768</interface-name>
            <arp-table-entry-flags>
                <none/>
            </arp-table-entry-flags>
        </arp-table-entry>
        <arp-entry-count>23</arp-entry-count>
    </arp-table-information>
    <cli>
        <banner>{master}</banner>
    </cli>
</rpc-reply>

{master}
    """
    cmd = "show arp | display xml"
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
