import datetime as dt

import pytest
import pytz

from tests_eats_nomenclature_viewer import models
from tests_eats_nomenclature_viewer import utils
from tests_eats_nomenclature_viewer.stq.update_stocks import constants

S3_STOCKS_PATH = '/stocks/some_path_1.json'
OLD_TIME = dt.datetime(2019, 3, 2, 12, tzinfo=pytz.UTC)
DEFAULT_TIME = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)


@pytest.mark.s3(files={S3_STOCKS_PATH: 'stock_item_template.json'})
@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=['brand.sql', 'place.sql', 'product_for_item_template.sql'],
)
async def test_insert(stq_runner, load, mds_s3_storage, sql):
    now = utils.now_with_tz()

    availability_file = models.PlaceAvailabilityFile(
        place_id=constants.PLACE_ID,
        file_datetime=dt.datetime(2019, 3, 2, 12, tzinfo=pytz.UTC),
    )
    sql.save(availability_file)
    mds_s3_storage.put_object(
        availability_file.file_path,
        load('availability_item_template.json').encode('utf-8'),
    )

    expected_fallback_file = models.PlaceFallbackFile(
        place_id=constants.PLACE_ID,
        task_type=models.PlaceTaskType.AVAILABILITY,
        file_path=f'{constants.FALLBACK_AVAILABILITY_DIR}/{constants.PLACE_ID}.json',  # noqa: E501
        file_datetime=dt.datetime(2019, 3, 2, 12, tzinfo=pytz.UTC),
    )

    await stq_runner.eats_nomenclature_viewer_update_stocks.call(
        task_id='1',
        kwargs={
            's3_path': S3_STOCKS_PATH,
            'place_id': expected_fallback_file.place_id,
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    db_fallback_files = _load_all_availability_fallbacks(sql)
    assert len(db_fallback_files) == 1
    db_fallback_file = db_fallback_files[0]

    assert db_fallback_file.updated_at >= now
    db_fallback_file.updated_at = None
    assert db_fallback_file == expected_fallback_file


@pytest.mark.s3(files={S3_STOCKS_PATH: 'stock_item_template.json'})
@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=['brand.sql', 'product_for_item_template.sql'],
)
async def test_update_new_file(stq_runner, load, mds_s3_storage, sql):
    old_time = OLD_TIME
    new_time = old_time + dt.timedelta(hours=4)

    place_id_1 = sql.save(models.Place(brand_id=constants.BRAND_ID))
    place_id_2 = sql.save(models.Place(brand_id=constants.BRAND_ID))

    availability_file_2 = models.PlaceAvailabilityFile(
        place_id=place_id_2, file_datetime=new_time,
    )
    sql.save(availability_file_2)
    mds_s3_storage.put_object(
        availability_file_2.file_path,
        load('availability_item_template.json').encode('utf-8'),
    )

    fallback_file_1 = models.PlaceFallbackFile(
        place_id=place_id_1,
        task_type=models.PlaceTaskType.AVAILABILITY,
        file_path=f'{constants.FALLBACK_AVAILABILITY_DIR}/{place_id_1}.json',
        file_datetime=old_time,
        updated_at=old_time,
    )
    fallback_file_2 = models.PlaceFallbackFile(
        place_id=place_id_2,
        task_type=models.PlaceTaskType.AVAILABILITY,
        file_path=f'{constants.FALLBACK_AVAILABILITY_DIR}/{place_id_2}.json',
        file_datetime=old_time,
        updated_at=old_time,
    )
    sql.save(fallback_file_1)
    sql.save(fallback_file_2)

    expected_fallback_file = fallback_file_2.clone()
    expected_fallback_file.updated_at = None
    expected_fallback_file.file_datetime = new_time

    await stq_runner.eats_nomenclature_viewer_update_stocks.call(
        task_id='1',
        kwargs={
            's3_path': S3_STOCKS_PATH,
            'place_id': expected_fallback_file.place_id,
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    db_fallback_files = {
        i.place_id: i for i in _load_all_availability_fallbacks(sql)
    }
    assert len(db_fallback_files) == 2
    db_fallback_file_1 = db_fallback_files[fallback_file_1.place_id]
    db_fallback_file_2 = db_fallback_files[fallback_file_2.place_id]

    assert db_fallback_file_1 == fallback_file_1
    assert db_fallback_file_2.updated_at > fallback_file_2.updated_at
    db_fallback_file_2.updated_at = None
    assert db_fallback_file_2 == expected_fallback_file


@pytest.mark.s3(files={S3_STOCKS_PATH: 'stock_item_template.json'})
@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=['brand.sql', 'place.sql', 'product_for_item_template.sql'],
)
async def test_update_ignore_old_file(stq_runner, load, mds_s3_storage, sql):
    old_time = OLD_TIME
    new_time = old_time + dt.timedelta(hours=2)

    availability_file = models.PlaceAvailabilityFile(
        place_id=constants.PLACE_ID, file_datetime=old_time,
    )
    sql.save(availability_file)
    mds_s3_storage.put_object(
        availability_file.file_path,
        load('availability_item_template.json').encode('utf-8'),
    )

    fallback_file = models.PlaceFallbackFile(
        place_id=constants.BRAND_ID,
        task_type=models.PlaceTaskType.AVAILABILITY,
        file_path=f'{constants.FALLBACK_AVAILABILITY_DIR}/{constants.BRAND_ID}.json',  # noqa: E501
        file_datetime=new_time,
        updated_at=new_time,
    )
    sql.save(fallback_file)

    await stq_runner.eats_nomenclature_viewer_update_stocks.call(
        task_id='1',
        kwargs={
            's3_path': S3_STOCKS_PATH,
            'place_id': fallback_file.place_id,
            'file_datetime': DEFAULT_TIME.isoformat(),
        },
    )

    db_fallback_files = _load_all_availability_fallbacks(sql)
    assert db_fallback_files == [fallback_file]


def _load_all_availability_fallbacks(sql):
    return [
        i
        for i in sql.load_all(models.PlaceFallbackFile)
        if i.task_type == models.PlaceTaskType.AVAILABILITY
    ]
