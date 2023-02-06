import datetime as dt
import json

import pytest
import pytz


class TestUtils:
    def __init__(self, stq_runner, mds_s3_storage):
        self._stq_runner = stq_runner
        self._mds_s3_storage = mds_s3_storage

    async def store_data_and_call_stq_update_prices(
            self, path, data, place_id,
    ):  # pylint: disable=C0103
        self._mds_s3_storage.put_object(path, json.dumps(data).encode('utf-8'))
        await self._stq_runner.eats_nomenclature_viewer_update_prices.call(
            task_id='1',
            kwargs={
                'place_id': place_id,
                's3_path': path,
                'file_datetime': (
                    dt.datetime.now()
                    .replace(microsecond=0)
                    .astimezone(pytz.UTC)
                    .isoformat()
                ),
            },
        )


@pytest.fixture
def test_utils(stq_runner, mds_s3_storage):
    return TestUtils(stq_runner, mds_s3_storage)
