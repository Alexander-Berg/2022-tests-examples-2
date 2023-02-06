import pytest

SCHEDULING_SETTINGS = {
    '100': {
        '223': {
            'RUS': {
                'yandex_taxi': 2,
                '$meta': {'solomon_children_labels': 'delivery_type'},
            },
            '$meta': {'solomon_children_labels': 'country_iso3'},
        },
        '$meta': {'solomon_children_labels': 'region_id'},
    },
    '1': {
        '223': {
            'RUS': {
                'yandex_taxi': 2,
                '$meta': {'solomon_children_labels': 'delivery_type'},
            },
            '$meta': {'solomon_children_labels': 'country_iso3'},
        },
        '$meta': {'solomon_children_labels': 'region_id'},
    },
    '2': {
        '223': {
            'RUS': {
                'yandex_taxi': 2,
                '$meta': {'solomon_children_labels': 'delivery_type'},
            },
            '$meta': {'solomon_children_labels': 'country_iso3'},
        },
        '$meta': {'solomon_children_labels': 'region_id'},
    },
    '$meta': {'solomon_children_labels': 'depot_id'},
}

MISSED_PIPELINE_DELIVERY_TYPE = {
    '1': {
        '223': {
            'RUS': {
                'yandex_taxi_night': 4,
                '$meta': {'solomon_children_labels': 'delivery_type'},
            },
            '$meta': {'solomon_children_labels': 'country_iso3'},
        },
        '$meta': {'solomon_children_labels': 'region_id'},
    },
    '$meta': {'solomon_children_labels': 'depot_id'},
}


@pytest.mark.config(
    GROCERY_SURGE_PIPELINE_METRICS={
        'use_metric_logging': True,
        'used_pipeline_names': ['calc_surge'],
        'use_depot_id_filter': True,
        'used_depot_ids': ['1'],
    },
)
@pytest.mark.experiments3(
    name='grocery_surge_js_pipeline_schedule',
    consumers=['grocery_surge/js_pipeline_scheduler'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'pipelines': [{'period': 15, 'pipeline': 'calc_surge'}]},
    is_config=True,
)
async def test_surge_writer(
        taxi_grocery_surge,
        pgsql,
        stq,
        stq_runner,
        taxi_grocery_surge_monitor,
        solomon_agent,
):
    await taxi_grocery_surge.tests_control(reset_metrics=True)

    task_id = 'task_id'
    for depot_id in ('1', '2', '100'):
        await stq_runner.grocery_surge_calculate_pipeline.call(
            task_id=task_id,
            kwargs={'pipeline': 'calc_surge', 'depot_id': depot_id},
        )

    assert stq.grocery_surge_calculate_pipeline.times_called == 3

    cursor = pgsql['grocery-surge'].cursor()

    cursor.execute(
        'SELECT pipeline, depot_id, load_level FROM surge.calculated;',
    )

    def sort_key(x):
        return x[1]

    db_payload = list(sorted(cursor, key=sort_key))
    expected_payload = [
        ('calc_surge', '1', 12.3),
        ('calc_surge', '100', 12.3),
        ('calc_surge', '2', 12.3),
    ]
    assert expected_payload == db_payload

    statistics = await taxi_grocery_surge_monitor.get_metric('surge_metrics')

    assert statistics['calculated_js_pipelines'] == 3
    assert (
        'calc_surge' not in statistics['failed_js_calculations_per_pipeline']
    )
    assert solomon_agent.times_called() == 1


