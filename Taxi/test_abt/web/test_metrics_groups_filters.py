import pytest

from test_abt.helpers import web as web_helpers


@pytest.fixture(name='invoke_handler')
def _invoke_handler(taxi_abt_web):
    return web_helpers.create_invoke(
        'get', '/v1/metrics_groups/filters', taxi_abt_web,
    )


@pytest.mark.config(
    ABT_AVAILABLE_SCOPES=[
        {'scope': 'taxi', 'description': 'taxi scope'},
        {'scope': 'eats', 'description': 'eda scope'},
    ],
)
async def test_get_scopes(invoke_handler):
    got = await invoke_handler()

    assert got == {
        'scopes': [
            {'scope': 'eats', 'description': 'eda scope'},
            {'scope': 'taxi', 'description': 'taxi scope'},
        ],
    }
