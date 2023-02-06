import base64
import datetime
import hashlib
import hmac
import json

from dateutil.tz import tzlocal
import pytest
import pytz

from taxi_tests import utils

from individual_tariffs_switch_parametrize import (
    PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS,
)
from order_core_exp_parametrize import CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
from protocol.order.order_draft_common import _ORDER_DRAFT_PATH
from protocol.order.order_draft_common import orderdraft


def _check_user_phone(expected_phone, db, phone_id):
    object = db.user_phones.find_one({'_id': phone_id})
    assert isinstance(object, dict)
    number = object['phone']
    assert number == expected_phone


def test_order_draft_bad_request(taxi_protocol):
    response = taxi_protocol.post(_ORDER_DRAFT_PATH, {})
    assert response.status_code == 400


def get_proc_collection(db, order_id):
    proc = db.order_proc.find_one(
        {'_id': order_id},
        {'order._id': 0, 'order.created': 0, 'order.status_updated': 0},
    )
    return proc


def check_response(
        data,
        load_json,
        db,
        request,
        order,
        due=None,
        phone=None,
        is_for_mystery_shopper=None,
):
    order_id = data['orderid']

    assert isinstance(order_id, str)
    actual_proc = get_proc_collection(db, order_id)
    expected_order = load_json(order + '/expected_order.json')
    if 'due' in request:
        due = due.astimezone(pytz.utc)
        expected_order['request']['due'] = datetime.datetime(
            due.year, due.month, due.day, due.hour, due.minute, due.second,
        )
        expected_urgency = expected_order['statistics'].pop('urgency')
        actual_urgency = actual_proc['order']['statistics'].pop('urgency')
        assert abs(actual_urgency - expected_urgency) <= 60

    if phone is not None:
        phone_doc = db.user_phones.find({'phone': phone})[0]
        expected_order['user_phone_id'] = phone_doc['_id']

    if is_for_mystery_shopper:  # not "is not None" on purpose
        expected_order['feedback'] = {
            'mystery_shopper': is_for_mystery_shopper,
        }

    if 'source_geoareas' in expected_order['request']:
        expected_order['request']['source_geoareas'] = set(
            expected_order['request']['source_geoareas'],
        )
        actual_proc['order']['request']['source_geoareas'] = set(
            actual_proc['order']['request']['source_geoareas'],
        )

    assert actual_proc['commit_state'] == expected_order.pop('commit_state')
    assert actual_proc['payment_tech'] == expected_order.pop('payment_tech')
    assert actual_proc['order'] == expected_order


@pytest.fixture()
def mock_mqc_personal_phones(mockserver):
    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _mock_presonal(request):
        return {
            'items': [
                {
                    'id': 'c6a07d2420d9461eadc8cbe815c36c28',
                    'value': '+79023217910',
                },
            ],
        }


def test_supported_features(
        taxi_protocol, mockserver, mock_mqc_personal_phones, load_json, db,
):
    order_path = 'order_1'
    request = load_json(order_path + '/request.json')
    request['supported'] = ['code_dispatch', 'other']
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    order_id = response['orderid']

    proc = db.order_proc.find_one(order_id)
    assert proc['order']['request']['supported'] == ['code_dispatch', 'other']


