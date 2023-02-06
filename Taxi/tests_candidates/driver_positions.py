# pylint: disable=import-error
from geobus_tools import geobus  # noqa: F401 C5521
from geobus_tools.channels import universal_signals  # noqa: F401 C5521
from tests_plugins import utils
from testsuite.utils import callinfo


# hack for flap tests
async def _publish(redis_store, channel, message, callback):
    for _ in range(5):
        redis_store.publish(channel, message)

        try:
            await callback.wait_call(2)
            return
        except callinfo.CallQueueTimeoutError:
            pass


def _convert_drivers(positions, now):
    drivers = []
    for pos in positions:
        driver = {
            'driver_id': pos['dbid_uuid'],
            'position': (
                pos['position']
                if 'position' in pos
                else pos['positions'][0]['position']
            ),
            'direction': pos.get('direction', 0),
            'timestamp': (int(utils.timestamp(now))),
            'speed': pos.get('speed', 0) * 1000 / 60 / 60,  # convert to m/s
            'accuracy': pos.get('accuracy', 0),
            'prediction_shift': pos.get('prediction_shift', 0),
        }
        drivers.append(driver)

    return drivers


def _convert_drivers_v2(drivers_positions, now):
    drivers = []
    for driver_positions in drivers_positions:
        driver = {
            'driver_id': driver_positions['dbid_uuid'],
            'direction': 0,
            'timestamp': (int(utils.timestamp(now))),
            'speed': 0,
            'accuracy': 0,
        }
        for position in driver_positions['positions']:
            if position['shift'] == 0:
                driver['position'] = position['position']
        drivers.append(driver)

    return drivers


def _convert_universal_drivers(drivers_pos, now):
    drivers = []
    for driver_pos in drivers_pos:
        driver = {
            'contractor_id': driver_pos['dbid_uuid'],
            'client_timestamp': (int(utils.timestamp(now)) * 1000000),
            'signals': [],
        }
        for pos in driver_pos['positions']:
            driver['signals'].append(
                {
                    'geo_position': {'position': pos['position']},
                    'prediction_shift': pos['shift'],
                },
            )
        drivers.append(driver)

    return drivers


def _convert_universal_drivers_v2(drivers_pos):
    drivers = []
    for driver_pos in drivers_pos:
        driver = {
            'contractor_id': driver_pos['driver_id'],
            'client_timestamp': (driver_pos['timestamp'] * 1000000),
            'signals': [
                {
                    'geo_position': {
                        'position': driver_pos['position'],
                        'speed': driver_pos['speed'],
                        'accuracy': driver_pos['accuracy'],
                        'direction': driver_pos['direction'],
                    },
                    'probability': 1.0,
                    'prediction_shift': driver_pos['prediction_shift'],
                },
            ],
        }
        drivers.append(driver)

    return drivers


# positions = [
#   {
#       'dbid_uuid': 'dbid_uuid',
#       'position': [lon, lat],
#       'prediction_shift': 0, // seconds
#       'speed': 0 // km/h
#   },
#   ...
# ]
# Alternatively
# positions = [
#   {
#       'dbid_uuid': 'dbid_uuid',
#       'positions': [
#           {
#               'position': [lon, lat],
#               'shift': shift,
#           },
#           ...
#       ],
#   },
#   ...
# ]
async def publish(taxi_candidates, positions, redis_store, testpoint, now):
    @testpoint('channel:yagr:position')
    def positions_tpoint(data):
        pass

    @testpoint('channel:yaga:universal_edge_positions')
    def edge_positions_tpoint(data):
        pass

    await taxi_candidates.enable_testpoints(no_auto_cache_cleanup=True)

    drivers = _convert_drivers(positions, now)
    yagr_message = geobus.serialize_positions_v2(drivers, now)
    await _publish(
        redis_store, 'channel:yagr:position', yagr_message, positions_tpoint,
    )

    edge_positions = {}
    # Stub for test
    if 'positions' in positions[0]:
        edge_positions['payload'] = _convert_universal_drivers(positions, now)
    else:
        edge_positions['payload'] = _convert_universal_drivers_v2(drivers)

    universal_message = universal_signals.serialize_message(
        edge_positions, now,
    )
    await _publish(
        redis_store,
        'channel:yaga:universal_edge_positions',
        universal_message,
        edge_positions_tpoint,
    )


# positions = [
#   {
#       'dbid_uuid': 'dbid_uuid',
#       'positions': [
#           {
#               'position': [lon, lat],
#               'shift': shift,
#           },
#           ...
#       ],
#   },
#   ...
# ]
async def publish_route_predicted(
        taxi_candidates, positions, redis_store, testpoint, now,
):
    @testpoint('channel:yagr:position')
    def positions_tpoint(data):
        pass

    @testpoint('channel:drw:route_predicted_positions')
    def universal_positions_tpoint(data):
        pass

    await taxi_candidates.enable_testpoints(no_auto_cache_cleanup=True)

    drivers = _convert_drivers_v2(positions, now)
    message = geobus.serialize_positions_v2(drivers, now)
    await _publish(
        redis_store, 'channel:yagr:position', message, positions_tpoint,
    )

    drivers = {}
    drivers['payload'] = _convert_universal_drivers(positions, now)
    universal_message = universal_signals.serialize_message(drivers, now)
    await _publish(
        redis_store,
        'channel:drw:route_predicted_positions',
        universal_message,
        universal_positions_tpoint,
    )
