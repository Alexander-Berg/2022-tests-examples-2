import datetime
import json

import bson
import pytest

from taxi_tests import utils

from launch_use_input_user_parametrize import LAUNCH_USE_INPUT_FIELDS
from protocol import brands

MIN_CARD_ORDERS_DEFAULT = 1


@pytest.fixture(scope='function', autouse=True)
def feedback_service(mockserver):
    @mockserver.json_handler('/feedback/1.0/wanted/retrieve')
    def mock_service(request):
        assert request.headers['YaTaxi-Api-Key'] == 'feedback_apikey'
        data = json.loads(request.get_data())
        assert sorted(data.keys()) == ['id', 'newer_than', 'phone_id']
        return {'orders': []}


def test_launch_simple(taxi_protocol):
    response = taxi_protocol.post('3.0/launch', {})
    assert response.status_code == 200
    data = response.json()
    assert not data['authorized']
    user_id = data['id']

    response = taxi_protocol.post('3.0/launch', {'id': user_id})
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == user_id
    assert not data['authorized']


@LAUNCH_USE_INPUT_FIELDS
def test_launch_user_chat(taxi_protocol, mockserver, use_input_fields):
    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        assert set(request.query_string.decode().split('&')) == {
            'method=oauth',
            'userip=',
            'format=json',
            'dbfields=subscription.suid.669',
            'aliases=1%2C10%2C16',
            'oauth_token=test_token',
            'getphones=bound',
            'get_login_id=yes',
            'phone_attributes=102%2C107%2C4',
            'attributes=1015',
        }
        return {
            'uid': {'value': '123'},
            'status': {'value': 'VALID'},
            'oauth': {'scope': 'yataxi:read yataxi:write yataxi:pay'},
            'aliases': {'10': 'phne-edcsaypw'},
            'phones': [
                {'attributes': {'102': '+79123456789'}, 'id': '1111'},
                {
                    'attributes': {'102': '+79123456789', '107': '1'},
                    'id': '2222',
                },
            ],
        }

    user_id = '536b24fa2816451b855d9a3e640215c3'
    phone_id = '594baaba779fb30a39a5381e'
    response = taxi_protocol.post(
        '3.0/launch',
        {'id': user_id, 'authorized': True, 'phone_id': phone_id},
        bearer='test_token',
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get('chat')
    assert data['chat'].get('new_chat_messages') == 2
    assert data['chat'].get('support_timestamp') == '2017-06-20T12:14:18+0000'
    assert 'brandings' not in data


@pytest.mark.now('2021-11-09T10:36:00+0000')
@pytest.mark.config(BILLING_METHOD_FALLBACK_ENABLED=False)
@pytest.mark.config(BILLING_USE_MONGO_STATS_COUNTER=True)
@pytest.mark.config(BILLING_AUTOMATIC_FALLBACK_MIN_EVENTS=100)
@pytest.mark.parametrize(
    'autofallback_enabled, static_ok_status',
    [
        pytest.param(
            False,
            False,
            marks=pytest.mark.config(BILLING_STATIC_COUNTER_STATUS=False),
            id='autofallback_disabled_static_not_ok',
        ),
        pytest.param(
            False,
            True,
            marks=pytest.mark.config(BILLING_STATIC_COUNTER_STATUS=True),
            id='autofallback_disabled_static_ok',
        ),
        pytest.param(True, None, id='autofallback_enabled'),
    ],
)
@pytest.mark.parametrize(
    'stat_counter_enabled',
    [
        pytest.param(False, id='stat_counter_disabled'),
        pytest.param(True, id='stat_counter_enabled'),
    ],
)
@pytest.mark.parametrize(
    'stat_counter_ok_status',
    [
        pytest.param(
            False,
            marks=pytest.mark.filldb(event_stats='billing_not_ok'),
            id='stat_counter_not_ok',
        ),
        pytest.param(
            True,
            marks=pytest.mark.filldb(event_stats='billing_ok'),
            id='stat_counter_ok',
        ),
    ],
)
@pytest.mark.parametrize(
    'statistics_enabled',
    [
        pytest.param(False, id='statistics_disabled'),
        pytest.param(True, id='statistics_enabled'),
    ],
)
@pytest.mark.parametrize(
    'statistics_ok_status',
    [
        pytest.param(False, id='statistics_not_ok'),
        pytest.param(True, id='statistics_ok'),
    ],
)
@LAUNCH_USE_INPUT_FIELDS
def test_launch_billing_autofallback(
        taxi_protocol,
        blackbox_service,
        testpoint,
        config,
        mockserver,
        autofallback_enabled,
        static_ok_status,
        stat_counter_enabled,
        stat_counter_ok_status,
        statistics_enabled,
        statistics_ok_status,
        use_input_fields,
):
    config.set_values(
        dict(
            BILLING_AUTOMATIC_FALLBACK_ENABLED=autofallback_enabled,
            BILLING_AUTOFALLBACK_STAT_COUNTERS_ENABLED=stat_counter_enabled,
            BILLING_AUTOFALLBACK_STATISTICS_ENABLED=statistics_enabled,
        ),
    )

    @mockserver.json_handler('/statistics_agent/v1/fallbacks/state')
    def mock_statistics_agent(request):
        return {
            'fallbacks': [
                {
                    'name': 'billing_call_simple.total.fallback',
                    'value': not statistics_ok_status,
                },
            ],
        }

    billing_ok_testpoint_calls = []

    @testpoint('BillingIsOK')
    def billing_ok_testpoint(data):
        billing_ok_testpoint_calls.append(data)

    response = taxi_protocol.post(
        '3.0/launch',
        {
            'id': '536b24fa2816451b855d9a3e640215c3',
            'phone_id': '594baaba779fb30a39a5381e',
            'authorized': True,
        },
        bearer='test_token',
    )
    assert response.status_code == 200

    assert billing_ok_testpoint.times_called == 1

    billing_is_ok = billing_ok_testpoint_calls[0]['billing_is_ok']

    if not autofallback_enabled:
        assert billing_is_ok == static_ok_status
        return

    # autofallback enabled
    if not statistics_enabled:
        # if new flow disabled - fallback to old flow
        assert billing_is_ok == stat_counter_ok_status
    else:
        # new flow enabled
        if stat_counter_enabled:
            # old flow has higher priority
            assert billing_is_ok == stat_counter_ok_status
        else:
            # only new flow enabled
            assert billing_is_ok == statistics_ok_status


@pytest.mark.config(BILLING_AUTOMATIC_FALLBACK_ENABLED=False)
@pytest.mark.filldb(orders='billing_fallback')
@pytest.mark.parametrize(
    'billing_ok,order_fallback,debts_included',
    [
        (True, True, True),
        (True, False, True),
        (False, False, True),
        (False, True, False),
    ],
)
@LAUNCH_USE_INPUT_FIELDS
def test_launch_billing_fallback(
        billing_ok,
        order_fallback,
        debts_included,
        use_input_fields,
        taxi_protocol,
        config,
        blackbox_service,
):

    # if BILLING_AUTOMATIC_FALLBACK_ENABLED is False, stat counter will return
    # static value. That is normally True, but can be changed via
    # BILLING_STATIC_COUNTER_STATUS
    config.set_values(
        dict(
            BILLING_STATIC_COUNTER_STATUS=billing_ok,
            BILLING_ORDER_AUTOFALLBACK_ENABLED=order_fallback,
        ),
    )
    # Check configs
    response = taxi_protocol.post(
        '3.0/launch',
        {
            'id': '536b24fa2816451b855d9a3e640215c3',
            'authorized': True,
            'phone_id': '594baaba779fb30a39a5381e',
        },
        bearer='test_token',
    )
    assert response.status_code == 200
    data = response.json()
    assert data['authorized']
    if debts_included:
        assert 'debt' in data['payment_statuses_filter']
        assert 'need_cvn' in data['payment_statuses_filter']


@pytest.mark.filldb(user_phones='for_experiments')
@pytest.mark.parametrize(
    'user_id,phone_id,phone_number,user_agent,expected_experiments',
    [
        (
            'c1768abf8e2c44d0bc90616d8ec31cd4',
            '5a05cf730bb9aa5ea83e1f8a',
            '+79036842891',
            '',
            [
                'simple',
                'simple_active',
                'percent_of_users_all',
                'percent_of_users_0-50',
            ],
        ),
        (
            '23328bd976e84153a4af51f44e86220b',
            '5a049a142df923ad4515ce04',
            '+79036848825',
            '',
            [
                'phone_id_last_digits',
                'simple',
                'simple_active',
                'percent_of_users_all',
                'percent_of_users_0-50',
            ],
        ),
        (
            '73f59768241048879a5ce69d1368cf9d',
            '5a05d4d20bb9aa5ea83e1f8c',
            '+79036542999',
            '',
            [
                'simple',
                'simple_active',
                'percent_of_users_all',
                'percent_of_users_0-50',
            ],
        ),
        (
            'eae3e4e89e4e4cf58026e612f2ea2d37',
            '5a06f0572df923bff00c8ae9',
            '+79126783535',
            '',
            [
                'simple',
                'simple_active',
                'vips',
                'percent_of_vips',
                'vips_or_taxi',
                'percent_of_users_all',
            ],
        ),
        (
            '38f7e46bd19f4d86b60f379fe727f119',
            '5a05d0670bb9aa5ea83e1f8b',
            '+79036542002',
            '',
            [
                'simple',
                'simple_active',
                'vips_or_taxi',
                'percent_of_users_all',
            ],
        ),
        (
            'c6e537dd5a3f4036a317cdfc529128e5',
            '5a07329c3a40367bc10e3c3f',
            '+79267202552',
            'ru.yandex.ytaxi/4.02.11463 '
            '(iPhone; iPhone5,2; iOS 10.3.3; Darwin)',
            [
                'simple',
                'simple_active',
                'percent_of_users_0-50',
                'percent_of_users_all',
                'iphone_platform',
            ],
        ),
        (
            'ea9efbab7d9446cc8a38e11a2f9ab9c4',
            '5a0d4fdba8070a73821eb772',
            '+79269898551',
            '',
            ['simple', 'simple_active', 'percent_of_users_all', 'all_yandex'],
        ),
    ],
)
@LAUNCH_USE_INPUT_FIELDS
def test_launch_experiments(
        taxi_protocol,
        mockserver,
        user_id,
        phone_id,
        phone_number,
        user_agent,
        expected_experiments,
        use_input_fields,
):
    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        assert set(request.query_string.decode().split('&')) == {
            'method=oauth',
            'userip=',
            'format=json',
            'dbfields=subscription.suid.669',
            'aliases=1%2C10%2C16',
            'oauth_token=test_token',
            'getphones=bound',
            'get_login_id=yes',
            'phone_attributes=102%2C107%2C4',
            'attributes=1015',
        }
        return {
            'uid': {'value': '123'},
            'status': {'value': 'VALID'},
            'oauth': {'scope': 'yataxi:read yataxi:write yataxi:pay'},
            'aliases': {'10': 'phne-edcsaypw'},
            'phones': [
                {'attributes': {'102': phone_number}, 'id': '1111'},
                {
                    'attributes': {'102': phone_number, '107': '1'},
                    'id': '2222',
                },
            ],
        }

    request_headers = ''
    if not user_agent == '':
        request_headers = {'User-Agent': user_agent}

    response = taxi_protocol.post(
        '3.0/launch',
        {'id': user_id, 'authorized': True, 'phone_id': phone_id},
        bearer='test_token',
        headers=request_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert set(data['experiments']) == set(expected_experiments)


def test_launch_invalid_body(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/launch', data=str('\xa0\xa1'), bearer='test_token',
    )
    assert response.status_code == 400
    data = response.json()
    assert data['error']['text'] == 'Invalid request_body format'


def test_launch_order_for_another_init_distance_meters(taxi_protocol):
    response = taxi_protocol.post('3.0/launch', {})
    assert response.status_code == 200
    data = response.json()
    assert data['order_for_another_init_distance_meters'] == 1000


@pytest.mark.now('2018-05-25T00:00:15+0000')
@pytest.mark.config(
    GDPR_COUNTRIES=['us', 'fr'],
    NEED_ACCEPT_GDPR=True,
    EULA_POLICY_TTL={'__default__': 86400},
    LOCALES_APPLICATION_PREFIXES={
        'yango_android': 'yango',
        'yango_iphone': 'yango',
    },
)
@pytest.mark.translations(
    client_messages={
        'gdpr.title': {'ru': 'gdpr.title'},
        'gdpr.text': {'ru': 'gdpr'},
        'gdpr.url.title': {'ru': 'default url title'},
        'gdpr.url.content': {'ru': 'default url content'},
        'gdpr.title.us': {'ru': 'gdpr.usa.title'},
        'gdpr.text.us': {'ru': 'gdpr.usa'},
        'gdpr.url.title.us': {'ru': 'gdpr us url title'},
        'gdpr.url.content.us': {'ru': 'gdpr us url content'},
        'yango.gdpr.title': {'ru': 'yango.gdpr.title'},
        'yango.gdpr.text': {'ru': 'yango.gdpr'},
        'yango.gdpr.url.title': {'ru': 'yango.default url title'},
        'yango.gdpr.url.content': {'ru': 'yango.default url content'},
        'yango.gdpr.title.us': {'ru': 'yango.gdpr.usa.title'},
        'yango.gdpr.text.us': {'ru': 'yango.gdpr.usa'},
        'yango.gdpr.url.title.us': {'ru': 'yango.gdpr us url title'},
        'yango.gdpr.url.content.us': {'ru': 'yango.gdpr us url content'},
    },
)
@pytest.mark.parametrize(
    'user_id,phone_id,user_ip,user_agent,accept_requests,'
    'expected_gdpr_text,expect_gdpr,updated',
    [
        # not authorized
        (None, None, '87.250.250.242', None, None, None, False, None),
        (None, None, '173.194.222.101', None, None, 'gdpr.usa', False, None),
        (None, None, '127.0.0.1', None, None, 'gdpr', False, None),
        (None, None, '89.185.38.136', None, None, 'gdpr', False, None),
        (None, None, '::ffff:87.250.250.242', None, None, None, False, None),
        (
            None,
            None,
            '::ffff:173.194.222.101',
            None,
            None,
            'gdpr.usa',
            False,
            None,
        ),
        (None, None, '::ffff:127.0.0.1', None, None, 'gdpr', False, None),
        (None, None, '::ffff:89.185.38.136', None, None, 'gdpr', False, None),
        # no requests
        (
            'user_empty_6451b855d9a3e640215c3',
            '000000000000000000000001',
            '87.250.250.242',
            None,
            None,
            None,
            False,
            None,
        ),
        (
            'user_empty_6451b855d9a3e640215c3',
            '000000000000000000000001',
            '173.194.222.101',
            None,
            None,
            'gdpr.usa',
            False,
            None,
        ),
        (
            'user_gdpr_16451b855d9a3e640215c3',
            '000000000000000000000002',
            '87.250.250.242',
            None,
            None,
            None,
            True,
            False,
        ),
        (
            'user_gdpr_16451b855d9a3e640215c3',
            '000000000000000000000002',
            '173.194.222.101',
            None,
            None,
            None,
            True,
            False,
        ),
        # gdpr request
        (None, None, '87.250.250.242', None, 'gdpr', None, False, None),
        (None, None, '173.194.222.101', None, 'gdpr', 'gdpr.usa', False, None),
        (
            'user_empty_6451b855d9a3e640215c3',
            '000000000000000000000001',
            '87.250.250.242',
            None,
            'gdpr',
            None,
            True,
            True,
        ),
        (
            'user_empty_6451b855d9a3e640215c3',
            '000000000000000000000001',
            '173.194.222.101',
            None,
            'gdpr',
            None,
            True,
            True,
        ),
        (
            'user_gdpr_16451b855d9a3e640215c3',
            '000000000000000000000002',
            '87.250.250.242',
            None,
            'gdpr',
            None,
            True,
            False,
        ),
        (
            'user_gdpr_16451b855d9a3e640215c3',
            '000000000000000000000002',
            '173.194.222.101',
            None,
            'gdpr',
            None,
            True,
            False,
        ),
        # yango gdpr
        (
            None,
            None,
            '173.194.222.101',
            'yango/3.78.1.15753 Android/7.1.2 (Xiaomi; Mi A1)',
            'gdpr',
            'yango.gdpr.usa',
            False,
            None,
        ),
    ],
)
@pytest.mark.filldb(users='for_eula', user_phones='for_eula')
@LAUNCH_USE_INPUT_FIELDS
def test_launch_eula(
        user_id,
        phone_id,
        user_ip,
        user_agent,
        accept_requests,
        expected_gdpr_text,
        expect_gdpr,
        updated,
        mockserver,
        taxi_protocol,
        db,
        now,
        use_input_fields,
):

    user_phone = (user_id or '') + '_phone'

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        return {
            'uid': {'value': user_id},
            'status': {'value': 'VALID'},
            'oauth': {'scope': 'yataxi:read yataxi:write yataxi:pay'},
            'aliases': {'10': 'phne-edcsaypw'},
            'phones': [
                {'attributes': {'102': user_phone}, 'id': '1111'},
                {'attributes': {'102': user_phone, '107': '1'}, 'id': '2222'},
            ],
        }

    request = {}
    if user_id is not None:
        request['id'] = user_id
        request['phone_id'] = phone_id
    if accept_requests:
        request['accepted'] = [{'type': 'gdpr'}]
    response = taxi_protocol.post(
        '3.0/launch',
        request,
        bearer='test_token',
        x_real_ip=user_ip,
        headers={'Accept-Language': 'ru', 'User-Agent': user_agent},
    )
    user_phone_obj = (
        db.user_phones.find_one({'phone': user_phone, 'type': 'yandex'}) or {}
    )
    client_id = 'user:%s:%s:gdpr' % (user_phone_obj.get('_id', ''), user_id)
    gdpr = db.accepted_eulas.find_one({'_id': client_id})
    if expect_gdpr:
        assert updated is not None, 'invalid test configuration'
        assert gdpr is not None
        assert gdpr['eula'] == 'gdpr'
        if updated:
            assert gdpr['updated'] == now
        else:
            assert isinstance(gdpr['updated'], datetime.datetime)
            assert gdpr['updated'] != now
    else:
        assert gdpr is None
        assert updated is None, 'invalid test configuration'

    assert response.status_code == 200
    response = response.json()
    if expected_gdpr_text is not None:
        assert 'need_acceptance' in response
        eulas = response['need_acceptance']
        assert list(eulas)
        assert len(eulas) == 1
        gdpr = eulas[0]
        assert gdpr['type'] == 'gdpr'
        assert gdpr['title'] is not None
        assert gdpr['content'] == expected_gdpr_text
        assert gdpr['header_image_tag'] == 'image_gdpr'
        assert gdpr['ttl'] == 86400
    else:
        assert 'need_acceptance' not in response


def test_multiorder_launch_no_orders_state_experiment_off(
        taxi_protocol, load_json, blackbox_service, pricing_data_preparer,
):
    make_order(taxi_protocol, load_json)
    launch_resp = make_launch_request(taxi_protocol, ['multiorder'])
    assert launch_resp.get('orders_state') is None  # experiment is off


@pytest.mark.config(MULTIORDER_ENABLED_IN_LAUNCH=True)
def test_multiorder_launch_no_orders_state_not_supported(
        taxi_protocol, load_json, blackbox_service, pricing_data_preparer,
):
    make_order(taxi_protocol, load_json)
    launch_resp = make_launch_request(taxi_protocol, ['not_multiorder'])
    assert launch_resp.get('orders_state') is None


def check_can_make_more_orders(taxi_protocol, expected, **http_kwargs):
    launch_resp = make_launch_request(
        taxi_protocol, ['multiorder'], **http_kwargs,
    )
    orders_state = launch_resp['orders_state']
    assert orders_state['can_make_more_orders'] == expected


def check_auth_and_cmmo(
        taxi_protocol, expected_cmmo, auth, user_id, **http_kwargs,
):
    launch_resp = make_launch_request(
        taxi_protocol, ['multiorder'], user_id, **http_kwargs,
    )
    assert launch_resp['authorized'] == auth
    orders_state = launch_resp['orders_state']
    assert orders_state['can_make_more_orders'] == expected_cmmo


@pytest.mark.config(
    MAX_MULTIORDER_CONCURRENT_ORDERS=2,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_ENABLED_IN_LAUNCH=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
)
@LAUNCH_USE_INPUT_FIELDS
def test_multiorder_launch_orders_state_can_make_orders(
        taxi_protocol,
        load_json,
        blackbox_service,
        pricing_data_preparer,
        use_input_fields,
):

    # no order, allowed
    check_can_make_more_orders(taxi_protocol, 'allowed')
    make_order(taxi_protocol, load_json)

    # have 1 order, limit 2, allowed to make more
    check_can_make_more_orders(taxi_protocol, 'allowed')
    make_order(taxi_protocol, load_json)

    # have 2 orders, can't make more
    check_can_make_more_orders(taxi_protocol, 'disallowed')


FRANCE_IP = '89.185.38.136'
RUSSIA_IP = '2.60.1.1'
DUMMY_IP = '0.0.0.0'


@pytest.mark.config(
    MAX_MULTIORDER_CONCURRENT_ORDERS=3,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_ENABLED_IN_LAUNCH=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
)
@pytest.mark.parametrize(
    'remote_ip,allowed_countries,expected_res',
    [
        (FRANCE_IP, None, 'allowed'),
        (FRANCE_IP, ['ru', 'us'], 'disallowed'),
        (FRANCE_IP, ['fr'], 'allowed'),
    ],
)
@LAUNCH_USE_INPUT_FIELDS
def test_multiorder_by_country(
        remote_ip,
        allowed_countries,
        expected_res,
        taxi_protocol,
        load_json,
        config,
        blackbox_service,
        pricing_data_preparer,
        use_input_fields,
):

    use_by_country_check = allowed_countries is not None
    config.set_values(dict(MULTIORDER_ENABLE_BY_COUNTRY=use_by_country_check))
    config.set_values(dict(MULTIORDER_ENABLED_COUNTRIES=allowed_countries))

    check_can_make_more_orders(taxi_protocol, 'allowed', x_real_ip=remote_ip)
    make_order(taxi_protocol, load_json)
    check_can_make_more_orders(
        taxi_protocol, expected_res, x_real_ip=remote_ip,
    )


@pytest.mark.config(
    MAX_MULTIORDER_CONCURRENT_ORDERS=1,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_ENABLED_IN_LAUNCH=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
)
@LAUNCH_USE_INPUT_FIELDS
def test_multiorder_launch_orders_state_no_can_make_orders(
        taxi_protocol,
        config,
        load_json,
        blackbox_service,
        pricing_data_preparer,
        use_input_fields,
):
    make_order(taxi_protocol, load_json)

    # allowed is a fallback when experiment is disabled
    check_can_make_more_orders(taxi_protocol, 'allowed')


USER_PHONE_ID = bson.ObjectId('594baaba779fb30a39a5381e')


@pytest.mark.config(
    MULTIORDER_ENABLING_MIN_COMPLETE_ORDERS_N=2,
    MAX_MULTIORDER_CONCURRENT_ORDERS=3,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_ENABLED_IN_LAUNCH=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS_CHECK_COMPLETE_ORDERS=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
    APPLICATION_MAP_BRAND={'__default__': 'yataxi', 'android': 'yataxi'},
)
@pytest.mark.parametrize(
    'complete,can_make_more',
    [(0, 'disallowed'), (1, 'disallowed'), (2, 'allowed'), (3, 'allowed')],
)
@pytest.mark.parametrize('set_total', [True, False])
@LAUNCH_USE_INPUT_FIELDS
def test_multiorder_launch_can_make_more_antifraud(
        taxi_protocol,
        load_json,
        blackbox_service,
        db,
        complete,
        can_make_more,
        set_total,
        pricing_data_preparer,
        use_input_fields,
):
    update = {'$set': {'stat.complete': complete}}
    if complete == 0:
        update = {'$unset': {'stat': True}}
    db.user_phones.find_and_modify({'_id': USER_PHONE_ID}, update)
    if set_total:
        db.user_phones.find_and_modify(
            {'_id': USER_PHONE_ID}, {'$set': {'stat.total': complete}},
        )

    check_can_make_more_orders(taxi_protocol, 'allowed')
    make_order(taxi_protocol, load_json)
    check_can_make_more_orders(taxi_protocol, can_make_more)


@pytest.mark.config(
    MAX_CONCURRENT_ORDERS=1,
    MAX_MULTIORDER_CONCURRENT_ORDERS=2,
    MULTIORDER_ENABLED_IN_LAUNCH=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
)
def test_multiorder_launch_orders_state_no_limits(
        taxi_protocol,
        config,
        load_json,
        blackbox_service,
        pricing_data_preparer,
):

    make_order(taxi_protocol, load_json)
    check_can_make_more_orders(taxi_protocol, 'disallowed')


@pytest.mark.config(
    MAX_MULTIORDER_CONCURRENT_ORDERS=3,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_ENABLED_IN_LAUNCH=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
)
@pytest.mark.parametrize(
    'user_id,auth,can_make_more',
    [
        ('None', False, 'disallowed'),
        ('no_such_id', False, 'disallowed'),
        # None means to use default user id
        (None, True, 'allowed'),
    ],
)
@LAUNCH_USE_INPUT_FIELDS
def test_multiorder_authorized_cmm_check(
        taxi_protocol,
        config,
        load_json,
        blackbox_service,
        user_id,
        auth,
        can_make_more,
        use_input_fields,
):
    check_auth_and_cmmo(taxi_protocol, can_make_more, auth, user_id)


def test_client_geo_disabled(taxi_protocol, db):
    taxi_protocol.invalidate_caches()
    response = taxi_protocol.post('3.0/launch', {})
    assert response.status_code == 200
    assert response.json()['client_geo_params'] == {'enabled': False}


@pytest.mark.user_experiments('client_geo')
def test_client_geo_enabled(taxi_protocol):
    taxi_protocol.invalidate_caches()
    response = taxi_protocol.post('3.0/launch', {})
    assert response.status_code == 200
    assert response.json()['client_geo_params'] == {
        'clientgeo_disable_distance': 900,
        'enabled': True,
        'track_in_background': False,
        'false_count': 10,
        'tracking_rate_battery_state': {'full': 10, 'half': 20, 'empty': 30},
        'request': {'show': False},
    }


@pytest.mark.user_experiments('client_geo', 'hacked_sdc')
def test_client_geo_enabled_for_sdc(taxi_protocol):
    taxi_protocol.invalidate_caches()
    response = taxi_protocol.post('3.0/launch', {})
    assert response.status_code == 200
    assert response.json()['client_geo_params'] == {
        'clientgeo_disable_distance': 900,
        'enabled': True,
        'track_in_background': False,
        'false_count': 10,
        'tracking_rate_battery_state': {'full': 10, 'half': 20, 'empty': 30},
        'request': {'show': False},
    }


@pytest.mark.config(CLIENT_GEO_DISABLED_FOR_SDC=True)
@pytest.mark.user_experiments('client_geo', 'hacked_sdc')
def test_client_geo_disabled_for_sdc(taxi_protocol):
    taxi_protocol.invalidate_caches()
    response = taxi_protocol.post('3.0/launch', {})
    assert response.status_code == 200
    assert response.json()['client_geo_params'] == {'enabled': False}


@pytest.mark.user_experiments('client_geo', 'client_geo_request')
def test_client_geo_request_show(taxi_protocol, mockserver):
    taxi_protocol.invalidate_caches()
    response = taxi_protocol.post('3.0/launch', {})
    assert response.status_code == 200
    assert response.json()['client_geo_params'] == {
        'clientgeo_disable_distance': 900,
        'enabled': True,
        'track_in_background': False,
        'false_count': 10,
        'tracking_rate_battery_state': {'full': 10, 'half': 20, 'empty': 30},
        'request': {'show': True, 'max_requests': 3, 'version': 'v1.0'},
    }


def get_launch_orders_state(taxi_protocol):
    resp = make_launch_request(taxi_protocol, ['multiorder'])
    return resp.get('orders_state')


def get_launch_order_state(taxi_protocol):
    resp = make_launch_request(taxi_protocol, [])
    return resp


TEST_DEVICE_ID = 'test_device_id'
TEST_USER_ID = '536b24fa2816451b855d9a3e640215c3'
TEST_USER_PHONE_ID = '594baaba779fb30a39a5381e'


def make_launch_request(
        taxi_protocol,
        supported_features,
        user_id=None,
        authorized=False,
        device_id=None,
        phone_id=None,
        yandex_uuid=None,
        has_ya_plus=None,
        has_cashback_plus=None,
        arg_uuid=None,
        **http_kwargs,
):
    if not user_id:
        user_id = TEST_USER_ID
        authorized = True
        device_id = TEST_DEVICE_ID
        phone_id = TEST_USER_PHONE_ID
    elif user_id == 'None':
        user_id = None
    args = ''
    if arg_uuid is not None:
        args = '?uuid=' + arg_uuid
    response = taxi_protocol.post(
        '3.0/launch' + args,
        {
            'id': user_id,
            'supported_features': supported_features,
            'device_id': device_id,
            'authorized': authorized,
            'phone_id': phone_id,
            'yandex_uuid': yandex_uuid,
            'has_ya_plus': has_ya_plus,
            'has_cashback_plus': has_cashback_plus,
        },
        bearer='test_token',
        **http_kwargs,
    )
    assert response.status_code == 200
    return response.json()


def make_order(taxi_protocol, load_json, **http_kwargs):
    request = load_json('basic_request.json')
    draft_resp = taxi_protocol.post('3.0/orderdraft', request, **http_kwargs)
    assert draft_resp.status_code == 200
    order_id = draft_resp.json()['orderid']

    commit_request = {'id': request['id'], 'orderid': order_id}

    resp = taxi_protocol.post('3.0/ordercommit', commit_request)
    assert resp.status_code == 200
    return order_id


def test_invalid_scope(taxi_protocol, db, blackbox_service):
    blackbox_service.set_token_info(
        'test_token',
        '123',
        phones=['*+72222222222'],
        scope='yataxi:yauber_request',
    )
    response = taxi_protocol.post('/3.0/launch', json={}, bearer='test_token')
    response = response.json()
    assert not response['authorized']
    assert not response['token_valid']


@pytest.mark.config(LAUNCH_OBTAIN_DATA_FROM_HEADERS=True)
@LAUNCH_USE_INPUT_FIELDS
@pytest.mark.parametrize(
    'header_uuid,arg_uuid',
    [
        (
            '289146501a14f6cf5aca0a0000000aaa',
            '289146501a14f6cf5aca0a0000000aaa',
        ),
        ('fake_uuid', '289146501a14f6cf5aca0a0000000aaa'),
    ],
)
def test_use_input_fields(
        taxi_protocol, testpoint, header_uuid, arg_uuid, use_input_fields,
):
    user_id = TEST_USER_ID
    authorized = True
    device_id = 'new_test_device_id'
    phone_id = 'cccbaaba779fb30a39a5381e'
    yandex_uuid = '289146501a14f6cf5aca0a0000000aaa'
    has_ya_plus = True
    has_cashback_plus = True

    @testpoint('ResultUserFields')
    def result_user_fields(data):
        if use_input_fields:
            assert data == {
                'user_id': TEST_USER_ID,
                'authorized': authorized,
                'device_id': device_id,
                'phone_id': phone_id,
                'yandex_uuid': yandex_uuid,
                'has_ya_plus': has_ya_plus,
                'has_cashback_plus': has_cashback_plus,
            }
        else:
            assert data == {
                'user_id': TEST_USER_ID,
                'authorized': True,
                'device_id': TEST_DEVICE_ID,
                'phone_id': TEST_USER_PHONE_ID,
                'yandex_uuid': '289146501a14f6cf5aca8a5885022cfc',
                'has_ya_plus': False,
                'has_cashback_plus': False,
            }

    headers = {'X-AppMetrica-UUID': header_uuid}
    make_launch_request(
        taxi_protocol,
        [],
        user_id=user_id,
        authorized=authorized,
        device_id=device_id,
        phone_id=phone_id,
        yandex_uuid=yandex_uuid,
        has_ya_plus=has_ya_plus,
        has_cashback_plus=has_cashback_plus,
        arg_uuid=arg_uuid,
        headers=headers,
    )
    assert result_user_fields.times_called == 1


@pytest.mark.filldb(tariff_settings='for_referrals')
@pytest.mark.config(REFERRALS_CONFIG={'creator': {'min_card_orders': 0}})
@pytest.mark.parametrize(
    'city_id,home_zone,can_generate',
    [
        ('Москва', 'moscow', True),
        ('Тула', 'tula', False),
        ('Москва', '', True),
        ('Тула', '', False),
        ('', 'moscow', True),
        ('', 'tula', False),
        ('', '', False),
        pytest.param(
            'Москва',
            'moscow',
            True,
            marks=pytest.mark.config(REFERRALS_ENABLED_BY_BRAND=['yataxi']),
            id='referrals_enabled_for_yataxi',
        ),
        pytest.param(
            'Москва',
            'moscow',
            False,
            marks=pytest.mark.config(REFERRALS_ENABLED_BY_BRAND=['yango']),
            id='referrals_disabled_for_yataxi',
        ),
    ],
)
@LAUNCH_USE_INPUT_FIELDS
def test_can_generate_referrals(
        taxi_protocol,
        db,
        blackbox_service,
        city_id,
        home_zone,
        can_generate,
        use_input_fields,
):
    user_id = TEST_USER_ID
    user_doc = db.users.find_one({'_id': user_id})
    db.user_phones.update(
        {'_id': user_doc['phone_id']},
        {
            '$set': {
                'last_order_city_id': city_id,
                'last_order_nearest_zone': home_zone,
            },
        },
    )

    response = make_launch_request(taxi_protocol, [])
    assert response.get('can_generate_referrals', False) == can_generate


@pytest.mark.filldb(tariff_settings='for_referrals')
@pytest.mark.parametrize('stat_complete', [0, 1, 2, 3])
@pytest.mark.parametrize('stat_complete_card', [0, 1, 2, 3])
@pytest.mark.parametrize('exp3', [True, False])
@LAUNCH_USE_INPUT_FIELDS
def test_can_generate_referrals_with_referral_orders_card(
        taxi_protocol,
        db,
        blackbox_service,
        experiments3,
        load_json,
        stat_complete,
        stat_complete_card,
        exp3,
        use_input_fields,
):
    if stat_complete < stat_complete_card:
        return

    if exp3:
        experiments3.add_experiments_json(
            load_json('exp3_referral_orders_by_card.json'),
        )
        can_generate = stat_complete_card >= MIN_CARD_ORDERS_DEFAULT
    else:
        can_generate = stat_complete >= MIN_CARD_ORDERS_DEFAULT

    user_id = TEST_USER_ID
    user_doc = db.users.find_one({'_id': user_id})
    db.user_phones.update(
        {'_id': user_doc['phone_id']},
        {
            '$set': {
                'stat': {
                    'complete': stat_complete,
                    'complete_card': stat_complete_card,
                },
            },
        },
    )

    response = make_launch_request(taxi_protocol, [])
    assert response.get('can_generate_referrals', False) == can_generate


def make_afs_is_spammer_true_response_builder(add_sec_to_block_time=0):
    def response_builder(now):
        blocked_until = now + datetime.timedelta(seconds=add_sec_to_block_time)
        return {
            'is_spammer': True,
            'blocked_until': utils.timestring(blocked_until),
        }

    return response_builder


def make_afs_is_spammer_response_builder(add_sec_to_block_time):
    def response_builder(now):
        if add_sec_to_block_time is None:
            return {'is_spammer': False}
        blocked_until = now + datetime.timedelta(seconds=add_sec_to_block_time)
        return {
            'is_spammer': True,
            'blocked_until': utils.timestring(blocked_until),
        }

    return response_builder


def afs_is_spammer_true_response_no_time_builder(_):
    return {'is_spammer': True}


def afs_is_spammer_false_response_builder(_):
    return {'is_spammer': False}


MUTLTIORDER_DISALLOWED_SPAMMER_ERR_BASE = (
    'Мультизаказ недоступен из-за частых отмен'
)
UNBLOCK_DUR = ', попробуйте через %(unblock_after_duration)s'


def make_multiorder_disallowed_in_duration_err(duration):
    prefix = MUTLTIORDER_DISALLOWED_SPAMMER_ERR_BASE + ', попробуйте через '
    return prefix + duration


@pytest.mark.translations(
    client_messages={
        'multiorder.warn_cant_make_more_orders_for_spammer': {
            'ru': MUTLTIORDER_DISALLOWED_SPAMMER_ERR_BASE,
        },
        'multiorder.warn_cant_make_more_orders_for_spammer_with_duration': {
            'ru': MUTLTIORDER_DISALLOWED_SPAMMER_ERR_BASE + UNBLOCK_DUR,
        },
    },
    tariff={
        'round.minute': {'ru': '%(value).0f мин'},
        'round.hours': {'ru': '%(value).0f ч'},
    },
)
@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_ENABLED_IN_LAUNCH=True,
    MULTIORDER_ANTIFRAUD_CHECK_IS_NOT_SPAMMER=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
    MULTIORDER_ANTIFRAUD_FOR_CAN_MAKE_MORE_ORDERS=True,
    APPLICATION_MAP_BRAND={'__default__': 'yataxi', 'android': 'yataxi'},
)
@pytest.mark.now('2018-11-20T11:00:00+0300')
@pytest.mark.parametrize(
    'afs_resp_builder,exp_reason',
    [
        (
            make_afs_is_spammer_true_response_builder(0),
            make_multiorder_disallowed_in_duration_err('1 мин'),
        ),
        (
            make_afs_is_spammer_true_response_builder(-1),
            make_multiorder_disallowed_in_duration_err('1 мин'),
        ),
        (
            make_afs_is_spammer_true_response_builder(60 * 60 * 4),
            make_multiorder_disallowed_in_duration_err('4 ч'),
        ),
        (
            afs_is_spammer_true_response_no_time_builder,
            MUTLTIORDER_DISALLOWED_SPAMMER_ERR_BASE,
        ),
        (afs_is_spammer_false_response_builder, None),
    ],
)
@LAUNCH_USE_INPUT_FIELDS
def test_multiorder_is_spammer_check(
        taxi_protocol,
        load_json,
        mockserver,
        now,
        blackbox_service,
        afs_resp_builder,
        exp_reason,
        pricing_data_preparer,
        use_input_fields,
):
    make_order(taxi_protocol, load_json)

    @mockserver.json_handler('/antifraud/client/user/is_spammer')
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'is_multiorder': True,
            'user_id': TEST_USER_ID,
            'user_phone_id': TEST_USER_PHONE_ID,
            'device_id': TEST_DEVICE_ID,
        }
        return afs_resp_builder(now)

    os = get_launch_orders_state(taxi_protocol)
    if exp_reason is None:
        assert os['can_make_more_orders'] == 'allowed'
        assert 'no_more_orders_reason' not in os
    else:
        assert os['can_make_more_orders'] == 'disallowed'
        assert os['no_more_orders_reason'] == exp_reason


