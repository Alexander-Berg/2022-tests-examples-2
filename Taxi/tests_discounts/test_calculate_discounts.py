import copy
import json

import pytest

from tests_discounts import common


DEFAULT_DISCOUNTS_REQUEST = {
    'route': [[53.000, 35.000], [55.100, 35.100]],
    'phone_id': '5714f45e98956f06baaae3d4',
    'phone_hash_id': '138aa82720f81ba2249011d',
    'personal_phone_id': 'cc6584d7a4464d63b62477f9fe1f7adb',
    'geoareas': ['moscow'],
    'geoareas_only_a': ['moscow'],
    'geoareas_only_b': ['moscow'],
    'payment_type': 'card',
    'zone': 'moscow',
    'calc_prices': [
        {'value': 100, 'class': 'econom'},
        {'value': 356, 'class': 'business'},
        {'value': 456, 'class': 'comfortplus'},
    ],
    'class_calc_prices': {'econom': 100, 'business': 356, 'comfortplus': 456},
    'min_prices': [
        {'value': 99, 'class': 'econom'},
        {'value': 199, 'class': 'business'},
        {'value': 299, 'class': 'comfortplus'},
    ],
    'class_min_prices': {'econom': 99, 'business': 199, 'comfortplus': 299},
    'surge_values_a': [{'class': 'econom', 'value': 1.2}],
    'class_surge_values_a': {'econom': 1.2},
    'completed_count': 1,
    'completed_googlepay_count': 0,
    'completed_applepay_count': 0,
    'big_first_count': 0,
    'is_from_or_to_airport': False,
    'requested_classes': ['econom'],
    'due': '2020-03-04T15:00:00Z',
    'daytime': '15:00',
    'is_workday': False,
    'experiments': [],
    'yaplus_classes': [],
}


@pytest.fixture(autouse=True)
def select_rules_request(mockserver):
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


def _find_discount_for_class(class_name, discounts_by_classes):
    return next(
        (
            item['discount']
            for item in discounts_by_classes
            if item['class'] == class_name
        ),
        None,
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
    'handler', ['v1/calculate-discount', 'v1/peek-discount'],
)
@pytest.mark.config(DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True})
async def test_day_time_restrictions(taxi_discounts, handler):
    await taxi_discounts.invalidate_caches()
    await taxi_discounts.invalidate_caches()
    data = copy.deepcopy(DEFAULT_DISCOUNTS_REQUEST)
    data['requested_classes'].append('business')
    data['requested_classes'].append('comfortplus')
    response = await taxi_discounts.post(
        handler,
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(data),
    )
    assert response.status_code == 200
    response_json = response.json()
    econom_discount = _find_discount_for_class(
        'econom', response_json['discounts'],
    )
    business_discount = _find_discount_for_class(
        'business', response_json['discounts'],
    )
    vip_discount = _find_discount_for_class(
        'comfortplus', response_json['discounts'],
    )

    assert not econom_discount
    assert business_discount
    assert vip_discount


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
    'handler', ['v1/calculate-discount', 'v1/peek-discount'],
)
@pytest.mark.config(DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True})
@pytest.mark.now('2020-03-04T15:10:000Z')
async def test_time_zone(taxi_discounts, mockserver, handler):
    await taxi_discounts.invalidate_caches()
    await taxi_discounts.invalidate_caches()
    data = copy.deepcopy(DEFAULT_DISCOUNTS_REQUEST)
    response = await taxi_discounts.post(
        handler,
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(data),
    )
    assert response.status_code == 200
    response_json = response.json()
    assert (
        response_json['discounts'][0]['discount']['description'] == 'discount3'
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
    'handler', ['v1/calculate-discount', 'v1/peek-discount'],
)
@pytest.mark.config(
    DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True},
    DISCOUNT_SEARCH_AGGLOMERATIONS_AFTER_ZONES={
        'enabled': True,
        'level': 1,
        'first_classes_match': False,
    },
)
@pytest.mark.now('2020-03-04T15:10:000Z')
async def test_find_aggl_after_zone(taxi_discounts, mockserver, handler):
    await taxi_discounts.invalidate_caches()
    await taxi_discounts.invalidate_caches()
    data = copy.deepcopy(DEFAULT_DISCOUNTS_REQUEST)
    data['requested_classes'].append('business')
    data['requested_classes'].append('comfortplus')
    response = await taxi_discounts.post(
        handler,
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(data),
    )
    assert response.status_code == 200
    response_json = response.json()
    econom_discount = _find_discount_for_class(
        'econom', response_json['discounts'],
    )
    business_discount = _find_discount_for_class(
        'business', response_json['discounts'],
    )
    vip_discount = _find_discount_for_class(
        'comfortplus', response_json['discounts'],
    )

    assert econom_discount
    assert business_discount
    assert vip_discount


