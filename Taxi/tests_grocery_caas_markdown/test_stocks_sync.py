import dataclasses
import decimal

import pytest

from tests_grocery_caas_markdown.common import constants
from tests_grocery_caas_markdown.plugins import (
    mock_grocery_wms as mock_grocery_wms_plugin,
)


@pytest.mark.suspend_periodic_tasks('stocks-sync-periodic')
async def test_grocery_wms_request(taxi_grocery_caas_markdown, grocery_wms):
    grocery_wms.setup_request_checking(stocks_filter='markdown_stocks')

    await taxi_grocery_caas_markdown.run_periodic_task('stocks-sync-periodic')

    assert grocery_wms.times_called == 1


@pytest.mark.suspend_periodic_tasks('stocks-sync-periodic')
async def test_one_product(
        taxi_grocery_caas_markdown, caas_markdown_db, grocery_wms,
):
    depot_id = constants.DEPOT_ID_WITH_MARKDOWNS
    product_id = constants.DEFAULT_PRODUCT_ID

    grocery_wms.add_stocks(depot_id, product_id)

    await taxi_grocery_caas_markdown.run_periodic_task('stocks-sync-periodic')

    assert grocery_wms.times_called == 2
    markdown_products = [
        dataclasses.asdict(mp)
        for mp in caas_markdown_db.get_markdown_products()
    ]

    assert markdown_products == [
        dict(
            depot_id=depot_id,
            product_id=product_id,
            quantity=constants.DEFAULT_PRODUCT_QUANTITY_PG,
        ),
    ]


@pytest.mark.suspend_periodic_tasks('stocks-sync-periodic')
async def test_multiple_products(
        taxi_grocery_caas_markdown, caas_markdown_db, grocery_wms,
):
    depot_id = constants.DEPOT_ID_WITH_MARKDOWNS
    product_id_1 = '123456789abcdef0002222000123456789abcdef0001'
    quantity_1 = decimal.Decimal(123)
    product_id_2 = '123456789abcdef0002222000123456789abcdef0002'
    quantity_2 = decimal.Decimal(321)

    grocery_wms.add_stocks(
        depot_id,
        [
            mock_grocery_wms_plugin.Stock(
                product_id=product_id_1, quantity=quantity_1,
            ),
            mock_grocery_wms_plugin.Stock(
                product_id=product_id_2, quantity=quantity_2,
            ),
        ],
    )

    await taxi_grocery_caas_markdown.run_periodic_task('stocks-sync-periodic')

    assert grocery_wms.times_called == 2
    markdown_products = [
        dataclasses.asdict(mp)
        for mp in caas_markdown_db.get_markdown_products()
    ]

    assert markdown_products == [
        dict(depot_id=depot_id, product_id=product_id_1, quantity=quantity_1),
        dict(depot_id=depot_id, product_id=product_id_2, quantity=quantity_2),
    ]


@pytest.mark.suspend_periodic_tasks('stocks-sync-periodic')
async def test_update_product(
        taxi_grocery_caas_markdown, caas_markdown_db, grocery_wms, mocked_time,
):
    depot_id = constants.DEPOT_ID_WITH_MARKDOWNS
    product_id = constants.DEFAULT_PRODUCT_ID
    new_quantity = decimal.Decimal(123)

    grocery_wms.add_stocks(depot_id, product_id)

    await taxi_grocery_caas_markdown.run_periodic_task('stocks-sync-periodic')
    markdown_products = [
        dataclasses.asdict(mp)
        for mp in caas_markdown_db.get_markdown_products()
    ]

    assert markdown_products == [
        dict(
            depot_id=depot_id,
            product_id=product_id,
            quantity=constants.DEFAULT_PRODUCT_QUANTITY_PG,
        ),
    ]

    grocery_wms.add_stocks(
        depot_id,
        mock_grocery_wms_plugin.Stock(
            product_id=product_id, quantity=new_quantity,
        ),
    )

    mocked_time.sleep(121)

    await taxi_grocery_caas_markdown.run_periodic_task('stocks-sync-periodic')
    markdown_products = [
        dataclasses.asdict(mp)
        for mp in caas_markdown_db.get_markdown_products()
    ]

    assert markdown_products == [
        dict(depot_id=depot_id, product_id=product_id, quantity=new_quantity),
    ]


@pytest.mark.parametrize('quantity', [decimal.Decimal(0), decimal.Decimal(-1)])
@pytest.mark.suspend_periodic_tasks('stocks-sync-periodic')
async def test_zero_or_below_zero_quantity(
        taxi_grocery_caas_markdown, caas_markdown_db, grocery_wms, quantity,
):
    depot_id = constants.DEPOT_ID_WITH_MARKDOWNS
    product_id = constants.DEFAULT_PRODUCT_ID

    grocery_wms.add_stocks(
        depot_id,
        mock_grocery_wms_plugin.Stock(
            product_id=product_id, quantity=quantity,
        ),
    )

    await taxi_grocery_caas_markdown.run_periodic_task('stocks-sync-periodic')
    markdown_products = [
        dataclasses.asdict(mp)
        for mp in caas_markdown_db.get_markdown_products()
    ]

    assert markdown_products == [
        dict(
            depot_id=depot_id,
            product_id=product_id,
            quantity=decimal.Decimal(0),
        ),
    ]


@pytest.mark.parametrize('shelf_type', ['store', 'parcel'])
@pytest.mark.suspend_periodic_tasks('stocks-sync-periodic')
async def test_invalid_shelf_type(
        taxi_grocery_caas_markdown, caas_markdown_db, grocery_wms, shelf_type,
):
    depot_id = constants.DEPOT_ID_WITH_MARKDOWNS
    product_id_1 = '123456789abcdef0002222000123456789abcdef0001'
    product_id_2 = '123456789abcdef0002222000123456789abcdef0002'

    grocery_wms.add_stocks(depot_id, product_id_1)
    grocery_wms.add_stocks(depot_id, product_id_2, shelf_type=shelf_type)

    await taxi_grocery_caas_markdown.run_periodic_task('stocks-sync-periodic')
    markdown_products = [
        dataclasses.asdict(mp)
        for mp in caas_markdown_db.get_markdown_products()
    ]

    assert markdown_products == [
        dict(
            depot_id=depot_id,
            product_id=product_id_1,
            quantity=constants.DEFAULT_PRODUCT_QUANTITY_PG,
        ),
    ]


@pytest.mark.suspend_periodic_tasks('stocks-sync-periodic')
async def test_multiple_depots(
        taxi_grocery_caas_markdown, caas_markdown_db, grocery_wms,
):
    depot_id_1 = '123456789abcdef0001111000123456789abcdef0011'
    product_id_1 = '123456789abcdef0002222000123456789abcdef0001'
    depot_id_2 = '123456789abcdef0001111000123456789abcdef0012'
    product_id_2 = '123456789abcdef0002222000123456789abcdef0002'

    grocery_wms.add_stocks(depot_id_1, product_id_1)
    grocery_wms.add_stocks(depot_id_2, product_id_2)

    await taxi_grocery_caas_markdown.run_periodic_task('stocks-sync-periodic')
    markdown_products = [
        dataclasses.asdict(mp)
        for mp in caas_markdown_db.get_markdown_products()
    ]

    assert markdown_products == [
        dict(
            depot_id=depot_id_1,
            product_id=product_id_1,
            quantity=constants.DEFAULT_PRODUCT_QUANTITY_PG,
        ),
        dict(
            depot_id=depot_id_2,
            product_id=product_id_2,
            quantity=constants.DEFAULT_PRODUCT_QUANTITY_PG,
        ),
    ]
