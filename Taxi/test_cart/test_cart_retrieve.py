# pylint: disable=too-many-lines
import copy

import pytest

from tests_grocery_cart import common
from tests_grocery_cart import experiments
from tests_grocery_cart.plugins import keys


BASIC_HEADERS = {
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
}
TAXI_HEADERS = {
    **BASIC_HEADERS,
    'X-YaTaxi-Session': 'taxi:1234',
    'X-YaTaxi-User': 'eats_user_id=12345',
    'X-Yandex-UID': 'some_uid',
}
EDA_HEADERS = {
    **BASIC_HEADERS,
    'X-YaTaxi-Session': 'eats:123',
    'X-YaTaxi-User': 'eats_user_id=12345',
    'X-Yandex-UID': 'some_other_uid',
}
EDATAXI_HEADERS = {
    **BASIC_HEADERS,
    'X-YaTaxi-Session': 'eats:123',
    #    'X-YaTaxi-Bound-Sessions': 'taxi:1234',
    'X-YaTaxi-User': 'eats_user_id=12345',
    'X-Yandex-UID': 'some_other_uid',
    'X-YaTaxi-Bound-Uids': 'some_uid',
}


@pytest.mark.parametrize(
    'test_case, headers, cart_id, item_id, expected_code',
    [
        ('find_by_user__eda', EDA_HEADERS, None, 'item_id_1', 200),
        ('find_by_user__edataxi', EDATAXI_HEADERS, None, 'item_id_1', 200),
        ('find_by_user__taxi', TAXI_HEADERS, None, 'item_id_2', 200),
        # Search with cart_id
        (
            'eda_cart__headers_taxi__1',
            TAXI_HEADERS,
            '11111111-2222-aaaa-bbbb-cccdddeee001',
            'item_id_1',
            404,
        ),
        (
            'eda_cart__headers_eda__1',
            EDA_HEADERS,
            '11111111-2222-aaaa-bbbb-cccdddeee001',
            'item_id_1',
            200,
        ),
        (
            'eda_cart__headers_taxieda__1',
            EDATAXI_HEADERS,
            '11111111-2222-aaaa-bbbb-cccdddeee001',
            'item_id_1',
            200,
        ),
        # Search with another cart_id
        (
            'eda_cart__headers_taxi__2',
            TAXI_HEADERS,
            '11111111-2222-aaaa-bbbb-cccdddeee002',
            'item_id_2',
            200,
        ),
        (
            'eda_cart__headers_eda__2',
            EDA_HEADERS,
            '11111111-2222-aaaa-bbbb-cccdddeee002',
            'item_id_2',
            404,
        ),
        (
            'eda_cart__headers_taxieda__2',
            EDATAXI_HEADERS,
            '11111111-2222-aaaa-bbbb-cccdddeee002',
            'item_id_2',
            404,
        ),
    ],
)
@pytest.mark.pgsql('grocery_cart', files=['one_item.sql'])
async def test_basic(
        taxi_grocery_cart,
        test_case,
        headers,
        cart_id,
        item_id,
        expected_code,
        overlord_catalog,
        grocery_p13n,
        grocery_coupons,
):
    price = '100'
    quantity = '100'
    overlord_catalog.add_product(
        product_id=item_id,
        price=price,
        in_stock=quantity,
        legal_restrictions=['RU_18+'],
    )

    grocery_coupons.check_check_request(**keys.CHECK_REQUEST_ADDITIONAL_DATA)
    request = {
        'position': keys.DEFAULT_POSITION,
        'additional_data': keys.DEFAULT_ADDITIONAL_DATA,
    }
    if cart_id is not None:
        request['cart_id'] = cart_id
        request['cart_version'] = 1
    headers['User-Agent'] = keys.DEFAULT_USER_AGENT
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve', json=request, headers=headers,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        response_json = response.json()
        assert response_json['items'] == [
            {
                'id': item_id,
                'price': '345',
                'catalog_price': price,
                'catalog_price_template': f'{price} $SIGN$$CURRENCY$',
                'catalog_total_price_template': f'{price} $SIGN$$CURRENCY$',
                'title': f'title for {item_id}',
                'quantity': '1',
                'currency': 'RUB',
                'quantity_limit': quantity,
                'subtitle': f'subtitle for {item_id}',
                'image_url_template': f'url for {item_id}',
                'image_url_templates': [f'url for {item_id}'],
                'restrictions': ['ru_18+'],
            },
        ]
        assert grocery_p13n.cashback_info_times_called == 1
        assert grocery_p13n.discount_modifiers_times_called == 1
    else:
        assert grocery_p13n.cashback_info_times_called == 0
        assert grocery_p13n.discount_modifiers_times_called == 0


@pytest.mark.parametrize(
    'test_case, headers, cart_id, depot_id',
    [
        (
            'eda_cart_id_not_found_1',
            EDA_HEADERS,
            '11111111-2222-aaaa-bbbb-cccdddeee333',
            '111',
        ),
        (
            'eda_cart_checked_out_1',
            EDA_HEADERS,
            '11111111-2222-aaaa-bbbb-cccdddeee011',
            '111',
        ),
        (
            'taxi_cart_id_not_found',
            TAXI_HEADERS,
            '11111111-2222-aaaa-bbbb-cccdddeee333',
            '222',
        ),
        (
            'taxi_cart_checked_out',
            TAXI_HEADERS,
            '11111111-2222-aaaa-bbbb-cccdddeee012',
            '222',
        ),
    ],
)
@pytest.mark.pgsql('grocery_cart', files=['non_existing_cart.sql'])
async def test_update_nonexisting_cart(
        taxi_grocery_cart, test_case, headers, cart_id, depot_id,
):
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        headers=headers,
        json={
            'position': keys.DEFAULT_POSITION,
            'cart_id': cart_id,
            'cart_version': 1,
        },
    )
    assert response.status_code == 404


@pytest.mark.pgsql('grocery_cart', files=['eda_one_item.sql'])
async def test_no_products_in_overlord(taxi_grocery_cart, grocery_p13n):
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        json={
            'position': keys.DEFAULT_POSITION,
            'cart_id': '8da556be-0971-4f3b-a454-d980130662cc',
            'cart_version': 1,
        },
        headers=EDA_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()['items'][0]['quantity_limit'] == '0'
    assert grocery_p13n.cashback_info_times_called == 1


@pytest.mark.pgsql('grocery_cart', files=['eda_one_item.sql'])
async def test_no_depot_in_overlord(
        taxi_grocery_cart, grocery_p13n, grocery_depots,
):
    grocery_depots.clear_depots()

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        json={
            'position': keys.DEFAULT_POSITION,
            'cart_id': '8da556be-0971-4f3b-a454-d980130662cc',
            'cart_version': 1,
        },
        headers=EDA_HEADERS,
    )

    assert response.status_code == 200
    data = response.json()
    assert not data['available_for_checkout']
    assert data['checkout_unavailable_reason'] == 'cannot_find_depot'
    assert grocery_p13n.discount_modifiers_times_called == 0


@pytest.mark.parametrize('offer_id', ['wrong_offer_id', None])
@pytest.mark.pgsql('grocery_cart', files=['one_item.sql'])
async def test_retrieve_wrong_offer(taxi_grocery_cart, offer_id):
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        headers=TAXI_HEADERS,
        json={
            'position': keys.DEFAULT_POSITION,
            'cart_id': '11111111-2222-aaaa-bbbb-cccdddeee002',
            'offer_id': offer_id,
            'cart_version': 1,
        },
    )
    assert response.status_code == 200
    assert response.json()['offer_id'] == '0'