@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
    ],
)
@pytest.mark.geoareas(filename='geoareas_ab.json')
@pytest.mark.parametrize(
    'handler', ['v1/calculate-discount', 'v1/peek-discount'],
)
@pytest.mark.config(DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True})
async def test_a_or_b_relation(taxi_discounts, handler):
    await taxi_discounts.invalidate_caches()
    await taxi_discounts.invalidate_caches()
    data = copy.deepcopy(DEFAULT_DISCOUNTS_REQUEST)
    data['geoareas'] = ['A', 'B']
    data['geoareas_only_a'] = ['A']
    data['geoareas_only_b'] = ['B']
    data['requested_classes'].append('business')
    data['requested_classes'].append('comfortplus')
    response = await taxi_discounts.post(
        handler,
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(data),
    )
    assert response.status_code == 200
    response_json = response.json()
    econom_discount = _find_discount_for_class(
        'econom', response_json['discounts'],
    )
    business_discount = _find_discount_for_class(
        'business', response_json['discounts'],
    )
    vip_discount = _find_discount_for_class(
        'comfortplus', response_json['discounts'],
    )

    assert econom_discount
    assert business_discount
    assert not vip_discount


@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
    ],
)
@pytest.mark.geoareas(filename='geoareas_ab.json')
@pytest.mark.parametrize(
    'handler', ['v1/calculate-discount', 'v1/peek-discount'],
)
@pytest.mark.config(DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True})
async def test_a_and_b_relation(taxi_discounts, handler):
    await taxi_discounts.invalidate_caches()
    await taxi_discounts.invalidate_caches()
    data = copy.deepcopy(DEFAULT_DISCOUNTS_REQUEST)
    data['geoareas'] = ['A', 'B']
    data['geoareas_only_a'] = ['A']
    data['geoareas_only_b'] = ['B']
    data['requested_classes'].append('business')
    data['requested_classes'].append('comfortplus')
    response = await taxi_discounts.post(
        handler,
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(data),
    )
    assert response.status_code == 200
    response_json = response.json()
    econom_discount = _find_discount_for_class(
        'econom', response_json['discounts'],
    )
    business_discount = _find_discount_for_class(
        'business', response_json['discounts'],
    )
    vip_discount = _find_discount_for_class(
        'comfortplus', response_json['discounts'],
    )

    assert econom_discount
    assert not business_discount
    assert not vip_discount


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
    DISCOUNT_SEARCH_AGGLOMERATIONS_AFTER_ZONES={
        'enabled': True,
        'level': 1,
        'first_classes_match': False,
    },
)
@pytest.mark.now('2020-03-04T15:10:000Z')
async def test_is_price_strikethrough(taxi_discounts, mockserver):
    await taxi_discounts.invalidate_caches()
    await taxi_discounts.invalidate_caches()
    data = copy.deepcopy(DEFAULT_DISCOUNTS_REQUEST)
    data['requested_classes'].append('business')
    data['requested_classes'].append('comfortplus')
    response = await taxi_discounts.post(
        'v1/calculate-discount',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(data),
    )
    assert response.status_code == 200
    response_json = response.json()
    econom_discount = _find_discount_for_class(
        'econom', response_json['discounts'],
    )
    business_discount = _find_discount_for_class(
        'business', response_json['discounts'],
    )
    vip_discount = _find_discount_for_class(
        'comfortplus', response_json['discounts'],
    )

    assert not econom_discount['is_price_strikethrough']
    assert business_discount['is_price_strikethrough']
    assert 'is_price_strikethrough' not in vip_discount


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
    DISCOUNT_SEARCH_AGGLOMERATIONS_AFTER_ZONES={
        'enabled': True,
        'level': 1,
        'first_classes_match': False,
    },
)
@pytest.mark.now('2020-03-04T15:10:000Z')
async def test_newbie_discounts(taxi_discounts, mockserver):
    data = copy.deepcopy(DEFAULT_DISCOUNTS_REQUEST)
    data['payment_type'] = 'googlepay'
    data['requested_classes'].append('business')
    data['requested_classes'].append('comfortplus')
    response = await taxi_discounts.post(
        'v1/calculate-discount',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(data),
    )

    assert response.status_code == 200
    response_json = response.json()
    econom_discount = _find_discount_for_class(
        'econom', response_json['discounts'],
    )
    business_discount = _find_discount_for_class(
        'business', response_json['discounts'],
    )
    vip_discount = _find_discount_for_class(
        'comfortplus', response_json['discounts'],
    )

    assert not econom_discount
    assert business_discount
    assert vip_discount
