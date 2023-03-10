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
  <session-id>97043</session-id>
</hello>
"""
req = """<get-interface-information><terse/></get-interface-information>"""
xml = """<rpc-reply xmlns:junos="http://xml.juniper.net/junos/18.4R3/junos" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
<interface-information xmlns="http://xml.juniper.net/junos/18.4R3/junos-interface" junos:style="terse">
<physical-interface>
<name>
gr-0/0/0
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
</physical-interface>
<physical-interface>
<name>
pfe-0/0/0
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<logical-interface>
<name>
pfe-0/0/0.16383
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
inet
</address-family-name>
</address-family>
<address-family>
<address-family-name>
inet6
</address-family-name>
</address-family>
</logical-interface>
</physical-interface>
<physical-interface>
<name>
pfh-0/0/0
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<logical-interface>
<name>
pfh-0/0/0.16383
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
inet
</address-family-name>
</address-family>
</logical-interface>
<logical-interface>
<name>
pfh-0/0/0.16384
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
inet
</address-family-name>
</address-family>
</logical-interface>
</physical-interface>
<physical-interface>
<name>
sxe-0/0/0
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<logical-interface>
<name>
sxe-0/0/0.16386
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>

</logical-interface>
</physical-interface>
<physical-interface>
<name>
sxe-0/0/1
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<logical-interface>
<name>
sxe-0/0/1.16386
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>

</logical-interface>
</physical-interface>
<physical-interface>
<name>
sxe-0/0/2
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<logical-interface>
<name>
sxe-0/0/2.16386
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>

