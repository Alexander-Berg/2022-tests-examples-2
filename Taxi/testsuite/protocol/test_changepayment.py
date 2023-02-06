import json

import dateutil.parser
import pytest

from notify_on_change_version_switch import NOTIFY_ON_CHANGE_VERSION_SWITCH
from validate_stq_task import validate_notify_on_change_stq_task
from validate_stq_task import validate_process_change_stq_task
from validate_stq_task import validate_process_update_stq_task


API_OVER_DATA_WORK_MODE = {
    '__default__': {'__default__': 'oldway'},
    'parks-activation-client': {'protocol': 'newway'},
}


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
        (
            '8c83b49edb274ce0992f337061047377',
            200,
            None,
            'yandex_card',
            'yandex_card_id',
        ),
        ('d41d8cd98f004204a9800998ecf84eed', 200, None, 'card', 'card-x1234'),
    ],
)
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_return_code(
        orderid,
        code,
        error_text,
        method_type,
        method_id,
        taxi_protocol,
        notify_on_change_version_switch,
):
    created_time = dateutil.parser.parse('2017-07-19T13:16:04Z')
    body = {
        'orderid': orderid,
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'created_time': created_time.isoformat(),
        'payment_method_id': method_id,
        'payment_method_type': method_type,
        'tips': {'type': 'percent', 'value': 15},
    }
    response = taxi_protocol.post('3.0/changepayment', json=body)
    assert response.status_code == code
    if code != 500:
        data = response.json()
        if error_text:
            assert data['error']['text'] == error_text


@pytest.mark.now('2017-07-19T17:15:15+0000')
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_empty_change_payment(
        taxi_protocol, mockserver, db, now, notify_on_change_version_switch,
):
    created_time = dateutil.parser.parse('2017-07-19T17:15:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': '8c83b49edb274ce0992f337061047375',
        'created_time': created_time.isoformat(),
        'payment_method_id': 'card-2311',
    }
    query = {'_id': request['orderid']}
    proc = db.order_proc.find_one(query)
    assert proc is not None
    version = proc['order']['version']
    assert 'changes' not in proc
    assert now > proc['updated']
    response = taxi_protocol.post('3.0/changepayment', request)
    assert response.status_code == 200
    data = response.json()
    assert data == {
        'change_id': data['change_id'],
        'status': 'pending',
        'name': 'payment',
        'value': 'card-2311',
    }
    order_proc = db.order_proc.find_one(query)
    assert order_proc['processing']['need_start'] is False
    assert order_proc['order_info']['need_sync'] is False
    assert order_proc['order']['version'] == version + 1
    changes = order_proc['changes']['objects']
    assert len(changes) == 2
    assert changes == [
        {
            'id': changes[0]['id'],
            'vl': 'cash',
            's': 'applied',
            'ci': request['id'],
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
            'ci': request['id'],
            'n': 'payment',
            'vr': version + 1,
            'c': now.replace(tzinfo=None, microsecond=0),
            't': created_time.replace(tzinfo=None, microsecond=0),
        },
    ]


@pytest.mark.filldb(users='crossdevice')
@pytest.mark.now('2017-07-19T17:15:15+0000')
@pytest.mark.parametrize('crossdevice_user_first', [True, False])
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_crossdevice(
        taxi_protocol,
        mockserver,
        db,
        now,
        crossdevice_user_first,
        notify_on_change_version_switch,
):
    """
    Ensure other user can change payment, and that second can "see" that change
    is in progress
    """
    user_id = 'b300bda7d41b4bae8d58dfa93221ef16'
    crossdevice_user_id = 'crossdeviceuser00000000000000000'
    card_id = 'card-2311'
    orderid = '8c83b49edb274ce0992f337061047376'
    created_time = dateutil.parser.parse('2017-07-19T17:15:20+0000')
    request = {
        'orderid': orderid,
        'created_time': created_time.isoformat(),
        'payment_method_id': card_id,
    }
    sequence = [user_id, crossdevice_user_id]
    responses = []
    if crossdevice_user_first:
        sequence = reversed(sequence)
    for user_id in sequence:
        request['id'] = user_id
        responses.append(taxi_protocol.post('3.0/changepayment', request))
    first_resp, second_resp = responses
    assert first_resp.status_code == 200, first_resp.json()
    change_json = first_resp.json()
    change_json.pop('change_id')
    assert change_json == {
        'status': 'pending',
        'name': 'payment',
        'value': card_id,
    }
    assert second_resp.status_code == 406
    assert second_resp.json() == {
        'error': {'text': 'payment_change_is_in_progress'},
    }


