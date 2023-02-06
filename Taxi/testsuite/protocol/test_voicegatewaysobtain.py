import datetime
import json

import pytest


@pytest.mark.now('2018-02-25T00:00:00')
def test_base(taxi_protocol, mockserver, db):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        body_request = json.loads(request.get_data())
        assert body_request['min_ttl'] == 3600
        assert body_request['new_ttl'] == 7200
        assert body_request['callee_phone'] == '+79031524200'
        assert body_request['external_ref_id'] == '<order_id>'
        assert body_request['caller'] == 'passenger'
        return {'phone': '+75557775522', 'ext': '007'}

    # DB preconditions
    assert db.order_talks.count() == 0
    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        'gateways': [
            {
                'gateway': {
                    'ext': '007',
                    'phone': '+75557775522',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
        ],
    }
    # Check database
    assert db.order_talks.count() == 1
    talks = db.order_talks.find_one({'_id': '<order_id>'})
    #  We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][0].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    #  Check equality for other
    assert talks == {
        '_id': '<order_id>',
        'forwardings': [
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'created': datetime.datetime(2018, 2, 25, 0),
                'expires': datetime.datetime(2018, 2, 25, 2),
                'callee': '+79031524200',
                'forwarding_id': '<order_id>02000000',
                'phone': '+75557775522',
                'ext': '007',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': ['<order_id>02000000'],
        'talks': [],
    }


@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.filldb(order_proc='blacklisted')
@pytest.mark.config(VGW_USE_VGW_API=True)
@pytest.mark.config(
    CALLCENTER_PHONES={
        'ru': {
            'formatted_phone': '+7 (800) 770-70-74',
            'mcc': '250',
            'phone': '+78007707074',
            'zones': {
                'moscow': {
                    'formatted_phone': '+7 (495) 999 99 99',
                    'phone': '+74959999999',
                },
            },
        },
    },
)
def test_blacklisted_forwarding(taxi_protocol, mockserver):
    # Mock calls to partner
    @mockserver.handler('/vgw-api/v1/forwardings')
    def _mock_redirections(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'code': 'PassengerBlackListed',
                    'message': 'Passenger phone number is blacklisted',
                    'error': {
                        'code': 'PassengerBlackListed',
                        'message': 'Passenger phone number is blacklisted',
                    },
                },
            ),
            status=400,
        )

    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id_passenger_blacklisted>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'gateways': [
            {
                'gateway': {
                    'ext': '',
                    'phone': '+74959999999',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
        ],
    }


@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.config(VGW_USE_VGW_API=True)
@pytest.mark.config(VGW_PROTOCOL_BLACKLISTED_SETTINGS={'__default__': False})
def test_notcheck_passenger_blacklisted(taxi_protocol, mockserver):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _mock_redirections(request):
        body_request = json.loads(request.get_data())
        assert not body_request['check_blacklisted']
        return {'phone': '+75557775522', 'ext': '007'}

    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )

    assert response.status_code == 200


@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.config(VGW_USE_VGW_API=True)
@pytest.mark.config(
    VGW_PROTOCOL_BLACKLISTED_SETTINGS={
        '__default__': False,
        'voicegatewayobtain': True,
    },
)
def test_check_passenger_blacklisted(taxi_protocol, mockserver):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _mock_redirections(request):
        body_request = json.loads(request.get_data())
        assert body_request['check_blacklisted']
        return {'phone': '+75557775522', 'ext': '007'}

    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    'request_body, status_code',
    [
        (
            {
                'requests': [
                    {
                        'order_id': '<order_id>',
                        'caller': 'user',
                        'callee': 'driver',
                        'callee_phone': '+79031524200',
                        'ttl_seconds_new': 2 * 60 * 60,
                        'ttl_seconds_min': 1 * 60 * 60,
                    },
                ],
            },
            200,
        ),  # OK
        ('', 400),  # empty request body
        ({}, 400),  # no requests field
        ({'requests': 1}, 400),  # incorrect requests field type
        ({'requests': None}, 400),  # requests field is None
    ],
)
@pytest.mark.now('2018-02-25T00:00:00')
def test_input_incorrect_requests_fields(
        taxi_protocol, mockserver, request_body, status_code,
):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        return {'phone': '+75557775522', 'ext': '007'}

    # Call
    response = taxi_protocol.post('voicegatewaysobtain', request_body)
    # Check response
    assert response.status_code == status_code


@pytest.mark.parametrize(
    'subfield, pop_subfield, value, status_code',
    [
        (None, False, None, 200),  # OK
        ('order_id', True, None, 400),  # no order_id
        ('order_id', False, None, 400),  # order_id is None
        ('order_id', False, 1234, 400),  # order_id has incorrect type
        ('caller', True, None, 400),  # no caller
        ('caller', False, None, 400),  # caller is None
        ('caller', False, 1234, 400),  # caller has incorrect type
        ('callee', True, None, 400),  # no callee
        ('callee', False, None, 400),  # callee is None
        ('callee', False, 1234, 400),  # callee has incorrect type
        ('callee_phone', True, None, 400),  # no callee_phone
        ('callee_phone', False, None, 400),  # callee_phone is None
        ('callee_phone', False, 1234, 400),  # callee_phone has incorrect type
        ('ttl_seconds_new', True, None, 400),  # no ttl_seconds_new
        ('ttl_seconds_new', False, None, 400),  # ttl_seconds_new is None
        # ttl_seconds_new has incorrect type
        ('ttl_seconds_new', False, '12', 400),
        ('ttl_seconds_min', True, None, 400),  # no ttl_seconds_min
        ('ttl_seconds_min', False, None, 400),  # ttl_seconds_min is None
        # ttl_seconds_min has incorrect type
        ('ttl_seconds_min', False, '12', 400),
    ],
)
@pytest.mark.now('2018-02-25T00:00:00')
def test_input_incorrect_requests_subfields(
        taxi_protocol, mockserver, subfield, pop_subfield, value, status_code,
):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        return {'phone': '+75557775522', 'ext': '007'}

    # Prepare params
    request_body = {
        'requests': [
            {
                'order_id': '<order_id>',
                'caller': 'user',
                'callee': 'driver',
                'callee_phone': '+79031524200',
                'ttl_seconds_new': 2 * 60 * 60,
                'ttl_seconds_min': 1 * 60 * 60,
            },
        ],
    }
    if subfield:
        if pop_subfield:
            request_body['requests'][0].pop(subfield)
        else:
            request_body['requests'][0][subfield] = value
    # Call
    response = taxi_protocol.post('voicegatewaysobtain', request_body)
    # Check response
    assert response.status_code == status_code


