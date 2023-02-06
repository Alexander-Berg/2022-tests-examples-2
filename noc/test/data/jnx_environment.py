caps = """<!-- No zombies were killed during the creation of this user interface -->
<!-- user gescheit, class j-super-user -->
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <capabilities>
    <capability>urn:ietf:params:netconf:base:1.0</capability>
    <capability>urn:ietf:params:netconf:capability:candidate:1.0</capability>
    <capability>urn:ietf:params:netconf:capability:confirmed-commit:1.0</capability>
    <capability>urn:ietf:params:netconf:capability:validate:1.0</capability>
    <capability>urn:ietf:params:netconf:capability:url:1.0?scheme=http,ftp,file</capability>
    <capability>urn:ietf:params:xml:ns:netconf:base:1.0</capability>
    <capability>urn:ietf:params:xml:ns:netconf:capability:candidate:1.0</capability>
    <capability>urn:ietf:params:xml:ns:netconf:capability:confirmed-commit:1.0</capability>
    <capability>urn:ietf:params:xml:ns:netconf:capability:validate:1.0</capability>
    <capability>urn:ietf:params:xml:ns:netconf:capability:url:1.0?protocol=http,ftp,file</capability>
    <capability>urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring</capability>
    <capability>http://xml.juniper.net/netconf/junos/1.0</capability>
    <capability>http://xml.juniper.net/dmi/system/1.0</capability>
  </capabilities>
  <session-id>4764</session-id>
</hello>
"""
req = """
    <get-environment-information>
    </get-environment-information>
"""
xml = """<rpc-reply xmlns:junos="http://xml.juniper.net/junos/18.4R3/junos" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
<environment-information xmlns="http://xml.juniper.net/junos/18.4R3/junos-chassis">
<environment-item>
<name>FPC 0 Power Supply 0</name>
<class>Power</class>
<status>OK</status>
<temperature junos:celsius="23">23 degrees C / 73 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 Power Supply 1</name>
<status>OK</status>
<temperature junos:celsius="23">23 degrees C / 73 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 Intake Temp Sensor</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="22">22 degrees C / 71 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 Exhaust Temp Sensor</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="27">27 degrees C / 80 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PE2 Temp Sensor</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="30">30 degrees C / 86 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PE1 Temp Sensor</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="28">28 degrees C / 82 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PF0 Temp Sensor</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="33">33 degrees C / 91 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PE0 Temp Sensor</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="28">28 degrees C / 82 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 CPU Die Temp Sensor</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="32">32 degrees C / 89 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 OCXO Temp Sensor</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="31">31 degrees C / 87 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE0-HMC0-DIE</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="33">33 degrees C / 91 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE0-HMC0-TOP</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="26">26 degrees C / 78 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE0-HMC0-BOT</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="35">35 degrees C / 95 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE0-HMC1-DIE</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="36">36 degrees C / 96 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE0-HMC1-TOP</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="28">28 degrees C / 82 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE0-HMC1-BOT</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="40">40 degrees C / 104 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE0-HMC2-DIE</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="37">37 degrees C / 98 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE0-HMC2-TOP</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="31">31 degrees C / 87 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE0-HMC2-BOT</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="41">41 degrees C / 105 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE1-HMC0-DIE</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="34">34 degrees C / 93 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE1-HMC0-TOP</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="30">30 degrees C / 86 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE1-HMC0-BOT</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="33">33 degrees C / 91 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE1-HMC1-DIE</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="37">37 degrees C / 98 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE1-HMC1-TOP</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="31">31 degrees C / 87 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE1-HMC1-BOT</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="38">38 degrees C / 100 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE1-HMC2-DIE</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="37">37 degrees C / 98 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE1-HMC2-TOP</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="34">34 degrees C / 93 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE1-HMC2-BOT</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="39">39 degrees C / 102 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE2-HMC0-DIE</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="35">35 degrees C / 95 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE2-HMC0-TOP</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="31">31 degrees C / 87 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE2-HMC0-BOT</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="34">34 degrees C / 93 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE2-HMC1-DIE</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="38">38 degrees C / 100 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE2-HMC1-TOP</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="35">35 degrees C / 95 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE2-HMC1-BOT</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="39">39 degrees C / 102 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE2-HMC2-DIE</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="40">40 degrees C / 104 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE2-HMC2-TOP</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="35">35 degrees C / 95 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 PFE2-HMC2-BOT</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="42">42 degrees C / 107 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 Fan Tray 0</name>
<class>Fans</class>
<status>OK</status>
<comment>Spinning at normal speed</comment>
</environment-item>
<environment-item>
<name>FPC 0 Fan Tray 1</name>
<status>OK</status>
<comment>Spinning at normal speed</comment>
</environment-item>
<environment-item>
<name>FPC 0 Fan Tray 2</name>
<status>OK</status>
<comment>Spinning at normal speed</comment>
</environment-item>
</environment-information>
</rpc-reply>
"""
