# pylint: disable=import-error
import datetime

import pytest
import yandex.maps.proto.bicycle.summary_pb2 as ProtoBicycleSummary
import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary
import yandex.maps.proto.masstransit.summary_pb2 as ProtoMasstransitSummary

from geobus_tools import geobus  # noqa: F401 C5521
from tests_plugins import utils


NOW = datetime.datetime(2000, 7, 20, 20, 17, 39)
UTC_NOW = NOW.replace(tzinfo=datetime.timezone.utc)

EDGE_TRACKS_CHANNEL = 'channel:yaga:edge_positions'
PEDESTRIAN_POSITIONS_CHANNEL = 'channel:yagr:pedestrian_positions'
TIMELEFTS_CHANNEL = 'channel:drw:timelefts'
DRIVERS_COUNT = 11


def _proto_driving_summary(summary):
    time = summary['time']
    distance = summary['distance']
    response = ProtoDrivingSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.time_with_traffic.value = time
    item.weight.time_with_traffic.text = ''
    item.weight.distance.value = distance
    item.weight.distance.text = ''
    item.flags.blocked = False
    return response.SerializeToString()


def _proto_masstransit_summary(summary):
    time = summary['time']
    distance = summary['distance']
    response = ProtoMasstransitSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.walking_distance.value = distance
    item.weight.walking_distance.text = ''
    item.weight.transfers_count = 1
    return response.SerializeToString()


def _proto_bicycle_summary(summary):
    time = summary['time']
    distance = summary['distance']
    response = ProtoBicycleSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.distance.value = distance
    item.weight.distance.text = ''
    return response.SerializeToString()


