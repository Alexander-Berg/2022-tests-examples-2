import datetime as dt

import pytest
import pytz

from tests_eats_nomenclature_viewer.stq.update_prices import constants
from tests_eats_nomenclature_viewer import models
from tests_eats_nomenclature_viewer import utils

S3_PRICE_FILE = '/some_path.json'
OLD_TIME = dt.datetime(2019, 3, 2, 12, tzinfo=pytz.UTC)
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=['brand.sql', 'place.sql', 'product_for_data_template.sql'],
)
async def test_insert(stq_runner, load, mds_s3_storage, sql):
    now = utils.now_with_tz()
    expected_fallback_file = models.PlaceFallbackFile(
        place_id=constants.PLACE_ID,
        task_type=models.PlaceTaskType.PRICE,
        file_path=f'{constants.FALLBACK_FILES_DIR}/{constants.PLACE_ID}.json',
        file_datetime=dt.datetime(2019, 3, 2, 12, tzinfo=pytz.UTC),
    )

    mds_s3_storage.put_object(
        S3_PRICE_FILE,
        load('single_object_data_template.json').encode('utf-8'),
    )
    await stq_runner.eats_nomenclature_viewer_update_prices.call(
        task_id='1',
        kwargs={
            's3_path': S3_PRICE_FILE,
            'place_id': expected_fallback_file.place_id,
            'file_datetime': expected_fallback_file.file_datetime.isoformat(),
        },
    )

    db_place_fallback_files = sql.load_all(models.PlaceFallbackFile)
    assert len(db_place_fallback_files) == 1
    db_place_fallback_file = db_place_fallback_files[0]

    assert db_place_fallback_file.updated_at >= now
    db_place_fallback_file.updated_at = None
    assert db_place_fallback_file == expected_fallback_file


@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=['brand.sql', 'product_for_data_template.sql'],
)
async def test_update_new_file(stq_runner, load, mds_s3_storage, sql):
    place_id_1 = sql.save(models.Place(brand_id=constants.BRAND_ID))
    place_id_2 = sql.save(models.Place(brand_id=constants.BRAND_ID))

    place_fallback_file_1 = models.PlaceFallbackFile(
        place_id=place_id_1,
        task_type=models.PlaceTaskType.PRICE,
        file_path=f'{constants.FALLBACK_FILES_DIR}/{place_id_1}.json',
        file_datetime=OLD_TIME,
        updated_at=OLD_TIME,
    )
    place_fallback_file_2 = models.PlaceFallbackFile(
        place_id=place_id_2,
        task_type=models.PlaceTaskType.PRICE,
        file_path=f'{constants.FALLBACK_FILES_DIR}/{place_id_2}.json',
        file_datetime=OLD_TIME,
        updated_at=OLD_TIME,
    )
    sql.save(place_fallback_file_1)
    sql.save(place_fallback_file_2)

    new_time = OLD_TIME + dt.timedelta(hours=4)
    expected_fallback_file = place_fallback_file_2.clone()
    expected_fallback_file.updated_at = None
    expected_fallback_file.file_datetime = new_time

    mds_s3_storage.put_object(
        S3_PRICE_FILE,
        load('single_object_data_template.json').encode('utf-8'),
    )
    await stq_runner.eats_nomenclature_viewer_update_prices.call(
        task_id='1',
        kwargs={
            's3_path': S3_PRICE_FILE,
            'place_id': expected_fallback_file.place_id,
            'file_datetime': expected_fallback_file.file_datetime.isoformat(),
        },
    )

    db_place_fallback_files = {
        i.place_id: i for i in sql.load_all(models.PlaceFallbackFile)
    }
    assert len(db_place_fallback_files) == 2
    db_place_fallback_file_1 = db_place_fallback_files[
        place_fallback_file_1.place_id
    ]
    db_place_fallback_file_2 = db_place_fallback_files[
        place_fallback_file_2.place_id
    ]

    assert db_place_fallback_file_1 == place_fallback_file_1
    assert (
        db_place_fallback_file_2.updated_at > place_fallback_file_2.updated_at
    )
    db_place_fallback_file_2.updated_at = None
    assert db_place_fallback_file_2 == expected_fallback_file


@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=['brand.sql', 'place.sql', 'product_for_data_template.sql'],
)
async def test_update_ignore_old_file(stq_runner, load, mds_s3_storage, sql):
    old_time = OLD_TIME
    new_time = old_time + dt.timedelta(hours=2)

    place_fallback_file = models.PlaceFallbackFile(
        place_id=constants.BRAND_ID,
        task_type=models.PlaceTaskType.PRICE,
        file_path=f'{constants.FALLBACK_FILES_DIR}/{constants.BRAND_ID}.json',
        file_datetime=new_time,
        updated_at=new_time,
    )
    sql.save(place_fallback_file)

    mds_s3_storage.put_object(
        S3_PRICE_FILE,
        load('single_object_data_template.json').encode('utf-8'),
    )
    await stq_runner.eats_nomenclature_viewer_update_prices.call(
        task_id='1',
        kwargs={
            's3_path': S3_PRICE_FILE,
            'place_id': place_fallback_file.place_id,
            'file_datetime': old_time.isoformat(),
        },
    )

    db_place_fallback_files = sql.load_all(models.PlaceFallbackFile)
    assert db_place_fallback_files == [place_fallback_file]
