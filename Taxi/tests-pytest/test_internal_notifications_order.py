# coding: utf-8
from __future__ import unicode_literals

import datetime
import collections

import json
import pytest

from taxi import config
from taxi.core import async
from taxi.core import db
from taxi.external import experiments3
from taxi.internal import dbh
from taxi.internal.notifications import order as notify
from taxi.internal.order_kit.plg import order_fsm, status_handling
from taxi.util import dates

from cardstorage_mock import mock_cardstorage
import helpers

NOW = datetime.datetime(2017, 6, 23)
MAGIC_UUID = u'2830227ea6944f95b894d27df5f9ace4'
FOR_OTHER_PUSH_ON_WAITING = 'on waiting'
FOR_OTHER_PUSH_CARD = 'for other card'
FOR_OTHER_PUSH_CASH = 'for other cash'


def _make_payload(text, status, order_id):
    return {
        'notification': {
            'deeplink': 'yandextaxi://linkedorder?key={}',
            'text': text
        },
        'from_uid': None,
        'intent': 'taxi_order_for_other_' + status,
        'meta': {'order_id': order_id},
        'locale': 'ru',
    }


@pytest.inline_callbacks
def mock_notify_on_driver_arriving_without_eta(proc, log_extra):
    result = yield notify.notify_on_driver_arriving(proc, None, log_extra)
    async.return_value(result)


@pytest.inline_callbacks
def mock_notify_on_driver_arriving_with_eta(proc, log_extra):
    result = yield notify.notify_on_driver_arriving(proc, 420, log_extra)
    async.return_value(result)


@pytest.fixture
def mocks_for_other_notification(patch):
    @patch('taxi_stq.client.add_notification_task')
    def add_notification_task(*args, **kwargs):
        return

    @patch('uuid.uuid4')
    def uuid4():
        uuid4_ = collections.namedtuple('uuid4', 'hex')
        return uuid4_(MAGIC_UUID)

    @patch('taxi.internal.notifications.order._arrival_interval')
    def _arrival_interval(*args, **kwargs):
        return False, 1

    @patch('taxi.internal.notifications.order._prepare_car_number')
    def _prepare_car_number(*args, **kwargs):
        return None

    @patch('taxi.internal.order_kit.invoice_handler.finish_check_card')
    def finish_check_card(*args, **kwargs):
        return

    @patch('taxi.internal.order_kit.plg.status_handling._log_arrival_time')
    def _log_arrival_time(*args, **kwargs):
        return

    @patch('taxi.internal.driver_manager._set_brand_model')
    def _set_brand_model(brand, model, car_doc):
        car_doc['brand'] = brand
        car_doc['model'] = model

    @patch('taxi.internal.driver_manager._set_color')
    def _set_color(color, car_doc):
        assert color == 'red'
        car_doc['color'] = 'red'
        car_doc['color_code'] = 'FAFBFB'

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    @patch('taxi.external.userapi.get_user_phone')
    def get_user_phone(phone_id, *args, **kwargs):
        if phone_id == 'phone_id1':
            return helpers.get_user_api_response('personal_phone_id1')
        elif phone_id == 'other_user_id1':
            return helpers.get_user_api_response('other_personal_phone_id1')


@pytest.fixture(autouse=True)
def mock_exp3_get_values(patch):
    @patch('taxi.external.experiments3.get_values')
    @async.inline_callbacks
    def _mock_exp3_get_values(*args, **kwargs):
        yield
        result = [
            experiments3.ExperimentsValue(
                name='order_client_notification',
                value={'enabled': False}
            )
        ]

        async.return_value(result)


@pytest.mark.filldb()
@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations([
    ('client_messages', 'time', 'ru', 'time'),
    ('notify', 'apns.moved_to_cash', 'ru', 'apns.text'),
    ('notify', 'apns.moved_to_cash_with_coupon', 'ru', 'apns.text2'),
    ('notify', 'time', 'ru', 'time'),
])
@pytest.mark.parametrize('with_coupon,event,text', [
    (False, 'apns.moved_to_cash', 'apns.text'),
    (True, 'apns.moved_to_cash_with_coupon', 'apns.text2'),
])
@pytest.inline_callbacks
def test_notify_on_moved_to_cash_aspn(patch, with_coupon, event, text):

    @patch('taxi.internal.dbh.notifications_queue.new_task')
    def new_task(*args, **kwargs):
        return dbh.notifications_queue.Doc()

    @patch('taxi_stq.client.add_notification_task')
    def add_notification_task(*args, **kwargs):
        return

    @patch('uuid.uuid4')
    def uuid4():
        uuid4_ = collections.namedtuple('uuid4', 'hex')
        return uuid4_(MAGIC_UUID)

    order_id = 'order_id1'
    user = yield dbh.users.Doc.find_one_by_id('iphone_user')
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc.order.request.due = NOW + datetime.timedelta(minutes=10)
    state = order_fsm.OrderFsm(proc=proc)
    yield notify.notify_on_moved_to_cash(state, with_coupon, None)

    calls = new_task.calls
    assert len(calls) == 1
    assert calls[0]['args'] == _get_expected_apns_args(
        user, order_id, event, text)


@pytest.mark.filldb()
@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations([
    ('client_messages', 'time', 'ru', 'time'),
    ('notify', 'apns.debt_allowed', 'ru', 'apns.text'),
    ('notify', 'time', 'ru', 'time'),
])
@pytest.inline_callbacks
def test_notify_on_debt_allowed(patch):

    @patch('taxi.internal.dbh.notifications_queue.new_task')
    def new_task(*args, **kwargs):
        return dbh.notifications_queue.Doc()

    @patch('taxi_stq.client.add_notification_task')
    def add_notification_task(*args, **kwargs):
        return

    @patch('uuid.uuid4')
    def uuid4():
        uuid4_ = collections.namedtuple('uuid4', 'hex')
        return uuid4_(MAGIC_UUID)

    order_id = 'order_id_debt'
    user = yield dbh.users.Doc.find_one_by_id('iphone_user')
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc.order.request.due = NOW + datetime.timedelta(minutes=10)
    state = order_fsm.OrderFsm(proc=proc)
    yield notify.notify_on_debt_allowed(state, None)

    calls = new_task.calls
    assert len(calls) == 1
    assert calls[0]['args'] == _get_expected_apns_args(
        user, order_id, 'apns.debt_allowed', 'apns.text')


@pytest.mark.filldb()
@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations([
    ('client_messages', 'time', 'ru', 'time'),
    ('notify', 'gcm.moved_to_cash', 'ru', 'gcm.text'),
    ('notify', 'gcm.moved_to_cash_with_coupon', 'ru', 'gcm.text2'),
    ('notify', 'apns.moved_to_cash', 'ru', 'gcm.text'),
    ('notify', 'apns.moved_to_cash_with_coupon', 'ru', 'gcm.text2'),
    ('notify', 'gcm.yandex_card_moved_to_cash', 'ru', 'gcm.text'),
    ('notify', 'gcm.yandex_card_moved_to_cash_with_coupon', 'ru', 'gcm.text2'),
    ('notify', 'apns.yandex_card_moved_to_cash', 'ru', 'gcm.text'),
    ('notify', 'apns.yandex_card_moved_to_cash_with_coupon', 'ru', 'gcm.text2'),
    ('notify', 'time', 'ru', 'time'),
])
@pytest.mark.parametrize('order_id,with_coupon,event', [
    ('order_id2', False, 'gcm.moved_to_cash'),
    ('order_id2', True, 'gcm.moved_to_cash_with_coupon'),
    ('order_yandex_card_1', False, 'gcm.yandex_card_moved_to_cash'),
    ('order_yandex_card_1', True, 'gcm.yandex_card_moved_to_cash_with_coupon'),
])
@pytest.inline_callbacks
def test_notify_on_moved_to_cash_gcm(patch, order_id, with_coupon, event):

    @patch('taxi.internal.dbh.notifications_queue.new_task')
    def new_task(*args, **kwargs):
        return dbh.notifications_queue.Doc()

    @patch('taxi_stq.client.add_notification_task')
    def add_notification_task(*args, **kwargs):
        return

    @patch('uuid.uuid4')
    def uuid4():
        uuid4_ = collections.namedtuple('uuid4', 'hex')
        return uuid4_(MAGIC_UUID)

    user = yield dbh.users.Doc.find_one_by_id('android_user')
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc.order.request.due = NOW + datetime.timedelta(minutes=10)
    state = order_fsm.OrderFsm(proc=proc)
    yield notify.notify_on_moved_to_cash(state, with_coupon, None)

    calls = new_task.calls
    assert len(calls) == 1
    assert calls[0]['args'] == _get_expected_gcm_args(
        user, order_id, event, with_coupon)


@pytest.mark.filldb()
@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations([
    ('client_messages', 'time', 'ru', 'time'),
    ('notify', 'mpns.moved_to_cash', 'ru', 'mpns.text'),
    ('notify', 'mpns.moved_to_cash_with_coupon', 'ru', 'mpns.text2'),
    ('notify', 'sms.moved_to_cash', 'ru', 'sms.text'),
    ('notify', 'sms.moved_to_cash_with_coupon', 'ru', 'sms.text2'),
    ('notify', 'sms.yandex_card_moved_to_cash', 'ru', 'sms.text'),
    ('notify', 'sms.yandex_card_moved_to_cash_with_coupon', 'ru', 'sms.text2'),
    ('notify', 'time', 'ru', 'time'),
])
@pytest.mark.parametrize('order_id,with_coupon,event,text', [
    ('order_id3', False, 'sms.moved_to_cash', 'sms.text'),
    ('order_id3', True, 'sms.moved_to_cash_with_coupon', 'sms.text2'),
    ('order_yandex_card_2', False, 'sms.yandex_card_moved_to_cash', 'sms.text'),
    ('order_yandex_card_2', True, 'sms.yandex_card_moved_to_cash_with_coupon', 'sms.text2'),
])
@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY2=True)
@pytest.inline_callbacks
def test_notify_on_moved_to_cash_mpns(
        patch, order_id, with_coupon, event, text, userapi_get_user_phone_mock,
        personal_retrieve_mock):
    @patch('taxi.internal.dbh.notifications_queue.new_task')
    def new_task(*args, **kwargs):
        return dbh.notifications_queue.Doc()

    @patch('taxi_stq.client.add_notification_task')
    def add_notification_task(*args, **kwargs):
        return

    @patch('uuid.uuid4')
    def uuid4():
        uuid4_ = collections.namedtuple('uuid4', 'hex')
        return uuid4_(MAGIC_UUID)

    user = yield dbh.users.Doc.find_one_by_id('mpns_user')
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc.order.request.due = NOW + datetime.timedelta(minutes=10)
    state = order_fsm.OrderFsm(proc=proc)
    yield notify.notify_on_moved_to_cash(state, with_coupon, None)

    calls = new_task.calls
    assert len(calls) == 1
    assert calls[0]['args'] == _get_expected_mpns_args(
        user, order_id, event, text)


@async.inline_callbacks
def _make_user_and_state(
        order_id, user_id, application, experiments, payment_type
):
    user = yield dbh.users.Doc.find_one_by_id(user_id)
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    if application in {'iphone', 'android'}:
        proc.order.dont_sms = True
    proc.order.user_id = user.pk
    proc.order.request.due = NOW + datetime.timedelta(minutes=10)
    proc.order.application = application
    proc.order.experiments = experiments
    proc.order.request.payment.type = payment_type
    state = order_fsm.OrderFsm(proc=proc)
    async.return_value((user, state))


