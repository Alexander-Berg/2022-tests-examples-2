# pylint: disable=redefined-outer-name
import datetime

import freezegun
import pytest

from taxi_approvals import queries
from taxi_approvals.exceptions import BaseError
from taxi_approvals.generated.cron import run_cron
from taxi_approvals.internal import drafts
from taxi_approvals.stuff import apply_drafts

FIND_SUCCEEDED_QUERY = (
    'SELECT id '
    'FROM approvals_schema.drafts '
    'WHERE status = \'succeeded\' AND NOT run_manually AND '
    'apply_time <= $1::timestamp;'
)
START_APPLY_TIME_MOCK = datetime.datetime(2017, 11, 1, 5, 10)
FINISH_APPLY_TIME_MOCK = datetime.datetime(2017, 11, 1, 5, 10, 55)


@pytest.mark.pgsql('approvals', files=['default.sql'])
async def test_apply_draft(approvals_cron_app, patch):
    @patch('taxi.clients.audit.AuditClient.create_log')
    async def _audit_log(document, **kwargs):
        draft_id = document['arguments']['applying_doc_id']
        assert document['object_id'] == 'test_value'
        assert document['action'] == 'test_apply_audit_action_id'
        if draft_id == 1:
            assert document['system_name'] == 'tplatform'
        else:
            assert document['system_name'] == 'tariff-editor'

        if draft_id == 1:
            assert document['tplatform_namespace'] == 'market'
        elif draft_id == 2:
            assert document['tplatform_namespace'] == 'taxi'
        else:
            assert not document.get('tplatform_namespace')
        return 'id'

    # pylint: disable=unused-variable
    @patch('taxi_approvals.stuff.apply_drafts.Scheduler')
    def test_need_to_run():
        class MockScheduler:
            def __init__(self):
                self.calls = 0

            async def need_to_run(self):
                self.calls += 1
                query_time = datetime.datetime.utcnow()
                if self.calls == 2:
                    await self._check_first_call_result(query_time)
                    frozen_datetime.move_to('2017-11-01T05:10:40')
                if self.calls == 3:
                    await self._check_second_call_result(query_time)
                    frozen_datetime.move_to('2017-11-01T05:10:55')
                return True

            async def _check_first_call_result(self, query_time):
                pool = approvals_cron_app['pool']
                async with pool.acquire() as connection:
                    result = await connection.fetch(
                        apply_drafts.FIND_APPROVED_QUERY, query_time,
                    )
                    assert result == []
                    result = await connection.fetch(
                        apply_drafts.FIND_APPLYING_QUERY, query_time,
                    )
                    assert result == []
                    result = await connection.fetch(
                        FIND_SUCCEEDED_QUERY, query_time,
                    )
                    assert len(result) == 2
                    result = await connection.fetch(
                        queries.SELECT_LOCKS.format(where=''), 0, 10,
                    )
                    assert len(result) == 1
                    result = await connection.fetch(
                        queries.FIND_BY_STATUS, drafts.EXPIRED_STATUS,
                    )
                    assert len(result) == 1
                    result = await connection.fetch(
                        queries.FIND_BY_STATUS, drafts.NEED_APPROVAL_STATUS,
                    )
                    assert len(result) == 1

            async def _check_second_call_result(self, query_time):
                pool = approvals_cron_app['pool']
                async with pool.acquire() as connection:
                    result = await connection.fetch(
                        apply_drafts.FIND_APPROVED_QUERY, query_time,
                    )
                    assert result == []
                    result = await connection.fetch(
                        apply_drafts.FIND_APPLYING_QUERY, query_time,
                    )
                    assert result == []
                    result = await connection.fetch(
                        FIND_SUCCEEDED_QUERY, query_time,
                    )
                    assert len(result) == 3
                    result = await connection.fetch(
                        queries.FIND_BY_STATUS, drafts.EXPIRED_STATUS,
                    )
                    assert len(result) == 1
                    result = await connection.fetch(
                        queries.FIND_BY_STATUS, drafts.NEED_APPROVAL_STATUS,
                    )
                    assert len(result) == 1

        return MockScheduler()

    with freezegun.freeze_time('2017-11-01T05:10:00') as frozen_datetime:
        await run_cron.main(['taxi_approvals.stuff.apply_drafts', '-t', '0'])


@pytest.mark.parametrize(
    'draft_status',
    [
        drafts.PARTIALLY_COMPLETED_STATUS,
        drafts.SUCCEEDED_STATUS,
        drafts.FAILED_STATUS,
    ],
)
@pytest.mark.pgsql('approvals', files=['one_approved_draft.sql'])
async def test_apply_draft_set_start_and_finish_apply_time(
        approvals_cron_app, patch, draft_status,
):
    @patch('taxi.clients.audit.AuditClient.create_log')
    async def _audit_log(document, **kwargs):
        assert document['object_id'] == 'test_value'
        assert document['action'] == 'test_apply_audit_action_id'
        return 'id'

    @patch('taxi_approvals.stuff.apply_drafts.Scheduler')
    def _scheduler_mock():
        class MockScheduler:
            def __init__(self):
                self.calls = 0

            async def need_to_run(self):
                self.calls += 1
                query_time = datetime.datetime.utcnow()
                if self.calls == 2:
                    await self._check_first_call_result(query_time)
                    return False

                return True

            async def _check_first_call_result(self, query_time):
                pool = approvals_cron_app['pool']
                async with pool.acquire() as connection:
                    result = await connection.fetch(
                        apply_drafts.FIND_APPROVED_QUERY, query_time,
                    )
                    assert result == []
                    result = await connection.fetch(
                        apply_drafts.FIND_APPLYING_QUERY, query_time,
                    )
                    assert result == []
                    result = await connection.fetch(
                        queries.FIND_BY_STATUS, draft_status,
                    )
                    assert len(result) == 1
                    assert (
                        result[0]['start_apply_time'] == START_APPLY_TIME_MOCK
                    )
                    assert (
                        result[0]['finish_apply_time']
                        == FINISH_APPLY_TIME_MOCK
                    )

        return MockScheduler()

    @patch('taxi_approvals.internal.requests.draft_external_request')
    async def _draft_external_request(*args, **kwargs):
        frozen_datetime.move_to(FINISH_APPLY_TIME_MOCK.isoformat())
        if draft_status == drafts.FAILED_STATUS:
            raise BaseError

        return {'status': draft_status}

    with freezegun.freeze_time(
            START_APPLY_TIME_MOCK.isoformat(),
    ) as frozen_datetime:
        await run_cron.main(['taxi_approvals.stuff.apply_drafts', '-t', '0'])

    assert len(_scheduler_mock.calls) == 1
    assert len(_draft_external_request.calls) == 1
