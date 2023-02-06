import pytest

from tests_subvention_schedule import utils


@pytest.mark.config(
    STATS_SETTINGS={
        'stats_queries_settings': {
            'count_descriptor_combinations': {'enabled': True},
            'count_empty_descriptors': {'enabled': True},
            'count_problematic_parameters': {'enabled': True},
            'count_schedule_items': {'enabled': True},
            'count_affected_descriptors': {'enabled': True},
            'count_affected_descriptors_update_time': {'enabled': True},
            'count_descriptors_update_time': {'enabled': True},
        },
    },
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': False, 'update_period': 100},
        'stats_fast': {'enabled': True, 'update_period': 100},
        'stats_slow': {'enabled': True, 'update_period': 100},
    },
)
@pytest.mark.parametrize(
    'original_db, expected_metrics',
    [
        (
            'single_rule_db.json',
            {
                'schedule_stats.moscow.item_count.average': 1,
                'schedule_stats.moscow.item_count.min': 1,
                'schedule_stats.moscow.item_count.max': 1,
                'schedule_stats.moscow.problematic_params.activities': 1,
                'schedule_stats.moscow.problematic_params.tags': 1,
                'schedule_stats.moscow.descriptor_combinations': 1,
                # descriptor_combinations_stats
                'schedule_stats.descriptor_combinations_stats.max': 1,
                'schedule_stats.descriptor_combinations_stats.min': 1,
                'schedule_stats.descriptor_combinations_stats.average': 1,
                # empty_descriptors
                'schedule_stats.number_of_empty_descriptors': 0,
                # affected_descriptors
                'schedule_stats.affected_descriptors.'
                'atomic_descriptors_count': 0,
                'schedule_stats.affected_descriptors.'
                'atomic_schedules_count': 0,
                'schedule_stats.affected_descriptors'
                '.atomic_total_update_time': 0,
                'schedule_stats.affected_descriptors'
                '.atomic_total_update_time_with_null_as_avg': 0,
                # update_times_by_zone
                'schedule_stats.moscow.update_times_by_zone.'
                'total_update_time': 1,
                'schedule_stats.moscow.update_times_by_zone'
                '.total_update_time_with_null_as_avg': 1,
                # misc
                'schedule_stats.update_job_lag': {'atomic_job': 0},
            },
        ),
        (
            'many_items_with_one_zone.json',
            {
                'schedule_stats.moscow.item_count.average': 3,
                'schedule_stats.moscow.item_count.min': 2,
                'schedule_stats.moscow.item_count.max': 3,
                'schedule_stats.moscow.problematic_params.activities': 1,
                'schedule_stats.moscow.problematic_params.tags': 2,
                'schedule_stats.moscow.descriptor_combinations': 2,
                # descriptor_combinations_stats
                'schedule_stats.descriptor_combinations_stats.max': 2,
                'schedule_stats.descriptor_combinations_stats.min': 2,
                'schedule_stats.descriptor_combinations_stats.average': 2,
                # empty_descriptors
                'schedule_stats.number_of_empty_descriptors': 0,
                # affected_descriptors
                'schedule_stats.affected_descriptors.'
                'atomic_descriptors_count': 0,
                'schedule_stats.affected_descriptors.'
                'atomic_schedules_count': 0,
                'schedule_stats.affected_descriptors'
                '.atomic_total_update_time': 0,
                'schedule_stats.affected_descriptors'
                '.atomic_total_update_time_with_null_as_avg': 0,
                # update_times_by_zone
                'schedule_stats.moscow.update_times_by_zone.'
                'total_update_time': 2,
                'schedule_stats.moscow.update_times_by_zone.'
                'total_update_time_with_null_as_avg': 2,
                # misc
                'schedule_stats.update_job_lag': {'atomic_job': 0},
            },
        ),
        (
            'many_items_with_many_zones.json',
            {
                # moscow
                'schedule_stats.moscow.item_count.average': 3,
                'schedule_stats.moscow.item_count.min': 2,
                'schedule_stats.moscow.item_count.max': 3,
                'schedule_stats.moscow.problematic_params.activities': 1,
                'schedule_stats.moscow.problematic_params.tags': 2,
                'schedule_stats.moscow.descriptor_combinations': 2,
                # almaty
                'schedule_stats.almaty.item_count.average': 2,
                'schedule_stats.almaty.item_count.min': 1,
                'schedule_stats.almaty.item_count.max': 4,
                'schedule_stats.almaty.problematic_params.activities': 3,
                'schedule_stats.almaty.problematic_params.tags': 1,
                'schedule_stats.almaty.descriptor_combinations': 3,
                # descriptor_combinations_stats
                'schedule_stats.descriptor_combinations_stats.max': 3,
                'schedule_stats.descriptor_combinations_stats.min': 2,
                'schedule_stats.descriptor_combinations_stats.average': 2,
                # empty_descriptors
                'schedule_stats.number_of_empty_descriptors': 0,
                # affected_descriptors
                'schedule_stats.affected_descriptors.'
                'atomic_descriptors_count': 0,
                'schedule_stats.affected_descriptors.'
                'atomic_schedules_count': 0,
                'schedule_stats.affected_descriptors'
                '.atomic_total_update_time': 0,
                'schedule_stats.affected_descriptors'
                '.atomic_total_update_time_with_null_as_avg': 0,
                # update_times_by_zone
                'schedule_stats.moscow.update_times_by_zone.'
                'total_update_time': 2,
                'schedule_stats.moscow.update_times_by_zone.'
                'total_update_time_with_null_as_avg': 2,
                'schedule_stats.almaty.update_times_by_zone.'
                'total_update_time': 3,
                'schedule_stats.almaty.update_times_by_zone.'
                'total_update_time_with_null_as_avg': 3,
                # misc
                'schedule_stats.update_job_lag': {'atomic_job': 0},
            },
        ),
        (
            'empty_descriptors.json',
            {
                # moscow
                'schedule_stats.moscow.item_count.average': 1,
                'schedule_stats.moscow.item_count.min': 1,
                'schedule_stats.moscow.item_count.max': 1,
                'schedule_stats.moscow.problematic_params.activities': 1,
                'schedule_stats.moscow.problematic_params.tags': 2,
                'schedule_stats.moscow.descriptor_combinations': 2,
                # almaty
                'schedule_stats.almaty.item_count.average': 1,
                'schedule_stats.almaty.item_count.min': 1,
                'schedule_stats.almaty.item_count.max': 1,
                'schedule_stats.almaty.problematic_params.activities': 2,
                'schedule_stats.almaty.problematic_params.tags': 1,
                'schedule_stats.almaty.descriptor_combinations': 2,
                # descriptor_combinations_stats
                'schedule_stats.descriptor_combinations_stats.max': 2,
                'schedule_stats.descriptor_combinations_stats.min': 2,
                'schedule_stats.descriptor_combinations_stats.average': 2,
                # empty_descriptors
                'schedule_stats.number_of_empty_descriptors': 2,
                # affected_descriptors
                'schedule_stats.affected_descriptors.'
                'atomic_descriptors_count': 0,
                'schedule_stats.affected_descriptors.'
                'atomic_schedules_count': 0,
                'schedule_stats.affected_descriptors'
                '.atomic_total_update_time': 0,
                'schedule_stats.affected_descriptors'
                '.atomic_total_update_time_with_null_as_avg': 0,
                # update_times_by_zone
                'schedule_stats.moscow.update_times_by_zone.'
                'total_update_time': 2,
                'schedule_stats.moscow.update_times_by_zone.'
                'total_update_time_with_null_as_avg': 2,
                'schedule_stats.almaty.update_times_by_zone.'
                'total_update_time': 2,
                'schedule_stats.almaty.update_times_by_zone.'
                'total_update_time_with_null_as_avg': 2,
                # misc
                'schedule_stats.update_job_lag': {'atomic_job': 0},
            },
        ),
        (
            'affected_descriptors.json',
            {
                # affected_descriptors
                'schedule_stats.affected_descriptors.'
                'atomic_descriptors_count': 1,
                'schedule_stats.affected_descriptors.'
                'atomic_schedules_count': 1,
                'schedule_stats.affected_descriptors'
                '.atomic_total_update_time': 1,
                'schedule_stats.affected_descriptors'
                '.atomic_total_update_time_with_null_as_avg': 1,
                # descriptor_combinations_stats
                'schedule_stats.descriptor_combinations_stats.max': 1,
                'schedule_stats.descriptor_combinations_stats.min': 1,
                'schedule_stats.descriptor_combinations_stats.average': 1,
                # empty_descriptors
                'schedule_stats.number_of_empty_descriptors': 0,
                # moscow
                'schedule_stats.moscow.item_count.average': 1,
                'schedule_stats.moscow.item_count.min': 1,
                'schedule_stats.moscow.item_count.max': 1,
                'schedule_stats.moscow.problematic_params.activities': 1,
                'schedule_stats.moscow.problematic_params.tags': 1,
                'schedule_stats.moscow.descriptor_combinations': 1,
                # update_times_by_zone
                'schedule_stats.moscow.update_times_by_zone.'
                'total_update_time': 1,
                'schedule_stats.moscow.update_times_by_zone.'
                'total_update_time_with_null_as_avg': 1,
                # misc
                'schedule_stats.update_job_lag': {'atomic_job': 0},
            },
        ),
    ],
)
@pytest.mark.parametrize('use_cron', [False, True])
@pytest.mark.now('2021-02-01T12:10:00+0300')
async def test_stats_job(
        taxi_subvention_schedule,
        pgsql,
        bsx,
        load_json,
        taxi_subvention_schedule_monitor,
        original_db,
        expected_metrics,
        use_cron,
):
    await taxi_subvention_schedule.tests_control(reset_metrics=True)

    utils.load_db(pgsql, load_json(original_db))

    await taxi_subvention_schedule.post(
        '/service/cron', json={'task_name': 'stats-slow'},
    )
    await taxi_subvention_schedule.post(
        '/service/cron', json={'task_name': 'stats-fast'},
    )

    slow_metrics = await taxi_subvention_schedule_monitor.get_metric(
        'slow-metrics',
    )
    fast_metrics = await taxi_subvention_schedule_monitor.get_metric(
        'fast-metrics',
    )

    metrics = {**slow_metrics, **fast_metrics}

    # the NOW() value in sql is not tied to the mock now() value,
    # thus resulting in an unfixed non_atomic_job value
    if 'non_atomic_job' in metrics['schedule_stats.update_job_lag']:
        del metrics['schedule_stats.update_job_lag']['non_atomic_job']
    if 'non_atomic_job' in expected_metrics['schedule_stats.update_job_lag']:
        del expected_metrics['schedule_stats.update_job_lag']['non_atomic_job']

    assert metrics == expected_metrics