@pytest.mark.pgsql('grocery_cart', files=['eda_one_item.sql'])
async def test_products_headers(taxi_grocery_cart, user_api):
    request_headers = {
        'X-YaTaxi-Session': 'taxi:1234',
        'X-YaTaxi-Bound-Sessions': 'eats:123',
        'X-Request-Language': 'ru',
        'X-Request-Application': 'app_name=android',
        'X-YaTaxi-User': 'personal_phone_id=phone-id,eats_user_id=12345',
        'X-Yandex-UID': 'yandex-uid',
    }

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        json={
            'position': keys.DEFAULT_POSITION,
            'cart_id': '8da556be-0971-4f3b-a454-d980130662cc',
            'cart_version': 1,
        },
        headers=request_headers,
    )
    assert response.status_code == 200


@pytest.mark.pgsql('grocery_cart', files=['non_existing_cart.sql'])
@pytest.mark.parametrize(
    'uid, allow_checked_out, expected_code',
    [(123, None, 404), (123, True, 200), (9876, None, 404), (9876, True, 404)],
)
async def test_retrieve_checked_out(
        taxi_grocery_cart, uid, allow_checked_out, expected_code,
):
    cart_id = '11111111-2222-aaaa-bbbb-cccdddeee011'

    request = {
        'position': keys.DEFAULT_POSITION,
        'cart_id': cart_id,
        'cart_version': 1,
    }
    if allow_checked_out:
        request['allow_checked_out'] = allow_checked_out

    headers = {
        'X-YaTaxi-User': f'eats_user_id={uid}',
        'X-YaTaxi-Session': f'eats:{uid}',
        **BASIC_HEADERS,
    }
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve', json=request, headers=headers,
    )

    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'code,user_id,cart_id',
    [
        (200, 0, '00000000-0000-0000-0000-000000000000'),
        (200, 1, '00000000-0000-0000-0000-000000000002'),
        (404, 2, None),  # 404 because last cart is checkedout and has order_id
    ],
)
@pytest.mark.pgsql('grocery_cart', files=['retrieve_last.sql'])
async def test_retrieve_last_cart(taxi_grocery_cart, code, user_id, cart_id):
    request = {'position': keys.DEFAULT_POSITION}
    headers = {
        'X-YaTaxi-User': f'eats_user_id={user_id}',
        'X-YaTaxi-Session': f'eats:{user_id}',
        **BASIC_HEADERS,
    }
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve', json=request, headers=headers,
    )

    assert response.status_code == code
    if cart_id is not None:
        assert response.json()['cart_id'] == cart_id


PAID_DELIVERY_SETTINGS = pytest.mark.experiments3(
    name='paid_delivery_settings',
    consumers=['grocery-cart'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'enabled': True,
                'l10n': [
                    {
                        'key': 'to_min_cart_with_delivery',
                        'tanker': {
                            'key': 'with_delivery_cart',
                            'keyset': 'grocery_cart',
                        },
                        'default': '',
                    },
                    {
                        'key': 'to_min_cart_without_delivery',
                        'tanker': {
                            'key': 'with_delivery_cart_2',
                            'keyset': 'grocery_cart',
                        },
                        'default': '',
                    },
                    {
                        'key': 'to_free_delivery_with_delivery',
                        'tanker': {
                            'key': 'with_delivery_cart_3',
                            'keyset': 'grocery_cart',
                        },
                        'default': '',
                    },
                    {
                        'key': 'to_free_delivery_without_delivery',
                        'tanker': {
                            'key': 'with_delivery_cart_4',
                            'keyset': 'grocery_cart',
                        },
                        'default': '',
                    },
                    {
                        'key': 'to_next_delivery_without_delivery',
                        'tanker': {
                            'key': 'with_delivery_cart_5',
                            'keyset': 'grocery_cart',
                        },
                        'default': '',
                    },
                    {
                        'key': 'delivery_price',
                        'tanker': {
                            'key': 'delivery_cost',
                            'keyset': 'grocery_cart',
                        },
                        'default': '',
                    },
                    {
                        'key': 'rover_delivery_title',
                        'tanker': {
                            'key': 'rover_delivery_title',
                            'keyset': 'grocery_cart',
                        },
                        'default': '',
                    },
                    {
                        'key': 'rover_delivery_title_percent',
                        'tanker': {
                            'key': 'rover_delivery_title_percent',
                            'keyset': 'grocery_cart',
                        },
                        'default': '',
                    },
                    {
                        'key': 'rover_delivery_title_plus',
                        'tanker': {
                            'key': 'rover_delivery_title_plus',
                            'keyset': 'grocery_cart',
                        },
                        'default': '',
                    },
                    {
                        'key': 'rover_delivery_subtitle',
                        'tanker': {
                            'key': 'rover_delivery_subtitle',
                            'keyset': 'grocery_cart',
                        },
                        'default': '',
                    },
                    {
                        'key': 'rover_delivery_subtitle_percent',
                        'tanker': {
                            'key': 'rover_delivery_subtitle_percent',
                            'keyset': 'grocery_cart',
                        },
                        'default': '',
                    },
                    {
                        'key': 'rover_delivery_subtitle_plus',
                        'tanker': {
                            'key': 'rover_delivery_subtitle_plus',
                            'keyset': 'grocery_cart',
                        },
                        'default': '',
                    },
                    {
                        'key': 'rover_delivery_link',
                        'tanker': {
                            'key': 'rover_delivery_link',
                            'keyset': 'grocery_cart',
                        },
                        'default': '',
                    },
                    {
                        'key': 'finish',
                        'tanker': {'key': 'finish', 'keyset': 'grocery_cart'},
                        'default': '',
                    },
                    {
                        'key': 'discount_short_text',
                        'tanker': {
                            'key': 'discount_short_text',
                            'keyset': 'grocery_cart',
                        },
                        'default': '',
                    },
                    {
                        'key': 'discount_short_text_percent',
                        'tanker': {
                            'key': 'discount_short_text_percent',
                            'keyset': 'grocery_cart',
                        },
                        'default': '',
                    },
                ],
            },
        },
    ],
    is_config=True,
)


