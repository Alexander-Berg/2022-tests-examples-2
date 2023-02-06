import copy
import json

import pytest

from tests_discounts import common

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from discounts_plugins.generated_tests import *  # noqa

DEFAULT_DISCOUNTS_REQUEST = {
    'route': [[53.000, 35.000], [53.100, 35.100]],
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

DEFAULT_USER_TAGS = ['dummy_tag']

# Generated via `tvmknife unittest service -s 123 -d 123321`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIexC5wwc:Q9I_85'
    'oQtOPXLu9Ds2xuQNWKPxksLjXJ4AqHbvuCulWBk5N'
    'O2CXoV4FoNn-5uN4gjYLAgq19i3AV5_hfSdGYfTph'
    'Ibm6wzagYf8nMoSTWW_7aBoY2VPHmmhJF9zDcN2Au'
    'MnuEXa5CTym5hyAM3g8lq-BfvL16ZAg7iTGOxipklY'
)


DEFAULT_ACQUIRE_RELEASE_REQUEST = {
    'phone_id': '5714f45e98956f06baaae3d4',
    'discount_id': 'limited_rides_discount',
    'order_id': 'dummy_order_id',
}


DEFAULT_DISCOUNT_REDIS_KEY = 'randomuserdiscount:tnjxn5:tnjz8m:discount1'


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


def _get_usage_stats(pgsql):
    cursor = pgsql['discounts'].cursor()
    cursor.execute(
        'SELECT phone_id,discount_id,order_id '
        'FROM discounts.discounts_usage_stats;',
    )
    result = list(cursor)
    cursor.close()
    return result


NOW = '2021-01-01T00:00:00+00:00'


async def _test_acquire_discount(request_data, taxi_discounts, pgsql):
    response = await taxi_discounts.post(
        'v1/acquire-discount',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(request_data),
    )
    assert response.status_code == 200
    result = _get_usage_stats(pgsql)
    assert len(result) == 1
    assert result[0] == (
        request_data['phone_id'],
        request_data['discount_id'],
        request_data['order_id'],
    )


async def _test_release_discount(request_data, taxi_discounts, pgsql):
    response = await taxi_discounts.post(
        'v1/release-discount',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(request_data),
    )

    assert response.status_code == 200
    result = _get_usage_stats(pgsql)
    assert not result


@pytest.mark.now(NOW)
@pytest.mark.config(DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': False})
async def test_acquire_release_discount(taxi_discounts, pgsql):
    await _test_acquire_discount(
        DEFAULT_ACQUIRE_RELEASE_REQUEST, taxi_discounts, pgsql,
    )
    await _test_release_discount(
        DEFAULT_ACQUIRE_RELEASE_REQUEST, taxi_discounts, pgsql,
    )


@pytest.mark.now(NOW)
@pytest.mark.config(DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True})
async def test_double_acquire_discount(taxi_discounts, pgsql):
    await _test_acquire_discount(
        DEFAULT_ACQUIRE_RELEASE_REQUEST, taxi_discounts, pgsql,
    )
    await _test_acquire_discount(
        DEFAULT_ACQUIRE_RELEASE_REQUEST, taxi_discounts, pgsql,
    )


