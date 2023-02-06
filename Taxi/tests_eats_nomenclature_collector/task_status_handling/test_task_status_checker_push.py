import datetime as dt
import json

import pytest
import pytz


CORE_INTEGRATIONS_HANDLER = (
    '/eats-core-integrations/integrations/nomenclature-collector/v1/tasks'
)
MOCK_NOW = dt.datetime(2021, 4, 1, 12, tzinfo=pytz.UTC)

BRAND_ID = '1'
PLACE_ID = '1'


@pytest.mark.parametrize(
    'brand_ids, place_ids, expected_task_ids',
    [
        pytest.param([], [], {'101', '102', '201'}),
        pytest.param([], ['101'], {'102', '201'}),
        pytest.param(['1'], [], {'201'}),
    ],
)
@pytest.mark.now(MOCK_NOW.isoformat())
async def test_push_model_brand_place(
        taxi_eats_nomenclature_collector,
        mock_eats_core_integrations,
        testpoint,
        sql_add_place_task_for_task_status_test,
        config_set_push_model,
        taxi_config,
        # parametrize params
        brand_ids,
        place_ids,
        expected_task_ids,
):
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_COLLECTOR_TASK_STATUS_CHECKERS_SETTINGS': {
                'period_in_sec': 60,
                'limit': 100,
                'brand_period_in_sec': 60,
                'batch_size': 10000,
            },
        },
    )
    config_set_push_model(brand_ids=brand_ids, place_ids=place_ids)

    _sql_add_place_task(
        sql_add_place_task_for_task_status_test,
        brand_id='1',
        place_id='101',
        task_id='101',
    )
    _sql_add_place_task(
        sql_add_place_task_for_task_status_test,
        brand_id='1',
        place_id='102',
        task_id='102',
    )
    _sql_add_place_task(
        sql_add_place_task_for_task_status_test,
        brand_id='2',
        place_id='201',
        task_id='201',
    )

    mock_eats_core_integrations()

    @testpoint('eats_nomenclature_collector::task-status-checker')
    def handle_finished(arg):
        pass

    tasks_to_update = set()

    @testpoint(
        'eats_nomenclature_collector::task-status-checker::tasks_to_update',
    )
    def tasks_to_update_point(arg):
        tasks_to_update.update(arg)

    await taxi_eats_nomenclature_collector.run_distlock_task(
        'task-status-checker',
    )
    handle_finished.next_call()
    assert tasks_to_update_point.has_calls

    assert tasks_to_update == expected_task_ids


@pytest.mark.parametrize(
    'sync_at, sync_timeout_in_sec, should_be_pulled',
    [
        pytest.param(MOCK_NOW - dt.timedelta(seconds=1000), 500, True),
        pytest.param(MOCK_NOW - dt.timedelta(seconds=250), 500, False),
    ],
)
@pytest.mark.now(MOCK_NOW.isoformat())
async def test_push_model_sync_timeout(
        taxi_eats_nomenclature_collector,
        mock_eats_core_integrations,
        testpoint,
        config_set_push_model,
        sql_add_place_task_for_task_status_test,
        taxi_config,
        # parametrize params
        sync_at,
        sync_timeout_in_sec,
        should_be_pulled,
):
    place_id = PLACE_ID

    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_COLLECTOR_TASK_STATUS_CHECKERS_SETTINGS': {
                'period_in_sec': 60,
                'limit': 100,
                'brand_period_in_sec': 60,
                'batch_size': 10000,
                'per_brand_push_model_synchronized_at_timeout': {
                    '__default__': {
                        'nomenclature': sync_timeout_in_sec,
                        'price': sync_timeout_in_sec,
                        'stock': sync_timeout_in_sec,
                        'availability': sync_timeout_in_sec,
                    },
                },
            },
        },
    )
    config_set_push_model(brand_ids=[], place_ids=[place_id])

    _sql_add_place_task(
        sql_add_place_task_for_task_status_test, place_id='999', task_id='999',
    )
    _sql_add_place_task(
        sql_add_place_task_for_task_status_test,
        place_id=place_id,
        task_id='1',
        synced_at=sync_at.isoformat(),
    )

    mock_eats_core_integrations()

    @testpoint('eats_nomenclature_collector::task-status-checker')
    def handle_finished(arg):
        pass

    tasks_to_update = set()

    @testpoint(
        'eats_nomenclature_collector::task-status-checker::tasks_to_update',
    )
    def tasks_to_update_point(arg):
        tasks_to_update.update(arg)

    await taxi_eats_nomenclature_collector.run_distlock_task(
        'task-status-checker',
    )
    handle_finished.next_call()
    assert tasks_to_update_point.has_calls

    if should_be_pulled:
        assert tasks_to_update == {'999', '1'}
    else:
        assert tasks_to_update == {'999'}