@pytest.mark.experiments3(
    name='grocery_rover_compensation_params',
    consumers=[
        'grocery-cart/order-cycle',
        'grocery-api/service-info',
        'grocery-cart',
    ],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'value': '100', 'is_percent': False, 'is_plus': False},
        },
    ],
    is_config=True,
)
@PAID_DELIVERY_SETTINGS
@pytest.mark.experiments3(
    name='grocery-p13n-surge',
    consumers=['grocery-surge-client/surge'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'delivery_cost': '100',
                'minimum_order': '150',
                'max_eta_minutes': '77',
                'min_eta_minutes': '33',
                'next_delivery_cost': '0',
                'next_delivery_threshold': '400',
                'surge': True,
            },
        },
    ],
    is_config=True,
)
@pytest.mark.now(keys.TS_NOW)
@pytest.mark.pgsql('grocery_cart', files=['eda_one_item.sql'])
async def test_products_experiment(
        taxi_grocery_cart,
        overlord_catalog,
        grocery_p13n,
        offers,
        umlaas_eta,
        grocery_surge,
        now,
        grocery_depots,
        user_api,
):
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

    assert offers.created_times == 1
    assert grocery_p13n.cashback_info_times_called == 1

    assert response.json()['l10n'] == {
        'to_min_cart_without_delivery': (
            'До доставки без доставки 50 $SIGN$$CURRENCY$ лол'
        ),
        'to_free_delivery_without_delivery': (
            'До бесплатной доставки без доставки 300 $SIGN$$CURRENCY$'
        ),
        'to_free_delivery_with_delivery': (
            'До бесплатной доставки с ценой доставки 200 $SIGN$$CURRENCY$'
        ),
        'to_next_delivery_without_delivery': (
            'Еще 50 $SIGN$$CURRENCY$ до доставки за 100 $SIGN$$CURRENCY$'
        ),
        'delivery_price': 'Доставка: 100 $SIGN$$CURRENCY$',
        'rover_delivery_title': 'Доставка ровером',
        'rover_delivery_subtitle': (
            'Можно доставить беспилотником! '
            'И получить скидку 100 $SIGN$$CURRENCY$!'
        ),
        'rover_delivery_link': 'ya.ru',
        'market_promocode_unavailable': (
            'Промокоды, выданные в Маркете не '
            'распространяются на заказы в Лавке'
        ),
    }


@PAID_DELIVERY_SETTINGS
@pytest.mark.experiments3(
    name='grocery_rover_ui_images',
    consumers=['grocery-cart'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Image by ISO3',
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_type': 'string',
                    'arg_name': 'country_iso3',
                    'value': 'RUS',
                },
            },
            'value': {'checkout_image': 'rover_checkout_image.jpg'},
        },
    ],
    is_config=True,
)
@pytest.mark.pgsql('grocery_cart', files=['eda_one_item.sql'])
async def test_rover_ui_images(taxi_grocery_cart):
    """ cart handlers returns rover images
    from grocery_rover_ui_images config """
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        json={
            'position': keys.DEFAULT_POSITION,
            'cart_id': '8da556be-0971-4f3b-a454-d980130662cc',
            'cart_version': 1,
            'offer_id': 'test_offer_id',
        },
        headers=EDATAXI_HEADERS,
    )
    assert response.status_code == 200
    assert (
        response.json()['l10n']['rover_delivery_image']
        == 'rover_checkout_image.jpg'
    )


@pytest.mark.now(keys.TS_NOW)
@pytest.mark.parametrize('depot_status', ['closed', 'coming_soon'])
async def test_depot_status(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        depot_status,
        grocery_depots,
):
    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        0,
        legacy_depot_id=keys.DEFAULT_LEGACY_DEPOT_ID,
        depot_id=keys.DEFAULT_WMS_DEPOT_ID,
        location=keys.DEFAULT_DEPOT_LOCATION_OBJ,
        status=depot_status,
    )
    await taxi_grocery_cart.invalidate_caches()

    item_id = 'item_id_1'
    quantity = 2
    price = '400'
    overlord_catalog.add_product(
        product_id=item_id, price=price, in_stock=str(quantity),
    )

    await cart.modify({item_id: {'q': quantity, 'p': price}})

    request = {'position': keys.DEFAULT_POSITION, 'offer_id': cart.offer_id}

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve', json=request, headers=TAXI_HEADERS,
    )

    assert response.status_code == 200
    data = response.json()
    assert data['checkout_unavailable_reason'] == 'depot_is_closed_now'
    assert data['depot'] == {
        'status': 'closed',
        'switch_time': '2020-03-13T21:00:00+00:00',
    }


@pytest.mark.parametrize('locale', ['ru', 'en', 'he'])
@pytest.mark.pgsql('grocery_cart', files=['localized_product.sql'])
async def test_product_title_localization(
        taxi_grocery_cart, overlord_catalog, locale, load_json,
):
    localized = load_json('expected_product_localization.json')
    price = '100'
    quantity = '100'
    item_id = 'localized_product'
    cart_id = '11111111-2222-aaaa-bbbb-cccdddeee005'

    overlord_catalog.add_product(
        product_id=item_id, price=price, in_stock=quantity,
    )

    request = {
        'position': keys.DEFAULT_POSITION,
        'cart_id': cart_id,
        'cart_version': 1,
    }

    headers = {**EDA_HEADERS, 'X-Request-Language': locale}

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve', json=request, headers=headers,
    )
    assert response.status_code == 200

    item = response.json()['items'][0]
    assert item['title'] == localized[locale]['title']
    assert item['subtitle'] == localized[locale]['subtitle']


@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        '__default__': {'grocery': 0.01, '__default__': 1},
    },
    CURRENCY_FORMATTING_RULES={
        'ILS': {'__default__': 2},
        'RUB': {'grocery': 2, '__default__': 0},
    },
)
@pytest.mark.parametrize(
    'currency,price,total',
    [
        ('RUB', '100.18', '100,18'),
        ('RUB', '100.01', '100,01'),
        ('RUB', '100.50', '100,5'),
        ('RUB', '100.51', '100,51'),
        ('ILS', '1.2', '1,2'),
        ('ILS', '1.9', '1,9'),
        ('ILS', '1.94', '1,94'),
        ('ILS', '1.951', '1,95'),
        ('ILS', '1.956', '1,95'),
    ],
)
async def test_cart_total_precision(
        cart, overlord_catalog, currency, price, total, grocery_depots,
):
    quantity = '1'
    item_id = 'item-id'

    # должен быть не '0', чтобы не резолвилось в дефолтный русский депот мока
    legacy_depot_id = '111'
    overlord_catalog.add_depot(
        legacy_depot_id=legacy_depot_id, currency=currency,
    )
    grocery_depots.add_depot(int(legacy_depot_id), currency=currency)

    overlord_catalog.add_product(
        product_id=item_id, price=price, in_stock=quantity,
    )

    await cart.modify({item_id: {'p': price, 'q': quantity}})
    response = await cart.retrieve()

    assert response['total_price_template'] == f'{total} $SIGN$$CURRENCY$'


# Если товара остается недостаточно, то не показываем скидку 1 + 1
@pytest.mark.translations(
    discount_descriptions={'test_discount_label': {'ru': 'купи 2 получи 1'}},
)
@pytest.mark.pgsql('grocery_cart', files=['one_item.sql'])
@pytest.mark.parametrize(
    'discount_quantity,discount_presented',
    [
        pytest.param('2', True, id='sufficient'),
        pytest.param('5', False, id='insufficient'),
    ],
)
async def test_hide_discount_labels(
        taxi_grocery_cart,
        overlord_catalog,
        grocery_p13n,
        discount_quantity,
        discount_presented,
):
    item_id = 'item_id_1'
    overlord_catalog.add_product(product_id=item_id, price='100', in_stock='3')

    grocery_p13n.add_modifier_product_payment(
        product_id=item_id,
        payment_per_product='100',
        quantity=discount_quantity,
        meta={'subtitle_tanker_key': 'test_discount_label'},
    )

    request = {
        'position': keys.DEFAULT_POSITION,
        'cart_id': '11111111-2222-aaaa-bbbb-cccdddeee001',
        'cart_version': 1,
    }
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve', json=request, headers=EDATAXI_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    if discount_presented:
        assert response_json['items'][0]['discount_label'] == 'купи 2 получи 1'
    else:
        assert 'discount_label' not in response_json['items'][0]


