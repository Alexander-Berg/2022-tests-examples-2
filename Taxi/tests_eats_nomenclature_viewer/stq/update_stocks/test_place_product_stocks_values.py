import datetime as dt
import decimal as dec

import pytest
import pytz

from tests_eats_nomenclature_viewer import models

S3_PATH = '/some_path.json'
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.s3(
    files={'new/availability/1.json': 'minimal_schema_availability_data.json'},
)
@pytest.mark.pgsql(
    'eats_nomenclature_viewer', files=['minimal_schema_data.sql'],
)
async def test_minimal_schema(load, test_utils, sql):
    expected_stocks = models.PlaceProductStock(
        place_id=1, product_nmn_id='00000000-0000-0000-0000-000000000001',
    )

    await test_utils.store_data_and_call_stq_update_stocks(
        path=S3_PATH,
        data=load('minimal_schema_data.json').encode('utf-8'),
        place_id=1,
    )

    db_stocks = sql.load_all(models.PlaceProductStock)
    # replace updated_at for equality check to work
    for i in db_stocks:
        i.reset_field_recursive('updated_at')
    assert db_stocks == [expected_stocks]


@pytest.mark.s3(
    files={'new/availability/1.json': 'full_schema_availability_data.json'},
)
@pytest.mark.pgsql('eats_nomenclature_viewer', files=['full_schema_data.sql'])
async def test_full_schema(load, test_utils, sql):
    expected_stocks = [
        models.PlaceProductStock(
            place_id=1,
            product_nmn_id='00000000-0000-0000-0000-000000000001',
            value=dec.Decimal('1.1'),
        ),
        models.PlaceProductStock(
            place_id=1,
            product_nmn_id='00000000-0000-0000-0000-000000000002',
            value=dec.Decimal('2.2'),
        ),
    ]

    await test_utils.store_data_and_call_stq_update_stocks(
        path=S3_PATH,
        data=load('full_schema_data.json').encode('utf-8'),
        place_id=1,
    )

    db_stocks = sql.load_all(models.PlaceProductStock)
    # replace updated_at for equality check to work
    for i in db_stocks:
        i.reset_field_recursive('updated_at')
    assert sorted(db_stocks) == sorted(expected_stocks)
