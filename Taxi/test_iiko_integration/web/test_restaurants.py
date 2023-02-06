import pytest


LOCALIZED_ADDRESS = 'Садовническая 82с2'
SCANNER_DEEPLINK = 'yandextaxi://qr_scanner'
CAFE_ADDRESS = {
    'fullname': LOCALIZED_ADDRESS,
    'country': 'Российская Федерация',
    'geopoint': [1, 1],
    'locality': 'Москва',
}

# pylint: disable=C0103
pytestmark = [
    pytest.mark.translations(
        qr_payment={
            'coffe_point': {'ru': 'Point Coffe & Food'},
            'coffe': {'ru': 'Кофе'},
        },
        client_messages={
            'common_strings.qr_pay.restaurant.error.title': {
                'ru': 'Не удалось загрузить',
            },
            'common_strings.qr_pay.restaurants.error.title': {
                'ru': 'Не удалось загрузить',
            },
            'common_strings.qr_pay.restaurants.error.text': {
                'ru': 'Что то пошло не так',
            },
            'qr_pay.restaurants.title': {'ru': 'Где получить кэшбэк'},
            'qr_pay.restaurants.list_button_title': {
                'ru': 'Получить кэшбэк в ресторане',
            },
            'qr_pay.restaurants.ride_button_title': {'ru': 'Поехать туда'},
            'qr_pay.cashback.title': {'ru': 'Кэшбек на Плюс'},
            'qr_pay.restaurants.restaurant_not_found': {
                'ru': 'Нет такого ресторана',
            },
            'qr_pay.restaurants.restaurant_disabled': {
                'ru': 'QR оплата не работает в этом ресторане',
            },
            'qr_pay.qr_button.title': {'ru': 'Сканировать QR-код'},
            'button_title': {'ru': 'Кнопка'},
        },
    ),
]


async def _default_request(web_app_client, lat='1.1', lon='1.2'):
    return await web_app_client.get(
        '/4.0/qr-pay/v1/restaurants',
        headers={'Accept-Language': 'ru-RU'},
        params={'lat': lat, 'lon': lon},
    )


def _add_required_config_fields(config, default_config):
    for config_key in config:
        default_config = default_config.copy()
        default_config.update(config[config_key])
        config[config_key] = default_config
    return config


def _update_restaurant_config(config):
    return _add_required_config_fields(
        config,
        {
            'restaurant_group_id': 'restaurant_group_01',
            'api_key_hash': 'iQCDpzllV2TQFNZJcTae1wcCLp+utI607sP3a+hqzk0=',
            'eda_place_id': 1,
            'geosearch_id': '1400568734',
            'address_ru': LOCALIZED_ADDRESS,
            'address_en': 'address_en',
            'geopoint': {'lon': 1, 'lat': 1},
            'phone_number': '1',
            'inn': '1234567890',
        },
    )


def _update_group_config_fields(config):
    return _add_required_config_fields(
        config,
        {
            'name_tanker_key': 'coffe_point',
            'eda_client_id': 1,
            'cashback': '30',
            'commission': '10',
            'tag_tanker_key': 'coffe',
            'upper_text_tanker_key': 'default_upper',
            'deeplink_template': 'default_{order_id}_1',
            'lower_text_tanker_key': 'default_lower',
        },
    )


@pytest.mark.parametrize(
    (),
    [
        pytest.param(
            marks=[
                pytest.mark.config(IIKO_INTEGRATION_SERVICE_AVAILABLE=False),
            ],
            id='service disabled',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(IIKO_INTEGRATION_SERVICE_AVAILABLE=True),
            ],
            id='restaurants not found',
        ),
    ],
)
async def test_restaurants_404(web_app_client):
    response = await _default_request(web_app_client)
    assert response.status == 404

    response_json = await response.json()
    assert response_json == {
        'code': 'restaurants_not_found',
        'details': {'title': 'Не удалось загрузить'},
        'message': 'Что то пошло не так',
    }


@pytest.mark.config(
    IIKO_INTEGRATION_SERVICE_AVAILABLE=True,
    IIKO_INTEGRATION_RESTAURANT_GROUP_INFO=_update_group_config_fields(
        {'restaurant_group_01': {}},
    ),
    IIKO_INTEGRATION_RESTAURANT_INFO=_update_restaurant_config(
        {
            'restaurant_01': {
                'geopoint': {'lat': 1.3, 'lon': 1.4},
                'phone_number': '+7 (900) 455-32-15',
            },
            'restaurant_02': {
                'geopoint': {'lat': 1.3, 'lon': 1.4},
                'phone_number': '+7 (900) 455-32-16',
                'enabled': False,
            },
        },
    ),
    QR_PAY_RESTAURANTS_HANDLER_SETTINGS={
        'details_template': '{restaurant_address}',
        'subtitle_template': '{restaurant_tag}{restaurant_work_hours}',
    },
)
async def test_single_restaurant(web_app_client, mockserver):
    response = await _default_request(web_app_client)
    assert response.status == 200
    response_json = await response.json()
    assert response_json['restaurants'] == [
        {
            'title': 'Point Coffe & Food',
            'subtitle': 'Кофе',
            'details': LOCALIZED_ADDRESS,
            'cashback': {'rate': '30%'},
            'open_deeplink': 'yandextaxi://qr_restaurant?id=restaurant_01',
            'restaurant_id': 'restaurant_01',
        },
    ]
    assert response_json['buttons'] == [
        {
            'deeplink': 'yandextaxi://qr_scanner',
            'style': 'cashback',
            'title': 'Получить кэшбэк в ресторане',
            'type': 'deeplink',
        },
    ]


