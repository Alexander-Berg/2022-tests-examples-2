import pytest


def create_draft(taxi_protocol, request, **http_kwargs):
    draft_resp = taxi_protocol.post('3.0/orderdraft', request, **http_kwargs)
    assert draft_resp.status_code == 200
    return draft_resp.json()['orderid']


def commit_order(taxi_protocol, order_id, request, **http_kwargs):
    commit_request = {
        'id': request['id'],
        'orderid': order_id,
        'check_unfinished_commit': False,
    }
    return taxi_protocol.post('3.0/ordercommit', commit_request, **http_kwargs)


def check_current_prices(
        order_proc,
        kind,
        total_price,
        total_display_price=None,
        ride_display_price=None,
        cashback_price=None,
        charity_price=None,
        toll_road_price=None,
):
    exp_total_price = total_price if total_price else 0.0
    exp_total_display_price = exp_total_price
    exp_ride_display_price = exp_total_price

    if total_display_price is not None:
        exp_total_display_price = total_display_price

    if ride_display_price is not None:
        exp_ride_display_price = ride_display_price

    current_prices = order_proc.get('order').get('current_prices')

    assert current_prices['user_total_price'] == exp_total_price
    assert (
        current_prices['user_total_display_price'] == exp_total_display_price
    )
    assert current_prices['user_ride_display_price'] == exp_ride_display_price
    assert current_prices['kind'] == kind

    if cashback_price:
        assert current_prices['cashback_price'] == cashback_price
    else:
        assert 'cashback_price' not in current_prices

    if toll_road_price:
        assert current_prices['toll_road_price'] == toll_road_price
    else:
        assert 'toll_road' not in current_prices

    if charity_price:
        assert current_prices['charity_price'] == charity_price
    else:
        assert 'charity_price' not in current_prices


@pytest.mark.parametrize(
    'method_id, is_ok', [('corp-asdasd', False), ('card-x1234123', True)],
)
@pytest.mark.config(PAYMENT_METHODS_REGEXPS={'yandex_card': '^card-.+$'})
def test_invalid_payment_method_id(taxi_protocol, db, method_id, is_ok):
    ORDER_ID = 'order_id'

    db.order_proc.update(
        {'_id': ORDER_ID},
        {'$set': {'order.request.payment.payment_method_id': method_id}},
    )
    db.order_offers.update(
        {'_id': 'offer_id'},
        {'$set': {'request.payment.payment_method_id': method_id}},
    )

    request = {'id': 'user_id', 'orderid': ORDER_ID}
    response = taxi_protocol.post('3.0/ordercommit', request)
    if not is_ok:
        assert response.status_code == 406
        json = response.json()
        assert json['error'] == {'code': 'BAD_PAYMENT_METHOD'}
    else:
        assert response.status_code == 200