@pytest.mark.parametrize(
    'orderid, card_id, changes_expected, use_order_core',
    [
        ('8c83b49edb274ce0992f337061047376', 'card-2311', 3, True),
        ('d41d8cd98f004204a9800998ecf8427e', 'card-0921', 2, False),
    ],
)
@pytest.mark.now('2017-07-19T17:15:15+0000')
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_change_payment(
        taxi_protocol,
        mockserver,
        db,
        now,
        orderid,
        card_id,
        changes_expected,
        config,
        use_order_core,
        mock_order_core,
        mock_stq_agent,
        notify_on_change_version_switch,
):
    if use_order_core:
        config.set_values(
            dict(PROCESSING_BACKEND_CPP_SWITCH=['changepayment']),
        )

    created_time = dateutil.parser.parse('2017-07-19T17:15:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': orderid,
        'created_time': created_time.isoformat(),
        'payment_method_id': card_id,
    }
    query = {'_id': request['orderid']}
    proc = db.order_proc.find_one(query)
    version = proc['order']['version']
    assert proc is not None
    assert now > proc['updated']
    response = taxi_protocol.post('3.0/changepayment', request)
    assert response.status_code == 200
    data = response.json()
    assert data == {
        'change_id': data['change_id'],
        'status': 'pending',
        'name': 'payment',
        'value': card_id,
    }
    order_proc = db.order_proc.find_one(query)
    assert order_proc['processing']['need_start'] is False
    assert order_proc['order_info']['need_sync'] is False
    validate_process_change_stq_task(
        mock_stq_agent, request['orderid'], 'payment',
    )

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
        'ci': request['id'],
        'n': 'payment',
        'vr': version + 1,
        'c': now.replace(tzinfo=None, microsecond=0),
        't': created_time.replace(tzinfo=None, microsecond=0),
    }
    assert mock_order_core.post_event_times_called == 0

    args = [mock_stq_agent, request['orderid'], 'destinations']
    validate_process_update_stq_task(*args, exists=False)
    validate_notify_on_change_stq_task(*args, exists=False)


@pytest.mark.parks_activation(
    [
        {
            'park_id': '999011',
            'city_id': 'Москва',
            'revision': 1,
            'last_modified': '1970-01-15T03:56:07.000',
            'data': {
                'deactivated': False,
                'can_cash': True,
                'can_card': True,
                'can_coupon': True,
                'can_corp': True,
            },
        },
    ],
)
@pytest.mark.parametrize(
    'orderid, card_id, changes_expected',
    [
        ('8c83b49edb274ce0992f337061047376', 'card-2311', 3),
        ('d41d8cd98f004204a9800998ecf8427e', 'card-0921', 2),
    ],
)
@pytest.mark.now('2017-07-19T17:15:15+0000')
@pytest.mark.config(API_OVER_DATA_WORK_MODE=API_OVER_DATA_WORK_MODE)
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_change_payment_park_activation(
        taxi_protocol,
        db,
        now,
        orderid,
        card_id,
        changes_expected,
        notify_on_change_version_switch,
):
    created_time = dateutil.parser.parse('2017-07-19T17:15:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': orderid,
        'created_time': created_time.isoformat(),
        'payment_method_id': card_id,
    }
    query = {'_id': request['orderid']}
    proc = db.order_proc.find_one(query)
    version = proc['order']['version']
    assert proc is not None
    assert now > proc['updated']
    response = taxi_protocol.post('3.0/changepayment', request)
    assert response.status_code == 200
    data = response.json()
    assert data == {
        'change_id': data['change_id'],
        'status': 'pending',
        'name': 'payment',
        'value': card_id,
    }
    order_proc = db.order_proc.find_one(query)
    assert order_proc['processing']['need_start'] is False
    assert order_proc['order_info']['need_sync'] is False
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
        'ci': request['id'],
        'n': 'payment',
        'vr': version + 1,
        'c': now.replace(tzinfo=None, microsecond=0),
        't': created_time.replace(tzinfo=None, microsecond=0),
    }


