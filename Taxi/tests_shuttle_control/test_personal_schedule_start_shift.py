# pylint: disable=import-only-modules, import-error, redefined-outer-name
import datetime

import pytest

from tests_shuttle_control.utils import select_named
from tests_shuttle_control.utils import stringify_detailed_view


class AnyNumber:
    def __eq__(self, other):
        return isinstance(other, int)


HEADERS = {
    'X-Request-Application': 'taximeter',
    'X-Request-Platform': 'android',
    'X-Request-Application-Version': '9.07',
    'X-YaTaxi-Park-Id': '111',
    'X-YaTaxi-Driver-Profile-Id': '888',
    'Accept-Language': 'ru',
}

NOW = datetime.datetime(2020, 6, 4, 10, 35, 21)


@pytest.fixture
def mocks_external(mockserver):
    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_shorttrack(request):
        return {
            'type': 'adjusted',
            'position': {
                'lat': 55.717235,
                'lon': 37.633790,
                'timestamp': 1600092910,
            },
        }

    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _mock_ui_profile(request):
        return {'display_mode': 'shuttle', 'display_profile': 'shuttle_fix'}

    @mockserver.json_handler('/driver-fix/v1/internal/status')
    def _mock_driver_fix(request):
        return {
            'time': {'seconds': 240, 'localized': '4 мин'},
            'guaranteed_money': {
                'value': 1999.85,
                'currency': 'RUB',
                'localized': '1999.85 руб.',
            },
            'cash_income': {
                'value': 0,
                'currency': 'RUB',
                'localized': '0 руб.',
            },
            'payoff': {'value': 0, 'currency': 'RUB', 'localized': '0 руб.'},
            'commission': {
                'value': 0,
                'currency': 'RUB',
                'localized': '0 руб.',
            },
            'total_income': {
                'value': 0,
                'currency': 'RUB',
                'localized': '0 руб.',
            },
        }


@pytest.fixture
def mocks_experiments(experiments3, start_shift):
    experiments3.add_config(
        name='shuttle_capacity',
        consumers=['shuttle-control/start_shift'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/start_shift'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'seats_available': 2},
            },
        ],
    )

    experiments3.add_config(
        name='shuttle_tickets_settings',
        consumers=['shuttle-control/start_shift'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/start_shift'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'route_1',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'enabled': True,
                    'ticket_length': 3,
                    'ticket_check_enabled': True,
                },
            },
        ],
    )

    experiments3.add_config(
        name='shuttle_status_settings',
        consumers=['shuttle-control/start_shift', 'shuttle-control/polling'],
        match={
            'enabled': True,
            'consumers': [
                {'name': 'shuttle-control/start_shift'},
                {'name': 'shuttle-control/polling'},
            ],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'pass_via_before_stop': False,
                    'remaining_distance': 100,
                    'stops_display_limit': 3,
                    'cyclic_route_points_limit_forward': 6,
                    'cyclic_route_points_limit_back': 0,
                    'prevent_early_stop': True,
                },
            },
        ],
    )

    experiments3.add_config(
        name='shuttle_shift_time_control',
        consumers=['shuttle-control/shift_time_control'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/shift_time_control'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'route_1',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'reservation_available': {
                        'from': {
                            'starting_point': 'scheduled_shift_start',
                            'time_direction': 'backward',
                            'time_amount': {'unit': 'hour', 'value': 2},
                        },
                        'to': {
                            'starting_point': 'scheduled_shift_start',
                            'time_direction': 'backward',
                            'time_amount': {'unit': 'minute', 'value': 10},
                        },
                    },
                    'start_shift_available': {
                        'from': {
                            'starting_point': 'scheduled_shift_start',
                            'time_direction': 'backward',
                            'time_amount': {
                                'unit': 'minute',
                                'value': start_shift,
                            },
                        },
                        'to': {
                            'starting_point': 'scheduled_shift_start',
                            'time_direction': 'forward',
                            'time_amount': {'unit': 'minute', 'value': 15},
                        },
                    },
                    'stop_shift_available': {
                        'from': {
                            'starting_point': 'scheduled_shift_end',
                            'time_direction': 'backward',
                            'time_amount': {'unit': 'minute', 'value': 10},
                        },
                        'to': {
                            'starting_point': 'scheduled_shift_end',
                            'time_direction': 'forward',
                            'time_amount': {'unit': 'minute', 'value': 15},
                        },
                    },
                    'cancel_reservation_available': {
                        'from': {
                            'starting_point': 'scheduled_shift_start',
                            'time_direction': 'backward',
                            'time_amount': {'unit': 'minute', 'value': 30},
                        },
                        'to': {
                            'starting_point': 'scheduled_shift_start',
                            'time_direction': 'forward',
                            'time_amount': {'unit': 'minute', 'value': 15},
                        },
                    },
                },
            },
        ],
    )


