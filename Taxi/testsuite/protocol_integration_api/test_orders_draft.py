import json

import pytest


TEST_PHONE = '+79061112233'
TEST_PERSONAL_PHONE_ID = 'p00000000000000000000000'


CC_HEADERS = {'User-Agent': 'call_center'}


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


def sample_request_base():
    return {
        'dont_call': False,
        'dont_sms': False,
        'parks': [],
        'offer': 'offer_id',
        'payment': {'type': 'cash'},
        'requirements': {},
        'route': [
            {
                'country': 'Russian Federation',
                'description': 'Moscow, Russian Federation',
                'fullname': 'Russian Federation, Moscow, Okhotny Ryad Street',
                'geopoint': [37.616724, 55.757743],
                'locality': 'Moscow',
                'object_type': 'другое',
                'porchnumber': '',
                'premisenumber': '',
                'short_text': 'Okhotny Ryad Street',
                'short_text_from': 'Okhotny Ryad Street',
                'short_text_to': 'Okhotny Ryad Street',
                'thoroughfare': 'Okhotny Ryad Street',
                'type': 'address',
            },
            {
                'country': 'Russian Federation',
                'description': 'Moscow, Russian Federation',
                'fullname': 'Russian Federation, Moscow, Lva Tolstogo Street',
                'geopoint': [37.588144, 55.733842],
                'locality': 'Moscow',
                'object_type': 'другое',
                'porchnumber': '',
                'premisenumber': '',
                'short_text': 'Lva Tolstogo Street',
                'short_text_from': 'Lva Tolstogo Street',
                'short_text_to': 'Lva Tolstogo Street',
                'thoroughfare': 'Lva Tolstogo Street',
                'type': 'address',
            },
        ],
        'corpweb': False,
        'service_level': 50,
        'zone_name': 'moscow',
        'class': ['econom'],
        'chainid': 'chainid_1',
        'discount_card': '031',
    }


def default_simple_override():
    return {
        'id': 'user_callcenter',
        'callcenter': {
            'phone': TEST_PHONE,
            'personal_phone_id': TEST_PERSONAL_PHONE_ID,
        },
    }


def sample_request_simple(override=None):
    if override is None:
        override = default_simple_override()

    request = sample_request_base()
    request.update(override)
    return request


def sample_request_route():
    return {
        'dont_call': False,
        'dont_sms': False,
        'parks': [],
        'offer': 'offer_id',
        'requirements': {},
        'route': [
            {'place_id': 'pointa_uri', 'point': [37.616, 55.757]},
            {'place_id': 'pointb_uri', 'point': [37.588, 55.734]},
        ],
        'zone_name': 'moscow',
        'class': ['econom'],
        'chainid': 'chainid_1',
    }


def sample_request_placeid_route():
    request = sample_request_route()
    request.update(
        {
            'id': 'user_callcenter',
            'payment': {'type': 'cash'},
            'callcenter': {
                'phone': TEST_PHONE,
                'personal_phone_id': TEST_PERSONAL_PHONE_ID,
            },
        },
    )
    return request


@pytest.fixture(autouse=True)
def default_mock(mockserver, load_json):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def zones(request):
        return {}


@pytest.mark.parametrize(
    'callcenter_key, headers, userid, order_app, order_source',
    [
        (None, CC_HEADERS, 'user_callcenter', 'call_center', 'call_center'),
        ('corp_cabinet', {}, 'user_corpcabinet', 'corpweb', 'corp_cabinet'),
        ('alice', {}, 'user_alice', 'alice', 'alice'),
        ('svo_order', {}, 'user_svo', 'call_center', 'svo_order'),
    ],
)
def test_simple(
        taxi_integration,
        db,
        callcenter_key,
        headers,
        userid,
        order_app,
        order_source,
        get_order,
):
    request = sample_request_simple()
    request.pop('offer')
    request['id'] = userid
    if callcenter_key:
        request['callcenter']['key'] = callcenter_key
    if callcenter_key == 'corp_cabinet':
        request['corpweb'] = True
    elif callcenter_key == 'alice':
        request['yandex_uid'] = '4003514353'

    response = taxi_integration.post(
        'v1/orders/draft', json=request, headers=headers,
    )
    assert response.status_code == 200, response.text

    response_body = response.json()
    assert response_body is not None
    assert 'orderid' in response_body
    order_id = response_body['orderid']
    order = get_order(order_id)
    assert order is not None
    assert order['statistics']['application'] == order_app
    assert order['user_id'] == userid
    assert order['source'] == order_source


