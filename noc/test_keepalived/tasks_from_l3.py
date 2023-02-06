CONFIG_SUCCESS_INTEG_TEST = {
    "id": 1245,
    "service": {"id": 94, "fqdn": "l3manager-agent-successful-integration-test.yandex.net", "name": "slb"},
    "vss": [
        {
            "id": 1528,
            "network_settings": {
                "ip": "2a02:6b8:0:3400:0:43c:0:3",
                "port": 80,
                "protocol": "TCP",
                "network_settings_hash": "9ad389ed0dece96ad82f725f3ecf8cc4fb3f512e33cf97e7109e4d914a78d588",
            },
            "config": {
                "method": "TUN",
                "announce": True,
                "quorum": 1,
                "hysteresis": 0,
                "scheduler": "wrr",
                "mh_fallback": False,
                "mh_port": False,
                "check_type": "TCP_CHECK",
                "http_protocol": None,
                "host": None,
                "check_url": "/ping",
                "connect_ip": "2a02:6b8:0:3400:0:43c:0:3",
                "connect_port": 80,
                "digest": None,
                "status_code": 200,
                "check_timeout": 1,
                "check_retry": 1,
                "check_retry_timeout": 1,
                "delay_loop": 10,
                "dc_filter": True,
                "inhibit_on_failure": False,
                "persistence_timeout": None,
                "dynamicweight": False,
                "dynamicweight_allow_zero": False,
                "dynamicweight_in_header": True,
                "dynamicweight_ratio": 30,
                "ops": False,
                "weight": 100,
                "min_vs_up": 1,
            },
            "rss": [
                {
                    "server_id": 3,
                    "fqdn": "mnt-myt.yandex.net",
                    "ip": "2a02:6b8:0:1482::115",
                    "fwmark": 1001,
                    "settings": {"weight": 1},
                },
                {
                    "server_id": 115,
                    "fqdn": "mnt-myt-focal.tt.yandex.net",
                    "ip": "2a02:6b8:0:1482::333",
                    "fwmark": 1003,
                    "settings": {"weight": 1},
                },
            ],
        }
    ],
    "lb": {"id": 117, "fqdn": "sas-1testenv-test-lb0aa.yndx.net", "name": "sas-1testenv-test-lb0aa"},
}


CONFIG_TEMPLATE_V2 = {
    "id": 1,
    "revision": 0,
    "locked": 1635430178,
    "service": "l3.tt.yandex-team.ru",
    "target": "ACTIVE",
    "state": "UNKNOWN",
    "vs_group": {
        "IP": {
            "min_vs_up": 1,
            "target_state": "DEPLOYED",
            "vss": [
                {
                    "config": {
                        "announce": {"enabled": True, "hysteresis": 0, "quorum": 1},
                        "check": {
                            "connect_params": {"ip": "", "port": 443, "timeout": 1},
                            "delay_loop": 10,
                            "options": {
                                "check_url": "/ping",
                                "digest": "",
                                "host": "l3.tt.yandex-team.ru",
                                "http_protocol": None,
                                "status_code": 204,
                            },
                            "retry_params": {"count": 1, "delay": 1},
                            "type": "SSL_GET",
                        },
                        "dynamicweight": {
                            "enabled": False,
                            "options": {"allow_zero": False, "in_header": False, "ratio": 30},
                        },
                        "inhibit_on_failure": False,
                        "method": "TUN",
                        "persistence_timeout": 0,
                        "scheduler": {
                            "options": {"mh_fallback": False, "mh_port": False, "ops": False},
                            "type": "wrr",
                        },
                    },
                    "id": 1069928,
                    "port": 80,
                    "protocol": "TCP",
                    "rss": {
                        "2a02:6b8:0:1482::115": {"config": {"weight": 1}, "fwmark": 1650, "id": 1554},
                        "2a02:6b8:b010:31::233": {"config": {"weight": 1}, "fwmark": 1651, "id": 1555},
                    },
                }
            ],
            "weight": 300,
        }
    },
}
