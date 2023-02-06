import datetime as dt
import decimal as dec

import pytest
import pytz

from tests_eats_nomenclature_viewer import models
from tests_eats_nomenclature_viewer import utils
from tests_eats_nomenclature_viewer.stq.update_stocks import constants

S3_PATH = '/some_path.json'
OLD_TIME = dt.datetime(2019, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=['brand.sql', 'place.sql', 'product_for_item_template.sql'],
)
async def test_merge_update_unchanged(load_json, sql, test_utils):
    old_stock = models.PlaceProductStock(
        updated_at=OLD_TIME, **constants.DEFAULT_STOCK_ITEM_VALUES,
    )
    sql.save(old_stock)

    # save the same data
    test_utils.save_availability_data(
        data=load_json('availability_item_template.json'),
        place_id=constants.PLACE_ID,
    )

    await test_utils.store_data_and_call_stq_update_stocks(
        place_id=constants.PLACE_ID,
        path=S3_PATH,
        data=load_json('stock_item_template.json'),
    )

    db_stocks = sql.load_all(models.PlaceProductStock)
    assert db_stocks == [old_stock]


@pytest.mark.parametrize(
    'old_db_value, new_json_value, expected_db_value',
    [
        pytest.param(
            {'value': dec.Decimal('1.1')},
            {'value': '2.2'},
            {'value': dec.Decimal('2.2')},
            id='value',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=['brand.sql', 'place.sql', 'product_for_item_template.sql'],
)
async def test_merge_update_changed(
        load_json,
        sql,
        test_utils,
        # parametrize
        old_db_value,
        new_json_value,
        expected_db_value,
):
    stock = models.PlaceProductStock(
        updated_at=OLD_TIME, **constants.DEFAULT_STOCK_ITEM_VALUES,
    )
    stock.update(old_db_value)
    sql.save(stock)

    test_utils.save_availability_data(
        data=load_json('availability_item_template.json'),
        place_id=constants.PLACE_ID,
    )

    # change value
    expected_stock = stock.clone()
    expected_stock.updated_at = None
    expected_stock.update(expected_db_value)

    stock_data = load_json('stock_item_template.json')
    utils.update_dict_by_paths(stock_data['items'][0], new_json_value)
    await test_utils.store_data_and_call_stq_update_stocks(
        place_id=constants.PLACE_ID, path=S3_PATH, data=stock_data,
    )

    db_stocks = sql.load_all(models.PlaceProductStock)
    assert len(db_stocks) == 1
    db_stocks_1 = db_stocks[0]

    assert db_stocks_1.updated_at > stock.updated_at
    db_stocks_1.updated_at = None
    assert db_stocks_1 == expected_stock


@pytest.mark.parametrize(
    'old_db_value',
    [
        pytest.param({'value': dec.Decimal('1.1')}, id='from value to zero'),
        pytest.param({'value': None}, id='from null to zero'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=['brand.sql', 'place.sql', 'product_for_item_template.sql'],
)
async def test_merge_update_changed_with_availability(
        load_json,
        sql,
        test_utils,
        # parametrize
        old_db_value,
):
    stock = models.PlaceProductStock(
        updated_at=OLD_TIME, **constants.DEFAULT_STOCK_ITEM_VALUES,
    )
    stock.update(old_db_value)
    sql.save(stock)

    # change value
    expected_stock = stock.clone()
    expected_stock.updated_at = None
    expected_stock.value = dec.Decimal('0.0')

    availability_data = load_json('availability_item_template.json')
    availability_data['items'][0]['available'] = False
    test_utils.save_availability_data(
        data=availability_data, place_id=constants.PLACE_ID,
    )

    await test_utils.store_data_and_call_stq_update_stocks(
        place_id=constants.PLACE_ID,
        path=S3_PATH,
        data=load_json('stock_item_template.json'),
    )

    db_stocks = sql.load_all(models.PlaceProductStock)
    assert len(db_stocks) == 1
    db_stocks_1 = db_stocks[0]

    assert db_stocks_1.updated_at > stock.updated_at
    db_stocks_1.updated_at = None
    assert db_stocks_1 == expected_stock


@pytest.mark.pgsql(
    'eats_nomenclature_viewer', files=['brand.sql', 'place.sql'],
)
async def test_merge_insert(load_json, sql, test_utils):
    product_1 = models.Product(
        brand_id=constants.BRAND_ID,
        nmn_id='00000000-0000-0000-0000-000000000001',
        origin_id='origin_id_1',
    )
    sql.save(product_1)

    product_2 = models.Product(
        brand_id=constants.BRAND_ID,
        nmn_id='00000000-0000-0000-0000-000000000002',
        origin_id='origin_id_2',
    )
    sql.save(product_2)

    stocks_1 = models.PlaceProductStock(
        place_id=constants.PLACE_ID,
        product_nmn_id=product_1.nmn_id,
        value=dec.Decimal('1.0'),
        updated_at=OLD_TIME,
    )
    sql.save(stocks_1)

    # insert new data
    availability_data = load_json('availability_item_template.json')
    availability_data['items'][0] = {
        'origin_id': product_2.origin_id,
        'available': True,
    }
    test_utils.save_availability_data(
        data=availability_data, place_id=constants.PLACE_ID,
    )

    expected_stock = models.PlaceProductStock(
        place_id=constants.PLACE_ID,
        product_nmn_id=product_2.nmn_id,
        value=dec.Decimal('2.0'),
    )

    stock_data = load_json('stock_item_template.json')
    stock_data['items'][0] = {
        'origin_id': product_2.origin_id,
        'value': str(expected_stock.value),
    }
    await test_utils.store_data_and_call_stq_update_stocks(
        place_id=constants.PLACE_ID, path=S3_PATH, data=stock_data,
    )

    id_to_data = {
        i.product_nmn_id: i for i in sql.load_all(models.PlaceProductStock)
    }
    assert len(id_to_data) == 2
    db_stocks_1 = id_to_data[stocks_1.product_nmn_id]
    db_stocks_2 = id_to_data[expected_stock.product_nmn_id]

    assert db_stocks_1 == stocks_1
    assert db_stocks_2.updated_at > stocks_1.updated_at
    db_stocks_2.updated_at = None
    assert db_stocks_2 == expected_stock
