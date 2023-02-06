# pylint: disable=redefined-outer-name,invalid-name
import datetime

import pytest

from test_transactions import helpers

_ENABLE_ARCHIVE = pytest.mark.config(
    TRANSACTIONS_ARCHIVE_ENABLED={'taxi': 1, '__default__': 0},
)


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[_ENABLE_ARCHIVE],
            id='it should return 404 when archive is enabled',
        ),
        pytest.param(id='it should return 404 when archive is disabled'),
    ],
)
@pytest.mark.now('2019-06-04T00:11:22')
async def test_invoice_clear_not_found(patch, web_app_client):
    helpers.patch_fetch_invoice(
        patch, result=None, expected_invoice_id='no-such-order',
    )
    response = await web_app_client.post(
        '/invoice/clear',
        json={'id': 'no-such-order', 'clear_eta': '2019-06-04T00:11:22'},
    )
    assert response.status == 404
    content = await response.json()
    assert content == {}


@pytest.mark.now('2019-06-04T00:11:22')
async def test_invoice_clear_automatic_clear_delay(web_app_client):
    response = await web_app_client.post(
        '/invoice/clear',
        json={
            'id': 'my-order-automatic-clear-delay',
            'clear_eta': '2019-06-04T00:11:22',
        },
    )
    assert response.status == 400
    content = await response.json()
    assert content['code'] == 'invoice_has_automatic_clear_delay'


@pytest.mark.now('2019-06-04T00:11:22')
async def test_invoice_clear_order(web_app_client, db, stq):
    response = await web_app_client.post(
        '/invoice/clear',
        json={'id': 'my-order', 'clear_eta': '2019-06-04T00:11:22'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}

    order = await db.orders.find_one('my-order')
    assert order['invoice_payment_tech']['clear_eta'] == (
        datetime.datetime(2019, 6, 4, 0, 11, 22)
    )
    assert stq.transactions_events.times_called == 1
    assert stq.transactions_events.next_call()['id'] == 'my-order'


@_ENABLE_ARCHIVE
@pytest.mark.now('2019-06-04T00:11:22')
async def test_invoice_clear_archive_order(patch, web_app_client, db, stq):
    fetch_result = {
        '_id': 'my-archive-order',
        'invoice_payment_tech': {},
        'updated': True,
    }
    fetch = helpers.patch_fetch_invoice(patch, fetch_result)
    order_before = await db.orders.find_one('my-archive-order')
    assert order_before is None
    response = await web_app_client.post(
        '/invoice/clear',
        json={'id': 'my-archive-order', 'clear_eta': '2019-06-04T00:11:22'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}

    order = await db.orders.find_one('my-archive-order')
    assert order['invoice_payment_tech']['clear_eta'] == (
        datetime.datetime(2019, 6, 4, 0, 11, 22)
    )
    assert stq.transactions_events.times_called == 1
    assert stq.transactions_events.next_call()['id'] == 'my-archive-order'
    assert len(fetch.calls) == 1
