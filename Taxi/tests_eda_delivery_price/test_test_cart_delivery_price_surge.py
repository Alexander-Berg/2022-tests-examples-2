import copy

import pytest

from testsuite.utils import matching

DEFAULT_REQUEST = {
    'due': '2021-03-30T12:55:00+00:00',
    'offer': '2021-03-30T12:55:00+00:00',
    'place_info': {
        'place_id': '1',
        'region_id': '2',
        'brand_id': '3',
        'position': [38.0, 57.0],
        'type': 'native',
        'currency': {'sign': '$'},
        'business_type': 'restaurant',
    },
    'user_info': {
        'position': [38.5, 57.5],
        'device_id': 'some_id',
        'user_id': 'user_id1',
        'personal_phone_id': '123',
    },
    'cart_info': {'subtotal': '250'},
    'zone_info': {'zone_type': 'pedestrian'},
    'shipping_type': 'delivery',
}

EMPTY_USER_INFO_REQUEST = dict(
    DEFAULT_REQUEST, user_info={'position': [38.5, 57.5]},
)

DEFAULT_HEADERS = {'X-Platform': 'ios_app', 'X-App-Version': '5.20.0'}


@pytest.mark.parametrize('headers', [DEFAULT_HEADERS, {}])
@pytest.mark.parametrize('requests_count', [1, 100])
async def test_cart_delivery_price_surge_start_test_200(
        taxi_eda_delivery_price,
        stq,
        headers,
        requests_count,
        check_test_results,
):
    request = {'payload': DEFAULT_REQUEST, 'requests_count': requests_count}
    start_test_response = await taxi_eda_delivery_price.post(
        'internal/v1/test-cart-delivery-price-surge',
        headers=headers,
        json=request,
    )
    assert start_test_response.status_code == 200
    assert (
        stq.eda_delivery_price_test_cart_delivery_price_surge.times_called == 1
    )
    next_call = (
        stq.eda_delivery_price_test_cart_delivery_price_surge.next_call()
    )
    test_id = next_call['id']
    kwargs = next_call['kwargs']
    del kwargs['log_extra']
    assert start_test_response.json() == {'test_id': test_id}
    assert kwargs == dict(request, headers=headers)
    await check_test_results(
        test_id,
        'internal/v1/test-cart-delivery-price-surge',
        expected_status='in_progress',
    )


async def test_cart_delivery_price_surge_start_test_400(
        taxi_eda_delivery_price, stq,
):
    payload = copy.deepcopy(DEFAULT_REQUEST)
    payload['place_info']['place_id'] = 'a'
    request = {'payload': payload, 'requests_count': 1}
    response = await taxi_eda_delivery_price.post(
        'internal/v1/test-cart-delivery-price-surge',
        headers=DEFAULT_HEADERS,
        json=request,
    )
    assert response.status_code == 400
    assert (
        not stq.eda_delivery_price_test_cart_delivery_price_surge.times_called
    )


@pytest.mark.now('2021-03-30T12:55:00+00:00')
@pytest.mark.experiments3(filename='calc_settings.json')
@pytest.mark.set_simple_pipeline_file(prefix='delivery_price_pipeline_2')
@pytest.mark.parametrize('requests_count', [1, 2])
@pytest.mark.parametrize(
    'request_body', [DEFAULT_REQUEST, EMPTY_USER_INFO_REQUEST],
)
async def test_cart_delivery_price_surge_test_results_ok(
        load_json,
        stq_runner,
        check_test_results,
        testpoint,
        request_body,
        requests_count,
):
    test_id = '1'

    await check_test_results(
        test_id,
        'internal/v1/test-cart-delivery-price-surge',
        expected_status=None,
    )

    user_info_field_values = {
        key: set()
        for key in ['user_id', 'device_id', 'yandex_uid', 'personal_phone_id']
    }
    user_infos = []

    @testpoint('cart_delivery_price_surge::user_info')
    def _request_user_info(data):
        user_infos.append(data)
        for key, value in data.items():
            if key in user_info_field_values.keys():
                user_info_field_values[key].add(str(value))

    await stq_runner.eda_delivery_price_test_cart_delivery_price_surge.call(
        task_id=test_id,
        kwargs={
            'payload': request_body,
            'requests_count': requests_count,
            'headers': DEFAULT_HEADERS,
        },
        expect_fail=False,
    )
    expected_response = load_json('expected_response.json')
    await check_test_results(
        test_id,
        'internal/v1/test-cart-delivery-price-surge',
        expected_status='finished',
        expected_responses=[expected_response] * requests_count,
        expected_errors=[],
    )
    for key, values in user_info_field_values.items():
        request_value = request_body['user_info'].get(key, None)
        if request_value is not None:
            assert values == {str(request_value)}
        else:
            assert len(values) == requests_count
            for value in values:
                assert value == matching.uuid_string


@pytest.mark.now('2021-03-30T12:55:00+00:00')
@pytest.mark.experiments3(filename='calc_settings.json')
@pytest.mark.set_simple_pipeline_file(prefix='delivery_price_pipeline_2')
@pytest.mark.parametrize(
    'request_body', [DEFAULT_REQUEST, EMPTY_USER_INFO_REQUEST],
)
@pytest.mark.parametrize('max_consequent_errors', [1, 2])
async def test_cart_delivery_price_surge_test_results_error(
        stq_runner,
        check_test_results,
        request_body,
        taxi_config,
        max_consequent_errors,
):
    taxi_config.set_values(
        {
            'EDA_DELIVERY_PRICE_TESTS': {
                'redis_ttl_minutes': 1,
                'max_consequent_errors': max_consequent_errors,
            },
        },
    )
    test_id = '1'
    requests_count = 100

    request_body = copy.deepcopy(request_body)
    request_body['place_info']['place_id'] = 'a'
    await stq_runner.eda_delivery_price_test_cart_delivery_price_surge.call(
        task_id=test_id,
        kwargs={
            'payload': request_body,
            'requests_count': requests_count,
            'headers': DEFAULT_HEADERS,
        },
        expect_fail=False,
    )
    await check_test_results(
        test_id,
        'internal/v1/test-cart-delivery-price-surge',
        expected_status='finished',
        expected_responses=[],
        expected_errors=[matching.any_string] * max_consequent_errors,
    )


async def test_cart_delivery_price_surge_test_results_invalid_request(
        stq_runner, check_test_results,
):
    test_id = '1'
    requests_count = 1

    await stq_runner.eda_delivery_price_test_cart_delivery_price_surge.call(
        task_id=test_id,
        kwargs={
            'payload': {},
            'requests_count': requests_count,
            'headers': {'X-Request-Application': 'a'},
        },
        expect_fail=False,
    )
    await check_test_results(
        test_id,
        'internal/v1/test-cart-delivery-price-surge',
        expected_status='finished',
        expected_responses=[],
        expected_errors=[
            matching.RegexString('^Failed to parse auth headers: .*$'),
            matching.RegexString('^Failed to parse request body: .*$'),
        ],
    )
