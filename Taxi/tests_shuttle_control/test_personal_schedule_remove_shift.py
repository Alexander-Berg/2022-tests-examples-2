# pylint: disable=import-only-modules, import-error, redefined-outer-name
import copy
import datetime

import pytest

from tests_shuttle_control.utils import select_named


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

SHUTTLE_STATUS = {
    'scheduling_panels': {
        'shift_schedule_ui': {
            'items': [
                {
                    'items': [
                        {
                            'background': {
                                'color_day': 'minor_bg',
                                'corner_radius': 'mu_2',
                                'type': 'rect',
                            },
                            'id': 'current_workshift_card_id',
                            'payload': {'type': 'navigate_to_shift_planning'},
                            'span_size': 2,
                            'sub_models': [
                                {'text': 'Слоты', 'type': 'text_header'},
                                {
                                    'bottom_caption': 'с гарантией',
                                    'title': '360 Сом/час',
                                    'top_caption': 'от',
                                    'type': 'title_captions_image_footer',
                                },
                            ],
                            'type': 'tile_2',
                        },
                        {
                            'background': {
                                'color_day': 'minor_bg',
                                'corner_radius': 'mu_2',
                                'type': 'rect',
                            },
                            'id': 'scheduled_workshifts_card_id',
                            'payload': {'type': 'navigate_to_shift_schedule'},
                            'span_size': 1,
                            'sub_models': [
                                {
                                    'text': 'Запланировано',
                                    'type': 'text_header',
                                },
                                {
                                    'bottom_caption': 'слотов',
                                    'title': '0',
                                    'type': 'title_captions_image_footer',
                                },
                            ],
                            'type': 'tile_2',
                        },
                    ],
                    'span_count': 3,
                    'type': 'grid_view',
                },
                {
                    'horizontal_divider_type': 'top_gap',
                    'left_tip': {'icon': {'icon_type': 'cal'}},
                    'padding_type': 'small_top',
                    'payload': {'type': 'navigate_to_shift_planning'},
                    'right_icon': 'navigate',
                    'title': 'Запланировать слот',
                    'type': 'tip_detail',
                },
            ],
        },
    },
    'state': 'scheduling',
}


@pytest.fixture
def mocks_experiments(experiments3):
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
                            'time_amount': {'unit': 'minute', 'value': 20},
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
                            'time_amount': {'unit': 'hour', 'value': 40},
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
    'now, response_code, shift_id',
    [
        pytest.param(
            datetime.datetime(2020, 6, 5, 9, 59, 0),
            400,
            '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            id='Cancel reservation range mismatch, time before left boundary',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 5, 10, 00, 0),
            200,
            '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            id='Exact left boundary of the cancel range',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 5, 10, 1, 0),
            200,
            '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            id='Match cancel range',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 5, 10, 45, 0),
            200,
            '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            id='Exact right boundary of the cancel range',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 5, 10, 46, 0),
            400,
            '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            id='Cancel reservation range mismatch, time after right boundary',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 5, 10, 46, 0),
            404,
            'ffffffff-ffff-1111-1111-ffffffffffff',
            id='Nonexistent shift_id',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 5, 10, 1, 0),
            400,
            '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            id='Status is not planned',
        ),
    ],
)
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
        pgsql,
        load_json,
        mocked_time,
        response_code,
        now,
        shift_id,
):
    mocked_time.set(now)
    await taxi_shuttle_control.invalidate_caches()

    headers = copy.deepcopy(HEADERS)
    headers['X-YaTaxi-Park-Id'] = 'dbid0'
    headers['X-YaTaxi-Driver-Profile-Id'] = 'uuid0'

    def get_active_subscribtions_():
        rows = select_named(
            """
            SELECT workshift_id FROM state.drivers_workshifts_subscriptions
            WHERE is_active = TRUE
            """,
            pgsql['shuttle_control'],
        )
        return {it['workshift_id'] for it in rows}

    expected = get_active_subscribtions_()
    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/personal-schedule/remove-shift',
        headers=headers,
        params={'shift_id': shift_id},
    )
    assert response.status_code == response_code
    if response_code == 200:
        expected.remove(shift_id)
        assert response.json() == {}
    elif response_code == 404:
        assert shift_id not in expected

    assert get_active_subscribtions_() == expected


@pytest.mark.parametrize(
    'now, response_code, expected_shuttle_status, shift_id',
    [
        pytest.param(
            datetime.datetime(2020, 6, 5, 9, 59, 0),
            400,
            {},
            '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            id='Cancel reservation range mismatch, time before left boundary',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 5, 10, 00, 0),
            200,
            SHUTTLE_STATUS,
            '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            id='Exact left boundary of the cancel range',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 5, 10, 1, 0),
            200,
            SHUTTLE_STATUS,
            '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            id='Match cancel range',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 5, 10, 45, 0),
            200,
            SHUTTLE_STATUS,
            '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            id='Exact right boundary of the cancel range',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 5, 10, 46, 0),
            400,
            {},
            '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            id='Cancel reservation range mismatch, time after right boundary',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 5, 10, 46, 0),
            404,
            {},
            'ffffffff-ffff-1111-1111-ffffffffffff',
            id='Nonexistent shift_id',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 5, 10, 1, 0),
            400,
            {},
            '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            id='Status is not planned',
        ),
    ],
)
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passengers',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['no_active_shuttles.sql'])
async def test_no_active_shuttles(
        mockserver,
        taxi_shuttle_control,
        experiments3,
        mocks_experiments,
        pgsql,
        load_json,
        mocked_time,
        response_code,
        now,
        expected_shuttle_status,
        shift_id,
):
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

    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _mock_ui_profile(request):
        return {'display_mode': 'shuttle', 'display_profile': 'shuttle_fix'}

    mocked_time.set(now)
    await taxi_shuttle_control.invalidate_caches()

    headers = copy.deepcopy(HEADERS)
    headers['X-YaTaxi-Park-Id'] = 'dbid0'
    headers['X-YaTaxi-Driver-Profile-Id'] = 'uuid0'

    def get_active_subscribtions_():
        rows = select_named(
            """
            SELECT workshift_id FROM state.drivers_workshifts_subscriptions
            WHERE is_active = TRUE
            """,
            pgsql['shuttle_control'],
        )
        return {it['workshift_id'] for it in rows}

    expected = get_active_subscribtions_()
    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v1/personal-schedule/remove-shift',
        headers=headers,
        params={'shift_id': shift_id},
    )
    assert response.status_code == response_code
    if response_code == 200:
        assert response.json()['shuttle_status'] == expected_shuttle_status
        expected.remove(shift_id)
    elif response_code == 404:
        assert shift_id not in expected

    assert get_active_subscribtions_() == expected
