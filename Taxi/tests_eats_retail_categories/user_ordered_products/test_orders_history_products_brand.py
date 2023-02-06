import datetime

import pytest

from tests_eats_retail_categories import utils


def make_config(days=None, orders=None, max_brand_products=None):
    return {
        'ordershistory_days': days,
        'ordershistory_orders': orders,
        'max_brand_products_in_db': max_brand_products,
    }


async def test_orders_history_products_brand_unknown_brand(
        taxi_eats_retail_categories,
):
    """
    Проверяется ответ 404 если в кэше нет запрошенного бренда
    """
    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_BRAND,
        json={'brand_id': utils.BRAND_ID},
        headers=utils.HEADERS,
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'brand_not_found',
        'message': 'Brand not found in cache',
    }


@pytest.mark.parametrize('headers', [{}, {'X-Eats-User': 'user_id='}])
async def test_orders_history_products_brand_no_eater_id(
        taxi_eats_retail_categories, headers,
):
    """
    Проверяется, что ручку нельзя вызвать без авторизации пользователя
    """
    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_BRAND,
        json={'brand_id': utils.BRAND_ID},
        headers=headers,
    )
    assert response.status_code == 401
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}


async def test_orders_history_products_brand_no_products(
        taxi_eats_retail_categories, pg_add_brand, pg_add_user_orders_updates,
):
    """
    Проверяется, что если в таблице user_orders есть запись о наличии данных
    по пользователю, но товаров он не заказывал, то вернется пустой ответ
    """
    pg_add_brand()
    pg_add_user_orders_updates()
    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_BRAND,
        json={'brand_id': utils.BRAND_ID},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'products': []}


@pytest.mark.parametrize('headers', [utils.HEADERS, utils.HEADERS_PARTNER])
async def test_orders_history_products_brand_with_products(
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_user_orders_updates,
        pg_add_user_ordered_product,
        headers,
):
    """
    Проверяется, что если в БД есть данные о товарах из истории заказов,
    то эти товары будут в ответе
    """
    pg_add_brand()
    pg_add_user_orders_updates()
    pg_add_user_ordered_product(public_id=utils.PUBLIC_IDS[0])
    pg_add_user_ordered_product(public_id=utils.PUBLIC_IDS[1], orders_count=2)
    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_BRAND,
        json={'brand_id': utils.BRAND_ID},
        headers=headers,
    )
    assert response.status_code == 200
    assert utils.sort_by_public_id(response.json()['products']) == [
        {'public_id': utils.PUBLIC_IDS[0], 'orders_count': 1},
        {'public_id': utils.PUBLIC_IDS[1], 'orders_count': 2},
    ]


async def test_orders_history_products_brand_ordershistory_no_products(
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
        pg_select_user_orders_updates,
        mock_ordershistory_context,
):
    """
    Проверяется, что если ordershistory вернула 0 товаров, то ответ будет
    пустой, а в таблице user_orders появится запись с eater_id
    """
    pg_add_brand()
    pg_add_place()

    users_in_db = pg_select_user_orders_updates()
    assert users_in_db == []

    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_BRAND,
        json={'brand_id': utils.BRAND_ID},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200

    assert mock_ordershistory_context.handler.times_called == 1

    assert response.json() == {'products': []}
    users_in_db = pg_select_user_orders_updates()
    assert len(users_in_db) == 1
    assert users_in_db[0]['eater_id'] == utils.EATER_ID


async def test_orders_history_products_brand_ordershistory_unkown_place(
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
        pg_select_user_orders_updates,
        mock_ordershistory_context,
        mock_public_id_by_origin_id_context,
):
    """
    Проверяется, что если ordershistory вернула заказ из неизвестного
    магазина, то запроса в eats-products не будет, в базу ничего записано
    не будет, товаров не вернется
    """
    pg_add_brand()
    pg_add_place()

    mock_ordershistory_context.add_product(utils.ORIGIN_IDS[0], place_id=123)

    users_in_db = pg_select_user_orders_updates()
    assert users_in_db == []

    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_BRAND,
        json={'brand_id': utils.BRAND_ID},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200

    assert mock_ordershistory_context.handler.times_called == 1
    assert mock_public_id_by_origin_id_context.handler.times_called == 0

    assert response.json() == {'products': []}
    users_in_db = pg_select_user_orders_updates()
    assert len(users_in_db) == 1
    assert users_in_db[0]['eater_id'] == utils.EATER_ID


