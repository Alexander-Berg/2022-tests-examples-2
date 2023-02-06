# flake8: noqa

caps = """<!-- No zombies were killed during the creation of this user interface -->
<!-- user netinfra-mon, class j-mon -->
<nc:hello xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
   <nc:capabilities>
    <nc:capability>urn:ietf:params:netconf:base:1.0</nc:capability>
    <nc:capability>urn:ietf:params:netconf:capability:candidate:1.0</nc:capability>
    <nc:capability>urn:ietf:params:netconf:capability:confirmed-commit:1.0</nc:capability>
    <nc:capability>urn:ietf:params:netconf:capability:validate:1.0</nc:capability>
    <nc:capability>urn:ietf:params:netconf:capability:url:1.0?protocol=http,ftp,file</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:netconf:base:1.0</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:netconf:capability:candidate:1.0</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:netconf:capability:confirmed-commit:1.0</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:netconf:capability:validate:1.0</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:netconf:capability:url:1.0?protocol=http,ftp,file</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring</nc:capability>
    <nc:capability>http://xml.juniper.net/netconf/junos/1.0</nc:capability>
    <nc:capability>http://xml.juniper.net/dmi/system/1.0</nc:capability>
  </nc:capabilities>
  <nc:session-id>40477</nc:session-id>
</nc:hello>
"""
req = """
    <get-environment-information>

    </get-environment-information>
"""
xml = """<nc:rpc-reply xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:junos="http://xml.juniper.net/junos/18.2R3/junos" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
<environment-information xmlns="http://xml.juniper.net/junos/18.2R3/junos-chassis">
<environment-item>
<name>CB 0 Top Right Inlet Sensor</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="31">31 degrees C / 87 degrees F</temperature>
</environment-item>
<environment-item>
<name>CB 0 Top Left Inlet Sensor</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="34">34 degrees C / 93 degrees F</temperature>
</environment-item>
<environment-item>
<name>CB 0 Top Right Exhaust Sensor</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="38">38 degrees C / 100 degrees F</temperature>
</environment-item>
<environment-item>
<name>CB 0 Top Left Exhaust Sensor</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="53">53 degrees C / 127 degrees F</temperature>
</environment-item>
<environment-item>
<name>CB 0 CPU Core-0 Temp</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="40">40 degrees C / 104 degrees F</temperature>
</environment-item>
<environment-item>
<name>CB 0 CPU Core-1 Temp</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="39">39 degrees C / 102 degrees F</temperature>
</environment-item>
<environment-item>
<name>CB 0 CPU Core-2 Temp</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="40">40 degrees C / 104 degrees F</temperature>
</environment-item>
<environment-item>
<name>CB 0 CPU Core-3 Temp</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="39">39 degrees C / 102 degrees F</temperature>
</environment-item>
<environment-item>
<name>CB 0 CPU Core-4 Temp</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="39">39 degrees C / 102 degrees F</temperature>
</environment-item>
<environment-item>
<name>CB 0 CPU Core-5 Temp</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="39">39 degrees C / 102 degrees F</temperature>
</environment-item>
<environment-item>
<name>CB 0 CPU Core-6 Temp</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="39">39 degrees C / 102 degrees F</temperature>
</environment-item>
<environment-item>
<name>CB 0 CPU Core-7 Temp</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="40">40 degrees C / 104 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 EA0_HMC0 Logic die </name>
<status>OK</status>
<temperature junos:celsius="66">66 degrees C / 150 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 EA0_HMC0 DRAM botm </name>
<status>OK</status>
<temperature junos:celsius="63">63 degrees C / 145 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 EA0_HMC1 Logic die </name>
<status>OK</status>
<temperature junos:celsius="71">71 degrees C / 159 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 EA0_HMC1 DRAM botm </name>
<status>OK</status>
<temperature junos:celsius="68">68 degrees C / 154 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 EA0 Chip</name>
<status>OK</status>
<temperature junos:celsius="73">73 degrees C / 163 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 EA0-XR0 Chip</name>
<status>OK</status>
<temperature junos:celsius="54">54 degrees C / 129 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 EA0-XR1 Chip</name>
<status>OK</status>
<temperature junos:celsius="58">58 degrees C / 136 degrees F</temperature>
</environment-item>
<environment-item>
<name>PEM 0</name>
<class>Power</class>
<status>OK</status>
<temperature junos:celsius="37">37 degrees C / 98 degrees F</temperature>
</environment-item>
<environment-item>
<name>PEM 1</name>
<class>Power</class>
<status>Check</status>
</environment-item>
<environment-item>
<name>Fan Tray 0 Fan 0</name>
<class>Fans</class>
<status>OK</status>
<comment>Spinning at normal speed</comment>
</environment-item>
<environment-item>
<name>Fan Tray 0 Fan 1</name>
<class>Fans</class>
<status>OK</status>
<comment>Spinning at normal speed</comment>
</environment-item>
<environment-item>
<name>Fan Tray 1 Fan 0</name>
<class>Fans</class>
<status>OK</status>
<comment>Spinning at normal speed</comment>
</environment-item>
<environment-item>
<name>Fan Tray 1 Fan 1</name>
<class>Fans</class>
<status>OK</status>
<comment>Spinning at normal speed</comment>
</environment-item>
<environment-item>
<name>Fan Tray 2 Fan 0</name>
<class>Fans</class>
<status>OK</status>
<comment>Spinning at normal speed</comment>
</environment-item>
<environment-item>
<name>Fan Tray 2 Fan 1</name>
<class>Fans</class>
<status>OK</status>
<comment>Spinning at normal speed</comment>
</environment-item>
</environment-information>
</nc:rpc-reply>
"""
