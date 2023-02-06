import pytest

from clownductor.generated.cron import run_cron
from clownductor.internal.utils import postgres


GET_JOBS_QUERY = """
    select
        id,
        name,
        service_id,
        branch_id,
        status,
        idempotency_token,
        change_doc_id
    from
        task_manager.jobs
    order by
        id
"""


@pytest.mark.config(
    CLOWNDUCTOR_SYNC_PARAMETERS={
        'enabled': True,
        'remove_old_jobs': {
            'enabled': True,
            'remain_amount': 2,
            'batch_size': 1,
        },
    },
)
@pytest.mark.now('2020-11-22T06:00:00.0Z')
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.parametrize(
    'expected_name',
    [pytest.param('add_change_doc_id.json', id='add_change_doc_id')],
)
async def test_sync_parameters(cron_context, expected_name, load_json):
    await run_cron.main(['clownductor.crontasks.update_parameters', '-t', '0'])

    jobs = await _get_jobs(cron_context)
    expected = load_json(f'expected/{expected_name}')
    assert jobs == expected


async def _get_jobs(cron_context):
    async with postgres.primary_connect(cron_context) as conn:
        jobs = await conn.fetch(GET_JOBS_QUERY)
    return [dict(job) for job in jobs]
