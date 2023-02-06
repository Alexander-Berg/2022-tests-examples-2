# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from typing import Optional
import urllib
import uuid

import pytest

from ride_discounts_plugins import *  # noqa: F403 F401

from tests_ride_discounts import common


def pytest_configure(config):
    config.addinivalue_line('markers', 'slow: mark slow test')


@pytest.fixture(autouse=True)
async def user_statistics_handler(mockserver):
    @mockserver.json_handler('/user-statistics/v1/orders')
    def _v1_orders(request):
        return {'data': []}


@pytest.fixture(name='start_revision')
def _start_revision():
    return '22'


@pytest.fixture
def reset_revision(pgsql, start_revision):
    pgsql['ride_discounts'].cursor().execute(
        'ALTER SEQUENCE ride_discounts.match_rules_revision '
        f'RESTART WITH {start_revision};',
    )


@pytest.fixture
def reset_data_id(pgsql):
    pg_cursor = pgsql['ride_discounts'].cursor()
    pg_cursor.execute(
        'ALTER SEQUENCE ride_discounts.match_data_data_id_seq '
        f'RESTART WITH {common.START_DATA_ID};',
    )


@pytest.fixture
async def additional_rules():
    return [
        {
            'condition_name': 'zone',
            'values': [
                {
                    'is_prioritized': False,
                    'name': 'br_moscow',
                    'type': 'geonode',
                },
            ],
        },
    ]


@pytest.fixture(autouse=True)
def mock_taxi_tariffs(mockserver):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    def _tariff_zones(request):
        zones = [
            {
                'name': name,
                'time_zone': 'Europe/Moscow',
                'country': 'rus',
                'translation': name,
                'currency': 'RUB',
            }
            for name in request.query.get(
                'zone_names', 'moscow,boryasvo,vko',
            ).split(',')
        ]
        return {'zones': zones}


@pytest.fixture(autouse=True)
def mock_tariff_settings(mockserver):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff_settings/list')
    def _mock_tariff_setting_list(request):
        params = urllib.parse.parse_qs(request.query_string.decode())
        cursor = params.get('cursor', [''])[0]
        if cursor == 'final':
            return {'zones': [], 'next_cursor': 'final'}
        return {
            'zones': [
                {
                    'categories': [
                        {
                            'can_be_default': True,
                            'card_payment_settings': {
                                'max_compensation': 5000,
                                'max_manual_charge': 5000,
                                'max_refund': 5000,
                            },
                            'charter_contract': True,
                            'client_constraints': [],
                            'client_requirements': [
                                'bicycle',
                                'childchair_moscow',
                                'yellowcarnumber',
                                'conditioner',
                                'nosmoking',
                            ],
                            'comments_disabled': False,
                            'disable_ban_for_feedback': False,
                            'disable_destination_change': False,
                            'disable_live_location': False,
                            'disable_zone_leave': False,
                            'driver_change_cost': {},
                            'fixed_price_enabled': True,
                            'free_cancel_timeout': 300,
                            'glued_requirements': [],
                            'is_default': True,
                            'legal_entities_enabled': True,
                            'mark_as_new': False,
                            'max_card_payment': 5000,
                            'max_corp_payment': 5000,
                            'max_route_points_count': 5,
                            'name': 'econom',
                            'only_for_soon_orders': False,
                            'persistent_requirements': [
                                'animaltransport',
                                'nosmoking',
                            ],
                            'req_destination': False,
                            'service_levels': [50],
                            'tanker_key': 'name.econom',
                            'toll_roads_enabled': False,
                        },
                    ],
                    'home_zone': 'moscow',
                    'timezone': 'Europe/Moscow',
                },
                {'home_zone': 'boryasvo', 'timezone': 'Europe/Moscow'},
                {'home_zone': 'vko', 'timezone': 'Europe/Moscow'},
            ],
            'next_cursor': 'final',
        }


@pytest.fixture(autouse=True)
def mock_billing_limits(mockserver):

    data = {
        'currency': 'RUB',
        'label': 'discount limit discount_limit_id',
        'windows': [
            {
                'type': 'tumbling',
                'value': '100000.0000',
                'size': 86400,
                'label': 'Daily limit',
                'threshold': 100,
                'tumbling_start': '2019-01-01T00:00:00+00:00',
            },
            {
                'type': 'sliding',
                'value': '700000.0000',
                'size': 604800,
                'label': 'Weekly limit',
                'threshold': 100,
                'tumbling_start': '2019-01-01T00:00:00+00:00',
            },
        ],
        'tickets': ['ticket-1'],
        'ref': 'discount_limit_id',
        'approvers': ['approver'],
        'tags': ['ride-discounts'],
    }

    @mockserver.json_handler('/billing-limits/v1/get')
    def _get(request):
        return data

    @mockserver.json_handler('/billing-limits/v1/create')
    def _create(request):
        return data


@pytest.fixture()
def client(taxi_ride_discounts):
    return taxi_ride_discounts


@pytest.fixture()
def add_rules_check_url():
    return common.ADD_RULES_CHECK_URL


@pytest.fixture()
def add_rules_url():
    return common.ADD_RULES_URL


@pytest.fixture()
def service_name():
    return 'ride_discounts'


@pytest.fixture()
def headers():
    return common.get_headers()


@pytest.fixture()
def default_discount():
    return common.make_discount(hierarchy_name='full_money_discounts')


@pytest.fixture()
def condition_descriptions(load_json):
    return load_json('condition_descriptions.json')


@pytest.fixture()
def prioritized_entity_url():
    return common.PRIORITIZED_ENTITY_URL


@pytest.fixture()
def hierarchy_descriptions_url():
    return '/v1/admin/match-discounts/hierarchy-descriptions'


@pytest.fixture()
def draft_id_is_uuid():
    return True


@pytest.fixture()
def add_discount(add_rules):
    async def wrapper(
            hierarchy_name: str,
            rules,
            series_id: Optional[uuid.UUID] = None,
            discount=None,
    ):
        await add_rules(
            {
                hierarchy_name: [
                    {
                        'rules': rules,
                        'discount': discount or common.make_discount(
                            hierarchy_name=hierarchy_name,
                        ),
                        'series_id': str(series_id) if series_id else None,
                    },
                ],
            },
        )

    return wrapper
