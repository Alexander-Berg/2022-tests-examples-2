import json

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from discounts_plugins import *  # noqa: F403 F401
# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name
import pytest  # pylint: disable=wrong-import-order


@pytest.fixture(name='taxi-tariffs', autouse=True)
def _mock_tariffs(mockserver):
    @mockserver.handler('/taxi-tariffs/v1/tariff_zones')
    def _bulk_retrieve(request):
        zone_response = {
            'zones': [
                {
                    'name': 'moscow',
                    'time_zone': 'Europe/Moscow',
                    'country': 'rus',
                    'translation': 'moscow',
                    'currency': 'RUB',
                },
                {
                    'name': 'perm',
                    'time_zone': 'Asia/Yekaterinburg',
                    'country': 'rus',
                    'translation': 'perm',
                    'currency': 'RUB',
                },
                {
                    'name': 'testsuite_zone',
                    'time_zone': 'EST',
                    'country': 'rus',
                    'translation': 'testsuite_zone',
                    'currency': 'RUB',
                },
                {
                    'name': 'testsuite_zone_1',
                    'time_zone': 'Europe/Moscow',
                    'country': 'rus',
                    'translation': 'testsuite_zone',
                    'currency': 'EUR',
                },
            ],
        }
        return mockserver.make_response(json.dumps(zone_response), 200)


@pytest.fixture(name='user-statistics', autouse=True)
def _mock_user_statistics(mockserver):
    @mockserver.handler('/user-statistics/v1/orders')
    def _bulk_retrieve(request):
        zone_response = {
            'data': [
                {
                    'identity': {
                        'type': 'phone_id',
                        'value': '5714f45e98956f06baaae3d4',
                    },
                    'counters': [
                        {
                            'properties': [
                                {'name': 'brand', 'value': 'vezet'},
                                {'name': 'payment_type', 'value': 'cash'},
                            ],
                            'value': 1,
                            'counted_from': '2019-10-01T12:54:46+0000',
                            'counted_to': '2019-10-01T12:54:46+0000',
                        },
                        {
                            'properties': [
                                {'name': 'brand', 'value': 'yango'},
                                {'name': 'payment_type', 'value': 'card'},
                            ],
                            'value': 1,
                            'counted_from': '2019-10-25T07:15:56+0000',
                            'counted_to': '2019-10-25T07:15:56+0000',
                        },
                        {
                            'properties': [
                                {'name': 'brand', 'value': 'yataxi'},
                                {'name': 'payment_type', 'value': 'card'},
                            ],
                            'value': 102,
                            'counted_from': '2019-03-29T07:07:20+0000',
                            'counted_to': '2020-09-22T13:01:59.863+0000',
                        },
                        {
                            'properties': [
                                {'name': 'brand', 'value': 'yataxi'},
                                {'name': 'payment_type', 'value': 'cash'},
                            ],
                            'value': 35,
                            'counted_from': '2018-11-29T09:02:15+0000',
                            'counted_to': '2020-09-10T10:48:57+0000',
                        },
                        {
                            'properties': [
                                {'name': 'brand', 'value': 'yataxi'},
                                {
                                    'name': 'payment_type',
                                    'value': 'coop_account',
                                },
                            ],
                            'value': 113,
                            'counted_from': '2019-03-29T10:15:10+0000',
                            'counted_to': '2020-06-19T16:26:39+0000',
                        },
                        {
                            'properties': [
                                {'name': 'brand', 'value': 'yataxi'},
                                {'name': 'payment_type', 'value': 'corp'},
                            ],
                            'value': 65,
                            'counted_from': '2020-04-01T13:14:40+0000',
                            'counted_to': '2020-09-03T14:35:17+0000',
                        },
                        {
                            'properties': [
                                {'name': 'brand', 'value': 'yataxi'},
                                {'name': 'payment_type', 'value': 'googlepay'},
                            ],
                            'value': 1,
                            'counted_from': '2018-11-29T08:45:06+0000',
                            'counted_to': '2018-11-29T08:45:06+0000',
                        },
                        {
                            'properties': [
                                {'name': 'brand', 'value': 'unknown'},
                                {'name': 'payment_type', 'value': 'card'},
                            ],
                            'value': 6,
                            'counted_from': '2019-03-05T09:26:47+0000',
                            'counted_to': '2019-03-05T10:12:38+0000',
                        },
                    ],
                },
            ],
        }
        return mockserver.make_response(json.dumps(zone_response), 200)
