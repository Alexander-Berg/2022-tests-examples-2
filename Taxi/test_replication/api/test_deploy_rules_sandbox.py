import pytest


@pytest.mark.parametrize(
    'token, expected_status, expected_body',
    [
        ('', 200, {'draft_deploy_link': 'stub'}),
        pytest.param(
            '',
            403,
            {'code': 'forbidden', 'message': 'Access is forbidden'},
            marks=pytest.mark.config(
                REPLICATION_RULES_DEPLOY={
                    'deploy_api': {'need_check_api_token': True},
                },
            ),
        ),
        pytest.param(
            'secret',
            200,
            {
                'draft_deploy_link': 'stub',
                'startrek_comment': 'Download link: link, draft: stub',
                'teamcity_comment': 'Draft: stub',
            },
            marks=pytest.mark.config(
                REPLICATION_RULES_DEPLOY={
                    'deploy_api': {
                        'need_check_api_token': True,
                        'need_startrek_comment': True,
                        'startrek_comment_template': (
                            'Download link: {download_link}, '
                            'draft: {draft_deploy_link}'
                        ),
                        'need_teamcity_comment': True,
                        'teamcity_comment_template': (
                            'Draft: {draft_deploy_link}'
                        ),
                    },
                },
            ),
        ),
        pytest.param(
            'secret',
            200,
            {'draft_deploy_link': 'https://unittests/replications/draft/101'},
            marks=pytest.mark.config(
                REPLICATION_RULES_DEPLOY={
                    'deploy_api': {
                        'need_check_api_token': True,
                        'need_create_deploy_draft': True,
                    },
                },
            ),
        ),
    ],
)
async def test_deploy(
        replication_client,
        token,
        expected_status,
        expected_body,
        _patch_secdist,
        _mock_approvals,
):
    response = await replication_client.post(
        '/deploy/v1/rules/sandbox/',
        headers={'X-YaTaxi-Api-Key': token},
        json={
            'startrek_ticket': 'TICKET-123',
            'download_link': 'link',
            'resource_link': 'link2',
            'package': 'replication-rules',
            'version': '123',
            'conductor_ticket': '12345',
        },
    )
    assert response.status == expected_status
    assert await response.json() == expected_body


@pytest.fixture
def _patch_secdist(simple_secdist):
    simple_secdist['settings_override'].update(
        {'REPLICATION_APIKEY': 'secret'},
    )


@pytest.fixture
def _mock_approvals(mockserver):
    @mockserver.json_handler('/taxi-approvals/drafts/create/')
    def _draft_create(request):
        return mockserver.make_response(
            status=200, json={'id': 101, 'version': 1},
        )
