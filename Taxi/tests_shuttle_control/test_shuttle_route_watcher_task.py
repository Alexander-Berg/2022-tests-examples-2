# pylint: disable=import-only-modules, too-many-lines
import datetime
import json

import pytest

from tests_shuttle_control.utils import get_task_name
from tests_shuttle_control.utils import select_named


MOCK_NOW_DT = datetime.datetime(2020, 9, 14, 14, 15, 16)


@pytest.mark.now(MOCK_NOW_DT.isoformat())
@pytest.mark.parametrize(
    'ticket_check_enabled, expected_status',
    [(False, 'transporting'), (True, 'cancelled')],
)
@pytest.mark.config(
    SHUTTLE_CONTROL_BILLING_SETTINGS={
        'enabled': True,
        'requests_bulk_size': 1,
    },
    SHUTTLE_CONTROL_SAVE_USERSTATS={'enabled': True},
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_main(
        taxi_shuttle_control,
        mockserver,
        pgsql,
        experiments3,
        stq,
        stq_runner,
        driver_trackstory_v2_shorttracks,
        ticket_check_enabled,
        expected_status,
):
    @mockserver.json_handler('/user-api/users/search')
    def _mock_userapi(request):
        assert json.loads(request.get_data()) == {
            'primary_replica': False,
            'id': 'userid_1',
            'fields': ['application', 'phone_id', 'id'],
        }
        return {
            'items': [
                {
                    'id': 'userid_1',
                    'application': 'android',
                    'phone_id': '5da589137984b5db625a707f',
                },
            ],
        }

    def build_shorttrack_response():
        responses = {
            'dbid0_uuid0': {
                'lat': 55.75,
                'lon': 37.516,
                'speed': 20,
                'timestamp': 1600092910,
                'direction': 70,
                'accuracy': 1.0,
            },
        }

        response = {'data': []}
        for key, value in responses.items():
            response['data'].append(
                {'driver_id': key, 'raw': [value], 'adjusted': [value]},
            )

        return response

    driver_trackstory_v2_shorttracks.set_data(build_shorttrack_response())

    experiments3.add_config(
        name='shuttle_route_watcher_settings',
        consumers=['shuttle-control/route_watcher'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'general_settings': {
                'shuttle_speed_limit': 180,
                'time_window_shift': 180,
            },
            'not_on_route_settings': {'max_not_on_route_time': 180},
            'immobility_settings': {
                'min_shuttle_speed': 1,
                'min_speed_markers_to_account': 1,
            },
        },
    )

    query = (
        f'UPDATE state.shuttles '
        f'SET ticket_check_enabled = {ticket_check_enabled}'
    )
    pgsql['shuttle_control'].cursor().execute(query)

    response = await taxi_shuttle_control.post(
        'service/cron', json={'task_name': get_task_name()},
    )
    assert response.status_code == 200

    rows = select_named(
        'SELECT shuttles.shuttle_id, '
        'stp.lap, stp.begin_stop_id, stp.next_stop_id, stp.updated_at, '
        'stp.average_speed, stp.advanced_at, stp.block_reason, '
        'stp.processed_at '
        'FROM state.shuttles '
        'INNER JOIN state.shuttle_trip_progress stp '
        'ON shuttles.shuttle_id = stp.shuttle_id '
        'ORDER BY shuttle_id',
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'shuttle_id': 1,
            'begin_stop_id': 1,
            'next_stop_id': 3,
            'lap': 1,
            'updated_at': MOCK_NOW_DT,
            'average_speed': 72,
            'advanced_at': MOCK_NOW_DT,
            'processed_at': MOCK_NOW_DT,
            'block_reason': 'none',
        },
    ]

    rows = select_named(
        """
        SELECT sp.booking_id, sp.status, sp.finished_at,
        bt.status AS ticket_status, bt.code
        FROM state.passengers sp
        INNER JOIN state.booking_tickets bt
        ON sp.booking_id = bt.booking_id
        ORDER BY sp.booking_id, bt.code
        """,
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'booking_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'status': 'finished',
            'finished_at': MOCK_NOW_DT,
            'ticket_status': 'confirmed',
            'code': '123',
        },
        {
            'booking_id': '427a330d-2506-464a-accf-346b31e288b9',
            'status': expected_status,
            'finished_at': (
                MOCK_NOW_DT if expected_status == 'cancelled' else None
            ),
            'ticket_status': (
                'revoked' if expected_status == 'cancelled' else 'confirmed'
            ),
            'code': '124',
        },
    ]

    assert stq.shuttle_send_success_order_event.times_called == 1
    event = stq.shuttle_send_success_order_event.next_call()
    event.pop('id')
    event.pop('eta')
    event['kwargs'].pop('log_extra')
    assert event == {
        'queue': 'shuttle_send_success_order_event',
        'args': [],
        'kwargs': {
            'booking': {
                'booking_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
                'created_at': '2020-01-17T18:00:00+0000',
                'user_id': 'userid_1',
                'yandex_uid': '0123456789',
                'payment_type': 'cash',
            },
        },
    }
    await stq_runner.shuttle_send_success_order_event.call(
        task_id='id',
        args=[],
        kwargs={
            'booking': {
                'booking_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
                'created_at': '2020-01-17T18:00:00+0000',
                'user_id': 'userid_1',
                'yandex_uid': '0123456789',
            },
        },
    )

    assert _mock_userapi.times_called == 1
    assert stq.userstats_order_complete.times_called == 1
    assert stq.success_shuttle_order_adjust_events.times_called == 1
    event = stq.userstats_order_complete.next_call()
    event.pop('id')
    event.pop('eta')
    event['kwargs'].pop('log_extra')
    assert event == {
        'queue': 'userstats_order_complete',
        'args': [],
        'kwargs': {
            'application': 'android',
            'phone_id': {'$oid': '5da589137984b5db625a707f'},
            'order_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'order_created': {'$date': '2020-01-17T18:00:00.000Z'},
            'tariff_class': 'shuttle',
            'payment_type': 'cash',
        },
    }
    event = stq.success_shuttle_order_adjust_events.next_call()
    event.pop('id')
    event.pop('eta')
    event['kwargs'].pop('log_extra')
    assert event == {
        'queue': 'success_shuttle_order_adjust_events',
        'args': [],
        'kwargs': {
            'app_name': 'android',
            'phone_id': '5da589137984b5db625a707f',
            'order_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'created_at': '2020-01-17T18:00:00.000000Z',
            'user_id': 'userid_1',
            'yandex_uid': '0123456789',
        },
    }

    rows = select_named(
        """
        SELECT * FROM state.order_billing_requests
        """,
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'request_id': 1,
            'booking_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'doc_id': None,
            'finished_at': None,
            'timezone': 'Europe/Moscow',
            'nearest_zone': None,
            'state': 'requested',
        },
    ]


