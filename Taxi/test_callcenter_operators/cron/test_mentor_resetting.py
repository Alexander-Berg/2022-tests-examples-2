import pytest

from callcenter_operators import utils
from callcenter_operators.storage.postgresql import db


async def _select_mentor(context, op_id):
    pool = await db.OperatorsRepo.get_ro_pool(context)

    async with pool.acquire() as conn:
        query = (
            'SELECT mentor_login FROM '
            'callcenter_auth.operators_access WHERE id=$1'
        )
        result = await utils.execute_query(query, conn, 'fetchval', int(op_id))
    return result


@pytest.mark.config(
    CALLCENTER_OPERATORS_AUTOMATIC_MENTOR_RESETTING={
        'enabled': False,
        'cutoff': 30,
    },
)
@pytest.mark.now('2021-06-22 19:10:00+00')
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_hanged_mentors.psql'],
)
async def test_disabled(cron_runner, cron_context):
    mentor = await _select_mentor(cron_context, 1)
    assert mentor is not None
    await cron_runner.operators_mentors_resetting()
    new_mentor = await _select_mentor(cron_context, 1)
    assert new_mentor is not None


@pytest.mark.config(
    CALLCENTER_OPERATORS_AUTOMATIC_MENTOR_RESETTING={
        'enabled': True,
        'cutoff': 3600,
    },
)
@pytest.mark.now('2020-02-10 19:10:00+00')
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_hanged_mentors.psql'],
)
async def test_not_hanged(cron_runner, cron_context):
    mentor = await _select_mentor(cron_context, 1)
    assert mentor is not None
    await cron_runner.operators_mentors_resetting()
    new_mentor = await _select_mentor(cron_context, 1)
    assert new_mentor is not None


@pytest.mark.config(
    CALLCENTER_OPERATORS_AUTOMATIC_MENTOR_RESETTING={
        'enabled': True,
        'cutoff': 30,
    },
)
@pytest.mark.now('2021-06-22 19:10:00+00')
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_hanged_mentors.psql'],
)
async def test_hanged(cron_runner, cron_context):
    mentor = await _select_mentor(cron_context, 1)
    assert mentor is not None
    await cron_runner.operators_mentors_resetting()
    new_mentor = await _select_mentor(cron_context, 1)
    assert new_mentor is None