@pytest.mark.skipif(
    True, reason='diff data for delivery steps has been removed',
)
@pytest.mark.parametrize('accept_delivery_cost', (True, False))
@pytest.mark.parametrize(
    'prev_delivery_cost,cur_delivery_cost', [('200', '100')],
)
async def test_diff_delivery(
        taxi_grocery_cart,
        cart,
        accept_delivery_cost,
        prev_delivery_cost,
        cur_delivery_cost,
        offers,
        experiments3,
        grocery_surge,
):
    price = '345'
    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id='offer_id',
        delivery={
            'delivery_cost': prev_delivery_cost,
            'next_delivery_cost': '100',
            'next_delivery_threshold': '400',
        },
    )

    await cart.init({'item_id_1': {'price': price}})

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        headers=common.TAXI_HEADERS,
        json={
            'position': cart.position,
            'cart_id': cart.cart_id,
            'offer_id': cart.offer_id,
        },
    )
    assert response.status_code == 200
    assert response.json()['diff_data'] == {}

    if accept_delivery_cost:
        await cart.accept_delivery_cost(prev_delivery_cost)

    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id='offer_id',
        delivery={
            'delivery_cost': cur_delivery_cost,
            'next_delivery_cost': '100',
            'next_delivery_threshold': '400',
        },
    )

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        headers=common.TAXI_HEADERS,
        json={
            'position': cart.position,
            'cart_id': cart.cart_id,
            'offer_id': cart.offer_id,
        },
    )

    diff = abs(int(cur_delivery_cost) - int(prev_delivery_cost))
    actual_cart_total = int(cur_delivery_cost) + int(price)
    prev_cart_total = int(prev_delivery_cost) + int(price)

    assert response.status_code == 200
    assert response.json()['diff_data'] == {
        'delivery_cost': {
            'actual_template': _to_template(cur_delivery_cost),
            'diff_template': _to_template(diff),
            'previous_template': _to_template(prev_delivery_cost),
            'trend': _trend(prev=prev_delivery_cost, actual=cur_delivery_cost),
        },
        'cart_total': {
            'actual_template': _to_template(actual_cart_total),
            'diff_template': _to_template(diff),
            'previous_template': _to_template(prev_cart_total),
            'trend': _trend(prev=prev_cart_total, actual=actual_cart_total),
        },
    }


@pytest.mark.now(keys.TS_NOW)
async def test_additional_offer_info_log(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        pgsql,
        testpoint,
        offers,
        experiments3,
        grocery_surge,
        grocery_depots,
):
    offer_id = cart.offer_id
    user_id = '123456abcd'

    item_id = 'item_id_1'
    price = '345'
    quantity = 1

    delivery_cost = '100'
    next_delivery_cost = '50'
    next_delivery_threshold = '350'
    min_eta = 20
    max_eta = 10
    minimum_order = '300'

    actual_delivery = {
        'cost': delivery_cost,
        'next_cost': next_delivery_cost,
        'next_threshold': next_delivery_threshold,
    }

    legacy_depot_id = keys.DEFAULT_LEGACY_DEPOT_ID

    overlord_catalog.add_product(product_id=item_id, price=price, in_stock='1')

    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=offer_id,
        depot_id=legacy_depot_id,
        delivery=actual_delivery,
        is_surge=True,
        min_eta=str(min_eta),
        max_eta=str(max_eta),
        minimum_order=minimum_order,
    )

    await cart.modify({item_id: {'q': quantity, 'p': price}})

    location_str = (
        str(float(keys.DEFAULT_DEPOT_LOCATION[1]))
        + ';'
        + str(float(keys.DEFAULT_DEPOT_LOCATION[0]))
    )

    @testpoint('yt_offer_additional_info')
    def yt_offer_additional_info(offer_additional_info):
        assert offer_additional_info['version'] == 1
        assert offer_additional_info['offer_id'] == offer_id
        assert offer_additional_info['doc'] == {
            'active_zone': 'foot',
            'foot': {
                'delivery_cost': delivery_cost,
                'delivery_conditions': [
                    {
                        'delivery_cost': delivery_cost,
                        'order_cost': minimum_order,
                    },
                    {
                        'delivery_cost': next_delivery_cost,
                        'order_cost': next_delivery_threshold,
                    },
                ],
                'is_surge': True,
                'is_manual': False,
                'next_delivery_cost': next_delivery_cost,
                'next_delivery_threshold': next_delivery_threshold,
                'max_eta_minutes': str(max_eta),
                'min_eta_minutes': str(min_eta),
                'surge_minimum_order': minimum_order,
            },
        }
        assert offer_additional_info['params'] == {
            'lat_lon': location_str,
            'depot_id': legacy_depot_id,
        }
        assert offer_additional_info['user_id'] == user_id

    json = {
        'position': keys.DEFAULT_POSITION,
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
    }

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        headers={**TAXI_HEADERS, **{'X-YaTaxi-UserId': user_id}},
        json=json,
    )

    assert response.status_code == 200
    assert yt_offer_additional_info.times_called == 1


@pytest.mark.pgsql('grocery_cart', files=['one_item.sql'])
async def test_parent_id_in_response(taxi_grocery_cart, overlord_catalog):
    price = '100'
    quantity = '100'
    item_id = 'item_id_2'
    cart_id = '11111111-2222-aaaa-bbbb-cccdddeee002'
    overlord_catalog.add_product(
        product_id=item_id,
        price=price,
        in_stock=quantity,
        parent_id='parent-id',
    )

    request = {
        'position': keys.DEFAULT_POSITION,
        'cart_id': cart_id,
        'cart_version': 1,
    }
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve', json=request, headers=TAXI_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()['items'] == [
        {
            'id': item_id,
            'price': '345',
            'catalog_price': price,
            'catalog_price_template': f'{price} $SIGN$$CURRENCY$',
            'catalog_total_price_template': f'{price} $SIGN$$CURRENCY$',
            'title': f'title for {item_id}',
            'quantity': '1',
            'currency': 'RUB',
            'quantity_limit': quantity,
            'subtitle': f'subtitle for {item_id}',
            'image_url_template': f'url for {item_id}',
            'image_url_templates': [f'url for {item_id}'],
            'parent_id': 'parent-id',
            'restrictions': [],
        },
    ]


def _trend(*, prev, actual):
    if int(prev) < int(actual):
        return 'increase'
    return 'decrease'


def _to_template(price):
    return f'{str(price)} $SIGN$$CURRENCY$'