@pytest.mark.parametrize(
    'dbid, uuid, response_code, expected_response_json, now, block_reason',
    [
        (
            'dbid0',
            'uuid0',
            200,
            'response_in_workshift.json',
            datetime.datetime(2020, 6, 4, 10, 40, 0),
            'none',
        ),
        (
            'dbid0',
            'uuid0',
            200,
            'response_out_of_workshift.json',
            datetime.datetime(2020, 6, 4, 10, 20, 0),
            'out_of_workshift',
        ),
        (
            'dbid1',
            'uuid1',
            400,
            '',
            datetime.datetime(2020, 6, 4, 10, 20, 0),
            None,
        ),
        (
            'dbid2',
            'uuid2',
            400,
            '',
            datetime.datetime(2020, 6, 4, 10, 20, 0),
            None,
        ),
    ],
)
@pytest.mark.parametrize('start_shift', [30])
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passengers',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_main(
        taxi_shuttle_control,
        experiments3,
        mocks_experiments,
        mocks_external,
        pgsql,
        load_json,
        mocked_time,
        dbid,
        uuid,
        response_code,
        expected_response_json,
        now,
        block_reason,
        start_shift,
):
    mocked_time.set(now)
    await taxi_shuttle_control.invalidate_caches()

    headers = HEADERS
    headers['X-YaTaxi-Park-Id'] = dbid
    headers['X-YaTaxi-Driver-Profile-Id'] = uuid

    # this replaces separate idempotency test for now
    for _ in range(0, 2):
        response = await taxi_shuttle_control.post(
            '/driver/v1/shuttle-control/v1/personal-schedule/start-shift',
            headers=HEADERS,
            params={'shift_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775'},
        )

        assert response.status_code == response_code

        rows = select_named(
            'SELECT * FROM state.shuttles', pgsql['shuttle_control'],
        )
        if response_code == 400:
            assert rows == []
        else:
            expected_response = load_json(expected_response_json)
            assert response.json() == expected_response

            assert rows == [
                {
                    'shuttle_id': 1,
                    'driver_id': f'({dbid},{uuid})',
                    'route_id': 1,
                    'capacity': 2,
                    'drw_state': 'Disabled',
                    'is_fake': False,
                    'revision': AnyNumber(),
                    'ticket_check_enabled': True,
                    'use_external_confirmation_code': False,
                    'ticket_length': 3,
                    'started_at': now,
                    'ended_at': None,
                    'work_mode': 'shuttle_fix',
                    'subscription_id': 1,
                    'view_id': None,
                    'vfh_id': None,
                    'remaining_pauses': 4,
                    'pause_state': 'inactive',
                    'pause_id': None,
                },
            ]

            rows = select_named(
                'SELECT * FROM state.shuttle_trip_progress',
                pgsql['shuttle_control'],
            )
            assert rows == [
                {
                    'shuttle_id': 1,
                    'begin_stop_id': 4,
                    'advanced_at': now,
                    'updated_at': now,
                    'average_speed': None,
                    'block_reason': block_reason,
                    'end_lap': None,
                    'end_stop_id': None,
                    'lap': 0,
                    'next_stop_id': 4,
                    'processed_at': now,
                    'arrived_stop_id': None,
                    'stop_arrival_timestamp': None,
                },
            ]


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize('start_shift', [30])
@pytest.mark.parametrize('vfh_id', [None, '0123456789'])
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passengers',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_vfh_id(
        taxi_shuttle_control,
        experiments3,
        mocks_experiments,
        mocks_external,
        pgsql,
        start_shift,
        vfh_id,
):
    dbid = 'dbid0'
    uuid = 'uuid0'

    if vfh_id:
        experiments3.add_experiment(
            name='shuttle_mt_vfh_id',
            consumers=['shuttle-control/start_shift'],
            clauses=[],
            match={
                'enabled': True,
                'consumers': [{'name': 'shuttle-control/start_shift'}],
                'predicate': {'type': 'true', 'init': {}},
            },
            default_value={'vfh_id': vfh_id},
        )
        await taxi_shuttle_control.invalidate_caches()

    headers = HEADERS
    headers['X-YaTaxi-Park-Id'] = dbid
    headers['X-YaTaxi-Driver-Profile-Id'] = uuid

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/personal-schedule/start-shift',
        headers=HEADERS,
        params={'shift_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775'},
    )
    assert response.status_code == 200

    rows = select_named(
        'SELECT * FROM state.shuttles', pgsql['shuttle_control'],
    )
    assert rows == [
        {
            'shuttle_id': 1,
            'driver_id': f'({dbid},{uuid})',
            'route_id': 1,
            'capacity': 2,
            'drw_state': 'Disabled',
            'is_fake': False,
            'revision': AnyNumber(),
            'ticket_check_enabled': True,
            'ticket_length': 3,
            'use_external_confirmation_code': False,
            'started_at': NOW,
            'ended_at': None,
            'work_mode': 'shuttle_fix',
            'subscription_id': 1,
            'view_id': None,
            'vfh_id': vfh_id,
            'remaining_pauses': 4,
            'pause_state': 'inactive',
            'pause_id': None,
        },
    ]


