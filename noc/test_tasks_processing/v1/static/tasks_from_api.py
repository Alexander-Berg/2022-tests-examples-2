TASK_L4 = {
    "id": 1,
    "task": "test",
    "data": {
        "id": 123456,
        "service": {"fqdn": "l3.tt.yandex-team.ru", "id": 137, "name": "dostavkatraffika"},
        "lb": {"name": "iva-b-lb1a", "id": 569, "fqdn": "iva-b-lb1a.yndx.net", "ip": "2a02:6b8:0:e05::13:b0aa"},
        "vss": [
            {
                "id": 1069929,
                "network_settings": {
                    "ip": "2a02:6b8:0:3400::50",
                    "port": 80,
                    "protocol": "TCP",
                    "network_settings_hash": "fedf943ccce1c167475dcd820360ba49772affc22aba23720521a7605aff728e",
                },
                "lb_ip": "2a02:6b8:0:e04::13:b0aa",
                "config": {
                    "announce": True,
                    "check_retry": 1,
                    "check_retry_timeout": 1,
                    "check_timeout": 1,
                    "check_type": "SSL_GET",
                    "check_url": "/ping",
                    "connect_ip": "",
                    "connect_port": 443,
                    "dc_filter": False,
                    "digest": "",
                    "dynamicweight": False,
                    "dynamicweight_allow_zero": False,
                    "dynamicweight_in_header": False,
                    "dynamicweight_ratio": 30,
                    "host": "l3.tt.yandex-team.ru",
                    "http_protocol": None,
                    "hysteresis": 0,
                    "inhibit_on_failure": False,
                    "method": "TUN",
                    "mh_port": False,
                    "mh_fallback": False,
                    "persistence_timeout": 0,
                    "quorum": 1,
                    "scheduler": "wrr",
                    "status_code": 204,
                    "weight": 100,
                    "min_vs_up": 2,
                    "ops": False,
                    "delay_loop": 2,
                },
                "rss": [
                    {
                        "state_id": 7968972,
                        "fqdn": "mnt-myt.yandex.net",
                        "ip": "2a02:6b8:0:1482::115",
                        "fwmark": 1767,
                        "server_id": 1554,
                        "settings": {"weight": 1},
                    },
                    {
                        "state_id": 7968973,
                        "fqdn": "mnt-sas.yandex.net",
                        "ip": "2a02:6b8:b010:31::233",
                        "fwmark": 1768,
                        "server_id": 1555,
                        "settings": {"weight": 1},
                    },
                ],
            },
            {
                "id": 1069928,
                "network_settings": {
                    "ip": "2a02:6b8:0:3400::50",
                    "port": 443,
                    "protocol": "TCP",
                    "network_settings_hash": "684d30c834c068b6ed2f9e1f6412601bfb8dc92e56b8b36a9f1329948dce3b05",
                },
                "lb_ip": "2a02:6b8:0:e04::13:b0aa",
                "config": {
                    "announce": True,
                    "check_retry": 1,
                    "check_retry_timeout": 1,
                    "check_timeout": 1,
                    "check_type": "SSL_GET",
                    "check_url": "/ping",
                    "connect_ip": "",
                    "connect_port": 443,
                    "dc_filter": False,
                    "digest": "",
                    "dynamicweight": False,
                    "dynamicweight_allow_zero": False,
                    "dynamicweight_in_header": False,
                    "dynamicweight_ratio": 30,
                    "host": "",
                    "http_protocol": None,
                    "hysteresis": 0,
                    "inhibit_on_failure": False,
                    "method": "TUN",
                    "mh_port": False,
                    "mh_fallback": False,
                    "persistence_timeout": 0,
                    "quorum": 1,
                    "scheduler": "wrr",
                    "status_code": 204,
                    "weight": 100,
                    "min_vs_up": 2,
                    "ops": False,
                    "delay_loop": 10,
                },
                "rss": [
                    {
                        "state_id": 7968972,
                        "fqdn": "mnt-myt.yandex.net",
                        "ip": "2a02:6b8:0:1482::115",
                        "fwmark": 1650,
                        "server_id": 1554,
                        "settings": {"weight": 1},
                    },
                    {
                        "state_id": 7968973,
                        "fqdn": "mnt-sas.yandex.net",
                        "ip": "2a02:6b8:b010:31::233",
                        "fwmark": 1651,
                        "server_id": 1555,
                        "settings": {"weight": 1},
                    },
                ],
            },
        ],
    },
}


