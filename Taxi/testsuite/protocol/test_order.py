import datetime
import json
import threading
import time

import bson
import pytest

from taxi_tests import utils

from individual_tariffs_switch_parametrize import (
    PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS,
)

PROTOCOL_USE_ORDER_CORE = pytest.mark.parametrize(
    'protocol_use_order_core',
    [
        pytest.param(False),
        pytest.param(
            True,
            marks=[
                pytest.mark.experiments3(
                    filename='protocol_use_order_core.json',
                ),
            ],
        ),
    ],
)


def _mock_pdp_discount(pricing_data_preparer, old_discounts_response):
    pricing_data_preparer.set_discount_offer_id(
        old_discounts_response['discount_offer_id'],
    )
    for discount_for_category in old_discounts_response['discounts']:
        category = discount_for_category['class']
        discount = discount_for_category['discount']
        discount_mock = {
            'id': discount['id'],
            'reason': discount['reason'],
            'method': discount['method'],
            'limit_id': discount['limit_id'],
        }
        pricing_data_preparer.set_discount(discount_mock, category)
        pricing_data_preparer.set_discount_meta(
            discount['price'], discount['value'], category,
        )


@pytest.fixture(autouse=True)
def pickuppoints_zones_handlers(mockserver):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def zones(request):
        return {}


@pytest.fixture()
def mock_user_api_set_authorized(mockserver, db):
    @mockserver.json_handler('/user-api/users/set_authorized')
    def mock_impl(request):
        db.users.update(
            {'_id': request.json['id']},
            {
                '$set': {
                    'authorized': request.json['authorized'],
                    'phone_id': bson.ObjectId(request.json['phone_id']),
                },
                '$unset': {'confirmation': True},
            },
        )

    return mock_impl


def check_support_commit(order_id, mock_stq_agent):
    tasks = mock_stq_agent.get_tasks('support_commit', order_id)
    assert len(tasks) == 1

    support_commit = tasks[0]

    a = support_commit.args
    assert a[0] == order_id
    assert 'log_extra' in a[1]
    assert a[2] == order_id
    assert a[3] is True
    assert a[4] == 5
    assert a[5] == 1
    assert a[6] == 1

    assert 'log_extra' in support_commit.kwargs
    assert support_commit.is_postponed


def check_sendsms_stq(mock_stq_agent):
    tasks = mock_stq_agent.get_tasks('send_sms')
    assert len(tasks) == 1

    send_sms = tasks[0]
    assert send_sms.args[1] == 'for_terminal_user'
    karg = send_sms.kwargs
    assert 'log_extra' in karg
    assert karg['locale'] == 'en'
    assert karg['address'] == 'Okhotny Ryad Street'
    assert karg['from_uid'] == '4003514353'


def check_created_order_in_stq(order_id, mock_stq_agent, support_commit=True):
    processing_tasks = mock_stq_agent.get_tasks('processing', order_id)
    assert len(processing_tasks) == 0

    if support_commit:
        check_support_commit(order_id, mock_stq_agent)


def send_create_order_request(taxi_protocol, request, **kwargs):
    return taxi_protocol.post('3.0/order', request, **kwargs)


def make_order(taxi_protocol, request, **kwargs):
    response = send_create_order_request(taxi_protocol, request, **kwargs)
    assert response.status_code == 200
    response_body = response.json()
    return response_body


def make_order_spam_checking(taxi_protocol, request, **kwargs):
    return send_create_order_request(taxi_protocol, request, **kwargs)


def send_create_draft_and_commit_request(taxi_protocol, request, **kwargs):
    draft_response = taxi_protocol.post('3.0/orderdraft', request, **kwargs)
    assert draft_response.status_code == 200
    order_id = draft_response.json()['orderid']

    commit_request = {'id': request['id'], 'orderid': order_id}

    return taxi_protocol.post('3.0/ordercommit', commit_request, **kwargs)


def make_order_draft_commit(taxi_protocol, request, **kwargs):
    commit_response = send_create_draft_and_commit_request(
        taxi_protocol, request, **kwargs,
    )
    assert commit_response.status_code == 200

    return commit_response.json()


def make_order_from_proc(taxi_protocol, order_id):
    request = {'orderid': order_id}
    response = taxi_protocol.post('internal/orderfromproc', request)
    assert response.status_code == 200


def _get_class_discount(discounts_list, class_name):
    discount = [d for d in discounts_list if d['class'] == class_name]
    if discount:
        return discount[0]
    else:
        return None


def get_surge_mock_response():
    return {
        'zone_id': 'moscow',
        'classes': [
            {
                'name': 'econom',
                'value': 1.2,
                'reason': 'pins_free',
                'antisurge': False,
                'value_raw': 1.0,
                'value_smooth': 1.0,
            },
        ],
    }


def get_yamaps_mock_response(request, load_json):
    geo_docs = load_json('yamaps.json')

    for doc in geo_docs:
        if request.query_string.decode().find(doc['url']) != -1:
            return doc['response']


@pytest.mark.parametrize(
    'users_set_authorized_with_user_api',
    [
        pytest.param(False),
        pytest.param(
            True,
            marks=pytest.mark.config(
                PROTOCOL_USERS_SET_AUTHORIZED_WITH_USER_API=True,
            ),
        ),
    ],
)
@PROTOCOL_USE_ORDER_CORE
@pytest.mark.parametrize(
    'create_order,support_commit',
    [(make_order, True), (make_order_draft_commit, False)],
)
def test_order(
        taxi_protocol,
        mockserver,
        load_json,
        db,
        create_order,
        support_commit,
        check_order_matches_proc,
        mock_stq_agent,
        mock_user_api_set_authorized,
        users_set_authorized_with_user_api,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return get_surge_mock_response()

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return get_yamaps_mock_response(request, load_json)

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    response_body = create_order(
        taxi_protocol,
        load_json('basic_request.json'),
        x_real_ip='my-ip-address',
    )
    order_id = response_body['orderid']
    assert response_body['status'] == 'search'
    check_created_order_in_stq(order_id, mock_stq_agent, support_commit)

    check_order_matches_proc(order_id)

    order = db.orders.find_one(order_id)
    proc = db.order_proc.find_one(order_id)
    assert order['request']['ip'] == 'my-ip-address'
    assert proc['order']['request']['ip'] == 'my-ip-address'
    assert order['creditcard']['tips'] == {'type': 'percent', 'value': 5}
    assert order['creditcard']['tips_perc_default'] == 5
    assert 'cost' not in order
    assert proc['order']['cost'] is None
    if users_set_authorized_with_user_api:
        assert mock_user_api_set_authorized.times_called == 1
    else:
        assert mock_user_api_set_authorized.times_called == 0


@pytest.mark.filldb(user_phones='is_spammer_check')
@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'retries': 1, 'timeout': 100},
        'order': {'use_afs': True, 'retries': 1, 'timeout': 100},
    },
)
@pytest.mark.parametrize(
    'create_order,support_commit', [(make_order_spam_checking, True)],
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
def test_order_spammer(
        taxi_protocol,
        mockserver,
        load_json,
        create_order,
        support_commit,
        now,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return get_surge_mock_response()

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return get_yamaps_mock_response(request, load_json)

    @mockserver.json_handler('/antifraud/client/user/is_spammer/order')
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'is_multiorder': False,
            'user_id': 'f4eb6aaa29ad4a6eb53f8a7620793561',
            'user_phone_id': '59246c5b6195542e9b084207',
            'device_id': 'c02c705e98588f724ca046ac59cafece65501e36',
        }
        blocked_until = now + datetime.timedelta(seconds=7)
        return {
            'is_spammer': True,
            'blocked_until': utils.timestring(blocked_until),
        }

    response = create_order(
        taxi_protocol,
        load_json('basic_request.json'),
        x_real_ip='my-ip-address',
    )
    assert response.status_code == 403
    assert response.json()['blocked'] == '2017-05-25T08:30:07+0000'


@pytest.mark.filldb(user_phones='is_spammer_check')
@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=False,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'retries': 1, 'timeout': 100},
        'order': {'use_afs': True, 'retries': 1, 'timeout': 100},
    },
)
@pytest.mark.parametrize(
    'create_order,support_commit', [(make_order_spam_checking, True)],
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
def test_order_is_spammer_disabled_in_client(
        taxi_protocol,
        mockserver,
        load_json,
        create_order,
        support_commit,
        now,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return get_surge_mock_response()

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return get_yamaps_mock_response(request, load_json)

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    @mockserver.json_handler('/antifraud/client/user/is_spammer/order')
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'is_multiorder': False,
            'user_id': 'f4eb6aaa29ad4a6eb53f8a7620793561',
            'user_phone_id': '59246c5b6195542e9b084207',
            'device_id': 'c02c705e98588f724ca046ac59cafece65501e36',
        }
        blocked_until = now + datetime.timedelta(seconds=7)
        return {
            'is_spammer': True,
            'blocked_until': utils.timestring(blocked_until),
        }

    response = create_order(
        taxi_protocol,
        load_json('basic_request.json'),
        x_real_ip='my-ip-address',
    )
    assert response.status_code == 200


@pytest.mark.filldb(user_phones='is_spammer_check')
@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'retries': 1, 'timeout': 100},
        'order': {'use_afs': True, 'retries': 1, 'timeout': 100},
    },
)
@pytest.mark.parametrize('create_order,support_commit', [(make_order, True)])
def test_order_not_spammer(
        taxi_protocol,
        mockserver,
        load_json,
        create_order,
        support_commit,
        mock_stq_agent,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return get_surge_mock_response()

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return get_yamaps_mock_response(request, load_json)

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    @mockserver.json_handler('/antifraud/client/user/is_spammer/order')
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'is_multiorder': False,
            'user_id': 'f4eb6aaa29ad4a6eb53f8a7620793561',
            'user_phone_id': '59246c5b6195542e9b084207',
            'device_id': 'c02c705e98588f724ca046ac59cafece65501e36',
        }
        return {'is_spammer': False}

    response_body = create_order(
        taxi_protocol,
        load_json('basic_request.json'),
        x_real_ip='my-ip-address',
    )
    order_id = response_body['orderid']
    assert response_body['status'] == 'search'
    check_created_order_in_stq(order_id, mock_stq_agent, support_commit)


