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
  <nc:session-id>6094</nc:session-id>
</nc:hello>
"""
req = """
    <get-environment-information>
    </get-environment-information>
"""
xml = """<nc:rpc-reply xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:junos="http://xml.juniper.net/junos/18.3R3/junos" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
<environment-information xmlns="http://xml.juniper.net/junos/18.3R3/junos-chassis">
<environment-item>
<name>FPC 0 Power Supply 0</name>
<class>Power</class>
<status>OK</status>
<temperature junos:celsius="39">39 degrees C / 102 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 Power Supply 1</name>
<status>Present</status>
</environment-item>
<environment-item>
<name>FPC 0 Sensor FrontLeft 2 In</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="29">29 degrees C / 84 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 Sensor Center</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="34">34 degrees C / 93 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 Sensor FrontLeft 3 In</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="29">29 degrees C / 84 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 Sensor Frontleft 1 In</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="28">28 degrees C / 82 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 Sensor RearLeft Ex</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="30">30 degrees C / 86 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 Sensor RearMiddle Ex</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="32">32 degrees C / 89 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 Sensor CPU Die Temp</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="40">40 degrees C / 104 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 Sensor RearRight Ex</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="31">31 degrees C / 87 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 Sensor FrontRight 1 In</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="29">29 degrees C / 84 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 Sensor FrontRight 2 In</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="28">28 degrees C / 82 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 Sensor FrontMiddle 1 In</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="32">32 degrees C / 89 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 Sensor FrontMiddle 2 In</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="32">32 degrees C / 89 degrees F</temperature>
</environment-item>
<environment-item>
<name>FPC 0 Sensor PFE Die Temp</name>
<class>Temp</class>
<status>OK</status>
<temperature junos:celsius="44">44 degrees C / 111 degrees F</temperature>
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
<environment-item>
<name>FPC 0 Fan Tray 3</name>
<status>OK</status>
<comment>Spinning at normal speed</comment>
</environment-item>
<environment-item>
<name>FPC 0 Fan Tray 4</name>
<status>OK</status>
<comment>Spinning at normal speed</comment>
</environment-item>
</environment-information>
</nc:rpc-reply>
"""