async def test_orders_history_products_brand_ordershistory_with_products(
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
        pg_select_user_brand_products,
        get_cursor,
        mock_ordershistory_context,
        mock_nomenclature_static_info_context,
        mock_public_id_by_origin_id_context,
):
    """
    Проверяется, что если ordershistory вернула товары, то они будут
    возвращены в ответе и записаны в БД
    """
    other_brand = 2
    other_place = 2
    pg_add_brand(utils.BRAND_ID)
    pg_add_place()
    pg_add_brand(other_brand)
    pg_add_place(
        other_place, place_slug=str(other_place), brand_id=other_brand,
    )

    mock_public_id_by_origin_id_context.add_product(
        utils.ORIGIN_IDS[0], utils.PUBLIC_IDS[0],
    )
    mock_public_id_by_origin_id_context.add_product(
        utils.ORIGIN_IDS[2], utils.PUBLIC_IDS[2],
    )
    mock_public_id_by_origin_id_context.add_product(
        utils.ORIGIN_IDS[3], utils.PUBLIC_IDS[3], place_id=other_place,
    )

    # Товар в 2 заказах
    mock_ordershistory_context.add_product(utils.ORIGIN_IDS[0])
    mock_ordershistory_context.add_product(utils.ORIGIN_IDS[0])
    # Товар без маппинга id
    mock_ordershistory_context.add_product(utils.ORIGIN_IDS[1])
    # Товар в 1 заказе
    mock_ordershistory_context.add_product(utils.ORIGIN_IDS[2])
    # Товар из магазина другого бренда
    mock_ordershistory_context.add_product(
        utils.ORIGIN_IDS[3], place_id=other_place,
    )

    products_in_db = pg_select_user_brand_products()
    assert products_in_db == []

    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_BRAND,
        json={'brand_id': utils.BRAND_ID},
        headers=utils.HEADERS,
    )
    assert mock_ordershistory_context.handler.times_called == 1
    assert mock_public_id_by_origin_id_context.handler.times_called == 2
    assert response.status_code == 200
    assert utils.sort_by_public_id(response.json()['products']) == [
        {'public_id': utils.PUBLIC_IDS[0], 'orders_count': 2},
        {'public_id': utils.PUBLIC_IDS[2], 'orders_count': 1},
    ]
    products_in_db = pg_select_user_brand_products()
    assert len(products_in_db) == 3
    assert products_in_db == [
        {
            'eater_id': utils.EATER_ID,
            'public_id': utils.PUBLIC_IDS[0],
            'brand_id': utils.BRAND_ID,
            'orders_count': 2,
        },
        {
            'eater_id': utils.EATER_ID,
            'public_id': utils.PUBLIC_IDS[2],
            'brand_id': utils.BRAND_ID,
            'orders_count': 1,
        },
        {
            'eater_id': utils.EATER_ID,
            'public_id': utils.PUBLIC_IDS[3],
            'brand_id': other_brand,
            'orders_count': 1,
        },
    ]


async def test_orders_history_products_brand_ordershistory_old_products(
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
        pg_select_user_brand_products,
        pg_add_user_ordered_product,
        mock_ordershistory_context,
        mock_nomenclature_static_info_context,
        mock_public_id_by_origin_id_context,
):
    """
    Проверяется, что если в БД были товары из старых заказов, то
    при обновлении они останутся неизменными и ответе не вернутся
    """
    now = datetime.datetime.now().timestamp()
    pg_add_brand()
    pg_add_place()

    mock_public_id_by_origin_id_context.add_product(
        utils.ORIGIN_IDS[0], utils.PUBLIC_IDS[0],
    )
    mock_public_id_by_origin_id_context.add_product(
        utils.ORIGIN_IDS[1], utils.PUBLIC_IDS[1],
    )

    mock_ordershistory_context.add_product(utils.ORIGIN_IDS[1])

    # Старый товар в БД (неординарная ситуация)
    pg_add_user_ordered_product(public_id=utils.PUBLIC_IDS[0])
    old_products_in_db = pg_select_user_brand_products(with_updated_at=True)
    assert len(old_products_in_db) == 1

    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_BRAND,
        json={'brand_id': utils.BRAND_ID},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200
    assert utils.sort_by_public_id(response.json()['products']) == [
        {'public_id': utils.PUBLIC_IDS[1], 'orders_count': 1},
    ]
    products_in_db = pg_select_user_brand_products(with_updated_at=True)

    assert len(products_in_db) == 2
    assert products_in_db[0] == old_products_in_db[0]
    assert products_in_db[1]['public_id'] == utils.PUBLIC_IDS[1]
    assert products_in_db[1]['updated_at'].timestamp() >= now


@pytest.mark.parametrize('status_code', [400, 429, 500])
async def test_orders_history_products_brand_ordershistory_bad_response(
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
        mock_ordershistory_context,
        status_code,
):
    """
    Проверяются плохие ответы от eats-ordershistory
    """
    pg_add_brand()
    pg_add_place()

    mock_ordershistory_context.set_status(status_code)

    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_BRAND,
        json={'brand_id': utils.BRAND_ID},
        headers=utils.HEADERS,
    )
    assert response.status_code == 500

    assert mock_ordershistory_context.handler.times_called == 1


