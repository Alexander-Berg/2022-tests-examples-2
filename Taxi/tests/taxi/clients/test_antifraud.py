# pylint: disable=unused-variable
import datetime

import aiohttp
import bson
import pytest

from taxi import config
from taxi import discovery
from taxi.clients import antifraud
from taxi.clients import tvm


@pytest.fixture(name='tvm_client')
def tvm_client_fixture(simple_secdist, aiohttp_client, patch):
    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    async def _get_auth_headers_mock(*args, **kwargs):
        return {tvm.TVM_TICKET_HEADER: 'ticket'}

    return tvm.TVMClient(
        service_name='billing_subventions',
        secdist=simple_secdist,
        config=config,
        session=aiohttp_client,
    )


async def test_check_orders(mockserver, tvm_client):
    @mockserver.json_handler('/antifraud/subvention/check_orders')
    def patch_request(request):
        assert request.json == {
            'orders': [
                {
                    'order_id': '79e24f61b8f94535971dcfa0e3c85b32',
                    'license': '6117434652',
                },
                {
                    'order_id': '8bf9395790a84943ac6723f22cc5288c',
                    'license': '0133312345',
                },
            ],
        }
        return {
            'orders': [
                {
                    'order_id': '79e24f61b8f94535971dcfa0e3c85b32',
                    'license': '6117434652',
                    'found': True,
                    'frauder': True,
                    'rule_id': 'small_cost_ban_rule',
                    'confidence': '10011',
                },
                {
                    'order_id': '8bf9395790a84943ac6723f22cc5288c',
                    'license': '0133312345',
                    'found': True,
                    'frauder': False,
                },
            ],
        }

    client = antifraud.AntifraudClient(
        discovery.find_service('antifraud'),
        aiohttp.ClientSession(),
        tvm_client,
    )
    response = await client.check_orders(
        [
            {
                'order_id': '79e24f61b8f94535971dcfa0e3c85b32',
                'license': '6117434652',
            },
            {
                'order_id': '8bf9395790a84943ac6723f22cc5288c',
                'license': '0133312345',
            },
        ],
    )
    assert len(response['orders']) == 2


async def test_check_driver(mockserver, tvm_client):
    @mockserver.json_handler('/antifraud/personal_subvention/check_drivers')
    def _wrapper(request):
        assert request.json == {
            'drivers': [
                {
                    'udi': '1' * 24,
                    'licenses': ['some_license'],
                    'rules': [
                        {'day_ride_count_days': 2, 'day_ride_count': [40]},
                    ],
                },
            ],
            'period_end': '2019-02-21T00:00:00+00:00',
        }
        return {
            'drivers': [
                {'found': True, 'frauder': False, 'license': 'some_license'},
            ],
        }

    client = antifraud.AntifraudClient(
        discovery.find_service('antifraud'),
        aiohttp.ClientSession(),
        tvm_client,
    )
    response = await client.check_driver(
        subvention_type=antifraud.SubventionType.GOAL,
        unique_driver_id=bson.ObjectId('1' * 24),
        driver_licenses=['some_license'],
        rule_info=antifraud.RuleInfo(days_span=2, min_num_orders=40),
        last_shift_date=datetime.date(2019, 2, 21),
    )
    assert len(response['drivers']) == 1
