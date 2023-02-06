import pytest

from abt import consts as app_consts
from test_abt.helpers import web as web_helpers


@pytest.fixture(name='invoke_handler')
def _invoke_handler(taxi_abt_web):
    return web_helpers.create_invoke('get', '/v1/facets', taxi_abt_web)


async def test_revision_not_found(invoke_handler):
    got = await invoke_handler(
        params={'revision_id': 100500}, expected_code=404,
    )

    assert got['code'] == app_consts.CODE_404


async def test_revisions_not_in_config(abt, invoke_handler):
    await abt.state.add_precomputes_table()
    await abt.state.add_experiment()
    revision = await abt.state.add_revision()
    await abt.state.add_facets('littlepony')

    got = await invoke_handler(
        params={'revision_id': revision['revision_id']}, expected_code=200,
    )

    assert got == {'facets': []}


@pytest.mark.config(
    ABT_FACETS_V2={
        'littlepony': {'description': 'dummy', 'title_key': 'some_tanker_key'},
    },
)
async def test_get_revisions(abt, invoke_handler):
    await abt.state.add_precomputes_table()
    await abt.state.add_experiment()
    revision = await abt.state.add_revision()
    await abt.state.add_facets('littlepony')

    got = await invoke_handler(
        params={'revision_id': revision['revision_id']}, expected_code=200,
    )

    assert got == {'facets': [{'facet': 'littlepony', 'title': 'littlepony'}]}
