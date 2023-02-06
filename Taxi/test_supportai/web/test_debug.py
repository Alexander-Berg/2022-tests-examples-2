import pytest

from supportai.common import agent as agent_module
from supportai.common import debug as debug_module


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai', files=['debug_info.sql']),
]


async def test_get_debug_from_db(web_app_client):
    response = await web_app_client.get(
        f'/v1/debug?project_slug=test_project&chat_id=1234&iteration_number=1',
    )
    assert response.status == 200


async def test_no_debug(web_app_client):
    response = await web_app_client.get(
        f'/v1/debug?project_slug=test_project&chat_id=1234&iteration_number=3',
    )
    assert response.status == 204


@pytest.mark.config(
    SUPPORTAI_DEBUG_SETTINGS={
        'default_debug_ttl_days': 1,
        'projects': ['test_project'],
    },
)
async def test_debug_refresh_cache(web_context):
    await web_context.supportai_debug_cache.refresh_cache()

    debug = debug_module.Debug('test_project')
    debug.init(web_context)
    await debug.save_debug(
        web_context,
        '456',
        1,
        agent_module.ApiFlags(simulated=False, mocked=False),
    )

    records = web_context.supportai_debug_cache.records_queue
    assert records.qsize() == 1

    await web_context.supportai_debug_cache.refresh_cache()

    records = web_context.supportai_debug_cache.records_queue
    assert records.empty()

    await debug.save_debug(
        web_context,
        '456',
        1,
        agent_module.ApiFlags(simulated=True, mocked=False),
    )

    records = web_context.supportai_debug_cache.records_queue
    assert records.empty()