@pytest.mark.now(MOCK_NOW_DT.isoformat())
@pytest.mark.config(
    SHUTTLE_CONTROL_BILLING_SETTINGS={
        'enabled': False,
        'requests_bulk_size': 1,
    },
)
@pytest.mark.parametrize(
    'stop, alter_statuses, cancel_bookings',
    [(2, True, False)],  # TODO(dvinokurov): return booking cancel check,
)
@pytest.mark.pgsql('shuttle_control', files=['main_dynamic_route.sql'])
async def test_main_dynamic_route(
        taxi_shuttle_control,
        mockserver,
        pgsql,
        experiments3,
        driver_trackstory_v2_shorttracks,
        stop,
        alter_statuses,
        cancel_bookings,
):
    def build_shorttrack_response():
        stops_coords = {
            2: {'lat': 55.750449, 'lon': 37.509801},
            4: {'lat': 55.750135, 'lon': 37.529171},
        }

        responses = {
            'dbid0_uuid0': [
                {  # near the nth stop
                    'lat': stops_coords[stop]['lat'],
                    'lon': stops_coords[stop]['lon'],
                    'speed': 20,
                    'timestamp': 1600092910,
                    'direction': 70,
                    'accuracy': 1.0,
                },
                {  # near the 3rd stop
                    'lat': 55.750182,
                    'lon': 37.520180,
                    'speed': 20,
                    'timestamp': 1600092910,
                    'direction': 70,
                    'accuracy': 1.0,
                },
                {
                    'lat': 60,
                    'lon': 40,
                    'speed': 20,
                    'timestamp': 1600092910,
                    'direction': 70,
                    'accuracy': 1.0,
                },
            ],
        }

        response = {'data': []}
        for key, value in responses.items():
            response['data'].append(
                {'driver_id': key, 'raw': value, 'adjusted': value},
            )

        return response

    driver_trackstory_v2_shorttracks.set_data(build_shorttrack_response())

    experiments3.add_config(
        name='shuttle_dynamic_route_watcher_settings',
        consumers=['shuttle-control/route_watcher'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'max_non_flapped_speed': 100,
            'stop_adjusting_radius': 100,
            'cancel_bookings': cancel_bookings,
        },
    )

    response = await taxi_shuttle_control.post(
        'service/cron', json={'task_name': get_task_name()},
    )
    assert response.status_code == 200

    rows = select_named(
        'SELECT shuttles.shuttle_id, '
        'stp.lap, stp.begin_stop_id, stp.next_stop_id, stp.updated_at, '
        'stp.average_speed, stp.advanced_at, stp.block_reason, '
        'stp.processed_at, stp.stop_arrival_timestamp, '
        'stp.arrived_stop_id '
        'FROM state.shuttles '
        'INNER JOIN state.shuttle_trip_progress stp '
        'ON shuttles.shuttle_id = stp.shuttle_id '
        'ORDER BY shuttle_id',
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'shuttle_id': 1,
            'begin_stop_id': 1,
            'next_stop_id': 2,
            'lap': 1,
            'updated_at': datetime.datetime(2020, 9, 14, 10, 15, 16),
            'average_speed': None,
            'advanced_at': MOCK_NOW_DT,
            'processed_at': MOCK_NOW_DT,
            'block_reason': 'none',
            'stop_arrival_timestamp': MOCK_NOW_DT,
            'arrived_stop_id': 2,
        },
    ]

    rows = select_named(
        """
        SELECT sp.booking_id, sp.status, sp.finished_at,
        bt.status AS ticket_status, bt.code
        FROM state.passengers sp
        INNER JOIN state.booking_tickets bt
        ON sp.booking_id = bt.booking_id
        ORDER BY sp.booking_id, bt.code
        """,
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'booking_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'status': 'transporting',
            'finished_at': None,
            'ticket_status': 'confirmed',
            'code': '123',
        },
        {
            'booking_id': '427a330d-2506-464a-accf-346b31e288b9',
            'status': (
                'cancelled'
                if alter_statuses and cancel_bookings
                else 'driving'
            ),
            'finished_at': (
                MOCK_NOW_DT if alter_statuses and cancel_bookings else None
            ),
            'ticket_status': (
                'revoked' if alter_statuses and cancel_bookings else 'issued'
            ),
            'code': '124',
        },
    ]

    rows = select_named(
        """
        SELECT * FROM state.order_billing_requests
        """,
        pgsql['shuttle_control'],
    )

    assert rows == []


