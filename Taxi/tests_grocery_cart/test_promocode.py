import pytest

from tests_grocery_cart import common
from tests_grocery_cart import experiments
from tests_grocery_cart.plugins import keys
from tests_grocery_cart.plugins import mock_eats_promocodes
from tests_grocery_cart.plugins import mock_grocery_coupons


BASIC_HEADERS = {
    'X-YaTaxi-Session': 'eats:123',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
    'X-YaTaxi-User': 'eats_user_id=12345',
}


@pytest.mark.parametrize(
    'promocode_valid, include_promocode, discount_type,'
    ' expected_promocode_discount, expected_total_price',
    [
        (True, True, 'fixed', '100', '445'),
        (True, True, 'percent', '164', '381'),
        (False, True, 'fixed', '100', '545'),
        (False, False, 'fixed', None, '545'),
    ],
)
@pytest.mark.now(keys.TS_NOW)
async def test_basic(
        taxi_grocery_cart,
        mockserver,
        grocery_coupons,
        promocode_valid,
        include_promocode,
        discount_type,
        expected_promocode_discount,
        expected_total_price,
        overlord_catalog,
        offers,
        experiments3,
        grocery_surge,
        grocery_p13n,
):
    cart_id = '8da556be-0971-4f3b-a454-d980130662cc'
    item_id = 'item_id_1'
    price = '345'

    overlord_catalog.add_product(product_id=item_id, price=price)
    grocery_coupons.set_check_response(
        status_code=200,
        response_body=mock_grocery_coupons.PROMO_ERROR_INVALID_CODE,
    )

    delivery = {'cost': '200', 'next_threshold': '400', 'next_cost': '100'}

    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id='offer_id',
        offer_time=keys.TS_NOW,
    )
    common.add_delivery_conditions(experiments3, delivery=delivery)

    @mockserver.json_handler('/eats-promocodes/promocodes/grocery/validate')
    def mock_validate(request):
        assert request.json == {
            'code': 'LAVKA1235',
            'user': {'id': '12345', 'idProvider': 'eats'},
            'place': {'id': '0'},
            'paymentMethod': 'taxi',
            'applyForAmount': '345',
        }
        validation_response = {
            'payload': {
                'validationResult': {'valid': promocode_valid, 'message': '1'},
            },
        }
        if include_promocode:
            discount = '200' if discount_type == 'fixed' else '30'
            discount_result = expected_promocode_discount
            validation_response['payload']['validationResult']['promocode'] = {
                'discount': discount,
                'discountType': discount_type,
                'discountLimit': '500',
                'discountResult': discount_result,
            }
        return validation_response

    grocery_coupons.check_check_request(**keys.CHECK_REQUEST_ADDITIONAL_DATA)
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/apply-promocode',
        json={
            'position': keys.DEFAULT_POSITION,
            'cart_id': cart_id,
            'offer_id': 'offer_id',
            'promocode': 'LAVKA1235',
            'cart_version': 1,
            'additional_data': keys.DEFAULT_ADDITIONAL_DATA,
        },
        headers={
            'X-Idempotency-Token': common.APPLY_PROMOCODE_IDEMPOTENCY_TOKEN,
            'User-Agent': keys.DEFAULT_USER_AGENT,
            **BASIC_HEADERS,
        },
    )
    grocery_p13n.set_modifiers_request_check(on_modifiers_request=None)
    grocery_coupons.check_check_request()
    assert response.status_code == 200
    expected_promocode_response = {
        'code': 'LAVKA1235',
        'messages': ['1'],
        'valid': promocode_valid,
    }
    if expected_promocode_discount is not None:
        expected_promocode_response['discount'] = expected_promocode_discount
        expected_promocode_response[
            'discount_template'
        ] = f'{expected_promocode_discount} $SIGN$$CURRENCY$'
        if discount_type == 'percent':
            expected_promocode_response['discount_percent'] = '30'
    response = response.json()
    assert response['promocode'] == expected_promocode_response
    expected_total_price_template = f'{expected_total_price} $SIGN$$CURRENCY$'
    assert response['total_price_template'] == expected_total_price_template
    if promocode_valid:
        assert response['full_price_template'] == '545 $SIGN$$CURRENCY$'
    else:
        assert 'full_price_template' not in response
    assert mock_validate.times_called == 1
    assert grocery_p13n.discount_modifiers_times_called == 1

    # check promocode is saved
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        json={
            'position': keys.DEFAULT_POSITION,
            'cart_id': '8da556be-0971-4f3b-a454-d980130662cc',
            'offer_id': 'offer_id',
            'cart_version': 2,
            'additional_data': keys.DEFAULT_ADDITIONAL_DATA,
        },
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()['promocode'] == expected_promocode_response
    assert mock_validate.times_called == 2

    # reset promocode
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/apply-promocode',
        json={
            'position': keys.DEFAULT_POSITION,
            'cart_id': '8da556be-0971-4f3b-a454-d980130662cc',
            'offer_id': 'offer_id',
            'cart_version': 2,
            'additional_data': keys.DEFAULT_ADDITIONAL_DATA,
        },
        headers={
            'X-Idempotency-Token': common.APPLY_PROMOCODE_IDEMPOTENCY_TOKEN,
            'User-Agent': keys.DEFAULT_USER_AGENT,
            **BASIC_HEADERS,
        },
    )
    assert response.status_code == 200
    assert 'promocode' not in response.json()

    # check promocode reset is saved
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        json={
            'position': keys.DEFAULT_POSITION,
            'cart_id': '8da556be-0971-4f3b-a454-d980130662cc',
            'offer_id': 'offer_id',
            'cart_version': 2,
            'additional_data': keys.DEFAULT_ADDITIONAL_DATA,
        },
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 200
    assert 'promocode' not in response.json()

    assert mock_validate.times_called == 2  # no additional calls


