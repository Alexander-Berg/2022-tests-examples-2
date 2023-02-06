import datetime

import pytest

from taxi.clients import approvals


@pytest.mark.config(SCRIPTS_FEATURES={'run_view_checks': True})
@pytest.mark.now('2020-06-07T12:00:00.0Z')
@pytest.mark.parametrize(
    'script, draft, expected_response',
    [
        (
            {'_id': 'waits-for-execute', 'status': 'need_approval'},
            {
                'id': 1,
                'status': approvals.DraftStatus.APPLYING,
                'change_doc_id': 'scripts_waits-for-execute',
                'created_by': 'd1mbas',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2020-06-07T11:59:30.0Z'},
                ],
                'run_manually': False,
            },
            {
                'id': 'waits-for-execute',
                'error_messages': [],
                'warning_messages': [],
            },
        ),
        (
            {
                '_id': 'waits-for-execute-too-long-warn',
                'status': 'need_approval',
            },
            {
                'id': 2,
                'status': approvals.DraftStatus.APPLYING,
                'change_doc_id': 'scripts_waits-for-execute-too-long-warn',
                'created_by': 'd1mbas',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2020-06-07T11:58:00.0Z'},
                ],
                'run_manually': False,
            },
            {
                'id': 'waits-for-execute-too-long-warn',
                'error_messages': [],
                'warning_messages': [
                    (
                        'Скрипт слишком долго находится в статусе '
                        '"Ожидание выполнения". '
                        'Проверьте что воркер на нужной машинке '
                        'установлен и работает.'
                    ),
                ],
            },
        ),
        (
            {
                '_id': 'waits-for-execute-too-long-crit',
                'status': 'need_approval',
            },
            {
                'id': 3,
                'status': approvals.DraftStatus.APPLYING,
                'change_doc_id': 'scripts_waits-for-execute-too-long-crit',
                'created_by': 'd1mbas',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2020-06-07T11:55:00.0Z'},
                ],
                'run_manually': False,
            },
            {
                'id': 'waits-for-execute-too-long-crit',
                'error_messages': [
                    (
                        'Скрипт слишком долго находится в статусе '
                        '"Ожидание выполнения". '
                        'Проверьте что воркер на нужной машинке '
                        'установлен и работает.'
                    ),
                ],
                'warning_messages': [],
            },
        ),
        (
            {
                '_id': 'running-too-long',
                'status': 'running',
                'started_running_at': datetime.datetime(2020, 6, 7, 11),
            },
            {
                'id': 4,
                'status': approvals.DraftStatus.APPLYING,
                'change_doc_id': 'scripts_running-too-long',
                'created_by': 'd1mbas',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2020-06-07T11:59:59.0Z'},
                ],
                'run_manually': False,
            },
            {
                'id': 'running-too-long',
                'error_messages': [],
                'warning_messages': [
                    (
                        'Скрипт работает достаточно долго. '
                        'Возможно стоит проверить что с ним всё в порядке.'
                    ),
                ],
            },
        ),
        (
            {
                '_id': 'failed-on-checkout',
                'status': 'failed',
                'started_running_at': None,
            },
            {
                'id': 1,
                'status': 'failed',
                'change_doc_id': 'scripts_failed-on-checkout',
                'created_by': 'd1mbas',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2020-06-07T11:59:30.0Z'},
                ],
                'run_manually': False,
            },
            {
                'id': 'failed-on-checkout',
                'error_messages': [],
                'warning_messages': [],
            },
        ),
    ],
)
async def test_extra_messages(
        patch, scripts_client, setup_scripts, script, draft, expected_response,
):
    @patch('taxi.clients.approvals.ApprovalsApiClient.get_drafts')
    async def _get_drafts_mock(*args, **kwargs):
        return [draft]

    await setup_scripts([script])

    response = await scripts_client.get(
        '/scripts/', headers={'X-Yandex-Login': 'd1mbas'},
    )
    data = await response.json()
    assert response.status == 200, data
    data = [
        {
            'error_messages': x['error_messages'],
            'warning_messages': x['warning_messages'],
            'id': x['id'],
        }
        for x in data['items']
    ]
    assert data == [expected_response]