@pytest.mark.translations(
    client_messages={
        'multiorder.warn_cant_make_more_orders_for_spammer': {
            'ru': MUTLTIORDER_DISALLOWED_SPAMMER_ERR_BASE,
        },
        'multiorder.warn_cant_make_more_orders_for_spammer_with_duration': {
            'ru': MUTLTIORDER_DISALLOWED_SPAMMER_ERR_BASE + UNBLOCK_DUR,
        },
    },
    tariff={
        'round.minute': {'ru': '%(value).0f мин'},
        'round.hours': {'ru': '%(value).0f ч'},
    },
)
@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=False,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_ENABLED_IN_LAUNCH=True,
    MULTIORDER_ANTIFRAUD_CHECK_IS_NOT_SPAMMER=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
    MULTIORDER_ANTIFRAUD_FOR_CAN_MAKE_MORE_ORDERS=True,
)
@pytest.mark.now('2018-11-20T11:00:00+0300')
@pytest.mark.parametrize(
    'afs_resp_builder',
    [
        (make_afs_is_spammer_true_response_builder(0)),
        (make_afs_is_spammer_true_response_builder(-1)),
        (make_afs_is_spammer_true_response_builder(60 * 60 * 4)),
        afs_is_spammer_true_response_no_time_builder,
        afs_is_spammer_false_response_builder,
    ],
)
@LAUNCH_USE_INPUT_FIELDS
def test_multiorder_is_spammer_check_is_spammer_disabled_in_client(
        taxi_protocol,
        load_json,
        mockserver,
        now,
        blackbox_service,
        afs_resp_builder,
        pricing_data_preparer,
        use_input_fields,
):
    make_order(taxi_protocol, load_json)

    @mockserver.json_handler('/antifraud/client/user/is_spammer')
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'is_multiorder': True,
            'user_id': TEST_USER_ID,
            'user_phone_id': TEST_USER_PHONE_ID,
            'device_id': TEST_DEVICE_ID,
        }
        return afs_resp_builder(now)

    os = get_launch_orders_state(taxi_protocol)
    assert os['can_make_more_orders'] == 'allowed'
    assert 'no_more_orders_reason' not in os