@pytest.mark.parametrize('user_had_choice', [True, False])
@pytest.mark.parametrize('user_chose_toll_road', [True, False])
@pytest.mark.parametrize('auto_payment', [True, False])
def test_order_with_toll_roads(
        taxi_integration,
        db,
        user_had_choice,
        user_chose_toll_road,
        auto_payment,
        get_order,
):
    request = sample_request_simple()
    toll_roads = {
        'user_had_choice': user_had_choice,
        'user_chose_toll_road': user_chose_toll_road,
        'auto_payment': auto_payment,
    }
    request['toll_roads'] = toll_roads
    response = taxi_integration.post(
        'v1/orders/draft', json=request, headers=CC_HEADERS,
    )
    assert response.status_code == 200, response.text
    response_body = response.json()
    assert response_body is not None
    assert 'orderid' in response_body
    order_id = response_body['orderid']
    order = get_order(order_id)
    assert 'toll_roads' in order['request']
    assert order['request']['toll_roads'] == toll_roads


def test_order_without_toll_roads(taxi_integration, get_order):
    request = sample_request_simple()
    response = taxi_integration.post(
        'v1/orders/draft', json=request, headers=CC_HEADERS,
    )
    assert response.status_code == 200, response.text
    response_body = response.json()
    assert response_body is not None
    assert 'orderid' in response_body
    order_id = response_body['orderid']
    order = get_order(order_id)
    assert 'request' in order
    assert 'toll_roads' not in order['request']


@pytest.mark.parametrize(
    'toll_roads',
    [{}, {'user_had_choice': False}, {'user_chose_toll_road': False}],
)
def test_order_incorrect_toll_roads(taxi_integration, toll_roads):
    request = sample_request_simple()
    request['toll_roads'] = toll_roads
    response = taxi_integration.post(
        'v1/orders/draft', json=request, headers=CC_HEADERS,
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'callback,code,error_msg',
    [
        (
            {
                'data': 'alice_callback',
                'notify_on': ['on_assigned', 'on_waiting'],
            },
            200,
            None,
        ),
        ({'data': 'alice_callback', 'notify_on': []}, 200, None),
        ({'data': 'alice_callback'}, 200, None),
        (
            {'data': 'alice_callback', 'notify_on': 5},
            400,
            {'error': {'text': 'invalid notify_on'}},
        ),
        ({'data': 5}, 400, {'error': {'text': 'invalid data'}}),
        ({'data': {'a': 5}}, 400, {'error': {'text': 'invalid data'}}),
    ],
)
def test_callback(taxi_integration, db, callback, code, error_msg, get_order):

    request = sample_request_simple()
    user_id = 'user_alice'
    request['id'] = user_id
    request['callcenter']['key'] = 'alice'
    request['yandex_uid'] = '4003514353'
    request['callback'] = callback

    response = taxi_integration.post('v1/orders/draft', json=request)
    assert response.status_code == code
    data = response.json()
    assert data is not None

    if response.status_code == 200:
        assert 'orderid' in data
        order_id = data['orderid']

        order = get_order(order_id)
        assert order is not None
        assert order['user_id'] == user_id
        assert order['callback'] == callback
    elif response.status_code == 400:
        assert data == error_msg
    else:
        assert False