# Проверяем что форматирование соответствует конфигам
@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        '__default__': {'grocery': 0.01, '__default__': 0.01},
    },
    CURRENCY_FORMATTING_RULES={'RUB': {'grocery': 2, '__default__': 0}},
    CURRENCY_KEEP_TRAILING_ZEROS={
        'RUB': {'__default__': False, 'grocery': True},
    },
)
@PAID_DELIVERY_SETTINGS
@pytest.mark.now(keys.TS_NOW)
async def test_right_formatting_in_l10n(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        offers,
        experiments3,
        grocery_surge,
        grocery_depots,
):
    offer_id = cart.offer_id
    user_id = '123456abcd'

    item_id = 'item_id_1'
    price = '345'
    quantity = 1

    delivery_cost = '1.25'
    next_delivery_cost = '50'
    next_delivery_threshold = '350'
    min_eta = 20
    max_eta = 10
    minimum_order = '300'

    actual_delivery = {
        'cost': delivery_cost,
        'next_cost': next_delivery_cost,
        'next_threshold': next_delivery_threshold,
    }

    legacy_depot_id = '111'
    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=offer_id,
        depot_id=legacy_depot_id,
        delivery=actual_delivery,
        min_eta=str(min_eta),
        max_eta=str(max_eta),
        minimum_order=minimum_order,
    )
    overlord_catalog.add_depot(legacy_depot_id=legacy_depot_id)
    grocery_depots.add_depot(int(legacy_depot_id))

    overlord_catalog.add_product(product_id=item_id, price=price, in_stock='1')

    await cart.modify({item_id: {'q': quantity, 'p': price}})

    json = {
        'position': keys.DEFAULT_POSITION,
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
    }

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        headers={**TAXI_HEADERS, **{'X-YaTaxi-UserId': user_id}},
        json=json,
    )

    assert response.status_code == 200
    assert (
        response.json()['l10n']['delivery_price']
        == 'Доставка: 1,25 $SIGN$$CURRENCY$'
    )


def _set_surge_conditions(experiments3, delivery_conditions=None):
    value = {
        'data': [
            {
                'payload': {
                    'delivery_conditions': delivery_conditions,
                    'min_eta_minutes': '5',
                    'max_eta_minutes': '15',
                },
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


# Проверяем, что информация о доставке заполняется верно
# в соответствии с delivery_conditions, а также:
# возвращает till_next_delivery, только если есть доставка дешевле;
# till_free_delivery не должно приходить, если бесплатной нет.
@PAID_DELIVERY_SETTINGS
@pytest.mark.experiments3(
    name='grocery_rover_compensation_params',
    consumers=[
        'grocery-cart/order-cycle',
        'grocery-api/service-info',
        'grocery-cart',
    ],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'value': '10', 'is_percent': True, 'is_plus': False},
        },
    ],
    is_config=True,
)
@pytest.mark.now(keys.TS_NOW)
@pytest.mark.pgsql('grocery_cart', files=['eda_one_item.sql'])
@pytest.mark.parametrize(
    'delivery_conditions, delivery_cost,'
    'next_threshold, next_cost, '
    ' max_threshold, max_threshold_cost',
    [
        (
            [
                {'order_cost': '0', 'delivery_cost': '10'},
                {'order_cost': '75', 'delivery_cost': '0'},
            ],
            '0',  # delivery_cost
            None,  # next_threshold
            None,  # next_cost
            75,  # max_threshold
            0,  # max_threshold_cost
        ),
        (
            [
                {'order_cost': '0', 'delivery_cost': '10'},
                {'order_cost': '75', 'delivery_cost': '5'},
                {'order_cost': '150', 'delivery_cost': '0'},
            ],
            '5',  # delivery_cost
            150,  # next_threshold
            '0',  # next_cost
            150,  # max_threshold
            0,  # max_threshold_cost
        ),
        (
            [
                {'order_cost': '0', 'delivery_cost': '20'},
                {'order_cost': '100', 'delivery_cost': '10'},
                {'order_cost': '150', 'delivery_cost': '5'},
            ],
            '10',  # delivery_cost
            150,  # next_threshold
            '5',  # next_cost
            150,  # max_threshold
            5,  # max_threshold_cost
        ),
        (
            [
                {'order_cost': '150', 'delivery_cost': '10'},
                {'order_cost': '200', 'delivery_cost': '0'},
            ],
            '10',  # delivery_cost
            150,  # next_threshold
            '10',  # next_cost
            200,  # max_threshold
            0,  # max_threshold_cost
        ),
        (
            [
                {'order_cost': '0', 'delivery_cost': '20'},
                {'order_cost': '100', 'delivery_cost': '10'},
            ],
            '10',  # delivery_cost
            None,  # next_threshold
            None,  # next_cost
            100,  # max_threshold
            10,  # max_threshold_cost
        ),
        (
            [{'order_cost': '0', 'delivery_cost': '20'}],
            '20',  # delivery_cost
            None,  # next_threshold
            None,  # next_cost
            0,  # max_threshold
            20,  # max_threshold_cost
        ),
    ],
)
async def test_delivery_conditions(
        experiments3,
        taxi_grocery_cart,
        overlord_catalog,
        grocery_p13n,
        offers,
        umlaas_eta,
        grocery_surge,
        now,
        delivery_conditions,
        delivery_cost,
        max_threshold,
        next_threshold,
        next_cost,
        max_threshold_cost,
        grocery_depots,
        user_api,
):
    _set_surge_conditions(
        experiments3, delivery_conditions=delivery_conditions,
    )

    request_headers = {
        'X-YaTaxi-Session': 'eats:123',
        'X-YaTaxi-Bound-Sessions': 'taxi:1234',
        'X-Request-Language': 'ru',
        'X-Request-Application': 'app_name=android',
        'X-YaTaxi-User': 'personal_phone_id=phone-id,eats_user_id=12345',
        'X-Yandex-UID': 'yandex-uid',
    }

    depot_id = '100'
    price = 150
    price_with_item_discount = 100
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

    overlord_catalog.add_depot(
        legacy_depot_id=depot_id, location=keys.DEFAULT_DEPOT_LOCATION,
    )
    grocery_depots.add_depot(
        int(depot_id), location=keys.DEFAULT_DEPOT_LOCATION,
    )
    product_id = 'item_id_1'
    overlord_catalog.add_product(
        product_id=product_id, price=str(price), in_stock='1234.5678',
    )
    # ступени доставки вычисляются от цены со скидкой
    grocery_p13n.add_modifier(
        product_id=product_id, value=str(price - price_with_item_discount),
    )
    # скидки на корзину не влияют на пороги доставки
    grocery_p13n.add_cart_modifier_with_rules(
        steps=[('40', '20', 'discount_value')],
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

    assert offers.created_times == 1
    assert grocery_p13n.cashback_info_times_called == 1

    expected_l10n = {
        'rover_delivery_title': 'Доставка ровером',
        'rover_delivery_subtitle': (
            'Можно доставить беспилотником! И получить 10% скидку'
        ),
        'rover_delivery_link': 'ya.ru',
        'market_promocode_unavailable': (
            'Промокоды, выданные в Маркете не '
            'распространяются на заказы в Лавке'
        ),
    }
    if int(delivery_cost) > 0:
        expected_l10n[
            'delivery_price'
        ] = f'Доставка: {delivery_cost} $SIGN$$CURRENCY$'
    if max_threshold > price_with_item_discount:
        if max_threshold_cost == 0:
            till_free_with_delivery = (
                max_threshold - price_with_item_discount - int(delivery_cost)
            )
            expected_l10n['to_free_delivery_with_delivery'] = (
                f'До бесплатной доставки с ценой доставки'
                f' {str(till_free_with_delivery)}'
                f' $SIGN$$CURRENCY$'
            )
            expected_l10n['to_free_delivery_without_delivery'] = (
                f'До бесплатной доставки без доставки'
                f' {str(max_threshold - price_with_item_discount)}'
                f' $SIGN$$CURRENCY$'
            )
        if next_threshold is not None:
            if next_threshold == max_threshold and max_threshold_cost == 0:
                expected_l10n['to_next_delivery_without_delivery'] = (
                    f'До бесплатной доставки без доставки'
                    f' {str(max_threshold - price_with_item_discount)} '
                    f'$SIGN$$CURRENCY$'
                )
            else:
                expected_l10n['to_next_delivery_without_delivery'] = (
                    f'Еще {str(next_threshold - price_with_item_discount)} '
                    f'$SIGN$$CURRENCY$'
                    f' до доставки за {next_cost} $SIGN$$CURRENCY$'
                )
    if int(delivery_conditions[0]['order_cost']) > price_with_item_discount:
        to_min_cart_without_delivery = str(
            int(delivery_conditions[0]['order_cost'])
            - price_with_item_discount,
        )
        to_min_cart = str(
            int(delivery_conditions[0]['order_cost'])
            - price_with_item_discount
            - int(delivery_conditions[0]['delivery_cost']),
        )
        expected_l10n['to_min_cart_without_delivery'] = (
            f'До доставки без доставки '
            f'{to_min_cart_without_delivery} $SIGN$$CURRENCY$ лол'
        )
        expected_l10n[
            'to_min_cart_with_delivery'
        ] = f'До доставки {to_min_cart} $SIGN$$CURRENCY$ лол'

    assert response.json()['l10n'] == expected_l10n


def parametrize_show_discounts(show_reward_discounts_enabled):
    return pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        is_config=True,
        name='grocery_show_reward_discounts',
        consumers=['grocery-cart'],
        clauses=[
            {
                'predicate': {'type': 'true'},
                'value': {'enabled': show_reward_discounts_enabled},
            },
        ],
    )