async def test_promocode_idempotency(
        cart, overlord_catalog, eats_promocodes, grocery_coupons,
):
    eats_promocodes.set_discount(100)

    overlord_catalog.add_product(product_id='test-item', price='345')

    # Create
    await cart.modify({'test-item': {'q': 1, 'p': 345}})
    assert cart.cart_version == 1

    grocery_coupons.check_check_request(**keys.CHECK_REQUEST_ADDITIONAL_DATA)
    # Update
    await cart.apply_promocode(
        'LAVKA1235', headers={'X-Idempotency-Token': 'p1'},
    )
    assert cart.cart_version == 2
    assert eats_promocodes.times_called() == 1

    cart_data = cart.fetch_db()
    assert cart_data.idempotency_token == 'p1'
    assert cart_data.promocode == 'LAVKA1235'

    # Update with other token, conflict
    cart.cart_version = 1
    with pytest.raises(cart.HttpError) as exc:
        await cart.apply_promocode(
            'LAVKA1235', headers={'X-Idempotency-Token': 'p2'},
        )
    assert exc.value.status_code == 409

    # Update with original token, ok
    await cart.apply_promocode(
        'LAVKA1235', headers={'X-Idempotency-Token': 'p1'},
    )
    assert cart.cart_version == 2


# Check that applyforamount is (cart_price + delivery_cost)
@pytest.mark.now(keys.TS_NOW)
async def test_promocode_apply_for_amount(
        cart,
        overlord_catalog,
        mockserver,
        offers,
        experiments3,
        grocery_surge,
        grocery_coupons,
):
    item_price = 345
    delivery_cost = 500
    discount = 100

    actual_delivery = {
        'cost': str(delivery_cost),
        'next_threshold': '400',
        'next_cost': '0',
    }

    @mockserver.json_handler('/eats-promocodes/promocodes/grocery/validate')
    def mock_validate(request):
        assert request.json['applyForAmount'] == str(item_price)
        return mock_eats_promocodes.discount_payload(discount=discount)

    overlord_catalog.add_product(product_id='test-item', price=str(item_price))
    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=cart.offer_id,
        offer_time=keys.TS_NOW,
    )
    common.add_delivery_conditions(experiments3, delivery=actual_delivery)

    await cart.modify({'test-item': {'q': 1, 'p': 345}})
    assert cart.cart_version == 1

    grocery_coupons.check_check_request(**keys.CHECK_REQUEST_ADDITIONAL_DATA)
    response = await cart.apply_promocode(
        'LAVKA100', headers={'X-Idempotency-Token': 'p1'},
    )
    assert cart.cart_version == 2
    assert mock_validate.times_called == 1

    total_price = item_price + delivery_cost - discount
    assert (
        response['total_price_template'] == f'{total_price} $SIGN$$CURRENCY$'
    )


