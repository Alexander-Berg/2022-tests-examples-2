import pytest


ORDERCOMMIT_URL = '3.0/ordercommit'


def assert_cashback_order(order_id, db, discount, plus):
    proc = db.order_proc.find_one(order_id)
    extra_data = proc.get('extra_data', {})
    assert extra_data.get('cashback')
    cashback = extra_data.get('cashback')
    assert cashback.get('is_cashback') is True
    assert cashback.get('is_discount_cashback') is discount
    assert cashback.get('is_plus_cashback') is plus


def assert_not_cashback_order(order_id, db):
    proc = db.order_proc.find_one(order_id)
    cashback = proc.get('extra_data', {}).get('cashback')
    assert not cashback


@pytest.mark.now('2019-06-26T21:19:09+0300')
def test_buffer_combo(taxi_protocol, db):
    request = {'id': 'user_id', 'orderid': 'orderid'}

    # enable buffer combo
    db.order_offers.update(
        {'_id': 'offer_id'},
        {
            '$set': {
                'buffer_combo': {
                    'approx_eta_min': 7,
                    'search_subtitle': 'search in 5 - 10',
                },
            },
        },
    )

    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    assert response.status_code == 200

    proc = db.order_proc.find_one('orderid')
    assert proc
    assert 'buffer_combo' in proc['order']
    assert proc['order']['buffer_combo'] == {
        'enabled': True,
        'multiorder_info': {'subtitle': 'search in 5 - 10'},
    }
