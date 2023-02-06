import pytest

from tests_pricing_admin import helpers


ZERO_PRICE = {
    'boarding': 0,
    'distance': 0,
    'time': 0,
    'waiting': 0,
    'requirements': 0,
    'transit_waiting': 0,
    'destination_waiting': 0,
}

UNARY_PRICE = {
    'boarding': 1,
    'distance': 1,
    'time': 1,
    'waiting': 1,
    'requirements': 1,
    'transit_waiting': 1,
    'destination_waiting': 1,
}

ZERO_TRIP_DETAILS = {
    'total_distance': 0,
    'total_time': 0,
    'waiting_time': 0,
    'waiting_in_transit_time': 0,
    'waiting_in_destination_time': 0,
    'user_options': {},
    'user_meta': {},
}

ZERO_TRIP_DETAILS_WITH_TEST_USER_OPTIONS = {
    'total_distance': 0,
    'total_time': 0,
    'waiting_time': 0,
    'waiting_in_transit_time': 0,
    'waiting_in_destination_time': 0,
    'user_options': {'test': 42.0},
    'user_meta': {},
}

ZERO_TRIP_DETAILS_WITH_TEST_USER_META = {
    'total_distance': 0,
    'total_time': 0,
    'waiting_time': 0,
    'waiting_in_transit_time': 0,
    'waiting_in_destination_time': 0,
    'user_options': {},
    'user_meta': {'test': 42.0},
}

BOARDING_42_PRICE = {
    'boarding': 42.0,
    'distance': 0,
    'time': 0,
    'waiting': 0,
    'requirements': 0,
    'transit_waiting': 0,
    'destination_waiting': 0,
}

BACKEND_VARS = {
    'surge_params': {
        'explicit_antisurge': {'value': 0.5},
        'value': 1.0,
        'value_raw': 1.0,
        'value_smooth': 1.0,
    },
    'user_tags': [],
    'requirements': {'select': {}, 'simple': []},
    'tariff': {
        'boarding_price': 129.0,
        'minimum_price': 0.0,
        'requirement_prices': {
            'animaltransport': 150.0,
            'bicycle': 150.0,
            'check': 0.0,
            'childchair_moscow': 100.0,
            'conditioner': 0.0,
            'nosmoking': 0.0,
            'waiting_in_transit': 9.0,
            'yellowcarnumber': 0.0,
        },
        'requirements_included_one_of': ['some_fake_requirement'],
        'waiting_price': {'free_waiting_time': 180, 'price_per_minute': 9.0},
    },
    'user_data': {'has_yaplus': False},
    'category_data': {'decoupling': False, 'fixed_price': True},
    'payment_type': 'SOME_PAYMENT_TYPE',
    'experiments': [],
}

BACKEND_VARS_2 = {
    'category_data': {'decoupling': False, 'fixed_price': False},
    'requirements': {'select': {}, 'simple': []},
    'surge_params': {
        'reason': 'no',
        'value': 1.0,
        'value_raw': 1.0,
        'value_smooth': 1.0,
    },
    'tariff': {
        'boarding_price': 0.0,
        'minimum_price': 0.0,
        'requirement_prices': {},
        'waiting_price': {'free_waiting_time': 0, 'price_per_minute': 0.0},
    },
    'user_data': {'has_yaplus': False},
    'user_tags': [],
}

TRIP_DETAILS_2 = {
    'total_distance': 0,
    'total_time': 2,
    'waiting_time': 0,
    'waiting_in_transit_time': 0,
    'waiting_in_destination_time': 0,
    'user_options': {},
    'user_meta': {},
}


