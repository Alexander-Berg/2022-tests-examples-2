import uuid

import pytest

from . import common
from . import consts
from . import models


def _get_formatted_time(time):
    return time.isoformat().replace('00:00', '0000')


@pytest.mark.parametrize(
    'compensation_type, v3_type, is_full, '
    'currency, numeric_value, rounded_value, description, error_code',
    [
        (
            'promocode',
            'promocode',
            False,
            None,
            '15',
            15,
            'Промокод на 15%',
            'bad_request',
        ),
        (
            'voucher',
            'voucher',
            False,
            'RUB',
            '9',
            9,
            'Ваучер на 9 ₽',
            'bad_request',
        ),
        (
            'superVoucher',
            'super_voucher',
            False,
            'RUB',
            '9',
            9,
            'Супер-ваучер на 9 ₽',
            'bad_request',
        ),
        (
            'refund',
            'refund',
            False,
            'RUB',
            '8.35',
            9,
            'Частичный рефанд (8.35 ₽)',
            'bad_request',
        ),
        (
            'refund',
            'full_refund',
            True,
            'RUB',
            '15',
            15,
            'Полный рефанд (15 ₽)',
            None,
        ),
        (
            'superPlus',
            'super_plus_voucher',
            False,
            None,
            '10',
            10,
            'Супер-ваучер на 10 баллов',
            'bad_request',
        ),
        (
            'percentPlus',
            'percent_plus_voucher',
            False,
            None,
            '2',
            2,
            'Супер-ваучер на 2 баллов',
            'bad_request',
        ),
    ],
)
@pytest.mark.now(models.NOW)
async def test_proxy_v3(
        taxi_grocery_support,
        pgsql,
        grocery_orders,
        grocery_cart,
        eats_compensations_matrix,
        now,
        compensation_type,
        v3_type,
        is_full,
        currency,
        numeric_value,
        rounded_value,
        description,
        error_code,
        mockserver,
):
    first_compensation_id = str(uuid.uuid4())
    compensation_maas_id = 11
    situation_maas_id = 14
    country_iso2 = 'ru'
    payment_method = 'card'
    cart_id = str(uuid.uuid4())
    source = 'admin_compensation'
    client_price = 15.0

    user = common.create_default_customer(pgsql, now)
    user.update_db()

    situation_first = common.create_situation_v2(
        pgsql, situation_maas_id, first_compensation_id,
    )
    situation_second = common.create_situation_v2(pgsql, situation_maas_id)

    compensation_info = {
        'compensation_value': rounded_value,
        'numeric_value': numeric_value,
        'status': 'success',
    }
    if currency:
        compensation_info['currency'] = currency

    compensation_first = common.create_compensation_v2(
        pgsql,
        first_compensation_id,
        compensation_maas_id,
        user,
        situations=[situation_first.get_id(), situation_second.get_id()],
        main_situation_id=situation_first.maas_id,
        compensation_info=compensation_info,
        source=source,
        compensation_type=compensation_type,
        is_full=is_full,
        rate=rounded_value,
        error_code=error_code,
    )

    situation_first.update_db()
    situation_second.update_db()
    compensation_first.update_db()

    assert compensation_first.get_situations() == [
        situation_first.get_id(),
        situation_second.get_id(),
    ]
    assert (
        situation_first.get_bound_compensation() == compensation_first.get_id()
    )

    grocery_orders.add_order(
        order_id=situation_first.order_id,
        user_info={'personal_phone_id': user.personal_phone_id},
        country_iso2=country_iso2,
        cart_id=cart_id,
        locale='ru',
    )
    grocery_cart.add_cart(cart_id)
    grocery_cart.set_client_price(str(client_price), cart_id=cart_id)
    grocery_cart.set_payment_method({'type': payment_method}, cart_id=cart_id)
    grocery_cart.set_items_v2(consts.CART_ITEMS)

    eats_compensations_matrix.check_request(
        {
            'situation_id': situation_maas_id,
            'source': situation_first.source,
            'order_cost': client_price,
            'payment_method_type': payment_method,
            'antifraud_score': user.antifraud_score,
            'country': country_iso2,
            'compensation_count': 1,  # as we created 1 compensation in db
        },
    )
    eats_compensations_matrix.set_compensation_list_response(
        common.create_matrix_response_json(situation_second),
    )
    eats_compensations_matrix.set_get_by_id_response(
        common.get_situation_by_code_response(
            situation_first, situation_first.situation_code,
        ),
    )
    headers = {'X-Yandex-Login': user.comments[0]['support_login']}
    request_json = {'order_id': situation_first.order_id}
    expected_response = {
        'selected_compensations': [
            {
                'yandex_login': user.comments[0]['support_login'],
                'compensation': {
                    'type': v3_type,
                    'description': description,
                    'created': _get_formatted_time(compensation_first.created),
                    'status': compensation_info['status'],
                    'source': source,
                },
                'situations': [
                    {
                        'situation_id': situation_first.maas_id,
                        'comment': situation_first.comment,
                        'source': situation_first.source,
                        'has_photo': situation_first.has_photo,
                        'product_infos': situation_first.product_infos,
                        'situation_code': situation_first.situation_code,
                        'eats_situation_description': (
                            common.get_situation_by_code_response(
                                situation_first,
                                situation_first.situation_code,
                            )['situation']
                        ),
                    },
                    {
                        'situation_id': situation_first.maas_id,
                        'comment': situation_first.comment,
                        'source': situation_first.source,
                        'has_photo': situation_first.has_photo,
                        'product_infos': situation_first.product_infos,
                        'situation_code': situation_first.situation_code,
                        'eats_situation_description': (
                            common.get_situation_by_code_response(
                                situation_first,
                                situation_first.situation_code,
                            )['situation']
                        ),
                    },
                ],
                'main_situation_id': situation_first.maas_id,
                'order_id': 'order_id',
            },
        ],
        'unbound_situations': [
            {
                'situation': {
                    'situation_id': situation_second.maas_id,
                    'comment': situation_second.comment,
                    'source': situation_second.source,
                    'has_photo': situation_second.has_photo,
                    'product_infos': situation_second.product_infos,
                    'situation_code': situation_second.situation_code,
                    'eats_situation_description': (
                        common.get_situation_by_code_response(
                            situation_second, situation_second.situation_code,
                        )['situation']
                    ),
                },
                'compensation_pack': [],
            },
        ],
    }

    response = await taxi_grocery_support.post(
        '/v3/api/compensation/get-matrix-info',
        json=request_json,
        headers=headers,
    )
    assert response.status_code == 200

    if error_code:
        expected_response['selected_compensations'][0][
            'compensation_error_code'
        ] = error_code

    assert response.json() == expected_response
    assert eats_compensations_matrix.times_compensation_list_called() == 1
    assert eats_compensations_matrix.times_get_by_id_called() == 1


