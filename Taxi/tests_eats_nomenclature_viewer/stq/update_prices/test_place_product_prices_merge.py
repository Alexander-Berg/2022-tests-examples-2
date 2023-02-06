import datetime as dt
import decimal as dec

import pytest
import pytz

from tests_eats_nomenclature_viewer import models
from tests_eats_nomenclature_viewer import utils
from tests_eats_nomenclature_viewer.stq.update_prices import constants

S3_PATH = '/some_path.json'
OLD_TIME = dt.datetime(2019, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=['brand.sql', 'place.sql', 'product_for_data_template.sql'],
)
async def test_merge_update_unchanged(load_json, sql, test_utils):
    old_place_product_price = models.PlaceProductPrice(
        updated_at=OLD_TIME, **constants.DEFAULT_PLACE_PRODUCT_ITEM_VALUES,
    )
    sql.save(old_place_product_price)

    # save the same data
    data_template = load_json('single_object_data_template.json')
    await test_utils.store_data_and_call_stq_update_prices(
        place_id=constants.PLACE_ID, path=S3_PATH, data=data_template,
    )

    db_place_product_prices = sql.load_all(models.PlaceProductPrice)
    assert db_place_product_prices == [old_place_product_price]


@pytest.mark.parametrize(
    'old_db_value, new_json_value, expected_db_value',
    [
        pytest.param(
            {'price': dec.Decimal('1.0')},
            {'price': '2.0'},
            {'price': dec.Decimal('2.0')},
            id='price',
        ),
        pytest.param(
            {'old_price': dec.Decimal('1.0')},
            {'old_price': '2.0'},
            {'old_price': dec.Decimal('2.0')},
            id='old_price',
        ),
        pytest.param(
            {'full_price': dec.Decimal('1.0')},
            {'full_price': '2.0'},
            {'full_price': dec.Decimal('2.0')},
            id='full_price',
        ),
        pytest.param(
            {'old_full_price': dec.Decimal('1.0')},
            {'old_full_price': '2.0'},
            {'old_full_price': dec.Decimal('2.0')},
            id='old_full_price',
        ),
        pytest.param({'vat': 1}, {'vat': '2'}, {'vat': 2}, id='vat'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=['brand.sql', 'place.sql', 'product_for_data_template.sql'],
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
    place_product_price = models.PlaceProductPrice(
        updated_at=OLD_TIME, **constants.DEFAULT_PLACE_PRODUCT_ITEM_VALUES,
    )
    place_product_price.update(old_db_value)
    sql.save(place_product_price)

    # change value
    expected_place_product_price = place_product_price.clone()
    expected_place_product_price.updated_at = None
    expected_place_product_price.update(expected_db_value)

    data_template = load_json('single_object_data_template.json')
    utils.update_dict_by_paths(data_template['items'][0], new_json_value)
    await test_utils.store_data_and_call_stq_update_prices(
        place_id=constants.PLACE_ID, path=S3_PATH, data=data_template,
    )

    db_place_product_prices = sql.load_all(models.PlaceProductPrice)
    assert len(db_place_product_prices) == 1
    db_place_product_price = db_place_product_prices[0]

    assert db_place_product_price.updated_at > place_product_price.updated_at
    db_place_product_price.updated_at = None
    assert db_place_product_price == expected_place_product_price


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

    place_product_price_1 = models.PlaceProductPrice(
        place_id=constants.PLACE_ID,
        product_nmn_id=product_1.nmn_id,
        price=dec.Decimal('1.0'),
        updated_at=OLD_TIME,
    )
    sql.save(place_product_price_1)

    # insert new data
    expected_place_product_price = models.PlaceProductPrice(
        place_id=constants.PLACE_ID,
        product_nmn_id=product_2.nmn_id,
        price=dec.Decimal('2.0'),
    )

    data_template = load_json('single_object_data_template.json')
    data_template['items'][0].update(
        {
            'origin_id': product_2.origin_id,
            'price': str(expected_place_product_price.price),
        },
    )
    await test_utils.store_data_and_call_stq_update_prices(
        place_id=constants.PLACE_ID, path=S3_PATH, data=data_template,
    )

    id_to_data = {
        i.product_nmn_id: i for i in sql.load_all(models.PlaceProductPrice)
    }
    assert len(id_to_data) == 2
    db_place_product_price_1 = id_to_data[place_product_price_1.product_nmn_id]
    db_place_product_price_2 = id_to_data[
        expected_place_product_price.product_nmn_id
    ]

    assert db_place_product_price_1 == place_product_price_1
    assert (
        db_place_product_price_2.updated_at > place_product_price_1.updated_at
    )
    db_place_product_price_2.updated_at = None
    assert db_place_product_price_2 == expected_place_product_price
