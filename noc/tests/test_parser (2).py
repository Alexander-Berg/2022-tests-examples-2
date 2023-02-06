from yanetagent.dns import DummyDNSCache
from yanetagent.parser import parse, Converter, ConversionSettings


class TestConverter:
    def test_tablearg_skipto_srcdsttable(self) -> None:
        text = r""":BEGIN
        table _SKIPTO_SRC_PREFIX_ add 5.45.192.0/18 :TUN64_TOWORLD_FASTTCP
        table _SKIPTO_SRC_PREFIX_ add 80.239.142.160/27 :TUN64_TOWORLD_TURBO
        table _SKIPTO_SRC_PREFIX_ add 77.88.46.0/25 :TUN64_TOWORLD_MEDIASTORAGE
        table _SKIPTO_DST_PREFIX_ add 213.180.200.0/25 :TUN64_FROMWORLD_MEDIASTORAGE
        table _SKIPTO_DST_PREFIX_ add 141.8.182.48/30 :TUN64_FROMWORLD_FASTTCP_DNS
        table _SKIPTO_DST_PREFIX_ add 149.5.241.0/28 :TUN64_FROMWORLD_FASTTCP_DNS

        add skipto :IN ip from any to any in

        :IN
        add skipto tablearg ip from table(_SKIPTO_SRC_PREFIX_) to any
        add skipto tablearg ip from any to table(_SKIPTO_DST_PREFIX_)
        add deny ip from any to any

        :TUN64_TOWORLD_FASTTCP
        add allow ip from any to any

        :TUN64_TOWORLD_TURBO
        add allow icmp from any to any
        add deny ip from any to any

        :TUN64_TOWORLD_MEDIASTORAGE
        add allow ip from any to any

        :TUN64_FROMWORLD_MEDIASTORAGE
        add deny tcp from any to any setup

        :TUN64_FROMWORLD_FASTTCP_DNS
        add deny icmp from any to any
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1
                }
            ],
            ":IN": [
                {
                    "filter": {"source": ["80.239.142.160/27"]},
                    "nextSection": ":TUN64_TOWORLD_TURBO",
                    "id": 1000000002
                },
                {
                    "filter": {"source": ["77.88.46.0/25"]},
                    "nextSection": ":TUN64_TOWORLD_MEDIASTORAGE",
                    "id": 1000100002
                },
                {
                    "filter": {"source": ["5.45.192.0/18"]},
                    "nextSection": ":TUN64_TOWORLD_FASTTCP",
                    "id": 1000200002
                },
                {
                    "filter": {"destination": ["213.180.200.0/25"]},
                    "nextSection": ":TUN64_FROMWORLD_MEDIASTORAGE",
                    "id": 1000000003
                },
                {
                    "filter": {"destination": ["149.5.241.0/28", "141.8.182.48/30"]},
                    "nextSection": ":TUN64_FROMWORLD_FASTTCP_DNS",
                    "id": 1000100003
                },
                {
                    "nextModule": "drop",
                    "id": 4
                }
            ],
            ":TUN64_TOWORLD_TURBO": [
                {
                    "filter": {"protocol": {"type": "icmp"}},
                    "id": 6
                },
                {
                    "nextModule": "drop",
                    "id": 7}
            ],
            ":TUN64_TOWORLD_MEDIASTORAGE": [
                {
                    "id": 8
                }
            ],
            ":TUN64_TOWORLD_FASTTCP": [
                {
                    "id": 5
                }
            ],
            ":TUN64_FROMWORLD_MEDIASTORAGE": [
                {
                    "filter": {"protocol": {"type": "tcp", "tcpflags": "syn,!ack"}},
                    "nextModule": "drop",
                    "id": 9
                }
            ],
            ":TUN64_FROMWORLD_FASTTCP_DNS": [
                {
                    "filter": {"protocol": {"type": "icmp"}},
                    "nextModule": "drop",
                    "id": 10
                }
            ]
        }

        tree = parse(text)
        assert expected == Converter().convert_to_yanet(tree)

    def test_rule_comment(self) -> None:
        text = r"""
        add skipto :IN ip from any to any in

        :IN
        add allow ip from any to 1.1.1.1 // TUN64_TO_MDS
        add deny ip from any to any
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1,
                },
            ],
            ":IN": [
                {
                    "filter": {
                        "destination": ["1.1.1.1"],
                    },
                    "id": 2,
                },
                {
                    "nextModule": "drop",
                    "id": 3,
                },
            ],
        }

        tree = parse(text)
        assert expected == Converter().convert_to_yanet(tree)

    def test_convert_simple(self) -> None:
        text = r""":BEGIN
        add skipto :IN ip from any to any in

        :IN
        add allow tcp from 2a02:6b8:ff1c:2030::/ffff:ffff:ffff:fff0:: to any 80
        add deny ip from any to any
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1,
                },
            ],
            ":IN": [
                {
                    "filter": {
                        "source": ["2a02:6b8:ff1c:2030::/ffff:ffff:ffff:fff0::"],
                        "protocol": {"type": "tcp", "destination": [80]},
                    },
                    "id": 2,
                },
                {
                    "nextModule": "drop",
                    "id": 3,
                },
            ],
        }

        tree = parse(text)
        assert expected == Converter().convert_to_yanet(tree)

    def test_convert_tcp_setup(self) -> None:
        text = r""":BEGIN
        add skipto :IN ip from any to any in

        :IN
        add deny tcp from any to any setup
        add allow tcp from any to any
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1,
                },
            ],
            ":IN": [
                {
                    "filter": {
                        "protocol": {"type": "tcp", "tcpflags": "syn,!ack"},
                    },
                    "nextModule": "drop",
                    "id": 2,
                },
                {
                    "filter": {
                        "protocol": {"type": "tcp"},
                    },
                    "id": 3,
                },
            ],
        }

        tree = parse(text)
        assert expected == Converter().convert_to_yanet(tree)

    def test_convert_autotest_example(self) -> None:
        text = r""":BEGIN
        add skipto :IN ip from any to any in

        :IN
        add deny udp from 10.0.0.0/24 to any
        add allow tcp from 10.0.0.0/24 to 10.0.0.0/24 dst-port 80,443
        add deny tcp from 10.1.0.0/24 to 21.0.0.16/28 src-port 1024 frag
        add allow tcp from 10.1.0.0/24 to 21.0.0.16/28 src-port 1024
        add allow icmp from 10.2.0.0/24 to any frag
        add deny icmp from 10.2.0.0/24 to any icmptypes 1,2,3,9,10,13
        add allow icmp from 10.0.0.0/8 to 10.0.0.0/8

        add deny tcp from any to 2000::1:0/112
        add allow udp from 2000::1:0/112 to 2000::1:0/112 dst-port 53
        add deny udp from 2000::0/112 to any src-port 53 dst-port 53 frag
        add allow udp from 2000::0/112 to any src-port 53 dst-port 53
        add deny icmp6 from 2200::/112 to 2000::/112
        add allow icmp6 from any to 2000::/112
        add deny tcp from 2300::/112 to 2300::/112 tcpflags urg,psh
        add allow tcp from 2300::/112 to 2300::/112
        add deny tcp from 2301::/112 to 2301::/112 tcpflags fin,!rst
        add allow tcp from 2301::/112 to 2301::/112

        add allow tcp from any to any established
        add deny ip from any to any
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {
                        "direction": "in"
                    },
                    "nextSection": ":IN",
                    "id": 1,
                }
            ],
            ":IN": [
                {
                    "filter": {
                        "source": [
                            "10.0.0.0/24"
                        ],
                        "protocol": {
                            "type": "udp"
                        }
                    },
                    "nextModule": "drop",
                    "id": 2,
                },
                {
                    "filter": {
                        "source": [
                            "10.0.0.0/24"
                        ],
                        "destination": [
                            "10.0.0.0/24"
                        ],
                        "protocol": {
                            "type": "tcp",
                            "destination": [
                                80,
                                443
                            ]
                        }
                    },
                    "id": 3,
                },
                {
                    "filter": {
                        "source": [
                            "10.1.0.0/24"
                        ],
                        "destination": [
                            "21.0.0.16/28"
                        ],
                        "fragmentaton": [
                            2
                        ],
                        "protocol": {
                            "type": "tcp",
                            "source": [
                                1024
                            ]
                        }
                    },
                    "nextModule": "drop",
                    "id": 4,
                },
                {
                    "filter": {
                        "source": [
                            "10.1.0.0/24"
                        ],
                        "destination": [
                            "21.0.0.16/28"
                        ],
                        "protocol": {
                            "type": "tcp",
                            "source": [
                                1024
                            ]
                        }
                    },
                    "id": 5,
                },
                {
                    "filter": {
                        "source": [
                            "10.2.0.0/24"
                        ],
                        "fragmentaton": [
                            2
                        ],
                        "protocol": {
                            "type": "icmp"
                        }
                    },
                    "id": 6,
                },
                {
                    "filter": {
                        "source": [
                            "10.2.0.0/24"
                        ],
                        "protocol": {
                            "type": "icmp",
                            "icmptypes": [
                                1,
                                2,
                                3,
                                9,
                                10,
                                13
                            ]
                        }
                    },
                    "nextModule": "drop",
                    "id": 7,
                },
                {
                    "filter": {
                        "source": [
                            "10.0.0.0/8"
                        ],
                        "destination": [
                            "10.0.0.0/8"
                        ],
                        "protocol": {
                            "type": "icmp"
                        }
                    },
                    "id": 8,
                },
                {
                    "filter": {
                        "destination": [
                            "2000::1:0/112"
                        ],
                        "protocol": {
                            "type": "tcp"
                        }
                    },
                    "nextModule": "drop",
                    "id": 9,
                },
                {
                    "filter": {
                        "source": [
                            "2000::1:0/112"
                        ],
                        "destination": [
                            "2000::1:0/112"
                        ],
                        "protocol": {
                            "type": "udp",
                            "destination": [
                                53
                            ]
                        }
                    },
                    "id": 10,
                },
                {
                    "filter": {
                        "source": [
                            "2000::/112"
                        ],
                        "fragmentaton": [
                            2
                        ],
                        "protocol": {
                            "type": "udp",
                            "source": [
                                53
                            ],
                            "destination": [
                                53
                            ]
                        }
                    },
                    "nextModule": "drop",
                    "id": 11,
                },
                {
                    "filter": {
                        "source": [
                            "2000::/112"
                        ],
                        "protocol": {
                            "type": "udp",
                            "source": [
                                53
                            ],
                            "destination": [
                                53
                            ]
                        }
                    },
                    "id": 12,
                },
                {
                    "filter": {
                        "source": [
                            "2200::/112"
                        ],
                        "destination": [
                            "2000::/112"
                        ],
                        "protocol": {
                            "type": "icmp6"
                        }
                    },
                    "nextModule": "drop",
                    "id": 13,
                },
                {
                    "filter": {
                        "destination": [
                            "2000::/112"
                        ],
                        "protocol": {
                            "type": "icmp6"
                        }
                    },
                    "id": 14,
                },
                {
                    "filter": {
                        "source": [
                            "2300::/112"
                        ],
                        "destination": [
                            "2300::/112"
                        ],
                        "protocol": {
                            "type": "tcp",
                            "tcpflags": "urg,psh"
                        }
                    },
                    "nextModule": "drop",
                    "id": 15,
                },
                {
                    "filter": {
                        "source": [
                            "2300::/112"
                        ],
                        "destination": [
                            "2300::/112"
                        ],
                        "protocol": {
                            "type": "tcp"
                        }
                    },
                    "id": 16,
                },
                {
                    "filter": {
                        "source": [
                            "2301::/112"
                        ],
                        "destination": [
                            "2301::/112"
                        ],
                        "protocol": {
                            "type": "tcp",
                            "tcpflags": "fin,!rst"
                        }
                    },
                    "nextModule": "drop",
                    "id": 17,
                },
                {
                    "filter": {
                        "source": [
                            "2301::/112"
                        ],
                        "destination": [
                            "2301::/112"
                        ],
                        "protocol": {
                            "type": "tcp"
                        }
                    },
                    "id": 18,
                },
                {
                    "filter": {
                        "protocol": {
                            "type": "tcp",
                            "tcpflags": "established"
                        }
                    },
                    "id": 19,
                },
                {
                    "nextModule": "drop",
                    "id": 20,
                }
            ]
        }

        tree = parse(text)
        assert expected == Converter().convert_to_yanet(tree)

    def test_convert_with_macro(self) -> None:
        text = r"""
        table _YANDEXNETS_ add 2a02:6b8::/32
        table _YANDEXNETS_ add 2620:10f:d000::/44

        add skipto :IN ip from any to any in

        :IN
        add allow tcp from _YANDEXNETS_ to any 80
        add deny ip from any to any
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1,
                },
            ],
            ":IN": [
                {
                    "filter": {
                        "source": ["2a02:6b8::/32", "2620:10f:d000::/44"],
                        "protocol": {"type": "tcp", "destination": [80]},
                    },
                    "id": 2,
                },
                {
                    "nextModule": "drop",
                    "id": 3,
                },
            ],
        }

        tree = parse(text)
        assert expected == Converter().convert_to_yanet(tree)

    def test_convert_with_hostname(self) -> None:
        text = r"""
        table _YANDEXNETS_ add 2a02:6b8::/32
        table _YANDEXNETS_ add 2620:10f:d000::/44

        add skipto :IN ip from any to any in

        :IN
        add allow tcp from _YANDEXNETS_ to yandex.ru 80
        add deny ip from any to any
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1,
                },
            ],
            ":IN": [
                {
                    "filter": {
                        "source": ["2a02:6b8::/32", "2620:10f:d000::/44"],
                        "destination": ["2a02:6b8:a::a"],
                        "protocol": {"type": "tcp", "destination": [80]},
                    },
                    "id": 2,
                },
                {
                    "nextModule": "drop",
                    "id": 3,
                },
            ],
        }

        tree = parse(text)
        assert expected == Converter(dnscache=DummyDNSCache({"yandex.ru": ["2a02:6b8:a::a"]})).convert_to_yanet(tree)

    def test_convert_with_port_range(self) -> None:
        text = r"""
        add skipto :IN ip from any to any in

        :IN
        add allow tcp from 2a02:6b8::/32 to 2a02:6b8::/32 80-228
        add deny ip from any to any
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1,
                },
            ],
            ":IN": [
                {
                    "filter": {
                        "source": ["2a02:6b8::/32"],
                        "destination": ["2a02:6b8::/32"],
                        "protocol": {"type": "tcp", "destination": [[80, 228]]},
                    },
                    "id": 2,
                },
                {
                    "nextModule": "drop",
                    "id": 3,
                },
            ],
        }

        tree = parse(text)
        assert expected == Converter().convert_to_yanet(tree)

    def test_convert_fix_ip(self) -> None:
        text = r"""
        add skipto :IN ip from any to any in

        :IN
        add allow tcp from { 109.188.067.072 or 95.163.10.10 } to any 80
        add deny ip from any to any
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1,
                },
            ],
            ":IN": [
                {
                    "filter": {
                        "source": ["109.188.67.72", "95.163.10.10"],
                        "protocol": {"type": "tcp", "destination": [80]},
                    },
                    "id": 2,
                },
                {
                    "nextModule": "drop",
                    "id": 3,
                },
            ],
        }

        tree = parse(text)
        assert expected == Converter().convert_to_yanet(tree)

    def test_convert_proto_or(self) -> None:
        text = r"""
        add skipto :IN ip from any to any in
        table _ADDC_ add polite.yandex.ru
        table _CORPDNS_ add ns-cache.yandex.net
        table _YANDEXNETS_ add 2a02:6b8::/32

        :IN
        add allow { udp or tcp } from { _ADDC_ or _CORPDNS_ } domain to { _YANDEXNETS_ }
        add deny ip from any to any
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1,
                },
            ],
            ":IN": [
                {
                    "filter": {
                        "source": ["2a02:6b8:0:1484::ad4", "2a02:6b8::1:1"],
                        "destination": ["2a02:6b8::/32"],
                        "protocol": {"type": "udp", "source": [53]},
                    },
                    "id": 2,
                },
                {
                    "filter": {
                        "source": ["2a02:6b8:0:1484::ad4", "2a02:6b8::1:1"],
                        "destination": ["2a02:6b8::/32"],
                        "protocol": {"type": "tcp", "source": [53]},
                    },
                    "id": 2,
                },
                {
                    "nextModule": "drop",
                    "id": 3,
                },
            ],
        }

        tree = parse(text)
        dnscache = DummyDNSCache({
            "polite.yandex.ru": ["2a02:6b8:0:1484::ad4"],
            "ns-cache.yandex.net": ["2a02:6b8::1:1"],
        })
        assert expected == Converter(dnscache=dnscache).convert_to_yanet(tree)

    def test_convert_icmptype_option(self) -> None:
        text = r"""
        add skipto :IN ip from any to any in

        :IN
        add allow icmp from any to any in icmptype 11
        add deny ip from any to any
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1,
                },
            ],
            ":IN": [
                {
                    "filter": {
                        "direction": "in",
                        "protocol": {"type": "icmp", "icmptypes": [11]},
                    },
                    "id": 2,
                },
                {
                    "nextModule": "drop",
                    "id": 3,
                },
            ],
        }

        tree = parse(text)
        assert expected == Converter().convert_to_yanet(tree)

    def test_convert_icmp6types_option(self) -> None:
        text = r"""
        add skipto :IN ip from any to any in

        :IN
        add allow icmp6 from any to any in icmp6types 11
        add deny ip from any to any
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1,
                },
            ],
            ":IN": [
                {
                    "filter": {
                        "direction": "in",
                        "protocol": {"type": "icmp6", "icmp6types": [11]},
                    },
                    "id": 2,
                },
                {
                    "nextModule": "drop",
                    "id": 3,
                },
            ],
        }

        tree = parse(text)
        assert expected == Converter().convert_to_yanet(tree)

    def test_convert_icmp6types_option_with_ip_protocol(self) -> None:
        text = r"""
        add skipto :IN ip from any to any in

        :IN
        add allow ip from any to any icmp6types 133,134,135,136 in
        add deny ip from any to any
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1,
                },
            ],
            ":IN": [
                {
                    "filter": {
                        "direction": "in",
                        "protocol": {"type": "icmp6", "icmp6types": [133, 134, 135, 136]},
                    },
                    "id": 2,
                },
                {
                    "nextModule": "drop",
                    "id": 3,
                },
            ],
        }

        tree = parse(text)
        print(Converter().convert_to_yanet(tree))
        assert expected == Converter().convert_to_yanet(tree)

    def test_convert_ipencap(self) -> None:
        text = r"""
        add skipto :IN ip from any to any in
        table _YANDEXNETS_ add 2a02:6b8::/32
        table _TUN64_ANYCAST_ add 2a02:6b8:b010:a0ff::/64

        :IN
        add allow ip from { _YANDEXNETS_ } to { _TUN64_ANYCAST_ } proto ipencap in
        add deny ip from any to any
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1,
                },
            ],
            ":IN": [
                {
                    "filter": {
                        "direction": "in",
                        "source": ["2a02:6b8::/32"],
                        "destination": ["2a02:6b8:b010:a0ff::/64"],
                        "protocol": {"type": "ipencap"},
                    },
                    "id": 2,
                },
                {
                    "nextModule": "drop",
                    "id": 3,
                },
            ],
        }

        tree = parse(text)
        assert expected == Converter().convert_to_yanet(tree)

    def test_convert_ospf(self) -> None:
        text = r"""
        add skipto :IN ip from any to any in

        :IN
        add allow ospf from 93.158.140.0/24 to any in
        add deny ip from any to any
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1,
                },
            ],
            ":IN": [
                {
                    "filter": {
                        "direction": "in",
                        "source": ["93.158.140.0/24"],
                        "protocol": {"type": "ospf"},
                    },
                    "id": 2,
                },
                {
                    "nextModule": "drop",
                    "id": 3,
                },
            ],
        }

        tree = parse(text)
        assert expected == Converter().convert_to_yanet(tree)

    def test_convert_index_rules(self) -> None:
        text = r""":BEGIN
            add skipto :IN ip from any to any in

            :IN
            add allow tcp from 2a02:6b8:ff1c:2030::/ffff:ffff:ffff:fff0:: to any 80
            add deny ip from any to any
            """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1,
                },
            ],
            ":IN": [
                {
                    "filter": {
                        "source": ["2a02:6b8:ff1c:2030::/ffff:ffff:ffff:fff0::"],
                        "protocol": {"type": "tcp", "destination": [80]},
                    },
                    "id": 2,
                },
                {
                    "nextModule": "drop",
                    "id": 3,
                },
            ],
        }

        tree = parse(text)
        assert expected == Converter().convert_to_yanet(tree)

    def test_convert_project_id(self) -> None:
        text = r""":BEGIN
        add skipto :IN ip from any to any in

        :IN
        add allow tcp from 1a2b3c@2a02:6b8::/32 to any 80
        add deny ip from any to any
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1,
                },
            ],
            ":IN": [
                {
                    "filter": {
                        "source": ["2a02:6b8::1a:2b3c:0:0/ffff:ffff::ffff:ffff:0:0"],
                        "protocol": {"type": "tcp", "destination": [80]},
                    },
                    "id": 2,
                },
                {
                    "nextModule": "drop",
                    "id": 3,
                },
            ],
        }

        tree = parse(text)
        assert expected == Converter().convert_to_yanet(tree)

    def test_convert_project_id_with_mask(self) -> None:
        text = r""":BEGIN
        add skipto :IN ip from any to any in

        :IN
        add allow tcp from b0b1b2/16@2a02:6b8:c00::/40 to any 80
        add deny ip from any to any
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1,
                },
            ],
            ":IN": [
                {
                    "filter": {
                        "source": ["2a02:6b8:c00:0:b0::/ffff:ffff:ff00:0:ffff::"],
                        "protocol": {"type": "tcp", "destination": [80]},
                    },
                    "id": 2,
                },
                {
                    "nextModule": "drop",
                    "id": 3,
                },
            ],
        }

        tree = parse(text)
        assert expected == Converter().convert_to_yanet(tree)

    def test_convert_ignore_me(self) -> None:
        text = r""":BEGIN
        add skipto :IN ip from any to any in

        :IN
        add allow tcp from 2a02:6b8:c00::/40 to any 80
        add allow tcp from any to { me or me6 } established in
        add deny ip from any to any
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1,
                },
            ],
            ":IN": [
                {
                    "filter": {
                        "source": ["2a02:6b8:c00::/40"],
                        "protocol": {"type": "tcp", "destination": [80]},
                    },
                    "id": 2,
                },
                {
                    "nextModule": "drop",
                    "id": 4,
                },
            ],
        }

        tree = parse(text)
        assert expected == Converter().convert_to_yanet(tree)

    def test_filter_tokens(self) -> None:
        text = r""":BEGIN
        add skipto :IN ip from any to any in

        :IN
        add skipto :HBF_IN ip from any to any in
        add allow tcp from 2a02:6b8:c00::/40 to any 80
        add deny ip from any to any

        :HBF_IN
        add allow tcp from 2a02:6b8:c00::/40 to 2a02:6b8:c00::/40 443
        """

        tree = parse(text)
        tree = Converter().filter_tokens(tree, {"IN"})
        assert len(tree) == 6

    def test_ip_or_ip6_with_ports(self) -> None:
        text = r""":BEGIN
        add skipto :IN ip from any to any in

        :IN
        add allow ip6 from fe80::/64 to fe80::/64 dst-port 179
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1,
                },
            ],
            ":IN": [
                {
                    "filter": {
                        "source": ["fe80::/64"],
                        "destination": ["fe80::/64"],
                        "protocol": {"type": "tcp", "destination": [179]},
                    },
                    "id": 2,
                },
                {
                    "filter": {
                        "source": ["fe80::/64"],
                        "destination": ["fe80::/64"],
                        "protocol": {"type": "udp", "destination": [179]},
                    },
                    "id": 2,
                }
            ],
        }

        tree = parse(text)
        assert expected == Converter().convert_to_yanet(tree)

    def test_handle_count(self) -> None:
        # Currently ignore count rules. This may be changed.
        text = r""":BEGIN
        add skipto :IN ip from any to any in

        :IN
        add count ip from any to any
        add allow ip6 from fe80::/64 to fe80::/64 dst-port 179
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1,
                },
            ],
            ":IN": [
                {
                    "filter": {
                        "source": ["fe80::/64"],
                        "destination": ["fe80::/64"],
                        "protocol": {"type": "tcp", "destination": [179]},
                    },
                    "id": 3,
                },
                {
                    "filter": {
                        "source": ["fe80::/64"],
                        "destination": ["fe80::/64"],
                        "protocol": {"type": "udp", "destination": [179]},
                    },
                    "id": 3,
                }
            ],
        }

        tree = parse(text)
        assert expected == Converter().convert_to_yanet(tree)

    def test_convert_fill_empty_sections(self) -> None:
        text = r""":BEGIN
        add skipto :IN ip from any to any in
        add skipto :EMPTY ip from any to any in
        add skipto :MORE_EMPTY ip from any to any in

        :EMPTY
        :MORE_EMPTY
        :IN
        add allow tcp from 2a02:6b8:ff1c:2030::/ffff:ffff:ffff:fff0:: to any 80
        add deny ip from any to any
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1,
                },
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":EMPTY",
                    "id": 2,
                },
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":MORE_EMPTY",
                    "id": 3,
                },
            ],
            ":IN": [
                {
                    "filter": {
                        "source": ["2a02:6b8:ff1c:2030::/ffff:ffff:ffff:fff0::"],
                        "protocol": {"type": "tcp", "destination": [80]},
                    },
                    "id": 4,
                },
                {
                    "nextModule": "drop",
                    "id": 5,
                },
            ],
            ":EMPTY": [],
            ":MORE_EMPTY": [],
        }

        tree = parse(text)
        assert expected == Converter().convert_to_yanet(tree)

    def test_cmd_number_changes_id(self) -> None:
        text = r""":BEGIN
        add skipto :IN ip from any to any in

        :IN
        add 1500 count ip from any to any
        add allow tcp from 2a02:6b8:ff1c:2030::/ffff:ffff:ffff:fff0:: to any 80
        add deny ip from any to any
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {"direction": "in"},
                    "nextSection": ":IN",
                    "id": 1,
                },
            ],
            ":IN": [
                {
                    "filter": {
                        "source": ["2a02:6b8:ff1c:2030::/ffff:ffff:ffff:fff0::"],
                        "protocol": {"type": "tcp", "destination": [80]},
                    },
                    "id": 1502,
                },
                {
                    "nextModule": "drop",
                    "id": 1503,
                },
            ],
        }

        tree = parse(text)
        assert expected == Converter().convert_to_yanet(tree)

    def test_skipto_hack(self) -> None:
        text = r""":BEGIN
        add allow ip from any to 2.2.2.2

        :IN
        add allow tcp from 2a02:6b8:ff1c:2030::/ffff:ffff:ffff:fff0:: to any 80
        add deny ip from 1.1.1.1 to any

        :OTHER
        add deny ip from any to any
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {
                        "destination": ["2.2.2.2"],
                    },
                    "id": 1,
                },
                {
                    "nextSection": ":IN",
                    "id": 0xffffff,
                }
            ],
            ":IN": [
                {
                    "filter": {
                        "source": ["2a02:6b8:ff1c:2030::/ffff:ffff:ffff:fff0::"],
                        "protocol": {"type": "tcp", "destination": [80]},
                    },
                    "id": 2,
                },
                {
                    "filter": {
                        "source": ["1.1.1.1"],
                    },
                    "nextModule": "drop",
                    "id": 3,
                },
                {
                    "nextSection": ":OTHER",
                    "id": 0xffffff,
                },
            ],
            ":OTHER": [
                {
                    "nextModule": "drop",
                    "id": 4,
                },
            ],
        }

        tree = parse(text)
        assert expected == Converter().convert_to_yanet_ext(tree, ConversionSettings(add_skipto_hack=True)).sections

    def test_via_table(self) -> None:
        text = r""":BEGIN
        table _TABLE_NAME_ create type iface
        table _TABLE_NAME_ add vlan1 :HBF1
        table _TABLE_NAME_ add vlan2 :HBF2
        table _TABLE_NAME_ add kni0.802.bh :HBF2
        table _TABLE_NAME1_ add kni0.1600 :HBF3

        add skipto tablearg ip from any to any via table(_TABLE_NAME_)
        add skipto tablearg ip from any to any via table(_TABLE_NAME1_) out

        add allow ip from any to 2.2.2.2

        :HBF1
        add deny ip from 1.1.1.1 to any
        add deny ip from any to any

        :HBF2
        add deny ip from 1.1.1.2 to any

        :HBF3
        add deny ip from any to any
        """

        expected = {
            ":BEGIN": [
                {'id': 1000000001, 'nextSection': ':HBF1', 'via': ['vlan1']},
                {'id': 1000100001, 'nextSection': ':HBF2', 'via': ['kni0.802.bh', 'vlan2']},
                {'id': 1000000002, 'nextSection': ':HBF3', 'via': ['kni0.1600'], 'filter': {'direction': 'out'}},
                {'id': 3, 'filter': {'destination': ['2.2.2.2']}},
                {"id": 0xffffff, "nextSection": ":HBF1"}
            ],
            ':HBF1': [
                {'filter': {'source': ['1.1.1.1']}, 'id': 4, 'nextModule': 'drop'},
                {'id': 5, 'nextModule': 'drop'}
            ],
            ':HBF2': [
                {'filter': {'source': ['1.1.1.2']}, 'id': 6, 'nextModule': 'drop'},
                {'id': 16777215, 'nextSection': ':HBF3'}
            ],
            ':HBF3': [
                {'id': 7, 'nextModule': 'drop'}
            ]
        }

        tree = parse(text)
        result = Converter().convert_to_yanet_ext(tree, ConversionSettings(add_skipto_hack=True, add_out_direction=True)).sections
        result[":BEGIN"][1]['via'].sort()
        assert expected == result

    def test_allow_from_any(self):
        text = r"""
        :BEGIN
        ALLOW_FROM_ANY(tcp, { pull-mirror.yandex.net }, 873)        
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {
                        "destination": ["2a02:6b8:a::a"],
                        "protocol": {"type": "tcp", "destination": [873]},
                    },
                    "id": 1,
                },
            ],
        }

        tree = parse(text)
        assert expected == Converter(dnscache=DummyDNSCache({"pull-mirror.yandex.net": ["2a02:6b8:a::a"]})).convert_to_yanet(tree)

    def test_allow_from_any_many_ports(self):
        text = r"""
        :BEGIN
        ALLOW_FROM_ANY(tcp, { pull-mirror.yandex.net }, 873, 123)        
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {
                        "destination": ["2a02:6b8:a::a"],
                        "protocol": {"type": "tcp", "destination": [873, 123]},
                    },
                    "id": 1,
                },
            ],
        }

        tree = parse(text)
        assert expected == Converter(dnscache=DummyDNSCache({"pull-mirror.yandex.net": ["2a02:6b8:a::a"]})).convert_to_yanet(tree)

    def test_allow_from_yandexnets(self):
        text = r"""
        table _YANDEXNETS_ add 2a02:6b8::/32
        
        :BEGIN
        ALLOW_FROM_YANDEXNETS(tcp, { pull-mirror.yandex.net }, 873)        
        """

        expected = {
            ":BEGIN": [
                {
                    "filter": {
                        "source": ["2a02:6b8::/32"],
                        "destination": ["2a02:6b8:a::a"],
                        "protocol": {"type": "tcp", "destination": [873]},
                    },
                    "id": 1,
                },
            ],
        }

        tree = parse(text)
        assert expected == Converter(dnscache=DummyDNSCache({"pull-mirror.yandex.net": ["2a02:6b8:a::a"]})).convert_to_yanet(tree)
