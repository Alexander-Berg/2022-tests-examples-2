import pytest

DEFAULT_HEADERS = {
    'X-Request-Language': 'ru',
    'X-YaTaxi-User': 'personal_phone_id=111,eats_user_id=222',
    'X-YaTaxi-Session': 'taxi:333',
    'X-Yandex-Uid': '3456723',
    'X-YaTaxi-Bound-Uids': '',
    'X-YaTaxi-Pass-Flags': 'portal',
    'content-type': 'application/json',
}

CATALOG_STORAGE_DATA = [
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
        'type': 'native',
    },
]


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.eats_discounts_match(
    [
        {
            'subquery_id': 'offer_0',
            'place_cashback': {
                'menu_value': {'value_type': 'fraction', 'value': '21.0'},
            },
        },
    ],
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_place_cashback_presentation.json',
)
@pytest.mark.eats_catalog_storage_cache(CATALOG_STORAGE_DATA)
async def test_cashback_place_eats_discounts_set_cashback(
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
        'internal/eats-plus/v1/presentation/cashback/place',
        json={'yandex_uid': '34567257', 'place_id': 1},
    )

    assert response.status_code == 200
    assert response.json() == {'cashback': 21, 'title': 'Смотри какой кешбек'}


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.eats_discounts_match([])
@pytest.mark.eats_catalog_storage_cache(CATALOG_STORAGE_DATA)
async def test_cashback_place_eats_discounts_no_cashback(
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
        'internal/eats-plus/v1/presentation/cashback/place',
        json={'yandex_uid': '34567257', 'place_id': 1},
    )
    assert response.status_code == 404


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.eats_discounts_match(
    [
        {
            'subquery_id': 'offer_0',
            'place_cashback': {
                'menu_value': {'value_type': 'fraction', 'value': '21.0'},
            },
        },
    ],
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
            'type': 'native',
        },
    ],
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_promo_for_catalog_slug.json',
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_place_cashback_presentation.json',
)
@pytest.mark.parametrize(
    ['yandex_uid', 'expected_response'],
    [
        pytest.param(
            '34567257',
            {'cashback': 21, 'title': 'Смотри какой кешбек'},
            id='to match default value where promos are disabled',
        ),
        pytest.param(
            '34567258',
            {
                'cashback': 21,
                'title': 'Смотри какой кешбек',
                'plus_promos': [
                    {
                        'description': (
                            'Повышенный кешбек 21% в счастливые часы'
                        ),
                        'id': 0,
                        'name': '21%',
                        'promo_type': {
                            'id': 200,
                            'name': 'plus_promo',
                            'picture_uri': 'picture_uri',
                        },
                    },
                ],
            },
            id='to match clause where promos are enabled and must be shown',
        ),
    ],
)
async def test_cashback_place_returns_promo_on_plus_promo(
        taxi_eats_plus,
        taxi_config,
        passport_blackbox,
        eats_order_stats,
        plus_wallet,
        eats_discounts_match,
        yandex_uid,
        expected_response,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 123321})
    eats_order_stats(has_orders=True)
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/presentation/cashback/place',
        json={'yandex_uid': yandex_uid, 'place_id': 1},
    )

    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
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
@pytest.mark.eats_discounts_match(
    [
        {
            'subquery_id': 'offer_0',
            'place_cashback': {
                'menu_value': {'value_type': 'fraction', 'value': '21.0'},
            },
            'yandex_cashback': {
                'menu_value': {'value_type': 'fraction', 'value': '21.0'},
            },
        },
    ],
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_promo_for_catalog_slug.json',
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_place_cashback_presentation.json',
)
async def test_cashback_place_merges_compound_promo(
        taxi_eats_plus,
        taxi_config,
        passport_blackbox,
        eats_order_stats,
        plus_wallet,
        eats_discounts_match,
        mockserver,
):
    """
    Это тест на схлопывание НА СЛАГЕ акции Плюса с софинансированием
    (фактически две акции в разных иерархиях - плейсовой
    и яндексовой)
    в один Promo.

    Тест проверяет, что если для одного плейса в двух кешбечных иерархиях есть
    скидка с одинаковым типом (happy_hours / first_orders),
    НА СЛАГЕ они мержатся в один Promo.

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

    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 123321})
    eats_order_stats(has_orders=True)

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/presentation/cashback/place',
        json={'yandex_uid': '34567258', 'place_id': 1},
    )

    expected_response = {
        'cashback': 42,
        'title': 'Смотри какой кешбек',
        'plus_promos': [
            {
                'description': (
                    # 42%, потому что 21 в яндексовой иерархии
                    # и 21 в плюсовой
                    'Повышенный кешбек 42% в счастливые часы'
                ),
                'id': 0,
                'name': '42%',
                'promo_type': {
                    'id': 200,
                    'name': 'plus_promo',
                    'picture_uri': 'picture_uri',
                },
            },
        ],
    }

    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
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
@pytest.mark.eats_discounts_match(
    [
        {
            'subquery_id': 'offer_0',
            'place_cashback': {
                'menu_value': {'value_type': 'fraction', 'value': '21.0'},
            },
            'yandex_cashback': {
                'menu_value': {'value_type': 'fraction', 'value': '21.0'},
            },
        },
    ],
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_promo_for_catalog_slug.json',
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_place_cashback_presentation.json',
)
@pytest.mark.parametrize(
    'locale, promos_resp',
    [
        pytest.param(
            'ru',
            [
                {
                    'description': 'Повышенный кешбек 42% в счастливые часы',
                    'id': 0,
                    'name': '42%',
                    'promo_type': {
                        'id': 200,
                        'name': 'plus_promo',
                        'picture_uri': 'picture_uri',
                    },
                },
            ],
            id='ru locale',
        ),
        pytest.param(
            'en',
            [
                {
                    'description': 'Happy Hours cahsback 42%',
                    'id': 0,
                    'name': '42%',
                    'promo_type': {
                        'id': 200,
                        'name': 'plus_promo',
                        'picture_uri': 'picture_uri',
                    },
                },
            ],
            id='en locale',
        ),
    ],
)
async def test_cashback_place_promo_translation(
        taxi_eats_plus,
        passport_blackbox,
        eats_order_stats,
        plus_wallet,
        eats_discounts_match,
        mockserver,
        locale,
        promos_resp,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 123321})
    eats_order_stats(has_orders=True)

    headers = DEFAULT_HEADERS.copy()
    headers['X-Yandex-Uid'] = '34567258'
    headers['X-Request-Language'] = locale

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/presentation/cashback/place',
        json={'yandex_uid': '34567258', 'place_id': 1},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json().get('plus_promos') == promos_resp
