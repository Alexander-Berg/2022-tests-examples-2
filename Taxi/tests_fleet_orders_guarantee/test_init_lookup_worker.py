import dateutil.parser
import pytest

from tests_fleet_orders_guarantee import db_utils


ORDERS_BEFORE = [
    {
        'id': 'order_id1',
        'park_id': 'park_id1',
        'contractor_id': 'driver_id1',
        'created_at': dateutil.parser.parse('2021-09-02T15:59:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-09-02T20:00:00Z'),
        'processed_at': None,
        'cancelled_at': None,
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
    },
    {
        'id': 'order_id2',
        'park_id': 'park_id2',
        'contractor_id': 'driver_id2',
        'created_at': dateutil.parser.parse('2021-09-02T16:59:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-09-02T22:10:00Z'),
        'processed_at': dateutil.parser.parse('2021-09-02T21:10:00Z'),
        'cancelled_at': None,
        'record_created_at': dateutil.parser.parse('2021-09-02T17:00:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-09-02T17:00:00Z'),
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
    },
    {
        'id': 'order_id3',
        'park_id': 'park_id3',
        'contractor_id': 'driver_id3',
        'created_at': dateutil.parser.parse('2021-09-02T17:09:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-09-02T22:05:00Z'),
        'processed_at': None,
        'cancelled_at': None,
        'record_created_at': dateutil.parser.parse('2021-09-02T17:10:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-09-02T17:10:00Z'),
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
    },
    {
        'id': 'order_id4',
        'park_id': 'park_id4',
        'contractor_id': 'driver_id4',
        'created_at': dateutil.parser.parse('2021-09-02T17:10:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-09-02T22:21:00Z'),
        'processed_at': None,
        'cancelled_at': None,
        'record_created_at': dateutil.parser.parse('2021-09-02T17:11:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-09-02T17:11:00Z'),
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
    },
    {
        'id': 'order_id5',
        'park_id': None,
        'contractor_id': None,
        'created_at': dateutil.parser.parse('2021-09-02T17:10:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-09-02T22:21:00Z'),
        'processed_at': None,
        'cancelled_at': None,
        'record_created_at': dateutil.parser.parse('2021-09-02T17:11:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-09-02T17:11:00Z'),
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
    },
]

ORDERS_AFTER = [
    {
        'id': 'order_id1',
        'park_id': 'park_id1',
        'contractor_id': 'driver_id1',
        'created_at': dateutil.parser.parse('2021-09-02T15:59:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-09-02T20:00:00Z'),
        'processed_at': None,
        'cancelled_at': None,
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
    },
    {
        'id': 'order_id2',
        'park_id': 'park_id2',
        'contractor_id': 'driver_id2',
        'created_at': dateutil.parser.parse('2021-09-02T16:59:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-09-02T22:10:00Z'),
        'processed_at': dateutil.parser.parse('2021-09-02T21:10:00Z'),
        'cancelled_at': None,
        'record_created_at': dateutil.parser.parse('2021-09-02T17:00:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-09-02T17:00:00Z'),
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
    },
    {
        'id': 'order_id3',
        'park_id': 'park_id3',
        'contractor_id': 'driver_id3',
        'created_at': dateutil.parser.parse('2021-09-02T17:09:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-09-02T22:05:00Z'),
        'processed_at': dateutil.parser.parse('2021-09-02T22:00:00Z'),
        'cancelled_at': None,
        'record_created_at': dateutil.parser.parse('2021-09-02T17:10:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-09-02T22:00:00Z'),
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
    },
    {
        'id': 'order_id4',
        'park_id': 'park_id4',
        'contractor_id': 'driver_id4',
        'created_at': dateutil.parser.parse('2021-09-02T17:10:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-09-02T22:21:00Z'),
        'processed_at': dateutil.parser.parse('2021-09-02T22:00:00Z'),
        'cancelled_at': None,
        'record_created_at': dateutil.parser.parse('2021-09-02T17:11:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-09-02T22:00:00Z'),
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
    },
    {
        'id': 'order_id5',
        'park_id': None,
        'contractor_id': None,
        'created_at': dateutil.parser.parse('2021-09-02T17:10:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-09-02T22:21:00Z'),
        'processed_at': None,
        'cancelled_at': None,
        'record_created_at': dateutil.parser.parse('2021-09-02T17:11:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-09-02T17:11:00Z'),
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
    },
]


