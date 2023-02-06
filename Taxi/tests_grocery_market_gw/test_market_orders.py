async def test_market_orders_200(
        taxi_grocery_market_gw, mockserver, market_checkouter,
):
    """Proxies ref_orders to market. Gets a lot of info, cherry-picks
    item pictures and a few other fields and returns them."""
    ref_orders = market_checkouter.get_order_ids()

    response = await taxi_grocery_market_gw.post(
        'lavka/v1/market-gw/v1/market/orders',
        json={'ref_orders': ref_orders},
        headers={'X-Yandex-UID': '12345', 'X-YaTaxi-Session': 'taxi: 1'},
    )
    assert response.status == 200
    response_json = response.json()
    assert len(ref_orders) == len(response_json['orders'])
    for order in response_json['orders']:
        assert 'ref_order' in order
        for item in order['items']:
            assert len(item['image_urls']) == 1
            assert 'id' in item
            assert item['count'] == 1
            assert 'title' in item


async def test_market_orders_not_found(
        taxi_grocery_market_gw, mockserver, market_checkouter,
):
    ref_orders = ['1', '2', '3']

    response = await taxi_grocery_market_gw.post(
        'lavka/v1/market-gw/v1/market/orders',
        json={'ref_orders': ref_orders},
        headers={'X-Yandex-UID': '12345', 'X-YaTaxi-Session': 'taxi: 1'},
    )
    assert response.status == 200
    assert response.json() == {'orders': []}


async def test_market_orders_no_ref_orders(
        taxi_grocery_market_gw, mockserver, market_checkouter,
):
    ref_orders = []
    response = await taxi_grocery_market_gw.post(
        'lavka/v1/market-gw/v1/market/orders',
        json={'ref_orders': ref_orders},
        headers={'X-Yandex-UID': '12345', 'X-YaTaxi-Session': 'taxi: 1'},
    )
    assert response.status == 200
    assert response.json() == {'orders': []}


async def test_market_orders_no_picture(
        taxi_grocery_market_gw, mockserver, market_checkouter, load_json,
):
    market_response = load_json('sample_market_order_response.json')
    order_id = market_response['orders'][0]['id']
    print(order_id)
    market_response['orders'][0]['items'][0]['pictures'][0].pop('url')
    print(market_response)
    market_checkouter.set_checkouter_response(new_response=market_response)

    ref_orders = market_checkouter.get_order_ids()
    print(ref_orders)
    response = await taxi_grocery_market_gw.post(
        'lavka/v1/market-gw/v1/market/orders',
        json={'ref_orders': ref_orders},
        headers={'X-Yandex-UID': '12345', 'X-YaTaxi-Session': 'taxi: 1'},
    )
    assert response.status == 200
    response_json = response.json()
    print(response_json)
    no_image_url_order = next(
        (
            order
            for order in response_json['orders']
            if order['ref_order'] == str(order_id)
        ),
        None,
    )
    assert 'image_urls' in no_image_url_order['items'][0]
    assert not no_image_url_order['items'][0]['image_urls']
