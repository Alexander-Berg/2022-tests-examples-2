# just accessibility test, see testsuite/protocol/test_changes.py
# for more tests (api/3.0/changes has the same handler)
def test_happy_path(taxi_integration, mockserver):
    response = taxi_integration.post(
        'v1/changes',
        {
            'id': 'USER_ID',
            'orders': [
                {
                    'orderid': 'ORDER_1',
                    'changes': [
                        {'change_id': 'CHANGE_1_1'},
                        {'change_id': 'CHANGE_1_2'},
                        {'change_id': 'CHANGE_1_3'},
                    ],
                },
            ],
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['orders']
    o0 = data['orders'][0]
    assert o0
    assert o0['orderid'] == 'ORDER_1'
    assert o0['changes']
    o0c0 = o0['changes'][0]
    assert o0c0
    assert o0c0['change_id'] == 'CHANGE_1_1'
    assert o0c0['value'] == {'k1': 'v1', 'k2': 'v2'}
    assert o0c0['status'] == 'failed'
    assert o0c0['name'] == 'NAME_1'
    o0c1 = o0['changes'][1]
    assert o0c1
    assert o0c1['change_id'] == 'CHANGE_1_2'
    assert o0c1['value'] is True
    assert o0c1['status'] == 'success'
    assert o0c1['name'] == 'NAME_2'
    o0c2 = o0['changes'][2]
    assert o0c2
    assert o0c2['change_id'] == 'CHANGE_1_3'
    assert o0c2['value'] == 123
    assert o0c2['status'] == 'pending'
    assert o0c2['name'] == 'payment'
