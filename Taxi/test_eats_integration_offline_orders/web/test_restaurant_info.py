import http

import pytest


def _create_response(
        table_id: str,
        enabled: bool = True,
        logo: str = '',
        title: str = '',
        greeting: str = '',
        tips_link: str = '',
        theme_id: str = '',
        call_waiter_enabled: bool = False,
        show_menu: bool = True,
        show_tips: bool = True,
        split_enabled: bool = True,
        offline_payment: bool = True,
        online_payment: bool = True,
        order_online: bool = True,
):
    return {
        'call_waiter_enabled': call_waiter_enabled,
        'options': {
            'show_call_waiter': call_waiter_enabled,
            'offline_payment': offline_payment,
            'online_payment': online_payment,
            'show_menu': show_menu,
            'show_tips': show_tips,
            'split_enabled': split_enabled,
            'order_online': order_online,
        },
        'enabled': enabled,
        'table_id': table_id,
        'theme_id': theme_id,
        'logo': logo,
        'title': title,
        'greeting': greeting,
        'tips_link': tips_link,
        'ya_discount': {'type': 'number', 'val': 0},
    }


@pytest.mark.parametrize(
    ('table_uuid', 'expected_code', 'expected_response'),
    (
        pytest.param(
            'uuid__1',
            http.HTTPStatus.OK,
            _create_response(
                table_id='1',
                theme_id='place_id__1_slug',
                title='Самый тестовый ресторан',
                greeting=(
                    'Он настолько тестовый, что его можно только тестировать'
                ),
                logo=(
                    'https://avatars.mds.yandex.net/get-inplace/135516/'
                    '147734d81d1de576476c6a217679e1c29f83eeb7/orig'
                ),
                tips_link='some_tips_link',
            ),
            id='OK',
        ),
        pytest.param(
            'uuid__2',
            http.HTTPStatus.OK,
            _create_response(
                table_id='2',
                theme_id='restaurant_slug_2',
                title='Ресторан "Мясо"',
                order_online=False,
            ),
            id='OK-no-options',
        ),
        pytest.param(
            'uuid__7',
            http.HTTPStatus.OK,
            _create_response(
                table_id='7',
                theme_id='restaurant_slug_4',
                title='Кафе "У меня нет фантазии"',
                order_online=False,
            ),
            id='OK-options-enabled-none',
        ),
        pytest.param(
            'qweqrer',
            http.HTTPStatus.NOT_FOUND,
            {'message': 'UUID not found'},
            id='not-found',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'restaurants_options.sql', 'tables.sql'],
)
async def test_get_restaurant_info(
        web_app_client, table_uuid, expected_code, expected_response,
):
    response = await web_app_client.get(
        '/v1/restaurant-info', params={'uuid': table_uuid},
    )
    assert response.status == expected_code
    data = await response.json()
    assert set(expected_response.keys()) <= set(data.keys())


@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql', 'tables.sql'],
)
async def test_get_theme_id_from_restaurant_info(
        web_app_client, table_uuid, restaurant_slug,
):
    response = await web_app_client.get(
        '/v1/restaurant-info', params={'uuid': table_uuid},
    )
    assert response.status == 200
    data = await response.json()
    assert 'theme_id' in data
    assert data['theme_id'] == restaurant_slug


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'restaurants_options.sql', 'tables.sql'],
)
async def test_get_restaurant_info_with_notifier(
        web_app_client, table_uuid, load_json, notify_telegram_selector,
):
    response = await web_app_client.get(
        f'/v1/restaurant-info?uuid={table_uuid}',
    )
    assert response.status == 200
    data = await response.json()
    assert set(
        load_json('restaurant_info_response_notifier.json').keys(),
    ) <= set(data.keys())


@pytest.mark.client_experiments3(
    consumer='eats-integration-offline-orders/ya_discount',
    config_name='eats_integration_offline_orders-ya_discount',
    args=[{'name': 'place_id', 'type': 'string', 'value': 'place_id__1'}],
    value={'val': '10%'},
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql', 'tables.sql'],
)
async def test_get_restaurant_info_with_ya_discount(
        web_app_client, table_uuid, load_json,
):
    response = await web_app_client.get(
        f'/v1/restaurant-info?uuid={table_uuid}',
    )
    assert response.status == 200
    data = await response.json()
    assert data['ya_discount'] == {'type': 'percents', 'val': 10}
