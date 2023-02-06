import pytest

from tests_grocery_cart.plugins import keys

NOW = '2020-03-13T07:19:00+00:00'


@pytest.fixture(name='grocery_eta')
def _grocery_eta(mockserver):
    class Context:
        def __init__(self):
            self.umlaas_grocery_eta_times_called = 0
            self.request_id = None

        def set_request_id(self, request_id):
            self.request_id = request_id

    context = Context()

    @mockserver.json_handler(
        '/umlaas-grocery-eta/internal/umlaas-grocery-eta/v1/delivery-eta',
    )
    def _umlaas_grocery_eta(request):
        context.umlaas_grocery_eta_times_called += 1
        assert request.query['offer_id'] == context.request_id
        return {
            'total_time': 0,
            'cooking_time': 0,
            'delivery_time': 0,
            'promise': {'min': 10 * 60, 'max': 20 * 60},
        }

    return context


@pytest.mark.now(NOW)
@pytest.mark.config(
    GROCERY_SURGE_CLIENT_CACHE_SETTINGS={'calculated_surge_info_ttl': 100},
)
@pytest.mark.parametrize(
    'test_handler',
    [
        '/internal/v2/cart/checkout',
        '/lavka/v1/cart/v1/retrieve',
        '/lavka/v1/cart/v1/update',
        '/lavka/v1/cart/v1/apply-promocode',
    ],
)
async def test_basic(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        grocery_eta,
        test_handler,
        grocery_surge,
        offers,
        now,
        grocery_depots,
        taxi_config,
):
    item_id = 'item_id_1'
    quantity = 1
    price = '5.30'
    legacy_depot_id = '100'
    depot_id = 'depot-id'
    currency = 'RUB'
    delivery_zone_type = 'pedestrian'
    offer_id = 'some_offer_id'

    grocery_eta.set_request_id(offer_id)

    offers.add_offer_elementwise(
        offer_id=offer_id,
        offer_time=now,
        depot_id=depot_id,
        location=keys.DEFAULT_DEPOT_LOCATION,
    )

    grocery_depots.add_depot(
        100,
        legacy_depot_id=legacy_depot_id,
        depot_id=depot_id,
        currency=currency,
        location=keys.DEFAULT_DEPOT_LOCATION,
    )
    overlord_catalog.add_depot(
        legacy_depot_id=legacy_depot_id,
        depot_id=depot_id,
        currency=currency,
        location=keys.DEFAULT_DEPOT_LOCATION,
    )
    overlord_catalog.add_location(
        legacy_depot_id=legacy_depot_id,
        location=keys.DEFAULT_DEPOT_LOCATION,
        zone_type=delivery_zone_type,
    )
    overlord_catalog.add_product(
        product_id=item_id, price=price, in_stock=str(quantity),
    )

    grocery_surge.add_record(
        legacy_depot_id=depot_id,
        timestamp=NOW,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    await taxi_grocery_cart.invalidate_caches()

    await cart.modify(
        {item_id: {'q': quantity, 'p': price}}, currency=currency,
    )

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': offer_id,
        'items': [
            {
                'id': item_id,
                'price': price,
                'quantity': str(quantity),
                'currency': currency,
            },
        ],
    }

    headers = {
        'X-Idempotency-Token': 'checkout-token',
        'X-YaTaxi-Session': 'taxi:1234',
        'X-Request-Language': 'ru',
        'X-Request-Application': 'app_name=android',
    }
    response = await taxi_grocery_cart.post(
        test_handler, headers=headers, json=json,
    )
    assert response.status_code == 200
    assert grocery_eta.umlaas_grocery_eta_times_called == 2
