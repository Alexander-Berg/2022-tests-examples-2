import datetime as dt

import pytest

PERIODIC_NAME = 'eats_nomenclature-collect_metrics-edadeal'


def settings(edadeal_unprocessed_threshold_in_hours=4):
    return {
        '__default__': {
            'assortment_outdated_threshold_in_hours': 2,
            'edadeal_unprocessed_threshold_in_hours': (
                edadeal_unprocessed_threshold_in_hours
            ),
        },
    }


@pytest.mark.suspend_periodic_tasks('edadeal-metrics')
@pytest.mark.config(EATS_NOMENCLATURE_METRICS=settings())
@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_data.sql'],
)
async def test_metrics(
        pgsql,
        taxi_config,
        taxi_eats_nomenclature,
        taxi_eats_nomenclature_monitor,
):
    metric_name = 'unprocessed_export_task_count'
    metric_threshold_config_name = 'edadeal_unprocessed_threshold_in_hours'

    async def check_metrics(taxi_eats_nomenclature_monitor, expected_count):
        metrics = await taxi_eats_nomenclature_monitor.get_metrics()
        assert metric_name in metrics['edadeal-metrics']
        assert metrics['edadeal-metrics'][metric_name] == expected_count

    def get_time_now(offset_in_minutes):
        return (
            dt.datetime.now() - dt.timedelta(minutes=offset_in_minutes)
        ).strftime('%Y-%m-%d %H:%M:%S')

    config = taxi_config.get('EATS_NOMENCLATURE_METRICS')['__default__']
    threshold_in_minutes = config[metric_threshold_config_name] * 60

    # No data
    await check_metrics(taxi_eats_nomenclature_monitor, 0)

    # New data
    sql_add_export_task_data(
        pgsql, s3_path='path_1', is_processed=False, update_time='2039-01-01',
    )
    await taxi_eats_nomenclature.run_periodic_task(PERIODIC_NAME)
    await check_metrics(taxi_eats_nomenclature_monitor, 0)

    # Old data, but above threshold
    sql_add_export_task_data(
        pgsql, s3_path='path_2', is_processed=False, update_time='2019-01-01',
    )
    sql_add_export_task_data(
        pgsql,
        s3_path='path_3',
        is_processed=False,
        update_time=get_time_now(threshold_in_minutes * 2),
    )
    await taxi_eats_nomenclature.run_periodic_task(PERIODIC_NAME)
    await check_metrics(taxi_eats_nomenclature_monitor, 2)

    # Old data, but below threshold
    sql_add_export_task_data(
        pgsql,
        s3_path='path_4',
        is_processed=False,
        update_time=get_time_now(threshold_in_minutes / 2),
    )
    await taxi_eats_nomenclature.run_periodic_task(PERIODIC_NAME)
    await check_metrics(taxi_eats_nomenclature_monitor, 2)

    # Old data and above threshold, but processed
    sql_add_export_task_data(
        pgsql,
        s3_path='path_5',
        is_processed=True,
        update_time=get_time_now(threshold_in_minutes * 2),
    )
    await taxi_eats_nomenclature.run_periodic_task(PERIODIC_NAME)
    await check_metrics(taxi_eats_nomenclature_monitor, 2)


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=False)


def sql_add_export_task_data(pgsql, s3_path, is_processed, update_time):

    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.edadeal_export_tasks
        (
            brand_id,
            s3_export_path,
            export_retailer_name,
            exported_at,
            processed
        )
        values (1, '{s3_path}', 'retailer', '{update_time}', {is_processed});
        """,
    )
