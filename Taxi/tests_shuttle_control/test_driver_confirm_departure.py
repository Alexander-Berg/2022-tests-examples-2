# pylint: disable=import-only-modules
import pytest

from tests_shuttle_control.utils import select_named
from tests_shuttle_control.utils import stringify_detailed_view


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
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main_dynamic.sql'])
async def test_confirm_departure(
        taxi_shuttle_control,
        mockserver,
        pgsql,
        experiments3,
        driver_trackstory_v2_shorttracks,
):
    def _mock_positions():
        return {
            'results': [
                {
                    'driver_id': 'dbid_1_uuid_1',
                    'type': 'adjusted',
                    'position': {
                        'lat': 55.735054,
                        'lon': 37.642933,
                        'timestamp': 1600092910,
                    },
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock_positions())

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

    shuttle_id = 'Pmp80rQ23L4wZYxd'
    booking_id = 'acfff773-398f-4913-b9e9-03bf5eda22ac'

    rows = select_named(
        f'SELECT sp.status '
        f'FROM state.passengers sp '
        f'WHERE booking_id = \'{booking_id}\'',
        pgsql['shuttle_control'],
    )
    assert len(rows) == 1
    assert rows[0]['status'] == 'driving'

    headers = {
        'X-Request-Application': 'taximeter',
        'X-Request-Platform': 'android',
        'X-Request-Application-Version': '9.07',
        'X-YaTaxi-Park-Id': 'dbid_1',
        'X-YaTaxi-Driver-Profile-Id': 'uuid_1',
        'Accept-Language': 'ru',
    }
    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/shuttle/confirm-departure',
        headers=headers,
        params={'shuttle_id': shuttle_id},
        json={'current_position': {}},
    )
    assert response.status_code == 200

    rows = select_named(
        f'SELECT sp.booking_id, sp.status, '
        f'sp.cancel_reason '
        f'FROM state.passengers sp '
        f'WHERE shuttle_id = 2 '
        f'ORDER BY booking_id',
        pgsql['shuttle_control'],
    )
    assert rows == [
        {
            'booking_id': 'acfff773-398f-4913-b9e9-03bf5eda22ac',
            'status': 'cancelled',
            'cancel_reason': 'not_appeared_at_pickup',
        },
        {
            'booking_id': 'acfff773-398f-4913-b9e9-03bf5eda22ad',
            'status': 'finished',
            'cancel_reason': None,
        },
    ]

    rows = select_named(
        f'SELECT sbt.status '
        f'FROM state.booking_tickets sbt '
        f'WHERE booking_id = \'{booking_id}\'',
        pgsql['shuttle_control'],
    )
    assert rows == [{'status': 'revoked'}]

    rows = select_named(
        f'SELECT stp.next_stop_id '
        f'FROM state.shuttle_trip_progress stp '
        f'WHERE shuttle_id = 2',
        pgsql['shuttle_control'],
    )
    assert rows == [{'next_stop_id': 4}]

    expected_traversal_plan = [(4, None, None)]
    rows = select_named(
        f'SELECT current_view, traversal_plan '
        f'FROM state.route_views '
        f'WHERE view_id = 2',
        pgsql['shuttle_control'],
    )
    assert rows == [
        {
            'current_view': [4],
            'traversal_plan': stringify_detailed_view(expected_traversal_plan),
        },
    ]
