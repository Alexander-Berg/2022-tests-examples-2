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
  <nc:session-id>47939</nc:session-id>
</nc:hello>
"""
req = """<get-route-engine-information></get-route-engine-information>"""
xml = """<nc:rpc-reply xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:junos="http://xml.juniper.net/junos/18.2R3/junos" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
<route-engine-information xmlns="http://xml.juniper.net/junos/18.2R3/junos-chassis">
<route-engine>
<status>OK</status>
<temperature junos:celsius="50">50 degrees C / 122 degrees F</temperature>
<cpu-temperature junos:celsius="49">49 degrees C / 120 degrees F</cpu-temperature>
<memory-dram-size>16339 MB</memory-dram-size>
<memory-installed-size>(16384 MB installed)</memory-installed-size>
<memory-buffer-utilization>6</memory-buffer-utilization>
<cpu-user>1</cpu-user>
<cpu-background>0</cpu-background>
<cpu-system>2</cpu-system>
<cpu-interrupt>0</cpu-interrupt>
<cpu-idle>96</cpu-idle>
<cpu-user1>1</cpu-user1>
<cpu-background1>0</cpu-background1>
<cpu-system1>1</cpu-system1>
<cpu-interrupt1>0</cpu-interrupt1>
<cpu-idle1>98</cpu-idle1>
<cpu-user2>1</cpu-user2>
<cpu-background2>0</cpu-background2>
<cpu-system2>1</cpu-system2>
<cpu-interrupt2>0</cpu-interrupt2>
<cpu-idle2>98</cpu-idle2>
<cpu-user3>1</cpu-user3>
<cpu-background3>0</cpu-background3>
<cpu-system3>1</cpu-system3>
<cpu-interrupt3>0</cpu-interrupt3>
<cpu-idle3>98</cpu-idle3>
<model>RE-S-1600x8</model>
<start-time junos:seconds="1604100082">2020-10-31 02:21:22 MSK</start-time>
<up-time junos:seconds="23921912">276 days, 20 hours, 58 minutes, 32 seconds</up-time>
<last-reboot-reason>0x4000:VJUNOS reboot</last-reboot-reason>
<load-average-one>0.16</load-average-one>
<load-average-five>0.19</load-average-five>
<load-average-fifteen>0.17</load-average-fifteen>
</route-engine>
</route-engine-information>
</nc:rpc-reply>
"""
