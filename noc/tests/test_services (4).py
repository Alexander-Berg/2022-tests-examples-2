import unittest.mock as um

from yanetagent.agent import parse_services_conf, parse_services_yaml


class TestParser:
    def test_services_conf(self) -> None:
        text = r"""[
  {
    "vip": "141.8.140.158",
    "vport": "60889",
    "proto": "tcp",
    "scheduler": "rr",
    "reals": [
      {
        "ip": "2a02:6b8:c01:8a:0:675:558e:3eb3",
        "port": "60889",
        "weight": 1
      },
      {
        "ip": "2a02:6b8:c01:89f:0:675:27cc:a0ff",
        "port": "60889",
        "weight": 1
      }
    ],
    "file": "man1-lb23a.yndx.net.natasha.inc.conf",
    "path": "/etc/keepalived"
  },
  {
    "vip": "213.180.205.37",
    "vport": "60889",
    "proto": "tcp",
    "scheduler": "rr",
    "reals": [
      {
        "ip": "2a02:6b8:c01:8a:0:675:558e:3eb3",
        "port": "60889",
        "weight": 1
      },
      {
        "ip": "2a02:6b8:c01:89f:0:675:27cc:a0ff",
        "port": "60889",
        "weight": 1
      }
    ],
    "file": "man1-lb23a.yndx.net.natasha.inc.conf",
    "path": "/etc/keepalived"
  }

]
    """
        with um.patch('builtins.open', um.mock_open(read_data=text)):
            services = parse_services_conf('Some path')
        expected = [
            {
                'vip': '141.8.140.158',
                'vport': '60889',
                'proto': 'tcp',
                'scheduler': 'rr',
                'reals': [
                    {'ip': '2a02:6b8:c01:89f:0:675:27cc:a0ff', 'port': '60889', 'weight': 1},
                    {'ip': '2a02:6b8:c01:8a:0:675:558e:3eb3', 'port': '60889', 'weight': 1}],
                'file': 'man1-lb23a.yndx.net.natasha.inc.conf', 'path': '/etc/keepalived'
            },
            {
                'vip': '213.180.205.37',
                'vport': '60889',
                'proto': 'tcp',
                'scheduler': 'rr',
                'reals': [
                    {'ip': '2a02:6b8:c01:89f:0:675:27cc:a0ff', 'port': '60889', 'weight': 1},
                    {'ip': '2a02:6b8:c01:8a:0:675:558e:3eb3', 'port': '60889', 'weight': 1}],
                'file': 'man1-lb23a.yndx.net.natasha.inc.conf', 'path': '/etc/keepalived'
            }]

        assert services == expected

    def test_services_yaml(self) -> None:
        text = """---
any.yandex.ru:
  ips: [213.180.204.242, 2a02:6b8::242]
---
any-test.yandex.net:
  ips: [93.158.157.126, 2a02:6b8:0:3400::3:126]
---
any-int.yandex.net:
  ips: []
---
redirect.yandex.kz:
  ips: [141.8.154.20]
---
ya.ru:
  ips: [87.250.250.242, 2a02:6b8::2:242]
---
ysa-test.passport.yandex.net:
  ips: []
  no_mss_fix: true
---
ysa.passport.yandex.net:
  ips: []
  no_mss_fix: true
---
zhpx-internal.kaizen.yandex.net:
  ips: [2a02:6b8:0:3400::928]
  chain_name: zhpx-internal.kaizen
---
ysa-test-static.passport.yandex.net:
  ips: [2a02:6b8:0:3400::929]
  chain_name: ysa-test-static.passport
---
events.portal.yandex.net:
  ips: [2a02:6b8:0:3400::930]
---
zpub-internal.kaizen.yandex.net:
  ips: [2a02:6b8:0:3400::932]
    """
        with um.patch('builtins.open', um.mock_open(read_data=text)):
            services = parse_services_yaml('Some path')
        expected = {
            'any-int.yandex.net': {'ips': []},
            'any-test.yandex.net': {'ips': ['93.158.157.126', '2a02:6b8:0:3400::3:126']},
            'any.yandex.ru': {'ips': ['213.180.204.242', '2a02:6b8::242']},
            'events.portal.yandex.net': {'ips': ['2a02:6b8:0:3400::930']},
            'redirect.yandex.kz': {'ips': ['141.8.154.20']},
            'ya.ru': {'ips': ['87.250.250.242', '2a02:6b8::2:242']},
            'ysa-test-static.passport.yandex.net': {'chain_name': 'ysa-test-static.passport', 'ips': ['2a02:6b8:0:3400::929']},
            'ysa-test.passport.yandex.net': {'ips': [], 'no_mss_fix': True},
            'ysa.passport.yandex.net': {'ips': [], 'no_mss_fix': True},
            'zhpx-internal.kaizen.yandex.net': {'chain_name': 'zhpx-internal.kaizen', 'ips': ['2a02:6b8:0:3400::928']},
            'zpub-internal.kaizen.yandex.net': {'ips': ['2a02:6b8:0:3400::932']}}
        assert services == expected