@pytest.mark.filldb()
@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations([
    ('client_messages', 'time', 'ru', 'time'),
    ('notify', 'apns.on_assigned', 'ru', 'apns.text'),
    ('notify', 'sms.on_assigned', 'ru', 'sms.text'),
    ('notify', 'apns.on_waiting', 'ru', 'apns.text'),
    ('notify', 'sms.on_waiting', 'ru', 'sms.text'),
    ('notify', 'time', 'ru', 'time'),
])
@pytest.mark.config(
    DECREASE_SMS_FROM_APPS=['web', 'mobileweb', 'terminal'],
    DECREASE_SMS_TYPES=['on_assigned', 'on_assigned_exact'],
    USER_API_USE_USER_PHONES_RETRIEVAL_PY2=True,
    IVR_CALL_APPS=[],
)
@pytest.mark.parametrize(
    'user_id,application,experiments,message_key,payment_type,'
    'expected_event,expected_text', [
        # 0. iphone, normal push
        ('iphone_user', 'iphone', [], 'on_assigned', 'card',
         'apns.on_assigned', 'apns.text'),
        ('iphone_user', 'iphone', ['decrease_sms_from_site'],
         'on_assigned', 'card',
         'apns.on_assigned', 'apns.text'),
        # 2. web without experiment, still send sms
        ('web_user', 'web', [], 'on_assigned', 'card',
         'sms.on_assigned', 'sms.text'),
        ('mobileweb_user', 'mobileweb', [], 'on_assigned', 'card',
         'sms.on_assigned', 'sms.text'),
        # 4. with experiment, don't send sms now
        ('web_user', 'web', ['decrease_sms_from_site'], 'on_assigned', 'card',
         None, None),
        ('mobileweb_user', 'mobileweb', ['decrease_sms_from_site'],
         'on_assigned', 'card',
         None, None),
        # 6. web without experiment, but on_waiting, so send sms
        ('web_user', 'web', [], 'on_waiting', 'card',
         'sms.on_waiting', 'sms.text'),
        ('mobileweb_user', 'mobileweb', [], 'on_waiting', 'card',
         'sms.on_waiting', 'sms.text'),
        # 8. with experiment, but on_waiting, so send sms
        ('web_user', 'web', ['decrease_sms_from_site'], 'on_waiting', 'card',
         'sms.on_waiting', 'sms.text'),
        ('mobileweb_user', 'mobileweb', ['decrease_sms_from_site'],
         'on_waiting', 'card',
         'sms.on_waiting', 'sms.text'),
        # 10. special 'win' case, send sms anyway
        ('mpns_user', 'win', [], 'on_assigned', 'card',
         'sms.on_assigned', 'sms.text'),
        ('mpns_user', 'win', ['decrease_sms_from_site'], 'on_assigned', 'card',
         'sms.on_assigned', 'sms.text'),
        ('mpns_user', 'win', [], 'on_waiting', 'card',
         'sms.on_waiting', 'sms.text'),
        ('mpns_user', 'win', ['decrease_sms_from_site'], 'on_waiting', 'card',
         'sms.on_waiting', 'sms.text'),
        # 14. win user with dont_sms experiment, so don't send sms
        ('mpns_user', 'win', ['dont_sms'], 'on_assigned', 'card',
         None, None),
        # 15. iphone user with dont_sms experiment, only push
        ('iphone_user', 'iphone', ['dont_sms'], 'on_assigned', 'card',
         'apns.on_assigned', 'apns.text'),
        # 16. iphone user with dont_sms experiment, on waiting, send push
        ('iphone_user', 'iphone', ['dont_sms'], 'on_waiting', 'card',
         'apns.on_waiting', 'apns.text'),
        # 17. win user with both experiments, so don't send sms
        ('mpns_user', 'win', ['dont_sms', 'decrease_sms_from_site'],
         'on_assigned', 'card',
         None, None),
        # 18. win user with both experiments, on waiting, still don't send sms
        ('mpns_user', 'win', ['dont_sms', 'decrease_sms_from_site'],
         'on_waiting', 'card',
         None, None),
        # 19. iphone user with both experiments on_assigned, send push
        ('iphone_user', 'iphone', ['dont_sms', 'decrease_sms_from_site'],
         'on_assigned', 'card',
         'apns.on_assigned', 'apns.text'),
        # 20. web user with both experiments, but corp, so send sms
        ('web_user', 'web', ['dont_sms', 'decrease_sms_from_site'],
         'on_assigned', 'corp',
         'sms.on_assigned', 'sms.text'),
        # 21. web user with dont_sms, but corp, so send sms
        ('web_user', 'web', ['dont_sms'],
         'on_assigned', 'corp',
         'sms.on_assigned', 'sms.text'),
        # 22. callcenter user with dont_sms, card, send sms
        ('call_user', 'callcenter', ['dont_sms'],
         'on_assigned', 'card',
         'sms.on_assigned', 'sms.text'),
        # 23. callcenter user with apns
        ('empty_apns', 'callcenter', ['dont_sms'],
         'on_assigned', 'card',
         'sms.on_assigned', 'sms.text'),
])
@pytest.inline_callbacks
def test_notify_decrease_sms(
        patch, user_id, application, experiments, message_key, payment_type,
        expected_event, expected_text, userapi_get_user_phone_mock,
        personal_retrieve_mock):

    @patch('taxi.internal.dbh.notifications_queue.new_task')
    def new_task(*args, **kwargs):
        return dbh.notifications_queue.Doc()

    @patch('taxi_stq.client.add_notification_task')
    def add_notification_task(*args, **kwargs):
        return

    @patch('uuid.uuid4')
    def uuid4():
        uuid4_ = collections.namedtuple('uuid4', 'hex')
        return uuid4_(MAGIC_UUID)

    order_id = 'order_id1'
    user, state = yield _make_user_and_state(
        order_id, user_id, application, experiments, payment_type
    )
    if message_key == 'on_assigned':
        yield notify.notify_on_assigned(state, None)
    elif message_key == 'on_waiting':
        yield notify.notify_on_waiting(state, None)

    calls = new_task.calls
    if expected_event is None:
        assert len(calls) == 0
    else:
        assert len(calls) == 1
        if 'sms' in expected_event or 'callcenter' in expected_event:
            expected_args = _get_expected_sms_args(
                user, order_id, expected_event, expected_text, message_key
            )
        else:
            expected_args = _get_expected_apns_args(
                user, order_id, expected_event, expected_text
            )
        assert calls[-1]['args'] == expected_args


def _get_expected_apns_args(user, order_id, event, text):
    index = -1
    taxi_status = None
    payload = {
        'sound': 'default',
        'thread-id': order_id,
        'interruption-level': 'time-sensitive',
        'id': MAGIC_UUID,
        'silent': True,
        'extra': {
            'status': taxi_status,
            'order_id': order_id,
        }
    }
    return (
        order_id,
        index,
        event,
        'apns',
        user.yandex_uuid,
        text,
        payload,
        user.pk,
        user.application,
        user.application_version,
    )


def _get_expected_gcm_args(user, order_id, event, with_coupon):
    index = -1
    text = 'gcm.text'
    if with_coupon:
        text = 'gcm.text2'
    payload = {
        'order_id': order_id,
        'updated': dates.timestring(NOW),
        'id': MAGIC_UUID,
    }
    return (
        order_id,
        index,
        event,
        'gcm',
        user.yandex_uuid,
        text,
        payload,
        user.pk,
        user.application,
        user.application_version,
    )


@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY2=True)
@pytest.mark.filldb()
@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations([
    ('notify', 'sms.on_assigned', 'ru',
        'sms driver phone: %(driver_phone)s'),
    ('notify', 'apns.on_assigned', 'ru',
        'apns driver phone: %(driver_phone)s'),
    ('notify', 'notifications.color', 'ru', '<color>'),
    ('notify', 'time', 'ru', 'time'),
])
@pytest.inline_callbacks
@pytest.mark.parametrize('mode, order_id, expected_phone', [
    ('driver_phone', 'order_id1', '+79871112233'),
    ('forwarding_phone', 'order_id_vgw', '+79871112277,009'),
    ('forwarding_phone_fail', 'order_id_vgw', '+79871112233')
])
@pytest.mark.parametrize('exp_new_flow_enabled', [True, False])
def test_notify_on_assigned(patch,
                            areq_request, mode,
                            order_id, expected_phone,
                            userapi_get_user_phone_mock,
                            personal_retrieve_mock, exp_new_flow_enabled):
    @patch('taxi.external.experiments3.get_values')
    @async.inline_callbacks
    def _mock_exp3_get_values(*args, **kwargs):
        yield
        result = [
            experiments3.ExperimentsValue(
                name='order_client_notification',
                value={'enabled': exp_new_flow_enabled, 'message_keys': ['on_assigned']}
            )
        ]
        async.return_value(result)

    @patch('taxi.internal.dbh.notifications_queue.new_task')
    def new_task(*args, **kwargs):
        return dbh.notifications_queue.Doc()

    @patch('taxi_stq.client.add_notification_task')
    def add_notification_task(*args, **kwargs):
        return

    @patch('uuid.uuid4')
    def uuid4():
        uuid4_ = collections.namedtuple('uuid4', 'hex')
        return uuid4_(MAGIC_UUID)

    @patch('taxi.internal.notifications.order._arrival_interval')
    def _arrival_interval(*args, **kwargs):
        return False, 1

    @patch('taxi.internal.notifications.order._prepare_car_number')
    def _prepare_car_number(*args, **kwargs):
        return None

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == ('http://taxi-protocol.taxi.tst.yandex.net/'
                       'voicegatewaysobtain'):
            if mode == 'forwarding_phone_fail':
                return areq_request.response(500)
            response = {
                'gateways': [{
                    'gateway': {
                        'phone': '+79871112277',
                        'ext': '009',
                    },
                }]
            }
            return areq_request.response(200, body=json.dumps(response))

        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    @patch('taxi.internal.driver_manager._set_brand_model')
    def _set_brand_model(brand, model, car_doc):
        car_doc['brand'] = brand
        car_doc['model'] = model

    @patch('taxi.internal.driver_manager._set_color')
    def _set_color(color, car_doc):
        assert color == 'red'
        car_doc['color'] = 'red'
        car_doc['color_code'] = 'FAFBFB'

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc.order.request.due = NOW + datetime.timedelta(minutes=10)
    state = order_fsm.OrderFsm(proc=proc)
    state._candidate_index = 0
    yield status_handling._handle_assigning(state)

    calls = new_task.calls

    if exp_new_flow_enabled:
        assert len(calls) == 0
        return

    assert len(calls) == 2
    assert [call['args'] for call in calls] == [
        (
            order_id,
            -1,
            'sms.on_assigned',
            'sms',
            '+72222222222',
            'sms driver phone: ' + expected_phone,
            {
                'from_uid': None,
                'intent': 'taxi_order_on_assigned',
                'meta': {'order_id': order_id},
                'locale': 'ru',
            },
            'iphone_user',
            'iphone',
            '1.2.3',
        ),
        (
            order_id,
            -1,
            'apns.on_assigned',
            'apns',
            'apns_user_uuid',
            'apns driver phone: ' + expected_phone,
            {
                'sound': 'default',
                'thread-id': order_id,
                'interruption-level': 'time-sensitive',
                'id': MAGIC_UUID,
                'silent': True,
                'extra': {
                    'status': None,
                    'order_id': order_id
                }
            },
            'iphone_user',
            'iphone',
            '1.2.3',
        )
    ]