async def _get_fields(*args, field, **kwargs):
    response = await _default_request(*args, **kwargs)
    assert response.status == 200
    restaurants = await response.json()
    return [restaurant[field] for restaurant in restaurants['restaurants']]


@pytest.mark.config(
    IIKO_INTEGRATION_SERVICE_AVAILABLE=True,
    IIKO_INTEGRATION_RESTAURANT_GROUP_INFO=_update_group_config_fields(
        {
            'restaurant_group_01': {'cashback': '1'},
            'restaurant_group_02': {'cashback': '2'},
        },
    ),
    IIKO_INTEGRATION_RESTAURANT_INFO=_update_restaurant_config(
        {
            'restaurant_01': {
                'restaurant_group_id': 'restaurant_group_01',
                'geopoint': {'lon': 1, 'lat': 1},
            },
            'restaurant_02': {
                'restaurant_group_id': 'restaurant_group_02',
                'geopoint': {'lon': 1, 'lat': 1.4},
                'phone_number': '2',
            },
        },
    ),
)
@pytest.mark.parametrize(
    ('user_lat', 'expected_cashback_order'),
    [
        pytest.param(
            '1.1', [{'rate': '1%'}, {'rate': '2%'}], id='user_closer_to_first',
        ),
        pytest.param(
            '1.3',
            [{'rate': '2%'}, {'rate': '1%'}],
            id='user_closer_to_second',
        ),
    ],
)
async def test_sorting(
        web_app_client, mockserver, user_lat, expected_cashback_order,
):
    cashback = await _get_fields(
        web_app_client, field='cashback', lat=user_lat,
    )
    assert cashback == expected_cashback_order


@pytest.mark.config(
    IIKO_INTEGRATION_SERVICE_AVAILABLE=True,
    IIKO_INTEGRATION_RESTAURANT_GROUP_INFO=_update_group_config_fields(
        {
            'restaurant_group_01': {'cashback': '1'},
            'restaurant_group_03': {
                'cashback': '3',
                'name_tanker_key': 'bad key',
                'tag_tanker_key': 'bad key',
            },
        },
    ),
    IIKO_INTEGRATION_RESTAURANT_INFO=_update_restaurant_config(
        {
            'restaurant_01': {'restaurant_group_id': 'restaurant_group_01'},
            'restaurant_02': {'restaurant_group_id': 'restaurant_group_02'},
            'restaurant_03': {'restaurant_group_id': 'restaurant_group_03'},
        },
    ),
)
async def test_restaurant_failure_handling(web_app_client, mockserver):
    assert await _get_fields(web_app_client, field='cashback') == [
        {'rate': '1%'},
    ]


