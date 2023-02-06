# pylint: disable=unused-variable
import pytest

from taxi import settings


@pytest.mark.parametrize(
    'env, status_code, is_error',
    [
        (None, 200, False),
        (settings.DEVELOPMENT, 200, False),
        (settings.UNSTABLE, 200, False),
        (settings.TESTING, 200, False),
        (settings.PRODUCTION, 400, True),
    ],
)
@pytest.mark.config(SCRIPTS_FEATURES={'optional_ticket_in_custom': True})
async def test_create_script_for_optional_ticket(
        monkeypatch,
        patch,
        scripts_client,
        find_script,
        env,
        status_code,
        is_error,
):
    if env:
        monkeypatch.setattr('taxi.settings.ENVIRONMENT', env)

    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def create_draft_mock(*args, **kwargs):
        return {}

    response = await scripts_client.post(
        '/scripts/',
        json={
            'url': (
                'https://github.yandex-team.ru/taxi/tools/blob/'
                '30665de7552ade50fd29b7d059c339e1fc1f93f0/'
                'migrations/m4326_debugging_script.py'
            ),
            'python_path': '/usr/lib/yandex/taxi-import',
            'arguments': [],
            'comment': 'some comment',
            'request_id': '123',
            'report_to_prod': True,
        },
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    data = await response.json()
    assert response.status == status_code
    if not is_error:
        assert data['status'] == 'ok'
        script = await find_script(data['id'])
        assert script['ticket'] is None
    else:
        assert data == {
            'status': 'error',
            'code': 'PROPERTY_IS_REQUIRED',
            'message': 'property "ticket" is required',
        }


async def test_get_script_with_no_ticket(patch, setup_scripts, scripts_client):
    await setup_scripts(
        [
            {
                'is_reported': False,
                'status': 'succeeded',
                '_id': 'non-reported-succeeded-empty-ticket',
                'ticket': None,
            },
        ],
    )

    @patch('taxi.clients.approvals.ApprovalsApiClient.get_draft')
    async def get_draft_mock(*args, **kwargs):
        return {
            'created_by': 'd1mbas',
            'id': 1,
            'description': '',
            'approvals': [],
            'run_manually': False,
            'status': 'need_approvals',
        }

    @patch('taxi.clients.approvals.ApprovalsApiClient.get_drafts')
    async def get_drafts_mock(data, log_extra):
        return [
            {
                'change_doc_id': 'scripts_non-reported-succeeded-empty-ticket',
                'created_by': 'd1mbas',
                'id': 2,
                'description': '',
                'approvals': [
                    {'login': 'd1mbas', 'created': '2019-05-24T10:00:00.0'},
                ],
                'run_manually': False,
                'status': 'need_approvals',
            },
        ]

    response = await scripts_client.get(
        '/non-reported-succeeded-empty-ticket/',
        headers={'X-Yandex-Login': 'somebody'},
    )
    assert response.status == 200
    result = await response.json()
    assert 'ticket' not in result

    response = await scripts_client.get(
        '/scripts/', headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200
    result = await response.json()
    assert len(result['items']) == 1
    assert 'ticket' not in result['items'][0]
