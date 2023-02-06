# pylint: disable=import-only-modules, import-error, redefined-outer-name
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

SHUTTLE_STATUS_1 = {
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
                            'payload': {
                                'type': 'navigate_to_shift_info',
                                'shift_id': (
                                    '2fef68c9-25d0-4174-9dd0-bdd1b3730777'
                                ),
                            },
                            'span_size': 2,
                            'sub_models': [
                                {
                                    'text': '5 июня, route1',
                                    'type': 'text_header',
                                },
                                {
                                    'bottom_caption': 'слот, 360 Сом/час',
                                    'title': '13:30-17:00',
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
                                    'title': '1',
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
SHUTTLE_STATUS_2 = {
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
                            'payload': {
                                'shift_id': (
                                    '2fef68c9-25d0-4174-9dd0-bdd1b3730778'
                                ),
                                'type': 'navigate_to_shift_info',
                            },
                            'span_size': 2,
                            'sub_models': [
                                {
                                    'text': '4 июня, route1',
                                    'type': 'text_header',
                                },
                                {
                                    'bottom_caption': 'слот, 360 Сом/час',
                                    'title': '19:30-20:00',
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
                                    'title': '2',
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

SHUTTLE_STATUS_3 = {
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

SHUTTLE_STATUS_4 = {
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
                            'payload': {
                                'shift_id': (
                                    'aaaaaaaa-aaaa-aaaa-aaaa-000000000003'
                                ),
                                'type': 'navigate_to_shift_info',
                            },
                            'span_size': 2,
                            'sub_models': [
                                {
                                    'text': '21 ноября, route1',
                                    'type': 'text_header',
                                },
                                {
                                    'bottom_caption': 'слот, 360 Сом/час',
                                    'title': '15:00-16:00',
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
                                    'type': 'text_header',
                                    'text': 'Запланировано',
                                },
                                {
                                    'bottom_caption': 'слотов',
                                    'title': '2',
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
        name='shuttle_shifts_control_access',
        consumers=['shuttle-control/shuttle_shifts_control_access'],
        match={
            'enabled': True,
            'consumers': [
                {'name': 'shuttle-control/shuttle_shifts_control_access'},
            ],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'title',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'reserve_enabled': True, 'cancel_enabled': True},
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
    'now, response_code, shifts, expected_title, approved',
    [
        pytest.param(
            datetime.datetime(2020, 6, 5, 10, 1, 0),
            200,
            ['2fef68c9-25d0-4174-9dd0-bdd1b3730777'],
            'ALL_SKIPPED',
            [],
            id='Shift already reserved',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 5, 10, 1, 0),
            404,
            [
                'ffffffff-ffff-1111-1111-ffffffffffff',
                '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            ],
            'NO_SUCH_WORKSHIFT',
            [],
            id='Nonexistent shift_id',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 4, 14, 30, 0),
            200,
            ['aaaaaaaa-aaaa-aaaa-aaaa-000000000001'],
            'ALL_SKIPPED',
            [],
            id='No available subscription',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 4, 14, 30, 0),
            409,
            ['aaaaaaaa-aaaa-aaaa-aaaa-000000000002'],
            'WORKSHIFT_INTERSECTS',
            [],
            id='Intersects with ongoing',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 4, 14, 30, 0),
            409,
            [
                'aaaaaaaa-aaaa-aaaa-aaaa-000000000001',
                'aaaaaaaa-aaaa-aaaa-aaaa-000000000002',
            ],
            'INTERNAL_INTERSECTION',
            [],
            id='Given shifts are intersects (same range)',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 4, 14, 30, 0),
            409,
            [
                'aaaaaaaa-aaaa-aaaa-aaaa-000000000004',
                'aaaaaaaa-aaaa-aaaa-aaaa-000000000005',
            ],
            'INTERNAL_INTERSECTION',
            [],
            id='Given shifts are intersects (overlap)',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 4, 14, 30, 0),
            409,
            [
                'aaaaaaaa-aaaa-aaaa-aaaa-000000000004',
                'aaaaaaaa-aaaa-aaaa-aaaa-000000000006',
            ],
            'INTERNAL_INTERSECTION',
            [],
            id='Given shifts are intersects',
        ),
        pytest.param(
            datetime.datetime(2020, 11, 21, 11, 30, 0),
            200,
            [
                'aaaaaaaa-aaaa-aaaa-aaaa-000000000003',
                'aaaaaaaa-aaaa-aaaa-aaaa-000000000004',
            ],
            None,
            [
                'aaaaaaaa-aaaa-aaaa-aaaa-000000000003',
                'aaaaaaaa-aaaa-aaaa-aaaa-000000000004',
            ],
            id='Reserve two shift',
        ),
        pytest.param(
            datetime.datetime(2020, 11, 21, 10, 59, 59),
            200,
            ['aaaaaaaa-aaaa-aaaa-aaaa-000000000004'],
            'ALL_SKIPPED',
            [],
            id='Reservation time range mismatch (before left boundary)',
        ),
        pytest.param(
            datetime.datetime(2020, 11, 21, 12, 50, 1),
            200,
            ['aaaaaaaa-aaaa-aaaa-aaaa-000000000004'],
            'ALL_SKIPPED',
            [],
            id='Reservation time range mismatch (after right boundary)',
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
        shifts,
        expected_title,
        approved,
):
    mocked_time.set(now)
    await taxi_shuttle_control.invalidate_caches()

    headers = HEADERS
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
        '/driver/v1/shuttle-control/v1/personal-schedule/reserve-shift',
        headers=HEADERS,
        json={'shifts': shifts},
    )
    assert response.status_code == response_code
    if expected_title:
        title = (
            response.json()['partial_reservation_reason']['title']
            if response_code == 200
            else response.json()['code']
        )
        assert title == expected_title

    if response_code == 200:
        expected.update(approved)
        assert 'shuttle_status' not in response.json()

    assert get_active_subscribtions_() == expected


@pytest.mark.parametrize(
    'now, response_code, shifts, expected_title, approved, '
    'expected_shuttle_status',
    [
        pytest.param(
            datetime.datetime(2020, 6, 5, 10, 1, 0),
            200,
            ['2fef68c9-25d0-4174-9dd0-bdd1b3730777'],
            'ALL_SKIPPED',
            [],
            SHUTTLE_STATUS_1,
            id='Shift already reserved',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 5, 10, 1, 0),
            404,
            [
                'ffffffff-ffff-1111-1111-ffffffffffff',
                '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            ],
            'NO_SUCH_WORKSHIFT',
            [],
            SHUTTLE_STATUS_1,
            id='Nonexistent shift_id',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 4, 14, 30, 0),
            200,
            ['aaaaaaaa-aaaa-aaaa-aaaa-000000000001'],
            'ALL_SKIPPED',
            [],
            SHUTTLE_STATUS_2,
            id='No available subscription',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 4, 14, 30, 0),
            409,
            ['aaaaaaaa-aaaa-aaaa-aaaa-000000000002'],
            'WORKSHIFT_INTERSECTS',
            [],
            SHUTTLE_STATUS_1,
            id='Intersects with ongoing',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 4, 14, 30, 0),
            409,
            [
                'aaaaaaaa-aaaa-aaaa-aaaa-000000000001',
                'aaaaaaaa-aaaa-aaaa-aaaa-000000000002',
            ],
            'INTERNAL_INTERSECTION',
            [],
            SHUTTLE_STATUS_1,
            id='Given shifts are intersects (same range)',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 4, 14, 30, 0),
            409,
            [
                'aaaaaaaa-aaaa-aaaa-aaaa-000000000004',
                'aaaaaaaa-aaaa-aaaa-aaaa-000000000005',
            ],
            'INTERNAL_INTERSECTION',
            [],
            SHUTTLE_STATUS_1,
            id='Given shifts are intersects (overlap)',
        ),
        pytest.param(
            datetime.datetime(2020, 6, 4, 14, 30, 0),
            409,
            [
                'aaaaaaaa-aaaa-aaaa-aaaa-000000000004',
                'aaaaaaaa-aaaa-aaaa-aaaa-000000000006',
            ],
            'INTERNAL_INTERSECTION',
            [],
            SHUTTLE_STATUS_1,
            id='Given shifts are intersects',
        ),
        pytest.param(
            datetime.datetime(2020, 11, 21, 11, 30, 0),
            200,
            [
                'aaaaaaaa-aaaa-aaaa-aaaa-000000000003',
                'aaaaaaaa-aaaa-aaaa-aaaa-000000000004',
            ],
            None,
            [
                'aaaaaaaa-aaaa-aaaa-aaaa-000000000003',
                'aaaaaaaa-aaaa-aaaa-aaaa-000000000004',
            ],
            SHUTTLE_STATUS_4,
            id='Reserve two shift',
        ),
        pytest.param(
            datetime.datetime(2020, 11, 21, 10, 59, 59),
            200,
            ['aaaaaaaa-aaaa-aaaa-aaaa-000000000004'],
            'ALL_SKIPPED',
            [],
            SHUTTLE_STATUS_3,
            id='Reservation time range mismatch (before left boundary)',
        ),
        pytest.param(
            datetime.datetime(2020, 11, 21, 12, 50, 1),
            200,
            ['aaaaaaaa-aaaa-aaaa-aaaa-000000000004'],
            'ALL_SKIPPED',
            [],
            SHUTTLE_STATUS_3,
            id='Reservation time range mismatch (after right boundary)',
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
        shifts,
        expected_title,
        approved,
        expected_shuttle_status,
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

    headers = HEADERS
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
        '/driver/v1/shuttle-control/v1/personal-schedule/reserve-shift',
        headers=HEADERS,
        json={'shifts': shifts},
    )
    assert response.status_code == response_code
    if expected_title:
        title = (
            response.json()['partial_reservation_reason']['title']
            if response_code == 200
            else response.json()['code']
        )
        assert title == expected_title

    if response_code == 200:
        expected.update(approved)
        assert response.json()['shuttle_status'] == expected_shuttle_status

    assert get_active_subscribtions_() == expected