@pytest.mark.config(
    PRICING_DATA_PREPARER_METADATA_MAPPING={
        'meow': {'taximeter': True, 'backend': True},
        'woof': {'taximeter': True, 'backend': True},
    },
)
@pytest.mark.parametrize(
    'body, output_price, test_result, test_error, status_code, metadata',
    [
        (  # 1
            {
                'source_code': 'return 0 * ride.price;',
                'backend_variables': BACKEND_VARS,
                'trip_details': ZERO_TRIP_DETAILS,
                'initial_price': ZERO_PRICE,
            },
            ZERO_PRICE,
            True,
            None,
            200,
            {},
        ),
        (  # 2
            {
                'source_code': 'return 0 * ride.price;',
                'backend_variables': {},
                'trip_details': ZERO_TRIP_DETAILS,
                'initial_price': ZERO_PRICE,
            },
            ZERO_PRICE,
            True,
            None,
            200,
            {},
        ),
        (  # 3
            {
                'source_code': 'funny code',
                'backend_variables': BACKEND_VARS,
                'trip_details': ZERO_TRIP_DETAILS,
                'initial_price': ZERO_PRICE,
            },
            ZERO_PRICE,
            False,
            'Error while verification source_code: Parsing failed near '
            '\'funny code\'',
            200,
            {},
        ),
        (  # 4
            {
                'source_code': 'return 0 * ride.price;',
                'backend_variables': BACKEND_VARS,
                'trip_details': {},
                'initial_price': ZERO_PRICE,
            },
            ZERO_PRICE,
            True,
            None,
            400,
            {},
        ),
        (  # 5
            {
                'source_code': 'return 0 * ride.price;',
                'backend_variables': BACKEND_VARS,
                'trip_details': ZERO_TRIP_DETAILS,
                'initial_price': {},
            },
            ZERO_PRICE,
            True,
            None,
            400,
            {},
        ),
        (  # 6
            {
                'source_code': (
                    'return (*(ride.price) > 10) ? '
                    'ride.price :'
                    ' ((10 / *ride.price) * ride.price);'
                ),
                'backend_variables': {},
                'trip_details': ZERO_TRIP_DETAILS,
                'initial_price': helpers.split_price(7),
            },
            helpers.make_price(1.43),
            True,
            None,
            200,
            {},
        ),
        (  # 7
            {
                'source_code': 'return ride.price;',
                'backend_variables': BACKEND_VARS_2,
                'trip_details': TRIP_DETAILS_2,
                'initial_price': UNARY_PRICE,
            },
            UNARY_PRICE,
            True,
            None,
            200,
            {},
        ),
        (  # 8
            {
                'source_code': 'return (70 / *ride.price) * ride.price;',
                'backend_variables': BACKEND_VARS,
                'trip_details': ZERO_TRIP_DETAILS,
                'initial_price': UNARY_PRICE,
            },
            {
                'boarding': 10,
                'distance': 10,
                'time': 10,
                'waiting': 10,
                'requirements': 10,
                'transit_waiting': 10,
                'destination_waiting': 10,
            },
            True,
            None,
            200,
            {},
        ),
        (  # 9
            {
                'source_code': 'return (7 / *ride.price) * ride.price;',
                'backend_variables': BACKEND_VARS,
                'trip_details': ZERO_TRIP_DETAILS,
                'initial_price': UNARY_PRICE,
            },
            UNARY_PRICE,
            True,
            None,
            200,
            {},
        ),
        (  # 10
            {
                'source_code': (
                    'return concat({metadata=["meow": 15]},'
                    + ' (7 / *ride.price) * ride.price);'
                ),
                'backend_variables': BACKEND_VARS,
                'trip_details': ZERO_TRIP_DETAILS,
                'initial_price': UNARY_PRICE,
            },
            UNARY_PRICE,
            True,
            None,
            200,
            {'meow': 15},
        ),
        (  # 11
            {
                'source_code': (
                    'return concat({metadata=["meow": 15, "woof": 4]},'
                    + ' (7 / *ride.price) * ride.price);'
                ),
                'backend_variables': BACKEND_VARS,
                'trip_details': ZERO_TRIP_DETAILS,
                'initial_price': UNARY_PRICE,
            },
            UNARY_PRICE,
            True,
            None,
            200,
            {'meow': 15, 'woof': 4},
        ),
        (  # 12
            {
                'source_code': (
                    'return {boarding=ride.ride.user_options["test"]};'
                ),
                'backend_variables': BACKEND_VARS,
                'trip_details': ZERO_TRIP_DETAILS_WITH_TEST_USER_OPTIONS,
                'initial_price': ZERO_PRICE,
            },
            BOARDING_42_PRICE,
            True,
            None,
            200,
            {},
        ),
        (  # 13
            {
                'source_code': (
                    'using(UserMeta) '
                    + '{ return {boarding=ride.ride.user_meta["test"]};}'
                    + ' return ride.price;'
                ),
                'price_calc_version': 'latest',
                'backend_variables': BACKEND_VARS,
                'trip_details': ZERO_TRIP_DETAILS_WITH_TEST_USER_META,
                'initial_price': ZERO_PRICE,
            },
            BOARDING_42_PRICE,
            True,
            None,
            200,
            {},
        ),
    ],
    ids=[
        'OK_return_0',  # 1
        'FAIL_no_backend_variables',  # 2
        'FAIL_parse_source_code',  # 3
        '400_no_trip_details',  # 4
        '400_no_initial_price',  # 5
        'OK_ternary',  # 6
        'OK_ride.price',  # 7
        'OK_return_70',  # 8
        'OK_metadata_not_emit',  # 9
        'OK_metadata_emit',  # 10
        'OK_metadata_emit_epsent',  # 11
        'OK_with_user_options',  # 12
        'OK_with_user_meta',  # 13
    ],
)
async def test_v1_testing_run_post(
        taxi_pricing_admin,
        body,
        output_price,
        test_result,
        test_error,
        status_code,
        metadata,
):
    response = await taxi_pricing_admin.post('v1/testing/run', json=body)
    assert response.status_code == status_code

    if response.status_code == 200:
        resp = response.json()
        assert resp['test_result'] == test_result
        if not resp['test_result']:  # test failed
            assert 'test_error' in resp
            assert resp['test_error'] == test_error
        else:  # test completed
            assert resp['output_price'] == output_price
            assert resp['metadata_map'] == metadata
            stats = resp['execution_statistic']['sizes']
            assert stats['raw_ast']
            assert stats['simplified_ast_fix_price']
            assert stats['simplified_ast_taximeter_price']
            assert 'bytecode_fix_price' in stats
            assert 'bytecode_taximeter_price' in stats
