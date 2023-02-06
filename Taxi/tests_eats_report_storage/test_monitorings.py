import pytest

REPORT_STORAGE_STATS_CONFIG = {'interval': 3600}


def set_synchronization_time(pgsql, sync_name, date):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute(
        f"""INSERT INTO eats_report_storage.greenplum_sync (sync_name, last_sync_time)
            VALUES (\'{sync_name}\', \'{date}\'::timestamptz)
            ON CONFLICT (sync_name) DO UPDATE
            SET last_sync_time = \'{date}\'::timestamptz;""",
    )


@pytest.mark.now('2021-08-17T18:30+03:00')
@pytest.mark.config(
    EATS_REPORT_STORAGE_REPORT_STORAGE_STATS=REPORT_STORAGE_STATS_CONFIG,
)
async def test_report_storage_stats(
        taxi_eats_report_storage, taxi_eats_report_storage_monitor, pgsql,
):
    set_synchronization_time(
        pgsql, 'sync-plus-stats', '2021-08-17 12:30+03:00',
    )
    await taxi_eats_report_storage.run_periodic_task(
        'report_storage_stats_task',
    )
    metrics = await taxi_eats_report_storage_monitor.get_metrics()
    assert (
        metrics['report-storage-stats'][
            'sync-plus-stats.hours_from_last_sync_time'
        ]
        == 6
    )

    set_synchronization_time(
        pgsql, 'sync-plus-stats', '2021-08-17 15:30+03:00',
    )
    set_synchronization_time(
        pgsql, 'sync-common-stats', '2021-08-17 16:30+03:00',
    )
    await taxi_eats_report_storage.run_periodic_task(
        'report_storage_stats_task',
    )
    metrics = await taxi_eats_report_storage_monitor.get_metrics()
    assert (
        metrics['report-storage-stats'][
            'sync-plus-stats.hours_from_last_sync_time'
        ]
        == 3
    )
    assert (
        metrics['report-storage-stats'][
            'sync-common-stats.hours_from_last_sync_time'
        ]
        == 2
    )
