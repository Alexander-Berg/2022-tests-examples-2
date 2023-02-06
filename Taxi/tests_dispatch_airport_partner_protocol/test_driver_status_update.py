import bson
import pytest

import tests_dispatch_airport_partner_protocol.utils as utils


@pytest.mark.pgsql(
    'dispatch_airport_partner_protocol',
    files=['parking_drivers_driver_status.sql'],
)
@pytest.mark.now('2020-02-02T00:00:00+00:00')
async def test_driver_status_update(
        taxi_dispatch_airport_partner_protocol,
        mockserver,
        pgsql,
        taxi_config,
        load_json,
):
    @mockserver.json_handler(
        'order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _get_fields(request):
        if request.query['order_id'] == 'order_id3':
            error_response = {
                'code': 'no_such_order',
                'message': 'no such order',
            }
            return mockserver.make_response(status=404, json=error_response)
        if request.query['order_id'] == 'order_id4':
            error_response = {'code': 'timeout', 'message': 'timeout'}
            return mockserver.make_response(status=500, json=error_response)
        response_fields = {
            'document': {'_id': '123', 'status': 'assigned'},
            'revision': {'processing.version': 1, 'order.version': 1},
        }
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(response_fields),
        )

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _driver_status(request):
        assert (
            sorted(request.json['driver_ids'], key=lambda d: d['park_id'])
            == [
                {'park_id': 'dbid1', 'driver_id': 'uuid1'},
                {'park_id': 'dbid2', 'driver_id': 'uuid2'},
                {'park_id': 'dbid3', 'driver_id': 'uuid3'},
                {'park_id': 'dbid4', 'driver_id': 'uuid4'},
                {'park_id': 'dbid5', 'driver_id': 'uuid5'},
                {'park_id': 'dbid6', 'driver_id': 'uuid6'},
                {'park_id': 'dbid7', 'driver_id': 'uuid7'},
                {'park_id': 'dbid8', 'driver_id': 'uuid8'},
            ]
        )
        return load_json('driver_status_response.json')

    taxi_config.set_values(
        {
            'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json'),
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_NOT_ALLOWED_TO_PARK_REASONS': (
                load_json('not_allowed_to_park_reasons.json')
            ),
        },
    )

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    await taxi_dispatch_airport_partner_protocol.run_task(
        'distlock/parking_drivers-update-scheduler-parking_lot1',
    )
    expected_result = load_json('expected_driver_status_result.json')
    await utils.compare_db_with_expected(
        pgsql,
        expected_result,
        [
            'driver_id',
            'driver_status',
            'order_id',
            'taxi_status',
            'has_suitable_order',
        ],
    )
