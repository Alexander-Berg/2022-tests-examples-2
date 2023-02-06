import typing as tp

import pytest

from workforce_management.common import constants
from workforce_management.storage.postgresql import db as operators_repo


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts.sql',
        'simple_shifts_drafts.sql',
    ],
)
@pytest.mark.parametrize(
    'approvals_drafts_by_id',
    [
        pytest.param(
            {
                '1': {
                    'id': 1,
                    'change_doc_id': '1',
                    'status': 'rejected',
                    'version': 2,
                },
            },
            id='base',
        ),
    ],
)
async def test_base(
        stq3_context, stq_runner, mockserver, stq, approvals_drafts_by_id,
):
    drafts_list_request: tp.Optional[tp.Dict] = None

    @mockserver.json_handler('/taxi-approvals/drafts/list/')
    def _approvals_drafts_list(request):
        nonlocal drafts_list_request
        if drafts_list_request:
            return []
        drafts_list_request = request.json
        return list(approvals_drafts_by_id.values())

    await stq_runner.workforce_management_periodic_jobs.call(
        task_id=constants.PeriodicJobTypes.approvals_drafts_puller.value,
        args=(),
        kwargs={},
    )

    operators_db = operators_repo.OperatorsRepo(stq3_context)
    async with operators_db.master.acquire() as connection:
        records = await operators_db.get_shifts_drafts(
            connection, draft_ids=list(approvals_drafts_by_id),
        )
        for draft in records:
            draft_id = draft['draft_id']
            status = constants.DraftStatus(draft['status']).name
            expected_status = approvals_drafts_by_id[draft_id]['status']
            assert status == expected_status
