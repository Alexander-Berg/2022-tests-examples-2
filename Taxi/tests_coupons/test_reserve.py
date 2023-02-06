import json

import pytest

from tests_coupons import util as coupons_util
from tests_coupons.referral import util


@pytest.mark.parametrize(
    'code, order_id, service',
    [
        pytest.param('secondpromocode', 'taxi_order_id', None),
        pytest.param(
            'secondpromocode',
            'taxi_order_id',
            'taxi',
            marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)],
        ),
        pytest.param(
            'edapromic',
            'cart:order2',
            'eats',
            marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)],
        ),
    ],
)
async def test_request_parsing(taxi_coupons, mongodb, code, order_id, service):
    request = coupons_util.mock_request_reserve(
        code=code,
        service=service,
        order_id=order_id,
        check_type='short',
        zone_name='moscow',
    )
    response = await taxi_coupons.post(
        'v1/couponreserve',
        json=request,
        headers={'X-Eats-User': 'personal_phone_id=123456789'},
    )
    response_json = response.json()
    assert response_json['exists'] is True
    assert response_json['valid'] is True
    assert response_json['valid_any'] is False
    assert 'series_meta' in response_json


@pytest.mark.config(COUPONS_SERVICE_ENABLED=False)
async def test_coupons_disabled(taxi_coupons):
    response = await taxi_coupons.post(
        'v1/couponreserve', json=coupons_util.mock_request_reserve(),
    )
    assert response.status_code == 429


async def test_reserve_fail(taxi_coupons, local_services):
    request = coupons_util.mock_request_reserve(code='xcode')

    response = await taxi_coupons.post('v1/couponreserve', json=request)

    assert response.status_code == 200
    content = response.json()

    assert content['valid'] is False
    assert content['valid_any'] is False


@pytest.mark.parametrize(
    'separate_flows_enabled',
    [
        pytest.param(
            True, marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)],
        ),
        pytest.param(
            False, marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=False)],
        ),
    ],
)
@pytest.mark.parametrize(
    'code, service',
    [
        pytest.param('firstpromocode', None, id='taxi_without_service'),
        pytest.param('firstpromocode', 'taxi', id='taxi_service'),
        pytest.param('lavkapromocode', 'grocery', id='lavka_service'),
        pytest.param('onlylavka1', 'grocery', id='only_lavka_service'),
        pytest.param('eatspromocode', 'eats', id='only_eats_service'),
        pytest.param(
            'grocerynew1', 'grocery', id='only_lavka_service_with_personal',
        ),
    ],
)
@pytest.mark.now('2019-03-06T11:30:00+0300')
async def test_reserve_single(
        taxi_coupons,
        mongodb,
        local_services_card,
        code,
        service,
        separate_flows_enabled,
):
    personal_phone_id = '1234567890'
    headers = (
        {'X-Eats-User': f'personal_phone_id={personal_phone_id}'}
        if separate_flows_enabled
        else None
    )
    request = coupons_util.mock_request_reserve(
        code=code, service=service, order_id='some_order_id',
    )
    response = await taxi_coupons.post(
        'v1/couponreserve', json=request, headers=headers,
    )
    is_grocery_new_flow = code == 'grocerynew1'

    assert response.status_code == 200
    promocode = coupons_util.collection_promocode_usages2(
        mongodb, service, separate_flows_enabled, is_grocery_new_flow,
    ).find_one({'code': code})
    if separate_flows_enabled and (service == 'eats' or is_grocery_new_flow):
        assert str(promocode['personal_phone_id']) == personal_phone_id
    else:
        assert str(promocode['phone_id']) == request['phone_id']
    assert 'updated_at' in promocode


