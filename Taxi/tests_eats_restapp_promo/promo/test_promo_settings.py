import pytest

# max_order_price not returned in response

GIFT = {
    'type': 'gift',
    'title': 'Блюдо в подарок',
    'description': (
        'Познакомить пользователей с новыми '
        'блюдами или поднять средний чек.'
    ),
    'can_create': True,
    'can_edit': False,
    'can_pause': True,
    'can_stop': False,
    'can_show_stats': False,
    'is_multiple_places_allowed': True,
    'icon_url': 'invalid.invalid2',
    'is_new': True,
    'configuration': {
        'item_id': {'disabled_categories': ['cat1', 'cat2']},
        'max_order_price': {'maximum': 200, 'minimum': 100},
    },
}

PLUS_HAPPY_HOURS = {
    'type': 'plus_happy_hours',
    'title': 'Повышенный кешбэк в счастливые часы',
    'description': 'Предложите повышенный кешбек за заказ в мёртвые часы.',
    'can_create': False,
    'can_edit': True,
    'can_pause': False,
    'can_stop': True,
    'can_show_stats': False,
    'is_multiple_places_allowed': False,
    'icon_url': 'invalid.invalid3',
    'is_new': False,
    'configuration': {
        'cashback': {'minimum': 1, 'maximum': 2},
        'max_order_price': {'minimum': 2, 'maximum': 5},
        'order_indexes': [1, 2, 3],
        'days_from_last_order': [
            {'days': 7, 'name': 'Неделя'},
            {'days': 14, 'name': '2 Недели'},
        ],
    },
}

PLUS_HAPPY_HOURS_DEFAULT = {
    'type': 'plus_happy_hours',
    'title': 'Повышенный кешбэк в счастливые часы',
    'description': 'Предложите повышенный кешбек за заказ в мёртвые часы.',
    'can_create': False,
    'can_edit': False,
    'can_pause': False,
    'can_stop': False,
    'can_show_stats': False,
    'is_multiple_places_allowed': False,
    'icon_url': 'invalid.invalid',
    'is_new': False,
    'configuration': {'cashback': {'minimum': 0, 'maximum': 0}},
}

FREE_DELIVERY = {
    'type': 'free_delivery',
    'title': 'Бесплатная доставка',
    'description': 'Предложите бесплатную доставку.',
    'can_create': False,
    'can_edit': False,
    'can_pause': False,
    'can_stop': False,
    'can_show_stats': False,
    'is_multiple_places_allowed': False,
    'icon_url': 'invalid.invalid1',
    'is_new': False,
    'configuration': {
        'max_order_price': {'minimum': 2, 'maximum': 5},
        'min_order_price': {'minimum': 100, 'maximum': 1000},
    },
}

DISCOUNT = {
    'type': 'discount',
    'title': 'Скидка на меню или некоторые позиции',
    'description': 'Увеличить выручку ресторана или поднять средний чек.',
    'can_create': True,
    'can_edit': True,
    'can_pause': True,
    'can_stop': False,
    'can_show_stats': False,
    'is_multiple_places_allowed': False,
    'icon_url': 'invalid.invalid4',
    'is_new': False,
    'configuration': {
        'discount': {'maximum': 40.0, 'minimum': 5.0},
        'item_ids': {
            'disabled_categories': [
                'Напитки',
                'Гарниры',
                'Соусы',
                'Дополнительно',
            ],
            'min_items': 3,
        },
        'available_shipping_types': [
            {'value': 'delivery', 'name': 'Доставка'},
            {'value': 'pickup', 'name': 'Недоставка'},
        ],
    },
}

ONE_PLUS_ONE = {
    'type': 'one_plus_one',
    'title': 'Два по цене одного',
    'description': (
        'Увеличить количество заказов или познакомить '
        'пользователей c новыми блюдами.'
    ),
    'can_create': True,
    'can_edit': False,
    'can_pause': False,
    'can_stop': True,
    'can_show_stats': False,
    'is_multiple_places_allowed': True,
    'icon_url': 'invalid.invalid5',
    'is_new': True,
    'configuration': {'item_ids': {'disabled_categories': [], 'min_items': 0}},
}

PLUS_FIRST_ORDERS = {
    'type': 'plus_first_orders',
    'title': 'Повышенный кешбэк для новичков',
    'description': (
        'Привлечь новых пользователей, предложив '
        'им повышенный кешбек за первые заказы.'
    ),
    'can_create': True,
    'can_edit': False,
    'can_pause': False,
    'can_stop': True,
    'can_show_stats': False,
    'is_multiple_places_allowed': True,
    'icon_url': 'invalid.invalid6',
    'is_new': True,
    'configuration': {
        'cashback': {'maximum': 30, 'minimum': 5},
        'max_order_price': {'minimum': 2, 'maximum': 5},
    },
}