@pytest.mark.parks_activation(
    [
        {
            'park_id': '999011',
            'city_id': 'Москва',
            'revision': 1,
            'last_modified': '1970-01-15T03:56:07.000',
            'data': {
                'deactivated': False,
                'can_cash': True,
                'can_card': False,
                'can_coupon': True,
                'can_corp': True,
            },
        },
    ],
)
@pytest.mark.parametrize(
    'orderid, card_id, changes_expected',
    [
        ('8c83b49edb274ce0992f337061047376', 'card-2311', 3),
        ('d41d8cd98f004204a9800998ecf8427e', 'card-0921', 2),
    ],
)
@pytest.mark.now('2017-07-19T17:15:15+0000')
@pytest.mark.config(API_OVER_DATA_WORK_MODE=API_OVER_DATA_WORK_MODE)
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_change_payment_park_activation_cant_card(
        taxi_protocol,
        orderid,
        card_id,
        changes_expected,
        notify_on_change_version_switch,
):
    created_time = dateutil.parser.parse('2017-07-19T17:15:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': orderid,
        'created_time': created_time.isoformat(),
        'payment_method_id': card_id,
    }

    response = taxi_protocol.post('3.0/changepayment', request)
    assert response.status_code == 406
    data = response.json()
    assert data == {'error': {'text': 'park_doesnt_accept_cards'}}


@pytest.mark.parametrize(
    'orderid, card_id, changes_expected',
    [
        ('8c83b49edb274ce0992f337061047376', 'card-2311', 3),
        ('d41d8cd98f004204a9800998ecf8427e', 'card-0921', 2),
    ],
)
@pytest.mark.now('2017-07-19T17:15:15+0000')
@pytest.mark.config(API_OVER_DATA_WORK_MODE=API_OVER_DATA_WORK_MODE)
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_change_payment_park_activation_no_park_activation(
        taxi_protocol,
        orderid,
        card_id,
        changes_expected,
        notify_on_change_version_switch,
):
    created_time = dateutil.parser.parse('2017-07-19T17:15:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': orderid,
        'created_time': created_time.isoformat(),
        'payment_method_id': card_id,
    }

    response = taxi_protocol.post('3.0/changepayment', request)
    assert response.status_code == 406
    data = response.json()
    assert data == {'error': {'text': 'unknown_park_id'}}


@pytest.mark.config(ALLOW_CHANGE_TO_CASH_IF_UNSUCCESSFUL_PAYMENT=True)
@pytest.mark.now('2017-07-19T17:15:15+0000')
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_change_payment_to_cash(
        taxi_protocol, db, now, notify_on_change_version_switch,
):
    orderid = 'd41d8cd98f004204a9800998ecf8427e'
    created_time = dateutil.parser.parse('2017-07-19T17:15:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': orderid,
        'created_time': created_time.isoformat(),
        'payment_method_type': 'cash',
    }

    response = taxi_protocol.post('3.0/changepayment', request)
    assert response.status_code == 406

    query = {'_id': request['orderid']}
    db.orders.update(
        query, {'$set': {'payment_tech.unsuccessful_payment': True}},
    )
    response = taxi_protocol.post('3.0/changepayment', request)
    assert response.status_code == 200