def _get_expected_mpns_args(user, order_id, event, text):
    index = -1
    payload = {
        'from_uid': None,
        'intent': 'taxi_order_{}'.format(event.split('.')[1]),
        'meta': {'order_id': order_id},
        'locale': 'ru',
    }
    return (
        order_id,
        index,
        event,
        'sms',
        '+72222222222',
        text,
        payload,
        user.pk,
        user.application,
        user.application_version,
    )


def _get_expected_sms_args(user, order_id, event, text, message_key):
    index = -1
    payload = {
        'from_uid': None,
        'intent': 'taxi_order_{}'.format(message_key),
        'meta': {'order_id': 'order_id1'},
        'locale': 'ru',
    }
    return (
        order_id,
        index,
        event,
        'sms',
        '+72222222222',
        text,
        payload,
        user.pk,
        user.application,
        user.application_version,
    )


@pytest.mark.filldb
@pytest.mark.parametrize('order_id,candidate_index,expected_fare', [
    # get currency from performer
    (
        '12e05188-354c-4772-a351-e6475f2443a7',
        0,
        {'currency_code': 'RUB', 'total': '116.0'}
    ),
    # get currency from zone -> tariff -> country
    (
        'order_id3',
        -1,
        {'currency_code': 'AMD', 'total': '0.0'}
    ),
    # fallback to default currency
    (
        'order_id2',
        -1,
        {'currency_code': 'RUB', 'total': '0.0'}
    ),
])
@pytest.inline_callbacks
def test_get_fare(order_id, candidate_index, expected_fare):
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    order_state = order_fsm.OrderFsm(proc=proc)
    order_state._candidate_index = candidate_index
    fare = yield notify._get_fare(order_state)
    assert fare == expected_fare


@pytest.mark.filldb
@pytest.inline_callbacks
def test_prepare_uber_state_changes():
    order_id = 'ac4708562acd4be2abeef45f6e9ca469'
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    order_state = order_fsm.OrderFsm(proc=proc)

    state_changes = notify._prepare_uber_state_changes(order_state)
    assert state_changes == [
        {
            'timestamp': 1522734451000,
            'state': 'dispatched',
            'latitude': 55.82159224522527,
            'longitude': 37.31253318135731
        },
        {
            'timestamp': 1522734936000,
            'state': 'arrived',
            'latitude': 55.822923659588255,
            'longitude': 37.30987010979837
        },
        {
            'timestamp': 1522735016000,
            'state': 'begintrip',
            'latitude': 55.82151443341197,
            'longitude': 37.312597327767925
        },
        {
            'timestamp': 1522736886000,
            'state': 'completed',
            'latitude': 55.864109257888856,
            'longitude': 37.42486426937844
        }
    ]


@pytest.mark.filldb
@pytest.inline_callbacks
def test_prepare_uber_payload():
    order_id = 'ac4708562acd4be2abeef45f6e9ca469'
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    order_state = order_fsm.OrderFsm(proc=proc)

    payload = notify._prepare_uber_payload(order_state, 'driver_arriving')

    assert payload == {
        'path': '/providers/trips/ac4708562acd4be2abeef45f6e9ca469/notifications',
        'headers': {
            'Accept-Language': 'ru'
        },
        'parameters': {
            'user_id': 'uber_219b',
            'event_time': 1522736886,
            'event_name': u'driver_arriving',
            'location': None,
            'vehicle': {
                'license_number': '',
                'make': u'\ufeff',
                'model': ''
            },
            'trip_id': u'ac4708562acd4be2abeef45f6e9ca469'
        }
    }


@pytest.mark.filldb
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize('state_changes,trip_status,expected_trip_status', [
    (
        [
            {
                'latitude': 54.9640729,
                'timestamp': 1523529642000,
                'state': 'arrived',
                'longitude': 82.9344691
            }
        ],
        'driver_arriving',
        'driver_arriving'
    ),
    (
        [],
        'some_trip_status',
        'unfulfilled'
    ),
])
@pytest.inline_callbacks
def test_prepare_uber_finish_order_payload(patch, state_changes, trip_status, expected_trip_status):

    @patch('taxi.external.geotracks.get_driver_track')
    def _get_driver_track(*args, **kwargs):
        return {'track': [
            {
                'point': [0, 0],
                'timestamp': 0,
            }
        ]}

    order_id = '12e05188-354c-4772-a351-e6475f2443a7'
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    order_state = order_fsm.OrderFsm(proc=proc)
    order_state._candidate_index = 0

    @patch('taxi.internal.notifications.order._prepare_uber_state_changes')
    def _prepare_uber_state_changes(order_state):
        return state_changes

    payload = yield notify._prepare_uber_finish_order_payload(order_state, trip_status)

    assert payload == {
        'path': '/providers/trips',
        'headers': {
            'Accept-Language': 'ru'
        },
        'parameters': {
            'city_name': 'moscow',
            'all_points': [{'latitude': 0, 'timestamp': 0, 'longitude': 0}],
            'user_id': '693622cc-a79c-4758-9e9c-fc6e4e3286e4',
            'trip_status': expected_trip_status,
            'vehicle': {
                'license_number': 'К748НН59',
                'make': u'\ufeff',
                'model': 'Renault Symbol'
            },
            'trip_source': 'yandex',
            'calculated_fare': {'currency_code': 'RUB', 'total': '116.0'},
            'state_changes': state_changes,
            'trip_id': order_id
        }
    }


@pytest.mark.config(
    ROUTE_SHARING_URL_TEMPLATES={
        'yandex': 'https://taxi.yandex.ru/route-enter/{key}?lang={lang}',
        'yataxi': 'https://taxi.yandex.ru/route-enter/{key}?lang={lang}',
        'yauber': 'https://support-uber.com/route/{key}?lang={lang}',
    },
    USER_API_USE_USER_PHONES_RETRIEVAL_PY2=True,
    ORDER_ROUTE_SHARING_TASK_CREATION_ENABLED=True,
    ORDER_ROUTE_SHARING_TARIFFS=['econom'],
)
@pytest.mark.filldb()
@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations([
    ('notify', 'sms.on_assigned', 'ru',
        'sms driver phone: %(driver_phone)s'),
    ('notify', 'apns.on_assigned', 'ru',
        'apns driver phone: %(driver_phone)s'),
    ('notify', 'notifications.color', 'ru', '<color>'),
    ('notify', 'time', 'ru', 'time'),
    ('notify', 'sms.order_for_other_paid_by_card_short', 'ru',
     'Order paid by card, %(driver_phone)s, %(estimate_short)s'),
    ('notify', 'sms.order_for_other_paid_by_cash_short', 'ru',
     'Order paid by cash, %(driver_phone)s, %(estimate_short)s'),
    ('notify', 'sms.on_waiting', 'ru', 'sms driver phone: %(driver_phone)s'),
    ('notify', 'express.sms.on_waiting', 'ru', 'express going to you: %(sharing_url)s'),
    ('notify', 'express.sms.on_transporting', 'ru', 'express going to you: %(sharing_url)s'),
    ('notify', 'apns.on_transporting', 'ru', 'Your ride has started'),
    ('notify', 'apns.on_waiting', 'ru', 'apns driver phone: %(driver_phone)s'),
    ('notify', 'push.on_waiting.for_other', 'ru', FOR_OTHER_PUSH_ON_WAITING),
    ('notify', 'push.order_for_other_paid_by_card_short', 'ru', FOR_OTHER_PUSH_CARD),
    ('notify', 'push.order_for_other_paid_by_cash_short', 'ru', FOR_OTHER_PUSH_CASH),
])
@pytest.inline_callbacks
@pytest.mark.parametrize('message_key,payment_tech_type,'
                         'order_id,expected_other_call_args,custom_configs',
[
    (
        'on_assigned',
        'cash',
        'order_id1',
        (
            u'order_id1_for_other',
            -1,
            'sms.on_assigned',
            'sms',
            u'+79997777777',
            u'Order paid by cash, +79871112233, 1',
            _make_payload(FOR_OTHER_PUSH_CASH, 'on_assigned', 'order_id1'),
            u'iphone_user',
            u'iphone',
            u'1.2.3',
        ),
        {},
    ),
    (
        'on_assigned',
        'card',
        'order_id1',
        (
            u'order_id1_for_other',
            -1,
            'sms.on_assigned',
            'sms',
            u'+79997777777',
            u'Order paid by card, +79871112233, 1',
            _make_payload(FOR_OTHER_PUSH_CARD, 'on_assigned', 'order_id1'),
            u'iphone_user',
            u'iphone',
            u'1.2.3'
        ),
        {},
    ),
    (
        'on_assigned',
        'applepay',
        'order_id1',
        (
            u'order_id1_for_other',
            -1,
            'sms.on_assigned',
            'sms',
            u'+79997777777',
            u'Order paid by card, +79871112233, 1',
            _make_payload(FOR_OTHER_PUSH_CARD, 'on_assigned', 'order_id1'),
            u'iphone_user',
            u'iphone',
            u'1.2.3'
        ),
        {},
    ),
    (
        'on_assigned',
        'googlepay',
        'order_id1',
        (
            u'order_id1_for_other',
            -1,
            'sms.on_assigned',
            'sms',
            u'+79997777777',
            u'Order paid by card, +79871112233, 1',
            _make_payload(FOR_OTHER_PUSH_CARD, 'on_assigned', 'order_id1'),
            u'iphone_user',
            u'iphone',
            u'1.2.3'
        ),
        {},
    ),
    (
        'on_waiting',
        'cash',
        'order_id1',
        (
            u'order_id1_for_other',
            -1,
            'sms.on_waiting',
            'sms',
            u'+79997777777',
            u'sms driver phone: +79871112233',
            _make_payload(FOR_OTHER_PUSH_ON_WAITING, 'on_waiting', 'order_id1'),
            u'iphone_user',
            u'iphone',
            u'1.2.3'
        ),
        {},
    ),
    (
        'on_waiting',
        'card',
        'order_id1',
        (
            u'order_id1_for_other',
            -1,
            'sms.on_waiting',
            'sms',
            u'+79997777777',
            u'express going to you: https://taxi.yandex.ru/route-enter/express_sharing_key?lang=ru',
            _make_payload(FOR_OTHER_PUSH_ON_WAITING, 'on_waiting', 'order_id1'),
            u'iphone_user',
            u'iphone',
            u'1.2.3'
        ),
        {'NOTIFICATION_PREFIX_BY_TARIFF': {
            'econom': {
                'on_waiting': {
                    'sms': 'express'
                }
            }
        }},
    ),
    (
        'on_waiting',
        'card',
        'order_id4',
        (
            u'order_id4_for_other',
            -1,
            'sms.on_waiting',
            'sms',
            u'+79997777777',
            u'express going to you: https://support-uber.com/route/express_sharing_key4?lang=ru',
            _make_payload(FOR_OTHER_PUSH_ON_WAITING, 'on_waiting', 'order_id4'),
            u'uber_iphone_user',
            u'uber_iphone',
            u'1.2.3'
        ),
        {'NOTIFICATION_PREFIX_BY_TARIFF': {
            'econom': {
                'on_waiting': {
                    'sms': 'express'
                }
            }
        }},
    ),
    (
        'on_assigned',
        'card',
        'order_id8',
        (
            u'order_id8_for_other',
            -1,
            'sms.on_assigned',
            'sms',
            u'+79997777777',
            u'express paid for you: https://support-uber.com/route/express_sharing_key8?lang=ru',
            _make_payload(FOR_OTHER_PUSH_CARD, 'on_assigned', 'order_id4'),
            u'uber_iphone_user',
            u'uber_iphone',
            u'1.2.3'
        ),
        {'NOTIFICATION_PREFIX_BY_TARIFF': {
            'express': {}
        }},
    ),
])
def test_notify_for_other(
        message_key, payment_tech_type, order_id,
        expected_other_call_args, patch, custom_configs,
        mocks_for_other_notification, personal_retrieve_mock,
        mock_processing_antifraud, areq_request
):
    @patch('taxi.internal.dbh.notifications_queue.new_task')
    def new_task(*args, **kwargs):
        return dbh.notifications_queue.Doc()

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    for key, value in custom_configs.iteritems():
        custom_config = getattr(config, key)
        yield custom_config.save(value)

    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc.order.request.due = NOW + datetime.timedelta(minutes=10)
    proc.order.request.extra_user_phone_id = 'other_user_id1'
    proc.payment_tech.type = payment_tech_type
    state = order_fsm.OrderFsm(proc=proc)
    state._candidate_index = 0

    if message_key == 'on_assigned':
        yield status_handling._handle_assigning(state)
    elif message_key == 'on_waiting':
        yield status_handling._handle_waiting(state)
    driver_phone_to_show = '+79871112233'

    new_task_user = expected_other_call_args[7]
    new_task_app = expected_other_call_args[8]

    calls = new_task.calls

    expected_args = [
        (
            order_id,
            -1,
            'sms.' + message_key,
            'sms',
            '+72222222222',
            'sms driver phone: ' + driver_phone_to_show,
            {
                'from_uid': None,
                'intent': 'taxi_order_{}'.format(message_key),
                'meta': {'order_id': u'order_id1'},
                'locale': 'ru',
            },
            new_task_user,
            new_task_app,
            '1.2.3',
        ),
        (
            order_id,
            -1,
            'apns.' + message_key,
            'apns',
            'apns_user_uuid',
            'apns driver phone: ' + driver_phone_to_show,
            {
                'sound': 'default',
                'thread-id': order_id,
                'interruption-level': 'time-sensitive',
                'id': MAGIC_UUID,
                'silent': True,
                'extra': {
                    'status': None,
                    'order_id': order_id
                }
            },
            new_task_user,
            new_task_app,
            '1.2.3',
        )
    ]
    expected_num_calls = 3
    if message_key == 'on_waiting':
        # we do not send usual sms on waiting, just push
        expected_args = expected_args[1:]
        expected_num_calls = 2
    if (message_key == 'on_assigned' and
        state.performer.tariff_class == 'express'):
        assert len(calls) == 2
        return

    assert len(calls) == expected_num_calls
    assert [call['args'] for call in calls][:-1] == expected_args
    assert calls[-1]['args'] == expected_other_call_args