@pytest.mark.parametrize(
    'table_name',
    [
        pytest.param(
            'chain_busy_drivers',
            marks=pytest.mark.config(
                BUSY_DRIVERS_POSTGRESQL_PARTITIONING_TYPE='declarative',
            ),
        ),
        pytest.param(
            'chain_busy_driver_parent',
            marks=pytest.mark.config(
                BUSY_DRIVERS_POSTGRESQL_PARTITIONING_TYPE='inheritance',
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                BUSY_DRIVERS_GEOBUS_ETA_SOURCE='timelefts',
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'max_route_distance, '
    'max_line_distance, '
    'expected_statuses, '
    'expected_router_calls,'
    'geobus_eta_expired,'
    'geobus_eta_linear_fallback,'
    'geobus_eta_left_time,'
    'geobus_eta_left_dist',
    [
        (
            3000,
            3000,
            [
                {
                    'driver_id': 'dbid_uuid1',
                    'order_id': 'order_id1',
                    'updated': UTC_NOW,
                },
                {
                    'driver_id': 'dbid_uuid2',
                    'order_id': 'order_id2',
                    'updated': UTC_NOW,
                },
            ],
            2,
            True,
            False,
            2500,
            2500,
        ),
        (2000, 2000, [], 0, True, False, 2500, 2500),
        (2000, 3000, [], 2, True, False, 2500, 2500),
        (2000, 3000, [], 2, True, True, 2500, 2500),
        (
            3000,
            3000,
            [
                {
                    'driver_id': 'dbid_uuid1',
                    'order_id': 'order_id1',
                    'updated': UTC_NOW,
                },
                {
                    'driver_id': 'dbid_uuid2',
                    'order_id': 'order_id2',
                    'updated': UTC_NOW,
                },
            ],
            2,
            False,
            False,
            2500,
            0,
        ),
        (
            3000,
            3000,
            [
                {
                    'driver_id': 'dbid_uuid1',
                    'order_id': 'order_id1',
                    'updated': UTC_NOW,
                },
                {
                    'driver_id': 'dbid_uuid2',
                    'order_id': 'order_id2',
                    'updated': UTC_NOW,
                },
            ],
            0,
            False,
            False,
            2500,
            2500,
        ),
        (3000, 3000, [], 0, False, True, 2500, 2500),
        (2000, 2000, [], 0, False, False, 2500, 2500),
        (2000, 3000, [], 0, False, False, 2500, 2500),
    ],
)
@pytest.mark.config(
    BUSY_DRIVERS_MAX_POSITION_AGE={
        'pedestrian_ttl': 60,
        'default_edge_ttl': 60,
    },
    BUSY_DRIVERS_DRIVERS_CHUNKS_COUNT=4,
    ROUTER_MAPS_ENABLED=True,
    ROUTER_SELECT=[
        {'routers': []},
        {'ids': ['moscow'], 'routers': ['yamaps']},
    ],
    TVM_ENABLED=False,
    BUSY_DRIVERS_ENABLE_CHAIN_FOR_TARIFFS_BY_ZONE={
        '__default__': {'__default__': True},
        'moscow': {'__default__': True, 'cargo': False},
        'tula': {'__default__': False},
    },
    BUSY_DRIVERS_DISABLE_CHAIN_FOR_SPECIAL_REQUIREMENTS={
        '__default__': {'__default__': []},
        'moscow': {
            '__default__': [],
            'business': [{'all_of': ['thermobag_delivery', 'child_seat']}],
        },
        'spb': {
            '__default__': [{'any_of': ['child_seat', 'thermobag_delivery']}],
        },
    },
)
@pytest.mark.pgsql(
    'busy_drivers', files=['orders.sql', 'chain_busy_drivers.sql'],
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_periodic_routing_estimation_task(
        table_name,
        geobus_eta_expired,
        geobus_eta_linear_fallback,
        geobus_eta_left_time,
        geobus_eta_left_dist,
        max_route_distance,
        max_line_distance,
        expected_statuses,
        expected_router_calls,
        pgsql,
        mockserver,
        taxi_busy_drivers,
        testpoint,
        redis_store,
        mocked_time,
        dispatch_settings_mocks,
        taxi_config,
):

    taxi_config.set_values(
        {
            'ORDER_CHAIN_SETTINGS': {
                '__default__': {
                    '__default__': {
                        'MAX_LINE_DISTANCE': max_line_distance,
                        'MAX_ROUTE_DISTANCE': max_route_distance,
                        'MAX_ROUTE_TIME': max_route_distance,
                        'MIN_TAXIMETER_VERSION': '8.06',
                        'PAX_EXCHANGE_TIME': 120,
                    },
                },
            },
        },
    )

    dispatch_settings_mocks.set_settings(
        settings=[
            {
                'zone_name': '__default__',
                'tariff_name': '__default__base__',
                'parameters': [
                    {
                        'values': {
                            'ORDER_CHAIN_MAX_LINE_DISTANCE': max_line_distance,
                            'ORDER_CHAIN_MAX_ROUTE_DISTANCE': (
                                max_route_distance
                            ),
                            'ORDER_CHAIN_MAX_ROUTE_TIME': max_route_distance,
                            'ORDER_CHAIN_PAX_EXCHANGE_TIME': 120,
                        },
                    },
                ],
            },
        ],
    )

    await taxi_busy_drivers.invalidate_caches()

    mock_calls = {'router': 0}

    mocked_time.set(NOW)

    timestamp = int(utils.timestamp(NOW))
    positions = [
        {
            'driver_id': 'dbid_uuid{}'.format(i),
            'position': [37.65, 55.73],
            'direction': 0,
            'timestamp': timestamp * 1000,  # seconds -> milliseconds
            'speed': 42 / 3.6,  # km/h -> m/s
            'accuracy': 0,
            'source': 'Gps',
        }
        for i in range(DRIVERS_COUNT)
    ]

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        mock_calls['router'] += 1
        data = {'time': 2500, 'distance': 2500}
        return mockserver.make_response(
            response=_proto_driving_summary(data),
            status=200,
            content_type='application/x-protobuf',
        )

    @testpoint('geobus-positions_payload_processed')
    def redis_pos_payload_processed(data):
        return data

    @testpoint('geobus-timelefts_payload_processed')
    def redis_timelefts_processed(data):
        return data

    await taxi_busy_drivers.enable_testpoints()

    redis_store.publish(
        EDGE_TRACKS_CHANNEL,
        geobus.serialize_edge_positions_v2(positions, NOW),
    )

    await redis_pos_payload_processed.wait_call()

    if geobus_eta_expired:
        timestamp = timestamp - 3600

    for i in range(DRIVERS_COUNT):
        timelefts = {
            'timestamp': timestamp * 1000,
            'update_timestamp': timestamp * 1000,
            'tracking_type': (
                'LinearFallback'
                if geobus_eta_linear_fallback
                else 'RouteTracking'
            ),
            'contractor_id': 'dbid_uuid{}'.format(i),
            'route_id': '0',
            'adjusted_pos': [37.65, 55.73],
            'timeleft_data': [
                {
                    'destination_position': [37.66, 55.71],
                    'distance_left': geobus_eta_left_dist,
                    # wrong service
                    'service_id': 'processing:driving',
                    'order_id': 'order_id{}'.format(i),
                    'time_left': geobus_eta_left_time,
                },
                {
                    # wrong coordinate
                    'destination_position': [38.66, 55.71],
                    'distance_left': geobus_eta_left_dist,
                    'service_id': 'processing:transporting',
                    'order_id': 'order_id{}'.format(i),
                    'time_left': geobus_eta_left_time,
                },
                {
                    # correct
                    'destination_position': [37.66, 55.71],
                    'distance_left': geobus_eta_left_dist,
                    'service_id': 'processing:transporting',
                    'order_id': 'order_id{}'.format(i),
                    'time_left': geobus_eta_left_time,
                },
                {
                    'destination_position': [37.66, 55.71],
                    'distance_left': geobus_eta_left_dist,
                    'service_id': 'processing:transporting',
                    # wrong order_id
                    'order_id': 'order_id{}'.format(100 * i),
                    'time_left': geobus_eta_left_time,
                },
            ],
            'adjusted_segment_index': 0,
        }

        message = {'timestamp': timestamp, 'payload': [timelefts]}

        redis_store.publish(
            TIMELEFTS_CHANNEL,
            geobus.timelefts.serialize_message(message, NOW),
        )

        await redis_timelefts_processed.wait_call()

    etas = [
        {
            'timestamp': timestamp * 1000,
            'update_timestamp': timestamp * 1000,
            'tracking_type': (
                'LinearFallback'
                if geobus_eta_linear_fallback
                else 'RouteTracking'
            ),
            'contractor_id': 'dbid_uuid{}'.format(i),
            'route_id': '0',
            'adjusted_pos': [37.65, 55.73],
            'timeleft_data': [
                {
                    'destination_position': [37.66, 55.71],
                    'distance_left': geobus_eta_left_dist,
                    'service_id': 'processing:transporting',
                    'order_id': 'order_id{}'.format(i),
                    'time_left': geobus_eta_left_time,
                },
            ],
        }
        for i in range(DRIVERS_COUNT)
    ]

    message = {'timestamp': timestamp, 'payload': [timelefts]}

    redis_store.publish(
        TIMELEFTS_CHANNEL, geobus.timelefts.serialize_message(message, NOW),
    )

    await redis_timelefts_processed.wait_call()

    await taxi_busy_drivers.run_task('distlock/chain-busy-drivers-updater')

    cursor = pgsql['busy_drivers'].cursor()
    cursor.execute(
        'select driver_id, order_id, updated'
        ' from busy_drivers.{}'
        ' where driver_skip_reason is null'.format(table_name),
    )
    colnames = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    statuses = [dict(zip(colnames, row)) for row in rows]

    assert sorted(statuses, key=lambda i: i['driver_id']) == expected_statuses
    assert mock_calls['router'] == expected_router_calls


@pytest.mark.config(
    BUSY_DRIVERS_MAX_POSITION_AGE={
        'pedestrian_ttl': 60,
        'default_edge_ttl': 60,
        'edge_ttl_by_transport': {'bicycle': 120},
    },
    BUSY_DRIVERS_DRIVERS_CHUNKS_COUNT=1,
    BUSY_DRIVERS_GEOBUS_ETA_SOURCE='timelefts',
    ROUTER_MAPS_ENABLED=True,
    ROUTER_BICYCLE_MAPS_ENABLED=True,
    ROUTER_SELECT=[
        {'routers': []},
        {'ids': ['moscow'], 'routers': ['yamaps']},
    ],
    TVM_ENABLED=False,
)
@pytest.mark.pgsql(
    'busy_drivers', files=['orders.sql', 'chain_busy_drivers.sql'],
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_router_by_transport_type(
        mockserver,
        taxi_busy_drivers,
        testpoint,
        redis_store,
        mocked_time,
        dispatch_settings_mocks,
):
    dispatch_settings_mocks.set_settings(
        settings=[
            {
                'zone_name': '__default__',
                'tariff_name': '__default__base__',
                'parameters': [
                    {
                        'values': {
                            'ORDER_CHAIN_MAX_LINE_DISTANCE': 3000,
                            'ORDER_CHAIN_MAX_ROUTE_DISTANCE': 3000,
                            'ORDER_CHAIN_MAX_ROUTE_TIME': 3000,
                            'ORDER_CHAIN_PAX_EXCHANGE_TIME': 120,
                        },
                    },
                ],
            },
        ],
    )

    await taxi_busy_drivers.invalidate_caches()

    idx_range = range(1, 4)
    mock_calls = {'routers': set()}

    mocked_time.set(NOW)

    timestamp = int(utils.timestamp(NOW))
    positions = [
        {
            'driver_id': 'dbid_uuid{}'.format(i),
            'position': [37.65, 55.73],
            'direction': 0,
            'timestamp': (
                timestamp - 70
            ) * 1000,  # seconds -> milliseconds, expired for car
            'speed': 42 / 3.6,  # km/h -> m/s
            'accuracy': 0,
            'source': 'Gps',
        }
        for i in [1, 3]
    ]

    pedestrian_positions = [
        {
            'driver_id': 'dbid_uuid2',
            'position': [37.65, 55.73],
            'direction': 0,
            'timestamp': timestamp,  # сырые позиции передаются в секундах
            'speed': 42 / 3.6,  # km/h -> m/s
            'accuracy': 0,
            'source': 'Gps',
        },
    ]

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        mock_calls['routers'].add('car')
        data = {'time': 2500, 'distance': 2500}
        return mockserver.make_response(
            response=_proto_driving_summary(data),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_pedestrian_router(request):
        mock_calls['routers'].add('pedestrian')
        data = {'time': 2500, 'distance': 2500}
        return mockserver.make_response(
            response=_proto_masstransit_summary(data),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-bicycle-router/v2/summary')
    def _mock_bicycle_router(request):
        mock_calls['routers'].add('bicycle')
        data = {'time': 2500, 'distance': 2500}
        return mockserver.make_response(
            response=_proto_bicycle_summary(data),
            status=200,
            content_type='application/x-protobuf',
        )

    @testpoint('geobus-positions_payload_processed')
    def redis_pos_payload_processed(data):
        return data

    @testpoint('geobus-pedestrian-positions_payload_processed')
    def redis_pedestrian_processed(data):
        return data

    @testpoint('geobus-timelefts_payload_processed')
    def redis_timelefts_processed(data):
        return data

    await taxi_busy_drivers.enable_testpoints()

    redis_store.publish(
        EDGE_TRACKS_CHANNEL,
        geobus.serialize_edge_positions_v2(positions, NOW),
    )
    await redis_pos_payload_processed.wait_call()

    redis_store.publish(
        PEDESTRIAN_POSITIONS_CHANNEL,
        geobus.serialize_positions_v2(pedestrian_positions, NOW),
    )
    await redis_pedestrian_processed.wait_call()

    # make geobus eta expired
    timestamp = timestamp - 3600

    for i in idx_range:
        timelefts = {
            'timestamp': timestamp * 1000,
            'update_timestamp': timestamp * 1000,
            'tracking_type': 'RouteTracking',
            'contractor_id': 'dbid_uuid{}'.format(i),
            'route_id': '0',
            'adjusted_pos': [37.65, 55.73],
            'timeleft_data': [
                {
                    'destination_position': [37.66, 55.71],
                    'distance_left': 2500,
                    'service_id': 'processing:transporting',
                    'order_id': 'order_id{}'.format(i),
                    'time_left': 2500,
                },
            ],
            'adjusted_segment_index': 0,
        }

        message = {'timestamp': timestamp, 'payload': [timelefts]}

        redis_store.publish(
            TIMELEFTS_CHANNEL,
            geobus.timelefts.serialize_message(message, NOW),
        )

        await redis_timelefts_processed.wait_call()

    await taxi_busy_drivers.run_task('distlock/chain-busy-drivers-updater')
    assert mock_calls['routers'] == {'pedestrian', 'bicycle'}