# Check that user receives friendly message on promocode external errors
async def test_promocode_failure_message_is_friendly(
        cart,
        overlord_catalog,
        mockserver,
        offers,
        experiments3,
        grocery_surge,
        grocery_coupons,
):
    @mockserver.json_handler('/eats-promocodes/promocodes/grocery/validate')
    def mock_validate(request):
        return mockserver.make_response('fail', status=500)

    grocery_coupons.set_check_response(
        status_code=200,
        response_body=mock_grocery_coupons.PROMO_ERROR_INVALID_CODE,
    )

    overlord_catalog.add_product(product_id='test-item', price='345')

    actual_delivery = {
        'cost': '500',
        'next_threshold': '400',
        'next_cost': '0',
    }
    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=cart.offer_id,
        delivery=actual_delivery,
    )

    await cart.modify({'test-item': {'q': 1, 'p': 345}})
    assert cart.cart_version == 1

    grocery_coupons.check_check_request(**keys.CHECK_REQUEST_ADDITIONAL_DATA)
    response = await cart.apply_promocode(
        'LAVKA100', headers={'X-Idempotency-Token': 'p1'},
    )
    assert cart.cart_version == 2
    assert response['promocode']['messages'] == ['Внешняя ошибка']
    assert mock_validate.times_called > 0


@pytest.mark.experiments3(filename='exp_del_type.json')
async def test_has_promocode_for_rover(
        cart, overlord_catalog, eats_promocodes, grocery_coupons,
):
    eats_promocodes.set_discount(100)

    item_id = 'item-id'
    price = '345'
    price_with_discount = '245'
    overlord_catalog.add_product(product_id=item_id, price=price)

    await cart.modify(
        {item_id: {'q': 1, 'p': price}},
        headers={'X-Yandex-Uid': '8484', **common.TAXI_HEADERS},
    )

    await cart.modify(
        {},
        delivery_type='rover',
        headers={'X-Yandex-Uid': '8484', **common.TAXI_HEADERS},
    )

    assert cart.cart_version == 2

    grocery_coupons.check_check_request(**keys.CHECK_REQUEST_ADDITIONAL_DATA)
    response = await cart.apply_promocode(
        'LAVKA100', headers={'X-Idempotency-Token': 'p1'},
    )
    grocery_coupons.check_check_request()
    assert 'promocode' in response
    assert eats_promocodes.times_called() == 1

    response = await cart.retrieve(headers={'X-Yandex-Uid': '8484'})
    assert (
        response['total_price_template']
        == f'{price_with_discount} $SIGN$$CURRENCY$'
    )

    assert 'promocode' in response
    assert eats_promocodes.times_called() == 2


