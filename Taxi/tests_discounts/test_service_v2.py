import json

import pytest

from tests_discounts import common


DEFAULT_DISCOUNTS_INFO_REQUEST = {
    'zone': 'moscow',
    'waypoints': [[53.000, 35.000], [53.100, 35.100]],
    'surge_values': {'econom': 1.2, 'business': 1.5},
    'user_info': {
        'user_id': 'user_id',
        'phone_id': '5714f45e98956f06baaae3d4',
        'phone_hash': '138aa82720f81ba2249011d',
        'personal_phone_id': 'cc6584d7a4464d63b62477f9fe1f7adb',
        'yandex_uid': 'Yandex_uid',
        'completed_count': 1,
        'completed_card_count': 0,
        'completed_googlepay_count': 0,
        'completed_applepay_count': 0,
        'big_first_count': 0,
    },
    'payment_info': {'type': 'card', 'method_id': 'card_method_id'},
    'due': '2019-01-01T00:00:00Z',
    'timezone': 'UTC',
    'is_workday': False,
    'is_airport_ride': False,
    'requested_categories': ['econom', 'business'],
    'yaplus_categories': [],
}

DEFAULT_USER_TAGS = ['dummy_tag']


@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
    ],
)
@pytest.mark.parametrize(
    'subvention_end, any_discounts',
    (('2029-01-01T00:00:00Z', True), ('9999-12-31T23:59:59Z', True)),
)
@pytest.mark.config(
    DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True},
    DISCOUNTS_CHECK_TAGS_TOPIC=True,
)
async def test_v2_get_discount(
        taxi_discounts, mockserver, subvention_end, any_discounts,
):
    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def mock_v2_match(request):
        data = json.loads(request.get_data())
        assert 'match' in data and data['match']
        match_types = [m_elem['type'] for m_elem in data['match']]
        assert 'personal_phone_id' in match_types
        assert 'user_phone_id' in match_types
        assert 'phone_hash_id' in match_types
        assert 'topics' in data
        assert data['topics'] == ['discounts']
        return {'tags': DEFAULT_USER_TAGS}

    @mockserver.json_handler('/cardstorage/v1/card')
    def mock_v1_card(request):
        return {
            'card_id': 'card_method_id',
            'billing_card_id': '',
            'permanent_card_id': '',
            'currency': 'rub',
            'expiration_month': 12,
            'expiration_year': 30,
            'number': '123456_____________',
            'owner': '',
            'possible_moneyless': True,
            'region_id': '',
            'regions_checked': [],
            'system': '',
            'valid': True,
            'bound': False,
            'unverified': False,
            'busy': False,
            'busy_with': [],
            'from_db': True,
        }

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _rules_select(request):
        return {
            'subventions': [
                {
                    'tariff_zones': ['moscow'],
                    'status': 'enabled',
                    'start': '2009-01-01T00:00:00Z',
                    'end': subvention_end,
                    'type': 'discount_payback',
                    'is_personal': False,
                    'taxirate': '',
                    'subvention_rule_id': '__moscow__',
                    'cursor': '',
                    'tags': [],
                    'time_zone': {'id': '', 'offset': ''},
                    'updated': '2019-01-01T00:00:00Z',
                    'currency': 'rub',
                    'visible_to_driver': False,
                    'week_days': [],
                    'hours': [],
                    'log': [],
                    'tariff_classes': [],
                },
            ],
        }

    await taxi_discounts.invalidate_caches()
    await taxi_discounts.invalidate_caches()
    response = await taxi_discounts.post(
        'v2/get-discount',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(DEFAULT_DISCOUNTS_INFO_REQUEST),
    )
    assert response.status_code == 200
    assert mock_v2_match.has_calls
    assert mock_v2_match.times_called == 1
    assert mock_v1_card.has_calls
    assert mock_v1_card.times_called == 1

    response_json = response.json()
    econom_discount = response_json['econom']
    assert econom_discount == {
        'calc_data': {
            'hyperbola_lower': {'a': 42000.0, 'c': 1400.0, 'p': -8.0},
            'hyperbola_upper': {'a': 3000.0, 'c': 0.0, 'p': 8.0},
            'threshold': 600.0,
        },
        'calc_type': 'hyperbolas',
        'id': 'econom_discount_hyperbolas',
        'is_cashback': False,
        'is_price_strikethrough': True,
        'restrictions': {
            'driver_less_coeff': 0.0,
            'limited_rides': False,
            'max_discount_coeff': 0.2,
            'min_discount_coeff': 0.01,
            'payment_type': 'card',
            'recalc_type': 'none',
        },
    }
    business_discount = response_json['business']
    assert business_discount == {
        'calc_data': [
            {'coeff': 0.5, 'price': 100.0},
            {'coeff': 0.3, 'price': 200.0},
            {'coeff': 0.1, 'price': 300.0},
        ],
        'calc_type': 'table',
        'id': 'business_discount_table',
        'is_cashback': False,
        'is_price_strikethrough': True,
        'restrictions': {
            'driver_less_coeff': 0.0,
            'limited_rides': False,
            'max_discount_coeff': 0.2,
            'min_discount_coeff': 0.01,
            'payment_type': 'card',
            'recalc_type': 'none',
        },
    }
