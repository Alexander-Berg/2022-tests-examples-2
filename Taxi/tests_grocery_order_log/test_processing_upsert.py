import datetime
import uuid

import pytest

from tests_grocery_order_log import helpers
from tests_grocery_order_log import models

EXTRA_RECEIPT = {
    'title': 'payment_receipt',
    'receipt_url': 'payment_receipt_url_extra',
}


def _copy_order_log_info(order_log, previous_order_log):
    order_log.cart_id = previous_order_log.cart_id
    order_log.order_state = previous_order_log.order_state
    order_log.depot_id = previous_order_log.depot_id
    order_log.receipts = previous_order_log.receipts
    order_log.destination = previous_order_log.destination
    order_log.cart_items = previous_order_log.cart_items
    order_log.order_created_date = previous_order_log.order_created_date
    order_log.order_finished_date = previous_order_log.order_finished_date
    order_log.eats_user_id = previous_order_log.eats_user_id
    order_log.short_order_id = previous_order_log.short_order_id
    order_log.yandex_uid = previous_order_log.yandex_uid
    order_log.refund = previous_order_log.refund
    order_log.courier = previous_order_log.courier
    order_log.cart_total_discount = previous_order_log.cart_total_discount
    order_log.cart_total_price = previous_order_log.cart_total_price
    order_log.delivery_cost = previous_order_log.delivery_cost
    order_log.geo_id = previous_order_log.geo_id
    order_log.country_iso3 = previous_order_log.country_iso3


def _copy_order_log_index(order_log_index, previous_order_log_index):
    order_log_index.cart_id = previous_order_log_index.cart_id
    order_log_index.eats_user_id = previous_order_log_index.eats_user_id
    order_log_index.short_order_id = previous_order_log_index.short_order_id
    order_log_index.yandex_uid = previous_order_log_index.yandex_uid
    order_log_index.personal_phone_id = (
        previous_order_log_index.personal_phone_id
    )


def _check_order_log_info(order_log, previous_order_log):
    assert order_log.order_state == previous_order_log.order_state
    assert order_log.updated != previous_order_log.updated

    assert (
        order_log.order_created_date == previous_order_log.order_created_date
    )
    assert (
        order_log.order_finished_date == previous_order_log.order_finished_date
    )

    assert order_log.cart_id == previous_order_log.cart_id
    assert order_log.depot_id == previous_order_log.depot_id
    assert str(order_log.refund) == str(previous_order_log.refund)
    assert order_log.receipts == previous_order_log.receipts
    assert order_log.destination == previous_order_log.destination
    assert order_log.eats_user_id == previous_order_log.eats_user_id
    assert order_log.short_order_id == previous_order_log.short_order_id
    assert order_log.yandex_uid == previous_order_log.yandex_uid
    assert order_log.courier == previous_order_log.courier
    assert str(order_log.cart_total_discount) == str(
        previous_order_log.cart_total_discount,
    )
    assert str(order_log.cart_total_price) == str(
        previous_order_log.cart_total_price,
    )
    assert str(order_log.delivery_cost) == str(
        previous_order_log.delivery_cost,
    )
    assert order_log.cart_items == previous_order_log.cart_items
    assert order_log.geo_id == previous_order_log.geo_id
    assert order_log.country_iso3 == previous_order_log.country_iso3


def _check_order_log_index(order_log_index, previous_log_index):
    assert (
        order_log_index.order_created_date
        == previous_log_index.order_created_date
    )
    assert order_log_index.eats_user_id == previous_log_index.eats_user_id
    assert order_log_index.short_order_id == previous_log_index.short_order_id
    assert order_log_index.yandex_uid == previous_log_index.yandex_uid
    assert (
        order_log_index.personal_phone_id
        == previous_log_index.personal_phone_id
    )


