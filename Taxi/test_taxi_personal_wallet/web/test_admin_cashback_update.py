from aiohttp import test_utils
from aiohttp import web
import pytest


@pytest.fixture(name='mock_plus_transactions_happy')
def _mock_plus_transactions_happy(mockserver):
    @mockserver.handler(
        '/plus-transactions/plus-transactions/v1/cashback/update',
    )
    async def _handle(request):
        return web.json_response(status=200)


@pytest.mark.client_experiments3(
    consumer='taxi_personal_wallet/admin/cashback/topup',
    experiment_name='personal_wallet_admin_enable_topup_cashback_on_wallet',
    args=[{'name': 'yandex_uid', 'type': 'string', 'value': '1111111'}],
    value={},
)
@pytest.mark.config(
    PERSONAL_WALLET_ADMIN_ADD_POINTS_PAYLOAD={
        'service_id': '1111',
        'consumer': 'consumer',
        'version': 1,
        'payload': {
            'order_id': '1qaz!QAZ',
            'cashback_service': 'yataxi',
            'cashback_type': 'type',
            'service_id': '123',
            'issuer': 'issuer',
            'campaign_name': 'name',
            'ticket': 'ticket',
            'has_plus': 'true',
            'product_id': 'product',
        },
    },
)
async def test_topup_happy_path(
        web_app_client: test_utils.TestClient, mock_plus_transactions_happy,
):
    body = {'yandex_uid': '1111111', 'amount': 150.5, 'currency': 'RUB'}
    response = await web_app_client.post('/v1/admin/cashback/topup', json=body)
    assert response.status == 200

    response_data = await response.json()

    assert response_data['status'] == 'success'


async def test_topup_disabled_by_exp(
        web_app_client: test_utils.TestClient, mock_plus_transactions_happy,
):

    body = {'yandex_uid': '1111111', 'amount': 150.5, 'currency': 'RUB'}
    response = await web_app_client.post('/v1/admin/cashback/topup', json=body)
    assert response.status == 503