@pytest.mark.parametrize(
    'separate_flows_enabled',
    [
        pytest.param(
            True, marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)],
        ),
        pytest.param(
            False, marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=False)],
        ),
    ],
)
@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.parametrize('check_type', ['short', 'full'])
@pytest.mark.parametrize(
    'code, service, order_id, reserve_key',
    [
        pytest.param(
            'firstpromocode',
            None,  # service
            'taxi_order_id',
            'taxi_order_id',
            id='taxi_without_service',
        ),
        pytest.param(
            'firstpromocode',
            'taxi',
            'taxi_order_id',
            'taxi_order_id',
            id='taxi_service',
        ),
        pytest.param(
            'lavkapromocode',
            'grocery',
            'grocery:cart:order_id',
            'grocery_grocery:cart:order_id',
            id='lavka_service',
        ),
        pytest.param(
            'onlylavka1',
            'grocery',
            'grocery:cart:order_id',
            'grocery_grocery:cart:order_id',
            id='only lavka service',
        ),
        pytest.param(
            'lavkacode100',
            'grocery',
            'grocery:cart:order_id',
            'grocery_grocery:cart:order_id',
            id='lavka percent promocode',
        ),
        pytest.param(
            'idempotence1',
            None,  # service
            'idempotent_order',
            'idempotent_order',
            id='test couponreserve idempotence',
        ),
        pytest.param(
            'eatspromocode', 'eats', 'eats_order_id', 'eats_cart:order',
        ),
        pytest.param(
            'grocerynew1',
            'grocery',
            'grocerynew:cart:order_id',
            'grocery_grocerynew:cart:order_id',
        ),
    ],
)
async def test_reserve_idempotency(
        taxi_coupons,
        mongodb,
        local_services_card,
        check_type,
        code,
        service,
        order_id,
        reserve_key,
        separate_flows_enabled,
):
    request = coupons_util.mock_request_reserve(
        code=code, service=service, order_id=order_id, check_type=check_type,
    )
    phone_id = '1234567890'
    headers = (
        {'X-Eats-User': f'personal_phone_id={phone_id}'}
        if separate_flows_enabled
        else None
    )

    first_response = await taxi_coupons.post(
        'v1/couponreserve', json=request, headers=headers,
    )
    assert first_response.status_code == 200
    assert first_response.json()['valid']
    for _ in range(0, 3):
        response = await taxi_coupons.post(
            'v1/couponreserve', json=request, headers=headers,
        )
        assert response.status_code == first_response.status_code
        assert response.json() == first_response.json()

    is_grocery_new_flow = code == 'grocerynew1'
    assert (
        coupons_util.collection_promocode_usages(
            mongodb, service, separate_flows_enabled, is_grocery_new_flow,
        ).count({'reserve': reserve_key})
        == 1
    )

    usages2 = coupons_util.collection_promocode_usages2(
        mongodb, service, separate_flows_enabled, is_grocery_new_flow,
    ).find_one({'code': code})
    reserve_list = [x['reserve'] for x in usages2['usages']]
    assert reserve_list == [reserve_key]


@pytest.mark.parametrize(
    'separate_flows_enabled',
    [
        pytest.param(
            True, marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)],
        ),
        pytest.param(
            False, marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=False)],
        ),
    ],
)
@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME,
    files=util.PGSQL_REFERRAL,
    queries=[
        util.SQL_CLEAR_REFERRAL_CONSUMER_CONFIGS,
        util.insert_referral_consumer_config(
            zone_name='moscow', series_id='msk_referral_series',
        ),
        util.insert_referral_consumer_config(
            zone_name='moscow_percent_promocode',
            series_id='seriespercentreferral',
        ),
    ],
)
@pytest.mark.parametrize('check_type', ['full', 'short'])
@pytest.mark.parametrize(
    'code, service, order_id, content_series, series, type_,'
    + 'zone_name, reserve_key',
    [
        pytest.param(
            'firstpromocode',
            None,  # service
            'taxi_order_id',
            'first',
            'first',
            'single',
            'moscow',
            'taxi_order_id',
            id='single_promocode',
        ),
        pytest.param(
            'secondpromocode',
            'taxi',
            'taxi_order_id',
            'secondpromocode',
            'secondpromocode',
            'multi',
            'moscow',
            'taxi_order_id',
            id='multy_promocode',
        ),
        pytest.param(
            'percentreferral',
            'taxi',
            'taxi_order_id',
            '_referral_',
            'seriespercentreferral',
            'referral',
            'moscow_percent_promocode',
            'taxi_order_id',
            id='referral_promocode_percent',
        ),
        pytest.param(
            'referral2',
            'taxi',
            'taxi_order_id',
            '_referral_',
            'msk_referral_series',
            'referral',
            'moscow',
            'taxi_order_id',
            marks=pytest.mark.filldb(promocode_series='referral'),
            id='referral_promocode_value',
        ),
        pytest.param(
            'lavkapromocode',
            'grocery',
            'grocery:cart:order_id',
            'services',
            'services',
            'single',
            'moscow',
            'grocery_grocery:cart:order_id',
            id='single_promocode_lavka',
        ),
        pytest.param(
            'onlylavka1',
            'grocery',
            'grocery:cart:order_id',
            'onlylavka',
            'onlylavka',
            'single',
            'moscow',
            'grocery_grocery:cart:order_id',
            id='single_promocode_lavka',
        ),
        pytest.param(
            'eatspromocode',
            'eats',
            'eats_order_id',
            'eatspromocode2',
            'eatspromocode2',
            'single',
            'moscow',
            'eats_eats_order_id',
        ),
        pytest.param(
            'grocerynew1',
            'grocery',
            'grocerynew_order_id',
            'grocerynew',
            'grocerynew',
            'single',
            'moscow',
            'grocery_grocerynew_order_id',
        ),
    ],
)
async def test_reserve_record_usages(
        taxi_coupons,
        mongodb,
        local_services_card,
        code,
        service,
        order_id,
        series,
        content_series,
        type_,
        zone_name,
        reserve_key,
        check_type,
        separate_flows_enabled,
):
    request = coupons_util.mock_request_reserve(
        code=code,
        service=service,
        order_id=order_id,
        check_type=check_type,
        zone_name=zone_name,
    )
    headers = (
        {'X-Eats-User': 'personal_phone_id=123456789'}
        if separate_flows_enabled
        else None
    )

    response = await taxi_coupons.post(
        'v1/couponreserve', json=request, headers=headers,
    )

    assert response.status_code == 200
    content = response.json()

    assert content['series'] == content_series
    assert content['valid'] is True
    assert content['exists'] is True

    is_grocery_new_flow = code == 'grocerynew1'

    usages = coupons_util.collection_promocode_usages(
        mongodb, service, separate_flows_enabled, is_grocery_new_flow,
    ).find_one({'series_id': series})
    assert usages
    assert usages['type'] == type_
    assert usages['series_id'] == series
    assert usages['reserve'] == reserve_key

    usages2 = coupons_util.collection_promocode_usages2(
        mongodb, service, separate_flows_enabled, is_grocery_new_flow,
    ).find_one({'series_id': series})
    assert usages2
    assert usages2['series_id'] == series
    assert usages2['rides'] == 1
    assert usages2['usages'][0]['reserve'] == reserve_key