@pytest.mark.config(
    USER_API_USE_USER_PHONES_RETRIEVAL_PY2=True,
    ROUTE_SHARING_URL_TEMPLATES={
        'yataxi': 'https://taxi.yandex.ru/route-enter/{key}',
    },
)
@pytest.mark.filldb()
@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations([
    ('notify', 'notifications.color', 'ru', '<color>'),
    ('notify', 'time', 'ru', 'time'),
    ('notify', 'sms.on_waiting', 'ru', 'sms driver phone: %(driver_phone)s'),
    ('notify', 'apns.on_waiting', 'ru', 'apns driver phone: %(driver_phone)s'),
    ('notify', 'sms.on_assigned', 'ru',
        'sms driver phone: %(driver_phone)s'),
    ('notify', 'apns.on_assigned', 'ru',
        'apns driver phone: %(driver_phone)s'),
])
@pytest.mark.parametrize(
    'order_id', ('corp_express', 'corp_econom', 'not_corp_express'),
)
@pytest.mark.parametrize('taxi_status', ('on_waiting', 'on_assigned'))
@pytest.inline_callbacks
def test_corpweb_waiting_sms(
        patch, mocks_for_other_notification, order_id, taxi_status,
        personal_retrieve_mock, areq_request
):
    @patch('taxi.internal.dbh.notifications_queue.new_task')
    def new_task(*args, **kwargs):
        return dbh.notifications_queue.Doc()

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    proc = yield dbh.order_proc.Doc.find_one_for_processing(order_id)
    proc.order.request.due = NOW + datetime.timedelta(minutes=10)
    state = order_fsm.OrderFsm(proc=proc)
    state._candidate_index = 0

    if taxi_status == 'on_waiting':
        yield status_handling._handle_waiting(state)
    elif taxi_status == 'on_assigned':
        yield status_handling._handle_assigning(state)

    calls = new_task.calls
    is_one_call = all(
        [
            order_id in ('corp_express', 'not_corp_express'),
            taxi_status == 'on_waiting',
        ],
    )
    if is_one_call:
        assert len(calls) == 1
        assert calls[0]['args'][2] == 'apns.on_waiting'
    else:
        assert len(calls) == 2
        assert calls[0]['args'][2] == 'sms.' + taxi_status
        assert calls[1]['args'][2] == 'apns.' + taxi_status


@pytest.mark.config(
    USER_API_USE_USER_PHONES_RETRIEVAL_PY2=True,
    ROUTE_SHARING_URL_TEMPLATES={
        'yataxi': 'https://taxi.yandex.ru/route-enter/{key}?lang={lang}',
    },
)
@pytest.mark.filldb()
@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations([
    ('notify', 'notifications.color', 'ru', '<color>'),
    ('notify', 'time', 'ru', 'time'),
    (
        'notify',
        'express.sms.on_transporting',
        'ru',
        'express going to you: %(sharing_url)s',
    ),
    ('notify', 'apns.on_transporting', 'ru', 'Your ride has started'),
    ('notify', 'sms.on_waiting', 'ru', 'sms driver phone: %(driver_phone)s'),
    ('notify', 'apns.on_waiting', 'ru', 'apns driver phone: %(driver_phone)s'),
])
@pytest.inline_callbacks
def test_not_delivery_sms(
        patch, mocks_for_other_notification, personal_retrieve_mock, areq_request
):
    @patch('taxi.internal.dbh.notifications_queue.new_task')
    def new_task(*args, **kwargs):
        return dbh.notifications_queue.Doc()

    @patch('taxi.internal.notifications.order.notify_other_on_waiting')
    def notify_other_on_waiting(*args, **kwargs):
        pass

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    proc = yield dbh.order_proc.Doc.find_one_by_id('order_id8')
    proc.order.request.due = NOW + datetime.timedelta(minutes=10)
    proc.order.request.extra_user_phone_id = 'other_user_id1'
    proc.order.performer.tariff.cls = 'express'
    state = order_fsm.OrderFsm(proc=proc)
    state._candidate_index = 0

    yield status_handling._handle_waiting(state)
    # No sms for other for delivery (express) tariff
    assert len(notify_other_on_waiting.calls) == 0


@pytest.mark.filldb()
@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations([
    ('notify', 'notifications.color', 'ru', '<color>'),
    ('notify', 'time', 'ru', 'time'),
    ('notify', 'sms.on_waiting', 'ru', 'waiting: %(sharing_url)s'),
    ('notify', 'apns.on_waiting', 'ru', 'apns driver phone: %(driver_phone)s'),
    ('notify', 'push.on_waiting.for_other', 'ru', FOR_OTHER_PUSH_ON_WAITING),
])
@pytest.mark.config(
    ROUTE_SHARING_URL_TEMPLATES={
        'yandex': 'https://taxi.yandex.ru/route-enter/{key}?lang={lang}',
        'yataxi': 'https://taxi.yandex.ru/route-enter/{key}?lang={lang}',
        'yauber': 'https://support-uber.com/route/{key}?lang={lang}',
    },
    USER_API_USE_USER_PHONES_RETRIEVAL_PY2=True,
    ORDER_ROUTE_SHARING_TASK_CREATION_ENABLED=True,
    ORDER_ROUTE_SHARING_TARIFFS=['econom']
)
@pytest.mark.parametrize(
    ['order_id', 'key', 'lang'],
    [
        ('order_id_no_locale', 'nani', ''),
        ('order_id1', 'express_sharing_key', 'ru'),
    ],
)
@pytest.inline_callbacks
def test_notify_sharing_url(
        order_id, key, lang, patch, mocks_for_other_notification,
        personal_retrieve_mock, mock_processing_antifraud, areq_request
):
    @patch('taxi.internal.dbh.notifications_queue.new_task')
    def new_task(*args, **kwargs):
        return dbh.notifications_queue.Doc()

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    SHARING_URL_TEMPLATE = 'https://taxi.yandex.ru/route-enter/{key}?lang={lang}'

    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc.order.request.due = NOW + datetime.timedelta(minutes=10)
    proc.order.request.extra_user_phone_id = 'other_user_id1'
    proc.payment_tech.type = 'card'
    state = order_fsm.OrderFsm(proc=proc)
    state._candidate_index = 0

    # will not notify on assignment, as it is moved to delivery service
    # using on_waiting as a workaround instead to test sharing link generation
    yield status_handling._handle_waiting(state)

    calls = new_task.calls

    assert len(calls) == 2

    assert calls[-1]['args'] == (
        order_id + '_for_other',
        -1,
        'sms.on_waiting',
        'sms',
        u'+79997777777',
        u'waiting: ' + SHARING_URL_TEMPLATE.format(key=key, lang=lang),
        _make_payload(FOR_OTHER_PUSH_ON_WAITING, 'on_waiting', order_id),
        u'iphone_user',
        u'iphone',
        u'1.2.3'
    )


@async.inline_callbacks
def check_sms_notification_text(patch, order_id, notify_cb, exp_key, exp_text):
    @patch('taxi.internal.dbh.notifications_queue.new_task')
    def new_task(*args, **kwargs):
        return dbh.notifications_queue.Doc()

    @patch('taxi_stq.client.add_notification_task')
    def add_notification_task(*args, **kwargs):
        return

    user = yield dbh.users.Doc.find_one_by_id('mpns_user')
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc.order.request.due = NOW + datetime.timedelta(minutes=10)

    state = order_fsm.OrderFsm(proc=proc)

    yield notify_cb(state, None)

    calls = new_task.calls
    assert len(calls) == 1
    assert calls[0]['args'] == (
        order_id,
        -1,
        'sms.' + exp_key,
        'sms',
        '+72222222222',
        exp_text,
        {
            'from_uid': None,
            'intent': 'taxi_order_{}'.format(exp_key),
            'meta': {'order_id': order_id},
            'locale': 'ru',
        },
        user.pk,
        user.application,
        user.application_version,
    )


@async.inline_callbacks
def check_apns_notification_text(patch, order_id, notify_cb, exp_key, exp_text,
                                 need_performer=False, cost=None,
                                 is_cashback=None, payment_type=None,
                                 complements=None, current_prices=None):
    @patch('taxi.internal.dbh.notifications_queue.new_task')
    def new_task(*args, **kwargs):
        return dbh.notifications_queue.Doc()

    @patch('taxi_stq.client.add_notification_task')
    def add_notification_task(*args, **kwargs):
        return

    @patch('uuid.uuid4')
    def uuid4():
        uuid4_ = collections.namedtuple('uuid4', 'hex')
        return uuid4_(MAGIC_UUID)

    user = yield dbh.users.Doc.find_one_by_id('iphone_user')
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    if cost:
        proc.order.cost = cost
    if is_cashback:
        proc.extra_data.cashback.is_cashback = is_cashback
    if payment_type:
        proc.payment_tech.type = payment_type
    if complements:
        proc.payment_tech.complements = complements
    if current_prices:
        proc.order.current_prices = current_prices
    proc.order.user_id = 'iphone_user'
    proc.order.request.due = NOW + datetime.timedelta(minutes=10)

    state = order_fsm.OrderFsm(proc=proc)
    if need_performer:
        state._candidate_index = proc.performer.candidate_index

    yield notify_cb(state, None)

    calls = new_task.calls
    assert len(calls) == 1
    assert calls[0]['args'] == _get_expected_apns_args(
        user, order_id, 'apns.' + exp_key, exp_text)


