import pytest


ORDER_ID = '8c83b49edb274ce0992f337061047375'
USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'

OLD_COST_CENTER = 'going home corp'
NEW_COST_CENTERS = [
    {'id': 'cost_center', 'title': 'Центр затрат', 'value': 'командировка'},
    {'id': 'ride_purpose', 'title': 'Цель поездки', 'value': 'из аэропорта'},
]


@pytest.mark.parametrize(
    'proc_updates',
    [
        pytest.param({}, id='no-cost-centers'),
        pytest.param({'old': OLD_COST_CENTER}, id='old-cost-center'),
        pytest.param({'new': NEW_COST_CENTERS}, id='new-cost-centers'),
        pytest.param(
            {'old': OLD_COST_CENTER, 'new': NEW_COST_CENTERS},
            id='both-old-and-new-cost-centers',
        ),
    ],
)
def test_cost_centers(taxi_protocol, db, proc_updates):
    _set = {}
    if 'old' in proc_updates:
        _set['order.request.corp.cost_center'] = proc_updates['old']
    if 'new' in proc_updates:
        _set['order.request.corp.cost_centers'] = proc_updates['new']
    if _set:
        db.order_proc.update({'_id': ORDER_ID}, {'$set': _set})

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {'format_currency': True, 'id': USER_ID, 'orderid': ORDER_ID},
    )
    response_content = response.json()
    assert response.status_code == 200
    order_request = response_content['request']

    if 'old' in proc_updates:
        assert order_request['corp_cost_center'] == proc_updates['old']
    assert 'cost_centers' in response_content['request']
    assert response_content['request']['cost_centers'] == {
        'can_change': True,  # TODO (add config-dependent cases here)
        'values': proc_updates.get('new', []),
    }