@pytest.mark.experiments3(filename='exp_del_type.json')
@pytest.mark.parametrize('is_taxi_promocode', [False, True])
async def test_no_promocode_for_pickup(
        cart,
        overlord_catalog,
        eats_promocodes,
        grocery_coupons,
        is_taxi_promocode,
):
    if is_taxi_promocode:
        grocery_coupons.set_check_response_custom(value='400')
        eats_promocodes.set_valid(False)
    else:
        eats_promocodes.set_discount(100)
        grocery_coupons.set_check_response(
            status_code=200,
            response_body=mock_grocery_coupons.PROMO_ERROR_INVALID_CODE,
        )

    markdown_item_id = 'item-id:st-md'
    price = '345'
    overlord_catalog.add_product(product_id=markdown_item_id, price=price)

    await cart.modify(
        {markdown_item_id: {'q': 1, 'p': price}},
        headers={'X-Yandex-Uid': '8484', **common.TAXI_HEADERS},
    )
    assert cart.cart_version == 1

    grocery_coupons.check_check_request(**keys.CHECK_REQUEST_ADDITIONAL_DATA)
    try:
        await cart.apply_promocode(
            'LAVKA100', headers={'X-Idempotency-Token': 'p1'},
        )
    except common.CartHttpError as exc:
        assert exc.status_code == 400
    else:
        assert is_taxi_promocode
    grocery_coupons.check_check_request()

    assert grocery_coupons.check_times_called() == 1
    assert eats_promocodes.times_called() == 1

    response = await cart.retrieve(headers={'X-Yandex-Uid': '8484'})
    assert response['total_price_template'] == f'{price} $SIGN$$CURRENCY$'

    assert grocery_coupons.check_times_called() == 2
    assert eats_promocodes.times_called() == 2
    assert ('promocode' in response) == is_taxi_promocode


@experiments.PROMOCODE_CHOOSE_ORDER_ENABLED_CYCLE
@experiments.PROMOCODE_CHOOSE_ORDER_CYCLE
@pytest.mark.experiments3(filename='exp_del_type.json')
@pytest.mark.parametrize('is_taxi_promocode', [False, True])
async def test_promocode_after_markdown_item(
        cart,
        overlord_catalog,
        eats_promocodes,
        grocery_coupons,
        is_taxi_promocode,
):
    discount = 100
    if is_taxi_promocode:
        grocery_coupons.set_check_response_custom(
            value=str(discount), promocode_type='fixed',
        )
        eats_promocodes.set_valid(False)
    else:
        eats_promocodes.set_discount(discount)
        grocery_coupons.set_check_response(
            status_code=200,
            response_body=mock_grocery_coupons.PROMO_ERROR_INVALID_CODE,
        )

    item_id = 'item-id'
    markdown_item_id = 'item-id:st-md'
    item_price = '345'
    markdown_price = '500'
    overlord_catalog.add_product(
        product_id=markdown_item_id, price=markdown_price,
    )
    overlord_catalog.add_product(product_id=item_id, price=item_price)

    headers = {'X-Yandex-Uid': '8484', **common.TAXI_HEADERS}
    await cart.modify({item_id: {'q': 1, 'p': item_price}}, headers=headers)

    grocery_coupons.check_check_request(**keys.CHECK_REQUEST_ADDITIONAL_DATA)
    response = await cart.apply_promocode('fixed_100', headers=headers)
    grocery_coupons.check_check_request()
    assert eats_promocodes.times_called() == 1
    assert grocery_coupons.check_times_called() == 1

    total = int(item_price) - discount
    assert response['total_price_template'] == f'{total} $SIGN$$CURRENCY$'

    response = await cart.modify(
        {markdown_item_id: {'q': 1, 'p': markdown_price}}, headers=headers,
    )

    if is_taxi_promocode:
        # has promocode after markdown product for taxi coupon
        total = int(item_price) + int(markdown_price) - discount
    else:
        # no promocode after markdown product for eats coupon
        total = int(item_price) + int(markdown_price)

    assert response['total_price_template'] == f'{total} $SIGN$$CURRENCY$'
    assert eats_promocodes.times_called() == 2
    assert grocery_coupons.check_times_called() == 2