@pytest.mark.now(models.NOW)
async def test_proxy_v3_404(
        taxi_grocery_support,
        pgsql,
        grocery_orders,
        grocery_cart,
        eats_compensations_matrix,
        now,
):
    situation_maas_id = 14
    country_iso2 = 'ru'
    order_cost = 11.0
    payment_method = 'card'
    cart_id = str(uuid.uuid4())

    user = common.create_default_customer(pgsql, now)
    user.update_db()

    situation_first = common.create_situation_v2(pgsql, situation_maas_id)

    situation_first.update_db()

    grocery_orders.add_order(
        order_id=situation_first.order_id,
        user_info={'personal_phone_id': user.personal_phone_id},
        country_iso2=country_iso2,
        cart_id=cart_id,
        locale='ru',
    )
    grocery_cart.add_cart(cart_id)
    grocery_cart.set_client_price(str(order_cost), cart_id=cart_id)
    grocery_cart.set_payment_method({'type': payment_method}, cart_id=cart_id)

    eats_compensations_matrix.set_error_code(400)

    headers = {'X-Yandex-Login': user.comments[0]['support_login']}
    request_json = {'order_id': situation_first.order_id}
    response = await taxi_grocery_support.post(
        '/v3/api/compensation/get-matrix-info',
        json=request_json,
        headers=headers,
    )
    assert response.status_code == 404


