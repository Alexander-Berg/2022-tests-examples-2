import datetime as dt
import json
import re

import pytest
import pytz

from . import constants

S3_NMN_PATH = 'data.json'
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.s3(files={S3_NMN_PATH: 'minimal_schema_data.json'})
@pytest.mark.pgsql('eats_nomenclature', files=['minimal_schema_data.sql'])
async def test_minimal_schema(
        stq, stq_runner, load_json, mds_s3_storage, test_utils,
):
    await stq_runner.eats_nomenclature_brand_processing.call(
        task_id='1',
        args=[],
        kwargs={
            'brand_id': '1',
            's3_path': S3_NMN_PATH,
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    s3_items = [
        i
        for i in mds_s3_storage.storage.items()
        if re.match(constants.S3_PATH_PATTERN, i[0])
    ]
    assert len(s3_items) == 1

    s3path, s3value = s3_items[0]
    assert test_utils.sorted_json_data(
        json.loads(s3value.data),
    ) == test_utils.sorted_json_data(load_json('minimal_schema_result.json'))

    task_info = stq.eats_nomenclature_viewer_update_vendor_data.next_call()
    assert task_info['kwargs']['s3_path'] == s3path
    assert task_info['kwargs']['place_id'] == 1


@pytest.mark.s3(files={S3_NMN_PATH: 'full_schema_data.json'})
@pytest.mark.pgsql('eats_nomenclature', files=['full_schema_data.sql'])
async def test_full_schema(
        stq_runner, stq, load_json, mds_s3_storage, test_utils,
):
    await stq_runner.eats_nomenclature_brand_processing.call(
        task_id='1',
        args=[],
        kwargs={
            'brand_id': '1',
            's3_path': S3_NMN_PATH,
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    s3_items = [
        i
        for i in mds_s3_storage.storage.items()
        if re.match(constants.S3_PATH_PATTERN, i[0])
    ]
    assert len(s3_items) == 1

    s3_path, s3_value = list(s3_items)[0]
    assert test_utils.sorted_json_data(
        json.loads(s3_value.data),
    ) == test_utils.sorted_json_data(load_json('full_schema_result.json'))

    place_ids = set()
    for _ in range(0, 2):
        task_info = stq.eats_nomenclature_viewer_update_vendor_data.next_call()
        place_ids.add(task_info['kwargs']['place_id'])
        assert task_info['kwargs']['s3_path'] == s3_path
    assert not stq.eats_nomenclature_viewer_update_vendor_data.has_calls
    assert place_ids == {1, 2}
