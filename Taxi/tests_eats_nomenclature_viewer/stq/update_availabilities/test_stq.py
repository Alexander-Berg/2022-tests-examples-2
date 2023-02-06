import datetime as dt

import pytest
import pytz

from tests_eats_nomenclature_viewer.stq.update_availabilities import constants
from tests_eats_nomenclature_viewer import models

S3_AVAILABILITY_FILE = '/some_path.json'
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)


async def test_unknown_place(stq_runner, load, mds_s3_storage, sql):
    brand_id = sql.save(models.Brand())
    unknown_place = models.Place(brand_id=brand_id)

    mds_s3_storage.put_object(
        S3_AVAILABILITY_FILE,
        load('availability_file_sample.json').encode('utf-8'),
    )
    await stq_runner.eats_nomenclature_viewer_update_availabilities.call(
        task_id='1',
        kwargs={
            's3_path': S3_AVAILABILITY_FILE,
            'place_id': unknown_place.place_id,
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    assert not sql.load_all(models.PlaceTaskStatus)


@pytest.mark.pgsql(
    'eats_nomenclature_viewer', files=['brand.sql', 'place.sql'],
)
async def test_stq_error_limit(
        mds_s3_storage, load, stq_runner, testpoint, update_taxi_config,
):
    max_retries_on_error = 2
    update_taxi_config(
        'EATS_NOMENCLATURE_VIEWER_STQ_PROCESSING_V2',
        {'__default__': {'max_retries_on_error': max_retries_on_error}},
    )

    @testpoint(
        'eats-nomenclature-viewer_stq_update_availabilities::failure-injector',
    )
    def task_testpoint(_):
        return {'inject': True}

    mds_s3_storage.put_object(
        S3_AVAILABILITY_FILE,
        load('availability_file_sample.json').encode('utf-8'),
    )

    for i in range(max_retries_on_error):
        await stq_runner.eats_nomenclature_viewer_update_availabilities.call(
            task_id='1',
            kwargs={
                's3_path': S3_AVAILABILITY_FILE,
                'place_id': constants.PLACE_ID,
                'file_datetime': DEFAULT_TIME.isoformat(),
            },
            expect_fail=True,
            exec_tries=i,
        )

    # should succeed because of the error limit
    await stq_runner.eats_nomenclature_viewer_update_availabilities.call(
        task_id='1',
        kwargs={
            's3_path': S3_AVAILABILITY_FILE,
            'place_id': constants.PLACE_ID,
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )

    assert task_testpoint.has_calls