@pytest.mark.parametrize(
    'dbid, uuid, response_code, expected_response_json, now, block_reason',
    [
        (
            'dbid0',
            'uuid0',
            200,
            'response_in_workshift_dynamic_route.json',
            datetime.datetime(2020, 6, 4, 10, 40, 0),
            'none',
        ),
    ],
)
@pytest.mark.parametrize('start_shift', [30])
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passengers',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main_dynamic_route.sql'])
async def test_main_dynamic_route(
        taxi_shuttle_control,
        experiments3,
        mocks_experiments,
        mocks_external,
        pgsql,
        load_json,
        mocked_time,
        dbid,
        uuid,
        response_code,
        expected_response_json,
        now,
        block_reason,
        start_shift,
):
    mocked_time.set(now)
    await taxi_shuttle_control.invalidate_caches()

    headers = HEADERS
    headers['X-YaTaxi-Park-Id'] = dbid
    headers['X-YaTaxi-Driver-Profile-Id'] = uuid

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/personal-schedule/start-shift',
        headers=HEADERS,
        params={'shift_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775'},
    )

    assert response.status_code == response_code

    rows = select_named(
        'SELECT * FROM state.shuttles', pgsql['shuttle_control'],
    )
    expected_response = load_json(expected_response_json)
    assert response.json() == expected_response

    assert rows == [
        {
            'shuttle_id': 1,
            'driver_id': f'({dbid},{uuid})',
            'route_id': 1,
            'capacity': 2,
            'drw_state': 'Disabled',
            'is_fake': False,
            'revision': AnyNumber(),
            'ticket_check_enabled': True,
            'use_external_confirmation_code': False,
            'ticket_length': 3,
            'started_at': now,
            'ended_at': None,
            'work_mode': 'shuttle_fix',
            'subscription_id': 1,
            'view_id': 1,
            'vfh_id': None,
            'remaining_pauses': 0,
            'pause_state': 'inactive',
            'pause_id': None,
        },
    ]

    rows = select_named(
        'SELECT * FROM state.route_views', pgsql['shuttle_control'],
    )
    assert rows == [
        {
            'view_id': 1,
            'route_id': 1,
            'current_view': [1, 4],
            'traversal_plan': stringify_detailed_view(
                [(1, None, None), (4, None, None)],
            ),
            'revision': AnyNumber(),
        },
    ]

    rows = select_named(
        'SELECT * FROM state.shuttle_trip_progress', pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'shuttle_id': 1,
            'begin_stop_id': 1,
            'advanced_at': now,
            'updated_at': now,
            'average_speed': None,
            'block_reason': block_reason,
            'end_lap': None,
            'end_stop_id': None,
            'lap': 0,
            'next_stop_id': 1,
            'processed_at': now,
            'arrived_stop_id': None,
            'stop_arrival_timestamp': None,
        },
    ]