@pytest.mark.skip(reason='Flaps detection is disabled now')
@pytest.mark.now(MOCK_NOW_DT.isoformat())
@pytest.mark.config(
    SHUTTLE_CONTROL_BILLING_SETTINGS={
        'enabled': False,
        'requests_bulk_size': 1,
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main_dynamic_route.sql'])
async def test_dynamic_route_flaps(
        taxi_shuttle_control,
        mockserver,
        pgsql,
        experiments3,
        driver_trackstory_v2_shorttracks,
):
    def build_shorttrack_response():
        responses = {
            'dbid0_uuid0': [
                {  # near the 2nd stop, before processed_at
                    'lat': 55.750449,
                    'lon': 37.509801,
                    'speed': 20,
                    'timestamp': 1600078455,
                    'direction': 70,
                    'accuracy': 1.0,
                },
                {  # near the 4th stop, flap, dist ~1.88km
                    'lat': 55.750135,
                    'lon': 37.529171,
                    'speed': 20,
                    'timestamp': 1600078521,
                    'direction': 70,
                    'accuracy': 1.0,
                },
                {
                    'lat': 60,
                    'lon': 40,
                    'speed': 20,
                    'timestamp': 1600092910,
                    'direction': 70,
                    'accuracy': 1.0,
                },
            ],
        }

        response = {'data': []}
        for key, value in responses.items():
            response['data'].append(
                {'driver_id': key, 'raw': value, 'adjusted': value},
            )

        return response

    driver_trackstory_v2_shorttracks.set_data(build_shorttrack_response())

    experiments3.add_config(
        name='shuttle_dynamic_route_watcher_settings',
        consumers=['shuttle-control/route_watcher'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'max_non_flapped_speed': 350,
            'stop_adjusting_radius': 100,
            'cancel_bookings': True,
        },
    )

    response = await taxi_shuttle_control.post(
        'service/cron', json={'task_name': get_task_name()},
    )
    assert response.status_code == 200

    rows = select_named(
        'SELECT shuttles.shuttle_id, '
        'stp.lap, stp.begin_stop_id, stp.next_stop_id, stp.updated_at, '
        'stp.average_speed, stp.advanced_at, stp.block_reason, '
        'stp.processed_at '
        'FROM state.shuttles '
        'INNER JOIN state.shuttle_trip_progress stp '
        'ON shuttles.shuttle_id = stp.shuttle_id '
        'ORDER BY shuttle_id',
        pgsql['shuttle_control'],
    )

    prev_now_dt = datetime.datetime(2020, 9, 14, 10, 15, 16)
    assert rows == [
        {
            'shuttle_id': 1,
            'begin_stop_id': 1,
            'next_stop_id': 1,
            'lap': 0,
            'updated_at': prev_now_dt,
            'average_speed': None,
            'advanced_at': prev_now_dt,
            'processed_at': MOCK_NOW_DT,
            'block_reason': 'none',
        },
    ]

    rows = select_named(
        """
        SELECT sp.booking_id, sp.status, sp.finished_at,
        bt.status AS ticket_status, bt.code
        FROM state.passengers sp
        INNER JOIN state.booking_tickets bt
        ON sp.booking_id = bt.booking_id
        ORDER BY sp.booking_id, bt.code
        """,
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'booking_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'status': 'transporting',
            'finished_at': None,
            'ticket_status': 'confirmed',
            'code': '123',
        },
        {
            'booking_id': '427a330d-2506-464a-accf-346b31e288b9',
            'status': 'driving',
            'finished_at': None,
            'ticket_status': 'issued',
            'code': '124',
        },
    ]

    rows = select_named(
        """
        SELECT * FROM state.order_billing_requests
        """,
        pgsql['shuttle_control'],
    )

    assert rows == []


@pytest.mark.now(MOCK_NOW_DT.isoformat())
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_main_immobility(
        taxi_shuttle_control,
        mockserver,
        pgsql,
        experiments3,
        driver_trackstory_v2_shorttracks,
):
    def build_shorttrack_response():
        responses = {
            'dbid0_uuid0': [
                {
                    'lat': 55.75,
                    'lon': 37.516,
                    'speed': 20,
                    'timestamp': 1600092910,
                    'direction': 70,
                    'accuracy': 1.0,
                },
                {
                    'lat': 55.75,
                    'lon': 37.516,
                    'speed': 40,
                    'timestamp': 1600092912,
                    'direction': 70,
                    'accuracy': 1.0,
                },
            ],
        }

        response = {'data': []}
        for key, values in responses.items():
            response['data'].append(
                {'driver_id': key, 'raw': values, 'adjusted': values},
            )

        return response

    driver_trackstory_v2_shorttracks.set_data(build_shorttrack_response())

    experiments3.add_config(
        name='shuttle_route_watcher_settings',
        consumers=['shuttle-control/route_watcher'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'general_settings': {
                'shuttle_speed_limit': 180,
                'time_window_shift': 180,
            },
            'not_on_route_settings': {'max_not_on_route_time': 180},
            'immobility_settings': {
                'min_shuttle_speed': 110,
                'min_speed_markers_to_account': 2,
            },
        },
    )

    response = await taxi_shuttle_control.post(
        'service/cron', json={'task_name': get_task_name()},
    )
    assert response.status_code == 200

    rows = select_named(
        'SELECT shuttles.shuttle_id, '
        'stp.lap, stp.begin_stop_id, stp.next_stop_id, stp.updated_at, '
        'stp.average_speed, stp.advanced_at, stp.block_reason '
        'FROM state.shuttles '
        'INNER JOIN state.shuttle_trip_progress stp '
        'ON shuttles.shuttle_id = stp.shuttle_id '
        'ORDER BY shuttle_id',
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'shuttle_id': 1,
            'begin_stop_id': 1,
            'next_stop_id': 3,
            'lap': 1,
            'updated_at': MOCK_NOW_DT,
            'average_speed': 108.0,
            'advanced_at': MOCK_NOW_DT,
            'block_reason': 'immobility',
        },
    ]


