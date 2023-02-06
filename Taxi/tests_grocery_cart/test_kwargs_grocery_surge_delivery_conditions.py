import pytest

from tests_grocery_cart.plugins import keys


@pytest.mark.pgsql('grocery_cart', files=['eda_one_item.sql'])
@pytest.mark.config(GROCERY_SURGE_CLIENT_ENABLE_DISTANCE_CALC=True)
async def test_kwargs_grocery_surge_delivery_conditions(
        taxi_grocery_cart,
        overlord_catalog,
        grocery_p13n,
        offers,
        umlaas_eta,
        grocery_surge,
        now,
        grocery_depots,
        user_api,
        mockserver,
        experiments3,
):
    experiments3.add_config(
        name='grocery-surge-delivery-conditions',
        consumers=['grocery-surge-client/surge'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {
                    'data': [
                        {
                            'payload': {'delivery_conditions': None},
                            'timetable': [
                                {
                                    'to': '24:00',
                                    'from': '00:00',
                                    'day_type': 'everyday',
                                },
                            ],
                        },
                    ],
                    'enabled': True,
                },
            },
        ],
    )
    route_to_pin = 10
    exp3_recorder = experiments3.record_match_tries(
        'grocery-surge-delivery-conditions',
    )

    @mockserver.json_handler(
        '/grocery-routing/internal/grocery-routing/v1/route',
    )
    def _get_route(_request):
        return {'distance': route_to_pin, 'eta': 60}

    request_headers = {
        'X-YaTaxi-Session': 'eats:123',
        'X-YaTaxi-Bound-Sessions': 'taxi:1234',
        'X-Request-Language': 'ru',
        'X-Request-Application': 'app_name=android',
        'X-YaTaxi-User': 'personal_phone_id=phone-id,eats_user_id=12345',
        'X-Yandex-UID': 'yandex-uid',
    }

    depot_id = '100'
    offers.add_offer_elementwise(
        offer_id=keys.CREATED_OFFER_ID,
        offer_time=now,
        depot_id=depot_id,
        location=keys.DEFAULT_DEPOT_LOCATION,
    )

    grocery_surge.add_record(
        legacy_depot_id=depot_id,
        timestamp=keys.TS_NOW,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    umlaas_eta.add_prediction(13, 17)

    grocery_depots.add_depot(
        int(depot_id), location=keys.DEFAULT_DEPOT_LOCATION_OBJ,
    )
    overlord_catalog.add_depot(
        legacy_depot_id=depot_id, location=keys.DEFAULT_DEPOT_LOCATION,
    )
    overlord_catalog.add_product(
        product_id='item_id_1', price='100', in_stock='1234.5678',
    )

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        json={
            'position': keys.DEFAULT_POSITION,
            'cart_id': '8da556be-0971-4f3b-a454-d980130662cc',
            'cart_version': 1,
            'offer_id': 'test_offer_id',
        },
        headers=request_headers,
    )
    assert response.status_code == 200

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    matched_qwargs = match_tries[0].kwargs

    assert matched_qwargs['route_to_pin'] == route_to_pin