@pytest.mark.filldb()
@pytest.mark.translations([
    ('notify', 'time', 'ru', 'time'),
    ('notify', 'mpns.on_failed', 'ru',
     '%(order_name_prefix)sВодитель из парка %(park_name)s отказался от заказа на %(due)s'),
    ('notify', 'sms.on_failed', 'ru',
     '%(order_name_prefix)sВодитель из парка %(park_name)s отказался от заказа на %(due)s'),
])
@pytest.mark.parametrize('order_id,exp_text', [
    ('order_id3', 'Водитель из парка 1 отказался от заказа на time'),
    ('order_id_in_multiorder', 'Заказ №1. Водитель из парка 1 отказался от заказа на time')
])
@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY2=True)
@pytest.inline_callbacks
def test_notify_on_failed(
        patch, order_id, exp_text, userapi_get_user_phone_mock,
        personal_retrieve_mock
):
    @patch('taxi.internal.notifications.order._last_performer_park')
    def _last_performer_park_name(order_state):
        return notify.LastPerformerPark('1', '')

    yield check_sms_notification_text(patch, order_id, notify.notify_on_failed,
                                  'on_failed', exp_text)


@pytest.mark.filldb()
@pytest.mark.translations([
    ('notify', 'time', 'ru', 'time'),
    ('notify', 'mpns.on_autoreorder_timeout', 'ru',
     '%(order_name_prefix)sК сожалению, водитель не смог выполнить заказ. ' +
     'Мы продолжаем поиск и сообщим, как только найдём замену'),
    ('notify', 'sms.on_autoreorder_timeout', 'ru',
     '%(order_name_prefix)sК сожалению, водитель не смог выполнить заказ. ' +
     'Мы продолжаем поиск и сообщим, как только найдём замену'),
])
@pytest.mark.parametrize('order_id,exp_text', [
    ('order_id3', 'К сожалению, водитель не смог выполнить заказ. Мы продолжаем ' +
     'поиск и сообщим, как только найдём замену'),
    ('order_id_in_multiorder', 'Заказ №1. К сожалению, водитель не смог выполнить заказ. ' +
     'Мы продолжаем поиск и сообщим, как только найдём замену'),
])
@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY2=True)
@pytest.inline_callbacks
def test_notify_on_autoreorder_timeout(
        patch, order_id, exp_text, userapi_get_user_phone_mock,
        personal_retrieve_mock,
):
    yield check_sms_notification_text(patch, order_id,
                                  notify.notify_on_autoreorder_timeout,
                                  'on_autoreorder_timeout', exp_text)


@pytest.mark.filldb()
@pytest.mark.translations([
    ('notify', 'time', 'ru', 'time'),
    ('notify', 'mpns.on_search_failed', 'ru',
     '%(order_name_prefix)sНе удалось найти такси на %(due)s'),
    ('notify', 'sms.on_search_failed', 'ru',
     '%(order_name_prefix)sНе удалось найти такси на %(due)s'),
])
@pytest.mark.parametrize('order_id,exp_text', [
    ('order_id3', 'Не удалось найти такси на time'),
    ('order_id_in_multiorder', 'Заказ №1. Не удалось найти такси на time'),
])
@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY2=True)
@pytest.inline_callbacks
def test_notify_on_search_expired(
        patch, order_id, exp_text, userapi_get_user_phone_mock,
        personal_retrieve_mock,
):
    yield check_sms_notification_text(patch, order_id,
                                  notify.notify_on_search_expired,
                                  'on_search_failed', exp_text)


@pytest.mark.filldb()
@pytest.mark.translations([
    ('notify', 'time', 'ru', 'time'),
    ('notify', 'mpns.on_waiting', 'ru',
     '%(order_name_prefix)sВодитель по заказу на %(due)s ждёт вас!'),
    ('notify', 'sms.on_waiting', 'ru',
     '%(order_name_prefix)sВодитель по заказу на %(due)s ждёт вас!'),
])
@pytest.mark.parametrize('order_id,exp_text', [
    ('order_id3', 'Водитель по заказу на time ждёт вас!'),
    ('order_id_in_multiorder', 'Заказ №1. Водитель по заказу на time ждёт вас!'),
])
@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY2=True)
@pytest.inline_callbacks
def test_notify_on_waiting(
        patch, order_id, exp_text, userapi_get_user_phone_mock,
        personal_retrieve_mock,
):
    yield check_sms_notification_text(patch, order_id,
                                  notify.notify_on_waiting,
                                  'on_waiting', exp_text)


@pytest.mark.filldb()
@pytest.mark.translations([
    ('notify', 'time', 'ru', 'time'),
    ('notify', 'sms.on_driver_arriving_with_waiting', 'ru',
     'Водитель подъезжает. Время бесплатного ожидания %(waiting)s мин'),
])
@pytest.mark.parametrize('order_id,exp_text,with_eta', [
    (
        'order_id_free_waiting',
        'Водитель подъезжает. Время бесплатного ожидания 10 мин',
        False,
    ),
    (
        'order_id_free_waiting_transfer',
        'Водитель подъезжает. Время бесплатного ожидания 15 мин',
        False,

    ),
    (
        'order_id_decoupling_free_waiting',
        'Водитель подъезжает. Время бесплатного ожидания 20 мин',
        False,

    ),
    (
        'order_id_decoupling_free_waiting_transfer',
        'Водитель подъезжает. Время бесплатного ожидания 25 мин',
        False,
    ),
    (
        'order_id_free_waiting',
        'Водитель подъезжает. Время бесплатного ожидания 13 мин',
        True,
    ),
    (
        'order_id_free_waiting_transfer',
        'Водитель подъезжает. Время бесплатного ожидания 18 мин',
        True,

    ),
    (
        'order_id_decoupling_free_waiting',
        'Водитель подъезжает. Время бесплатного ожидания 23 мин',
        True,
    ),
    (
        'order_id_decoupling_free_waiting_transfer',
        'Водитель подъезжает. Время бесплатного ожидания 28 мин',
        True,
    ),
])
@pytest.mark.config(SEND_NOTIFICATION_ON_DRIVER_ARRIVING=True)
@pytest.mark.config(SEND_NOTIFICATION_ON_DRIVER_ARRIVING_BY_ZONES=["moscow"])
@pytest.mark.config(
    NOTIFICATION_ON_DRIVER_ARRIVING_SETTINGS={
        "__default__": {
            "__default__": {
                "hide_waiting_if_longer_than_mins": 30,
                "send_free_waiting": True,
                "send_notification_timings": [
                    {
                        "from": 0,
                        "send_eta": 90
                    }
                ]
            }
        }
    }
)
@pytest.mark.config(
    NOTIFICATION_TYPES_FOR_DRIVER_ARRIVING=["sms"],
    USER_API_USE_USER_PHONES_RETRIEVAL_PY2=True,
)
@pytest.mark.now(NOW.isoformat())
@pytest.inline_callbacks
def test_notify_on_driver_arriving_with_waiting(
        patch, order_id, exp_text, with_eta, userapi_get_user_phone_mock,
        personal_retrieve_mock,
):
    @patch('taxi.external.corp_tariffs.get_tariff')
    @pytest.inline_callbacks
    def corp_tariffs_get_tariff(corp_tariff_id, **kwargs):
        yield
        async.return_value({
            'tariff': {
                'categories': [{
                    'name': 'business',
                    'waiting_included': 20,
                    'id': 'corp-category-id',
                    "zonal_prices": [
                        {
                            "source": "svo",
                            "destination": "dme",
                            "price": {
                                "waiting_included": 25
                            }
                        }
                    ]
                }]
            }
        })

    if with_eta:
        func = mock_notify_on_driver_arriving_with_eta
    else:
        func = mock_notify_on_driver_arriving_without_eta

    yield check_sms_notification_text(patch, order_id, func, 'on_driver_arriving_with_waiting', exp_text)


@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY2=True)
@pytest.mark.filldb()
@pytest.mark.translations([
    ('notify', 'time', 'ru', 'time'),
    ('notify', 'mpns.on_assigned', 'ru',
     '%(order_name_prefix)sCar. Через estimate мин.'),
    ('notify', 'sms.on_assigned', 'ru',
     '%(order_name_prefix)sCar. Через estimate мин.'),

])
@pytest.mark.parametrize('order_id,exp_text', [
    ('order_id3', 'Car. Через estimate мин.'),
    ('order_id_in_multiorder',
     'Заказ №1. Car. Через estimate мин.'),
])
@pytest.inline_callbacks
def test_notify_on_assigned_multiorder(
        patch, order_id, exp_text, userapi_get_user_phone_mock,
        personal_retrieve_mock,
):
    yield check_sms_notification_text(patch, order_id,
                                  notify.notify_on_assigned,
                                  'on_assigned', exp_text)


@pytest.mark.filldb()
@pytest.mark.translations([
    ('notify', 'time', 'ru', 'time'),
    ('notify', 'sms.on_driver_arriving', 'ru',
     '%(order_name_prefix)sМашина подъезжает'),
])
@pytest.mark.parametrize('order_id,exp_text', [
    ('order_id3', 'Машина подъезжает'),
    ('order_id_in_multiorder', 'Заказ №1. Машина подъезжает'),
])
@pytest.mark.config(SEND_NOTIFICATION_ON_DRIVER_ARRIVING=True)
@pytest.mark.config(SEND_NOTIFICATION_ON_DRIVER_ARRIVING_BY_ZONES=["moscow"])
@pytest.mark.config(
    NOTIFICATION_ON_DRIVER_ARRIVING_SETTINGS={
        "__default__": {
            "__default__": {
                "hide_waiting_if_longer_than_mins": 30,
                "send_free_waiting": True,
                "send_notification_timings": [
                    {
                        "from": 0,
                        "send_eta": 90
                    }
                ]
            }
        }
    }
)
@pytest.mark.config(
    NOTIFICATION_TYPES_FOR_DRIVER_ARRIVING=["sms"],
    USER_API_USE_USER_PHONES_RETRIEVAL_PY2=True,
)
@pytest.inline_callbacks
def test_notify_on_driver_arriving_multiorder(
        patch, order_id, exp_text, userapi_get_user_phone_mock,
        personal_retrieve_mock,
):
    yield check_sms_notification_text(patch, order_id,
                                  mock_notify_on_driver_arriving_without_eta,
                                  'on_driver_arriving', exp_text)


@pytest.mark.filldb()
@pytest.mark.translations([
    ('notify', 'time', 'ru', 'time'),
    ('notify', 'apns.on_transporting', 'ru',
     '%(order_name_prefix)sВодитель начал выполнение заказа от %(due)s'),
])
@pytest.mark.parametrize('order_id,exp_text', [
    ('order_id3', 'Водитель начал выполнение заказа от time'),
    ('order_id_in_multiorder',
     'Заказ №1. Водитель начал выполнение заказа от time'),
])
@pytest.inline_callbacks
def test_notify_on_transporting_multiorder(patch, order_id, exp_text):
    yield check_apns_notification_text(patch, order_id,
                                  notify.notify_on_transporting,
                                  'on_transporting', exp_text)


