# pylint: disable=import-only-modules
import copy

import pytest

from tests_shuttle_control.utils import select_named

HEADERS = {
    'X-Request-Application': 'taximeter',
    'X-Request-Platform': 'android',
    'X-Request-Application-Version': '9.07',
    'X-YaTaxi-Park-Id': 'dbid_0',
    'X-YaTaxi-Driver-Profile-Id': 'uuid_0',
    'Accept-Language': 'ru',
}


STATE = {
    'state': 'en_route',
    'shuttle_id': 'gkZxnYQ73QGqrKyz',
    'route': {
        'is_cyclic': False,
        'is_dynamic': False,
        'route_name': 'main_route',
        'points': [
            {
                'meta': {
                    'name': 'Мэйн стоп',
                    'title': 'Заберите 2 пассажиров',
                    'passengers': [
                        {
                            'type': 'accepted',
                            'background_color': 'main_green',
                            'code': '0202',
                        },
                        {'type': 'incoming', 'background_color': 'main_green'},
                        {'type': 'incoming', 'background_color': 'main_green'},
                    ],
                },
                'type': 'stop',
                'remaining_distance': 100,
                'point': [30.0, 60.0],
            },
            {
                'meta': {
                    'title': 'Двигайтесь к конечной остановке - second_stop',
                    'name': 'second_stop',
                    'passengers': [],
                },
                'type': 'stop',
                'remaining_distance': 100,
                'point': [60.0, 30.0],
            },
        ],
    },
    'settings': {'tickets': {'length': 3}},
    'en_route_panels': {
        'work_mode_info': {
            'title': 'Режим дохода "Шаттл"',
            'text': 'Продолжайте движение по маршруту',
            'icon': 'bus',
            'action_status': 'en_route',
        },
    },
    'available_actions': [
        {'action': 'stop', 'is_disabled': False, 'text': 'Закончить слот'},
    ],
}

STATE_2 = {
    'state': 'en_route',
    'shuttle_id': 'Pmp80rQ23L4wZYxd',
    'route': {
        'is_cyclic': False,
        'is_dynamic': False,
        'route_name': 'main_route',
        'points': [
            {
                'meta': {
                    'name': 'Мэйн стоп',
                    'title': '',
                    'passengers': [
                        {
                            'type': 'accepted',
                            'background_color': 'main_green',
                            'code': '2222',
                        },
                    ],
                },
                'type': 'stop',
                'remaining_distance': 100,
                'point': [30.0, 60.0],
            },
            {
                'meta': {
                    'title': 'Двигайтесь к конечной остановке - second_stop',
                    'name': 'second_stop',
                    'passengers': [],
                },
                'type': 'stop',
                'remaining_distance': 100,
                'point': [60.0, 30.0],
            },
        ],
    },
    'settings': {'tickets': {'length': 3}},
    'en_route_panels': {
        'work_mode_info': {
            'title': 'Режим дохода "Шаттл"',
            'text': 'Продолжайте движение по маршруту',
            'icon': 'bus',
            'action_status': 'en_route',
        },
    },
    'shift_id': '427a330d-2506-464a-accf-346b31e288b8',
    'available_actions': [
        {'action': 'stop', 'is_disabled': False, 'text': 'Закончить слот'},
    ],
}