class StartLookupContext:
    def __init__(self):
        self.response = None
        self.expected_order_ids = []
        self.failing = False
        self.call_times = 0

    def set_response(self, response):
        self.response = response

    def set_expected_requests(self, expected_order_ids):
        self.expected_order_ids = expected_order_ids

    def set_failing(self, failing):
        self.failing = failing


@pytest.fixture(name='mock_order_core')
def _mock_personal(mockserver):

    context = StartLookupContext()

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/start-lookup',
    )
    def _phones_retrieve(request):
        context.call_times += 1

        if context.failing:
            return mockserver.make_response('fail', status=500)

        assert request.args['order_id'] in context.expected_order_ids
        return context.response

    return context


@pytest.mark.now('2021-09-02T22:00:00')
@pytest.mark.pgsql('fleet_orders_guarantee', files=['orders.sql'])
@pytest.mark.config(
    FLEET_ORDERS_GUARANTEE_INIT_LOOKUP_SETTINGS={
        'job_period_seconds': 60,
        'init_time_minutes': 60,
        'routing_enabled': False,
        'router_type': 'yandex',
        'duration_factor': 1.0,
        'extra_duration_minutes': 10,
        'notify_time_minutes': 5,
    },
)
async def test_job(
        testpoint, pgsql, taxi_fleet_orders_guarantee, mock_order_core,
):
    @testpoint('lookup-init-worker-finished')
    def handle_finished(arg):
        pass

    cursor = pgsql['fleet_orders_guarantee'].cursor()
    mock_order_core.set_expected_requests(['order_id3', 'order_id4'])

    assert db_utils.get_orders(cursor) == ORDERS_BEFORE

    await taxi_fleet_orders_guarantee.run_distlock_task('lookup-init-task')

    result = handle_finished.next_call()
    assert result == {'arg': ['order_id3', 'order_id4']}

    assert db_utils.get_orders(cursor) == ORDERS_AFTER
    assert mock_order_core.call_times == 2


DRIVER_POSITION = {
    'direction': 0,
    'lat': 37.5783920288086,
    'lon': -55.7350642053194,
    'speed': 0,
    'timestamp': 100,
}


def _rll_to_array(rll):
    raw_points = rll.split('~')
    string_points = [p.split(',') for p in raw_points]
    return [[float(x), float(y)] for x, y in string_points]


@pytest.fixture(name='mock_routes')
def mock_maps_router(mockserver, load_binary):
    class RoutesContext:
        def __init__(self):
            self.geopoints = []
            self.v2_route_use_count = 0

        def set_geopoints(self, geopoints):
            self.geopoints = geopoints

    context = RoutesContext()

    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        context.v2_route_use_count += 1
        rll = _rll_to_array(request.args['rll'])
        assert rll in context.geopoints
        return mockserver.make_response(
            response=load_binary('maps_response.pb'),
            status=200,
            content_type='application/x-protobuf',
        )

    return context