@pytest.mark.parametrize(
    'update, headers, status_code, order_source, error_response',
    [
        pytest.param(
            {
                'id': 'user_callcenter',
                'callcenter': {
                    'phone': TEST_PHONE,
                    'personal_phone_id': TEST_PERSONAL_PHONE_ID,
                },
            },
            CC_HEADERS,
            200,
            'call_center',
            None,
            id='CallCenter Ok',
        ),
        pytest.param(
            {
                'id': 'unauthorized',
                'callcenter': {
                    'phone': TEST_PHONE,
                    'personal_phone_id': TEST_PERSONAL_PHONE_ID,
                },
            },
            CC_HEADERS,
            401,
            None,
            {'error': {'text': 'Unauthorized'}},
            id='User is not auhorized',
        ),
        pytest.param(
            {'id': 'user_callcenter', 'callcenter': {}},
            CC_HEADERS,
            400,
            None,
            {
                'error': {
                    'text': (
                        'either personal_phone_id or phone should be passed'
                    ),
                },
            },
            id='CallCenter no phone',
        ),
        pytest.param(
            {
                'id': 'user_corpcabinet',
                'callcenter': {
                    'key': 'corp_cabinet',
                    'phone': TEST_PHONE,
                    'personal_phone_id': TEST_PERSONAL_PHONE_ID,
                },
                'corpweb': True,
            },
            {},
            200,
            'corp_cabinet',
            None,
            id='Corp Ok',
        ),
        pytest.param(
            {
                'id': 'user_corpcabinet',
                'callcenter': {'key': 'corp_cabinet'},
                'corpweb': True,
            },
            {},
            400,
            None,
            {
                'error': {
                    'text': (
                        'either personal_phone_id or phone should be passed'
                    ),
                },
            },
            id='Corp no phone',
        ),
        pytest.param(
            {
                'id': 'user_alice',
                'callcenter': {
                    'key': 'alice',
                    'phone': TEST_PHONE,
                    'personal_phone_id': TEST_PERSONAL_PHONE_ID,
                },
                'yandex_uid': '4003514353',
            },
            {},
            200,
            'alice',
            None,
            id='Alice Ok',
        ),
        pytest.param(
            {
                'id': 'user_alice',
                'callcenter': {
                    'key': 'alice',
                    'phone': TEST_PHONE,
                    'personal_phone_id': TEST_PERSONAL_PHONE_ID,
                },
                'yandex_uid': '4003514353',
                'class': [
                    'express',
                ],  # should not be allowed in default fixture
            },
            {},
            400,
            None,
            {'error': {'text': 'class is not enabled for alice'}},
            id='Alice not supported class',
        ),
        pytest.param(
            {'id': 'user_cargo', 'cargo_ref_id': 'some_cargo_id'},
            {},
            200,
            'cargo',
            None,
            id='Cargo OK',
        ),
    ],
)
def test_input_errors(
        taxi_integration,
        db,
        update,
        headers,
        status_code,
        order_source,
        error_response,
        get_order,
):

    request = sample_request_base()
    request.update(update)

    response = taxi_integration.post(
        'v1/orders/draft', json=request, headers=headers,
    )
    assert response.status_code == status_code
    data = response.json()
    assert data is not None
    if response.status_code == 200:
        assert 'orderid' in data
        order_id = data['orderid']
        order = get_order(order_id)
        assert order is not None
        assert order['user_id'] == request['id']
        assert order['source'] == order_source
        if 'cargo_ref_id' in request:
            assert order['request']['cargo_ref_id'] == request['cargo_ref_id']
    else:
        assert data == error_response


@pytest.mark.parametrize(
    'callcenter_key,code',
    [
        ('corp_cabinet', 200),
        ('alice', 200),
        ('svo_order', 200),
        ('uber', 400),
        ('wrong', 400),
    ],
)
def test_callcenter_key(taxi_integration, db, callcenter_key, code):

    request = sample_request_simple()

    if callcenter_key == 'alice':
        user_id = 'user_alice'
        request.update({'yandex_uid': '4003514353'})
    else:
        user_id = 'user_callcenter'
        db.users.update(
            {'_id': user_id}, {'$set': {'sourceid': callcenter_key}},
        )

    request['id'] = user_id
    request['callcenter']['key'] = callcenter_key
    if callcenter_key == 'corp_cabinet':
        request['corpweb'] = True

    response = taxi_integration.post('v1/orders/draft', json=request)

    assert response.status_code == code, response
    data = response.json()

    if code == 200:
        assert data is not None
        assert 'orderid' in data
    elif code == 400:
        assert data == {'error': {'text': 'source_id invalid'}}
    else:
        assert False


