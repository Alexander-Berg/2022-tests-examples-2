# -*- coding: utf-8 -*-
from datetime import datetime
import json

import mock
from mock import Mock
from nose.tools import (
    eq_,
    istest,
    ok_,
)
from passport.backend.api import legacy
from passport.backend.api.test.mock_objects import (
    mock_frodobox_karma,
    mock_headers,
    mock_statbox_account_modification_entries,
)
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_requested
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_get_hosts_response,
    blackbox_loginoccupation_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.frodo.utils import get_password_metadata
from passport.backend.core.builders.mail_apis.faker import husky_delete_user_response
from passport.backend.core.dbmanager.manager import DBError
from passport.backend.core.eav_type_mapping import (
    ALIAS_NAME_TO_TYPE as ALT,
    ATTRIBUTE_NAME_TO_TYPE as AT,
)
from passport.backend.core.frodo.exceptions import FrodoError
from passport.backend.core.models.account import ACCOUNT_DISABLED
from passport.backend.core.models.mailhost import MailHost
from passport.backend.core.models.password import (
    PASSWORD_ENCODING_VERSION_MD5_CRYPT,
    PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
)
from passport.backend.core.suggest.login_suggester import LoginSuggester
from passport.backend.core.test.data import (
    TEST_IMPOSSIBLE_PASSWORD,
    TEST_SERIALIZED_PASSWORD,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.gender import Gender
from passport.backend.utils.string import smart_text
from six import string_types


TEST_HOST = 'passport-internal.yandex.ru'


@with_settings_hosts(
    OAUTH_URL='http://localhost/',
    OAUTH_RETRIES=5,
    HUSKY_API_URL='http://localhost/',
    HUSKY_API_TIMEOUT=1,
    HUSKY_API_RETRIES=1,
)
class LegacyAdmSubscribeTestCase(BaseTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_subscribe_with_0_uid_error(self):
        blackbox_response = blackbox_userinfo_response(uid=None)
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(
            mock_grants(consumer='fotki', grants={'subscription': {'fotki': '*'}}),
        )
        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={
                'uid': 0,
                'from': 'fotki',
            },
        )

        self.check_xml_output(
            rv.data,
            {'page': {'error': 'unknownuid', 'message': u'Пользователь с таким UID не найден.'}},
            {'job': 'rejected'},
        )

    def test_subscribe_impossible_error(self):
        blackbox_response = blackbox_userinfo_response(uid=1)
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(
            mock_grants(consumer='passport', grants={'subscription': ['*']}),
        )
        for sid in [70, 74, 79, 82]:
            rv = self.env.client.get(
                path='/passport/admsubscribe',
                query_string={
                    'uid': 1,
                    'sid': sid,
                    'from': 'passport',
                },
            )

            self.check_xml_output(
                rv.data,
                {
                    'page': {
                        'error': 'interr',
                        'message': u'Подписка на данный сид невозможна',
                        'mode': 'subscribe',
                    },
                },
                {'job': 'rejected'},
            )

    def test_subscribe_ok(self):
        blackbox_response = blackbox_userinfo_response(login='test', unsubscribed_from=[5])
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(
            mock_grants(consumer='fotki', grants={'subscription': {'fotki': '*'}}),
        )
        self.env.db.serialize(blackbox_response)
        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={
                'uid': 1,
                'from': 'fotki',
            },
        )

        self.check_xml_output(
            rv.data,
            {'page': {'status': 'ok', 'uid': '1', 'mode': 'subscribe', 'sid': '5'}},
            {'job': 'accepted'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'subscription.5', '1', uid=1, db='passportdbshard1')

        names_values = {'action': 'admsubscribe', 'sid.add': '5', 'from': 'fotki'}
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_subscribe_to_galatasaray(self):
        blackbox_response = blackbox_userinfo_response(login='test')
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='galatasaray', grants={'subscription': {'galatasaray': '*'}},
        ))
        self.env.db.serialize(blackbox_response)
        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={
                'uid': 1,
                'from': 'galatasaray',
            },
        )

        self.check_xml_output(
            rv.data,
            {'page': {'status': 'ok', 'uid': '1', 'mode': 'subscribe', 'sid': '61'}},
            {'job': 'accepted'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 1)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        self.env.db.check('aliases', 'altdomain', '1/test', uid=1, db='passportdbcentral')

        names_values = {
            'action': 'admsubscribe',
            'alias.altdomain.add': '1/test',
            'from': 'galatasaray',
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_subscribe_to_galatasaray_error(self):
        """Запрещена подписка на sid=61 для не-нормалов"""
        blackbox_response = blackbox_userinfo_response(
            login='test@mk.ru',
            aliases={
                'lite': 'test@mk.ru',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='galatasaray', grants={'subscription': {'galatasaray': '*'}},
        ))
        self.env.db.serialize(blackbox_response)
        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={
                'uid': 1,
                'from': 'galatasaray',
            },
        )

        self.check_xml_output(
            rv.data,
            {
                'page': {
                    'error': 'interr',
                    'mode': 'subscribe',
                    'message': u'Подписка на данный сид невозможна для пользователя с uid 1',
                },
            },
            {'job': 'rejected'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        self.env.db.check_missing('aliases', 'altdomain', uid=1, db='passportdbcentral')

    def test_subscribe_to_galatasaray_already_subscribed_ok(self):
        """Уже есть подписка на sid=61"""
        userinfo_response = blackbox_userinfo_response(
            login='test',
            aliases={
                'portal': 'test',
                'altdomain': 'foo@galatasaray.net',
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='galatasaray', grants={'subscription': {'galatasaray': '*'}},
        ))
        self.env.db.serialize(userinfo_response)

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={
                'uid': 1,
                'from': 'galatasaray',
            },
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        self.check_xml_output(
            rv.data,
            {'page': {'status': 'nothingtodo', 'uid': '1', 'sid': '61', 'mode': 'subscribe'}},
            {'job': 'accepted'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        # ничего не делали - в лог ничего не писали
        self.assert_events_are_logged(self.env.handle_mock, {})

    def test_unsubscribe_galatasaray(self):
        """
        Молча не отписываем
        """
        blackbox_response = blackbox_userinfo_response(
            aliases={
                'portal': 'test',
                'altdomain': 'test@galatasaray.net',
            },
        )

        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='yastaff', grants={'subscription': {'galatasaray': ['*']}},
        ))
        self.env.db.serialize(blackbox_response)

        self.env.db.check('aliases', 'altdomain', '1/test', uid=1, db='passportdbcentral')

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={
                'uid': 1,
                'from': 'galatasaray',
                'unsubscribe': True,
            },
        )
        self.check_xml_output(
            rv.data,
            {
                'page': {
                    'status': 'ok',
                    'uid': '1',
                    'sid': '61',
                    'mode': 'unsubscribe',
                },
            },
            {
                'job': 'accepted',
            },
        )

        self.assert_events_are_empty(self.env.handle_mock)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.env.db.check('aliases', 'altdomain', '1/test', uid=1, db='passportdbcentral')
        self.env.db.check_missing('removed_aliases', 'altdomain', uid=1, db='passportdbcentral')

    def test_unsubscribe_pdd_from_mail(self):
        blackbox_response = blackbox_userinfo_response(
            login='test@okna.ru',
            aliases={
                'pdd': 'test@okna.ru',
            },
            subscribed_to=[2],
        )

        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='mail', grants={'subscription': {'mail': ['*']}},
        ))
        self.env.db.serialize(blackbox_response)

        self.env.db.check('aliases', 'pdd', '1234/test', uid=1, db='passportdbcentral')

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={
                'uid': 1,
                'from': 'mail',
                'unsubscribe': True,
            },
        )
        self.check_xml_output(
            rv.data,
            {'page': {'mode': 'unsubscribe', 'error': 'badsid'}},
            {'job': 'rejected'},
            skip_elements=['message'],
        )

        self.assert_events_are_empty(self.env.handle_mock)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

    def test_unsubscribe_portal_with_pdd_alias_from_mailpro(self):
        blackbox_response = blackbox_userinfo_response(
            login='test@okna.ru',
            aliases={
                'portal': 'test',
                'pdd': 'test@okna.ru',
            },
            subscribed_to=[122],
        )

        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='mail', grants={'subscription': {'mailpro': ['*']}},
        ))
        self.env.db.serialize(blackbox_response)

        self.env.db.check('aliases', 'pdd', '1234/test', uid=1, db='passportdbcentral')

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={
                'uid': 1,
                'from': 'mailpro',
                'unsubscribe': True,
            },
        )
        self.check_xml_output(
            rv.data,
            {
                'page': {
                    'status': 'ok',
                    'uid': '1',
                    'sid': '122',
                    'mode': 'unsubscribe',
                },
            },
            {
                'job': 'accepted',
            },
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

        names_values = {'action': 'admsubscribe', 'sid.rm': '122|test', 'from': 'mailpro'}
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_admsubscribe_wwwdgt(self):
        blackbox_response = blackbox_userinfo_response(
            unsubscribed_from=[42], dbfields={'subscription.host_id.42': ''},
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='wwwdgt', grants={'subscription': {'wwwdgt': ['*']}},
        ))
        self.env.db.serialize(blackbox_response)
        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={
                'uid': 1,
                'from': 'wwwdgt',
                'wmode': 10,
            },
        )

        self.check_xml_output(
            rv.data,
            {'page': {'status': 'ok', 'uid': '1', 'mode': 'subscribe', 'sid': '42'}},
            {'job': 'accepted'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'subscription.wwwdgt.mode', '10', uid=1, db='passportdbshard1')

        names_values = {'action': 'admsubscribe', 'sid.add': '42', 'sid.wwwdgt_wmode': '10', 'from': 'wwwdgt'}
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_subscribe_wwwdgt_existing_subscription(self):
        blackbox_response = blackbox_userinfo_response(
            subscribed_to=[42],
            dbfields={
                'subscription.host_id.42': '2',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(
            mock_grants(consumer='wwwdgt', grants={'subscription': {'wwwdgt': ['*']}}),
        )

        self.env.db.serialize(blackbox_response)

        self.env.db.check('attributes', 'subscription.wwwdgt.mode', '2', uid=1, db='passportdbshard1')

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={
                'uid': 1,
                'from': 'wwwdgt',
                'wmode': 10,
            },
        )

        self.check_xml_output(
            rv.data,
            {'page': {'status': 'ok', 'uid': '1', 'mode': 'subscribe', 'sid': '42'}},
            {'job': 'accepted'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'subscription.wwwdgt.mode', '10', uid=1, db='passportdbshard1')

        names_values = {'action': 'admsubscribe', 'sid.add': '42', 'sid.wwwdgt_wmode': '10', 'from': 'wwwdgt'}
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_admsubscribe_yastaff(self):
        def blackbox_request(method, url, data=None, headers=None, cookies=None):
            if data and data.get('sid') == 669:
                return Mock(content=blackbox_userinfo_response(uid=None), status_code=200)
            else:
                return Mock(content=blackbox_userinfo_response(unsubscribed_from=[669]), status_code=200)

        self.env.blackbox.set_blackbox_response_side_effect('userinfo', blackbox_request)
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='yastaff', grants={'subscription': {'yastaff': ['*']}},
        ))
        self.env.db.serialize(blackbox_request('GET', '').content)

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={
                'uid': 1,
                'from': 'yastaff',
                'yastaff_login': 'foo',
            },
        )

        self.check_xml_output(
            rv.data,
            {'page': {'status': 'ok', 'uid': '1', 'mode': 'subscribe', 'sid': '669'}},
            {'job': 'accepted'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 1)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.env.db.check('aliases', 'yandexoid', 'foo', uid=1, db='passportdbcentral')

        names_values = {
            'action': 'admsubscribe',
            'alias.yandexoid.add': 'foo',
            'from': 'yastaff',
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_admsubscribe_unsubscribe_yastaff(self):
        blackbox_response = blackbox_userinfo_response(
            aliases={
                'portal': 'test',
                'yandexoid': 'yastaff_login',
            },
        )

        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='yastaff', grants={'subscription': {'yastaff': ['*']}},
        ))
        self.env.db.serialize(blackbox_response)

        self.env.db.check('aliases', 'yandexoid', 'yastaff_login', uid=1, db='passportdbcentral')

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={
                'uid': 1,
                'from': 'yastaff',
                'unsubscribe': True,
            },
        )
        self.check_xml_output(
            rv.data,
            {
                'page': {
                    'status': 'ok',
                    'uid': '1',
                    'sid': '669',
                    'mode': 'unsubscribe',
                },
            },
            {
                'job': 'accepted',
            },
        )
        names_values = {
            'action': 'admsubscribe',
            'alias.yandexoid.rm': 'yastaff_login',
            'from': 'yastaff',
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.env.db.check_missing('aliases', 'yandexoid', uid=1, db='passportdbcentral')
        self.env.db.check('removed_aliases', 'yandexoid', 'yastaff_login', uid=1, db='passportdbcentral')

    def test_admsubscribe_yastaff_login_occupied(self):
        blackbox_response = blackbox_userinfo_response()
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='yastaff', grants={'subscription': {'yastaff': ['*']}},
        ))
        self.env.db.serialize(blackbox_response)
        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={
                'uid': 1,
                'from': 'yastaff',
                'yastaff_login': 'foo',
            },
        )

        self.check_xml_output(
            rv.data,
            {'page': {'mode': 'subscribe', 'error': 'occupied'}},
            {'job': 'rejected'},
            skip_elements=['message'],
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

    def test_admsubscribe_mail_without_narodmail(self):
        blackbox_response = blackbox_userinfo_response(
            login='test', unsubscribed_from=[2, 16],
            dbfields={
                'subscription.host_id.16': '',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        self.env.grants.set_grants_return_value(mock_grants(consumer='mail', grants={'subscription': {'mail': ['*']}}))
        self.env.db.serialize(blackbox_response)

        self.env.db.check('aliases', 'portal', 'test', uid=1, db='passportdbcentral')

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={
                'uid': 1,
                'login': 'mail-login',
                'from': 'mail',
            },
        )

        self.check_xml_output(
            rv.data,
            {'page': {'status': 'ok', 'uid': '1', 'sid': '2', 'mode': 'subscribe'}},
            {'job': 'accepted'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('suid2', 'suid', 1, uid=1, db='passportdbcentral')
        # Почтовый логин совпадает с portal => aliases.mail не создается
        self.env.db.check_missing('aliases', 'mail', uid=1, db='passportdbcentral')
        self.env.db.check_missing('attributes', 'subscription.mail.login_rule', uid=1, db='passportdbshard1')

        names_values = {
            'action': 'admsubscribe',
            'sid.add': '2',
            'from': 'mail',
            'mail.add': '1',
            'info.mail_status': '1',
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_admsubscribe_unsubscribe_mail_without_narodmail(self):
        blackbox_response = blackbox_userinfo_response(
            subscribed_to=[2], unsubscribed_from=[16],
            dbfields={
                'subscription.login.2': 'mail_login',
                'subscription.suid.2': '999',
                'subscription.host_id.16': '',
            },
            attributes={
                'subscription.mail.status': '1',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.husky_api.set_response_value('delete_user', husky_delete_user_response())
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='mail', grants={'subscription': {'mail': ['*']}},
        ))

        self.env.db.serialize(blackbox_response)
        self.env.db.insert('aliases', uid=1, type=ALT['mail'], value='mail_login', db='passportdbcentral')

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={
                'uid': 1,
                'from': 'mail',
                'unsubscribe': True,
            },
        )
        self.check_xml_output(
            rv.data,
            {
                'page': {
                    'status': 'ok',
                    'uid': '1',
                    'sid': '2',
                    'mode': 'unsubscribe',
                },
            },
            {
                'job': 'accepted',
            },
        )
        names_values = {
            'action': 'admsubscribe',
            'sid.rm': '2|mail_login',
            'from': 'mail',
            'sid.rm.info': '1|mail_login|999',
            'mail.rm': '999',
            'info.mail_status': '-',
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

        eq_(self.env.db.query_count('passportdbcentral'), 3)  # -suid2 -aliases +removed_aliases
        eq_(self.env.db.query_count('passportdbshard1'), 1)  # -attributes
        self.env.db.check_missing('aliases', 'mail', uid=1, db='passportdbcentral')
        self.env.db.check('removed_aliases', 'mail', 'mail_login', uid=1, db='passportdbcentral')
        self.env.db.check_missing('suid2', 'suid', uid=1, db='passportdbcentral')
        self.env.db.check_missing('attributes', 'subscription.mail.login_rule', uid=1, db='passportdbshard1')
        eq_(len(self.env.husky_api.requests), 1)

    def test_admsubscribe_unsubscribe_mail_with_narodmail(self):
        blackbox_response = blackbox_userinfo_response(
            subscribed_to=[2, 16],
            dbfields={
                'subscription.suid.2': '999',
                'subscription.login.2': 'mail_login',
                'subscription.host_id.16': '7',
                'subscription.login.16': 'narodmail_login',
            },
            attributes={
                'subscription.mail.status': '1',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.husky_api.set_response_value('delete_user', husky_delete_user_response())
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='mail', grants={'subscription': {'mail': ['*']}},
        ))

        self.env.db.serialize(blackbox_response)
        self.env.db.insert(
            'aliases',
            uid=1,
            type=ALT['mail'],
            surrogate_type=str(ALT['mail']),
            value='mail_login',
            db='passportdbcentral',
        )
        self.env.db.insert(
            'aliases',
            uid=1,
            type=ALT['narodmail'],
            surrogate_type=str(ALT['narodmail']),
            value='narodmail_login',
            db='passportdbcentral',
        )
        self.env.db.check('suid2', 'suid', 999, uid=1, db='passportdbcentral')

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={
                'uid': 1,
                'from': 'mail',
                'unsubscribe': True,
            },
        )
        self.check_xml_output(
            rv.data,
            {
                'page': {
                    'status': 'ok',
                    'uid': '1',
                    'sid': '2',
                    'mode': 'unsubscribe',
                },
            },
            {
                'job': 'accepted',
            },
        )
        names_values = {
            'action': 'admsubscribe',
            'sid.rm': '16|narodmail_login,2|mail_login',
            'from': 'mail',
            'sid.rm.info': '1|mail_login|999',
            'mail.rm': '999',
            'info.mail_status': '-',
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

        eq_(self.env.db.query_count('passportdbcentral'), 3)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check_missing('aliases', 'mail', uid=1, db='passportdbcentral')
        self.env.db.check_missing('aliases', 'narodmail', uid=1, db='passportdbcentral')
        self.env.db.check('removed_aliases', 'mail', 'mail_login', uid=1, db='passportdbcentral')
        self.env.db.check('removed_aliases', 'narodmail', 'narodmail_login', uid=1, db='passportdbcentral')
        self.env.db.check_missing('attributes', 'subscription.mail.login_rule', uid=1, db='passportdbshard1')
        eq_(len(self.env.husky_api.requests), 1)

    def test_subscribe_pdd_sid_ok_with_uid_instead_login(self):
        uid = self.env.TEST_PDD_UID
        blackbox_response = blackbox_userinfo_response(
            uid=uid,
            login='test@okna.ru',
            aliases={
                'pdd': 'test@okna.ru',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='lenta', grants={'subscription': {'lenta': ['*']}},
        ))
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={
                'uid': self.env.TEST_PDD_UID,
                'from': 'lenta',
            },
        )

        eq_(rv.status_code, 200)
        self.check_xml_output(
            rv.data,
            {'page': {'status': 'ok', 'uid': str(uid), 'sid': '23', 'mode': 'subscribe'}},
            {'job': 'accepted'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard2'), 1)
        self.env.db.check('attributes', 'subscription.23', '1', uid=uid, db='passportdbshard2')

        names_values = {'action': 'admsubscribe', 'sid.add': '23', 'from': 'lenta'}
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_subscribe_pdd_mobilemusic(self):
        uid = self.env.TEST_PDD_UID
        blackbox_response = blackbox_userinfo_response(
            uid=uid,
            login='test@okna.ru',
            aliases={
                'pdd': 'test@okna.ru',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='mobilemusic',
                grants={'subscription': {'mobilemusic': ['*']}},
            ),
        )
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={
                'uid': self.env.TEST_PDD_UID,
                'from': 'mobilemusic',
            },
        )

        eq_(rv.status_code, 200)
        self.check_xml_output(
            rv.data,
            {'page': {'status': 'ok', 'uid': str(uid), 'sid': '78', 'mode': 'subscribe'}},
            {'job': 'accepted'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard2'), 1)
        self.env.db.check('attributes', 'subscription.78', '1', uid=uid, db='passportdbshard2')

        names_values = {'action': 'admsubscribe', 'sid.add': '78', 'from': 'mobilemusic'}
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_subscribe_pdd_sid_wrong(self):
        blackbox_response = blackbox_userinfo_response(
            uid=self.env.TEST_PDD_UID,
            login='test@okna.ru',
            aliases={
                'pdd': 'test@okna.ru',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='slova', grants={'subscription': {'slova': ['*']}},
        ))
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={
                'uid': self.env.TEST_PDD_UID,
                'from': 'slova',
            },
        )

        eq_(rv.status_code, 200)
        self.check_xml_output(
            rv.data,
            {
                'page': {
                    'error': 'badsid',
                    'mode': 'subscribe',
                    'message': u'Подписка запрещена для ПДД',
                },
            },
            {
                'job': 'rejected',
            },
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard2'), 0)

        self.assert_events_are_empty(self.env.handle_mock)

    def test_lite_sid_ok(self):
        blackbox_response = blackbox_userinfo_response(
            uid=1,
            login='test@okna.ru',
            aliases={
                'lite': 'test@okna.ru',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='disk', grants={'subscription': {'disk': ['*']}},
        ))
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={
                'uid': 1,
                'from': 'disk',
            },
        )

        eq_(rv.status_code, 200)
        self.check_xml_output(
            rv.data,
            {'page': {'status': 'ok', 'uid': '1', 'sid': '44', 'mode': 'subscribe'}},
            {'job': 'accepted'},
        )
        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'subscription.disk.login_rule', '1', uid=1, db='passportdbshard1')

        names_values = {'action': 'admsubscribe', 'sid.add': '44', 'from': 'disk'}
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_unknownlogin(self):
        blackbox_response = blackbox_userinfo_response(uid=None)
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='mail', grants={'subscription': {'mail': ['*']}},
        ))

        rv = self.env.client.get(path='/passport/admsubscribe',
                                 query_string={'login': 'login',
                                               'from': 'mail',
                                               },
                                 )
        self.check_xml_output(
            rv.data,
            {'page': {'error': 'unknownlogin',
                      'message': u'Пользователь с указанным логином не найден.'}},
            {'job': 'rejected'},
        )

    def test_sid_requires_login__ok(self):
        blackbox_response = blackbox_userinfo_response(login='test', unsubscribed_from=[5])
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(
            mock_grants(consumer='fotki', grants={'subscription': {'fotki': '*'}}),
        )
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={'uid': 1, 'from': 'fotki'},
        )

        self.check_xml_output(
            rv.data,
            {'page': {'status': 'ok', 'uid': '1', 'sid': '5', 'mode': 'subscribe'}},
            {'job': 'accepted'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

    def test_sid_requires_login_error(self):
        blackbox_response = blackbox_userinfo_response(
            login='',
            unsubscribed_from=[5],
            aliases={
                'social': 'uid-test',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(
            mock_grants(consumer='fotki', grants={'subscription': {'fotki': '*'}}),
        )
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={'uid': 1, 'from': 'fotki'},
        )

        self.check_xml_output(
            rv.data,
            {'page': {'mode': 'subscribe', 'error': 'accountwithloginrequired'}},
            {'job': 'rejected'},
            skip_elements=['message'],
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

    def test_with_bad_headers(self):
        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={'uid': 1, 'from': 'fotki'},
            headers=mock_headers('127.0.0.1,123.4.5.6'),
        )

        eq_(rv.status_code, 200)
        self.check_xml_output(
            rv.data,
            {'page': {'error': 'interror'}},
            {'job': 'rejected'},
            skip_elements=['message', 'text'],
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

    def test_sid_requires_login_with_lite_user(self):
        blackbox_response = blackbox_userinfo_response(
            uid=1,
            login='test@okna.ru',
            aliases={
                'lite': 'test@okna.ru',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(
            mock_grants(consumer='disk', grants={'subscription': {'mail': ['*']}}),
        )
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={'uid': 1, 'from': 'mail'},
        )

        eq_(rv.status_code, 200)
        self.check_xml_output(
            rv.data,
            {'page': {'mode': 'subscribe', 'error': 'accountwithloginrequired'}},
            {'job': 'rejected'},
            skip_elements=['message'],
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

    def test_sid_requires_login_with_social_user(self):
        blackbox_response = blackbox_userinfo_response(
            uid=1,
            login='',
            aliases={
                'social': 'uid-aasjf375',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        self.env.grants.set_grants_return_value(
            mock_grants(consumer='disk', grants={'subscription': {'mail': ['*']}}),
        )
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={'uid': 1, 'from': 'mail'},
        )

        eq_(rv.status_code, 200)
        self.check_xml_output(
            rv.data,
            {'page': {'mode': 'subscribe', 'error': 'accountwithloginrequired'}},
            {'job': 'rejected'},
            skip_elements=['message'],
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

    def test_sid_requires_password__ok(self):
        blackbox_response = blackbox_userinfo_response(
            login='test',
            unsubscribed_from=[27],
            attributes={'password.encrypted': '1:secret'},
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(
            mock_grants(consumer='jabber', grants={'subscription': {'jabber': '*'}}),
        )
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={'uid': 1, 'from': 'jabber'},
        )

        self.check_xml_output(
            rv.data,
            {'page': {'status': 'ok', 'uid': '1', 'sid': '27', 'mode': 'subscribe'}},
            {'job': 'accepted'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

    def test_sid_requires_password_error(self):
        blackbox_response = blackbox_userinfo_response(
            login='test',
            unsubscribed_from=[27],
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(
            mock_grants(consumer='jabber', grants={'subscription': {'jabber': '*'}}),
        )
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={'uid': 1, 'from': 'jabber'},
        )

        self.check_xml_output(
            rv.data,
            {'page': {'mode': 'subscribe', 'error': 'accountwithpasswordrequired'}},
            {'job': 'rejected'},
            skip_elements=['message'],
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

    def test_existing_subscription(self):
        blackbox_response = blackbox_userinfo_response(subscribed_to=[2])
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(
            mock_grants(consumer='jabber', grants={'subscription': {'mail': '*'}}),
        )
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={'uid': 1, 'from': 'mail'},
        )

        self.check_xml_output(
            rv.data,
            {'page': {'status': 'nothingtodo', 'uid': '1', 'sid': '2', 'mode': 'subscribe'}},
            {'job': 'accepted'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

    def test_admsubscribe_strongpwd_oauth_ok(self):
        timenow = TimeNow()
        blackbox_response = blackbox_userinfo_response(login='test.test', crypt_password='1:abc')
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(
            mock_grants(consumer='strongpwd', grants={'subscription': {'strongpwd': '*'}}),
        )
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={'uid': 1, 'from': 'strongpwd'},
        )

        self.check_xml_output(
            rv.data,
            {'page': {'status': 'ok', 'uid': '1', 'sid': '67', 'mode': 'subscribe'}},
            {'job': 'accepted'},
        )

        eq_(len(self.env.oauth.requests), 0)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'account.global_logout_datetime', timenow, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'subscription.67', '1', uid=1, db='passportdbshard1')

        names_values = {
            'action': 'admsubscribe',
            'sid.add': '67',
            'from': 'strongpwd',
            'info.glogout': TimeNow(),
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_admsubscribe_lite_login_with_unknownlogin(self):
        blackbox_response = blackbox_userinfo_response(
            uid=1,
            aliases={
                'lite': 'lite@okna.ru',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(
            mock_grants(consumer='disk', grants={'subscription': {'disk': ['*']}}),
        )
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={'login': 'lite@okna.ru', 'from': 'disk'},
        )

        eq_(rv.status_code, 200)

        self.check_xml_output(
            rv.data,
            {'page': {
                'error': 'unknownlogin',
                'message': u'Пользователь с указанным логином не найден.',
            }},
            {'job': 'rejected'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

    def test_admsubscribe_pdd_login_with_unknownlogin(self):
        blackbox_response = blackbox_userinfo_response(
            uid=self.env.TEST_PDD_UID,
            login='test@okna.ru',
            aliases={
                'pdd': 'test@okna.ru',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(
            mock_grants(consumer='lenta', grants={'subscription': {'lenta': ['*']}}),
        )
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={'login': 'test@okna.ru', 'from': 'lenta'},
        )

        eq_(rv.status_code, 200)
        self.check_xml_output(
            rv.data,
            {'page': {
                'error': 'unknownlogin',
                'message': u'Пользователь с указанным логином не найден.',
            }},
            {'job': 'rejected'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

    def test_admsubscribe_ya_login(self):
        blackbox_response = blackbox_userinfo_response(uid=1, login='test')
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(
            mock_grants(consumer='fotki', grants={'subscription': {'fotki': ['*']}}),
        )
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admsubscribe',
            query_string={
                'login': 'test@yandex.ru',
                'from': 'fotki',
            },
        )

        eq_(rv.status_code, 200)
        self.check_xml_output(
            rv.data,
            {'page': {'status': 'ok', 'uid': '1', 'sid': '5', 'mode': 'subscribe'}},
            {'job': 'accepted'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'subscription.fotki', '1', uid=1, db='passportdbshard1')

        names_values = {'action': 'admsubscribe', 'sid.add': '5', 'from': 'fotki'}
        self.assert_events_are_logged(self.env.handle_mock, names_values)


@with_settings_hosts()
class LegacyAdmLoginruleTestCase(BaseTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_1(self):
        blackbox_response = blackbox_userinfo_response(subscribed_to=[8])
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        self.env.grants.set_grants_return_value(mock_grants(
            consumer='mail',
            grants={'subscription': {'mail': ['*']}},
        ))
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admloginrule',
            query_string={'uid': 1, 'login_rule': 1, 'from': 'mail'},
        )

        self.check_xml_output(
            rv.data,
            {'result': {'error': 'nosubscription', 'text': u'У пользователя нет подписки на указанный сервис.'}},
            {'status': 'error'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        self.assert_events_are_empty(self.env.handle_mock)

    def test_2(self):
        blackbox_response = blackbox_userinfo_response(
            subscribed_to=[2], dbfields={'subscription.login_rule.2': '1'},
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='mail',
            grants={'subscription': {'mail': ['*']}},
        ))
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admloginrule',
            query_string={'uid': 1, 'login_rule': 1, 'from': 'mail'},
        )

        self.check_xml_output(
            rv.data,
            {'result': {'login_rule': '1', 'uid': '1', 'sid': '2'}},
            {'status': 'ok'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        self.assert_events_are_empty(self.env.handle_mock)

    def test_3(self):
        """В новой схеме не хранится запись о дефолтном значении login_rule=1"""
        blackbox_response = blackbox_userinfo_response(
            subscribed_to=[2],
            dbfields={'subscription.login_rule.2': 222},
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='mail',
            grants={'subscription': {'mail': ['*']}},
        ))
        self.env.db.serialize(blackbox_response)

        self.env.db.check('attributes', 'subscription.mail.login_rule', '222', uid=1, db='passportdbshard1')

        rv = self.env.client.get(
            path='/passport/admloginrule',
            query_string={'uid': 1, 'login_rule': 1, 'from': 'mail'},
        )

        self.check_xml_output(
            rv.data,
            {'result': {'login_rule': '1', 'uid': '1', 'sid': '2'}},
            {'status': 'ok'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)  # В новой схеме сделали `delete from attributes`
        self.env.db.check_missing('attributes', 'subscription.mail.login_rule', uid=1, db='passportdbshard1')

        events = {
            'sid.login_rule': '2|1',
            'action': 'admloginrule',
            'from': 'mail',
        }
        self.assert_events_are_logged(self.env.handle_mock, events)

    def test__clear_needpasschange_flag__ok(self):
        blackbox_response = blackbox_userinfo_response(
            dbfields={'subscription.login_rule.8': '5'},
            attributes={'password.forced_changing_reason': '1'},
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='passport',
            grants={'password': ['is_changing_required']},
        ))
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admloginrule',
            query_string={'uid': 1, 'need_change_pass': 0, 'login_rule': 1, 'from': 'passport'},
        )

        self.check_xml_output(
            rv.data,
            {'result': {'login_rule': '0', 'uid': '1', 'sid': '8'}},
            {'status': 'ok'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check_missing('attributes', 'password.forced_changing_reason', uid=1, db='passportdbshard1')

        names_values = {
            'action': 'admloginrule',
            'sid.login_rule': '8|1',
            'from': 'passport',
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_2fa_need_change_password_error(self):
        """
        Так как направление на принудительную смена пароля для пользователя со
        включенным 2FA не имеет смысла, выдаем ошибку.
        """
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='passport',
            grants={
                'password': [
                    'is_changing_required',
                ],
            },
        ))
        account_args = dict(
            uid=1,
            login='test_login',
            attributes={
                'account.2fa_on': '1',
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**account_args),
        )

        rv = self.env.client.get(
            path='/passport/admloginrule',
            query_string={
                'uid': 1,
                'need_change_pass': 1,
                'service': 8,
                'from': 'passport',
                'login_rule': 1,
            },
        )
        self.check_xml_output(
            rv.data,
            {
                'result': {
                    'error': 'interror',
                },
            },
            {
                'status': 'error',
            },
            skip_elements=['text'],
        )


@with_settings_hosts()
class LegacyAdmKarmaTestCase(BaseTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'karma': ['*']}))
        self.login = 'user1'

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_with_bad_headers(self):
        bad_headers = '127.0.0.1,123.4.5.6'

        rv = self.env.client.get(
            path='/passport/admkarma',
            query_string={'uid': 1, 'karma': 100},
            headers=mock_headers(bad_headers),
        )

        eq_(rv.status_code, 200)
        ok_(bad_headers in rv.data)

    def test__set_user_karma__ok(self):
        blackbox_response = blackbox_userinfo_response(
            login=self.login,
            karma='75',
            dbfields={'userinfo.reg_date.uid': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admkarma',
            query_string={'uid': 1, 'karma': 100},
        )

        self.check_xml_output(
            rv.data,
            {'result': {'uid': '1', 'karma': '100'}},
            {'status': 'ok'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'karma.value', '100', uid=1, db='passportdbshard1')

        names_values = {'action': 'admkarma', 'info.karma': '100', 'info.karma_full': '100'}
        self.assert_events_are_logged(self.env.handle_mock, names_values)

        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [mock_frodobox_karma(
                consumer='-', login=self.login,
                old_karma='75', new_karma='100', action='admkarma',
            )],
        )

    def test_2(self):
        blackbox_response = blackbox_userinfo_response()
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admkarma',
            query_string={'uid': 1, 'prefix': 2},
        )

        self.check_xml_output(
            rv.data,
            {'result': {'uid': '1', 'prefix': '2'}},
            {'status': 'ok'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'karma.value', '2000', uid=1, db='passportdbshard1')

        names_values = {'action': 'admkarma', 'info.karma_prefix': '2', 'info.karma_full': '2000'}
        self.assert_events_are_logged(self.env.handle_mock, names_values)


@with_settings_hosts()
class LegacyAdmBlockTestCase(BaseTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='mail',
            grants={
                'karma': ['*'],
                'account': ['*'],
                'subscription': {'mail': ['*']},
            },
        ))

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_block_from(self):
        blackbox_response = blackbox_userinfo_response(
            login='bad-guy',
            subscribed_to=[2],
            dbfields={
                'subscription.login_rule.2': '1',
                'userinfo.reg_date.uid': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admblock',
            query_string={'uid': 1, 'from': 'mail'},
        )

        self.check_xml_output(
            rv.data,
            {'result': {'uid': '1', 'sid': '2', 'login_rule': '0', 'ena': '0'}},
            {'status': 'ok'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'account.is_disabled', '1', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'karma.value', '3000', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'subscription.mail.login_rule', '0', uid=1, db='passportdbshard1')

        names_values = {
            'action': 'admblock',
            'from': 'mail',
            'sid.login_rule': '2|0',
            'info.karma_prefix': '3',
            'info.karma_full': '3000',
            'info.ena': '0',
            'info.disabled_status': '1',
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            mock_statbox_account_modification_entries(
                operation='updated',
                names_values=[
                    ('account.disabled_status', 'enabled', 'disabled'),
                ],
                consumer='-',
            ) + [
                mock_frodobox_karma(
                    consumer='-', login='bad-guy', old_karma='0',
                    new_karma='3000', suid='1', action='admblock',
                ),
            ],
        )

    def test_already_blocked(self):
        blackbox_response = blackbox_userinfo_response(
            subscribed_to=[2],
            dbfields={
                'subscription.login_rule.2': '0',
            },
            attributes={
                AT['account.is_disabled']: ACCOUNT_DISABLED,
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admblock',
            query_string={'uid': 1, 'from': 'mail'},
        )

        self.check_xml_output(
            rv.data,
            {'result': {'error': 'unknownuid'}},
            {'status': 'error'},
            skip_elements=['text'],
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.env.db.check('attributes', 'account.is_disabled', '1', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'karma.value', uid=1, db='passportdbshard1')

    def test_block_without_from(self):
        self.env.grants.set_grants_return_value(
            mock_grants(consumer='dev', grants={'karma': ['*'], 'account': ['*']}),
        )
        blackbox_response = blackbox_userinfo_response(
            subscribed_to=[2],
            dbfields={'subscription.login_rule.2': '1'},
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        rv = self.env.client.get(
            path='/passport/admblock',
            query_string={'uid': 1},
        )

        self.check_xml_output(
            rv.data,
            {'result': {'uid': '1', 'ena': '0'}},
            {'status': 'ok'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'account.is_disabled', '1', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'karma.value', '3000', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'subscription.mail.login_rule', uid=1, db='passportdbshard1')

        names_values = {
            'action': 'admblock',
            'info.karma_prefix': '3',
            'info.ena': '0',
            'info.disabled_status': '1',
            'info.karma_full': '3000',
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)


@with_settings_hosts()
class LegacyAdmChangeRegTestCase(BaseTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        blackbox_response = blackbox_userinfo_response(login='test')
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)
        self.env.grants.set_grants_return_value(
            mock_grants(consumer='mail', grants={'admchangereg': ['*']}),
        )

    def tearDown(self):
        self.env.stop()
        del self.env

    tests = [
        ({}, 'nofield'),
        ({'uid': '1'}, 'nofield'),
        ({'uid': '1', 'from': 'mail'}, 'nofield'),
        ({'uid': '1', 'sid': '2'}, 'nofield'),
        ({'uid': '1', 'from': 'mail', 'sid': '2'}, 'nofield'),
        ({'uid': '1', 'from': 'mail', 'sid': '2', 'lang': 'en'},
         {'sid': '2', 'lang': 'en', 'uid': '1'}),
        ({'uid': '1', 'from': 'mail', 'sid': '2', 'lang': 'en', 'sex': '2'},
         {'sid': '2', 'lang': 'en', 'sex': '2', 'uid': '1'}),
        ({'uid': -111111172, 'from': 'mail', 'sid': '2', 'lang': 'en'}, 'nofield'),
        ({'uid': '1', 'from': 'mail', 'sex': ''}, 'nofield'),
        ({'uid': '1', 'from': 'mail', 'sex': '3'}, 'badsex'),
        ({'uid': '1', 'from': 'mail', 'sex': '2'},
         {'sid': '2', 'sex': '2', 'uid': '1'}),
        ({'uid': '1', 'from': 'mail', 'birth_date': ''}, 'nofield'),
        ({'uid': '1', 'from': 'mail', 'birth_date': '00'}, 'nofield'),
        ({'uid': '1', 'from': 'mail', 'birth_date': '00-00-00'}, 'nofield'),
        ({'uid': '1', 'from': 'mail', 'birth_date': '1988-00-00'},
         {'sid': '2', 'birth_date': '1988-00-00', 'uid': '1'}),
        ({'uid': '1', 'from': 'mail', 'timezone': ''}, 'nofield'),
        ({'uid': '1', 'from': 'mail', 'timezone': 'Europe/Fakezone'}, 'badtimezone'),
        ({'uid': '1', 'from': 'mail', 'timezone': 'Europe/London'},
         {'sid': '2', 'timezone': 'Europe/London', 'uid': '1'}),
        ({'uid': '1', 'from': 'mail', 'iname': ''}, 'nofield'),
        ({'uid': '1', 'from': 'mail', 'iname': 'aa'},
         {'sid': '2', 'iname': 'aa', 'uid': '1'}),
        ({'uid': '1', 'from': 'mail', 'fname': ''}, 'nofield'),
        ({'uid': '1', 'from': 'mail', 'fname': 'aa'},
         {'sid': '2', 'fname': 'aa', 'uid': '1'}),
        ({'uid': '1', 'from': 'mail', 'lang': ''}, 'badlang'),
        ({'uid': '1', 'from': 'mail', 'lang': 'klingon'}, 'badlang'),
        ({'uid': '1', 'from': 'mail', 'lang': 'en'},
         {'sid': '2', 'lang': 'en', 'uid': '1'}),
        ({'uid': '1', 'from': 'mail', 'display_name': 'aa'},
         {'sid': '2', 'display_name': 'p:aa', 'uid': '1'}),
        ({'uid': '1', 'from': 'mail', 'display_name': 'aa', 'provider': 'fb'},
         'baddisplayname'),
        ({'uid': '1', 'from': 'mail', 'display_name': 'aa', 'provider': 'fake '},
         'baddisplayname'),
        ({'uid': '1', 'from': 'mail', 'display_name': 'aa', 'profile_id': 'aa '},
         'baddisplayname'),
        ({'uid': '1', 'from': 'mail', 'display_name': 'aa', 'profile_id': '11 '},
         'baddisplayname'),
        ({'uid': '1', 'from': 'mail', 'display_name': 'aa', 'provider': 'fb', 'profile_id': 'aa'},
         'baddisplayname'),
        ({'uid': '1', 'from': 'mail', 'display_name': 'aa', 'provider': 'fake ', 'profile_id': 'aa'},
         'baddisplayname'),
        ({'uid': '1', 'from': 'mail', 'display_name': 'aa', 'provider': 'fake ', 'profile_id': '1'},
         'baddisplayname'),
        ({'uid': '1', 'from': 'mail', 'display_name': 'aa', 'provider': 'fb', 'profile_id': '1'},
         {'sid': '2', 'display_name': 's:1:fb:aa', 'uid': '1'}),
        ({'display_name': u'\u0415\u0432\u0433\u0435\u043d\u0438\u0439 \u0410\u0440\u0434\u0430\u0440\u043e\u0432',
          'uid': u'1', 'provider': u'vk', 'from': u'mail',
          'profile_id': u'582', 'mode': u'admchangereg'},
         {'uid': '1', 'display_name': u's:582:vk:%s' % u'\u0415\u0432\u0433\u0435\u043d\u0438\u0439 \u0410\u0440\u0434\u0430\u0440\u043e\u0432',
          'sid': '2'}),
        ({'from': 'test', 'display_name': '', 'uid': '1'},
         'baddisplayname'),
    ]

    def test_admchangereg_without_subscription_login_rule_8(self):
        blackbox_response = blackbox_userinfo_response(
            uid=1,
            unsubscribed_from=[8],
            dbfields={
                'subscription.login_rule.8': '',
            },
            attributes={
                'person.firstname': 'firstname',
                'person.lastname': 'lastname',
            },
            display_name={
                'name': 'display_name',
                'social': {'provider': 'vk', 'profile': '582'},
            },
        )

        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        test_params = {
            'display_name': u'blabla',
            'uid': u'1',
            'provider': u'vk',
            'from': u'social',
            'profile_id': u'9377465',
            'mode': u'admchangereg',
        }
        rv = self.env.client.get(
            path='/passport/admchangereg',
            query_string=test_params,
        )

        display_name = 's:9377465:vk:blabla'

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'account.display_name', display_name, uid=1, db='passportdbshard1')

        events = {
            'action': 'admchangereg',
            'from': 'social',
            'info.display_name': display_name,
        }
        self.assert_events_are_logged(self.env.handle_mock, events)

        self.check_xml_output(
            rv.data,
            {'result': {'display_name': display_name, 'sid': '58', 'uid': '1'}},
            {'status': 'ok'},
        )

    def normalize(self, key, value):
        if key == 'sex':
            return Gender.to_char(int(value))
        else:
            return value

    def admchangereg_run(self, test_params, expected_result):
        blackbox_response = blackbox_userinfo_response(
            uid=test_params.get('uid') if int(test_params.get('uid', 1)) > 0 else None,
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        rv = self.env.client.get(
            path='/passport/admchangereg',
            query_string=test_params,
        )

        if isinstance(expected_result, string_types):
            self.check_xml_output(
                rv.data,
                {'result': {'error': expected_result}},
                {'status': 'error'},
                skip_elements=['text'],
            )
        else:
            self.check_xml_output(rv.data, {'result': expected_result}, {'status': 'ok'})
            events = {'action': 'admchangereg', 'from': 'mail'}

            uid = expected_result['uid']

            event_dict = {
                'display_name': 'info.display_name',
                'iname': 'info.firstname',
                'fname': 'info.lastname',
                'sex': 'info.sex',
                'birth_date': 'info.birthday',
                'lang': 'info.lang',
                'timezone': 'info.tz',
            }

            column_dict = {
                'display_name': 'display_name',
                'iname': 'firstname',
                'fname': 'lastname',
                'sex': 'sex',
                'birth_date': 'birth_date',
                'lang': 'lang',
                'timezone': 'tz',
            }

            new_scheme_column_dict = {
                'display_name': 'account.display_name',
                'iname': 'person.firstname',
                'fname': 'person.lastname',
                'sex': 'person.gender',
                'birth_date': 'person.birthday',
                'lang': 'person.language',
                'timezone': 'person.timezone',
            }

            old_event_dict = {
                'iname': 'iname',
                'fname': 'fname',
                'sex': 'sex',
                'birth_date': 'bdate',
                'lang': 'lang',
            }

            statbox_event_dict = {
                'iname': 'person.firstname',
                'fname': 'person.lastname',
                'lang': 'person.language',
                'sex': 'person.gender',
                'birth_date': 'person.birthday',
                'display_name': 'person.display_name',
            }

            statbox_old_values = {
                'iname': '\\\\u0414',
                'fname': '\\\\u0424',
                'lang': 'ru',
                'sex': 'm',
                'birth_date': '1963-05-15',
                'display_name': '',
            }

            old_events = {}
            names_values = []
            for key, value in expected_result.items():
                # данные для БД
                if key in column_dict:
                    new_scheme_expected_value = self.normalize(key, value).encode('utf-8')
                    name = new_scheme_column_dict[key]
                    self.env.db.check('attributes', name, new_scheme_expected_value, uid=uid, db='passportdbshard1')

                value = smart_text(value)
                # данные для нового event.log
                if key in event_dict:
                    events[event_dict[key]] = value.encode('utf-8')
                # данные для старого event.log
                if key in old_event_dict:
                    old_events[old_event_dict[key]] = value
                if key in statbox_event_dict:
                    expected_value = self.normalize(key, value)
                    names_values.append((statbox_event_dict[key], statbox_old_values[key], expected_value))

            self.assert_events_are_logged(self.env.handle_mock, events)

            if 'iname' in expected_result or 'fname' in expected_result:
                if 'iname' in expected_result and 'fname' in expected_result:
                    new_value = '{} {}'.format(expected_result['iname'], expected_result['fname'])
                elif 'iname' in expected_result:
                    new_value = expected_result['iname']
                else:
                    new_value = expected_result['fname']
                names_values.append(('person.fullname', '\\\\u0414 \\\\u0424', new_value,))

            account_modification_statbox_entries = mock_statbox_account_modification_entries(
                operation='updated',
                names_values=names_values,
                consumer='-',
            )

            self.check_statbox_log_entries(
                self.env.statbox_handle_mock,
                account_modification_statbox_entries,
            )


# nosetests не поддерживет методы-генераторы тестов для классов, отнаследованных от TestCase (WAT?)
# тесты-функции сейчас не поддерживаются @with_settings_hosts, + setUp и tearDown опираются на общее состояние
def add_admchangereg_check(index, testdata, expected_result):
    test_func = istest(lambda self: self.admchangereg_run(testdata, expected_result))
    test_func.__doc__ = 'AdmChangeReg: %s\tExpected: %s' % (testdata, expected_result)
    setattr(LegacyAdmChangeRegTestCase, 'test_admchangereg_%d' % index, test_func)

for index, test in enumerate(LegacyAdmChangeRegTestCase.tests):
    add_admchangereg_check(index, *test)


@with_settings_hosts()
class LegacyTestApi(BaseTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants())

        self.apis = {
            'get': [
                ('/passport/admloginrule', {'login_rule': 1, 'uid': 1, 'from': 'dev'}),
                ('/passport/admsubscribe', {'from': 'lenta', 'uid': 1}),
                ('/passport/admkarma', {'uid': 1, 'karma': 100}),
                ('/passport/admblock', {'from': 'dev', 'uid': 1}),
                ('/passport/admchangereg', {'from': 'dev', 'uid': 1, 'fname': 1}),
            ],
            'post': [
                ('/passport/admloginrule', {'login_rule': 1, 'uid': 1, 'from': 'dev'}),
                ('/passport/admsubscribe', {'from': 'lenta', 'uid': 1}),
                ('/passport/admkarma', {'uid': 1, 'karma': 100}),
                ('/passport/admblock', {'from': 'dev', 'uid': 1}),
                ('/passport/admchangereg', {'from': 'dev', 'uid': 1, 'fname': 1}),
            ],
        }

    def tearDown(self):
        self.env.stop()
        del self.env

    def api_request(self, method, path, params):
        if method in ['post', 'put']:
            return getattr(self.env.client, method)(path=path, data=params)

        return getattr(self.env.client, method)(path=path, query_string=params)

    def test_without_grants(self):
        self.env.grants.set_grants_return_value({})

        for method, apis in self.apis.items():
            for path, qs in apis:
                rv = self.api_request(method, path, qs)
                eq_(rv.status_code, 200, rv.data)
                eq_(rv.data, legacy.common.HTML_ERROR_RESPONSE)

    def test_without_grants_for_ip(self):
        for method, apis in self.apis.items():
            for path, qs in apis:
                rv = getattr(self.env.client, method)(path=path, query_string=qs, remote_addr='127.0.0.3')
                eq_(rv.status_code, 200, rv.data)
                eq_(rv.data, legacy.common.HTML_ERROR_RESPONSE)

    def test_with_invalid_params(self):
        for method, apis in self.apis.items():
            for path, qs in apis:
                del qs['uid']
                rv = self.api_request(method, path, qs)
                eq_(rv.status_code, 200, rv.data)

                if 'admsubscribe' in path:
                    self.check_xml_output(
                        rv.data,
                        {'page': {'error': 'nofield', 'message': 'At least 1 of uid, login is required'}},
                        {'job': 'rejected'},
                    )
                    continue

                self.check_xml_output(
                    rv.data,
                    {'result': {'error': 'nofield', 'text': 'uid: Missing value'}},
                    {'status': 'error'},
                )

    def test_blackbox_error(self):
        bb_errors = [
            (blackbox.BaseBlackboxError('Blackbox failed'), 200),
            (blackbox.BlackboxTemporaryError('Request failed'), 200),
            (blackbox.AccessDenied('Blackbox ACL failed'), 200),
        ]
        for method, apis in self.apis.items():
            for path, qs in apis:
                for bb_error, status_code in bb_errors:
                    self.env.blackbox.set_blackbox_response_side_effect('userinfo', bb_error)
                    rv = self.api_request(method, path, qs)
                    eq_(rv.status_code, status_code, [path, method, rv.status_code, rv.data])

                    if 'admsubscribe' in path:
                        self.check_xml_output(
                            rv.data,
                            {'page': {'error': 'interror', 'message': str(bb_error)}},
                            {'job': 'rejected'},
                        )
                        continue

                    self.check_xml_output(
                        rv.data,
                        {'result': {'error': 'interror', 'text': str(bb_error)}},
                        {'status': 'error'},
                    )

    def test_unknownuid(self):
        blackbox_response = blackbox_userinfo_response(uid=None)
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        for method, apis in self.apis.items():
            for path, qs in apis:
                rv = self.api_request(method, path, qs)
                eq_(rv.status_code, 200, rv.data)

                if 'admsubscribe' in path:
                    self.check_xml_output(
                        rv.data,
                        {'page': {'error': 'unknownuid', 'message': u'Пользователь с таким UID не найден.'}},
                        {'job': 'rejected'},
                    )
                    continue

                self.check_xml_output(
                    rv.data,
                    {'result': {'error': 'unknownuid', 'text': u'Пользователь с таким UID не найден.'}},
                    {'status': 'error'},
                )

    def test_dbmanager_error(self):
        blackbox_response = blackbox_userinfo_response()
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        db_error = 'DB request failed'
        self.env.db.set_side_effect_for_db('passportdbcentral', DBError(db_error))
        self.env.db.set_side_effect_for_db('passportdbshard1', DBError(db_error))
        for method, requests in self.apis.items():
            for path, params in requests:
                rv = self.api_request(method, path, params)
                eq_(rv.status_code, 200, [rv.status_code, rv.data])
                if 'admsubscribe' in path:
                    self.check_xml_output(
                        rv.data,
                        {'page': {'error': 'interror', 'message': db_error}},
                        {'job': 'rejected'},
                    )
                    continue

                    # FIXME: Разобраться, в каком случае ожидается такой ответ
                    self.check_xml_output(
                        rv.data,
                        {'result': {'error': 'interror', 'text': db_error}},
                        {'status': 'error'},
                    )


@with_settings_hosts(
    FRODO_URL='http://localhost/',
)
class LegacyAdmSimpleRegTestCase(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(consumer='mail', grants={'admsimplereg': ['*']}))
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_userinfo_response(uid=None))
        self.env.frodo.set_response_value(u'check', u'<spamlist></spamlist>')
        self.env.frodo.set_response_value(u'confirm', u'')

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_simple_reg(self):
        timenow = TimeNow()
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'Te-st': 'free'}),
        )

        rv = self.env.client.get(
            path='/passport/admsimplereg',
            query_string={
                'login': 'Te-st',
            },
        )

        self.check_xml_output(
            rv.data,
            {'page': {'login': 'Te-st'}},
            {'status': 'ok', 'uid': '1'},
        )

        assert_builder_requested(self.env.frodo, times=0)

        eq_(self.env.db.query_count('passportdbcentral'), 4)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

        self.env.db.check('aliases', 'portal', 'te-st', uid=1, db='passportdbcentral')
        self.env.db.check('attributes', 'account.registration_datetime', timenow, uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.firstname', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.lastname', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.birthday', uid=1, db='passportdbshard1')

        # Подписали на sid=8, sid=2
        self.env.db.check('suid2', 'suid', 1, uid=1, db='passportdbcentral')
        self.env.db.check_missing('attributes', 'subscription.mail.login_rule', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'account.is_employee', '1', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'account.is_maillist', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'account.user_defined_login', 'Te-st', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'account.registration_datetime', timenow, uid=1, db='passportdbshard1')

        self.env.db.check_missing('attributes', 'hint.question.serialized', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'hint.answer.encrypted', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'karma.value', uid=1, db='passportdbshard1')

        self.env.db.check_missing('attributes', 'password.forced_changing_reason', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'password.update_datetime', timenow, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'password.quality', '3:0', uid=1, db='passportdbshard1')

        self.env.db.check('attributes', 'password.encrypted', TEST_IMPOSSIBLE_PASSWORD, uid=1, db='passportdbshard1')

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'action': 'admsimplereg',
                'info.login': 'te-st',
                'info.login_wanted': 'Te-st',
                'sid.add': '8|Te-st,2',
                'mail.add': '1',
                'info.mail_status': '1',
                'alias.portal.add': 'te-st',
                'info.reg_date': DatetimeNow(convert_to_datetime=True),
                'info.password_quality': '0',
                'info.password': TEST_IMPOSSIBLE_PASSWORD,
                'info.password_update_time': TimeNow(),
                'info.karma': '0',
                'info.karma_prefix': '0',
                'info.karma_full': '0',
                'info.is_employee': '1',
            },
        )

    def test_maillist_reg(self):
        timenow = TimeNow()
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'Te-st': 'free'}),
        )

        rv = self.env.client.get(
            path='/passport/admsimplereg',
            query_string={
                'login': 'Te-st',
                'maillist': '1',
            },
        )

        self.check_xml_output(
            rv.data,
            {'page': {'login': 'Te-st'}},
            {'status': 'ok', 'uid': '1'},
        )

        assert_builder_requested(self.env.frodo, times=0)
        eq_(self.env.db.query_count('passportdbcentral'), 4)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

        self.env.db.check('suid2', 'suid', 1, uid=1, db='passportdbcentral')
        self.env.db.check('aliases', 'portal', 'te-st', uid=1, db='passportdbcentral')
        self.env.db.check('attributes', 'account.user_defined_login', 'Te-st', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'account.registration_datetime', timenow, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'account.is_maillist', '1', uid=1, db='passportdbshard1')

        self.env.db.check_missing('attributes', 'account.is_employee', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.firstname', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.lastname', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.birthday', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'password.forced_changing_reason', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'hint.question.serialized', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'hint.answer.encrypted', uid=1, db='passportdbshard1')

        self.env.db.check_missing('attributes', 'subscription.mail.login_rule', uid=1, db='passportdbshard1')

        self.env.db.check('attributes', 'password.encrypted', TEST_IMPOSSIBLE_PASSWORD, uid=1, db='passportdbshard1')

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'action': 'admsimplereg',
                'info.login': 'te-st',
                'info.login_wanted': 'Te-st',
                'sid.add': '8|Te-st,2',
                'mail.add': '1',
                'info.mail_status': '1',
                'alias.portal.add': 'te-st',
                'info.reg_date': DatetimeNow(convert_to_datetime=True),
                'info.password_quality': '0',
                'info.password': TEST_IMPOSSIBLE_PASSWORD,
                'info.password_update_time': TimeNow(),
                'info.karma': '0',
                'info.karma_prefix': '0',
                'info.karma_full': '0',
                'info.is_maillist': '1',
            },
        )

    def test_occupied(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'te-st': 'occupied'}),
        )
        rv = self.env.client.get(
            path='/passport/admsimplereg',
            query_string={
                'login': 'te-st',
                'maillist': '1',
            },
        )

        self.check_xml_output(
            rv.data,
            {'page': {
                'login': 'te-st', 'error': 'occupied',
                'error_text': 'That username is already taken on Yandex. Try a different one.',
            }},
            {'status': 'error'},
        )

    def test_nologin(self):
        rv = self.env.client.get(
            path='/passport/admsimplereg',
            query_string={
                'login': '',
                'maillist': '1',
            },
        )

        self.check_xml_output(
            rv.data,
            {'page': {'login': None, 'error': 'nologin', 'error_text': 'login: Please enter a value'}},
            {'status': 'error'},
        )

    def test_badlogin(self):
        rv = self.env.client.get(
            path='/passport/admsimplereg',
            query_string={
                'login': '!@*&^!*(@^(!*&^(!@*^',
                'maillist': '1',
            },
        )

        self.check_xml_output(
            rv.data,
            {'page': {
                'login': '!@*&^!*(@^(!*&^(!@*^', 'error': 'badlogin',
                'error_text': 'login: Login has prohibited symbols',
            }},
            {'status': 'error'},
        )

    def test_badmaillist(self):
        rv = self.env.client.get(
            path='/passport/admsimplereg',
            query_string={
                'login': 'test-login',
                'maillist': 'abrakadabra',
            },
        )

        self.check_xml_output(
            rv.data,
            {'page': {
                'login': 'test-login', 'error': 'badmaillist',
                'error_text': "maillist: Value should be 'true' or 'false'",
            }},
            {'status': 'error'},
        )

    def test_dbmanager_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'te-st': 'free'}),
        )
        db_error = 'DB request failed'
        self.env.db.set_side_effect_for_db('passportdbcentral', DBError(db_error))
        self.env.db.set_side_effect_for_db('passportdbshard1', DBError(db_error))

        rv = self.env.client.get(
            path='/passport/admsimplereg',
            query_string={'login': 'te-st'},
        )

        eq_(rv.status_code, 200, rv.data)
        self.check_xml_output(
            rv.data,
            {'result': {'error': 'interror', 'text': db_error}},
            {'status': 'error'},
        )

    def test_blackbox_error(self):
        bb_errors = [
            blackbox.BaseBlackboxError('Blackbox failed'),
            blackbox.BlackboxTemporaryError('Request failed'),
            blackbox.AccessDenied('Blackbox ACL failed'),
        ]
        for bb_error in bb_errors:
            self.env.blackbox.set_blackbox_response_side_effect(
                'loginoccupation',
                bb_error,
            )

            rv = self.env.client.get(
                path='/passport/admsimplereg',
                query_string={'login': 'te-st'},
            )

            eq_(rv.status_code, 200, rv.data)
            self.check_xml_output(
                rv.data,
                {'result': {'error': 'interror', 'text': str(bb_error)}},
                {'status': 'error'},
            )


@with_settings_hosts(
    FRODO_URL='http://localhost/',
    BASIC_PASSWORD_POLICY_MIN_QUALITY=0,
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
)
class LegacyAdmRegTestCase(BaseTestViews):
    is_password_hash_from_blackbox = True
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='mail',
                grants={
                    'admreg': ['*'],
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )

        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )
        self.env.frodo.set_response_value(u'check', u'<spamlist></spamlist>')
        self.env.frodo.set_response_value(u'confirm', u'')

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_admreg(self):
        timenow = TimeNow()
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'te.st': 'free'}),
        )

        rv = self.env.client.get(
            path='/passport/admreg',
            query_string={
                'login': 'te.st',
                'passwd': 'testtest',
                'passwd2': 'testtest',
                'iname': 'Itest',
                'fname': 'Ftest',
            },
        )

        self.check_xml_output(
            rv.data,
            {'page': {'login': 'te.st', 'iname': 'Itest', 'fname': 'Ftest'}},
            {'status': 'ok', 'uid': '1'},
        )

        # uid, suid, suid2, aliases
        eq_(self.env.db.query_count('passportdbcentral'), 4)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

        self.env.db.check('aliases', 'portal', 'te-st', uid=1, db='passportdbcentral')
        self.env.db.check('attributes', 'account.registration_datetime', timenow, uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.firstname', 'Itest', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'person.lastname', 'Ftest', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.birthday', uid=1, db='passportdbshard1')

        self.env.db.check('suid2', 'suid', 1, uid=1, db='passportdbcentral')

        self.env.db.check('attributes', 'account.user_defined_login', 'te.st', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'password.is_creating_required', '1', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'password.quality', '3:12', uid=1, db='passportdbshard1')
        self.env.db.check('attributes', 'password.update_datetime', timenow, uid=1, db='passportdbshard1')

        self.env.db.check_missing('attributes', 'hint.question.serialized', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'hint.answer.encrypted', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'account.is_disabled', uid=1, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'karma.value', uid=1, db='passportdbshard1')

        eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=1, db='passportdbshard1')
        if self.is_password_hash_from_blackbox:
            eq_(eav_pass_hash, TEST_SERIALIZED_PASSWORD)
        else:
            eq_(len(eav_pass_hash), 36)
            ok_(eav_pass_hash.startswith('%s:' % self.password_hash_version))

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'action': 'account_create_admreg',
                'info.login': 'te-st',
                'info.login_wanted': 'te.st',
                'sid.add': '8|te.st,2,100',
                'mail.add': '1',
                'info.mail_status': '1',
                'alias.portal.add': 'te-st',
                'info.ena': '1',
                'info.disabled_status': '0',
                'info.firstname': 'Itest',
                'info.lastname': 'Ftest',
                'info.country': 'ru',
                'info.reg_date': DatetimeNow(convert_to_datetime=True),
                'info.password_quality': '12',
                'info.password': eav_pass_hash,
                'info.password_update_time': TimeNow(),
                'info.karma': '0',
                'info.karma_prefix': '0',
                'info.karma_full': '0',
            },
        )

        self.check_statbox_log_entry(
            self.env.statbox_handle_mock,
            self.env.statbox_logger.entry(
                'base',
                mode='admreg',
                action='account_created',
                karma='0',
                uid='1',
                login='te-st',
                country='ru',
            ),
        )

    def test_reg_call_frodo_with_from(self):
        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='fotki',
                grants={
                    'admreg': ['*'],
                    'subscription': {'fotki': ['*']},
                },
            ),
        )

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'test': 'free'}),
        )
        self.env.frodo.set_response_value(
            u'check',
            u'<spamlist><spam_user login="test" weight="85" /></spamlist>',
        )
        self.env.frodo.set_response_value(u'confirm', u'')

        rv = self.env.client.get(
            path='/passport/admreg',
            query_string={
                'login': 'test',
                'passwd': 'testtest',
                'passwd2': 'testtest',
                'iname': 'Itest',
                'fname': 'Ftest',
                'from': 'fotki',
            },
        )

        self.check_xml_output(
            rv.data,
            {'page': {'login': 'test', 'iname': 'Itest', 'fname': 'Ftest', 'from': 'fotki'}},
            {'status': 'ok', 'uid': '1'},
        )
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma', '85')
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma_full', '85')

        eq_(self.env.db.query_count('passportdbcentral'), 4)
        eq_(self.env.db.query_count('passportdbshard1'), 2)
        self.env.db.check('attributes', 'karma.value', '85', uid=1, db='passportdbshard1')

        # Проверяем параметры для frodo
        requests = self.env.frodo.requests
        eq_(len(requests), 2)
        passwd, passwdex = get_password_metadata('testtest')
        requests[0].assert_query_contains({
            'login': 'test',
            'passwd': passwd,
            'passwdex': passwdex,
            'iname': 'Itest',
            'fname': 'Ftest',
            'from': 'fotki',
        })

    def test_reg_call_frodo_without_from(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'test': 'free'}),
        )
        self.env.frodo.set_response_value(
            u'check',
            u'<spamlist><spam_user login="test" weight="85" /></spamlist>',
        )
        self.env.frodo.set_response_value(u'confirm', u'')

        self.env.client.get(
            path='/passport/admreg',
            query_string={
                'login': 'test',
                'passwd': 'testtest',
                'passwd2': 'testtest',
                'iname': 'Itest',
                'fname': 'Ftest',
            },
        )

        # Проверяем параметры для frodo
        requests = self.env.frodo.requests
        eq_(len(requests), 2)
        passwd, passwdex = get_password_metadata('testtest')
        requests[0].assert_query_contains({
            'login': 'test',
            'passwd': passwd,
            'passwdex': passwdex,
            'iname': 'Itest',
            'fname': 'Ftest',
            'from': '',
        })

    def test_reg_call_frodo_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'test': 'free'}),
        )
        self.env.frodo.set_response_side_effect(u'check', FrodoError('Failed'))

        rv = self.env.client.get(
            path='/passport/admreg',
            query_string={
                'login': 'test',
                'passwd': 'testtest',
                'passwd2': 'testtest',
                'iname': 'Itest',
                'fname': 'Ftest',
            },
        )

        self.check_xml_output(
            rv.data,
            {'page': {'login': 'test', 'iname': 'Itest', 'fname': 'Ftest'}},
            {'status': 'ok', 'uid': '1'},
        )

        self.assert_event_is_logged(self.env.handle_mock, 'info.karma', '0')
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma_full', '0')

        eq_(self.env.db.query_count('passportdbcentral'), 4)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check_missing('attributes', 'karma.value', uid=1, db='passportdbshard1')

    def test_reg_and_subscribe(self):
        self.env.grants.set_grants_return_value(mock_grants(consumer='fotki', grants={
            'admreg': ['*'],
            'subscription': {'fotki': ['*']},
        }))

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'te.st': 'free'}),
        )

        rv = self.env.client.get(
            path='/passport/admreg',
            query_string={
                'login': 'te.st',
                'passwd': 'testtest',
                'passwd2': 'testtest',
                'iname': 'Itest',
                'fname': 'Ftest',
                'from': 'fotki',
            },
        )

        self.check_xml_output(
            rv.data,
            {'page': {'login': 'te.st', 'iname': 'Itest', 'fname': 'Ftest', 'from': 'fotki'}},
            {'status': 'ok', 'uid': '1'},
        )

        # uid, suid (mail), suid2, aliases
        eq_(self.env.db.query_count('passportdbcentral'), 4)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('aliases', 'portal', 'te-st', uid=1, db='passportdbcentral')
        self.env.db.check('suid2', 'suid', 1, uid=1, db='passportdbcentral')
        self.env.db.check('attributes', 'subscription.fotki', '1', uid=1, db='passportdbshard1')

        self.assert_event_is_logged(self.env.handle_mock, 'sid.add', '8|te.st,2,100,5')

    def test_reg_ena_false(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'test': 'free'}),
        )

        rv = self.env.client.get(
            path='/passport/admreg',
            query_string={
                'login': 'test',
                'passwd': 'testtest',
                'passwd2': 'testtest',
                'iname': 'Itest',
                'fname': 'Ftest',
                'ena': '0',
            },
        )

        self.check_xml_output(
            rv.data,
            {'page': {'login': 'test', 'iname': 'Itest', 'fname': 'Ftest'}},
            {'status': 'ok', 'uid': '1'},
        )
        self.assert_event_is_logged(self.env.handle_mock, 'info.ena', '0')
        self.assert_event_is_logged(self.env.handle_mock, 'info.disabled_status', '1')

        eq_(self.env.db.query_count('passportdbcentral'), 4)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'account.is_disabled', '1', uid=1, db='passportdbshard1')

    def test_reg_and_subscribe_yastaff(self):
        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='yastaff', grants={
                    'admreg': ['*'],
                    'subscription': {
                        'yastaff': ['*'],
                    },
                },
            ),
        )

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'te.st': 'free'}),
        )

        rv = self.env.client.get(
            path='/passport/admreg',
            query_string={
                'login': 'te.st',
                'passwd': 'testtest',
                'passwd2': 'testtest',
                'iname': 'Itest',
                'fname': 'Ftest',
                'from': 'yastaff',
                'yastaff_login': 'stafftest',
            },
        )

        self.check_xml_output(
            rv.data,
            {'page': {'login': 'te.st', 'iname': 'Itest', 'fname': 'Ftest', 'from': 'yastaff'}},
            {'status': 'ok', 'uid': '1'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 4)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('aliases', 'portal', 'te-st', uid=1, db='passportdbcentral')
        self.env.db.check('aliases', 'yandexoid', 'stafftest', uid=1, db='passportdbcentral')
        self.env.db.check('suid2', 'suid', 1, uid=1, db='passportdbcentral')

        eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=1, db='passportdbshard1')
        if self.is_password_hash_from_blackbox:
            eq_(eav_pass_hash, TEST_SERIALIZED_PASSWORD)
        else:
            eq_(len(eav_pass_hash), 36)
            ok_(eav_pass_hash.startswith('%s:' % self.password_hash_version))

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'action': 'account_create_admreg',
                'info.login': 'te-st',
                'info.login_wanted': 'te.st',
                'info.ena': '1',
                'info.disabled_status': '0',
                'info.firstname': 'Itest',
                'info.lastname': 'Ftest',
                'info.country': 'ru',
                'info.reg_date': DatetimeNow(convert_to_datetime=True),
                'info.password_quality': '12',
                'info.password': eav_pass_hash,
                'info.password_update_time': TimeNow(),
                'info.karma': '0',
                'info.karma_prefix': '0',
                'info.karma_full': '0',
                'from': 'yastaff',
                'sid.add': '8|te.st,2,100',
                'mail.add': '1',
                'info.mail_status': '1',
                'alias.portal.add': 'te-st',
                'alias.yandexoid.add': 'stafftest',
            },
        )

    def test_reg_and_subscribe_yastaff_with_dot(self):
        self.env.grants.set_grants_return_value(mock_grants(consumer='yastaff', grants={
            'admreg': ['*'],
            'subscription': {'yastaff': ['*']},
        }))

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'te.st': 'free'}),
        )

        rv = self.env.client.get(
            path='/passport/admreg',
            query_string={
                'login': 'te.st',
                'passwd': 'testtest',
                'passwd2': 'testtest',
                'iname': 'Itest',
                'fname': 'Ftest',
                'from': 'yastaff',
                'yastaff_login': 'staff.test',
            },
        )

        self.check_xml_output(
            rv.data,
            {'page': {'login': 'te.st', 'iname': 'Itest', 'fname': 'Ftest', 'from': 'yastaff'}},
            {'status': 'ok', 'uid': '1'},
        )

        eq_(self.env.db.query_count('passportdbcentral'), 4)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('aliases', 'portal', 'te-st', uid=1, db='passportdbcentral')
        self.env.db.check('aliases', 'yandexoid', 'staff.test', uid=1, db='passportdbcentral')
        self.env.db.check('suid2', 'suid', 1, uid=1, db='passportdbcentral')

        eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=1, db='passportdbshard1')
        if self.is_password_hash_from_blackbox:
            eq_(eav_pass_hash, TEST_SERIALIZED_PASSWORD)
        else:
            eq_(len(eav_pass_hash), 36)
            ok_(eav_pass_hash.startswith('%s:' % self.password_hash_version))

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'action': 'account_create_admreg',
                'info.login': 'te-st',
                'info.login_wanted': 'te.st',
                'info.ena': '1',
                'info.disabled_status': '0',
                'info.firstname': 'Itest',
                'info.lastname': 'Ftest',
                'info.country': 'ru',
                'info.reg_date': DatetimeNow(convert_to_datetime=True),
                'info.password_quality': '12',
                'info.password': eav_pass_hash,
                'info.password_update_time': TimeNow(),
                'info.karma': '0',
                'info.karma_prefix': '0',
                'info.karma_full': '0',
                'from': 'yastaff',
                'sid.add': '8|te.st,2,100',
                'mail.add': '1',
                'info.mail_status': '1',
                'alias.portal.add': 'te-st',
                'alias.yandexoid.add': 'staff-test',
            },
        )

    def test_reg_and_subscribe_yastaff_exists(self):
        self.env.grants.set_grants_return_value(mock_grants(consumer='yastaff', grants={
            'admreg': ['*'],
            'subscription': {'yastaff': ['*']},
        }))

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=1),
        )

        rv = self.env.client.get(
            path='/passport/admreg',
            query_string={
                'login': 'te.st',
                'passwd': 'testtest',
                'passwd2': 'testtest',
                'iname': 'Itest',
                'fname': 'Ftest',
                'from': 'yastaff',
                'yastaff_login': 'stafftest',
            },
        )

        eq_(rv.status_code, 500, rv.status_code)
        ok_(rv.data.startswith('500: '), rv.data)

    def test_reg_and_subscribe_with_yastaff_login_for_bad_sid(self):
        self.env.grants.set_grants_return_value(mock_grants(consumer='fotki', grants={
            'admreg': ['*'],
            'subscription': {'fotki': ['*']},
        }))

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'te.st': 'free'}),
        )

        rv = self.env.client.get(
            path='/passport/admreg',
            query_string={
                'login': 'te.st',
                'passwd': 'testtest',
                'passwd2': 'testtest',
                'iname': 'Itest',
                'fname': 'Ftest',
                'from': 'fotki',
                'yastaff_login': 'stafftest',
            },
        )

        eq_(rv.status_code, 500, rv.status_code)
        ok_(rv.data.startswith('500: yastaff_login:'), rv.data)

    def test_reg_grant_missing(self):
        self.env.grants.set_grants_return_value({})

        rv = self.env.client.get(
            path='/passport/admreg',
            query_string={
                'login': 'te.st',
                'passwd': 'testtest',
                'passwd2': 'testtest',
                'iname': 'Itest',
                'fname': 'Ftest',
                'from': 'mail',
            },
        )

        eq_(rv.status_code, 200)
        eq_(rv.data, legacy.common.HTML_ERROR_RESPONSE)

    def test_invalid_params(self):
        rv = self.env.client.get(
            path='/passport/admreg',
            query_string={'login': 'te.st'},
        )

        eq_(rv.status_code, 500)
        ok_(rv.data.startswith('500: '), rv.data)

    def test_with_bad_headers(self):
        bad_headers = '127.0.0.1,123.4.5.6'

        rv = self.env.client.get(
            path='/passport/admreg',
            query_string={'login': 'te.st'},
            headers=mock_headers(bad_headers),
        )

        eq_(rv.status_code, 500)
        ok_(bad_headers in rv.data)

    def test_not_matched_passwd(self):
        rv = self.env.client.get(
            path='/passport/admreg',
            query_string={
                'login': 'te.st',
                'passwd': '1234567',
                'passwd2': '12345679',
                'iname': 'Itest',
                'fname': 'Ftest',
            },
        )

        eq_(rv.status_code, 500)
        ok_(rv.data.startswith('500: form:'), rv.data)

    def test_login_taken(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'loginoccupation',
            [
                blackbox_loginoccupation_response({'test': 'occupied'}),
                blackbox_loginoccupation_response({'test1': 'free', 'test2': 'free'}),
            ],
        )
        with mock.patch.object(LoginSuggester, 'next_pack') as suggest_patch:
            suggest_patch.side_effect = [['test1', 'test2'], []]
            rv = self.env.client.get(
                path='/passport/admreg',
                query_string={
                    'login': 'test',
                    'passwd': 'testtest',
                    'passwd2': 'testtest',
                    'iname': 'Itest',
                    'fname': 'Ftest',
                },
            )

            self.check_xml_output(
                rv.data,
                {
                    'page':
                    {
                        'login': 'test',
                        'iname': 'Itest',
                        'fname': 'Ftest',
                        'variants': [('login', 'test1'), ('login', 'test2')],
                    },
                },
                {'status': 'occupied'},
                check_elements=['variants'],
            )

    def test_login_in_stoplist(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'loginoccupation',
            [
                blackbox_loginoccupation_response({'reserved': 'stoplist'}),
                blackbox_loginoccupation_response({'reserved1': 'free', 'reserved2': 'free'}),
            ],
        )
        with mock.patch.object(LoginSuggester, 'next_pack') as suggest_patch:
            suggest_patch.side_effect = [['reserved1', 'reserved2'], []]
            rv = self.env.client.get(
                path='/passport/admreg',
                query_string={
                    'login': 'reserved',
                    'passwd': 'testtest',
                    'passwd2': 'testtest',
                    'iname': 'Itest',
                    'fname': 'Ftest',
                },
            )

            self.check_xml_output(
                rv.data,
                {
                    'page':
                    {
                        'login': 'reserved',
                        'iname': 'Itest',
                        'fname': 'Ftest',
                        'variants': [('login', 'reserved1'), ('login', 'reserved2')],
                    },
                },
                {'status': 'occupied'},
                check_elements=['variants'],
            )

    def test_ignore_stoplist(self):
        self.env.grants.set_grants_return_value(
            mock_grants(consumer='fotki', grants={'admreg': ['*'], 'ignore_stoplist': ['*']}),
        )

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'reserved': 'free'}),
        )

        rv = self.env.client.get(
            path='/passport/admreg',
            query_string={
                'login': 'reserved',
                'passwd': 'testtest',
                'passwd2': 'testtest',
                'iname': 'Itest',
                'fname': 'Ftest',
                'ignore_stoplist': '1',
            },
        )

        self.env.blackbox.requests[0].assert_query_contains(
            dict(
                logins='reserved',
                ignore_stoplist='1',
            ),
        )
        self.check_xml_output(
            rv.data,
            {'page': {'login': 'reserved', 'iname': 'Itest', 'fname': 'Ftest'}},
            {'status': 'ok', 'uid': '1'},
        )

    def test_dbmanager_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'te.st': 'free'}),
        )
        db_error = 'DB request failed'
        self.env.db.set_side_effect_for_db('passportdbcentral', DBError(db_error))
        self.env.db.set_side_effect_for_db('passportdbshard1', DBError(db_error))

        rv = self.env.client.get(
            path='/passport/admreg',
            query_string={
                'login': 'te.st',
                'passwd': 'testtest',
                'passwd2': 'testtest',
                'iname': 'Itest',
                'fname': 'Ftest',
                'ignore_stoplist': '1',
            },
        )

        eq_(rv.status_code, 500)
        ok_(rv.data.startswith('500: %s' % db_error), rv.data)

    def test_blackbox_error(self):
        bb_errors = [
            blackbox.BaseBlackboxError('Blackbox failed'),
            blackbox.BlackboxTemporaryError('Request failed'),
            blackbox.AccessDenied('Blackbox ACL failed'),
        ]
        for bb_error in bb_errors:
            self.env.blackbox.set_blackbox_response_side_effect(
                'loginoccupation',
                bb_error,
            )

            rv = self.env.client.get(
                path='/passport/admreg',
                query_string={
                    'login': 'te.st',
                    'passwd': 'testtest',
                    'passwd2': 'testtest',
                    'iname': 'Itest',
                    'fname': 'Ftest',
                    'ignore_stoplist': '1',
                },
            )

            eq_(rv.status_code, 500)
            ok_(rv.data.startswith('500: %s' % bb_error), rv.data)


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class LegacyAdmRegTestCaseNoBlackboxHash(LegacyAdmRegTestCase):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT


class BaseLegacyMailHostTestCase(BaseTestViews):
    default_url = '/mailhost'

    def setUp(self):
        super(BaseLegacyMailHostTestCase, self).setUp()

        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={'mailhost': ['*']},
            ),
        )

        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

    def tearDown(self):
        self.env.stop()
        del self.env
        super(BaseLegacyMailHostTestCase, self).tearDown()

    def query_params(self, operation, **kwargs):
        params = {
            'op': operation,
        }
        params.update(kwargs)
        return params

    def make_request(self, query_params=None, headers=None):
        return self.env.client.get(
            path=self.default_url,
            query_string=query_params or {},
            headers=headers or {},
        )

    def assert_xml_error(self, response, error_code):
        eq_(response.status_code, 200)
        expected = {'doc': [('status', error_code, {'id': '1'})]}
        self.check_xml_list(response.data, expected)

    def assert_xml_ok(self, response):
        eq_(response.status_code, 200)
        expected = {'doc': [('status', 'OK', {'id': '0'})]}
        self.check_xml_list(response.data, expected)

    def assert_xml_exception(self, response, error):
        eq_(response.status_code, 200)
        expected = {'doc': [
            ('exception', 'UNKNOWN', {'id': '1'}),
            ('error', error, {}),
        ]}
        self.check_xml_list(response.data, expected)

    def assert_no_db_actions(self):
        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

    def assert_no_historydb_actions(self):
        eq_(self.env.handle_mock.call_count, 0)