@experiments.PROMOCODE_CHOOSE_ORDER_ENABLED_CYCLE
@experiments.PROMOCODE_CHOOSE_ORDER_CYCLE
@pytest.mark.experiments3(filename='exp_del_type.json')
@pytest.mark.parametrize('is_taxi_promocode', [False, True])
async def test_apply_promocode_after_change_delivery_type(
        cart,
        overlord_catalog,
        eats_promocodes,
        grocery_coupons,
        is_taxi_promocode,
):
    discount = 100
    if is_taxi_promocode:
        grocery_coupons.set_check_response_custom(
            value=str(discount), promocode_type='fixed',
        )
        eats_promocodes.set_valid(False)
    else:
        eats_promocodes.set_discount(discount)
        grocery_coupons.set_check_response(
            status_code=200,
            response_body=mock_grocery_coupons.PROMO_ERROR_INVALID_CODE,
        )

    item_id = 'item-id'
    markdown_item_id = 'item-id:st-md'
    item_price = '345'
    markdown_price = '500'
    overlord_catalog.add_product(
        product_id=markdown_item_id, price=markdown_price,
    )
    overlord_catalog.add_product(product_id=item_id, price=item_price)

    headers = {'X-Yandex-Uid': '8484', **common.TAXI_HEADERS}

    await cart.modify({item_id: {'q': 1, 'p': item_price}}, headers=headers)
    response = await cart.apply_promocode('fixed_100', headers=headers)
    total = int(item_price) - discount
    assert response['total_price_template'] == f'{total} $SIGN$$CURRENCY$'

    response = await cart.modify({}, headers=headers, delivery_type='pickup')
    if not is_taxi_promocode:
        total = item_price
    assert response['total_price_template'] == f'{total} $SIGN$$CURRENCY$'

    response = await cart.modify(
        {}, headers=headers, delivery_type='eats_dispatch',
    )
    total = int(item_price) - discount
    assert response['total_price_template'] == f'{total} $SIGN$$CURRENCY$'


@experiments.PROMOCODE_CHOOSE_ORDER_ENABLED_CYCLE
@experiments.PROMOCODE_CHOOSE_ORDER_CYCLE
@pytest.mark.experiments3(filename='exp_del_type.json')
@pytest.mark.parametrize('is_taxi_promocode', [False, True])
async def test_promocode_in_checkout_for_pickup(
        cart,
        overlord_catalog,
        eats_promocodes,
        grocery_coupons,
        is_taxi_promocode,
):
    if is_taxi_promocode:
        grocery_coupons.set_check_response_custom(value='400')
        eats_promocodes.set_valid(False)
    else:
        grocery_coupons.set_check_response(
            status_code=200,
            response_body=mock_grocery_coupons.PROMO_ERROR_INVALID_CODE,
        )
        eats_promocodes.set_valid(True)

    item_id = 'item-id'
    markdown_item_id = 'item-id:st-md'
    item_price = '345'
    markdown_price = '500'
    overlord_catalog.add_product(
        product_id=markdown_item_id, price=markdown_price,
    )
    overlord_catalog.add_product(product_id=item_id, price=item_price)

    headers = {'X-Yandex-Uid': '8484', **common.TAXI_HEADERS}

    await cart.modify({item_id: {'q': 1, 'p': item_price}}, headers=headers)
    grocery_coupons.check_check_request(**keys.CHECK_REQUEST_ADDITIONAL_DATA)
    await cart.apply_promocode('fixed_100', headers=headers)
    grocery_coupons.check_check_request()
    await cart.modify({}, headers=headers, delivery_type='pickup')
    response = await cart.checkout(headers=headers)
    assert ('promocode' in response) == is_taxi_promocode


@pytest.mark.pgsql('grocery_cart', files=['localized_product.sql'])
@pytest.mark.parametrize('locale', ['ru', 'en', 'he'])
async def test_promocode_response_has_localized_product(
        cart,
        overlord_catalog,
        eats_promocodes,
        load_json,
        locale,
        grocery_coupons,
):
    localized = load_json('expected_product_localization.json')
    eats_promocodes.set_discount(100)

    overlord_catalog.add_product(product_id='localized_product', price='345')

    # Create
    await cart.modify({'localized_product': {'q': 1, 'p': 345}})

    grocery_coupons.check_check_request(**keys.CHECK_REQUEST_ADDITIONAL_DATA)
    # Update
    response = await cart.apply_promocode(
        'LAVKA1235',
        headers={'X-Idempotency-Token': 'p1', 'X-Request-Language': locale},
    )

    assert response['items'][0]['title'] == localized[locale]['title']
    assert response['items'][0]['subtitle'] == localized[locale]['subtitle']
