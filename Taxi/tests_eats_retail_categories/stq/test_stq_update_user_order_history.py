import pytest

from tests_eats_retail_categories import utils


def make_config(brand_products=None, cross_brand_products=None):
    return pytest.mark.config(
        EATS_RETAIL_CATEGORIES_ORDERS_HISTORY_SETTINGS={
            'max_brand_products_in_db': brand_products,
            'max_cross_brand_products_in_db': cross_brand_products,
        },
    )


async def test_stq_update_user_order_history_brand_products(
        stq_runner,
        pg_add_brand,
        pg_add_place,
        pg_select_user_orders_updates,
        pg_select_user_brand_products,
        mock_ordershistory_context,
        mock_public_id_by_origin_id_context,
        mock_nomenclature_static_info_context,
):
    """
    Проверяется, что при вызове stq в БД сохраняются товары,
    которые пользователь заказывал в магазинах разных брендов
    """
    pg_add_brand()
    pg_add_place()

    other_brand = 2
    other_place = 2
    pg_add_brand(other_brand)
    pg_add_place(
        other_place, place_slug=str(other_place), brand_id=other_brand,
    )

    assert not pg_select_user_orders_updates()
    assert not pg_select_user_brand_products()

    mock_ordershistory_context.add_product(utils.ORIGIN_IDS[0])
    mock_ordershistory_context.add_product(utils.ORIGIN_IDS[0])
    mock_public_id_by_origin_id_context.add_product(
        utils.ORIGIN_IDS[0], utils.PUBLIC_IDS[0],
    )

    mock_ordershistory_context.add_product(
        utils.ORIGIN_IDS[1], place_id=other_place,
    )
    mock_public_id_by_origin_id_context.add_product(
        utils.ORIGIN_IDS[1], utils.PUBLIC_IDS[1], place_id=other_place,
    )

    await stq_runner.eats_retail_categories_update_user_order_history.call(
        task_id=f'{utils.EATER_ID}',
        kwargs={'eater_id': utils.EATER_ID},
        expect_fail=False,
    )
    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_public_id_by_origin_id_context.handler.times_called == 2
    assert mock_ordershistory_context.handler.times_called == 1
    user_in_db = pg_select_user_orders_updates()
    assert len(user_in_db) == 1
    assert user_in_db[0]['eater_id'] == utils.EATER_ID

    products_in_db = pg_select_user_brand_products()
    assert products_in_db == [
        {
            'eater_id': utils.EATER_ID,
            'public_id': utils.PUBLIC_IDS[0],
            'brand_id': utils.BRAND_ID,
            'orders_count': 2,
        },
        {
            'eater_id': utils.EATER_ID,
            'public_id': utils.PUBLIC_IDS[1],
            'brand_id': other_brand,
            'orders_count': 1,
        },
    ]


@pytest.mark.parametrize(
    'brand_products_size',
    [
        pytest.param(1, marks=make_config(brand_products=1)),
        pytest.param(2, marks=make_config(brand_products=2)),
        pytest.param(5, marks=make_config(brand_products=5)),
        pytest.param(5, marks=make_config(brand_products=6)),
        pytest.param(None),
    ],
)
async def test_stq_update_user_order_history_max_brand_products(
        stq_runner,
        pg_add_brand,
        pg_add_place,
        pg_select_user_orders_updates,
        pg_select_user_brand_products,
        mock_ordershistory_context,
        mock_public_id_by_origin_id_context,
        mock_nomenclature_static_info_context,
        brand_products_size,
):
    """
    Проверяется, что при вызове stq в БД сохраняются товары,
    которые пользователь заказывал в магазинах разных брендов
    в зависимости от ограничений из конфига
    """
    pg_add_brand()
    pg_add_place()

    assert not pg_select_user_orders_updates()
    assert not pg_select_user_brand_products()

    expected_brand = []
    for i in range(5):
        orders_count = 5 - i
        for _ in range(orders_count):
            mock_ordershistory_context.add_product(utils.ORIGIN_IDS[i])
        mock_public_id_by_origin_id_context.add_product(
            utils.ORIGIN_IDS[i], utils.PUBLIC_IDS[i],
        )
        expected_brand.append(
            {
                'eater_id': utils.EATER_ID,
                'public_id': utils.PUBLIC_IDS[i],
                'brand_id': utils.BRAND_ID,
                'orders_count': orders_count,
            },
        )

    await stq_runner.eats_retail_categories_update_user_order_history.call(
        task_id=f'{utils.EATER_ID}',
        kwargs={'eater_id': utils.EATER_ID},
        expect_fail=False,
    )
    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_public_id_by_origin_id_context.handler.times_called == 1
    assert mock_ordershistory_context.handler.times_called == 1

    user_in_db = pg_select_user_orders_updates()
    assert len(user_in_db) == 1
    assert user_in_db[0]['eater_id'] == utils.EATER_ID

    if brand_products_size is not None:
        expected_brand = expected_brand[:brand_products_size]
    assert pg_select_user_brand_products() == expected_brand


