BASIC_HEADERS = {
    'X-Request-Language': 'ru',
    'X-Request-Application': f'app_name=mobileweb_yango_android',
    'X-YaTaxi-User': (
        f'eats_user_id=eats-user-id, personal_phone_id=personal-phone-id'
    ),
    'X-Yandex-UID': 'yandex_uid',
    'X-Remote-IP': '1.1.1.1',
    'X-Login-Id': 'login-id',
    'X-YaTaxi-Session': 'taxi:user-id',
    'X-YaTaxi-PhoneId': 'phone-id',
    'X-AppMetrica-DeviceId': 'some_appmetrica',
}

CART_ID = '0fe426b3-96ba-438e-a73a-d2cd70dbe3d9'


async def test_actual_cart_200(taxi_grocery_eats_gateway, grocery_cart):
    grocery_cart.check_request(fields_to_check={}, headers=BASIC_HEADERS)
    grocery_cart.set_cart_data(cart_id=CART_ID)

    response = await taxi_grocery_eats_gateway.post(
        '/internal/grocery-eats-gateway/v1/actual-cart',
        json={},
        headers=BASIC_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['cart_id'] == CART_ID


async def test_actual_cart_404(taxi_grocery_eats_gateway, grocery_cart):
    grocery_cart.check_request(fields_to_check={}, headers=BASIC_HEADERS)
    grocery_cart.set_actual_cart_error(code=404)

    response = await taxi_grocery_eats_gateway.post(
        '/internal/grocery-eats-gateway/v1/actual-cart',
        json={},
        headers=BASIC_HEADERS,
    )

    assert response.status_code == 404


async def test_actual_cart_401(taxi_grocery_eats_gateway):
    response = await taxi_grocery_eats_gateway.post(
        '/internal/grocery-eats-gateway/v1/actual-cart', json={},
    )

    assert response.status_code == 401
