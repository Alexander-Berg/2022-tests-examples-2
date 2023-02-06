from __future__ import unicode_literals

import datetime
import json

import pytest

from taxi import config
from taxi.core import async
from taxi.core import db
from taxi.internal.city_kit import country_manager
from taxi.internal.subvention_kit import notify
from taxi.internal.subvention_kit import personal_notify

TRANSLATIONS = [
    (
        'taximeter_messages', 'subventions_feed.rule_sum', 'ru',
        '%(sum)s %(currency)s'
    ),
    (
        'taximeter_messages', 'subventions_done_feed.n_orders', 'ru',
        '%(count)s orders'
    ),
    (
        'taximeter_messages', 'subventions_feed.n_orders', 'ru',
        '%(count)s and more orders'
    ),
    (
        'taximeter_messages', 'subventions_feed.bonus_title', 'ru',
        'bonus title'
    ),
    (
        'taximeter_messages', 'subventions_feed.bonus_title_armeny', 'ru',
        'armeny bonus title'
    ),
    (
        'taximeter_messages', 'subventions_done_feed.bonus_title', 'ru',
        'done bonus title'
    ),
    (
        'taximeter_messages', 'subventions_done_feed.bonus_title_armeny', 'ru',
        'armeny done bonus title'
    ),
    (
        'taximeter_messages', 'subventions_done_feed.bonus_text', 'ru',
        'you got %(cost)s, good job!'
    ),
    (
        'taximeter_messages', 'subventions_done_feed.bonus_text_armeny', 'ru',
        'armeny you got %(cost)s, good job!'
    ),
    (
        'taximeter_messages', 'subventions_done_feed.bonus_text_sms',
        'ru', 'you got %(cost)s by sms, good job!'
    ),
    (
        'taximeter_messages', 'subventions_done_feed.bonus_text_sms_armeny',
        'ru', 'armeny you got %(cost)s by sms, good job!'
    ),
    (
        'taximeter_messages', 'subventions_feed.bonus_text', 'ru',
        'bonus %(cost)s get %(num_orders)s %(in_zone)s from %(from)s to %(to)s'
    ),
    (
        'taximeter_messages', 'subventions_feed.bonus_text_armeny', 'ru',
        'armeny bonus %(cost)s get %(num_orders)s %(in_zone)s'
        ' from %(from)s to %(to)s'
    ),
    (
        'taximeter_messages', 'subventions_feed.bonus_text_sms', 'ru',
        'sms %(cost)s get %(num_orders)s %(in_zone)s from %(from)s to %(to)s'
    ),
    (
        'taximeter_messages', 'subventions_feed.bonus_text_sms_armeny', 'ru',
        'armeny sms %(cost)s get %(num_orders)s %(in_zone)s'
        ' from %(from)s to %(to)s'
    ),
    (
        'taximeter_messages', 'subventions_feed.bonus_text_with_hours', 'ru',
        'bonus %(cost)s get %(num_orders)s %(in_zone)s at %(begin_time)s - %(end_time)s, active from %(from)s to %(to)s'
    ),
    (
        'taximeter_messages', 'subventions_feed.bonus_text_sms_with_hours', 'ru',
        'sms %(cost)s get %(num_orders)s %(in_zone)s at %(begin_time)s - %(end_time)s, active from %(from)s to %(to)s'
    ),
    (
        'taximeter_messages', 'subventions_feed.bonus_text_with_hours_armeny', 'ru',
        (
         'armeny bonus %(cost)s get %(num_orders)s %(in_zone)s at'
         ' %(begin_time)s - %(end_time)s, active from %(from)s to %(to)s'
        )
    ),
    (
        'taximeter_messages', 'subventions_feed.bonus_text_sms_with_hours_armeny', 'ru',
        (
         'armeny sms %(cost)s get %(num_orders)s %(in_zone)s at'
        ' %(begin_time)s - %(end_time)s, active from %(from)s to %(to)s'
        )
    ),
    (
        'taximeter_messages', 'subventions_feed.rule_date', 'ru',
        '%(day)s %(month)s'
    ),
    (
        'taximeter_messages', 'subventions_feed.in_zone.moscow', 'ru',
        'in Moscow'
    ),
    (
        'tariff', 'currency.rub', 'ru', 'rub'
    ),
    (
        'notify', 'helpers.month_7_part', 'ru', 'july'
    ),
    (
        'taximeter_messages', 'subventions_feed.in_zone.ekb', 'ru',
        'in Yekaterinburg'
    ),
    (
        'taximeter_messages', 'subventions_feed.rule_sum', 'az',
        '%(sum)s %(currency)s'
    ),
    (
        'taximeter_messages', 'subventions_done_feed.n_orders', 'az',
        '%(count)s orders'
    ),
    (
        'taximeter_messages', 'subventions_feed.n_orders', 'az',
        '%(count)s and more orders'
    ),
    (
        'taximeter_messages', 'subventions_feed.bonus_title', 'az',
        'bonus title'
    ),
    (
        'taximeter_messages', 'subventions_done_feed.bonus_title', 'az',
        'done bonus title'
    ),
    (
        'taximeter_messages', 'subventions_done_feed.bonus_text', 'az',
        'you got %(cost)s, good job!'
    ),
    (
        'taximeter_messages', 'subventions_done_feed.bonus_text_sms',
        'az', 'you got %(cost)s by sms, good job!'
    ),
    (
        'taximeter_messages', 'subventions_feed.bonus_text', 'az',
        'bonus %(cost)s get %(num_orders)s %(in_zone)s from %(from)s to %(to)s'
    ),
    (
        'taximeter_messages', 'subventions_feed.bonus_text_sms', 'az',
        'sms %(cost)s get %(num_orders)s %(in_zone)s from %(from)s to %(to)s'
    ),
    (
        'taximeter_messages', 'subventions_feed.bonus_text_with_hours', 'az',
        'bonus %(cost)s get %(num_orders)s %(in_zone)s at %(begin_time)s - %(end_time)s, active from %(from)s to %(to)s'
    ),
    (
        'taximeter_messages', 'subventions_feed.bonus_text_sms_with_hours', 'az',
        'sms %(cost)s get %(num_orders)s %(in_zone)s at %(begin_time)s - %(end_time)s, active from %(from)s to %(to)s'
    ),
    (
        'taximeter_messages', 'subventions_feed.rule_date', 'az',
        '%(day)s %(month)s'
    ),
    (
        'taximeter_messages', 'subventions_feed.in_zone.baku', 'az',
        'in Baku'
    ),
    (
        'tariff', 'currency.rub', 'az', 'az'
    ),
    (
        'notify', 'helpers.month_7_part', 'az', 'july'
    ),
]