@pytest.mark.pgsql('shuttle_control', files=['main.sql', 'workshifts.sql'])
@pytest.mark.parametrize(
    'ticket,expected_response_check_valid,passenger_change_status',
    [
        pytest.param('0101', True, True, id='ticket_ok_created'),
        pytest.param('0202', True, False, id='ticket_ok_transporting'),
        pytest.param('0303', False, False, id='ticket_ok_finished'),
        pytest.param('4242', False, False, id='ticket_bad'),
        pytest.param('0404', False, False, id='ticket_on_other_shuttle'),
        pytest.param(
            '0505', True, True, id='same_ticket_on_finished_and_created',
        ),
    ],
)
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'main_route': {
            'driver': 'shuttle_control.routes.main_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.main_route.name_for_passenger'
            ),
        },
    },
)
async def test_pickup_passengers(
        taxi_shuttle_control,
        ticket,
        expected_response_check_valid,
        passenger_change_status,
        pgsql,
):
    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v2/shuttle/pickup_passengers?'
        'shuttle_id=gkZxnYQ73QGqrKyz',
        headers=HEADERS,
        json={
            'pickup_position': {'some': 'taximeter_data'},
            'passengers': [{'ticket': ticket}],
        },
    )

    assert response.status_code == 200
    resp = response.json()

    state = copy.deepcopy(STATE)
    if passenger_change_status:
        state['route']['points'][0]['meta']['title'] = 'Заберите пассажира'
        state['route']['points'][0]['meta']['passengers'].pop()
        # fix UB below
        state['route']['points'][0]['meta']['passengers'].insert(
            1,
            {
                'type': 'accepted',
                'background_color': 'main_green',
                'code': ticket,
            },
        )

    if expected_response_check_valid:
        if ticket in ('0101', '0202', '0505'):
            assert 'meta' in resp['ticket_check_results'][ticket]
            assert resp['ticket_check_results'][ticket]['meta'] == {
                'type': 'detail_tip',
                'right_tip': {
                    'icon': {'icon_type': 'cash2'},
                    'form': 'square',
                },
                'title': 'Оплата наличными',
                'title_text_style': 'body',
                'subtitle': '10 руб.',
                'subtitle_text_style': 'title_medium',
                'secondary_text_color': 'main_text',
            }
            del resp['ticket_check_results'][ticket]['meta']

        assert resp['ticket_check_results'] == {
            ticket: {
                'result': 'ok',
                'text': f'Билет {ticket} успешно проверен',
            },
        }
        rows = select_named(
            'SELECT sp.status FROM state.passengers sp '
            'INNER JOIN state.booking_tickets bt '
            'ON sp.booking_id = bt.booking_id '
            'WHERE sp.shuttle_id=1 AND '
            f'bt.code = \'{ticket}\' '
            'AND sp.status NOT IN (\'cancelled\', \'finished\')',
            pgsql['shuttle_control'],
        )
        assert len(rows) == 1
        assert rows[0]['status'] == 'transporting'
    else:
        assert resp['ticket_check_results'] == {
            ticket: {
                'result': 'invalid_ticket',
                'text': (
                    f'Информация о пассажире с билетом {ticket} отсутствует'
                ),
            },
        }

    assert 'shift_id' in resp['status']
    subscriptions = select_named(
        'SELECT workshift_id '
        'FROM state.shuttles ss '
        'LEFT JOIN state.drivers_workshifts_subscriptions sdws '
        'ON ss.driver_id = sdws.driver_id '
        'WHERE ss.shuttle_id = 1',  # decode("gkZxnYQ73QGqrKyz") == 1
        pgsql['shuttle_control'],
    )
    assert resp['status']['shift_id'] in subscriptions[0]['workshift_id']
    del resp['status']['shift_id']

    assert resp['status'] == state