@with_settings_hosts()
class MailHostFormErrorsTestCase(BaseLegacyMailHostTestCase):
    """Здесь проверим все ошибки неверных входных данных"""

    def test_empty_operation__error(self):
        resp = self.make_request({})
        self.assert_xml_error(resp, 'unknown op')
        self.assert_no_db_actions()

    def test_unknown_operation__error(self):
        resp = self.make_request(
            self.query_params('unknown'),
        )
        self.assert_xml_error(resp, 'unknown op')
        self.assert_no_db_actions()

    def test_create_no_db_id_param__error(self):
        resp = self.make_request(
            self.query_params('create', prio='-25', mx='mx.yandex.ru'),
        )
        self.assert_xml_error(resp, 'missing parameter db_id')
        self.assert_no_db_actions()

    def test_create_no_prio_param__error(self):
        resp = self.make_request(
            self.query_params('create', db_id='db2', mx='mx.yandex.ru'),
        )
        self.assert_xml_error(resp, 'missing parameter prio')
        self.assert_no_db_actions()

    def test_create_positive_prio_param__error(self):
        resp = self.make_request(
            self.query_params('create', db_id='db2', mx='mx.yandex.ru', prio='5'),
        )
        self.assert_xml_error(resp, 'prio must be negative')
        self.assert_no_db_actions()

    def test_create_no_mx_param__error(self):
        resp = self.make_request(
            self.query_params('create', db_id='db2', prio='-25'),
        )
        self.assert_xml_error(resp, 'missing parameter mx')
        self.assert_no_db_actions()

    def test_setprio_no_db_id_param__error(self):
        resp = self.make_request(
            self.query_params('setprio', prio='-25'),
        )
        self.assert_xml_error(resp, 'missing parameter db_id')
        self.assert_no_db_actions()

    def test_setprio_no_prio_param__error(self):
        resp = self.make_request(
            self.query_params('setprio', db_id='_id'),
        )
        self.assert_xml_error(resp, 'missing parameter prio')
        self.assert_no_db_actions()

    def test_setprio_positive_prio_param__error(self):
        resp = self.make_request(
            self.query_params('setprio', db_id='_id', prio='5'),
        )
        self.assert_xml_error(resp, 'prio must be negative')
        self.assert_no_db_actions()

    def test_delete_no_db_id_param__error(self):
        resp = self.make_request(
            self.query_params('delete'),
        )
        self.assert_xml_error(resp, 'missing parameter db_id')
        self.assert_no_db_actions()

    def test_assign_no_db_id_param__error(self):
        resp = self.make_request(
            self.query_params('assign', suid='42'),
        )
        self.assert_xml_error(resp, 'missing parameter db_id')
        self.assert_no_db_actions()

    def test_assign_no_suid_param__error(self):
        resp = self.make_request(
            self.query_params('assign', db_id='db2'),
        )
        self.assert_xml_error(resp, 'missing parameter suid')
        self.assert_no_db_actions()

    def test_find_no_prio_param__error(self):
        resp = self.make_request(
            self.query_params('find'),
        )
        self.assert_xml_error(resp, 'missing parameter prio')
        self.assert_no_db_actions()


