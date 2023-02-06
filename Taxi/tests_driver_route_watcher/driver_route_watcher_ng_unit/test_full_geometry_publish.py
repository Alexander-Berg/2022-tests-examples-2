# pylint: disable=import-error,too-many-lines
from geobus_tools import geobus  # noqa: F401 C5521
import pytest

from tests_plugins import utils

import tests_driver_route_watcher.utils as Utils


@pytest.mark.redis_store(['flushall'])
@pytest.mark.config(
    DRIVER_ROUTE_WATCHER_FULL_GEOMETRY_POSITIONS_PUBLISH_SETTINGS={
        'enabled': True,
        'period': 200,
    },
)
async def test_full_geometry_publish(
        driver_route_watcher_ng_adv, now, mockserver, load_binary, testpoint,
):
    drw = driver_route_watcher_ng_adv

    driver_id = {'uuid': 'uuidfullgeometry', 'dbid': 'dbid1023'}
    service_id = 'service_id'
    raw_position = [37.466104, 55.727191]
    destination = [37.454099, 55.718486]

    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        # 37.466104,55.727191 -> 37.454099,55.718486
        return mockserver.make_response(
            response=load_binary('maps_response.pb'),
            status=200,
            content_type='application/x-protobuf',
        )

    @testpoint('route-message-processed')
    def route_message_processed(data):
        pass

    @testpoint('master-slave-locked')
    def master_slave_locked(data):
        pass

    @testpoint('master-slave-confirmed')
    def master_slave_confirmed(data):
        pass

    @testpoint('stop-watch-message-processed')
    def stop_watch_message_processed(data):
        pass

    @testpoint('full-geometry-point-publish')
    def full_geometry_point_publish(position):
        assert position == {
            'lat': 55.72718,
            'lon': 37.466111,
            'direction': 0,
            'source': 'Gps',
            'timestamp': int(utils.timestamp(now)),
            'speed': 42.0,
        }

    @testpoint('restore-aggregator-callback-start')
    def restore_aggregator_callback(data):  # noqa: C0103
        pass

    @testpoint('restore-aggregator-callback-success')
    def restore_aggregator_callback_ok(data):  # noqa: C0103
        pass

    await drw.invalidate_caches()

    # wait to become master before writing route
    await master_slave_locked.wait_call()
    await drw.run_periodic_task('watches-synchronizer')
    await master_slave_confirmed.wait_call()

    # start watch
    Utils.publish_edge_position(driver_id, raw_position, drw.redis_store, now)
    await drw.start_watch(driver_id, destination, service_id)

    await drw.run_periodic_task('RestoreMessageAggregator0')
    await restore_aggregator_callback.wait_call()
    await restore_aggregator_callback_ok.wait_call()
    await route_message_processed.wait_call()

    await full_geometry_point_publish.wait_call()

    await drw.stop_watch(driver_id, destination, service_id)
    await stop_watch_message_processed.wait_call()