@pytest.mark.parametrize('status_code', [400, 404, 429, 500])
async def test_orders_history_products_brand_mapping_bad_response(
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
        mock_ordershistory_context,
        mock_public_id_by_origin_id_context,
        status_code,
):
    """
    Проверяются плохие ответы от eats-products
    """
    pg_add_brand()
    pg_add_place()

    mock_ordershistory_context.add_product(utils.ORIGIN_IDS[0])
    mock_public_id_by_origin_id_context.set_status(status_code)

    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_BRAND,
        json={'brand_id': utils.BRAND_ID},
        headers=utils.HEADERS,
    )
    if status_code != 404:
        assert response.status_code == 500
    else:
        assert response.status_code == 200
        assert response.json() == {'products': []}

    assert mock_ordershistory_context.handler.times_called == 1


@pytest.mark.parametrize('status_code', [400, 404, 429, 500])
async def test_orders_history_products_brand_static_info_bad_response(
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
        mock_ordershistory_context,
        mock_public_id_by_origin_id_context,
        mock_nomenclature_static_info_context,
        status_code,
):
    """
    Проверяются плохие ответы от eats-nomenclature
    """
    pg_add_brand()
    pg_add_place()

    mock_ordershistory_context.add_product(utils.ORIGIN_IDS[0])
    mock_public_id_by_origin_id_context.add_product(
        utils.ORIGIN_IDS[0], utils.PUBLIC_IDS[0],
    )
    mock_nomenclature_static_info_context.set_status(status_code)

    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_BRAND,
        json={'brand_id': utils.BRAND_ID},
        headers=utils.HEADERS,
    )
    if status_code == 404:
        assert response.status_code == status_code
    else:
        assert response.status_code == 500

    assert mock_ordershistory_context.handler.times_called == 1


@pytest.mark.parametrize(
    'ordershistory_times_called',
    [
        pytest.param(1, id='no config'),
        pytest.param(
            1,
            id='only by days',
            marks=pytest.mark.config(
                EATS_RETAIL_CATEGORIES_ORDERS_HISTORY_SETTINGS=make_config(
                    days=1,
                ),
            ),
        ),
        pytest.param(
            1,
            id='only by orders',
            marks=pytest.mark.config(
                EATS_RETAIL_CATEGORIES_ORDERS_HISTORY_SETTINGS=make_config(
                    orders=1,
                ),
            ),
        ),
        pytest.param(
            2,
            id='by both',
            marks=pytest.mark.config(
                EATS_RETAIL_CATEGORIES_ORDERS_HISTORY_SETTINGS=make_config(
                    days=1, orders=1,
                ),
            ),
        ),
    ],
)
async def test_orders_history_products_brand_ordershistory_request_settings(
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
        pg_select_user_orders_updates,
        mock_ordershistory_context,
        mock_nomenclature_static_info_context,
        ordershistory_times_called,
):
    """
    Проверяется, у пользователя нет заказов в ритейле, то ручка истории
    заказов будет вызвана разное количество раз в зависимости от настроек:
    1. Указаны дни и кол-во заказов -> 2 раза
    2. Указаны только дни-> 1 раз
    3. Указано только кол-во заказов -> 1 раз
    3. Ничего не указано -> 1 раз
    """
    pg_add_brand()
    pg_add_place()

    users_in_db = pg_select_user_orders_updates()
    assert users_in_db == []

    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_BRAND,
        json={'brand_id': utils.BRAND_ID},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200

    assert (
        mock_ordershistory_context.handler.times_called
        == ordershistory_times_called
    )
    assert mock_nomenclature_static_info_context.handler.times_called == 0

    assert response.json() == {'products': []}
    users_in_db = pg_select_user_orders_updates()
    assert len(users_in_db) == 1
    assert users_in_db[0]['eater_id'] == utils.EATER_ID


