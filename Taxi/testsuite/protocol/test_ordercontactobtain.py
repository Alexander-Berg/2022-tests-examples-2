import json

import bson
import pytest

from replica_dbusers_switch_parametrize import (
    PROTOCOL_SWITCH_TO_REPLICA_DBUSERS,
)


@pytest.fixture
def mock_personal(mockserver):
    class PersonalDataContext:
        def __init__(self):
            self.phones_data = {}
            self.retrieve_use_count = 0

        def set_phones_data(self, phones_data):
            self.phones_data = phones_data

    context = PersonalDataContext()

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _phones_retrieve(request):
        pd_id = request.json['id']
        context.retrieve_use_count += 1
        if 'id_' in pd_id:
            return {'id': pd_id, 'value': pd_id.replace('id_', '')}
        else:
            if pd_id in context.phones_data:
                return context.phones_data[pd_id]
            else:
                return {}

    context.phones_retrieve = _phones_retrieve

    return context


@pytest.mark.filldb(order_proc='get_driver_phone')
@PROTOCOL_SWITCH_TO_REPLICA_DBUSERS
def test_ordercontactobtain_no_forwarding(
        taxi_protocol, mock_personal, testpoint, read_from_replica_dbusers,
):
    @testpoint('User::FetchBson')
    def replica_dbusers_test_point(data):
        assert read_from_replica_dbusers == data['replica']

    response = taxi_protocol.post(
        '3.0/ordercontactobtain',
        {
            'idempotency_token': 'token',
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'order_id': '8c83b49edb274ce0992f337061047375',
        },
    )

    assert response.status_code == 200
    content = response.json()
    assert content['gateway']['phone'] == '+79122999924'
    assert 'ext' not in content['gateway']

    assert mock_personal.retrieve_use_count == 1
    assert replica_dbusers_test_point.times_called == 1


@pytest.mark.parametrize(
    'source, key',
    [
        ('id', 'b300bda7d41b4bae8d58dfa93221ef16'),
        ('shared_route_id', '7071c41bba3407914e2b8db8fe3e5be4'),
    ],
)
@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.filldb(order_proc='get_forwarding')
@pytest.mark.config(VGW_USE_VGW_API=True)
def test_ordercontactobtain_forwarding(
        taxi_protocol, mockserver, source, key, mock_personal,
):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        req_data = json.loads(request.get_data())
        assert req_data['caller'] == 'passenger'
        assert req_data['callee'] == 'driver'
        assert req_data['caller_phone'] == '+79031520355'
        assert req_data['callee_phone'] == '+79122999924'
        assert (
            req_data['external_ref_id'] == '8c83b49edb274ce0992f337061047375'
        )
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

    response = taxi_protocol.post(
        '3.0/ordercontactobtain',
        {
            'idempotency_token': 'token',
            source: key,
            'order_id': '8c83b49edb274ce0992f337061047375',
        },
    )

    assert response.status_code == 200
    content = response.json()
    assert content['gateway']['phone'] == '+75557775522'
    assert content['gateway']['ext'] == '007'


@pytest.mark.filldb(order_proc='finished_orders')
@pytest.mark.config(ORDERS_HISTORY_SHOW_DRIVER_CONTACTS_HOURS=248)
def test_ordercontactobtain_finished_order(
        taxi_protocol, mockserver, mock_personal,
):
    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        req_data = json.loads(request.get_data())
        assert req_data['caller'] == 'passenger'
        assert req_data['callee'] == 'driver'
        assert req_data['caller_phone'] == '+79031520355'
        assert req_data['callee_phone'] == '+79122999924'
        assert (
            req_data['external_ref_id'] == '8c83b49edb274ce0992f337061047376'
        )
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

    response = taxi_protocol.post(
        '3.0/ordercontactobtain',
        {
            'idempotency_token': 'token',
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'order_id': '8c83b49edb274ce0992f337061047376',
        },
    )

    assert response.status_code == 200


@pytest.mark.filldb(order_proc='get_park_phone')
def test_ordercontactobtain_raw_driver_phone(
        taxi_protocol, mockserver, mock_personal,
):
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _mock_redirections(request):
        return mockserver.make_response(status=500)

    response = taxi_protocol.post(
        '3.0/ordercontactobtain',
        {
            'idempotency_token': 'token',
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'order_id': '8c83b49edb274ce0992f337061047375',
        },
    )

    assert response.status_code == 200
    content = response.json()
    assert content['gateway']['phone'] == '+79122999924'
    assert 'ext' not in content['gateway']


@pytest.mark.filldb(order_proc='get_park_phone')
@pytest.mark.config(
    HIDE_DRIVER_INFO={
        '__default__': {
            'car_number': False,
            'driver_phone': True,
            'fio': False,
            'park_phone': False,
        },
    },
)
def test_ordercontactobtain_park_phone(
        taxi_protocol, mockserver, mock_personal,
):
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _mock_redirections(request):
        return mockserver.make_response(status=500)

    mock_personal.set_phones_data(
        {
            '1fab75363700481a9adf5e31c3b6e673': {
                'id': '1fab75363700481a9adf5e31c3b6e673',
                'value': '+79321259615',
            },
        },
    )

    response = taxi_protocol.post(
        '3.0/ordercontactobtain',
        {
            'idempotency_token': 'token',
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'order_id': '8c83b49edb274ce0992f337061047375',
        },
    )

    assert response.status_code == 200
    content = response.json()
    assert content['gateway']['phone'] == '+79321259615'
    assert 'ext' not in content['gateway']


