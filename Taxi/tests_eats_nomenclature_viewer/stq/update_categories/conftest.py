import datetime as dt
import json

import pytest
import pytz


class TestUtils:
    def __init__(self, stq_runner, mds_s3_storage):
        self._stq_runner = stq_runner
        self._mds_s3_storage = mds_s3_storage

    async def store_data_and_call_stq_update_categories(
            self, data, path, brand_id, place_ids, assortment_name='partner',
    ):  # pylint: disable=C0103
        if isinstance(data, dict):
            data = json.dumps(data).encode('utf-8')
        self._mds_s3_storage.put_object(path, data)

        await self._stq_runner.eats_nomenclature_viewer_update_categories.call(
            task_id='1',
            kwargs={
                's3_path': path,
                'assortment_name': assortment_name,
                'brand_id': brand_id,
                'place_ids': place_ids,
                'file_datetime': (
                    dt.datetime.now()
                    .replace(microsecond=0)
                    .astimezone(pytz.UTC)
                    .isoformat()
                ),
            },
        )


@pytest.fixture
def nmn_test_utils(stq_runner, mds_s3_storage):
    return TestUtils(stq_runner, mds_s3_storage)