@pytest.mark.pgsql('shuttle_control', files=['main.sql', 'workshifts.sql'])
@pytest.mark.parametrize(
    'ticket,expected_response_check_valid,passenger_change_status,'
    'confirmation_code,tickets_cnt',
    [
        pytest.param('0707', True, True, '1111', 1, id='ticket_ok_created'),
        pytest.param(
            '0808', True, True, '2222', 1, id='ticket_ok_transporting',
        ),
        pytest.param('0909', False, True, '3333', 1, id='ticket_ok_finished'),
        pytest.param('4242', False, True, '4242', 1, id='ticket_bad'),
        pytest.param(
            '1010', False, False, '4444', 1, id='ticket_on_other_shuttle',
        ),
        pytest.param(
            '1212',
            True,
            True,
            '5555',
            1,
            id='same_ticket_on_finished_and_created',
        ),
        pytest.param(
            '8888',  # 8889, 8887
            True,
            True,
            '8888',
            3,
            id='three_passengers_ok',
        ),
    ],
)
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'main_route': {
            'driver': 'shuttle_control.routes.main_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.main_route.name_for_passenger'
            ),
        },
    },
)
async def test_pickup_passengers_with_confirmation_code(
        taxi_shuttle_control,
        ticket,
        expected_response_check_valid,
        passenger_change_status,
        confirmation_code,
        tickets_cnt,
        pgsql,
):
    req_headers = copy.deepcopy(HEADERS)
    req_headers['X-YaTaxi-Park-Id'] = 'dbid_1'
    req_headers['X-YaTaxi-Driver-Profile-Id'] = 'uuid_1'

    response = await taxi_shuttle_control.post(
        '/driver/v1/shuttle-control/v2/shuttle/pickup_passengers?'
        'shuttle_id=Pmp80rQ23L4wZYxd',
        headers=req_headers,
        json={
            'pickup_position': {'some': 'taximeter_data'},
            'passengers': [{'ticket': confirmation_code}],
        },
    )

    assert response.status_code == 200
    resp = response.json()
    state = copy.deepcopy(STATE_2)
    waiting_cnt = 5

    if (
            confirmation_code == '1111'
            or confirmation_code == '8888'
            or confirmation_code == '5555'
    ):
        for _ in range(tickets_cnt):
            state['route']['points'][0]['meta']['passengers'].append(
                {
                    'type': 'accepted',
                    'background_color': 'main_green',
                    'code': confirmation_code,
                },
            )
        waiting_cnt = 5 - tickets_cnt

    take_passengers_text = 'Заберите ' + str(waiting_cnt) + ' пассажиров'
    if waiting_cnt == 1:
        take_passengers_text = 'Заберите пассажира'
    state['route']['points'][0]['meta']['title'] = take_passengers_text

    for _ in range(waiting_cnt):
        state['route']['points'][0]['meta']['passengers'].append(
            {'type': 'incoming', 'background_color': 'main_green'},
        )

    if expected_response_check_valid:

        if ticket in ('0707', '0808', '1212', '8888'):
            assert 'meta' in resp['ticket_check_results'][confirmation_code]
            price = 10 * tickets_cnt
            assert resp['ticket_check_results'][confirmation_code]['meta'] == {
                'type': 'detail_tip',
                'right_tip': {
                    'icon': {'icon_type': 'cash2'},
                    'form': 'square',
                },
                'title': 'Оплата наличными',
                'title_text_style': 'body',
                'subtitle': str(price) + ' руб.',
                'subtitle_text_style': 'title_medium',
                'secondary_text_color': 'main_text',
            }
            del resp['ticket_check_results'][confirmation_code]['meta']

        assert resp['ticket_check_results'] == {
            confirmation_code: {
                'result': 'ok',
                'text': (
                    f'Бронь {confirmation_code} успешно проверена. '
                    f'Количество пассажиров: ' + str(tickets_cnt)
                ),
            },
        }
        rows = select_named(
            'SELECT sp.status FROM state.passengers sp '
            'INNER JOIN state.booking_tickets bt '
            'ON sp.booking_id = bt.booking_id '
            'WHERE sp.shuttle_id=2 AND '
            f'bt.code=\'{ticket}\' AND '
            'sp.status NOT IN (\'cancelled\', \'finished\')',
            pgsql['shuttle_control'],
        )
        assert len(rows) == 1
        assert rows[0]['status'] == 'transporting'
    else:
        assert resp['ticket_check_results'] == {
            confirmation_code: {
                'result': 'invalid_ticket',
                'text': (
                    f'Информация о брони по коду {confirmation_code}'
                    f' отсутствует'
                ),
            },
        }
    assert resp['status'] == state
