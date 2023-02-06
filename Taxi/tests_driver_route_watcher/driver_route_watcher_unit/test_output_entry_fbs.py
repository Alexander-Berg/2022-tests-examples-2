import tests_driver_route_watcher.output_entry_fbs as OutputEntryFbs
import tests_driver_route_watcher.points_list_fbs as PointslistFbs


async def test_output_entry():
    orig = {
        'time_left': 42,
        'distance_left': 100500,
        'position': [37, 55],
        'raw_position': [37, 55],
        'destination': [38, 56],
        'direction': 127,
        'raw_direction': 289,
        'tracking_type': 'linear_fallback',  # or route_tracking
        'service_id': 'some-service-id',
        'metainfo': {'order_id': '12345', 'taxi_status': 'driving'},
        'points': PointslistFbs.to_point_list([[11, 22], [33, 44]]),
        'order_id': 'testorderid',
        'segment_id': 333,
        'etas': [
            {'time_left': 10, 'distance_left': 2000},
            {'time_left': 20, 'distance_left': 20000},
            {'time_left': 42, 'distance_left': 100500},
        ],
        'updated_since': 1234567,
        'eta_multiplier': 1,
    }
    data = OutputEntryFbs.serialize_output_entry(orig)
    entry = OutputEntryFbs.deserialize_output_entry(data)
    assert orig == entry