@pytest.mark.now('2017-07-19T17:15:15+0000')
@pytest.mark.parametrize(
    'tips,expected_code,expected_tips',
    [
        (
            {'type': 'percent', 'value': 0},
            200,
            {'type': 'percent', 'value': 0},
        ),
        (
            {'type': 'percent', 'decimal_value': '0'},
            200,
            {'type': 'percent', 'value': 0},
        ),
        ({'type': 'flat', 'value': 0}, 200, {'type': 'flat', 'value': 0}),
        (
            {'type': 'flat', 'decimal_value': '0'},
            200,
            {'type': 'flat', 'value': 0},
        ),
        ({'type': 'percent', 'value': 150}, 400, None),
        ({'type': 'percent', 'decimal_value': '150'}, 400, None),
        (
            {'type': 'flat', 'value': 150.23},
            200,
            {'type': 'flat', 'value': 150.23},
        ),
        (
            {'type': 'flat', 'decimal_value': '150.23'},
            200,
            {'type': 'flat', 'value': 150.23},
        ),
        ({'type': 'flat', 'decimal_value': '!!!'}, 400, None),
    ],
)
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_change_payment_tips(
        taxi_protocol,
        mockserver,
        db,
        now,
        tips,
        expected_code,
        expected_tips,
        notify_on_change_version_switch,
):
    created_time = dateutil.parser.parse('2017-07-19T17:15:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': '8c83b49edb274ce0992f337061047376',
        'created_time': created_time.isoformat(),
        'payment_method_id': 'card-2311',
        'tips': tips,
    }

    response = taxi_protocol.post('3.0/changepayment', request)
    assert response.status_code == expected_code

    if expected_code == 200:
        proc = db.order_proc.find_one({'_id': request['orderid']})
        assert proc['changes']['objects'][-1]['vl']['tips'] == expected_tips


@pytest.mark.filldb(users='cardantifraud')
@pytest.mark.experiments3(filename='use_card_antifraud.json')
@pytest.mark.parametrize(
    'ca_code,all_payments_available,available_cards,expected_code',
    [
        (200, True, [], 200),
        (200, False, [{'card_id': 'card-2311'}], 200),
        (200, False, [], 406),
        (500, False, [], 200),
    ],
    ids=[
        'device_verified',
        'card_in_verified_cards',
        'empty_verified_cards',
        'card_antifraud_unavailable',
    ],
)
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_card_antifraud_different_states(
        mockserver,
        taxi_protocol,
        ca_code,
        all_payments_available,
        available_cards,
        expected_code,
        notify_on_change_version_switch,
):
    order_id = '8c83b49edb274ce0992f337061047377'
    method_id = 'card-2311'

    @mockserver.json_handler('/card_antifraud/v1/payment/availability')
    def _mock_ca_payment_availability(request):
        assert request.args.to_dict() == {
            'user_id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'card_id': method_id,
            'yandex_uid': '4003514353',
        }
        response = {
            'all_payments_available': all_payments_available,
            'available_cards': available_cards,
        }
        return mockserver.make_response(
            json.dumps(response) if ca_code == 200 else '', ca_code,
        )

    created_time = dateutil.parser.parse('2017-07-19T13:16:04Z')
    body = {
        'orderid': order_id,
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'created_time': created_time.isoformat(),
        'payment_method_id': method_id,
        'payment_method_type': 'card',
    }

    response = taxi_protocol.post('3.0/changepayment', json=body)

    assert response.status_code == expected_code
    if expected_code == 406:
        assert response.json() == {'error': {'text': 'need_card_antifraud'}}