_BONUS_TITLE = u'bonus title'
_BONUS_TEXT = 'bonus 200 rub get 1 and more orders in Moscow from 14 july to 14 july'
_BONUS_TEXT_HOUR = ('bonus 200 rub get 1 and more orders in Moscow at'
    ' 01:00 - 01:59, active from 14 july to 14 july')
_A_BONUS_TITLE = u'armeny bonus title'
_A_BONUS_TEXT = 'armeny bonus 200 rub get 1 and more orders in Moscow from 14 july to 14 july'
_A_BONUS_TEXT_HOUR = ('armeny bonus 200 rub get 1 and more orders in Moscow at'
    ' 01:00 - 01:59, active from 14 july to 14 july')


def _spam(title, text):
    return {
        'alert': False,
        'drivers': [('dbid', 'uuid')],
        'texts': [text],
        'expires_at': datetime.datetime(2017, 7, 15, 10, 5),
        'important': False,
        'request_id': u'rule_id_ru',
        'title': title,
        'tvm_src_service': u'test_tvm',
        'log_extra': {
            'extdict': {
                'route': 'taxi',
                'tariffzone': u'moscow'
            }
        }
    }


_SMS_TEXT = 'sms 200 rub get 1 and more orders in Moscow from 14 july to 14 july'
_SMS_TEXT_HOUR = 'sms 200 rub get 1 and more orders in Moscow at 01:00 - 01:59, active from 14 july to 14 july'
_A_SMS_TEXT = 'armeny sms 200 rub get 1 and more orders in Moscow from 14 july to 14 july'
_A_SMS_TEXT_HOUR = 'armeny sms 200 rub get 1 and more orders in Moscow at 01:00 - 01:59, active from 14 july to 14 july'


