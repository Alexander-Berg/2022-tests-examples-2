import json

import pytest

from tests_discounts import common


def mock_request(payment_info=None):
    if payment_info is None:
        payment_info = {'type': 'card', 'method_id': 'card_method_id'}

    return {
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
        'payment_info': payment_info,
        'due': '2019-01-01T00:00:00Z',
        'timezone': 'UTC',
        'is_workday': False,
        'is_airport_ride': False,
        'requested_categories': ['econom', 'business', 'comfortplus'],
        'yaplus_categories': [],
    }


def expected_discount(
        calc_type,
        discount_id,
        description,
        reason,
        discount_class='discount_class1',
        is_price_strikethrough=False,
        payment_type='card',
        card_bin=None,
):
    if calc_type == 'hyperbolas':
        calc_data = {
            'hyperbola_lower': {'a': 42000.0, 'c': 1400.0, 'p': -8.0},
            'hyperbola_upper': {'a': 3000.0, 'c': 0.0, 'p': 8.0},
            'threshold': 600.0,
        }
    elif calc_type == 'table':
        calc_data = [
            {'coeff': 0.5, 'price': 100.0},
            {'coeff': 0.3, 'price': 200.0},
            {'coeff': 0.1, 'price': 300.0},
        ]

    discount = {
        'calc_data': calc_data,
        'calc_type': calc_type,
        'is_cashback': False,
        'restrictions': {
            'driver_less_coeff': 0.0,
            'max_discount_coeff': 0.2,
            'min_discount_coeff': 0.01,
            'payment_type': payment_type,
            'recalc_type': 'none',
        },
        'discount_info': {
            'description': description,
            'discount_id': discount_id,
            'discount_class': discount_class,
            'limited_rides': False,
            'method': 'full',
            'reason': reason,
            'is_price_strikethrough': is_price_strikethrough,
        },
    }

    if card_bin is not None:
        discount['discount_info']['card_bin'] = card_bin

    return discount


DEFAULT_USER_TAGS = ['dummy_tag']


@pytest.fixture(autouse=True)
def mock_services(mockserver):
    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def _mock_v2_match(request):
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
    def _mock_v1_card(request):
        return {
            'card_id': 'card_method_id',
            'ebin_tags': ['main_bin_label', 'another_bin_label'],
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
                    'end': '9999-12-31T23:59:59Z',
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

    @mockserver.json_handler(
        '/taxi-shared-payments/internal/coop_account/paymentmethod/short_info',
    )
    def _coop_account(request):
        return {
            'account_type': 'business',
            'owner_uid': '0123456789',
            'payment_method_id': 'card_method_id',
            'payment_method_type': 'card',
        }


@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
        'bin_label_sets.sql',
    ],
)
@pytest.mark.config(
    DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True},
    DISCOUNTS_CHECK_TAGS_TOPIC=True,
)
@pytest.mark.parametrize(
    'enocom_discount_id,econom_description, has_bussness',
    (
        pytest.param(
            'econom_discount_hyperbolas',
            'discount1',
            True,
            id='with disabled filter by bin labels',
        ),
        pytest.param(
            'econom_discount_hyperbolas_with_valid_bin_labels',
            'discount_with_bin_label',
            False,
            marks=pytest.mark.config(
                DISCOUNTS_FILTER_BY_BIN_LABELS_ENABLED=True,
            ),
            id='with enabled filter by bin labels',
        ),
    ),
)
async def test_v3_get_discount(
        taxi_discounts, enocom_discount_id, econom_description, has_bussness,
):
    response = await taxi_discounts.post(
        'v3/get-discount',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        json=mock_request(),
    )
    assert response.status_code == 200

    response_json = response.json()

    assert response_json['discounts']['econom'] == expected_discount(
        calc_type='hyperbolas',
        discount_id=enocom_discount_id,
        description=econom_description,
        reason='analytics',
        is_price_strikethrough=True,
        discount_class='discount_class1',
        card_bin='123456',
    )
    if has_bussness:
        assert response_json['discounts']['business'] == expected_discount(
            calc_type='table',
            discount_id='business_discount_table',
            description='discount3',
            discount_class='discount_class3',
            reason='for_all',
        )
    else:
        assert 'business' not in response_json['discounts']


@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
    ],
)
@pytest.mark.config(
    DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True},
    DISCOUNTS_CHECK_TAGS_TOPIC=True,
)
async def test_v3_get_discount_geoareas(taxi_discounts, mockserver):
    request = mock_request()
    request['geoareas_only_b'] = ['spb']
    response = await taxi_discounts.post(
        'v3/get-discount',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        json=request,
    )
    assert response.status_code == 200

    response_json = response.json()
    discounts = response_json['discounts']
    assert not discounts