@pytest.mark.now(NOW)
@pytest.mark.config(DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True})
async def test_double_release_discount(taxi_discounts, pgsql):
    await _test_release_discount(
        DEFAULT_ACQUIRE_RELEASE_REQUEST, taxi_discounts, pgsql,
    )
    await _test_release_discount(
        DEFAULT_ACQUIRE_RELEASE_REQUEST, taxi_discounts, pgsql,
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
@pytest.mark.config(
    DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True},
    DISCOUNTS_CHECK_TAGS_TOPIC=True,
)
async def test_get_discount_simple(taxi_discounts, mockserver):
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

    response = await taxi_discounts.post(
        'v1/calculate-discount',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(DEFAULT_DISCOUNTS_REQUEST),
    )
    assert response.status_code == 200
    assert mock_v2_match.has_calls
    assert mock_v2_match.times_called == 1


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
    'is_complement, config_enabled, has_discounts',
    [
        (False, False, True),
        (False, True, True),
        (True, False, True),
        (True, True, False),
    ],
)
@pytest.mark.config(DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True})
async def test_filter_cashback_by_config(
        taxi_discounts,
        taxi_config,
        is_complement,
        config_enabled,
        has_discounts,
):
    taxi_config.set_values(
        {'NO_CASHBACK_DISCOUNT_ON_COMPLEMENT_PAYMENT': config_enabled},
    )
    data = copy.deepcopy(DEFAULT_DISCOUNTS_REQUEST)
    data['client_supports'] = ['cashback']

    if is_complement:
        data['complement_payment_methods'] = [{'type': 'personal_wallet'}]

    response = await taxi_discounts.post(
        'v1/calculate-discount',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(data),
    )
    assert response.status_code == 200
    response_has_cashback_discounts = len(response.json()['discounts']) > 0
    assert response_has_cashback_discounts == has_discounts


@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
    ],
)
@pytest.mark.parametrize('suffix', ['_pg'])
@pytest.mark.parametrize(
    'handler', ['v1/calculate-discount', 'v1/peek-discount'],
)
@pytest.mark.config(DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True})
async def test_discounts_filtered_by_surge(taxi_discounts, suffix, handler):
    data = copy.deepcopy(DEFAULT_DISCOUNTS_REQUEST)
    data['requested_classes'].append('business')
    data['surge_values_a'].append({'class': 'business', 'value': 1.9})
    data['class_surge_values_a']['business'] = 1.9
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
    assert econom_discount
    assert econom_discount['description'] == 'discount1' + suffix
    assert business_discount
    assert business_discount['description'] == 'discount2' + suffix


@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
        'discounts_usage_stats.sql',
    ],
)
@pytest.mark.parametrize(
    'handler', ['v1/calculate-discount', 'v1/peek-discount'],
)
@pytest.mark.config(DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True})
async def test_limited_rides_pg(taxi_discounts, handler):
    data = copy.deepcopy(DEFAULT_DISCOUNTS_REQUEST)
    data['requested_classes'].append('business')
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
    assert not econom_discount
    assert business_discount


@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
    ],
)
@pytest.mark.config(DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True})
async def test_random_discount(taxi_discounts, redis_store):
    data = copy.deepcopy(DEFAULT_DISCOUNTS_REQUEST)
    data['requested_classes'].append('business')
    del data['experiments']
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

    discount_decision = redis_store.get(DEFAULT_DISCOUNT_REDIS_KEY)
    assert discount_decision is not None
    if discount_decision == b'y':
        assert econom_discount is not None
    else:
        assert econom_discount is None


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
async def test_discount_and_yaplus(taxi_discounts, handler):
    data = copy.deepcopy(DEFAULT_DISCOUNTS_REQUEST)
    data['requested_classes'].append('business')
    data['yaplus_classes'] = ['econom']
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
    assert econom_discount
    assert business_discount
    assert econom_discount['id'] == 'econom_discount_with_yaplus'
    assert business_discount['id'] == 'business_discount_with_yaplus'


@pytest.mark.parametrize('application_platform', ('yataxi', 'call_center'))
@pytest.mark.config(APPLICATION_MAP_DISCOUNTS={'call_center': 'callcenter'})
@pytest.mark.config(
    APPLICATION_MAP_BRAND={'kz_yataxi': 'yataxi', 'call_center': 'turboapp'},
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
async def test_discount_by_application(
        taxi_discounts, handler, application_platform,
):
    data = copy.deepcopy(DEFAULT_DISCOUNTS_REQUEST)
    data['requested_classes'].append('business')
    data['requested_classes'].append('comfortplus')
    data['application_platform'] = application_platform
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
    comfortplus_discount = _find_discount_for_class(
        'comfortplus', response_json['discounts'],
    )
    assert econom_discount
    assert econom_discount['id'] == 'econom_discount_for_yataxi'
    assert business_discount
    assert business_discount['id'] == 'business_discount_any_application'
    assert comfortplus_discount
    assert comfortplus_discount['id'] == 'comfortplus_discount_wo_applications'


@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
    ],
)
@pytest.mark.config(DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True})
async def test_discount_basic_price(taxi_discounts):
    data = copy.deepcopy(DEFAULT_DISCOUNTS_REQUEST)
    data['requested_classes'].append('business')
    data['class_basic_prices'] = {'econom': 90, 'business': 110}
    data['class_calc_prices']['econom'] = 150
    data['class_calc_prices']['business'] = 200
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
    assert econom_discount
    assert econom_discount['value'] == 0.61
    business_discount = _find_discount_for_class(
        'business', response_json['discounts'],
    )
    assert business_discount
    assert business_discount['value'] == 0.64


