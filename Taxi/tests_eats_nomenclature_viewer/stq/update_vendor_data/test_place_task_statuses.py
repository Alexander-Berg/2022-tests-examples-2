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
    expected_task_status = models.PlaceTaskStatus(
        place_id=constants.PLACE_ID,
        task_type=models.PlaceTaskType.VENDOR_DATA,
        task_is_in_progress=False,
    )

    await test_utils.store_data_and_call_stq_update_vendor_data(
        path=S3_PATH,
        data=load('single_object_data_template.json').encode('utf-8'),
        place_id=expected_task_status.place_id,
    )

    db_place_task_statuses = sql.load_all(models.PlaceTaskStatus)
    assert len(db_place_task_statuses) == 1
    db_place_task_status = db_place_task_statuses[0]

    assert db_place_task_status.updated_at >= now
    assert db_place_task_status.task_started_at >= now
    assert db_place_task_status.task_finished_at >= now
    db_place_task_status.updated_at = None
    db_place_task_status.task_started_at = None
    db_place_task_status.task_finished_at = None

    assert db_place_task_status == expected_task_status


@pytest.mark.parametrize(**utils.gen_bool_params('is_outdated'))
@pytest.mark.parametrize(**utils.gen_bool_params('is_in_progress'))
@pytest.mark.pgsql(
    'eats_nomenclature_viewer',
    files=['brand.sql', 'place.sql', 'product_for_data_template.sql'],
)
async def test_update_in_progress(
        test_utils,
        load,
        sql,
        update_taxi_config,
        # parametrize
        is_outdated,
        is_in_progress,
):
    outdated_in_progress_treshold = dt.timedelta(minutes=30)
    update_taxi_config(
        'EATS_NOMENCLATURE_VIEWER_PLACE_TASK_TIMEOUTS',
        {
            '__default__': {
                'in_progress_task_timeout_in_ms': (
                    outdated_in_progress_treshold.seconds * 1000
                ),
            },
        },
    )

    task_started_at = utils.now_with_tz()
    if is_outdated and is_in_progress:
        task_started_at -= outdated_in_progress_treshold * 2

    old_task_status = models.PlaceTaskStatus(
        place_id=constants.PLACE_ID,
        task_type=models.PlaceTaskType.VENDOR_DATA,
        task_is_in_progress=is_in_progress,
        task_started_at=task_started_at,
        task_finished_at=OLD_TIME,
        updated_at=OLD_TIME,
    )
    sql.save(old_task_status)

    await test_utils.store_data_and_call_stq_update_vendor_data(
        path=S3_PATH,
        data=load('single_object_data_template.json').encode('utf-8'),
        place_id=old_task_status.place_id,
    )

    db_task_statuses = sql.load_all(models.PlaceTaskStatus)
    assert len(db_task_statuses) == 1
    db_task_status = db_task_statuses[0]

    if is_in_progress and not is_outdated:
        assert db_task_status == old_task_status
    else:
        assert not db_task_status.task_is_in_progress
        assert db_task_status.updated_at > old_task_status.updated_at
        assert db_task_status.task_started_at > old_task_status.task_started_at
        assert (
            db_task_status.task_finished_at > old_task_status.task_finished_at
        )