TASK_DYNAMIC_WEIGHT = {
    "id": 100,
    "task": "test",
    "data": {
        "id": 123456,
        "service": {"fqdn": "passport-test.yandex.ru", "id": 137, "name": "passp"},
        "lb": {"name": "iva-b-lb1a", "id": 569, "fqdn": "iva-b-lb1a.yndx.net", "ip": "2a02:6b8:0:e05::13:b0aa"},
        "vss": [
            {
                "id": 2520354,
                "network_settings": {
                    "ip": "2a02:6b8:0:3400::3:16",
                    "port": 443,
                    "protocol": "TCP",
                    "network_settings_hash": "fedf943ccce1c167475dcd820360ba49772affc22aba23720521a7605aff728e",
                },
                "lb_ip": "2a02:6b8:0:e04::13:b0aa",
                "config": {
                    "announce": True,
                    "check_retry": 1,
                    "check_retry_timeout": 1,
                    "check_timeout": 1,
                    "check_type": "SSL_GET",
                    "check_url": "/ping.html",
                    "connect_ip": "",
                    "connect_port": 443,
                    "dc_filter": False,
                    "digest": "69e24a7fd90ef6988e07480b522d6f80",
                    "dynamicweight": True,
                    "dynamicweight_allow_zero": False,
                    "dynamicweight_in_header": True,
                    "dynamicweight_ratio": 30,
                    "host": "passport-test.yandex.ru",
                    "http_protocol": None,
                    "hysteresis": 0,
                    "inhibit_on_failure": False,
                    "method": "TUN",
                    "mh_port": False,
                    "mh_fallback": False,
                    "persistence_timeout": 0,
                    "quorum": 1,
                    "scheduler": "wrr",
                    "status_code": 200,
                    "weight": 100,
                    "min_vs_up": 2,
                    "ops": False,
                    "delay_loop": 10,
                },
                "rss": [
                    {
                        "state_id": 86110877,
                        "fqdn": "passport-test-f1.passport.yandex.net",
                        "ip": "2a02:6b8:c01:710:8000:611:0:11",
                        "fwmark": 1564,
                        "server_id": 3082264,
                        "settings": {"weight": 0},
                    },
                    {
                        "state_id": 83311083,
                        "fqdn": "passport-test-m1.passport.yandex.net",
                        "ip": "2a02:6b8:c03:763:8000:611:0:17",
                        "fwmark": 2605,
                        "server_id": 3082265,
                        "settings": {"weight": 0},
                    },
                    {
                        "state_id": 86110853,
                        "fqdn": "passport-test-s1.passport.yandex.net",
                        "ip": "2a02:6b8:c02:500:8000:611:0:d",
                        "fwmark": 2415,
                        "server_id": 3082266,
                        "settings": {"weight": 0},
                    },
                ],
            }
        ],
    },
}