@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME,
    files=util.PGSQL_REFERRAL,
    queries=[
        util.SQL_CLEAR_REFERRAL_CONSUMER_CONFIGS,
        util.insert_referral_consumer_config(
            zone_name='moscow', series_id='seriespercentreferralonlycash',
        ),
        util.insert_referral_consumer_config(
            zone_name='moscow', series_id='seriespercentreferral',
        ),
    ],
)
@pytest.mark.parametrize(
    'code, expected_result',
    [
        pytest.param(
            'paymentmethods1',
            True,
            id='valid promo-code with a lot of payments methods(single)',
        ),
        pytest.param(
            'bizpaymentmethod1',
            False,
            id='not valid promo-code with only business payment(single)',
        ),
        pytest.param(
            'multi567',
            False,
            id='not valid promo-code with only cash payment(multi)',
        ),
        pytest.param(
            'multi123',
            True,
            id='valid promo-code with only card payment(multi)',
        ),
        pytest.param(
            'referal123',
            True,
            id='valid promo-code with credit card only(referral)',
        ),
        pytest.param(
            'referal567',
            False,
            id='not valid promo-code with only cash payment(referral)',
        ),
    ],
)
@pytest.mark.filldb(promocode_series='check_payment_in_short')
@pytest.mark.filldb(promocodes='check_payment_in_short')
async def test_reserve_check_payment_in_short(
        taxi_coupons, code, expected_result, local_services_card,
):
    request_reserve = coupons_util.mock_request_reserve(
        code=code, order_id='taxi_order_id', check_type='short',
    )
    request_check = coupons_util.mock_request_couponcheck(
        code, request_reserve['payment_info'].copy(),
    )
    check_response = await taxi_coupons.post(
        'v1/couponcheck', json=request_check,
    )
    reserve_response = await taxi_coupons.post(
        'v1/couponreserve', json=request_reserve,
    )
    assert check_response.status_code == 200
    if expected_result:
        assert check_response.json()['valid']
    else:
        assert (
            check_response.json()['error_code']
            == 'ERROR_INVALID_PAYMENT_METHOD'
        )
    assert reserve_response.status_code == 200
    assert reserve_response.json()['exists'] is True
    assert reserve_response.json()['valid'] == expected_result


