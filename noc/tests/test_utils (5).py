import itertools
import logging
from unittest.mock import patch, Mock

from django.test import TestCase
from parameterized import parameterized

from ..utils import update_rt_networks, sync_rt_services
from ..services import RackTablesApi, RackTablesNetworkInfo, RackTablesServiceInfo
from ..exceptions import RackTablesServicesUpdateException
from ..models import RackTablesService
from l3mgr.models import VirtualServer, Service

logger = logging.getLogger(__file__)


class TasksTestCase(TestCase):
    databases = "__all__"

    EXIST_RT_NETWORKS = {
        "5.45.197.0/24": ("Ивантеевка", ["IVA"]),
        "37.140.168.192/28": ("Строганов", ["ASH"]),
        "37.140.170.0/23": ("Строганов", ["ASH", "SAS"]),
        "5.45.241.0/24": ("Бенуа", ["SAS", "ASH"]),
        "192.0.2.4/32": ("Мытищи", ["MYT"]),
        "2a02:6b8:f000:ff00::/64": ("Сасово-1", ["SAS"]),
    }

    EXIST_MANUAL_NETWORKS = {
        "5.45.252.128/26": ("Бенуа", ["SAS", "ASH"]),
        "77.88.12.0/28": ("Бенуа", ["SAS", "ASH"]),
        "2a02:6b8:0:3400:0:71d::/96": ("rclb", []),
    }

    @parameterized.expand(
        [
            # Check update operation
            (
                EXIST_RT_NETWORKS,
                EXIST_MANUAL_NETWORKS,
                {
                    "37.140.170.0/23": ("Несуществующая локация пропускается", ["SAS", "ASH"]),
                    "5.45.241.0/24": ("Владимир", ["VLA"]),
                    "5.45.197.0/24": ("Мянтсяля-1.2", ["NOT EXIST LOCATION"]),
                },
                {
                    # location and original cannot changed,
                    # because original doesn't exist in mappings
                    "37.140.170.0/23": EXIST_RT_NETWORKS.get("37.140.170.0/23"),
                    # update location to single array value
                    "5.45.241.0/24": ("Владимир", ["VLA"]),
                    # define location to exist
                    "5.45.197.0/24": ("Мянтсяля-1.2", ["MAN"]),
                },
                EXIST_MANUAL_NETWORKS,
            ),
            # Check create operation
            (
                EXIST_RT_NETWORKS,
                EXIST_MANUAL_NETWORKS,
                {"2a02:6b8:b020:5000::/52": ("Мянтсяля-1", [])},
                {"2a02:6b8:b020:5000::/52": ("Мянтсяля-1", ["MAN"])},
                EXIST_MANUAL_NETWORKS,
            ),
            # Check assertion error: MANUAL network wouldn't be updated, but RT is empty
            (
                EXIST_RT_NETWORKS,
                EXIST_MANUAL_NETWORKS,
                {"2a02:6b8:0:3400:0:71d::/96": ("Мянтсяля-1", [])},
                {},
                EXIST_MANUAL_NETWORKS,
            ),
        ]
    )
    def test_rt_networks_update(
        self,
        prepared_rt_networks,
        prepared_manual_networks,
        mocked_rt_networks_response,
        expected_rt_networks,
        expected_manual_networks,
    ):
        from l3mgr.models import LocationNetwork

        # prepare database data
        LocationNetwork.objects.bulk_create(
            [
                LocationNetwork(ip=ip, original=tag, location=location, source="RACKTABLES")
                for ip, (tag, location) in prepared_rt_networks.items()
            ]
        )
        LocationNetwork.objects.bulk_create(
            [
                LocationNetwork(ip=ip, original=tag, location=location, source="MANUAL")
                for ip, (tag, location) in prepared_manual_networks.items()
            ]
        )

        # mocking rtapi call
        with patch("l3racktables.utils._RACKTABLES_API") as rt_api_mock:

            rt_api_mock.get_networks_info = Mock()
            rt_api_mock.get_networks_info.return_value = [
                RackTablesNetworkInfo(ip, tag, "") for ip, (tag, _) in mocked_rt_networks_response.items()
            ]

            update_rt_networks()

        self.assertEqual(len(expected_manual_networks), LocationNetwork.objects.filter(source="MANUAL").count())
        self.assertEqual(len(expected_rt_networks), LocationNetwork.objects.filter(source="RACKTABLES").count())

        for prefix, (tag, location) in expected_rt_networks.items():
            prefix_description = LocationNetwork.objects.get(ip=prefix, source="RACKTABLES")
            self.assertEqual(tag, prefix_description.original)
            self.assertEqual(set(location), set(prefix_description.location))

    @parameterized.expand(
        [
            (
                "2a02:6b8:b020:5000::/56\tМянтсяля-1\tbackbone\n"
                "5.45.241.0/24\tВладимир\tbackbone\n"
                "37.140.170.0/23\tНесуществующая_локация\tbackbone\n",
                {
                    "2a02:6b8:b020:5000::/56": ("Мянтсяля-1", ["MAN"]),
                    "5.45.241.0/24": ("Владимир", ["VLA"]),
                    "37.140.170.0/23": ("Несуществующая_локация", []),
                },
            ),
            (
                "2a02:6b8:b010:502a::/64\tИвантеевка\tbackbone\n" "87.250.239.56/31\tМытищи\tbackbone\n",
                {
                    "2a02:6b8:b010:502a::/64": ("Ивантеевка", ["IVA"]),
                    "87.250.239.56/31": ("Мытищи", ["MYT"]),
                },
            ),
            (
                "5.45.224.0/24\tВладимир\tbackbone\n"
                "5.45.236.0/22\tВладимир AZ\tbackbone\n"
                "5.255.198.0/23\tВладимир\tbackbone\n",
                {
                    "5.45.224.0/24": ("Владимир", ["VLA"]),
                    "5.45.236.0/22": ("Владимир AZ", ["VLX"]),
                    "5.255.198.0/23": ("Владимир", ["VLA"]),
                },
            ),
            ("", {}),
        ],
    )
    def test_rt_networks_update_mocked_body(self, racktables_payload, expected_rt_networks):
        from l3mgr.models import LocationNetwork

        with patch.object(RackTablesApi, "_read_text", autospec=True) as read_text:
            read_text.return_value = racktables_payload
            update_rt_networks()

        self.assertEqual(len(expected_rt_networks), LocationNetwork.objects.filter(source="RACKTABLES").count())
        for prefix, (tag, location) in expected_rt_networks.items():
            prefix_description = LocationNetwork.objects.get(ip=prefix, source="RACKTABLES")
            self.assertEqual(tag, prefix_description.original)
            self.assertEqual(set(location), set(prefix_description.location))


