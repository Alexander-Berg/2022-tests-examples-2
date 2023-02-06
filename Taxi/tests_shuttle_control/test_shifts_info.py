# pylint: disable=import-only-modules, import-error, redefined-outer-name
import pytest


HEADERS = {
    'X-Request-Application': 'taximeter',
    'X-Request-Platform': 'android',
    'X-Request-Application-Version': '9.07',
    'X-YaTaxi-Park-Id': '111',
    'X-YaTaxi-Driver-Profile-Id': '888',
    'Accept-Language': 'ru',
}


@pytest.mark.now('2020-06-04T10:20:00+0000')
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passengers',
        },
    },
)
@pytest.mark.parametrize(
    'workshift_id, dbid, uuid, start_shift_from, response_code, '
    'expected_response, driver_work_mode',
    [
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'dbid0',
            'uuid0',
            30,
            200,
            {
                'title': 'route1',
                'info_items_ui': [
                    {
                        'title': 'Четверг',
                        'detail': '13:30-17:00',
                        'accent': True,
                        'horizontal_divider_type': 'bottom_gap',
                        'type': 'tip_detail',
                    },
                    {
                        'title': 'Заработок',
                        'detail': '360 Сом/час',
                        'horizontal_divider_type': 'bottom_gap',
                        'type': 'tip_detail',
                    },
                    {
                        'title': 'Бонус за качество',
                        'detail': '100 сом/час',
                        'horizontal_divider_type': 'bottom_gap',
                        'type': 'tip_detail',
                    },
                ],
                'allowed_actions': ['start', 'cancel'],
                'available_actions': [
                    {
                        'action': 'start',
                        'is_disabled': False,
                        'text': 'Начать слот',
                    },
                    {
                        'action': 'cancel',
                        'is_disabled': False,
                        'text': 'Отменить слот',
                    },
                ],
            },
            'shuttle_fix',
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
            'dbid0',
            'uuid0',
            0,
            200,
            {
                'title': 'route1',
                'info_items_ui': [
                    {
                        'title': 'Четверг',
                        'detail': '13:30-17:00',
                        'accent': True,
                        'horizontal_divider_type': 'bottom_gap',
                        'type': 'tip_detail',
                    },
                    {
                        'title': 'Заработок',
                        'detail': '360 Сом/час',
                        'horizontal_divider_type': 'bottom_gap',
                        'type': 'tip_detail',
                    },
                    {
                        'title': 'Цель по поездкам',
                        'detail': '50 сом за 30 поездок',
                        'horizontal_divider_type': 'bottom_gap',
                        'type': 'tip_detail',
                    },
                    {
                        'title': 'Бонус за качество',
                        'detail': '100 сом/час',
                        'horizontal_divider_type': 'bottom_gap',
                        'type': 'tip_detail',
                    },
                ],
                'allowed_actions': ['cancel'],
                'available_actions': [
                    {
                        'action': 'cancel',
                        'is_disabled': False,
                        'text': 'Отменить слот',
                    },
                ],
            },
            'shuttle_fix',
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'dbid1',
            'uuid1',
            30,
            200,
            {
                'title': 'route1',
                'info_items_ui': [
                    {
                        'title': 'Четверг',
                        'detail': '13:30-17:00',
                        'accent': True,
                        'horizontal_divider_type': 'bottom_gap',
                        'type': 'tip_detail',
                    },
                    {
                        'title': 'Заработок',
                        'detail': '360 Сом/час',
                        'horizontal_divider_type': 'bottom_gap',
                        'type': 'tip_detail',
                    },
                    {
                        'title': 'Бонус за качество',
                        'detail': '100 сом/час',
                        'horizontal_divider_type': 'bottom_gap',
                        'type': 'tip_detail',
                    },
                ],
                'allowed_actions': ['stop'],
                'available_actions': [],
            },
            'shuttle_fix',
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'dbid2',
            'uuid2',
            30,
            200,
            {
                'title': 'route1',
                'info_items_ui': [
                    {
                        'title': 'Четверг',
                        'detail': '13:30-17:00',
                        'accent': True,
                        'horizontal_divider_type': 'bottom_gap',
                        'type': 'tip_detail',
                    },
                    {
                        'title': 'Заработок',
                        'detail': '360 Сом/час',
                        'horizontal_divider_type': 'bottom_gap',
                        'type': 'tip_detail',
                    },
                    {
                        'title': 'Бонус за качество',
                        'detail': '100 сом/час',
                        'horizontal_divider_type': 'bottom_gap',
                        'type': 'tip_detail',
                    },
                ],
                'allowed_actions': [],
                'available_actions': [],
            },
            'shuttle_fix',
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'dbid3',
            'uuid3',
            30,
            200,
            {
                'title': 'route1',
                'info_items_ui': [
                    {
                        'title': 'Четверг',
                        'detail': '13:30-17:00',
                        'accent': True,
                        'horizontal_divider_type': 'bottom_gap',
                        'type': 'tip_detail',
                    },
                    {
                        'title': 'Заработок',
                        'detail': '360 Сом/час',
                        'horizontal_divider_type': 'bottom_gap',
                        'type': 'tip_detail',
                    },
                    {
                        'title': 'Бонус за качество',
                        'detail': '100 сом/час',
                        'horizontal_divider_type': 'bottom_gap',
                        'type': 'tip_detail',
                    },
                ],
                'allowed_actions': [],
                'available_actions': [],
            },
            'shuttle_fix',
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            'dbid3',
            'uuid3',
            30,
            404,
            {},
            'shuttle_fix',
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
            'dbid1',
            'uuid1',
            30,
            404,
            {},
            'shuttle_fix',
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
            'dbid0',
            'uuid0',
            0,
            200,
            {
                'title': 'route1',
                'info_items_ui': [
                    {
                        'title': 'Четверг',
                        'detail': '13:30-17:00',
                        'accent': True,
                        'horizontal_divider_type': 'bottom_gap',
                        'type': 'tip_detail',
                    },
                ],
                'allowed_actions': ['cancel'],
                'available_actions': [
                    {
                        'action': 'cancel',
                        'is_disabled': False,
                        'text': 'Отменить слот',
                    },
                ],
            },
            'shuttle',
        ),
    ],
)
@pytest.mark.parametrize('cancel_shift_enabled', [True, False])
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_main(
        mockserver,
        taxi_shuttle_control,
        experiments3,
        workshift_id,
        dbid,
        uuid,
        start_shift_from,
        response_code,
        cancel_shift_enabled,
        expected_response,
        driver_work_mode,
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
        return {'display_mode': 'shuttle', 'display_profile': driver_work_mode}

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
                                'value': start_shift_from,
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
                            'time_amount': {'unit': 'hour', 'value': 4},
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
                'value': {
                    'reserve_enabled': True,
                    'cancel_enabled': cancel_shift_enabled,
                },
            },
        ],
    )

    headers = HEADERS
    headers['X-YaTaxi-Park-Id'] = dbid
    headers['X-YaTaxi-Driver-Profile-Id'] = uuid

    response = await taxi_shuttle_control.get(
        '/driver/v1/shuttle-control/v1/shifts/info',
        headers=headers,
        params={'shift_id': workshift_id},
    )

    assert response.status_code == response_code

    if response_code == 200:
        if (
                not cancel_shift_enabled
                and 'cancel' in expected_response['allowed_actions']
        ):
            expected_response['allowed_actions'].remove('cancel')
            for idx, action in enumerate(
                    expected_response['available_actions'],
            ):
                if action['action'] == 'cancel':
                    del expected_response['available_actions'][idx]
                    break

        assert response.json() == expected_response