# Проверяем, что информация о стимулирующем блоке заполняеся верно
@pytest.mark.parametrize(
    'show_reward_discounts',
    [
        pytest.param(True, marks=(parametrize_show_discounts(True))),
        pytest.param(False, marks=(parametrize_show_discounts(False))),
    ],
)
@PAID_DELIVERY_SETTINGS
@pytest.mark.parametrize('use_item_discount', [True, False])
@pytest.mark.now(keys.TS_NOW)
@pytest.mark.pgsql('grocery_cart', files=['eda_one_item.sql'])
@pytest.mark.parametrize(
    'cart_price, item_discount, '
    'expected_progresses, expected_till_next_threshold,'
    'expected_till_next_threshold_without_discounts',
    [
        (
            70,
            20,
            [66, 0, 0, 0, 0, 0, 0],
            dict(
                message='Еще 25 $SIGN$$CURRENCY$ до минимального заказа',
                value='25',
            ),
            dict(
                message='Еще 25 $SIGN$$CURRENCY$ до минимального заказа',
                value='25',
            ),
        ),
        (
            130,
            30,
            [100, 100, 33, 0, 0, 0, 0],
            dict(
                message='Еще 50 $SIGN$$CURRENCY$ до доставки за 10 '
                '$SIGN$$CURRENCY$',
                value='50',
            ),
            dict(
                message='Еще 50 $SIGN$$CURRENCY$ до доставки за 10 '
                '$SIGN$$CURRENCY$',
                value='50',
            ),
        ),
        (
            170,
            20,
            [100, 100, 100, 0, 0, 0, 0],
            dict(
                message='Еще 50 $SIGN$$CURRENCY$ до скидки — 10%', value='50',
            ),
            dict(message='А это всегда приятно', value='0'),
        ),
        (
            190,
            20,
            [100, 100, 100, 40, 0, 0, 0],
            dict(
                message='Еще 30 $SIGN$$CURRENCY$ до скидки — 10%', value='30',
            ),
            dict(message='А это всегда приятно', value='0'),
        ),
        (
            250,
            20,
            [100, 100, 100, 100, 30, 0, 0],
            dict(
                message='Еще 70 $SIGN$$CURRENCY$ до скидки — 20 '
                '$SIGN$$CURRENCY$',
                value='70',
            ),
            dict(message='А это всегда приятно', value='0'),
        ),
        (
            368,
            20,
            [100, 100, 100, 100, 100, 48, 0],
            dict(
                message='Еще 52 $SIGN$$CURRENCY$ до кешбэка 5% на Плюс',
                value='52',
            ),
            dict(message='А это всегда приятно', value='0'),
        ),
        (
            520,
            50,
            [100, 100, 100, 100, 100, 100, 70],
            dict(
                message='Еще 30 $SIGN$$CURRENCY$ до 50 баллов на Плюс',
                value='30',
            ),
            dict(message='А это всегда приятно', value='0'),
        ),
        (
            620,
            20,
            [100, 100, 100, 100, 100, 100, 100],
            dict(message='А это всегда приятно', value='0'),
            dict(message='А это всегда приятно', value='0'),
        ),
    ],
)
async def test_reward_block(
        experiments3,
        taxi_grocery_cart,
        overlord_catalog,
        offers,
        umlaas_eta,
        grocery_surge,
        now,
        cart_price,
        item_discount,
        expected_progresses,
        expected_till_next_threshold,
        expected_till_next_threshold_without_discounts,
        grocery_p13n,
        show_reward_discounts,
        use_item_discount,
        grocery_depots,
        user_api,
):
    delivery_conditions = [
        {'order_cost': '75', 'delivery_cost': '199'},
        {'order_cost': '150', 'delivery_cost': '10'},
    ]
    discount_steps = [
        ('200', '10.2', 'discount_percent'),
        ('300', '20', 'discount_value'),
        ('400', '5.3', 'gain_percent'),
        ('500', '50', 'gain_value'),
    ]
    _set_surge_conditions(
        experiments3, delivery_conditions=delivery_conditions,
    )

    request_headers = {
        'X-YaTaxi-Session': 'eats:123',
        'X-YaTaxi-Bound-Sessions': 'taxi:1234',
        'X-Request-Language': 'ru',
        'X-Request-Application': 'app_name=android',
        'X-YaTaxi-User': 'personal_phone_id=phone-id,eats_user_id=12345',
        'X-Yandex-UID': 'yandex-uid',
        'X-Idempotency-Token': common.UPDATE_IDEMPOTENCY_TOKEN,
    }

    depot_id = '100'
    if not use_item_discount:
        price = cart_price - item_discount
    else:
        price = cart_price

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

    overlord_catalog.add_depot(
        legacy_depot_id=depot_id, location=keys.DEFAULT_DEPOT_LOCATION,
    )
    grocery_depots.add_depot(
        int(depot_id), location=keys.DEFAULT_DEPOT_LOCATION,
    )
    product_id = 'item_id_1'
    overlord_catalog.add_product(
        product_id=product_id, price=str(price), in_stock='1234.5678',
    )
    grocery_p13n.add_cart_modifier_with_rules(steps=discount_steps)

    if use_item_discount:
        # ступени доставки вычисляются от цены со скидкой
        grocery_p13n.add_modifier(
            product_id=product_id, value=str(item_discount),
        )
    else:
        grocery_p13n.add_modifier_product_payment(
            product_id=product_id,
            payment_per_product='100',
            quantity='2',
            meta={'subtitle_tanker_key': 'test_discount_label'},
        )

        request = {
            'position': keys.DEFAULT_POSITION,
            'cart_id': '8da556be-0971-4f3b-a454-d980130662cc',
            'cart_version': 1,
            'items': [
                {
                    'id': product_id,
                    'price': str(price),
                    'quantity': '2',
                    'currency': 'RUB',
                },
            ],
        }

        await taxi_grocery_cart.post(
            '/lavka/v1/cart/v1/update', json=request, headers=request_headers,
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

    assert offers.created_times == 1
    progresses = []
    response_json = response.json()
    for item in response_json['reward_block']['items']:
        progresses.append(item['progress'])
        item.pop('progress')

    expected_items = [
        {
            'cart_cost_threshold': '75 $SIGN$$CURRENCY$',
            'reward_short_value': '75 $SIGN$$CURRENCY$',
            'reward_value': 'Минимальная корзина',
            'type': 'min_cart',
        },
        {
            'cart_cost_threshold': 'от 75 $SIGN$$CURRENCY$',
            'reward_short_value': '199 $SIGN$$CURRENCY$',
            'reward_value': 'Доставка: 199 $SIGN$$CURRENCY$',
            'type': 'delivery',
        },
        {
            'cart_cost_threshold': 'от 150 $SIGN$$CURRENCY$',
            'reward_short_value': '10 $SIGN$$CURRENCY$',
            'reward_value': 'Доставка: 10 $SIGN$$CURRENCY$',
            'type': 'delivery',
        },
    ]

    reward_block = response_json['reward_block']
    if show_reward_discounts:
        expected_items = expected_items + [
            {
                'cart_cost_threshold': 'от 200 $SIGN$$CURRENCY$',
                'reward_short_value': '10%',
                'reward_value': 'Скидка 10%',
                'type': 'cart_money_discount',
            },
            {
                'cart_cost_threshold': 'от 300 $SIGN$$CURRENCY$',
                'reward_short_value': '-20 $SIGN$$CURRENCY$',
                'reward_value': 'Скидка 20 $SIGN$$CURRENCY$',
                'type': 'cart_money_discount',
            },
            {
                'cart_cost_threshold': 'от 400 $SIGN$$CURRENCY$',
                'reward_short_value': '5%',
                'reward_value': '5% вернется на Плюс',
                'type': 'cart_cashback',
            },
            {
                'cart_cost_threshold': 'от 500 $SIGN$$CURRENCY$',
                'reward_short_value': '50',
                'reward_value': '50 баллов на Плюс',
                'type': 'cart_cashback',
            },
        ]

        message = expected_till_next_threshold['message']
        value = expected_till_next_threshold['value']
    else:
        message = expected_till_next_threshold_without_discounts['message']
        value = expected_till_next_threshold_without_discounts['value']

        expected_progresses = expected_progresses[:3]

    assert reward_block['till_next_threshold'] == message
    assert reward_block['till_next_threshold_numeric'] == value
    assert progresses == expected_progresses

    assert response_json['reward_block']['items'] == expected_items


# Проверяем, что значение до минимальной корзины в requirements и в
# checkout_unavailable_reason совпадают
@PAID_DELIVERY_SETTINGS
@pytest.mark.now(keys.TS_NOW)
@pytest.mark.pgsql('grocery_cart', files=['eda_one_item.sql'])
async def test_requirements_match(
        experiments3,
        taxi_grocery_cart,
        overlord_catalog,
        offers,
        grocery_surge,
        now,
        grocery_p13n,
        grocery_depots,
        user_api,
):
    delivery_conditions = [
        {'order_cost': '350', 'delivery_cost': '199'},
        {'order_cost': '700', 'delivery_cost': '10'},
    ]
    _set_surge_conditions(
        experiments3, delivery_conditions=delivery_conditions,
    )

    request_headers = {
        'X-YaTaxi-Session': 'eats:123',
        'X-YaTaxi-Bound-Sessions': 'taxi:1234',
        'X-Request-Language': 'ru',
        'X-Request-Application': 'app_name=android',
        'X-YaTaxi-User': 'personal_phone_id=phone-id,eats_user_id=12345',
        'X-Yandex-UID': 'yandex-uid',
    }

    depot_id = '100'
    price = 395
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

    overlord_catalog.add_depot(
        legacy_depot_id=depot_id, location=keys.DEFAULT_DEPOT_LOCATION,
    )
    grocery_depots.add_depot(
        int(depot_id), location=keys.DEFAULT_DEPOT_LOCATION,
    )

    product_id = 'item_id_1'
    overlord_catalog.add_product(
        product_id=product_id, price=str(price), in_stock='1234.5678',
    )
    grocery_p13n.add_modifier(product_id=product_id, value='50')

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

    assert offers.created_times == 1
    response_json = response.json()
    # Порог минимальной корзины равен 350, добавили товар на 395 и скидку на 50
    # Проверяем, что в обоих местах считается одинаково(с учетом скидки)
    available_for_checkout = True
    if response_json['checkout_unavailable_reason'] == 'minimum-price':
        available_for_checkout = False
    available_in_requirements = False
    if response_json['requirements']['sum_to_min_order'] == '0':
        available_in_requirements = True
    assert available_in_requirements == available_for_checkout


@pytest.mark.parametrize('force_hide_price_mismatch', [True, False, None])
async def test_force_hide_price_mismatch(
        taxi_grocery_cart,
        cart,
        experiments3,
        overlord_catalog,
        force_hide_price_mismatch,
):
    if force_hide_price_mismatch is not None:
        experiments3.add_config(
            name='grocery_force_hide_price_mismatch',
            consumers=['grocery-cart'],
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'enabled': force_hide_price_mismatch},
                },
            ],
        )

    await cart.init({'item_id_1': {'price': '123', 'quantity': '1'}})

    overlord_catalog.add_product(product_id='item_id_1', price='456')

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve',
        headers=common.TAXI_HEADERS,
        json={
            'position': cart.position,
            'cart_id': cart.cart_id,
            'offer_id': cart.offer_id,
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    if force_hide_price_mismatch is True:
        assert response_json['hide_price_mismatch'] is True
    else:
        assert 'hide_price_mismatch' not in response_json

    assert response.json()['diff_data'] == {
        'cart_total': {
            'actual_template': '456 $SIGN$$CURRENCY$',
            'diff_template': '333 $SIGN$$CURRENCY$',
            'previous_template': '123 $SIGN$$CURRENCY$',
            'trend': 'increase',
        },
        'products': [
            {
                'price': {
                    'actual_template': '456 $SIGN$$CURRENCY$',
                    'diff_template': '333 $SIGN$$CURRENCY$',
                    'previous_template': '123 $SIGN$$CURRENCY$',
                    'trend': 'increase',
                },
                'product_id': 'item_id_1',
            },
        ],
    }


@pytest.mark.now(keys.TS_NOW)
@pytest.mark.parametrize('is_heavy_cart_enabled', [False, True])
@pytest.mark.parametrize(
    'products_amount_pack,result_weight',
    [([1, 1, 1, 1], '0,02'), ([2, 1, 1, 1], '0,021')],
)
async def test_heavy_cart(
        taxi_grocery_cart,
        overlord_catalog,
        experiments3,
        cart,
        is_heavy_cart_enabled,
        products_amount_pack,
        result_weight,
):

    experiments.set_heavy_cart_settings(experiments3, is_heavy_cart_enabled)

    common_measurements = {
        'width': 1,
        'height': 2,
        'depth': 3,
        'net_weight': 5,
    }

    measurements = [
        {**common_measurements, 'gross_weight': 1},
        {**common_measurements, 'gross_weight': 2},
        {**common_measurements, 'gross_weight': 3},
        {**common_measurements, 'gross_weight': 5},
    ]

    item_ids = ['item_id_1', 'item_id_2', 'item_id_3', 'item_id_4']
    price = '10'

    for item_id, measurement, amount_pack in zip(
            item_ids, measurements, products_amount_pack,
    ):
        overlord_catalog.add_product(
            product_id=item_id,
            price=price,
            measurements=measurement,
            amount_pack=amount_pack,
        )

    await cart.modify(
        {
            item_ids[0]: {'q': 1, 'p': price},
            item_ids[1]: {'q': 1, 'p': price},
            item_ids[2]: {'q': 4, 'p': price},
            item_ids[3]: {'q': 1, 'p': price},
        },
    )

    assert overlord_catalog.times_called() == 1

    diff = {
        'cart_total': {
            'actual_template': '70 $SIGN$$CURRENCY$',
            'diff_template': '1950 $SIGN$$CURRENCY$',
            'previous_template': '-1880 $SIGN$$CURRENCY$',
            'trend': 'increase',
        },
        'products': [
            {
                'product_id': 'item_id_3',
                'quantity': {'actual_limit': '1', 'wanted': '4'},
            },
            {
                'product_id': 'item_id_4',
                'quantity': {'actual_limit': '0', 'wanted': '1'},
            },
        ],
    }

    json = {
        'position': keys.DEFAULT_POSITION,
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
        'items': [],
    }

    headers = {
        'X-Idempotency-Token': 'checkout-token',
        'X-YaTaxi-Session': 'taxi:1234',
        'X-Request-Language': 'ru',
        'X-Request-Application': 'app_name=android',
    }
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve', headers=headers, json=json,
    )
    assert response.status_code == 200
    response_json = response.json()

    if is_heavy_cart_enabled:
        assert response_json['diff_data'] == diff
        assert response_json['checkout_unavailable_reason'] == 'too_heavy_cart'
        assert 'heavy_cart_title' in response_json['l10n']
        assert (
            response_json['l10n']['heavy_cart_title']
            == 'Не получится добавить товар'
        )
        assert 'heavy_cart_text' in response_json['l10n']
        assert (
            response_json['l10n']['heavy_cart_text']
            == f'Тяжёлая корзина 0,007 кг {result_weight} кг'
        )
        assert 'heavy_cart_image_link' in response_json['l10n']
        assert response_json['l10n']['heavy_cart_image_link'] == 'some-link'
    else:
        assert response_json['diff_data'] == {}
        assert 'checkout_unavailable_reason' not in response_json
        assert 'heavy_cart_title' not in response_json['l10n']
        assert 'heavy_cart_text' not in response_json['l10n']
        assert 'heavy_cart_image_link' not in response_json['l10n']

    assert overlord_catalog.times_called() == 2


