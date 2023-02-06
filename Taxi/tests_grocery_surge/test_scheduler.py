import datetime

import pytest


@pytest.mark.now('2020-07-07T00:00:00Z')
@pytest.mark.experiments3(
    name='grocery_surge_js_pipeline_schedule',
    consumers=['grocery_surge/js_pipeline_scheduler'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set': ['1', '2'],
                    'arg_name': 'depot_id',
                    'set_elem_type': 'string',
                },
            },
            'title': 'test clause',
            'value': {
                'pipelines': [
                    {'period': 60, 'pipeline': 'pipeline1'},
                    {'period': 15, 'pipeline': 'pipeline2'},
                ],
            },
        },
    ],
    default_value={'pipelines': []},
    is_config=True,
)
async def test_watchdog_scheduling(
        taxi_grocery_surge, stq, stq_runner, mocked_time, mockserver,
):
    watchdog_period = 60
    await stq_runner.grocery_surge_calculator_watchdog.call(
        task_id='task_id', kwargs={'period': watchdog_period},
    )
    assert stq.grocery_surge_calculator_watchdog.times_called == 1
    assert stq.grocery_surge_calculator_watchdog.next_call() == {
        'args': None,
        'eta': mocked_time.now() + datetime.timedelta(seconds=watchdog_period),
        'id': 'task_id',
        'kwargs': None,
        'queue': 'grocery_surge_calculator_watchdog',
    }

    assert stq.grocery_surge_calculate_pipeline.times_called == 4

    def _check_task(task, depot_id, pipeline, eta_range):
        assert task['kwargs']['depot_id'] == depot_id
        assert task['kwargs']['pipeline'] == pipeline
        assert (
            mocked_time.now() + datetime.timedelta(seconds=eta_range[0])
            <= task['eta']
        )
        assert (
            mocked_time.now() + datetime.timedelta(seconds=eta_range[1])
            > task['eta']
        )

    _check_task(
        stq.grocery_surge_calculate_pipeline.next_call(),
        '1',
        'pipeline2',
        [15, 30],
    )
    _check_task(
        stq.grocery_surge_calculate_pipeline.next_call(),
        '1',
        'pipeline1',
        [60, 120],
    )
    _check_task(
        stq.grocery_surge_calculate_pipeline.next_call(),
        '2',
        'pipeline2',
        [15, 30],
    )
    _check_task(
        stq.grocery_surge_calculate_pipeline.next_call(),
        '2',
        'pipeline1',
        [60, 120],
    )


@pytest.mark.now('2020-07-07T00:00:00Z')
@pytest.mark.experiments3(
    name='grocery_surge_js_pipeline_schedule',
    consumers=['grocery_surge/js_pipeline_scheduler'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set': ['1'],
                    'arg_name': 'depot_id',
                    'set_elem_type': 'string',
                },
            },
            'title': 'test clause',
            'value': {'pipelines': [{'period': 15, 'pipeline': 'calc_surge'}]},
        },
    ],
    default_value={'pipelines': []},
    is_config=True,
)
async def test_pipeline_rescheduling(
        taxi_grocery_surge, stq, stq_runner, mocked_time,
):
    task_id = 'task_id'
    await stq_runner.grocery_surge_calculate_pipeline.call(
        task_id=task_id, kwargs={'pipeline': 'calc_surge', 'depot_id': '1'},
    )
    assert stq.grocery_surge_calculate_pipeline.times_called == 1
    assert stq.grocery_surge_calculate_pipeline.next_call() == {
        'args': None,
        'eta': mocked_time.now() + datetime.timedelta(seconds=15),
        'id': 'task_id',
        'kwargs': None,
        'queue': 'grocery_surge_calculate_pipeline',
    }
