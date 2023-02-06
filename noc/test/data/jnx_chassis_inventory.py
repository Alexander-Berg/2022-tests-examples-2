# pylint: skip-file

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
  <session-id>95034</session-id>
</hello>
"""
req = """get-chassis-inventory"""
xml = """<rpc-reply xmlns:junos="http://xml.juniper.net/junos/18.4R3/junos" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
<chassis-inventory xmlns="http://xml.juniper.net/junos/18.4R3/junos-chassis">
<chassis junos:style="inventory">
<name>Chassis</name>
<serial-number>DA636</serial-number>
<description>QFX10002-36Q</description>
<chassis-module>
<name>Pseudo CB 0</name>
</chassis-module>
<chassis-module>
<name>Routing Engine 0</name>
<part-number>BUILTIN</part-number>
<serial-number>BUILTIN</serial-number>
<description>RE-QFX10002-36Q</description>
<clei-code>CMMTM00ARA</clei-code>
<model-number>QFX10002-36Q-CHAS</model-number>
</chassis-module>
<chassis-module>
<name>FPC 0</name>
<version>REV 26</version>
<part-number>750-059497</part-number>
<serial-number>ACNJ5607</serial-number>
<description>QFX10002-36Q</description>
<clei-code>CMMTM00ARA</clei-code>
<model-number>QFX10002-36Q-CHAS</model-number>
<chassis-sub-module>
<name>CPU</name>
<part-number>BUILTIN</part-number>
<serial-number>BUILTIN</serial-number>
<description>FPC CPU</description>
</chassis-sub-module>
<chassis-sub-module>
<name>PIC 0</name>
<part-number>BUILTIN</part-number>
<serial-number>BUILTIN</serial-number>
<description>36X40G</description>
<clei-code>CMMTM00ARA</clei-code>
<model-number>QFX10002-36Q-CHAS</model-number>
<chassis-sub-sub-module>
<name>Xcvr 19</name>
<version>424</version>
<part-number>NON-JNPR</part-number>
<serial-number>MT2023FT13588</serial-number>
<description>QSFP-100GBASE-SR4</description>
</chassis-sub-sub-module>
<chassis-sub-sub-module>
<name>Xcvr 23</name>
<part-number>NON-JNPR</part-number>
<serial-number>033GAMNMKA000729</serial-number>
<description>QSFP-100G-CWDM4</description>
</chassis-sub-sub-module>
<chassis-sub-sub-module>
<name>Xcvr 25</name>
<version>715</version>
<part-number>NON-JNPR</part-number>
<serial-number>MT2023FT12737</serial-number>
<description>QSFP-100GBASE-SR4</description>
</chassis-sub-sub-module>
<chassis-sub-sub-module>
<name>Xcvr 29</name>
<part-number>NON-JNPR</part-number>
<serial-number>033GAMNMKA000711</serial-number>
<description>QSFP-100G-CWDM4</description>
</chassis-sub-sub-module>
<chassis-sub-sub-module>
<name>Xcvr 31</name>
<part-number>NON-JNPR</part-number>
<serial-number>033GAMNMKB000023</serial-number>
<description>QSFP-100G-CWDM4</description>
</chassis-sub-sub-module>
<chassis-sub-sub-module>
<name>Xcvr 35</name>
<part-number>NON-JNPR</part-number>
<serial-number>033GAMNMKA000588</serial-number>
<description>QSFP-100G-CWDM4</description>
</chassis-sub-sub-module>
</chassis-sub-module>
<chassis-sub-module>
<name>Mezz</name>
<version>REV 02</version>
<part-number>711-059316</part-number>
<serial-number>ACNG3352</serial-number>
<description>QFX10002 36X40G Mezz</description>
</chassis-sub-module>
</chassis-module>
<chassis-module>
<name>Power Supply 0</name>
<version>REV 03</version>
<part-number>740-054405</part-number>
<serial-number>1EDN5345818</serial-number>
<description>AC AFO 1600W PSU</description>
<clei-code>CMUPADHBAA</clei-code>
<model-number>JPSU-1600W-AC-AFO</model-number>
</chassis-module>
<chassis-module>
<name>Power Supply 1</name>
<version>REV 03</version>
<part-number>740-054405</part-number>
<serial-number>1EDN5345621</serial-number>
<description>AC AFO 1600W PSU</description>
<clei-code>CMUPADHBAA</clei-code>
<model-number>JPSU-1600W-AC-AFO</model-number>
</chassis-module>
<chassis-module>
<name>Fan Tray 0</name>
<description>QFX10002 Fan Tray 0, Front to Back Airflow - AFO</description>
<model-number>QFX10002, Assy,Sub,80mm Fan Tray,AFO-AFO</model-number>
</chassis-module>
<chassis-module>
<name>Fan Tray 1</name>
<description>QFX10002 Fan Tray 1, Front to Back Airflow - AFO</description>
<model-number>QFX10002, Assy,Sub,80mm Fan Tray,AFO-AFO</model-number>
</chassis-module>
<chassis-module>
<name>Fan Tray 2</name>
<description>QFX10002 Fan Tray 2, Front to Back Airflow - AFO</description>
<model-number>QFX10002, Assy,Sub,80mm Fan Tray,AFO-AFO</model-number>
</chassis-module>
</chassis>
</chassis-inventory>
</rpc-reply>
"""
