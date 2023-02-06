import pytest

from tests_grocery_order_log import models


@pytest.fixture(name='internal_load')
def _internal_load(taxi_grocery_order_log):
    async def _inner(order_id: str, status_code=200):
        response = await taxi_grocery_order_log.post(
            '/internal/orders/v1/takeout/load', json={'order_id': order_id},
        )

        assert response.status_code == status_code
        return response.json()

    return _inner


async def test_basic(internal_load, pgsql):
    order_id = 'order_id'
    order_log = models.OrderLog(
        pgsql=pgsql,
        order_id=order_id,
        yandex_uid='yandex_uid',
        order_source='lavka',
        eats_user_id='eats_user_id',
        appmetrica_device_id='appmetrica_device_id',
        cart_items=[
            {
                'id': 'id',
                'item_name': 'item_name',
                'price': '100',
                'quantity': '2',
            },
        ],
    )
    order_log.update_db()

    order_log_index = models.OrderLogIndex(
        pgsql=pgsql,
        order_id=order_id,
        order_state=order_log.order_state,
        yandex_uid='yandex_uid',
        eats_user_id='eats_user_id',
        personal_phone_id='personal_phone_id',
        personal_email_id='personal_email_id',
    )
    order_log_index.update_db()

    expected_data = {
        'order_id': order_log.order_id,
        'short_order_id': order_log.short_order_id,
        'order_created_date': order_log.order_created_date.isoformat(),
        'order_finished_date': order_log.order_finished_date.isoformat(),
        'order_source': order_log.order_source,
        'destination': order_log.destination,
        'receipts': order_log.receipts,
        'cart_items': _format_cart_items(order_log),
    }
    expected_sensitive_data = {
        'yandex_uid': order_log.yandex_uid,
        'eater_id': order_log.eats_user_id,
        'appmetrica_device_id': order_log.appmetrica_device_id,
        'personal_phone_id': order_log_index.personal_phone_id,
        'personal_email_id': order_log_index.personal_email_id,
    }
    expected_object = {
        'id': order_id,
        'data': expected_data,
        'sensitive_data': expected_sensitive_data,
    }

    response = await internal_load(order_id=order_id)
    assert response['objects'] == [expected_object]


async def test_invalid_cart_decimals(internal_load, pgsql):
    order_id = 'order_id'
    order_log = models.OrderLog(
        pgsql=pgsql,
        order_id=order_id,
        cart_items=[
            {
                'id': 'id',
                'item_name': 'item_name',
                'price': '100.000000',
                'quantity': '2.000000',
            },
        ],
    )
    order_log.update_db()

    order_log_index = models.OrderLogIndex(pgsql=pgsql, order_id=order_id)
    order_log_index.update_db()

    response = await internal_load(order_id=order_id)
    cart_items = response['objects'][0]['data']['cart_items']
    assert cart_items == _format_cart_items(order_log)


def _format_cart_items(order_log):
    return [
        {
            'title': item['item_name'],
            'price': item['price'],
            'quantity': item['quantity'],
        }
        for item in order_log.cart_items
    ]
