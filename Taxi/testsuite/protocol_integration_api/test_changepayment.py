import dateutil.parser
import pytest

from notify_on_change_version_switch import NOTIFY_ON_CHANGE_VERSION_SWITCH


PARTNER_ORDERS_API_TVM_TICKET = (
    '3:serv:CBAQ__________9_IgQIexAX:Pz6rEHFgRT2AO2zGiBtmM63-k1uQW7aszfGy6l7d'
    'VPk8DhhM6WBIAlGRdZUIVP8rG5STuXkS6fFq_x7pYzgYEHRa9i2ak-8Q0R1cQerNtgpjTfZe6'
    'q7hoRIUpk6RUZhQkGLFSHZARzsSDgvnIDnk_K6sBMAdOHTWGdV6evyOqEs'
)

OTHER_SERVICE_TVM_TICKET = (
    '3:serv:CBAQ__________9_IgUIlAEQFw:PH8b7-4r_Ush8d5ie-x2tklJtQtjSS5CFrWol4x'
    'd_xU0pmnCq28mQP8QxCOxQ8piw8cGco5hBma3kP73Z0Hg0yyzblhvpkfnpMKOMZYr7CRNao3F'
    'Ul_juY8IqfYtQUCkPHrw0Ebyw6UO9rvzyqFAnNe88AfQqDT-lGjqOVwPNLg'
)


@pytest.mark.parametrize(
    'orderid, card_id, changes_expected',
    [
        ('8c83b49edb274ce0992f337061047376', 'card-2311', 3),
        ('d41d8cd98f004204a9800998ecf8427e', 'card-0921', 2),
    ],
)
@pytest.mark.now('2017-07-19T17:15:15+0000')
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_simple(
        taxi_integration,
        mockserver,
        db,
        now,
        orderid,
        card_id,
        changes_expected,
        notify_on_change_version_switch,
):
    created_time = dateutil.parser.parse('2017-07-19T17:15:15+0000')
    request = {
        'userid': 'user_alice',
        'orderid': orderid,
        'payment_method_id': card_id,
        'payment_method_type': 'card',
        'sourceid': 'alice',
    }
    query = {'_id': request['orderid']}
    proc = db.order_proc.find_one(query)
    version = proc['order']['version']
    assert proc is not None
    assert now > proc['updated']
    response = taxi_integration.post('v1/changepayment', request)
    assert response.status_code == 200
    data = response.json()
    assert data == {
        'change_id': data['change_id'],
        'status': 'pending',
        'name': 'payment',
        'value': card_id,
    }
    order_proc = db.order_proc.find_one(query)
    assert order_proc['order']['version'] == version + 1
    changes = order_proc['changes']['objects']
    assert len(changes) == changes_expected
    change = changes[changes_expected - 1]
    assert change == {
        'id': change['id'],
        'vl': {
            'payment_method_id': card_id,
            'payment_method_type': 'card',
            'ip': change['vl']['ip'],
            'yandex_uid': change['vl']['yandex_uid'],
        },
        's': 'pending',
        'ci': request['userid'],
        'n': 'payment',
        'vr': version + 1,
        'c': now.replace(tzinfo=None, microsecond=0),
        't': created_time.replace(tzinfo=None, microsecond=0),
    }


