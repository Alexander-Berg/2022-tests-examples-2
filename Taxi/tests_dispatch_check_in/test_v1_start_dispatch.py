import datetime

import bson
import pytest

DEFAULT_APPLICATION = (
    'app_name=iphone,app_ver1=3,app_ver2=2,app_ver3=4,app_brand=yataxi'
)


@pytest.mark.pgsql('dispatch_check_in', files=['check_in_orders.sql'])
@pytest.mark.experiments3(filename='start_dispatch_experiments.json')
@pytest.mark.parametrize(
    'request_json, pickup_lines_config, '
    'expected_error, expected_event_args',
    [
        # case 0: pickup lines config empty
        (
            {'order_id': 'order_id1'},
            None,
            'FAILED_TO_DEDUCE_PICKUP_LINE',
            None,
        ),
        # case 1: non existing order
        ({'order_id': 'non_existing_order'}, None, 'ORDER_NOT_FOUND', None),
        # case 2: happy path with only one enabled pickup line
        (
            {'order_id': 'order_id1'},
            {
                'svo_line_1': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': [],
                    'pickup_points': [],
                },
                'svo_line_2': {
                    'enabled': False,
                    'terminal_id': 'svo',
                    'allowed_tariffs': [],
                    'pickup_points': [],
                },
            },
            None,
            {'pickup_line': 'svo_line_1', 'lookup_ttl': 300},
        ),
        # case 3: two pickup lines enabled - can't choose
        (
            {'order_id': 'order_id1'},
            {
                'svo_line_1': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': [],
                    'pickup_points': [],
                },
                'svo_line_2': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': [],
                    'pickup_points': [],
                },
            },
            'PICKUP_LINE_AMBIGUATION',
            None,
        ),
        # case 4: happy path, second pickup line enabled, ttl differs by exp
        (
            {'order_id': 'order_id1'},
            {
                'svo_line_1': {
                    'enabled': False,
                    'terminal_id': 'svo',
                    'allowed_tariffs': [],
                    'pickup_points': [],
                },
                'svo_line_2': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': [],
                    'pickup_points': [],
                },
            },
            None,
            {'pickup_line': 'svo_line_2', 'lookup_ttl': 3000},
        ),
        # case 5: happy path, pickup line set in request
        (
            {'order_id': 'order_id1', 'pickup_line_id': 'svo_line_1'},
            {
                'svo_line_1': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': [],
                    'pickup_points': [],
                },
                'svo_line_2': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': [],
                    'pickup_points': [],
                },
            },
            None,
            {'pickup_line': 'svo_line_1', 'lookup_ttl': 300},
        ),
        # case 6: happy path, pickup line set in request, but wrong terminal
        (
            {'order_id': 'order_id1', 'pickup_line_id': 'svo_line_1'},
            {
                'svo_line_1': {
                    'enabled': True,
                    'terminal_id': 'svo2',
                    'allowed_tariffs': [],
                    'pickup_points': [],
                },
                'svo_line_2': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': [],
                    'pickup_points': [],
                },
            },
            'INVALID_PICKUP_LINE',
            None,
        ),
        # case 7: happy path, with qr code check
        (
            {'order_id': 'order_id2', 'qr_code_value': '7'},
            {
                'svo_line_1': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': [],
                    'pickup_points': [],
                },
            },
            None,
            {'pickup_line': 'svo_line_1', 'lookup_ttl': 300},
        ),
        # case 8: invalid qr code value
        (
            {'order_id': 'order_id2', 'qr_code_value': '8'},
            {
                'svo_line_1': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': [],
                    'pickup_points': [],
                },
            },
            'INVALID_QR_CODE_VALUE',
            None,
        ),
        # case 9: invalid qr code value (not set)
        (
            {'order_id': 'order_id2'},
            {
                'svo_line_1': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': [],
                    'pickup_points': [],
                },
            },
            'INVALID_QR_CODE_VALUE',
            None,
        ),
        # case 10: invalid qr code value, but qr code check disabled by exp
        (
            {'order_id': 'order_id3'},
            {
                'svo_line_1': {
                    'enabled': True,
                    'terminal_id': 'svo',
                    'allowed_tariffs': [],
                    'pickup_points': [],
                },
            },
            None,
            {'pickup_line': 'svo_line_1', 'lookup_ttl': 300},
        ),
    ],
)
async def test_v1_start_dispatch(
        taxi_config,
        taxi_dispatch_check_in,
        mockserver,
        request_json,
        pickup_lines_config,
        expected_error,
        expected_event_args,
):
    @mockserver.handler(
        '/order-core/internal/processing/v1/event/start-dispatch-check-in',
    )
    async def mock_processing(request, *args, **kwargs):
        assert request.query['order_id'] == request_json['order_id']
        body = bson.BSON(request.get_data()).decode()
        assert body == {'event_arg': expected_event_args}

        data = bson.BSON.encode(
            {
                'dispatch_check_in.check_in_time': datetime.datetime(
                    2020, 2, 20, 13, 55,
                ),
            },
        )
        return mockserver.make_response(
            status=200, content_type='application/bson', response=data,
        )

    if pickup_lines_config:
        taxi_config.set(DISPATCH_CHECK_IN_PICKUP_LINES=pickup_lines_config)
    if request_json['order_id'] == 'order_id3':
        taxi_config.set(DISPATCH_CHECK_IN_QR_CODE_CHECK_ENABLED=False)

    headers = {
        'X-Yandex-Uid': '123456',
        'X-YaTaxi-UserId': 'testsuite',
        'X-Request-Application': DEFAULT_APPLICATION,
    }

    response = await taxi_dispatch_check_in.post(
        '/4.0/dispatch-check-in/v1/start-dispatch',
        json=request_json,
        headers=headers,
    )

    if expected_error:
        assert response.status == 400
        assert response.json()['code'] == expected_error
    else:
        assert response.status == 200
        assert mock_processing.times_called == 1


@pytest.mark.pgsql('dispatch_check_in', files=['check_in_orders_retry.sql'])
@pytest.mark.config(
    DISPATCH_CHECK_IN_PICKUP_LINES={
        'svo_line_1': {
            'enabled': True,
            'terminal_id': 'svo',
            'allowed_tariffs': [],
            'pickup_points': [],
            'check_in_zone_coordinates': [10, 10],
        },
    },
)
async def test_v1_start_dispatch_retry(taxi_dispatch_check_in, mockserver):
    @mockserver.handler(
        '/order-core/internal/processing/v1/event/start-dispatch-check-in',
    )
    async def mock_processing(request, *args, **kwargs):
        assert request.query['order_id'] == 'order_id1'

        data = bson.BSON.encode(
            {
                'dispatch_check_in.check_in_time': datetime.datetime(
                    2020, 2, 20, 13, 55,
                ),
            },
        )
        return mockserver.make_response(
            status=200, content_type='application/bson', response=data,
        )

    headers = {
        'X-Yandex-Uid': '123456',
        'X-YaTaxi-UserId': 'testsuite',
        'X-Request-Application': DEFAULT_APPLICATION,
    }

    response = await taxi_dispatch_check_in.post(
        '/4.0/dispatch-check-in/v1/start-dispatch',
        json={'order_id': 'order_id1'},
        headers=headers,
    )

    # check that processing is not called when there is check-in-time in db
    assert mock_processing.times_called == 0
    assert response.status == 200
