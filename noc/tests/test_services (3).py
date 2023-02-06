from django.test import TestCase
from unittest.mock import patch

from ..services import RackTablesApi


class RackTablesApiTestCase(TestCase):
    @patch("l3racktables.services.RackTablesApi._read_lines")
    def test_get_rt_services_info(self, rt_api_mock):
        rt_api_mock.side_effect = [
            [
                "52.59.139.0/24	id: 7699, name: AWS SLB",
                "77.88.8.0/24	id: 1416, name: public VIPs безопасных DNS",
                "	77.88.8.1 - dns.yandex.ru",
                "	77.88.8.2 - safe.dns.yandex.ru",
                "	77.88.8.3 - family.dns.yandex.ru",
                "	77.88.8.7 - one-more-family.dns.yandex.ru",
                "	77.88.8.7 - family.dns.yandex.ru",
                "77.88.21.0/24	id: 10, name: Публичные виртуальные сервисы",
                "	77.88.21.92 - ",
                "	77.88.21.255 - ",
                "	77.88.21.1 - ns4.yandex.ru",
                "	77.88.21.2 - alet-external-afisha-mapi.stable.qloud-b.yandex.net",
            ],
            [
                "2620:10f:d001::/48	id: 29604, name: IPv6 SLB VIP Public (ARIN)",
                "	2620:10f:d001::231 - cdn.yandex.net",
                "2a02:6b8::/62	id: 18469, name:",
                "	2a02:6b8::25 - mail.yandex.ru",
                "	2a02:6b8::64 - ",
                "	2a02:6b8::88 - ext-support.taxi.yandex.net",
            ],
        ]
        rt_api = RackTablesApi("https://fake-url.test", "https://rw.fake-url.test")
        services_info = list(rt_api.get_rt_services_info())
        self.assertEqual(len(services_info), 13)
        self.assertEqual(len([svc for svc in services_info if svc.fqdn == "family.dns.yandex.ru"]), 2)
        self.assertTrue([svc for svc in services_info if svc.ip == "77.88.21.1"])
        self.assertTrue([svc for svc in services_info if svc.ip == "2a02:6b8::25"])
        self.assertEqual([svc for svc in services_info if svc.ip == "2a02:6b8::64"][0].fqdn, "")
