import datetime

import pytest

from tests_eats_retail_categories import utils


def make_config(days=None, orders=None, max_products=None):
    return {
        'ordershistory_days': days,
        'ordershistory_orders': orders,
        'max_cross_brand_products_in_db': max_products,
    }


async def test_orders_history_products_cross_brand_unknown_place(
        taxi_eats_retail_categories,
):
    """
    Проверяется ответ 404 если в кэше нет запрошенного магазина
    """
    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_CROSS_BRAND,
        json={'place_id': 100500},
        headers=utils.HEADERS,
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'place_not_found',
        'message': 'Place not found in cache',
    }


@pytest.mark.parametrize('headers', [{}, {'X-Eats-User': 'user_id='}])
async def test_orders_history_products_cross_brand_no_eater_id(
        taxi_eats_retail_categories, headers,
):
    """
    Проверяется, что ручку нельзя вызвать без авторизации пользователя
    """
    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_CROSS_BRAND,
        json={'place_id': utils.PLACE_ID},
        headers=headers,
    )
    assert response.status_code == 401
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}


async def test_orders_history_products_cross_brand_no_products(
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
        pg_add_user_orders_updates,
):
    """
    Проверяется, что если в таблице user_orders есть запись о наличии данных
    по пользователю, но товаров он не заказывал, то вернется пустой ответ
    """
    pg_add_brand()
    pg_add_place()
    pg_add_user_orders_updates()
    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_CROSS_BRAND,
        json={'place_id': utils.PLACE_ID},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'products': []}


async def test_orders_history_products_cross_brand_db_products(
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
        pg_add_user_orders_updates,
        pg_add_user_crossbrand_product,
        pg_add_user_ordered_product,
        mock_public_id_by_sku_id_context,
):
    """
    Проверяется, что если в БД есть кросс-брендовые товары для пользователя,
    они будут возвращены в ответе. При этом товары, купленные в текущем бренде
    тоже будут возвращены, даже если у них нет sku_id
    """
    pg_add_brand()
    pg_add_place()
    pg_add_user_orders_updates()
    # Кросс брендовый товар, был заказан в этом бренде
    pg_add_user_crossbrand_product(sku_id=utils.SKU_IDS[0])
    pg_add_user_ordered_product(public_id=utils.PUBLIC_IDS[0])
    # Кросс брендовый товар, был заказан в другом
    pg_add_user_crossbrand_product(sku_id=utils.SKU_IDS[1], orders_count=2)
    # Товар, заказанный в этом бренде, нет sku_id
    pg_add_user_ordered_product(public_id=utils.PUBLIC_IDS[2])

    mock_public_id_by_sku_id_context.add_product(
        sku_id=utils.SKU_IDS[0], public_id=utils.PUBLIC_IDS[0],
    )
    mock_public_id_by_sku_id_context.add_product(
        sku_id=utils.SKU_IDS[1], public_id=utils.PUBLIC_IDS[3],
    )
    mock_public_id_by_sku_id_context.add_product(
        sku_id=utils.SKU_IDS[3], public_id=utils.PUBLIC_IDS[4],
    )

    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_CROSS_BRAND,
        json={'place_id': utils.PLACE_ID},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200
    products = utils.sort_by_public_id(response.json()['products'])
    assert products == [
        {
            'public_id': utils.PUBLIC_IDS[0],
            'sku_id': utils.SKU_IDS[0],
            'orders_count': 1,
        },
        {'public_id': utils.PUBLIC_IDS[2], 'orders_count': 1},
        {
            'public_id': utils.PUBLIC_IDS[3],
            'sku_id': utils.SKU_IDS[1],
            'orders_count': 2,
        },
    ]