TASK_FWMARK = {
    "id": 10,
    "task": "test",
    "data": {
        "id": 123456,
        "service": {"fqdn": "mirror.yandex.ru", "id": 10000, "name": "mirror"},
        "lb": {"name": "iva-b-lb1a", "id": 569, "fqdn": "iva-b-lb1a.yndx.net", "ip": "2a02:6b8:0:e04::13:b0aa"},
        "vss": [
            {
                "id": 1069929,
                "fwmark_settings": {
                    "services": [
                        {
                            "id": 123456,
                            "ip": "2a02:6b8::183",
                            "weight": 100,
                        }
                    ],
                    "fwmark": 52407,
                    "protocol": "TCP",
                },
                "lb_ip": "2a02:6b8:0:e04::13:b0aa",
                "config": {
                    "announce": True,
                    "check_retry": 1,
                    "check_retry_timeout": 1,
                    "check_timeout": 1,
                    "check_type": "HTTP_GET",
                    "check_url": "/.ok.txt",
                    "connect_ip": "2a02:6b8::183",
                    "connect_port": 80,
                    "dc_filter": False,
                    "digest": "",
                    "dynamicweight": False,
                    "dynamicweight_allow_zero": False,
                    "dynamicweight_in_header": False,
                    "dynamicweight_ratio": 30,
                    "host": "l3.tt.yandex-team.ru",
                    "http_protocol": None,
                    "hysteresis": 0,
                    "inhibit_on_failure": False,
                    "method": "TUN",
                    "mh_port": False,
                    "mh_fallback": False,
                    "persistence_timeout": 300,
                    "quorum": 1,
                    "scheduler": "wrr",
                    "status_code": 200,
                    "weight": 100,
                    "min_vs_up": 1,
                    "ops": False,
                    "delay_loop": 10,
                },
                "rss": [
                    {
                        "state_id": 7968972,
                        "fqdn": "mirror01sas.mds.yandex.net",
                        "ip": "2a02:6b8:c02:7f4:0:1429:f3fd:d8d0",
                        "fwmark": 2965,
                        "server_id": 11554,
                        "settings": {"weight": 1},
                    }
                ],
            },
            {
                "id": 1069928,
                "fwmark_settings": {
                    "services": [
                        {
                            "id": 123456,
                            "ip": "213.180.204.183",
                            "weight": 100,
                        }
                    ],
                    "fwmark": 52407,
                    "protocol": "TCP",
                },
                "lb_ip": "5.255.254.27",
                "config": {
                    "announce": True,
                    "check_retry": 1,
                    "check_retry_timeout": 1,
                    "check_timeout": 1,
                    "check_type": "HTTP_GET",
                    "check_url": "/.ok.txt",
                    "connect_ip": "213.180.204.183",
                    "connect_port": 80,
                    "dc_filter": False,
                    "digest": "",
                    "dynamicweight": False,
                    "dynamicweight_allow_zero": False,
                    "dynamicweight_in_header": False,
                    "dynamicweight_ratio": 30,
                    "host": "",
                    "http_protocol": None,
                    "hysteresis": 0,
                    "inhibit_on_failure": False,
                    "method": "TUN",
                    "mh_port": False,
                    "mh_fallback": False,
                    "persistence_timeout": 300,
                    "quorum": 1,
                    "scheduler": "wrr",
                    "status_code": 200,
                    "weight": 100,
                    "min_vs_up": 1,
                    "ops": False,
                    "delay_loop": 10,
                },
                "rss": [
                    {
                        "state_id": 8968972,
                        "fqdn": "mirror01sas.mds.yandex.net",
                        "ip": "2a02:6b8:c02:7f4:0:1429:f3fd:d8d0",
                        "fwmark": 2965,
                        "server_id": 21554,
                        "settings": {"weight": 1},
                    }
                ],
            },
        ],
    },
}