@pytest.mark.filldb(users='cardantifraud')
@pytest.mark.parametrize(
    'user_agent,expected_code',
    [
        (
            'ru.yandex.taxi.inhouse/3.0.0 '
            '(iPhone; iPhone7,1; iOS 10.1.1; Darwin)',
            406,
        ),
        ('yandex-taxi/3.0.0 Android/7.0 (android test client)', 406),
        (
            'ru.yandex.taxi.inhouse/35.0.0 '
            '(iPhone; iPhone7,1; iOS 10.1.1; Darwin)',
            200,
        ),
        ('yandex-taxi/35.0.0 Android/7.0 (android test client)', 200),
    ],
    ids=[
        'iphone_match',
        'android_match',
        'iphone_mismatch',
        'android_mismatch',
    ],
)
@pytest.mark.experiments3(filename='use_card_antifraud.json')
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_app_version_experiment(
        taxi_protocol,
        mockserver,
        user_agent,
        expected_code,
        notify_on_change_version_switch,
):
    order_id = '8c83b49edb274ce0992f337061047377'
    method_id = 'card-2311'

    @mockserver.json_handler('/card_antifraud/v1/payment/availability')
    def _mock_ca_payment_availability(request):
        assert request.args.to_dict() == {
            'user_id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'card_id': method_id,
            'yandex_uid': '4003514353',
        }
        response = {'all_payments_available': False, 'available_cards': []}
        return mockserver.make_response(json.dumps(response), 200)

    headers = {'User-Agent': user_agent}
    created_time = dateutil.parser.parse('2017-07-19T13:16:04Z')
    body = {
        'orderid': order_id,
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'created_time': created_time.isoformat(),
        'payment_method_id': method_id,
        'payment_method_type': 'card',
    }

    response = taxi_protocol.post(
        '3.0/changepayment', json=body, headers=headers,
    )

    assert response.status_code == expected_code


@pytest.mark.filldb(users='cardantifraud')
@pytest.mark.experiments3(filename='use_card_antifraud.json')
@pytest.mark.parametrize('yandex_uid_type', ['phonish', None])
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_card_antifraud_not_portal(
        taxi_protocol, db, yandex_uid_type, notify_on_change_version_switch,
):
    order_id = '8c83b49edb274ce0992f337061047377'
    user_id = 'b300bda7d41b4bae8d58dfa93221ef16'
    created_time = dateutil.parser.parse('2017-07-19T13:16:04Z')
    if yandex_uid_type is None:
        query = {'$unset': {'yandex_uid_type': ''}}
    else:
        query = {'$set': {'yandex_uid_type': yandex_uid_type}}
    db.users.update({'_id': user_id}, query)
    body = {
        'orderid': order_id,
        'id': user_id,
        'created_time': created_time.isoformat(),
        'payment_method_id': 'card-2311',
        'payment_method_type': 'card',
    }

    response = taxi_protocol.post('3.0/changepayment', json=body)

    assert response.status_code == 200


@pytest.mark.config(ALLOW_CHANGE_TO_CASH_IF_UNSUCCESSFUL_PAYMENT=True)
@pytest.mark.experiments3(filename='use_card_antifraud.json')
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_card_antifraud_not_card(
        taxi_protocol, db, notify_on_change_version_switch,
):
    order_id = 'd41d8cd98f004204a9800998ecf8427e'
    user_id = 'b300bda7d41b4bae8d58dfa93221ef16'
    created_time = dateutil.parser.parse('2017-07-19T13:16:04Z')
    body = {
        'orderid': order_id,
        'id': user_id,
        'created_time': created_time.isoformat(),
        'payment_method_type': 'cash',
    }
    db.orders.update(
        {'_id': order_id},
        {'$set': {'payment_tech.unsuccessful_payment': True}},
    )

    response = taxi_protocol.post('3.0/changepayment', json=body)

    assert response.status_code == 200


@pytest.mark.filldb(users='cardantifraud')
@pytest.mark.experiments3(filename='use_card_antifraud.json')
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_card_antifraud_login_id(
        mockserver, taxi_protocol, notify_on_change_version_switch,
):
    order_id = '8c83b49edb274ce0992f337061047377'
    method_id = 'card-2311'

    @mockserver.json_handler('/card_antifraud/v1/payment/availability')
    def mock_ca_payment_availability(request):
        assert request.args.to_dict() == {
            'user_id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'card_id': method_id,
            'yandex_uid': '4003514353',
            'yandex_login_id': 't:1234',
        }
        response = {'all_payments_available': True, 'available_cards': []}
        return response

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        query = set(request.query_string.decode().split('&'))
        assert 'get_login_id=yes' in query
        return {
            'uid': {'value': '4003514353'},
            'status': {'value': 'VALID'},
            'login_id': 't:1234',
            'oauth': {'scope': 'yataxi:read yataxi:write yataxi:pay'},
            'phones': [
                {'attributes': {'102': '+71111111111'}, 'id': '1111'},
                {
                    'attributes': {'102': '+72222222222', '107': '1'},
                    'id': '2222',
                },
            ],
        }

    created_time = dateutil.parser.parse('2017-07-19T13:16:04Z')
    body = {
        'orderid': order_id,
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'created_time': created_time.isoformat(),
        'payment_method_id': method_id,
        'payment_method_type': 'card',
    }

    response = taxi_protocol.post(
        '3.0/changepayment',
        json=body,
        bearer='test_token',
        x_real_ip='my-ip-address',
    )

    assert response.status_code == 200
    assert mock_ca_payment_availability.has_calls is True
    assert mock_blackbox.has_calls is True


