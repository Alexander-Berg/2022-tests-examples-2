# -*- coding: utf-8 -*-

import json

from nose.tools import eq_
from passport.backend.adm_api.test.mock_objects import (
    mock_grants,
    mock_headers,
)
from passport.backend.adm_api.test.utils import with_settings_hosts
from passport.backend.adm_api.test.views import (
    BaseViewTestCase,
    ViewsTestEnvironment,
)
from passport.backend.adm_api.tests.views.restore.data import *
from passport.backend.adm_api.views.restore.helpers import MASKED_ANSWER
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_response
from passport.backend.core.builders.historydb_api import HistoryDBApiTemporaryError
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    event_item,
    event_restore_item,
    events_response,
    events_restore_response,
)
from passport.backend.core.historydb.events import *


class RestoreAttemptViewBaseTestCase(BaseViewTestCase):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[event_restore_item(restore_id=TEST_RESTORE_ID)]),
        )
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response())
        self.env.historydb_api.set_response_value('events', events_response(events=[]))
        self.env.grants_loader.set_grants_json(mock_grants())

    def tearDown(self):
        self.env.stop()

    def make_request(self, restore_id=TEST_RESTORE_ID, headers=None):
        query = dict(restore_id=restore_id)
        return self.env.client.get(
            '/1/restore/attempt/',
            query_string=query,
            headers=headers,
        )

    def get_headers(self, cookie=TEST_COOKIE, host=TEST_HOST, ip=TEST_IP):
        return mock_headers(cookie=cookie, host=host, user_ip=ip)


@with_settings_hosts()
class RestoreAttemptViewTestCase(RestoreAttemptViewBaseTestCase):

    def test_no_headers(self):
        resp = self.make_request(restore_id=TEST_RESTORE_ID_2)
        self.check_response_error(resp, ['ip.empty', 'cookie.empty', 'host.empty'])

    def test_no_grants(self):
        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, headers=self.get_headers())
        self.check_response_error(resp, ['access.denied'])

    def test_attempt_not_found(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, headers=self.get_headers())
        self.check_response_error(resp, ['restore_id.not_found'])

    def test_historydb_events_restore_fail(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.historydb_api.set_response_side_effect('events_restore', HistoryDBApiTemporaryError)
        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, headers=self.get_headers())
        self.check_response_error(resp, ['backend.historydb_api_failed'])

    def test_historydb_events_fail(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        data_json = json.dumps(TEST_FACTORS_DATA_VERSION_2)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )
        self.env.historydb_api.set_response_side_effect('events', HistoryDBApiTemporaryError)
        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_error(resp, ['backend.historydb_api_failed'])

    def test_attempt_found_unknown_data(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_error(resp, ['restore_id.unknown_version'])


@with_settings_hosts()
class RestoreAttemptViewVersion2TestCase(RestoreAttemptViewBaseTestCase):

    def test_attempt_json_data_form(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        data_json = json.dumps(TEST_FACTORS_DATA_VERSION_2)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())

        self.check_response_ok(
            resp,
            restore_attempt=dict(
                TEST_FACTORS_OUTPUT_VERSION_2,
                initial_support_decision=None,
                support_decision=None,
            ),
        )

    def test_attempt_with_support_decision(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        data_json = json.dumps(TEST_FACTORS_DATA_VERSION_2)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )
        historydb_response = [
            event_item(
                name=EVENT_ACTION,
                timestamp=1,
                value=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            ),
            event_item(
                name=EVENT_INFO_RESTORE_ID,
                timestamp=1,
                value=TEST_RESTORE_ID,
            ),
            event_item(
                name=EVENT_ACTION,
                timestamp=2,
                value=ACTION_RESTORE_SEMI_AUTO_DECISION,
                admin='support',
            ),
            event_item(
                name=EVENT_INFO_RESTORE_ID,
                timestamp=2,
                value=TEST_RESTORE_ID,
            ),
            event_item(
                name=EVENT_INFO_RESTORE_STATUS,
                timestamp=2,
                value=RESTORE_STATUS_PASSED,
            ),
        ]
        self.env.historydb_api.set_response_value('events', events_response(events=historydb_response))

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())

        decision = {
            u'timestamp': 2,
            u'datetime': DATETIME_FOR_TS_2,
            u'admin': u'support',
            u'status': RESTORE_STATUS_PASSED,
        }
        self.check_response_ok(
            resp,
            restore_attempt=dict(
                TEST_FACTORS_OUTPUT_VERSION_2,
                initial_support_decision=decision,
                support_decision=decision,
            ),
        )

    def test_attempt_user_entered_question_formatting(self):
        """Обработка пользовательского вопроса, не найденного в истории"""
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        raw_factors = dict(TEST_FACTORS_DATA_VERSION_2)
        raw_factors['answer'] = {
            'question': u'-2:мой вопрос',
            'entered': u'мой ответ',
            'history_best_match': None,
            'factor_absence': 0,
            'factor': TEST_STRING_FACTOR_NO_MATCH,
            'history': [],
        }
        data_json = json.dumps(raw_factors)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())

        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)
        eq_(
            resp['restore_attempt']['data']['answer'],
            {
                u'incoming': [{'question': u'99:мой вопрос', 'answer': u'мой ответ'}],
                u'errors': {},
                u'trusted': [],
                u'factors_summary': u'no_match',
                u'factors': u'no_match',
            },
        )

    def test_attempt_answer_masked(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='support'))
        raw_factors = dict(TEST_FACTORS_DATA_VERSION_2)
        raw_factors['answer'] = {
            'question': u'1:кв',
            'entered': u'ответ',
            'history_best_match': None,
            'factor_absence': 0,
            'factor': TEST_STRING_FACTOR_NO_MATCH,
            'history': ['answer1', 'answer2'],
        }
        data_json = json.dumps(raw_factors)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())

        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)
        eq_(
            resp['restore_attempt']['data']['answer'],
            {
                u'incoming': [{'question': u'1:кв', 'answer': MASKED_ANSWER}],
                u'errors': {},
                u'trusted': [MASKED_ANSWER, MASKED_ANSWER],
                u'factors_summary': u'no_match',
                u'factors': u'no_match',
            },
        )

    def test_attempt_social_profile_data_formatting(self):
        """Вывод данных соц. профиля, привязанного к аккаунту"""
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        profile_data = {
            'addresses': ['https://plus.google.com/115988632795903816809'],
            'firstname': u'Имя',
            'lastname': u'Фамилия',
            'birthday': '',
        }
        raw_factors = dict(
            TEST_FACTORS_DATA_VERSION_2,
            social_accounts={
                'entered': None,
                'api_status': True,
                'profiles': [dict(profile_data, birthday_factor=-1)],  # все доп. поля не выводятся
                'factor_absence': 0,
            }
        )
        data_json = json.dumps(raw_factors)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())

        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)
        eq_(
            resp['restore_attempt']['data']['social_accounts'],
            {
                u'trusted': [profile_data],
                u'errors': {u'api_status': True},
                u'incoming': [],
                u'factors_summary': u'',
                u'factors': {},
            },
        )

    def test_attempt_password_formatting(self):
        """Вывод информации о введённом пароле"""
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        raw_factors = dict(TEST_FACTORS_DATA_VERSION_2)
        raw_factors['password'] = {
            'used_until': None,
            'used_since': 1,
            'api_status': True,
            'auth_date_entered': '2010-10-10 MSK+0300',
            'factor': [['auth_found', 1], ['auth_date', -1]],
        }

        data_json = json.dumps(raw_factors)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())

        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)
        eq_(
            resp['restore_attempt']['data']['password'],
            {
                u'errors': {u'api_status': True},
                u'incoming': [u'2010-10-10 MSK+0300'],
                u'trusted': [{
                    u'used_since': DATETIME_FOR_TS_1,
                    u'used_until': None,
                }],
                u'factors_summary': u'match',
                u'factors': {u'auth_date': u'not_calculated', u'auth_found': u'match'},
            },
        )

    def test_attempt_delivery_address_formatting(self):
        """Вывод информации об адресах доставки аккаунта в ограниченном варианте"""
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        raw_factors = dict(TEST_FACTORS_DATA_VERSION_2)
        raw_factors['delivery_addresses'] = {
            'matches': [],
            'entered': None,
            'account': [{
                'building': '11', 'city': 'Moscow', 'entrance': '1', 'metro': '', 'zip': '11', 'flat': '',
                'firstname': '', 'country': 'Russia', 'cargolift': '', 'floor': '', 'comment': '',
                'fathersname': '', 'phone': '', 'street': 'Timura Frunze', 'lastname': '', 'suite': '',
                'intercom': '', 'phone_extra': '', 'email': '',
            }],
            'factor': [['entered_count', 0], ['account_count', 0], ['matches_count', 0], ['absence', 0]],
        }
        data_json = json.dumps(raw_factors)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())

        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)
        eq_(
            resp['restore_attempt']['data']['delivery_addresses'],
            {
                u'incoming': [],
                u'trusted': [{
                    'building': '11',
                    'city': 'Moscow',
                    'country': 'Russia',
                    'street': 'Timura Frunze',
                    'suite': '',
                }],
                u'factors_summary': u'no_match',
                u'factors': u'no_match',
                u'errors': {},
            },
        )