# Проверяем, что возвращаем флаг есть ли замены для товара, если
# товара нет в наличии, если товар есть в наличии флаг не возвращается
@pytest.mark.parametrize(
    'product_substitutions,has_substitutions',
    [
        pytest.param(
            ['product-2', 'product-3'], True, id='with_substitutions',
        ),
        pytest.param([], False, id='no_substitutions'),
    ],
)
async def test_substitutions(
        cart,
        overlord_catalog,
        grocery_upsale,
        product_substitutions,
        has_substitutions,
):
    item_1 = 'item_1'
    item_2 = 'item_2'
    quantity = 1
    price = '345'

    overlord_catalog.add_product(product_id=item_1, price=price, in_stock='1')
    overlord_catalog.add_product(product_id=item_2, price=price, in_stock='1')
    grocery_upsale.add_product_substitutions(product_substitutions)

    await cart.modify(
        {
            item_1: {'q': quantity, 'p': price},
            item_2: {'q': quantity, 'p': price},
        },
    )

    overlord_catalog.remove_product(product_id=item_1)
    overlord_catalog.remove_product(product_id=item_2)
    overlord_catalog.add_product(product_id=item_1, price=price, in_stock='0')
    overlord_catalog.add_product(product_id=item_2, price='100', in_stock='1')

    response = await cart.retrieve()
    products = response['diff_data']['products']
    assert products[0]['has_substitutions'] == has_substitutions
    assert 'has_substitutions' not in products[1]


