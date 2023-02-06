import pytest


CONFIG_REQUIREMENTS_SECTION = {
    'patterns': ['req:([\\w|\\.]+):(price|per_unit|included|count)'],
    'tanker': {'keyset': 'requirements_keyset', 'key_prefix': 'prefix.'},
}

CONSUMER_SERVICES_SECTION = {
    'patterns': [
        'waiting_price',
        'waiting_in_transit_price',
        'waiting_in_destination_price',
        'base_price.boarding',
        'base_price.time',
        'base_price.distance',
        'base_price',
        'waiting_delta',
        'waiting_in_destination_delta',
        'coupon_value',
        'surge_delta',
        'use_cost_includes_coupon',
    ],
    'tanker': {'keyset': 'services_keyset', 'key_suffix': '.suffix'},
}

UNKNOWN_CONSUMER_SERVICES_SECTION = {
    'patterns': [
        'waiting_price',
        'waiting_in_transit_price',
        'waiting_in_destination_price',
    ],
    'tanker': {'keyset': 'services_keyset', 'key_suffix': '.suffix'},
}


@pytest.mark.parametrize(
    'order_id, consumer, expected_code, expected_response',
    [
        ('unexistent_order', '', 404, 'order_not_found_response.json'),
        (
            'without_current_prices',
            '',
            404,
            'current_prices_not_found_response.json',
        ),
        (
            'without_final_cost_meta',
            '',
            404,
            'final_cost_meta_not_found_response.json',
        ),
        ('without_user_meta', '', 500, None),
        ('without_driver_meta', '', 500, None),
        ('with_invalid_meta', '', 500, None),
        ('with_empty_meta', '', 200, 'empty_meta_response.json'),
        (
            'good_order',
            'unknown_consumer',
            200,
            'unknown_consumer_response.json',
        ),
        ('good_order', 'consumer', 200, 'with_consumer_response.json'),
    ],
    ids=[
        'order_not_found',  # 0
        'current_prices_not_found',  # 1
        'final_cost_meta_not_found',  # 2
        'user_meta_not_found',  # 3
        'driver_meta_not_found',  # 4
        'invalid_meta_format',  # 5
        'empty_meta',  # 6
        'unknown_consumer',  # 7
        'with_consumer',  # 8
    ],
)
@pytest.mark.config(
    PRICING_DATA_PREPARER_DETAILING_BY_CONSUMERS={
        '__default__': {
            'requirements': CONFIG_REQUIREMENTS_SECTION,
            'services': UNKNOWN_CONSUMER_SERVICES_SECTION,
        },
        'consumer': {
            'requirements': CONFIG_REQUIREMENTS_SECTION,
            'services': CONSUMER_SERVICES_SECTION,
        },
    },
)
@pytest.mark.now('2021-01-01 00:00:00.0000+03')
async def test_v1_fetch_final_price_details(
        taxi_pricing_admin,
        order_id,
        consumer,
        expected_code,
        expected_response,
        load_json,
        order_archive_mock,
):
    def sorted_details(details):
        if 'services' in details:
            details['services'] = sorted(
                details['services'], key=lambda el: el['name'],
            )
        if 'requirements' in details:
            details['requirements'] = sorted(
                details['requirements'], key=lambda el: el['name'],
            )
        return details

    order_archive_mock.set_order_proc(load_json('db_order_proc.json'))

    request = {'consumer': consumer}
    response = await taxi_pricing_admin.post(
        'v1/fetch_final_price_details',
        params={'order_id': order_id},
        json=request,
    )

    assert response.status_code == expected_code
    if response.status_code != 500:
        expected_json = load_json(expected_response)
        response_json = response.json()
        if 'code' not in response_json:
            response_json['user']['details'] = sorted_details(
                response_json['user']['details'],
            )
            response_json['driver']['details'] = sorted_details(
                response_json['driver']['details'],
            )
        assert response_json == expected_json