class RTServicesTestCase(TestCase):
    databases = "__all__"

    @parameterized.expand(
        [
            (
                {
                    "192.0.2.1": "fqdn-v4-1.test",
                    "192.0.2.2": "fqdn-v4-2.test",
                    "192.0.2.5": "fqdn-v4-5.test",
                    "192.0.2.6": "fqdn-v4-6.test",
                    "192.0.2.7": "fqdn-v4-7.test",
                    "2001:db8:ffff::3": "fqdn-v6-3.test",
                    "2001:db8:ffff::4": "fqdn-v6-4.test",
                    "2001:db8:ffff::5": "fqdn-v6-5.test",
                    "2001:db8:ffff::6": "fqdn-v6-6.test",
                    "2001:db8:ffff::7": "fqdn-v6-7.test",
                },
                {
                    "192.0.2.3": "fqdn-v4-3.test",
                    "192.0.2.4": "fqdn-v4-4.test",
                    "2001:db8:ffff::1": "fqdn-v6-1.test",
                    "2001:db8:ffff::2": "fqdn-v6-2.test",
                },
                {
                    "192.0.2.1": "fqdn-v4-1-c.test",
                    "192.0.2.2": "fqdn-v4-2.test",
                    "192.0.2.3": "fqdn-v4-3.test",
                    "192.0.2.4": "fqdn-v4-4.test",
                    "192.0.2.5": "fqdn-v4-5.test",
                    "192.0.2.6": "fqdn-v4-6.test",
                    "192.0.2.7": "fqdn-v4-7.test",
                    "2001:db8:ffff::1": "fqdn-v6-1.test",
                    "2001:db8:ffff::2": "fqdn-v6-2.test",
                    "2001:db8:ffff::3": "fqdn-v6-3.test",
                    "2001:db8:ffff::4": "fqdn-v6-4.test",
                    "2001:db8:ffff::5": "fqdn-v6-5.test",
                    "2001:db8:ffff::6": "fqdn-v6-6.test",
                    "2001:db8:ffff::7": "fqdn-v6-7-c.test",
                },
                {
                    "192.0.2.1": "fqdn-v4-1-c.test",
                    "192.0.2.2": "fqdn-v4-2.test",
                    "192.0.2.5": "fqdn-v4-5.test",
                    "192.0.2.6": "fqdn-v4-6.test",
                    "192.0.2.7": "fqdn-v4-7.test",
                    "2001:db8:ffff::3": "fqdn-v6-3.test",
                    "2001:db8:ffff::4": "fqdn-v6-4.test",
                    "2001:db8:ffff::5": "fqdn-v6-5.test",
                    "2001:db8:ffff::6": "fqdn-v6-6.test",
                    "2001:db8:ffff::7": "fqdn-v6-7-c.test",
                },
            ),
            (
                {
                    "192.0.2.1": "fqdn-v4-1.test",
                    "192.0.2.2": "fqdn-v4-2.test",
                    "192.0.2.3": "fqdn-v4-3.test",
                    "2001:db8:ffff::3": "fqdn-v6-3.test",
                    "2001:db8:ffff::4": "fqdn-v6-4.test",
                    "2001:db8:ffff::5": "fqdn-v6-5.test",
                },
                {
                    "192.0.2.4": "fqdn-v4-4.test",
                    "192.0.2.5": "fqdn-v4-5.test",
                    "2001:db8:ffff::1": "fqdn-v6-1.test",
                    "2001:db8:ffff::2": "fqdn-v6-2.test",
                },
                {
                    "192.0.2.1": "fqdn-v4-1.test",
                    "192.0.2.2": "fqdn-v4-2.test",
                    "192.0.2.3": "fqdn-v4-3.test",
                    "192.0.2.4": "fqdn-v4-4.test",
                    "192.0.2.5": "fqdn-v4-5.test",
                    "192.0.2.6": "fqdn-v4-6.test",
                    "2001:db8:ffff::1": "fqdn-v6-1.test",
                    "2001:db8:ffff::2": "fqdn-v6-2.test",
                    "2001:db8:ffff::3": "fqdn-v6-3.test",
                    "2001:db8:ffff::4": "fqdn-v6-4.test",
                    "2001:db8:ffff::5": "fqdn-v6-5.test",
                    "2001:db8:ffff::6": "fqdn-v6-5.test",
                },
                {
                    "192.0.2.1": "fqdn-v4-1.test",
                    "192.0.2.2": "fqdn-v4-2.test",
                    "192.0.2.3": "fqdn-v4-3.test",
                    "192.0.2.6": "fqdn-v4-6.test",
                    "2001:db8:ffff::3": "fqdn-v6-3.test",
                    "2001:db8:ffff::4": "fqdn-v6-4.test",
                    "2001:db8:ffff::5": "fqdn-v6-5.test",
                    "2001:db8:ffff::6": "fqdn-v6-5.test",
                },
            ),
            (
                {
                    "192.0.2.1": "fqdn-v4-1.test",
                    "192.0.2.2": "fqdn-v4-2.test",
                    "192.0.2.3": "fqdn-v4-3.test",
                    "2001:db8:ffff::3": "fqdn-v6-3.test",
                    "2001:db8:ffff::4": "fqdn-v6-4.test",
                    "2001:db8:ffff::5": "fqdn-v6-5.test",
                },
                {
                    "192.0.2.4": "fqdn-v4-4.test",
                    "192.0.2.5": "fqdn-v4-5.test",
                    "2001:db8:ffff::1": "fqdn-v6-1.test",
                    "2001:db8:ffff::2": "fqdn-v6-2.test",
                },
                {
                    "192.0.2.1": "fqdn-v4-1.test",
                    "192.0.2.2": "fqdn-v4-2.test",
                    "192.0.2.4": "fqdn-v4-4.test",
                    "192.0.2.5": "fqdn-v4-5.test",
                    "2001:db8:ffff::1": "fqdn-v6-1.test",
                    "2001:db8:ffff::3": "fqdn-v6-3.test",
                    "2001:db8:ffff::4": "fqdn-v6-4.test",
                    "2001:db8:ffff::5": "fqdn-v6-5.test",
                },
                # don't care about ::2 deletion in RT, cause it's L3 Manager native
                {
                    "192.0.2.1": "fqdn-v4-1.test",
                    "192.0.2.2": "fqdn-v4-2.test",
                    "2001:db8:ffff::3": "fqdn-v6-3.test",
                    "2001:db8:ffff::4": "fqdn-v6-4.test",
                    "2001:db8:ffff::5": "fqdn-v6-5.test",
                },
            ),
        ]
    )
    def test_sync_rt_services(self, existing_rt_services, existing_vs, mocked_rt_response, expected_result):
        l3m_service = Service.objects.create(fqdn="service.test", abc="dostavkatraffika")

        RackTablesService.objects.bulk_create(
            [RackTablesService(ip=ip, fqdn=fqdn) for ip, fqdn in existing_rt_services.items()]
        )
        VirtualServer.objects.bulk_create(
            [VirtualServer(service=l3m_service, config="", ip=ip, port=80, protocol="TCP") for ip in existing_vs.keys()]
        )

        with patch("l3racktables.utils._RACKTABLES_API") as rt_api_mock:
            rt_api_mock.get_rt_services_info = Mock()
            rt_api_mock.get_rt_services_info.return_value = [
                RackTablesServiceInfo(ip, fqdn) for ip, fqdn in mocked_rt_response.items()
            ]

            sync_rt_services()

        self.assertEqual(len(expected_result), RackTablesService.objects.all().count())

        for ip, fqdn in expected_result.items():
            rt_service = RackTablesService.objects.get(ip=ip)
            self.assertEqual(fqdn, rt_service.fqdn)

    @patch("l3racktables.utils._RACKTABLES_API")
    def test_sync_rt_services_too_many_deletions(self, rtapi_mock):
        mocked_rt_response = {"192.0.2.1": "fqdn-v4-1.test", "2001:db8:ffff::5": "fqdn-v6-5.test"}
        rtapi_mock.get_rt_services_info = Mock()
        rtapi_mock.get_rt_services_info.return_value = [
            RackTablesServiceInfo(ip, fqdn) for ip, fqdn in mocked_rt_response.items()
        ]
        existing_rt_services = {
            "192.0.2.1": "fqdn-v4-1.test",
            "192.0.2.2": "fqdn-v4-2.test",
            "192.0.2.5": "fqdn-v4-5.test",
            "2001:db8:ffff::3": "fqdn-v6-3.test",
            "2001:db8:ffff::4": "fqdn-v6-4.test",
            "2001:db8:ffff::5": "fqdn-v6-5.test",
        }
        RackTablesService.objects.bulk_create(
            [RackTablesService(ip=ip, fqdn=fqdn) for ip, fqdn in existing_rt_services.items()]
        )
        with self.assertRaises(RackTablesServicesUpdateException):
            sync_rt_services()

    @patch("l3racktables.utils._RACKTABLES_API")
    def test_sync_rt_services_too_many_deletions_but_force(self, rtapi_mock):
        mocked_rt_response = {"192.0.2.1": "fqdn-v4-1.test", "2001:db8:ffff::5": "fqdn-v6-5.test"}
        rtapi_mock.get_rt_services_info = Mock()
        rtapi_mock.get_rt_services_info.return_value = [
            RackTablesServiceInfo(ip, fqdn) for ip, fqdn in mocked_rt_response.items()
        ]
        existing_rt_services = {
            "192.0.2.1": "fqdn-v4-1.test",
            "192.0.2.2": "fqdn-v4-2.test",
            "192.0.2.5": "fqdn-v4-5.test",
            "2001:db8:ffff::3": "fqdn-v6-3.test",
            "2001:db8:ffff::4": "fqdn-v6-4.test",
            "2001:db8:ffff::5": "fqdn-v6-5.test",
        }
        RackTablesService.objects.bulk_create(
            [RackTablesService(ip=ip, fqdn=fqdn) for ip, fqdn in existing_rt_services.items()]
        )
        sync_rt_services(force=True)
        self.assertEqual(RackTablesService.objects.all().count(), 2)