@pytest.mark.parametrize(
    'field, value, status_code, response_body',
    [
        (
            None,
            None,
            200,
            {
                'gateways': [
                    {
                        'gateway': {
                            'ext': '007',
                            'phone': '+75557775522',
                            'ttl_seconds': 2 * 60 * 60,
                        },
                    },
                ],
            },
        ),  # OK
        (
            'caller',
            'not_user',
            200,
            {
                'gateways': [
                    {
                        'error': {
                            'code': 'BadCaller',
                            'message': 'Unknown caller type: not_user',
                        },
                    },
                ],
            },
        ),  # incorrect caller
        (
            'callee',
            'not_driver',
            200,
            {
                'gateways': [
                    {
                        'error': {
                            'code': 'BadCallee',
                            'message': 'Unknown callee type: not_driver',
                        },
                    },
                ],
            },
        ),  # incorrect callee
    ],
)
@pytest.mark.now('2018-02-25T00:00:00')
def test_input_bad_values(
        taxi_protocol,
        mockserver,
        db,
        field,
        value,
        status_code,
        response_body,
):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        return {'phone': '+75557775522', 'ext': '007'}

    # DB preconditions
    assert db.order_talks.count() == 0
    # Prepare params
    request_body = {
        'requests': [
            {
                'order_id': '<order_id>',
                'caller': 'user',
                'callee': 'driver',
                'callee_phone': '+79031524200',
                'ttl_seconds_new': 2 * 60 * 60,
                'ttl_seconds_min': 1 * 60 * 60,
            },
        ],
    }
    if field:
        request_body['requests'][0][field] = value
    # Call
    response = taxi_protocol.post('voicegatewaysobtain', request_body)
    # Check response
    assert response.status_code == status_code
    # Check response
    assert response.status_code == 200
    assert response.json() == response_body
    # Check database
    if field:
        assert db.order_talks.count() == 0
    else:
        assert db.order_talks.count() == 1
        talks = db.order_talks.find_one({'_id': '<order_id>'})
        # We can't mock $currentDate now, so check it separately
        item_updated = talks['forwardings'][0].pop('updated')
        assert abs(
            datetime.datetime.utcnow() - item_updated,
        ) < datetime.timedelta(minutes=10)
        doc_updated = talks.pop('updated')
        assert abs(
            datetime.datetime.utcnow() - doc_updated,
        ) < datetime.timedelta(minutes=10)
        # Check other fields
        assert talks == {
            '_id': '<order_id>',
            'forwardings': [
                {
                    'driver_id': '<driver_id>',
                    'gateway_id': 'vgw-api',
                    'created': datetime.datetime(2018, 2, 25, 0),
                    'expires': datetime.datetime(2018, 2, 25, 2),
                    'callee': '+79031524200',
                    'forwarding_id': '<order_id>02000000',
                    'phone': '+75557775522',
                    'ext': '007',
                    'type': 'ondriver4user',
                },
            ],
            'forwardings_active': ['<order_id>02000000'],
            'talks': [],
        }


@pytest.mark.now('2018-02-25T00:00:00')
def test_partner_invalid_phone_number(taxi_protocol, mockserver, db):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        body_request = json.loads(request.get_data())
        assert body_request['min_ttl'] == 3600
        assert body_request['new_ttl'] == 7200
        assert body_request['callee_phone'] == '+79031524200'
        assert body_request['external_ref_id'] == '<order_id>'
        assert body_request['caller'] == 'passenger'
        return {'phone': 'bla-bla-bla', 'ext': '007'}

    # DB preconditions
    assert db.order_talks.count() == 0
    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        'gateways': [
            {
                'error': {
                    'code': 'PartnerUnableToHandle',
                    'message': (
                        'invalid phone number bla-bla-bla; '
                        'code = PartnerUnableToHandle'
                    ),
                },
            },
        ],
    }
    # Check database
    assert db.order_talks.count() == 1
    talks = db.order_talks.find_one({'_id': '<order_id>'})
    # We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][0].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    # Check other fields
    assert talks == {
        '_id': '<order_id>',
        'forwardings': [
            {
                'draft_state': 'broken',
                'driver_id': '<driver_id>',
                'created': datetime.datetime(2018, 2, 25, 0),
                'expires': datetime.datetime(2018, 2, 25, 2),
                'callee': '+79031524200',
                'forwarding_id': '<order_id>02000000',
                'gateway_id': 'vgw-api',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': [],
        'talks': [],
    }


@pytest.mark.now('2018-02-25T00:00:00')
def test_unknown_order(taxi_protocol, mockserver, db):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        return [{'phone': '+75557775522', 'ext': '007'}]

    # DB preconditions
    assert db.order_talks.count() == 0
    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<incorrect_order_id>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        'gateways': [
            {
                'error': {
                    'code': 'UnknownOrder',
                    'message': 'Unknown order: <incorrect_order_id>',
                },
            },
        ],
    }
    # Check database
    assert db.order_talks.count() == 0


@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.parametrize(
    'caller, callee, phone, intro, doctype, short_doctype',
    [
        ('user', 'driver', '+79031524200', 'mobile', 'ondriver4user', '02'),
        (
            'user',
            'dispatcher',
            '+79031524203',
            'mobile',
            'ondispatch4user',
            '03',
        ),
        ('driver', 'user', '+79031524201', 'driver', 'onuser4driver', '00'),
        ('dispatcher', 'user', '+79031524201', 'op', 'onuser4dispatch', '01'),
    ],
)
def test_misc_callers_and_callees(
        taxi_protocol,
        mockserver,
        db,
        caller,
        callee,
        phone,
        intro,
        doctype,
        short_doctype,
):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        body_request = json.loads(request.get_data())
        assert body_request['min_ttl'] == 3600
        assert body_request['new_ttl'] == 7200
        assert body_request['callee_phone'] == phone
        assert body_request['external_ref_id'] == '<order_id>'
        caller_type = 'passenger' if caller == 'user' else caller
        callee_type = 'passenger' if callee == 'user' else callee
        assert body_request['caller'] == caller_type
        assert body_request['callee'] == callee_type
        return {'phone': '+75557775522', 'ext': '007'}

    # DB preconditions
    assert db.order_talks.count() == 0
    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id>',
                    'caller': caller,
                    'callee': callee,
                    'callee_phone': phone,
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        'gateways': [
            {
                'gateway': {
                    'ext': '007',
                    'phone': '+75557775522',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
        ],
    }
    # Check database
    assert db.order_talks.count() == 1
    talks = db.order_talks.find_one({'_id': '<order_id>'})
    #  We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][0].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    #  Check other values
    assert talks == {
        '_id': '<order_id>',
        'forwardings': [
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'created': datetime.datetime(2018, 2, 25, 0),
                'expires': datetime.datetime(2018, 2, 25, 2),
                'callee': phone,
                'forwarding_id': '<order_id>' + short_doctype + '000000',
                'phone': '+75557775522',
                'ext': '007',
                'type': doctype,
            },
        ],
        'forwardings_active': ['<order_id>' + short_doctype + '000000'],
        'talks': [],
    }


@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.parametrize(
    'caller, callee, phone, current_phone',
    [
        ('user', 'driver', '+79031524100', '+79031524200'),
        ('user', 'dispatcher', '+79031524103', '+79031524203'),
        ('driver', 'user', '+79031524101', '+79031524201'),
        ('dispatcher', 'user', '+79031524101', '+79031524201'),
    ],
)
def test_conflict_phone_errors(
        taxi_protocol, mockserver, db, caller, callee, phone, current_phone,
):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        return {'phone': '+75557775522', 'ext': '007'}

    # DB preconditions
    assert db.order_talks.count() == 0
    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id>',
                    'caller': caller,
                    'callee': callee,
                    'callee_phone': phone,
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        'gateways': [
            {
                'error': {
                    'code': 'ConflictByPhone',
                    'message': (
                        'Callee current phone mismatch: ' + current_phone
                    ),
                },
            },
        ],
    }
    # Check database
    assert db.order_talks.count() == 0


