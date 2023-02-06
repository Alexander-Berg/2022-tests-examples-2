import copy
import datetime as dt
import json

import pytest
import pytz

from tests_eats_nomenclature_viewer.stq.update_vendor_data import constants
from tests_eats_nomenclature_viewer import utils

S3_PATH = '/some_path.json'
OLD_TIME = dt.datetime(2019, 3, 2, 12, tzinfo=pytz.UTC)
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=['brand.sql', 'place.sql', 'product_for_data_template.sql'],
)
async def test_new(test_utils, load, mds_s3_storage):
    expected_path = f'{constants.FALLBACK_FILES_DIR}/{constants.PLACE_ID}.json'
    json_data = load('single_object_data_template.json').encode('utf-8')

    await test_utils.store_data_and_call_stq_update_vendor_data(
        path=S3_PATH,
        data=load('single_object_data_template.json').encode('utf-8'),
        place_id=constants.PLACE_ID,
    )

    assert mds_s3_storage.storage[expected_path].data == json_data


@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=['brand.sql', 'place.sql', 'product_for_data_template.sql'],
)
async def test_overwrite(mds_s3_storage, load_json, test_utils):
    now = utils.now_with_tz()
    path = f'{constants.FALLBACK_FILES_DIR}/{constants.PLACE_ID}.json'
    json_data = load_json('single_object_data_template.json')

    old_json_data = copy.deepcopy(json_data)
    old_json_data['items'][0]['vendor_code'] = '1'
    old_json_data = json.dumps(old_json_data).encode('utf-8')

    mds_s3_storage.put_object(
        key=path, body=old_json_data, last_modified=OLD_TIME,
    )

    new_json_data = copy.deepcopy(json_data)
    new_json_data['items'][0]['vendor_code'] = '2'
    new_json_data = json.dumps(new_json_data).encode('utf-8')

    await test_utils.store_data_and_call_stq_update_vendor_data(
        path=S3_PATH, data=new_json_data, place_id=constants.PLACE_ID,
    )

    s3value = mds_s3_storage.storage[path]
    assert s3value.data == new_json_data
    assert dt.datetime.fromisoformat(s3value.meta['Last-Modified']) >= now
