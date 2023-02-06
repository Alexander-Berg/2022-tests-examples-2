import pytest

from test_abt import utils
from test_abt.helpers import web as web_helpers


@pytest.fixture(name='invoke_handler')
def _invoke_handler(taxi_abt_web):
    return web_helpers.create_invoke(
        'post', '/v1/metrics_groups', taxi_abt_web,
    )


@pytest.mark.config(
    ABT_AVAILABLE_SCOPES=[
        {'scope': 'scope_for_create', 'description': 'dummy'},
    ],
)
async def test_create_success(
        yt_apply, abt, build_create_request, invoke_handler, stq,
):
    body, _ = build_create_request()

    assert await abt.pg.metrics_groups.count() == 0
    assert await abt.pg.precomputes_tables.count() == 0

    assert await invoke_handler(body=body) == {}

    metrics_group = await abt.pg.metrics_groups.first()

    assert (
        utils.fields(
            metrics_group,
            [
                'title',
                'description',
                'owners',
                'scopes',
                'is_collapsed',
                'enabled',
                'position',
                'version',
                'config_source',
            ],
        )
        == {
            **utils.fields(
                body['metrics_group'],
                [
                    'title',
                    'description',
                    'owners',
                    'scopes',
                    'is_collapsed',
                    'enabled',
                    'position',
                ],
            ),
            **{'config_source': body['metrics_group']['config'], 'version': 1},
        }
    )

    assert stq.abt_index_precomputes.times_called == 1
    stq_call = stq.abt_index_precomputes.next_call()
    assert stq_call['queue'] == 'abt_index_precomputes'
    assert stq_call['id'] == (
        f'precomputes_table/hahn.//home/testsuite/precomputes/'
        f'{metrics_group["id"]}'
    )
    assert stq_call['args'] == ['hahn', '//home/testsuite/precomputes']
    assert stq_call['kwargs'] == {'metrics_group_id': metrics_group['id']}

    assert stq.abt_update_docs.times_called == 1
    stq_docs_call = stq.abt_update_docs.next_call()
    assert stq_docs_call['queue'] == 'abt_update_docs'
    assert stq_docs_call['args'] == []
    assert stq_docs_call['kwargs'] == {}


@pytest.mark.config(
    ABT_AVAILABLE_SCOPES=[
        {'scope': 'scope_for_create', 'description': 'dummy'},
    ],
)
async def test_with_existing_precomputes_table(
        abt, build_create_request, invoke_handler, stq,
):
    await abt.state.add_precomputes_table()

    body, config = build_create_request()

    await invoke_handler(body=body)

    assert await abt.pg.metrics_groups.count() == 1
    assert await abt.pg.precomputes_tables.count() == 1

    precomputes_table = await abt.pg.precomputes_tables.first()

    assert (
        utils.fields(
            precomputes_table, ['yt_cluster', 'yt_path'], as_tuple=True,
        )
        == utils.fields(
            config['precomputes'][0]['storage']['yt'][0],
            ['cluster', 'path'],
            as_tuple=True,
        )
    )

    assert stq.abt_index_precomputes.has_calls is False


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
