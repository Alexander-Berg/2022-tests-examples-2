import datetime as dt

import pytest
import pytz


QUEUE_NAME = 'eats_nomenclature_collector_task_status_updater'

MOCK_NOW = dt.datetime(2021, 4, 1, 12, tzinfo=pytz.UTC)

BRAND_ID = '1'
PLACE_ID = '1'


@pytest.mark.parametrize(
    'config_brand_ids, config_place_ids, should_process',
    [
        pytest.param([], [PLACE_ID], True),
        pytest.param([BRAND_ID], [], True),
        pytest.param([], [], False),
    ],
)
@pytest.mark.now(MOCK_NOW.isoformat())
async def test_push_model_config(
        testpoint,
        sql_add_place_task_for_task_status_test,
        config_set_push_model,
        stq_enqueue_and_call,
        # parametrize params
        config_brand_ids,
        config_place_ids,
        should_process,
):
    config_set_push_model(
        brand_ids=config_brand_ids, place_ids=config_place_ids,
    )

    task_id = PLACE_ID

    _sql_add_place_task(
        sql_add_place_task_for_task_status_test,
        task_id=task_id,
        brand_id=BRAND_ID,
        place_id=PLACE_ID,
    )

    @testpoint(
        f'eats-nomenclature-collector::{QUEUE_NAME}::has_task_to_process',
    )
    def _has_task_to_process(param):
        pass

    kwargs = {
        'place_id': PLACE_ID,
        'integration_task_id': task_id,
        'integration_task_type': 'nomenclature',
        'status': 'created',
    }

    await stq_enqueue_and_call(QUEUE_NAME, task_id=task_id, kwargs=kwargs)

    assert _has_task_to_process.has_calls == should_process


def _sql_add_place_task(
        sql_add_place_task_for_task_status_test,
        task_id,
        place_id=PLACE_ID,
        brand_id=BRAND_ID,
):
    sql_add_place_task_for_task_status_test(
        task_id=task_id,
        place_id=place_id,
        brand_id=brand_id,
        task_type='nomenclature',
        synced_at=MOCK_NOW.isoformat(),
        status='created',
    )
