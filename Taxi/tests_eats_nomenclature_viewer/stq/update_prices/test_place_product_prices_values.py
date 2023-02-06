import datetime as dt
import decimal as dec

import pytest
import pytz

from tests_eats_nomenclature_viewer import models

S3_PATH = '/some_path.json'
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.pgsql(
    'eats_nomenclature_viewer', files=['minimal_schema_data.sql'],
)
async def test_minimal_schema(stq_runner, load, mds_s3_storage, sql):
    expected_place_product_price = models.PlaceProductPrice(
        place_id=1,
        product_nmn_id='00000000-0000-0000-0000-000000000001',
        price=dec.Decimal('10.0'),
    )

    mds_s3_storage.put_object(
        S3_PATH, load('minimal_schema_data.json').encode('utf-8'),
    )
    await stq_runner.eats_nomenclature_viewer_update_prices.call(
        task_id='1',
        kwargs={
            'place_id': 1,
            's3_path': S3_PATH,
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    db_place_product_prices = sql.load_all(models.PlaceProductPrice)
    # replace updated_at for equality check to work
    for i in db_place_product_prices:
        i.reset_field_recursive('updated_at')
    assert db_place_product_prices == [expected_place_product_price]


@pytest.mark.pgsql('eats_nomenclature_viewer', files=['full_schema_data.sql'])
async def test_full_schema(stq_runner, load, mds_s3_storage, sql):
    expected_place_product_prices = [
        models.PlaceProductPrice(
            place_id=1,
            product_nmn_id='00000000-0000-0000-0000-000000000001',
            price=dec.Decimal('1.0'),
            old_price=dec.Decimal('2.0'),
            full_price=dec.Decimal('3.0'),
            old_full_price=dec.Decimal('4.0'),
            vat=5,
        ),
        models.PlaceProductPrice(
            place_id=1,
            product_nmn_id='00000000-0000-0000-0000-000000000002',
            price=dec.Decimal('6.0'),
            old_price=dec.Decimal('7.0'),
            full_price=dec.Decimal('8.0'),
            old_full_price=dec.Decimal('9.0'),
            vat=10,
        ),
    ]

    mds_s3_storage.put_object(
        S3_PATH, load('full_schema_data.json').encode('utf-8'),
    )
    await stq_runner.eats_nomenclature_viewer_update_prices.call(
        task_id='1',
        kwargs={
            'place_id': 1,
            's3_path': S3_PATH,
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    db_place_product_prices = sql.load_all(models.PlaceProductPrice)
    # replace updated_at for equality check to work
    for i in db_place_product_prices:
        i.reset_field_recursive('updated_at')
    assert sorted(db_place_product_prices) == sorted(
        expected_place_product_prices,
    )
