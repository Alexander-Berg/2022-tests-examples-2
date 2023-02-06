import json

import bson
import pytest

from tests_meters_integration_api import utils


@pytest.mark.experiments3(filename='exp3_external_meters_settings.json')
@pytest.mark.parametrize(
    [
        'order_core_code',
        'rides_put_code',
        'rides_get_code',
        'result_code',
        'rides_calls',
        'order_price',
        'pro_price',
        'external_price',
        'payment_type',
        'user_driver_prices_differed',
        'get_price_invalid_state',
        'expected_common_metrics',
        'expected_metrics',
    ],
    [
        (
            200,
            200,
            200,
            200,
            2,
            42.24,
            42.24,
            4004,
            'cash',
            False,
            False,
            {'called': 1, 'enabled': 1, 'success': 1},
            {
                'called': 1,
                'enabled': 1,
                'success': 1,
                'fixed_price_rejected': 0,
                'get_price_invalid_state': 0,
                'invalid_external_price': 0,
                'user_driver_prices_differed': 0,
                'dry_run_enabled': 0,
            },
        ),
        (
            400,
            None,
            None,
            400,
            0,
            None,
            42.24,
            None,
            'cash',
            False,
            False,
            {'called': 1, 'enabled': 0, 'success': 0},
            {
                'called': 0,
                'enabled': 0,
                'success': 0,
                'fixed_price_rejected': 0,
                'get_price_invalid_state': 0,
                'invalid_external_price': 0,
                'user_driver_prices_differed': 0,
            },
        ),
        (
            200,
            400,
            None,
            400,
            1,
            42.24,
            42.24,
            4004,
            'cash',
            False,
            False,
            {'called': 1, 'enabled': 1, 'success': 0},
            {
                'called': 1,
                'enabled': 1,
                'success': 0,
                'fixed_price_rejected': 0,
                'get_price_invalid_state': 0,
                'invalid_external_price': 0,
                'user_driver_prices_differed': 0,
            },
        ),
        (
            200,
            200,
            400,
            400,
            2,
            42.24,
            42.24,
            4004,
            'cash',
            False,
            False,
            {'called': 1, 'enabled': 1, 'success': 0},
            {
                'called': 1,
                'enabled': 1,
                'success': 0,
                'fixed_price_rejected': 0,
                'get_price_invalid_state': 0,
                'invalid_external_price': 0,
                'user_driver_prices_differed': 0,
            },
        ),
        (
            200,
            200,
            200,
            200,
            2,
            42.24,
            42.24,
            4304,
            'cash',
            False,
            False,
            {'called': 1, 'enabled': 1, 'success': 1},
            {
                'called': 1,
                'enabled': 1,
                'success': 1,
                'fixed_price_rejected': 0,
                'get_price_invalid_state': 0,
                'invalid_external_price': 0,
                'user_driver_prices_differed': 0,
            },
        ),
        (
            200,
            None,
            None,
            400,
            0,
            42.24,
            43.24,
            4004,
            'cash',
            False,
            False,
            {'called': 1, 'enabled': 1, 'success': 0},
            {
                'called': 1,
                'enabled': 0,
                'success': 0,
                'fixed_price_rejected': 1,
                'get_price_invalid_state': 0,
                'invalid_external_price': 0,
                'user_driver_prices_differed': 0,
            },
        ),
        (
            200,
            200,
            200,
            400,
            2,
            42.24,
            42.24,
            2004,
            'cash',
            False,
            False,
            {'called': 1, 'enabled': 1, 'success': 0},
            {
                'called': 1,
                'enabled': 1,
                'success': 0,
                'fixed_price_rejected': 0,
                'get_price_invalid_state': 0,
                'invalid_external_price': 1,
                'user_driver_prices_differed': 0,
            },
        ),
        (
            200,
            None,
            None,
            400,
            0,
            42.24,
            42.24,
            4004,
            'corp',
            False,
            False,
            {'called': 1, 'enabled': 0, 'success': 0},
            {
                'called': 0,
                'enabled': 0,
                'success': 0,
                'fixed_price_rejected': 0,
                'get_price_invalid_state': 0,
                'invalid_external_price': 0,
                'user_driver_prices_differed': 0,
            },
        ),
        (
            200,
            None,
            None,
            400,
            0,
            42.24,
            42.24,
            4004,
            'cash',
            True,
            False,
            {'called': 1, 'enabled': 1, 'success': 0},
            {
                'called': 1,
                'enabled': 0,
                'success': 0,
                'fixed_price_rejected': 0,
                'get_price_invalid_state': 0,
                'invalid_external_price': 0,
                'user_driver_prices_differed': 1,
            },
        ),
        (
            200,
            200,
            200,
            400,
            2,
            42.24,
            42.24,
            4004,
            'cash',
            False,
            True,
            {'called': 1, 'enabled': 1, 'success': 0},
            {
                'called': 1,
                'enabled': 1,
                'success': 0,
                'fixed_price_rejected': 0,
                'get_price_invalid_state': 1,
                'invalid_external_price': 0,
                'user_driver_prices_differed': 0,
            },
        ),
    ],
    ids=[
        'ok lt',
        'bad order_core',
        'bad update ride',
        'bad get ride',
        'ok gt',
        'rejected fixed price',
        'invalid external price',
        'b2b',
        'user and driver prices differed',
        'invalid state in get ride',
    ],
)
@pytest.mark.config(
    COMBO_CONTRACTORS_ORDER_FIELDS_DESC={
        'alternative_type_names': ['combo_outer'],
        'cargo_tariff_class_names': [],
    },
)
async def test_finish_ride_monitex(
        taxi_meters_integration_api,
        mockserver,
        taxi_meters_integration_api_monitor,
        order_core_code,
        rides_put_code,
        rides_get_code,
        result_code,
        rides_calls,
        order_price,
        pro_price,
        external_price,
        payment_type,
        user_driver_prices_differed,
        get_price_invalid_state,
        expected_common_metrics,
        expected_metrics,
):
    order_id = utils.DEFAULT_ORDER_ID
    ride_id = utils.DEFAULT_RIDE_ID
    park_id = utils.DEFAULT_PARK_ID
    driver_id = utils.DEFAULT_DRIVER_ID

    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_core(request):
        assert request.content_type == 'application/bson'
        assert request.query['order_id'] == order_id
        assert request.query['order_id_type'] == 'alias_id'
        assert bson.BSON.decode(request.get_data()) == {
            'fields': [
                'candidates.taximeter_version',
                'order.application',
                'order.calc.alternative_type',
                'order.external_meter_ride_id',
                'order.fixed_price.price',
                'order.nz',
                'order.performer.car_number',
                'order.performer.db_id',
                'order.performer.tariff.class',
                'order.performer.uuid',
                'payment_tech.type',
                'performer.candidate_index',
            ],
        }

        if order_core_code == 200:
            mock_response = {
                'document': {
                    '_id': order_id,
                    'candidates': [{'taximeter_version': '9.93 (7880)'}],
                    'order': {
                        'application': 'yango_iphone',
                        'calc': {'alternative_type': 'combo_outer'},
                        'fixed_price': {'price': order_price},
                        'nz': 'tel_aviv',
                        'performer': {
                            'car_number': '123456',
                            'tariff': {'class': 'comfortplus'},
                            'db_id': park_id,
                            'uuid': driver_id,
                        },
                        'external_meter_ride_id': ride_id,
                    },
                    'payment_tech': {'type': payment_type},
                    'performer': {'candidate_index': 0},
                },
            }
            return mockserver.make_response(
                status=order_core_code,
                content_type='application/bson',
                response=bson.BSON.encode(mock_response),
            )
        mock_response = {'code': 'no_such_order', 'message': 'error'}
        return mockserver.make_response(
            status=order_core_code,
            content_type='application/json',
            response=json.dumps(mock_response),
        )

    @mockserver.json_handler('/monitex-meters-int-api/rides', prefix=True)
    def _mock_rides(request):
        assert request.path.rsplit('/', 1)[-1] == ride_id
        assert request.headers['Authorization'] == 'Bearer token'

        if request.method == 'PUT':
            assert request.json == {
                'state': 'COMPLETED',
                'paymentMethod': 'CASH' if payment_type == 'cash' else 'APP',
            }
            return mockserver.make_response(
                status=rides_put_code, json={'status': 'OK'},
            )

        state = 'COMPLETED' if not get_price_invalid_state else 'IN_PROGRESS'
        return mockserver.make_response(
            status=rides_get_code,
            json={
                'id': ride_id,
                'driverId': '123456789',
                'state': state,
                'totalPrice': external_price,
            },
        )

    driver_price = (
        pro_price if not user_driver_prices_differed else pro_price + 1.0
    )

    await taxi_meters_integration_api.tests_control(reset_metrics=True)
    response = await taxi_meters_integration_api.post(
        '/driver/v1/meters-integration-api/finish-ride',
        json={
            'order_id': order_id,
            'user_price': pro_price,
            'driver_price': driver_price,
        },
    )
    assert response.status == result_code
    if result_code == 200:
        expected_price = external_price / 100.0
        assert response.json() == {'price': expected_price}
    assert _mock_order_core.times_called == 1
    assert _mock_rides.times_called == rides_calls

    common_metrics = await taxi_meters_integration_api_monitor.get_metric(
        'ride_end',
    )
    assert common_metrics == expected_common_metrics

    metrics = (
        await taxi_meters_integration_api_monitor.get_metric('monitex')
    )['ride_end']
    assert metrics.items() >= expected_metrics.items()


