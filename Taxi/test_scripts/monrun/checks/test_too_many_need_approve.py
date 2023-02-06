# pylint: disable=protected-access,unused-variable
import datetime

import pytest

from taxi.util import dates

from scripts.monrun.checks import too_many_need_approve


NOW = datetime.datetime(2019, 5, 30, 14)


@pytest.mark.parametrize(
    'script_docs,drafts',
    [
        ([], []),
        (
            [
                {'_id': '1', 'status': 'need_approval'},
                {'_id': '2', 'status': 'running'},
            ],
            [{'change_doc_id': 'scripts_1'}],
        ),
        (
            [
                {'_id': '1', 'status': 'need_approval'},
                {'_id': '2', 'status': 'running'},
            ],
            [{'change_doc_id': 'scripts_1'}, {'change_doc_id': 'scripts_2'}],
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    SCRIPTS_MONITORING_CONFIGS={
        'too_many_need_approve': {'elder_then_delay': 5, 'threshold': 2},
    },
)
async def test_check_ok(
        patch, scripts_tasks_app, setup_scripts, script_docs, drafts,
):
    @patch('taxi.clients.approvals.ApprovalsApiClient.get_drafts')
    async def get_drafts_mock(data, log_extra=None):
        return drafts

    await setup_scripts(script_docs)

    result = await too_many_need_approve._check(scripts_tasks_app, None)
    assert result == '0; OK'


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    SCRIPTS_MONITORING_CONFIGS={
        'too_many_need_approve': {'elder_then_delay': 5, 'threshold': 2},
    },
)
@pytest.mark.usefixtures('setup_many_scripts')
async def test_check_warn(patch, scripts_tasks_app):
    @patch('taxi.clients.approvals.ApprovalsApiClient.get_drafts')
    async def get_drafts_mock(data, log_extra=None):
        return [
            {'change_doc_id': 'scripts_test-approve-self-created'},
            {'change_doc_id': 'scripts_test-filter-by-org'},
        ]

    result = await too_many_need_approve._check(scripts_tasks_app, None)
    msg = (
        '1; WARN: 2 scripts are still in need_approval state '
        f'elder then {dates.timestring(NOW-datetime.timedelta(minutes=5))}'
    )
    assert result == msg
