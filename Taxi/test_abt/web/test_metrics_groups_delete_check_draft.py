import pytest

from abt import consts as app_consts
from abt import models
from test_abt.helpers import web as web_helpers


@pytest.fixture(name='invoke_handler')
def _invoke_handler(taxi_abt_web):
    return web_helpers.create_invoke(
        'delete', '/v1/metrics_groups/check-draft', taxi_abt_web,
    )


async def test_check_draft_success(abt, invoke_handler):
    metrics_group = models.MetricsGroup.from_record(
        await abt.state.add_metrics_group(),
    )

    got = await invoke_handler(params={'metrics_group_id': metrics_group.id})

    assert got == {
        'change_doc_id': f'delete/metrics_group/{metrics_group.id}',
        'data': {},
    }


async def test_check_draft_not_found(abt, invoke_handler):
    got = await invoke_handler(
        params={'metrics_group_id': 100500}, expected_code=404,
    )

    assert got['code'] == app_consts.CODE_404
