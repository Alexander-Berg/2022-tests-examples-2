import json

import pytest

from . import consts
from . import headers
from . import helpers
from . import models
from .plugins import mock_grocery_payments

BILLING_SETTING_VERSION = 'billing_settings'

ITEM_ID_1 = 'item_id_1'
CURRENT_QUANTITY = '4'
NEW_QUANTITY_REMOVE = '1'
NEW_QUANTITY_ADD = '7'


def _prepare_for_wms_revert(
        grocery_cart,
        grocery_wms_gateway,
        *,
        order,
        correcting_type='remove',
        reserve_timeout=None,
):
    item_id_1 = 'item_id_1'
    item_id_2 = 'item_id_2'
    old_quantity = '3'
    price = '100'
    full_sum_after_revert = '600'

    reverted_items = [
        models.GroceryCartItem(
            item_id=item_id_1, quantity=old_quantity, price=price,
        ),
        models.GroceryCartItem(
            item_id=item_id_2, quantity=old_quantity, price=price,
        ),
    ]

    grocery_cart.set_correcting_type(correcting_type=correcting_type)
    grocery_cart.set_cart_data(
        cart_id=order.cart_id, cart_version=order.cart_version,
    )
    grocery_cart.set_items(reverted_items)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    grocery_wms_gateway.check_reserve(
        items=reverted_items,
        full_sum=full_sum_after_revert,
        order=order,
        order_revision=str(order.order_revision),
        reserve_timeout=reserve_timeout,
    )


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize('wms_code', [200, 409, 400])
async def test_revert_wms(
        pgsql,
        taxi_grocery_orders,
        grocery_cart,
        grocery_wms_gateway,
        grocery_payments,
        processing,
        wms_code,
        grocery_depots,
):
    order = models.Order(
        pgsql=pgsql,
        billing_settings_version=BILLING_SETTING_VERSION,
        edit_status='failed',
        order_revision=1,
        state=models.OrderState(
            hold_money_status='failed', wms_reserve_status='success',
        ),
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    if wms_code != 200:
        grocery_wms_gateway.set_http_resp(
            resp='{"code": "WMS_400", "message": "Bad request"}',
            code=wms_code,
        )

    _prepare_for_wms_revert(
        grocery_cart, grocery_wms_gateway, order=order, reserve_timeout=7 * 60,
    )

    event_policy = {
        'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
        'stop_retry_after': helpers.skip_minutes(consts.STOP_AFTER_MINUTES),
        'retry_interval': consts.RETRY_INTERVAL_MINUTES * 60,
        'retry_count': 10,
    }

    to_revert = {'revert_money': False, 'revert_wms': True}
    request = {
        'order_id': order.order_id,
        'order_revision': order.order_revision,
        'to_revert': to_revert,
        'event_policy': event_policy,
    }

    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/revert', json=request,
    )

    prev_revision = order.order_revision
    prev_cart_version = order.cart_version
    order.update()

    assert response.status_code == 200
    if wms_code != 200:
        assert order.order_revision == prev_revision

        events = list(processing.events(scope='grocery', queue='processing'))
        assert len(events) == 2
    else:
        assert order.state.hold_money_status == 'success'
        assert order.state.wms_reserve_status is None
        assert order.order_revision == prev_revision
        assert order.edit_status is None
        assert order.child_cart_id is None

    assert grocery_cart.retrieve_times_called() == 1
    assert grocery_wms_gateway.times_reserve_called() == 1
    assert order.cart_version == prev_cart_version


CURRENT_ITEMS = [
    models.GroceryCartItem(
        item_id=ITEM_ID_1, quantity=CURRENT_QUANTITY, price='100',
    ),
    models.GroceryCartItem(item_id='item_id_2', quantity='4', price='100'),
]


def _get_new_quantity(correcting_type='remove'):
    if correcting_type == 'add':
        return NEW_QUANTITY_ADD
    return NEW_QUANTITY_REMOVE


def _get_corrected_items(correcting_type='remove'):
    return [
        models.GroceryCartItem(
            item_id=ITEM_ID_1,
            quantity=_get_new_quantity(correcting_type),
            price='100',
        ),
        models.GroceryCartItem(item_id='item_id_2', quantity='4', price='100'),
    ]


@pytest.fixture
def _prepare(pgsql, grocery_cart, grocery_payments, grocery_depots):
    def _do(country, correcting_type='remove'):
        order = models.Order(
            pgsql=pgsql,
            status='assembling',
            billing_settings_version=BILLING_SETTING_VERSION,
            state=models.OrderState(
                hold_money_status='success', wms_reserve_status='failed',
            ),
        )

        grocery_cart.set_cart_data(
            cart_id=order.cart_id, cart_version=order.cart_version,
        )
        grocery_cart.set_items(CURRENT_ITEMS)
        grocery_cart.set_correcting_type(correcting_type=correcting_type)

        payment_method = {'type': 'card', 'id': 'test_payment_method_id'}
        grocery_cart.set_payment_method(payment_method)

        grocery_depots.add_depot(
            legacy_depot_id=order.depot_id,
            country_iso3=country.country_iso3,
            currency=country.currency,
        )

        grocery_payments.check_update(
            order_id=order.order_id,
            operation_id='update-{}-{}'.format(
                order.order_revision, order.order_version,
            ),
            country_iso3=country.country_iso3,
            items_by_payment_types=[
                mock_grocery_payments.get_items_by_payment_type(
                    CURRENT_ITEMS, payment_method,
                ),
            ],
            user_info=mock_grocery_payments.USER_INFO,
        )

        models.OrderAuthContext(
            pgsql=pgsql,
            order_id=order.order_id,
            raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
        )

        return order

    return _do


