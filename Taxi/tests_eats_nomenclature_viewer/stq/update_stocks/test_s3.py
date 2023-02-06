import copy
import datetime as dt
import json

import pytest
import pytz

from tests_eats_nomenclature_viewer import utils
from tests_eats_nomenclature_viewer.stq.update_stocks import constants

S3_PATH = '/some_path.json'
OLD_TIME = dt.datetime(2019, 3, 2, 12, tzinfo=pytz.UTC)
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.s3(
    files={constants.S3_AVAILABILITY_FILE: 'availability_item_template.json'},
)
@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=[
        'brand.sql',
        'place.sql',
        'product_for_item_template.sql',
        'availability_file.sql',
    ],
)
async def test_new(mds_s3_storage, load, test_utils):
    expected_path = f'{constants.FALLBACK_STOCK_DIR}/{constants.PLACE_ID}.json'
    json_data = load('stock_item_template.json').encode('utf-8')

    await test_utils.store_data_and_call_stq_update_stocks(
        place_id=constants.PLACE_ID, path=S3_PATH, data=json_data,
    )

    assert mds_s3_storage.storage[expected_path].data == json_data


@pytest.mark.s3(
    files={constants.S3_AVAILABILITY_FILE: 'availability_item_template.json'},
)
@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=[
        'brand.sql',
        'place.sql',
        'product_for_item_template.sql',
        'availability_file.sql',
    ],
)
async def test_overwrite(mds_s3_storage, load_json, test_utils):
    now = utils.now_with_tz()
    path = f'{constants.FALLBACK_STOCK_DIR}/{constants.PLACE_ID}.json'
    json_data = load_json('stock_item_template.json')

    old_json_data = copy.deepcopy(json_data)
    old_json_data['items'][0]['value'] = '1.0'
    old_json_data = json.dumps(old_json_data).encode('utf-8')

    mds_s3_storage.put_object(
        key=path, body=old_json_data, last_modified=OLD_TIME,
    )

    new_json_data = copy.deepcopy(json_data)
    new_json_data['items'][0]['value'] = '2.0'
    new_json_data = json.dumps(new_json_data).encode('utf-8')

    await test_utils.store_data_and_call_stq_update_stocks(
        place_id=constants.PLACE_ID, path=S3_PATH, data=new_json_data,
    )

    s3value = mds_s3_storage.storage[path]
    assert s3value.data == new_json_data
    assert dt.datetime.fromisoformat(s3value.meta['Last-Modified']) >= now
