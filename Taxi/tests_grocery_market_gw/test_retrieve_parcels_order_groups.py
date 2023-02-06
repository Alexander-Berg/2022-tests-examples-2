import datetime

NOW = datetime.datetime.fromisoformat('2022-04-09T10:00:00+00:00')
PARCELS_RESPONSE = {
    'order_groups': [
        {
            'orders': [
                {
                    'ref_order': 'ref-order-000002',
                    'vendor': 'vendor-000001',
                    'token': 'some-token',
                },
                {
                    'ref_order': 'ref-order-000001',
                    'vendor': 'vendor-000001',
                    'token': 'some-token',
                },
            ],
            'legacy_depot_id': '123',
            'customer_location': [37.1, 55.2],
            'state': 'in_depot',
            'has_paid_delivery': True,
        },
        {
            'orders': [
                {
                    'ref_order': 'ref-order-000006',
                    'vendor': 'vendor-000001',
                    'token': 'some-token',
                },
            ],
            'grocery_order_id': '00000000000000000000000000000001-grocery',
            'state': 'delivered',
        },
    ],
}


def _set_surge_conditions(experiments3, delivery_conditions=None):
    value = {
        'data': [
            {
                'payload': {'delivery_conditions': delivery_conditions},
                'timetable': [
                    {'to': '24:00', 'from': '00:00', 'day_type': 'everyday'},
                ],
            },
        ],
        'enabled': True,
    }

    experiments3.add_config(
        name='grocery-surge-delivery-conditions',
        consumers=['grocery-surge-client/surge'],
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': value,
            },
        ],
    )


async def test_retrieve_groups(
        taxi_grocery_market_gw,
        mockserver,
        offers,
        grocery_surge,
        grocery_depots,
        experiments3,
):
    """ Proxy uid to tristero-parcels and return tristero response with
         mild change of several field's names and pricing
        conditions from surger. """

    delivery_conditions = [
        {'order_cost': '0', 'delivery_cost': '10'},
        {'order_cost': '25', 'delivery_cost': '5'},
        {'order_cost': '50', 'delivery_cost': '0'},
    ]
    _set_surge_conditions(experiments3, delivery_conditions)

    parcels_response = PARCELS_RESPONSE

    grocery_depots.add_depot(depot_test_id=123)

    timestamp = NOW.isoformat()
    grocery_surge.add_record(
        legacy_depot_id='123',
        timestamp=timestamp,
        pipeline='calc_surge_grocery_v1',
        load_level=1,
    )

    await taxi_grocery_market_gw.invalidate_caches()

    @mockserver.json_handler(
        'tristero-parcels/internal/v1/parcels/v1/retrieve-order-groups',
    )
    def _mock_parcels_retrieve_groups(request):
        assert 'X-Yandex-UID' in request.headers
        return parcels_response

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/market-gw/v1/parcels/retrieve-orders',
        json={},
        headers={'X-Yandex-UID': '12345'},
    )

    response_json = response.json()
    print(response_json)
    assert response.status == 200
    assert len(response_json['order_groups']) == 2
    for order in response_json['order_groups'][0]['orders']:
        assert order['order_id'] in [
            order['ref_order']
            for order in PARCELS_RESPONSE['order_groups'][0]['orders']
        ]

    assert 'offer_id' in response_json['order_groups'][0]
    assert (
        response_json['order_groups'][0]['pricing_conditions'][
            'service_fee_value'
        ]
        == delivery_conditions[0]['delivery_cost']
    )