@pytest.mark.parametrize(
    'products_in_db',
    [
        pytest.param(5, id='no config'),
        pytest.param(
            1,
            id='only 1 saved',
            marks=pytest.mark.config(
                EATS_RETAIL_CATEGORIES_ORDERS_HISTORY_SETTINGS=make_config(
                    max_brand_products=1,
                ),
            ),
        ),
        pytest.param(
            2,
            id='only 2 saved',
            marks=pytest.mark.config(
                EATS_RETAIL_CATEGORIES_ORDERS_HISTORY_SETTINGS=make_config(
                    max_brand_products=2,
                ),
            ),
        ),
        pytest.param(
            5,
            id='all 5 saved',
            marks=pytest.mark.config(
                EATS_RETAIL_CATEGORIES_ORDERS_HISTORY_SETTINGS=make_config(
                    max_brand_products=5,
                ),
            ),
        ),
        pytest.param(
            5,
            id='all 5 saved',
            marks=pytest.mark.config(
                EATS_RETAIL_CATEGORIES_ORDERS_HISTORY_SETTINGS=make_config(
                    max_brand_products=6,
                ),
            ),
        ),
    ],
)
async def test_orders_history_products_brand_max_brand_products(
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
        pg_select_user_brand_products,
        mock_ordershistory_context,
        mock_public_id_by_origin_id_context,
        mock_nomenclature_static_info_context,
        products_in_db,
):
    """
    Проверяется, что в БД будет сохранено то количество товаров,
    которое указано в конфиге
    """
    pg_add_brand()
    pg_add_place()

    for i in range(5):
        mock_ordershistory_context.add_product(utils.ORIGIN_IDS[i])
        mock_public_id_by_origin_id_context.add_product(
            utils.ORIGIN_IDS[i], utils.PUBLIC_IDS[i],
        )

    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_BRAND,
        json={'brand_id': utils.BRAND_ID},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200

    assert mock_ordershistory_context.handler.times_called == 1
    assert mock_public_id_by_origin_id_context.handler.times_called == 1
    assert mock_nomenclature_static_info_context.handler.times_called == 1

    assert len(response.json()['products']) == products_in_db
    assert len(pg_select_user_brand_products()) == products_in_db


async def test_orders_history_products_brand_count_mapping_requests(
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
        mock_ordershistory_context,
        mock_public_id_by_origin_id_context,
        mock_nomenclature_static_info_context,
):
    """
    Проверяется, кол-во запросов в eats-products за маппингом
    origin_id в public_id
    """
    second_brand = 2
    second_place = 2

    third_brand = 3
    third_place = 3

    pg_add_brand(utils.BRAND_ID)
    pg_add_place()

    pg_add_brand(second_brand)
    pg_add_brand(third_brand)

    pg_add_place(
        second_place, place_slug=str(second_place), brand_id=second_brand,
    )
    pg_add_place(
        third_place, place_slug=str(third_place), brand_id=third_brand,
    )

    mock_public_id_by_origin_id_context.add_product(
        utils.ORIGIN_IDS[0], utils.PUBLIC_IDS[0], place_id=second_place,
    )
    mock_public_id_by_origin_id_context.add_product(
        utils.ORIGIN_IDS[1], utils.PUBLIC_IDS[1],
    )

    mock_public_id_by_origin_id_context.add_product(
        utils.ORIGIN_IDS[2], utils.PUBLIC_IDS[2], place_id=third_place,
    )

    mock_ordershistory_context.add_product(
        utils.ORIGIN_IDS[0], place_id=second_place,
    )
    mock_ordershistory_context.add_product(utils.ORIGIN_IDS[1])
    mock_ordershistory_context.add_product(
        utils.ORIGIN_IDS[2], place_id=third_place,
    )

    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_BRAND,
        json={'brand_id': utils.BRAND_ID},
        headers=utils.HEADERS,
    )

    # 3 place_id. один дефолтный, 2 добавил в ручную в тесте
    assert mock_public_id_by_origin_id_context.handler.times_called == 3
    assert response.status_code == 200


async def test_orders_history_products_brand_products_from_cross_brand(
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
        pg_select_crossbrand_products,
        mock_ordershistory_context,
        mock_nomenclature_static_info_context,
        mock_public_id_by_origin_id_context,
):
    """
    Проверяется, что если в БД сохраняются кросс-брендовые товары после
    получения товаров из eats-ordershistory, даже если вызывалась ручка
    товаров в выбранном бренде
    """
    pg_add_brand()
    pg_add_place()

    assert not pg_select_crossbrand_products()

    for i in range(2):
        mock_public_id_by_origin_id_context.add_product(
            utils.ORIGIN_IDS[i], utils.PUBLIC_IDS[i],
        )
        mock_ordershistory_context.add_product(utils.ORIGIN_IDS[i])
        mock_nomenclature_static_info_context.add_product(
            utils.PUBLIC_IDS[i], sku_id=utils.SKU_IDS[i],
        )

    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_BRAND,
        json={'brand_id': utils.BRAND_ID},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200

    assert pg_select_crossbrand_products() == [
        {'eater_id': '123', 'orders_count': 1, 'sku_id': 'sku_id_1'},
        {'eater_id': '123', 'orders_count': 1, 'sku_id': 'sku_id_2'},
    ]
