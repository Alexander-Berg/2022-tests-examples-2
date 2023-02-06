import datetime as dt
import json

import pytest
import pytz


class TestUtils:
    def __init__(self, stq_runner, mds_s3_storage):
        self._stq_runner = stq_runner
        self._mds_s3_storage = mds_s3_storage

    async def store_data_and_call_stq_update_vendor_data(
            self, path, data, place_id, file_datetime=None,
    ):  # pylint: disable=C0103
        if isinstance(data, dict):
            data = json.dumps(data).encode('utf-8')
        if not file_datetime:
            file_datetime = (
                dt.datetime.now().replace(microsecond=0).astimezone(pytz.UTC)
            )

        self._mds_s3_storage.put_object(path, data)
        await self._stq_runner.eats_nomenclature_viewer_update_vendor_data.call(  # noqa: E501
            task_id='1',
            kwargs={
                'place_id': place_id,
                's3_path': path,
                'file_datetime': file_datetime.isoformat(),
            },
        )


@pytest.fixture
def test_utils(stq_runner, mds_s3_storage):
    return TestUtils(stq_runner, mds_s3_storage)