@pytest.mark.parametrize(
    'task_type', ['nomenclature', 'price', 'stock', 'availability'],
)
@pytest.mark.now(MOCK_NOW.isoformat())
async def test_push_model_sync_timeout_by_task_type(
        taxi_eats_nomenclature_collector,
        mock_eats_core_integrations,
        testpoint,
        config_set_push_model,
        sql_add_place_task_for_task_status_test,
        taxi_config,
        # parametrize
        task_type,
):
    place_id = PLACE_ID
    sync_timeout_in_sec = 500
    sync_at = MOCK_NOW - dt.timedelta(seconds=sync_timeout_in_sec * 2)

    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_COLLECTOR_TASK_STATUS_CHECKERS_SETTINGS': {
                'period_in_sec': 60,
                'limit': 100,
                'brand_period_in_sec': 60,
                'batch_size': 10000,
                'per_brand_push_model_synchronized_at_timeout': {
                    '__default__': {
                        'nomenclature': (
                            sync_timeout_in_sec
                            if task_type == 'nomenclature'
                            else sync_timeout_in_sec * 100
                        ),
                        'price': (
                            sync_timeout_in_sec
                            if task_type == 'price'
                            else sync_timeout_in_sec * 100
                        ),
                        'stock': (
                            sync_timeout_in_sec
                            if task_type == 'stock'
                            else sync_timeout_in_sec * 100
                        ),
                        'availability': (
                            sync_timeout_in_sec
                            if task_type == 'availability'
                            else sync_timeout_in_sec * 100
                        ),
                    },
                },
            },
        },
    )
    config_set_push_model(brand_ids=[], place_ids=[place_id])

    _sql_add_place_task(
        sql_add_place_task_for_task_status_test,
        place_id=place_id,
        task_id='nomenclature',
        task_type='nomenclature',
        synced_at=sync_at.isoformat(),
    )
    _sql_add_place_task(
        sql_add_place_task_for_task_status_test,
        place_id=place_id,
        task_id='price',
        task_type='price',
        synced_at=sync_at.isoformat(),
    )
    _sql_add_place_task(
        sql_add_place_task_for_task_status_test,
        place_id=place_id,
        task_id='stock',
        task_type='stock',
        synced_at=sync_at.isoformat(),
    )
    _sql_add_place_task(
        sql_add_place_task_for_task_status_test,
        place_id=place_id,
        task_id='availability',
        task_type='availability',
        synced_at=sync_at.isoformat(),
    )

    mock_eats_core_integrations()

    @testpoint('eats_nomenclature_collector::task-status-checker')
    def handle_finished(arg):
        pass

    tasks_to_update = set()

    @testpoint(
        'eats_nomenclature_collector::task-status-checker::tasks_to_update',
    )
    def tasks_to_update_point(arg):
        tasks_to_update.update(arg)

    await taxi_eats_nomenclature_collector.run_distlock_task(
        'task-status-checker',
    )
    handle_finished.next_call()
    assert tasks_to_update_point.has_calls

    assert tasks_to_update == {task_type}


def _sql_add_place_task(
        sql_add_place_task_for_task_status_test,
        task_id,
        place_id=PLACE_ID,
        brand_id=BRAND_ID,
        task_type='nomenclature',
        synced_at=MOCK_NOW.isoformat(),
):
    sql_add_place_task_for_task_status_test(
        task_id=task_id,
        place_id=place_id,
        brand_id=brand_id,
        task_type=task_type,
        synced_at=synced_at,
        status='created',
    )


@pytest.fixture(name='mock_eats_core_integrations')
def _mock_eats_core_integrations(mockserver):
    def impl():
        @mockserver.json_handler(CORE_INTEGRATIONS_HANDLER)
        def _handler(request):
            return mockserver.make_response(
                json.dumps(
                    {
                        'errors': [
                            {'code': '404', 'message': 'Task not found.'},
                        ],
                    },
                ),
                404,
            )

        return _handler

    return impl