@pytest.mark.config(CHANGEPAYMENT_CHECK_PAYMENT_BY_ZONE=True)
@pytest.mark.parametrize(
    'nearest_zone,required_payment_type,expected_status,error_text',
    (
        ('moscow', 'googlepay', 200, None),
        ('moscow', 'applepay', 200, None),
        ('almaty', 'googlepay', 406, 'google_pay_not_available'),
        ('almaty', 'applepay', 406, 'apple_pay_not_available'),
    ),
)
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_check_applepay_googlepay(
        db,
        taxi_protocol,
        nearest_zone,
        required_payment_type,
        expected_status,
        error_text,
        notify_on_change_version_switch,
):
    # There are applepay and googlepay in moscow tariff_settings
    # There are not applepay and googlepay in almaty tariff_settings
    db.order_proc.update_one(
        {'_id': '8c83b49edb274ce0992f337061047377'},
        {'$set': {'order.nz': nearest_zone}},
    )
    created_time = dateutil.parser.parse('2017-07-19T13:16:04Z')
    body = {
        'orderid': '8c83b49edb274ce0992f337061047377',
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'created_time': created_time.isoformat(),
        'payment_method_id': 'some_id',
        'payment_method_type': required_payment_type,
    }
    response = taxi_protocol.post('3.0/changepayment', json=body)
    assert response.status_code == expected_status
    if expected_status != 200:
        data = response.json()
        if error_text:
            assert data['error']['text'] == error_text


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
        taxi_protocol,
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

    created_time = dateutil.parser.parse('2017-07-19T13:16:04Z')
    body = {
        'orderid': order_id,
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'created_time': created_time.isoformat(),
        'payment_method_id': 'some_id',
        'payment_method_type': 'card',
    }
    response = taxi_protocol.post('3.0/changepayment', json=body)
    assert response.status_code == expected_status
    antifraud_call_holder.check_calls(call_count, order_id)
    if expected_status != 200:
        data = response.json()
        assert (
            data['error']['text'] == 'Block change payment method by antifraud'
        )


@pytest.mark.parametrize(
    'method_type, method_id, is_ok',
    [
        ('yandex_card', 'corp-garbage', False),
        ('yandex_card', 'card-x1234123', True),
        ('yandex_card', None, False),
        ('googlepay', None, True),
        ('applepay', 'apple_token-', False),
        ('applepay', 'apple_token-TOKEN_VAL', True),
    ],
)
@pytest.mark.config(
    PAYMENT_METHODS_REGEXPS={
        'yandex_card': '^card-.+$',
        'applepay': '^apple_token-.+$',
    },
)
def test_invalid_payment_method_id(
        taxi_protocol, db, method_type, method_id, is_ok,
):
    order_id = '8c83b49edb274ce0992f337061047377'
    db.orders.update_one(
        {'_id': order_id}, {'$set': {'payment_tech.type': 'cash'}},
    )

    created_time = dateutil.parser.parse('2017-07-19T13:16:04Z')
    body = {
        'orderid': '8c83b49edb274ce0992f337061047377',
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'created_time': created_time.isoformat(),
        'payment_method_type': method_type,
    }
    if method_id:
        body['payment_method_id'] = method_id
    response = taxi_protocol.post('3.0/changepayment', json=body)
    if is_ok:
        assert response.status_code == 200
    else:
        assert response.status_code == 400
