from grocery_tests import user_model


def _get_water_category(api, user, modes_root_json):
    category_tmp = [
        x
        for x in modes_root_json['products']
        if x['title'] == 'category.water.beverages_group.long_title'
    ]
    assert category_tmp
    category = category_tmp[0]

    response = api.modes_category(
        user, category['id'], modes_root_json['offer_id'],
    )
    assert response.status_code == 200
    response_json = response.json()

    assert 'modes' in response_json
    assert response_json['modes']

    assert 'products' in response_json
    assert response_json['products']

    return response.json()


def _set_payment(cart, offer_id, user, cart_json):
    response = cart.set_payment_method(
        offer_id,
        cart_json['cart_id'],
        cart_json['cart_version'],
        cart_json['next_idempotency_token'],
        user,
    )

    assert response.status_code == 200

    return response.json()


def test_checkout_flow(api, cart, orders, search_maps):
    api.set_host('http://grocery-api.lavka.yandex.net')
    cart.set_host('http://grocery-cart.lavka.yandex.net')
    user = user_model.GroceryUser()

    response = api.modes_root(user)
    assert response.status_code == 200
    modes_root_json = response.json()

    assert 'offer_id' in modes_root_json

    assert 'modes' in modes_root_json
    assert modes_root_json['modes']

    assert 'products' in modes_root_json
    assert modes_root_json['products']

    category_response = _get_water_category(api, user, modes_root_json)

    sweet_water_tmp = [
        x
        for x in category_response['products']
        if x['id'] == 'some_water_id_idk'
    ]
    assert sweet_water_tmp
    sweet_water = sweet_water_tmp[0]

    response = cart.add_product(
        modes_root_json['offer_id'],
        sweet_water['id'],
        sweet_water['pricing']['price'],
        user,
    )
    assert response.status_code == 200
    cart_json = response.json()

    assert 'cart_id' in cart_json
    assert 'cart_version' in cart_json

    cart_json = _set_payment(cart, cart_json['offer_id'], user, cart_json)
    assert 'cart_id' in cart_json
    assert 'cart_version' in cart_json

    search_maps.register_company(
        coordinates=user.get_location(),
        text='grocery-src-point',
        name='Яндекс.Такси',
        address='Садовническая улица, 82с1',
    )

    submit_response = orders.submit_v2(cart_json, user)
    assert submit_response.status_code == 200
    assert 'order_id' in submit_response.json()