@pytest.mark.parametrize(
    'dbid, uuid, response_code, expected_response_json, now, block_reason',
    [
        (
            'dbid0',
            'uuid0',
            200,
            'response_in_workshift_flex_route.json',
            datetime.datetime(2020, 6, 4, 10, 40, 0),
            'none',
        ),
    ],
)
@pytest.mark.parametrize('start_shift', [30])
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passengers',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main_flex_route.sql'])
async def test_main_flex_route(
        taxi_shuttle_control,
        experiments3,
        mocks_experiments,
        mocks_external,
        pgsql,
        load_json,
        mocked_time,
        dbid,
        uuid,
        response_code,
        expected_response_json,
        now,
        block_reason,
        start_shift,
):
    mocked_time.set(now)
    await taxi_shuttle_control.invalidate_caches()

    headers = HEADERS
    headers['X-YaTaxi-Park-Id'] = dbid
    headers['X-YaTaxi-Driver-Profile-Id'] = uuid

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/personal-schedule/start-shift',
        headers=HEADERS,
        params={'shift_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775'},
    )

    assert response.status_code == response_code

    rows = select_named(
        'SELECT * FROM state.shuttles', pgsql['shuttle_control'],
    )
    expected_response = load_json(expected_response_json)
    assert response.json() == expected_response

    assert rows == [
        {
            'shuttle_id': 1,
            'driver_id': f'({dbid},{uuid})',
            'route_id': 1,
            'capacity': 2,
            'drw_state': 'Disabled',
            'is_fake': False,
            'revision': AnyNumber(),
            'ticket_check_enabled': True,
            'use_external_confirmation_code': False,
            'ticket_length': 3,
            'started_at': now,
            'ended_at': None,
            'work_mode': 'shuttle_fix',
            'subscription_id': 1,
            'view_id': 1,
            'vfh_id': None,
            'remaining_pauses': 0,
            'pause_state': 'inactive',
            'pause_id': None,
        },
    ]

    rows = select_named(
        'SELECT * FROM state.route_views', pgsql['shuttle_control'],
    )
    assert rows == [
        {
            'view_id': 1,
            'route_id': 1,
            'current_view': [4],
            'traversal_plan': stringify_detailed_view([(4, None, None)]),
            'revision': AnyNumber(),
        },
    ]

    rows = select_named(
        'SELECT * FROM state.shuttle_trip_progress', pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'shuttle_id': 1,
            'begin_stop_id': 4,
            'advanced_at': now,
            'updated_at': now,
            'average_speed': None,
            'block_reason': block_reason,
            'end_lap': None,
            'end_stop_id': None,
            'lap': 0,
            'next_stop_id': 4,
            'processed_at': now,
            'arrived_stop_id': None,
            'stop_arrival_timestamp': None,
        },
    ]


@pytest.mark.now('2020-06-04T10:20:00+0000')
@pytest.mark.translations(notify={'helpers.month_6_part': {'ru': 'сентября'}})
@pytest.mark.parametrize('start_shift', [0])
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passengers',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['planned_bad.sql'])
async def test_planned_out_of_start_time(
        taxi_shuttle_control,
        experiments3,
        mocks_experiments,
        mocks_external,
        pgsql,
        start_shift,
):
    headers = HEADERS
    headers['X-YaTaxi-Park-Id'] = 'dbid0'
    headers['X-YaTaxi-Driver-Profile-Id'] = 'uuid0'

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/personal-schedule/start-shift',
        headers=HEADERS,
        params={'shift_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775'},
    )
    assert response.status_code == 403

    rows = select_named(
        """
        SELECT * FROM state.shuttles
        """,
        pgsql['shuttle_control'],
    )
    assert rows == []