@pytest.mark.now(MOCK_NOW_DT.isoformat())
@pytest.mark.pgsql('shuttle_control', files=['main.sql', 'workshifts.sql'])
async def test_main_out_of_workshift(
        taxi_shuttle_control,
        mockserver,
        pgsql,
        experiments3,
        driver_trackstory_v2_shorttracks,
):
    def build_shorttrack_response():
        responses = {
            'dbid0_uuid0',
            'dbid1_uuid1',
            'dbid2_uuid2',
            'dbid3_uuid3',
            'dbid4_uuid4',
        }
        arr = [
            {
                'lat': 55.75,
                'lon': 37.516,
                'speed': 20,
                'timestamp': 1600092910,
                'direction': 70,
                'accuracy': 1.0,
            },
            {
                'lat': 55.75,
                'lon': 37.516,
                'speed': 40,
                'timestamp': 1600092912,
                'direction': 70,
                'accuracy': 1.0,
            },
        ]

        response = {'data': []}
        for key in responses:
            response['data'].append(
                {'driver_id': key, 'raw': arr, 'adjusted': arr},
            )

        return response

    driver_trackstory_v2_shorttracks.set_data(build_shorttrack_response())

    experiments3.add_config(
        name='shuttle_route_watcher_settings',
        consumers=['shuttle-control/route_watcher'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'general_settings': {
                'shuttle_speed_limit': 180,
                'time_window_shift': 180,
            },
            'not_on_route_settings': {'max_not_on_route_time': 180},
            'immobility_settings': {
                'min_shuttle_speed': 1,
                'min_speed_markers_to_account': 2,
            },
        },
    )

    response = await taxi_shuttle_control.post(
        'service/cron', json={'task_name': get_task_name()},
    )
    assert response.status_code == 200

    rows = select_named(
        'SELECT shuttles.shuttle_id, '
        'stp.lap, stp.begin_stop_id, stp.next_stop_id, stp.updated_at, '
        'stp.average_speed, stp.advanced_at, stp.block_reason '
        'FROM state.shuttles '
        'INNER JOIN state.shuttle_trip_progress stp '
        'ON shuttles.shuttle_id = stp.shuttle_id '
        'ORDER BY shuttle_id',
        pgsql['shuttle_control'],
    )

    assert rows == [
        # смена закончена, но есть заказ
        {
            'shuttle_id': 1,
            'begin_stop_id': 1,
            'next_stop_id': 3,
            'lap': 1,
            'updated_at': MOCK_NOW_DT,
            'average_speed': 108.0,
            'advanced_at': MOCK_NOW_DT,
            'block_reason': 'none',
        },
        # смена закончене, заказов нет
        {
            'shuttle_id': 4,
            'begin_stop_id': 1,
            'next_stop_id': 3,
            'lap': 1,
            'updated_at': MOCK_NOW_DT,
            'average_speed': 108.0,
            'advanced_at': MOCK_NOW_DT,
            'block_reason': 'out_of_workshift',
        },
        # смена не закончена
        {
            'shuttle_id': 5,
            'begin_stop_id': 1,
            'next_stop_id': 3,
            'lap': 1,
            'updated_at': MOCK_NOW_DT,
            'average_speed': 108.0,
            'advanced_at': MOCK_NOW_DT,
            'block_reason': 'none',
        },
    ]


