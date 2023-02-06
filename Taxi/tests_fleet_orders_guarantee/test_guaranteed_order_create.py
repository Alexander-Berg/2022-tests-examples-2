import datetime
import decimal

import bson
import dateutil.parser
import pytest

from tests_fleet_orders_guarantee import db_utils


def _rll_to_array(rll):
    raw_points = rll.split('~')
    string_points = [p.split(',') for p in raw_points]
    return [[float(x), float(y)] for x, y in string_points]


DEFAULT_DB_ORDER = {
    'contractor_id': 'driver_id1',
    'id': 'order_id1',
    'location_from': [13.388378, 52.519894],
    'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
    'created_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
    'client_booked_at': dateutil.parser.parse('2021-09-02T20:00:00Z'),
    'park_id': 'park_id1',
    'cancelled_at': None,
    'processed_at': None,
    'record_created_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
    'record_updated_at': dateutil.parser.parse('2021-09-02T16:00:00Z'),
    'source_park_id': None,
    'zone_id': None,
    'tariff_class': None,
    'duration_estimate': None,
    'address_from': None,
    'addresses_to': None,
    'driver_price': None,
    'comment': None,
    'distance': None,
    'durations': None,
    'event_index': 0,
}

EXPECTED_NEW_ORDER = {
    'id': 'order_id2',
    'park_id': 'park_id1',
    'contractor_id': 'driver_id2',
    'location_from': [13.388378, 52.519894],
    'address_from': 'A',
    'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
    'addresses_to': ['B', 'C'],
    'created_at': dateutil.parser.parse('2021-09-02T18:00:00Z'),
    'client_booked_at': dateutil.parser.parse('2021-09-02T22:00:00Z'),
    'cancelled_at': None,
    'processed_at': None,
    'record_created_at': dateutil.parser.parse('2021-09-02T17:00:00Z'),
    'record_updated_at': dateutil.parser.parse('2021-09-02T17:00:00Z'),
    'source_park_id': 'park_id1',
    'zone_id': 'moscow',
    'tariff_class': 'econom',
    'duration_estimate': datetime.timedelta(seconds=818),
    'driver_price': decimal.Decimal('100.70'),
    'comment': 'order comment',
    'distance': 10982,
    'durations': [
        datetime.timedelta(seconds=409),
        datetime.timedelta(seconds=409),
    ],
    'event_index': 0,
}

EXPECTED_NEW_ORDER_WITHOUT_CONTRACTOR = {
    'id': 'order_id2',
    'park_id': None,
    'contractor_id': None,
    'location_from': [13.388378, 52.519894],
    'address_from': 'A',
    'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
    'addresses_to': ['B', 'C'],
    'created_at': dateutil.parser.parse('2021-09-02T18:00:00Z'),
    'client_booked_at': dateutil.parser.parse('2021-09-02T22:00:00Z'),
    'cancelled_at': None,
    'processed_at': None,
    'record_created_at': dateutil.parser.parse('2021-09-02T17:00:00Z'),
    'record_updated_at': dateutil.parser.parse('2021-09-02T17:00:00Z'),
    'source_park_id': None,
    'zone_id': 'moscow',
    'tariff_class': 'econom',
    'duration_estimate': datetime.timedelta(seconds=818),
    'driver_price': None,
    'comment': None,
    'distance': 10982,
    'durations': [
        datetime.timedelta(seconds=409),
        datetime.timedelta(seconds=409),
    ],
    'event_index': 0,
}

EXPECTED_NEW_ORDER_AUTO_ASSIGNED = {
    'id': 'order_id2',
    'park_id': 'park_id1',
    'contractor_id': 'driver_id3',
    'location_from': [13.388378, 52.519894],
    'address_from': 'A',
    'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
    'addresses_to': ['B', 'C'],
    'created_at': dateutil.parser.parse('2021-09-02T18:00:00Z'),
    'client_booked_at': dateutil.parser.parse('2021-09-02T20:20:00Z'),
    'cancelled_at': None,
    'processed_at': None,
    'record_created_at': dateutil.parser.parse('2021-09-02T17:00:00Z'),
    'record_updated_at': dateutil.parser.parse('2021-09-02T17:00:00Z'),
    'source_park_id': 'park_id1',
    'zone_id': 'moscow',
    'tariff_class': 'econom',
    'duration_estimate': datetime.timedelta(seconds=818),
    'driver_price': None,
    'comment': None,
    'distance': 10982,
    'durations': [
        datetime.timedelta(seconds=409),
        datetime.timedelta(seconds=409),
    ],
    'event_index': 0,
}