def _sms(text):
    return {
        'identity': 'taxi_personal_subs',
        'phones_and_messages': [(
            '+myphone',
            text,
        )],
        'route': 'taxi',
    }


def _communications_sms(text, phone_pd_id):
    return {
        'text': text,
        'intent': 'taxi_personal_subs_taxi',
        'tvm_src_service_name': 'test_tvm',
        'phone': None,
        'phone_id': phone_pd_id,
        'park_id': None,
        'driver_id': None,
        'locale': None,
        'log_extra': {
            'extdict': {'tariffzone': 'moscow', 'route': 'taxi'}
        }
    }


@pytest.mark.translations(TRANSLATIONS)
@pytest.mark.parametrize(('suffix', 'dbupdate', 'spam', 'sms'), [
    (
        None,
        {
            'is_once': True,
            'is_bonus': True,
            'type': 'add',
        },
        [_spam(title=_BONUS_TITLE, text=_BONUS_TEXT)],
        [_sms(_SMS_TEXT)],
    ),
    (
        'armeny',
        {
            'is_once': True,
            'is_bonus': True,
            'type': 'add',
        },
        [_spam(title=_A_BONUS_TITLE, text=_A_BONUS_TEXT)],
        [_sms(_A_SMS_TEXT)]
    ),
    (
        None,
        {
            'hour': [1],
            'is_once': True,
            'is_bonus': True,
            'type': 'add',
        },
        [_spam(title=_BONUS_TITLE, text=_BONUS_TEXT_HOUR)],
        [_sms(_SMS_TEXT_HOUR)],
    ),
    (
        'armeny',
        {
            'hour': [1],
            'is_once': True,
            'is_bonus': True,
            'type': 'add',
        },
        [_spam(title=_A_BONUS_TITLE, text=_A_BONUS_TEXT_HOUR)],
        [_sms(_A_SMS_TEXT_HOUR)],
    ),
])
@pytest.mark.config(PASSPORT_SMS_DEFAULT_ROUTE='taxi')
@pytest.mark.now('2017-07-15T10:00:00')
@pytest.inline_callbacks
def test_notify_on_new_subventions(patch, suffix, dbupdate, spam, sms):
    yield config.NOTIFY_ON_NEW_PERSONAL_SUBVENTIONS.save(True)
    yield config.SUBVENTIONS_PERSONAL_SEND_SMS.save(True)
    if dbupdate:
        yield db.personal_subvention_rules.update(
            {'_id': 'rule_id'},
            {'$set': dbupdate},
        )
    original_get_doc = country_manager.get_doc

    @patch('taxi.internal.city_kit.country_manager.get_doc')
    @async.inline_callbacks
    def get_doc(country_code, **kwargs):
        country = yield original_get_doc(country_code, **kwargs)
        if suffix is not None and country['_id'] == 'rus':
            country['subventions_text_suffix'] = suffix
        async.return_value(country)

    @patch('taxi.external.communications.notify_drivers')
    def notify_drivers(request_id, title, drivers, texts=None, expires_at=None,
                       alert=False, important=False, tvm_src_service=None, log_extra=None):
        pass

    @patch('taxi.internal.sms_sender.register_task')
    def register_task(phones_and_messages, identity=None, route=None):
        assert identity == personal_notify.PERSONAL_SUBS_IDENTITY
        return 1

    @patch('taxi.internal.sms_sender.start_task')
    def start_task(task_id, schedule_time=None):
        pass

    yield personal_notify.notify_on_new_subventions(
        'personal_subventions_notify', 'test_tvm'
    )
    assert notify_drivers.calls == spam
    assert register_task.calls == sms
    assert start_task.calls == [{'schedule_time': None, 'task_id': 1}]