@pytest.mark.parametrize(
    'code, value, limit',
    [
        pytest.param('foo123', 400, 400, id='without_usages'),
        pytest.param('foo124', 390, 390, id='without_usages_volatile_value'),
        pytest.param('validpromocode', 400, 110, id='has_usages'),
    ],
)
@pytest.mark.filldb(promocode_usages2='limits')
async def test_reserve_limit(
        taxi_coupons, local_services, mongodb, code, value, limit,
):
    request = coupons_util.mock_request_reserve(
        code=code, order_id='some_order_id', check_type='short',
    )
    response = await taxi_coupons.post('v1/couponreserve', json=request)

    content = response.json()
    assert content['valid'] is True
    assert content['value'] == value
    assert content['limit'] == limit


BILLING_SERVICE_NAME_MAP_BY_BRAND = {
    '__default__': 'unknown',
    'yataxi': 'card',
    'yango': 'card',
    'yauber': 'uber',
}
APPLICATION_MAP_BRAND = {
    '__default__': 'unknown',
    'iphone': 'yataxi',
    'yango_android': 'yango',
    'uber_iphone': 'yauber',
}


@pytest.mark.config(
    BILLING_SERVICE_NAME_MAP_BY_BRAND=BILLING_SERVICE_NAME_MAP_BY_BRAND,
    APPLICATION_MAP_BRAND=APPLICATION_MAP_BRAND,
    COUPONS_CARDSTORAGE_REQUESTS_PARAMS={
        '__default__': {
            'timeout_ms': 10000,
            'retries': 3,
            'pass_renew_after': True,
        },
        'couponreserve': {
            'timeout_ms': 15000,
            'retries': 2,
            'pass_renew_after': False,
        },
    },
)
@pytest.mark.parametrize(
    'app_name',
    ['iphone', 'yango_android', 'uber_iphone', 'mobileweb_android'],
)
async def test_cardstorage_request(
        taxi_coupons, local_services, mockserver, app_name,
):
    local_services.check_service_type(
        BILLING_SERVICE_NAME_MAP_BY_BRAND, APPLICATION_MAP_BRAND, app_name,
    )

    response = await taxi_coupons.post(
        'v1/couponreserve',
        json=coupons_util.mock_request_reserve(
            code='firstpromocode', app_name=app_name,
        ),
    )
    assert response.status_code == 200

    assert local_services.mock_cardstorage.has_calls

    coupons_util.check_cardstorage_requests(
        local_services.cardstorage_requests,
        expected_num_requests=2,
        expected_num_requests_wo_renew_after=2,
        expected_timeout_ms=15000,
    )


@pytest.mark.config(
    COUPONS_USER_AGENT_RESTRICTIONS={
        'hon30': '^.+\\(HUAWEI; (BMH|EBG)-AN10\\)$',
    },
)
@pytest.mark.parametrize(
    'code, need_check_ua',
    [
        pytest.param('prefixhonsuffix', False),
        pytest.param('prefixhon30suffix', False),
        pytest.param('hon30', False),
        pytest.param('hon30suffix', True),
    ],
)
@pytest.mark.parametrize(
    'user_agent, ua_match',
    [
        pytest.param(
            'yandex-taxi/3.151.0.121403 Android/9 (HUAWEI; CLT-L29)',
            False,
            id='other_huawei',
        ),
        pytest.param(
            'yandex-taxi/3.113.0.85658 Android/9 (OnePlus; ONEPLUS A5010)',
            False,
            id='other_android',
        ),
        pytest.param(
            'ru.yandex.taxi/9.99.9 (iPhone; x86_64; iOS 12.2; Darwin)',
            False,
            id='iphone',
        ),
        pytest.param(
            'yandex-taxi/3.151.0.121403 Android/9 (HUAWEI; BMH-AN10)',
            True,
            id='honor_30',
        ),
        pytest.param(
            'yandex-taxi/3.151.0.121403 Android/9 (HUAWEI; EBG-AN10)',
            True,
            id='honor_30_pro',
        ),
        pytest.param(None, True, id='skip check without UA'),
    ],
)
@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.skip(reason='flapping test, will be fixed in TAXIBACKEND-41551')
async def test_reserve_user_agent(
        taxi_coupons,
        mongodb,
        local_services_card,
        code,
        need_check_ua,
        user_agent,
        ua_match,
):
    request = coupons_util.mock_request_reserve(
        code=code, order_id='some_order_id',
    )
    response = await taxi_coupons.post(
        'v1/couponreserve', json=request, headers={'User-Agent': user_agent},
    )

    assert response.status_code == 200
    content = response.json()

    valid = not need_check_ua or ua_match
    assert content['valid'] is valid
    assert content['valid_any'] is False


