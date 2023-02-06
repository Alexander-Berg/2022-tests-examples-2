import pytest

from abt import consts as app_consts
from abt import models
from test_abt.helpers import web as web_helpers


@pytest.fixture(name='invoke_handler')
def _invoke_handler(taxi_abt_web):
    return web_helpers.create_invoke(
        'get', '/v1/metrics_groups/retrieve', taxi_abt_web,
    )


async def test_response_fields(abt, invoke_handler):
    metrics_group = models.MetricsGroup.from_record(
        await abt.state.add_metrics_group(),
    )

    got = await invoke_handler(params={'metrics_group_id': metrics_group.id})

    assert got == {
        'metrics_group': {
            'id': metrics_group.id,
            'title': metrics_group.title,
            'description': metrics_group.description,
            'owners': metrics_group.owners,
            'scopes': metrics_group.scopes,
            'is_collapsed': metrics_group.is_collapsed,
            'enabled': metrics_group.enabled,
            'updated_at': metrics_group.updated_at_timestring,
            'created_at': metrics_group.created_at_timestring,
            'version': metrics_group.version,
            'position': metrics_group.position,
            'config': metrics_group.config_source,
        },
    }


async def test_not_found(invoke_handler):
    got = await invoke_handler(
        params={'metrics_group_id': 100500}, expected_code=404,
    )

    assert got['code'] == app_consts.CODE_404


async def test_json_config_converted(abt, invoke_handler):
    config_builder = (
        abt.builders.get_mg_config_builder()
        .add_value_metric()
        .add_precomputes()
    )

    metrics_group = models.MetricsGroup.from_record(
        await abt.state.add_metrics_group(config=config_builder.build()),
    )

    got = await invoke_handler(params={'metrics_group_id': metrics_group.id})

    assert got['metrics_group']['config'] == config_builder.build_yaml()