@pytest.mark.now('2018-02-25T00:00:00')
def test_many_different_orders(taxi_protocol, mockserver, db):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        body_request = json.loads(request.get_data())
        assert body_request['min_ttl'] == 3600
        assert body_request['new_ttl'] == 7200
        if body_request['external_ref_id'] == '<order_id_0>':
            assert body_request['callee_phone'] == '+79031524200'
            assert body_request['caller'] == 'passenger'
            return {'phone': '+75557775500', 'ext': '007'}
        if body_request['external_ref_id'] == '<order_id_1>':
            assert body_request['callee_phone'] == '+79031524200'
            assert body_request['caller'] == 'passenger'
            return {'phone': '+75557775500', 'ext': '007'}
        elif body_request['external_ref_id'] == '<order_id_2>':
            assert body_request['callee_phone'] == '+79031524201'
            assert body_request['caller'] == 'driver'
            return {'phone': '+75557775501', 'ext': '008'}
        assert False

    # DB preconditions
    assert db.order_talks.count() == 0
    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id_0>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
                {
                    'order_id': '<order_id_1>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
                {
                    'order_id': '<order_id_2>',
                    'caller': 'driver',
                    'callee': 'user',
                    'callee_phone': '+79031524201',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        'gateways': [
            {
                'gateway': {
                    'ext': '007',
                    'phone': '+75557775500',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
            {
                'gateway': {
                    'ext': '007',
                    'phone': '+75557775500',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
            {
                'gateway': {
                    'ext': '008',
                    'phone': '+75557775501',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
        ],
    }
    # Check database
    assert db.order_talks.count() == 3
    #  Check doc 0
    talks = db.order_talks.find_one({'_id': '<order_id_0>'})
    #   We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][0].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    #   Check other fields
    assert talks == {
        '_id': '<order_id_0>',
        'forwardings': [
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'created': datetime.datetime(2018, 2, 25, 0),
                'expires': datetime.datetime(2018, 2, 25, 2),
                'callee': '+79031524200',
                'forwarding_id': '<order_id_0>02000000',
                'phone': '+75557775500',
                'ext': '007',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': ['<order_id_0>02000000'],
        'talks': [],
    }
    #  Check doc 1
    talks = db.order_talks.find_one({'_id': '<order_id_1>'})
    #   We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][0].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    #   Check other fields
    assert talks == {
        '_id': '<order_id_1>',
        'forwardings': [
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'created': datetime.datetime(2018, 2, 25, 0),
                'expires': datetime.datetime(2018, 2, 25, 2),
                'callee': '+79031524200',
                'forwarding_id': '<order_id_1>02000000',
                'phone': '+75557775500',
                'ext': '007',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': ['<order_id_1>02000000'],
        'talks': [],
    }
    #  Check doc 2
    talks = db.order_talks.find_one({'_id': '<order_id_2>'})
    #   We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][0].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    #   Check other fields
    assert talks == {
        '_id': '<order_id_2>',
        'forwardings': [
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'created': datetime.datetime(2018, 2, 25, 0),
                'expires': datetime.datetime(2018, 2, 25, 2),
                'callee': '+79031524201',
                'forwarding_id': '<order_id_2>00000000',
                'phone': '+75557775501',
                'ext': '008',
                'type': 'onuser4driver',
            },
        ],
        'forwardings_active': ['<order_id_2>00000000'],
        'talks': [],
    }


@pytest.mark.now('2018-02-25T00:00:00')
def test_single_order_many_types(taxi_protocol, mockserver, db):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        body_request = json.loads(request.get_data())
        assert body_request['min_ttl'] == 3600
        assert body_request['new_ttl'] == 7200
        assert body_request['external_ref_id'] == '<order_id_0>'
        if body_request['callee'] == 'driver':
            assert body_request['callee_phone'] == '+79031524200'
            assert body_request['caller'] == 'passenger'
            return {'phone': '+75557775500', 'ext': '007'}
        if body_request['callee'] == 'passenger':
            assert body_request['callee_phone'] == '+79031524201'
            assert body_request['caller'] == 'driver'
            return {'phone': '+75557775501', 'ext': '008'}
        if body_request['callee'] == 'dispatcher':
            assert body_request['callee_phone'] == '+79031524203'
            assert body_request['caller'] == 'passenger'
            return {'phone': '+75557775502', 'ext': '009'}
        assert False

    # DB preconditions
    assert db.order_talks.count() == 0
    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id_0>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
                {
                    'order_id': '<order_id_0>',
                    'caller': 'driver',
                    'callee': 'user',
                    'callee_phone': '+79031524201',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
                {
                    'order_id': '<order_id_0>',
                    'caller': 'user',
                    'callee': 'dispatcher',
                    'callee_phone': '+79031524203',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        'gateways': [
            {
                'gateway': {
                    'ext': '007',
                    'phone': '+75557775500',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
            {
                'gateway': {
                    'ext': '008',
                    'phone': '+75557775501',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
            {
                'gateway': {
                    'ext': '009',
                    'phone': '+75557775502',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
        ],
    }
    # Check database
    assert db.order_talks.count() == 1
    talks = db.order_talks.find_one({'_id': '<order_id_0>'})
    #  We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][0].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    item_updated = talks['forwardings'][1].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    item_updated = talks['forwardings'][2].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    #  Check forwardings
    forwardings_dict = dict()
    for forwarding in talks.pop('forwardings'):
        forwardings_dict[forwarding['forwarding_id']] = forwarding
    assert forwardings_dict == {
        '<order_id_0>02000000': {
            'driver_id': '<driver_id>',
            'gateway_id': 'vgw-api',
            'created': datetime.datetime(2018, 2, 25, 0),
            'expires': datetime.datetime(2018, 2, 25, 2),
            'callee': '+79031524200',
            'forwarding_id': '<order_id_0>02000000',
            'phone': '+75557775500',
            'ext': '007',
            'type': 'ondriver4user',
        },
        '<order_id_0>00000000': {
            'driver_id': '<driver_id>',
            'gateway_id': 'vgw-api',
            'created': datetime.datetime(2018, 2, 25, 0),
            'expires': datetime.datetime(2018, 2, 25, 2),
            'callee': '+79031524201',
            'forwarding_id': '<order_id_0>00000000',
            'phone': '+75557775501',
            'ext': '008',
            'type': 'onuser4driver',
        },
        '<order_id_0>03000000': {
            'driver_id': '<driver_id>',
            'gateway_id': 'vgw-api',
            'created': datetime.datetime(2018, 2, 25, 0),
            'expires': datetime.datetime(2018, 2, 25, 2),
            'callee': '+79031524203',
            'forwarding_id': '<order_id_0>03000000',
            'phone': '+75557775502',
            'ext': '009',
            'type': 'ondispatch4user',
        },
    }
    #  Check forwardings_active
    assert set(talks.pop('forwardings_active')) == {
        '<order_id_0>02000000',
        '<order_id_0>00000000',
        '<order_id_0>03000000',
    }
    #  Check other fields
    assert talks == {'_id': '<order_id_0>', 'talks': []}


@pytest.mark.now('2018-02-25T00:00:00')
def test_single_order_many_equal_types(taxi_protocol, mockserver, db):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        body_request = json.loads(request.get_data())
        assert body_request['min_ttl'] == 3600
        assert body_request['new_ttl'] == 7200
        if body_request['external_ref_id'] == '<order_id_0>':
            assert body_request['callee_phone'] == '+79031524200'
            assert body_request['caller'] == 'passenger'
            return {'phone': '+75557775500', 'ext': '007'}
        assert False

    # DB preconditions
    assert db.order_talks.count() == 0
    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id_0>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
                {
                    'order_id': '<order_id_0>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
                {
                    'order_id': '<order_id_0>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
    # Check response
    assert response.status_code == 200
    gateways = response.json()['gateways']
    assert len(gateways)
    for gateway_or_error in gateways:
        if 'gateway' in gateway_or_error:
            assert gateway_or_error == {
                'gateway': {
                    'ext': '007',
                    'phone': '+75557775500',
                    'ttl_seconds': 2 * 60 * 60,
                },
            }
        else:
            assert gateway_or_error['error']['code'] == 'DraftCreationConflict'
    # Check database
    assert db.order_talks.count() == 1
    talks = db.order_talks.find_one({'_id': '<order_id_0>'})
    #  We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][0].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    #  Check other fields
    assert talks == {
        '_id': '<order_id_0>',
        'forwardings': [
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'created': datetime.datetime(2018, 2, 25, 0),
                'expires': datetime.datetime(2018, 2, 25, 2),
                'callee': '+79031524200',
                'forwarding_id': '<order_id_0>02000000',
                'phone': '+75557775500',
                'ext': '007',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': ['<order_id_0>02000000'],
        'talks': [],
    }


@pytest.mark.skip(
    reason='Hard to find the reason. Postponed on later.' ' TAXIFLAPTEST-309',
)
@pytest.mark.now('2018-02-25T00:00:00')
def test_some_orders_some_types_some_exists_forwardings(
        taxi_protocol, mockserver, db,
):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        body_request = json.loads(request.get_data())
        assert body_request['min_ttl'] == 3600
        assert body_request['new_ttl'] == 7200
        if body_request['external_ref_id'] == '<order_id_0>':
            if body_request['callee'] == 'driver':
                assert body_request['callee_phone'] == '+79031524200'
                assert body_request['caller'] == 'passenger'
                return {'phone': '+75557775500', 'ext': '007'}
            if body_request['callee'] == 'passenger':
                assert body_request['callee_phone'] == '+79031524201'
                assert body_request['caller'] == 'driver'
                return {'phone': '+75557775501', 'ext': '008'}
            if body_request['callee'] == 'dispatcher':
                assert body_request['callee_phone'] == '+79031524203'
                assert body_request['caller'] == 'passenger'
                return {'phone': '+75557775502', 'ext': '009'}
        if body_request['external_ref_id'] == '<order_id_1>':
            assert body_request['callee_phone'] == '+79031524200'
            assert body_request['caller'] == 'passenger'
            return {'phone': '+75557775500', 'ext': '010'}
        if body_request['external_ref_id'] == '<order_id_2>':
            assert body_request['callee_phone'] == '+79031524200'
            assert body_request['caller'] == 'passenger'
            return {'phone': '+75557775500', 'ext': '011'}
        assert False

    # DB preconditions
    assert db.order_talks.count() == 0
    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id_0>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
                {
                    'order_id': '<order_id_0>',
                    'caller': 'driver',
                    'callee': 'user',
                    'callee_phone': '+79031524201',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
                {
                    'order_id': '<order_id_0>',
                    'caller': 'user',
                    'callee': 'dispatcher',
                    'callee_phone': '+79031524203',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
                {
                    'order_id': '<order_id_1>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
                {
                    'order_id': '<order_id_2>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        'gateways': [
            {
                'gateway': {
                    'ext': '007',
                    'phone': '+75557775500',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
            {
                'gateway': {
                    'ext': '008',
                    'phone': '+75557775501',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
            {
                'gateway': {
                    'ext': '009',
                    'phone': '+75557775502',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
            {
                'gateway': {
                    'ext': '010',
                    'phone': '+75557775500',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
            {
                'gateway': {
                    'ext': '011',
                    'phone': '+75557775500',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
        ],
    }
    # Check database
    assert db.order_talks.count() == 3
    #  Check document 1
    talks = db.order_talks.find_one({'_id': '<order_id_0>'})
    #   We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][0].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    item_updated = talks['forwardings'][1].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    item_updated = talks['forwardings'][2].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    #   Check forwardings
    forwardings_dict = dict()
    for forwarding in talks.pop('forwardings'):
        forwardings_dict[forwarding['forwarding_id']] = forwarding
    assert forwardings_dict == {
        '<order_id_0>02000000': {
            'driver_id': '<driver_id>',
            'gateway_id': 'vgw-api',
            'created': datetime.datetime(2018, 2, 25, 0),
            'expires': datetime.datetime(2018, 2, 25, 2),
            'callee': '+79031524200',
            'forwarding_id': '<order_id_0>02000000',
            'phone': '+75557775500',
            'ext': '007',
            'type': 'ondriver4user',
        },
        '<order_id_0>00000000': {
            'driver_id': '<driver_id>',
            'gateway_id': 'vgw-api',
            'created': datetime.datetime(2018, 2, 25, 0),
            'expires': datetime.datetime(2018, 2, 25, 2),
            'callee': '+79031524201',
            'forwarding_id': '<order_id_0>00000000',
            'phone': '+75557775501',
            'ext': '008',
            'type': 'onuser4driver',
        },
        '<order_id_0>03000000': {
            'driver_id': '<driver_id>',
            'gateway_id': 'vgw-api',
            'created': datetime.datetime(2018, 2, 25, 0),
            'expires': datetime.datetime(2018, 2, 25, 2),
            'callee': '+79031524203',
            'forwarding_id': '<order_id_0>03000000',
            'phone': '+75557775502',
            'ext': '009',
            'type': 'ondispatch4user',
        },
    }
    #   Check forwardings_active
    assert set(talks.pop('forwardings_active')) == {
        '<order_id_0>02000000',
        '<order_id_0>00000000',
        '<order_id_0>03000000',
    }
    #   Check other fields
    assert talks == {'_id': '<order_id_0>', 'talks': []}
    #  Check document 1
    talks = db.order_talks.find_one({'_id': '<order_id_1>'})
    #   We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][0].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    #   Check other fields
    assert talks == {
        '_id': '<order_id_1>',
        'forwardings': [
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'created': datetime.datetime(2018, 2, 25, 0),
                'expires': datetime.datetime(2018, 2, 25, 2),
                'callee': '+79031524200',
                'forwarding_id': '<order_id_1>02000000',
                'phone': '+75557775500',
                'ext': '010',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': ['<order_id_1>02000000'],
        'talks': [],
    }
    #  Check document 2
    talks = db.order_talks.find_one({'_id': '<order_id_2>'})
    #   We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][0].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    #   Check other fields
    assert talks == {
        '_id': '<order_id_2>',
        'forwardings': [
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'created': datetime.datetime(2018, 2, 25, 0),
                'expires': datetime.datetime(2018, 2, 25, 2),
                'callee': '+79031524200',
                'forwarding_id': '<order_id_2>02000000',
                'phone': '+75557775500',
                'ext': '011',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': ['<order_id_2>02000000'],
        'talks': [],
    }


@pytest.mark.now('2018-02-25T00:00:00')
def test_responses_with_errors_and_ok(taxi_protocol, mockserver, db):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        body_request = json.loads(request.get_data())
        assert body_request['min_ttl'] == 3600
        assert body_request['new_ttl'] == 7200
        if body_request['external_ref_id'] == '<order_id_0>':
            assert body_request['callee_phone'] == '+79031524200'
            assert body_request['caller'] == 'passenger'
            return mockserver.make_response('Not Found', status=404)
        if body_request['external_ref_id'] == '<order_id_1>':
            assert body_request['callee_phone'] == '+79031524200'
            assert body_request['caller'] == 'passenger'
            return {'phone': '+75557775500', 'ext': '007'}
        if body_request['external_ref_id'] == '<order_id_2>':
            assert body_request['callee_phone'] == '+79031524201'
            assert body_request['caller'] == 'driver'
            return mockserver.make_response('Service Unavailable', status=503)
        if body_request['external_ref_id'] == '<order_id_3>':
            assert body_request['callee_phone'] == '+79031524201'
            assert body_request['caller'] == 'driver'
            return {'phone': '+75557775501', 'ext': '008'}
        assert False

    # DB preconditions
    assert db.order_talks.count() == 0
    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id_0>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
                {
                    'order_id': '<incorrect_order_id>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
                {
                    'order_id': '<order_id_1>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
                {
                    'order_id': '<order_id_2>',
                    'caller': 'driver',
                    'callee': 'user',
                    'callee_phone': '+79031524201',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
                {
                    'order_id': '<order_id_3>',
                    'caller': 'driver',
                    'callee': 'user',
                    'callee_phone': '+79031524201',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        'gateways': [
            {
                'error': {
                    'code': 'PartnerResponsedNotFound',
                    'message': (
                        'got 404: Not Found; '
                        'code = PartnerResponsedNotFound'
                    ),
                },
            },
            {
                'error': {
                    'code': 'UnknownOrder',
                    'message': 'Unknown order: <incorrect_order_id>',
                },
            },
            {
                'gateway': {
                    'ext': '007',
                    'phone': '+75557775500',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
            {
                'error': {
                    'code': 'PartnerServerUnavailable',
                    'message': (
                        'got 503: Service Unavailable; '
                        'code = PartnerServerUnavailable'
                    ),
                },
            },
            {
                'gateway': {
                    'ext': '008',
                    'phone': '+75557775501',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
        ],
    }
    # Check database
    assert db.order_talks.count() == 4
    #  Check <order_id_0>
    talks = db.order_talks.find_one({'_id': '<order_id_0>'})
    #   We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][0].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    #   Check equality for other
    assert talks == {
        '_id': '<order_id_0>',
        'forwardings': [
            {
                'draft_state': 'broken',
                'driver_id': '<driver_id>',
                'created': datetime.datetime(2018, 2, 25, 0),
                'expires': datetime.datetime(2018, 2, 25, 2),
                'callee': '+79031524200',
                'forwarding_id': '<order_id_0>02000000',
                'gateway_id': 'vgw-api',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': [],
        'talks': [],
    }
    #  Check <order_id_1>
    talks = db.order_talks.find_one({'_id': '<order_id_1>'})
    #   We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][0].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    #   Check equality for other
    assert talks == {
        '_id': '<order_id_1>',
        'forwardings': [
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'created': datetime.datetime(2018, 2, 25, 0),
                'expires': datetime.datetime(2018, 2, 25, 2),
                'callee': '+79031524200',
                'forwarding_id': '<order_id_1>02000000',
                'phone': '+75557775500',
                'ext': '007',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': ['<order_id_1>02000000'],
        'talks': [],
    }
    #  Check <order_id_2>
    talks = db.order_talks.find_one({'_id': '<order_id_2>'})
    #   We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][0].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    #   Check equality for other
    assert talks == {
        '_id': '<order_id_2>',
        'forwardings': [
            {
                'draft_state': 'broken',
                'driver_id': '<driver_id>',
                'created': datetime.datetime(2018, 2, 25, 0),
                'expires': datetime.datetime(2018, 2, 25, 2),
                'callee': '+79031524201',
                'forwarding_id': '<order_id_2>00000000',
                'gateway_id': 'vgw-api',
                'type': 'onuser4driver',
            },
        ],
        'forwardings_active': [],
        'talks': [],
    }
    #  Check <order_id_3>
    talks = db.order_talks.find_one({'_id': '<order_id_3>'})
    #   We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][0].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    #   Check equality for other
    assert talks == {
        '_id': '<order_id_3>',
        'forwardings': [
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'created': datetime.datetime(2018, 2, 25, 0),
                'expires': datetime.datetime(2018, 2, 25, 2),
                'callee': '+79031524201',
                'forwarding_id': '<order_id_3>00000000',
                'phone': '+75557775501',
                'ext': '008',
                'type': 'onuser4driver',
            },
        ],
        'forwardings_active': ['<order_id_3>00000000'],
        'talks': [],
    }


@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.filldb(order_talks='existing_gateway')
def test_existing_gateway_is_ok(taxi_protocol, mockserver, db):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        return {'phone': '+75557775522', 'ext': '007'}

    # DB preconditions
    assert db.order_talks.count() == 1
    assert db.order_talks.find_one({'_id': '<order_id>'}) == {
        '_id': '<order_id>',
        'updated': datetime.datetime(2018, 2, 24, 0, 0),
        'forwardings': [
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'updated': datetime.datetime(2018, 2, 24, 0, 0),
                'created': datetime.datetime(2018, 2, 24, 0, 0),
                'expires': datetime.datetime(2018, 2, 25, 1, 30),
                'callee': '+79031524200',
                'forwarding_id': '<order_id>02000000',
                'phone': '+75557775522',
                'ext': '007',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': ['<order_id>02000000'],
        'talks': [],
    }
    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        'gateways': [
            {
                'gateway': {
                    'ext': '007',
                    'phone': '+75557775522',
                    'ttl_seconds': 90 * 60,
                },
            },
        ],
    }
    # Check database
    assert db.order_talks.count() == 1
    assert db.order_talks.find_one({'_id': '<order_id>'}) == {
        '_id': '<order_id>',
        'updated': datetime.datetime(2018, 2, 24, 0, 0),
        'forwardings': [
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'updated': datetime.datetime(2018, 2, 24, 0, 0),
                'created': datetime.datetime(2018, 2, 24, 0, 0),
                'expires': datetime.datetime(2018, 2, 25, 1, 30),
                'callee': '+79031524200',
                'forwarding_id': '<order_id>02000000',
                'phone': '+75557775522',
                'ext': '007',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': ['<order_id>02000000'],
        'talks': [],
    }


@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.filldb(order_talks='existing_gateway')
def test_existing_gateway_is_expired_but_active(taxi_protocol, mockserver, db):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        return {'phone': '+75557775522', 'ext': '007'}

    # DB preconditions
    assert db.order_talks.count() == 1
    assert db.order_talks.find_one({'_id': '<order_id>'}) == {
        '_id': '<order_id>',
        'updated': datetime.datetime(2018, 2, 24, 0, 0),
        'forwardings': [
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'updated': datetime.datetime(2018, 2, 24, 0, 0),
                'created': datetime.datetime(2018, 2, 24, 0, 0),
                'expires': datetime.datetime(2018, 2, 25, 1, 30),
                'callee': '+79031524200',
                'forwarding_id': '<order_id>02000000',
                'phone': '+75557775522',
                'ext': '007',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': ['<order_id>02000000'],
        'talks': [],
    }
    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 3 * 60 * 60,
                    'ttl_seconds_min': 2 * 60 * 60,
                },
            ],
        },
    )
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        'gateways': [
            {
                'gateway': {
                    'ext': '007',
                    'phone': '+75557775522',
                    'ttl_seconds': 3 * 60 * 60,
                },
            },
        ],
    }
    # Check database
    assert db.order_talks.count() == 1
    talks = db.order_talks.find_one({'_id': '<order_id>'})
    #  We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][1].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    #  Check other fields
    assert talks == {
        '_id': '<order_id>',
        'forwardings': [
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'updated': datetime.datetime(2018, 2, 24, 0, 0),
                'created': datetime.datetime(2018, 2, 24, 0, 0),
                'expires': datetime.datetime(2018, 2, 25, 1, 30),
                'callee': '+79031524200',
                'forwarding_id': '<order_id>02000000',
                'phone': '+75557775522',
                'ext': '007',
                'type': 'ondriver4user',
            },
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'created': datetime.datetime(2018, 2, 25, 0),
                'expires': datetime.datetime(2018, 2, 25, 3),
                'callee': '+79031524200',
                'forwarding_id': '<order_id>02000001',
                'phone': '+75557775522',
                'ext': '007',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': ['<order_id>02000000', '<order_id>02000001'],
        'talks': [],
    }


@pytest.mark.now('2018-02-26T00:00:00')
@pytest.mark.filldb(order_talks='existing_gateway')
def test_existing_gateway_is_expired_not_active(taxi_protocol, mockserver, db):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        return {'phone': '+75557775522', 'ext': '007'}

    # DB preconditions
    assert db.order_talks.count() == 1
    assert db.order_talks.find_one({'_id': '<order_id>'}) == {
        '_id': '<order_id>',
        'updated': datetime.datetime(2018, 2, 24, 0, 0),
        'forwardings': [
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'updated': datetime.datetime(2018, 2, 24, 0, 0),
                'created': datetime.datetime(2018, 2, 24, 0, 0),
                'expires': datetime.datetime(2018, 2, 25, 1, 30),
                'callee': '+79031524200',
                'forwarding_id': '<order_id>02000000',
                'phone': '+75557775522',
                'ext': '007',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': ['<order_id>02000000'],
        'talks': [],
    }
    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        'gateways': [
            {
                'gateway': {
                    'ext': '007',
                    'phone': '+75557775522',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
        ],
    }
    # Check database
    assert db.order_talks.count() == 1
    talks = db.order_talks.find_one({'_id': '<order_id>'})
    #  We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][1].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    #  Check other fields
    assert talks == {
        '_id': '<order_id>',
        'forwardings': [
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'updated': datetime.datetime(2018, 2, 24, 0, 0),
                'created': datetime.datetime(2018, 2, 24, 0, 0),
                'expires': datetime.datetime(2018, 2, 25, 1, 30),
                'callee': '+79031524200',
                'forwarding_id': '<order_id>02000000',
                'phone': '+75557775522',
                'ext': '007',
                'type': 'ondriver4user',
            },
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'created': datetime.datetime(2018, 2, 26, 0),
                'expires': datetime.datetime(2018, 2, 26, 2),
                'callee': '+79031524200',
                'forwarding_id': '<order_id>02000001',
                'phone': '+75557775522',
                'ext': '007',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': ['<order_id>02000000', '<order_id>02000001'],
        'talks': [],
    }


@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.filldb(order_talks='existing_gateway_has_another_phone')
def test_existing_gateway_has_another_phone(taxi_protocol, mockserver, db):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        return {'phone': '+75557775522', 'ext': '007'}

    # DB preconditions
    assert db.order_talks.count() == 1
    assert db.order_talks.find_one({'_id': '<order_id>'}) == {
        '_id': '<order_id>',
        'updated': datetime.datetime(2018, 2, 24, 0, 0),
        'forwardings': [
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'updated': datetime.datetime(2018, 2, 24, 0, 0),
                'created': datetime.datetime(2018, 2, 24, 0, 0),
                'expires': datetime.datetime(2018, 2, 25, 1, 30),
                'callee': '+79031524199',
                'forwarding_id': '<order_id>02000000',
                'phone': '+75557775522',
                'ext': '007',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': ['<order_id>02000000'],
        'talks': [],
    }
    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        'gateways': [
            {
                'gateway': {
                    'ext': '007',
                    'phone': '+75557775522',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
        ],
    }
    # Check database
    talks = db.order_talks.find_one({'_id': '<order_id>'})
    #  We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][1].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    #  Check other fields
    assert talks == {
        '_id': '<order_id>',
        'forwardings': [
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'updated': datetime.datetime(2018, 2, 24, 0, 0),
                'created': datetime.datetime(2018, 2, 24, 0, 0),
                'expires': datetime.datetime(2018, 2, 25, 1, 30),
                'callee': '+79031524199',
                'forwarding_id': '<order_id>02000000',
                'phone': '+75557775522',
                'ext': '007',
                'type': 'ondriver4user',
            },
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'created': datetime.datetime(2018, 2, 25, 0),
                'expires': datetime.datetime(2018, 2, 25, 2),
                'callee': '+79031524200',
                'forwarding_id': '<order_id>02000001',
                'phone': '+75557775522',
                'ext': '007',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': ['<order_id>02000000', '<order_id>02000001'],
        'talks': [],
    }


@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.filldb(order_talks='existing_gateway_has_another_doc_type')
def test_existing_gateway_has_another_doc_type(taxi_protocol, mockserver, db):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        return {'phone': '+75557775522', 'ext': '007'}

    # DB preconditions
    assert db.order_talks.count() == 1
    assert db.order_talks.find_one({'_id': '<order_id>'}) == {
        '_id': '<order_id>',
        'updated': datetime.datetime(2018, 2, 24, 0, 0),
        'forwardings': [
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'updated': datetime.datetime(2018, 2, 24, 0, 0),
                'created': datetime.datetime(2018, 2, 24, 0, 0),
                'expires': datetime.datetime(2018, 2, 25, 1, 30),
                'callee': '+79031524201',
                'forwarding_id': '<order_id>02000000',
                'phone': '+75557775522',
                'ext': '007',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': ['<order_id>02000000'],
        'talks': [],
    }
    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id>',
                    'caller': 'driver',
                    'callee': 'user',
                    'callee_phone': '+79031524201',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        'gateways': [
            {
                'gateway': {
                    'ext': '007',
                    'phone': '+75557775522',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
        ],
    }
    # Check database
    assert db.order_talks.count() == 1
    talks = db.order_talks.find_one({'_id': '<order_id>'})
    #  We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][1].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    #  Check other fields
    assert talks == {
        '_id': '<order_id>',
        'forwardings': [
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'updated': datetime.datetime(2018, 2, 24, 0, 0),
                'created': datetime.datetime(2018, 2, 24, 0, 0),
                'expires': datetime.datetime(2018, 2, 25, 1, 30),
                'callee': '+79031524201',
                'forwarding_id': '<order_id>02000000',
                'phone': '+75557775522',
                'ext': '007',
                'type': 'ondriver4user',
            },
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'created': datetime.datetime(2018, 2, 25, 0),
                'expires': datetime.datetime(2018, 2, 25, 2),
                'callee': '+79031524201',
                'forwarding_id': '<order_id>00000000',
                'phone': '+75557775522',
                'ext': '007',
                'type': 'onuser4driver',
            },
        ],
        'forwardings_active': ['<order_id>02000000', '<order_id>00000000'],
        'talks': [],
    }


@pytest.mark.now('2018-02-24T00:00:03')
@pytest.mark.filldb(order_talks='existing_created_draft')
@pytest.mark.config(VGW_TIMEOUT_MS=5000)
def test_existing_processing_draft(taxi_protocol, mockserver, db):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        return {'phone': '+75557775522', 'ext': '007'}

    # DB preconditions
    assert db.order_talks.count() == 1
    assert db.order_talks.find_one({'_id': '<order_id>'}) == {
        '_id': '<order_id>',
        'updated': datetime.datetime(2018, 2, 24, 0, 0),
        'forwardings': [
            {
                'draft_state': 'created',
                'driver_id': '<driver_id>',
                'updated': datetime.datetime(2018, 2, 24, 0, 0),
                'created': datetime.datetime(2018, 2, 24, 0, 0),
                'expires': datetime.datetime(2018, 2, 24, 2, 0),
                'callee': '+79031524200',
                'forwarding_id': '<order_id>02000000',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': [],
        'talks': [],
    }
    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        'gateways': [
            {
                'error': {
                    'code': 'DraftCreationConflict',
                    'message': (
                        'can not create new draft while old is not ' 'expired'
                    ),
                },
            },
        ],
    }
    # Check database
    assert db.order_talks.count() == 1
    assert db.order_talks.find_one({'_id': '<order_id>'}) == {
        '_id': '<order_id>',
        'updated': datetime.datetime(2018, 2, 24, 0, 0),
        'forwardings': [
            {
                'draft_state': 'created',
                'driver_id': '<driver_id>',
                'updated': datetime.datetime(2018, 2, 24, 0, 0),
                'created': datetime.datetime(2018, 2, 24, 0, 0),
                'expires': datetime.datetime(2018, 2, 24, 2, 0),
                'callee': '+79031524200',
                'forwarding_id': '<order_id>02000000',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': [],
        'talks': [],
    }


@pytest.mark.now('2018-02-24T00:00:07')
@pytest.mark.filldb(order_talks='existing_created_draft')
@pytest.mark.config(VGW_TIMEOUT_MS=5000)
@pytest.mark.parametrize('test_elem_match', [False, True])
def test_existing_expired_draft(
        taxi_protocol, mockserver, testpoint, db, test_elem_match,
):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        return {'phone': '+75557775522', 'ext': '007'}

    @testpoint('voicegateways::gatewayobtained')
    def make_draft_incorrect(data):
        assert data is None
        if test_elem_match:
            db.order_talks.update(
                {
                    '_id': '<order_id>',
                    'forwardings.forwarding_id': '<order_id>02000001',
                },
                {'$set': {'forwardings.$.draft_state': 'broken'}},
            )

    # DB preconditions
    assert db.order_talks.count() == 1
    assert db.order_talks.find_one({'_id': '<order_id>'}) == {
        '_id': '<order_id>',
        'updated': datetime.datetime(2018, 2, 24, 0, 0),
        'forwardings': [
            {
                'draft_state': 'created',
                'driver_id': '<driver_id>',
                'updated': datetime.datetime(2018, 2, 24, 0, 0),
                'created': datetime.datetime(2018, 2, 24, 0, 0),
                'expires': datetime.datetime(2018, 2, 24, 2, 0),
                'callee': '+79031524200',
                'forwarding_id': '<order_id>02000000',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': [],
        'talks': [],
    }
    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
    # Check test point was called
    if test_elem_match:
        assert make_draft_incorrect.times_called == 1
    # Check response
    assert response.status_code == 200
    if test_elem_match:
        assert response.json() == {
            'gateways': [
                {
                    'error': {
                        'code': 'InternalProblem',
                        'message': (
                            'no draft with such forwarding id = '
                            '<order_id>02000001'
                        ),
                    },
                },
            ],
        }
    else:
        assert response.json() == {
            'gateways': [
                {
                    'gateway': {
                        'ext': '007',
                        'phone': '+75557775522',
                        'ttl_seconds': 7200,
                    },
                },
            ],
        }
    # Check database
    assert db.order_talks.count() == 1
    talks = db.order_talks.find_one({'_id': '<order_id>'})
    if test_elem_match:
        assert talks == {
            '_id': '<order_id>',
            'updated': datetime.datetime(2018, 2, 24, 0, 0, 7),
            'forwardings': [
                {
                    'draft_state': 'created',
                    'driver_id': '<driver_id>',
                    'created': datetime.datetime(2018, 2, 24, 0, 0),
                    'updated': datetime.datetime(2018, 2, 24, 0, 0),
                    'expires': datetime.datetime(2018, 2, 24, 2, 0),
                    'callee': '+79031524200',
                    'forwarding_id': '<order_id>02000000',
                    'type': 'ondriver4user',
                },
                {
                    'draft_state': 'broken',
                    'driver_id': '<driver_id>',
                    'created': datetime.datetime(2018, 2, 24, 0, 0, 7),
                    'updated': datetime.datetime(2018, 2, 24, 0, 0, 7),
                    'expires': datetime.datetime(2018, 2, 24, 2, 0, 7),
                    'callee': '+79031524200',
                    'forwarding_id': '<order_id>02000001',
                    'gateway_id': 'vgw-api',
                    'type': 'ondriver4user',
                },
            ],
            'forwardings_active': [],
            'talks': [],
        }
    else:
        #  We can't mock $currentDate now, so check it separately
        item_updated = talks['forwardings'][1].pop('updated')
        assert abs(
            datetime.datetime.utcnow() - item_updated,
        ) < datetime.timedelta(minutes=10)
        doc_updated = talks.pop('updated')
        assert abs(
            datetime.datetime.utcnow() - doc_updated,
        ) < datetime.timedelta(minutes=10)
        #  Check equality for other
        assert talks == {
            '_id': '<order_id>',
            'forwardings': [
                {
                    'draft_state': 'created',
                    'driver_id': '<driver_id>',
                    'updated': datetime.datetime(2018, 2, 24, 0, 0),
                    'created': datetime.datetime(2018, 2, 24, 0, 0),
                    'expires': datetime.datetime(2018, 2, 24, 2, 0),
                    'callee': '+79031524200',
                    'forwarding_id': '<order_id>02000000',
                    'type': 'ondriver4user',
                },
                {
                    'driver_id': '<driver_id>',
                    'created': datetime.datetime(2018, 2, 24, 0, 0, 7),
                    'expires': datetime.datetime(2018, 2, 24, 2, 0, 7),
                    'callee': '+79031524200',
                    'forwarding_id': '<order_id>02000001',
                    'gateway_id': 'vgw-api',
                    'phone': '+75557775522',
                    'ext': '007',
                    'type': 'ondriver4user',
                },
            ],
            'forwardings_active': ['<order_id>02000001'],
            'talks': [],
        }


@pytest.mark.now('2018-02-24T00:00:03')
@pytest.mark.filldb(order_talks='existing_broken_draft')
@pytest.mark.config(VGW_TIMEOUT_MS=5000)
def test_existing_broken_draft(taxi_protocol, mockserver, db):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        return {'phone': '+75557775522', 'ext': '007'}

    # DB preconditions
    assert db.order_talks.count() == 1
    assert db.order_talks.find_one({'_id': '<order_id>'}) == {
        '_id': '<order_id>',
        'updated': datetime.datetime(2018, 2, 24, 0, 0, 2),
        'forwardings': [
            {
                'draft_state': 'broken',
                'driver_id': '<driver_id>',
                'updated': datetime.datetime(2018, 2, 24, 0, 0, 2),
                'created': datetime.datetime(2018, 2, 24, 0, 0, 0),
                'expires': datetime.datetime(2018, 2, 24, 2, 0, 0),
                'callee': '+79031524200',
                'forwarding_id': '<order_id>02000000',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': [],
        'talks': [],
    }
    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        'gateways': [
            {
                'gateway': {
                    'ext': '007',
                    'phone': '+75557775522',
                    'ttl_seconds': 7200,
                },
            },
        ],
    }
    # Check database
    assert db.order_talks.count() == 1
    talks = db.order_talks.find_one({'_id': '<order_id>'})
    #  We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][1].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    #  Check equality for other
    assert talks == {
        '_id': '<order_id>',
        'forwardings': [
            {
                'draft_state': 'broken',
                'driver_id': '<driver_id>',
                'updated': datetime.datetime(2018, 2, 24, 0, 0, 2),
                'created': datetime.datetime(2018, 2, 24, 0, 0, 0),
                'expires': datetime.datetime(2018, 2, 24, 2, 0, 0),
                'callee': '+79031524200',
                'forwarding_id': '<order_id>02000000',
                'type': 'ondriver4user',
            },
            {
                'driver_id': '<driver_id>',
                'created': datetime.datetime(2018, 2, 24, 0, 0, 3, 0),
                'expires': datetime.datetime(2018, 2, 24, 2, 0, 3, 0),
                'callee': '+79031524200',
                'forwarding_id': '<order_id>02000001',
                'gateway_id': 'vgw-api',
                'phone': '+75557775522',
                'ext': '007',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': ['<order_id>02000001'],
        'talks': [],
    }


@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.filldb(order_proc='vgw_api')
def test_vgw_api_experiment(taxi_protocol, mockserver, db):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        req_data = json.loads(request.get_data())
        assert req_data['caller'] == 'passenger'
        assert req_data['callee'] == 'driver'
        assert req_data['caller_phone'] == '+79031524201'
        assert req_data['callee_phone'] == '+79031524200'
        assert req_data['external_ref_id'] == '<order_id>'
        assert len(req_data['nonce']) == 32
        assert req_data['consumer'] == 2
        assert req_data['call_location'] == [
            37.58917997300821,
            55.73341076871702,
        ]

        return {
            'expires_at': '2019-03-12T16:11:55+0300',
            'phone': '+75557775522',
            'ext': '007',
        }

    # DB preconditions
    assert db.order_talks.count() == 0
    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        'gateways': [
            {
                'gateway': {
                    'ext': '007',
                    'phone': '+75557775522',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
        ],
    }
    # Check database
    assert db.order_talks.count() == 1
    talks = db.order_talks.find_one({'_id': '<order_id>'})
    #  We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][0].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    #  Check equality for other
    assert talks == {
        '_id': '<order_id>',
        'forwardings': [
            {
                'driver_id': '<driver_id>',
                'gateway_id': 'vgw-api',
                'created': datetime.datetime(2018, 2, 25, 0),
                'expires': datetime.datetime(2018, 2, 25, 2),
                'callee': '+79031524200',
                'forwarding_id': '<order_id>02000000',
                'phone': '+75557775522',
                'ext': '007',
                'type': 'ondriver4user',
            },
        ],
        'forwardings_active': ['<order_id>02000000'],
        'talks': [],
    }


@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.filldb(order_proc='vgw_api_full')
@pytest.mark.config(
    VGW_TOTW_DRIVER_VOICE_FORWARDING_TTL_SECONDS_MIN=3600,
    VGW_TOTW_DRIVER_VOICE_FORWARDING_TTL_SECONDS_NEW=7200,
    VGW_USE_VGW_API=True,
)
def test_vgw_api_experiment_full(taxi_protocol, mockserver, db):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        req_data = json.loads(request.get_data())
        assert req_data['caller'] == 'passenger'
        assert req_data['callee'] == 'driver'
        assert req_data['caller_phone'] == '+79031524201'
        assert req_data['callee_phone'] == '+79031524200'
        assert req_data['external_ref_id'] == '<order_id>'
        assert len(req_data['nonce']) == 32
        assert req_data['consumer'] == 2
        assert req_data['call_location'] == [
            37.58917997300821,
            55.73341076871702,
        ]
        assert req_data['min_ttl'] == 3600
        assert req_data['new_ttl'] == 7200

        return {
            'expires_at': '2019-03-12T16:11:55+0300',
            'phone': '+75557775522',
            'ext': '007',
        }

    # DB preconditions
    assert db.order_talks.count() == 0
    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        'gateways': [
            {
                'gateway': {
                    'ext': '007',
                    'phone': '+75557775522',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
        ],
    }
    # Check database
    assert db.order_talks.count() == 0


@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.filldb(order_proc='vgw_api')
@pytest.mark.config(VGW_USE_VGW_API=True)
@pytest.mark.config(
    VGW_TOTW_DRIVER_VOICE_FORWARDING_TTL_SECONDS_MIN=3600,
    VGW_TOTW_DRIVER_VOICE_FORWARDING_TTL_SECONDS_NEW=7200,
)
def test_vgw_api_config(taxi_protocol, mockserver, db):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        req_data = json.loads(request.get_data())
        assert req_data['caller'] == 'passenger'
        assert req_data['callee'] == 'driver'
        assert req_data['caller_phone'] == '+79031524201'
        assert req_data['callee_phone'] == '+79031524200'
        assert req_data['external_ref_id'] == '<order_id>'
        assert len(req_data['nonce']) == 32
        assert req_data['consumer'] == 2
        assert req_data['call_location'] == [
            37.58917997300821,
            55.73341076871702,
        ]
        assert req_data['min_ttl'] == 3600
        assert req_data['new_ttl'] == 7200

        return {
            'expires_at': '2019-03-12T16:11:55+0300',
            'phone': '+75557775522',
            'ext': '007',
        }

    # DB preconditions
    assert db.order_talks.count() == 0
    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        'gateways': [
            {
                'gateway': {
                    'ext': '007',
                    'phone': '+75557775522',
                    'ttl_seconds': 2 * 60 * 60,
                },
            },
        ],
    }
    # Check database
    assert db.order_talks.count() == 0


@pytest.mark.filldb(order_proc='vgw_api_full')
@pytest.mark.parametrize(
    'order_id, tariff, user_id',
    [
        ('<order_id>', 'business', '<user_id>'),
        ('<order_id_2>', 'econom', '<user_id_2>'),
    ],
)
def test_vgw_api_send_service_level(
        taxi_protocol, mockserver, order_id, tariff, user_id, db,
):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        req_data = json.loads(request.get_data())

        service_level = req_data['service_level']
        assert tariff == service_level

        return {
            'expires_at': '2019-03-12T16:11:55+0300',
            'phone': '+75557775522',
            'ext': '007',
        }

    taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': order_id,
                    'caller': user_id,
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
