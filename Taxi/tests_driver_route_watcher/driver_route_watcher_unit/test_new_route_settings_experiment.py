# pylint: disable=import-error,too-many-lines

# from geobus_tools import geobus  # noqa: F401 C5521
# import pytest
#
# import tests_driver_route_watcher.utils as Utils
# import tests_driver_route_watcher.watch_list as WatchList
#
#
# @pytest.mark.experiments3(
#     match={'predicate': {'type': 'true'}, 'enabled': True},
#     name='driver_route_watcher_new_router_settings',
#     consumers=['driver_route_watcher/new_router_settings'],
#     clauses=[
#         {
#             'enabled': True,
#             'predicate': {'type': 'true'},
#             'title': 'Условие segmentation',
#             'value': {'mode': 'best', 'vehicle_type': 'vehicle_taxi'},
#         },
#     ],
# )
# @pytest.mark.config(
#     TVM_RULES=[{'dst': 'yamaps', 'src': 'driver-route-watcher'}],
#     DRIVER_ROUTE_WATCHER_ENABLE_TIMELEFTS_PUBLISH=True,
# )
# async def test_new_router_settings_exp(
#         taxi_driver_route_watcher_adv,
#         redis_store,
#         now,
#         mockserver,
#         load_binary,
#         testpoint,
# ):
#     drw = taxi_driver_route_watcher_adv
#
#     @mockserver.handler('/maps-router/v2/route')
#     def _mock_route(request):
#         # 37.466104,55.727191 -> 37.454099,55.718486
#         # we made request with 'toll_roads': false
#         assert request.args['avoid'] == 'tolls'
#         return mockserver.make_response(
#             response=load_binary('maps_response.pb'),
#             status=200,
#             content_type='application/x-protobuf',
#         )
#
#     @testpoint('master-slave-locked')
#     def master_slave_locked(data):
#         pass
#
#     @testpoint('master-slave-confirmed')
#     def master_slave_confirmed(data):
#         pass
#
#     @testpoint('stop-watch-message-processed')
#     def stop_watch_message_processed(data):
#         pass
#
#     @testpoint('new-router-settings')
#     def new_route_settings(data):
#         assert data['mode'] == 'best'
#         assert data['vehicle_type'] == 'taxi'
#
#     @testpoint('reset-watch-completed')
#     def reset_watch_completed(data):
#         pass
#
#     driver_id = {'uuid': 'uuid100', 'dbid': 'dbid'}
#     raw_position = [37.466104, 55.727191]
#     destination = [37.454099, 55.718486]
#
#     # wait to become master before writing route
#     await Utils.request_ping(drw)
#     await master_slave_locked.wait_call()
#     await drw.run_periodic_task('watches-synchronizer')
#     await master_slave_confirmed.wait_call()
#
#     Utils.publish_edge_position(driver_id, raw_position, redis_store, now)
#
#     await drw.start_watch(
#         driver_id,
#         destination,
#         meta='{"order_id":"12345","taxi_status":"driving"}',
#     )
#     await new_route_settings.wait_call()
#
#     # stop watch
#     await drw.stop_watch(driver_id, destination)
#     await stop_watch_message_processed.wait_call()
#     await reset_watch_completed.wait_call()
#
#     # After stop watch request watchlist entry must be deleted
#     watchlist = WatchList.get_watchlist(redis_store)
#     assert watchlist == {}
