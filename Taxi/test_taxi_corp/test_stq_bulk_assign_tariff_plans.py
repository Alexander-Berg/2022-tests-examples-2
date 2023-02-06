import datetime

import pytest
import pytz

from taxi.stq.async_worker_old import TaskInfo

from taxi_corp.stq import bulk_assign_tariff_plans


NOW = datetime.datetime.utcnow().replace(microsecond=0, tzinfo=pytz.utc)


def days(_days: int):
    return datetime.timedelta(_days)


@pytest.mark.parametrize(
    ['task_info', 'payload', 'result', 'created_ctps'],
    [
        pytest.param(
            {
                'id': 'long_operation_1',
                'exec_tries': 0,
                'reschedule_counter': 0,
            },
            {
                'tariff_plan_series_id': 'tariff_plan_series_id_1',
                'service': 'taxi',
                'since': (NOW + days(1)).isoformat(),
                'client_ids': ['client_id_2'],
            },
            'long_tasks_valid_case.json',
            1,
            id='valid case',
        ),
        pytest.param(
            {
                'id': 'long_operation_1',
                'exec_tries': 0,
                'reschedule_counter': 0,
            },
            {
                'tariff_plan_series_id': 'non_existent_tp',
                'service': 'taxi',
                'since': (NOW + days(1)).isoformat(),
                'client_ids': ['client_id_2'],
            },
            'long_tasks_nonexistent_tp.json',
            0,
            id='non existent tariff plan',
        ),
        pytest.param(
            {
                'id': 'long_operation_1',
                'exec_tries': 0,
                'reschedule_counter': 0,
            },
            {
                'tariff_plan_series_id': 'tariff_plan_series_id_1',
                'service': 'taxi',
                'since': (NOW + days(1)).isoformat(),
                'client_ids': ['nonexistent_client', 'client_id_2'],
            },
            'long_tasks_nonexistent_client.json',
            0,
            id='non existent client',
        ),
        pytest.param(
            {
                'id': 'long_operation_1',
                'exec_tries': 5,
                'reschedule_counter': 0,
            },
            {
                'tariff_plan_series_id': 'tariff_plan_series_id_1',
                'service': 'taxi',
                'since': (NOW + days(1)).isoformat(),
                'client_ids': ['nonexistent_client', 'client_id_2'],
            },
            'long_tasks_exec_tries_exceeded.json',
            0,
            id='exec tries exceeded',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_bulk_validation(
        db,
        taxi_corp_app_stq,
        payload,
        task_info,
        result,
        load_json,
        created_ctps,
):
    await bulk_assign_tariff_plans.assign_tariff_plans(
        taxi_corp_app_stq,
        TaskInfo(
            id=task_info['id'],
            exec_tries=task_info['exec_tries'],
            reschedule_counter=task_info['reschedule_counter'],
        ),
        payload,
    )
    long_task = await db.corp_long_tasks.find_one({'_id': task_info['id']})
    expected = load_json(result)

    assert long_task['status'] == expected['status']
    assert long_task['idempotency_token'] == expected['idempotency_token']
    assert long_task.get('response_data') == expected.get('response_data')
    assert long_task.get('error_code') == expected.get('error_code')

    client_tariff_plans_count = await db.corp_client_tariff_plans.count(
        {'client_id': 'client_id_2'},
    )
    assert client_tariff_plans_count == created_ctps


@pytest.mark.now(NOW.isoformat())
async def test_bulk_apply_create(db, taxi_corp_app_stq):
    date_from = NOW
    data = {
        'tariff_plan_series_id': 'tariff_plan_series_id_1',
        'service': 'taxi',
        'since': date_from.isoformat(),
        'client_ids': ['client_id_2'],
    }
    await bulk_assign_tariff_plans.assign_tariff_plans(
        taxi_corp_app_stq,
        TaskInfo(id='some_id', exec_tries=0, reschedule_counter=0),
        data,
    )

    new_client_plan = await db.corp_client_tariff_plans.find_one(
        {'client_id': 'client_id_2'}, projection={'_id': False},
    )
    assert new_client_plan == {
        'client_id': 'client_id_2',
        'service': 'taxi',
        'tariff_plan_series_id': 'tariff_plan_series_id_1',
        'date_from': date_from.replace(tzinfo=None),
        'date_to': None,
        'created': NOW.replace(tzinfo=None),
        'updated': NOW.replace(tzinfo=None),
    }
