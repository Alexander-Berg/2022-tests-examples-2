import json

import bson
import pytest


@pytest.mark.parametrize(
    'card_id,payment_type,user_id,order_id,exp_status',
    [
        (
            'card-x5619',
            'card',
            '2ac1273e169d487fb4329c8a21064c42',
            'async_payorder_target',
            200,
        ),
        (
            'card-x5619',
            'card',
            '2ac1273e169d487fb4329c8a21064c42',
            'archived_order_id',
            200,
        ),
        (
            'card-x5619',
            'card',
            '2ac1273e169d487fb4329c8a21064c42',
            'async_payorder_target_reentry',
            200,
        ),
        (
            'card-x5619',
            'yandex_card',
            '2ac1273e169d487fb4329c8a21064c42',
            'async_payorder_target',
            200,
        ),
        (
            'card-x5619',
            'yandex_card',
            '2ac1273e169d487fb4329c8a21064c42',
            'archived_order_id',
            200,
        ),
        (
            'card-x5619',
            'yandex_card',
            '2ac1273e169d487fb4329c8a21064c42',
            'async_payorder_target_reentry',
            200,
        ),
    ],
)
@pytest.mark.config(PAYORDER_POLLING_TIMEOUT=0)
@pytest.mark.parametrize('use_order_core', [False, True])
def test_async_payorder(
        taxi_protocol,
        cardstorage,
        db,
        mockserver,
        mock_order_core,
        config,
        card_id,
        payment_type,
        user_id,
        order_id,
        exp_status,
        use_order_core,
):
    if use_order_core:
        config.set_values(dict(PROCESSING_BACKEND_CPP_SWITCH=['pay-order']))

    cardstorage.persistent_id = 'card1234'
    cardstorage.trust_response = 'billing-cards-response.json'

    @mockserver.json_handler('/archive-api/archive/order_proc/restore')
    def _mock_archive_order_proc_restore(request):
        request_data = json.loads(request.get_data())
        order_id = request_data['id']
        assert order_id == 'archived_order_id'
        response = json.dumps([{'id': order_id, 'status': 'restored'}])
        db.order_proc.insert(
            {
                '_id': 'archived_order_id',
                '_shard_id': 0,
                'order': {
                    'nz': 'moscow',
                    'user_phone_id': bson.ObjectId('58247911c0d947f1eef0b1bb'),
                    'user_uid': '4006998555',
                },
                'order_info': {'statistics': {'status_updates': []}},
            },
        )
        return mockserver.make_response(response, 200)

    response = taxi_protocol.post(
        '3.0/payorder',
        json={
            'id': user_id,
            'cardid': card_id,
            'orderid': order_id,
            'type': payment_type,
        },
    )
    assert response.status_code == exp_status

    if use_order_core and order_id != 'async_payorder_target_reentry':
        assert mock_order_core.post_event_times_called == 1
        return

    order_proc = db.order_proc.find_one(order_id)
    status_updates = order_proc['order_info']['statistics']['status_updates']
    assert len(status_updates) == 1

    status_update = status_updates[0]
    assert status_update['q'] == 'payorder'

    reason_arg = status_update['a']
    assert reason_arg['request_id']
    assert reason_arg['payment_method_id'] == 'card-x5619'
    if order_id == 'async_payorder_target_reentry':
        assert reason_arg['payment_type'] == 'card'
    else:
        assert reason_arg['payment_type'] == payment_type
    assert reason_arg['user_ip'] == ''
    assert reason_arg['user_id'] == '2ac1273e169d487fb4329c8a21064c42'
    assert reason_arg['user_phone_id'] == bson.ObjectId(
        '58247911c0d947f1eef0b1bb',
    )
    assert reason_arg['user_yandex_uid'] == '4006934797'
    assert reason_arg['user_initiated']