@pytest.mark.filldb()
@pytest.mark.translations([
    ('notify', 'time', 'ru', 'time'),
    ('notify', 'apns.on_complete', 'ru',
     '%(order_name_prefix)sОцените поездку'),
])
@pytest.mark.parametrize('order_id,exp_text', [
    ('order_id3', 'Оцените поездку'),
    ('order_id_in_multiorder',
     'Заказ №1. Оцените поездку'),
])
@pytest.inline_callbacks
def test_notify_on_complete_multiorder(patch, order_id, exp_text):
    @patch('taxi.internal.order_kit.order_helpers.need_to_get_user_feedback')
    def need_to_get_user_feedback(*args, **kwargs):
        return True

    yield check_apns_notification_text(patch, order_id,
                                  notify.notify_on_complete,
                                  'on_complete', exp_text)


@pytest.mark.config(
    NOTIFY_ON_COMPLETE_PERSONAL_WALLET_ENABLED=True,
)
@pytest.mark.filldb()
@pytest.mark.translations([
    ('notify', 'time', 'ru', 'time'),
    ('notify', 'apns.on_complete', 'ru', 'Оцените поездку'),
    ('notify', 'apns.on_complete_price', 'ru',
     'Стоимость поездки %(cost_with_currency)s. Оцените поездку'),
    ('notify', 'apns.on_complete_price_personal_wallet', 'ru',
     'Стоимость поездки %(cost_with_currency)s. Вы оплатили её баллами Плюса.'
     ' Оцените поездку'),
    ('notify', 'apns.on_complete_price_complements', 'ru',
     'Стоимость поездки %(cost_with_currency)s. Часть суммы оплачена баллами'
     ' Плюса. Оцените поездку'),
    ('notify', 'apns.on_complete_price_cashback', 'ru',
     'Стоимость поездки %(cost_with_currency)s.'
     ' Кэшбэк уже на вашем Плюсе. Оцените поездку'),
    ('tariff', 'currency_with_sign.default', 'ru',
     '$SIGN$$VALUE$$CURRENCY$'),
    ('tariff', 'currency.rub', 'ru',
     '₽'),
])
@pytest.mark.parametrize('order_id,exp_text,exp_key,cost,is_cashback,payment_type,complements', [
    ('order_id3', 'Оцените поездку', 'on_complete', None, False, 'card', None),
    ('order_id3', 'Стоимость поездки 300₽. Оцените поездку',
     'on_complete_price', '300', False, 'card', None),
    ('order_id3', 'Стоимость поездки 300₽. '
                  'Вы оплатили её баллами Плюса. Оцените поездку',
     'on_complete_price_personal_wallet', '300', False,
     'personal_wallet', None),
    ('order_id3', 'Стоимость поездки 300₽. '
                  'Часть суммы оплачена баллами Плюса. Оцените поездку',
     'on_complete_price_complements', '300', False, 'card',
     [{'type': 'personal_wallet'}]),
    ('order_id3', 'Стоимость поездки 300₽. Кэшбэк уже на вашем Плюсе.'
                  ' Оцените поездку', 'on_complete_price_cashback', '300',
     True, 'card', None),
])
@pytest.inline_callbacks
def test_notify_on_complete(patch, order_id, exp_text, exp_key, cost, is_cashback, payment_type, complements):
    @patch('taxi.internal.order_kit.order_helpers.need_to_get_user_feedback')
    def need_to_get_user_feedback(*args, **kwargs):
        return True

    yield check_apns_notification_text(
        patch, order_id, notify.notify_on_complete, exp_key, exp_text,
        need_performer=True, cost=cost, is_cashback=is_cashback,
        payment_type=payment_type, complements=complements)


@pytest.mark.config(
    NOTIFY_ON_COMPLETE_PERSONAL_WALLET_ENABLED=True,
    NOTIFY_ON_COMPLETE_CASHBACK_USING_CURRENT_PRICES=True,
    NOTIFY_ON_COMPLETE_PERSONAL_WALLET_USING_CURRENT_PRICES_ENABLED=True
)
@pytest.mark.filldb()
@pytest.mark.translations([
    ('notify', 'time', 'ru', 'time'),
    ('notify', 'apns.on_complete', 'ru', 'Оцените поездку'),
    ('notify', 'apns.on_complete_price', 'ru',
     'Стоимость поездки %(cost_with_currency)s. Оцените поездку'),
    ('notify', 'apns.on_complete_price_personal_wallet_with_amount', 'ru',
     'Поездка была оплачена плюсом: %(cost_paid_by_wallet_with_currency)s. Оцените поездку'),
    ('notify', 'apns.on_complete_price_complements_with_amount', 'ru',
     'Стоимость поездки %(cost_with_currency)s. %(cost_paid_by_wallet_with_currency)s было оплачено баллами'
     ' Плюса. Оцените поездку'),
    ('notify', 'apns.on_complete_price_cashback_with_amount', 'ru',
     'Стоимость поездки %(cost_with_currency)s.'
     ' Кэшбэк +%(cashback_amount)s баллов. Оцените поездку'),
    ('tariff', 'currency_with_sign.default', 'ru',
     '$SIGN$$VALUE$$CURRENCY$'),
    ('tariff', 'currency.rub', 'ru',
     '₽'),
])
@pytest.mark.parametrize('order_id,exp_text,exp_key,cost,payment_type,current_prices', [
    ('order_id3', 'Оцените поездку', 'on_complete', None, 'card', None),
    ('order_id3', 'Стоимость поездки 300₽. Оцените поездку',
     'on_complete_price', 300.0, 'card', None),
    ('order_id3', 'Поездка была оплачена плюсом: 300₽. Оцените поездку',
     'on_complete_price_personal_wallet_with_amount', 300.0, 'personal_wallet',
     {'cost_breakdown': [{'amount': 300.0, 'type': 'personal_wallet'}], 'user_total_display_price': 300.0}),
    ('order_id3', 'Стоимость поездки 300₽. '
                  '100₽ было оплачено баллами Плюса. Оцените поездку',
     'on_complete_price_complements_with_amount', 300.0, 'card',
     {'cost_breakdown': [{'amount': 100.0, 'type': 'personal_wallet'}, {'amount': 200.0, 'type': 'card'}],
      'user_total_display_price': 300.0}),
    ('order_id3', 'Поездка была оплачена плюсом: 300₽. Оцените поездку',
     'on_complete_price_personal_wallet_with_amount', 300.0, 'card',
     {'cost_breakdown': [{'amount': 300.0, 'type': 'personal_wallet'}],
      'user_total_display_price': 300.0}),
    ('order_id3', 'Стоимость поездки 300₽. Кэшбэк +300 баллов.'
                  ' Оцените поездку', 'on_complete_price_cashback_with_amount', 300.0,
    'card', {'cashback_price': 100.0, 'discount_cashback': 200.0, 'user_total_display_price': 300.0}),
    ('order_id3', 'Стоимость поездки 300₽. Кэшбэк +200 баллов.'
                  ' Оцените поездку', 'on_complete_price_cashback_with_amount', 300.0,
    'card', {'discount_cashback': 200.0, 'user_total_display_price': 300.0}),
    ('order_id3', 'Стоимость поездки 300₽. Кэшбэк +100 баллов.'
                  ' Оцените поездку', 'on_complete_price_cashback_with_amount', 300.0,
    'card', {'cashback_price': 100.0, 'user_total_display_price': 300.0}),
    ('order_id3', 'Стоимость поездки 300₽. Оцените поездку',
                  'on_complete_price', 300.0,
    'card', {'cashback_price': 0.0, 'user_total_display_price': 300.0}),
])
@pytest.inline_callbacks
def test_notify_on_complete_using_current_prices(patch, order_id, exp_text, exp_key, cost, payment_type,
                                                 current_prices):
    @patch('taxi.internal.order_kit.order_helpers.need_to_get_user_feedback')
    def need_to_get_user_feedback(*args, **kwargs):
        return True

    yield check_apns_notification_text(
        patch, order_id, notify.notify_on_complete, exp_key, exp_text,
        need_performer=True, cost=cost,
        payment_type=payment_type, current_prices=current_prices)


@pytest.mark.filldb()
@pytest.mark.config(
    CURRENT_PRICES_WORK_MODE='oldway',
)
@pytest.inline_callbacks
def test_get_order_user_display_cost_oldway(patch):
    order_id = '12e05188-354c-4772-a351-e6475f2443a7'
    expected_cost = 116.0
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)

    cost = yield notify._get_order_user_display_cost(proc)
    assert cost == expected_cost


@pytest.mark.filldb()
@pytest.mark.config(
    CURRENT_PRICES_WORK_MODE='newway',
)
@pytest.inline_callbacks
def test_get_order_user_display_cost_newway_no_currency_prices(patch):
    order_id = '12e05188-354c-4772-a351-e6475f2443a7'
    expected_cost = 116.0
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)

    cost = yield notify._get_order_user_display_cost(proc)
    assert cost == expected_cost


@pytest.mark.filldb()
@pytest.mark.config(
    CURRENT_PRICES_WORK_MODE='newway',
)
@pytest.inline_callbacks
def test_get_order_user_display_cost_newway(patch):
    order_id = '12e05188-354c-4772-a351-e6475f2443a7'
    expected_cost = 600.0
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc.order['current_prices'] = {
        'user_total_display_price': 600.0,
    }

    cost = yield notify._get_order_user_display_cost(proc)
    assert cost == expected_cost


@pytest.mark.filldb()
@pytest.mark.config(
    CURRENT_PRICES_WORK_MODE='dryrun',
)
@pytest.inline_callbacks
def test_get_order_user_display_cost_dryrun(patch):
    order_id = '12e05188-354c-4772-a351-e6475f2443a7'
    expected_cost = 116.0
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc.order['current_prices'] = {
        'user_total_display_price': 600.0,
    }

    cost = yield notify._get_order_user_display_cost(proc)
    assert cost == expected_cost


@pytest.mark.filldb()
@pytest.mark.config(
    CURRENT_PRICES_WORK_MODE='tryout',
)
@pytest.inline_callbacks
def test_get_order_user_display_cost_tryout(patch):
    order_id = '12e05188-354c-4772-a351-e6475f2443a7'
    expected_cost = 600.0
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc.order['current_prices'] = {
        'user_total_display_price': 600.0,
    }

    cost = yield notify._get_order_user_display_cost(proc)
    assert cost == expected_cost


@pytest.mark.filldb()
@pytest.mark.config(
    CURRENT_PRICES_WORK_MODE='oldway',
)
@pytest.mark.parametrize('price_label', ['cashback_price', 'charity_price'])
@pytest.inline_callbacks
def test_get_order_user_display_cost_oldway_cashback_price(patch, price_label):
    order_id = '12e05188-354c-4772-a351-e6475f2443a7'
    expected_cost = 600.0
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc.order['current_prices'] = {
        'user_total_display_price': 600.0,
        price_label: 400,
    }

    cost = yield notify._get_order_user_display_cost(proc)
    assert cost == expected_cost


ON_REORDER_SUGGEST_TEXT = 'Не удается найти водителей на заказ. '\
                          'Попробуйте изменить параметры поиска'