@pytest.mark.now(MOCK_NOW_DT.isoformat())
@pytest.mark.parametrize(
    'bad_position',
    [True, False],  # return either bad position, or no shorttrack
)
@pytest.mark.pgsql(
    'shuttle_control', files=['main.sql', 'upd_shuttle_on_route.sql'],
)
async def test_main_not_on_route(
        taxi_shuttle_control,
        mockserver,
        load,
        pgsql,
        experiments3,
        bad_position,
        driver_trackstory_v2_shorttracks,
):
    def build_shorttrack_response():
        responses = {
            'dbid0_uuid0': {
                'lat': 0,
                'lon': 0,
                'speed': 20,
                'timestamp': 1600092910,
                'direction': 70,
                'accuracy': 1.0,
            },
        }

        response = {'data': []}
        for key, value in responses.items():
            response['data'].append(
                {'driver_id': key, 'raw': [value], 'adjusted': [value]},
            )

        return response

    if bad_position:
        driver_trackstory_v2_shorttracks.set_data(build_shorttrack_response())
    else:
        driver_trackstory_v2_shorttracks.throw_exception()

    experiments3.add_config(
        name='shuttle_route_watcher_settings',
        consumers=['shuttle-control/route_watcher'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'general_settings': {
                'shuttle_speed_limit': 180,
                'time_window_shift': 180,
            },
            'not_on_route_settings': {'max_not_on_route_time': 180},
            'immobility_settings': {
                'min_shuttle_speed': 1,
                'min_speed_markers_to_account': 1,
            },
        },
    )

    response = await taxi_shuttle_control.post(
        'service/cron', json={'task_name': get_task_name()},
    )
    assert response.status_code == 200

    rows = select_named(
        'SELECT shuttles.shuttle_id, '
        'stp.lap, stp.begin_stop_id, stp.next_stop_id, stp.updated_at, '
        'stp.average_speed, stp.advanced_at, stp.block_reason, '
        'stp.processed_at '
        'FROM state.shuttles '
        'INNER JOIN state.shuttle_trip_progress stp '
        'ON shuttles.shuttle_id = stp.shuttle_id '
        'ORDER BY shuttle_id',
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'shuttle_id': 1,
            'begin_stop_id': 1,
            'next_stop_id': 2,
            'lap': 1,
            'updated_at': datetime.datetime(2020, 9, 14, 9, 15, 16),
            'processed_at': datetime.datetime(2020, 9, 14, 14, 15, 16),
            'average_speed': None,
            'advanced_at': datetime.datetime(2020, 9, 14, 10, 15, 16),
            'block_reason': 'not_on_route',
        },
    ]


