import pytest

from . import utils

MENU_ITEM_ID = 232323
PRODUCT_ID = 2
PLACE_SLUG = 'place123'


def make_headers(eater_id):
    return {
        'X-YaTaxi-Session': 'eats:',
        'X-YaTaxi-Bound-UserIds': '',
        'X-YaTaxi-Bound-Sessions': '',
        'X-Eats-User': f'user_id={eater_id},',
    }


@pytest.mark.parametrize('eater_id', ['eater1', 'eater2'])
@pytest.mark.parametrize('has_min_cart', [True, False])
@pytest.mark.parametrize('min_order_price', [0, 170, 250])
@pytest.mark.pgsql('eats_cart', files=['insert_items.sql'])
@utils.setup_available_checkers(['CheckMinOrderSubtotal'])
async def test_validate_subtotal(
        taxi_eats_cart,
        local_services,
        load_json,
        eats_cart_cursor,
        min_order_price,
        has_min_cart,
        eater_id,
):
    eats_cart_cursor.execute(
        'SELECT sum(price) FROM eats_cart.cart_items '
        'WHERE cart_id=(SELECT id FROM eats_cart.carts '
        f'  WHERE eater_id = \'{eater_id}\')',
    )
    cart_subtotal = eats_cart_cursor.fetchone()[0]

    local_services.set_place_slug(PLACE_SLUG)
    local_services.eats_products_items_request = [
        str(PRODUCT_ID),
        str(MENU_ITEM_ID),
        '3',
    ]

    place_response = load_json('eats_catalog_internal_place.json')
    place_response['place']['delivery']['thresholds'] = [
        {'delivery_cost': '50', 'order_price': str(min_order_price)},
        {'delivery_cost': '20', 'order_price': '500'},
    ]
    local_services.catalog_place_response = place_response

    local_services.delivery_price_status = 200
    local_services.delivery_price_response = {
        'surge_result': {'placeId': 1},
        'service_fee': '15',
    }

    if has_min_cart:
        local_services.delivery_price_response['cart_delivery_price'] = {
            'min_cart': str(min_order_price),
            'delivery_fee': '500',
        }

    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )

    response = await utils.call_lock_cart(
        taxi_eats_cart, eater_id, make_headers(eater_id), False,
    )

    assert local_services.mock_eats_catalog.times_called == 1

    if min_order_price is None or min_order_price <= cart_subtotal:
        assert response.status_code == 200
        assert response.json()['applied_checkers'] == ['CheckMinOrderSubtotal']
        assert local_services.mock_eda_delivery_price.times_called == 2
    else:
        assert response.status_code == 400
        assert local_services.mock_eda_delivery_price.times_called == 1
        assert response.json() == {
            'code': 114,
            'domain': 'UserData',
            'err': 'error.minimal_order_price_not_exceeded',
            'payload': {},
        }


@pytest.mark.parametrize(
    'response_status', [200, 400, 500, 'NetworkError', 'Timeout'],
)
@pytest.mark.pgsql('eats_cart', files=['insert_items.sql'])
@utils.setup_available_checkers(['CheckMinOrderSubtotal'])
async def test_validate_subtotal_missing_thresholds(
        taxi_eats_cart, local_services, load_json, mockserver, response_status,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.eats_products_items_request = [
        str(PRODUCT_ID),
        str(MENU_ITEM_ID),
        '3',
    ]

    place_response = load_json('eats_catalog_internal_place.json')
    place_response['place']['delivery']['thresholds'] = []
    local_services.catalog_place_response = place_response

    @mockserver.json_handler(
        '/eda-delivery-price/internal/v1/cart-delivery-price-surge',
    )
    def _mock_eda_delivery_price(request):
        if response_status == 'NetworkError':
            raise mockserver.NetworkError()
        if response_status == 'Timeout':
            raise mockserver.TimeoutError()
        return mockserver.make_response(
            json={
                'error': 'error',
                'surge_result': {'placeId': 1},
                'service_fee': '15',
            },
            status=response_status,
        )

    local_services.eats_products_items_response = load_json(
        'eats_products_menu_items.json',
    )

    response = await utils.call_lock_cart(
        taxi_eats_cart, 'eater2', make_headers('eater2'), False,
    )

    has_response = response_status in (200, 400)
    assert _mock_eda_delivery_price.times_called == 2 if has_response else 1
    assert response.status_code == (200 if has_response else 500)

    if has_response:
        assert response.json()['applied_checkers'] == ['CheckMinOrderSubtotal']