@pytest.mark.translations(
    client_messages={
        'multiorder.warn_cant_make_more_orders_for_spammer': {
            'ru': MUTLTIORDER_DISALLOWED_SPAMMER_ERR_BASE,
        },
        'multiorder.warn_cant_make_more_orders_for_spammer_with_duration': {
            'ru': MUTLTIORDER_DISALLOWED_SPAMMER_ERR_BASE + UNBLOCK_DUR,
        },
    },
    tariff={
        'round.minute': {'ru': '%(value).0f мин'},
        'round.hours': {'ru': '%(value).0f ч'},
    },
)
@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_ENABLED_IN_LAUNCH=True,
    MULTIORDER_ANTIFRAUD_CHECK_IS_NOT_SPAMMER=False,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
    MULTIORDER_ANTIFRAUD_FOR_CAN_MAKE_MORE_ORDERS=True,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'timeout': 100, 'retries': 1},
        'launch': {'use_afs': True, 'timeout': 200, 'retries': 2},
    },
)
@pytest.mark.now('2018-11-20T11:00:00+0300')
@pytest.mark.parametrize(
    'afs_resp_builder,time_offset',
    [
        (make_afs_is_spammer_response_builder, 0),
        (make_afs_is_spammer_response_builder, -1),
        (make_afs_is_spammer_response_builder, 60 * 60 * 4),
        (make_afs_is_spammer_response_builder, None),
    ],
)
@LAUNCH_USE_INPUT_FIELDS
def test_is_spammer_block_info_check(
        taxi_protocol,
        load_json,
        mockserver,
        now,
        blackbox_service,
        afs_resp_builder,
        time_offset,
        use_input_fields,
):
    @mockserver.json_handler('/antifraud/client/user/is_spammer/launch')
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'is_multiorder': False,
            'user_id': TEST_USER_ID,
            'user_phone_id': TEST_USER_PHONE_ID,
            'device_id': TEST_DEVICE_ID,
        }
        # device_id
        return afs_resp_builder(time_offset)(now)

    os = get_launch_order_state(taxi_protocol)
    if time_offset is not None:
        assert 'blocked' in os
        assert 'blocked' in os['blocked']
        assert os['blocked']['blocked'] == (
            now + datetime.timedelta(seconds=time_offset)
        ).strftime(format='%Y-%m-%dT%H:%M:%S+0000')
    else:
        assert 'blocked' not in os