@pytest.mark.now(MOCK_NOW_DT.isoformat())
@pytest.mark.pgsql(
    'shuttle_control', files=['main.sql', 'insert_shuttles.sql'],
)
async def test_chunk_updating(
        taxi_shuttle_control,
        mockserver,
        load,
        pgsql,
        experiments3,
        driver_trackstory_v2_shorttracks,
):
    def build_shorttrack_response():
        responses = {'dbid0_uuid0', 'dbid1_uuid1', 'dbid2_uuid2'}

        response = {'data': []}
        for key in responses:
            response['data'].append(
                {
                    'driver_id': key,
                    'raw': [
                        {
                            'lat': 55.75,
                            'lon': 37.516,
                            'speed': 20,
                            'timestamp': 1600092910,
                            'direction': 70,
                            'accuracy': 1.0,
                        },
                    ],
                    'adjusted': [
                        {
                            'lat': 55.75,
                            'lon': 37.516,
                            'speed': 20,
                            'timestamp': 1600092910,
                            'direction': 70,
                            'accuracy': 1.0,
                        },
                    ],
                },
            )

        return response

    driver_trackstory_v2_shorttracks.set_data(build_shorttrack_response())

    experiments3.add_config(
        name='shuttle_route_watcher_settings',
        consumers=['shuttle-control/route_watcher'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'general_settings': {
                'shuttle_speed_limit': 180,
                'time_window_shift': 180,
            },
            'not_on_route_settings': {'max_not_on_route_time': 180},
            'immobility_settings': {
                'min_shuttle_speed': 1,
                'min_speed_markers_to_account': 1,
            },
        },
    )

    response = await taxi_shuttle_control.post(
        'service/cron', json={'task_name': get_task_name()},
    )
    assert response.status_code == 200

    rows = select_named(
        'SELECT * FROM state.shuttle_trip_progress ORDER BY shuttle_id ',
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'shuttle_id': 1,
            'lap': 1,
            'begin_stop_id': 1,
            'next_stop_id': 3,
            'updated_at': datetime.datetime(2020, 9, 14, 14, 15, 16),
            'average_speed': 72.0,
            'advanced_at': datetime.datetime(2020, 9, 14, 14, 15, 16),
            'processed_at': datetime.datetime(2020, 9, 14, 14, 15, 16),
            'block_reason': 'none',
            'end_lap': None,
            'end_stop_id': None,
            'stop_arrival_timestamp': None,
            'arrived_stop_id': None,
        },
        {
            'shuttle_id': 2,
            'lap': 1,
            'begin_stop_id': 1,
            'next_stop_id': 3,
            'updated_at': datetime.datetime(2020, 9, 14, 14, 15, 16),
            'average_speed': 72.0,
            'advanced_at': datetime.datetime(2020, 9, 14, 14, 15, 16),
            'processed_at': datetime.datetime(2020, 9, 14, 14, 15, 16),
            'block_reason': 'none',
            'end_lap': None,
            'end_stop_id': None,
            'stop_arrival_timestamp': None,
            'arrived_stop_id': None,
        },
        {
            'shuttle_id': 3,
            'lap': 1,
            'begin_stop_id': 1,
            'next_stop_id': 3,
            'updated_at': datetime.datetime(2020, 9, 14, 14, 15, 16),
            'average_speed': 72.0,
            'advanced_at': datetime.datetime(2020, 9, 14, 14, 15, 16),
            'processed_at': datetime.datetime(2020, 9, 14, 14, 15, 16),
            'block_reason': 'none',
            'end_lap': None,
            'end_stop_id': None,
            'stop_arrival_timestamp': None,
            'arrived_stop_id': None,
        },
    ]


