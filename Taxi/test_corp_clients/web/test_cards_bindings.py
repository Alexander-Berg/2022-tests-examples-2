# pylint: disable=redefined-outer-name
from aiohttp import web
import pytest


@pytest.fixture
def mock_trust_bindings_429(mock_yb_trust_payments):
    @mock_yb_trust_payments('/bindings')
    async def _handler(request):
        return web.json_response(
            {'status_code': 'too_many_active_bindings', 'status': 'error'},
            status=500,
        )

    return _handler


async def test_cards_bindings_post(
        web_app_client,
        load_json,
        mock_trust_bindings,
        mock_trust_bindings_start,
):
    response = await web_app_client.post(
        '/v1/cards/bindings',
        json={'currency': 'ILS'},
        params={'client_id': 'client_id_1'},
        headers={'X-Request-Language': 'en'},
    )

    assert response.status == 200


async def test_cards_bindings_post_429(
        web_app_client,
        load_json,
        mock_trust_bindings_429,
        mock_trust_bindings_start,
):
    response = await web_app_client.post(
        '/v1/cards/bindings',
        json={'currency': 'ILS'},
        params={'client_id': 'client_id_1'},
        headers={'X-Request-Language': 'en'},
    )

    assert response.status == 429
