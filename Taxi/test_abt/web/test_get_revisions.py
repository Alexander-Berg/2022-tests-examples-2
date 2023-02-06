import pytest

from abt import consts as app_consts
from test_abt.helpers import web as web_helpers


@pytest.fixture(name='invoke_handler')
def _invoke_handler(taxi_abt_web, mockserver, load_json):
    @mockserver.json_handler('/taxi-exp/v1/history/')
    def _history_request(request):
        return mockserver.make_response(
            json=load_json('taxi_exp_history_resp.json'), status=200,
        )

    return web_helpers.create_invoke('get', '/v1/revisions', taxi_abt_web)


async def test_revision_not_found(invoke_handler):
    got = await invoke_handler(
        params={'revision_id': 100500}, expected_code=404,
    )

    assert got['code'] == app_consts.CODE_404


async def test_get_revisions(abt, invoke_handler, load_json):
    await abt.state.add_precomputes_table()
    await abt.state.add_experiment()
    revision = await abt.state.add_revision()

    got = await invoke_handler(
        params={'revision_id': revision['revision_id']}, expected_code=200,
    )

    assert got == load_json('get_revisions_response_ok.json')