@pytest.mark.translations(TRANSLATIONS)
@pytest.mark.parametrize(('suffix', 'dbupdate', 'spam', 'sms'), [
    (
        None,
        {
            'is_once': True,
            'is_bonus': True,
            'type': 'add',
        },
        [_spam(title=_BONUS_TITLE, text=_BONUS_TEXT)],
        [
            _communications_sms(_SMS_TEXT, phone_pd_id='phone_pd_id_1'),
            _communications_sms(_SMS_TEXT, phone_pd_id='phone_pd_id_2'),
        ],
    ),
])
@pytest.mark.config(
    BILLING_USE_PHONE_PD_ID_FOR_NEW_PERSONAL_GOAL_SMS=True,
    PASSPORT_SMS_DEFAULT_ROUTE='taxi',
)
@pytest.mark.now('2017-07-15T10:00:00')
@pytest.inline_callbacks
def test_sms_via_communications_on_new_subventions(
        patch, suffix, dbupdate, spam, sms):
    yield config.NOTIFY_ON_NEW_PERSONAL_SUBVENTIONS.save(True)
    yield config.SUBVENTIONS_PERSONAL_SEND_SMS.save(True)
    if dbupdate:
        yield db.personal_subvention_rules.update(
            {'_id': 'rule_id'},
            {'$set': dbupdate},
        )
    original_get_doc = country_manager.get_doc

    @patch('taxi.internal.city_kit.country_manager.get_doc')
    @async.inline_callbacks
    def get_doc(country_code, **kwargs):
        country = yield original_get_doc(country_code, **kwargs)
        if suffix is not None and country['_id'] == 'rus':
            country['subventions_text_suffix'] = suffix
        async.return_value(country)

    @patch('taxi.external.communications.notify_drivers')
    def notify_drivers(request_id, title, drivers, texts=None, expires_at=None,
                       alert=False, important=False, tvm_src_service=None,
                       log_extra=None):
        pass

    @patch('taxi.external.communications.send_driver_sms')
    def send_driver_sms(text, intent, tvm_src_service_name, phone=None,
                        phone_id=None, park_id=None, driver_id=None,
                        locale=None, log_extra=None):
        pass

    @patch('taxi.external.driver_profiles.retrieve_driver_profiles')
    def retrieve_driver_profiles(
            id_in_set, projection, consumer, log_extra=None):
        return {
            'profiles': [
                {
                    'data': {
                        'phone_pd_ids': [
                            {
                                'pd_id': 'phone_pd_id_1'
                            },
                            {
                                'pd_id': 'phone_pd_id_1'
                            },
                            {
                                'pd_id': 'phone_pd_id_2'
                            }
                        ]
                    },
                    'park_driver_profile_id': 'dbid_uuid',
                }
            ]
        }

    def _sorted_sms_calls(calls):
        return sorted(calls, key=lambda call: call['phone_id'])

    yield personal_notify.notify_on_new_subventions(
        'personal_subventions_notify', 'test_tvm'
    )
    assert notify_drivers.calls == spam
    calls = send_driver_sms.calls
    assert _sorted_sms_calls(calls) == _sorted_sms_calls(sms)


