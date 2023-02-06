import pytest

from clownductor.generated.cron import run_cron
from clownductor.internal.utils import postgres


GET_REMOVE_JOBS_QUERY = """
    select
        id,
        service_id,
        idempotency_token,
        change_doc_id
    from
        task_manager.jobs
    where
        name = 'RemoveNannyBranch'
    order by
        id
"""

EXPECTED_JOBS = [
    {
        'id': 8,
        'idempotency_token': 'RemoveNannyBranch_3',
        'change_doc_id': None,
        'service_id': 1,
    },
    {
        'id': 9,
        'idempotency_token': 'RemoveNannyBranch_6',
        'change_doc_id': None,
        'service_id': 2,
    },
]


@pytest.mark.config(
    CLOWNDUCTOR_TANK_BRANCHES={
        'delete_settings': {
            'enabled': True,
            'only_search': False,
            'max_age_in_days': 7,
        },
        'possible_regions': ['man', 'vla', 'sas'],
    },
)
@pytest.mark.now('2020-11-17T19:00:00.0Z')
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_remove_old_tank_branches(cron_context):
    await run_cron.main(
        ['clownductor.crontasks.remove_old_tank_branches', '-t', '0'],
    )

    jobs = await _get_jobs(cron_context)
    assert jobs == EXPECTED_JOBS


async def _get_jobs(cron_context):
    async with postgres.primary_connect(cron_context) as conn:
        jobs = await conn.fetch(GET_REMOVE_JOBS_QUERY)
    return [dict(job) for job in jobs]
