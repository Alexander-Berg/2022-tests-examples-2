# pylint: disable=too-many-lines
import pytest

from tests_eats_orders_info import utils

BDU_ORDER_URL = '/eats/v1/orders-info/v1/order'


@pytest.mark.config(EATS_ORDERS_INFO_RECEIPTS_ENABLED={'enabled': True})
@pytest.mark.config(EATS_ORDERS_INFO_USE_GROCERY_FOR_ORDER=True)
@utils.order_details_titles_config3()
async def test_only_grocery_order(
        taxi_eats_orders_info, mockserver, load_json, grocery_order,
):
    @mockserver.json_handler(
        f'eats-core-orders/internal-api/v1/order/{utils.ORDER_NR_ID}/metainfo',
    )
    def core_order_info(request):
        return mockserver.make_response(status=404, json=None)

    @mockserver.json_handler(
        'persey-payments/internal/v1/charity/multibrand/ride_donations',
    )
    def ride_donations(request):
        return mockserver.make_response(status=404, json=None)

    response = await taxi_eats_orders_info.get(
        BDU_ORDER_URL,
        params={'order_nr': utils.ORDER_NR_ID},
        headers=utils.get_auth_headers(),
    )
    assert core_order_info.times_called == 1
    assert grocery_order.times_called_info() == 1
    assert ride_donations.times_called == 1
    assert response.status_code == 200
    assert response.json() == load_json('grocery_order.json')


@pytest.mark.config(EATS_ORDERS_INFO_USE_GROCERY_FOR_ORDER=True)
async def test_no_grocery_order(taxi_eats_orders_info, mockserver, load_json):
    @mockserver.json_handler(
        f'eats-core-orders/internal-api/v1/order/{utils.ORDER_NR_ID}/metainfo',
    )
    def core_order_info(request):
        return mockserver.make_response(status=404, json=None)

    @mockserver.json_handler(
        'persey-payments/internal/v1/charity/multibrand/ride_donations',
    )
    def ride_donations(request):
        return mockserver.make_response(status=404, json=None)

    @mockserver.json_handler(
        '/grocery-eats-gateway/internal/grocery-eats-gateway/v1/order',
    )
    def grocery_eats_gateway(request):
        return mockserver.make_response(status=404, json=None)

    response = await taxi_eats_orders_info.get(
        BDU_ORDER_URL,
        params={'order_nr': utils.ORDER_NR_ID},
        headers=utils.get_auth_headers(),
    )

    assert core_order_info.times_called == 1
    assert grocery_eats_gateway.times_called == 1
    assert ride_donations.times_called == 0
    assert response.status_code == 404
