import datetime
import json

import pytest

from taxi_tests import utils


def test_ordercommit_fraudcheck(taxi_protocol, mockserver, load, db, now):
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': '8c83b49edb274ce0992f337061047399',
    }
    headers = {'Cookie': 'yandexuid=invalid; fuid01=invalid'}
    response = taxi_protocol.post('3.0/ordercommit', request, headers=headers)
    assert response.status_code == 406
    json_response = response.json()
    assert json_response['error']['code'] == 'FRAUD_DETECTED'


def test_ordercommit_fraudcheck1(
        taxi_protocol, mockserver, load, db, now, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 1.1,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }

    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': '8c83b49edb274ce0992f337061047399',
    }
    headers = {
        'Cookie': 'yandexuid=0000000001498742336; fuid01=595abaef00000000',
    }
    response = taxi_protocol.post('3.0/ordercommit', request, headers=headers)
    assert response.status_code == 200


@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'retries': 1, 'timeout': 100},
        'order_commit': {'use_afs': True, 'retries': 1, 'timeout': 100},
    },
)
def test_ordercommit_spammer(taxi_protocol, mockserver, now):
    _ORDER_ID = '8c83b49edb274ce0992f337061047399'
    _USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 1.1,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }

    @mockserver.json_handler('/antifraud/client/user/is_spammer/order_commit')
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'is_multiorder': False,
            'user_id': _USER_ID,
            'user_phone_id': '5714f45e98956f06baaae3d4',
            'order_id': _ORDER_ID,
            'device_id': 'E4249906-EA48-4269-A8D1-D230572845ED',
        }
        blocked_until = now + datetime.timedelta(seconds=17)
        return {
            'is_spammer': True,
            'blocked_until': utils.timestring(blocked_until),
        }

    request = {'id': _USER_ID, 'orderid': _ORDER_ID}
    headers = {
        'Cookie': 'yandexuid=0000000001498742336; fuid01=595abaef00000000',
    }
    response = taxi_protocol.post('3.0/ordercommit', request, headers=headers)
    assert response.status_code == 403
    assert 'blocked' in response.json()


@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=False,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'retries': 1, 'timeout': 100},
        'order_commit': {'use_afs': True, 'retries': 1, 'timeout': 100},
    },
)
def test_ordercommit_is_spammer_disabled_in_client(
        taxi_protocol, mockserver, now, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    _ORDER_ID = '8c83b49edb274ce0992f337061047399'
    _USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 1.1,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }

    @mockserver.json_handler('/antifraud/client/user/is_spammer/order_commit')
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'is_multiorder': False,
            'user_id': _USER_ID,
            'user_phone_id': '5714f45e98956f06baaae3d4',
            'order_id': _ORDER_ID,
            'device_id': 'E4249906-EA48-4269-A8D1-D230572845ED',
        }
        blocked_until = now + datetime.timedelta(seconds=17)
        return {
            'is_spammer': True,
            'blocked_until': utils.timestring(blocked_until),
        }

    request = {'id': _USER_ID, 'orderid': _ORDER_ID}
    headers = {
        'Cookie': 'yandexuid=0000000001498742336; fuid01=595abaef00000000',
    }
    response = taxi_protocol.post('3.0/ordercommit', request, headers=headers)
    assert response.status_code == 200


@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'retries': 1, 'timeout': 100},
        'order_commit': {'use_afs': True, 'retries': 1, 'timeout': 100},
    },
)
def test_ordercommit_not_spammer(
        taxi_protocol, mockserver, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    _ORDER_ID = '8c83b49edb274ce0992f337061047399'
    _USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 1.1,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }

    @mockserver.json_handler('/antifraud/client/user/is_spammer/order_commit')
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'is_multiorder': False,
            'user_id': _USER_ID,
            'user_phone_id': '5714f45e98956f06baaae3d4',
            'order_id': _ORDER_ID,
            'device_id': 'E4249906-EA48-4269-A8D1-D230572845ED',
        }
        return {'is_spammer': False}

    request = {'id': _USER_ID, 'orderid': _ORDER_ID}
    headers = {
        'Cookie': 'yandexuid=0000000001498742336; fuid01=595abaef00000000',
    }
    response = taxi_protocol.post('3.0/ordercommit', request, headers=headers)
    assert response.status_code == 200


@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'retries': 1, 'timeout': 100},
        'order_commit': {'use_afs': True, 'retries': 1, 'timeout': 100},
    },
)
@pytest.mark.parametrize('response_code', [500, 400, 403])
def test_ordercommit_is_spammer_affected(
        taxi_protocol, mockserver, response_code, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    _ORDER_ID = '8c83b49edb274ce0992f337061047399'
    _USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 1.1,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }

    @mockserver.json_handler('/antifraud/client/user/is_spammer/order_commit')
    def mock_afs_is_spammer_invalid(request):
        return mockserver.make_response(
            '{"code":' + str(response_code) + '}', response_code,
        )

    request = {'id': _USER_ID, 'orderid': _ORDER_ID}
    headers = {
        'Cookie': 'yandexuid=0000000001498742336; fuid01=595abaef00000000',
    }
    response = taxi_protocol.post('3.0/ordercommit', request, headers=headers)
    assert response.status_code == 200


NOW_TIMESTAMP = 1539360300


@pytest.mark.now(NOW_TIMESTAMP)
@pytest.mark.config(AFS_USER_CHECK_CAN_MAKE_ORDER=True)
def test_ordercommit_afs_can_make_order(
        taxi_protocol, mockserver, mock_solomon,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 1.1,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }

    _ORDER_ID = '8c83b49edb274ce0992f337061047399'
    _USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'

    @mockserver.json_handler('/antifraud/client/user/can_make_order')
    def mock_afs(request):
        data = json.loads(request.get_data())
        assert data == {
            'user_id': _USER_ID,
            'user_phone_id': '5714f45e98956f06baaae3d4',
            'order_id': _ORDER_ID,
            'initial_payment_type': 'cash',
            'application': '',
        }
        return {'can_make_order': False}

    mock_solomon.reset()
    mock_solomon.set_ordered(False)
    mock_solomon.add(
        [
            {
                'kind': 'IGAUGE',
                'labels': {'reason': 'antifraud', 'sensor': 'order_429'},
                'timeseries': [{'ts': NOW_TIMESTAMP, 'value': 1.0}],
            },
        ],
    )

    request = {'id': _USER_ID, 'orderid': _ORDER_ID}
    headers = {
        'Cookie': 'yandexuid=0000000001498742336; fuid01=595abaef00000000',
    }
    response = taxi_protocol.post('3.0/ordercommit', request, headers=headers)
    assert response.status_code == 429

    mock_solomon.wait_for()
