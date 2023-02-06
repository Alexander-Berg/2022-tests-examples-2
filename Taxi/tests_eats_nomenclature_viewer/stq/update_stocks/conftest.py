import datetime as dt
import json

import pytest
import pytz

from tests_eats_nomenclature_viewer import models


class TestUtils:
    def __init__(self, stq_runner, sql, mds_s3_storage):
        self._stq_runner = stq_runner
        self._mds_s3_storage = mds_s3_storage
        self._sql = sql

    async def store_data_and_call_stq_update_stocks(
            self, path, data, place_id, file_datetime=None,
    ):  # pylint: disable=C0103
        if isinstance(data, dict):
            data = json.dumps(data).encode('utf-8')
        if not file_datetime:
            file_datetime = (
                dt.datetime.now().replace(microsecond=0).astimezone(pytz.UTC)
            )

        self._mds_s3_storage.put_object(path, data)
        await self._stq_runner.eats_nomenclature_viewer_update_stocks.call(  # noqa: E501
            task_id='1',
            kwargs={
                'place_id': place_id,
                's3_path': path,
                'file_datetime': file_datetime.isoformat(),
            },
        )

    def save_availability_data(self, place_id, data):
        if isinstance(data, dict):
            data = json.dumps(data).encode('utf-8')

        availability_file = models.PlaceAvailabilityFile(place_id=place_id)
        self._sql.save(availability_file)
        self._mds_s3_storage.put_object(availability_file.file_path, data)


@pytest.fixture
def test_utils(stq_runner, sql, mds_s3_storage):
    return TestUtils(stq_runner, sql, mds_s3_storage)
