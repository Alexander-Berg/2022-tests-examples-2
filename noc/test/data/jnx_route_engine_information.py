# flake8: noqa

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
  <session-id>35971</session-id>
</hello>
"""
req = """
    <get-route-engine-information>

    </get-route-engine-information>
"""
xml = """<rpc-reply xmlns:junos="http://xml.juniper.net/junos/18.4R3/junos" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
<route-engine-information xmlns="http://xml.juniper.net/junos/18.4R3/junos-chassis">
<route-engine>
<slot>0</slot>
<mastership-state>master</mastership-state>
<status>OK</status>
<temperature junos:celsius="23">23 degrees C / 73 degrees F</temperature>
<cpu-temperature junos:celsius="23">23 degrees C / 73 degrees F</cpu-temperature>
<memory-dram-size>7766 MB</memory-dram-size>
<memory-installed-size>(8192 MB installed)</memory-installed-size>
<memory-buffer-utilization>10</memory-buffer-utilization>
<cpu-user>1</cpu-user>
<cpu-background>0</cpu-background>
<cpu-system>1</cpu-system>
<cpu-interrupt>0</cpu-interrupt>
<cpu-idle>98</cpu-idle>
<cpu-user1>2</cpu-user1>
<cpu-background1>0</cpu-background1>
<cpu-system1>2</cpu-system1>
<cpu-interrupt1>0</cpu-interrupt1>
<cpu-idle1>96</cpu-idle1>
<cpu-user2>2</cpu-user2>
<cpu-background2>0</cpu-background2>
<cpu-system2>2</cpu-system2>
<cpu-interrupt2>0</cpu-interrupt2>
<cpu-idle2>96</cpu-idle2>
<cpu-user3>2</cpu-user3>
<cpu-background3>0</cpu-background3>
<cpu-system3>2</cpu-system3>
<cpu-interrupt3>0</cpu-interrupt3>
<cpu-idle3>96</cpu-idle3>
<model>RE-QFX10002-36Q</model>
<serial-number>BUILTIN</serial-number>
<start-time junos:seconds="1605610127">2020-11-17 13:48:47 MSK</start-time>
<up-time junos:seconds="10291386">119 days, 2 hours, 43 minutes, 6 seconds</up-time>
<last-reboot-reason>0x1:power cycle/failure</last-reboot-reason>
<load-average-one>0.24</load-average-one>
<load-average-five>0.24</load-average-five>
<load-average-fifteen>0.25</load-average-fifteen>
</route-engine>
</route-engine-information>
</rpc-reply>
"""