class SyncRTServicesTestCase(TestCase):
    def test_sync_rt_services(self):
        rt_objects = [
            RackTablesService(ip="1.1.1.1", fqdn="cloudflare.com"),
            RackTablesService(ip="8.8.8.8", fqdn="alet-external-afisha-mapi.stable.qloud-b.yandex.net"),
            RackTablesService(ip="77.88.8.3", fqdn="ur.xednay.snd.ylimaf"),
            *[RackTablesService(ip=f"0.0.0.{i}", fqdn=f"random-{i}-service.yandex.net") for i in range(0, 4)],
        ]
        created = RackTablesService.objects.bulk_create(rt_objects)
        self.assertEqual(len(rt_objects), len(created))

        with patch.object(RackTablesApi, "_read_lines", autospec=True) as read_text:
            read_text.return_value = (
                "77.88.8.0/24	id: 1416, name: public VIPs безопасных DNS",
                "	77.88.8.3 - family.dns.yandex.ru",
                "	77.88.8.7 - one-more-family.dns.yandex.ru",
                "	77.88.8.7 - family.dns.yandex.ru",
                "	77.88.8.8 - one-more-family.dns.yandex.ru",
                "77.88.21.0/24	id: 10, name: Публичные виртуальные сервисы",
                "	77.88.21.2 - alet-external-afisha-mapi.stable.qloud-b.yandex.net",
            )
            with self.assertRaises(RackTablesServicesUpdateException):
                sync_rt_services()
            self.assertDictEqual(
                {rt.fqdn: rt.ip for rt in rt_objects},
                dict(RackTablesService.objects.values_list("fqdn", "ip")),
            )

            sync_rt_services(force=True)
        self.assertCountEqual(
            [
                {"ip": "77.88.8.3", "fqdn": "family.dns.yandex.ru"},
                {"ip": "77.88.8.7", "fqdn": "one-more-family.dns.yandex.ru"},
                {"ip": "77.88.8.7", "fqdn": "family.dns.yandex.ru"},
                {"ip": "77.88.8.8", "fqdn": "one-more-family.dns.yandex.ru"},
                {"ip": "77.88.21.2", "fqdn": "alet-external-afisha-mapi.stable.qloud-b.yandex.net"},
            ],
            list(RackTablesService.objects.values("fqdn", "ip")),
        )