@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
    ],
)
@pytest.mark.config(
    DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True},
    DISCOUNTS_CHECK_TAGS_TOPIC=True,
)
async def test_discount_ride_properties(taxi_discounts):
    request = mock_request()
    request['ride_options'] = ['boxberry_opt']
    response = await taxi_discounts.post(
        'v3/get-discount',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        json=request,
    )
    assert response.status_code == 200

    response_json = response.json()

    assert response_json['discounts']['econom'] == expected_discount(
        calc_type='hyperbolas',
        discount_id='econom_discount_for_iphone',
        discount_class='discount_class',
        description='discount2',
        reason='for_all',
    )
    assert response_json['discounts']['business'] == expected_discount(
        calc_type='hyperbolas',
        discount_id='business_discount_for_ipnone',
        discount_class='discount_class',
        description='discount4',
        reason='for_all',
    )


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
    'request_patch,expected_discounts',
    [
        pytest.param(
            {
                'waypoints': [
                    [37.566359, 55.742975],
                    [37.565221, 55.742112],
                    [37.661230, 55.756989],
                ],
            },
            [
                'econom_intermediate_points_not_prohibited',
                'comfortplus_intermediate_points_not_prohibited',
            ],
            id='Route has 3 points',
        ),
        # kazansky railway -> domodedovo airport
        pytest.param(
            {'waypoints': [[37.661230, 55.756989], [37.899361, 55.414867]]},
            [
                'econom_intermediate_points_prohibited',
                'comfortplus_intermediate_points_not_prohibited',
            ],
            id='Route has 2 points',
        ),
    ],
)
@pytest.mark.config(
    DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True},
    DISCOUNTS_CHECK_TAGS_TOPIC=True,
)
async def test_v3_intermediate_prohibited_discount(
        taxi_discounts, request_patch, expected_discounts,
):
    data = mock_request()
    data['requested_categories'] = ['econom', 'comfortplus']
    data.update(request_patch)
    response = await taxi_discounts.post(
        'v3/get-discount', headers=common.DEFAULT_DISCOUNTS_HEADER, json=data,
    )
    assert response.status_code == 200
    response_json = response.json()
    dicounts_json = response_json['discounts']
    response_discounts = [
        dicounts_json[d]['discount_info']['discount_id'] for d in dicounts_json
    ]
    assert set(response_discounts) == set(expected_discounts)


@pytest.mark.geoareas(filename='geoareas.json')
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
    'request_patch,expected_discounts',
    [
        # only city discount
        # kiyevsky railway -> kazansky railway
        pytest.param(
            {'waypoints': [[37.566359, 55.742975], [37.661230, 55.756989]]},
            ['city_discount_econom', 'city_comfortplus'],
        ),
        # kazansky railway -> domodedovo airport
        pytest.param(
            {'waypoints': [[37.661230, 55.756989], [37.899361, 55.414867]]},
            ['to_airport_discount_econom', 'from_or_to_airport_comfortplus'],
        ),
        #  domodedovo airport -> kazansky railway
        pytest.param(
            {'waypoints': [[37.899361, 55.414867], [37.661230, 55.756989]]},
            ['from_airport_discount_econom', 'from_or_to_airport_comfortplus'],
        ),
    ],
)
@pytest.mark.config(
    DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True},
    DISCOUNTS_CHECK_TAGS_TOPIC=True,
)
async def test_airport_discounts_v3(
        taxi_discounts, request_patch, expected_discounts,
):
    data = mock_request()
    data['requested_categories'] = ['econom', 'comfortplus']
    data.update(request_patch)
    response = await taxi_discounts.post(
        'v3/get-discount', headers=common.DEFAULT_DISCOUNTS_HEADER, json=data,
    )
    assert response.status_code == 200
    response_json = response.json()
    dicounts_json = response_json['discounts']
    response_discounts = [
        dicounts_json[d]['discount_info']['discount_id'] for d in dicounts_json
    ]
    assert set(response_discounts) == set(expected_discounts)


@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
    ],
)
@pytest.mark.config(
    DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True},
    DISCOUNTS_CHECK_TAGS_TOPIC=True,
)
@pytest.mark.parametrize(
    'payment_method_id, discount_classes',
    [
        pytest.param(None, {'business'}, id='no_bin_without_method_id'),
        pytest.param(
            'family-789', {'econom', 'business'}, id='coop_account_discounts',
        ),
        pytest.param(
            'business-123',
            {'econom', 'business', 'comfortplus'},
            id='business_account_discounts',
        ),
    ],
)
async def test_v3_get_discount_coop_account(
        taxi_discounts, payment_method_id, discount_classes,
):
    request = mock_request(
        payment_info={'type': 'coop_account', 'method_id': payment_method_id},
    )

    response = await taxi_discounts.post(
        'v3/get-discount',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        json=request,
    )
    assert response.status_code == 200

    response_json = response.json()

    assert response_json['discounts'].keys() == discount_classes

    if 'econom' in discount_classes:
        assert response_json['discounts']['econom'] == expected_discount(
            calc_type='hyperbolas',
            discount_id='econom_discount_hyperbolas',
            description='discount1',
            payment_type='coop_account',
            reason='analytics',
            is_price_strikethrough=True,
            card_bin='123456',
        )
    if 'business' in discount_classes:
        assert response_json['discounts']['business'] == expected_discount(
            calc_type='table',
            discount_id='business_discount_table',
            discount_class='discount_class3',
            description='discount3',
            payment_type='coop_account',
            reason='for_all',
        )
    if 'comfortplus' in discount_classes:
        assert response_json['discounts']['comfortplus'] == expected_discount(
            calc_type='hyperbolas',
            discount_id='comfortplus_discount_wo_applications',
            description='discount5',
            discount_class='discount_class5',
            payment_type='coop_account',
            reason='for_all',
            is_price_strikethrough=True,
        )
