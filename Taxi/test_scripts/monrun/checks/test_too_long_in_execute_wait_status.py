# pylint: disable=protected-access, unused-variable
import datetime

import pytest

from scripts.monrun.checks import too_long_in_execute_wait

NOW = datetime.datetime(2020, 5, 7, 12, 10)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'script_docs, drafts',
    [
        ([], []),
        (
            [{'_id': '1', 'status': 'running'}],
            [
                {
                    'change_doc_id': 'scripts_1',
                    'status': 'applying',
                    'updated': '2020-05-07T12:09:30Z',
                    'approvals': [
                        {'login': 'd1mbas', 'created': '2020-05-07T12:09:30Z'},
                    ],
                },
            ],
        ),
        ([{'_id': '1', 'status': 'need_approval'}], []),
        (
            [{'_id': '1', 'status': 'need_approval'}],
            [
                {
                    'change_doc_id': 'scripts_1',
                    'status': 'applying',
                    'updated': '2020-05-07T12:09:30Z',
                    'approvals': [
                        {'login': 'd1mbas', 'created': '2020-05-07T12:09:30Z'},
                    ],
                },
            ],
        ),
    ],
)
async def test_ok(
        patch, setup_scripts, scripts_tasks_app, script_docs, drafts,
):
    @patch('taxi.clients.approvals.ApprovalsApiClient.get_drafts')
    async def get_drafts_mock(data, log_extra=None):
        return drafts

    await setup_scripts(script_docs)

    result = await too_long_in_execute_wait._check(scripts_tasks_app, None)
    assert result == '0; OK'


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'script_docs, drafts, message',
    [
        (
            [{'_id': '1', 'status': 'need_approval'}],
            [
                {
                    'change_doc_id': 'scripts_1',
                    'status': 'applying',
                    'updated': '2020-05-07T12:08:20Z',
                    'approvals': [
                        {'login': 'd1mbas', 'created': '2020-05-07T12:08:20Z'},
                    ],
                },
            ],
            '1; WARN: 1 scripts are too long in execute_wait status',
        ),
        (
            [{'_id': '1', 'status': 'need_approval'}],
            [
                {
                    'change_doc_id': 'scripts_1',
                    'status': 'applying',
                    'updated': '2020-05-07T12:07:20Z',
                    'approvals': [
                        {'login': 'd1mbas', 'created': '2020-05-07T12:07:20Z'},
                    ],
                },
            ],
            '2; CRIT: 1 scripts are too long in execute_wait status',
        ),
    ],
)
async def test_check_non_ok(
        patch, setup_scripts, scripts_tasks_app, script_docs, drafts, message,
):
    @patch('taxi.clients.approvals.ApprovalsApiClient.get_drafts')
    async def get_drafts_mock(data, log_extra=None):
        return drafts

    await setup_scripts(script_docs)

    result = await too_long_in_execute_wait._check(scripts_tasks_app, None)
    assert result == message
