import pytest

from abt import consts as app_consts
from abt import models
from test_abt.helpers import web as web_helpers


@pytest.fixture(name='invoke_handler')
def _invoke_handler(taxi_abt_web):
    return web_helpers.create_invoke(
        'delete', '/v1/metrics_groups', taxi_abt_web,
    )


async def test_delete_success(abt, invoke_handler, stq):
    metrics_group = models.MetricsGroup.from_record(
        await abt.state.add_metrics_group(),
    )

    got = await invoke_handler(params={'metrics_group_id': metrics_group.id})

    assert got == {}
    assert (await abt.pg.metrics_groups.by_id(metrics_group.id)) is None

    linked_precomputes_tables = await abt.pg.mg_pt.fetch_by_query(
        f"""
        SELECT precomputes_tables_id
        FROM abt.{abt.pg.mg_pt.table_name}
        WHERE metrics_groups_id = {metrics_group.id}
        """,
    )

    assert not linked_precomputes_tables

    assert stq.abt_update_docs.times_called == 1
    stq_docs_call = stq.abt_update_docs.next_call()
    assert stq_docs_call['queue'] == 'abt_update_docs'
    assert stq_docs_call['args'] == []
    assert stq_docs_call['kwargs'] == {}


async def test_update_not_found(abt, build_update_request, invoke_handler):
    got = await invoke_handler(
        params={'metrics_group_id': 100500}, expected_code=404,
    )

    assert got['code'] == app_consts.CODE_404