ORDERS_AFTER_IF_ROUTING = [
    {
        'id': 'order_id1',
        'park_id': 'park_id1',
        'contractor_id': 'driver_id1',
        'created_at': dateutil.parser.parse('2021-09-02T15:59:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-09-02T20:00:00Z'),
        'processed_at': None,
        'cancelled_at': None,
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
    },
    {
        'id': 'order_id2',
        'park_id': 'park_id2',
        'contractor_id': 'driver_id2',
        'created_at': dateutil.parser.parse('2021-09-02T16:59:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-09-02T22:10:00Z'),
        'processed_at': dateutil.parser.parse('2021-09-02T21:10:00Z'),
        'cancelled_at': None,
        'record_created_at': dateutil.parser.parse('2021-09-02T17:00:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-09-02T17:00:00Z'),
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
    },
    {
        'id': 'order_id3',
        'park_id': 'park_id3',
        'contractor_id': 'driver_id3',
        'created_at': dateutil.parser.parse('2021-09-02T17:09:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-09-02T22:05:00Z'),
        'processed_at': dateutil.parser.parse('2021-09-02T22:00:00Z'),
        'cancelled_at': None,
        'record_created_at': dateutil.parser.parse('2021-09-02T17:10:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-09-02T22:00:00Z'),
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
    },
    {
        'id': 'order_id4',
        'park_id': 'park_id4',
        'contractor_id': 'driver_id4',
        'created_at': dateutil.parser.parse('2021-09-02T17:10:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-09-02T22:21:00Z'),
        'processed_at': None,
        'cancelled_at': None,
        'record_created_at': dateutil.parser.parse('2021-09-02T17:11:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-09-02T17:11:00Z'),
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
    },
    {
        'id': 'order_id5',
        'park_id': None,
        'contractor_id': None,
        'created_at': dateutil.parser.parse('2021-09-02T17:10:00Z'),
        'location_from': [13.388378, 52.519894],
        'locations_to': [[13.396846, 52.502811], [13.397283, 52.503113]],
        'client_booked_at': dateutil.parser.parse('2021-09-02T22:21:00Z'),
        'processed_at': None,
        'cancelled_at': None,
        'record_created_at': dateutil.parser.parse('2021-09-02T17:11:00Z'),
        'record_updated_at': dateutil.parser.parse('2021-09-02T17:11:00Z'),
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
    },
]