@pytest.mark.parametrize('status_code', [400, 404, 429, 500])
async def test_orders_history_products_cross_brand_bad_sku_id_responses(
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
        pg_add_user_orders_updates,
        pg_add_user_crossbrand_product,
        mock_public_id_by_sku_id_context,
        status_code,
):
    """
    Проверяется ответ ручки, в зависимости от ответа id-by-sku-id номенклатуры
    400 -> 500
    404 -> 404
    429 -> 500
    500 -> 500
    """
    pg_add_brand()
    pg_add_place()
    pg_add_user_orders_updates()
    pg_add_user_crossbrand_product(sku_id=utils.SKU_IDS[0])

    mock_public_id_by_sku_id_context.set_status(status_code)

    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_CROSS_BRAND,
        json={'place_id': utils.PLACE_ID},
        headers=utils.HEADERS,
    )
    if status_code == 404:
        assert response.status_code == status_code
    else:
        assert response.status_code == 500


@pytest.mark.parametrize('status_code', [400, 404, 429, 500])
async def test_orders_history_products_cross_brand_bad_static_info_responses(
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
        mock_public_id_by_sku_id_context,
        mock_public_id_by_origin_id_context,
        mock_nomenclature_static_info_context,
        mock_ordershistory_context,
        status_code,
):
    """
    Проверяется ответ ручки, в зависимости от ответа v1/products/info:
    400 -> 500
    404 -> 404
    429 -> 500
    500 -> 500
    """
    pg_add_brand()
    pg_add_place()

    mock_ordershistory_context.add_product(utils.ORIGIN_IDS[0])
    mock_public_id_by_origin_id_context.add_product(
        utils.ORIGIN_IDS[0], utils.PUBLIC_IDS[0],
    )
    mock_public_id_by_sku_id_context.add_product(
        sku_id=utils.SKU_IDS[0], public_id=utils.PUBLIC_IDS[0],
    )

    mock_nomenclature_static_info_context.set_status(status_code)

    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_CROSS_BRAND,
        json={'place_id': utils.PLACE_ID},
        headers=utils.HEADERS,
    )
    if status_code == 404:
        assert response.status_code == status_code
    else:
        assert response.status_code == 500


async def test_orders_history_products_cross_brand_ordershistory_unkown_place(
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
        pg_select_user_orders_updates,
        pg_select_crossbrand_products,
        mock_ordershistory_context,
):
    """
    Проверяется, что если ordershistory вернула заказ из неизвестного
    магазина, то запроса в eats-products и eats-nomenclature не будет, в базу
    ничего записано не будет, товаров не вернется
    """
    pg_add_brand()
    pg_add_place()

    mock_ordershistory_context.add_product(utils.ORIGIN_IDS[0], place_id=123)

    assert not pg_select_user_orders_updates()

    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_CROSS_BRAND,
        json={'place_id': utils.PLACE_ID},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200

    assert mock_ordershistory_context.handler.times_called == 1

    assert response.json() == {'products': []}
    users_in_db = pg_select_user_orders_updates()
    assert len(users_in_db) == 1
    assert users_in_db[0]['eater_id'] == utils.EATER_ID
    assert not pg_select_crossbrand_products()