@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.filldb(promocode_usages2='percent')
@pytest.mark.filldb(promocodes='percent')
@pytest.mark.filldb(promocode_series='percent')
@pytest.mark.parametrize(
    'coupon, percent_limit_per_trip',
    [
        pytest.param(
            'percentpertripcode', True, id='percent_limit_per_trip_true',
        ),
        pytest.param(
            'percentnotpertrip', False, id='percent_limit_per_trip_false',
        ),
        pytest.param(
            'percentemptypertrip', False, id='percent_limit_per_trip_none',
        ),
    ],
)
async def test_percent_limit_per_trip(
        mongodb,
        taxi_coupons,
        local_services_card,
        coupon,
        percent_limit_per_trip,
):
    request = coupons_util.mock_request_reserve(
        code=coupon, order_id='some_order_id',
    )
    response = await taxi_coupons.post('v1/couponreserve', json=request)
    assert response.status_code == 200

    response = response.json()
    # if coupon is percent_limit_per_trip it means the value is const = 400
    # else the value is decreasing so it should be 300(have cost_usage = 100)
    assert (
        response['limit'] == 400
        if percent_limit_per_trip
        else response['limit'] == 300
    )


def get_metric_safe(path, metrics):
    data = metrics
    for level in path.split('.'):
        data = data.get(level, {})
    return 0 if data == {} else data


@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.parametrize('check_type', ['short', 'full'])
async def test_check_type_metrics(
        taxi_coupons, taxi_coupons_monitor, local_services_card, check_type,
):
    metrics = await taxi_coupons_monitor.get_metrics()
    init_metric_value = get_metric_safe(
        f'couponreserve.check-type.{check_type}', metrics,
    )

    request = coupons_util.mock_request_reserve(
        code='firstpromocode',
        service='taxi',
        order_id='taxi_order_id',
        check_type=check_type,
    )
    await taxi_coupons.post('v1/couponreserve', json=request)

    metrics = await taxi_coupons_monitor.get_metrics()
    final_metric_value = get_metric_safe(
        f'couponreserve.check-type.{check_type}', metrics,
    )
    assert final_metric_value - init_metric_value == 1


@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.config(
    COUPONS_USAGES_EXTENDED_ANTIFRAUD_USER_IDS=['device_id', 'card_id'],
)
@pytest.mark.filldb(promocode_series='extended_antifraud')
@pytest.mark.parametrize('check_type', ['full', 'short'])
@pytest.mark.parametrize(
    'valid_reserve, expected_rides',
    [
        pytest.param(True, 1, id='no_previous_reserves'),
        pytest.param(
            True,
            2,
            id='partial_reserve_by_phone',
            marks=pytest.mark.filldb(promocode_usages2='part_usage_phone'),
        ),
        pytest.param(
            True,
            2,
            id='partial_reserve_by_device',
            marks=pytest.mark.filldb(promocode_usages2='part_usage_device'),
        ),
        pytest.param(
            True,
            2,
            id='partial_reserve_by_card',
            marks=pytest.mark.filldb(promocode_usages2='part_usage_card'),
        ),
        pytest.param(
            True,
            3,
            id='partial_reserve_by_phone_device',
            marks=pytest.mark.filldb(
                promocode_usages2='part_usage_phone_device',
            ),
        ),
        pytest.param(
            False,
            None,
            id='full_reserve_by_phone',
            marks=pytest.mark.filldb(promocode_usages2='full_usage_phone'),
        ),
        pytest.param(
            False,
            None,
            id='full_reserve_by_device',
            marks=pytest.mark.filldb(promocode_usages2='full_usage_device'),
        ),
        pytest.param(
            False,
            None,
            id='full_reserve_by_card',
            marks=pytest.mark.filldb(promocode_usages2='full_usage_card'),
        ),
        pytest.param(
            False,
            None,
            id='full_reserve_by_phone_device_card',
            marks=pytest.mark.filldb(
                promocode_usages2='full_usage_phone_device_card',
            ),
        ),
    ],
)
@pytest.mark.skip(reason='flapping test, will be fixed in TAXIBACKEND-41551')
async def test_reserve_usages_extended_antifraud(
        taxi_coupons,
        mongodb,
        local_services_card,
        check_type,
        valid_reserve,
        expected_rides,
):
    # multiuser promocode
    code = 'secondpromocode'

    order_id = 'taxi_order_id'

    request = coupons_util.mock_request_reserve(
        code=code, order_id=order_id, check_type=check_type,
    )
    response = await taxi_coupons.post('v1/couponreserve', json=request)

    assert response.status_code == 200

    content = response.json()
    assert content['valid'] is valid_reserve
    assert content['exists'] is True
    usages = list(mongodb.promocode_usages2.find({'code': code}).sort('_id'))
    if valid_reserve:
        total_rides = sum(usage['rides'] for usage in usages)
        assert total_rides == expected_rides

        # In case of multiple usages docs reserve will be added
        # to the first one according to the sort order by _id field.
        usage = usages[0]
        assert usage['usages'][-1]['reserve'] == order_id


