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
  <nc:session-id>13340</nc:session-id>
</nc:hello>
"""
req = """<get-chassis-inventory></get-chassis-inventory>"""
xml = """<nc:rpc-reply xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:junos="http://xml.juniper.net/junos/17.3R3/junos" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
<chassis-inventory xmlns="http://xml.juniper.net/junos/17.3R3/junos-chassis">
<chassis junos:style="inventory">
<name>Chassis</name>
<serial-number>JN11E9CD7AFA</serial-number>
<description>MX960</description>
<chassis-module>
<name>Midplane</name>
<version>REV 01</version>
<part-number>710-030012</part-number>
<serial-number>ACAB3223</serial-number>
<description>MX960 Backplane</description>
<clei-code>COM8T00CRB</clei-code>
<model-number>CHAS-BP-MX960-S</model-number>
</chassis-module>
<chassis-module>
<name>FPM Board</name>
<version>REV 03</version>
<part-number>710-014974</part-number>
<serial-number>CAAB4517</serial-number>
<description>Front Panel Display</description>
<model-number>CRAFT-MX960-S</model-number>
</chassis-module>
<chassis-module>
<name>PDM</name>
<version>Rev 03</version>
<part-number>740-013110</part-number>
<serial-number>QCS15515065</serial-number>
<description>Power Distribution Module</description>
</chassis-module>
<chassis-module>
<name>PEM 0</name>
<version>Rev 07</version>
<part-number>740-027760</part-number>
<serial-number>QCS1602N05U</serial-number>
<description>PS 4.1kW; 200-240V AC in</description>
<model-number>PWR-MX960-4100-AC-S</model-number>
</chassis-module>
<chassis-module>
<name>PEM 1</name>
<version>Rev 07</version>
<part-number>740-027760</part-number>
<serial-number>QCS1602N05W</serial-number>
<description>PS 4.1kW; 200-240V AC in</description>
<model-number>PWR-MX960-4100-AC-S</model-number>
</chassis-module>
<chassis-module>
<name>PEM 2</name>
<version>Rev 07</version>
<part-number>740-027760</part-number>
<serial-number>QCS1602N061</serial-number>
<description>PS 4.1kW; 200-240V AC in</description>
<model-number>PWR-MX960-4100-AC-S</model-number>
</chassis-module>
<chassis-module>
<name>PEM 3</name>
<version>Rev 07</version>
<part-number>740-027760</part-number>
<serial-number>QCS1603N00K</serial-number>
<description>PS 4.1kW; 200-240V AC in</description>
<model-number>PWR-MX960-4100-AC-S</model-number>
</chassis-module>
<chassis-module>
<name>Routing Engine 0</name>
<version>REV 08</version>
<part-number>750-072923</part-number>
<serial-number>CANC2281</serial-number>
<description>RE-S-2X00x6</description>
<clei-code>CMUCAKGCAB</clei-code>
<model-number>RE-S-X6-64G-LT-S</model-number>
</chassis-module>
<chassis-module>
<name>Routing Engine 1</name>
<version>REV 08</version>
<part-number>750-072923</part-number>
<serial-number>CANC2250</serial-number>
<description>RE-S-2X00x6</description>
<clei-code>CMUCAKGCAB</clei-code>
<model-number>RE-S-X6-64G-LT-S</model-number>
</chassis-module>
<chassis-module>
<name>CB 0</name>
<version>REV 13</version>
<part-number>750-062572</part-number>
<serial-number>CANE7270</serial-number>
<description>Enhanced MX SCB 2</description>
<clei-code>COUCATYBAC</clei-code>
<model-number>SCBE2-MX-S</model-number>
</chassis-module>
<chassis-module>
<name>CB 1</name>
<version>REV 13</version>
<part-number>750-062572</part-number>
<serial-number>CANE7369</serial-number>
<description>Enhanced MX SCB 2</description>
<clei-code>COUCATYBAC</clei-code>
<model-number>SCBE2-MX-S</model-number>
</chassis-module>
<chassis-module>
<name>FPC 2</name>
<version>REV 32</version>
<part-number>750-028467</part-number>
<serial-number>ZV2978</serial-number>
<description>MPC 3D 16x 10GE</description>
<model-number>MPC-3D-16XGE-SFPP</model-number>
<chassis-sub-module>
<name>CPU</name>
<version>REV 10</version>
<part-number>711-029089</part-number>
<serial-number>ZT1884</serial-number>
<description>AMPC PMB</description>
</chassis-sub-module>
<chassis-sub-module>
<name>PIC 0</name>
<part-number>BUILTIN</part-number>
<serial-number>BUILTIN</serial-number>
<description>4x 10GE(LAN) SFP+</description>
<chassis-sub-sub-module>
<name>Xcvr 0</name>
<part-number>NON-JNPR</part-number>
<serial-number>S1810120979</serial-number>
<description>SFP+-10G-LR</description>
</chassis-sub-sub-module>
<chassis-sub-sub-module>
<name>Xcvr 1</name>
<version>S</version>
<part-number>NON-JNPR</part-number>
<serial-number>S1810120980</serial-number>
<description>SFP+-10G-LR</description>
</chassis-sub-sub-module>
<chassis-sub-sub-module>
<name>Xcvr 2</name>
<version>i]#v</version>
<part-number>NON-JNPR</part-number>
<serial-number>S1810120981</serial-number>
<description>SFP+-10G-LR</description>
</chassis-sub-sub-module>
<chassis-sub-sub-module>
<name>Xcvr 3</name>
<version>8</version>
<part-number>NON-JNPR</part-number>
<serial-number>S1810120983</serial-number>
<description>SFP+-10G-LR</description>
</chassis-sub-sub-module>
</chassis-sub-module>
<chassis-sub-module>
<name>PIC 1</name>
<part-number>BUILTIN</part-number>
<serial-number>BUILTIN</serial-number>
<description>4x 10GE(LAN) SFP+</description>
<chassis-sub-sub-module>
<name>Xcvr 0</name>
<part-number>NON-JNPR</part-number>
<serial-number>S1810120984</serial-number>
<description>SFP+-10G-LR</description>
</chassis-sub-sub-module>
<chassis-sub-sub-module>
<name>Xcvr 1</name>
<part-number>NON-JNPR</part-number>
<serial-number>S1810120985</serial-number>
<description>SFP+-10G-LR</description>
</chassis-sub-sub-module>
<chassis-sub-sub-module>
<name>Xcvr 2</name>
<version>|</version>
<part-number>NON-JNPR</part-number>
<serial-number>S1810120987</serial-number>
<description>SFP+-10G-LR</description>
</chassis-sub-sub-module>
<chassis-sub-sub-module>
<name>Xcvr 3</name>
<part-number>NON-JNPR</part-number>
<serial-number>S1810120988</serial-number>
<description>SFP+-10G-LR</description>
</chassis-sub-sub-module>
</chassis-sub-module>
<chassis-sub-module>
<name>PIC 2</name>
<part-number>BUILTIN</part-number>
<serial-number>BUILTIN</serial-number>
<description>4x 10GE(LAN) SFP+</description>
<chassis-sub-sub-module>
<name>Xcvr 0</name>
<version> </version>
<part-number>NON-JNPR</part-number>
<serial-number>S1810120989</serial-number>
<description>SFP+-10G-LR</description>
</chassis-sub-sub-module>
<chassis-sub-sub-module>
<name>Xcvr 1</name>
<part-number>NON-JNPR</part-number>
<serial-number>S1810120990</serial-number>
<description>SFP+-10G-LR</description>
</chassis-sub-sub-module>
<chassis-sub-sub-module>
<name>Xcvr 2</name>
<part-number>NON-JNPR</part-number>
<serial-number>S1810121000</serial-number>
<description>SFP+-10G-LR</description>
</chassis-sub-sub-module>
<chassis-sub-sub-module>
<name>Xcvr 3</name>
<version>N</version>
<part-number>NON-JNPR</part-number>
<serial-number>S1810120999</serial-number>
<description>SFP+-10G-LR</description>
</chassis-sub-sub-module>
</chassis-sub-module>
<chassis-sub-module>
<name>PIC 3</name>
<part-number>BUILTIN</part-number>
<serial-number>BUILTIN</serial-number>
<description>4x 10GE(LAN) SFP+</description>
<chassis-sub-sub-module>
<name>Xcvr 0</name>
<version> </version>
<part-number>NON-JNPR</part-number>
<serial-number>A0CC6UM</serial-number>
<description>SFP+-10G-LR</description>
</chassis-sub-sub-module>
<chassis-sub-sub-module>
<name>Xcvr 1</name>
<version> </version>
<part-number>NON-JNPR</part-number>
<serial-number>A0CBTKR</serial-number>
<description>SFP+-10G-LR</description>
</chassis-sub-sub-module>
<chassis-sub-sub-module>
<name>Xcvr 2</name>
<version> </version>
<part-number>NON-JNPR</part-number>
<serial-number>A0DA3SN</serial-number>
<description>SFP+-10G-LR</description>
</chassis-sub-sub-module>
<chassis-sub-sub-module>
<name>Xcvr 3</name>
<version> </version>
<part-number>NON-JNPR</part-number>
<serial-number>A0DA3RZ</serial-number>
<description>SFP+-10G-LR</description>
</chassis-sub-sub-module>
</chassis-sub-module>
</chassis-module>
<chassis-module>
<name>Fan Tray 0</name>
<version>REV 08</version>
<part-number>740-031521</part-number>
<serial-number>ACAD6296</serial-number>
<description>Enhanced Fan Tray</description>
<model-number>FFANTRAY-MX960-HC-S</model-number>
</chassis-module>
<chassis-module>
<name>Fan Tray 1</name>
<version>REV 08</version>
<part-number>740-031521</part-number>
<serial-number>ACAD6112</serial-number>
<description>Enhanced Fan Tray</description>
<model-number>FFANTRAY-MX960-HC-S</model-number>
</chassis-module>
</chassis>
</chassis-inventory>
</nc:rpc-reply>
"""