@pytest.mark.config(
    INTEGRATION_SUPPORTED_APPLICATIONS=['alice'],
    APPLICATION_DETECTION_RULES_NEW={
        'rules': [
            {'match': 'alice', '@app_name': 'alice', '@app_ver1': '2'},
            {'@app_name': 'foolish', '@app_ver1': '2'},
        ],
    },
)
@pytest.mark.parametrize(
    'user_agent,code',
    [('alice', 200), ('siri', 400)],
    ids=['valid_app', 'invalid_app'],
)
def test_application(taxi_integration, user_agent, code, db):
    request = sample_request_simple()

    user_id = 'user_alice'
    db.users.update({'_id': user_id}, {'$set': {'sourceid': user_agent}})
    request['id'] = user_id
    request['yandex_uid'] = '4003514353'

    response = taxi_integration.post(
        'v1/orders/draft', json=request, headers={'User-Agent': user_agent},
    )

    assert response.status_code == code, response
    data = response.json()

    if code == 200:
        assert data is not None
        assert 'orderid' in data
    elif code == 400:
        assert data == {'error': {'text': 'Invalid application'}}
    else:
        assert False


def test_placeid_route(taxi_integration, yamaps, db, get_order):
    yamaps.location_add(
        [37.616, 55.757],
        {
            'description': 'description a',
            'text': 'point a',
            'short_text': 'short a',
            'full_text': 'full a',
        },
        lang='en',
        uri='pointa_uri',
    )
    yamaps.location_add(
        [37.588, 55.734],
        {
            'description': 'description b',
            'text': 'point b',
            'short_text': 'short b',
            'full_text': 'full b',
            'point': [10, 10],
        },
        lang='en',
        uri='pointb_uri',
    )

    response = taxi_integration.post(
        'v1/orders/draft',
        json=sample_request_placeid_route(),
        headers={'Accept-Language': 'en', 'User-Agent': 'call_center'},
    )
    assert response.status_code == 200, response.text

    response_body = response.json()
    assert response_body is not None
    assert 'orderid' in response_body
    order_id = response_body['orderid']
    order = get_order(order_id)
    assert order is not None
    assert order['statistics']['application'] == 'call_center'
    assert order['user_id'] == 'user_callcenter'
    assert order['source'] == 'call_center'
    assert order['request']['source'] == {
        'object_type': '\u0434\u0440\u0443\u0433\u043e\u0435',
        'description': 'description a',
        'thoroughfare': 'Point',
        'locality': 'Moscow',
        'country': 'Russia',
        'geopoint': [37.616, 55.757],
        'fullname': 'full a',
        'premisenumber': '1',
        'type': 'address',
        'short_text': 'short a',
    }
    assert order['request']['destinations'] == [
        {
            'object_type': '\u0434\u0440\u0443\u0433\u043e\u0435',
            'description': 'description b',
            'thoroughfare': 'Point',
            'locality': 'Moscow',
            'country': 'Russia',
            'geopoint': [37.588, 55.734],
            'fullname': 'full b',
            'premisenumber': '1',
            'type': 'address',
            'short_text': 'short b',
        },
    ]


@pytest.fixture()
def get_order(db):
    def getter(order_id):
        doc = db.order_proc.find_one({'_id': order_id})
        return doc['order']

    return getter