@with_settings_hosts()
class RestoreAttemptViewVersionMultistep3TestCase(RestoreAttemptViewBaseTestCase):
    def test_attempt_json_data_form(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        data_json = json.dumps(TEST_FACTORS_DATA_VERSION_MULTISTEP_3)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())

        self.check_response_ok(
            resp,
            restore_attempt=dict(
                TEST_FACTORS_OUTPUT_VERSION_MULTISTEP_3,
                initial_support_decision=None,
                support_decision=None,
            ),
        )

    def test_attempt_answer_masked(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='support'))
        data_json = json.dumps(TEST_FACTORS_DATA_VERSION_MULTISTEP_3)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())

        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)

        # данные в incoming и trusted замаскированы
        eq_(
            resp['restore_attempt']['data']['answer']['incoming'],
            [
                {u'answer': u'*****', u'question': u'99:question'},
            ],
        )
        eq_(
            resp['restore_attempt']['data']['answer']['trusted'],
            [u'*****', u'*****'],
        )

    def test_attempt_with_multiple_support_decisions(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        data_json = json.dumps(TEST_FACTORS_DATA_VERSION_MULTISTEP_3)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )
        historydb_response = [
            event_item(
                name=EVENT_ACTION,
                timestamp=1,
                value=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            ),
            event_item(
                name=EVENT_INFO_RESTORE_ID,
                timestamp=1,
                value=TEST_RESTORE_ID,
            ),
            event_item(
                name=EVENT_ACTION,
                timestamp=2,
                value=ACTION_RESTORE_SEMI_AUTO_DECISION,
                admin='support',
            ),
            event_item(
                name=EVENT_INFO_RESTORE_ID,
                timestamp=2,
                value=TEST_RESTORE_ID,
            ),
            event_item(
                name=EVENT_INFO_RESTORE_STATUS,
                timestamp=2,
                value=RESTORE_STATUS_REJECTED,
            ),
            event_item(
                name=EVENT_ACTION,
                timestamp=4,
                value=ACTION_RESTORE_SEMI_AUTO_DECISION,
                admin='support',
            ),
            event_item(
                name=EVENT_INFO_RESTORE_ID,
                timestamp=4,
                value=TEST_RESTORE_ID,
            ),
            event_item(
                name=EVENT_INFO_RESTORE_STATUS,
                timestamp=4,
                value=RESTORE_STATUS_PASSED,
            ),
        ]
        self.env.historydb_api.set_response_value('events', events_response(events=historydb_response))

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())

        self.check_response_ok(
            resp,
            restore_attempt=dict(
                TEST_FACTORS_OUTPUT_VERSION_MULTISTEP_3,
                initial_support_decision={
                    u'timestamp': 2,
                    u'datetime': DATETIME_FOR_TS_2,
                    u'admin': u'support',
                    u'status': RESTORE_STATUS_REJECTED,
                },
                support_decision={
                    u'timestamp': 4,
                    u'datetime': DATETIME_FOR_TS_4,
                    u'admin': u'support',
                    u'status': RESTORE_STATUS_PASSED,
                },
            ),
        )

    def test_attempt_social_profile_data_formatting(self):
        """Вывод данных по соц. профилям, привязанным к аккаунту и переданным пользователем"""
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        profile_data = {
            u'username': 'test-login',
            u'uid': 1234,
            u'profile_id': 101796,
            u'userid': '1234',
            u'person': {
                u'firstname': u'Имя',
                u'lastname': u'Фамилия',
                u'profile_id': 101791,
                u'birthday': 'None',
                u'gender': 'm',
                u'nickname': '',
                u'email': 'test-login@gmail.com',
            },
            u'allow_auth': False,
            u'provider': 'google',
            u'addresses': ['https://plus.google.com/11832068466758413025'],
        }
        profile_data_without_person = {
            u'provider': 'facebook',
            u'addresses': ['https://facebook.com/11832068466758413025'],
            u'userid': '4321',
            u'uid': 4321,
            u'profile_id': 100500,
        }
        short_profile_info = {
            u'addresses': [
                u'https://plus.google.com/11832068466758413025',
            ],
            u'birthday': 'None',
            u'firstname': u'Имя',
            u'lastname': u'Фамилия',
            u'belongs_to_account': True,
            u'is_matched': True,
        }
        short_bad_info = {
            u'addresses': [
                u'https://facebook.com/11832068466758413025',
            ],
            u'birthday': None,
            u'lastname': None,
            u'firstname': None,
            u'belongs_to_account': False,
            u'other_uids': u'4321',
        }
        raw_factors = dict(
            TEST_FACTORS_DATA_VERSION_MULTISTEP_3,
            social_accounts={
                'api_status': True,
                'account_profiles': [profile_data],
                'entered_profiles': [profile_data, profile_data_without_person],
                'factor': {
                    'account_profiles_count': 1,
                    'matches_count': 1,
                    'entered_profiles_count': 1,
                    'entered_accounts_count': 1,
                },
            },
        )
        data_json = json.dumps(raw_factors)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())

        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)
        eq_(
            resp['restore_attempt']['data']['social_accounts'],
            {
                u'trusted': [short_profile_info, short_bad_info],
                u'errors': {u'api_status': True},
                u'incoming': [],
                u'factors_summary': u'match',
                u'factors': u'match',
            },
        )

    def test_attempt_delivery_address_formatting(self):
        """Вывод информации об адресах доставки аккаунта в ограниченном варианте"""
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        raw_factors = dict(TEST_FACTORS_DATA_VERSION_MULTISTEP_3)
        raw_factors['delivery_addresses'] = {
            'matches': [],
            'entered': None,
            'account': [{
                'building': '11', 'city': 'Moscow', 'entrance': '1', 'metro': '', 'zip': '11', 'flat': '',
                'firstname': '', 'country': 'Russia', 'cargolift': '', 'floor': '', 'comment': '',
                'fathersname': '', 'phone': '', 'street': 'Timura Frunze', 'lastname': '', 'suite': '',
                'intercom': '', 'phone_extra': '', 'email': '',
            }],
            'factor': [['entered_count', 0], ['account_count', 0], ['matches_count', 0], ['absence', 0]],
        }
        data_json = json.dumps(raw_factors)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())

        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)
        eq_(
            resp['restore_attempt']['data']['delivery_addresses'],
            {
                u'incoming': [],
                u'trusted': [{
                    'building': '11',
                    'city': 'Moscow',
                    'country': 'Russia',
                    'street': 'Timura Frunze',
                    'suite': '',
                }],
                u'factors_summary': u'no_match',
                u'factors': u'no_match',
                u'errors': {},
            },
        )