@pytest.mark.experiments3(
    filename='exp3_external_meters_settings_optumplus.json',
)
async def test_finish_ride_optumplus(
        taxi_meters_integration_api,
        taxi_meters_integration_api_monitor,
        mockserver,
):
    order_id = utils.DEFAULT_ORDER_ID
    ride_id = utils.DEFAULT_RIDE_ID
    park_id = utils.DEFAULT_PARK_ID
    driver_id = utils.DEFAULT_DRIVER_ID
    price = 42.24
    car_number = '123456789'

    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_core(request):
        mock_response = {
            'document': {
                '_id': order_id,
                'candidates': [{'taximeter_version': '9.93 (7880)'}],
                'order': {
                    'application': 'yango_iphone',
                    'fixed_price': {'price': price},
                    'nz': 'riga',
                    'performer': {
                        'car_number': car_number,
                        'tariff': {'class': 'comfortplus'},
                        'db_id': park_id,
                        'uuid': driver_id,
                    },
                    'external_meter_ride_id': ride_id,
                },
                'payment_tech': {'type': 'cash'},
                'performer': {'candidate_index': 0},
            },
        }
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(mock_response),
        )

    @mockserver.json_handler('/optumplus-meters-int-api/submit_price')
    def _mock_submit_price(request):
        assert request.headers['Authorization'] == 'Bearer token'
        assert request.json == {'car_number': car_number, 'price': price * 100}

        return mockserver.make_response(status=200)

    await taxi_meters_integration_api.tests_control(reset_metrics=True)
    response = await taxi_meters_integration_api.post(
        '/driver/v1/meters-integration-api/finish-ride',
        json={
            'order_id': order_id,
            'user_price': price,
            'driver_price': price,
        },
    )
    assert response.status == 200
    assert _mock_order_core.times_called == 1
    assert _mock_submit_price.times_called == 1

    common_metrics = await taxi_meters_integration_api_monitor.get_metric(
        'ride_end',
    )
    assert common_metrics == {'called': 1, 'enabled': 1, 'success': 1}

    metrics = (
        await taxi_meters_integration_api_monitor.get_metric('optumplus')
    )['ride_end']
    assert metrics == {
        'called': 1,
        'enabled': 1,
        'success': 1,
        'submit_price_error': 0,
        'user_driver_prices_differed': 0,
    }


