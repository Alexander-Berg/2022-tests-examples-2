import json
import uuid

import pytest

from . import common
from . import experiments
from . import models

ML_PRODUCT_INFOS = [
    {'product_id': 'id1', 'item_price': '20', 'quantity': 4, 'currency': '$'},
]

COMPENSATION_EVENT_POLICY = {
    'error_after': models.ONE_MINUTE_FROM_NOW,
    'retry_interval': 10,
    'stop_retry_after': models.SIX_MINUTES_FROM_NOW,
    'retry_count': 1,
}


def _create_situation_ml(pgsql, maas_id, code, compensation_id=None):
    return models.SituationV2(
        pgsql,
        bound_compensation=compensation_id,
        source='ml',
        has_photo=False,
        situation_id=str(uuid.uuid4()),
        maas_id=maas_id,
        order_id='order_id',
        situation_code=code,
        product_infos=ML_PRODUCT_INFOS,
    )


def _create_situation_rover(pgsql, maas_id, code, compensation_id=None):
    return models.SituationV2(
        pgsql,
        bound_compensation=compensation_id,
        source='system',
        has_photo=False,
        situation_id=str(uuid.uuid4()),
        maas_id=maas_id,
        order_id='order_id',
        situation_code=code,
    )


def _create_compensation(
        pgsql,
        comp_id,
        maas_id,
        user,
        rate=None,
        situations=None,
        main_situation_id=None,
        compensation_info=None,
        source=None,
        situation_code=None,
        compensation_type='superVoucher',
):
    if compensation_info is None:
        compensation_info = common.get_promocode_info()

    return models.CompensationV2(
        pgsql,
        maas_id=maas_id,
        compensation_id=comp_id,
        order_id='order_id',
        support_login=user.comments[0]['support_login'],
        personal_phone_id=user.personal_phone_id,
        rate=rate,
        compensation_type=compensation_type,
        situation_ids=situations,
        main_situation_id=main_situation_id,
        raw_compensation_info=json.dumps(compensation_info),
        source=source,
        main_situation_code=situation_code,
    )


@pytest.mark.now(models.NOW)
@experiments.GROCERY_PROCESSING_EVENTS_POLICY
async def test_create_new_compensation(
        taxi_grocery_support,
        grocery_orders,
        grocery_cart,
        eats_compensations_matrix,
        pgsql,
        now,
        processing,
):
    order_id = 'order_id'
    situation_code = 'test_code'
    cart_id = str(uuid.uuid4())
    compensation_uid = str(uuid.uuid4())
    compensation_maas_id = 11
    situation_maas_id = 14
    custom_voucher_value = 123.385
    source = 'ml'

    customer = common.create_ml_customer(pgsql, now)

    compensation_info = {
        'compensation_value': int(custom_voucher_value) + 1,
        'numeric_value': str(custom_voucher_value),
        'status': 'in_progress',
        'currency': 'RUB',
    }
    situation = _create_situation_ml(
        pgsql, situation_maas_id, situation_code, compensation_uid,
    )
    compensation = _create_compensation(
        pgsql,
        compensation_uid,
        compensation_maas_id,
        customer,
        None,
        [situation.situation_id],
        situation_maas_id,
        compensation_info,
        source,
        situation_code,
    )

    order = models.Order(pgsql, order_id=order_id)
    grocery_orders.add_order(
        order_id=situation.order_id,
        user_info={
            'personal_phone_id': customer.personal_phone_id,
            'yandex_uid': customer.yandex_uid,
            'phone_id': customer.phone_id,
        },
        country_iso2='ru',
        cart_id=cart_id,
        locale='ru',
    )
    grocery_cart.add_cart(cart_id)
    grocery_cart.set_client_price(str(100), cart_id=cart_id)
    grocery_cart.set_payment_method({'type': 'card'}, cart_id=cart_id)

    eats_compensations_matrix.set_get_by_code_response(
        common.get_situation_by_code_response(situation, situation_code),
    )
    eats_compensations_matrix.set_compensation_list_response(
        common.get_submit_situation_response(
            situation, compensation, 'some_code',
        ),
    )

    request_json = {
        'order_id': order.order_id,
        'situation_code': situation_code,
        'product_infos': ML_PRODUCT_INFOS,
        'custom_voucher_value': str(custom_voucher_value),
    }

    response = await taxi_grocery_support.post(
        '/internal/ml/v1/get-compensation-by-situation-code',
        json=request_json,
    )
    assert response.status_code == 201

    events = list(processing.events(scope='grocery', queue='compensations'))
    assert len(events) == 2
    event = events[0]
    assert event.payload['order_id'] == order.order_id
    assert event.payload['reason'] == 'created'
    assert 'event_policy' not in event.payload

    compensation_event = events[1]
    assert compensation_event.payload['order_id'] == order.order_id
    assert compensation_event.payload['reason'] == 'compensation_promocode'
    assert (
        compensation_event.payload['event_policy'] == COMPENSATION_EVENT_POLICY
    )
    assert (
        compensation_event.payload['promocode_value']
        == int(custom_voucher_value) + 1
    )
    assert compensation_event.payload['promocode_value_numeric'] == str(
        custom_voucher_value,
    )

    situation.compare_with_db()
    compensation.compare_with_db()

    assert eats_compensations_matrix.times_get_by_code_called() == 1


