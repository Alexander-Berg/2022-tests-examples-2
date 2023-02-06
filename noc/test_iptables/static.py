from collections import namedtuple

from balancer_agent.operations.balancer_configs.config_containers import AFSpec

V6_RULES_MC = """-P INPUT DROP
-A INPUT -d 2a02:6b8::1:119/128 -j mc.y.ru
-A INPUT -d 2a02:6b8:0:DEAD::BEEF/128 -j mc-internal.metrika.y.net
-A INPUT -d ff00::/8 -m set --match-set _YANDEXNETS_v6 src -j DROP
-A INPUT -p tcp -m tcp --dport 25 -j REJECT --reject-with icmp6-port-unreachable
-A INPUT -m set --match-set _YANDEXNETS_v6 src -m limit --limit 1/sec -j LOG""".split(
    "\n"
)


V4_RULES_MC = """-P INPUT DROP
-P FORWARD ACCEPT
-P OUTPUT DROP
-N 77.88.44.48/28
-A 213.180.193.0/24 -d 213.180.193.240/28 -j 213.180.193.240/28
-A 213.180.193.0/24 -j DROP
-A 213.180.193.0/28 -j DROP
-A 213.180.193.112/28 -d 213.180.193.119/32 -j mc.y.ru
-A 5.45.202.0/28 -d 5.45.202.5/32 -j mc.y.ru
-A 5.45.202.0/28 -d 5.45.202.6/32 -j mc.y.ru
-A 5.45.202.0/28 -d 5.45.202.7/32 -j mc.y.ru
-A 5.45.202.0/28 -d 5.45.202.8/32 -j mc.y.ru
-A 5.45.202.0/28 -j DROP
-A 77.88.21.112/28 -d 77.88.21.119/32 -j mc.y.ru
-A 87.250.250.112/28 -d 87.250.250.119/32 -j mc.y.ru
-A 87.250.251.112/28 -d 87.250.251.119/32 -j mc.y.ru
-A 93.158.134.112/28 -d 93.158.134.119/32 -j mc.y.ru
-A VIP_INPUT -j DROP
-A mc-internal.metrika.y.net -s 80.80.0.192/27 -p tcp -m tcp --dport 1234 -j ACCEPT
-A mc-internal.metrika.y.net -j VIP_INPUT
-A mc.y.ru -p tcp -m multiport --dports 80,443 -j ACCEPT
-A mc.y.ru -j VIP_INPUT
""".split(
    "\n"
)


MockVS = namedtuple("MockVS", "ip, af")


MC_VSS = [
    MockVS("5.45.202.5", AFSpec.IP),
    MockVS("5.45.202.6", AFSpec.IP),
    MockVS("5.45.202.7", AFSpec.IP),
    MockVS("5.45.202.8", AFSpec.IP),
    MockVS("77.88.21.119", AFSpec.IP),
    MockVS("87.250.250.119", AFSpec.IP),
    MockVS("87.250.251.119", AFSpec.IP),
    MockVS("93.158.134.119", AFSpec.IP),
    MockVS("213.180.193.119", AFSpec.IP),
    MockVS("2a02:6b8::1:119", AFSpec.IPV6),
]


class MockedConfig:
    vss = MC_VSS
    fqdn = "mc.yandex.ru"

    @property
    def body(self):
        return self

    @property
    def service(self):
        return self