@pytest.mark.parametrize(
    'callcenter_data, expected_code, personal_times_called',
    [
        pytest.param({'phone': TEST_PHONE}, 200, 1, id='only_phone'),
        pytest.param(
            {'personal_phone_id': TEST_PERSONAL_PHONE_ID},
            200,
            0,
            id='only_personal_phone_id',
        ),
        pytest.param(
            {'phone': TEST_PHONE, 'personal_phone_id': TEST_PERSONAL_PHONE_ID},
            200,
            0,
            id='both',
        ),
        pytest.param({}, 400, 0, id='none'),
        pytest.param(
            {'phone': '+79039876543'}, 400, 1, id='phone_does_not_exist',
        ),
    ],
)
def test_personal(
        taxi_integration,
        mockserver,
        callcenter_data,
        expected_code,
        personal_times_called,
):
    """
    Test checks whether personal client should be called based on user_identity
    passed with request. If personal_phone_id is missing it should be retrieved
    via personal service.
    """

    @mockserver.json_handler('/personal/v1/phones/find')
    def mock_personal(request):
        request_json = json.loads(request.get_data())
        assert 'value' in request_json
        if request_json['value'] == TEST_PHONE:
            return {'id': TEST_PERSONAL_PHONE_ID, 'value': TEST_PHONE}
        else:
            return mockserver.make_response({}, 404)

    request = sample_request_simple(
        {'id': 'user_callcenter', 'callcenter': callcenter_data},
    )

    response = taxi_integration.post(
        'v1/orders/draft', json=request, headers=CC_HEADERS,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert mock_personal.times_called == personal_times_called


@pytest.mark.parametrize(
    'need_localize_cfg, payment_method_id, expect_refetched',
    (
        [True, 'test_method', False],
        [True, 'not_test_method', True],
        [False, 'not_test_method', False],
    ),
)
@pytest.mark.experiments3(filename='exp3_do_not_refetch_addresses.json')
def test_need_refetch_addresses(
        taxi_integration,
        db,
        get_order,
        taxi_config,
        need_localize_cfg,
        payment_method_id,
        expect_refetched,
):
    taxi_config.set_values({'LOCALIZE_BY_YAMAPS_ENABLED': need_localize_cfg})

    request = sample_request_simple()
    request.update(
        {
            'payment': {
                'type': 'card',
                'payment_method_id': payment_method_id,
            },
            'comment': 'some line\nsocial products\nanother line',
        },
    )
    TEST_SHORT_TEXT = 'test short text'
    request['route'][1]['short_text'] = TEST_SHORT_TEXT

    response = taxi_integration.post(
        'v1/orders/draft', json=request, headers=CC_HEADERS,
    )
    assert response.status_code == 200, response.text
    response_body = response.json()
    assert response_body is not None
    assert 'orderid' in response_body
    order_id = response_body['orderid']

    order = get_order(order_id)
    assert order is not None
    res_short_text = order['request']['destinations'][0]['short_text']
    if expect_refetched:
        assert res_short_text != TEST_SHORT_TEXT
    else:
        assert res_short_text == TEST_SHORT_TEXT


@pytest.mark.parametrize(
    'payment_method_id, dispatch_type, expected_source',
    (
        [
            'corp-7ff7900803534212a3a66f4d0e114fc2',
            'logistic-dispatcher',
            'cargo',
        ],
        ['corp-123', 'default', 'cargo'],
        ['corp-123', None, 'cargo'],
    ),
)
def test_new_dispatcher_replace_cargo_source(
        taxi_integration,
        get_order,
        payment_method_id,
        dispatch_type,
        expected_source,
):
    request = sample_request_simple()
    request.update(
        {
            'cargo_ref_id': 'some_cargo_id',
            'payment': {
                'type': 'corp',
                'payment_method_id': payment_method_id,
            },
            'comment': 'some line\nsocial products\nanother line',
        },
    )
    if dispatch_type:
        request['dispatch_type'] = dispatch_type

    response = taxi_integration.post(
        'v1/orders/draft', json=request, headers=CC_HEADERS,
    )
    assert response.status_code == 200
    response_body = response.json()
    assert response_body is not None
    assert 'orderid' in response_body
    order_id = response_body['orderid']

    order = get_order(order_id)
    assert order['source'] == expected_source


@pytest.mark.config(
    INTEGRATION_API_SOURCES_FOR_SAVING_CLIENT_APPLICATION_IN_PROC=['turboapp'],
    INTEGRATION_API_USE_APP_INSTEAD_OF_SOURCE_ID=['turboapp'],
)
def test_saving_application_in_proc(taxi_integration, db, get_order):
    request = sample_request_simple()
    request.pop('offer')
    request['id'] = 'without_source_id'
    request['callcenter']['key'] = 'turboapp'

    response = taxi_integration.post(
        'v1/orders/draft',
        json=request,
        headers={'User-Agent': 'app1-turboapp'},
    )
    assert response.status_code == 200
    response_body = response.json()
    assert response_body is not None
    assert 'orderid' in response_body
    order_id = response_body['orderid']

    order = get_order(order_id)
    assert order is not None
    assert order['statistics']['application'] == 'app1-turboapp'
    assert order['application'] == 'app1-turboapp'
    assert order['source'] == 'turboapp'


@pytest.mark.config(
    INTEGRATION_API_USE_APP_INSTEAD_OF_SOURCE_ID=['agent_007'],
    APPLICATION_DETECTION_RULES_NEW={'rules': [{'@app_name': 'agent_007'}]},
)
@pytest.mark.parametrize(
    'agent_application', ['callcenter', 'partner_application', None],
)
def test_orders_draft_agent(taxi_integration, get_order, agent_application):
    request = sample_request_base()
    user_id = 'agent_user'
    agent_obj = (
        {
            'agent_id': '007',
            'agent_user_type': 'individual',
            'agent_application': agent_application,
            'agent_order_id': 'agent_order_id_1',
        }
        if agent_application
        else {
            'agent_id': '007',
            'agent_user_type': 'individual',
            'agent_order_id': 'agent_order_id_1',
        }
    )
    request['id'] = user_id
    request['agent'] = agent_obj
    response = taxi_integration.post(
        'v1/orders/draft', json=request, headers={'User-Agent': 'agent_007'},
    )
    assert response.status_code == 200, response.text

    response_body = response.json()
    assert response_body is not None
    assert 'orderid' in response_body
    order_id = response_body['orderid']
    order = get_order(order_id)
    assert order['agent'] == agent_obj


@pytest.mark.config(
    INTEGRATION_API_USE_APP_INSTEAD_OF_SOURCE_ID=['agent_007'],
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
@pytest.mark.parametrize(
    'tvm_ticket, expected_code',
    [
        pytest.param(
            PARTNER_ORDERS_API_TVM_TICKET, 200, id='partner-orders-api',
        ),
        pytest.param(OTHER_SERVICE_TVM_TICKET, 406, id='other-service'),
    ],
)
def test_orders_draft_agent_not_acceptable(
        taxi_integration, tvm_ticket, expected_code,
):
    request = sample_request_base()
    user_id = 'agent_user'
    agent_obj = {
        'agent_id': '007',
        'agent_user_type': 'individual',
        'agent_order_id': 'agent_order_id_1',
    }
    request['id'] = user_id
    request['agent'] = agent_obj
    headers = {'User-Agent': 'agent_007'}

    headers['X-Ya-Service-Ticket'] = tvm_ticket
    response = taxi_integration.post(
        'v1/orders/draft', json=request, headers=headers,
    )
    assert response.status_code == expected_code


def test_virtual_tariffs(taxi_integration, get_order):
    virtual_tariffs = [
        {
            'class': 'econom',
            'special_requirements': [{'id': 'id1'}, {'id': 'id2'}],
        },
        {
            'class': 'express',
            'special_requirements': [{'id': 'id1'}, {'id': 'id2'}],
        },
    ]
    request = sample_request_simple()
    user_id = 'user_alice'
    request['id'] = user_id
    request['callcenter']['key'] = 'alice'
    request['yandex_uid'] = '4003514353'
    request['virtual_tariffs'] = virtual_tariffs
    response = taxi_integration.post('v1/orders/draft', json=request)
    assert response.status_code == 200, response.text

    response_body = response.json()
    assert response_body is not None
    assert 'orderid' in response_body
    order_id = response_body['orderid']
    order = get_order(order_id)
    assert order['virtual_tariffs'] == virtual_tariffs


@pytest.mark.config(
    INTEGRATION_API_USE_APP_INSTEAD_OF_SOURCE_ID=['agent_007'],
    APPLICATION_DETECTION_RULES_NEW={'rules': [{'@app_name': 'agent_007'}]},
)
@pytest.mark.parametrize(
    'agent_user_type,is_valid',
    [('individual', True), ('corporate', True), ('unsupported', False)],
)
def test_agent_order_user_type_check(
        taxi_integration, get_order, agent_user_type, is_valid,
):
    request = sample_request_base()
    user_id = 'agent_user'
    request['id'] = user_id
    request['agent'] = {
        'agent_user_type': agent_user_type,
        'agent_id': '007',
        'agent_order_id': 'agent_order_id_1',
    }
    response = taxi_integration.post(
        'v1/orders/draft', json=request, headers={'User-Agent': 'agent_007'},
    )

    if is_valid:
        assert response.status_code == 200
        r_json = response.json()
        assert 'orderid' in r_json
        order_id = r_json['orderid']
        order = get_order(order_id)
        assert order['agent']['agent_user_type'] == agent_user_type
    else:
        assert response.status_code == 400


@pytest.mark.experiments3(filename='exp3_is_cash_change_blocking_enabled.json')
def test_antifraud_events(taxi_integration, mockserver, load_json):
    class OrderIdHolder:
        id = None

    order_id_holder = OrderIdHolder()

    @mockserver.json_handler('/uantifraud/v1/events/order/draft')
    def mock_antifraud_events(request):
        data = request.json
        order_id_holder.id = data['order_id']
        assert data['user_id'] == 'user_callcenter'
        assert data['phone_id'] == '59246c5b6195542e9b084206'
        assert data['personal_phone_id'] == 'p00000000000000000000000'
        assert data['nz'] == 'moscow'
        assert 'yandex_uid' not in data
        assert 'device_id' not in data
        return {}

    request = sample_request_simple()
    response = taxi_integration.post(
        'v1/orders/draft', json=request, headers=CC_HEADERS,
    )
    mock_antifraud_events.wait_call()
    response_body = response.json()
    assert order_id_holder.id == response_body['orderid']


@pytest.mark.config(
    INTEGRATION_API_USE_APP_INSTEAD_OF_SOURCE_ID=['agent_007'],
    APPLICATION_DETECTION_RULES_NEW={'rules': [{'@app_name': 'agent_007'}]},
)
def test_agent_payment_method(taxi_integration, get_order):
    request = sample_request_base()
    request['id'] = 'agent_user'
    request['agent'] = {
        'agent_user_type': 'individual',
        'agent_id': '007',
        'agent_order_id': 'agent_order_id_1',
    }
    request['payment'] = {'type': 'agent', 'payment_method_id': 'agent_007'}
    response = taxi_integration.post(
        'v1/orders/draft', json=request, headers={'User-Agent': 'agent_007'},
    )
    assert response.status_code == 200
    r_json = response.json()
    assert 'orderid' in r_json
    order_id = r_json['orderid']
    order = get_order(order_id)
    if 'payment_tech' in order:
        assert order['payment_tech']['type'] == 'agent'
        assert order['payment_tech']['main_card_payment_id'] == 'agent_007'


def whitelabel_request(user_id, explicit_requirements, forced_fixprice):
    request = sample_request_simple()
    request['id'] = user_id
    request['callcenter']['key'] = 'turboapp'

    if explicit_requirements:
        request['white_label_requirements'] = {
            'source_park_id': 'park_id',
            'dispatch_requirement': 'only_source_park',
            'park_performer_compensation_fix': 10,
            'park_performer_compensation_percent': 10,
        }
        if forced_fixprice:
            request['white_label_requirements']['forced_fixprice'] = 100

    return request


@pytest.mark.parametrize(
    'order_origin, explicit_requirements, forced_fixprice, expected_code',
    [
        pytest.param(
            'unknown',
            True,
            False,
            400,
            id='unknown_order_explicit_requirements',
        ),
        pytest.param(
            'superweb',
            True,
            False,
            200,
            id='superweb_order_explicit_requirements',
        ),
        pytest.param(
            'superweb',
            True,
            True,
            200,
            id='superweb_order_explicit_requirements',
        ),
        pytest.param(
            'superweb',
            False,
            False,
            200,
            id='superweb_order_no_explicit_requirements',
        ),
        pytest.param(
            'turboapp',
            False,
            False,
            200,
            id='turboapp_order_no_explicit_requirements',
        ),
    ],
)
def test_whitelabel(
        taxi_integration,
        whitelabel_fixtures,
        get_order,
        order_origin,
        explicit_requirements,
        forced_fixprice,
        expected_code,
):
    user_id = f'whitelabel_{order_origin}_user_id'
    request = whitelabel_request(
        user_id,
        explicit_requirements=explicit_requirements,
        forced_fixprice=forced_fixprice,
    )

    path = 'v1/orders/draft'
    user_agent = (
        f'Mozilla/5.0 Chrome/89.0 whitelabel/{order_origin}/whitelabel_0'
    )

    response = taxi_integration.post(
        path, json=request, headers={'User-Agent': user_agent},
    )
    assert response.status_code == expected_code

    if expected_code != 200:
        return

    response_json = response.json()
    assert 'orderid' in response_json

    order_id = response_json['orderid']
    order = get_order(order_id)

    expected_white_label_requirements = {
        'source_park_id': 'park_id',
        'dispatch_requirement': 'only_source_park',
    }
    if explicit_requirements:
        expected_white_label_requirements = {
            **expected_white_label_requirements,
            'park_performer_compensation_fix': 10,
            'park_performer_compensation_percent': 10,
        }
    if forced_fixprice:
        expected_white_label_requirements['forced_fixprice'] = 100

    assert (
        order['request']['white_label_requirements']
        == expected_white_label_requirements
    )

    assert whitelabel_fixtures.mock_fleet_parks.times_called == (
        0 if explicit_requirements else 1
    )
