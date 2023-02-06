import pytest

from abt import consts as app_consts
from abt import models
from test_abt.helpers import web as web_helpers


@pytest.fixture(name='invoke_handler')
def _invoke_handler(taxi_abt_web):
    return web_helpers.create_invoke(
        'put', '/v1/metrics_groups/check-draft', taxi_abt_web,
    )


@pytest.mark.config(
    ABT_AVAILABLE_SCOPES=[
        {'scope': 'scope_for_update', 'description': 'dummy'},
    ],
)
async def test_check_draft_success(abt, build_update_request, invoke_handler):
    metrics_group = models.MetricsGroup.from_record(
        await abt.state.add_metrics_group(),
    )
    body, _ = build_update_request(metrics_group)

    got = await invoke_handler(
        params={'metrics_group_id': metrics_group.id}, body=body,
    )

    assert got == {
        'change_doc_id': f'update/metrics_group/{metrics_group.id}',
        'data': body,
    }


async def test_check_draft_not_found(
        abt, build_update_request, invoke_handler,
):
    metrics_group = models.MetricsGroup.from_record(
        await abt.state.add_metrics_group(),
    )
    body, _ = build_update_request(metrics_group)

    got = await invoke_handler(
        params={'metrics_group_id': 100500}, body=body, expected_code=404,
    )

    assert got['code'] == app_consts.CODE_404


@pytest.mark.config(
    ABT_AVAILABLE_SCOPES=[
        {'scope': 'scope_for_update', 'description': 'dummy'},
    ],
)
async def test_invoke_relevant_validators(
        mockserver, build_update_request, invoke_handler, abt,
):
    invoke_validators = []

    @mockserver.json_handler('/service/run_validation')
    async def _run_validation(request):
        invoke_validators.append(request.json['validator_name'])

    metrics_group = models.MetricsGroup.from_record(
        await abt.state.add_metrics_group(),
    )

    body, _ = build_update_request(metrics_group)

    await invoke_handler(
        params={'metrics_group_id': metrics_group.id}, body=body,
    )

    assert invoke_validators == [
        'MetricsGroupsConfigSyntaxValidator',
        'MetricsGroupsScopesValidator',
        'EqualityValidator',
    ]
