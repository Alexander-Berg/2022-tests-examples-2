# pylint: disable=import-only-modules, import-error
import pytest

from tests_shuttle_control.utils import select_named


MOCK_NOW = '2020-09-14T14:15:16+0000'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'dynamic_route': {
            'driver': 'shuttle_control.routes.dynamic_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.dynamic_route.name_for_passenger'
            ),
        },
        'main_route': {
            'driver': 'shuttle_control.routes.main_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.main_route.name_for_passenger'
            ),
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'shuttle_id, park_id, profile_id, expected_code, expected_state',
    [
        ('gkZxnYQ73QGqrKyz', 'dbid_0', 'uuid_0', 200, 'requested'),  # retry
        (
            'Pmp80rQ23L4wZYxd',
            'dbid_1',
            'uuid_1',
            200,
            'requested',
        ),  # valid query, one pax
        (
            '80vm7DQm7Ml24ZdO',
            'dbid_2',
            'uuid_2',
            200,
            'in_work',
        ),  # already in pause
        ('VlAK13MzaLx6Bmnd', 'dbid_3', 'uuid_3', 403, None),
        ('bjoAWlMYJRG14Nnm', 'dbid_4', 'uuid_4', 403, None),
        ('x7A42mRDWMG6jYzP', 'dbid_x', 'uuid_x', 404, None),
        ('invalid_id', 'dbid_x', 'uuid_x', 400, None),
    ],
)
async def test_request_pause(
        taxi_shuttle_control,
        mockserver,
        pgsql,
        experiments3,
        shuttle_id,
        park_id,
        profile_id,
        expected_code,
        expected_state,
        driver_trackstory_v2_shorttracks,
):
    @mockserver.handler('/maps-router/v2/route')
    def _mock_router_route(request):
        return mockserver.make_response(
            status=200, content_type='application/x-protobuf',
        )

    def _mock():
        return {
            'results': [
                {
                    'driver_id': f'{park_id}_{profile_id}',
                    'type': 'adjusted',
                    'position': {
                        'lat': 55.735054,
                        'lon': 37.642933,
                        'timestamp': 1600092910,
                    },
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock())

    @mockserver.json_handler('/driver-fix/v1/internal/status')
    def _mock_driver_fix(request):
        return {
            'time': {'seconds': 240, 'localized': '4 мин'},
            'guaranteed_money': {
                'value': 2000,
                'currency': 'RUB',
                'localized': '2000 руб.',
            },
            'cash_income': {
                'value': 12,
                'currency': 'RUB',
                'localized': '12 руб.',
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

    experiments3.add_config(
        name='shuttle_status_settings',
        consumers=['shuttle-control/start_trip', 'shuttle-control/polling'],
        match={
            'enabled': True,
            'consumers': [
                {'name': 'shuttle-control/start_trip'},
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

    await taxi_shuttle_control.invalidate_caches()

    headers = {
        'X-Request-Application': 'taximeter',
        'X-Request-Platform': 'android',
        'X-Request-Application-Version': '9.07',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': profile_id,
        'Accept-Language': 'ru',
    }
    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/pause-management/request-pause',
        headers=headers,
        params={'shuttle_id': shuttle_id},
    )
    assert response.status_code == expected_code

    if expected_code == 200:
        rows = select_named(
            f"""
            SELECT shuttle_id, pause_state, pause_id
            FROM state.shuttles
            WHERE driver_id = (\'{park_id}\',\'{profile_id}\')::db.driver_id
            """,
            pgsql['shuttle_control'],
        )
        assert len(rows) == 1
        assert rows[0]['pause_state'] == expected_state
        shuttle_idx = rows[0]['shuttle_id']
        pause_id = rows[0]['pause_id']

        rows = select_named(
            f'SELECT pause_requested, pause_started, pause_finished '
            f'FROM state.pauses '
            f'WHERE pause_id = {pause_id} AND shuttle_id = {shuttle_idx}',
            pgsql['shuttle_control'],
        )
        assert len(rows) == 1
        assert rows[0]['pause_requested'] is not None
        if expected_state == 'requested':
            assert rows[0]['pause_started'] is None
        else:
            assert rows[0]['pause_started'] is not None
        assert rows[0]['pause_finished'] is None


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'dynamic_route': {
            'driver': 'shuttle_control.routes.dynamic_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.dynamic_route.name_for_passenger'
            ),
        },
        'main_route': {
            'driver': 'shuttle_control.routes.main_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.main_route.name_for_passenger'
            ),
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'shuttle_id, pause_id, park_id, profile_id, expected_code, expected_state',
    [
        (
            'gkZxnYQ73QGqrKyz',
            'Pmp80rQ23L4wZYxd',
            'dbid_0',
            'uuid_0',
            200,
            'requested',
        ),
        (
            'gkZxnYQ73QGqrKyz',
            '80vm7DQm7Ml24ZdO',
            'dbid_0',
            'uuid_0',
            404,
            'requested',
        ),
        ('x7A42mRDWMG6jYzP', 'abcdf', 'dbid_x', 'uuid_x', 400, None),
        ('invalid_id', 'abcdf', 'dbid_x', 'uuid_x', 400, None),
    ],
)
async def test_finish_pause(
        taxi_shuttle_control,
        mockserver,
        pgsql,
        experiments3,
        shuttle_id,
        pause_id,
        park_id,
        profile_id,
        expected_code,
        expected_state,
        driver_trackstory_v2_shorttracks,
):
    @mockserver.handler('/maps-router/v2/route')
    def _mock_router_route(request):
        return mockserver.make_response(
            status=200, content_type='application/x-protobuf',
        )

    def _mock():
        return {
            'results': [
                {
                    'driver_id': f'{park_id}_{profile_id}',
                    'type': 'adjusted',
                    'position': {
                        'lat': 55.735054,
                        'lon': 37.642933,
                        'timestamp': 1600092910,
                    },
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock())

    @mockserver.json_handler('/driver-fix/v1/internal/status')
    def _mock_driver_fix(request):
        return {
            'time': {'seconds': 240, 'localized': '4 мин'},
            'guaranteed_money': {
                'value': 2000,
                'currency': 'RUB',
                'localized': '2000 руб.',
            },
            'cash_income': {
                'value': 12,
                'currency': 'RUB',
                'localized': '12 руб.',
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

    experiments3.add_config(
        name='shuttle_status_settings',
        consumers=['shuttle-control/start_trip', 'shuttle-control/polling'],
        match={
            'enabled': True,
            'consumers': [
                {'name': 'shuttle-control/start_trip'},
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

    await taxi_shuttle_control.invalidate_caches()

    rows = select_named(
        f'SELECT pause_id '
        f'FROM state.shuttles '
        f'WHERE driver_id = (\'{park_id}\',\'{profile_id}\')::db.driver_id',
        pgsql['shuttle_control'],
    )
    active_pause_id = None if rows == [] else rows[0]['pause_id']

    headers = {
        'X-Request-Application': 'taximeter',
        'X-Request-Platform': 'android',
        'X-Request-Application-Version': '9.07',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': profile_id,
        'Accept-Language': 'ru',
    }
    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/pause-management/finish-pause',
        headers=headers,
        params={'shuttle_id': shuttle_id, 'pause_id': pause_id},
    )
    assert response.status_code == expected_code

    if expected_code == 200:
        rows = select_named(
            f"""
            SELECT shuttle_id, pause_state, pause_id
            FROM state.shuttles
            WHERE driver_id = (\'{park_id}\',\'{profile_id}\')::db.driver_id
            """,
            pgsql['shuttle_control'],
        )
        assert len(rows) == 1
        assert rows[0]['pause_state'] == expected_state
        if expected_state == 'requested':
            assert rows[0]['pause_id'] == active_pause_id
        else:
            assert rows[0]['pause_id'] is None
        shuttle_idx = rows[0]['shuttle_id']

        if active_pause_id is not None:
            rows = select_named(
                f'SELECT pause_requested, pause_started, pause_finished '
                f'FROM state.pauses '
                f'WHERE pause_id = {active_pause_id}'
                f' AND shuttle_id = {shuttle_idx}',
                pgsql['shuttle_control'],
            )
            assert len(rows) == 1
            assert rows[0]['pause_requested'] is not None
            if expected_state == 'requested':
                assert rows[0]['pause_started'] is None
                assert rows[0]['pause_finished'] is None
            else:
                assert rows[0]['pause_started'] is not None
                assert rows[0]['pause_finished'] is not None
