import pytest

from eats_integration_workers.generated.cron import run_cron


@pytest.mark.pgsql(
    'eats_integration_workers', files=['data_status_created.sql'],
)
@pytest.mark.parametrize(
    'enable_cron_task, start_count_task, end_count_task',
    [[False, 3, 3], [True, 3, 1]],
)
async def test_correct_task(
        cron_context,
        pgsql,
        load_json,
        taxi_config,
        enable_cron_task,
        start_count_task,
        end_count_task,
):
    taxi_config.set_values(
        {
            'EATS_INTEGRATION_WORKERS_UPDATE_STATUS_CREATED': {
                'enable_cron_task': enable_cron_task,
            },
        },
    )

    assert get_status_created_count(pgsql) == start_count_task
    await run_cron.main(
        [
            'eats_integration_workers.crontasks.update_status_created',
            '-t',
            '0',
        ],
    )
    assert get_status_created_count(pgsql) == end_count_task


def get_status_created_count(pgsql):
    with pgsql['eats_integration_workers'].cursor() as cursor:
        cursor.execute(
            'SELECT COUNT(*) FROM eats_integration_workers.integration_task where status = \'created\'',  # noqa: F401,E501
        )
        count = list(row[0] for row in cursor)[0]
    return count
