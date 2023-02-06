import datetime as dt

import pytest
import pytz

from tests_eats_nomenclature_viewer import models

S3_PATH = '/some_path.json'
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.pgsql(
    'eats_nomenclature_viewer', files=['minimal_schema_data.sql'],
)
async def test_minimal_schema(load, test_utils, sql):
    expected_vendor_data = models.PlaceProductVendorData(
        place_id=1, product_nmn_id='00000000-0000-0000-0000-000000000001',
    )

    await test_utils.store_data_and_call_stq_update_vendor_data(
        path=S3_PATH,
        data=load('minimal_schema_data.json').encode('utf-8'),
        place_id=1,
    )

    db_vendor_data = sql.load_all(models.PlaceProductVendorData)
    # replace updated_at for equality check to work
    for i in db_vendor_data:
        i.reset_field_recursive('updated_at')
    assert db_vendor_data == [expected_vendor_data]


@pytest.mark.pgsql('eats_nomenclature_viewer', files=['full_schema_data.sql'])
async def test_full_schema(load, test_utils, sql):
    expected_vendor_data = [
        models.PlaceProductVendorData(
            place_id=1,
            product_nmn_id='00000000-0000-0000-0000-000000000001',
            vendor_code='code 1',
            position='position 1',
        ),
        models.PlaceProductVendorData(
            place_id=1,
            product_nmn_id='00000000-0000-0000-0000-000000000002',
            vendor_code='code 2',
            position='position 2',
        ),
    ]

    await test_utils.store_data_and_call_stq_update_vendor_data(
        path=S3_PATH,
        data=load('full_schema_data.json').encode('utf-8'),
        place_id=1,
    )

    db_vendor_data = sql.load_all(models.PlaceProductVendorData)
    # replace updated_at for equality check to work
    for i in db_vendor_data:
        i.reset_field_recursive('updated_at')
    assert sorted(db_vendor_data) == sorted(expected_vendor_data)