@pytest.mark.translations(
    client_messages={
        'multiorder.warn_cant_make_more_orders_for_spammer': {
            'ru': MUTLTIORDER_DISALLOWED_SPAMMER_ERR_BASE,
        },
        'multiorder.warn_cant_make_more_orders_for_spammer_with_duration': {
            'ru': MUTLTIORDER_DISALLOWED_SPAMMER_ERR_BASE + UNBLOCK_DUR,
        },
    },
    tariff={
        'round.minute': {'ru': '%(value).0f мин'},
        'round.hours': {'ru': '%(value).0f ч'},
    },
)
@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_ENABLED_IN_LAUNCH=True,
    MULTIORDER_ANTIFRAUD_CHECK_IS_NOT_SPAMMER=False,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
    MULTIORDER_ANTIFRAUD_FOR_CAN_MAKE_MORE_ORDERS=True,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'timeout': 100, 'retries': 1},
        'launch': {'use_afs': True, 'timeout': 200, 'retries': 2},
    },
)
@pytest.mark.parametrize('response_code', [500, 400, 403])
def test_antifraud_affecting(
        taxi_protocol, load_json, mockserver, blackbox_service, response_code,
):
    @mockserver.handler('/antifraud/client/user/is_spammer/launch')
    def mock_detect_invalid(request):
        return mockserver.make_response(
            '{"code":' + str(response_code) + '}', response_code,
        )

    get_launch_order_state(taxi_protocol)
    get_launch_orders_state(taxi_protocol)