async def test_orders_history_products_cross_brand_ordershistory_with_products(
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
        pg_select_user_orders_updates,
        pg_select_crossbrand_products,
        pg_select_user_brand_products,
        mock_ordershistory_context,
        mock_public_id_by_origin_id_context,
        mock_public_id_by_sku_id_context,
        mock_nomenclature_static_info_context,
):
    """
    Проверяется, что если ordershistory вернула товары, то они будут
    возвращены в ответе и записаны в БД
    """
    other_brand = 2
    other_place = 2
    pg_add_brand(utils.BRAND_ID)
    pg_add_place(utils.PLACE_ID, brand_id=utils.BRAND_ID)
    pg_add_brand(other_brand)
    pg_add_place(
        other_place, place_slug=str(other_place), brand_id=other_brand,
    )

    # Кросс брендовый товар из текущего магазина
    mock_ordershistory_context.add_product(utils.ORIGIN_IDS[0])
    mock_ordershistory_context.add_product(utils.ORIGIN_IDS[0])
    mock_public_id_by_origin_id_context.add_product(
        utils.ORIGIN_IDS[0], utils.PUBLIC_IDS[0],
    )
    mock_nomenclature_static_info_context.add_product(
        utils.PUBLIC_IDS[0], sku_id=utils.SKU_IDS[0],
    )
    mock_public_id_by_sku_id_context.add_product(
        sku_id=utils.SKU_IDS[0], public_id=utils.PUBLIC_IDS[0],
    )

    # Товар без маппинга
    mock_ordershistory_context.add_product(utils.ORIGIN_IDS[1])
    mock_nomenclature_static_info_context.add_product(
        utils.PUBLIC_IDS[1], sku_id=utils.SKU_IDS[1],
    )

    # Товар из магазина другого бренда
    mock_ordershistory_context.add_product(
        utils.ORIGIN_IDS[2], place_id=other_place,
    )
    mock_public_id_by_origin_id_context.add_product(
        utils.ORIGIN_IDS[2], utils.PUBLIC_IDS[2], place_id=other_place,
    )
    mock_nomenclature_static_info_context.add_product(
        utils.PUBLIC_IDS[2], sku_id=utils.SKU_IDS[2],
    )
    mock_public_id_by_sku_id_context.add_product(
        sku_id=utils.SKU_IDS[2], public_id=utils.PUBLIC_IDS[5],
    )

    # Не кросс-брендовый товар
    mock_ordershistory_context.add_product(utils.ORIGIN_IDS[3])
    mock_public_id_by_origin_id_context.add_product(
        utils.ORIGIN_IDS[3], utils.PUBLIC_IDS[3],
    )
    mock_nomenclature_static_info_context.add_product(utils.PUBLIC_IDS[3])

    # Товар из магазина другого бренда (куплен 2 раза),
    # sku_id которого совпадает с другим товаром
    mock_ordershistory_context.add_product(
        utils.ORIGIN_IDS[4], place_id=other_place,
    )
    mock_ordershistory_context.add_product(
        utils.ORIGIN_IDS[4], place_id=other_place,
    )
    mock_public_id_by_origin_id_context.add_product(
        utils.ORIGIN_IDS[4], utils.PUBLIC_IDS[4], place_id=other_place,
    )
    mock_nomenclature_static_info_context.add_product(
        utils.PUBLIC_IDS[4], sku_id=utils.SKU_IDS[2],
    )

    assert not pg_select_crossbrand_products()
    assert not pg_select_user_orders_updates()

    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_CROSS_BRAND,
        json={'place_id': utils.PLACE_ID},
        headers=utils.HEADERS,
    )

    assert mock_ordershistory_context.handler.times_called == 1
    assert mock_public_id_by_origin_id_context.handler.times_called == 2
    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_public_id_by_sku_id_context.handler.times_called == 1

    assert response.status_code == 200
    assert utils.sort_by_public_id(response.json()['products']) == [
        {
            'public_id': utils.PUBLIC_IDS[0],
            'sku_id': utils.SKU_IDS[0],
            'orders_count': 2,
        },
        {'public_id': utils.PUBLIC_IDS[3], 'orders_count': 1},
        {
            'public_id': utils.PUBLIC_IDS[5],
            'sku_id': utils.SKU_IDS[2],
            'orders_count': 3,
        },
    ]

    assert pg_select_user_orders_updates()
    assert pg_select_crossbrand_products() == [
        {
            'eater_id': utils.EATER_ID,
            'sku_id': utils.SKU_IDS[0],
            'orders_count': 2,
        },
        {
            'eater_id': utils.EATER_ID,
            'sku_id': utils.SKU_IDS[2],
            'orders_count': 3,
        },
    ]

    assert pg_select_user_brand_products() == [
        {
            'eater_id': utils.EATER_ID,
            'public_id': utils.PUBLIC_IDS[0],
            'brand_id': utils.BRAND_ID,
            'orders_count': 2,
        },
        {
            'eater_id': utils.EATER_ID,
            'public_id': utils.PUBLIC_IDS[2],
            'brand_id': other_brand,
            'orders_count': 1,
        },
        {
            'eater_id': utils.EATER_ID,
            'public_id': utils.PUBLIC_IDS[3],
            'brand_id': utils.BRAND_ID,
            'orders_count': 1,
        },
        {
            'eater_id': utils.EATER_ID,
            'public_id': utils.PUBLIC_IDS[4],
            'brand_id': other_brand,
            'orders_count': 2,
        },
    ]


