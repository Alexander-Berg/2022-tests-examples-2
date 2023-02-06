import pytest

from . import utils

EATER_ID = 'eater2'
MENU_ITEM_ID = 232323


@pytest.mark.config(EATS_CART_METRICS_UPDATE_INTERVAL_SEC=120)
async def test_db_metrics_collector_dynamic_change(
        taxi_eats_cart, local_services, testpoint,
):
    @testpoint('eats-cart-collect-statistics')
    def task_finished(data):
        return data

    await taxi_eats_cart.enable_testpoints()
    await taxi_eats_cart.run_task('distlock/db-metrics-collector')

    response = await task_finished.wait_call()

    assert response['data']['new_created_carts'] == 0

    local_services.set_place_slug('place123')
    post_item_body = dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES)
    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(EATER_ID),
        json=post_item_body,
    )

    assert response.status_code == 200

    await taxi_eats_cart.run_task('distlock/db-metrics-collector')
    response = await task_finished.wait_call()
    assert response['data']['new_created_carts'] == 1