@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.filldb(order_proc='get_forwarding')
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
def test_ordercontactobtain_blacklisted_forwarding(
        taxi_protocol, mockserver, mock_personal,
):
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
        '3.0/ordercontactobtain',
        {
            'idempotency_token': 'token',
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'order_id': '8c83b49edb274ce0992f337061047375',
        },
    )

    assert response.status_code == 200
    content = response.json()
    assert content['gateway']['phone'] == '+74959999999'
    assert 'ext' not in content['gateway']


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
        '3.0/ordercontactobtain',
        {
            'idempotency_token': 'token',
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'order_id': '8c83b49edb274ce0992f337061047375',
        },
    )

    assert response.status_code == 200


@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.config(VGW_USE_VGW_API=True)
@pytest.mark.config(
    VGW_PROTOCOL_BLACKLISTED_SETTINGS={
        '__default__': False,
        'ordercontactobtain': True,
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
        '3.0/ordercontactobtain',
        {
            'idempotency_token': 'token',
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'order_id': '8c83b49edb274ce0992f337061047375',
        },
    )

    assert response.status_code == 200


@pytest.mark.filldb(order_proc='get_park_phone')
def test_ordercontactobtain_no_order(taxi_protocol, mockserver):
    @mockserver.json_handler('/order-archive/v1/order_proc/retrieve')
    def archive_api_handler(request):
        return mockserver.make_response(status=404)

    response = taxi_protocol.post(
        '3.0/ordercontactobtain',
        {
            'idempotency_token': 'token',
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'order_id': '8c83b49edb274ce0992f337061047376',
        },
    )

    assert response.status_code == 400
    content = response.json()
    assert content['error']['text'] == 'Order Not Found'


@pytest.mark.filldb(order_proc='bad_park_id')
@pytest.mark.config(
    HIDE_DRIVER_INFO={
        '__default__': {
            'car_number': False,
            'driver_phone': True,
            'fio': False,
            'park_phone': False,
        },
    },
)
def test_ordercontactobtain_bad_park_id(
        taxi_protocol, mockserver, mock_personal,
):
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
        '3.0/ordercontactobtain',
        {
            'idempotency_token': 'token',
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'order_id': '8c83b49edb274ce0992f337061047375',
        },
    )

    assert response.status_code == 504


@pytest.mark.filldb(order_proc='finished_orders')
@pytest.mark.config(ORDERCONTACTOBTAIN_VALID_ORDER_STATUS_SET=['driving'])
def test_ordercontactobtain_bad_state(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/ordercontactobtain',
        {
            'idempotency_token': 'token',
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'order_id': '8c83b49edb274ce0992f337061047375',
        },
    )

    assert response.status_code == 406
    content = response.json()
    assert content['error']['text'] == 'Bad Order State'


@pytest.mark.filldb(order_proc='finished_orders')
@pytest.mark.config(ORDERS_HISTORY_SHOW_DRIVER_CONTACTS_HOURS=1)
def test_ordercontactobtain_expired_order(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/ordercontactobtain',
        {
            'idempotency_token': 'token',
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'order_id': '8c83b49edb274ce0992f337061047375',
        },
    )

    assert response.status_code == 406
    content = response.json()
    assert content['error']['text'] == (
        'Finished order expired. ' 'Valid finished order hours = 1'
    )


@pytest.mark.config(
    SHARED_ROUTE_CALL_MODE_ALLOWED_CATEGORIES={
        'enabled': True,
        'allowed_categories': ['econom'],
    },
)
def test_ordercontactobtain_shared_route_allowed(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/ordercontactobtain',
        {
            'idempotency_token': 'token',
            'shared_route_id': '7071c41bba3407914e2b8db8fe3e5be4',
        },
    )

    assert response.status_code == 200


@pytest.mark.config(
    SHARED_ROUTE_CALL_MODE_ALLOWED_CATEGORIES={
        'enabled': True,
        'allowed_categories': ['something_wrong'],
    },
)
def test_ordercontactobtain_shared_route_forbidden(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/ordercontactobtain',
        {
            'idempotency_token': 'token',
            'shared_route_id': '7071c41bba3407914e2b8db8fe3e5be4',
        },
    )

    assert response.status_code == 403


@pytest.mark.config(
    SHARED_ROUTE_CALL_MODE_ALLOWED_CATEGORIES={
        'enabled': True,
        'allowed_categories': [],
    },
    SHARED_ROUTE_CALL_MODE_ALLOWED_APPLICATIONS=['iphone'],
)
def test_ordercontactobtain_shared_route_allowed_by_app(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/ordercontactobtain',
        {
            'idempotency_token': 'token',
            'shared_route_id': '7071c41bba3407914e2b8db8fe3e5be4',
        },
    )

    assert response.status_code == 200


@pytest.mark.config(
    SHARED_ROUTE_CALL_MODE_ALLOWED_CATEGORIES={
        'enabled': True,
        'allowed_categories': [],
    },
)
def test_ordercontactobtain_shared_route_allowed_for_other(taxi_protocol, db):
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            '$set': {
                'order.request.extra_user_phone_id': bson.ObjectId(
                    '5714f45e98956f06baaae3d5',
                ),
            },
        },
    )

    response = taxi_protocol.post(
        '3.0/ordercontactobtain',
        {
            'idempotency_token': 'token',
            'shared_route_id': '7071c41bba3407914e2b8db8fe3e5be4',
        },
    )

    assert response.status_code == 200