async def test_orders_history_products_cross_brand_ordershistory_old_products(
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
        pg_select_crossbrand_products,
        pg_add_user_crossbrand_product,
        mock_ordershistory_context,
        mock_nomenclature_static_info_context,
        mock_public_id_by_sku_id_context,
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
    mock_nomenclature_static_info_context.add_product(
        utils.PUBLIC_IDS[1], sku_id=utils.SKU_IDS[1],
    )
    mock_public_id_by_sku_id_context.add_product(
        sku_id=utils.SKU_IDS[1], public_id=utils.PUBLIC_IDS[1],
    )
    mock_ordershistory_context.add_product(utils.ORIGIN_IDS[1])

    # Старый товар в БД (неординарная ситуация)
    pg_add_user_crossbrand_product(sku_id=utils.SKU_IDS[0])
    old_products_in_db = pg_select_crossbrand_products(with_updated_at=True)
    assert len(old_products_in_db) == 1

    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_CROSS_BRAND,
        json={'place_id': utils.PLACE_ID},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200
    assert utils.sort_by_public_id(response.json()['products']) == [
        {
            'public_id': utils.PUBLIC_IDS[1],
            'sku_id': utils.SKU_IDS[1],
            'orders_count': 1,
        },
    ]
    products_in_db = pg_select_crossbrand_products(with_updated_at=True)

    assert len(products_in_db) == 2
    assert products_in_db[0] == old_products_in_db[0]
    assert products_in_db[1]['sku_id'] == utils.SKU_IDS[1]
    assert products_in_db[1]['updated_at'].timestamp() >= now


@pytest.mark.parametrize(
    'products_in_db',
    [
        pytest.param(5, id='no config'),
        pytest.param(
            1,
            id='only 1 saved',
            marks=pytest.mark.config(
                EATS_RETAIL_CATEGORIES_ORDERS_HISTORY_SETTINGS=make_config(
                    max_products=1,
                ),
            ),
        ),
        pytest.param(
            2,
            id='only 2 saved',
            marks=pytest.mark.config(
                EATS_RETAIL_CATEGORIES_ORDERS_HISTORY_SETTINGS=make_config(
                    max_products=2,
                ),
            ),
        ),
        pytest.param(
            5,
            id='all 5 saved',
            marks=pytest.mark.config(
                EATS_RETAIL_CATEGORIES_ORDERS_HISTORY_SETTINGS=make_config(
                    max_products=5,
                ),
            ),
        ),
        pytest.param(
            5,
            id='all 5 saved',
            marks=pytest.mark.config(
                EATS_RETAIL_CATEGORIES_ORDERS_HISTORY_SETTINGS=make_config(
                    max_products=6,
                ),
            ),
        ),
    ],
)
async def test_orders_history_products_cross_brand_max_products(
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
        pg_select_crossbrand_products,
        mock_ordershistory_context,
        mock_public_id_by_origin_id_context,
        mock_nomenclature_static_info_context,
        mock_public_id_by_sku_id_context,
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
        mock_nomenclature_static_info_context.add_product(
            utils.PUBLIC_IDS[i], sku_id=utils.SKU_IDS[i],
        )
        mock_public_id_by_sku_id_context.add_product(
            sku_id=utils.SKU_IDS[i], public_id=utils.PUBLIC_IDS[i],
        )

    response = await taxi_eats_retail_categories.post(
        utils.Handlers.USER_PRODUCTS_CROSS_BRAND,
        json={'place_id': utils.PLACE_ID},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200

    assert mock_ordershistory_context.handler.times_called == 1
    assert mock_public_id_by_origin_id_context.handler.times_called == 1
    assert mock_nomenclature_static_info_context.handler.times_called == 1

    assert len(response.json()['products']) == 5
    assert len(pg_select_crossbrand_products()) == products_in_db