@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'retries': 1, 'timeout': 100},
        'order': {'use_afs': True, 'retries': 1, 'timeout': 100},
    },
)
@pytest.mark.parametrize('create_order,support_commit', [(make_order, True)])
@pytest.mark.parametrize('response_code', [500, 400, 403])
def test_order_is_spammer_affected(
        taxi_protocol,
        mockserver,
        load_json,
        create_order,
        support_commit,
        mock_stq_agent,
        response_code,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return get_surge_mock_response()

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return get_yamaps_mock_response(request, load_json)

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    @mockserver.json_handler('/antifraud/client/user/is_spammer/order')
    def mock_afs_is_spammer_invalid(request):
        return mockserver.make_response(
            '{"code":' + str(response_code) + '}', response_code,
        )

    response_body = create_order(
        taxi_protocol,
        load_json('basic_request.json'),
        x_real_ip='my-ip-address',
    )
    order_id = response_body['orderid']
    assert response_body['status'] == 'search'
    check_created_order_in_stq(order_id, mock_stq_agent, support_commit)


@PROTOCOL_USE_ORDER_CORE
def test_order_with_supported_features(
        taxi_protocol, mockserver, load_json, db, check_order_matches_proc,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return get_surge_mock_response()

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return get_yamaps_mock_response(request, load_json)

    request = load_json('basic_request.json')
    request['supported'] = ['feature1', 'feature2']
    response_body = make_order_draft_commit(
        taxi_protocol, request, x_real_ip='my-ip-address',
    )
    order_id = response_body['orderid']
    check_order_matches_proc(order_id)
    assert response_body['status'] == 'search'
    order = db.orders.find_one(order_id)
    proc = db.order_proc.find_one(order_id)
    assert 'supported' not in order['request']
    assert proc['order']['request']['supported'] == ['feature1', 'feature2']


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.translations(
    notify={
        'sms.for_terminal_user': {
            'en': (
                'We have accepted your order for %(address)s. '
                'To cancel, text #1 to 3443.'
            ),
        },
    },
)
@pytest.mark.config(USER_API_USE_USER_PHONES_CREATION=True)
@pytest.mark.experiments3(filename='experiments3_sms_via_communications.json')
def test_order_terminal(
        taxi_protocol,
        mockserver,
        load_json,
        now,
        check_order_matches_proc,
        mock_stq_agent,
        mock_user_api,
        pricing_data_preparer,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return get_surge_mock_response()

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return get_yamaps_mock_response(request, load_json)

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        data = request.json
        assert 'phone' not in data
        assert data['phone_id'] == 'personal_phone_id'
        assert data['text'] == {
            'key': 'sms.for_terminal_user',
            'keyset': 'notify',
            'params': {'address': 'Okhotny Ryad Street'},
        }
        assert data['intent'] == 'order_by_terminal'
        return mockserver.make_response('', 200)

    response_body = make_order(taxi_protocol, load_json('basic_request.json'))
    mock_communications_sendsms.wait_call()

    order_id = response_body['orderid']
    assert response_body['status'] == 'search'
    check_created_order_in_stq(order_id, mock_stq_agent)
    check_order_matches_proc(order_id)


@PROTOCOL_USE_ORDER_CORE
def test_order_with_new_card(
        taxi_protocol,
        load,
        load_json,
        db,
        mockserver,
        check_order_matches_proc,
        cardstorage,
        pricing_data_preparer,
):
    cardstorage.trust_response = 'billing-cards-response.json'

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 1.2,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }

    request = load_json('basic_request_card.json')
    response = taxi_protocol.post('3.0/order', request)
    assert response.status_code == 200
    response_body = response.json()
    order_id = response_body['orderid']
    check_order_matches_proc(order_id)
    order = db.orders.find_one({'_id': order_id})
    assert order['creditcard']['credentials'] == {
        'card_number': '411111****1111',
        'card_system': 'VISA',
    }
    payment_tech = order['payment_tech']
    proc = db.order_proc.find_one({'_id': order_id})
    assert proc['order']['creditcard']['credentials'] == {
        'card_number': '411111****1111',
        'card_system': 'VISA',
    }
    card = db.cards.find_one({'payment_id': 'card-x8502'})
    assert card['persistent_id'] == payment_tech['main_card_persistent_id']


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.filldb(tariff_settings='creditcard')
def test_order_with_new_card_with_creditcard(
        taxi_protocol,
        load,
        load_json,
        db,
        mockserver,
        check_order_matches_proc,
        cardstorage,
        pricing_data_preparer,
):
    cardstorage.trust_response = 'billing-cards-response.json'

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 1.2,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }

    request = load_json('basic_request_card.json')
    response = taxi_protocol.post('3.0/order', request)
    assert response.status_code == 200
    response_body = response.json()
    order_id = response_body['orderid']
    check_order_matches_proc(order_id)
    order = db.orders.find_one({'_id': order_id})
    payment_tech = order['payment_tech']
    card = db.cards.find_one({'payment_id': 'card-x8502'})
    assert card['persistent_id'] == payment_tech['main_card_persistent_id']


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.translations(
    notify={
        'sms.for_terminal_user': {
            'en': (
                'We have accepted your order for %(address)s. '
                'To cancel, text #1 to 3443.'
            ),
        },
    },
)
def test_order_terminal_with_no_authorized_phone(
        taxi_protocol,
        yamaps,
        mockserver,
        load_json,
        check_order_matches_proc,
        mock_stq_agent,
        pricing_data_preparer,
):
    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return get_yamaps_mock_response(request, load_json)

    request = load_json('basic_request.json')
    # set unauthorized user to check auto-auth
    request['id'] = 'f4eb6aaa29ad4a6eb53f8a7620793000'
    request['terminal']['phone'] = '+7(902)3217999'
    response = taxi_protocol.post('3.0/order', request)
    assert response.status_code == 200
    response_body = response.json()
    order_id = response_body['orderid']
    assert response_body['status'] == 'search'

    check_created_order_in_stq(order_id, mock_stq_agent)
    check_order_matches_proc(order_id)


def test_order_invalid_terminal(taxi_protocol, load_json):
    request = load_json('invalid_terminal.json')
    response = taxi_protocol.post('3.0/order', request)
    assert response.status_code == 403
    assert response.json()['type'] == 'id'


@pytest.mark.parametrize(
    'send_request',
    [send_create_order_request, send_create_draft_and_commit_request],
)
@pytest.mark.filldb(tariff_settings='disable_zone_leave')
def test_order_disable_zone_leave_with_destination(
        taxi_protocol,
        mockserver,
        load_json,
        send_request,
        pricing_data_preparer,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return get_surge_mock_response()

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return get_yamaps_mock_response(request, load_json)

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    request = load_json('disable_leave_zone_point_b_forbidden.json')
    response = send_request(taxi_protocol, request)
    assert response.status_code == 406
    assert (
        response.json()['error']['text']
        == 'You cant leave zone on this tariff'
    )

    request = load_json('disable_leave_zone_point_b_allowed.json')
    response = send_request(taxi_protocol, request)
    assert response.status_code == 200
    response_body = response.json()
    assert response_body['status'] == 'search'


@pytest.mark.parametrize(
    'send_request',
    [send_create_order_request, send_create_draft_and_commit_request],
)
@pytest.mark.filldb(tariff_settings='disable_zone_leave')
def test_order_disable_zone_leave_without_destination(
        taxi_protocol, mockserver, load_json, send_request,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return get_surge_mock_response()

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return get_yamaps_mock_response(request, load_json)

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    request = load_json('disable_leave_zone_no_point_b_forbidden.json')
    response = send_request(taxi_protocol, request)
    assert response.status_code == 406
    assert (
        response.json()['error']['text']
        == 'You cant leave zone on this tariff'
    )

    request = load_json('disable_leave_zone_no_point_b_allowed.json')
    response = send_request(taxi_protocol, request)
    assert response.status_code == 200
    response_body = response.json()
    assert response_body['status'] == 'search'


@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
@pytest.mark.parametrize(
    'can_order, zone_available',
    [(True, False), (False, True), (False, False)],
)
@pytest.mark.parametrize(
    'send_request',
    [send_create_order_request, send_create_draft_and_commit_request],
)
def test_wrong_corp_order(
        taxi_protocol,
        mockserver,
        load_json,
        can_order,
        zone_available,
        send_request,
        pricing_data_preparer,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return get_surge_mock_response()

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return get_yamaps_mock_response(request, load_json)

    @mockserver.json_handler('/corp_integration_api/corp_paymentmethods')
    def mock_corp_paymentmethods(request):
        method = {
            'type': 'corp',
            'id': 'corp-corp_client_id',
            'label': '-',
            'description': '-',
            'can_order': can_order,
            'cost_center': '',
            'zone_available': zone_available,
            'hide_user_cost': False,
            'user_id': 'corp_user_id',
            'client_comment': 'corp_comment',
            'currency': 'RUB',
        }
        if not can_order:
            method['order_disable_reason'] = 'reason'
        if not zone_available:
            method['zone_disable_reason'] = 'reason'
        return {'methods': [method]}

    request = load_json('wrong_request.json')
    request['payment']['payment_method_id'] = 'cash-not-found'
    response = send_request(taxi_protocol, request)
    assert response.status_code == 406
    assert response.json()['error']['code'] == 'NOT_CORP_CLIENT'

    request['payment']['payment_method_id'] = 'corp-corp_client_id'
    response = send_request(taxi_protocol, request)
    assert response.status_code == 406
    data = response.json()
    error_code = None
    if not can_order:
        error_code = 'CORP_CANNOT_ORDER'
    if not zone_available:
        error_code = 'CORP_ZONE_UNAVAILABLE'
    assert data == {'error': {'code': error_code, 'text': 'reason'}}


cookie_str = 'yandexuid=6543707321492163921; Session_id=5'


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.config(
    DAY_ORDER_LIMITS=[{'yandex_login': 'login', 'order_limit': 100}],
)
def test_order_user_with_order_limit(
        taxi_protocol,
        yamaps,
        load_json,
        db,
        blackbox_service,
        check_order_matches_proc,
):
    blackbox_service.set_sessionid_info('5', uid='4003514353', login='login')

    request = load_json('basic_request.json')
    request['intermediary'] = 'partner'
    request['client_forwarded_phone'] = '+71112223344'
    request.pop('terminal', None)
    response = taxi_protocol.post(
        '3.0/order',
        request,
        bearer=None,
        headers={'Cookie': cookie_str, 'Accept-Language': 'ru_BY'},
    )
    assert response.status_code == 200
    order_id = response.json()['orderid']
    check_order_matches_proc(order_id)
    data = db.orders.find_one({'_id': order_id})
    assert data != {}
    assert data['statistics']['application'] == 'partner'
    assert data['operator_login'] == 'login'
    assert data['user_locale'] == 'ru'
    assert data['original_locale'] == 'ru_BY'


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.config(
    DAY_ORDER_LIMITS=[{'yandex_login': 'login', 'order_limit': 100}],
)
def test_partner_order_with_order_limit_and_no_authorized_phone(
        taxi_protocol,
        yamaps,
        load_json,
        db,
        blackbox_service,
        check_order_matches_proc,
        pricing_data_preparer,
):
    blackbox_service.set_sessionid_info(
        '5', uid='4003514353', login='login', phones=['+71111111111'],
    )

    request = load_json('basic_request.json')
    request['id'] = 'f4eb6aaa29ad4a6eb53f8a7620793000'
    request['intermediary'] = 'partner'
    request['client_forwarded_phone'] = '+71112223344'
    request.pop('terminal', None)
    response = taxi_protocol.post(
        '3.0/order', request, bearer=None, headers={'Cookie': cookie_str},
    )
    assert response.status_code == 200
    order_id = response.json()['orderid']
    check_order_matches_proc(order_id)
    data = db.orders.find_one({'_id': order_id})
    assert data != {}
    assert data['statistics']['application'] == 'partner'
    assert data['operator_login'] == 'login'

    data = db.users.find_one({'_id': 'f4eb6aaa29ad4a6eb53f8a7620793000'})
    assert data['authorized']
    phone_id = data['phone_id']
    phone_data = db.user_phones.find_one({'_id': phone_id})
    assert phone_data['phone'] == '+71111111111'


def test_partner_order_with_order_limit_no(
        taxi_protocol, blackbox_service, load_json, pricing_data_preparer,
):
    blackbox_service.set_sessionid_info('5', uid='4003514353', login='login')
    request = load_json('basic_request.json')
    request.pop('terminal', None)
    request['intermediary'] = 'partner'
    request['client_forwarded_phone'] = '+71112223344'
    response = taxi_protocol.post(
        '3.0/order', request, bearer=None, headers={'Cookie': cookie_str},
    )
    assert response.status_code == 403


@pytest.mark.config(
    DAY_ORDER_LIMITS=[{'yandex_login': 'login', 'order_limit': 1}],
)
def test_partner_order_with_order_limit_many(
        taxi_protocol, blackbox_service, yamaps, load_json,
):
    blackbox_service.set_sessionid_info('5', uid='4003514353', login='login')

    # 1st order
    request = load_json('basic_request.json')
    request['intermediary'] = 'partner'
    request['client_forwarded_phone'] = '+71112223344'
    request.pop('terminal', None)
    response = taxi_protocol.post(
        '3.0/order', request, bearer=None, headers={'Cookie': cookie_str},
    )
    assert response.status_code == 200

    # 2nd order
    request['client_forwarded_phone'] = '+71112223322'
    response = taxi_protocol.post(
        '3.0/order', request, bearer=None, headers={'Cookie': cookie_str},
    )
    assert response.status_code == 405


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.order_experiments('surge_add_business')
def test_order_extra_contact_phone(
        taxi_protocol, load_json, db, check_order_matches_proc,
):
    request = load_json('basic_request_extra_contact_phone.json')
    request['offer'] = 'extra_contact_phone'
    response = taxi_protocol.post('3.0/order', request)
    assert response.status_code == 200
    order_id = response.json()['orderid']
    check_order_matches_proc(order_id)
    data = db.orders.find_one({'_id': order_id})
    assert data != {}
    request = data['request']
    extra_user_phone_id = request['extra_user_phone_id']
    object = db.user_phones.find_one({'_id': extra_user_phone_id})
    phone = object['phone']
    assert phone == '+73842111111'


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.config(SURGE_CREATE_PIN_WITH_ORDER=True)
@pytest.mark.parametrize('create_order', [make_order, make_order_draft_commit])
def test_order_with_pin_create(
        taxi_protocol,
        load_json,
        db,
        blackbox_service,
        mockserver,
        create_order,
        check_order_matches_proc,
):
    blackbox_service.set_sessionid_info('5', uid='4003514353', login='login')

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    surger_call_event = threading.Event()
    testcase = {'order_id_in_pin': None, 'event': surger_call_event}

    @mockserver.json_handler('/pin_storage/v1/create_pin')
    def mock_pin_storage_create_pin(request):
        input_json = json.loads(request.get_data()).get('pin')
        assert 'tariff_zone' in input_json
        if 'order_id' in input_json:
            testcase['order_id_in_pin'] = input_json['order_id']
        testcase['event'].set()
        return {}

    request = load_json('basic_request.json')
    response = create_order(
        taxi_protocol, request, bearer=None, headers={'Cookie': cookie_str},
    )
    order_id = response['orderid']
    check_order_matches_proc(order_id)
    data = db.orders.find_one({'_id': order_id})
    assert data
    # call to surger is async in protocol, wait max 60 sec
    # for this call in mock
    surger_call_event.wait(60)
    assert testcase['order_id_in_pin'] == order_id


@pytest.mark.config(SURGE_CREATE_PIN_WITH_ORDER=True)
def test_order_with_pin_create_personal_phone_id(
        taxi_protocol, load_json, blackbox_service, mockserver,
):
    blackbox_service.set_sessionid_info('5', uid='4003514353', login='login')

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    @mockserver.json_handler('/personal/v1/phones/store')
    def mock_personal_phone_store(request):
        data = json.loads(request.get_data())
        # 'phone' required by:
        # clients::personal::Client::Store(...)
        # ->ParseResponse(...)
        # ->ResponseToPersonalDoc(...)
        return {'id': 'test personal phone id', 'value': data['value']}

    @mockserver.json_handler('/pin_storage/v1/create_pin')
    def mock_pin_storage_create_pin(request):
        data = json.loads(request.get_data()).get('pin')
        assert data['personal_phone_id'] == 'test personal phone id'
        assert 'user_phone_hash' not in data
        return {}

    request = load_json('basic_request.json')
    response = make_order(
        taxi_protocol, request, bearer=None, headers={'Cookie': cookie_str},
    )
    assert 'orderid' in response
    assert mock_pin_storage_create_pin.wait_call()


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.order_experiments('surge_add_business')
@pytest.mark.filldb(users='with_ya_plus')
@pytest.mark.parametrize('create_order', [make_order, make_order_draft_commit])
def test_order_with_ya_plus_user(
        taxi_protocol,
        load_json,
        db,
        create_order,
        check_order_matches_proc,
        pricing_data_preparer,
):
    request = load_json('basic_request_ya_plus.json')
    request['offer'] = 'ya_plus_multiplier'
    response = create_order(taxi_protocol, request)
    order_id = response['orderid']
    # check in order_proc
    data = db.order_proc.find_one({'_id': order_id})
    assert data['price_modifiers']['items'][0]['reason'] == 'ya_plus'
    assert data['price_modifiers']['items'][0]['pay_subventions']
    cat = data['price_modifiers']['items'][0]['tariff_categories'][0]
    assert cat == 'econom'
    cat = data['price_modifiers']['items'][0]['tariff_categories'][1]
    assert cat == 'minivan'
    # check in order
    check_order_matches_proc(order_id)
    data = db.orders.find_one({'_id': order_id})
    assert data['price_modifiers']['items'][0]['reason'] == 'ya_plus'
    assert data['price_modifiers']['items'][0]['pay_subventions']
    cat = data['price_modifiers']['items'][0]['tariff_categories'][0]
    assert cat == 'econom'
    cat = data['price_modifiers']['items'][0]['tariff_categories'][1]
    assert cat == 'minivan'


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(
    PERSONAL_STATE_BANNED_COMMENTS_LIST_USERSTATE=[
        {
            'redirect_to': 'child_tariff',
            'words': ['banned phrase', 'chair', 'дети', 'երեխա'],
        },
        {
            'redirect_to': 'express',
            'words': ['dostavka', 'доставк', 'Доставить'],
            'excluded_classes': ['cargo', 'courier'],
        },
        {
            'redirect_to': 'express',
            'words': ['экспресс', 'express'],
            'included_classes': ['econom'],
        },
    ],
    ALL_CATEGORIES=[
        'econom',
        'comfortplus',
        'child_tariff',
        'express',
        'cargo',
    ],
)
@pytest.mark.parametrize(
    ('tariff', 'requirements', 'comment', 'error_code', 'response_code'),
    [
        pytest.param(
            ['econom'],
            {},
            'long text about chair',
            'CHILDCHAIR_BANNED_COMMENT',
            406,
            id='econom_childchair_1',
        ),
        pytest.param(
            ['econom'],
            {},
            'ChAiR',
            'CHILDCHAIR_BANNED_COMMENT',
            406,
            id='econom_childchair_2',
        ),
        pytest.param(
            ['econom'],
            {},
            'ДетИ',
            'CHILDCHAIR_BANNED_COMMENT',
            406,
            id='econom_childchair_3',
        ),
        pytest.param(
            ['econom'],
            {},
            'Երեխաներ',
            'CHILDCHAIR_BANNED_COMMENT',
            406,
            id='econom_childchair_4',
        ),
        pytest.param(
            ['econom'], {}, 'correct phrase', None, 200, id='econom_ok',
        ),
        pytest.param(
            ['econom'],
            {},
            'comment about dosTAvKa',
            'EXPRESS_BANNED_COMMENT',
            406,
            id='econom_express_1',
        ),
        pytest.param(
            ['econom'],
            {},
            'хочу дОстАВку',
            'EXPRESS_BANNED_COMMENT',
            406,
            id='econom_express_2',
        ),
        pytest.param(
            ['econom'],
            {},
            'Доставить к пятому подъезду',
            'EXPRESS_BANNED_COMMENT',
            406,
            id='econom_express_3',
        ),
        pytest.param(
            ['econom'],
            {},
            'express',
            'EXPRESS_BANNED_COMMENT',
            406,
            id='econom_express_included_classes',
        ),
        pytest.param(
            ['comfortplus'],
            {'childchair_for_child_tariff': [7, 7]},
            'long text about chair',
            None,
            200,
            id='comfortplus_childchair_for_child_tariff_ok',
        ),
        pytest.param(
            ['comfortplus'],
            {'childchair_for_child_tariff': [7, 7]},
            'correct phrase',
            None,
            200,
            id='comfortplus_ok',
        ),
        pytest.param(
            ['comfortplus'],
            {'childchair_for_child_tariff': [7, 7]},
            'comment about dosTAvKa',
            'EXPRESS_BANNED_COMMENT',
            406,
            id='comfortplus_express',
        ),
        pytest.param(
            ['comfortplus'],
            {},
            'express',
            None,
            200,
            id='comforplus_not_included',
        ),
        pytest.param(
            ['child_tariff'],
            {},
            'long text about chair',
            None,
            200,
            id='child_tariff_childchair_ok',
        ),
        pytest.param(
            ['child_tariff'],
            {},
            'correct phrase',
            None,
            200,
            id='child_tariff_ok',
        ),
        pytest.param(
            ['child_tariff'],
            {},
            'comment about dosTAvKa',
            'EXPRESS_BANNED_COMMENT',
            406,
            id='child_tariff_express',
        ),
        pytest.param(
            ['express'],
            {},
            'long text about chair',
            'CHILDCHAIR_BANNED_COMMENT',
            406,
            id='express_childchair',
        ),
        pytest.param(
            ['express'], {}, 'correct phrase', None, 200, id='express_ok',
        ),
        pytest.param(
            ['express'],
            {},
            'comment about dosTAvKa',
            None,
            200,
            id='express_delivery_ok',
        ),
        pytest.param(
            ['cargo'],
            {},
            'long text about chair',
            'CHILDCHAIR_BANNED_COMMENT',
            406,
            id='cargo_childchair',
        ),
        pytest.param(
            ['cargo'], {}, 'correct phrase', None, 200, id='cargo_ok',
        ),
        pytest.param(
            ['cargo'],
            {},
            'comment about dosTAvKa',
            None,
            200,
            id='cargo_delivery_ok',
        ),
    ],
)
@pytest.mark.filldb(
    tariff_settings='for_banned_comments', tariffs='for_banned_comments',
)
@pytest.mark.order_experiments('child_chair_ban_comment')
@pytest.mark.experiments3(filename='exp3_banned_comments.json')
@pytest.mark.now('2020-02-14T23:59:00+0300')
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_order_with_bannable_comment(
        tariff,
        requirements,
        comment,
        error_code,
        response_code,
        taxi_protocol,
        load_json,
        db,
        pricing_data_preparer,
        individual_tariffs_switch_on,
):
    pricing_data_preparer.set_fixed_price(enable=False)
    request = load_json('basic_request_fixprice_without_class_and_reqs.json')
    if 'childchair_for_child_tariff' in requirements:
        request['offer'] = 'fixed_price_fullupgrade_chair'
    else:
        request['offer'] = 'fixed_price_fullupgrade'
    request['class'] = tariff
    request['requirements'] = requirements
    request['comment'] = comment

    response = taxi_protocol.post('3.0/order', request)
    assert response.status_code == response_code, (
        response.json().get('error', {}).get('code')
    )
    if response_code != 200:
        response = response.json()
        assert 'error' in response
        assert 'code' in response['error']
        assert response['error']['code'] == error_code


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(
    ORDER_DRAFT_BANNED_WORDS_IN_COMMENT_LIST=[
        {
            'tanker_key_suffix_error': 'BANNED_WORDS_IN_COMMENTS_HACKER',
            'words': ['хаКер', 'hacker'],
        },
        {
            'tanker_key_suffix_error': 'BANNED_WORDS_IN_COMMENTS_WAKE_UP',
            'words': ['вСТАвай', 'Подъем'],
        },
    ],
    ALL_CATEGORIES=['econom', 'comfortplus'],
)
@pytest.mark.parametrize(
    ('tariff', 'comment', 'error_code', 'response_code'),
    [
        pytest.param(
            ['econom'],
            'хакеР атакует',
            'BANNED_WORDS_IN_COMMENTS_HACKER',
            406,
            id='econom_hacker_attack_1',
        ),
        pytest.param(
            ['econom'],
            'контрнаступление Hackera',
            'BANNED_WORDS_IN_COMMENTS_HACKER',
            406,
            id='econom_hacker_attack_2',
        ),
        pytest.param(
            ['comfortplus'],
            'Вставай страна',
            'BANNED_WORDS_IN_COMMENTS_WAKE_UP',
            406,
            id='comfortplus_podyom_1',
        ),
        pytest.param(
            ['comfortplus'],
            'пОдъем страна',
            'BANNED_WORDS_IN_COMMENTS_WAKE_UP',
            406,
            id='comfortplus_podyom_2',
        ),
        pytest.param(
            ['comfortplus'],
            'Все стабилизируется',
            None,
            200,
            id='comfortplus_stable',
        ),
    ],
)
@pytest.mark.filldb(
    tariff_settings='for_banned_comments', tariffs='for_banned_comments',
)
@pytest.mark.experiments3(filename='exp3_check_banned_words_in_comment.json')
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_order_with_banned_words_in_comment(
        tariff,
        comment,
        error_code,
        response_code,
        taxi_protocol,
        load_json,
        db,
        pricing_data_preparer,
        individual_tariffs_switch_on,
):
    pricing_data_preparer.set_fixed_price(enable=False)
    request = load_json('basic_request_fixprice_without_class_and_reqs.json')
    request['offer'] = 'fixed_price_fullupgrade'
    request['class'] = tariff
    request['requirements'] = {}
    request['comment'] = comment

    response = taxi_protocol.post('3.0/order', request)
    assert response.status_code == response_code
    if response_code != 200:
        response = response.json()
        assert 'error' in response
        assert 'code' in response['error']
        assert response['error']['code'] == error_code


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.order_experiments('surge_add_business')
@pytest.mark.filldb(users='with_ya_plus')
@pytest.mark.user_experiments('discount_strike', 'fixed_price', 'ya_plus')
@pytest.mark.config(
    YANDEX_PLUS_DISCOUNT={'rus': {'econom': 0.1, 'minivan': 0.1}},
)
@pytest.mark.parametrize('create_order', [make_order, make_order_draft_commit])
def test_order_with_ya_plus_user_without_offer(
        taxi_protocol,
        load_json,
        db,
        mockserver,
        create_order,
        check_order_matches_proc,
        pricing_data_preparer,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return get_surge_mock_response()

    request = load_json('basic_request_ya_plus_no_dst.json')
    response = create_order(taxi_protocol, request)
    order_id = response['orderid']
    # check in order_proc
    data = db.order_proc.find_one({'_id': order_id})
    assert data['price_modifiers']['items'][0]['reason'] == 'ya_plus'
    cat = data['price_modifiers']['items'][0]['tariff_categories'][0]
    assert cat == 'econom'
    cat = data['price_modifiers']['items'][0]['tariff_categories'][1]
    assert cat == 'minivan'
    # must be also in orders
    check_order_matches_proc(order_id)
    data = db.orders.find_one({'_id': order_id})
    assert data['price_modifiers']['items'][0]['reason'] == 'ya_plus'
    cat = data['price_modifiers']['items'][0]['tariff_categories'][0]
    assert cat == 'econom'
    cat = data['price_modifiers']['items'][0]['tariff_categories'][1]
    assert cat == 'minivan'


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.filldb(users='with_ya_plus')
@pytest.mark.parametrize('create_order', [make_order, make_order_draft_commit])
@pytest.mark.config(
    VGW_TOTW_DRIVER_VOICE_FORWARDING_ENABLED_ZONES={
        '__default__': False,
        'moscow': True,
    },
    VGW_TOTW_DRIVER_VOICE_FORWARDING_DISABLE_THRESHOLD_BY_COUNTRY={
        '__default__': 30,
    },
)
def test_order_with_vgw(
        taxi_protocol, load_json, db, create_order, check_order_matches_proc,
):
    request = load_json('basic_request_ya_plus.json')
    request['offer'] = 'ya_plus_multiplier'
    response = create_order(taxi_protocol, request)
    order_id = response['orderid']
    order = db.order_proc.find_one({'_id': order_id})
    assert order['fwd_driver_phone']
    check_order_matches_proc(order_id)


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.filldb(users='with_ya_plus')
@pytest.mark.parametrize('create_order', [make_order, make_order_draft_commit])
@pytest.mark.config(
    VGW_TOTW_DRIVER_VOICE_FORWARDING_ENABLED_ZONES={
        '__default__': False,
        'moscow': True,
    },
)
def test_order_no_vgw_not_newbie(
        taxi_protocol, load_json, db, create_order, check_order_matches_proc,
):
    request = load_json('basic_request_ya_plus.json')
    request['offer'] = 'ya_plus_multiplier'
    response = create_order(taxi_protocol, request)
    order_id = response['orderid']
    order = db.order_proc.find_one({'_id': order_id})
    assert not order['fwd_driver_phone']
    check_order_matches_proc(order_id)


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.parametrize('client_geo_sharing_enabled', [None, True, False])
def test_order_client_geo_sharing_enabled(
        taxi_protocol,
        load_json,
        db,
        client_geo_sharing_enabled,
        check_order_matches_proc,
        mockserver,
):
    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    request = load_json('basic_request.json')
    if client_geo_sharing_enabled is not None:
        request['client_geo_sharing_enabled'] = client_geo_sharing_enabled
    response = make_order(taxi_protocol, request)
    order_id = response['orderid']
    check_order_matches_proc(order_id)
    data = db.orders.find_one({'_id': order_id})
    assert data is not None
    if client_geo_sharing_enabled is not None:
        assert data['client_geo_sharing_enabled'] is client_geo_sharing_enabled
    else:
        assert 'client_geo_sharing_enabled' not in data
    order_proc = db.order_proc.find_one({'_id': order_id})
    assert 'order' in order_proc
    if client_geo_sharing_enabled is not None:
        assert (
            order_proc['order']['client_geo_sharing_enabled']
            is client_geo_sharing_enabled
        )
    else:
        assert 'client_geo_sharing_enabled' not in order_proc['order']


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.now('2018-07-06T14:15:16+0300')
@pytest.mark.filldb(cards='bin_filter', order_offers='empty')
@pytest.mark.parametrize(
    'payment_method_id, response_code, discount_result',
    [
        ('cash', 200, {'discounts': [], 'discount_offer_id': '123456'}),
        (
            'card-invalid',
            406,
            {'discounts': [], 'discount_offer_id': '123456'},
        ),
        (
            'card-no_discount',
            200,
            {'discounts': [], 'discount_offer_id': '123456'},
        ),
        (
            'card-discount',
            200,
            {
                'discounts': [
                    {
                        'class': 'econom',
                        'discount': {
                            'value': 0.1,
                            'price': 100,
                            'id': 'a122c228ba2b4d3189971a430ca6d2d3',
                            'reason': 'for_all',
                            'method': 'full',
                            'limit_id': '1a2b3c4d5e6f',
                        },
                    },
                ],
                'discount_offer_id': '123456',
            },
        ),
    ],
)
def test_order_bincard_discount(
        taxi_protocol,
        load_json,
        db,
        payment_method_id,
        response_code,
        discount_result,
        mockserver,
        load,
        check_order_matches_proc,
        cardstorage,
        pricing_data_preparer,
):
    _mock_pdp_discount(pricing_data_preparer, discount_result)

    cardstorage.trust_response = 'billing-cards-response-bin-filter.json'

    @mockserver.handler('/greed-ts1f.yandex.ru:8018/simple/xmlrpc')
    def mock_billing(request):
        data = load('lpm_bin_filter.xml')
        return mockserver.make_response(data, content_type='text/xml')

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    request = load_json('basic_request_2points.json')
    if payment_method_id == 'cash':
        payment = {'type': 'cash'}
    else:
        payment = {'type': 'card', 'payment_method_id': payment_method_id}
    request['payment'] = payment
    response = send_create_order_request(taxi_protocol, request)
    assert response.status_code == response_code
    if response_code != 200:
        return

    response = response.json()
    order_id = response['orderid']
    order_proc = db.order_proc.find_one({'_id': order_id})
    order = order_proc['order']
    if discount_result['discounts']:
        assert 'discount' in order
        discount = order['discount']
        assert discount['reason'] == 'for_all'
        assert 'by_classes' in discount
        econom_discount = _get_class_discount(discount['by_classes'], 'econom')
        assert econom_discount
        assert econom_discount['reason'] == 'for_all'
        assert econom_discount['limit_id'] == '1a2b3c4d5e6f'
    else:
        assert 'discount' not in order

    check_order_matches_proc(order_id)


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.now('2018-07-06T14:15:16+0300')
@pytest.mark.parametrize(
    'num_rides_applepay, discount_result',
    [
        (
            0,
            {
                'discounts': [
                    {
                        'class': 'econom',
                        'discount': {
                            'value': 0.1,
                            'price': 100,
                            'id': 'a122c228ba2b4d3189971a430ca6d2d3',
                            'reason': 'newbie_applepay',
                            'method': 'full',
                            'limit_id': '1a2b3c4d5e6f',
                        },
                    },
                ],
                'discount_offer_id': '123456',
            },
        ),
        (10, {'discounts': [], 'discount_offer_id': '123456'}),
    ],
)
@pytest.mark.filldb(order_offers='empty')
def test_order_applepay_discount(
        taxi_protocol,
        load_json,
        db,
        num_rides_applepay,
        discount_result,
        check_order_matches_proc,
        mockserver,
        pricing_data_preparer,
):
    _mock_pdp_discount(pricing_data_preparer, discount_result)

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    request = load_json('basic_request_2points.json')
    user = db.users.find_one({'_id': request['id']})
    phone_id = user['phone_id']
    result = db.user_phones.update(
        {'_id': phone_id},
        {'$set': {'stat.complete_apple': num_rides_applepay}},
    )
    assert result['nModified'] == 1
    response = send_create_order_request(taxi_protocol, request)
    assert response.status_code == 200

    response = response.json()
    order_id = response['orderid']
    order_proc = db.order_proc.find_one({'_id': order_id})
    order = order_proc['order']
    if discount_result['discounts']:
        assert 'discount' in order
        discount = order['discount']
        assert discount['reason'] == 'newbie_applepay'
        assert 'by_classes' in discount
        econom_discount = _get_class_discount(discount['by_classes'], 'econom')
        assert econom_discount
        assert econom_discount['reason'] == 'newbie_applepay'
        assert econom_discount['limit_id'] == '1a2b3c4d5e6f'
    else:
        assert 'discount' not in order

    check_order_matches_proc(order_id)


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.now('2018-07-06T14:15:16+0300')
@pytest.mark.parametrize(
    'num_rides, discount_result',
    [
        (
            1,
            {
                'discounts': [
                    {
                        'class': 'econom',
                        'discount': {
                            'value': 0.1,
                            'price': 100,
                            'id': 'a122c228ba2b4d3189971a430ca6d2d3',
                            'reason': 'analytics',
                            'method': 'full',
                            'limit_id': '1a2b3c4d5e6f',
                        },
                    },
                ],
                'discount_offer_id': '123456',
            },
        ),
        (2, {'discounts': [], 'discount_offer_id': '123456'}),
    ],
)
@pytest.mark.filldb(order_offers='empty')
@pytest.mark.user_experiments('use_discounts_service')
def test_order_limited_rides_discount(
        taxi_protocol,
        load_json,
        db,
        num_rides,
        discount_result,
        check_order_matches_proc,
        mockserver,
        pricing_data_preparer,
):
    _mock_pdp_discount(pricing_data_preparer, discount_result)

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    request = load_json('basic_request_2points.json')
    user = db.users.find_one({'_id': request['id']})
    phone_id = user['phone_id']
    result = db.discounts_usage_stats.update(
        {'phone_id': phone_id, 'discount_id': 'discount0'},
        {'$set': {'rides_count': num_rides}},
        upsert=True,
    )
    assert result['upserted']
    response = send_create_order_request(taxi_protocol, request)
    assert response.status_code == 200

    response = response.json()
    order_id = response['orderid']
    order_proc = db.order_proc.find_one({'_id': order_id})
    order = order_proc['order']
    if discount_result['discounts']:
        assert 'discount' in order
        discount = order['discount']
        assert discount['reason'] == 'analytics'
        assert 'by_classes' in discount
        econom_discount = _get_class_discount(discount['by_classes'], 'econom')
        assert econom_discount
        assert econom_discount['reason'] == 'analytics'
        assert econom_discount['limit_id'] == '1a2b3c4d5e6f'
    else:
        assert 'discount' not in order

    check_order_matches_proc(order_id)


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.order_experiments('fixed_price')
@pytest.mark.parametrize('create_order', [make_order, make_order_draft_commit])
@pytest.mark.parametrize(
    'cls, no_cars_order',
    [('econom', True), ('business', False), ('comfortplus', True)],
)
def test_order_no_cars_order(
        taxi_protocol,
        load_json,
        db,
        cls,
        no_cars_order,
        create_order,
        check_order_matches_proc,
):
    def check_fields_in_order(order):
        assert order != {}
        assert 'no_cars_order' in order
        assert order['no_cars_order'] == no_cars_order

    request = load_json('basic_request_fixprice.json')
    request['offer'] = 'no_cars_order'
    request['class'] = [cls]
    response = create_order(taxi_protocol, request)
    order_id = response['orderid']

    check_order_matches_proc(order_id)
    order_doc = db.orders.find_one({'_id': order_id})
    check_fields_in_order(order_doc)

    order_proc_doc = db.order_proc.find_one({'_id': order_id})
    assert 'order' in order_proc_doc
    check_fields_in_order(order_proc_doc['order'])
    assert 'user_tags' not in order_proc_doc['order']


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.order_experiments('fixed_price')
@pytest.mark.parametrize('create_order', [make_order, make_order_draft_commit])
@pytest.mark.parametrize(
    'cls, dp, psp',
    [
        ('econom', 335.0, 192.0),
        ('business', 336.0, 193.0),
        ('comfortplus', 337.0, None),
    ],
)
def test_order_paid_supply_price(
        taxi_protocol,
        load_json,
        db,
        cls,
        dp,
        psp,
        create_order,
        check_order_matches_proc,
):
    def check_fields_in_order(order):
        assert order != {}
        assert 'no_cars_order' in order
        assert not order['no_cars_order']
        fp = order['fixed_price']
        assert fp['driver_price'] == dp
        if psp is None:
            assert 'paid_supply_price' not in fp
        else:
            assert 'paid_supply_price' in fp
            assert fp['paid_supply_price'] == psp

    request = load_json('basic_request_fixprice.json')
    request['offer'] = 'paid_supply_price'
    request['class'] = [cls]
    response = create_order(taxi_protocol, request)
    order_id = response['orderid']

    check_order_matches_proc(order_id)
    order_doc = db.orders.find_one({'_id': order_id})
    check_fields_in_order(order_doc)

    order_proc_doc = db.order_proc.find_one({'_id': order_id})
    assert 'order' in order_proc_doc
    check_fields_in_order(order_proc_doc['order'])
    assert 'user_tags' not in order_proc_doc['order']
    assert 'paid_cancel_in_driving' not in order_proc_doc['order']


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.order_experiments('fixed_price')
@pytest.mark.parametrize('create_order', [make_order, make_order_draft_commit])
def test_order_user_tags(
        taxi_protocol, load_json, db, create_order, check_order_matches_proc,
):
    request = load_json('basic_request_fixprice.json')
    request['offer'] = 'user_tags'
    request['class'] = ['econom']
    response = create_order(taxi_protocol, request)
    order_id = response['orderid']

    check_order_matches_proc(order_id)

    order_proc_doc = db.order_proc.find_one({'_id': order_id})
    assert 'order' in order_proc_doc
    assert 'user_tags' in order_proc_doc['order']
    user_tags = set(order_proc_doc['order']['user_tags'])
    assert user_tags == set(['tag1', 'tag2', 'third_tag'])


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.order_experiments('fixed_price')
@pytest.mark.parametrize('create_order', [make_order, make_order_draft_commit])
def test_order_paid_cancel_in_driving(
        taxi_protocol, load_json, db, create_order, check_order_matches_proc,
):
    request = load_json('basic_request_fixprice.json')
    request['offer'] = 'paid_cancel_in_driving'
    request['class'] = ['business']
    response = create_order(taxi_protocol, request)
    order_id = response['orderid']

    check_order_matches_proc(order_id)

    order_proc_doc = db.order_proc.find_one({'_id': order_id})
    assert 'order' in order_proc_doc
    assert 'paid_cancel_in_driving' in order_proc_doc['order']
    paid_cancel_in_driving = order_proc_doc['order']['paid_cancel_in_driving']
    assert paid_cancel_in_driving == {
        'price': 109,
        'free_cancel_timeout': 320,
        'for_paid_supply': False,
    }


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.order_experiments('fixed_price')
@pytest.mark.parametrize('create_order', [make_order, make_order_draft_commit])
def test_order_pricing_data(
        taxi_protocol, load_json, db, create_order, check_order_matches_proc,
):
    request = load_json('basic_request_fixprice.json')
    request['offer'] = 'pricing_data'
    request['class'] = ['business']
    response = create_order(taxi_protocol, request)
    order_id = response['orderid']

    check_order_matches_proc(order_id)

    order_proc_doc = db.order_proc.find_one({'_id': order_id})
    assert 'order' in order_proc_doc
    assert 'pricing_data' in order_proc_doc['order']
    pricing_data = order_proc_doc['order']['pricing_data']
    assert pricing_data == load_json('pricing_data.json')


def check_order_pick_method(order_id, db, metrica_action, metrica_method):
    order = db.orders.find_one({'_id': order_id})
    assert 'request' in order
    request = order['request']
    assert 'source' in request
    source = request['source']

    assert 'metrica_method' in source
    assert source['metrica_method'] == metrica_method

    assert 'metrica_action' in source
    assert source['metrica_action'] == metrica_action


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.now('2018-07-06T14:15:16+0300')
def test_order_metrica_method(
        taxi_protocol, mockserver, load_json, db, check_order_matches_proc,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return get_surge_mock_response()

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return get_yamaps_mock_response(request, load_json)

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    response_body = make_order(
        taxi_protocol, load_json('basic_request_with_metrica_method.json'),
    )
    order_id = response_body['orderid']
    check_order_matches_proc(order_id)
    assert response_body['status'] == 'search'
    check_order_pick_method(order_id, db, 'manual', 'nearestposition')


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.parametrize(
    'request_json,num_completed_orders,phone_forwarded',
    [
        ('basic_request.json', 4, True),
        ('basic_request.json', 5, False),
        ('basic_request_kaz.json', 9, True),
        ('basic_request_kaz.json', 10, False),
    ],
)
@pytest.mark.config(
    VGW_TOTW_DRIVER_VOICE_FORWARDING_DISABLE_THRESHOLD_BY_COUNTRY={
        '__default__': 5,
        'kaz': 10,
    },
)
@pytest.mark.filldb(
    user_phones='complete_update', tariffs='with_almaty_workday_category',
)
def test_order_vgw_driver_voice_forwarding_disable(
        taxi_protocol,
        mockserver,
        load_json,
        db,
        request_json,
        num_completed_orders,
        phone_forwarded,
        check_order_matches_proc,
        pricing_data_preparer,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(_):
        return get_surge_mock_response()

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    request = load_json(request_json)
    db.user_phones.update(
        {'phone': request['terminal']['phone']},
        {'$set': {'stat.complete': num_completed_orders}},
    )

    response = make_order(taxi_protocol, request)
    order_id = response['orderid']
    order = db.order_proc.find_one({'_id': order_id})

    assert phone_forwarded == order['fwd_driver_phone']
    check_order_matches_proc(order_id)


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.parametrize('personal_wallet_enabled', [None, True, False])
@pytest.mark.parametrize('create_order', [make_order, make_order_draft_commit])
def test_order_personal_wallet_enabled(
        taxi_protocol,
        load_json,
        db,
        personal_wallet_enabled,
        create_order,
        check_order_matches_proc,
        mockserver,
):
    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    request = load_json('basic_request.json')
    if personal_wallet_enabled is not None:
        request['personal_wallet_enabled'] = personal_wallet_enabled
    response = create_order(taxi_protocol, request)
    order_id = response['orderid']
    check_order_matches_proc(order_id)
    data = db.orders.find_one({'_id': order_id})
    assert data is not None
    if personal_wallet_enabled is not None:
        assert data['personal_wallet_enabled'] is personal_wallet_enabled
    else:
        assert 'personal_wallet_enabled' not in data
    order_proc = db.order_proc.find_one({'_id': order_id})
    assert 'order' in order_proc
    if personal_wallet_enabled is not None:
        assert (
            order_proc['order']['personal_wallet_enabled']
            is personal_wallet_enabled
        )
    else:
        assert 'personal_wallet_enabled' not in order_proc['order']


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.filldb(tariff_settings='creditcard')
@pytest.mark.parametrize('create_order', [make_order, make_order_draft_commit])
def test_order_family_member_card(
        taxi_protocol,
        load,
        load_json,
        db,
        mockserver,
        check_order_matches_proc,
        cardstorage,
        pricing_data_preparer,
        create_order,
):
    cardstorage.trust_response = 'billing-cards-response-family-member.json'

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 1.2,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }

    request = load_json('basic_request_card.json')
    response = create_order(taxi_protocol, request)
    order_id = response['orderid']
    check_order_matches_proc(order_id)
    order = db.orders.find_one({'_id': order_id})
    payment_tech = order['payment_tech']
    assert 'family' in payment_tech
    card = db.cards.find_one({'payment_id': 'card-x8502'})
    assert card['persistent_id'] == payment_tech['main_card_persistent_id']


@pytest.fixture
def check_order_matches_proc(
        db, taxi_protocol, mock_order_core, protocol_use_order_core,
):
    def check(order_id):
        proc = db.order_proc.find_one(order_id)

        assert db.orders.find_one(order_id) is None
        make_order_from_proc(taxi_protocol, order_id)
        assert mock_order_core.get_fields_times_called == int(
            protocol_use_order_core,
        )

        order = db.orders.find_one(order_id)
        assert order is not None
        order_app = order['statistics']['application']
        proc['order']['request'].pop('supported', None)
        assert proc['order'].pop('application', None) == order_app

        assert proc['payment_tech'] == order['payment_tech']

        # todo maybe we need same in proc in order, may be not
        proc['order']['status_updated'] = order['status_updated']
        assert order.pop('payment_tech', None) is not None
        assert order.pop('updated') is not None
        assert proc['order'].pop('user_ready', None) is False
        assert proc['order'].pop('cost') is None

        if (
                'offer' in proc['order']['request']
                and proc['order']['request']['offer'] == 'paid_supply_price'
        ):
            assert proc['order'].pop('routestats_link') == 'routestats-link'
            assert proc['order'].pop('routestats_type') == 'routestats'

        for only_in_order_proc in [
                'user_tags',
                'paid_cancel_in_driving',
                'pricing_data',
                'using_new_pricing',
                'fixed_price_discard_reason',
                'current_prices',
                'personal_phone_id',
        ]:
            if only_in_order_proc in proc['order']:
                del proc['order'][only_in_order_proc]
        assert proc['order'] == order

    return check


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.now('2018-04-24T10:15:00+0000')
@pytest.mark.parametrize(
    'create_order,support_commit',
    [
        (make_order, True),
        # (make_order_draft_commit, False),
    ],
)
def test_without_params(
        taxi_protocol,
        load_json,
        db,
        create_order,
        yamaps,
        support_commit,
        check_order_matches_proc,
        mockserver,
        mock_stq_agent,
        pricing_data_preparer,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return get_surge_mock_response()

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return get_yamaps_mock_response(request, load_json)

    locale = 'en'

    yamaps.location_add(
        [37.50, 55.70],
        {'short_text': 'point A %s' % locale},
        lang=locale,
        uri='point_1',
    )

    yamaps.location_add(
        [37.60, 55.80],
        {'short_text': 'point B %s' % locale},
        lang=locale,
        uri='point_2',
    )

    response_body = create_order(
        taxi_protocol,
        load_json('basic_request_without_params.json'),
        x_real_ip='my-ip-address',
    )

    order_id = response_body['orderid']
    assert response_body['status'] == 'search'
    check_created_order_in_stq(order_id, mock_stq_agent, support_commit)

    check_order_matches_proc(order_id)

    order = db.orders.find_one(order_id)
    proc = db.order_proc.find_one(order_id)

    assert order['request']['ip'] == 'my-ip-address'
    assert proc['order']['request']['ip'] == 'my-ip-address'

    waited_response = load_json('ans_for_request_without_params.json')
    assert order['request']['source'] == waited_response['source']
    assert order['request']['destinations'] == waited_response['destinations']


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.filldb(users='with_ya_plus')
@pytest.mark.parametrize('create_order', [make_order, make_order_draft_commit])
@pytest.mark.config(VGW_USE_EXPERIMENTS3=True)
@pytest.mark.parametrize(
    ['expected_fwd_driver_phone'],
    [
        pytest.param(
            True,
            marks=[
                pytest.mark.experiments3(
                    filename='experiments3_softswitch.json',
                ),
            ],
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.experiments3(
                    filename='experiments3_softswitch_override_true.json',
                ),
            ],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.experiments3(
                    filename='experiments3_softswitch_override_false.json',
                ),
            ],
        ),
    ],
)
def test_order_with_vgw_experiments3(
        taxi_protocol,
        load_json,
        db,
        create_order,
        check_order_matches_proc,
        expected_fwd_driver_phone,
):
    request = load_json('basic_request_ya_plus.json')
    request['offer'] = 'ya_plus_multiplier'
    response = create_order(taxi_protocol, request)
    order_id = response['orderid']
    order = db.order_proc.find_one({'_id': order_id})
    assert order['fwd_driver_phone'] == expected_fwd_driver_phone
    check_order_matches_proc(order_id)


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.parametrize(
    'request_json,num_completed_orders,phone_forwarded',
    [
        ('basic_request.json', 2, True),
        ('basic_request.json', 30, True),
        ('basic_request_kaz.json', 4, True),
        ('basic_request_kaz.json', 6, False),
    ],
)
@pytest.mark.config(
    VGW_TOTW_DRIVER_VOICE_FORWARDING_DISABLE_THRESHOLD_BY_COUNTRY={
        '__default__': 5,
        'kaz': 10,
    },
    VGW_USE_EXPERIMENTS3=True,
)
@pytest.mark.filldb(
    user_phones='complete_update', tariffs='with_almaty_workday_category',
)
@pytest.mark.experiments3(filename='experiments3_softswitch.json')
def test_order_vgw_driver_voice_forwarding_disable_experiments3(
        taxi_protocol,
        mockserver,
        load_json,
        db,
        request_json,
        num_completed_orders,
        phone_forwarded,
        check_order_matches_proc,
        pricing_data_preparer,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(_):
        return get_surge_mock_response()

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    request = load_json(request_json)
    db.user_phones.update(
        {'phone': request['terminal']['phone']},
        {'$set': {'stat.complete': num_completed_orders}},
    )

    response = make_order(taxi_protocol, request)
    order_id = response['orderid']
    order = db.order_proc.find_one({'_id': order_id})

    assert phone_forwarded == order['fwd_driver_phone']
    check_order_matches_proc(order_id)


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.now('2019-10-22T11:32:00+0300')
@pytest.mark.config(CSH_METADATA_STORAGE_ENABLED=True)
@pytest.mark.experiments3(filename='exp3_very_busy.json')
def test_order_metadata_storage(
        taxi_protocol, load_json, check_order_matches_proc, mockserver,
):
    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    @mockserver.json_handler('/metadata_storage/v1/metadata/store')
    def mock_metadata_store(request):
        data = json.loads(request.get_data())
        experiments = [item['name'] for item in data['value']['experiments']]
        assert 'very_busy' in experiments
        return mockserver.make_response('', 200)

    request = load_json('basic_request.json')
    response = make_order(taxi_protocol, request)
    check_order_matches_proc(response['orderid'])

    end = datetime.datetime.now() + datetime.timedelta(seconds=5)
    while datetime.datetime.now() < end:
        if mock_metadata_store.has_calls:
            break
        time.sleep(0.1)
    assert mock_metadata_store.has_calls


@pytest.mark.parametrize('user_had_choice', [True, False])
@pytest.mark.parametrize('user_chose_toll_road', [True, False])
def test_order_with_toll_roads(
        taxi_protocol, load_json, db, user_had_choice, user_chose_toll_road,
):
    request = load_json('basic_request_nonfixprice.json')
    toll_roads = {
        'user_had_choice': user_had_choice,
        'user_chose_toll_road': user_chose_toll_road,
    }
    request['toll_roads'] = toll_roads
    response = make_order(taxi_protocol, request)
    order_id = response['orderid']
    order_proc = db.order_proc.find_one({'_id': order_id})
    assert 'order' in order_proc
    assert 'request' in order_proc['order']
    assert 'toll_roads' in order_proc['order']['request']
    assert order_proc['order']['request']['toll_roads'] == toll_roads


def test_order_without_toll_roads(taxi_protocol, load_json, db):
    request = load_json('basic_request_nonfixprice.json')
    response = make_order(taxi_protocol, request)
    order_id = response['orderid']
    order_proc = db.order_proc.find_one({'_id': order_id})
    assert 'order' in order_proc
    assert 'request' in order_proc['order']
    assert 'toll_roads' not in order_proc['order']['request']


@pytest.mark.parametrize(
    'toll_roads',
    [{}, {'user_had_choice': False}, {'user_chose_toll_road': False}],
)
def test_order_incorrect_toll_roads(taxi_protocol, load_json, db, toll_roads):
    request = load_json('basic_request_nonfixprice.json')
    request['toll_roads'] = toll_roads
    response = send_create_order_request(taxi_protocol, request)
    assert response.status_code == 400


@pytest.mark.experiments3(filename='experiments3_use_card_antifraud.json')
@pytest.mark.parametrize(
    'ca_code,all_payments_available,available_cards,uid_type,expected_code',
    [
        (200, True, [], 'portal', 200),
        (200, False, [{'card_id': 'card-x8502'}], 'portal', 200),
        (200, False, [], 'portal', 406),
        (500, False, [], 'portal', 200),
        (200, False, [], 'phonish', 200),
    ],
    ids=[
        'device_verified',
        'card_in_verified_cards',
        'empty_verified_cards',
        'card_antifraud_unavailable',
        'user_not_portal',
    ],
)
def test_card_antifraud(
        taxi_protocol,
        load_json,
        mockserver,
        db,
        ca_code,
        all_payments_available,
        available_cards,
        uid_type,
        expected_code,
        pricing_data_preparer,
):
    @mockserver.json_handler('/card_antifraud/v1/payment/availability')
    def _mock_ca_payment_availability(request):
        response = {
            'all_payments_available': all_payments_available,
            'available_cards': available_cards,
        }
        return mockserver.make_response(
            json.dumps(response) if ca_code == 200 else '', ca_code,
        )

    request = load_json('basic_request_card.json')
    user_id = request['id']
    db.users.update({'_id': user_id}, {'$set': {'yandex_uid_type': uid_type}})

    response = send_create_order_request(taxi_protocol, request)

    code = response.status_code
    assert response.status_code == expected_code
    if code == 406:
        assert response.json() == {'error': {'code': 'NEED_CARD_ANTIFRAUD'}}


@pytest.mark.experiments3(filename='experiments3_use_card_antifraud.json')
def test_card_antifraud_not_card(taxi_protocol, load_json, mockserver):
    @mockserver.json_handler('/ucommunications/user/sms/send')
    def _mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    @mockserver.json_handler('/addrs.yandex/search')
    def _mock_yamaps(request):
        return get_yamaps_mock_response(request, load_json)

    @mockserver.json_handler('/card_antifraud/v1/payment/availability')
    def _mock_ca_payment_availability(request):
        return mockserver.make_response('', 200)

    request = load_json('basic_request.json')
    make_order(taxi_protocol, request)

    assert not _mock_ca_payment_availability.has_calls


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
@pytest.mark.experiments3(filename='experiments3_use_card_antifraud.json')
def test_card_antifraud_app_version(
        taxi_protocol,
        mockserver,
        db,
        load_json,
        user_agent,
        expected_code,
        pricing_data_preparer,
):
    @mockserver.json_handler('/card_antifraud/v1/payment/availability')
    def _mock_ca_payment_availability(request):
        response = {'all_payments_available': False, 'available_cards': []}
        return mockserver.make_response(json.dumps(response), 200)

    request = load_json('basic_request_card.json')
    user_id = request['id']
    db.users.update({'_id': user_id}, {'$set': {'yandex_uid_type': 'portal'}})
    headers = {'User-Agent': user_agent}

    response = send_create_order_request(
        taxi_protocol, request, headers=headers,
    )

    code = response.status_code
    assert response.status_code == expected_code
    if code == 406:
        assert response.json() == {'error': {'code': 'NEED_CARD_ANTIFRAUD'}}


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.parametrize('create_order', [make_order, make_order_draft_commit])
@pytest.mark.parametrize('support_commit', [True, False])
@pytest.mark.parametrize('with_request_extra_fields', [True, False])
def test_order_with_request_extra_fields(
        taxi_protocol,
        mockserver,
        load_json,
        db,
        create_order,
        support_commit,
        with_request_extra_fields,
        check_order_matches_proc,
        mock_stq_agent,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return get_surge_mock_response()

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return get_yamaps_mock_response(request, load_json)

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    if with_request_extra_fields:
        request = load_json('extra_fields_request.json')
    else:
        request = load_json('basic_request.json')

    response_body = create_order(
        taxi_protocol, request, x_real_ip='my-ip-address',
    )
    order_id = response_body['orderid']
    assert response_body['status'] == 'search'
    check_created_order_in_stq(order_id, mock_stq_agent, support_commit)

    check_order_matches_proc(order_id)

    order = db.orders.find_one(order_id)
    proc = db.order_proc.find_one(order_id)
    assert order['request']['ip'] == 'my-ip-address'
    assert proc['order']['request']['ip'] == 'my-ip-address'
    assert order['creditcard']['tips'] == {'type': 'percent', 'value': 5}
    assert order['creditcard']['tips_perc_default'] == 5
    assert 'cost' not in order
    assert proc['order']['cost'] is None
    if with_request_extra_fields:
        assert proc['order']['request']['lookup_ttl'] == 117
        assert order['request']['lookup_ttl'] == 117
        assert (
            proc['order']['request']['dispatch_type'] == 'logistic-dispatcher'
        )
        assert order['request']['dispatch_type'] == 'logistic-dispatcher'
        assert proc['order']['request']['lookup_extra'] == {
            'intent': 'grocery',
            'performer_id': 'dbid_uuid',
        }
        assert order['request']['lookup_extra'] == {
            'intent': 'grocery',
            'performer_id': 'dbid_uuid',
        }
        assert proc['order']['request']['just_partner_payments'] is True
        assert order['request']['just_partner_payments'] is True
        assert proc['order']['request']['check_new_logistic_contract'] is True
        assert order['request']['check_new_logistic_contract'] is True
        assert proc['order']['request']['shift'] == {
            'type': 'grocery',
            'zone_group': {'required_ids': ['depot_1', 'depot_2']},
        }
        assert order['request']['shift'] == {
            'type': 'grocery',
            'zone_group': {'required_ids': ['depot_1', 'depot_2']},
        }
        assert order['request']['eats_batch'] == [
            {
                'context': {
                    'cooking_time': 420,
                    'items_cost': {'currency': 'RUB', 'value': '100'},
                    'delivery_cost': {'currency': 'RUB', 'value': '15'},
                    'route_to_client': {
                        'pedestrian': {
                            'distance': 123.12,
                            'time': 120,
                            'is_precise': True,
                        },
                        'transit': {
                            'distance': 153.26,
                            'time': 100,
                            'is_precise': True,
                        },
                        'auto': {
                            'distance': 243.26,
                            'time': 50,
                            'is_precise': False,
                        },
                    },
                    'delivery_flow_type': 'courier',
                    'device_id': 'test_device_id',
                    'has_slot': False,
                    'is_asap': True,
                    'is_fast_food': True,
                    'logistic_group': 'ya_eats_group',
                    'order_confirmed_at': 1635516057000,
                    'order_flow_type': 'native',
                    'order_id': 275270737,
                    'order_must_be_delivered_at': 1635516057000,
                    'promise_max_at': 1635516057000,
                    'promise_min_at': 1635516057000,
                    'region_id': 1,
                    'send_to_place_at': 1635516057000,
                    'order_cancel_at': 1635516057000,
                    'weight': '1.5',
                    'place_id': 999,
                },
            },
        ]
        assert (
            proc['order']['request']['eats_batch']
            == order['request']['eats_batch']
        )
        assert proc['order']['request']['delivery'] == {
            'include_rovers': True,
            'is_phoenix_payment_flow': False,
        }
        assert order['request']['delivery'] == {
            'include_rovers': True,
            'is_phoenix_payment_flow': False,
        }
    else:
        assert 'lookup_extra' not in proc['order']['request']
        assert 'lookup_extra' not in order['request']
        assert 'lookup_ttl' not in proc['order']['request']
        assert 'lookup_ttl' not in order['request']
        assert 'dispatch_type' not in proc['order']['request']
        assert 'dispatch_type' not in order['request']
        assert 'just_partner_payments' not in proc['order']['request']
        assert 'just_partner_payments' not in order['request']
        assert 'check_new_logistic_contract' not in proc['order']['request']
        assert 'check_new_logistic_contract' not in order['request']
        assert 'shift' not in proc['order']['request']
        assert 'shift' not in order['request']
        assert 'eats_batch' not in proc['order']['request']
        assert 'eats_batch' not in order['request']
        assert 'delivery' not in proc['order']['request']
        assert 'delivery' not in order['request']


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.parametrize(
    ['create_order', 'support_commit'],
    [(make_order, True), (make_order_draft_commit, False)],
)
@pytest.mark.parametrize('with_lookup_ttl_from_request', [False, True])
@pytest.mark.parametrize('with_lookup_ttl_from_exp', [False, True])
@pytest.mark.parametrize('with_alternative_type', [False, True])
def test_order_lookup_ttl_from_experiment(
        taxi_protocol,
        mockserver,
        load_json,
        db,
        experiments3,
        check_order_matches_proc,
        mock_stq_agent,
        create_order,
        support_commit,
        with_lookup_ttl_from_request,
        with_lookup_ttl_from_exp,
        with_alternative_type,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return get_surge_mock_response()

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return get_yamaps_mock_response(request, load_json)

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    experiments3.add_experiment(
        match={
            'predicate': {'type': 'true'},
            'enabled': with_lookup_ttl_from_exp,
        },
        name='global_control_lookup_ttl',
        consumers=['protocol/createdraft'],
        clauses=[
            {
                'title': 'clause for alt type',
                'value': {'lookup_ttl_sec': 379},
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'alternative_type',
                        'arg_type': 'string',
                        'value': 'some_alternative_type',
                    },
                },
            },
            {
                'title': 'use old scoring logic',
                'value': {'lookup_ttl_sec': 248},
                'predicate': {'type': 'true'},
            },
        ],
    )

    request = load_json('basic_request.json')
    if with_lookup_ttl_from_request:
        request['lookup_ttl'] = 117
    if with_alternative_type:
        request['alternative_type'] = 'some_alternative_type'
    response_body = create_order(
        taxi_protocol, request, x_real_ip='my-ip-address',
    )
    order_id = response_body['orderid']
    assert response_body['status'] == 'search'
    check_created_order_in_stq(order_id, mock_stq_agent, support_commit)

    check_order_matches_proc(order_id)

    order = db.orders.find_one(order_id)
    proc = db.order_proc.find_one(order_id)
    assert order['request']['ip'] == 'my-ip-address'
    assert proc['order']['request']['ip'] == 'my-ip-address'
    assert order['creditcard']['tips'] == {'type': 'percent', 'value': 5}
    assert order['creditcard']['tips_perc_default'] == 5
    assert 'cost' not in order
    assert proc['order']['cost'] is None
    if with_lookup_ttl_from_request:
        assert proc['order']['request']['lookup_ttl'] == 117
        assert order['request']['lookup_ttl'] == 117
    elif with_lookup_ttl_from_exp and with_alternative_type:
        assert proc['order']['request']['lookup_ttl'] == 379
        assert order['request']['lookup_ttl'] == 379
    elif with_lookup_ttl_from_exp:
        assert proc['order']['request']['lookup_ttl'] == 248
        assert order['request']['lookup_ttl'] == 248
    else:
        assert proc['order']['request'].get('lookup_ttl') is None
        assert order['request'].get('lookup_ttl') is None


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.parametrize(
    'create_order,support_commit, with_is_delayed',
    [
        (make_order, True, True),
        (make_order_draft_commit, False, True),
        (make_order, True, False),
        (make_order_draft_commit, False, False),
    ],
)
def test_order_is_delayed(
        taxi_protocol,
        mockserver,
        load_json,
        db,
        create_order,
        support_commit,
        with_is_delayed,
        check_order_matches_proc,
        mock_stq_agent,
        pricing_data_preparer,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return get_surge_mock_response()

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return get_yamaps_mock_response(request, load_json)

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    if with_is_delayed:
        request = load_json('is_delayed_request.json')
    else:
        request = load_json('basic_request.json')
    response_body = create_order(
        taxi_protocol, request, x_real_ip='my-ip-address',
    )
    order_id = response_body['orderid']
    assert response_body['status'] == 'search'
    check_created_order_in_stq(order_id, mock_stq_agent, support_commit)

    check_order_matches_proc(order_id)

    order = db.orders.find_one(order_id)
    proc = db.order_proc.find_one(order_id)
    assert order['request']['ip'] == 'my-ip-address'
    assert proc['order']['request']['ip'] == 'my-ip-address'
    assert order['creditcard']['tips'] == {'type': 'percent', 'value': 5}
    assert order['creditcard']['tips_perc_default'] == 5
    assert 'cost' not in order
    assert proc['order']['cost'] is None
    if with_is_delayed:
        assert proc['order']['request']['is_delayed'] is True
        assert order['request']['is_delayed'] is True
    else:
        assert proc['order']['request'].get('is_delayed') is None
        assert order['request'].get('is_delayed') is None


def test_is_delayed_bad_request(taxi_protocol, load_json):
    request = load_json('is_delayed_request.json')
    request.pop('due', None)
    response = send_create_order_request(taxi_protocol, request)
    assert response.status_code == 400
    assert response.json() == {
        'error': {'text': 'is_delayed field is true while due is not passed'},
    }


@pytest.mark.experiments3(filename='experiments3_use_card_antifraud.json')
def test_card_antifraud_login_id(
        taxi_protocol, load_json, mockserver, db, pricing_data_preparer,
):
    @mockserver.json_handler('/card_antifraud/v1/payment/availability')
    def mock_ca_payment_availability(request):
        assert request.args.to_dict() == {
            'user_id': 'f4eb6aaa29ad4a6eb53f8a7620793123',
            'card_id': 'card-x8502',
            'yandex_uid': '4003514123',
            'yandex_login_id': 't:1234',
        }
        response = {'all_payments_available': True, 'available_cards': []}
        return response

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        query = set(request.query_string.decode().split('&'))
        assert 'get_login_id=yes' in query
        return {
            'uid': {'value': '4003514123'},
            'status': {'value': 'VALID'},
            'login_id': 't:1234',
            'oauth': {'scope': 'yataxi:read yataxi:write yataxi:pay'},
            'phones': [
                {'attributes': {'102': '+74956661123'}, 'id': '1111'},
                {
                    'attributes': {'102': '+72222222222', '107': '1'},
                    'id': '2222',
                },
            ],
        }

    request = load_json('basic_request_card.json')
    user_id = request['id']
    db.users.update({'_id': user_id}, {'$set': {'yandex_uid_type': 'portal'}})

    response = send_create_order_request(
        taxi_protocol, request, bearer='test_token', x_real_ip='my-ip-address',
    )

    assert response.status_code == 200
    assert mock_ca_payment_availability.has_calls is True
    assert mock_blackbox.has_calls is True


@PROTOCOL_USE_ORDER_CORE
@pytest.mark.parametrize('create_order', [make_order, make_order_draft_commit])
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_order_corp(
        mockserver,
        taxi_protocol,
        load_json,
        db,
        create_order,
        check_order_matches_proc,
):
    @mockserver.json_handler('/corp_integration_api/corp_paymentmethods')
    def mock_corp_paymentmethods(request):
        method = {
            'type': 'corp',
            'id': 'corp-b22a310c841f47b2b1b459b0bb4430c0',
            'label': '-',
            'description': '-',
            'can_order': True,
            'cost_center': '',
            'zone_available': True,
            'hide_user_cost': False,
            'user_id': 'corp_user_id',
            'client_comment': 'corp_comment',
            'currency': 'RUB',
            'without_vat_contract': True,
        }
        return {'methods': [method]}

    request = load_json('basic_request_corp.json')
    response = create_order(taxi_protocol, request)
    order_id = response['orderid']
    check_order_matches_proc(order_id)