@pytest.mark.translations(TRANSLATIONS)
@pytest.mark.parametrize('suffix,spam,sms', [
    (
        None,
        [{
            'alert': False,
            'drivers': [(u'db_id', u'uuid')],
            'texts': [u'you got 200 rub, good job!'],
            'expires_at': datetime.datetime(2017, 7, 17, 10, 0),
            'important': False,
            'request_id': u'rule_id_ru_feed_id',
            'title': u'done bonus title',
            'tvm_src_service': u'test_tvm',
            'log_extra': {
                'extdict': {
                    'route': 'taxi',
                    'tariffzone': u'moscow'
                }
            }
        }],
        [{
            'identity': 'taxi_personal_subs',
            'phones_and_messages': [(
                '+79213540214',
                'you got 200 rub by sms, good job!'
            )],
            'route': 'taxi',
        }]
    ),
    (
        'armeny',
        [{
            'alert': False,
            'drivers': [(u'db_id', u'uuid')],
            'texts': [u'armeny you got 200 rub, good job!'],
            'expires_at': datetime.datetime(2017, 7, 17, 10, 0),
            'important': False,
            'request_id': u'rule_id_ru_feed_id',
            'title': u'armeny done bonus title',
            'tvm_src_service': u'test_tvm',
            'log_extra': {
                'extdict': {
                    'route': 'taxi',
                    'tariffzone': u'moscow'
                }
            }
        }],
        [{
            'identity': 'taxi_personal_subs',
            'phones_and_messages': [(
                '+79213540214',
                'armeny you got 200 rub by sms, good job!'
            )],
            'route': 'taxi'
        }]
    ),
])
@pytest.mark.config(PASSPORT_SMS_DEFAULT_ROUTE='taxi')
@pytest.mark.now('2017-07-15T10:00:00')
@pytest.inline_callbacks
def test_notify_on_done_subventions(patch, suffix, spam, sms, areq_request):
    yield config.NOTIFY_ON_DONE_PERSONAL_SUBVENTIONS.save(True)
    yield config.SUBVENTIONS_PERSONAL_SEND_SMS.save(True)
    original_get_doc = country_manager.get_doc

    @patch('taxi.internal.city_kit.country_manager.get_doc')
    @async.inline_callbacks
    def get_doc(country_code, **kwargs):
        country = yield original_get_doc(country_code, **kwargs)
        if suffix is not None and country['_id'] == 'rus':
            country['subventions_text_suffix'] = suffix
        async.return_value(country)

    @patch('taxi.external.communications.notify_drivers')
    def notify_drivers(request_id, title, drivers, texts=None, expires_at=None,
                       alert=False, important=False, tvm_src_service=None, log_extra=None):
        pass

    @patch('taxi.internal.sms_sender.register_task')
    def register_task(phones_and_messages, identity=None, route=None):
        assert identity == personal_notify.PERSONAL_SUBS_IDENTITY
        return 1

    @patch('taxi.internal.sms_sender.start_task')
    def start_task(task_id, schedule_time=None):
        pass

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

    yield personal_notify.notify_on_done_subventions(
        'done_personal_subventions_notify', 'test_tvm'
    )
    assert notify_drivers.calls == spam
    assert register_task.calls == sms
    assert start_task.calls == [{'schedule_time': None, 'task_id': 1}]


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('locale,expected_locale', [
    ('ru', 'ru'),
    ('en', 'en'),
    ('xx', 'ru'),
])
@pytest.inline_callbacks
def test_get_known_locale(locale, expected_locale):
    actual_locale = yield notify.get_known_locale(locale)
    assert actual_locale == expected_locale


@pytest.mark.translations(TRANSLATIONS)
@pytest.mark.now('2017-07-15T10:00:00')
@pytest.mark.config(SUBVENTIONS_PERSONAL_SMS_ROUTES={
            'rus': 'yandex',
            'aze': 'uber',
            'foo': 'bar'
        })
