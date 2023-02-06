# coding=utf-8

import uuid

from order_core_exp_parametrize import CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP


@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_basic(
        taxi_integration,
        db,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        pricing_data_preparer,
        load_json,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def zones(request):
        return {}

    order_id = uuid.uuid4().hex
    user_id = '297d52da8caf4b5f86abf4cbd58e5a88'
    request = _make_request(order_id, user_id)
    response = taxi_integration.post('v1/orders/draft', json=request)
    assert response.status_code == 200
    response = response.json()
    assert response['orderid'] == order_id, response

    proc = db.order_proc.find_one({'_id': order_id})
    assert proc is not None
    order = proc['order']
    assert 'source' not in order
    assert order['nz'] == 'boryasvo'
    assert order['city'] == 'Москва'

    commit_request = {
        'orderid': order_id,
        'userid': user_id,
        'sourceid': 'svo_legacy',
    }
    response = taxi_integration.post('v1/orders/commit', json=commit_request)
    assert response.status_code == 200
    assert mock_order_core.create_draft_times_called == 0


@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_draft_idempotency(
        taxi_integration,
        db,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        pricing_data_preparer,
        load_json,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def zones(request):
        return {}

    order_id = uuid.uuid4().hex
    user_id = '297d52da8caf4b5f86abf4cbd58e5a88'
    request = _make_request(order_id, user_id)
    orders_before = list(db.order_proc.find({}))

    assert list(db.orders.find({})) == []
    for _ in range(5):
        response = taxi_integration.post('v1/orders/draft', json=request)
        assert response.status_code == 200
        response = response.json()
        assert response['orderid'] == order_id, response

    orders_after = list(db.order_proc.find({}))
    assert len(orders_after) == len(orders_before) + 1
    assert mock_order_core.create_draft_times_called == 0


def _make_request(order_id, user_id):
    source_obj = {
        'accepts_exact5': True,
        'city': 'Москва',
        'country': 'Россия',
        'description': (
            'Россия, Московская область, городской округ Химки, '
            'аэропорт Шереметьево'
        ),
        'exact': True,
        'fullname': (
            'Россия, Московская область, городской округ Химки, '
            'аэропорт Шереметьево, Международный аэропорт Шереметьево'
        ),
        'house': '',
        'object_type': 'аэропорт',
        'oid': '1101237450',
        'geopoint': [37.407217, 55.962141],
        'short_text': 'Международный аэропорт Шереметьево',
        'short_text_from': 'Международный аэропорт Шереметьево',
        'short_text_to': 'Международный аэропорт Шереметьево',
        'street': 'Международный аэропорт Шереметьево',
        'type': 'organization',
    }
    return {
        'id': user_id,
        'class': ['econom', 'business', 'comformplus', 'vip'],
        'payment': {'type': 'cash'},
        'parks': [],
        'route': [source_obj],
        'zone_name': 'boryasvo',
        'legacy_svo': {'car_number': 'XXX1234YY', 'order_id': order_id},
    }