@pytest.mark.config(
    ADMIN_MQC_USER_PHONES=['79034431132', '+79023217910', '79023217960'],
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_order_draft_1(
        taxi_protocol,
        mockserver,
        mock_mqc_personal_phones,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
        individual_tariffs_switch_on,
):
    order_path = 'order_1'
    request = load_json(order_path + '/request.json')
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    check_response(response, load_json, db, request, order_path)
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.config(MAX_ENTRANCE_LENGTH=6)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_order_draft_long_porchnumber(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
        individual_tariffs_switch_on,
):
    order_path = 'order_long_porchnumber'
    request = load_json(order_path + '/request.json')
    request['route'][0]['porchnumber'] = '9' * 7
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    check_response(response, load_json, db, request, order_path)
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.config(
    ADMIN_MQC_USER_PHONES=['79034431132', '+79023217910', '79023217960'],
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_order_draft_1_mqc_personal(
        taxi_protocol,
        mockserver,
        mock_mqc_personal_phones,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
        individual_tariffs_switch_on,
):
    order_path = 'order_1'
    request = load_json(order_path + '/request.json')
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    check_response(response, load_json, db, request, order_path)
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.config(
    ADMIN_MQC_USER_PHONES=['79034431132', '+79023217910', '79023217960'],
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_order_draft_1_pp_zone(
        taxi_protocol,
        mockserver,
        mock_mqc_personal_phones,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
        individual_tariffs_switch_on,
):
    order_path = 'order_within_pp_zone'
    request = load_json(order_path + '/request.json')
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
        zones_filename='zones.json',
    )
    check_response(response, load_json, db, request, order_path)
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.config(
    ADMIN_MQC_USER_PHONES=['79034431132', '+79023217910', '79023217960'],
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
@pytest.mark.config(IGNORE_CLIENT_PARKS_BLACKLIST=True)
def test_order_draft_2(
        taxi_protocol,
        mockserver,
        mock_mqc_personal_phones,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
):
    order_path = 'order_2'
    request = load_json(order_path + '/request.json')
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        cookie='yandexuid=6543707321492163921; Session_id=5',
    )
    check_response(response, load_json, db, request, order_path)
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.experiments3(
    filename='order_reset_entrance/exp3_reset_entrance.json',
)
@pytest.mark.config(
    ADMIN_MQC_USER_PHONES=['79034431132', '+79023217910', '79023217960'],
)
@pytest.mark.config(IGNORE_CLIENT_PARKS_BLACKLIST=True)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_reset_entrance(
        taxi_protocol,
        mockserver,
        mock_mqc_personal_phones,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
):
    order_path = 'order_reset_entrance'
    request = load_json(order_path + '/request.json')

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return load_json(order_path + '/yamaps.json')

    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        cookie='yandexuid=6543707321492163921; Session_id=5',
        is_yamaps_mocked=True,
    )
    check_response(response, load_json, db, request, order_path)
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


def ignore_excluded_parks_geoarea(taxi_protocol, db, geoareas, ignore):
    search = {'name': 'moscow', 'removed': {'$in': [False, None]}}
    if ignore:
        update = {'$set': {'ignore_excluded_parks': True}}
    else:
        update = {'$unset': {'ignore_excluded_parks': ''}}

    db.geoareas.update(search, update)

    geoareas.get_dict()['moscow']['ignore_excluded_parks'] = ignore

    response = taxi_protocol.post('tests/control', {'invalidate_caches': True})
    assert response.status_code == 200


@pytest.mark.config(
    ADMIN_MQC_USER_PHONES=['79034431132', '+79023217910', '79023217960'],
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_3(
        taxi_protocol,
        mockserver,
        mock_mqc_personal_phones,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
        geoareas,
):
    order_path = 'order_3'
    request = load_json(order_path + '/request.json')

    due = datetime.datetime.now(tzlocal())
    due += datetime.timedelta(minutes=10)

    request['due'] = due.strftime('%Y-%m-%dT%H:%M:%S%z')

    ignore_excluded_parks_geoarea(taxi_protocol, db, geoareas, True)
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    check_response(response, load_json, db, request, order_path, due=due)
    ignore_excluded_parks_geoarea(taxi_protocol, db, geoareas, False)
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.config(
    ADMIN_MQC_USER_PHONES=['79034431132', '+79023217910', '79023217960'],
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
@pytest.mark.config(BILLING_CORP_ENABLED=True)
def test_order_draft_4(
        taxi_protocol,
        mockserver,
        mock_mqc_personal_phones,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
):
    order_path = 'order_4'
    request = load_json(order_path + '/request.json')
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    check_response(response, load_json, db, request, order_path)
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.config(
    ADMIN_MQC_USER_PHONES=['79034431132', '+79023217910', '79023217960'],
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_5(
        taxi_protocol,
        mockserver,
        mock_mqc_personal_phones,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
):
    order_path = 'order_5'
    request = load_json(order_path + '/request.json')
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    check_response(response, load_json, db, request, order_path)
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.config(
    ADMIN_MQC_USER_PHONES=['79034431132', '+79023217910', '79023217960'],
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_7(
        taxi_protocol,
        mockserver,
        mock_mqc_personal_phones,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
):
    order_path = 'order_7'
    request = load_json(order_path + '/request.json')
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
        headers={
            'User-Agent': (
                'yandex-taxi/99.99.99.00000 ' 'Android/10.0.0 (testenv client)'
            ),
        },
    )
    check_response(response, load_json, db, request, order_path)
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.config(
    ADMIN_MQC_USER_PHONES=['79034431132', '+79023217910', '79023217960'],
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_8(
        taxi_protocol,
        mockserver,
        mock_mqc_personal_phones,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
):
    order_path = 'order_8'
    request = load_json(order_path + '/request.json')
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    check_response(response, load_json, db, request, order_path)
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.config(
    ADMIN_MQC_USER_PHONES=['79034431132', '+79023217910', '79023217960'],
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_with_addresses_uri(
        taxi_protocol,
        mockserver,
        mock_mqc_personal_phones,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
):
    order_path = 'order_with_addresses_uri'
    request = load_json(order_path + '/request.json')
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    check_response(response, load_json, db, request, order_path)
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'retries': 1, 'timeout': 100},
        'order_draft': {'use_afs': True, 'retries': 1, 'timeout': 100},
    },
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_spammer(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        now,
):
    _SPAMMER_USER_ID = 'f4eb6aaa29ad4a6eb53f8a7620793111'
    _SPAMMER_PHONE_ID = '59246c5b6195542e9b084207'
    _SPAMMER_DEVICE_ID = 'c02c705e98588f724ca046ac59cafece65501e36'

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        query = set(request.query_string.decode().split('&'))
        assert (
            query
            == {
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
            or query
            == {
                'method=sessionid',
                'userip=',
                'host=yandex.ru',
                'format=json',
                'dbfields=subscription.suid.669',
                'sessionid=5',
                'getphones=bound',
                'get_login_id=yes',
                'phone_attributes=102%2C107',
            }
        )
        return {
            'uid': {'value': '4003514353'},
            'status': {'value': 'VALID'},
            'oauth': {'scope': 'yataxi:read yataxi:write yataxi:pay'},
            'phones': [
                {'attributes': {'102': '+71111111111'}, 'id': '1111'},
                {
                    'attributes': {'102': '+72222222222', '107': '1'},
                    'id': '2222',
                },
            ],
        }

    @mockserver.json_handler('/antifraud/client/user/is_spammer/order_draft')
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'is_multiorder': False,
            'user_id': _SPAMMER_USER_ID,
            'user_phone_id': _SPAMMER_PHONE_ID,
            'device_id': _SPAMMER_DEVICE_ID,
        }
        blocked_until = now + datetime.timedelta(seconds=17)
        return {
            'is_spammer': True,
            'blocked_until': utils.timestring(blocked_until),
        }

    order_path = 'order_1'
    request = load_json(order_path + '/request.json')
    request['id'] = _SPAMMER_USER_ID
    response = taxi_protocol.post(
        _ORDER_DRAFT_PATH, request, bearer='test_token',
    )
    assert response.status_code == 403
    assert response.json()['blocked'] == '2017-05-25T08:30:17+0000'


@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=False,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'retries': 1, 'timeout': 100},
        'order_draft': {'use_afs': True, 'retries': 1, 'timeout': 100},
    },
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_is_spammer_disabled_in_client(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        now,
):
    _SPAMMER_USER_ID = 'f4eb6aaa29ad4a6eb53f8a7620793111'
    _SPAMMER_PHONE_ID = '59246c5b6195542e9b084207'
    _SPAMMER_DEVICE_ID = 'c02c705e98588f724ca046ac59cafece65501e36'

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        query = set(request.query_string.decode().split('&'))
        assert (
            query
            == {
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
            or query
            == {
                'method=sessionid',
                'userip=',
                'host=yandex.ru',
                'format=json',
                'dbfields=subscription.suid.669',
                'sessionid=5',
                'getphones=bound',
                'get_login_id=yes',
                'phone_attributes=102%2C107',
            }
        )
        return {
            'uid': {'value': '4003514353'},
            'status': {'value': 'VALID'},
            'oauth': {'scope': 'yataxi:read yataxi:write yataxi:pay'},
            'phones': [
                {'attributes': {'102': '+71111111111'}, 'id': '1111'},
                {
                    'attributes': {'102': '+72222222222', '107': '1'},
                    'id': '2222',
                },
            ],
        }

    @mockserver.json_handler('/antifraud/client/user/is_spammer/order_draft')
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'is_multiorder': False,
            'user_id': _SPAMMER_USER_ID,
            'user_phone_id': _SPAMMER_PHONE_ID,
            'device_id': _SPAMMER_DEVICE_ID,
        }
        blocked_until = now + datetime.timedelta(seconds=17)
        return {
            'is_spammer': True,
            'blocked_until': utils.timestring(blocked_until),
        }

    order_path = 'order_1'
    request = load_json(order_path + '/request.json')
    request['id'] = _SPAMMER_USER_ID
    response = taxi_protocol.post(
        _ORDER_DRAFT_PATH, request, bearer='test_token',
    )
    assert response.status_code == 200
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'retries': 1, 'timeout': 100},
        'order_draft': {'use_afs': True, 'retries': 1, 'timeout': 100},
    },
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_not_spammer(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
):
    _SPAMMER_USER_ID = 'f4eb6aaa29ad4a6eb53f8a7620793111'
    _SPAMMER_PHONE_ID = '59246c5b6195542e9b084207'
    _SPAMMER_DEVICE_ID = 'c02c705e98588f724ca046ac59cafece65501e36'

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        query = set(request.query_string.decode().split('&'))
        assert (
            query
            == {
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
            or query
            == {
                'method=sessionid',
                'userip=',
                'host=yandex.ru',
                'format=json',
                'dbfields=subscription.suid.669',
                'sessionid=5',
                'getphones=bound',
                'get_login_id=yes',
                'phone_attributes=102%2C107',
            }
        )
        return {
            'uid': {'value': '4003514353'},
            'status': {'value': 'VALID'},
            'oauth': {'scope': 'yataxi:read yataxi:write yataxi:pay'},
            'phones': [
                {'attributes': {'102': '+71111111111'}, 'id': '1111'},
                {
                    'attributes': {'102': '+72222222222', '107': '1'},
                    'id': '2222',
                },
            ],
        }

    @mockserver.json_handler('/antifraud/client/user/is_spammer/order_draft')
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'is_multiorder': False,
            'user_id': _SPAMMER_USER_ID,
            'user_phone_id': _SPAMMER_PHONE_ID,
            'device_id': _SPAMMER_DEVICE_ID,
        }
        return {'is_spammer': False}

    order_path = 'order_1'
    request = load_json(order_path + '/request.json')
    request['id'] = _SPAMMER_USER_ID
    response = taxi_protocol.post(
        _ORDER_DRAFT_PATH, request, bearer='test_token',
    )
    assert response.status_code == 200
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'retries': 1, 'timeout': 100},
        'order_draft': {'use_afs': True, 'retries': 1, 'timeout': 100},
    },
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
@pytest.mark.parametrize('response_code', [500, 400, 403])
def test_order_draft_is_spammer_affected(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        cardstorage,
        load_json,
        response_code,
):
    _SPAMMER_USER_ID = 'f4eb6aaa29ad4a6eb53f8a7620793111'

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        query = set(request.query_string.decode().split('&'))
        assert (
            query
            == {
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
            or query
            == {
                'method=sessionid',
                'userip=',
                'host=yandex.ru',
                'format=json',
                'dbfields=subscription.suid.669',
                'sessionid=5',
                'getphones=bound',
                'get_login_id=yes',
                'phone_attributes=102%2C107',
            }
        )
        return {
            'uid': {'value': '4003514353'},
            'status': {'value': 'VALID'},
            'oauth': {'scope': 'yataxi:read yataxi:write yataxi:pay'},
            'phones': [
                {'attributes': {'102': '+71111111111'}, 'id': '1111'},
                {
                    'attributes': {'102': '+72222222222', '107': '1'},
                    'id': '2222',
                },
            ],
        }

    @mockserver.json_handler('/antifraud/client/user/is_spammer/order_draft')
    def mock_afs_is_spammer_invalid(request):
        return mockserver.make_response(
            '{"code":' + str(response_code) + '}', response_code,
        )

    order_path = 'order_1'
    request = load_json(order_path + '/request.json')
    request['id'] = _SPAMMER_USER_ID
    response = taxi_protocol.post(
        _ORDER_DRAFT_PATH, request, bearer='test_token',
    )
    assert response.status_code == 200
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.parametrize(
    'payment_type, payment_id, config_dict, expected_code',
    [
        ('card', 'card-test', {'BILLING_CREDITCARD_ENABLED': True}, 200),
        ('card', 'card-test', {'BILLING_CREDITCARD_ENABLED': False}, 406),
        ('corp', 'corp-test', {'BILLING_CORP_ENABLED': True}, 200),
        ('corp', 'corp-test', {'BILLING_CORP_ENABLED': False}, 406),
        (
            'personal_wallet',
            'passwal-RUB',
            {'BILLING_PERSONAL_WALLET_ENABLED': True},
            200,
        ),
        (
            'personal_wallet',
            'passwal-RUB',
            {'BILLING_PERSONAL_WALLET_ENABLED': False},
            406,
        ),
        (
            'coop_account',
            'coop-123',
            {'BILLING_COOP_ACCOUNT_ENABLED': True},
            200,
        ),
        (
            'coop_account',
            'coop-123',
            {'BILLING_COOP_ACCOUNT_ENABLED': False},
            406,
        ),
        ('sbp', None, {'BILLING_SBP_ENABLED': True}, 200),
        ('sbp', None, {'BILLING_SBP_ENABLED': False}, 406),
    ],
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_billing_resolution(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
        config,
        payment_type,
        payment_id,
        config_dict,
        expected_code,
):
    config.set_values(config_dict)
    order_path = 'order_personal_wallet'
    request = load_json(order_path + '/request.json')
    request['payment']['type'] = payment_type
    if payment_id is None:
        request['payment'].pop('payment_method_id')
    else:
        request['payment']['payment_method_id'] = payment_id

    orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
        expected_code=expected_code,
    )
    if expected_code == 200:
        assert (
            mock_order_core.create_draft_times_called == order_core_exp_enabled
        )


@pytest.mark.parametrize(
    'payment_type, payment_id',
    [
        ('card', 'card-test'),
        ('corp', 'corp-test'),
        ('applepay', 'card-test'),
        ('googlepay', 'card-test'),
        ('personal_wallet', 'passwall-RUB'),
        ('coop_account', 'coop-123'),
        ('yandex_card', 'yandex_card_id'),
        ('sbp', None),
    ],
)
@pytest.mark.parametrize(
    'payment_allowed, expected_code', [(True, 200), (False, 406)],
)
@pytest.mark.config(
    BILLING_PERSONAL_WALLET_ENABLED=True,
    BILLING_COOP_ACCOUNT_ENABLED=True,
    CHECK_PAYMENT_ORDERS_IN_ORDERDRAFT=True,
    BILLING_SBP_ENABLED=True,
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_tariff_payment_options(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
        config,
        payment_type,
        payment_id,
        payment_allowed,
        expected_code,
):
    if payment_allowed:
        update = {'$push': {'payment_options': payment_type}}
    else:
        update = {'$pull': {'payment_options': payment_type}}

    db.tariff_settings.update({'hz': 'moscow'}, update)
    order_path = 'order_personal_wallet'
    request = load_json(order_path + '/request.json')
    request['payment']['type'] = payment_type
    if payment_id is None:
        request['payment'].pop('payment_method_id')
    else:
        request['payment']['payment_method_id'] = payment_id

    orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
        expected_code=expected_code,
    )
    if expected_code == 200:
        assert (
            mock_order_core.create_draft_times_called == order_core_exp_enabled
        )


@pytest.mark.translations(
    client_messages={
        'common_errors.INVALID_PHONE_NUMBER': {
            'ru': 'INVALID_PHONE_NUMBER_ru',
        },
    },
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_incorrect_contact_phone(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
):
    order_path = 'order_extra_contact_phone'
    request = load_json(order_path + '/request.json')
    request['extra_contact_phone'] = '913 (70) 43-48-0'
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
        expected_code=406,
    )
    assert response['error']['code'] == 'INVALID_PHONE_NUMBER'
    assert response['error']['text'] == 'INVALID_PHONE_NUMBER_ru'


@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_extra_contact_phone(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
):
    order_path = 'order_extra_contact_phone'
    request = load_json(order_path + '/request.json')
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    response_id = response['orderid']
    response_as_proc = get_proc_collection(db, response_id)
    order_request = response_as_proc['order']['request']

    extra_user_phone_id = order_request['extra_user_phone_id']
    object = db.user_phones.find_one({'_id': extra_user_phone_id})
    assert isinstance(object, dict)
    number = object['phone']
    assert number == '+79152319545'
    assert isinstance(number, str)
    assert object['phone_hash'] is not None
    assert object['phone_salt'] is not None
    assert (
        object['phone_hash']
        == hmac.new(
            base64.b64decode(object['phone_salt']) + b'secdist_salt',
            object['phone'].encode(),
            hashlib.sha256,
        ).hexdigest()
    )

    comment = order_request['comment']
    expected_comment = 'please fast'
    assert comment == expected_comment
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_no_extra_contact_phone(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
):
    order_path = 'order_3'
    request = load_json(order_path + '/request.json')
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    response_id = response['orderid']
    response_as_proc = get_proc_collection(db, response_id)
    order_request = response_as_proc['order']['request']
    assert 'extra_user_phone_id' not in order_request

    comment = order_request['comment']
    assert comment == 'commet it'
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.user_experiments('mystery_shopper')
@pytest.mark.config(
    MYSTERY_SHOPPER_ENABLED=True,
    MYSTERY_SHOPPER_CLIENT_ID=['b22a310c841f47b2b1b459b0bb4430c0'],
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_mystery_shopper_experiment(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
):
    order_path = 'order_4'
    request = load_json(order_path + '/request.json')
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    check_response(
        response,
        load_json,
        db,
        request,
        order_path,
        is_for_mystery_shopper=True,
    )
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.user_experiments('mystery_shopper')
@pytest.mark.config(MYSTERY_SHOPPER_ENABLED=True, MYSTERY_SHOPPER_CLIENT_ID=[])
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_mystery_shopper_experiment_failing(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
):
    order_path = 'order_4'
    request = load_json(order_path + '/request.json')
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    check_response(
        response,
        load_json,
        db,
        request,
        order_path,
        is_for_mystery_shopper=False,
    )
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.parametrize('add_empty_country', [True, False])
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_without_params(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
        add_empty_country,
):

    order_path = 'order_without_params'
    request = load_json(order_path + '/request.json')
    if add_empty_country:
        request['route'][0]['country'] = ''
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    check_response(response, load_json, db, request, order_path)
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.config(
    ADMIN_MQC_USER_PHONES=['79034431132', '+79023217910', '79023217960'],
)
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
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_tips(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        mock_mqc_personal_phones,
        load_json,
        db,
        tips,
        expected_code,
        expected_tips,
):
    order_path = 'order_1'
    request = load_json(order_path + '/request.json')
    request['tips'] = tips
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
        expected_code=expected_code,
    )

    if expected_tips:
        order_id = response['orderid']
        assert isinstance(order_id, str)
        actual_proc = get_proc_collection(db, order_id)
        assert actual_proc['order']['creditcard']['tips'] == expected_tips
    if expected_code == 200:
        assert (
            mock_order_core.create_draft_times_called == order_core_exp_enabled
        )


@pytest.mark.parametrize(
    'config_enabled,enabled_classes,db_stored_classes,expected_code',
    [
        # request with ["econom", "business", "comfort"]
        # no `comfort` in tariff settings
        (False, [], [], 406),
        (True, [], [], 406),
        (True, ['econom'], ['econom'], 200),
        (True, ['comfort'], [], 406),
        (True, ['econom', 'comfort', 'business'], ['econom', 'business'], 200),
        (True, ['econom', 'vip', 'maybach'], ['econom'], 200),
        (True, ['econom', 'comfort'], ['econom'], 200),
        (
            True,
            ['econom', 'business', 'vip', 'comfortplus'],
            ['econom', 'business'],
            200,
        ),
        (True, ['vip', 'maybach', 'comfortplus'], [], 406),
    ],
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_multiclass(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
        config,
        config_enabled,
        enabled_classes,
        db_stored_classes,
        expected_code,
):
    order_path = 'order_multiclass'
    request = load_json(order_path + '/request.json')

    config.set_values(
        {
            'MULTICLASS_ENABLED': config_enabled,
            'MULTICLASS_TARIFFS_BY_ZONE': {'__default__': enabled_classes},
        },
    )

    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
        expected_code=expected_code,
    )

    if expected_code == 200:
        order_id = response['orderid']
        proc = db.order_proc.find_one(order_id)
        assert proc['order']['request']['class'] == db_stored_classes
        assert (
            mock_order_core.create_draft_times_called == order_core_exp_enabled
        )


@pytest.mark.parametrize(
    'delay_min, expected_is_delayed, preorder_guarantee',
    [
        pytest.param(0, None, None, id='simple order'),
        pytest.param(10, None, None, id='simple order'),
        pytest.param(11, True, None, id='preorder'),
        pytest.param(
            11,
            True,
            True,
            marks=[
                pytest.mark.experiments3(
                    filename='order_delayed/exp3_preorder_guarantee.json',
                ),
            ],
            id='preorder_guarantee',
        ),
    ],
)
@pytest.mark.config(DELAYED_ORDER_DETECTION_THRESHOLD_MIN=10)
@pytest.mark.now('2020-06-22T03:50:00+0300')
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_delayed(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
        delay_min,
        expected_is_delayed,
        preorder_guarantee,
):
    order_path = 'order_delayed'
    request = load_json(order_path + '/request.json')

    if delay_min:
        due = datetime.datetime.strptime(request['due'], '%Y-%m-%dT%H:%M:%S%z')
        due += datetime.timedelta(minutes=delay_min)
        request.update({'due': due.strftime('%Y-%m-%dT%H:%M:%S%z')})

    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )

    order_id = response['orderid']
    proc = db.order_proc.find_one(order_id)
    if expected_is_delayed:
        assert 'is_delayed' in proc['order']['request']
        assert proc['order']['request']['is_delayed'] is True
        if preorder_guarantee:
            assert proc['order']['request']['lookup_extra'] == {
                'intent': 'preorder_guarantee',
            }
        else:
            assert 'lookup_extra' not in proc['order']['request']

    else:
        assert 'is_delayed' not in proc['order']['request']
        assert 'lookup_extra' not in proc['order']['request']

    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_sdc_check(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        config,
):
    order_path = 'order_sdc_check'
    request = load_json(order_path + '/request.json')

    config.set_values(
        {
            'ZONEINFO_TARIFFS_SETTINGS_BY_MODES_IN_ZONES': {
                'moscow': {'selfdriving': ['sdc']},
            },
            'MODES': [
                {
                    'experiment': 'enable_sdc_2',
                    'mode': 'sdc',
                    'title': 'zoneinfo.modes.title.sdc',
                    'zone_activation': {
                        'point_image_tag': 'custom_pp_icons_2_red',
                        'point_title': 'selfdriving.pickuppoint_name',
                        'zone_type': 'sdc',
                    },
                },
            ],
            'ALL_CATEGORIES': ['selfdriving'],
            'APPLICATION_BRAND_CATEGORIES_SETS': {
                '__default__': ['selfdriving'],
            },
        },
    )

    orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
        expected_code=400,
    )