@with_settings_hosts()
class RestoreAttemptViewVersionMultistep4TestCase(RestoreAttemptViewBaseTestCase):
    def test_extra_info(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        data_json = json.dumps(TEST_FACTORS_DATA_VERSION_MULTISTEP_4)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)

        eq_(
            resp['restore_attempt']['extra_info'],
            {
                u'is_current_version': False,
                u'version': u'multistep.4',
                u'restore_status': u'pending',
                u'is_for_learning': False,
                u'request_source': u'restore',
                u'contact_email': u'vasia@пупкин.рф',
            },
        )

    def test_ip_info(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        data_json = json.dumps(TEST_FACTORS_DATA_VERSION_MULTISTEP_4)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)

        eq_(
            resp['restore_attempt']['ip_info'],
            {
                u'ip': u'5.45.207.254',
                u'subnet': u'5.45.192.0/18',
                u'ua': u'os.name: windows xp, browser.name: firefox, yandexuid: yandexuid',

                u'ip_registration': None,
                u'subnet_registration': None,
                u'ua_registration': u'',

                u'ip_first_auth': None,
                u'subnet_first_auth': None,
                u'ua_first_auth': u'1970-01-01',

                u'ip_last_auth': None,
                u'subnet_last_auth': None,
                u'ua_last_auth': u'1970-01-01',

                u'factors': [
                    [
                        {u'name': u'registration_date', u'value': u'2010-10-10 10:20:30'},
                        {u'name': u'auths_limit_not_reached', u'value': 1},
                    ],
                    [
                        {u'name': u'ip_auth_interval', u'value': -1},
                        {u'name': u'ip_eq_reg', u'value': -1},
                        {u'name': u'ip_first_auth_depth', u'value': -1},
                    ],
                    [
                        {u'name': u'subnet_auth_interval', u'value': -1},
                        {u'name': u'subnet_eq_reg', u'value': -1},
                        {u'name': u'subnet_first_auth_depth', u'value': -1},
                    ],
                    [
                        {u'name': u'ua_auth_interval', u'value': 0.5},
                        {u'name': u'ua_eq_reg', u'value': 0},
                        {u'name': u'ua_first_auth_depth', u'value': 1},
                    ],
                ],
                u'gathered_auths_count': 3,
                u'errors': {u'auths_aggregated_runtime_api_status': True},
            },
        )

    def test_events_info(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        data_json = json.dumps(TEST_FACTORS_DATA_VERSION_MULTISTEP_4)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)

        eq_(
            resp['restore_attempt']['events_info'],
            {
                u'passwords': {
                    u'last_change_ua_first_auth': u'1970-01-01',
                    u'last_change_subnet_first_auth': u'1970-01-01',
                    u'last_change_ip_first_auth': u'1970-01-01',
                    u'change_envs': [
                        {u'user_ip': u'5.45.207.254', u'user_agent': u'yandexuid/yandexuid', u'datetime': u'1970-01-01 03:16:40 MSK+0300'},
                    ],
                    u'factor': [
                        [
                            {u'name': u'change_count', u'value': 0},
                            {u'name': u'last_change_depth', u'value': -1},
                        ],
                        [
                            {u'name': u'last_change_ip_eq_user', u'value': -1},
                            {u'name': u'last_change_subnet_eq_user', u'value': -1},
                            {u'name': u'last_change_ua_eq_user', u'value': -1},
                        ],
                        [
                            {u'name': u'last_change_ip_first_auth_depth', u'value': -1},
                            {u'name': u'last_change_subnet_first_auth_depth', u'value': 0.0},
                            {u'name': u'last_change_ua_first_auth_depth', u'value': 0.0},
                        ],
                        [
                            {u'name': u'last_change_is_forced_change', u'value': -1},
                            {u'name': u'forced_change_pending', u'value': 1},
                        ],
                    ],
                },
                u'recovery_changes': {
                    u'answer': {
                        u'change_envs': [
                            {u'user_ip': u'5.45.207.254', u'datetime': u'1970-01-01 03:00:03 MSK+0300', u'user_agent': u'yandexuid/123'},
                            {u'user_ip': u'5.45.207.254', u'datetime': u'1970-01-01 03:00:04 MSK+0300', u'user_agent': u'yandexuid/123'},
                            {u'user_ip': u'5.45.207.254', u'datetime': u'1970-01-01 03:00:06 MSK+0300', u'user_agent': u'yandexuid/123'},
                        ],
                        u'factor': [
                            [
                                {u'name': u'change_count', u'value': 3},
                                {u'name': u'change_depth', u'value': u'-1, -1, -1'},
                            ],
                            [
                                {u'name': u'change_ip_eq_user', u'value': u'1, 1, 1'},
                                {u'name': u'change_subnet_eq_user', u'value': u'1, 1, 1'},
                                {u'name': u'change_ua_eq_user', u'value': u'0, 0, 0'},
                            ],
                        ],
                        u'change_indices': [-3, -2, -1],
                    },
                    u'phone_numbers': {
                        u'change_envs': [
                            None,
                            {u'user_ip': u'5.45.207.254', u'datetime': u'1970-01-01 03:00:02 MSK+0300', u'user_agent': u'yandexuid/123'},
                            {u'user_ip': u'5.45.207.254', u'datetime': u'1970-01-01 03:00:04 MSK+0300', u'user_agent': u'yandexuid/123'},
                        ],
                        u'factor': [
                            [
                                {u'name': u'change_count', u'value': 2},
                                {u'name': u'change_depth', u'value': u'-1, 1, 1'},
                            ],
                            [
                                {u'name': u'change_ip_eq_user', u'value': u'-1, 1, 1'},
                                {u'name': u'change_subnet_eq_user', u'value': u'-1, 1, 1'},
                                {u'name': u'change_ua_eq_user', u'value': u'-1, 0, 0'},
                            ],
                        ],
                        u'change_indices': [-3, -2, -1],
                    },
                },
                u'aggregated': {
                    u'personal_and_recovery_change_one_day': {
                        u'ip_first_auth': [u'1970-01-01', u'1970-01-01', None, None],
                        u'subnet_first_auth': [u'1970-01-01', None, None, None],
                        u'ua_first_auth': [u'1970-01-01', None, None, None],
                        u'factor': [
                            [
                                {u'name': u'ip_match', u'value': 0},
                                {u'name': u'subnet_match', u'value': 1},
                                {u'name': u'ua_match', u'value': 1},
                            ],
                            [
                                {u'name': u'ip_eq_user', u'value': 1},
                                {u'name': u'subnet_eq_user', u'value': 0},
                                {u'name': u'ua_eq_user', u'value': 1},
                            ],
                            [
                                {u'name': u'ip_eq_reg', u'value': -1},
                                {u'name': u'subnet_eq_reg', u'value': -1},
                                {u'name': u'ua_eq_reg', u'value': 0},
                            ],
                            [
                                {u'name': u'ip_first_auth_depth', u'value': u'1.0, 0.8, -1, -1'},
                                {u'name': u'subnet_first_auth_depth', u'value': u'1.0, -1, -1, -1'},
                                {u'name': u'ua_first_auth_depth', u'value': u'1.0, -1, -1, -1'},
                            ],
                        ],
                    },
                },
            },
        )

    def test_changes_info_in_personal_data(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        data_json = json.dumps(TEST_FACTORS_DATA_VERSION_MULTISTEP_4)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)

        eq_(
            resp['restore_attempt']['data']['names'],
            {
                'changes_info': {
                    u'change_envs': [
                        {u'user_ip': u'5.45.207.1', u'user_agent': u'yandexuid/123', u'datetime': u'1970-01-01 03:00:02 MSK+0300'},
                        None,
                        {u'user_ip': u'5.45.207.1', u'user_agent': u'yandexuid/123', u'datetime': u'1970-01-01 03:00:02 MSK+0300'},
                    ],
                    u'change_indices': [0, -2, -1],
                    u'factor': [
                        [
                            {u'name': u'change_count', u'value': 1},
                            {u'name': u'change_depth', u'value': u'1.0, -1, 1.0'},
                        ],
                        [
                            {u'name': u'change_ip_eq_user', u'value': u'0, -1, 0'},
                            {u'name': u'change_subnet_eq_user', u'value': u'1, -1, 1'},
                            {u'name': u'change_ua_eq_user', u'value': u'0, -1, 0'},
                        ],
                        [
                            {u'name': u'change_ip_eq_reg', u'value': u'0, -1, 0'},
                            {u'name': u'change_subnet_eq_reg', u'value': u'1, -1, 1'},
                            {u'name': u'change_ua_eq_reg', u'value': u'1, -1, 1'},
                        ],
                    ],
                },
                u'errors': {u'historydb_api_events_status': True},
                u'factors': {u'current': u'no_match', u'intermediate': u'not_calculated', u'registration': u'no_match'},
                u'factors_summary': u'no_match',
                u'incoming': [u'A B', u'A P'],
                u'indices': {u'current': [1, 1], u'intermediate': None, u'registration': [1, 0]},
                u'trusted': [
                    u'\u041f\u0435\u0442\u0440 \u041f\u0435\u0442\u0440\u043e\u0432',
                    u'\u041f\u0435\u0442\u0440 Petroff',
                ],
                u'trusted_intervals': [
                    [
                        {
                            u'start': {u'user_ip': u'5.45.207.254', u'timestamp': 1, u'yandexuid': u'123', u'datetime': u'1970-01-01 03:00:01 MSK+0300'},
                            u'end': {u'user_ip': u'5.45.207.1', u'timestamp': 2, u'yandexuid': u'123', u'datetime': u'1970-01-01 03:00:02 MSK+0300'},
                        },
                    ],
                    [
                        {
                            u'start': {u'user_ip': u'5.45.207.1', u'timestamp': 2, u'yandexuid': u'123', u'datetime': u'1970-01-01 03:00:02 MSK+0300'},
                            u'end': None,
                        },
                    ],
                ],
            },
        )

        eq_(
            resp['restore_attempt']['data']['birthday'],
            {
                u'changes_info': {
                    u'change_indices': [0, -2, -1],
                    u'change_envs': [
                        {u'user_ip': None, u'datetime': None},
                        None,
                        {u'user_ip': None, u'datetime': None}
                    ],
                    u'factor': [
                        [
                            {u'name': u'change_count', u'value': 1},
                            {u'name': u'change_depth', u'value': u'-1, -1, -1'},
                        ],
                        [
                            {u'name': u'change_ip_eq_user', u'value': u'-1, -1, -1'},
                            {u'name': u'change_subnet_eq_user', u'value': u'-1, -1, -1'},
                            {u'name': u'change_ua_eq_user', u'value': u'0, -1, 0'},
                        ],
                        [
                            {u'name': u'change_ip_eq_reg', u'value': u'-1, -1, -1'},
                            {u'name': u'change_subnet_eq_reg', u'value': u'-1, -1, -1'},
                            {u'name': u'change_ua_eq_reg', u'value': u'0, -1, 0'},
                        ],
                    ],
                },
                u'errors': {u'historydb_api_events_status': True},
                u'factors': {u'current': u'no_match', u'intermediate': u'not_calculated', u'registration': u'no_match'},
                u'factors_summary': u'no_match',
                u'incoming': [u'2012-01-01'],
                u'indices': {u'current': 1, u'intermediate': None, u'registration': 0},
                u'trusted': [u'2011-11-11', u'2000-10-01'],
                u'trusted_intervals': [
                    [
                        {
                            u'start': {u'user_ip': u'5.45.207.254', u'timestamp': 1, u'yandexuid': u'123', u'datetime': u'1970-01-01 03:00:01 MSK+0300'},
                            u'end': {u'timestamp': None, u'datetime': None},
                        },
                    ],
                    [
                        {
                            u'start': {u'timestamp': None, u'datetime': None},
                            u'end': None,
                        },
                    ],
                ],
            },
        )


