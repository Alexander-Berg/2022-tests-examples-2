import pytest

# pylint: disable=invalid-name
pytestmark = [pytest.mark.experiments3(filename='experiments3_defaults.json')]

HEADERS = {
    'X-SDK-Client-ID': 'taxi.test',
    'X-SDK-Version': '10.10.10',
    'X-Yandex-UID': '111111',
    'X-YaTaxi-Pass-Flags': 'portal,cashback-plus',
    'X-Request-Language': 'ru',
    'X-Remote-IP': '185.15.98.233',
}


@pytest.mark.parametrize(
    'mediabilling_status, result_status, sync_features',
    [
        ('ok', 'success', True),
        ('ok', 'pending', False),
        ('ok', 'success', None),
        ('refund', 'success', True),
        ('refund', 'pending', False),
        ('refund', 'success', None),
        ('cancelled', 'failure', True),
        ('pending', 'pending', True),
        ('fail-3ds', 'failure', True),
        ('error', 'failure', True),
    ],
)
async def test_purchase_status_billing_resp(
        taxi_plus_sweet_home,
        mockserver,
        mediabilling_status,
        result_status,
        sync_features,
):
    @mockserver.json_handler(
        '/mediabilling/internal-api/account/billing/order-info',
    )
    def _mock_billing_order_info(request):
        resp = {'status': mediabilling_status, 'orderId': 1000}
        if sync_features is not None:
            resp['synchronizationState'] = {'featuresSync': sync_features}
        return {'result': resp}

    response = await taxi_plus_sweet_home.get(
        '/4.0/sweet-home/v1/subscriptions/purchase/status',
        params={'purchase_id': '123456789'},
        headers=HEADERS,
    )

    assert response.status_code == 200
    content = response.json()
    assert content['status'] == result_status


async def test_mediabillling_404_ok(taxi_plus_sweet_home, mockserver):
    @mockserver.json_handler(
        '/mediabilling/internal-api/account/billing/order-info',
    )
    def _mock_billing_order_info(request):
        return mockserver.make_response(status=404)

    response = await taxi_plus_sweet_home.get(
        '/4.0/sweet-home/v1/subscriptions/purchase/status',
        params={'purchase_id': '123456789'},
        headers=HEADERS,
    )

    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'failure'