@pytest.mark.now(MOCK_NOW_DT.isoformat())
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_WATCHER_GLOBAL_SETTINGS={'shuttles_chunk_size': 5},
)
@pytest.mark.pgsql(
    'shuttle_control', files=['main.sql', 'insert_many_shuttles.sql'],
)
async def test_shuttles_more_than_chunk(
        taxi_shuttle_control,
        mockserver,
        pgsql,
        experiments3,
        driver_trackstory_v2_shorttracks,
):
    def build_shorttrack_response():
        responses = {
            'dbid0_uuid0',
            'dbid1_uuid1',
            'dbid2_uuid2',
            'dbid3_uuid2',
            'dbid4_uuid2',
            'dbid5_uuid2',
            'dbid6_uuid2',
        }

        response = {'data': []}
        for key in responses:
            response['data'].append(
                {
                    'driver_id': key,
                    'raw': [
                        {
                            'lat': 55.75,
                            'lon': 37.516,
                            'speed': 20,
                            'timestamp': 1600092910,
                            'direction': 70,
                            'accuracy': 1.0,
                        },
                    ],
                    'adjusted': [
                        {
                            'lat': 55.75,
                            'lon': 37.516,
                            'speed': 20,
                            'timestamp': 1600092910,
                            'direction': 70,
                            'accuracy': 1.0,
                        },
                    ],
                },
            )

        return response

    driver_trackstory_v2_shorttracks.set_data(build_shorttrack_response())

    experiments3.add_config(
        name='shuttle_route_watcher_settings',
        consumers=['shuttle-control/route_watcher'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'general_settings': {
                'shuttle_speed_limit': 180,
                'time_window_shift': 180,
            },
            'not_on_route_settings': {'max_not_on_route_time': 180},
            'immobility_settings': {
                'min_shuttle_speed': 1,
                'min_speed_markers_to_account': 1,
            },
        },
    )

    response = await taxi_shuttle_control.post(
        'service/cron', json={'task_name': get_task_name()},
    )
    assert response.status_code == 200

    rows = select_named(
        'SELECT * FROM state.shuttle_trip_progress ORDER BY shuttle_id ',
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'shuttle_id': 1,
            'lap': 1,
            'begin_stop_id': 1,
            'next_stop_id': 3,
            'updated_at': MOCK_NOW_DT,
            'average_speed': 72.0,
            'advanced_at': MOCK_NOW_DT,
            'processed_at': MOCK_NOW_DT,
            'block_reason': 'none',
            'end_lap': None,
            'end_stop_id': None,
            'stop_arrival_timestamp': None,
            'arrived_stop_id': None,
        },
        {
            'shuttle_id': 2,
            'lap': 1,
            'begin_stop_id': 1,
            'next_stop_id': 3,
            'updated_at': MOCK_NOW_DT,
            'average_speed': 72.0,
            'advanced_at': MOCK_NOW_DT,
            'processed_at': MOCK_NOW_DT,
            'block_reason': 'none',
            'end_lap': None,
            'end_stop_id': None,
            'stop_arrival_timestamp': None,
            'arrived_stop_id': None,
        },
        {
            'shuttle_id': 3,
            'lap': 1,
            'begin_stop_id': 1,
            'next_stop_id': 3,
            'updated_at': MOCK_NOW_DT,
            'average_speed': 72.0,
            'advanced_at': MOCK_NOW_DT,
            'processed_at': MOCK_NOW_DT,
            'block_reason': 'none',
            'end_lap': None,
            'end_stop_id': None,
            'stop_arrival_timestamp': None,
            'arrived_stop_id': None,
        },
        {
            'shuttle_id': 4,
            'lap': 1,
            'begin_stop_id': 1,
            'next_stop_id': 3,
            'updated_at': MOCK_NOW_DT,
            'average_speed': 72.0,
            'advanced_at': MOCK_NOW_DT,
            'processed_at': MOCK_NOW_DT,
            'block_reason': 'none',
            'end_lap': None,
            'end_stop_id': None,
            'stop_arrival_timestamp': None,
            'arrived_stop_id': None,
        },
        {
            'shuttle_id': 5,
            'lap': 1,
            'begin_stop_id': 1,
            'next_stop_id': 3,
            'updated_at': MOCK_NOW_DT,
            'average_speed': 72.0,
            'advanced_at': MOCK_NOW_DT,
            'processed_at': MOCK_NOW_DT,
            'block_reason': 'none',
            'end_lap': None,
            'end_stop_id': None,
            'stop_arrival_timestamp': None,
            'arrived_stop_id': None,
        },
        # this shuttle doesn't fit into chunk
        {
            'shuttle_id': 6,
            'lap': 1,
            'begin_stop_id': 1,
            'next_stop_id': 2,
            'updated_at': datetime.datetime(2020, 9, 14, 10, 15, 16),
            'average_speed': None,
            'advanced_at': datetime.datetime(2020, 9, 14, 10, 15, 16),
            'processed_at': datetime.datetime(2020, 9, 14, 10, 15, 17),
            'block_reason': 'not_on_route',
            'end_lap': None,
            'end_stop_id': None,
            'stop_arrival_timestamp': None,
            'arrived_stop_id': None,
        },
    ]


@pytest.mark.now(MOCK_NOW_DT.isoformat())
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_WATCHER_GLOBAL_SETTINGS={'shuttles_chunk_size': 5},
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'position_lon,booking_is_finished',
    [(37.504, False), (37.508, False), (37.513, True), (37.518, True)],
)
async def test_shuttle_dropoff_passenger(
        taxi_shuttle_control,
        mockserver,
        pgsql,
        experiments3,
        driver_trackstory_v2_shorttracks,
        position_lon,
        booking_is_finished,
):
    def build_shorttrack_response():
        responses = {
            'dbid0_uuid0': {
                'lat': 55.75,
                'lon': position_lon,
                'speed': 20,
                'timestamp': 1600092910,
                'direction': 70,
                'accuracy': 1.0,
            },
        }

        response = {'data': []}
        for key, value in responses.items():
            response['data'].append(
                {'driver_id': key, 'raw': [value], 'adjusted': [value]},
            )

        return response

    driver_trackstory_v2_shorttracks.set_data(build_shorttrack_response())

    experiments3.add_config(
        name='shuttle_route_watcher_settings',
        consumers=['shuttle-control/route_watcher'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'general_settings': {
                'shuttle_speed_limit': 180,
                'time_window_shift': 180,
            },
            'not_on_route_settings': {'max_not_on_route_time': 180},
            'immobility_settings': {
                'min_shuttle_speed': 1,
                'min_speed_markers_to_account': 1,
            },
        },
    )

    response = await taxi_shuttle_control.post(
        'service/cron', json={'task_name': get_task_name()},
    )
    assert response.status_code == 200

    rows = select_named(
        """
        SELECT sp.status, sp.finished_at, bt.status AS ticket_status, bt.code
        FROM state.passengers sp
        INNER JOIN state.booking_tickets bt
        ON sp.booking_id = bt.booking_id
        WHERE sp.booking_id = '2fef68c9-25d0-4174-9dd0-bdd1b3730775'
        """,
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'status': 'finished' if booking_is_finished else 'transporting',
            'finished_at': MOCK_NOW_DT if booking_is_finished else None,
            'ticket_status': 'confirmed',
            'code': '123',
        },
    ]