@pytest.mark.now(models.NOW)
async def test_proxy_v3_with_errors(
        taxi_grocery_support, pgsql, grocery_orders, grocery_cart, now,
):
    country_iso2 = 'ru'
    order_cost = '11.0'
    order_id = 'test_id'
    cart_id = str(uuid.uuid4())

    user = common.create_default_customer(pgsql, now)
    user.update_db()

    grocery_orders.add_order(
        order_id=order_id,
        user_info={'personal_phone_id': user.personal_phone_id},
        country_iso2=country_iso2,
        cart_id=cart_id,
    )
    grocery_cart.add_cart(cart_id)
    grocery_cart.set_client_price(order_cost, cart_id=cart_id)

    headers = {'X-Yandex-Login': user.comments[0]['support_login']}
    request_json = {'order_id': order_id}
    response = await taxi_grocery_support.post(
        '/v3/api/compensation/get-matrix-info',
        json=request_json,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()['errors'] == [
        'no_locale_in_order',
        'no_cart_payment_method',
    ]


@pytest.mark.now(models.NOW)
async def test_proxy_v3_filtering(
        taxi_grocery_support,
        pgsql,
        grocery_orders,
        grocery_cart,
        eats_compensations_matrix,
        now,
):
    situation_maas_id = 14
    country_iso2 = 'ru'
    payment_method = 'card'
    cart_id = str(uuid.uuid4())
    client_price = 15.0

    user = common.create_default_customer(pgsql, now)
    user.update_db()

    situation_second = common.create_situation_v2(pgsql, situation_maas_id)
    situation_second.update_db()

    grocery_orders.add_order(
        order_id=situation_second.order_id,
        user_info={'personal_phone_id': user.personal_phone_id},
        country_iso2=country_iso2,
        cart_id=cart_id,
        locale='ru',
    )
    grocery_cart.add_cart(cart_id)
    grocery_cart.set_client_price(str(client_price), cart_id=cart_id)
    grocery_cart.set_payment_method({'type': payment_method}, cart_id=cart_id)
    grocery_cart.set_items_v2(consts.CART_ITEMS)

    eats_compensations_matrix.check_request(
        {
            'situation_id': situation_maas_id,
            'source': situation_second.source,
            'order_cost': client_price,
            'payment_method_type': payment_method,
            'antifraud_score': user.antifraud_score,
            'country': country_iso2,
            'compensation_count': 0,
        },
    )
    eats_compensations_matrix.set_compensation_list_response(
        common.create_filtering_response_json(situation_second),
    )
    eats_compensations_matrix.set_get_by_id_response(
        common.get_situation_by_code_response(
            situation_second, situation_second.situation_code,
        ),
    )

    headers = {'X-Yandex-Login': user.comments[0]['support_login']}
    request_json = {'order_id': situation_second.order_id}
    expected_response = {
        'selected_compensations': [],  # Delivery and tips were filtered
        'unbound_situations': [
            {
                'situation': {
                    'situation_id': situation_second.maas_id,
                    'comment': situation_second.comment,
                    'source': situation_second.source,
                    'has_photo': situation_second.has_photo,
                    'product_infos': situation_second.product_infos,
                    'situation_code': situation_second.situation_code,
                    'eats_situation_description': (
                        common.get_situation_by_code_response(
                            situation_second, situation_second.situation_code,
                        )['situation']
                    ),
                },
                'compensation_pack': [],
            },
        ],
    }

    response = await taxi_grocery_support.post(
        '/v3/api/compensation/get-matrix-info',
        json=request_json,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.now(models.NOW)
async def test_proxy_v3_tristero_filtering(
        taxi_grocery_support,
        pgsql,
        grocery_orders,
        grocery_cart,
        eats_compensations_matrix,
        now,
):
    situation_maas_id = 14
    country_iso2 = 'ru'
    payment_method = 'card'
    cart_id = str(uuid.uuid4())
    client_price = 0.0

    user = common.create_default_customer(pgsql, now)
    user.update_db()

    situation_second = common.create_situation_v2(pgsql, situation_maas_id)
    situation_second.update_db()

    grocery_orders.add_order(
        order_id=situation_second.order_id,
        user_info={'personal_phone_id': user.personal_phone_id},
        country_iso2=country_iso2,
        cart_id=cart_id,
        locale='ru',
        grocery_flow_version='tristero_flow_v2',
    )
    grocery_cart.add_cart(cart_id)
    grocery_cart.set_client_price(str(client_price), cart_id=cart_id)

    eats_compensations_matrix.check_request(
        {
            'situation_id': situation_maas_id,
            'source': situation_second.source,
            'order_cost': client_price,
            'payment_method_type': payment_method,
            'antifraud_score': user.antifraud_score,
            'country': country_iso2,
            'compensation_count': 0,
        },
    )
    eats_compensations_matrix.set_compensation_list_response(
        common.create_tristero_response_json(situation_second),
    )
    eats_compensations_matrix.set_get_by_id_response(
        common.get_situation_by_code_response(
            situation_second, situation_second.situation_code,
        ),
    )

    headers = {'X-Yandex-Login': user.comments[0]['support_login']}
    request_json = {'order_id': situation_second.order_id}
    expected_response = {
        'errors': ['no_cart_payment_method'],
        'selected_compensations': [],
        'unbound_situations': [
            {
                'situation': {
                    'situation_id': situation_second.maas_id,
                    'comment': situation_second.comment,
                    'source': situation_second.source,
                    'has_photo': situation_second.has_photo,
                    'product_infos': situation_second.product_infos,
                    'situation_code': situation_second.situation_code,
                    'eats_situation_description': (
                        common.get_situation_by_code_response(
                            situation_second, situation_second.situation_code,
                        )['situation']
                    ),
                },
                # Refund and voucher were filtered
                'compensation_pack': [
                    {
                        'pack_description': 'Промокод на 10%',
                        'requires_custom_value': False,
                        'id': 3,
                    },
                ],
            },
        ],
    }

    response = await taxi_grocery_support.post(
        '/v3/api/compensation/get-matrix-info',
        json=request_json,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'is_fraud, expected_antifraud_score', [(True, 'bad'), (False, 'good')],
)
@pytest.mark.config(
    GROCERY_SUPPORT_ENABLE_ORDER_FRAUD_COMPENSATION_FILTER=True,
)
@pytest.mark.now(models.NOW)
async def test_compensations_antifraud_check(
        taxi_grocery_support,
        pgsql,
        grocery_orders,
        grocery_cart,
        eats_compensations_matrix,
        now,
        is_fraud,
        expected_antifraud_score,
        antifraud,
):
    first_compensation_id = str(uuid.uuid4())
    compensation_maas_id = 11
    situation_maas_id = 14
    country_iso2 = 'ru'
    payment_method = 'card'
    client_price = 15.0

    antifraud.set_is_fraud(is_fraud)
    user = common.create_default_customer(pgsql, now)
    user.update_db()

    situation_first = common.create_situation_v2(
        pgsql, situation_maas_id, first_compensation_id,
    )

    compensation_first = common.create_compensation_v2(
        pgsql,
        first_compensation_id,
        compensation_maas_id,
        user,
        situations=[situation_first.get_id()],
        main_situation_id=situation_first.maas_id,
    )
    situation_first.update_db()
    compensation_first.update_db()

    order = grocery_orders.add_order(
        order_id=situation_first.order_id,
        user_info={'personal_phone_id': user.personal_phone_id},
        country_iso2=country_iso2,
        locale='ru',
        city='Москва',
        street='Большие Каменьщики',
        house='37',
        flat='24',
    )
    short_address = '{}, {} {} {}'.format(
        order['city'], order['street'], order['house'], order['flat'],
    )

    antifraud.check_order_antifraud_request(
        order_nr=order['order_id'], short_address=short_address,
    )
    eats_compensations_matrix.check_request(
        {
            'situation_id': situation_maas_id,
            'source': situation_first.source,
            'order_cost': client_price,
            'payment_method_type': payment_method,
            'antifraud_score': expected_antifraud_score,
            'country': country_iso2,
            'compensation_count': 1,
        },
    )
    eats_compensations_matrix.set_get_by_id_response(
        common.get_situation_by_code_response(
            situation_first, situation_first.situation_code,
        ),
    )
    headers = {'X-Yandex-Login': user.comments[0]['support_login']}
    request_json = {'order_id': situation_first.order_id}

    response = await taxi_grocery_support.post(
        '/v3/api/compensation/get-matrix-info',
        json=request_json,
        headers=headers,
    )
    assert response.status_code == 200
    assert eats_compensations_matrix.times_get_by_id_called() == 1


@pytest.mark.parametrize(
    'compensation_type, is_full, rate, description, requires_custom_value',
    [
        ('promocode', False, 15, 'Промокод на 15%', False),
        ('superVoucher', False, 10, 'Супер-ваучер на 10 ₽', False),
        (
            'superVoucher',
            False,
            None,
            'Супер-ваучер на произвольную сумму',
            True,
        ),
    ],
)
@pytest.mark.now(models.NOW)
async def test_unbound_situations_text(
        taxi_grocery_support,
        pgsql,
        grocery_orders,
        grocery_cart,
        eats_compensations_matrix,
        now,
        compensation_type,
        is_full,
        rate,
        description,
        requires_custom_value,
        mockserver,
):
    compensation_maas_id = 10
    situation_maas_id = 14
    country_iso2 = 'ru'
    payment_method = 'card'
    cart_id = str(uuid.uuid4())
    client_price = 15.0

    user = common.create_default_customer(pgsql, now)
    user.update_db()

    situation = common.create_situation_v2(pgsql, situation_maas_id)
    situation.update_db()

    grocery_orders.add_order(
        order_id=situation.order_id,
        user_info={'personal_phone_id': user.personal_phone_id},
        country_iso2=country_iso2,
        cart_id=cart_id,
        locale='ru',
    )
    grocery_cart.add_cart(cart_id)
    grocery_cart.set_client_price(str(client_price), cart_id=cart_id)
    grocery_cart.set_payment_method({'type': payment_method}, cart_id=cart_id)
    grocery_cart.set_items_v2(consts.CART_ITEMS)

    compensation = common.create_compensation_v2(
        pgsql,
        str(uuid.uuid4()),
        compensation_maas_id,
        user,
        compensation_type=compensation_type,
        source=situation.source,
        is_full=is_full,
        rate=rate,
    )
    eats_compensations_matrix.set_compensation_list_response(
        common.get_submit_situation_response(
            situation, compensation, 'some_code', compensation_type,
        ),
    )
    eats_compensations_matrix.set_get_by_id_response(
        common.get_situation_by_code_response(
            situation, situation.situation_code,
        ),
    )

    headers = {'X-Yandex-Login': user.comments[0]['support_login']}
    request_json = {'order_id': situation.order_id}
    expected_pack = (
        {
            'pack_description': description,
            'requires_custom_value': requires_custom_value,
            'id': 123,
        },
    )
    response = await taxi_grocery_support.post(
        '/v3/api/compensation/get-matrix-info',
        json=request_json,
        headers=headers,
    )
    assert response.status_code == 200
    assert len(response.json()['unbound_situations']) == 1
    assert (
        response.json()['unbound_situations'][0]['compensation_pack'][0]
        == expected_pack[0]
    )
