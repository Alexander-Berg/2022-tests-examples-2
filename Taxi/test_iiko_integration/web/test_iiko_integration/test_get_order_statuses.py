import dataclasses
from typing import Any
from typing import Dict
from typing import Optional

import pytest

from test_iiko_integration import stubs


@dataclasses.dataclass
class OrderStatusesRequest:
    api_key: str
    json: Dict[str, Any]


@dataclasses.dataclass
class ExpectedResponse:
    status: int
    json: Optional[Dict[str, Any]] = None


@pytest.mark.config(
    IIKO_INTEGRATION_ORDER_STATUS_POLLING_DELAY=3,
    **stubs.RESTAURANT_INFO_CONFIGS,
)
@pytest.mark.now('2020-02-25T18:50:00')
@pytest.mark.parametrize(
    ['order_statuses_request', 'expected_response'],
    [
        pytest.param(
            OrderStatusesRequest(
                api_key=stubs.ApiKey.RESTAURANT_01,
                json={
                    'order_ids': [
                        '01',
                        '02',
                        '03',
                        '04',
                        '05',
                        '06',
                        '07',
                        '08',
                        '09',
                        '10',
                        '11',
                    ],
                },
            ),
            ExpectedResponse(
                status=200,
                json={
                    'order_statuses': [
                        {'order_id': '01', 'status': 'PENDING'},
                        {'order_id': '02', 'status': 'NOT_FOUND'},
                        {'order_id': '03', 'status': 'CANCELED'},
                        {'order_id': '04', 'status': 'CLOSED'},
                        {'order_id': '05', 'status': 'PENDING'},
                        {'order_id': '06', 'status': 'PAID'},
                        {'order_id': '07', 'status': 'PAYMENT_CONFIRMED'},
                        {'order_id': '08', 'status': 'PENDING'},
                        {'order_id': '09', 'status': 'PAYMENT_CONFIRMED'},
                        {'order_id': '10', 'status': 'PAYMENT_CONFIRMED'},
                        {'order_id': '11', 'status': 'EXPIRED'},
                    ],
                    'retry_after': 3,
                },
            ),
        ),
        pytest.param(
            OrderStatusesRequest(
                api_key=stubs.ApiKey.INVALID, json={'order_ids': []},
            ),
            ExpectedResponse(status=403),
        ),
    ],
)
async def test_get_order_statuses(
        web_app_client,
        order_statuses_request: OrderStatusesRequest,
        expected_response: ExpectedResponse,
):
    target_url = '/external/v1/orders/status/list'
    headers = {'X-YaTaxi-Api-Key': order_statuses_request.api_key}
    response = await web_app_client.post(
        target_url, headers=headers, json=order_statuses_request.json,
    )
    assert response.status == expected_response.status
    if expected_response.json is not None:
        response_json = await response.json()
        assert response_json == expected_response.json
