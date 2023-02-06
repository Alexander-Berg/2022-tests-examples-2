# pylint: disable=import-error
import datetime

import pytest
import reposition_api.fbs.v1.airport_queue.state.Request as StateRequest

from tests_dispatch_airport import common
import tests_dispatch_airport.utils as utils


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql(
    'dispatch_airport', files=['drivers_queue.sql', 'driver_events.sql'],
)
@pytest.mark.config(
    SVO_POLYGON_NAMES={
        'DL1': {
            'full_text': 'aeroport sheremetevo D',
            'point': [61, 11],
            'target_airport_id': 'svo',
        },
    },
)
async def test_reposition(
        taxi_dispatch_airport,
        experiments3,
        mockserver,
        taxi_dispatch_airport_monitor,
        now,
        load_json,
        testpoint,
        redis_store,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        zone_id = request.json['zone_id']
        assert zone_id in ('ekb_home_zone', 'svo_home_zone')
        if zone_id == 'svo_home_zone':
            assert len(request.json['driver_ids']) == 4
        else:
            assert len(request.json['driver_ids']) == 3
        return load_json('candidates.json')[zone_id]

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    def _mock(request):
        helper = utils.MakeOfferFbHelper()
        request_json = helper.parse_request(request.get_data())
        response_data = [
            {
                'park_db_id': request_json[0]['park_db_id'],
                'driver_id': request_json[0]['driver_id'],
                'point_id': 'reposition_id',
            },
        ]
        return mockserver.make_response(
            response=helper.build_response(response_data),
            content_type='application/x-flatbuffers',
        )

    @mockserver.json_handler('/reposition/v1/service/make_offer')
    def _mock_reposition_make_offer(request):
        return _mock(request)

    @mockserver.json_handler('/reposition-api/v1/service/make_offer')
    def _mock_reposition_api_make_offer(request):
        return _mock(request)

    @mockserver.handler('/reposition-api/v1/service/airport_queue/state')
    def _reposition(request):
        request = StateRequest.Request.GetRootAsRequest(request.get_data(), 0)
        assert request.AirportQueueId() is None
        # assert request.DriversLength() == 4
        for i in range(4):
            driver = request.Drivers(i)
            dbid = driver.ParkDbId().decode()
            uuid = driver.DriverProfileId().decode()
            if uuid in ('uuid5', 'uuid6'):
                break

        drivers = [
            {
                'dbid': dbid,
                'uuid': uuid,
                'airport_id': 'svo' if uuid == 'uuid6' else 'ekb',
                'mode': 'Sintegro',
                'unique_driver_id': uuid,
            },
        ]
        return mockserver.make_response(
            response=utils.generate_reposition_api_drivers(drivers),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/session/stop',
    )
    def _reposition_stop(request):
        return {}

    @testpoint('account_reposition_offer_sent')
    def account_offer_sent(data):
        return data

    @testpoint('account_accepted_reposition_offer')
    def account_offer_accepted(data):
        return data

    @testpoint('account_successful_reposition')
    def account_reposition_successful(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    # dbid_uuid1 - ekb, entered on_reposition ->
    # queued, succsessful reposition
    # dbid_uuid2 - svo, entered on_reposition ->
    # queued, succsessful reposition
    # dbid_uuid3 - ekb -> svo DL1, queued ->
    # sent offer -> reposition offer sent
    # dbid_uuid4 - svo -> svo DL1, queued ->
    # sent offer -> reposition offer sent
    # dbid_uuid5 - ekb - new driver ->
    # entered on reposition -> reposition offer accepted
    # dbid_uuid6 - svo - new driver ->
    # entered on reposition -> reposition offer accepted
    # dbid_uuid7 - svo - not queued driver ->
    # reposition offer wasn't sent
    # dbid_uuid8 - svo - driver changed tariff
    # during reposition -> reposition was not successful
    # dbid_uuid9 - svo - driver didn't reach
    # notification zone -> reposition offer was not accepted

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    await taxi_dispatch_airport.run_task('reset_business_statistics')

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='dispatch_airport_reposition_api_make_offer',
        consumers=['dispatch_airport/reposition_api_make_offer'],
        default_value={'enabled': True},
        clauses=[],
    )

    for car_number, _ in [
            ('a123fg', 'uuid3'),
            ('a123hi', 'uuid4'),
            ('a123jl', 'uuid7'),
    ]:
        await taxi_dispatch_airport.post(
            '/v1/relocate/start',
            {'car_number': car_number, 'polygon_id': 'DL1'},
            headers=common.DEFAULT_DISPATCH_AIRPORT_HEADER,
        )

    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid2': {
            'position': utils.SVO_WAITING_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid5': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid6': {
            'position': utils.SVO_NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid9': {
            'position': utils.OUT_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-svo')
    await utils.wait_certain_testpoint('svo', queue_update_finished)

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    assert (
        utils.get_calls_sorted_two_keys(
            account_offer_sent, 2, 'data', 'driver_id', 'airport_id',
        )
        == [
            {'driver_id': 'dbid_uuid3', 'airport_id': 'svo'},
            {'driver_id': 'dbid_uuid4', 'airport_id': 'svo'},
        ]
    )

    assert (
        utils.get_calls_sorted_two_keys(
            account_offer_accepted, 2, 'data', 'driver_id', 'airport_id',
        )
        == [
            {'driver_id': 'dbid_uuid5', 'airport_id': 'ekb'},
            {'driver_id': 'dbid_uuid6', 'airport_id': 'svo'},
        ]
    )

    assert (
        utils.get_calls_sorted_two_keys(
            account_reposition_successful,
            2,
            'data',
            'driver_id',
            'airport_id',
        )
        == [
            {'driver_id': 'dbid_uuid1', 'airport_id': 'ekb'},
            {'driver_id': 'dbid_uuid2', 'airport_id': 'svo'},
        ]
    )

    metric = await taxi_dispatch_airport_monitor.get_metric(
        'dispatch_airport_metrics',
    )
    assert metric['reposition'] == {
        'ekb': {'offers_sent': 0, 'offers_accepted': 1, 'offers_completed': 1},
        'svo': {'offers_sent': 2, 'offers_accepted': 1, 'offers_completed': 1},
        '$meta': {'solomon_children_labels': 'airport_id'},
    }


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    DISPATCH_AIRPORT_DRIVER_EVENTS_PSQL_ENABLED=True,
    DISPATCH_AIRPORT_AREA_ENTRY_TRACKING={
        'ekb': {
            'marked_area_type': 'terminal',
            'maximum_number_of_entries': 1,
            'enter_accumulation_period': 90,
        },
        'svo': {
            'maximum_number_of_entries': 3,
            'enter_accumulation_period': 30,
        },
    },
)
async def test_driver_entry_and_area_tracking_config(
        taxi_dispatch_airport,
        testpoint,
        pgsql,
        mockserver,
        mocked_time,
        now,
        redis_store,
        taxi_dispatch_airport_monitor,
        taxi_config,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        airport = request.json['zone_id']
        if airport == 'ekb_home_zone':
            return {
                'drivers': [
                    {
                        'car_id': 'car_id_3',
                        'classes': ['econom'],
                        'dbid': 'dbid',
                        'position': [0, 0],
                        'status': {'driver': 'free', 'taximeter': 'free'},
                        'unique_driver_id': 'udid3',
                        'uuid': 'uuid3',
                    },
                ],
            }
        return {
            'drivers': [
                {
                    'car_id': 'car_id_4',
                    'classes': ['comfortplus'],
                    'dbid': 'dbid',
                    'position': [0, 0],
                    'status': {'driver': 'free', 'taximeter': 'free'},
                    'unique_driver_id': 'udid4',
                    'uuid': 'uuid4',
                },
            ],
        }

    @mockserver.json_handler(
        '/driver-categories-api/v2/aggregation/categories',
    )
    def _(request):
        drivers = request.json['drivers']
        assert len(drivers) == 1
        driver_number = drivers[0]['driver_id'][-1:]
        return {
            'drivers': [
                {
                    'car_id': 'car_id_' + driver_number,
                    'categories': ['comfortplus'],
                    'driver_id': 'uuid' + driver_number,
                    'park_id': 'dbid',
                },
            ],
        }

    async def move_drivers(move_request, delay=2):
        await taxi_dispatch_airport.invalidate_caches()
        geobus_now = now + datetime.timedelta(seconds=delay)
        geobus_drivers = {}
        for drivers in move_request.values():
            for driver in drivers:
                geobus_drivers[driver['driver_id']] = {
                    'position': driver['position'],
                    'timestamp': geobus_now,
                }
        utils.publish_positions(redis_store, geobus_drivers, now)
        await merge_finished.wait_call()

        for zone in move_request:
            await taxi_dispatch_airport.run_task(
                'distlock/queue-update-scheduler-' + zone,
            )
            await utils.wait_certain_testpoint(zone, queue_update_finished)

    async def clean_database():
        cursor = pgsql['dispatch_airport'].cursor()
        cursor.execute('DELETE FROM dispatch_airport.drivers_queue;')
        await taxi_dispatch_airport.run_task('distlock/psql-cleaner')

    await taxi_dispatch_airport.enable_testpoints()
    await taxi_dispatch_airport.run_task('reset_business_statistics')

    config = taxi_config.get_values()['DISPATCH_AIRPORT_ZONES']
    config['ekb'].update({'terminal_area': 'ekb_airport_notification'})
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': config})

    #  check that entering wrong area does nothing
    await move_drivers(
        {
            'ekb': [
                {
                    'driver_id': 'dbid_uuid1',
                    'position': utils.AIRPORT_POSITION,
                },
            ],
            'svo': [
                {
                    'driver_id': 'dbid_uuid2',
                    'position': utils.SVO_WAITING_POSITION,
                },
            ],
        },
    )

    metric = await taxi_dispatch_airport_monitor.get_metric(
        'dispatch_airport_metrics',
    )
    assert metric['driver_entry'] == {
        '$meta': {'solomon_children_labels': 'airport_id'},
    }

    for i in range(5):
        await clean_database()

        now = now + datetime.timedelta(seconds=200)
        mocked_time.sleep(200)
        await move_drivers(
            {
                'ekb': [
                    {
                        'driver_id': 'dbid_uuid3',
                        'position': utils.NOTIFICATION_POSITION,
                    },
                ],
                'svo': [
                    {
                        'driver_id': 'dbid_uuid4',
                        'position': utils.SVO_AIRPORT_POSITION,
                    },
                ],
            },
        )

        await move_drivers(
            {
                'ekb': [
                    {
                        'driver_id': 'dbid_uuid3',
                        'position': utils.OUT_POSITION,
                    },
                ],
                'svo': [
                    {
                        'driver_id': 'dbid_uuid4',
                        'position': utils.SVO_OUT_POSITION,
                    },
                ],
            },
            4,
        )

        metric = (
            await taxi_dispatch_airport_monitor.get_metric(
                'dispatch_airport_metrics',
            )
        )['driver_entry']
        if i > 2:
            assert metric['svo'] == {
                'drivers_reached_max_allowed_entry_count': 1 if i > 1 else 0,
                'drivers_exceeded_max_allowed_entry_count': 1 if i > 2 else 0,
                'entry_events_exceeded_max_allowed_entry_count': (
                    i - 2 if i > 2 else 0
                ),
                'drivers_got_order_when_reached_enter_limit': 0,
            }
        assert metric['ekb'] == {
            'drivers_reached_max_allowed_entry_count': 1,
            'drivers_exceeded_max_allowed_entry_count': 1 if i > 0 else 0,
            'entry_events_exceeded_max_allowed_entry_count': i,
            'drivers_got_order_when_reached_enter_limit': 0,
        }

    mocked_time.sleep(30 * 60)
    now = now + datetime.timedelta(minutes=30)
    await clean_database()

    # check that period is resetting correctly
    await move_drivers(
        {
            'ekb': [
                {
                    'driver_id': 'dbid_uuid3',
                    'position': utils.NOTIFICATION_POSITION,
                },
            ],
            'svo': [
                {
                    'driver_id': 'dbid_uuid4',
                    'position': utils.SVO_AIRPORT_POSITION,
                },
            ],
        },
    )

    metric = (
        await taxi_dispatch_airport_monitor.get_metric(
            'dispatch_airport_metrics',
        )
    )['driver_entry']

    assert metric == {
        'svo': {
            'drivers_reached_max_allowed_entry_count': 1,
            'drivers_exceeded_max_allowed_entry_count': 1,
            'entry_events_exceeded_max_allowed_entry_count': 2,
            'drivers_got_order_when_reached_enter_limit': 0,
        },
        'ekb': {
            'drivers_reached_max_allowed_entry_count': 1,
            'drivers_exceeded_max_allowed_entry_count': 2,
            'entry_events_exceeded_max_allowed_entry_count': 5,
            'drivers_got_order_when_reached_enter_limit': 0,
        },
        '$meta': {'solomon_children_labels': 'airport_id'},
    }


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    DISPATCH_AIRPORT_DRIVER_EVENTS_PSQL_ENABLED=True,
    DISPATCH_AIRPORT_AREA_ENTRY_TRACKING={
        'ekb': {
            'marked_area_type': 'terminal',
            'maximum_number_of_entries': 2,
            'enter_accumulation_period': 30,
        },
    },
)
@pytest.mark.busy_drivers(
    busy_drivers=[
        {
            'driver_id': 'dbid_uuid1',
            'order_id': 'order_id_1',
            'taxi_status': 1,
            'final_destination': {'lat': 11.0, 'lon': 21.0},
        },
        {
            'driver_id': 'dbid_uuid2',
            'order_id': 'order_id_2',
            'taxi_status': 2,
            'final_destination': {'lat': 11.0, 'lon': 21.0},
        },
        {
            'driver_id': 'dbid_uuid3',
            'order_id': 'order_id_3',
            'taxi_status': 3,
            'final_destination': {'lat': 11.0, 'lon': 21.0},
        },
        {
            'driver_id': 'dbid_uuid4',
            'order_id': 'order_id_4',
            'taxi_status': 1,
            'final_destination': {'lat': 11.0, 'lon': 21.0},
        },
    ],
)
@pytest.mark.pgsql(
    'dispatch_airport',
    files=['orders_drivers_queue.sql', 'orders_driver_events.sql'],
)
@pytest.mark.now('2021-08-19T10:04:00+0000')
async def test_driver_entry_orders(
        taxi_dispatch_airport,
        testpoint,
        mockserver,
        taxi_dispatch_airport_monitor,
        order_archive_mock,
        load_json,
        pgsql,
):
    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @testpoint('got_order_when_reached_entry_limit')
    def got_order_when_reached_limit(driver_id):
        return driver_id

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        return utils.generate_candidates_response(
            request.json['driver_ids'], ['econom', 'comfortplus'],
        )

    @mockserver.json_handler(
        '/driver-categories-api/v2/aggregation/categories',
    )
    def _driver_categories(request):
        return utils.generate_categories_response(
            [driver['driver_id'] for driver in request.json['drivers']],
            ['comfortplus', 'econom'],
        )

    # dbid_uuid1 - 1 entry, new order
    # dbid_uuid2 - 2 entries, new order
    # dbid_uuid3 - 3 entries, same order
    # dbid_uuid4 - 3 entries, new order, in terminal area

    orders = load_json('orders.json')
    order_archive_mock.set_order_proc(orders)
    old_events = utils.get_driver_events(pgsql['dispatch_airport'])
    await taxi_dispatch_airport.enable_testpoints()
    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.run_task('reset_business_statistics')
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    metric = (
        await taxi_dispatch_airport_monitor.get_metric(
            'dispatch_airport_metrics',
        )
    )['driver_entry']
    assert metric == {
        'ekb': {
            'drivers_exceeded_max_allowed_entry_count': 0,
            'drivers_reached_max_allowed_entry_count': 0,
            'entry_events_exceeded_max_allowed_entry_count': 0,
            'drivers_got_order_when_reached_enter_limit': 1,
        },
        '$meta': {'solomon_children_labels': 'airport_id'},
    }

    assert utils.get_calls_sorted(
        got_order_when_reached_limit, 1, 'driver_id', None,
    ) == ['dbid_uuid2']

    events = utils.get_driver_events(pgsql['dispatch_airport'])
    assert old_events.items() <= events.items()
    new_events = {
        key: value for key, value in events.items() if key not in old_events
    }
    assert new_events == {
        (
            'udid2',
            'old_session_id2_1629367440order_id_2',
            'got_order_when_reached_enter_limit',
        ): {
            'airport_id': 'ekb',
            'driver_id': 'dbid_uuid2',
            'details': {'enter_exceeded_order_id': 'order_id_2'},
        },
    }


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    DISPATCH_AIRPORT_PICKUP_LINE_ALERT_SETTINGS={
        'svo_d_line1': {
            'used_classes': ['comfortplus', 'econom'],
            'available_drivers_airport_id': 'ekb',
            'available_drivers_threshold': 1,
        },
        'svo': {
            'used_classes': ['comfortplus', 'vip'],
            'available_drivers_airport_id': 'ekb',
            'available_drivers_threshold': 0,
        },
    },
)
@pytest.mark.pgsql(
    'dispatch_airport', files=['drivers_queue.sql', 'driver_events.sql'],
)
@pytest.mark.now('2021-08-19T10:04:00+0000')
async def test_pickup_line_driver_count_below_predict(
        taxi_dispatch_airport,
        taxi_dispatch_airport_monitor,
        taxi_config,
        load_json,
):

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.run_task(
        'business_metrics_collector.periodic_task',
    )

    # check when pickup line queue is empty

    metric = (
        await taxi_dispatch_airport_monitor.get_metric(
            'dispatch_airport_metrics',
        )
    )['queue']
    assert metric['svo_d_line1'] == {
        'comfortplus': {'pickup_line_driver_count_below_predict': 0},
        'econom': {'pickup_line_driver_count_below_predict': 0},
    }

    # econom is not processed
    # comfort has cars
    # vip has no cars, has predicted and available drivers

    metric = metric['svo']
    assert metric['comfortplus']['pickup_line_driver_count_below_predict'] == 0
    assert metric['vip']['pickup_line_driver_count_below_predict'] == 1

    config = taxi_config.get('DISPATCH_AIRPORT_PICKUP_LINE_ALERT_SETTINGS')
    config['svo']['available_drivers_threshold'] = 1
    taxi_config.set_values(
        {'DISPATCH_AIRPORT_PICKUP_LINE_ALERT_SETTINGS': config},
    )

    await taxi_dispatch_airport.invalidate_caches()
    metric = (
        await taxi_dispatch_airport_monitor.get_metric(
            'dispatch_airport_metrics',
        )
    )['queue']
    metric = metric['svo']

    # available drivers are now below threshold, metric isn't triggered

    assert metric['vip']['pickup_line_driver_count_below_predict'] == 0