@pytest.mark.parametrize('has_personal_phone_id', [True, False])
async def test_no_phone_id(
        taxi_grocery_cart,
        user_api,
        grocery_coupons,
        cart,
        has_personal_phone_id,
):
    headers = copy.deepcopy(TAXI_HEADERS)
    if has_personal_phone_id:
        headers['X-YaTaxi-User'] = 'personal_phone_id=personal-phone-id'

    await cart.modify({'item_id': {'q': '1', 'p': '10'}})

    request = {
        'position': keys.DEFAULT_POSITION,
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
        'items': [],
    }
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve', json=request, headers=headers,
    )
    assert response.status_code == 200
    assert user_api.times_called == (1 if has_personal_phone_id else 0)


# Проверяем, что возвращаем флаг private_label
@pytest.mark.parametrize('private_label', [True, False])
async def test_private_label(cart, overlord_catalog, private_label):
    item_1 = 'item_1'
    price = '100'

    overlord_catalog.add_product(
        product_id=item_1, private_label=private_label,
    )

    update_response = await cart.modify({item_1: {'q': '1', 'p': price}})
    # Проверяем флаг в /lavka/v1/cart/v1/update
    assert not update_response['items'][0]['private_label'] ^ private_label

    response = await cart.retrieve()
    assert not response['items'][0]['private_label'] ^ private_label


# Проверяем достаем новые title из вмсного или
# голубиного кейсетов в зависимости от конфига
@pytest.mark.translations(
    pigeon_product_title={'external_id_1': {'en': 'pigeon_title'}},
    wms_items={
        'product-1_title': {'en': 'wms_title'},
        'product-1_long_title': {'en': 'wms_long_title'},
    },
    pigeon_product_long_title={'external_id_1': {'en': 'pigeon_long_title'}},
)
@pytest.mark.parametrize(
    'pigeon_long_title_enabled,long_title',
    [
        pytest.param(False, 'wms_long_title', id='wms'),
        pytest.param(True, 'pigeon_long_title', id='pigeon'),
    ],
)
@pytest.mark.parametrize(
    'pigeon_short_title_enabled,title',
    [
        pytest.param(True, 'pigeon_title', id='pigeon'),
        pytest.param(False, 'wms_title', id='wms'),
    ],
)
async def test_product_pigeon_titles(
        taxi_config,
        cart,
        overlord_catalog,
        pigeon_short_title_enabled,
        title,
        pigeon_long_title_enabled,
        long_title,
):
    taxi_config.set(
        GROCERY_LOCALIZATION_PIGEON_PRODUCT_TITLE={
            'keyset': 'pigeon_product_title',
            'enabled': pigeon_short_title_enabled,
        },
    )
    taxi_config.set(
        GROCERY_LOCALIZATION_PIGEON_LONG_TITLE={
            'keyset': 'pigeon_product_long_title',
            'enabled': pigeon_long_title_enabled,
        },
    )
    item_1 = 'product-1'
    price = '100'

    overlord_catalog.add_product(
        product_id=item_1, external_id='external_id_1',
    )

    await cart.modify({item_1: {'q': '1', 'p': price}})
    response = await cart.retrieve()
    assert response['items'][0]['title'] == title
    assert response['items'][0]['subtitle'] == long_title
