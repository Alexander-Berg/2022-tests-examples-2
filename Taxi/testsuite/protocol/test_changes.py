import copy

import pytest

query_set = {
    'method=oauth',
    'userip=',
    'format=json',
    'dbfields=subscription.suid.669',
    'aliases=1%2C10%2C16',
    'oauth_token=test_token',
    'getphones=bound',
    'get_login_id=yes',
    'phone_attributes=102%2C107%2C4',
}

auth_info = {
    'uid': {'value': 'UID'},
    'status': {'value': 'VALID'},
    'oauth': {'scope': 'yataxi:read yataxi:write yataxi:pay'},
    'phones': [
        {
            'attributes': {'102': '+71112223344'},
            'id': 'deadbeefdeadbeefdeadbeef',
        },
    ],
}


def test_success(taxi_protocol, mockserver):
    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        assert set(request.query_string.decode().split('&')) == query_set
        return auth_info

    response = taxi_protocol.post(
        '3.0/changes',
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
        bearer='test_token',
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


@pytest.mark.filldb(users='crossdevice')
def test_crossdevice_success(taxi_protocol, mockserver):
    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        return auth_info

    request_base = {
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
    }
    o_req = copy.deepcopy(request_base)
    o_req['id'] = 'USER_ID'
    o_resp = taxi_protocol.post('3.0/changes', o_req)

    cd_req = copy.deepcopy(request_base)
    cd_req['id'] = 'CROSSDEVICE_USER_ID'
    cd_resp = taxi_protocol.post('3.0/changes', cd_req)

    assert o_resp.status_code == 200
    assert o_resp.status_code == cd_resp.status_code
    assert o_resp.json() == cd_resp.json()


def test_reorder(taxi_protocol, mockserver):
    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        assert set(request.query_string.decode().split('&')) == query_set
        return auth_info

    response = taxi_protocol.post(
        '3.0/changes',
        {
            'id': 'USER_ID',
            'orders': [
                {
                    'orderid': 'REORDER',
                    'changes': [{'change_id': 'CHANGE_2_1'}],
                },
            ],
        },
        bearer='test_token',
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['orders']
    o0 = data['orders'][0]
    assert o0
    assert o0['orderid'] == 'REORDER'
    assert o0['changes']
    o0c0 = o0['changes'][0]
    assert o0c0
    assert o0c0['change_id'] == 'CHANGE_2_1'
    assert o0c0['value'] == 'TEXT'
    assert o0c0['status'] == 'failed'
    assert o0c0['name'] == 'NAME_1'


def test_no_order(taxi_protocol, mockserver):
    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        assert set(request.query_string.decode().split('&')) == query_set
        return auth_info

    response = taxi_protocol.post(
        '3.0/changes',
        {
            'id': 'USER_ID',
            'orders': [
                {
                    'orderid': 'UNEXIST',
                    'changes': [
                        {'change_id': 'CHANGE_1_1'},
                        {'change_id': 'CHANGE_1_2'},
                        {'change_id': 'CHANGE_1_3'},
                    ],
                },
            ],
        },
        bearer='test_token',
    )
    assert response.status_code == 404


def test_no_id(taxi_protocol, mockserver):
    response = taxi_protocol.post(
        '3.0/changes',
        {
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
        bearer='test_token',
    )
    assert response.status_code == 400


def test_bad_id(taxi_protocol, mockserver):
    response = taxi_protocol.post(
        '3.0/changes',
        {
            'id': 123,
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
        bearer='test_token',
    )
    assert response.status_code == 400


def test_no_orders(taxi_protocol, mockserver):
    response = taxi_protocol.post(
        '3.0/changes', {'id': 'USER_ID'}, bearer='test_token',
    )
    assert response.status_code == 400


def test_bad_orders(taxi_protocol, mockserver):
    response = taxi_protocol.post(
        '3.0/changes', {'id': 'USER_ID', 'orders': 123}, bearer='test_token',
    )
    assert response.status_code == 400


def test_no_changes(taxi_protocol, mockserver):
    response = taxi_protocol.post(
        '3.0/changes',
        {'id': 'USER_ID', 'orders': [{'orderid': 'ORDER_1'}]},
        bearer='test_token',
    )
    assert response.status_code == 400


def test_bad_changes(taxi_protocol, mockserver):
    response = taxi_protocol.post(
        '3.0/changes',
        {'id': 'USER_ID', 'orders': [{'orderid': 'ORDER_1', 'changes': 123}]},
        bearer='test_token',
    )
    assert response.status_code == 400


def test_no_change_id(taxi_protocol, mockserver):
    response = taxi_protocol.post(
        '3.0/changes',
        {
            'id': 'USER_ID',
            'orders': [
                {
                    'orderid': 'ORDER_1',
                    'changes': [
                        {},
                        {'change_id': 'CHANGE_1_2'},
                        {'change_id': 'CHANGE_1_3'},
                    ],
                },
            ],
        },
        bearer='test_token',
    )
    assert response.status_code == 400


def test_bad_change_id(taxi_protocol, mockserver):
    response = taxi_protocol.post(
        '3.0/changes',
        {
            'id': 'USER_ID',
            'orders': [
                {
                    'orderid': 'ORDER_1',
                    'changes': [
                        {'change_id': 'CHANGE_1_1'},
                        {'change_id': 22},
                        {'change_id': 'CHANGE_1_3'},
                    ],
                },
            ],
        },
        bearer='test_token',
    )
    assert response.status_code == 400