@pytest.mark.config(GDPR_COUNTRIES=['ua', 'fr'])
@pytest.mark.parametrize(
    'remote_ip,expected_sync_flag',
    [(RUSSIA_IP, False), (FRANCE_IP, True), (DUMMY_IP, False)],
)
def test_disable_background_data_sync(
        taxi_protocol, blackbox_service, remote_ip, expected_sync_flag,
):
    response = make_launch_request(taxi_protocol, [], x_real_ip=remote_ip)
    assert (
        response['parameters']['disable_background_data_sync']
        == expected_sync_flag
    )


@pytest.fixture
def blackbox_mockserver(mockserver):
    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        return {
            'uid': {'value': '123'},
            'status': {'value': 'VALID'},
            'oauth': {'scope': 'yataxi:read yataxi:write yataxi:pay'},
            'aliases': {'10': 'phne-edcsaypw'},
            'phones': [
                {'attributes': {'102': '+71111111111'}, 'id': '1111'},
                {
                    'attributes': {'102': '+72222222222', '107': '1'},
                    'id': '2222',
                },
            ],
        }


@pytest.mark.parametrize(
    'passenger_profile_response',
    [{'first_name': 'Алексей', 'rating': '4.90'}, {'rating': '5'}],
    ids=['full_response', 'rating_only'],
)
@pytest.mark.config(TVM_ENABLED=False)
@LAUNCH_USE_INPUT_FIELDS
def test_launch_with_passenger_profile(
        taxi_protocol,
        mockserver,
        blackbox_mockserver,
        experiments3,
        load_json,
        passenger_profile_response,
        use_input_fields,
):
    experiments3.add_experiments_json(load_json('exp3_passenger_profile.json'))

    @mockserver.json_handler('/passenger_profile/passenger-profile/v1/profile')
    def mock_passenger_profile(request):
        def _parse_app_vars(application_header: str):
            result = {}
            for key_value in application_header.split(','):
                key, value = key_value.split('=')
                result[key] = value
            return result

        expected_app_vars = {
            'app_brand': 'yataxi',
            'app_name': 'iphone',
            'app_build': 'release',
            'platform_ver1': '12',
            'platform_ver2': '2',
            'app_ver1': '4',
            'app_ver2': '81',
            'app_ver3': '30920',
        }
        assert (
            _parse_app_vars(request.headers['X-Request-Application'])
            == expected_app_vars
        )
        return passenger_profile_response

    headers = {
        'User-Agent': (
            'ru.yandex.ytaxi/4.81.30920 (iPhone; iPhone6,2; iOS 12.2; Darwin)'
        ),
        'X-Yandex-UID': '4003514353',
    }
    response = taxi_protocol.post(
        '3.0/launch',
        {
            'id': TEST_USER_ID,
            'authorized': True,
            'phone_id': TEST_USER_PHONE_ID,
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data['authorized']

    assert data['passenger_profile'] == passenger_profile_response


@pytest.mark.parametrize('error_code', [500, 503, 400])
@LAUNCH_USE_INPUT_FIELDS
def test_launch_passenger_profile_error(
        taxi_protocol,
        mockserver,
        blackbox_mockserver,
        db,
        experiments3,
        load_json,
        error_code,
        use_input_fields,
):
    experiments3.add_experiments_json(load_json('exp3_passenger_profile.json'))

    @mockserver.json_handler('/passenger_profile/passenger-profile/v1/profile')
    def mock_passenger_profile(request):
        return mockserver.make_response(status=error_code)

    response = taxi_protocol.post(
        '3.0/launch',
        {
            'id': TEST_USER_ID,
            'authorized': True,
            'phone_id': TEST_USER_PHONE_ID,
        },
        bearer='test_token',
    )
    assert response.status_code == 200
    data = response.json()
    assert data['authorized']

    assert 'passenger_profile' not in data


@pytest.mark.now('2016-12-19T10:05:00+0000')
@pytest.mark.config(
    LAUNCH_PAYMENT_FILTERS_FILTER_BY_APP_ENABLED=True,
    BILLING_ORDER_AUTOFALLBACK_ENABLED=False,
    APPLICATION_MAP_BRAND={
        '__default__': 'unknown',
        'android': 'yataxi',
        'iphone': 'yataxi',
        'yango_iphone': 'yango1',
        'yango_android': 'yango2',
    },
)
@pytest.mark.filldb(orders='payment_filters_app')
@pytest.mark.parametrize(
    'headers,expect_dept,expect_need_cvn,expect_need_accept,expect_by_card',
    [
        (brands.yataxi.android.headers, True, False, True, True),
        (brands.yataxi.iphone.headers, True, False, True, True),
        (brands.yango.android.headers, True, True, False, False),
        (brands.yango.iphone.headers, False, False, False, True),
    ],
)
@LAUNCH_USE_INPUT_FIELDS
def test_launch_payment_filters_by_apps(
        headers,
        expect_dept,
        expect_need_cvn,
        expect_need_accept,
        expect_by_card,
        taxi_protocol,
        blackbox_service,
        use_input_fields,
):

    response = make_launch_request(taxi_protocol, [], headers=headers)

    expected = []
    if expect_dept:
        expected.append('debt')
    if expect_need_cvn:
        expected.append('need_cvn')
    if expect_need_accept:
        expected.append('need_accept')
    if expect_by_card:
        expected.append('can_be_paid_by_card')

    assert sorted(expected) == sorted(response['payment_statuses_filter'])


@LAUNCH_USE_INPUT_FIELDS
@pytest.mark.config(LAUNCH_OBTAIN_DATA_FROM_HEADERS=True)
@pytest.mark.parametrize(
    'doc_id,input_id,metrica_id',
    [
        ('device_id1', 'device_id2', 'appmetrica_device_id'),
        ('device_id1', '', 'appmetrica_device_id'),
        ('device_id1', '', ''),
        ('', 'device_id2', 'appmetrica_device_id'),
        ('', 'device_id2', ''),
    ],
)
def test_launch_device_id_usage(
        use_input_fields,
        doc_id,
        input_id,
        metrica_id,
        taxi_protocol,
        db,
        blackbox_service,
):
    db.users.update({'_id': TEST_USER_ID}, {'$set': {'device_id': doc_id}})
    response = taxi_protocol.post(
        '3.0/launch',
        {'id': TEST_USER_ID, 'device_id': input_id},
        bearer='test_token',
        headers={'X-AppMetrica-DeviceId': metrica_id},
    )
    assert response.status_code == 200

    result_id = response.json()['device_id']
    if use_input_fields:
        if len(input_id) == 0:
            assert result_id == metrica_id
        else:
            assert result_id == input_id
    else:
        if len(doc_id) == 0:
            if len(metrica_id) == 0:
                assert result_id == input_id
            else:
                assert result_id == metrica_id
        else:
            assert result_id == doc_id
