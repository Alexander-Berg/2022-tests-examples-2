from testsuite.utils import matching


async def test_orders_by_external_order_id(
        taxi_cargo_c2c, create_cargo_claims_orders, get_default_order_id,
):
    response = await taxi_cargo_c2c.post(
        '/v1/clients-orders',
        json={
            'order_id': get_default_order_id(),
            'order_provider_id': 'cargo-claims',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'orders': [
            {
                'id': {
                    'order_id': 'b1fe01ddc30247279f806e6c5e210a9f',
                    'order_provider_id': 'cargo-claims',
                    'phone_pd_id': 'phone_pd_id_1',
                },
                'sharing_key': matching.AnyString(),
                'sharing_url': matching.AnyString(),
                'roles': ['sender'],
                'user_id': 'user_id_1_2',
                'additional_delivery_description': {},
            },
            {
                'id': {
                    'order_id': 'b1fe01ddc30247279f806e6c5e210a9f',
                    'order_provider_id': 'cargo-claims',
                    'phone_pd_id': 'phone_pd_id_2',
                },
                'sharing_key': matching.AnyString(),
                'sharing_url': matching.AnyString(),
                'roles': ['recipient'],
                'user_id': 'user_id_2_2',
                'additional_delivery_description': {},
            },
            {
                'id': {
                    'order_id': 'b1fe01ddc30247279f806e6c5e210a9f',
                    'order_provider_id': 'cargo-claims',
                    'phone_pd_id': 'phone_pd_id_3',
                },
                'sharing_key': matching.AnyString(),
                'sharing_url': matching.AnyString(),
                'roles': ['recipient'],
                'additional_delivery_description': {},
            },
        ],
    }

    for order in response.json()['orders']:
        assert order['sharing_url'] == 'http://host/' + order['sharing_key']


async def test_intiator_order(taxi_cargo_c2c, create_cargo_c2c_orders, pgsql):
    order_id = await create_cargo_c2c_orders(add_user_default_tips=True)
    response = await taxi_cargo_c2c.post(
        '/v1/intiator-client-order', json={'cargo_c2c_order_id': order_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'user_id': 'some_user_id',
        'user_agent': 'some_agent',
        'offer_expectations': {
            'meters_to_arrive': 7067,
            'seconds_to_arrive': 778,
        },
        'tips': {'type': 'percent', 'value': 10},
    }


async def test_save_orders(taxi_cargo_c2c, get_default_order_id):
    request = {
        'orders': [
            {
                'id': {
                    'phone_pd_id': 'phone_pd_id_1',
                    'order_id': get_default_order_id(),
                    'order_provider_id': 'cargo-claims',
                },
                'roles': ['sender'],
            },
            {
                'id': {
                    'phone_pd_id': 'phone_pd_id_2',
                    'order_id': get_default_order_id(),
                    'order_provider_id': 'cargo-claims',
                },
                'roles': ['recipient'],
            },
            {
                'id': {
                    'phone_pd_id': 'phone_pd_id_3',
                    'order_id': get_default_order_id(),
                    'order_provider_id': 'cargo-claims',
                },
                'roles': ['recipient'],
            },
        ],
    }
    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-clients-orders', json=request,
    )
    assert response.status_code == 200
    assert response.json() == {
        'orders': [
            {
                'id': {
                    'order_id': get_default_order_id(),
                    'order_provider_id': 'cargo-claims',
                    'phone_pd_id': 'phone_pd_id_1',
                },
                'roles': ['sender'],
                'sharing_key': matching.AnyString(),
                'user_id': 'user_id_1_2',
                'additional_delivery_description': {},
            },
            {
                'id': {
                    'order_id': get_default_order_id(),
                    'order_provider_id': 'cargo-claims',
                    'phone_pd_id': 'phone_pd_id_2',
                },
                'roles': ['recipient'],
                'sharing_key': matching.AnyString(),
                'user_id': 'user_id_2_2',
                'additional_delivery_description': {},
            },
            {
                'id': {
                    'order_id': 'b1fe01ddc30247279f806e6c5e210a9f',
                    'order_provider_id': 'cargo-claims',
                    'phone_pd_id': 'phone_pd_id_3',
                },
                'roles': ['recipient'],
                'sharing_key': matching.AnyString(),
                'additional_delivery_description': {},
            },
        ],
    }
    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-clients-orders', json=request,
    )
    assert response.status_code == 200
    assert response.json() == {'orders': []}