@pytest.mark.parametrize(
    'partner_id, available',
    [
        pytest.param(
            1,
            [
                DISCOUNT,
                FREE_DELIVERY,
                GIFT,
                ONE_PLUS_ONE,
                PLUS_FIRST_ORDERS,
                PLUS_HAPPY_HOURS,
            ],
            marks=pytest.mark.experiments3(filename='promos_settings.json'),
            id='6_promos',
        ),
        pytest.param(
            2,
            [PLUS_HAPPY_HOURS_DEFAULT],
            marks=pytest.mark.experiments3(filename='promos_settings.json'),
            id='1_promo',
        ),
        pytest.param(
            1,
            [FREE_DELIVERY, ONE_PLUS_ONE, PLUS_HAPPY_HOURS],
            marks=pytest.mark.experiments3(
                filename='promos_settings_with_disabled_promos.json',
            ),
            id='disabled',
        ),
        pytest.param(
            1,
            [],
            marks=pytest.mark.experiments3(
                filename='promos_settings_empty.json',
            ),
            id='empty',
        ),
        pytest.param(
            1,
            'expected_response_all.json',
            marks=pytest.mark.experiments3(
                filename='promos_settings_all.json',
            ),
            id='all',
        ),
        pytest.param(
            1,
            'expected_response_can_show_stats.json',
            marks=pytest.mark.experiments3(
                filename='promo_settings_can_show_stats.json',
            ),
            id='can_show_stats',
        ),
    ],
)
async def test_promo_settings(
        taxi_eats_restapp_promo,
        partner_id,
        available,
        mock_partners_info_200,
        load_json,
):
    """
    Тест проверяет, что ходим в конфиги и достаем актуальные акции.
    Одна из акций имеет restrictions,
    проверяем, что они прокидываются в ответ ручки.
    """

    if isinstance(available, str):
        available = load_json(available)

    response = await taxi_eats_restapp_promo.get(
        '/4.0/restapp-front/promo/v1/promo/settings',
        headers={'X-YaEda-PartnerId': str(partner_id)},
    )

    assert mock_partners_info_200.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'available': available, 'tabs': []}


@pytest.mark.parametrize(
    'partner_id, available',
    [
        pytest.param(
            1,
            [
                {'name': 'Все акции', 'types': []},
                {
                    'name': 'Увеличить количество заказов',
                    'types': ['discount'],
                },
                {
                    'name': '3 типов',
                    'types': ['discount', 'free_delivery', 'gift'],
                },
                {
                    'name': 'другие 3 типов',
                    'types': [
                        'one_plus_one',
                        'plus_first_orders',
                        'plus_happy_hours',
                    ],
                },
            ],
            marks=[
                pytest.mark.experiments3(filename='promos_settings.json'),
                pytest.mark.experiments3(filename='promos_settings_tabs.json'),
            ],
            id='6_promos',
        ),
        pytest.param(
            2,
            [
                {'name': 'Все акции', 'types': []},
                {'name': 'другие 3 типов', 'types': ['plus_happy_hours']},
            ],
            marks=[
                pytest.mark.experiments3(filename='promos_settings.json'),
                pytest.mark.experiments3(filename='promos_settings_tabs.json'),
            ],
            id='1_promo',
        ),
        pytest.param(
            1,
            [
                {'name': 'Все акции', 'types': []},
                {'name': '3 типов', 'types': ['free_delivery']},
                {
                    'name': 'другие 3 типов',
                    'types': ['one_plus_one', 'plus_happy_hours'],
                },
            ],
            marks=[
                pytest.mark.experiments3(
                    filename='promos_settings_with_disabled_promos.json',
                ),
                pytest.mark.experiments3(filename='promos_settings_tabs.json'),
            ],
            id='disabled',
        ),
        pytest.param(
            1,
            [],
            marks=[
                pytest.mark.experiments3(
                    filename='promos_settings_empty.json',
                ),
                pytest.mark.experiments3(filename='promos_settings_tabs.json'),
            ],
            id='empty',
        ),
        pytest.param(
            1,
            [
                {'name': 'Все акции', 'types': []},
                {
                    'name': 'Увеличить количество заказов',
                    'types': ['discount'],
                },
                {
                    'name': '3 типов',
                    'types': ['discount', 'free_delivery', 'gift'],
                },
                {
                    'name': 'другие 3 типов',
                    'types': [
                        'one_plus_one',
                        'plus_first_orders',
                        'plus_happy_hours',
                    ],
                },
            ],
            marks=[
                pytest.mark.experiments3(filename='promos_settings.json'),
                pytest.mark.experiments3(filename='promos_settings_tabs.json'),
            ],
            id='all',
        ),
    ],
)
async def test_promo_settings_tabs(
        taxi_eats_restapp_promo, partner_id, available, mock_partners_info_200,
):
    """
    Тест проверяет, что ходим в конфиги и достаем табы для настроек,
    проверяем, что они прокидываются в ответ ручки.
    """

    response = await taxi_eats_restapp_promo.get(
        '/4.0/restapp-front/promo/v1/promo/settings',
        headers={'X-YaEda-PartnerId': str(partner_id)},
    )

    assert mock_partners_info_200.times_called == 1
    assert response.status_code == 200
    assert response.json()['tabs'] == available