@pytest.mark.config(
    IIKO_INTEGRATION_SERVICE_AVAILABLE=True,
    IIKO_INTEGRATION_RESTAURANT_GROUP_INFO=_update_group_config_fields(
        {'restaurant_group_01': {}},
    ),
    IIKO_INTEGRATION_RESTAURANT_INFO=_update_restaurant_config(
        {
            'restaurant_01': {
                'geopoint': {'lon': 1, 'lat': 1.01},
                'work_hours_ru': 'Пн-Пт 9:00 - 20:00',
                'work_hours_en': 'Mon-Fri 9AM - 8PM',
            },
            'restaurant_02': {'geopoint': {'lon': 1, 'lat': 1.02}},
            'restaurant_03': {'geopoint': {'lon': 1, 'lat': 1.03}},
            'restaurant_04': {
                'geopoint': {'lon': 1, 'lat': 1.03},
                'enabled': False,
            },
        },
    ),
    QR_PAY_RESTAURANTS_HANDLER_SETTINGS={
        'limit': 1,
        'subtitle_template': (
            'test subtitle template params {user_lat} '
            '{user_lon} {restaurant_lat} {restaurant_lon} '
            '{restaurant_tag} {restaurant_address}'
        ),
        'details_template': (
            'test details template params {restaurant_work_hours}'
        ),
        'list_buttons': [
            {
                'title_key': 'button_title',
                'style': 'default',
                'deeplink_template': (
                    'test list deeplink template params 1 '
                    '{user_lat} {user_lon}'
                ),
            },
            {
                'title_key': 'button_title',
                'style': 'cashback',
                'deeplink_template': (
                    'test list deeplink template params 2 '
                    '{user_lat} {user_lon}'
                ),
            },
        ],
    },
)
async def test_restaurants_list_settings(web_app_client, mockserver):
    response = await _default_request(web_app_client, lat=1, lon=1)
    assert response.status == 200

    response_json = await response.json()
    assert response_json == {
        'title': 'Где получить кэшбэк',
        'buttons': [
            {
                'deeplink': 'test list deeplink template params 1 1.0 1.0',
                'style': 'default',
                'title': 'Кнопка',
                'type': 'deeplink',
            },
            {
                'deeplink': 'test list deeplink template params 2 1.0 1.0',
                'style': 'cashback',
                'title': 'Кнопка',
                'type': 'deeplink',
            },
        ],
        'restaurants': [
            {
                'cashback': {'rate': '30%'},
                'title': 'Point Coffe & Food',
                'subtitle': (
                    'test subtitle template params 1.0 1.0 1.01 1 Кофе '
                    + LOCALIZED_ADDRESS
                ),
                'details': 'test details template params Пн-Пт 9:00 - 20:00',
                'open_deeplink': 'yandextaxi://qr_restaurant?id=restaurant_01',
                'restaurant_id': 'restaurant_01',
            },
        ],
    }


async def _get_restaurant(
        web_app_client,
        mockserver,
        restaurant_id='restaurant_01',
        expected_code=200,
):
    response = await web_app_client.get(
        '/4.0/qr-pay/v1/restaurant',
        headers={'Accept-Language': 'ru-RU'},
        params={'lat': '1', 'lon': '1', 'id': restaurant_id},
    )

    assert response.status == expected_code
    return await response.json()


@pytest.mark.config(
    IIKO_INTEGRATION_RESTAURANT_GROUP_INFO=_update_group_config_fields(
        {'restaurant_group_01': {'default_card_image_url': 'image_url'}},
    ),
    IIKO_INTEGRATION_RESTAURANT_INFO=_update_restaurant_config(
        {
            'restaurant_01': {'work_hours_ru': 'Пн-Пт 9:00 - 20:00'},
            'restaurant_03': {
                'enabled': False,
                'work_hours_ru': 'Пн-Пт 9:00 - 20:00',
            },
        },
    ),
)
@pytest.mark.parametrize(
    ('restaurant_id', 'expected_code', 'expected_body'),
    [
        pytest.param(
            'restaurant_01',
            200,
            {
                'address_text': LOCALIZED_ADDRESS,
                'cashback': {'rate': '30%'},
                'name': 'Point Coffe & Food',
                'phone': '1',
                'work_hours': 'Пн-Пт 9:00 - 20:00',
                'card_image_url': 'image_url',
                'ui_elements': {
                    'qr_button': {
                        'title': 'Сканировать QR-код',
                        'deeplink': 'yandextaxi://qr_scanner',
                    },
                    'buttons': [
                        {
                            'deeplink': (
                                'yandextaxi://route?start-lat=1.0&'
                                'start-lon=1.0&end-lat=1&end-lon=1'
                            ),
                            'title': 'Поехать туда',
                            'type': 'deeplink',
                            'style': 'default',
                        },
                    ],
                },
            },
            id='restaurant-found-by-id',
        ),
        pytest.param(
            'restaurant_02',
            404,
            {
                'code': 'restaurant_not_found',
                'message': 'Нет такого ресторана',
                'details': {'title': 'Не удалось загрузить'},
            },
            id='restaurant-not-found-by-id',
        ),
        pytest.param(
            'restaurant_03',
            404,
            {
                'code': 'restaurant_disabled',
                'message': 'QR оплата не работает в этом ресторане',
                'details': {'title': 'Не удалось загрузить'},
            },
            id='restaurant-disabled',
        ),
    ],
)
async def test_restaurant_handler(
        web_app_client,
        mockserver,
        restaurant_id,
        expected_code,
        expected_body,
):
    response_json = await _get_restaurant(
        web_app_client, mockserver, restaurant_id, expected_code,
    )
    assert response_json == expected_body


@pytest.mark.config(
    IIKO_INTEGRATION_RESTAURANT_GROUP_INFO=_update_group_config_fields(
        {
            'restaurant_group_01': {
                'default_card_image_url': 'default_image_url',
            },
        },
    ),
    IIKO_INTEGRATION_RESTAURANT_INFO=_update_restaurant_config(
        {'restaurant_01': {'card_image_url': 'image_url'}},
    ),
)
async def test_card_image_tag(web_app_client, mockserver):
    response_json = await _get_restaurant(web_app_client, mockserver)
    assert response_json['card_image_url'] == 'image_url'
