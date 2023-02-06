import typing

import pytest

OLD_COST_CENTER = {'corp_cost_center': 'going home corp'}
NEW_COST_CENTERS = {
    'cost_centers': [
        {
            'id': 'cost_center',
            'title': 'Центр затрат',
            'value': 'командировка',
        },
        {
            'id': 'ride_purpose',
            'title': 'Цель поездки',
            'value': 'из аэропорта',
        },
    ],
}
NEW_COST_CENTERS_EMPTY: typing.Dict[str, typing.List] = {'cost_centers': []}

COMBO_ORDER = {'combo_order': {'delivery_id': 'delivery1'}}


@pytest.mark.parametrize(
    'handler_url',
    [
        pytest.param('3.0/orderdraft', id='orderdraft'),
        pytest.param('/internal/orderdraft', id='internal-orderdraft'),
    ],
)
@pytest.mark.parametrize(
    'request_update',
    [
        pytest.param({}, id='no-cost-centers'),
        pytest.param(OLD_COST_CENTER, id='old-cost-center'),
        pytest.param(NEW_COST_CENTERS, id='new-cost-centers'),
        pytest.param(NEW_COST_CENTERS_EMPTY, id='new-cost-centers-empty'),
        pytest.param(
            dict(NEW_COST_CENTERS, **OLD_COST_CENTER),
            id='both-old-and-new-cost-centers',
        ),
    ],
)
def test_cost_centers(
        taxi_protocol, db, load_json, handler_url, request_update,
):
    request = load_json('base_request.json')
    request.update(request_update)
    response = taxi_protocol.post(handler_url, request)
    response_content = response.json()

    assert response.status_code == 200
    assert 'orderid' in response_content
    proc = db.order_proc.find_one({'_id': response_content['orderid']})
    assert proc is not None
    order = proc.get('order')
    assert order is not None
    assert 'corp' in order['request']
    corp = order['request']['corp']

    if 'corp_cost_center' in request_update:
        assert corp['cost_center'] == request_update['corp_cost_center']
    else:
        assert corp['cost_center'] == ''

    if 'cost_centers' in request_update:
        assert corp['cost_centers'] == request_update['cost_centers']
    else:
        assert 'cost_centers' not in corp


def test_combo_order(taxi_protocol, db, load_json):
    request = load_json('base_request.json')
    request.update(COMBO_ORDER)

    handler_url = '/internal/orderdraft'
    response = taxi_protocol.post(handler_url, request)
    response_content = response.json()

    assert response.status_code == 200
    assert 'orderid' in response_content
    proc = db.order_proc.find_one({'_id': response_content['orderid']})
    assert proc is not None
    order = proc.get('order')
    assert order is not None
    assert 'corp' in order['request']
    corp = order['request']['corp']

    assert corp['combo_order'] == COMBO_ORDER['combo_order']