@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
    ],
)
@pytest.mark.config(DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True})
async def test_discount_surged_price(taxi_discounts):
    data = copy.deepcopy(DEFAULT_DISCOUNTS_REQUEST)
    data['requested_classes'].append('business')
    data['class_basic_prices'] = {'econom': 90, 'business': 110}
    data['class_calc_prices']['econom'] = 150
    data['class_calc_prices']['business'] = 100
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
    assert econom_discount
    assert econom_discount['value'] == 0.14
    business_discount = _find_discount_for_class(
        'business', response_json['discounts'],
    )
    assert business_discount
    assert business_discount['value'] == 0.35


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
async def test_discount_cashback(taxi_discounts, handler):
    data = copy.deepcopy(DEFAULT_DISCOUNTS_REQUEST)
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
    assert not econom_discount

    data['client_supports'] = ['cashback']
    data['route'] = list(({'lon': x[0], 'lat': x[1]} for x in data['route']))
    response = await taxi_discounts.post(
        'v1/get-discount',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(data),
    )
    assert response.status_code == 200
    response_json = response.json()
    econom_discount = _find_discount_for_class(
        'econom', response_json['discounts'],
    )
    assert econom_discount
    assert econom_discount['is_cashback'] is True


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
    DISCOUNTS_CHECK_TAGS_TOPIC=True,
)
async def test_discount_by_service_tags(taxi_discounts, mockserver, handler):
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

    response = await taxi_discounts.post(
        handler,
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(DEFAULT_DISCOUNTS_REQUEST),
    )
    assert response.status_code == 200
    assert mock_v2_match.has_calls
    assert mock_v2_match.times_called == 1
    response_json = response.json()
    econom_discount = _find_discount_for_class(
        'econom', response_json['discounts'],
    )
    assert econom_discount
    if handler != 'v1/peek-discount':
        assert econom_discount['value'] == 0.5


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
@pytest.mark.experiments3(filename='experiments3.json')
async def test_discount_by_tags_from_experiment(taxi_discounts, mockserver):
    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def _mock_v2_match(request):
        return {'tags': ['invalid']}

    response = await taxi_discounts.post(
        'v1/peek-discount',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(DEFAULT_DISCOUNTS_REQUEST),
    )
    assert response.status_code == 200
    response_json = response.json()
    econom_discount = _find_discount_for_class(
        'econom', response_json['discounts'],
    )
    assert econom_discount
    assert econom_discount == {
        'reason': 'analytics',
        'method': 'subvention-fix',
        'description': 'discount1',
        'id': 'discount1',
        'limited_rides': False,
    }


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
async def test_cashback_discount_without_subvention(taxi_discounts, handler):
    data = copy.deepcopy(DEFAULT_DISCOUNTS_REQUEST)
    data['requested_classes'].append('business')
    data['client_supports'] = ['cashback']
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
    assert econom_discount
    assert business_discount

    if handler == 'v1/calculate-discount':
        assert business_discount['is_cashback'] is True