TASK_MAGLEV_AND_HTTP_PROTOCOL = {
    "id": 1,
    "task": "test",
    "data": {
        "id": 123456,
        "service": {"fqdn": "l3.tt.yandex-team.ru", "id": 137, "name": "dostavkatraffika"},
        "lb": {"name": "iva-b-lb1a", "id": 569, "fqdn": "iva-b-lb1a.yndx.net", "ip": "2a02:6b8:0:e05::13:b0aa"},
        "vss": [
            {
                "id": 1069929,
                "network_settings": {
                    "ip": "2a02:6b8:0:3400::50",
                    "port": 80,
                    "protocol": "TCP",
                    "network_settings_hash": "fedf943ccce1c167475dcd820360ba49772affc22aba23720521a7605aff728e",
                },
                "lb_ip": "2a02:6b8:0:e04::13:b0aa",
                "config": {
                    "announce": True,
                    "check_retry": 1,
                    "check_retry_timeout": 1,
                    "check_timeout": 1,
                    "check_type": "SSL_GET",
                    "check_url": "/ping",
                    "connect_ip": "",
                    "connect_port": 443,
                    "dc_filter": False,
                    "digest": "",
                    "dynamicweight": False,
                    "dynamicweight_allow_zero": False,
                    "dynamicweight_in_header": False,
                    "dynamicweight_ratio": 30,
                    "host": "l3.tt.yandex-team.ru",
                    "http_protocol": None,
                    "hysteresis": 0,
                    "inhibit_on_failure": False,
                    "method": "TUN",
                    "persistence_timeout": 0,
                    "quorum": 1,
                    "scheduler": "mh",
                    "mh_port": True,
                    "mh_fallback": False,
                    "status_code": 204,
                    "weight": 100,
                    "min_vs_up": 2,
                    "ops": False,
                    "delay_loop": 10,
                },
                "rss": [
                    {
                        "state_id": 7968972,
                        "fqdn": "mnt-myt.yandex.net",
                        "ip": "2a02:6b8:0:1482::115",
                        "fwmark": 1767,
                        "server_id": 1554,
                        "settings": {"weight": 1},
                    },
                    {
                        "state_id": 7968973,
                        "fqdn": "mnt-sas.yandex.net",
                        "ip": "2a02:6b8:b010:31::233",
                        "fwmark": 1768,
                        "server_id": 1555,
                        "settings": {"weight": 1},
                    },
                ],
            },
            {
                "id": 1069928,
                "network_settings": {
                    "ip": "2a02:6b8:0:3400::50",
                    "port": 443,
                    "protocol": "TCP",
                    "network_settings_hash": "684d30c834c068b6ed2f9e1f6412601bfb8dc92e56b8b36a9f1329948dce3b05",
                },
                "lb_ip": "2a02:6b8:0:e04::13:b0aa",
                "config": {
                    "announce": True,
                    "check_retry": 1,
                    "check_retry_timeout": 1,
                    "check_timeout": 1,
                    "check_type": "SSL_GET",
                    "check_url": "/ping",
                    "connect_ip": "",
                    "connect_port": 443,
                    "dc_filter": False,
                    "digest": "",
                    "dynamicweight": False,
                    "dynamicweight_allow_zero": False,
                    "dynamicweight_in_header": False,
                    "dynamicweight_ratio": 30,
                    "host": "",
                    "http_protocol": "1.0C",
                    "hysteresis": 0,
                    "inhibit_on_failure": False,
                    "method": "TUN",
                    "mh_port": False,
                    "mh_fallback": False,
                    "persistence_timeout": 0,
                    "quorum": 1,
                    "scheduler": "wrr",
                    "status_code": 204,
                    "weight": 100,
                    "min_vs_up": 2,
                    "ops": False,
                    "delay_loop": 10,
                },
                "rss": [
                    {
                        "state_id": 7968972,
                        "fqdn": "mnt-myt.yandex.net",
                        "ip": "2a02:6b8:0:1482::115",
                        "fwmark": 1650,
                        "server_id": 1554,
                        "settings": {"weight": 1},
                    },
                    {
                        "state_id": 7968973,
                        "fqdn": "mnt-sas.yandex.net",
                        "ip": "2a02:6b8:b010:31::233",
                        "fwmark": 1651,
                        "server_id": 1555,
                        "settings": {"weight": 1},
                    },
                ],
            },
        ],
    },
}