@pytest.mark.now('2021-09-02T22:00:00')
@pytest.mark.pgsql('fleet_orders_guarantee', files=['orders.sql'])
@pytest.mark.config(
    FLEET_ORDERS_GUARANTEE_INIT_LOOKUP_SETTINGS={
        'job_period_seconds': 60,
        'init_time_minutes': 60,
        'routing_enabled': True,
        'router_type': 'yandex',
        'duration_factor': 1.0,
        'extra_duration_minutes': 10,
        'notify_time_minutes': 5,
    },
)
async def test_job_with_routing(
        testpoint,
        pgsql,
        taxi_fleet_orders_guarantee,
        mock_order_core,
        mock_routes,
        mockserver,
):
    @testpoint('lookup-init-worker-finished')
    def handle_finished(arg):
        pass

    @mockserver.json_handler('/fleet-parks/v1/parks')
    def _mock_v1_parks_list(request):
        if request.args['park_id'] == 'park_id3':
            return mockserver.make_response(
                json={
                    'city_id': 'Берлин',
                    'country_id': 'rus',
                    'demo_mode': False,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                    'id': 'park_id3',
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'locale': 'ru',
                    'login': 'login',
                    'name': 'name',
                    'tz_offset': 3,
                },
                status=200,
            )
        else:
            return mockserver.make_response(status=404)

    @mockserver.json_handler('/feeds/v1/create')
    def _mock_v1_create(request):
        assert request.json == {
            'request_id': 'order_id3',
            'service': 'contractor-preorders',
            'payload': {'text': 'Next order at 1:05'},
            'channels': [{'channel': 'taximeter:Driver:park_id3:driver_id3'}],
            'status': 'published',
            'ignore_filters': False,
        }
        return {
            'feed_ids': {'taximeter:Driver:park_id3:driver_id3': 'feed_id1'},
            'service': 'contractor-preorders',
            'filtered': [],
        }

    @mockserver.json_handler('/client-notify/v2/push')
    def _mock_v2_push(request):
        assert request.json['intent'] == 'MessageNew'
        assert request.json['service'] == 'taximeter'
        assert request.json['client_id'] == 'park_id3-driver_id3'
        assert request.json['data'] == {
            'message': {
                'key': 'push_order_next',
                'keyset': 'taximeter_driver_messages_yango',
                'params': {'hours': '1', 'minutes': '05'},
            },
        }

        return {'notification_id': '024a3c5cd41e4a8ca5993bafb20e346b'}

    @mockserver.json_handler('/driver-trackstory/positions')
    def _driver_trackstory_positions(request):
        assert request.json in [
            {
                'driver_ids': ['park_id3_driver_id3', 'park_id4_driver_id4'],
                'type': 'adjusted',
            },
        ]
        return mockserver.make_response(
            json={
                'results': [
                    {
                        'driver_id': 'park_id3_driver_id3',
                        'position': DRIVER_POSITION,
                        'type': 'raw',
                    },
                    {
                        'driver_id': 'park_id4_driver_id4',
                        'position': DRIVER_POSITION,
                        'type': 'raw',
                    },
                ],
            },
            status=200,
        )

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _driver_status_statuses(request):
        assert request.json == {
            'driver_ids': [
                {'park_id': 'park_id3', 'driver_id': 'driver_id3'},
                {'park_id': 'park_id4', 'driver_id': 'driver_id4'},
            ],
        }

        return mockserver.make_response(
            json={
                'statuses': [
                    {
                        'park_id': 'park_id3',
                        'driver_id': 'driver_id3',
                        'status': 'online',
                        'updated_ts': 1637915919974,
                    },
                    {
                        'park_id': 'park_id4',
                        'driver_id': 'driver_id4',
                        'status': 'offline',
                        'orders': [
                            {'id': 'order_id7', 'status': 'transporting'},
                            {'id': 'order_id8', 'status': 'none'},
                            {'id': 'order_id9', 'status': 'none'},
                        ],
                    },
                ],
            },
            status=200,
        )

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core_order_fields(request):
        assert (
            {x: request.json[x] for x in request.json if x != 'order_id'}
            == {
                'fields': [
                    'order.request.destinations',
                    'order.request.due',
                    'order.request.source',
                ],
                'lookup_flags': 'allow_alias',
                'require_latest': False,
                'search_archive': False,
            }
        )
        order_id = request.json['order_id']
        assert order_id in ['order_id7', 'order_id8', 'order_id9']

        return mockserver.make_response(
            json={
                'fields': {
                    '_id': order_id,
                    'order': {
                        'request': {
                            'destinations': [
                                {
                                    'geopoint': (
                                        [13.29943, 52.518814]
                                        if order_id == 'order_id9'
                                        else [13.26943, 52.528814]
                                    ),
                                    'fullname': (
                                        'Germany, Berlin, '
                                        'Kaiser-Friedrich-Straße, 2'
                                    ),
                                    'short_text': 'Kaiser-Friedrich-Straße, 2',
                                },
                            ],
                            'due': (
                                '2021-11-28T21:36:01+00:00'
                                if order_id == 'order_id9'
                                else '2021-11-28T21:46:01+00:00'
                            ),
                            'source': {
                                'geopoint': (
                                    [13.411732, 52.509602]
                                    if order_id == 'order_id9'
                                    else [13.411832, 52.506602]
                                ),
                                'fullname': 'Germany, Berlin, Annenstraße, 14',
                                'short_text': 'Annenstraße, 14',
                            },
                        },
                    },
                },
                'order_id': order_id,
                'replica': 'secondary',
                'version': 'DAAAAAAABgAMAAQABgAAACudhGh9AQAA',
            },
            status=200,
        )

    cursor = pgsql['fleet_orders_guarantee'].cursor()
    mock_order_core.set_expected_requests(['order_id3', 'order_id4'])
    mock_routes.set_geopoints(
        [
            [[-55.735064, 37.578392], [13.388378, 52.519894]],
            [
                [-55.735064, 37.578392],
                [13.26943, 52.528814],
                [13.411732, 52.509602],
                [13.29943, 52.518814],
                [13.411832, 52.506602],
                [13.26943, 52.528814],
                [13.388378, 52.519894],
            ],
        ],
    )

    assert db_utils.get_orders(cursor) == ORDERS_BEFORE

    await taxi_fleet_orders_guarantee.run_distlock_task('lookup-init-task')

    result = handle_finished.next_call()
    assert result == {'arg': ['order_id3']}

    assert db_utils.get_orders(cursor) == ORDERS_AFTER_IF_ROUTING
    assert mock_order_core.call_times == 1