async def test_basic(taxi_grocery_order_log, pgsql):
    order_log = models.OrderLog(pgsql)
    order_log_index = models.OrderLogIndex(pgsql, order_id=order_log.order_id)
    order_log.update_db()
    order_log_index.update_db()
    request = helpers.get_upsert_request(
        order_log.order_id, order_log.cart_id, order_log.depot_id,
    )
    response = await taxi_grocery_order_log.post(
        '/processing/v1/insert', json=request,
    )
    assert response.status_code == 200
    order_log.update()
    helpers.check_upserted_order_log(order_log, request)
    order_log_index.update()
    helpers.check_upserted_order_log_index(order_log_index, request)


async def test_upsert_empty_data(taxi_grocery_order_log, pgsql):
    order_log = models.OrderLog(
        pgsql,
        order_created_date=models.NOW_DT,
        short_order_id='short_order_id',
        order_state='created',
        order_source='market',
        cart_total_price='2222.0000',
        cart_total_discount='222.0000',
        delivery_cost='2.2222',
        refund='3.3333',
        currency='RUB',
        cart_items=helpers.CART_ITEMS,
        receipts=helpers.RECEIPTS,
        destination=helpers.DESTINATION,
        courier='courier',
        yandex_uid='yandex_uid',
        eats_user_id='eats_user_id',
        depot_id='depot_id',
        cart_id='cart_id',
        geo_id='geo_id',
        country_iso3='RUS',
    )
    previous_order_log = models.OrderLog(
        pgsql, updated=datetime.datetime.now(),
    )
    _copy_order_log_info(
        order_log=previous_order_log, previous_order_log=order_log,
    )
    order_log.update_db()

    order_log_index = models.OrderLogIndex(
        pgsql,
        order_created_date=models.NOW,
        order_id=order_log.order_id,
        yandex_uid='yandex_uid',
        eats_user_id='eats_user_id',
        personal_phone_id='personal_phone_id',
        cart_id='cart_id',
    )
    previous_log_index = models.OrderLogIndex(
        pgsql, order_id=order_log.order_id,
    )
    _copy_order_log_index(previous_log_index, order_log_index)
    order_log_index.update_db()

    request = {
        'order_id': order_log.order_id,
        'order_log_info': {'order_state': 'closed'},
    }
    response = await taxi_grocery_order_log.post(
        '/processing/v1/insert', json=request,
    )
    assert response.status_code == 200
    order_log.update()
    previous_order_log.order_state = order_log.order_state
    _check_order_log_info(order_log, previous_order_log)

    order_log_index.update()
    _check_order_log_index(order_log_index, previous_log_index)


async def test_upsert_on_empty_log(taxi_grocery_order_log, pgsql):
    order_log = models.OrderLog(
        pgsql,
        order_state='created',
        order_created_date=None,
        order_finished_date=None,
        yandex_uid=None,
        cart_id=None,
    )
    order_log_index = models.OrderLogIndex(
        pgsql, order_id=order_log.order_id, order_created_date=models.NOT_NOW,
    )
    order_log.update_db()
    order_log_index.update_db()
    request = helpers.get_upsert_request(
        order_log.order_id, 'test_cart_id', 'test_depot_id',
    )
    response = await taxi_grocery_order_log.post(
        '/processing/v1/insert', json=request,
    )
    assert response.status_code == 200
    order_log.update()
    order_log_index.update()
    helpers.check_upserted_order_log(order_log, request)
    helpers.check_upserted_order_log_index(order_log_index, request)