@with_settings_hosts()
class RestoreAttemptViewVersionMultistep41TestCase(RestoreAttemptViewBaseTestCase):
    def test_extra_info(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        data_json = json.dumps(TEST_FACTORS_DATA_VERSION_MULTISTEP_41)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)

        eq_(
            resp['restore_attempt']['extra_info'],
            {
                u'is_current_version': False,
                u'version': u'multistep.4.1',
                u'restore_status': u'pending',
                u'is_for_learning': False,
                u'request_source': u'restore',
                u'contact_email': u'vasia@пупкин.рф',
            },
        )

    def test_events_info_passwords(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        data_json = json.dumps(TEST_FACTORS_DATA_VERSION_MULTISTEP_41)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)

        eq_(
            resp['restore_attempt']['events_info']['passwords'],
            {
                u'last_change_ua_first_auth': u'1970-01-01',
                u'last_change_subnet_first_auth': u'1970-01-01',
                u'last_change_ip_first_auth': u'1970-01-01',
                u'change_envs': [
                    {u'user_ip': u'5.45.207.254', u'user_agent': u'yandexuid/yandexuid', u'datetime': u'1970-01-01 03:16:40 MSK+0300'},
                ],
                u'factor': [
                    [
                        {u'name': u'change_count', u'value': 0},
                        {u'name': u'last_change_depth', u'value': -1},
                    ],
                    [
                        {u'name': u'last_change_ip_eq_user', u'value': -1},
                        {u'name': u'last_change_subnet_eq_user', u'value': -1},
                        {u'name': u'last_change_ua_eq_user', u'value': -1},
                    ],
                    [
                        {u'name': u'last_change_ip_first_auth_depth', u'value': -1},
                        {u'name': u'last_change_subnet_first_auth_depth', u'value': 0.0},
                        {u'name': u'last_change_ua_first_auth_depth', u'value': 0.0},
                    ],
                    [
                        {u'name': u'last_change_is_forced_change', u'value': -1},
                        {u'name': u'forced_change_pending', u'value': 1},
                    ],
                ],
            },
        )


