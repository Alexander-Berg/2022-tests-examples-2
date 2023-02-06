import asynctest
import pytest

from eats_integration_offline_orders.components.pos import (
    base_client as base_pos_client,
)


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'tables.sql', 'orders.sql'],
)
@pytest.mark.parametrize(
    'pos_status, response_status', [(200, 200), (400, 400), (500, 500)],
)
async def test_loyalty_apply_return_200(
        web_app_client,
        pos_client_mock,
        order_uuid,
        pos_status,
        response_status,
):

    pos_client_mock.apply_loyalty = asynctest.CoroutineMock(
        return_value=base_pos_client.POSResponse(status=pos_status),
    )

    response = await web_app_client.post(
        f'/v1/loyalty/apply',
        json={
            'order_uuid': order_uuid,
            'loyalty_identifier': 'loyalty_identifier__1',
        },
    )

    assert response.status == response_status
    assert pos_client_mock.apply_loyalty.called
