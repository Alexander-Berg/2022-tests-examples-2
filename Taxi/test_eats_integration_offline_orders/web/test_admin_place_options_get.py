import http

import pytest

from test_eats_integration_offline_orders import conftest


@pytest.mark.parametrize(
    'params, expected_code, expected_response',
    (
        pytest.param(
            {'place_id': 'place_id__1'},
            http.HTTPStatus.OK,
            {
                'notifications': {
                    'iiko_waiter': {
                        'enabled': False,
                        'department_id': 'department_1',
                    },
                    'telegram_chats': [
                        {
                            'chat_id': 100500,
                            'chat_type': 'group',
                            'enabled': True,
                        },
                    ],
                    'telegram_managers': [conftest.ADMIN_PLACE_1_MANGERS_1],
                },
                'iiko_transport': {
                    'organization_id': 'organization_id_1',
                    'place_id': 'place_id__1',
                    'terminal_group_id': 'terminal_group_id_1',
                    'updated_at': '2022-05-16 13:00:30',
                },
                'options': {
                    'enabled': True,
                    'show_tips': True,
                    'show_menu': True,
                    'order_online': True,
                    'payment_offline': True,
                    'payment_online': True,
                    'payment_split': True,
                    'show_call_waiter': True,
                    'parse_menu': True,
                },
            },
            id='ok-options-found',
        ),
        pytest.param(
            {'place_id': 'place_id__2'},
            http.HTTPStatus.OK,
            {
                'notifications': {
                    'telegram_chats': [
                        {
                            'chat_id': -888888888,
                            'chat_type': 'group',
                            'enabled': False,
                        },
                        {
                            'chat_id': 19921031,
                            'chat_type': 'group',
                            'enabled': True,
                        },
                        {
                            'chat_id': 1234567890,
                            'chat_type': 'group',
                            'enabled': True,
                        },
                    ],
                    'telegram_managers': [],
                },
                'options': {
                    'enabled': True,
                    'show_tips': True,
                    'show_menu': True,
                    'order_online': False,
                    'payment_offline': True,
                    'payment_online': True,
                    'payment_split': True,
                    'show_call_waiter': True,
                    'parse_menu': False,
                },
            },
            id='ok-options-not-found-enabled-null',
        ),
        pytest.param(
            {'place_id': 'place_id__3'},
            http.HTTPStatus.OK,
            {
                'notifications': {
                    'iiko_waiter': {
                        'enabled': True,
                        'department_id': 'department_3',
                    },
                    'telegram_chats': [],
                    'telegram_managers': [],
                },
                'options': {
                    'enabled': False,
                    'show_tips': True,
                    'show_menu': True,
                    'order_online': False,
                    'payment_offline': True,
                    'payment_online': True,
                    'payment_split': True,
                    'show_call_waiter': True,
                    'parse_menu': False,
                },
            },
            id='ok-options-not-found-enabled-false',
        ),
        pytest.param(
            {'place_id': '100000'},
            http.HTTPStatus.NOT_FOUND,
            {'message': 'place not found', 'code': 'not_found'},
            id='not-found',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=[
        'restaurants.sql',
        'restaurants_options.sql',
        'iiko_waiter_data.sql',
        'iiko_transport_meta.sql',
        'telegram_chats.sql',
        'telegram_managers.sql',
    ],
)
async def test_admin_place_options_get(
        web_app_client, params, expected_code, expected_response,
):
    response = await web_app_client.get(
        '/admin/v1/place/options', params=params,
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
