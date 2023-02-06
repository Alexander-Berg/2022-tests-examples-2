import dataclasses
from typing import Optional

import pytest

from test_iiko_integration import stubs


@dataclasses.dataclass
class ExpectedResponse:
    status: int
    payload: Optional[dict] = None
    cashback: Optional[str] = None


@pytest.mark.config(**stubs.RESTAURANT_INFO_CONFIGS)
@pytest.mark.parametrize(
    ['held', 'cleared', 'order_id', 'expected_response'],
    [
        pytest.param(
            '95.55',
            '204.45',
            'one_percent_cashback',
            ExpectedResponse(
                status=200,
                cashback='3',
                payload={
                    'service_id': '645',
                    'order_id': 'one_percent_cashback',
                    'amount': '3',
                    'base_amount': '300.00',
                    'has_plus': 'True',
                    'commission_percent': '10',
                    'cashback_service': 'qr_restaurant',
                    'cashback_type': 'transaction',
                },
            ),
            id='held and cleared is not zero',
        ),
        pytest.param(
            '95.55',
            '204.45',
            'with_complement',
            ExpectedResponse(status=409),
            id='order with complement payment method',
        ),
        pytest.param(
            '0',
            '300',
            'one_percent_cashback',
            ExpectedResponse(
                status=200,
                cashback='3',
                payload={
                    'service_id': '645',
                    'order_id': 'one_percent_cashback',
                    'amount': '3',
                    'base_amount': '300',
                    'has_plus': 'True',
                    'commission_percent': '10',
                    'cashback_service': 'qr_restaurant',
                    'cashback_type': 'transaction',
                },
            ),
            id='held is zero',
        ),
        pytest.param(
            '300',
            '0',
            'one_percent_cashback',
            ExpectedResponse(
                status=200,
                cashback='3',
                payload={
                    'service_id': '645',
                    'order_id': 'one_percent_cashback',
                    'amount': '3',
                    'base_amount': '300',
                    'has_plus': 'True',
                    'commission_percent': '10',
                    'cashback_service': 'qr_restaurant',
                    'cashback_type': 'transaction',
                },
            ),
            id='cleared is zero',
        ),
        pytest.param(
            '0.0',
            '0.0',
            'one_percent_cashback',
            ExpectedResponse(
                status=200,
                cashback='0',
                payload={
                    'service_id': '645',
                    'order_id': 'one_percent_cashback',
                    'amount': '0',
                    'base_amount': '0.0',
                    'has_plus': 'True',
                    'commission_percent': '10',
                    'cashback_service': 'qr_restaurant',
                    'cashback_type': 'transaction',
                },
            ),
            id='held and cleared is zero',
        ),
        pytest.param(
            '95.55',
            '204.45',
            'no_cashback',
            ExpectedResponse(status=409),
            id='zero percent cashback order',
        ),
        pytest.param(
            '95.55',
            '204.45',
            'NON-EXISTING',
            ExpectedResponse(status=409),
            id='order doesnt exist',
        ),
        pytest.param(
            '-95.55',
            '-204.45',
            'restaurantid_orderid',
            ExpectedResponse(status=400),
            id='held and cleared is negative',
        ),
        pytest.param(
            'cat',
            'dog',
            'restaurantid_orderid',
            ExpectedResponse(status=400),
            id='held and cleared is not number',
        ),
    ],
)
async def test_get_cashback(
        mockserver,
        web_app_client,
        held: str,
        cleared: str,
        order_id: str,
        expected_response: ExpectedResponse,
):
    @mockserver.json_handler('/user_api-api/users/get')
    def _user_get(req):
        return {'has_ya_plus': True}

    response = await web_app_client.post(
        f'/v1/cashback?order_id={order_id}',
        json={'held': held, 'cleared': cleared, 'currency': 'rub'},
    )
    assert response.status == expected_response.status
    if expected_response.cashback is not None:
        body = await response.json()
        assert body['cashback'] == expected_response.cashback
        assert body['payload'] == expected_response.payload