@pytest.mark.experiments3(
    filename='exp3_external_meters_settings_dry_run_on.json',
)
async def test_monitex_dry_run(
        taxi_meters_integration_api,
        mockserver,
        taxi_meters_integration_api_monitor,
):
    order_id = utils.DEFAULT_ORDER_ID
    ride_id = utils.DEFAULT_RIDE_ID
    park_id = utils.DEFAULT_PARK_ID
    driver_id = utils.DEFAULT_DRIVER_ID

    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_core(request):
        mock_response = {
            'document': {
                '_id': order_id,
                'candidates': [{'taximeter_version': '9.93 (7880)'}],
                'order': {
                    'application': 'yango_iphone',
                    'fixed_price': {'price': 25.0},
                    'nz': 'tel_aviv',
                    'performer': {
                        'car_number': '123456',
                        'tariff': {'class': 'comfortplus'},
                        'db_id': park_id,
                        'uuid': driver_id,
                    },
                    'external_meter_ride_id': ride_id,
                },
                'payment_tech': {'type': 'card'},
                'performer': {'candidate_index': 0},
            },
        }
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(mock_response),
        )

    @mockserver.json_handler('/monitex-meters-int-api/rides', prefix=True)
    def _mock_rides(request):
        if request.method == 'PUT':
            assert request.json == {
                'state': 'COMPLETED',
                'paymentMethod': 'APP',
            }
            return mockserver.make_response(status=200, json={'status': 'OK'})

        return mockserver.make_response(
            status=200,
            json={
                'id': ride_id,
                'driverId': '123456789',
                'state': 'COMPLETED',
                'totalPrice': 2400,
            },
        )

    await taxi_meters_integration_api.tests_control(reset_metrics=True)
    response = await taxi_meters_integration_api.post(
        '/driver/v1/meters-integration-api/finish-ride',
        json={'order_id': order_id, 'user_price': 25.0, 'driver_price': 25.0},
    )
    assert response.status == 400

    metrics = (
        await taxi_meters_integration_api_monitor.get_metric('monitex')
    )['ride_end']
    assert metrics.items() >= {'dry_run_enabled': 1}.items()