@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='do_not_change_cash_after_complete',
    consumers=['protocol/payorder'],
    clauses=[
        {
            'title': '1',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.config(PAYORDER_POLLING_TIMEOUT=0)
def test_payorder_complete_with_cash(
        taxi_protocol, cardstorage, db, mockserver,
):
    card_id = 'card-x5619'
    user_id = '2ac1273e169d487fb4329c8a21064c42'
    order_id = 'complete_with_cash'
    cardstorage.persistent_id = 'card1234'
    cardstorage.trust_response = 'billing-cards-response.json'

    response = taxi_protocol.post(
        '3.0/payorder',
        json={
            'id': user_id,
            'cardid': card_id,
            'orderid': order_id,
            'type': 'card',
        },
    )
    assert response.status_code == 200
    order_proc = db.order_proc.find_one(order_id)

    status_updates = order_proc['order_info']['statistics']['status_updates']
    assert len(status_updates) == 0


@pytest.mark.parametrize(
    'zone_name,payment_method_type,expected_status,error_text',
    [
        ('moscow', 'applepay', 200, None),
        ('moscow', 'googlepay', 200, None),
        ('moscow', 'yandex_card', 200, None),
        ('almaty', 'applepay', 406, 'apple_pay_not_available'),
        ('almaty', 'googlepay', 406, 'google_pay_not_available'),
        ('almaty', 'yandex_card', 406, 'yandex_card_not_available'),
    ],
)
@pytest.mark.config(
    PAYORDER_POLLING_TIMEOUT=0, PAYORDER_CHECK_PAYMENT_BY_ZONE=True,
)
def test_check_payments_by_zone(
        taxi_protocol,
        cardstorage,
        db,
        zone_name,
        payment_method_type,
        expected_status,
        error_text,
):
    cardstorage.persistent_id = 'card1234'
    cardstorage.trust_response = 'billing-cards-response.json'

    db.order_proc.update_one(
        {'_id': 'async_payorder_target'}, {'$set': {'order.nz': zone_name}},
    )

    response = taxi_protocol.post(
        '3.0/payorder',
        json={
            'id': '2ac1273e169d487fb4329c8a21064c42',
            'cardid': 'card-x5619',
            'orderid': 'async_payorder_target',
            'type': payment_method_type,
        },
    )
    assert response.status_code == expected_status


@pytest.mark.experiments3(filename='exp3_cash_change_blocking_enabled.json')
@pytest.mark.parametrize(
    'payment_type,antifraud_status,expected_status,call_count',
    (
        ('cash', 'block', 406, 1),
        ('cash', 'allow', 200, 1),
        ('cash', None, 200, 3),
        ('card', 'block', 200, 0),
    ),
)
@pytest.mark.user_experiments('async_payorder')
def test_block_by_antifraud(
        taxi_protocol,
        cardstorage,
        mock_uantifraud_payment_available,
        db,
        payment_type,
        antifraud_status,
        expected_status,
        call_count,
):
    order_id = 'async_payorder_target'
    cardstorage.persistent_id = 'card1234'
    cardstorage.trust_response = 'billing-cards-response.json'

    db.order_proc.update_one(
        {'_id': order_id}, {'$set': {'payment_tech.type': payment_type}},
    )

    antifraud_call_holder = mock_uantifraud_payment_available(antifraud_status)

    response = taxi_protocol.post(
        '3.0/payorder',
        json={
            'id': '2ac1273e169d487fb4329c8a21064c42',
            'cardid': 'card-x5619',
            'orderid': order_id,
            'type': 'card',
        },
    )

    antifraud_call_holder.check_calls(call_count, order_id)
    assert response.status_code == expected_status


def test_payorder_sbp(taxi_protocol, cardstorage, db):
    user_id = '2ac1273e169d487fb4329c8a21064c42'
    order_id = 'sbp_order'
    cardstorage.persistent_id = 'card1234'
    cardstorage.trust_response = 'billing-cards-response.json'

    response = taxi_protocol.post(
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
