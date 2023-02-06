import bson


def test_payorder_sbp(taxi_integration, cardstorage, db):
    user_id = '2ac1273e169d487fb4329c8a21064c42'
    order_id = 'sbp_order'
    cardstorage.persistent_id = 'card1234'
    cardstorage.trust_response = 'billing-cards-response.json'

    response = taxi_integration.post(
        '3.0/payorder',
        json={'id': user_id, 'orderid': order_id, 'type': 'sbp'},
    )
    assert response.status_code == 200
    order_proc = db.order_proc.find_one(order_id)

    status_updates = order_proc['order_info']['statistics']['status_updates']

    assert len(status_updates) == 1

    status_update = status_updates[0]
    assert status_update['q'] == 'payorder'

    reason_arg = status_update['a']
    assert reason_arg['request_id']
    assert reason_arg['payment_type'] == 'sbp'
    assert reason_arg['payment_method_id'] == 'sbp_qr'
    assert reason_arg['user_ip'] == ''
    assert reason_arg['user_id'] == '2ac1273e169d487fb4329c8a21064c42'
    assert reason_arg['user_phone_id'] == bson.ObjectId(
        '58247911c0d947f1eef0b1bb',
    )
    assert reason_arg['user_yandex_uid'] == '4006934797'
    assert reason_arg['user_initiated']
