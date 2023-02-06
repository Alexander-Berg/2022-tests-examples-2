import datetime

import freezegun
import pytest

from taxi_approvals.generated.cron import run_cron


TIME_MOCK = datetime.datetime(2017, 11, 1, 5, 10)

GET_QUERY = """
    select
        id
    from
        approvals_schema.drafts
    where status = 'expired'
    order by id;
"""


@pytest.mark.parametrize(
    'expected_drafts_id',
    [
        pytest.param(
            [1, 2, 3],
            id='expired_on',
            marks=pytest.mark.config(
                APPROVALS_TIME_LIMITS={
                    'enable': True,
                    'rules': {
                        'need_approval': {
                            'expire_enabled': True,
                            'days_to_expire': 1,
                        },
                    },
                },
            ),
        ),
        pytest.param(
            [3],
            id='expired_off',
            marks=pytest.mark.config(
                APPROVALS_TIME_LIMITS={
                    'enable': True,
                    'rules': {
                        'need_approval': {
                            'expire_enabled': False,
                            'days_to_expire': 1,
                        },
                    },
                },
            ),
        ),
    ],
)
@pytest.mark.pgsql('approvals', files=['test_expired.sql'])
async def test_expired_drafts(approvals_cron_app, expected_drafts_id):
    with freezegun.freeze_time(TIME_MOCK.isoformat()):
        await run_cron.main(['taxi_approvals.stuff.expired_drafts', '-t', '0'])
    pool = approvals_cron_app['pool']
    async with pool.acquire() as connection:
        raw_result = await connection.fetch(GET_QUERY)
        result = [doc['id'] for doc in raw_result]
        assert result == expected_drafts_id
