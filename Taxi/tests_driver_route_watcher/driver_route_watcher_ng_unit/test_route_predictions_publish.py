# pylint: disable=import-error,too-many-lines
from geobus_tools import geobus  # noqa: F401 C5521
import pytest

from tests_plugins import utils

import tests_driver_route_watcher.utils as Utils


@pytest.mark.redis_store(['flushall'])
@pytest.mark.config(
    DRIVER_ROUTE_WATCHER_PREDICTED_POSITIONS_PUBLISH_SETTINGS={
        'enabled': True,
        'period': 200,
        'percentage': 100,
    },
    DRIVER_ROUTE_WATCHER_PREDICTION_PERIODS=[15, 40],
    DRIVER_ROUTE_WATCHER_ADJUST_PREDICTIONS_SETTINGS={
        'percentage': 100,
        'adjust_radius': 5,
    },
)
async def test_route_predicted_points_publish(
        driver_route_watcher_ng_adv, now, mockserver, load_binary, testpoint,
):
    drw = driver_route_watcher_ng_adv

    driver_id = {'uuid': 'uuidpredictionspublish', 'dbid': 'dbid1023'}
    dbid_uuid = '{}_{}'.format(driver_id['dbid'], driver_id['uuid'])
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

    @testpoint('route-predicted-point-publish')
    def route_predicted_point_publish(prediction):
        for i in range(len(prediction['signals'])):
            prediction['signals'][i]['geo_position']['lat'] = round(
                prediction['signals'][i]['geo_position']['lat'], 6,
            )
            prediction['signals'][i]['geo_position']['lon'] = round(
                prediction['signals'][i]['geo_position']['lon'], 6,
            )
            prediction['signals'][i]['position_on_edge'][
                'edge_displacement'
            ] = (
                round(
                    prediction['signals'][i]['position_on_edge'][
                        'edge_displacement'
                    ],
                    3,
                )
            )
        assert prediction == {
            'client_timestamp': int(utils.timestamp(now) * 1e3) * 1e3,
            'contractor_id': dbid_uuid,
            'signals': [
                {
                    'geo_position': {
                        'direction': 252,
                        'lat': 55.726431,
                        'lon': 37.461947,
                        'timestamp': int(utils.timestamp(now)) + 15,
                    },
                    'position_on_edge': {
                        'edge_displacement': 0.501,
                        'persistent_edge': 10564621977454761634,
                    },
                    'prediction_shift': 15,
                    'probability': 1.0,
                },
                {
                    'geo_position': {
                        'direction': 246,
                        'lat': 55.72506,
                        'lon': 37.455267,
                        'timestamp': int(utils.timestamp(now)) + 40,
                    },
                    'position_on_edge': {
                        'edge_displacement': 0.613,
                        'persistent_edge': 2404331225615138845,
                    },
                    'prediction_shift': 40,
                    'probability': 1.0,
                },
            ],
            'source': '',
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

    await route_predicted_point_publish.wait_call()

    await drw.stop_watch(driver_id, destination, service_id)
    await stop_watch_message_processed.wait_call()