@pytest.inline_callbacks
def test_notify_on_new_subventions_with_routes(patch):
    yield config.NOTIFY_ON_NEW_PERSONAL_SUBVENTIONS.save(True)
    yield config.SUBVENTIONS_PERSONAL_SEND_SMS.save(True)

    right_route_for_phone = {
        '+myphone': [None, 'yandex'],
        '+79213540215': [None, 'yandex'],
        '+79213540216': ['uber'],
    }

    @patch('taxi.external.communications.notify_drivers')
    def notify_drivers(request_id, title, drivers, texts=None, expires_at=None,
                       alert=False, important=False, tvm_src_service=None,
                       log_extra=None):
        pass

    @patch('taxi.internal.sms_sender.register_task')
    def register_task(phones_and_messages, identity=None, route=None):
        for phone, _ in phones_and_messages:
            assert phone in right_route_for_phone
            assert route in right_route_for_phone[phone]
        return 1

    @patch('taxi.internal.sms_sender.start_task')
    def start_task(task_id, schedule_time=None):
        pass

    dbupdate = {
                    'is_once': True,
                    'is_bonus': True,
                    'type': 'add',
                }

    yield db.personal_subvention_rules.update(
        {'_id': 'rule_id'},
        {'$set': dbupdate},
    )

    yield personal_notify.notify_on_new_subventions(
        'personal_subventions_notify', 'test_tvm'
    )

    yield db.personal_subvention_rules.update(
        {'_id': 'rule_id2'},
        {'$set': dbupdate},
    )

    yield personal_notify.notify_on_new_subventions(
        'personal_subventions_notify', 'test_tvm'
    )

    yield db.personal_subvention_rules.update(
        {'_id': 'rule_id3'},
        {'$set': dbupdate},
    )

    yield personal_notify.notify_on_new_subventions(
        'personal_subventions_notify', 'test_tvm'
    )


@pytest.mark.translations(TRANSLATIONS)
@pytest.mark.now('2017-07-15T10:00:00')
@pytest.mark.config(SUBVENTIONS_PERSONAL_SMS_ROUTES={
            'rus': 'yandex',
            'aze': 'uber',
            'foo': 'bar'
        })
@pytest.mark.parametrize('use_ucommunications', [
    (True),
    (False),
])
@pytest.inline_callbacks
def test_notify_on_done_subventions_with_routes(patch, use_ucommunications):
    yield config.NOTIFY_ON_NEW_PERSONAL_SUBVENTIONS.save(True)
    yield config.SUBVENTIONS_PERSONAL_SEND_SMS.save(True)
    yield config.DONE_PERSONAL_SUBVENTIONS_UCOMMUNICATION_SMS.save(True)

    right_route_for_phone = {
        '+myphone': [None, 'yandex'],
        '+mskphone': [None, 'yandex'],
        '+79213540216': ['uber'],
    }

    @patch('taxi.external.communications.notify_drivers')
    def notify_drivers(request_id, title, drivers, texts=None, expires_at=None,
                       alert=False, important=False, tvm_src_service=None, log_extra=None):
        pass

    @patch('taxi.internal.sms_sender.register_task')
    def register_task(phones_and_messages, identity=None, route=None):
        for phone, _ in phones_and_messages:
            assert phone in right_route_for_phone
            assert route in right_route_for_phone[phone]
        return 1

    @patch('taxi.internal.sms_sender.start_task')
    def start_task(task_id, schedule_time=None):
        pass

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    @patch('taxi.external.communications.send_driver_sms')
    @async.inline_callbacks
    def send_driver_sms(text, intent, tvm_src_service_name, phone=None,
                        phone_id=None, park_id=None, driver_id=None,
                        locale=None, log_extra=None):
        pass

    yield personal_notify.notify_on_done_subventions(
        'done_personal_subventions_notify', 'test_tvm'
    )

    yield personal_notify.notify_on_done_subventions(
        'done_personal_subventions_notify', 'test_tvm'
    )

    yield personal_notify.notify_on_done_subventions(
        'done_personal_subventions_notify', 'test_tvm'
    )