@pytest.mark.filldb()
@pytest.mark.translations([
    ('notify', 'time', 'ru', 'time'),
    ('notify', 'sms.on_reorder_suggest', 'ru',
     '%(order_name_prefix)s' + ON_REORDER_SUGGEST_TEXT),
])
@pytest.mark.parametrize('order_id,exp_text', [
    ('order_id3', ON_REORDER_SUGGEST_TEXT),
    ('order_id_in_multiorder', 'Заказ №1. ' + ON_REORDER_SUGGEST_TEXT),
])
@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY2=True)
@pytest.inline_callbacks
def test_notify_on_reorder_suggest_multiorder(
        patch, order_id, exp_text, userapi_get_user_phone_mock,
        personal_retrieve_mock,
):
    yield check_sms_notification_text(patch, order_id,
                                  notify.notify_on_reorder_suggest,
                                  'on_reorder_suggest', exp_text)


@pytest.mark.filldb()
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize('callback,num_calls', [
    (
        None,
        0
    ),
    (
        {
            'data': 'alice_callback',
            'notify_on': ['on_assigned', 'on_waiting']
        },
        1
    ),
    (
        {
            'data': 'alice_callback',
            'notify_on': []
        },
        0
    ),
    (
        {
            'data': 'alice_callback',
        },
        1
    )
])
@pytest.mark.config(ALICE_NOTIFICATIONS_ENABLED=True)
@pytest.mark.config(ALICE_NOTIFICATIONS=['on_assigned'])
@pytest.mark.translations([
    ('client_messages', 'time', 'ru', 'time'),
    ('notify', 'notifications.color', 'ru', '<color>'),
    ('notify', 'time', 'ru', 'time'),
])
@pytest.inline_callbacks
def test_notify_alice_simple(patch, load, callback,
                             num_calls, areq_request):

    @patch('taxi.internal.dbh.notifications_queue.new_task')
    def new_task(*args, **kwargs):
        return dbh.notifications_queue.Doc()

    @patch('taxi_stq.client.add_notification_task')
    def add_notification_task(*args, **kwargs):
        return

    @patch('uuid.uuid4')
    def uuid4():
        uuid4_ = collections.namedtuple('uuid4', 'hex')
        return uuid4_(MAGIC_UUID)

    @patch('taxi.internal.notifications.order._arrival_interval')
    def _arrival_interval(*args, **kwargs):
        return False, 1

    @patch('taxi.internal.notifications.order._order_tz')
    def _order_tz(*args, **kwargs):
        return "Europe/Moscow"

    @patch('taxi.internal.driver_manager._set_brand_model')
    def _set_brand_model(brand, model, car_doc):
        car_doc['brand'] = brand
        car_doc['model'] = model

    @patch('taxi.internal.driver_manager._set_color')
    def _set_color(color, car_doc):
        assert color == 'red'
        car_doc['color'] = 'red'
        car_doc['color_code'] = 'FAFBFB'

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    order_id = '12e05188-354c-4772-a351-e6475f2443a7'

    order_update = {'source': 'alice'}
    proc_update = {'order.source': 'alice'}
    if callback:
        order_update.update({'callback': callback})
        proc_update.update({'order.callback': callback})

    db.orders.update({'_id': order_id}, {'$set': order_update})
    db.order_proc.update({'_id': order_id}, {'$set': proc_update})

    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc.order.request.due = NOW + datetime.timedelta(minutes=10)
    order_state = order_fsm.OrderFsm(proc=proc)
    order_state._candidate_index = 0
    yield status_handling._handle_assigning(order_state)

    calls = new_task.calls
    assert len(calls) == num_calls
    if calls:
        key = order_state.order_id
        index = order_state.event_index
        event = 'alice.on_assigned'
        destination_type = 'alice'
        destination = None
        text = None
        application = {}
        app_version = {}
        payload = json.loads(load('payloads/notify_alice_simple.json'))
        payload['callback_data'] = callback['data']
        user_id = order_state.proc.order.user_id
        for call in calls:
            push_id = call['args'][6].pop('id')
            assert push_id is not None
            assert call['args'] == (
                key,
                index,
                event,
                destination_type,
                destination,
                text,
                payload,
                user_id,
                application,
                app_version
            )


@pytest.mark.filldb()
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize('handling,event_state', [
    (status_handling._handle_assigning, 'on_assigned'),
    (status_handling._handle_waiting, 'on_waiting'),
    (status_handling._handle_transporting, 'on_transporting'),
    (status_handling._handle_autoreorder_timeout, 'on_autoreorder_timeout'),
    (status_handling._handle_search_failed, 'on_search_failed'),
    (mock_notify_on_driver_arriving_without_eta, 'on_driver_arriving'),
    (status_handling._handle_moved_to_cash, 'on_moved_to_cash'),
    (status_handling._handle_debt_allowed, 'on_debt_allowed'),
    (status_handling._handle_cancel_by_park, 'on_failed'),
    (status_handling._handle_fail_by_park, 'on_failed'),
    (status_handling._handle_cancel_by_park, 'on_failed_price'),
    (status_handling._handle_fail_by_park, 'on_failed_price'),
    (status_handling._handle_cancel_by_park, 'on_failed_price_with_coupon'),
    (status_handling._handle_fail_by_park, 'on_failed_price_with_coupon')
])
@pytest.mark.config(ALICE_NOTIFICATIONS_ENABLED=True)
@pytest.mark.config(ALICE_NOTIFICATIONS=[
    'on_assigned',
    'on_waiting',
    'on_transporting',
    'on_assigned_exact',
    'on_autoreorder_timeout',
    'on_search_failed',
    'on_moved_to_cash',
    'on_moved_to_cash_with_coupon',
    'on_debt_allowed',
    'on_failed',
    'on_failed_price',
    'on_failed_price_with_coupon'
])
@pytest.mark.translations([
    ('client_messages', 'time', 'ru', 'time'),
    ('notify', 'notifications.color', 'ru', '<color>'),
    ('notify', 'time', 'ru', 'time'),
])
@pytest.inline_callbacks
def test_notify_alice_all(patch, load, handling, event_state, areq_request):

    @patch('taxi.internal.dbh.notifications_queue.new_task')
    def new_task(*args, **kwargs):
        return dbh.notifications_queue.Doc()

    @patch('taxi_stq.client.add_notification_task')
    def add_notification_task(*args, **kwargs):
        return

    @patch('uuid.uuid4')
    def uuid4():
        uuid4_ = collections.namedtuple('uuid4', 'hex')
        return uuid4_(MAGIC_UUID)

    @patch('taxi.internal.notifications.order._arrival_interval')
    def _arrival_interval(*args, **kwargs):
        return False, 1

    @patch('taxi.internal.notifications.order._order_tz')
    def _order_tz(*args, **kwargs):
        return "Europe/Moscow"

    @patch('taxi.internal.driver_manager._set_brand_model')
    def _set_brand_model(brand, model, car_doc):
        car_doc['brand'] = brand
        car_doc['model'] = model

    @patch('taxi.internal.driver_manager._set_color')
    def _set_color(color, car_doc):
        assert color == 'red'
        car_doc['color'] = 'red'
        car_doc['color_code'] = 'FAFBFB'

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    def form_payload(event_state, callback):
        payload = {
            'event': event_state,
            'callback_data': callback['data'],
        }

        if event_state in {
            'on_assigned',
            'on_waiting',
            'on_transporting',
            'on_driver_arriving'
        }:
            payload['service_data'] = json.loads(load('payloads/notify_alice_all/on_assigned.json'))
        elif event_state in {
            'on_search_failed',
            'on_autoreorder_timeout',
            'on_moved_to_cash',
            'on_moved_to_cash_with_coupon',
            'on_debt_allowed'
        }:
            payload['service_data'] = json.loads(load('payloads/notify_alice_all/on_search_failed.json'))
        elif event_state in {
            'on_failed',
            'on_failed_price',
            'on_failed_price_with_coupon'
        }:
            payload['service_data'] = json.loads(load('payloads/notify_alice_all/on_failed.json'))

        if event_state == 'on_assigned':
            payload['service_data'].update({'time_left': '1'})
        elif event_state == 'on_driver_arriving':
            payload['service_data'].update({'free_waiting': 5})
        elif event_state == 'on_failed_price':
            payload['service_data'].update({
                'currency': 'RUB',
                'cost': 116
            })
        elif event_state == 'on_failed_price_with_coupon':
            payload['service_data'].update({
                'currency': 'RUB',
                'cost': 116,
                'discount': 20,
                'final_cost': 96
            })

        return payload

    def prepare_order(order_id, event_state, callback):

        order_update = {'source': 'alice',
                        'callback': callback}
        proc_update = {'order.source': 'alice',
                       'order.callback': callback}

        db.orders.update({'_id': order_id}, {'$set': order_update})

        unset_proc = {}
        if event_state == 'on_failed':
            unset_proc .update({'order.cost': True})
        elif event_state == 'on_failed_price_with_coupon':
            proc_update.update({
                'order.coupon.valid': True,
                'order.coupon.was_used': True,
                'order.coupon.value': 20,
            })
        changes = {'$set': proc_update}
        if unset_proc:
            changes.update({'$unset': unset_proc})

        db.order_proc.update({'_id': order_id}, changes)

    callback = {'data': 'alice_callback'}
    order_id = '12e05188-354c-4772-a351-e6475f2443a7'
    prepare_order(order_id, event_state, callback)

    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc.order.request.due = NOW + datetime.timedelta(minutes=10)
    order_state = order_fsm.OrderFsm(proc=proc)
    order_state._handle_assigned({'i': 0})  # set last_candidate
    yield handling(order_state, log_extra=None)

    key = order_state.order_id
    index = order_state.event_index
    event = 'alice.' + event_state
    destination_type = 'alice'
    destination = None
    text = None
    application = {}
    app_version = {}
    payload = form_payload(event_state, callback)

    user_id = order_state.proc.order.user_id

    calls = new_task.calls
    assert len(calls) == 1
    for call in calls:
        push_id = call['args'][6].pop('id')
        assert push_id is not None
        assert call['args'] == (
            key,
            index,
            event,
            destination_type,
            destination,
            text,
            payload,
            user_id,
            application,
            app_version
        )


@pytest.mark.parametrize('status_updates,expected', [
    ([], None),
    (
        [
            {
                'a': {
                    'payment_type': 'card',
                },
                'q': 'change_payment',
            }
        ],
        True,
    ),
    (
        [
            {
                'a': {
                    'payment_type': 'card',
                },
                'q': 'switch_to_card',
            }
        ],
        True,
    ),
    (
        [
            {
                'a': {
                    'payment_type': 'card',
                },
                'q': 'foo',
            }
        ],
        None,
    ),
    (
        [
            {
                'a': {
                    'payment_type': 'card',
                },
                'q': 'change_payment',
            },
            {
                'a': {
                    'payment_type': 'cash',
                },
                'q': 'change_payment',
            }
        ],
        None,
    ),
    (
        [
            {
                'a': {
                    'payment_type': 'card',
                },
                'q': 'change_payment',
            },
            {
                'a': {
                    'payment_type': 'cash',
                },
                'q': 'change_payment',
            },
            {
                'a': {
                    'payment_type': 'card',
                },
                'q': 'switch_to_card',
            },
        ],
        True,
    ),
])
@pytest.inline_callbacks
def test_get_user_switched_to_card(patch, status_updates, expected):

    mock_cardstorage(patch)

    for event in status_updates:
        event['a'].update({
            'billing_card_id': 'foo',
            'change_value': {
                'ip': 'bar',
                'yandex_uid': 'baz',
            }
        })
        event['h'] = True

    proc = dbh.order_proc.Doc(
        {
            '_id': 'proc_id',
            'order_info': {
                'statistics': {
                    'status_updates': status_updates,
                },
            },
        },
    )
    state = order_fsm.OrderFsm(proc=proc)
    yield status_handling._handle_preupdate_order_change_payment(state)
    method_info = proc.preupdated_order_data.payment_method_info

    if expected is None:
        if len(method_info) != 0:
            assert method_info[0]['tag'] == 'payment_method_info'
            assert method_info[0]['data'].type == dbh.orders.PAYMENT_TYPE_CASH
    else:
        assert method_info[0]['tag'] == 'payment_method_info'
        assert method_info[0]['data'].type == dbh.orders.PAYMENT_TYPE_CARD

    for event in status_updates:
        event.pop('h')

    result = notify._get_user_switched_to_card(proc)

    assert result == expected