@with_settings_hosts()
class MailHostTestCase(BaseLegacyMailHostTestCase):

    def setup_blackbox_userinfo(self, sids=None, mail_host=None):
        sids = [2] if sids is None else sids
        dbfields = {} if mail_host is None else {
            'subscription.suid.2': 42,
        }
        attributes = {}
        blackbox_response = blackbox_userinfo_response(
            uid=1,
            login='test',
            subscribed_to=sids,
            dbfields=dbfields,
            attributes=attributes,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        self.env.db.serialize(blackbox_response)

    def setup_blackbox_get_hosts(self, db_id=None, **kwargs):
        blackbox_response = blackbox_get_hosts_response(db_id=db_id, **kwargs)
        self.env.blackbox.set_blackbox_response_value(
            'get_hosts',
            blackbox_response,
        )

    def setUp(self):
        super(MailHostTestCase, self).setUp()
        self.setup_blackbox_get_hosts()

    def test_create__new_mailhost__ok(self):
        resp = self.make_request(
            self.query_params('create', db_id='db', prio=-10, mx='mx.ya.ru'),
        )

        self.assert_xml_ok(resp)

        expected = {
            'host_id': 1, 'db_id': 'db', 'prio': -10, 'mx': 'mx.ya.ru', 'sid': 2,
            'host_number': 0, 'host_ip': None, 'host_name': None,
        }
        self.env.db.check_line('hosts', expected, host_id=1, db='passportdbcentral')
        self.env.db.check_line('domains_hosts', expected, host_id=1, db='passportdbcentral')
        self.assert_no_historydb_actions()

    def test_create__this_db_id_already_present__ok(self):
        """
        Поведение для совместимости
        Пришел запрос на создание новой записи с какими-то параметрами
        В БД уже есть запись с указанным db_id
        Отвечаем ОК
        """
        existing_db_id = 'db'
        self.setup_blackbox_get_hosts(db_id=existing_db_id)
        resp = self.make_request(
            self.query_params('create', db_id=existing_db_id, prio=-20, mx='ms.ya.ru'),
        )

        self.assert_xml_ok(resp)
        self.assert_no_db_actions()

    def test_setprio__ok(self):
        # Подготовим БД и консистентный ответ ЧЯ
        self.setup_blackbox_get_hosts(db_id='db', prio=-100)
        host = MailHost().parse({'host_id': 1, 'db_id': 'db', 'prio': -100, 'sid': 2})
        self.env.db._serialize_to_eav(host)

        resp = self.make_request(
            self.query_params('setprio', db_id='db', prio=-10),
        )

        self.assert_xml_ok(resp)

        expected = {
            'host_id': 1, 'db_id': 'db', 'prio': -10, 'mx': None, 'sid': 2,
            'host_number': 0, 'host_ip': None, 'host_name': None,
        }
        self.env.db.check_line('hosts', expected, host_id=1, db='passportdbcentral')
        self.env.db.check_line('domains_hosts', expected, host_id=1, db='passportdbcentral')
        self.assert_no_historydb_actions()

    def test_setprio__this_db_id_not_present__ok(self):
        """
        Поведение для совместимости
        Пришел запрос на изменение приоритета какого-то хоста
        В БД не найден хост с указанным db_id
        Отвечаем ОК
        """
        self.setup_blackbox_get_hosts(db_id='db')

        resp = self.make_request(
            self.query_params('setprio', db_id='333', prio=-10),
        )

        self.assert_xml_ok(resp)
        self.assert_no_db_actions()

    def test_delete__ok(self):
        # Подготовим БД и консистентный ответ ЧЯ
        db_id, host_id = 'db', 1
        self.setup_blackbox_get_hosts(db_id=db_id, host_id=host_id)
        host = MailHost().parse({'host_id': host_id, 'db_id': db_id, 'prio': -100, 'sid': 2})
        self.env.db._serialize_to_eav(host)

        resp = self.make_request(
            self.query_params('delete', db_id=db_id),
        )

        self.assert_xml_ok(resp)
        self.env.db.check_missing('hosts', host_id=host_id, db='passportdbcentral')
        self.env.db.check_missing('domains_hosts', host_id=host_id, db='passportdbcentral')
        self.assert_no_historydb_actions()

    def test_delete__this_db_id_not_present__ok(self):
        """
        Поведение для совместимости
        Пришел запрос на удаление записи
        В БД не найден хост с указанным db_id
        Отвечаем ОК
        """
        host = MailHost().parse({'host_id': 1, 'db_id': 'db', 'prio': -100, 'sid': 2})
        self.env.db._serialize_to_eav(host)

        resp = self.make_request(
            self.query_params('delete', db_id='unknown-db-id'),
        )

        self.assert_xml_ok(resp)
        self.assert_no_db_actions()

    def test_assign__ok(self):
        uid, suid = 1, 42
        db_id, new_host_id = 'db', 100
        self.setup_blackbox_get_hosts(db_id=db_id, host_id=new_host_id)
        self.setup_blackbox_userinfo(mail_host=10)

        resp = self.make_request(
            self.query_params('assign', db_id=db_id, suid=suid),
        )

        self.assert_xml_ok(resp)

    def test_assign__no_such_account__ok(self):
        """
        Поведение для совместимости
        Приходит запрос о смене хоста для какого-то пользователя в Почте
        Указанный аккаунт не найден в ЧЯ по переданному suid
        Отвечаем ОК
        """
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            json.dumps({'users': [{'id': '', 'uid': {}}]}),
        )

        resp = self.make_request(
            self.query_params('assign', db_id='333', suid=42),
        )

        self.assert_xml_ok(resp)
        self.assert_no_db_actions()
        self.assert_no_historydb_actions()

    def test_account__has_no_mail_sid__error(self):
        """
        Поведение для совместимости
        Приходит запрос о смене хоста для какого-то пользователя в Почте
        Указанный аккаунт не имеет подписки на Почту
        Отвечаем ОК

        Обрати внимание: пользователь ищется в ЧЯ по sid=2 & suid
        Если пользователь найден, ожидается, что он будет подписан на Почту
        """
        self.setup_blackbox_userinfo(sids=[67])

        resp = self.make_request(
            self.query_params('assign', suid=42, db_id='333'),
        )

        self.assert_xml_error(resp, 'account without mail subscription')
        self.assert_no_db_actions()
        self.assert_no_historydb_actions()

    def test_assign__with_unknown_old_db_id__error(self):
        suid = 42
        db_id, new_host_id = 'db', 100
        bad = 'unknown-db-id'
        self.setup_blackbox_get_hosts(db_id=db_id, host_id=new_host_id)

        resp = self.make_request(
            self.query_params('assign', db_id=db_id, suid=suid, old_db_id=bad),
        )

        self.assert_xml_error(resp, 'old_db_id=%s isn\'t exist' % bad)
        self.assert_no_db_actions()
        self.assert_no_historydb_actions()

    def test_assign__with_old_db_id__db_id_collizion__ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'get_hosts',
            {
                'hosts': [
                    dict(
                        host_id='1', db_id='mxt', sid='2',
                    ),
                    dict(
                        host_id='2', db_id='mxt', sid='99',
                    ),
                    dict(
                        host_id='19', db_id='lol', sid='-10',
                    ),
                ],
            },
        )
        uid, suid = 1, 42
        mail_host_id = 1
        old_db_id = 'mxt'
        new_db_id, new_host_id = 'lol', 19
        self.setup_blackbox_userinfo(mail_host=mail_host_id)

        resp = self.make_request(
            self.query_params('assign', db_id=new_db_id, suid=suid, old_db_id=old_db_id),
        )

        self.assert_xml_ok(resp)

    def test_assign__with_old_db_id__ok(self):
        """
        Случай, когда передается параметр old_db_id, отличается только тем,
        что возможны две ошибки, если был передан плохой old_db_id
        """
        old_db_id, old_host_id = '333', 1  # Эти данные описывают текущее состояние аккаунта
        self.setup_blackbox_get_hosts()
        self.setup_blackbox_userinfo(mail_host=old_host_id)
        new_db_id, new_host_id = 'mxt', 17  # Это валидные тестовые данные
        uid, suid = 1, 42  # Это произвольные тестовые данне

        resp = self.make_request(
            self.query_params('assign', db_id=new_db_id, suid=suid, old_db_id=old_db_id),
        )

        self.assert_xml_ok(resp)

    def test_assign__no_such_db_id__error(self):
        self.setup_blackbox_get_hosts(db_id='db')

        db_id = 'unknown-db-id'
        resp = self.make_request(
            self.query_params('assign', db_id=db_id, suid='42'),
        )

        self.assert_xml_error(resp, 'db_id=%s isn\'t exist' % db_id)
        self.assert_no_db_actions()

    def test_find__ok(self):
        priority = -20
        resp = self.make_request(
            self.query_params('find', prio=priority),
        )

        eq_(resp.status_code, 200)

        expected_bb_response = json.loads(blackbox_get_hosts_response())
        # Дублируем логику ручки
        entries = [
            ('entry', None, host)
            for host in expected_bb_response['hosts']
            if int(host['prio']) > priority
        ]

        # FIXME: В perl была опечатка -- ее перенесли без изменений. Совместимость
        perl_legacy_typo = 'hostd_id'
        for _, _, attrs in entries:
            attrs[perl_legacy_typo] = attrs.pop('host_id')

        expected = {'doc': [('status', 'OK', {'id': '0'})] + entries}
        self.check_xml_list(resp.data, expected)
        self.assert_no_db_actions()
        self.assert_no_historydb_actions()

    def test_db_error__legacy_xml(self):
        self.env.db.set_side_effect_for_db('passportdbcentral', DBError)

        resp = self.make_request(
            self.query_params('create', db_id='db-id', prio=-20, mx='ms.ya.ru'),
        )

        self.assert_xml_exception(resp, 'DBError')

    def test_bb_error__legacy_xml(self):
        self.env.blackbox.set_response_side_effect('userinfo', blackbox.BlackboxUnknownError)

        resp = self.make_request(self.query_params('assign', db_id='333', suid=1234))

        self.assert_xml_exception(resp, 'BlackboxUnknownError')

    def test_unknown_exception__legacy_xml(self):
        self.env.db.set_side_effect_for_db('passportdbcentral', Exception)

        resp = self.make_request(
            self.query_params('create', db_id='db-id', prio=-20, mx='ms.ya.ru'),
        )

        eq_(resp.status_code, 500)
        eq_(
            json.loads(resp.data),
            {
                'status': 'error',
                'errors': [
                    {
                        "field": None,
                        "message": "Internal error",
                        "code": "internal",
                    },
                ],
            },
        )

    def test_grant_missing(self):
        self.env.grants.set_grants_return_value({})

        resp = self.make_request(
            self.query_params('create', db_id='db-id', prio=-20, mx='ms.ya.ru'),
        )

        eq_(resp.status_code, 200)
        eq_(resp.data, legacy.common.HTML_ERROR_RESPONSE)