@pytest.mark.parametrize(
    'current_receipts, new_receipts, expected_receipts',
    [
        (None, helpers.RECEIPTS, helpers.RECEIPTS),
        ([], helpers.RECEIPTS, helpers.RECEIPTS),
        ({}, helpers.RECEIPTS, helpers.RECEIPTS),
        (helpers.RECEIPTS, None, helpers.RECEIPTS),
        (helpers.RECEIPTS, [], helpers.RECEIPTS),
        (helpers.RECEIPTS, helpers.RECEIPTS, helpers.RECEIPTS),
        (
            helpers.RECEIPTS,
            [EXTRA_RECEIPT],
            helpers.RECEIPTS + [EXTRA_RECEIPT],
        ),
        (helpers.RECEIPTS, helpers.RECEIPTS * 2, helpers.RECEIPTS),
        ([], [], []),
        (None, [], []),
        (None, None, []),
    ],
)
async def test_append_receipts(
        taxi_grocery_order_log,
        pgsql,
        current_receipts,
        new_receipts,
        expected_receipts,
):
    order_log = models.OrderLog(
        pgsql, order_state='closed', receipts=current_receipts,
    )
    previous_order_log = models.OrderLog(
        pgsql, updated=datetime.datetime.now(),
    )
    _copy_order_log_info(
        order_log=previous_order_log, previous_order_log=order_log,
    )
    order_log.update_db()

    order_log_index = models.OrderLogIndex(pgsql, order_id=order_log.order_id)
    order_log_index.update_db()

    request = {
        'order_id': order_log.order_id,
        'order_log_info': {'receipts': new_receipts},
    }
    response = await taxi_grocery_order_log.post(
        '/processing/v1/insert', json=request,
    )
    assert response.status_code == 200

    order_log.update()
    assert order_log.order_state == 'closed'
    assert order_log.receipts == expected_receipts

    previous_order_log.receipts = order_log.receipts
    _check_order_log_info(order_log, previous_order_log)


@pytest.mark.parametrize(
    'order_log_extra, expect_retrieve',
    [
        (dict(order_state='created'), False),
        (dict(order_state='closed'), True),
        (dict(receipts=None), True),
        (dict(receipts=[]), True),
    ],
)
async def test_retrieve_curr_state(
        taxi_grocery_order_log,
        pgsql,
        testpoint,
        order_log_extra,
        expect_retrieve,
):
    order_log = models.OrderLog(pgsql)
    order_log.update_db()

    order_log_index = models.OrderLogIndex(pgsql, order_id=order_log.order_id)
    order_log_index.update_db()

    @testpoint('retrieve_current_state')
    def _retrieve_current_state(_):
        pass

    request = helpers.get_upsert_request(
        order_log.order_id, order_log.cart_id, order_log.depot_id,
    )
    request['order_log_info'].update(**order_log_extra)

    response = await taxi_grocery_order_log.post(
        '/processing/v1/insert', json=request,
    )
    assert response.status_code == 200
    assert _retrieve_current_state.times_called == int(expect_retrieve)


async def test_filter_sensitive(taxi_grocery_order_log, pgsql):
    order_log = models.OrderLog(pgsql, anonym_id='anonym_id')
    order_log.update_db()

    order_log_index = models.OrderLogIndex(pgsql, order_id=order_log.order_id)
    order_log_index.update_db()

    expected_order_log = models.OrderLog(pgsql)
    _copy_order_log_info(
        order_log=expected_order_log, previous_order_log=order_log,
    )

    expected_order_log_index = models.OrderLogIndex(pgsql)
    _copy_order_log_index(
        order_log_index=expected_order_log_index,
        previous_order_log_index=order_log_index,
    )

    request = {
        'order_id': order_log.order_id,
        'order_log_info': {
            'yandex_uid': str(uuid.uuid4()),
            'eats_user_id': str(uuid.uuid4()),
            'personal_phone_id': str(uuid.uuid4()),
            'personal_email_id': str(uuid.uuid4()),
            'appmetrica_device_id': str(uuid.uuid4()),
        },
    }
    response = await taxi_grocery_order_log.post(
        '/processing/v1/insert', json=request,
    )
    assert response.status_code == 200

    order_log.update()
    _check_order_log_info(order_log, expected_order_log)

    order_log_index.update()
    _check_order_log_index(order_log_index, expected_order_log_index)