def _prepare_on_assign_translations(custom_translations):
    required_translations = [
        ('notify', 'time', 'ru', ''),
        ('tariff', 'currency_with_sign.default', 'ru',
         '$VALUE$ $SIGN$$CURRENCY$'),
        ('tariff', 'currency.rub', 'ru', 'rub'),
        ('notify', 'notifications.color', 'ru', ''),
    ]
    required_translations.extend(custom_translations)
    return required_translations


@pytest.mark.config(
    NOTIFICATION_PREFIX_BY_TARIFF={
        'econom': {
            'on_assigned': {
                'apns': 'econom_prefix'
            }
        }
    }
)
@pytest.mark.translations(_prepare_on_assign_translations([
    ('notify', 'sms.on_assigned', 'ru', ''),
    ('notify', 'apns.on_assigned', 'ru',
     'Assigned ordinary driver %(driver_short_name)s'),
    ('notify', 'econom_prefix.apns.on_assigned', 'ru',
     'Assigned econom driver %(driver_short_name)s')
]))
@pytest.mark.parametrize(('order_id', 'notify_text'), [
    ('econom_order', 'Assigned econom driver Ivan'),
    ('business_order', 'Assigned ordinary driver Ivan')
])
@pytest.mark.filldb(order_proc='econom_and_business')
@pytest.inline_callbacks
def test_notify_assigned_with_prefix(patch, order_id, notify_text,
                                     areq_request):
    @patch('taxi.internal.driver_manager._set_brand_model')
    def _set_brand_model(brand, model, car_doc):
        car_doc['brand'] = brand
        car_doc['model'] = model

    @patch('taxi.internal.driver_manager._set_color')
    def _set_color(color, car_doc):
        assert color == 'red'
        car_doc['color'] = 'red'
        car_doc['color_code'] = 'FAFBFB'

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    yield check_apns_notification_text(
        patch, order_id, notify.notify_on_assigned,
        'on_assigned', notify_text, need_performer=True
    )


@pytest.mark.config(
    NOTIFICATION_PREFIX_BY_TARIFF={
        'econom': {
            'on_waiting': {
                'apns': 'econom_prefix'
            }
        }
    }
)
@pytest.mark.translations(_prepare_on_assign_translations([
    ('notify', 'sms.on_waiting', 'ru', ''),
    ('notify', 'apns.on_waiting', 'ru',
     'Ordinary driver %(driver_short_name)s is waiting'),
    ('notify', 'econom_prefix.apns.on_waiting', 'ru',
     'Econom driver %(driver_short_name)s is waiting')
]))
@pytest.mark.parametrize(('order_id', 'notify_text'), [
    ('econom_order', 'Econom driver Ivan is waiting'),
    ('business_order', 'Ordinary driver Ivan is waiting')
])
@pytest.mark.filldb(order_proc='econom_and_business')
@pytest.inline_callbacks
def test_notify_waiting_with_prefix(patch, order_id, notify_text, areq_request):
    @patch('taxi.internal.driver_manager._set_brand_model')
    def _set_brand_model(brand, model, car_doc):
        car_doc['brand'] = brand
        car_doc['model'] = model

    @patch('taxi.internal.driver_manager._set_color')
    def _set_color(color, car_doc):
        assert color == 'red'
        car_doc['color'] = 'red'
        car_doc['color_code'] = 'FAFBFB'

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    yield check_apns_notification_text(
        patch, order_id, notify.notify_on_waiting,
        'on_waiting', notify_text, need_performer=True
    )


@pytest.mark.config(
    NOTIFICATION_PREFIX_BY_TARIFF={
        'econom': {
            'on_waiting': {
                'sms': 'econom_prefix'
            }
        }
    }
)
@pytest.mark.translations(_prepare_on_assign_translations([
    ('notify', 'sms.on_assigned', 'ru', ''),
    ('notify', 'apns.on_assigned', 'ru', 'without prefix'),
    ('notify', 'econom_prefix.apns.on_assigned', 'ru', 'with prefix'),
    ('notify', 'apns.on_waiting', 'ru', 'without prefix'),
    ('notify', 'econom_prefix.apns.on_waiting', 'ru', 'with prefix')
]))
@pytest.mark.parametrize(('notify_cb', 'destination'), [
    (notify.notify_on_assigned, 'on_assigned'),
    (notify.notify_on_waiting, 'on_waiting')
])
@pytest.mark.filldb(order_proc='econom_and_business')
@pytest.inline_callbacks
def test_notify_no_wrong_prefix(patch, notify_cb, destination, areq_request):
    @patch('taxi.internal.driver_manager._set_brand_model')
    def _set_brand_model(brand, model, car_doc):
        car_doc['brand'] = brand
        car_doc['model'] = model

    @patch('taxi.internal.driver_manager._set_color')
    def _set_color(color, car_doc):
        assert color == 'red'
        car_doc['color'] = 'red'
        car_doc['color_code'] = 'FAFBFB'

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    yield check_apns_notification_text(
        patch, 'econom_order', notify_cb,
        destination, 'without prefix', need_performer=True
    )


@pytest.mark.config(PREORDER_USE_CUSTOM_NOTIFICATIONS=True)
@pytest.mark.translations(_prepare_on_assign_translations([
    ('notify', 'apns.on_assigned', 'ru', 'notification without price'),
    ('notify', 'apns.on_assigned_preorder', 'ru',
     'preorder_price %(fixed_price).2f formatted %(formatted_fixed_price)s'),
]))
@pytest.mark.parametrize(('order_id', 'expected_text', 'exp_key'), [
    ('fixed_price_preorder', 'preorder_price 115.15 formatted 115 rub',
     'on_assigned_preorder'),
    ('priceless_preorder', 'notification without price', 'on_assigned'),
    ('incomplete_fixed_price_preorder', 'notification without price',
     'on_assigned'),
])
@pytest.mark.filldb(order_proc='preorder')
@pytest.inline_callbacks
def test_preorder_on_assign(patch, order_id, expected_text, exp_key, areq_request):
    @patch('taxi.internal.driver_manager._set_brand_model')
    def _set_brand_model(brand, model, car_doc):
        car_doc['brand'] = brand
        car_doc['model'] = model

    @patch('taxi.internal.driver_manager._set_color')
    def _set_color(color, car_doc):
        assert color == 'red'
        car_doc['color'] = 'red'
        car_doc['color_code'] = 'FAFBFB'

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    yield check_apns_notification_text(
        patch, order_id, notify.notify_on_assigned,
        exp_key, expected_text, need_performer=True,
    )


@pytest.mark.translations(_prepare_on_assign_translations([
    ('notify', 'apns.on_assigned', 'ru', 'notification without price'),
]))
@pytest.mark.filldb(order_proc='preorder')
@pytest.inline_callbacks
def test_preorder_notification_disabled(patch, areq_request):
    @patch('taxi.internal.driver_manager._set_brand_model')
    def _set_brand_model(brand, model, car_doc):
        car_doc['brand'] = brand
        car_doc['model'] = model

    @patch('taxi.internal.driver_manager._set_color')
    def _set_color(color, car_doc):
        assert color == 'red'
        car_doc['color'] = 'red'
        car_doc['color_code'] = 'FAFBFB'

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    order_id = 'fixed_price_preorder'
    expected_text = 'notification without price'
    yield check_apns_notification_text(
        patch, order_id, notify.notify_on_assigned,
        'on_assigned', expected_text, need_performer=True,
    )


@pytest.mark.translations(_prepare_on_assign_translations([
    ('notify', 'apns.on_assigned', 'ru',
     '%(car_info)s|%(car_info_space_separator)s'),
]))
@pytest.mark.filldb(order_proc='econom_and_business')
@pytest.inline_callbacks
def test_on_assigned_car_info(patch, areq_request):
    @patch('taxi.internal.driver_manager._set_brand_model')
    def _set_brand_model(brand, model, car_doc):
        car_doc['brand'] = brand
        car_doc['model'] = model

    @patch('taxi.internal.driver_manager._set_color')
    def _set_color(color, car_doc):
        assert color == 'red'
        car_doc['color'] = 'red'
        car_doc['color_code'] = 'FAFBFB'

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    # Changed to latin letters
    line_break_part = 'K748HH59\nRed vehicle model'
    space_part = 'K748HH59 Red vehicle model'
    expected_text = line_break_part + '|' + space_part
    yield check_apns_notification_text(
        patch, 'econom_order', notify.notify_on_assigned,
        'on_assigned', expected_text, need_performer=True,
    )


@pytest.mark.filldb(order_proc='en_locale')
@pytest.mark.translations([
    ('notify', 'time', 'en', 'time'),
    ('notify', 'mpns.on_failed', 'en',
     '%(order_name_prefix)sDriver from park %(park_name)s refused order for %(due)s'),
    ('notify', 'sms.on_failed', 'en',
     '%(order_name_prefix)sDriver from park %(park_name)s refused order for %(due)s'),
])
@pytest.mark.parametrize('order_id,exp_text', [
    ('order_id1', 'Driver from park 1 refused order for time'),
])
@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY2=True)
@pytest.inline_callbacks
def test_pass_locale_in_communications(
        patch, order_id, exp_text, userapi_get_user_phone_mock,
        personal_retrieve_mock
):
    @patch('taxi.internal.notifications.order._last_performer_park')
    def _last_performer_park_name(order_state):
        return notify.LastPerformerPark('1', '')

    @patch('taxi.internal.dbh.notifications_queue.new_task')
    def new_task(*args, **kwargs):
        return dbh.notifications_queue.Doc()

    @patch('taxi_stq.client.add_notification_task')
    def add_notification_task(*args, **kwargs):
        return

    exp_key = 'on_failed'

    user = yield dbh.users.Doc.find_one_by_id('mpns_user')
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc.order.request.due = NOW + datetime.timedelta(minutes=10)

    state = order_fsm.OrderFsm(proc=proc)

    yield notify.notify_on_failed(state, None)

    calls = new_task.calls
    assert len(calls) == 1
    assert calls[0]['args'] == (
        order_id,
        -1,
        'sms.' + exp_key,
        'sms',
        '+72222222222',
        exp_text,
        {
            'from_uid': None,
            'intent': 'taxi_order_{}'.format(exp_key),
            'meta': {'order_id': order_id},
            'locale': 'en',
        },
        user.pk,
        user.application,
        user.application_version,
    )
    assert calls[0]['kwargs']['localizable_text'] == {
        'key': 'sms.on_failed',
        'keyset': 'notify',
        'params': {
            'due': 'time',
            'order_id': 'order_id1',
            'order_name_prefix': '',
            'park_name': u'1',
            'tz': u'Europe/Moscow',
        }
    }