@pytest.mark.config(
    USE_AGGLOMERATIONS_CACHE=True,
    DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True},
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
async def test_discount_by_agglomeration(taxi_discounts, mockserver):
    await taxi_discounts.invalidate_caches()
    await taxi_discounts.invalidate_caches()
    data = copy.deepcopy(DEFAULT_DISCOUNTS_REQUEST)
    data['route'] = list(({'lon': x[0], 'lat': x[1]} for x in data['route']))
    data['requested_classes'].append('business')
    data['class_basic_prices'] = {'econom': 90, 'business': 110}
    data['class_calc_prices']['econom'] = 150
    data['class_calc_prices']['business'] = 200
    response = await taxi_discounts.post(
        'v1/get-discount',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(data),
    )
    assert response.status_code == 200
    response_json = response.json()
    econom_discount = _find_discount_for_class(
        'econom', response_json['discounts'],
    )
    assert econom_discount
    assert econom_discount['value'] == 0.61
    business_discount = _find_discount_for_class(
        'business', response_json['discounts'],
    )
    assert business_discount
    assert business_discount['value'] == 0.64


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
    'expected_data',
    [
        # 1st agglomeration discount is not suitable
        pytest.param(
            {},
            marks=pytest.mark.config(
                DISCOUNT_SEARCH_AGGLOMERATIONS_AFTER_ZONES={
                    'enabled': True,
                    'level': 1,
                    'first_classes_match': False,
                },
            ),
        ),
        # use 2nd agglomeration discount
        pytest.param(
            {'econom': 0.67, 'business': 0.7},
            marks=pytest.mark.config(
                DISCOUNT_SEARCH_AGGLOMERATIONS_AFTER_ZONES={
                    'enabled': True,
                    'level': 2,
                    'first_classes_match': False,
                },
            ),
        ),
    ],
)
@pytest.mark.config(DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True})
async def test_discount_by_2nd_agglomeration(
        taxi_discounts, mockserver, expected_data,
):
    await taxi_discounts.invalidate_caches()
    await taxi_discounts.invalidate_caches()
    data = copy.deepcopy(DEFAULT_DISCOUNTS_REQUEST)
    data['route'] = list(({'lon': x[0], 'lat': x[1]} for x in data['route']))
    data['requested_classes'].append('business')
    data['class_basic_prices'] = {'econom': 90, 'business': 110}
    data['class_calc_prices']['econom'] = 150
    data['class_calc_prices']['business'] = 200
    response = await taxi_discounts.post(
        'v1/get-discount',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(data),
    )
    assert response.status_code == 200
    response_json = response.json()
    if not expected_data:
        assert not response_json['discounts']
    else:
        for class_, value in expected_data.items():
            class_discount = _find_discount_for_class(
                class_, response_json['discounts'],
            )
            assert class_discount
            assert class_discount['value'] == value


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
        pytest.param(
            {'route': [[37.566359, 55.742975], [37.661230, 55.756989]]},
            ['city_discount_econom', 'city_comfortplus'],
        ),
        pytest.param(
            {'route': [[37.661230, 55.756989], [37.899361, 55.414867]]},
            ['to_airport_discount_econom', 'from_or_to_airport_comfortplus'],
        ),
        pytest.param(
            {'route': [[37.899361, 55.414867], [37.661230, 55.756989]]},
            ['from_airport_discount_econom', 'from_or_to_airport_comfortplus'],
        ),
    ],
)
@pytest.mark.config(DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True})
async def test_airport_discounts(
        taxi_discounts, request_patch, expected_discounts,
):
    data = copy.deepcopy(DEFAULT_DISCOUNTS_REQUEST)
    data['requested_classes'].append('comfortplus')
    data['class_basic_prices'] = {'econom': 90, 'comfortplus': 110}
    data['class_calc_prices']['econom'] = 150
    data['class_calc_prices']['comfortplus'] = 200
    del data['is_from_or_to_airport']
    data.update(request_patch)
    response = await taxi_discounts.post(
        'v1/calculate-discount',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        data=json.dumps(data),
    )
    assert response.status_code == 200
    response_json = response.json()
    response_discounts = [
        d['discount']['id'] for d in response_json['discounts']
    ]
    assert set(response_discounts) == set(expected_discounts)