EXPECTED_NEW_ORDER_AUTO_ASSIGNED_NO_DRIVER_FOUND = {
    'id': 'order_id3',
    'park_id': None,
    'contractor_id': None,
    'location_from': [13.388378, 52.519894],
    'address_from': 'A',
    'locations_to': [[13.396846, 52.502811]],
    'addresses_to': ['B'],
    'created_at': dateutil.parser.parse('2021-09-02T18:00:00Z'),
    'client_booked_at': dateutil.parser.parse('2021-09-02T20:20:00Z'),
    'cancelled_at': None,
    'processed_at': None,
    'record_created_at': dateutil.parser.parse('2021-09-02T17:00:00Z'),
    'record_updated_at': dateutil.parser.parse('2021-09-02T17:00:00Z'),
    'source_park_id': 'park_id1',
    'zone_id': 'moscow',
    'tariff_class': 'econom',
    'duration_estimate': datetime.timedelta(seconds=409),
    'driver_price': None,
    'comment': None,
    'distance': 5491,
    'durations': [datetime.timedelta(seconds=409)],
    'event_index': 0,
}


@pytest.mark.now('2021-09-02T17:00:00+00:00')
@pytest.mark.pgsql('fleet_orders_guarantee', files=['orders.sql'])
@pytest.mark.parametrize(
    'stq_kwargs, db_state',
    [
        (
            # new guaranteed order
            {
                'order_id': 'order_id2',
                'source_park_id': 'park_id1',
                'contractor_id': 'park_id1_driver_id2',
                'created_at': {'$date': '2021-09-02T18:00:00Z'},
                'location_from': [13.388378, 52.519894],
                'address_from': 'A',
                'locations_to': [
                    [13.396846, 52.502811],
                    [13.397283, 52.503113],
                ],
                'addresses_to': ['B', 'C'],
                'client_booked_at': {'$date': '2021-09-02T22:00:00Z'},
                'zone_id': 'moscow',
                'tariff_class': 'econom',
                'duration': 300,
                'price': 100.70,
                'comment': 'order comment',
                'event_index': 0,
            },
            [DEFAULT_DB_ORDER, EXPECTED_NEW_ORDER],
        ),
        (
            # new guaranteed order only driver_id
            {
                'order_id': 'order_id2',
                'source_park_id': 'park_id1',
                'contractor_id': 'driver_id2',
                'created_at': {'$date': '2021-09-02T18:00:00Z'},
                'location_from': [13.388378, 52.519894],
                'address_from': 'A',
                'locations_to': [
                    [13.396846, 52.502811],
                    [13.397283, 52.503113],
                ],
                'addresses_to': ['B', 'C'],
                'client_booked_at': {'$date': '2021-09-02T22:00:00Z'},
                'zone_id': 'moscow',
                'tariff_class': 'econom',
                'duration': 300,
                'price': 100.70,
                'comment': 'order comment',
                'event_index': 0,
            },
            [DEFAULT_DB_ORDER, EXPECTED_NEW_ORDER],
        ),
        (
            # new guaranteed order without contractor
            {
                'order_id': 'order_id2',
                'source_park_id': None,
                'contractor_id': None,
                'created_at': {'$date': '2021-09-02T18:00:00Z'},
                'location_from': [13.388378, 52.519894],
                'address_from': 'A',
                'locations_to': [
                    [13.396846, 52.502811],
                    [13.397283, 52.503113],
                ],
                'addresses_to': ['B', 'C'],
                'client_booked_at': {'$date': '2021-09-02T22:00:00Z'},
                'zone_id': 'moscow',
                'tariff_class': 'econom',
                'event_index': 0,
            },
            [DEFAULT_DB_ORDER, EXPECTED_NEW_ORDER_WITHOUT_CONTRACTOR],
        ),
        (
            # existing order
            {
                'order_id': 'order_id1',
                'source_park_id': 'park_id1',
                'contractor_id': 'driver_id2',
                'created_at': {'$date': '2021-09-02T18:00:00Z'},
                'location_from': [13.388378, 52.519894],
                'address_from': 'A',
                'locations_to': [
                    [13.396846, 52.502811],
                    [13.397283, 52.503113],
                ],
                'addresses_to': ['B', 'C'],
                'client_booked_at': {'$date': '2021-09-02T22:00:00Z'},
                'zone_id': 'moscow',
                'tariff_class': 'econom',
                'event_index': 0,
            },
            [DEFAULT_DB_ORDER],
        ),
        (
            # order without assignee, park with auto-assignemnt
            {
                'order_id': 'order_id2',
                'source_park_id': 'park_id1',
                'contractor_id': None,
                'created_at': {'$date': '2021-09-02T18:00:00Z'},
                'location_from': [13.388378, 52.519894],
                'address_from': 'A',
                'locations_to': [
                    [13.396846, 52.502811],
                    [13.397283, 52.503113],
                ],
                'addresses_to': ['B', 'C'],
                'client_booked_at': {'$date': '2021-09-02T20:20:00Z'},
                'zone_id': 'moscow',
                'tariff_class': 'econom',
                'event_index': 0,
            },
            [DEFAULT_DB_ORDER, EXPECTED_NEW_ORDER_AUTO_ASSIGNED],
        ),
        (
            # order without assignee, park without auto-assignemnt
            {
                'order_id': 'order_id2',
                'source_park_id': 'park_id2',
                'contractor_id': None,
                'created_at': {'$date': '2021-09-02T18:00:00Z'},
                'location_from': [13.388378, 52.519894],
                'address_from': 'A',
                'locations_to': [
                    [13.396846, 52.502811],
                    [13.397283, 52.503113],
                ],
                'addresses_to': ['B', 'C'],
                'client_booked_at': {'$date': '2021-09-02T20:20:00Z'},
                'zone_id': 'moscow',
                'tariff_class': 'econom',
                'event_index': 0,
            },
            [DEFAULT_DB_ORDER],
        ),
        (
            # order without assignee, non-existing park
            {
                'order_id': 'order_id2',
                'source_park_id': 'park_id3',
                'contractor_id': None,
                'created_at': {'$date': '2021-09-02T18:00:00Z'},
                'location_from': [13.388378, 52.519894],
                'address_from': 'A',
                'locations_to': [
                    [13.396846, 52.502811],
                    [13.397283, 52.503113],
                ],
                'addresses_to': ['B', 'C'],
                'client_booked_at': {'$date': '2021-09-02T20:20:00Z'},
                'zone_id': 'moscow',
                'tariff_class': 'econom',
                'event_index': 0,
            },
            [DEFAULT_DB_ORDER],
        ),
        (
            # order without assignee, no available drivers
            {
                'order_id': 'order_id3',
                'source_park_id': 'park_id1',
                'contractor_id': None,
                'created_at': {'$date': '2021-09-02T18:00:00Z'},
                'location_from': [13.388378, 52.519894],
                'address_from': 'A',
                'locations_to': [[13.396846, 52.502811]],
                'addresses_to': ['B'],
                'client_booked_at': {'$date': '2021-09-02T20:20:00Z'},
                'zone_id': 'moscow',
                'tariff_class': 'econom',
                'event_index': 0,
            },
            [
                DEFAULT_DB_ORDER,
                EXPECTED_NEW_ORDER_AUTO_ASSIGNED_NO_DRIVER_FOUND,
            ],
        ),
    ],
)
async def test_stq_handle(
        stq_runner, pgsql, stq_kwargs, db_state, load_binary, mockserver,
):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/handle_editing',
    )
    def _mock_handle_editing(request):
        assert request.args['order_id'] == 'order_id2'
        body = bson.BSON.decode(request.get_data())
        assert body == {}
        return {}

    @mockserver.json_handler('/client-notify/v2/push')
    def _mock_v2_push(request):
        return {'notification_id': '024a3c5cd41e4a8ca5993bafb20e346b'}

    @mockserver.json_handler('/fleet-parks/v1/parks')
    async def _mock_parks(request):
        return {
            'id': 'park_id1',
            'login': 'login',
            'is_active': True,
            'city_id': 'city',
            'locale': 'en',
            'is_billing_enabled': True,
            'is_franchising_enabled': True,
            'demo_mode': False,
            'country_id': 'country_id',
            'name': 'some park name',
            'tz_offset': 4,
            'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
        }

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _get_order_fields(request):
        assert request.args['order_id'] == stq_kwargs['order_id']

        return mockserver.make_response(
            bson.BSON.encode(
                {
                    'document': {'_id': stq_kwargs['order_id']},
                    'revision': {
                        'processing.version': 42,
                        'order.version': 42,
                    },
                },
            ),
            200,
            content_type='application/bson',
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def _set_order_fields(request):
        assert request.args['order_id'] == stq_kwargs['order_id']
        assert bson.BSON.decode(request.get_data()) == {
            'update': {
                '$set': {
                    'order.request.dispatch_type': 'forced_performer',
                    'order.request.lookup_extra.intent': 'yango',
                    'order.request.lookup_extra.performer_id': (
                        'park_id1_driver_id3'
                    ),
                },
            },
            'revision': {'order.version': 42, 'processing.version': 42},
        }
        return mockserver.make_response(
            bson.BSON.encode({}), 200, content_type='application/bson',
        )

    @mockserver.json_handler('/fleet-parks/internal/v1/order-settings')
    def _order_settings(request):
        assert request.headers['X-Park-ID'] in stq_kwargs['source_park_id']

        if request.headers['X-Park-ID'] == 'park_id3':
            return mockserver.make_response(
                status=404,
                json={
                    'code': 'PARK_NOT_FOUND',
                    'message': 'No park found for park_id non_existing_park',
                },
            )

        return {
            'is_getting_orders_from_app': True,
            'auto_assign_preorders': (
                request.headers['X-Park-ID'] in ('park_id1', 'park_id4')
            ),
        }

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_park_id',
    )
    def _profiles_retrieve_by_park_id(request):
        assert request.json['projection'] == ['data.uuid', 'data.work_status']
        assert request.json['park_id_in_set'] in [['park_id1'], ['park_id4']]
        profiles = [
            {
                'data': {'uuid': 'driver_id1', 'work_status': 'working'},
                'park_driver_profile_id': 'park_id1_driver_id1',
            },
            {
                'data': {'uuid': 'driver_id2', 'work_status': 'not_working'},
                'park_driver_profile_id': 'park_id1_driver_id2',
            },
            {
                'data': {'uuid': 'driver_id3', 'work_status': 'working'},
                'park_driver_profile_id': 'park_id1_driver_id3',
            },
        ]
        return {
            'profiles_by_park_id': [
                {
                    'park_id': 'park_id1',
                    'profiles': (
                        profiles
                        if stq_kwargs['order_id'] == 'order_id2'
                        else profiles[:2]
                    ),
                },
            ],
        }

    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        rll = _rll_to_array(request.args['rll'])
        assert rll in (
            [[13.388378, 52.519894], [13.396846, 52.502811]],
            [[13.396846, 52.502811], [13.397283, 52.503113]],
        )
        return mockserver.make_response(
            response=load_binary('maps_response.pb'),
            status=200,
            content_type='application/x-protobuf',
        )

    cursor = pgsql['fleet_orders_guarantee'].cursor()

    assert db_utils.get_orders(cursor) == [DEFAULT_DB_ORDER]

    await stq_runner.fleet_orders_guarantee_create_handling.call(
        task_id='task_id', kwargs=stq_kwargs,
    )

    if stq_kwargs['contractor_id'] is not None or (
            stq_kwargs['source_park_id'] == 'park_id1'
            and stq_kwargs['order_id'] == 'order_id2'
    ):
        assert _mock_v2_push.times_called == 1
    else:
        assert _mock_v2_push.times_called == 0

    assert db_utils.get_orders(cursor) == db_state