@pytest.mark.experiments3(
    name='grocery_surge_js_pipeline_schedule',
    consumers=['grocery_surge/js_pipeline_scheduler'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'pipelines': [{'period': 15, 'pipeline': 'calc_surge'}]},
    is_config=True,
)
@pytest.mark.experiments3(
    name='grocery_surge_delivery_type_to_js_pipeline_matching',
    consumers=['grocery_surge/js_pipeline_calculator'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'init': {
                    'arg_name': 'delivery_type',
                    'set_elem_type': 'string',
                    'set': ['pedestrian', 'yandex_taxi'],
                },
                'type': 'in_set',
            },
            'value': {'pipeline': 'calc_surge'},
        },
    ],
    is_config=True,
)
async def test_delivery_types_written(pgsql, stq, stq_runner):
    task_id = 'task_id'
    for depot_id in ('1', '2'):
        await stq_runner.grocery_surge_calculate_pipeline.call(
            task_id=task_id,
            kwargs={'pipeline': 'calc_surge', 'depot_id': depot_id},
        )

    assert stq.grocery_surge_calculate_pipeline.times_called == 2

    cursor = pgsql['grocery-surge'].cursor()

    cursor.execute(
        'SELECT pipeline, depot_id, delivery_types FROM surge.calculated;',
    )

    db_payload = list(sorted(cursor))
    expected_payload = [
        ('calc_surge', '1', ['pedestrian', 'yandex_taxi']),
        ('calc_surge', '2', ['pedestrian', 'yandex_taxi']),
    ]
    assert expected_payload == db_payload


@pytest.mark.experiments3(
    name='grocery_surge_js_pipeline_schedule',
    consumers=['grocery_surge/js_pipeline_scheduler'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'pipelines': [{'period': 15, 'pipeline': 'test_pipeline'}]},
    is_config=True,
)
@pytest.mark.experiments3(
    name='grocery_surge_delivery_type_to_js_pipeline_matching',
    consumers=['grocery_surge/js_pipeline_calculator'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'init': {
                    'arg_name': 'delivery_type',
                    'set_elem_type': 'string',
                    'set': ['pedestrian', 'yandex_taxi'],
                },
                'type': 'in_set',
            },
            'value': {'pipeline': 'calc_surge'},
        },
    ],
    is_config=True,
)
@pytest.mark.config(
    GROCERY_SURGE_PIPELINE_METRICS={
        'use_metric_logging': True,
        'used_pipeline_names': ['calc_surge'],
        'use_depot_id_filter': True,
        'used_depot_ids': ['1'],
    },
)
async def test_lost_scheduling_settings(
        taxi_grocery_surge, stq_runner, taxi_grocery_surge_monitor,
):
    await taxi_grocery_surge.tests_control(reset_metrics=True)

    task_id = 'task_id'
    for depot_id in ('1', '2', '100'):
        await stq_runner.grocery_surge_calculate_pipeline.call(
            task_id=task_id,
            kwargs={'pipeline': 'calc_surge', 'depot_id': depot_id},
        )

    statistics = await taxi_grocery_surge_monitor.get_metric('surge_metrics')

    assert statistics['scheduling_settings_not_found'] == SCHEDULING_SETTINGS


@pytest.mark.experiments3(
    name='grocery_surge_js_pipeline_schedule',
    consumers=['grocery_surge/js_pipeline_scheduler'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'pipelines': [{'period': 15, 'pipeline': 'test_pipeline'}]},
    is_config=True,
)
@pytest.mark.config(
    GROCERY_SURGE_PIPELINE_METRICS={
        'use_metric_logging': True,
        'used_pipeline_names': ['calc_surge'],
        'use_depot_id_filter': True,
        'used_depot_ids': ['1'],
    },
)
async def test_missed_js_pipeline_for_delivery_type(
        taxi_grocery_surge, stq_runner, taxi_grocery_surge_monitor,
):
    await taxi_grocery_surge.tests_control(reset_metrics=True)

    task_id = 'task_id'

    await stq_runner.grocery_surge_calculate_pipeline.call(
        task_id=task_id, kwargs={'pipeline': 'calc_surge', 'depot_id': '1'},
    )

    statistics = await taxi_grocery_surge_monitor.get_metric('surge_metrics')

    assert (
        statistics['missed_js_pipeline_for_delivery_type']
        == MISSED_PIPELINE_DELIVERY_TYPE
    )