@pytest.mark.now(models.NOW)
@experiments.GROCERY_PROCESSING_EVENTS_POLICY
async def test_create_new_compensation_rover(
        taxi_grocery_support,
        grocery_orders,
        grocery_cart,
        eats_compensations_matrix,
        pgsql,
        now,
        processing,
):
    order_id = 'order_id'
    situation_code = 'rover_promo'
    cart_id = str(uuid.uuid4())
    compensation_uid = str(uuid.uuid4())
    compensation_maas_id = 11
    situation_maas_id = 14
    custom_promocode_value = 15
    custom_compensation_value = 20
    source = 'admin_compensation'

    customer = common.create_system_customer(pgsql, now)

    compensation_info = {
        'compensation_value': custom_compensation_value,
        'numeric_value': str(custom_compensation_value),
        'status': 'in_progress',
    }
    situation = _create_situation_rover(
        pgsql, situation_maas_id, situation_code, compensation_uid,
    )
    compensation = _create_compensation(
        pgsql,
        compensation_uid,
        compensation_maas_id,
        customer,
        custom_compensation_value,
        [],
        situation_maas_id,
        compensation_info,
        source,
        situation_code=situation_code,
        compensation_type='promocode',
    )

    order = models.Order(pgsql, order_id=order_id)
    grocery_orders.add_order(
        order_id=situation.order_id,
        user_info={
            'personal_phone_id': customer.personal_phone_id,
            'yandex_uid': customer.yandex_uid,
            'phone_id': customer.phone_id,
        },
        country_iso2='ru',
        cart_id=cart_id,
        locale='ru',
    )
    grocery_cart.add_cart(cart_id)
    grocery_cart.set_client_price(str(100), cart_id=cart_id)
    grocery_cart.set_payment_method({'type': 'card'}, cart_id=cart_id)

    eats_compensations_matrix.set_get_by_code_response(
        common.get_situation_by_code_response(situation, situation_code),
    )
    eats_compensations_matrix.set_compensation_list_response(
        common.get_submit_situation_response(
            situation, compensation, situation_code,
        ),
    )

    request_json = {
        'order_id': order.order_id,
        'situation_code': situation_code,
        'custom_promocode_value': str(custom_promocode_value),
    }

    response = await taxi_grocery_support.post(
        '/processing/v1/get-compensation-by-situation-code', json=request_json,
    )
    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='compensations'))
    assert len(events) == 2
    event = events[0]
    assert event.payload['order_id'] == order.order_id
    assert event.payload['reason'] == 'created'
    assert 'event_policy' not in event.payload

    compensation_event = events[1]
    assert compensation_event.payload['order_id'] == order.order_id
    assert compensation_event.payload['reason'] == 'compensation_promocode'
    assert (
        compensation_event.payload['event_policy'] == COMPENSATION_EVENT_POLICY
    )
    assert compensation_event.payload['promocode_value'] == int(
        custom_compensation_value,
    )

    compensation.compare_with_db()

    assert eats_compensations_matrix.times_get_by_code_called() == 1