@consts.COUNTRIES
@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize('money_code', [200, 500, 409, 400])
async def test_revert_money(
        taxi_grocery_orders,
        grocery_cart,
        grocery_payments,
        processing,
        country,
        _prepare,
        money_code,
):
    order = _prepare(country)

    if money_code != 200:
        grocery_payments.set_error_code(
            handler=mock_grocery_payments.UPDATE, code=money_code,
        )

    event_policy = {
        'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
        'stop_retry_after': helpers.skip_minutes(consts.STOP_AFTER_MINUTES),
        'retry_interval': consts.RETRY_INTERVAL_MINUTES * 60,
        'retry_count': 10,
    }

    to_revert = {'revert_money': True, 'revert_wms': False}
    request = {
        'order_id': order.order_id,
        'order_revision': order.order_revision,
        'to_revert': to_revert,
        'event_policy': event_policy,
    }

    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/revert', json=request,
    )
    prev_revision = order.order_revision
    prev_cart_version = order.cart_version
    order.update()

    if money_code == 200:
        assert response.status_code == 200
        assert order.state.wms_reserve_status == 'success'
        assert order.order_revision == prev_revision
        assert order.state.hold_money_status is None
        assert order.edit_status is None
        assert order.child_cart_id is None
    elif money_code == 500:
        assert response.status_code == 200
        assert order.order_revision == prev_revision

        events = list(processing.events(scope='grocery', queue='processing'))
        assert len(events) == 1
    else:
        assert response.status_code == 500
        assert order.order_revision == prev_revision

    assert grocery_payments.times_update_called() == 1
    assert grocery_cart.retrieve_times_called() == 1
    assert order.cart_version == prev_cart_version


@pytest.mark.now(consts.NOW)
async def test_wrong_revision(pgsql, taxi_grocery_orders):
    order = models.Order(pgsql=pgsql)

    request = {
        'order_id': order.order_id,
        'order_revision': order.order_revision - 1,
        'to_revert': {'revert_money': True, 'revert_wms': False},
    }

    response = await taxi_grocery_orders.post(
        '/processing/v1/correct/revert', json=request,
    )

    assert response.status_code == 409


async def test_stop_after(
        processing, mocked_time, _run_with_error, _retry_after_error,
):
    mocked_time.set(consts.NOW_DT)
    # Without retry_interval and error_after we cannot return 429 error, we
    # should return 500 to see it in alert chat/grafana.
    order = await _run_with_error(
        expected_code=500,
        event_policy={
            'stop_retry_after': {'minutes': consts.STOP_AFTER_MINUTES},
        },
    )

    # try again later, after "stop_after".
    await _retry_after_error(
        order=order,
        to_revert={'revert_money': True, 'revert_wms': False},
        after_minutes=consts.STOP_AFTER_MINUTES + 1,
        event_policy={
            'stop_retry_after': helpers.skip_minutes(
                consts.STOP_AFTER_MINUTES,
            ),
        },
        expected_code=200,
    )

    events = list(processing.events(scope='grocery', queue='processing'))
    assert not events


async def test_error_after(
        _run_with_error, processing, mocked_time, _retry_after_error,
):
    mocked_time.set(consts.NOW_DT)
    # With `error_after` we don't want to see messages in alert chat, we want
    # to ignore problems until `error_after` happened.
    order = await _run_with_error(
        expected_code=429,
        event_policy={
            'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
        },
    )

    await _retry_after_error(
        order=order,
        to_revert={'revert_money': True, 'revert_wms': False},
        after_minutes=consts.ERROR_AFTER_MINUTES + 1,
        event_policy={
            'error_after': helpers.skip_minutes(consts.ERROR_AFTER_MINUTES),
        },
        expected_code=500,
    )

    events = list(processing.events(scope='grocery', queue='processing'))
    assert not events


@pytest.fixture
def _run_with_error(
        pgsql,
        grocery_depots,
        grocery_cart,
        grocery_payments,
        taxi_grocery_orders,
        grocery_wms_gateway,
        _prepare,
):
    async def _do(expected_code, event_policy, times_called=1):
        order = _prepare(models.Country.Russia)

        grocery_payments.set_error_code(
            handler=mock_grocery_payments.UPDATE, code=500,
        )

        to_revert = {'revert_money': True, 'revert_wms': False}
        request = {
            'order_id': order.order_id,
            'order_revision': order.order_revision,
            'to_revert': to_revert,
            'event_policy': event_policy,
        }

        response = await taxi_grocery_orders.post(
            '/processing/v1/correct/revert', json=request,
        )
        order.update()

        assert response.status_code == expected_code

        return order

    return _do


@pytest.fixture
def _retry_after_error(mocked_time, taxi_grocery_orders):
    return helpers.retry_processing(
        '/processing/v1/correct/revert', mocked_time, taxi_grocery_orders,
    )
