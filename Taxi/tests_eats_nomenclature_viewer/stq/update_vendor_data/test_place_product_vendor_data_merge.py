import datetime as dt

import pytest
import pytz

from tests_eats_nomenclature_viewer import models
from tests_eats_nomenclature_viewer import utils
from tests_eats_nomenclature_viewer.stq.update_vendor_data import constants

S3_PATH = '/some_path.json'
OLD_TIME = dt.datetime(2019, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=['brand.sql', 'place.sql', 'product_for_data_template.sql'],
)
async def test_merge_update_unchanged(load_json, sql, test_utils):
    old_vendor_data = models.PlaceProductVendorData(
        updated_at=OLD_TIME, **constants.DEFAULT_PLACE_PRODUCT_ITEM_VALUES,
    )
    sql.save(old_vendor_data)

    # save the same data
    data_template = load_json('single_object_data_template.json')
    await test_utils.store_data_and_call_stq_update_vendor_data(
        place_id=constants.PLACE_ID, path=S3_PATH, data=data_template,
    )

    db_vendor_data = sql.load_all(models.PlaceProductVendorData)
    assert db_vendor_data == [old_vendor_data]


@pytest.mark.parametrize(
    'old_db_value, new_json_value, expected_db_value',
    [
        pytest.param(
            {'vendor_code': '1'},
            {'vendor_code': '2'},
            {'vendor_code': '2'},
            id='vendor_code',
        ),
        pytest.param(
            {'position': '1'},
            {'position': '2'},
            {'position': '2'},
            id='position',
        ),
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
    vendor_data = models.PlaceProductVendorData(
        updated_at=OLD_TIME, **constants.DEFAULT_PLACE_PRODUCT_ITEM_VALUES,
    )
    vendor_data.update(old_db_value)
    sql.save(vendor_data)

    # change value
    expected_vendor_data = vendor_data.clone()
    expected_vendor_data.updated_at = None
    expected_vendor_data.update(expected_db_value)

    data_template = load_json('single_object_data_template.json')
    utils.update_dict_by_paths(data_template['items'][0], new_json_value)
    await test_utils.store_data_and_call_stq_update_vendor_data(
        place_id=constants.PLACE_ID, path=S3_PATH, data=data_template,
    )

    db_vendor_data = sql.load_all(models.PlaceProductVendorData)
    assert len(db_vendor_data) == 1
    db_vendor_data_1 = db_vendor_data[0]

    assert db_vendor_data_1.updated_at > vendor_data.updated_at
    db_vendor_data_1.updated_at = None
    assert db_vendor_data_1 == expected_vendor_data


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

    vendor_data_1 = models.PlaceProductVendorData(
        place_id=constants.PLACE_ID,
        product_nmn_id=product_1.nmn_id,
        vendor_code='1',
        updated_at=OLD_TIME,
    )
    sql.save(vendor_data_1)

    # insert new data
    expected_vendor_data = models.PlaceProductVendorData(
        place_id=constants.PLACE_ID,
        product_nmn_id=product_2.nmn_id,
        vendor_code='2',
    )

    data_template = load_json('single_object_data_template.json')
    data_template['items'][0].update(
        {
            'origin_id': product_2.origin_id,
            'vendor_code': expected_vendor_data.vendor_code,
        },
    )
    await test_utils.store_data_and_call_stq_update_vendor_data(
        place_id=constants.PLACE_ID, path=S3_PATH, data=data_template,
    )

    id_to_data = {
        i.product_nmn_id: i
        for i in sql.load_all(models.PlaceProductVendorData)
    }
    assert len(id_to_data) == 2
    db_vendor_data_1 = id_to_data[vendor_data_1.product_nmn_id]
    db_vendor_data_2 = id_to_data[expected_vendor_data.product_nmn_id]

    assert db_vendor_data_1 == vendor_data_1
    assert db_vendor_data_2.updated_at > vendor_data_1.updated_at
    db_vendor_data_2.updated_at = None
    assert db_vendor_data_2 == expected_vendor_data