@pytest.mark.now(models.NOW)
@pytest.mark.parametrize(
    'compensation_info, expected_code',
    [
        (
            {
                'generated_promo': 'test_promo',
                'compensation_value': 15,
                'status': 'success',
            },
            200,
        ),
        ({'compensation_value': 15, 'status': 'in_progress'}, 201),
    ],
)
async def test_existing_compensation(
        taxi_grocery_support,
        grocery_orders,
        pgsql,
        now,
        compensation_info,
        expected_code,
):
    order_id = 'order_id'
    situation_code = 'test_code'
    compensation_uid = str(uuid.uuid4())
    compensation_maas_id = 11
    situation_maas_id = 14

    customer = common.create_ml_customer(pgsql, now)
    situation = _create_situation_ml(
        pgsql, situation_maas_id, situation_code, compensation_uid,
    )
    compensation = common.create_compensation_v2(
        pgsql,
        compensation_uid,
        compensation_maas_id,
        customer,
        [situation.situation_id],
        situation_maas_id,
        compensation_info,
        main_situation_code=situation_code,
    )

    situation.update_db()
    compensation.update_db()

    order = models.Order(pgsql, order_id=order_id)
    grocery_orders.add_order(
        order_id=situation.order_id,
        user_info={
            'personal_phone_id': customer.personal_phone_id,
            'yandex_uid': customer.yandex_uid,
            'phone_id': customer.phone_id,
        },
    )

    request_json = {
        'order_id': order.order_id,
        'situation_code': situation_code,
        'product_infos': ML_PRODUCT_INFOS,
    }

    response = await taxi_grocery_support.post(
        '/internal/ml/v1/get-compensation-by-situation-code',
        json=request_json,
    )
    assert response.status_code == expected_code

    if response.status_code == 200:
        assert response.json()['compensation']['id'] == compensation.maas_id
        assert (
            response.json()['compensation']['type']
            == compensation.compensation_type
        )
        assert (
            response.json()['compensation']['promocode_info']
            == compensation_info
        )


@pytest.mark.parametrize(
    'compensation_info, expected_code',
    [
        (
            {
                'generated_promo': 'test_promo',
                'compensation_value': 15,
                'status': 'success',
            },
            200,
        ),
    ],
)
async def test_existing_compensation_rover(
        taxi_grocery_support,
        grocery_orders,
        pgsql,
        now,
        compensation_info,
        expected_code,
):
    order_id = 'order_id'
    situation_code = 'test_code'
    compensation_uid = str(uuid.uuid4())
    compensation_maas_id = 11
    situation_maas_id = 14

    customer = common.create_ml_customer(pgsql, now)
    situation = _create_situation_ml(
        pgsql, situation_maas_id, situation_code, compensation_uid,
    )
    compensation = common.create_compensation_v2(
        pgsql,
        compensation_uid,
        compensation_maas_id,
        customer,
        [situation.situation_id],
        situation_maas_id,
        compensation_info,
        main_situation_code=situation_code,
    )

    situation.update_db()
    compensation.update_db()

    order = models.Order(pgsql, order_id=order_id)
    grocery_orders.add_order(
        order_id=situation.order_id,
        user_info={
            'personal_phone_id': customer.personal_phone_id,
            'yandex_uid': customer.yandex_uid,
            'phone_id': customer.phone_id,
        },
    )

    request_json = {
        'order_id': order.order_id,
        'situation_code': situation_code,
        'product_infos': ML_PRODUCT_INFOS,
    }

    response = await taxi_grocery_support.post(
        '/processing/v1/get-compensation-by-situation-code', json=request_json,
    )
    assert response.status_code == expected_code


@pytest.mark.now(models.NOW)
@pytest.mark.parametrize(
    'handler',
    [
        '/internal/ml/v1/get-compensation-by-situation-code',
        '/processing/v1/get-compensation-by-situation-code',
    ],
)
async def test_404(
        taxi_grocery_support,
        grocery_orders,
        grocery_cart,
        eats_compensations_matrix,
        pgsql,
        now,
        handler,
):
    order_id = 'order_id'
    cart_id = str(uuid.uuid4())
    situation_code = 'test_code'
    situation_maas_id = 14

    customer = common.create_ml_customer(pgsql, now)
    situation = _create_situation_ml(pgsql, situation_maas_id, situation_code)

    order = models.Order(pgsql, order_id=order_id)
    grocery_orders.add_order(
        order_id=situation.order_id,
        user_info={
            'personal_phone_id': customer.personal_phone_id,
            'yandex_uid': customer.yandex_uid,
            'phone_id': customer.phone_id,
        },
        country_iso2='ru',
        cart_id=cart_id,
        locale='ru',
    )
    grocery_cart.add_cart(cart_id)
    grocery_cart.set_client_price(str(100), cart_id=cart_id)
    grocery_cart.set_payment_method({'type': 'card'}, cart_id=cart_id)

    eats_compensations_matrix.set_get_by_code_response(
        common.get_situation_by_code_response(situation, situation_code),
    )
    eats_compensations_matrix.set_compensation_list_response(
        common.create_matrix_response_json(situation),
    )

    request_json = {
        'order_id': order.order_id,
        'situation_code': situation_code,
        'product_infos': ML_PRODUCT_INFOS,
    }

    response = await taxi_grocery_support.post(handler, json=request_json)
    assert response.status_code == 404
