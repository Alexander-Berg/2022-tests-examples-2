import pytest

from test_abt.helpers import web as web_helpers


@pytest.fixture(name='invoke_handler')
def _invoke_handler(taxi_abt_web):
    return web_helpers.create_invoke(
        'post', '/v1/metrics_groups/check-draft', taxi_abt_web,
    )


@pytest.mark.config(
    ABT_AVAILABLE_SCOPES=[
        {'scope': 'scope_for_create', 'description': 'dummy'},
    ],
)
async def test_check_draft_success(abt, build_create_request, invoke_handler):
    body, _ = build_create_request()

    got = await invoke_handler(body=body)

    assert got['change_doc_id'].startswith('create/metrics_group/')
    assert got['data'] == body


@pytest.mark.config(
    ABT_AVAILABLE_SCOPES=[
        {'scope': 'scope_for_create', 'description': 'dummy'},
    ],
)
async def test_invoke_relevant_validators(
        mockserver, build_create_request, invoke_handler,
):
    invoke_validators = []

    @mockserver.json_handler('/service/run_validation')
    async def _run_validation(request):
        invoke_validators.append(request.json['validator_name'])

    body, _ = build_create_request()

    await invoke_handler(body=body)

    assert invoke_validators == [
        'MetricsGroupsConfigSyntaxValidator',
        'MetricsGroupsScopesValidator',
    ]
