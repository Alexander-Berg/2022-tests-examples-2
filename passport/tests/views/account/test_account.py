# -*- coding: utf-8 -*-
from datetime import datetime
import json

from nose.tools import eq_
from nose_parameterized import parameterized
from passport.backend.api.test.mixins import make_clean_web_test_mixin
from passport.backend.api.test.mock_objects import (
    mock_frodobox_karma,
    mock_statbox_account_modification_entries,
    mock_statbox_subscriptions_entries,
)
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.eav_type_mapping import ATTRIBUTE_NAME_TO_TYPE as AT
from passport.backend.core.models.account import ACCOUNT_DISABLED
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts()
class AccountTestCase(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['*']}))

    def tearDown(self):
        self.env.stop()
        del self.env

    def account_request(self, **kwargs):
        return self.env.client.post('/1/account/1/?consumer=dev', **kwargs)

    def test_empty_request__error(self):
        blackbox_response = blackbox_userinfo_response()
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        rv = self.account_request()

        eq_(rv.status_code, 400)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.assert_events_are_empty(self.env.handle_mock)

    def test_enable_account__ok(self):
        blackbox_response = blackbox_userinfo_response(
            uid=self.env.TEST_UID,
            attributes={
                AT['account.is_disabled']: ACCOUNT_DISABLED,
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        rv = self.account_request(data={'is_enabled': 1})

        eq_(rv.status_code, 200)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check_missing('attributes', 'account.is_disabled', uid=self.env.TEST_UID, db='passportdbshard1')

        names_values = {
            'action': 'account',
            'info.ena': '1',
            'info.disabled_status': '0',
            'consumer': 'dev',
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_with_admin_params__ok(self):
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'account': ['*'],
                    'admin': ['log_action'],
                },
            ),
        )
        blackbox_response = blackbox_userinfo_response(
            uid=self.env.TEST_UID,
            attributes={
                AT['account.is_disabled']: ACCOUNT_DISABLED,
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        rv = self.account_request(data={
            'is_enabled': 1,
            'admin_name': 'test-admin',
            'comment': 'test-comment',
        })

        eq_(rv.status_code, 200)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

        names_values = {
            'action': 'account',
            'info.ena': '1',
            'info.disabled_status': '0',
            'admin': 'test-admin',
            'comment': 'test-comment',
            'consumer': 'dev',
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_admin_params_no_grants__error(self):
        blackbox_response = blackbox_userinfo_response(uid=self.env.TEST_UID)
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        rv = self.account_request(data={
            'is_enabled': 1,
            'admin_name': 'test-admin',
            'comment': 'test-comment',
        })

        eq_(rv.status_code, 403, rv.data)

    def test_enable_app_password__ok(self):
        blackbox_response = blackbox_userinfo_response(uid=self.env.TEST_UID)
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        rv = self.account_request(data={'is_enabled_app_password': 1})

        eq_(rv.status_code, 200)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'account.enable_app_password', '1', uid=self.env.TEST_UID, db='passportdbshard1')

        names_values = {'action': 'account', 'info.enable_app_password': '1', 'consumer': 'dev'}
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_disable_app_password__ok(self):
        blackbox_response = blackbox_userinfo_response(
            uid=self.env.TEST_UID,
            attributes={'account.enable_app_password': '1'},
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        rv = self.account_request(data={'is_enabled_app_password': 0})

        eq_(rv.status_code, 200)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check_missing('attributes', 'account.enable_app_password', uid=self.env.TEST_UID, db='passportdbshard1')

        names_values = {'action': 'account', 'info.enable_app_password': '0', 'consumer': 'dev'}
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_enable_app_password_no_grants__error(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={}))

        rv = self.account_request(data={'is_enabled_app_password': 1})

        eq_(rv.status_code, 403, rv.data)

    def test_enable_account_without_changes__ok(self):
        blackbox_response = blackbox_userinfo_response(
            uid=self.env.TEST_UID,
            dbfields={'accounts.ena.uid': '1'},
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        rv = self.account_request(data={'is_enabled': 1})

        eq_(rv.status_code, 200)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.env.db.check_missing('attributes', 'account.is_disabled', uid=self.env.TEST_UID, db='passportdbshard1')

        self.assert_events_are_logged(self.env.handle_mock, {})


@with_settings_hosts()
class KarmaTestCase(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'karma': ['*']}))
        self.uid = self.env.TEST_UID

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.uid

    def karma_request(self, **kwargs):
        return self.env.client.post('/1/account/1/karma/?consumer=dev', **kwargs)

    def test_empty_request__error(self):
        blackbox_response = blackbox_userinfo_response()
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        rv = self.karma_request()

        eq_(rv.status_code, 400)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.assert_events_are_empty(self.env.handle_mock)

    def test_set__ok(self):
        blackbox_response = blackbox_userinfo_response(
            uid=self.uid,
            login='login1',
            karma='75',
            dbfields={'userinfo.reg_date.uid': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        rv = self.karma_request(data={'prefix': 1, 'suffix': 100})

        eq_(rv.status_code, 200, rv.data)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'karma.value', str(1100), uid=self.uid, db='passportdbshard1')

        names_values = {
            'action': 'karma',
            'info.karma': '100',
            'info.karma_prefix': '1',
            'info.karma_full': '1100',
            'consumer': 'dev',
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [mock_frodobox_karma(login='login1', new_karma='1100', old_karma='75')],
        )

    def test_set_with_admin_params__ok(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={'karma': ['*'], 'admin': ['log_action']}))
        blackbox_response = blackbox_userinfo_response(
            uid=self.uid,
            login='login1',
            karma='75',
            dbfields={'userinfo.reg_date.uid': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        rv = self.karma_request(data={
            'prefix': 1,
            'suffix': 100,
            'admin_name': 'test-admin',
            'comment': 'test-comment',
        })

        eq_(rv.status_code, 200, rv.data)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

        names_values = {
            'action': 'karma',
            'info.karma': '100',
            'info.karma_prefix': '1',
            'info.karma_full': '1100',
            'admin': 'test-admin',
            'comment': 'test-comment',
            'consumer': 'dev',
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_admin_params_no_grants__error(self):
        blackbox_response = blackbox_userinfo_response(uid=self.env.TEST_UID)
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        rv = self.karma_request(data={
            'prefix': 1,
            'suffix': 100,
            'admin_name': 'test-admin',
            'comment': 'test-comment',
        })

        eq_(rv.status_code, 403, rv.data)

    def test_set_for_mail__statbox(self):
        """Проверяется только отправка значения кармы в ФО"""
        blackbox_response = blackbox_userinfo_response(
            login='login1',
            karma='75',
            subscribed_to=[2],
            dbfields={
                'userinfo.reg_date.uid': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'subscription.suid.2': '1112',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        rv = self.karma_request(data={'prefix': 1, 'suffix': 100})

        eq_(rv.status_code, 200, rv.data)

        # Проверяем, что записали suid для второго сида в логи ФО
        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [mock_frodobox_karma(login='login1', new_karma='1100', old_karma='75', suid='1112')],
        )


@with_settings_hosts(
    CLEAN_WEB_API_ENABLED=False,
)
class PersonDBTestCase(BaseTestViews, make_clean_web_test_mixin('test_statbox', ['firstname', 'lastname', 'display_name'], is_bundle=False, statbox_action=None)):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_userinfo_response())
        self.env.grants.set_grants_return_value(mock_grants(grants={'person': ['*']}))
        self.uid = self.env.TEST_UID
        blackbox_response = blackbox_userinfo_response(uid=self.uid)
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.uid

    def create_query_params(self, **kwargs):
        query = {
            'firstname': 'Fname',
            'lastname': 'Lname',
            'display_name': 'Dname',
            'profile_id': '100',
            'provider': 'fb',
            'gender': '2',
            'birthday': '2012-12-12',
            'country': 'us',
            'city': 'Moscow',
            'language': 'en',
            'timezone': 'US/Pacific',
            'contact_phone_number': '+79261234567',
        }
        query.update(**kwargs)
        return query

    @parameterized.expand(['firstname', 'lastname'])
    def test_fraud(self, field):
        rv = self.env.client.post(
            '/1/account/1/person/?consumer=dev',
            data=self.create_query_params(
                **{field: u'Заходи дорогой, гостем будешь +79261234567'}
            ),
        )
        eq_(rv.status_code, 400)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': field,
                    u'message': u'Invalid value',
                    u'code': u'invalid',
                }],
            },
        )

    def test_fraud_display_name(self):
        rv = self.env.client.post(
            '/1/account/1/person/?consumer=dev',
            data=self.create_query_params(
                display_name='s:1:fb:Заходи дорогой, www.yandex.ru',
            ),
        )
        eq_(rv.status_code, 400)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [{
                    u'field': u'display_name',
                    u'message': u'Invalid value',
                    u'code': u'invalid',
                }],
            },
        )

    def test_full_info__stored_to_db(self):
        expected_phone_number = '79261234567'

        rv = self.env.client.post('/1/account/1/person/?consumer=dev', data=self.create_query_params())

        eq_(rv.status_code, 200)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'account.display_name', 's:100:fb:Dname', uid=self.uid, db='passportdbshard1')
        self.env.db.check('attributes', 'person.firstname', 'Fname', uid=self.uid, db='passportdbshard1')
        self.env.db.check('attributes', 'person.lastname', 'Lname', uid=self.uid, db='passportdbshard1')
        self.env.db.check('attributes', 'person.gender', 'f', uid=self.uid, db='passportdbshard1')
        self.env.db.check('attributes', 'person.birthday', '2012-12-12', uid=self.uid, db='passportdbshard1')
        self.env.db.check('attributes', 'person.country', 'us', uid=self.uid, db='passportdbshard1')
        self.env.db.check('attributes', 'person.city', 'Moscow', uid=self.uid, db='passportdbshard1')
        self.env.db.check('attributes', 'person.language', 'en', uid=self.uid, db='passportdbshard1')
        self.env.db.check('attributes', 'person.timezone', 'US/Pacific', uid=self.uid, db='passportdbshard1')
        self.env.db.check(
            'attributes',
            'person.contact_phone_number',
            expected_phone_number,
            uid=self.uid,
            db='passportdbshard1',
        )

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'consumer': 'dev',
                'action': 'person',
                'info.display_name': 's:100:fb:Dname',
                'info.firstname': 'Fname',
                'info.lastname': 'Lname',
                'info.sex': '2',
                'info.birthday': '2012-12-12',
                'info.lang': 'en',
                'info.tz': 'US/Pacific',
                'info.country': 'us',
                'info.city': 'Moscow',
                'sid.add': '89|%s' % expected_phone_number,
            },
        )

    def test_statbox(self):
        rv = self.env.client.post('/1/account/1/person/?consumer=dev', data=self.create_query_params())
        eq_(rv.status_code, 200)

        names_values = [
            ('person.firstname', '\\\\u0414', 'Fname'),
            ('person.lastname', '\\\\u0424', 'Lname'),
            ('person.language', 'ru', 'en'),
            ('person.country', 'ru', 'us'),
            ('person.gender', 'm', 'f'),
            ('person.birthday', '1963-05-15', '2012-12-12'),
            ('person.display_name', '', 's:100:fb:Dname'),
            ('person.fullname', '\\\\u0414 \\\\u0424', 'Fname Lname'),
        ]
        account_modification_statbox_entries = mock_statbox_account_modification_entries(
            operation='updated',
            names_values=names_values,
        )

        subscription_statbox_entries = mock_statbox_subscriptions_entries(
            operation='added',
            sids=['89'],
        )

        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            account_modification_statbox_entries + subscription_statbox_entries,
        )