@pytest.mark.now('2018-01-01T11:30:00+0300')
@pytest.mark.parametrize(
    'body,expected_code,expected_response',
    [
        (
            {
                'userid': 'user_alice',
                'orderid': '8c83b49edb274ce0992f337061047376',
                'payment_method_id': 'card-2311',
                'payment_method_type': 'card',
                'sourceid': 'alice',
            },
            200,
            {'name': 'payment', 'status': 'pending', 'value': 'card-2311'},
        ),
        (
            {  # no 'payment_method_id', but 'payment_method_type': 'card',
                'userid': 'user_alice',
                'orderid': '8c83b49edb274ce0992f337061047376',
                'payment_method_type': 'card',
                'sourceid': 'alice',
            },
            400,
            {'error': {'text': 'Bad Request'}},
        ),
        (
            {  # no sourceid
                'userid': 'user_alice',
                'orderid': '8c83b49edb274ce0992f337061047376',
                'payment_method_id': 'card-2311',
                'payment_method_type': 'card',
            },
            200,
            {'name': 'payment', 'status': 'pending', 'value': 'card-2311'},
        ),
        (
            {  # no payment_method_type
                'userid': 'user_alice',
                'orderid': '8c83b49edb274ce0992f337061047376',
                'payment_method_id': 'card-2311',
                'sourceid': 'alice',
            },
            200,
            {'name': 'payment', 'status': 'pending', 'value': 'card-2311'},
        ),
        (
            {  # no orderid
                'userid': 'user_alice',
                'payment_method_id': 'card-2311',
                'payment_method_type': 'card',
                'sourceid': 'alice',
            },
            400,
            {'error': {'text': 'Bad Request'}},
        ),
        (
            {  # no user_id
                'orderid': '8c83b49edb274ce0992f337061047376',
                'payment_method_id': 'card-2311',
                'payment_method_type': 'card',
                'sourceid': 'alice',
            },
            400,
            {'error': {'text': 'Bad Request'}},
        ),
    ],
)
@pytest.mark.config(INTEGRATION_ORDER_TIME_TO_CANCEL=600)
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_api(
        taxi_integration,
        taxi_config,
        body,
        expected_code,
        expected_response,
        notify_on_change_version_switch,
):
    headers = {}
    if body.get('sourceid') is None:
        taxi_config.set_values(
            {'INTEGRATION_API_USE_APP_INSTEAD_OF_SOURCE_ID': ['turboapp']},
        )
        headers['User-Agent'] = 'app1-turboapp'
    response = taxi_integration.post('v1/changepayment', body, headers=headers)
    assert response.status_code == expected_code
    data = response.json()
    if response.status_code == 200:
        data.pop('change_id')
    assert data == expected_response


@pytest.mark.parametrize(
    'orderid, code, error_text, method_type, method_id',
    [
        ('8c83b49edb274ce0992f337061047377', 200, None, 'card', 'card-2311'),
        ('d41d8cd98f004204a9800998ecf84eee', 200, None, 'card', 'card-2311'),
        (
            'd41d8cd98f004204a9800998ecf84eee',
            406,
            'cant_change_from_anything_to_personal_wallet',
            'personal_wallet',
            'passwall-RUS',
        ),
        (
            '8c83b49edb274ce0992f337061047378',
            406,
            'unknown_park_id',
            'card',
            'card-2311',
        ),
        (
            '8c83b49edb274ce0992f337061047379',
            406,
            'park_doesnt_accept_cards',
            'card',
            'card-2311',
        ),
        (
            '8c83b49edb274ce0992f337061047380',
            406,
            'park_doesnt_accept_cards',
            'card',
            'card-2311',
        ),
        (
            '8c83b49edb274ce0992f337061047381',
            406,
            'payment_change_is_in_progress',
            'card',
            'card-2311',
        ),
        (
            '8c83b49edb274ce0992f337061047482',
            406,
            'cant_change_from_personal_wallet_to_anything',
            'card',
            'card-2311',
        ),
        (
            '8c83b49edb274ce0992f337061047383',
            500,
            'unknown_city_id',
            'card',
            'card-2311',
        ),
        (
            '8c83b49edb274ce0992f337061047384',
            406,
            'city_doesnt_accept_cards',
            'card',
            'card-2311',
        ),
        (
            '8c83b49edb274ce0992f337061047385',
            406,
            'cant_change_payment_experiment',
            'card',
            'card-2311',
        ),
        (
            '8c83b49edb274ce0992f337061047386',
            404,
            'order is finished',
            'card',
            'card-2311',
        ),
    ],
)
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_return_code(
        orderid,
        code,
        error_text,
        method_type,
        method_id,
        taxi_integration,
        notify_on_change_version_switch,
):
    request = {
        'orderid': orderid,
        'userid': 'user_alice',
        'payment_method_id': method_id,
        'payment_method_type': method_type,
        'sourceid': 'alice',
    }
    response = taxi_integration.post('v1/changepayment', json=request)
    assert response.status_code == code
    if code != 500:
        data = response.json()
        if error_text:
            assert data['error']['text'] == error_text