@with_settings_hosts()
class RestoreAttemptViewVersionMultistep42TestCase(RestoreAttemptViewBaseTestCase):
    def test_form_updates(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        data_json = json.dumps(TEST_FACTORS_DATA_VERSION_MULTISTEP_42)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)

        eq_(
            resp['restore_attempt']['extra_info'],
            {
                u'is_current_version': False,
                u'version': u'multistep.4.2',
                u'restore_status': u'pending',
                u'is_for_learning': False,
                u'request_source': u'restore',
                u'contact_email': u'vasia@пупкин.рф',
            },
        )

        eq_(
            resp['restore_attempt']['events_info'],
            {
                u'aggregated': {
                    u'personal_and_recovery_change_one_day': {
                        u'matches': [
                            {
                                u'envs': [
                                    {
                                        u'subnet': u'5.45.192.0/18',
                                        u'datetime': u'1970-01-01 03:16:40',
                                        u'ip': u'5.45.207.254',
                                        u'subnet_first_auth_info': u'1970-01-01',
                                        u'entity': u'name',
                                        u'ua_first_auth_info': None,
                                        u'ua': u'yandexuid: 123',
                                        u'ip_first_auth_info': u'1970-01-01',
                                    },
                                    {
                                        u'subnet': u'5.45.192.0/18',
                                        u'datetime': u'1970-01-01 03:16:40',
                                        u'ip': u'5.45.207.254',
                                        u'subnet_first_auth_info': u'1970-01-01',
                                        u'entity': u'phone_number',
                                        u'ua_first_auth_info': None,
                                        u'ua': u'yandexuid: 123',
                                        u'ip_first_auth_info': u'1970-01-01',
                                    },
                                ],
                                u'fields': [u'ip', u'subnet'],
                            },
                            {
                                u'envs': [
                                    {
                                        u'subnet': None,
                                        u'datetime': u'1970-01-01 03:16:40',
                                        u'ip': u'192.168.0.1',
                                        u'subnet_first_auth_info': None,
                                        u'entity': u'birthday',
                                        u'ua_first_auth_info': u'1970-01-01',
                                        u'ua': u'os.name: windows xp, browser.name: firefox, yandexuid: yandexuid',
                                        u'ip_first_auth_info': None,
                                    },
                                    {
                                        u'subnet': None,
                                        u'datetime': u'1970-01-01 03:16:40',
                                        u'ip': u'10.10.10.10',
                                        u'subnet_first_auth_info': None,
                                        u'entity': u'answer',
                                        u'ua_first_auth_info': u'1970-01-01',
                                        u'ua': u'os.name: windows xp, browser.name: firefox, yandexuid: yandexuid',
                                        u'ip_first_auth_info': None,
                                    },
                                ],
                                u'fields': [u'ua'],
                            },
                        ],
                        u'factor': [
                            [
                                {u'name': u'ip_match', u'value': 0},
                                {u'name': u'subnet_match', u'value': 1},
                                {u'name': u'ua_match', u'value': 1},
                            ],
                            [
                                {u'name': u'ip_eq_user', u'value': 1},
                                {u'name': u'subnet_eq_user', u'value': 0},
                                {u'name': u'ua_eq_user', u'value': 1},
                            ],
                            [
                                {u'name': u'ip_eq_reg', u'value': -1},
                                {u'name': u'subnet_eq_reg', u'value': -1},
                                {u'name': u'ua_eq_reg', u'value': 0},
                            ],
                            [
                                {u'name': u'ip_first_auth_depth', u'value': u'1.0, 0.8, -1, -1'},
                                {u'name': u'subnet_first_auth_depth', u'value': u'1.0, -1, -1, -1'},
                                {u'name': u'ua_first_auth_depth', u'value': u'1.0, -1, -1, -1'},
                            ],
                        ],
                    },
                },
                u'passwords': {
                    u'change_envs': [
                        {
                            u'ip_first_auth_date': u'1970-01-01',
                            u'datetime': u'1970-01-01 03:16:40 MSK+0300',
                            u'user_ip': u'5.45.207.254',
                            u'user_agent': u'yandexuid/yandexuid',
                            u'subnet_first_auth_date': u'1970-01-01',
                            u'position': u'Last',
                            u'ua_first_auth_date': u'1970-01-01',
                        },
                    ],
                    u'factor': [
                        [
                            {u'name': u'change_count', u'value': 0},
                            {u'name': u'change_depth', u'value': u'-1'},
                        ],
                        [
                            {u'name': u'change_ip_eq_user', u'value': u'-1'},
                            {u'name': u'change_subnet_eq_user', u'value': u'-1'},
                            {u'name': u'change_ua_eq_user', u'value': u'-1'},
                        ],
                        [
                            {u'name': u'change_ip_first_auth_depth', u'value': u'-1'},
                            {u'name': u'change_subnet_first_auth_depth', u'value': u'0.0'},
                            {u'name': u'change_ua_first_auth_depth', u'value': u'0.0'},
                        ],
                        [
                            {u'name': u'last_change_is_forced_change', u'value': -1},
                            {u'name': u'forced_change_pending', u'value': 1},
                        ],
                    ],
                },
                u'recovery_changes': {
                    u'answer': {
                        u'change_indices': [-3, -2, -1],
                        u'change_envs': [
                            {
                                u'user_ip': u'5.45.207.254',
                                u'position': u'Third-to-last',
                                u'user_agent': u'yandexuid/123',
                                u'datetime': u'1970-01-01 03:00:03 MSK+0300',
                            },
                            {
                                u'user_ip': u'5.45.207.254',
                                u'position': u'Next-to-last',
                                u'user_agent': u'yandexuid/123',
                                u'datetime': u'1970-01-01 03:00:04 MSK+0300',
                            },
                            {
                                u'user_ip': u'5.45.207.254',
                                u'position': u'Last',
                                u'user_agent': u'yandexuid/123',
                                u'datetime': u'1970-01-01 03:00:06 MSK+0300',
                            },
                        ],
                        u'factor': [
                            [
                                {u'name': u'change_count', u'value': 3},
                                {u'name': u'change_depth', u'value': u'-1, -1, -1'},
                            ],
                            [
                                {u'name': u'change_ip_eq_user', u'value': u'1, 1, 1'},
                                {u'name': u'change_subnet_eq_user', u'value': u'1, 1, 1'},
                                {u'name': u'change_ua_eq_user', u'value': u'0, 0, 0'},
                            ],
                        ],
                    },
                    u'phone_numbers': {
                        u'change_indices': [-3, -2, -1],
                        u'change_envs': [
                            {
                                u'user_ip': u'5.45.207.254',
                                u'position': u'Third-to-last',
                                u'user_agent': u'yandexuid/123',
                                u'datetime': u'1970-01-01 03:00:01 MSK+0300',
                            },
                            {
                                u'user_ip': u'5.45.207.254',
                                u'position': u'Next-to-last',
                                u'user_agent': u'yandexuid/123',
                                u'datetime': u'1970-01-01 03:00:02 MSK+0300',
                            },
                            {
                                u'user_ip': u'5.45.207.254',
                                u'position': u'Last',
                                u'user_agent': u'yandexuid/123',
                                u'datetime': u'1970-01-01 03:00:04 MSK+0300',
                            },
                        ],
                        u'factor': [
                            [
                                {u'name': u'change_count', u'value': 2},
                                {u'name': u'change_depth', u'value': u'-1, 1, 1'},
                            ],
                            [
                                {u'name': u'change_ip_eq_user', u'value': u'-1, 1, 1'},
                                {u'name': u'change_subnet_eq_user', u'value': u'-1, 1, 1'},
                                {u'name': u'change_ua_eq_user', u'value': u'-1, 0, 0'},
                            ],
                        ],
                    },
                },
            },
        )

        eq_(
            resp['restore_attempt']['data']['names'],
            {
                u'changes_info': {
                    u'change_indices': [0, -2, -1],
                    u'change_envs': [
                        {
                            u'user_ip': u'5.45.207.1',
                            u'position': u'First',
                            u'user_agent': u'yandexuid/123',
                            u'datetime': u'1970-01-01 03:00:02 MSK+0300',
                        },
                    ],
                    u'factor': [
                        [
                            {u'name': u'change_count', u'value': 1},
                            {u'name': u'change_depth', u'value': u'1.0, -1, 1.0'},
                        ],
                        [
                            {u'name': u'change_ip_eq_user', u'value': u'0, -1, 0'},
                            {u'name': u'change_subnet_eq_user', u'value': u'1, -1, 1'},
                            {u'name': u'change_ua_eq_user', u'value': u'0, -1, 0'},
                        ],
                        [
                            {u'name': u'change_ip_eq_reg', u'value': u'0, -1, 0'},
                            {u'name': u'change_subnet_eq_reg', u'value': u'1, -1, 1'},
                            {u'name': u'change_ua_eq_reg', u'value': u'3, -1, 3'},
                        ],
                        [
                            {u'name': u'intermediate_depth', u'value': -1},
                        ],
                    ],
                },
                u'errors': {u'historydb_api_events_status': True},
                u'factors': {
                    u'current_lastname': u'no_match',
                    u'registration_firstname': u'no_match',
                    u'registration_lastname': u'no_match',
                    u'intermediate_firstname': u'not_calculated',
                    u'current_firstname': u'no_match',
                    u'intermediate_lastname': u'not_calculated',
                },
                u'factors_summary': u'no_match',
                u'incoming': [u'A B', u'A P'],
                u'indices': {u'current': [[0, 1], 1], u'intermediate': None, u'registration': [[0, 1], 0]},
                u'trusted': [
                    u'\u041f\u0435\u0442\u0440 \u041f\u0435\u0442\u0440\u043e\u0432',
                    u'\u041f\u0435\u0442\u0440 Petroff',
                ],
                u'trusted_intervals': [
                    [
                        {
                            u'start': {u'user_ip': u'5.45.207.254', u'timestamp': 1, u'yandexuid': u'123', u'datetime': u'1970-01-01 03:00:01 MSK+0300'},
                            u'end': {u'user_ip': u'5.45.207.1', u'timestamp': 2, u'yandexuid': u'123', u'datetime': u'1970-01-01 03:00:02 MSK+0300'},
                        },
                    ],
                    [
                        {
                            u'start': {u'user_ip': u'5.45.207.1', u'timestamp': 2, u'yandexuid': u'123', u'datetime': u'1970-01-01 03:00:02 MSK+0300'},
                            u'end': None,
                        },
                    ],
                ],
            },
        )

        eq_(
            resp['restore_attempt']['data']['birthday'],
            {
                u'changes_info': {
                    u'change_indices': [0, -2, -1],
                    u'change_envs': [
                        {
                            u'user_ip': None,
                            u'position': u'First',
                            u'datetime': None,
                        },
                    ],
                    u'factor': [
                        [
                            {u'name': u'change_count', u'value': 1},
                            {u'name': u'change_depth', u'value': u'-1, -1, -1'},
                        ],
                        [
                            {u'name': u'change_ip_eq_user', u'value': u'-1, -1, -1'},
                            {u'name': u'change_subnet_eq_user', u'value': u'-1, -1, -1'},
                            {u'name': u'change_ua_eq_user', u'value': u'0, -1, 0'},
                        ],
                        [
                            {u'name': u'change_ip_eq_reg', u'value': u'-1, -1, -1'},
                            {u'name': u'change_subnet_eq_reg', u'value': u'-1, -1, -1'},
                            {u'name': u'change_ua_eq_reg', u'value': u'0, -1, 0'},
                        ],
                        [
                            {u'name': u'intermediate_depth', u'value': -1},
                        ],
                    ],
                },
                u'errors': {u'historydb_api_events_status': True},
                u'factors': {u'current': u'match', u'intermediate': u'not_calculated', u'registration': u'inexact_match'},
                u'factors_summary': u'match',
                u'incoming': [u'2012-01-01'],
                u'indices': {u'current': 1, u'intermediate': None, u'registration': 0},
                u'trusted': [u'2011-11-11', u'2000-10-01'],
                u'trusted_intervals': [
                    [
                        {
                            u'start': {u'user_ip': u'5.45.207.254', u'timestamp': 1, u'yandexuid': u'123', u'datetime': u'1970-01-01 03:00:01 MSK+0300'},
                            u'end': {u'timestamp': None, u'datetime': None},
                        },
                    ],
                    [
                        {u'start': {u'timestamp': None, u'datetime': None}, u'end': None},
                    ],
                ],
            },
        )

        eq_(
            resp['restore_attempt']['data']['phone_numbers']['changes_info'],
            {
                u'change_envs': [
                    {
                        u'user_ip': u'5.45.207.254',
                        u'position': u'Second',
                        u'user_agent': u'yandexuid/123',
                        u'datetime': u'1970-01-01 03:00:02 MSK+0300',
                    },
                    {
                        u'user_ip': u'5.45.207.254',
                        u'position': u'Second',
                        u'user_agent': u'yandexuid/123',
                        u'datetime': u'1970-01-01 03:00:04 MSK+0300',
                    },
                ],
                u'factor': [
                    [
                        {u'name': u'match_ip_eq_user', u'value': u'1, 1'},
                        {u'name': u'match_subnet_eq_user', u'value': u'1, 1'},
                        {u'name': u'match_ua_eq_user', u'value': u'0, 0'},
                    ],
                    [
                        {u'name': u'match_ip_eq_reg', u'value': u'-1, -1'},
                        {u'name': u'match_subnet_eq_reg', u'value': u'-1, -1'},
                        {u'name': u'match_ua_eq_reg', u'value': u'0, 0'},
                    ],
                    [
                        {u'name': u'match_ip_first_auth_depth', u'value': u'-1, -1'},
                        {u'name': u'match_subnet_first_auth_depth', u'value': u'-1, -1'},
                        {u'name': u'match_ua_first_auth_depth', u'value': u'-1, -1'},
                    ],
                    [
                        {u'name': u'match_depth', u'value': u'1.0, 1.0'},
                    ],
                ],
            },
        )

        eq_(
            resp['restore_attempt']['data']['answer']['changes_info'],
            {
                u'change_envs': [
                    {
                        u'user_ip': u'5.45.207.254',
                        u'position': u'Second',
                        u'user_agent': u'yandexuid/123',
                        u'datetime': u'1970-01-01 03:00:04 MSK+0300',
                    },
                ],
                u'factor': [
                    [
                        {u'name': u'match_ip_eq_user', u'value': u'0, 1'},
                        {u'name': u'match_subnet_eq_user', u'value': u'1, 1'},
                        {u'name': u'match_ua_eq_user', u'value': u'0, 3'},
                    ],
                    [
                        {u'name': u'match_ip_eq_reg', u'value': u'-1, -1'},
                        {u'name': u'match_subnet_eq_reg', u'value': u'-1, -1'},
                        {u'name': u'match_ua_eq_reg', u'value': u'0, 0'},
                    ],
                    [
                        {u'name': u'match_ip_first_auth_depth', u'value': u'-1, 0.7'},
                        {u'name': u'match_subnet_first_auth_depth', u'value': u'-1, 1.0'},
                        {u'name': u'match_ua_first_auth_depth', u'value': u'0.0, -1'},
                    ],
                    [
                        {u'name': u'match_depth', u'value': u'1.0, 1.0'},
                    ],
                ],
            },
        )

    def test_attempt_answer_masked(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='support'))
        data_json = json.dumps(TEST_FACTORS_DATA_VERSION_MULTISTEP_42)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())

        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)
        # данные в incoming и trusted замаскированы
        eq_(
            resp['restore_attempt']['data']['answer']['incoming'],
            [
                {u'answer': u'*****', u'question': u'99:my question'},
            ],
        )
        eq_(
            resp['restore_attempt']['data']['answer']['trusted'],
            [u'*****', u'*****', u'*****'],
        )