async def test_stq_update_user_order_history_cross_brand_products(
        stq_runner,
        pg_add_brand,
        pg_add_place,
        pg_select_user_orders_updates,
        pg_select_crossbrand_products,
        mock_ordershistory_context,
        mock_public_id_by_origin_id_context,
        mock_nomenclature_static_info_context,
):
    """
    Проверяется, что при вызове stq в БД сохраняются кроссбрендовые товары,
    которые пользователь заказывал в магазинах разных брендов
    """
    pg_add_brand()
    pg_add_place()

    other_brand = 2
    other_place = 2
    pg_add_brand(other_brand)
    pg_add_place(
        other_place, place_slug=str(other_place), brand_id=other_brand,
    )

    assert not pg_select_user_orders_updates()
    assert not pg_select_crossbrand_products()

    # Кросс брендовый товар в 2 заказах
    mock_ordershistory_context.add_product(utils.ORIGIN_IDS[0])
    mock_ordershistory_context.add_product(utils.ORIGIN_IDS[0])
    mock_public_id_by_origin_id_context.add_product(
        utils.ORIGIN_IDS[0], utils.PUBLIC_IDS[0],
    )
    mock_nomenclature_static_info_context.add_product(
        utils.PUBLIC_IDS[0], sku_id=utils.SKU_IDS[0],
    )

    # Кросс брендовый товар из другого бренда
    mock_ordershistory_context.add_product(
        utils.ORIGIN_IDS[1], place_id=other_place,
    )
    mock_public_id_by_origin_id_context.add_product(
        utils.ORIGIN_IDS[1], utils.PUBLIC_IDS[1], place_id=other_place,
    )
    mock_nomenclature_static_info_context.add_product(
        utils.PUBLIC_IDS[1], sku_id=utils.SKU_IDS[1],
    )

    # Не кросс брендовый товар
    mock_ordershistory_context.add_product(utils.ORIGIN_IDS[2])
    mock_public_id_by_origin_id_context.add_product(
        utils.ORIGIN_IDS[2], utils.PUBLIC_IDS[2],
    )
    mock_nomenclature_static_info_context.add_product(utils.PUBLIC_IDS[0])

    await stq_runner.eats_retail_categories_update_user_order_history.call(
        task_id=f'{utils.EATER_ID}',
        kwargs={'eater_id': utils.EATER_ID},
        expect_fail=False,
    )
    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_public_id_by_origin_id_context.handler.times_called == 2
    assert mock_ordershistory_context.handler.times_called == 1

    user_in_db = pg_select_user_orders_updates()
    assert len(user_in_db) == 1
    assert user_in_db[0]['eater_id'] == utils.EATER_ID

    products_in_db = pg_select_crossbrand_products()
    assert products_in_db == [
        {
            'eater_id': utils.EATER_ID,
            'sku_id': utils.SKU_IDS[0],
            'orders_count': 2,
        },
        {
            'eater_id': utils.EATER_ID,
            'sku_id': utils.SKU_IDS[1],
            'orders_count': 1,
        },
    ]


@pytest.mark.parametrize(
    'cross_brand_products_size',
    [
        pytest.param(1, marks=make_config(cross_brand_products=1)),
        pytest.param(2, marks=make_config(cross_brand_products=2)),
        pytest.param(5, marks=make_config(cross_brand_products=5)),
        pytest.param(5, marks=make_config(cross_brand_products=6)),
        pytest.param(None),
    ],
)
async def test_stq_update_user_order_history_max_cross_brand_products(
        stq_runner,
        pg_add_brand,
        pg_add_place,
        pg_select_user_orders_updates,
        pg_select_crossbrand_products,
        mock_ordershistory_context,
        mock_public_id_by_origin_id_context,
        mock_nomenclature_static_info_context,
        cross_brand_products_size,
):
    """
    Проверяется, что при вызове stq в БД сохраняются кросс брендовые товары,
    которые пользователь заказывал в магазинах разных брендов
    в зависимости от ограничений из конфига
    """
    pg_add_brand()
    pg_add_place()

    assert not pg_select_user_orders_updates()
    assert not pg_select_crossbrand_products()

    expected_cross_brand = []
    for i in range(5):
        orders_count = 5 - i
        for _ in range(orders_count):
            mock_ordershistory_context.add_product(utils.ORIGIN_IDS[i])
        mock_public_id_by_origin_id_context.add_product(
            utils.ORIGIN_IDS[i], utils.PUBLIC_IDS[i],
        )
        mock_nomenclature_static_info_context.add_product(
            utils.PUBLIC_IDS[i], sku_id=utils.SKU_IDS[i],
        )
        expected_cross_brand.append(
            {
                'eater_id': utils.EATER_ID,
                'sku_id': utils.SKU_IDS[i],
                'orders_count': orders_count,
            },
        )

    await stq_runner.eats_retail_categories_update_user_order_history.call(
        task_id=f'{utils.EATER_ID}',
        kwargs={'eater_id': utils.EATER_ID},
        expect_fail=False,
    )
    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_public_id_by_origin_id_context.handler.times_called == 1
    assert mock_ordershistory_context.handler.times_called == 1

    user_in_db = pg_select_user_orders_updates()
    assert len(user_in_db) == 1
    assert user_in_db[0]['eater_id'] == utils.EATER_ID

    if cross_brand_products_size is not None:
        expected_cross_brand = expected_cross_brand[:cross_brand_products_size]
    assert pg_select_crossbrand_products() == expected_cross_brand