@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.parametrize('code', ['firstpromocode', 'secondpromocode'])
async def test_reserve_additional_params(
        taxi_coupons, mongodb, local_services_card, code,
):
    def check_response_body(response_body):
        series = response_body['series']
        promocode_info = mongodb.promocode_series.find_one({'_id': series})
        assert response_body['currency_code'] == promocode_info['currency']
        assert response_body['exists'] is True
        assert response_body['valid'] is True
        assert response_body['valid_any'] is False
        assert response_body['value'] == promocode_info['value']
        assert (
            coupons_util.utc_datetime_from_str(response_body['expire_at'])
            == promocode_info['finish']
        )
        assert response_body['descr'] == promocode_info['descr']
        if 'external_meta' in promocode_info:
            assert (
                response_body['series_meta'] == promocode_info['external_meta']
            )

    request = coupons_util.mock_request_reserve(
        code=code, order_id='some_order_id',
    )
    response = await taxi_coupons.post('v1/couponreserve', json=request)
    assert response.status_code == 200
    promocode = coupons_util.collection_promocode_usages2(
        mongodb, None, False,
    ).find_one({'code': code})
    check_response_body(response.json())
    assert str(promocode['phone_id']) == request['phone_id']
    assert 'updated_at' in promocode


@pytest.mark.config(COUPONS_EXTERNAL_VALIDATION_SERVICES=['eats'])
@pytest.mark.parametrize(
    'pass_error',
    [
        pytest.param(False, id='do_not_pass_error'),
        pytest.param(
            True,
            marks=pytest.mark.config(
                COUPONS_EXTERNAL_SERVICES_FORWARD_ERRORS={
                    'forward_codes_for_services': ['eats'],
                    'forward_description_for_services': ['eats'],
                },
            ),
            id='pass_error',
        ),
    ],
)
@pytest.mark.parametrize(
    'force_empty_code_and_details',
    [
        pytest.param(False, id='fill_code_and_details'),
        pytest.param(
            True,
            marks=pytest.mark.config(
                COUPONS_COUPONRESERVE_BUILDER_SETTING={
                    'empty_error_code_and_details': True,
                },
            ),
            id='force_empty_code_and_details',
        ),
    ],
)
async def test_pass_eats_coupons_errors(
        taxi_coupons,
        mockserver,
        local_services,
        local_services_card,
        pass_error,
        force_empty_code_and_details,
):
    error_code = 'SOME_ERROR'
    error_description = 'Some error from eats validator'

    @mockserver.json_handler('/eats-coupons/internal/v1/coupons/validate')
    def mock_eats_coupons_validate(req):
        assert req.json['source_handler'] == 'reserve'
        return mockserver.make_response(
            json.dumps(
                {
                    'valid': False,
                    'valid_any': False,
                    'descriptions': [],
                    'details': [],
                    'error_code': error_code,
                    'error_description': error_description,
                },
            ),
            status=200,
        )

    request = coupons_util.mock_request_reserve(
        code='edapromic2', order_id='some_order_id', service='eats',
    )
    response = await taxi_coupons.post('v1/couponreserve', json=request)

    assert mock_eats_coupons_validate.times_called == 1

    resp_json = response.json()
    assert not resp_json['valid']
    if force_empty_code_and_details:
        assert 'error_code' not in resp_json
        assert 'details' not in resp_json
    else:
        if pass_error:
            assert resp_json['error_code'] == error_code
            assert resp_json['details'] == [error_description]
        else:
            assert (
                resp_json['error_code'] == 'ERROR_EXTERNAL_VALIDATION_FAILED'
            )
            assert resp_json['details'] == ['Invalid code']
