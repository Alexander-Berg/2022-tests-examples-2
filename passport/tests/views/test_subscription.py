# -*- coding: utf-8 -*-
from datetime import date
import json

from mock import Mock
from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.builders.mail_apis.faker import husky_delete_user_response
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ALT
from passport.backend.core.services import SERVICES
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow


@with_settings_hosts()
class SubscriptionTestCase(BaseTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'subscription': ['*']}))

    def tearDown(self):
        self.env.stop()
        del self.env

    def subscription_request(self, slug, uid=None, **kwargs):
        uid = uid or self.env.TEST_UID
        return self.env.client.post('/1/account/%s/subscription/%s/?consumer=dev' % (uid, slug), **kwargs)

    def assert_statbox_entry(self, service_name, **kwargs):
        names_values = {
            'action': 'subscription',
            'consumer': 'dev',
            'service': service_name,
            'sid.add': str(SERVICES[service_name]),
        }
        names_values.update(kwargs)
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_invalid_slug(self):
        rv = self.subscription_request('fake')
        eq_(rv.status_code, 404, [rv.status_code, rv.data])

    def test_subscription__blank_user__ok(self):
        """Подписываемся на test сервис, при этом у аккаунта еще нет никаких подписок"""
        blackbox_response = blackbox_userinfo_response(uid=self.env.TEST_UID)
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        service_name = 'test'
        sid = SERVICES[service_name].sid
        uid = self.env.TEST_UID

        rv = self.subscription_request(service_name)

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        # Проверки БД в новой схеме
        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'account.is_test', '1', uid=uid, db='passportdbshard1')

        names_values = {
            'action': 'subscription',
            'consumer': 'dev',
            'service': service_name,
            'sid.add': str(sid),
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_subscription__user_have_other_subscriptions__ok(self):
        """Подписываемся на новый сервис с сохранением существующих подписок"""
        blackbox_response = blackbox_userinfo_response(subscribed_to=[2])
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        service_name = 'test'
        uid = self.env.TEST_UID

        rv = self.subscription_request(service_name)

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'account.is_test', '1', uid=uid, db='passportdbshard1')

        self.assert_statbox_entry(service_name)

    def test_subscription__resubscribe_to_existing_subscription__no_action(self):
        """При повторной подписке на уже подписанный сервис, ничего не делаем"""
        service_name = 'test'
        subscription_sid = SERVICES[service_name].sid

        blackbox_response = blackbox_userinfo_response(subscribed_to=[subscription_sid])
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        rv = self.subscription_request(service_name)

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        # В БД ничего не писали
        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        self.assert_events_are_empty(self.env.handle_mock)

    def test_update_existing_subscription(self):
        """Обновление login_rule на существующей подписке"""
        subscription = 'jabber'
        sid = SERVICES[subscription].sid

        blackbox_response = blackbox_userinfo_response(
            login='test',
            subscribed_to=[sid],
            dbfields={'subscription.login_rule.27': 1},
            attributes={'password.encrypted': '1:secret'},
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        rv = self.subscription_request(subscription, data={'login_rule': 0})

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'subscription.jabber.login_rule', '0', uid=1, db='passportdbshard1')

        names_values = {
            'action': 'subscription',
            'consumer': 'dev',
            'service': 'jabber',
            'sid.login_rule': '27|0',
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_subscription__wwwdgt__ok(self):
        """Логика сохранения host_id для sid=42"""
        service_name = 'wwwdgt'
        sid = SERVICES[service_name].sid
        host_id = 10
        uid = self.env.TEST_UID

        blackbox_response = blackbox_userinfo_response(
            unsubscribed_from=[sid],
            dbfields={'subscription.host_id.42': ''},
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        rv = self.subscription_request(service_name, data={'wmode': host_id})

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'subscription.wwwdgt.mode', str(host_id), uid=uid, db='passportdbshard1')

        self.assert_statbox_entry(service_name, **{
            'sid.wwwdgt_wmode': str(host_id),
        })

    def test_subscription__resubscribe_to_wwwdgt__update(self):
        """Повторная подписка на sid=42 обновляет значение host_id"""
        service_name = 'wwwdgt'
        sid = SERVICES[service_name].sid
        host_id = 2
        new_host_id = 10
        uid = self.env.TEST_UID

        TEST_BORN_DATE = date(2000, 1, 1)
        BORN_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
        blackbox_response = blackbox_userinfo_response(
            subscribed_to=[sid],
            dbfields={
                'subscription.host_id.%s' % sid: str(host_id),
                'subscription.born_date.%s' % sid: TEST_BORN_DATE.strftime(BORN_DATE_FORMAT),
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        self.env.db.check('attributes', 'subscription.wwwdgt.mode', str(host_id), uid=uid, db='passportdbshard1')

        rv = self.subscription_request('wwwdgt', data={'wmode': new_host_id})

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'subscription.wwwdgt.mode', str(new_host_id), uid=uid, db='passportdbshard1')

        names_values = {
            'action': 'subscription',
            'consumer': 'dev',
            'service': 'wwwdgt',
            'sid.wwwdgt_wmode': str(new_host_id),
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_subscription__yastaff__ok(self):
        """Успешная подписка на sid=669"""
        def blackbox_request(method, url, data=None, headers=None, cookies=None):
            if data and data.get('sid') == 669:
                return Mock(content=blackbox_userinfo_response(uid=None), status_code=200)
            else:
                return Mock(content=blackbox_userinfo_response(unsubscribed_from=[669]), status_code=200)

        service_name = 'yastaff'
        login = 'foo'
        uid = self.env.TEST_UID

        self.env.blackbox.set_blackbox_response_side_effect('userinfo', blackbox_request)
        self.env.db.serialize(blackbox_request('GET', '').content)

        rv = self.subscription_request(service_name, data={'yastaff_login': login})

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 1)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.env.db.check('aliases', 'yandexoid', login, uid=uid, db='passportdbcentral')

        names_values = {
            'action': 'subscription',
            'consumer': 'dev',
            'service': 'yastaff',
            'alias.yandexoid.add': 'foo',
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_subscription__yastaff__already_subscribed(self):
        """Пытаемся подписать на sid=669 уже подписанного"""
        def blackbox_request(method, url, data=None, headers=None, cookies=None):
            if 'sid=669' in url:
                return Mock(content=blackbox_userinfo_response(uid=None), status_code=200)
            else:
                return Mock(
                    status_code=200,
                    content=blackbox_userinfo_response(
                        subscribed_to=[669],
                        aliases={
                            'portal': 'test',
                            'yandexoid': 'foo',
                        },
                    ),
                )

        service_name = 'yastaff'
        login = 'foo'

        self.env.blackbox.set_blackbox_response_side_effect('userinfo', blackbox_request)
        self.env.db.serialize(blackbox_request('GET', '').content)

        rv = self.subscription_request(service_name, data={'yastaff_login': login})

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        # ничего не делали - в лог ничего не писали
        self.assert_events_are_logged(self.env.handle_mock, {})

    def test_subscription__yastaff__already_subscribed_for_another_login(self):
        """Пытаемся подписать на sid=669 уже подписанного"""
        def blackbox_request(method, url, data=None, headers=None, cookies=None):
            if 'sid=669' in url:
                return Mock(content=blackbox_userinfo_response(uid=None), status_code=200)
            else:
                return Mock(
                    status_code=200,
                    content=blackbox_userinfo_response(
                        aliases={
                            'portal': 'test',
                            'yandexoid': 'bar',
                        },
                    ),
                )

        service_name = 'yastaff'
        login = 'foo'

        self.env.blackbox.set_blackbox_response_side_effect('userinfo', blackbox_request)
        self.env.db.serialize(blackbox_request('GET', '').content)

        rv = self.subscription_request(service_name, data={'yastaff_login': login})

        eq_(rv.status_code, 400, [rv.status_code, rv.data])

        # ничего не делали - в лог ничего не писали
        self.assert_events_are_logged(self.env.handle_mock, {})

    def test_subscription__galatasaray__ok(self):
        """Успешная подписка на sid=61"""
        login = 'foo'

        service_name = 'galatasaray'
        uid = self.env.TEST_UID

        userinfo_response = blackbox_userinfo_response(login=login)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.env.db.serialize(userinfo_response)

        rv = self.subscription_request(service_name, data={})

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 1)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.env.db.check('aliases', 'altdomain', '1/%s' % login, uid=uid, db='passportdbcentral')

        names_values = {
            'action': 'subscription',
            'consumer': 'dev',
            'service': 'galatasaray',
            'alias.altdomain.add': '1/foo',
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_subscription__galatasaray__impossible(self):
        """Запрещена подписка на sid=61 для не-нормалов"""
        login = 'foo@mk.ru'

        service_name = 'galatasaray'
        uid = self.env.TEST_UID

        userinfo_response = blackbox_userinfo_response(
            login=login,
            aliases={
                'lite': login,
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.env.db.serialize(userinfo_response)

        rv = self.subscription_request(service_name, data={})

        eq_(rv.status_code, 400)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.env.db.check_missing('aliases', 'altdomain', uid=uid, db='passportdbcentral')

    def test_subscription__galatasaray__already_subscribed_ok(self):
        """Уже есть подписка на sid=61"""
        login = 'foo'

        service_name = 'galatasaray'

        userinfo_response = blackbox_userinfo_response(
            login=login,
            aliases={
                'portal': login,
                'altdomain': 'foo@galatasaray.net',
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.env.db.serialize(userinfo_response)

        rv = self.subscription_request(service_name, data={})

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        # ничего не делали - в лог ничего не писали
        self.assert_events_are_logged(self.env.handle_mock, {})

    def test_subscription___yastaff_login_occupied__error(self):
        blackbox_response = blackbox_userinfo_response(unsubscribed_from=[669])
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        rv = self.subscription_request('yastaff', data={'yastaff_login': 'foo'})

        eq_(rv.status_code, 400, [rv.status_code, rv.data])

    def test_subscription__mail_only__ok(self):
        """Подпишем пустого пользователя на mail-сервис"""
        login = 'test'
        service_name = 'mail'
        uid = self.env.TEST_UID

        blackbox_response = blackbox_userinfo_response(
            login=login, unsubscribed_from=[2, 16],
            dbfields={
                'subscription.host_id.2': '',
                'subscription.host_id.16': '',
                'subscription.suid.16': '',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        rv = self.subscription_request(service_name)

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check_missing('aliases', 'narodmail', uid=uid, db='passportdbcentral')
        self.env.db.check('suid2', 'suid', 1, uid=uid, db='passportdbcentral')

        names_values = {
            'action': 'subscription',
            'consumer': 'dev',
            'service': 'mail',
            'sid.add': '2',
            'mail.add': '1',
            'info.mail_status': '1',
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_subscription__mail_only__new_hostid__ok(self):
        """
        Подпишем пустого пользователя, попадающего в эксперимент по логину, на mail-сервис.
        При этом ему должен проставиться новый host_id.
        """
        login = 'test'
        service_name = 'mail'
        uid = self.env.TEST_UID

        blackbox_response = blackbox_userinfo_response(
            login=login, unsubscribed_from=[2, 16],
            dbfields={
                'subscription.host_id.2': '',
                'subscription.host_id.16': '',
                'subscription.suid.16': '',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        with settings_context():
            rv = self.subscription_request(service_name)

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check_missing('aliases', 'narodmail', uid=uid, db='passportdbcentral')
        self.env.db.check('suid2', 'suid', 1, uid=uid, db='passportdbcentral')

        names_values = {
            'action': 'subscription',
            'consumer': 'dev',
            'service': 'mail',
            'sid.add': '2',
            'mail.add': '1',
            'info.mail_status': '1',
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_subscribe_pdd__mobilemusic__sid(self):
        uid = self.env.TEST_PDD_UID
        blackbox_response = blackbox_userinfo_response(
            uid=uid,
            login='test@okna.ru',
            aliases={
                'pdd': 'test@okna.ru',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)
        service_name = 'mobilemusic'
        sid = SERVICES[service_name].sid

        rv = self.subscription_request(service_name, uid)

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard2'), 1)
        self.env.db.check('attributes', 'subscription.%s' % sid, '1', uid=uid, db='passportdbshard2')

        self.assert_statbox_entry(service_name)

    def test_subscribe_pdd__sid_ok__uid_instead_login(self):
        uid = self.env.TEST_PDD_UID
        blackbox_response = blackbox_userinfo_response(
            uid=uid,
            login='test@okna.ru',
            aliases={
                'pdd': 'test@okna.ru',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)
        service_name = 'lenta'
        sid = SERVICES[service_name].sid

        rv = self.subscription_request(service_name, uid)

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard2'), 1)
        self.env.db.check('attributes', 'subscription.%s' % sid, '1', uid=uid, db='passportdbshard2')

        self.assert_statbox_entry(service_name)

    def test_pdd_sid_wrong(self):
        blackbox_response = blackbox_userinfo_response(
            uid=self.env.TEST_PDD_UID,
            login='test@okna.ru',
            aliases={
                'pdd': 'test@okna.ru',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        rv = self.subscription_request('slova', self.env.TEST_PDD_UID)
        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                u'errors': [
                    {
                        'code': 'subscriptionnotallowed',
                        'field': None,
                        'message': 'Subscription to sid 14 for PDD users is not allowed',
                    },
                ],
                'status': 'error'
            },
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        self.assert_events_are_empty(self.env.handle_mock)

    def test_subscribe__lite_sid__ok(self):
        blackbox_response = blackbox_userinfo_response(
            uid=self.env.TEST_UID,
            login='test@okna.ru',
            aliases={
                'lite': 'test@okna.ru',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)
        service_name = 'disk'
        sid = SERVICES[service_name].sid
        uid = self.env.TEST_UID

        rv = self.subscription_request(service_name)

        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'subscription.%s' % sid, '1', uid=uid, db='passportdbshard1')

        self.assert_statbox_entry(service_name)

    def test_subscribe__sid_requires_login__ok(self):
        blackbox_response = blackbox_userinfo_response(login='test', unsubscribed_from=[5])
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        rv = self.subscription_request('fotki')
        eq_(rv.status_code, 200, [rv.status_code, rv.data])

    def test_sid_requires_login_error(self):
        blackbox_response = blackbox_userinfo_response(
            login='',
            aliases={
                'social': 'uid-test',
            },
            unsubscribed_from=[5],
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        rv = self.subscription_request('fotki')

        eq_(rv.status_code, 400, [rv.status_code, rv.data])

    def test_sid_requires_login_with_lite_user(self):
        blackbox_response = blackbox_userinfo_response(
            uid=self.env.TEST_UID,
            login='test@okna.ru',
            aliases={
                'lite': 'test@okna.ru',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        rv = self.subscription_request('mail')

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {u'errors': [{u'code': u'requiresaccountwithlogin',
                          u'field': None,
                          u'message': u'Subscription to sid 2 requires account with login'}],
             u'status': u'error'}
        )

    def test_sid_requires_login_with_social_user(self):
        blackbox_response = blackbox_userinfo_response(
            uid=self.env.TEST_UID,
            login='uid-aasjf375',
            aliases={
                'social': 'uid-aasjf375',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        rv = self.subscription_request('mail')

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {u'errors': [{u'code': u'requiresaccountwithlogin',
                          u'field': None,
                          u'message': u'Subscription to sid 2 requires account with login'}],
             u'status': u'error'}
        )

    def test_subscribe__sid_requires_password__ok(self):
        blackbox_response = blackbox_userinfo_response(
            login='test', unsubscribed_from=[27],
            attributes={'password.encrypted': '1:secret'},
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        rv = self.subscription_request('jabber')
        eq_(rv.status_code, 200, [rv.status_code, rv.data])

    def test_subscribe__sid_requires_password__2fa_ok(self):
        blackbox_response = blackbox_userinfo_response(
            login='test', unsubscribed_from=[27],
            attributes={
                'account.2fa_on': '1',
                'password.encrypted': '',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        rv = self.subscription_request('jabber')
        eq_(rv.status_code, 200, [rv.status_code, rv.data])

    def test_sid_requires_password_error(self):
        blackbox_response = blackbox_userinfo_response(login='test', unsubscribed_from=[27])
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        rv = self.subscription_request('jabber')
        eq_(rv.status_code, 400, [rv.status_code, rv.data])

    def test_susbcription_impossible_error(self):
        blackbox_response = blackbox_userinfo_response(login='test')
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        for subscription in ['tune', 'yandsearch', 'contest', 'mobileproxy']:
            rv = self.subscription_request(subscription)
            eq_(rv.status_code, 400, [rv.status_code, rv.data])

    def test_subscription_strongpwd_oauth_ok(self):
        blackbox_response = blackbox_userinfo_response(uid=self.env.TEST_UID, login='test.test', crypt_password='1:abc')
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)
        service_name = 'strongpwd'
        sid = SERVICES[service_name].sid
        uid = self.env.TEST_UID
        timenow = TimeNow()

        rv = self.subscription_request(service_name)
        eq_(rv.status_code, 200, [rv.status_code, rv.data])

        eq_(len(self.env.oauth.requests), 0)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('attributes', 'account.global_logout_datetime', timenow, uid=uid, db='passportdbshard1')
        self.env.db.check('attributes', 'subscription.%s' % sid, '1', uid=uid, db='passportdbshard1')

        self.assert_statbox_entry(service_name, **{
            'info.glogout': TimeNow(),
        })

    def test_subscribe_cloud_with_federal__ok(self):
        blackbox_response = blackbox_userinfo_response(
            uid=self.env.TEST_PDD_UID,
            aliases={
                'federal': '123/test',
                'pdd': 'any_login',
            },
            unsubscribed_from=[59],
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        rv = self.subscription_request('cloud')
        eq_(rv.status_code, 200, [rv.status_code, rv.data])


@with_settings_hosts(
    HUSKY_API_URL='http://localhost/',
    HUSKY_API_TIMEOUT=1,
    HUSKY_API_RETRIES=2,
)
class DeleteSubscriptionTestCase(BaseTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(
            grants={'subscription': {'mail': ['delete']}}
        ))

    def tearDown(self):
        self.env.stop()
        del self.env

    def subscription_request(self, service, uid=None):
        uid = uid or self.env.TEST_UID
        return self.env.client.delete('/1/account/%s/subscription/%s/?consumer=dev' % (uid, service))

    def setup_account(self, uid):
        blackbox_response = blackbox_userinfo_response(
            subscribed_to=[2], login='fake', unsubscribed_from=[16],
            dbfields={
                'subscription.login.2': 'fake1',
                'subscription.suid.2': '999',
                'subscription.host_id.16': '',
            },
            attributes={
                'subscription.mail.status': '1',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)
        self.env.db.insert('aliases', uid=1, type=ALT['mail'], value='fake1', db='passportdbcentral')
        self.env.db.check('suid2', 'suid', 999, uid=uid, db='passportdbcentral')

    def check_db_ok(self, uid):
        # Удалена запись из suid2 и из aliases
        eq_(self.env.db.query_count('passportdbcentral'), 3)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

        self.env.db.check_missing('suid2', 'suid', uid=uid, db='passportdbcentral')
        self.env.db.check_missing('aliases', 'mail', uid=uid, db='passportdbcentral')
        self.env.db.check('removed_aliases', 'mail', 'fake1', uid=uid, db='passportdbcentral')

    def check_events_are_logged(self):
        names_values = {
            'action': 'delete_subscription',
            'consumer': 'dev',
            'service': 'mail',
            'sid.rm': '2|fake1',
            'sid.rm.info': '1|fake1|999',
            'mail.rm': '999',
            'info.mail_status': '-',
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_unsubscribe__mail_only__ok(self):
        uid = self.env.TEST_UID
        self.setup_account(uid)
        self.env.husky_api.set_response_value('delete_user', husky_delete_user_response())
        rv = self.subscription_request('mail')
        eq_(rv.status_code, 200, rv.data)

        self.check_db_ok(uid)
        eq_(len(self.env.husky_api.requests), 1)
        self.check_events_are_logged()

    def test_unsubscribe_mail_husky_task_exists__ok(self):
        uid = self.env.TEST_UID
        self.setup_account(uid)
        self.env.husky_api.set_response_value('delete_user', husky_delete_user_response(status='error', code=4))

        rv = self.subscription_request('mail')
        eq_(rv.status_code, 200, rv.data)

        self.check_db_ok(uid)
        self.check_events_are_logged()
        eq_(len(self.env.husky_api.requests), 1)

    def test_unsubscribe_mail_husky_temporary__error(self):
        self.setup_account(self.env.TEST_UID)
        self.env.husky_api.set_response_value('delete_user', husky_delete_user_response(status='error'))

        rv = self.subscription_request('mail')
        eq_(rv.status_code, 500)
        eq_(
            json.loads(rv.data),
            {
                u'errors': [
                    {
                        'code': 'backend.husky_failed',
                        'field': None,
                        'message': 'Husky API failed',
                    },
                ],
                'status': 'error'
            },
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        self.assert_events_are_empty(self.env.handle_mock)
        eq_(len(self.env.husky_api.requests), 2)

    def test_unsubscribe_mail_husky_permanent__error(self):
        self.setup_account(self.env.TEST_UID)
        self.env.husky_api.set_response_value('delete_user', husky_delete_user_response(status='error', code=10))

        rv = self.subscription_request('mail')
        eq_(rv.status_code, 500)
        eq_(
            json.loads(rv.data),
            {
                u'errors': [
                    {
                        'code': 'backend.husky_failed',
                        'field': None,
                        'message': 'Husky API failed',
                    },
                ],
                'status': 'error'
            },
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        self.assert_events_are_empty(self.env.handle_mock)
        eq_(len(self.env.husky_api.requests), 1)

    def test_unsubscribe__mail_and_narodmail__ok(self):
        """Отписка от почты и как следствие и от 'почты на народе'"""
        uid = self.env.TEST_UID
        blackbox_response = blackbox_userinfo_response(
            subscribed_to=[2, 16], login='fake',
            dbfields={
                'subscription.suid.2': '999',
                'subscription.login.2': 'mail_login',
                'subscription.host_id.16': '7',
                'subscription.login.16': 'narodmail_login',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.husky_api.set_response_value('delete_user', husky_delete_user_response())
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
        self.env.db.check('suid2', 'suid', 999, uid=uid, db='passportdbcentral')

        rv = self.subscription_request('mail')
        eq_(rv.status_code, 200, rv.data)

        eq_(self.env.db.query_count('passportdbcentral'), 3)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check_missing('aliases', 'mail', uid=uid, db='passportdbcentral')
        self.env.db.check_missing('aliases', 'narodmail', uid=uid, db='passportdbcentral')
        self.env.db.check('removed_aliases', 'mail', 'mail_login', uid=uid, db='passportdbcentral')
        self.env.db.check('removed_aliases', 'narodmail', 'narodmail_login', uid=uid, db='passportdbcentral')

        names_values = {
            'action': 'delete_subscription',
            'consumer': 'dev',
            'service': 'mail',
            'sid.rm': '16|narodmail_login,2|mail_login',
            'sid.rm.info': '1|mail_login|999',
            'mail.rm': '999',
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)
        eq_(len(self.env.husky_api.requests), 1)

    def test_unsubscribe__yastaff__ok(self):
        uid = self.env.TEST_UID

        self.env.grants.set_grants_return_value(mock_grants(
            grants={'subscription': {'yastaff': ['delete']}}
        ))
        blackbox_response = blackbox_userinfo_response(
            uid=self.env.TEST_UID,
            aliases={
                'portal': 'test',
                'yandexoid': 'yastaff_login',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        self.env.db.check('aliases', 'yandexoid', 'yastaff_login', uid=uid, db='passportdbcentral')

        rv = self.subscription_request('yastaff')
        eq_(rv.status_code, 200, rv.data)

        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.env.db.check('removed_aliases', 'yandexoid', 'yastaff_login', uid=uid, db='passportdbcentral')
        self.env.db.check_missing('aliases', 'yandexoid', uid=uid, db='passportdbcentral')

        names_values = {
            'action': 'delete_subscription',
            'alias.yandexoid.rm': 'yastaff_login',
            'consumer': 'dev',
            'service': 'yastaff',
        }
        self.assert_events_are_logged(self.env.handle_mock, names_values)

    def test_unsubscribe__missing_subscription__error(self):
        blackbox_response = blackbox_userinfo_response()
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        rv = self.subscription_request('mail')
        eq_(rv.status_code, 404, rv.data)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        self.assert_events_are_empty(self.env.handle_mock)

    def test_unsubscribe_galatasaray(self):
        """
        Молча не отписываем
        """
        uid = self.env.TEST_UID

        self.env.grants.set_grants_return_value(mock_grants(
            grants={'subscription': {'galatasaray': ['delete']}}
        ))
        blackbox_response = blackbox_userinfo_response(
            uid=self.env.TEST_UID,
            aliases={
                'portal': 'test',
                'altdomain': 'test@galatasaray.net',
            },
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        self.env.db.check('aliases', 'altdomain', '1/test', uid=uid, db='passportdbcentral')

        rv = self.subscription_request('galatasaray')
        eq_(rv.status_code, 200, rv.data)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.env.db.check('aliases', 'altdomain', '1/test', uid=uid, db='passportdbcentral')
        self.env.db.check_missing('removed_aliases', 'altdomain', uid=uid, db='passportdbcentral')

        self.assert_events_are_empty(self.env.handle_mock)

    def test_unsubscribe_mailpro_with_pdd_alias__ok(self):
        self.env.grants.set_grants_return_value(mock_grants(
            grants={'subscription': {'mailpro': ['delete']}}
        ))
        blackbox_response = blackbox_userinfo_response(
            uid=self.env.TEST_UID,
            aliases={
                'portal': 'test',
                'pdd': 'any_login',
            },
            subscribed_to=[122, 8]
        )
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        rv = self.subscription_request('mailpro')
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok'
            },
        )

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

        names_values = {'action': 'delete_subscription', 'sid.rm': '122|test', 'service': 'mailpro', 'consumer': 'dev'}
        self.assert_events_are_logged(self.env.handle_mock, names_values)
