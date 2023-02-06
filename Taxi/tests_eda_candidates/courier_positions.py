# pylint: disable=import-error

from geobus_tools import geobus  # noqa: F401 C5521

from tests_plugins import utils


# positions = [
#   {
#       'id': 'id',
#       'position': [lon, lat]
#   },
#   ...
# ]
async def publish(taxi_eda_candidates, positions, redis_store, testpoint, now):
    @testpoint('channel:eda:courier_position_v2')
    def positions_tpoint(data):
        pass

    geobus_positions = []
    for pos in positions:
        geobus_positions.append(
            {
                'driver_id': 'eda_' + pos['id'],
                'position': pos['position'],
                'direction': 0,
                'timestamp': int(utils.timestamp(now)),
                'speed': 0,
                'accuracy': 0,
            },
        )

    await taxi_eda_candidates.enable_testpoints(no_auto_cache_cleanup=True)

    message = geobus.serialize_positions_v2(geobus_positions, now)
    redis_store.publish('channel:eda:courier_position_v2', message)
    await positions_tpoint.wait_call()