@pytest.mark.now('2017-07-19T17:15:15+0000')
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_empty_change_payment(
        taxi_integration, mockserver, db, now, notify_on_change_version_switch,
):
    created_time = dateutil.parser.parse('2017-07-19T17:15:15+0000')
    request = {
        'userid': 'user_alice',
        'orderid': '8c83b49edb274ce0992f337061047375',
        'payment_method_id': 'card-2311',
        'payment_method_type': 'card',
        'sourceid': 'alice',
    }
    query = {'_id': request['orderid']}
    proc = db.order_proc.find_one(query)
    assert proc is not None
    version = proc['order']['version']
    assert 'changes' not in proc
    assert now > proc['updated']
    response = taxi_integration.post('v1/changepayment', request)
    assert response.status_code == 200
    data = response.json()
    assert data == {
        'change_id': data['change_id'],
        'status': 'pending',
        'name': 'payment',
        'value': 'card-2311',
    }
    order_proc = db.order_proc.find_one(query)
    assert order_proc['order_info']['need_sync'] is False
    assert order_proc['order']['version'] == version + 1
    changes = order_proc['changes']['objects']
    assert len(changes) == 2
    assert changes == [
        {
            'id': changes[0]['id'],
            'vl': 'cash',
            's': 'applied',
            'ci': request['userid'],
            'n': 'payment',
            'vr': version + 1,
            'c': now.replace(tzinfo=None, microsecond=0),
            't': created_time.replace(tzinfo=None, microsecond=0),
            'si': {'s': 'delivered', 'c': 0},
        },
        {
            'id': changes[1]['id'],
            'vl': {
                'payment_method_id': 'card-2311',
                'payment_method_type': 'card',
                'ip': changes[1]['vl']['ip'],
                'yandex_uid': changes[1]['vl']['yandex_uid'],
            },
            's': 'pending',
            'ci': request['userid'],
            'n': 'payment',
            'vr': version + 1,
            'c': now.replace(tzinfo=None, microsecond=0),
            't': created_time.replace(tzinfo=None, microsecond=0),
        },
    ]


@pytest.mark.config(ALLOW_CHANGE_TO_CASH_IF_UNSUCCESSFUL_PAYMENT=True)
@pytest.mark.now('2017-07-19T17:15:15+0000')
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_change_payment_to_cash(
        taxi_integration, db, now, notify_on_change_version_switch,
):
    orderid = 'd41d8cd98f004204a9800998ecf8427e'
    request = {
        'userid': 'user_alice',
        'orderid': orderid,
        'payment_method_type': 'cash',
        'sourceid': 'alice',
    }

    response = taxi_integration.post('v1/changepayment', request)
    assert response.status_code == 406

    query = {'_id': request['orderid']}
    db.orders.update(
        query, {'$set': {'payment_tech.unsuccessful_payment': True}},
    )
    response = taxi_integration.post('v1/changepayment', request)
    assert response.status_code == 200


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
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_block_by_antifraud(
        db,
        mock_uantifraud_payment_available,
        taxi_integration,
        payment_type,
        antifraud_status,
        expected_status,
        call_count,
        notify_on_change_version_switch,
):
    order_id = '8c83b49edb274ce0992f337061047377'
    db.orders.update_one(
        {'_id': order_id}, {'$set': {'payment_tech.type': payment_type}},
    )

    antifraud_call_holder = mock_uantifraud_payment_available(antifraud_status)

    body = {
        'orderid': order_id,
        'userid': 'user_alice',
        'payment_method_id': 'some_id',
        'payment_method_type': 'card',
        'sourceid': 'alice',
    }
    response = taxi_integration.post('v1/changepayment', body)
    assert response.status_code == expected_status
    antifraud_call_holder.check_calls(call_count, order_id)
    if expected_status != 200:
        data = response.json()
        assert (
            data['error']['text'] == 'Block change payment method by antifraud'
        )


