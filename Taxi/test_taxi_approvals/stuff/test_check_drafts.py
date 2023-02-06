import pytest

from taxi_approvals import exceptions
from taxi_approvals.generated.cron import run_cron


REMINDED_QUERY = """
    select
        id,
        description,
        status,
        service_name,
        api_path,
        data,
        reminded
    from
        approvals_schema.drafts
    where
        id = any($1::int[]);
"""

GET_LOCKS = """
    select
        draft_id,
        lock_id
    from
        approvals_schema.lock_ids
"""


@pytest.mark.pgsql('approvals', files=['one_approved_draft.sql'])
@pytest.mark.now('2017-11-01T03:00:00')
async def test_check_drafts(approvals_cron_app, mockserver, check_route_mock):
    check_route_mock(
        change_doc_id='test_doc_id',
        lock_ids=None,
        route_method='POST',
        route_headers=None,
        route_params=None,
        tickets={
            'create_data': {
                'summary': 'test_summary',
                'description': 'test_description',
                'components': [45167],
                'tags': ['test_tag'],
                'relationships': {'relates': ['TESTTICKET-1', 'TESTTICKET-2']},
            },
        },
        summon_users=['test_login'],
        mode='push',
        data={'test_data_key': 'test_data_value'},
        description='description_from_service_answer',
    )
    pool = approvals_cron_app['pool']
    await run_cron.main(['taxi_approvals.stuff.check_drafts', '-t', '0'])
    async with pool.acquire() as connection:
        result = await connection.fetch(REMINDED_QUERY, [1, 2])
        assert len(result) == 2
        for row in result:
            if row['id'] == 2:
                assert row['status'] == 'need_approval'
            if row['status'] == 'need_approval':
                assert row['description'] == 'description_from_service_answer'


@pytest.mark.pgsql('approvals', files=['one_approved_draft.sql', 'locks.sql'])
async def test_check_drafts_fail(
        patch, approvals_cron_app, mockserver, check_route_mock,
):
    @patch('taxi_approvals.internal.check_draft.mode_check')
    async def _draft_mode_check_fail(*args, **kwargs):
        raise exceptions.BaseError(
            code=404, msg='Test exception', status='TEST_EXC',
        )

    pool = approvals_cron_app['pool']
    await run_cron.main(['taxi_approvals.stuff.check_drafts', '-t', '0'])
    async with pool.acquire() as connection:
        result = await connection.fetch(GET_LOCKS)
        assert len(result) == 1
        result = await connection.fetch(REMINDED_QUERY, [2])
        assert result[0]['status'] == 'failed'