@with_settings_hosts()
class RestoreAttemptViewVersionMultistep43TestCase(RestoreAttemptViewBaseTestCase):
    def test_version_and_passwords_data(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='support'))
        data_json = json.dumps(TEST_FACTORS_DATA_VERSION_MULTISTEP_43)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(
                restore_events=[
                    event_restore_item(
                        restore_id=TEST_RESTORE_ID,
                        data_json=data_json,
                    ),
                ],
            ),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())

        eq_(resp.status_code, 200)
        resp = json.loads(resp.data)
        eq_(
            resp['restore_attempt']['data']['passwords']['factors'],
            {
                u'first_auth_depth_0': -1,
                u'first_auth_depth_1': -1,
                u'first_auth_depth_2': -1,
                u'auth_date_0': u'not_calculated',
                u'auth_date_1': u'not_calculated',
                u'auth_date_2': u'not_calculated',
                u'equals_current_0': u'no_match',
                u'equals_current_1': u'not_calculated',
                u'equals_current_2': u'not_calculated',
                u'auth_found_0': u'no_match',
                u'auth_found_1': u'not_calculated',
                u'auth_found_2': u'not_calculated',
            },
        )
        eq_(
            resp['restore_attempt']['extra_info'],
            {
                u'is_current_version': True,
                u'version': u'multistep.4.3',
                u'restore_status': u'pending',
                u'is_for_learning': False,
                u'request_source': u'restore',
                u'contact_email': u'vasia@пупкин.рф',
            },
        )
