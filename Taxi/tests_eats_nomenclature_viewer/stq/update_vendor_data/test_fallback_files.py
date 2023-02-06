import datetime as dt

import pytest
import pytz

from tests_eats_nomenclature_viewer.stq.update_vendor_data import constants
from tests_eats_nomenclature_viewer import models
from tests_eats_nomenclature_viewer import utils

S3_PATH = '/some_path.json'
OLD_TIME = dt.datetime(2019, 3, 2, 12, tzinfo=pytz.UTC)
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=['brand.sql', 'place.sql', 'product_for_data_template.sql'],
)
async def test_insert(test_utils, load, sql):
    now = utils.now_with_tz()
    expected_fallback_file = models.PlaceFallbackFile(
        place_id=constants.PLACE_ID,
        task_type=models.PlaceTaskType.VENDOR_DATA,
        file_path=f'{constants.FALLBACK_FILES_DIR}/{constants.PLACE_ID}.json',
        file_datetime=dt.datetime(2019, 3, 2, 12, tzinfo=pytz.UTC),
    )

    await test_utils.store_data_and_call_stq_update_vendor_data(
        path=S3_PATH,
        data=load('single_object_data_template.json').encode('utf-8'),
        place_id=expected_fallback_file.place_id,
        file_datetime=expected_fallback_file.file_datetime,
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
async def test_update_new_file(test_utils, load, sql):
    place_id_1 = sql.save(models.Place(brand_id=constants.BRAND_ID))
    place_id_2 = sql.save(models.Place(brand_id=constants.BRAND_ID))

    place_fallback_file_1 = models.PlaceFallbackFile(
        place_id=place_id_1,
        task_type=models.PlaceTaskType.VENDOR_DATA,
        file_path=f'{constants.FALLBACK_FILES_DIR}/{place_id_1}.json',
        file_datetime=OLD_TIME,
        updated_at=OLD_TIME,
    )
    place_fallback_file_2 = models.PlaceFallbackFile(
        place_id=place_id_2,
        task_type=models.PlaceTaskType.VENDOR_DATA,
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

    await test_utils.store_data_and_call_stq_update_vendor_data(
        path=S3_PATH,
        data=load('single_object_data_template.json').encode('utf-8'),
        place_id=expected_fallback_file.place_id,
        file_datetime=expected_fallback_file.file_datetime,
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
async def test_update_ignore_old_file(test_utils, load, sql):
    old_time = OLD_TIME
    new_time = old_time + dt.timedelta(hours=2)

    place_fallback_file = models.PlaceFallbackFile(
        place_id=constants.BRAND_ID,
        task_type=models.PlaceTaskType.VENDOR_DATA,
        file_path=f'{constants.FALLBACK_FILES_DIR}/{constants.BRAND_ID}.json',
        file_datetime=new_time,
        updated_at=new_time,
    )
    sql.save(place_fallback_file)

    await test_utils.store_data_and_call_stq_update_vendor_data(
        path=S3_PATH,
        data=load('single_object_data_template.json').encode('utf-8'),
        place_id=place_fallback_file.place_id,
        file_datetime=old_time,
    )

    db_place_fallback_files = sql.load_all(models.PlaceFallbackFile)
    assert db_place_fallback_files == [place_fallback_file]
