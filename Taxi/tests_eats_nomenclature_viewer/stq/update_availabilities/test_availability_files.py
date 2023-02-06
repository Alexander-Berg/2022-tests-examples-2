import datetime as dt

import pytest
import pytz

from tests_eats_nomenclature_viewer import models
from tests_eats_nomenclature_viewer import utils
from tests_eats_nomenclature_viewer.stq.update_stocks import constants

S3_AVAILABILITY_FILE = '/some_path.json'
OLD_TIME = dt.datetime(2019, 3, 2, 12, tzinfo=pytz.UTC)
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.pgsql(
    'eats_nomenclature_viewer', files=['brand.sql', 'place.sql'],
)
async def test_insert(stq_runner, load, mds_s3_storage, sql):
    now = utils.now_with_tz()
    expected_availability_file = models.PlaceAvailabilityFile(
        place_id=constants.PLACE_ID,
        file_path=S3_AVAILABILITY_FILE,
        file_datetime=dt.datetime(2019, 3, 2, 12, tzinfo=pytz.UTC),
    )

    mds_s3_storage.put_object(
        S3_AVAILABILITY_FILE,
        load('availability_file_sample.json').encode('utf-8'),
    )
    await stq_runner.eats_nomenclature_viewer_update_availabilities.call(
        task_id='1',
        kwargs={
            's3_path': expected_availability_file.file_path,
            'place_id': expected_availability_file.place_id,
            'file_datetime': (
                expected_availability_file.file_datetime.isoformat()
            ),
        },
    )

    db_place_availability_files = sql.load_all(models.PlaceAvailabilityFile)
    assert len(db_place_availability_files) == 1
    db_place_availability_file = db_place_availability_files[0]

    assert db_place_availability_file.updated_at >= now
    db_place_availability_file.updated_at = None
    assert db_place_availability_file == expected_availability_file


@pytest.mark.pgsql('eats_nomenclature_viewer', files=['brand.sql'])
async def test_update_new_file(stq_runner, load, mds_s3_storage, sql):
    place_id_1 = sql.save(models.Place(brand_id=constants.BRAND_ID))
    place_id_2 = sql.save(models.Place(brand_id=constants.BRAND_ID))

    place_availability_file_1 = models.PlaceAvailabilityFile(
        place_id=place_id_1,
        file_path='path_1.json',
        file_datetime=OLD_TIME,
        updated_at=OLD_TIME,
    )
    place_availability_file_2 = models.PlaceAvailabilityFile(
        place_id=place_id_2,
        file_path='path_2.json',
        file_datetime=OLD_TIME,
        updated_at=OLD_TIME,
    )
    sql.save(place_availability_file_1)
    sql.save(place_availability_file_2)

    new_time = OLD_TIME + dt.timedelta(hours=4)
    new_path = S3_AVAILABILITY_FILE
    expected_availability_file = place_availability_file_2.clone()
    expected_availability_file.updated_at = None
    expected_availability_file.file_path = new_path
    expected_availability_file.file_datetime = new_time

    mds_s3_storage.put_object(
        expected_availability_file.file_path,
        load('availability_file_sample.json').encode('utf-8'),
    )
    await stq_runner.eats_nomenclature_viewer_update_availabilities.call(
        task_id='1',
        kwargs={
            's3_path': expected_availability_file.file_path,
            'place_id': expected_availability_file.place_id,
            'file_datetime': (
                expected_availability_file.file_datetime.isoformat()
            ),
        },
    )

    db_place_availability_files = {
        i.place_id: i for i in sql.load_all(models.PlaceAvailabilityFile)
    }
    assert len(db_place_availability_files) == 2
    db_place_availability_file_1 = db_place_availability_files[
        place_availability_file_1.place_id
    ]
    db_place_availability_file_2 = db_place_availability_files[
        place_availability_file_2.place_id
    ]

    assert db_place_availability_file_1 == place_availability_file_1
    assert (
        db_place_availability_file_2.updated_at
        > place_availability_file_2.updated_at
    )
    db_place_availability_file_2.updated_at = None
    assert db_place_availability_file_2 == expected_availability_file


@pytest.mark.pgsql(
    'eats_nomenclature_viewer', files=['brand.sql', 'place.sql'],
)
async def test_update_ignore_old_file(stq_runner, load, mds_s3_storage, sql):
    old_time = OLD_TIME
    new_time = old_time + dt.timedelta(hours=2)

    place_availability_file = models.PlaceAvailabilityFile(
        place_id=constants.BRAND_ID,
        file_path='old_path.json',
        file_datetime=new_time,
        updated_at=new_time,
    )
    sql.save(place_availability_file)

    mds_s3_storage.put_object(
        S3_AVAILABILITY_FILE,
        load('availability_file_sample.json').encode('utf-8'),
    )
    await stq_runner.eats_nomenclature_viewer_update_availabilities.call(
        task_id='1',
        kwargs={
            's3_path': S3_AVAILABILITY_FILE,
            'place_id': place_availability_file.place_id,
            'file_datetime': old_time.isoformat(),
        },
    )

    db_place_availability_files = sql.load_all(models.PlaceAvailabilityFile)
    assert db_place_availability_files == [place_availability_file]