@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_with_orgs(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
):
    is_checked_as_org = False
    is_checked_as_addr = False

    order_path = 'order_with_orgs'

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        if request.args.get('business_oid') is not None:
            nonlocal is_checked_as_org
            is_checked_as_org = True
            return load_json(order_path + '/org_yamaps_response.json')

        nonlocal is_checked_as_addr
        is_checked_as_addr = True
        return load_json(order_path + '/addr_yamaps_response.json')

    request = load_json(order_path + '/request.json')
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
        is_yamaps_mocked=True,
    )
    order_id = response['orderid']

    assert is_checked_as_org
    assert is_checked_as_addr

    proc = db.order_proc.find_one(order_id)
    source = proc['order']['request']['source']
    assert source == load_json(order_path + '/expected_source_in_db.json')
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.config(
    HOURLY_RENTAL_CRUTCH_DESTINATIONS=True, HOURLY_RENTAL_ENABLED=True,
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_hourly_rental(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
):
    order_path = 'order_hourly_rental'
    request = load_json(order_path + '/request.json')
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    order_id = response['orderid']
    proc = db.order_proc.find_one(order_id)
    assert proc['order']['request']['destinations'] == []
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'cargo'],
    APPLICATION_BRAND_CATEGORIES_SETS={'__default__': ['econom', 'cargo']},
    DEFAULT_REQUIREMENTS={'__default__': {'cargo': {'cargo_type': 'lcv_m'}}},
)
@pytest.mark.parametrize(
    ('selected_class', 'request_requirements', 'order_requirements'),
    [
        pytest.param('econom', {}, {}, id='requested_reqs_for_other_class'),
        pytest.param(
            'cargo',
            {'cargo_type': 'van'},
            {'cargo_type': 'van'},
            id='requested_reqs_for_config_class',
        ),
        pytest.param(
            'cargo',
            {},
            {'cargo_type': 'lcv_m'},
            id='default_reqs_for_config_class',
        ),
    ],
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_default_requirements(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
        selected_class,
        request_requirements,
        order_requirements,
):
    order_path = 'order_2'
    request = load_json(order_path + '/request.json')
    request['class'] = [selected_class]
    request['requirements'] = request_requirements

    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    order_id = response['orderid']
    proc = db.order_proc.find_one(order_id)

    assert proc['order']['request']['requirements'] == order_requirements
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'business'],
    APPLICATION_BRAND_CATEGORIES_SETS={'__default__': ['econom', 'business']},
    USER_API_USE_USER_PHONES_BULK_CREATION=True,
)
@pytest.mark.parametrize(
    'user_api_available',
    [
        pytest.param(False, id='user_api_not_available'),
        pytest.param(True, id='user_api_available'),
    ],
)
@pytest.mark.parametrize(
    'phone_a, phone_b',
    [
        pytest.param('+79161112233', '+79169998877', id='different_phones'),
        pytest.param('+79161112233', '+79161112233', id='same_phones'),
    ],
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_route_extra_data(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
        phone_a,
        phone_b,
        user_api_available,
):
    extra_data_a = {
        'contact_phone': phone_a,
        'floor': '13',
        'apartment': '42',
        'doorphone_number': '112#1024',
        'porch': '2',
        'comment': 'No comments',
    }
    extra_data_b = {
        'contact_phone': phone_b,
        'floor': '1',
        'porch': '3',
        'doorphone_number': '112#1024',
    }
    route_extra_data = [extra_data_a, extra_data_b]

    phone_ids = dict()
    phone_ids[phone_a] = 'a86ec02343e7eac9b35f7819'
    if phone_a != phone_b:
        phone_ids[phone_b] = 'b86ec02343e7eac9b35f7819'

    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def mock_personal_phones_bulk_store(request):
        return mockserver.make_response(status=500)

    @mockserver.json_handler('/user-api/user_phones/bulk')
    def mock_user_phones_bulk(request):
        data = json.loads(request.get_data())
        assert data['items'] == [
            {'phone': phone_a, 'type': 'yandex'},
            {'phone': phone_b, 'type': 'yandex'},
        ]
        if not user_api_available:
            return mockserver.make_response(status=500)
        result = {
            'items': [
                {
                    'id': phone_ids[phone_a],
                    'personal_phone_id': 'a846b87de6894e87815b8719da22b10d',
                    'phone': phone_a,
                    'type': 'yandex',
                },
            ],
        }
        if phone_a != phone_b:
            result['items'].append(
                {
                    'id': phone_ids[phone_b],
                    'personal_phone_id': 'b846b87de6894e87815b8719da22b10d',
                    'phone': phone_b,
                    'type': 'yandex',
                },
            )

        return result

    order_path = 'order_3'
    request = load_json(order_path + '/request.json')
    for i in range(len(route_extra_data)):
        request['route'][i]['extra_data'] = route_extra_data[i]

    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    order_id = response['orderid']
    proc = db.order_proc.find_one({'_id': order_id})

    for i in range(len(route_extra_data)):
        raw_extra_data = route_extra_data[i]
        if i == 0:
            order_point = proc['order']['request']['source']
        else:
            order_point = proc['order']['request']['destinations'][i - 1]
        order_extra_data = order_point['extra_data']

        for field in ['floor', 'apartment', 'comment', 'doorphone_number']:
            if field in raw_extra_data:
                assert order_extra_data[field] == raw_extra_data[field]
            else:
                assert field not in order_extra_data

            if 'porch' in raw_extra_data:
                assert order_point['porchnumber'] == raw_extra_data['porch']

        phone_id = order_extra_data['contact_phone_id']
        expected_phone = raw_extra_data['contact_phone']
        if not user_api_available:
            phone_doc = db.user_phones.find({'_id': phone_id})[0]
            assert phone_doc['phone'] == expected_phone
        else:
            assert phone_ids[expected_phone] == str(phone_id)
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.config(
    ADDITIONAL_COUNTRIES_PHONE_FORMAT_RULES={
        'fin': [
            {'local_prefix': '4', 'international_prefix': '3584'},
            {'local_prefix': '', 'international_prefix': '358433999444'},
        ],
    },
)
@pytest.mark.parametrize(
    'input_phone, expected_phone, expected_code',
    (
        pytest.param(
            '0-333-999', '+358333999', 200, id='national format short',
        ),
        pytest.param(
            '0-333-999-444-11',
            '+35833399944411',
            200,
            id='national format long',
        ),
        pytest.param(
            '43399944411', '+35843399944411', 200, id='additional format',
        ),
        pytest.param(
            '11',
            '+35843399944411',
            200,
            id='additional format with empty local prefix',
        ),
        pytest.param(
            '+358-333-999', '+358333999', 200, id='international format short',
        ),
        pytest.param(
            '+358-333-999-44-411',
            '+35833399944411',
            200,
            id='international format long',
        ),
        pytest.param(
            '+7(965) 8443421',
            '+79658443421',
            200,
            id='international format other country',
        ),
        pytest.param(
            '8928 3138817', '', 406, id='national format other country',
        ),
        pytest.param('aaa', '', 406, id='wrong phone'),
    ),
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_international_phone_format(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
        input_phone,
        expected_phone,
        expected_code,
):
    order_path = 'order_international_phone_format'
    request = load_json(order_path + '/request.json')
    request['extra_contact_phone'] = input_phone
    request['route'][0]['extra_data']['contact_phone'] = input_phone

    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
        expected_code=expected_code,
    )
    if expected_code == 200:
        response_id = response['orderid']
        response_as_proc = get_proc_collection(db, response_id)
        order_request = response_as_proc['order']['request']

        extra_user_phone_id = order_request['extra_user_phone_id']
        _check_user_phone(expected_phone, db, extra_user_phone_id)
        extra_data_source = order_request['source']['extra_data']
        source_phone_id = extra_data_source['contact_phone_id']
        _check_user_phone(expected_phone, db, source_phone_id)
        assert (
            mock_order_core.create_draft_times_called == order_core_exp_enabled
        )

    if expected_code == 406:
        assert response['error']['code'] == 'INVALID_PHONE_NUMBER'


@pytest.mark.parametrize(
    'complement',
    (
        {'type': 'personal_wallet', 'payment_method_id': 'wallet_id/1234567'},
        {
            'type': 'personal_wallet',
            'payment_method_id': 'wallet_id/1234567',
            'withdraw_amount': '99.99',
        },
    ),
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_complement_payments(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
        complement,
):
    order_path = 'order_complement_payments'
    request = load_json(order_path + '/request.json')
    request['payment']['complements'] = [complement]

    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    order_id = response['orderid']
    proc = db.order_proc.find_one(order_id)

    complement_copy = complement.copy()
    if 'withdraw_amount' in complement_copy:
        # we save withdraw_amount in mongo as a number
        complement_copy['withdraw_amount'] = float(
            complement_copy['withdraw_amount'],
        )

    assert proc['order']['request']['payment'] == {
        'payment_method_id': 'card-x9285',
        'type': 'card',
        'complements': [complement_copy],
    }
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.experiments3(
    filename='antifraud/exp3_is_cash_change_blocking_enabled.json',
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_antifraud_events(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        mock_mqc_personal_phones,
        load_json,
        db,
):
    class OrderIdHolder:
        id = None

    order_id_holder = OrderIdHolder()

    @mockserver.json_handler('/uantifraud/v1/events/order/draft')
    def mock_antifraud_events(request):
        data = json.loads(request.get_data())
        order_id_holder.id = data.pop('order_id')

        assert data == {
            'user_id': 'f4eb6aaa29ad4a6eb53f8a7620793561',
            'phone_id': '59246c5b6195542e9b084206',
            'device_id': 'c02c705e98588f724ca046ac59cafece65501e36',
            'yandex_uid': '4003514353',
            'nz': 'moscow',
        }
        return {}

    order_path = 'order_1'
    request = load_json(order_path + '/request.json')
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    mock_antifraud_events.wait_call()
    assert order_id_holder.id == response['orderid']
    check_response(response, load_json, db, request, order_path)
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.config(ORDER_SHARDS=[3])
@pytest.mark.parametrize(
    'expected_shard_id',
    [
        pytest.param(3),
        pytest.param(
            3,
            marks=[
                pytest.mark.experiments3(
                    filename='order_shards_experiment/disabled.json',
                ),
            ],
        ),
        pytest.param(
            3,
            marks=[
                pytest.mark.experiments3(
                    filename='order_shards_experiment/not-matching.json',
                ),
            ],
        ),
        pytest.param(
            5,
            marks=[
                pytest.mark.experiments3(
                    filename='order_shards_experiment/ok.json',
                ),
            ],
        ),
    ],
)
def test_generate_shard_id(
        taxi_protocol, mockserver, load_json, db, expected_shard_id,
):
    order_path = 'order_1'
    request = load_json(order_path + '/request.json')
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    order_id = response['orderid']
    proc = db.order_proc.find_one({'_id': order_id})
    assert proc['_shard_id'] == expected_shard_id
    assert proc.get('updated') is not None


@pytest.mark.config(
    ADMIN_MQC_USER_PHONES=['79034431132', '+79023217910', '79023217960'],
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_order_draft_with_login_id(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        mock_mqc_personal_phones,
        load_json,
        db,
):
    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        query = set(request.query_string.decode().split('&'))
        assert (
            query
            == {
                'method=oauth',
                'userip=my-ip-address',
                'format=json',
                'dbfields=subscription.suid.669',
                'aliases=1%2C10%2C16',
                'oauth_token=test_token',
                'getphones=bound',
                'get_login_id=yes',
                'phone_attributes=102%2C107%2C4',
            }
            or query
            == {
                'method=sessionid',
                'userip=my-ip-address',
                'host=yandex.ru',
                'format=json',
                'dbfields=subscription.suid.669',
                'sessionid=5',
                'getphones=bound',
                'get_login_id=yes',
                'phone_attributes=102%2C107',
            }
        )
        return {
            'uid': {'value': '4003514353'},
            'status': {'value': 'VALID'},
            'oauth': {'scope': 'yataxi:read yataxi:write yataxi:pay'},
            'login_id': 't:1234',
            'phones': [
                {'attributes': {'102': '+71111111111'}, 'id': '1111'},
                {
                    'attributes': {'102': '+72222222222', '107': '1'},
                    'id': '2222',
                },
            ],
        }

    order_path = 'order_with_login_id'
    request = load_json(order_path + '/request.json')
    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
        is_blackbox_mocked=True,
    )
    check_response(response, load_json, db, request, order_path)
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_antifraud_enabled(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
):
    order_path = 'order_9'
    request = load_json(order_path + '/request.json')

    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    order_id = response['orderid']
    order_proc = db.order_proc.find_one(order_id)

    assert not order_proc['payment_tech']['antifraud_finished']
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.parametrize(
    'expected_code',
    [
        pytest.param(
            200, marks=pytest.mark.config(LIMIT_PAYMENT_METHODS_BY_CLASS={}),
        ),
        pytest.param(
            406,
            marks=pytest.mark.config(
                LIMIT_PAYMENT_METHODS_BY_CLASS={'econom': ['corp']},
            ),
        ),
        pytest.param(
            200,
            marks=pytest.mark.config(
                LIMIT_PAYMENT_METHODS_BY_CLASS={'econom': ['card']},
            ),
        ),
    ],
)
@pytest.mark.config(
    ADMIN_MQC_USER_PHONES=['79034431132', '+79023217910', '79023217960'],
)
@pytest.mark.config(IGNORE_CLIENT_PARKS_BLACKLIST=True)
def test_payment_method_limit_by_class(
        taxi_protocol,
        mockserver,
        mock_mqc_personal_phones,
        mock_order_core,
        load_json,
        expected_code,
):
    order_path = 'order_payment_method_limit_by_class'
    request = load_json(order_path + '/request.json')

    orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        cookie='yandexuid=6543707321492163921; Session_id=5',
        expected_code=expected_code,
    )


@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_passenger_price(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load_json,
        db,
):
    order_path = 'order_9'
    request = load_json(order_path + '/request.json')
    request['passenger_price'] = '500'

    response = orderdraft(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    order_id = response['orderid']
    order_proc = db.order_proc.find_one(order_id)

    assert order_proc['order']['request']['passenger_price'] == 500
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled
