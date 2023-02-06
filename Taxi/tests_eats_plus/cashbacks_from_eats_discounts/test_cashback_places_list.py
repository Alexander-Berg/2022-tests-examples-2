# pylint: disable=too-many-lines

import pytest


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.eats_discounts_match(
    [
        {
            'subquery_id': '1',
            'place_cashback': {
                'menu_value': {
                    'value_type': 'fraction',
                    'value': '21.0',
                    'maximum_discount': '1234',
                },
            },
        },
        {
            'subquery_id': '2',
            'place_cashback': {
                'menu_value': {
                    'value_type': 'fraction',
                    'value': '36.0',
                    'maximum_discount': '1234',
                },
            },
        },
        {
            'subquery_id': '3',
            'place_cashback': {
                'menu_value': {
                    'value_type': 'fraction',
                    'value': '44.0',
                    'maximum_discount': '1234',
                },
            },
        },
    ],
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 1,
            'revision_id': 1,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'location': {'geo_point': [47.525496503606774, 55.75568074159372]},
            'country': {
                'id': 1,
                'code': 'abc',
                'name': 'USSR',
                'currency': {'sign': '$', 'code': 'RUB'},
            },
            'region': {
                'id': 123,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
            'categories': [{'id': 1, 'name': 'some_name'}],
            'business': 'store',
            'type': 'marketplace',
        },
        {
            'id': 2,
            'revision_id': 5,
            'updated_at': '2020-11-26T10:00:00.000000Z',
            'location': {'geo_point': [55.798910, 49.105788]},
            'country': {
                'id': 1,
                'code': 'abc',
                'name': 'USSR',
                'currency': {'sign': '$', 'code': 'RUB'},
            },
            'region': {
                'id': 123,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
            'categories': [{'id': 1, 'name': 'some_name'}],
            'business': 'store',
            'type': 'marketplace',
        },
        {
            'id': 3,
            'revision_id': 8,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'location': {'geo_point': [37.567595, 55.743064]},
            'country': {
                'id': 1,
                'code': 'abc',
                'name': 'USSR',
                'currency': {'sign': '$', 'code': 'RUB'},
            },
            'region': {
                'id': 123,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
            'categories': [{'id': 1, 'name': 'some_name'}],
            'business': 'store',
            'type': 'marketplace',
        },
    ],
)
async def test_cashback_places_list_eats_discounts_set_cashback(
        taxi_eats_plus, passport_blackbox, eats_order_stats, plus_wallet,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 123321})
    eats_order_stats(has_orders=True)
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/presentation/cashback/places-list',
        json={'yandex_uid': '34567257', 'place_ids': [1, 2, 3]},
    )

    assert response.status_code == 200
    assert response.json() == {
        'cashback': [
            {'place_id': 1, 'cashback': 21},
            {'place_id': 2, 'cashback': 36},
            {'place_id': 3, 'cashback': 44},
        ],
    }


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.eats_discounts_match(
    [
        {
            'subquery_id': '1_plus_happy_hours',
            'place_cashback': {
                'menu_value': {'value_type': 'fraction', 'value': '21.0'},
            },
        },
    ],
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 1,
            'revision_id': 1,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'location': {'geo_point': [47.525496503606774, 55.75568074159372]},
            'country': {
                'id': 1,
                'code': 'abc',
                'name': 'USSR',
                'currency': {'sign': '$', 'code': 'RUB'},
            },
            'region': {
                'id': 123,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
            'categories': [{'id': 1, 'name': 'some_name'}],
            'business': 'store',
            'type': 'marketplace',
        },
    ],
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_promo_for_catalog_restlist.json',
)
@pytest.mark.parametrize(
    ['yandex_uid', 'enabled'],
    [
        pytest.param(
            '34567257',
            False,
            id='to match default value where promos are disabled',
        ),
        pytest.param(
            '34567258', True, id='to match clause where promos are enabled',
        ),
    ],
)
async def test_cashback_places_list_get_info_action(
        taxi_eats_plus,
        passport_blackbox,
        eats_order_stats,
        plus_wallet,
        yandex_uid,
        enabled,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 123321})
    eats_order_stats(has_orders=True)
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/presentation/cashback/places-list',
        json={'yandex_uid': yandex_uid, 'place_ids': [1]},
    )

    expected_response = {'cashback': [{'place_id': 1, 'cashback': 21}]}
    if enabled:
        expected_response['cashback'][0].update(
            {
                'plus_promo_info_actions': [
                    {
                        'accent_color': [
                            {'theme': 'dark', 'value': '#CE7E00'},
                            {'theme': 'light', 'value': '#CE7E00'},
                        ],
                        'description': (
                            'Повышенный кешбек 21% ' 'в счастливые часы'
                        ),
                        'extended': {
                            'button': {
                                'title': (
                                    'Ну тут в общем название кнопки '
                                    'на шторке, '
                                    'а скидку даем 21%'
                                ),
                                'url': 'invalid.invalid',
                            },
                            'content': (
                                'Ну тут в общем текст шторки, '
                                'а скидку даем 21%'
                            ),
                            'title': (
                                'Ну тут в общем заголовок шторки, '
                                'а скидку даем 21%'
                            ),
                        },
                        'icon_url': 'icon_url',
                        'title': (
                            'Повышенный кешбек 21% ' 'в счастливые часы'
                        ),
                    },
                ],
            },
        )

    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 1,
            'revision_id': 1,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'location': {'geo_point': [47.525496503606774, 55.75568074159372]},
            'country': {
                'id': 1,
                'code': 'abc',
                'name': 'USSR',
                'currency': {'sign': '$', 'code': 'RUB'},
            },
            'region': {
                'id': 123,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
            'categories': [{'id': 1, 'name': 'some_name'}],
            'business': 'store',
            'type': 'marketplace',
        },
    ],
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_promo_for_catalog_restlist.json',
)
async def test_cashback_places_list_base_match_does_not_overlap_plus(
        taxi_eats_plus,
        passport_blackbox,
        eats_order_stats,
        plus_wallet,
        mockserver,
):
    """
    Это тест на баг в обработке ответа eats-discounts,
    когда сматчившийся базовый кешбек перекрывает акцию Плюса,
    и вызывает невозврат promo в ответе ручки places-list.
    Ожидаемое поведение: promo всё равно возвращается,
    даже если что-то перекрывало акцию.
    """

    @mockserver.json_handler('/eats-discounts/v2/match-discounts')
    def _mock_eats_discounts_match(json_request):
        return {
            'match_results': [
                {
                    'discounts': [
                        {
                            'discount_id': '1085',
                            'cashback_value': {
                                'menu_value': {
                                    'value': '34',
                                    'value_type': 'fraction',
                                },
                            },
                            'discount_meta': {'name': 'base'},
                        },
                    ],
                    'discount_id': '1085',
                    'hierarchy_name': 'place_cashback',
                },
                {
                    'discounts': [
                        {
                            'discount_id': '389',
                            'cashback_value': {
                                'menu_value': {
                                    'value': '23',
                                    'value_type': 'fraction',
                                },
                            },
                            'discount_meta': {'name': 'plus_happy_hours'},
                        },
                    ],
                    'discount_id': '389',
                    'hierarchy_name': 'yandex_cashback',
                    'subquery_results': [{'id': '1', 'discount_id': '389'}],
                },
            ],
        }

    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 123321})
    eats_order_stats(has_orders=True)
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/presentation/cashback/places-list',
        json={'yandex_uid': '34567258', 'place_ids': [1]},
    )

    cashback = response.json()['cashback'][0]['cashback']

    assert response.status_code == 200
    assert response.json() == {
        'cashback': [
            {
                'place_id': 1,
                'cashback': cashback,
                'plus_promo_info_actions': [
                    {
                        'accent_color': [
                            {'theme': 'dark', 'value': '#CE7E00'},
                            {'theme': 'light', 'value': '#CE7E00'},
                        ],
                        'description': (
                            'Повышенный кешбек 23% ' 'в счастливые часы'
                        ),
                        'extended': {
                            'button': {
                                'title': (
                                    'Ну тут в общем название кнопки '
                                    'на шторке, '
                                    'а скидку даем 23%'
                                ),
                                'url': 'invalid.invalid',
                            },
                            'content': (
                                'Ну тут в общем текст шторки, '
                                'а скидку даем 23%'
                            ),
                            'title': (
                                'Ну тут в общем заголовок шторки, '
                                'а скидку даем 23%'
                            ),
                        },
                        'icon_url': 'icon_url',
                        'title': (
                            'Повышенный кешбек 23% ' 'в счастливые часы'
                        ),
                    },
                ],
            },
        ],
    }


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 1,
            'revision_id': 1,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'location': {'geo_point': [47.525496503606774, 55.75568074159372]},
            'country': {
                'id': 1,
                'code': 'abc',
                'name': 'USSR',
                'currency': {'sign': '$', 'code': 'RUB'},
            },
            'region': {
                'id': 123,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
            'categories': [{'id': 1, 'name': 'some_name'}],
            'business': 'store',
            'type': 'marketplace',
        },
    ],
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_promo_for_catalog_restlist.json',
)
async def test_cashback_places_list_another_discount_does_not_overlap_plus(
        taxi_eats_plus,
        passport_blackbox,
        eats_order_stats,
        plus_wallet,
        mockserver,
):
    """
    Это тест на баг в обработке ответа eats-discounts,
    когда следующий кешбек в ответе (даже для другого плейса,
    и даже не являющийся акцией Плюса)
    перекрывает успешно сматчившуюся акцию Плюса
    и вызывает невозврат promo в ответе ручки places-list.
    Ожидаемое поведение: promo всё равно возвращается,
    даже если при парсинге акция с plus_happy_hours была не последней.
    """

    @mockserver.json_handler('/eats-discounts/v2/match-discounts')
    def _mock_eats_discounts_match(json_request):
        return {
            'match_results': [
                {
                    'discounts': [
                        {
                            'discount_id': '1',
                            'cashback_value': {
                                'menu_value': {
                                    'value': '5',
                                    'value_type': 'fraction',
                                },
                            },
                            'discount_meta': {'name': 'plus_happy_hours'},
                        },
                        {
                            'discount_id': '2',
                            'cashback_value': {
                                'menu_value': {
                                    'value': '4',
                                    'value_type': 'fraction',
                                },
                            },
                            'discount_meta': {'name': 'base'},
                        },
                    ],
                    'subquery_results': [
                        {'id': '1', 'discount_id': '1'},
                        {'id': '2', 'discount_id': '2'},
                    ],
                    'hierarchy_name': 'place_cashback',
                },
            ],
        }

    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 123321})
    eats_order_stats(has_orders=True)
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/presentation/cashback/places-list',
        json={'yandex_uid': '34567258', 'place_ids': [1]},
    )

    cashback = response.json()['cashback'][0]['cashback']

    assert response.status_code == 200
    assert response.json() == {
        'cashback': [
            {
                'place_id': 1,
                'cashback': cashback,
                'plus_promo_info_actions': [
                    {
                        'accent_color': [
                            {'theme': 'dark', 'value': '#CE7E00'},
                            {'theme': 'light', 'value': '#CE7E00'},
                        ],
                        'description': (
                            'Повышенный кешбек 5% ' 'в счастливые часы'
                        ),
                        'extended': {
                            'button': {
                                'title': (
                                    'Ну тут в общем название кнопки '
                                    'на шторке, '
                                    'а скидку даем 5%'
                                ),
                                'url': 'invalid.invalid',
                            },
                            'content': (
                                'Ну тут в общем текст шторки, '
                                'а скидку даем 5%'
                            ),
                            'title': (
                                'Ну тут в общем заголовок шторки, '
                                'а скидку даем 5%'
                            ),
                        },
                        'icon_url': 'icon_url',
                        'title': ('Повышенный кешбек 5% ' 'в счастливые часы'),
                    },
                ],
            },
        ],
    }


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_promo_for_catalog_restlist.json',
)
@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 1,
            'revision_id': 1,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'location': {'geo_point': [47.525496503606774, 55.75568074159372]},
            'country': {
                'id': 1,
                'code': 'abc',
                'name': 'USSR',
                'currency': {'sign': '$', 'code': 'RUB'},
            },
            'region': {
                'id': 123,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
            'categories': [{'id': 1, 'name': 'some_name'}],
            'business': 'store',
            'type': 'marketplace',
        },
        {
            'id': 2,
            'revision_id': 5,
            'updated_at': '2020-11-26T10:00:00.000000Z',
            'location': {'geo_point': [55.798910, 49.105788]},
            'country': {
                'id': 1,
                'code': 'abc',
                'name': 'USSR',
                'currency': {'sign': '$', 'code': 'RUB'},
            },
            'region': {
                'id': 123,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
            'categories': [{'id': 1, 'name': 'some_name'}],
            'business': 'store',
            'type': 'marketplace',
        },
    ],
)
async def test_cashback_places_list_another_place_does_not_affect_ours(
        taxi_eats_plus,
        passport_blackbox,
        eats_order_stats,
        plus_wallet,
        mockserver,
):
    """
    Это тест на баг в обработке ответа eats-discounts,
    когда при матчинге акции Плюса в places-list, не только
    сматчивший плейс получает InfoAction, но и другие.
    Ожидаемое поведение: InfoAction возвращается только для плейсов,
    в subqueries которых eats-discounts вернул акцию Плюса.
    """

    @mockserver.json_handler('/eats-discounts/v2/match-discounts')
    def _mock_eats_discounts_match(json_request):
        return {
            'match_results': [
                {
                    'discounts': [
                        {
                            'discount_id': '1',
                            'cashback_value': {
                                'menu_value': {
                                    'value': '5',
                                    'value_type': 'fraction',
                                },
                            },
                            'discount_meta': {'name': 'plus_happy_hours'},
                        },
                        {
                            'discount_id': '2',
                            'cashback_value': {
                                'menu_value': {
                                    'value': '4',
                                    'value_type': 'fraction',
                                },
                            },
                            'discount_meta': {'name': 'base'},
                        },
                    ],
                    'subquery_results': [
                        {'id': '1', 'discount_id': '1'},
                        {'id': '2', 'discount_id': '2'},
                    ],
                    'hierarchy_name': 'place_cashback',
                },
            ],
        }

    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 123321})
    eats_order_stats(has_orders=True)
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/presentation/cashback/places-list',
        json={'yandex_uid': '34567258', 'place_ids': [1, 2]},
    )

    assert response.status_code == 200
    assert response.json() == {
        'cashback': [
            {
                'cashback': 5.0,
                'place_id': 1,
                'plus_promo_info_actions': [
                    {
                        'accent_color': [
                            {'theme': 'dark', 'value': '#CE7E00'},
                            {'theme': 'light', 'value': '#CE7E00'},
                        ],
                        'description': (
                            'Повышенный кешбек 5% ' 'в счастливые часы'
                        ),
                        'extended': {
                            'button': {
                                'title': (
                                    'Ну тут в общем название кнопки '
                                    'на шторке, '
                                    'а скидку даем 5%'
                                ),
                                'url': 'invalid.invalid',
                            },
                            'content': (
                                'Ну тут в общем текст шторки, '
                                'а скидку даем 5%'
                            ),
                            'title': (
                                'Ну тут в общем заголовок шторки, '
                                'а скидку даем 5%'
                            ),
                        },
                        'icon_url': 'icon_url',
                        'title': ('Повышенный кешбек 5% ' 'в счастливые часы'),
                    },
                ],
            },
            {'cashback': 4.0, 'place_id': 2},
        ],
    }


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_promo_for_catalog_restlist.json',
)
@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 1,
            'revision_id': 1,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'location': {'geo_point': [47.525496503606774, 55.75568074159372]},
            'country': {
                'id': 1,
                'code': 'abc',
                'name': 'USSR',
                'currency': {'sign': '$', 'code': 'RUB'},
            },
            'region': {
                'id': 123,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
            'categories': [{'id': 1, 'name': 'some_name'}],
            'business': 'store',
            'type': 'marketplace',
        },
        {
            'id': 2,
            'revision_id': 5,
            'updated_at': '2020-11-26T10:00:00.000000Z',
            'location': {'geo_point': [55.798910, 49.105788]},
            'country': {
                'id': 1,
                'code': 'abc',
                'name': 'USSR',
                'currency': {'sign': '$', 'code': 'RUB'},
            },
            'region': {
                'id': 123,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
            'categories': [{'id': 1, 'name': 'some_name'}],
            'business': 'store',
            'type': 'marketplace',
        },
    ],
)
async def test_cashback_places_list_plus_promo_merging_compound_discount(
        taxi_eats_plus,
        passport_blackbox,
        eats_order_stats,
        plus_wallet,
        mockserver,
):
    """
    Это тест на схлопывание НА РЕСТЛИСТЕ акции Плюса с софинансированием
    (фактически две акции в разных иерархиях - плейсовой
    и яндексовой)
    в один InfoAction.

    Тест проверяет, что если для одного плейса в двух кешбечных иерархиях есть
    скидка с одинаковым типом (happy_hours / first_orders),
    НА РЕСТЛИСТЕ они мержатся в один InfoAction.

    note: поведение такое, потому что сейчас две акции с одинаковым типом
    в разных кешбечных иерархиях - это фактически одна акция
    с софинансированием (часть платит Яндекс, а часть партнер,
    н-р 3% Яндекс и 3% партнер - акция кешбек 6%).
    Но теоретически когда-нибудь кто-то может
    начать создавать разные акции: одна яндексовая,
    вторая партнерская, и друг к другу они не имеют отношения.
    Тогда придется какие-то акции (которые на самом деле являются одной
    с софинансированием) мержить, а какие-то нет.
    Но сейчас этот случай не учитываем и на уровне eats-discounts
    отличить такие акции нельзя.
    """

    @mockserver.json_handler('/eats-discounts/v2/match-discounts')
    def _mock_eats_discounts_match(json_request):
        return {
            'match_results': [
                {
                    'discounts': [
                        {
                            'discount_id': '1',
                            'cashback_value': {
                                'menu_value': {
                                    'value': '5',
                                    'value_type': 'fraction',
                                },
                            },
                            'discount_meta': {'name': 'plus_happy_hours'},
                        },
                        {
                            'discount_id': '2',
                            'cashback_value': {
                                'menu_value': {
                                    'value': '4',
                                    'value_type': 'fraction',
                                },
                            },
                            'discount_meta': {'name': 'base'},
                        },
                    ],
                    'subquery_results': [
                        {'id': '1', 'discount_id': '1'},
                        {'id': '2', 'discount_id': '2'},
                    ],
                    'hierarchy_name': 'place_cashback',
                },
                {
                    'discounts': [
                        {
                            'discount_id': '1',
                            'cashback_value': {
                                'menu_value': {
                                    'value': '5',
                                    'value_type': 'fraction',
                                },
                            },
                            'discount_meta': {'name': 'plus_happy_hours'},
                        },
                    ],
                    'subquery_results': [{'id': '1', 'discount_id': '1'}],
                    'hierarchy_name': 'yandex_cashback',
                },
            ],
        }

    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 123321})
    eats_order_stats(has_orders=True)
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/presentation/cashback/places-list',
        json={'yandex_uid': '34567258', 'place_ids': [1, 2]},
    )

    assert response.status_code == 200
    assert response.json() == {
        'cashback': [
            {
                'cashback': 10.0,
                'place_id': 1,
                'plus_promo_info_actions': [
                    {
                        'accent_color': [
                            {'theme': 'dark', 'value': '#CE7E00'},
                            {'theme': 'light', 'value': '#CE7E00'},
                        ],
                        'description': (
                            # 10, потому что 5 в одной иерархии и 5 в другой
                            'Повышенный кешбек 10% '
                            'в счастливые часы'
                        ),
                        'extended': {
                            'button': {
                                'title': (
                                    'Ну тут в общем название кнопки '
                                    'на шторке, '
                                    'а скидку даем 10%'
                                ),
                                'url': 'invalid.invalid',
                            },
                            'content': (
                                'Ну тут в общем текст шторки, '
                                'а скидку даем 10%'
                            ),
                            'title': (
                                'Ну тут в общем заголовок шторки, '
                                'а скидку даем 10%'
                            ),
                        },
                        'icon_url': 'icon_url',
                        'title': (
                            'Повышенный кешбек 10% ' 'в счастливые часы'
                        ),
                    },
                ],
            },
            {'cashback': 4.0, 'place_id': 2},
        ],
    }


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.eats_discounts_match(
    [
        {
            'subquery_id': '1',
            'place_cashback': {
                'menu_value': {
                    'value_type': 'fraction',
                    'value': '21.0',
                    'maximum_discount': '1234',
                },
            },
        },
        {
            'subquery_id': '3',
            'place_cashback': {
                'menu_value': {
                    'value_type': 'fraction',
                    'value': '36.0',
                    'maximum_discount': '1234',
                },
            },
        },
        {
            'subquery_id': '5',
            'place_cashback': {
                'menu_value': {
                    'value_type': 'fraction',
                    'value': '44.0',
                    'maximum_discount': '1234',
                },
            },
        },
    ],
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 1,
            'revision_id': 1,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'location': {'geo_point': [47.525496503606774, 55.75568074159372]},
            'country': {
                'id': 1,
                'code': 'abc',
                'name': 'USSR',
                'currency': {'sign': '$', 'code': 'RUB'},
            },
            'region': {
                'id': 123,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
            'categories': [{'id': 1, 'name': 'some_name'}],
            'business': 'store',
            'type': 'marketplace',
        },
        {
            'id': 2,
            'revision_id': 5,
            'updated_at': '2020-11-26T10:00:00.000000Z',
            'location': {'geo_point': [55.798910, 49.105788]},
            'country': {
                'id': 1,
                'code': 'abc',
                'name': 'USSR',
                'currency': {'sign': '$', 'code': 'RUB'},
            },
            'region': {
                'id': 123,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
            'categories': [{'id': 1, 'name': 'some_name'}],
            'business': 'store',
            'type': 'marketplace',
        },
        {
            'id': 3,
            'revision_id': 8,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'location': {'geo_point': [37.567595, 55.743064]},
            'country': {
                'id': 1,
                'code': 'abc',
                'name': 'USSR',
                'currency': {'sign': '$', 'code': 'RUB'},
            },
            'region': {
                'id': 123,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
            'categories': [{'id': 1, 'name': 'some_name'}],
            'business': 'store',
            'type': 'marketplace',
        },
        {
            'id': 4,
            'revision_id': 8,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'location': {'geo_point': [37.567595, 55.743064]},
            'country': {
                'id': 1,
                'code': 'abc',
                'name': 'USSR',
                'currency': {'sign': '$', 'code': 'RUB'},
            },
            'region': {
                'id': 123,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
            'categories': [{'id': 1, 'name': 'some_name'}],
            'business': 'store',
            'type': 'marketplace',
        },
        {
            'id': 5,
            'revision_id': 8,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'location': {'geo_point': [37.567595, 55.743064]},
            'country': {
                'id': 1,
                'code': 'abc',
                'name': 'USSR',
                'currency': {'sign': '$', 'code': 'RUB'},
            },
            'region': {
                'id': 123,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
            'categories': [{'id': 1, 'name': 'some_name'}],
            'business': 'store',
            'type': 'marketplace',
        },
    ],
)
@pytest.mark.config(
    EATS_PLUS_EATS_DISCOUNTS_REQUEST_SETTINGS={'max_places_in_request': 2},
)
async def test_cashback_places_list_eats_discounts_async_batch(
        taxi_eats_plus,
        passport_blackbox,
        eats_order_stats,
        plus_wallet,
        eats_discounts_match,
):

    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 123321})
    eats_order_stats(has_orders=True)
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/presentation/cashback/places-list',
        json={'yandex_uid': '34567257', 'place_ids': [1, 2, 3, 4, 5]},
    )

    assert response.status_code == 200
    assert response.json() == {
        'cashback': [
            {'place_id': 1, 'cashback': 21},
            {'place_id': 3, 'cashback': 36},
            {'place_id': 5, 'cashback': 44},
        ],
    }

    assert eats_discounts_match.times_called == 3


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 1,
            'revision_id': 1,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'location': {'geo_point': [47.525496503606774, 55.75568074159372]},
            'country': {
                'id': 1,
                'code': 'abc',
                'name': 'USSR',
                'currency': {'sign': '$', 'code': 'RUB'},
            },
            'region': {'id': 123, 'geobase_ids': [1], 'time_zone': 'UTC+3'},
            'brand': {
                'id': 122333,
                'slug': 'slug',
                'name': 'name',
                'picture_scale_type': 'aspect_fit',
            },
            'categories': [{'id': 1, 'name': 'some_name'}],
            'business': 'store',
            'type': 'native',
        },
    ],
)
@pytest.mark.experiments3(filename='exp3_eats_plus_discounts_experiment.json')
@pytest.mark.parametrize(
    ['yandex_uid', 'cashback'],
    [
        pytest.param(
            '34567257',
            [{'place_id': 1, 'cashback': 5}],
            id='exp does not match -> only base cashback given',
        ),
        pytest.param(
            '34567258',
            [{'place_id': 1, 'cashback': 5}],
            id='disabled from exp -> only base cashback given',
        ),
        pytest.param(
            '34567259',
            [{'place_id': 1, 'cashback': 10}],
            id='exp matches -> additional discount given',
        ),
    ],
)
async def test_cashback_places_list_discount_using_exp(
        taxi_eats_plus,
        passport_blackbox,
        eats_order_stats,
        plus_wallet,
        mockserver,
        yandex_uid,
        cashback,
):
    # Тест проверяет, что матч эксперимента с именем,
    # которое есть в условиях скидки,
    # передается в условиях в запросе, и скидка матчится.

    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 123321})
    eats_order_stats(has_orders=True)

    @mockserver.json_handler('/eats-discounts/v2/match-discounts')
    def _match_discounts(json_request):
        experiment = json_request.json['common_conditions']['conditions'].get(
            'experiment', None,
        )

        discount_value = 5
        if experiment and experiment == ['discounts_experiment_value_enabled']:
            discount_value = 10

        response = {
            'match_results': [
                {
                    'discounts': [
                        {
                            'discount_id': '1240',
                            'cashback_value': {
                                'menu_value': {
                                    'value': f'{discount_value}.000000',
                                    'value_type': 'fraction',
                                },
                            },
                            'discount_meta': {'name': 'base'},
                        },
                    ],
                    'hierarchy_name': 'place_cashback',
                    'subquery_results': [{'id': '1', 'discount_id': '1240'}],
                },
                {'discounts': [], 'hierarchy_name': 'yandex_cashback'},
            ],
        }

        return response

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/presentation/cashback/places-list',
        json={'yandex_uid': yandex_uid, 'place_ids': [1]},
    )

    assert response.status_code == 200
    assert response.json() == {'cashback': cashback}