@pytest.mark.config(
    INTEGRATION_API_USE_APP_INSTEAD_OF_SOURCE_ID=['agent_007'],
    INTEGRATION_SUPPORTED_APPLICATIONS=['agent_007'],
    APPLICATION_DETECTION_RULES_NEW={'rules': [{'@app_name': 'agent_007'}]},
    INTEGRATION_API_AGENT_ORDERS_CHECK_SRC=True,
    TVM_ENABLED=True,
    TVM_RULES=[
        {'src': 'partner-orders-api', 'dst': 'integration-api'},
        {'src': 'other-service', 'dst': 'integration-api'},
    ],
    TVM_SERVICES={
        'integration-api': 23,
        'partner-orders-api': 123,
        'other-service': 148,
    },
)
@pytest.mark.now('2017-07-19T17:15:15+0000')
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_change_to_agent_disallowed(
        taxi_integration, db, now, notify_on_change_version_switch,
):
    orderid = 'd41d8cd98f004204a9800998ecf8427e'
    request = {
        'userid': 'user_alice',
        'orderid': orderid,
        'payment_method_type': 'agent',
        'payment_method_id': 'agent_007',
    }

    response = taxi_integration.post(
        'v1/changepayment',
        request,
        headers={
            'X-Ya-Service-Ticket': OTHER_SERVICE_TVM_TICKET,
            'User-Agent': 'some_user_agent',
        },
    )
    assert response.status_code == 406


@pytest.mark.config(
    INTEGRATION_API_USE_APP_INSTEAD_OF_SOURCE_ID=['agent_007'],
    INTEGRATION_SUPPORTED_APPLICATIONS=['agent_007'],
    APPLICATION_DETECTION_RULES_NEW={'rules': [{'@app_name': 'agent_007'}]},
    INTEGRATION_API_AGENT_ORDERS_CHECK_SRC=True,
    TVM_ENABLED=True,
    TVM_RULES=[
        {'src': 'partner-orders-api', 'dst': 'integration-api'},
        {'src': 'other-service', 'dst': 'integration-api'},
    ],
    TVM_SERVICES={
        'integration-api': 23,
        'partner-orders-api': 123,
        'other-service': 148,
    },
)
@pytest.mark.now('2017-07-19T17:15:15+0000')
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_change_from_cash_to_agent(
        taxi_integration, db, now, notify_on_change_version_switch,
):
    orderid = 'agent_cash_order'
    request = {
        'userid': 'agent_user',
        'orderid': orderid,
        'payment_method_type': 'agent',
        'payment_method_id': 'agent_007',
    }

    response = taxi_integration.post(
        'v1/changepayment',
        request,
        headers={
            'X-Ya-Service-Ticket': PARTNER_ORDERS_API_TVM_TICKET,
            'User-Agent': 'agent_007',
        },
    )
    assert response.status_code == 200


@pytest.mark.config(
    INTEGRATION_API_USE_APP_INSTEAD_OF_SOURCE_ID=['agent_007'],
    INTEGRATION_SUPPORTED_APPLICATIONS=['agent_007'],
    APPLICATION_DETECTION_RULES_NEW={'rules': [{'@app_name': 'agent_007'}]},
    INTEGRATION_API_AGENT_ORDERS_CHECK_SRC=True,
    TVM_ENABLED=True,
    TVM_RULES=[
        {'src': 'partner-orders-api', 'dst': 'integration-api'},
        {'src': 'other-service', 'dst': 'integration-api'},
    ],
    TVM_SERVICES={
        'integration-api': 23,
        'partner-orders-api': 123,
        'other-service': 148,
    },
)
@pytest.mark.now('2017-07-19T17:15:15+0000')
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_change_from_agent_to_cash_not_acceptable(
        taxi_integration, db, now, notify_on_change_version_switch,
):
    orderid = 'agent_cash_order'
    request = {
        'userid': 'agent_user',
        'orderid': orderid,
        'payment_method_type': 'agent',
        'payment_method_id': 'agent_007',
    }
    headers = {
        'X-Ya-Service-Ticket': PARTNER_ORDERS_API_TVM_TICKET,
        'User-Agent': 'agent_007',
    }

    response = taxi_integration.post(
        'v1/changepayment', request, headers=headers,
    )
    assert response.status_code == 200

    request = {
        'userid': 'agent_user',
        'orderid': orderid,
        'payment_method_type': 'cash',
    }
    response = taxi_integration.post(
        'v1/changepayment', request, headers=headers,
    )
    assert response.status_code == 406
