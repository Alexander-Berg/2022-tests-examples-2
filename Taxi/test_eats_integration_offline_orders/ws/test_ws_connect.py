import aiohttp
import pytest


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['pos_ws_tokens.sql', 'restaurants.sql'],
)
async def test_ws_connect(web_app_client, pos_ws_token, pos_ws_id):
    response = await web_app_client.ws_connect(
        f'/v1/ws?pos_id={pos_ws_id}', headers={'Authorization': pos_ws_token},
    )

    assert isinstance(response, aiohttp.ClientWebSocketResponse)
