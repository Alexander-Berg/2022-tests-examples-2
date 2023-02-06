import aiohttp.web
import pytest

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from corp_billing_orders_plugins.generated_tests import *  # noqa


# Every service must have this handler
@pytest.mark.config(CORP_BILLING_ORDERS_SYNC_ENABLED=True)
@pytest.mark.servicetest
async def test_ping(
        mockserver,
        taxi_corp_billing_orders,
        billing_docs_service,
        billing_accounts_service,
):
    dummy_docs_service = billing_docs_service(keep_history=False)  # noqa: F841
    dummy_accs_service = (  # noqa: F841 E501,  pylint: disable=C0301
        billing_accounts_service(keep_history=False)
    )

    @mockserver.json_handler('/corp-billing-orders/internal/order/process')
    async def handler(request):  # pylint: disable=W0612
        response = await taxi_corp_billing_orders.post(
            '/internal/order/process', json=request.json,
        )
        if response.status_code == 200:
            return response.json()
        return aiohttp.web.Response(
            status=response.status_code, text=response.text,
        )

    response = await taxi_corp_billing_orders.get('ping')
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''
