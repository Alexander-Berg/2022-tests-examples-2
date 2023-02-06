import pytest

PHONE_ID_1 = '00aaaaaaaaaaaaaaaaaaaa01'

EXPECT_CLIENT_FLAGS = {
    'show_driving_route': True,
    'door_to_door': False,
    'icons_type': 'c2c',
    'metrica_order_type': 'c2c',
    'show_point_a': True,
    'show_track': True,
}


async def test_ping(taxi_order_route_sharing_web):
    response = await taxi_order_route_sharing_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''


def count_shown(pgsql, shared_key, phone_id) -> int:
    cursor = pgsql['order_route_sharing'].cursor()
    cursor.execute(
        f'SELECT count(*) FROM order_route_sharing.phone_ids '
        f'WHERE sharing_key=\'{shared_key}\' AND phone_id=\'{phone_id}\' '
        f'AND is_shown=True',
    )

    return cursor.fetchone()[0]


@pytest.mark.parametrize(
    'phone_id, expect_response',
    [
        pytest.param(
            PHONE_ID_1,
            {'shared_orders': [{'key': 'key_1', 'status': 'search'}]},
            id='sharing key exist',
        ),
        pytest.param(
            'any_phone_id', {'shared_orders': []}, id='sharing key not exist',
        ),
        pytest.param(
            '00aaaaaaaaaaaaaaaaaaaa04',
            {'shared_orders': [{'key': 'key_4', 'status': 'search'}]},
            id=' status',
        ),
        pytest.param(
            '00aaaaaaaaaaaaaaaaaaaa03',
            {'shared_orders': [{'key': 'key_5', 'status': 'search'}]},
            id='check corp client id',
        ),
    ],
)
@pytest.mark.config(
    ORDER_ROUTE_SHARING_SUPPORTED_CORPS={
        'corp_client_id_1': {'ru': 'Яндекс', 'en': 'Yandex'},
    },
)
async def test_get_sharing_keys(
        taxi_order_route_sharing_web, phone_id, expect_response,
):
    response = await taxi_order_route_sharing_web.get(
        '/v1/shared_orders', headers={'X-YaTaxi-PhoneId': phone_id},
    )
    assert response.status == 200
    content = await response.json()
    assert content == expect_response


@pytest.mark.translations(
    client_messages={
        'shared_order.popup_title.econom': {'ru': 'Такси'},
        'shared_order.status_title.c2c.econom.driving': {
            'ru': 'Водитель едет к пассажиру',
        },
        'shared_order.status_title.c2c.econom.transporting.with_time': {
            'ru': 'Водитель выполняет заказ, осталось %(minutes_left)s мин',
        },
    },
)
@pytest.mark.parametrize(
    'key, phone_id, status, tariff_class, time_left, expect_info',
    [
        pytest.param(
            'key_5',
            '00aaaaaaaaaaaaaaaaaaaa03',
            'driving',
            'econom',
            None,
            {
                'popup_title': 'Такси',
                'status_title': 'Водитель едет к пассажиру',
            },
            id='econom',
        ),
        pytest.param(
            'key_6',
            '00aaaaaaaaaaaaaaaaaaaa06',
            'transporting',
            'business',
            123.45,
            {
                'popup_title': 'Такси',
                'status_title': 'Водитель выполняет заказ, осталось 2 мин',
            },
            id='business',
        ),
    ],
)
async def test_info(
        taxi_order_route_sharing_web,
        pgsql,
        key,
        phone_id,
        status,
        tariff_class,
        time_left,
        expect_info,
):
    params = {'key': key, 'status': status}
    if time_left:
        params['time_left'] = time_left

    response = await taxi_order_route_sharing_web.get(
        '/v1/info',
        params=params,
        headers={'Accept-Language': 'ru', 'X-YaTaxi-PhoneId': phone_id},
    )
    if not expect_info:
        assert response.status == 404
        return

    expect_info.update(
        {
            'apartment_label': '',
            'intercom_label': '',
            'porch_label': '',
            'floor_label': '',
            'status_icon': f'class_{tariff_class}_icon_7',
        },
    )

    assert response.status == 200

    content = await response.json()
    assert count_shown(pgsql, key, phone_id) == 1

    assert content['display_info'] == expect_info
    assert content['internal'] == {'show_phone': True}

    expect_client_flags = EXPECT_CLIENT_FLAGS
    assert content['client_flags'] == expect_client_flags


@pytest.mark.parametrize(
    'key',
    [
        pytest.param('key_1', id='exist'),
        pytest.param('key_66', id='not exist'),
    ],
)
async def test_track(taxi_order_route_sharing_web, key):
    response = await taxi_order_route_sharing_web.get(
        '/v1/track', params={'key': key},
    )
    if key == 'key_66':
        assert response.status == 404
        return

    assert response.status == 200
    content = await response.json()
    assert not content['static_icon']


@pytest.mark.parametrize(
    'key',
    [
        pytest.param('key_1', id='exist'),
        pytest.param('key_66', id='not exist'),
    ],
)
async def test_order_id(taxi_order_route_sharing_web, key):
    response = await taxi_order_route_sharing_web.get(
        '/v1/internal/order_id', params={'key': key},
    )
    if key == 'key_66':
        assert response.status == 404
        return

    assert response.status == 200
    content = await response.json()
    assert content['order_id'] == 'order_1'