</logical-interface>
</physical-interface>
<physical-interface>
<name>
et-0/0/19
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<logical-interface>
<name>
et-0/0/19.1
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
aenet
</address-family-name>
<ae-bundle-name>
ae321.1
</ae-bundle-name>
</address-family>
</logical-interface>
<logical-interface>
<name>
et-0/0/19.10
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
aenet
</address-family-name>
<ae-bundle-name>
ae321.10
</ae-bundle-name>
</address-family>
</logical-interface>
<logical-interface>
<name>
et-0/0/19.32767
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
aenet
</address-family-name>
<ae-bundle-name>
ae321.32767
</ae-bundle-name>
</address-family>
</logical-interface>
</physical-interface>
<physical-interface>
<name>
et-0/0/23
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<logical-interface>
<name>
et-0/0/23.1
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
aenet
</address-family-name>
<ae-bundle-name>
ae2.1
</ae-bundle-name>
</address-family>
</logical-interface>
<logical-interface>
<name>
et-0/0/23.10
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
aenet
</address-family-name>
<ae-bundle-name>
ae2.10
</ae-bundle-name>
</address-family>
</logical-interface>
<logical-interface>
<name>
et-0/0/23.32767
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
aenet
</address-family-name>
<ae-bundle-name>
ae2.32767
</ae-bundle-name>
</address-family>
</logical-interface>
</physical-interface>
<physical-interface>
<name>
et-0/0/25
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<logical-interface>
<name>
et-0/0/25.1
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
aenet
</address-family-name>
<ae-bundle-name>
ae321.1
</ae-bundle-name>
</address-family>
</logical-interface>
<logical-interface>
<name>
et-0/0/25.10
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
aenet
</address-family-name>
<ae-bundle-name>
ae321.10
</ae-bundle-name>
</address-family>
</logical-interface>
<logical-interface>
<name>
et-0/0/25.32767
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
aenet
</address-family-name>
<ae-bundle-name>
ae321.32767
</ae-bundle-name>
</address-family>
</logical-interface>
</physical-interface>
<physical-interface>
<name>
et-0/0/29
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<logical-interface>
<name>
et-0/0/29.1
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
aenet
</address-family-name>
<ae-bundle-name>
ae1.1
</ae-bundle-name>
</address-family>
</logical-interface>
<logical-interface>
<name>
et-0/0/29.10
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
aenet
</address-family-name>
<ae-bundle-name>
ae1.10
</ae-bundle-name>
</address-family>
</logical-interface>
<logical-interface>
<name>
et-0/0/29.32767
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
aenet
</address-family-name>
<ae-bundle-name>
ae1.32767
</ae-bundle-name>
</address-family>
</logical-interface>
</physical-interface>
<physical-interface>
<name>
et-0/0/31
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<logical-interface>
<name>
et-0/0/31.1
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
aenet
</address-family-name>
<ae-bundle-name>
ae1.1
</ae-bundle-name>
</address-family>
</logical-interface>
<logical-interface>
<name>
et-0/0/31.10
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
aenet
</address-family-name>
<ae-bundle-name>
ae1.10
</ae-bundle-name>
</address-family>
</logical-interface>
<logical-interface>
<name>
et-0/0/31.32767
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
aenet
</address-family-name>
<ae-bundle-name>
ae1.32767
</ae-bundle-name>
</address-family>
</logical-interface>
</physical-interface>
<physical-interface>
<name>
et-0/0/35
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<logical-interface>
<name>
et-0/0/35.1
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
aenet
</address-family-name>
<ae-bundle-name>
ae2.1
</ae-bundle-name>
</address-family>
</logical-interface>
<logical-interface>
<name>
et-0/0/35.10
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
aenet
</address-family-name>
<ae-bundle-name>
ae2.10
</ae-bundle-name>
</address-family>
</logical-interface>
<logical-interface>
<name>
et-0/0/35.32767
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
aenet
</address-family-name>
<ae-bundle-name>
ae2.32767
</ae-bundle-name>
</address-family>
</logical-interface>
</physical-interface>
<physical-interface>
<name>
ae1
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<logical-interface>
<name>
ae1.1
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
inet
</address-family-name>
<interface-address>
<ifa-local junos:emit="emit">
87.250.239.27/31
</ifa-local>
</interface-address>
</address-family>
<address-family>
<address-family-name>
inet6
</address-family-name>
<interface-address>
<ifa-local junos:emit="emit">
fe80::231:4600:1ee:e952/64
</ifa-local>
</interface-address>
</address-family>
<address-family>
<address-family-name junos:emit="emit">
mpls
</address-family-name>
</address-family>
</logical-interface>
<logical-interface>
<name>
ae1.10
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
inet
</address-family-name>
<interface-address>
<ifa-local junos:emit="emit">
10.255.3.65/31
</ifa-local>
</interface-address>
</address-family>
<address-family>
<address-family-name>
inet6
</address-family-name>
<interface-address>
<ifa-local junos:emit="emit">
fe80::231:4600:aee:e952/64
</ifa-local>
</interface-address>
</address-family>
<address-family>
<address-family-name junos:emit="emit">
mpls
</address-family-name>
</address-family>
</logical-interface>
<logical-interface>
<name>
ae1.32767
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
</logical-interface>
</physical-interface>
<physical-interface>
<name>
ae2
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<logical-interface>
<name>
ae2.1
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
inet
</address-family-name>
<interface-address>
<ifa-local junos:emit="emit">
87.250.239.129/31
</ifa-local>
</interface-address>
</address-family>
<address-family>
<address-family-name>
inet6
</address-family-name>
<interface-address>
<ifa-local junos:emit="emit">
fe80::231:4600:1ee:e953/64
</ifa-local>
</interface-address>
</address-family>
<address-family>
<address-family-name junos:emit="emit">
mpls
</address-family-name>
</address-family>
</logical-interface>
<logical-interface>
<name>
ae2.10
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
inet
</address-family-name>
<interface-address>
<ifa-local junos:emit="emit">
10.255.3.67/31
</ifa-local>
</interface-address>
</address-family>
<address-family>
<address-family-name>
inet6
</address-family-name>
<interface-address>
<ifa-local junos:emit="emit">
fe80::231:4600:aee:e953/64
</ifa-local>
</interface-address>
</address-family>
<address-family>
<address-family-name junos:emit="emit">
mpls
</address-family-name>
</address-family>
</logical-interface>
<logical-interface>
<name>
ae2.32767
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
</logical-interface>
</physical-interface>
<physical-interface>
<name>
ae321
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<logical-interface>
<name>
ae321.1
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
inet
</address-family-name>
<interface-address>
<ifa-local junos:emit="emit">
213.180.213.38/31
</ifa-local>
</interface-address>
</address-family>
<address-family>
<address-family-name>
inet6
</address-family-name>
<interface-address>
<ifa-local junos:emit="emit">
fe80::231:4600:1ee:e954/64
</ifa-local>
</interface-address>
</address-family>
<address-family>
<address-family-name junos:emit="emit">
mpls
</address-family-name>
</address-family>
</logical-interface>
<logical-interface>
<name>
ae321.10
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
inet
</address-family-name>
<interface-address>
<ifa-local junos:emit="emit">
10.255.3.68/31
</ifa-local>
</interface-address>
</address-family>
<address-family>
<address-family-name>
inet6
</address-family-name>
<interface-address>
<ifa-local junos:emit="emit">
fe80::231:4600:aee:e954/64
</ifa-local>
</interface-address>
</address-family>
<address-family>
<address-family-name junos:emit="emit">
mpls
</address-family-name>
</address-family>
</logical-interface>
<logical-interface>
<name>
ae321.32767
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
</logical-interface>
</physical-interface>
<physical-interface>
<name>
bme0
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<logical-interface>
<name>
bme0.0
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
inet
</address-family-name>
<interface-address>
<ifa-local junos:emit="emit">
128.0.0.1/2
</ifa-local>
</interface-address>
<interface-address>
<ifa-local junos:emit="emit">
128.0.0.4/2
</ifa-local>
</interface-address>
<interface-address>
<ifa-local junos:emit="emit">
128.0.0.63/2
</ifa-local>
</interface-address>
</address-family>
</logical-interface>
</physical-interface>
<physical-interface>
<name>
cbp0
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
</physical-interface>
<physical-interface>
<name>
dsc
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
</physical-interface>
<physical-interface>
<name>
em0
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<logical-interface>
<name>
em0.0
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
inet
</address-family-name>
<interface-address>
<ifa-local junos:emit="emit">
172.24.212.189/22
</ifa-local>
</interface-address>
</address-family>
</logical-interface>
</physical-interface>
<physical-interface>
<name>
em1
</name>
<admin-status>
up
</admin-status>
<oper-status>
down
</oper-status>
</physical-interface>
<physical-interface>
<name>
em2
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<logical-interface>
<name>
em2.32768
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
inet
</address-family-name>
<interface-address>
<ifa-local junos:emit="emit">
192.168.1.2/24
</ifa-local>
</interface-address>
</address-family>
</logical-interface>
</physical-interface>
<physical-interface>
<name>
em3
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
</physical-interface>
<physical-interface>
<name>
esi
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
</physical-interface>
<physical-interface>
<name>
gre
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
</physical-interface>
<physical-interface>
<name>
ipip
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
</physical-interface>
<physical-interface>
<name>
irb
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
</physical-interface>
<physical-interface>
<name>
lo0
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<logical-interface>
<name>
lo0.0
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
inet
</address-family-name>
<interface-address>
<ifa-local>
87.250.228.168
</ifa-local>
<ifa-destination junos:emit="emit">
0/0
</ifa-destination>
</interface-address>
<interface-address>
<ifa-local>
127.0.0.1
</ifa-local>
<ifa-destination junos:emit="emit">
0/0
</ifa-destination>
</interface-address>
</address-family>
<address-family>
<address-family-name>
inet6
</address-family-name>
<interface-address>
<ifa-local>
fe80::231:460f:fcee:e038
</ifa-local>
<ifa-destination junos:emit="emit">
</ifa-destination>
</interface-address>
</address-family>
</logical-interface>
<logical-interface>
<name>
lo0.10
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
inet
</address-family-name>
<interface-address>
<ifa-local>
10.255.0.71
</ifa-local>
<ifa-destination junos:emit="emit">
0/0
</ifa-destination>
</interface-address>
</address-family>
</logical-interface>
<logical-interface>
<name>
lo0.16385
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
<filter-information>
</filter-information>
<address-family>
<address-family-name>
inet
</address-family-name>
</address-family>
</logical-interface>
</physical-interface>
<physical-interface>
<name>
lsi
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
</physical-interface>
<physical-interface>
<name>
mtun
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
</physical-interface>
<physical-interface>
<name>
pimd
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
</physical-interface>
<physical-interface>
<name>
pime
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
</physical-interface>
<physical-interface>
<name>
pip0
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
</physical-interface>
<physical-interface>
<name>
ptp0
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
</physical-interface>
<physical-interface>
<name>
tap
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
</physical-interface>
<physical-interface>
<name>
vtep
</name>
<admin-status>
up
</admin-status>
<oper-status>
up
</oper-status>
</physical-interface>
</interface-information>
</rpc-reply>
"""
