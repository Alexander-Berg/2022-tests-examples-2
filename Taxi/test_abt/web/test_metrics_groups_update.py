import pytest

from abt import consts as app_consts
from abt import models
from test_abt import utils
from test_abt.helpers import web as web_helpers


@pytest.fixture(name='invoke_handler')
def _invoke_handler(taxi_abt_web):
    return web_helpers.create_invoke('put', '/v1/metrics_groups', taxi_abt_web)


@pytest.mark.config(
    ABT_AVAILABLE_SCOPES=[
        {'scope': 'scope_for_update', 'description': 'dummy'},
    ],
)
async def test_update_success(
        yt_apply, abt, build_update_request, invoke_handler, stq,
):
    await abt.state.add_precomputes_table()

    metrics_group = models.MetricsGroup.from_record(
        await abt.state.add_metrics_group(),
    )
    body, config = build_update_request(metrics_group)

    assert (
        await invoke_handler(
            params={'metrics_group_id': metrics_group.id}, body=body,
        )
        == {}
    )

    metrics_group_updated = await abt.pg.metrics_groups.by_id(metrics_group.id)

    assert (
        utils.fields(
            metrics_group_updated,
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
            **{
                'config_source': body['metrics_group']['config'],
                'version': metrics_group.version + 1,
            },
        }
    )

    linked_precomputes_tables = await abt.pg.mg_pt.fetch_by_query(
        f"""
        SELECT precomputes_tables_id
        FROM abt.{abt.pg.mg_pt.table_name}
        WHERE metrics_groups_id = {metrics_group.id}
        """,
    )

    assert len(linked_precomputes_tables) == 1

    precomputes_table = await abt.pg.precomputes_tables.by_id(
        linked_precomputes_tables[0]['precomputes_tables_id'],
    )

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

    assert stq.abt_update_docs.times_called == 1
    stq_docs_call = stq.abt_update_docs.next_call()
    assert stq_docs_call['queue'] == 'abt_update_docs'
    assert stq_docs_call['args'] == []
    assert stq_docs_call['kwargs'] == {}


async def test_update_not_found(abt, build_update_request, invoke_handler):
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
