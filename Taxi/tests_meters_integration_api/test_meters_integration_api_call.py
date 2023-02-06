import bson
import pytest

from tests_meters_integration_api import utils


@pytest.mark.experiments3(filename='exp3_external_meters_settings.json')
@pytest.mark.parametrize(
    [
        'expected_order_core_get',
        'expected_driver_profiles',
        'expected_personal',
        'expected_submit_ride',
        'expected_get_ride',
        'expected_get_revision',
        'expected_order_core_set',
        'expected_driver_orders_builder',
        'expected_client_notify',
        'setcar_flag',
        'payment_type',
        'empty_ride_id',
        'empty_driver_pd_id',
        'empty_number_pd_id',
        'cannot_submit_ride',
        'expected_common_metrics',
        'expected_metrics',
    ],
    [
        (
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 206, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            'true',
            'cash',
            False,
            False,
            False,
            False,
            {'called': 1, 'enabled': 1, 'success': 1},
            {
                'called': 1,
                'enabled': 1,
                'success': 1,
                'cannot_submit_ride': 0,
                'empty_ride_id': 0,
                'empty_number_pd_id': 0,
                'empty_driver_pd_id': 0,
            },
        ),
        (
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 201, 'calls': 1},
            {'calls': 0},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            'true',
            'cash',
            False,
            False,
            False,
            False,
            {'called': 1, 'enabled': 1, 'success': 1},
            {
                'called': 1,
                'enabled': 1,
                'success': 1,
                'cannot_submit_ride': 0,
                'empty_ride_id': 0,
                'empty_number_pd_id': 0,
                'empty_driver_pd_id': 0,
            },
        ),
        (
            {'code': 400, 'calls': 1},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            None,
            'cash',
            False,
            False,
            False,
            False,
            {'called': 1, 'enabled': 0, 'success': 0},
            {
                'called': 0,
                'enabled': 0,
                'success': 0,
                'cannot_submit_ride': 0,
                'empty_ride_id': 0,
                'empty_number_pd_id': 0,
                'empty_driver_pd_id': 0,
            },
        ),
        (
            {'code': 200, 'calls': 1},
            {'code': 400, 'calls': 1},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            'false',
            'cash',
            False,
            False,
            False,
            False,
            {'called': 1, 'enabled': 1, 'success': 0},
            {
                'called': 1,
                'enabled': 1,
                'success': 0,
                'cannot_submit_ride': 0,
                'empty_ride_id': 0,
                'empty_number_pd_id': 0,
                'empty_driver_pd_id': 0,
            },
        ),
        (
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 400, 'calls': 1},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            'false',
            'cash',
            False,
            False,
            False,
            False,
            {'called': 1, 'enabled': 1, 'success': 0},
            {
                'called': 1,
                'enabled': 1,
                'success': 0,
                'cannot_submit_ride': 0,
                'empty_ride_id': 0,
                'empty_number_pd_id': 0,
                'empty_driver_pd_id': 0,
            },
        ),
        (
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 400, 'calls': 1},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            'false',
            'cash',
            False,
            False,
            False,
            False,
            {'called': 1, 'enabled': 1, 'success': 0},
            {
                'called': 1,
                'enabled': 1,
                'success': 0,
                'cannot_submit_ride': 0,
                'empty_ride_id': 0,
                'empty_number_pd_id': 0,
                'empty_driver_pd_id': 0,
            },
        ),
        (
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 206, 'calls': 1},
            {'code': 400, 'calls': 1},
            {'calls': 0},
            {'calls': 0},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            'false',
            'cash',
            False,
            False,
            False,
            False,
            {'called': 1, 'enabled': 1, 'success': 0},
            {
                'called': 1,
                'enabled': 1,
                'success': 0,
                'cannot_submit_ride': 0,
                'empty_ride_id': 0,
                'empty_number_pd_id': 0,
                'empty_driver_pd_id': 0,
            },
        ),
        (
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 206, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 400, 'calls': 1},
            {'calls': 0},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            'false',
            'cash',
            False,
            False,
            False,
            False,
            {'called': 1, 'enabled': 1, 'success': 0},
            {
                'called': 1,
                'enabled': 1,
                'success': 0,
                'cannot_submit_ride': 0,
                'empty_ride_id': 0,
                'empty_number_pd_id': 0,
                'empty_driver_pd_id': 0,
            },
        ),
        (
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 206, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 400, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            'false',
            'cash',
            False,
            False,
            False,
            False,
            {'called': 1, 'enabled': 1, 'success': 0},
            {
                'called': 1,
                'enabled': 1,
                'success': 0,
                'cannot_submit_ride': 0,
                'empty_ride_id': 0,
                'empty_number_pd_id': 0,
                'empty_driver_pd_id': 0,
            },
        ),
        (
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 206, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 400, 'calls': 1},
            {'calls': 0},
            'true',
            'cash',
            False,
            False,
            False,
            False,
            {'called': 1, 'enabled': 1, 'success': 1},
            {
                'called': 1,
                'enabled': 1,
                'success': 1,
                'cannot_submit_ride': 0,
                'empty_ride_id': 0,
                'empty_number_pd_id': 0,
                'empty_driver_pd_id': 0,
            },
        ),
        (
            {'code': 200, 'calls': 1},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            None,
            'corp',
            False,
            False,
            False,
            False,
            {'called': 1, 'enabled': 0, 'success': 0},
            {
                'called': 0,
                'enabled': 0,
                'success': 0,
                'cannot_submit_ride': 0,
                'empty_ride_id': 0,
                'empty_number_pd_id': 0,
                'empty_driver_pd_id': 0,
            },
        ),
        (
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            'false',
            'cash',
            False,
            True,
            False,
            False,
            {'called': 1, 'enabled': 1, 'success': 0},
            {
                'called': 1,
                'enabled': 1,
                'success': 0,
                'cannot_submit_ride': 0,
                'empty_ride_id': 0,
                'empty_number_pd_id': 0,
                'empty_driver_pd_id': 1,
            },
        ),
        (
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            'false',
            'cash',
            False,
            False,
            True,
            False,
            {'called': 1, 'enabled': 1, 'success': 0},
            {
                'called': 1,
                'enabled': 1,
                'success': 0,
                'cannot_submit_ride': 0,
                'empty_ride_id': 0,
                'empty_number_pd_id': 1,
                'empty_driver_pd_id': 0,
            },
        ),
        (
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 206, 'calls': 1},
            {'calls': 0},
            {'calls': 0},
            {'calls': 0},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            'false',
            'cash',
            True,
            False,
            False,
            False,
            {'called': 1, 'enabled': 1, 'success': 0},
            {
                'called': 1,
                'enabled': 1,
                'success': 0,
                'cannot_submit_ride': 0,
                'empty_ride_id': 1,
                'empty_number_pd_id': 0,
                'empty_driver_pd_id': 0,
            },
        ),
        (
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            {'code': 206, 'calls': 1},
            {'code': 200, 'calls': 3},
            {'calls': 0},
            {'calls': 0},
            {'code': 200, 'calls': 1},
            {'code': 200, 'calls': 1},
            'false',
            'cash',
            False,
            False,
            False,
            True,
            {'called': 1, 'enabled': 1, 'success': 0},
            {
                'called': 1,
                'enabled': 1,
                'success': 0,
                'cannot_submit_ride': 1,
                'empty_ride_id': 0,
                'empty_number_pd_id': 0,
                'empty_driver_pd_id': 0,
            },
        ),
    ],
    ids=[
        'ok 206',
        'ok 201',
        'bad order_core get',
        'bad driver_profiles',
        'bad personal',
        'bad submit ride',
        'bad get ride',
        'bad get revision',
        'bad order_core set',
        'bad driver_orders_builder',
        'b2b',
        'empty driver_pd_id',
        'empty number_pd_id',
        'empty ride_id',
        'cannot submit ride',
    ],
)
@pytest.mark.config(
    COMBO_CONTRACTORS_ORDER_FIELDS_DESC={
        'alternative_type_names': ['combo_outer'],
        'cargo_tariff_class_names': [],
    },
)
async def test_meters_integration_api_call(
        stq_runner,
        mockserver,
        taxi_meters_integration_api,
        taxi_meters_integration_api_monitor,
        expected_order_core_get,
        expected_driver_profiles,
        expected_personal,
        expected_submit_ride,
        expected_get_ride,
        expected_get_revision,
        expected_order_core_set,
        expected_driver_orders_builder,
        expected_client_notify,
        setcar_flag,
        payment_type,
        empty_ride_id,
        empty_driver_pd_id,
        empty_number_pd_id,
        cannot_submit_ride,
        expected_common_metrics,
        expected_metrics,
):
    order_id = utils.DEFAULT_ORDER_ID
    alias_id = utils.DEFAULT_ALIAS_ID
    park_id = utils.DEFAULT_PARK_ID
    driver_id = utils.DEFAULT_DRIVER_ID
    ride_id = utils.DEFAULT_RIDE_ID if not empty_ride_id else ''
    price = 42.24
    car_number = '1234567'
    number_pd_id = 'some_number_pd_id' if not empty_number_pd_id else ''
    personal_id_number = (
        'some_personal_id_number' if not empty_driver_pd_id else ''
    )

    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_core_get(request):
        assert request.content_type == 'application/bson'
        assert request.query['order_id'] == order_id
        assert request.query['order_id_type'] == 'exact_id'

        fields = bson.BSON.decode(request.get_data())
        if fields == {'fields': ['revision']}:
            mock_response = {
                'revision': {'processing.version': 1, 'order.version': 2},
            }
            return mockserver.make_response(
                status=expected_get_revision['code'],
                content_type='application/bson',
                response=bson.BSON.encode(mock_response),
            )
        assert bson.BSON.decode(request.get_data()) == {
            'fields': [
                'candidates.taximeter_version',
                'order.application',
                'order.calc.alternative_type',
                'order.fixed_price.price',
                'order.nz',
                'order.performer.car_number',
                'order.performer.db_id',
                'order.performer.tariff.class',
                'order.performer.uuid',
                'payment_tech.type',
                'performer.alias_id',
                'performer.candidate_index',
            ],
        }

        mock_response = {
            'document': {
                '_id': order_id,
                'candidates': [{'taximeter_version': '9.93 (7880)'}],
                'order': {
                    'application': 'yango_iphone',
                    'calc': {'alternative_type': 'combo_outer'},
                    'fixed_price': {'price': price},
                    'nz': 'tel_aviv',
                    'performer': {
                        'car_number': car_number,
                        'db_id': park_id,
                        'tariff': {'class': 'comfortplus'},
                        'uuid': driver_id,
                    },
                },
                'payment_tech': {'type': payment_type},
                'performer': {'alias_id': alias_id, 'candidate_index': 0},
            },
        }
        return mockserver.make_response(
            status=expected_order_core_get['code'],
            content_type='application/bson',
            response=bson.BSON.encode(mock_response),
        )

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        assert request.args['consumer'] == 'meters-integration-api'
        assert request.json == {
            'id_in_set': [f'{park_id}_{driver_id}'],
            'projection': ['data.identification_pd_ids'],
        }
        return mockserver.make_response(
            status=expected_driver_profiles['code'],
            json={
                'profiles': [
                    {
                        'park_driver_profile_id': f'{park_id}_{driver_id}',
                        'data': {'identification_pd_ids': [number_pd_id]},
                    },
                ],
            },
        )

    @mockserver.json_handler('/personal/v1/identifications/retrieve')
    def _mock_personal(request):
        assert request.json['id'] == number_pd_id
        return mockserver.make_response(
            status=expected_personal['code'],
            json={
                'id': number_pd_id,
                'value': f'{{"number": "{personal_id_number}"}}',
            },
        )

    @mockserver.json_handler('/monitex-meters-int-api/ride')
    def _mock_submit_ride(request):
        assert request.headers['Authorization'] == 'Bearer token'
        converted_price = price * 100.0
        assert request.json == {
            'driverId': personal_id_number,
            'vehicleLicense': car_number,
            'priceLimit': converted_price,
        }
        if expected_submit_ride['code'] == 201:
            status = 'OK'
        else:
            status = 'PENDING'
        return mockserver.make_response(
            status=expected_submit_ride['code'],
            json={'status': status, 'rideId': ride_id},
        )

    @mockserver.json_handler('/monitex-meters-int-api/rides', prefix=True)
    def _mock_get_ride(request):
        assert request.path.rsplit('/', 1)[-1] == ride_id
        assert request.headers['Authorization'] == 'Bearer token'
        state = 'IN_PROGRESS' if not cannot_submit_ride else 'PENDING'
        return mockserver.make_response(
            status=expected_get_ride['code'],
            json={
                'state': state,
                'id': ride_id,
                'driverId': personal_id_number,
            },
        )

    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def _mock_order_core_set(request):
        assert request.content_type == 'application/bson'
        assert request.query['order_id'] == order_id
        assert request.query['order_id_type'] == 'exact_id'
        assert bson.BSON.decode(request.get_data()) == {
            'update': {
                '$set': {'order.external_meter_ride_id': ride_id},
                '$inc': {'order.version': 1},
            },
            'revision': {'order.version': 2, 'processing.version': 1},
        }
        return mockserver.make_response(status=expected_order_core_set['code'])

    @mockserver.json_handler('/driver-orders-builder/v1/setcar/update-lite')
    def _mock_driver_orders_builder(request):
        assert request.query['order_id'] == alias_id
        assert request.query['park_id'] == park_id
        assert request.query['driver_profile_id'] == driver_id
        assert request.json == {
            'changes': [
                {
                    'field': 'taximeter_settings.is_external_meter_run',
                    'value': setcar_flag,
                },
            ],
        }
        return mockserver.make_response(
            status=expected_driver_orders_builder['code'],
        )

    @mockserver.json_handler('/client-notify/v2/push')
    def _mock_client_notify(request):
        assert request.json == {
            'service': 'taximeter',
            'intent': 'ForcePollingOrder',
            'client_id': f'{park_id}-{driver_id}',
            'data': {'code': 1600},
        }
        return mockserver.make_response(
            status=expected_client_notify['code'],
            json={'notification_id': 'some_id'},
        )

    await taxi_meters_integration_api.tests_control(reset_metrics=True)
    await stq_runner.meters_integration_api_call.call(
        task_id='test_task', kwargs={'order_id': order_id},
    )

    assert (
        _mock_order_core_get.times_called
        == expected_order_core_get['calls'] + expected_get_revision['calls']
    )
    assert (
        _mock_driver_profiles.times_called == expected_driver_profiles['calls']
    )
    assert _mock_personal.times_called == expected_personal['calls']
    assert _mock_submit_ride.times_called == expected_submit_ride['calls']
    assert _mock_get_ride.times_called == expected_get_ride['calls']
    assert (
        _mock_order_core_set.times_called == expected_order_core_set['calls']
    )
    assert (
        _mock_driver_orders_builder.times_called
        == expected_driver_orders_builder['calls']
    )
    assert _mock_client_notify.times_called == expected_client_notify['calls']

    common_metrics = await taxi_meters_integration_api_monitor.get_metric(
        'ride_start',
    )
    assert common_metrics == expected_common_metrics

    metrics = (
        await taxi_meters_integration_api_monitor.get_metric('monitex')
    )['ride_start']
    assert metrics == expected_metrics