@pytest.mark.now(MOCK_NOW_DT.isoformat())
@pytest.mark.pgsql(
    'shuttle_control',
    files=['main.sql', 'workshifts.sql', 'insert_shuttles.sql', 'pauses.sql'],
)
async def test_switch_pause(
        taxi_shuttle_control,
        mockserver,
        pgsql,
        experiments3,
        driver_trackstory_v2_shorttracks,
):
    def build_shorttrack_response():
        profiles = ['dbid0_uuid0', 'dbid1_uuid1', 'dbid2_uuid2']

        data = []
        for profile in profiles:
            data.append(
                {
                    'driver_id': profile,
                    'raw': [
                        {
                            'lat': 55.75,
                            'lon': 37.516,
                            'speed': 20,
                            'timestamp': 1600092910,
                        },
                    ],
                    'adjusted': [
                        {
                            'lat': 55.75,
                            'lon': 37.516,
                            'speed': 20,
                            'timestamp': 1600092910,
                        },
                    ],
                },
            )
        return {'data': data}

    driver_trackstory_v2_shorttracks.set_data(build_shorttrack_response())

    experiments3.add_config(
        name='shuttle_route_watcher_settings',
        consumers=['shuttle-control/route_watcher'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'general_settings': {
                'shuttle_speed_limit': 180,
                'time_window_shift': 180,
            },
            'not_on_route_settings': {'max_not_on_route_time': 180},
            'immobility_settings': {
                'min_shuttle_speed': 1,
                'min_speed_markers_to_account': 1,
            },
        },
    )

    response = await taxi_shuttle_control.post(
        'service/cron', json={'task_name': get_task_name()},
    )
    assert response.status_code == 200

    rows = select_named(
        'SELECT sp.booking_id, sp.status, sp.shuttle_id '
        'FROM state.passengers sp '
        'ORDER BY sp.shuttle_id, sp.booking_id',
        pgsql['shuttle_control'],
    )
    assert rows == [
        {
            'booking_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'status': 'finished',
            'shuttle_id': 1,
        },
        {
            'booking_id': '427a330d-2506-464a-accf-346b31e288b9',
            'status': 'transporting',
            'shuttle_id': 1,
        },
        {
            'booking_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730001',
            'status': 'finished',
            'shuttle_id': 2,
        },
        {
            'booking_id': '427a330d-2506-464a-accf-346b31e20002',
            'status': 'cancelled',
            'shuttle_id': 2,
        },
    ]

    rows = select_named(
        'SELECT shuttle_id, pause_state, pause_id '
        'FROM state.shuttles '
        'ORDER BY shuttle_id',
        pgsql['shuttle_control'],
    )
    assert rows == [
        {'shuttle_id': 1, 'pause_state': 'requested', 'pause_id': 1},
        {'shuttle_id': 2, 'pause_state': 'in_work', 'pause_id': 2},
        {'shuttle_id': 3, 'pause_state': 'inactive', 'pause_id': None},
        {'shuttle_id': 4, 'pause_state': 'inactive', 'pause_id': None},
        {'shuttle_id': 5, 'pause_state': 'inactive', 'pause_id': None},
    ]

    rows = select_named(
        'SELECT pause_id, shuttle_id, pause_requested,'
        ' pause_started, pause_finished, expected_pause_finish '
        'FROM state.pauses',
        pgsql['shuttle_control'],
    )
    assert rows == [
        {
            'pause_id': 1,
            'shuttle_id': 1,
            'pause_requested': datetime.datetime(2020, 9, 14, 14, 5, 55),
            'pause_started': None,
            'expected_pause_finish': None,
            'pause_finished': None,
        },
        {
            'pause_id': 2,
            'shuttle_id': 2,
            'pause_requested': datetime.datetime(2020, 9, 14, 14, 6, 55),
            'pause_started': datetime.datetime(2020, 9, 14, 14, 15, 16),
            'expected_pause_finish': datetime.datetime(
                2020, 9, 14, 14, 25, 16,
            ),
            'pause_finished': None,
        },
    ]
