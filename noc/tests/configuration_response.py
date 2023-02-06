import collections
import typing

from l3mgr import models as mgr_models


def get_expected(allocation: mgr_models.Allocation):
    vss: typing.Dict[str, typing.List[int]] = collections.defaultdict(list)
    rss: typing.Dict[str, typing.Dict[str, int]] = collections.defaultdict(dict)
    for vs in allocation.presentation.configuration.vss:
        vss[vs.ip].append(vs.id)
        for rs in vs.servers:
            rss[vs.ip][rs.ip] = rs.id
    return {
        "revision": allocation.id,
        "id": allocation.presentation.configuration_id,
        "target": "ACTIVE",
        "service": "l3.tt.yandex-team.ru",
        "vs_group": {
            "5.255.240.50": {
                "target_state": "DEPLOYED",
                "weight": 100,
                "min_vs_up": 2,
                "vss": [
                    {
                        "id": vss["5.255.240.50"][0],
                        "port": 80,
                        "protocol": "TCP",
                        "config": {
                            "method": "TUN",
                            "inhibit_on_failure": False,
                            "persistence_timeout": None,
                            "announce": {"enabled": True, "quorum": 1, "hysteresis": 0},
                            "scheduler": {
                                "type": "wrr",
                                "options": {"ops": False, "mh_fallback": False, "mh_port": False},
                            },
                            "check": {
                                "type": "HTTP_GET",
                                "connect_params": {"ip": "5.255.240.50", "port": 80, "timeout": 1},
                                "retry_params": {"count": 1, "delay": 1},
                                "delay_loop": 10,
                                "options": {
                                    "http_protocol": None,
                                    "host": "l3.tt.yandex-team.ru",
                                    "check_url": "/ping",
                                    "digest": None,
                                    "status_code": 204,
                                },
                            },
                            "dynamicweight": {
                                "enabled": False,
                                "options": {"ratio": None, "allow_zero": False, "in_header": False},
                            },
                        },
                        "rss": {
                            "77.88.1.115": {
                                "id": rss["5.255.240.50"]["77.88.1.115"],
                                "fwmark": 1001,
                                "config": {"weight": 1},
                            },
                            "93.158.158.87": {
                                "id": rss["5.255.240.50"]["93.158.158.87"],
                                "fwmark": 1002,
                                "config": {"weight": 1},
                            },
                        },
                    },
                    {
                        "id": vss["5.255.240.50"][1],
                        "port": 443,
                        "protocol": "TCP",
                        "config": {
                            "method": "TUN",
                            "inhibit_on_failure": False,
                            "persistence_timeout": None,
                            "announce": {"enabled": True, "quorum": 1, "hysteresis": 0},
                            "scheduler": {
                                "type": "wrr",
                                "options": {"ops": False, "mh_fallback": False, "mh_port": False},
                            },
                            "check": {
                                "type": "HTTP_GET",
                                "connect_params": {"ip": "5.255.240.50", "port": 443, "timeout": 1},
                                "retry_params": {"count": 1, "delay": 1},
                                "delay_loop": 10,
                                "options": {
                                    "http_protocol": None,
                                    "host": None,
                                    "check_url": "/ping",
                                    "digest": None,
                                    "status_code": 204,
                                },
                            },
                            "dynamicweight": {
                                "enabled": False,
                                "options": {"ratio": None, "allow_zero": False, "in_header": False},
                            },
                        },
                        "rss": {
                            "77.88.1.115": {
                                "id": rss["5.255.240.50"]["77.88.1.115"],
                                "fwmark": 1001,
                                "config": {"weight": 1},
                            },
                            "93.158.158.87": {
                                "id": rss["5.255.240.50"]["93.158.158.87"],
                                "fwmark": 1002,
                                "config": {"weight": 1},
                            },
                        },
                    },
                ],
            },
            "2a02:6b8:0:3400::50": {
                "target_state": "DEPLOYED",
                "weight": 100,
                "min_vs_up": 2,
                "vss": [
                    {
                        "id": vss["2a02:6b8:0:3400::50"][0],
                        "port": 80,
                        "protocol": "TCP",
                        "config": {
                            "method": "TUN",
                            "inhibit_on_failure": False,
                            "persistence_timeout": None,
                            "announce": {"enabled": True, "quorum": 1, "hysteresis": 0},
                            "scheduler": {
                                "type": "wrr",
                                "options": {"ops": False, "mh_fallback": False, "mh_port": False},
                            },
                            "check": {
                                "type": "HTTP_GET",
                                "connect_params": {"ip": "2a02:6b8:0:3400::50", "port": 80, "timeout": 1},
                                "retry_params": {"count": 1, "delay": 1},
                                "delay_loop": 10,
                                "options": {
                                    "http_protocol": None,
                                    "host": "l3.tt.yandex-team.ru",
                                    "check_url": "/ping",
                                    "digest": None,
                                    "status_code": 204,
                                },
                            },
                            "dynamicweight": {
                                "enabled": False,
                                "options": {"ratio": None, "allow_zero": False, "in_header": False},
                            },
                        },
                        "rss": {
                            "2a02:6b8:0:1482::115": {
                                "id": rss["2a02:6b8:0:3400::50"]["2a02:6b8:0:1482::115"],
                                "fwmark": 1003,
                                "config": {"weight": 1},
                            },
                            "2a02:6b8:b010:31::233": {
                                "id": rss["2a02:6b8:0:3400::50"]["2a02:6b8:b010:31::233"],
                                "fwmark": 1004,
                                "config": {"weight": 1},
                            },
                        },
                    },
                    {
                        "id": vss["2a02:6b8:0:3400::50"][1],
                        "port": 443,
                        "protocol": "TCP",
                        "config": {
                            "method": "TUN",
                            "inhibit_on_failure": False,
                            "persistence_timeout": None,
                            "announce": {"enabled": True, "quorum": 1, "hysteresis": 0},
                            "scheduler": {
                                "type": "wrr",
                                "options": {"ops": False, "mh_fallback": False, "mh_port": False},
                            },
                            "check": {
                                "type": "HTTP_GET",
                                "connect_params": {"ip": "2a02:6b8:0:3400::50", "port": 443, "timeout": 1},
                                "retry_params": {"count": 1, "delay": 1},
                                "delay_loop": 10,
                                "options": {
                                    "http_protocol": None,
                                    "host": None,
                                    "check_url": "/ping",
                                    "digest": None,
                                    "status_code": 204,
                                },
                            },
                            "dynamicweight": {
                                "enabled": False,
                                "options": {"ratio": None, "allow_zero": False, "in_header": False},
                            },
                        },
                        "rss": {
                            "2a02:6b8:0:1482::115": {
                                "id": rss["2a02:6b8:0:3400::50"]["2a02:6b8:0:1482::115"],
                                "fwmark": 1003,
                                "config": {"weight": 1},
                            },
                            "2a02:6b8:b010:31::233": {
                                "id": rss["2a02:6b8:0:3400::50"]["2a02:6b8:b010:31::233"],
                                "fwmark": 1004,
                                "config": {"weight": 1},
                            },
                        },
                    },
                ],
            },
        },
        "state": "UNKNOWN",
        "locked": None,
    }
