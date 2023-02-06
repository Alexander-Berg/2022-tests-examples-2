# -*- coding: utf-8 -*-
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_ACCOUNT_DATA,
    TEST_BLACKBOX_RESPONSE_ACCOUNT_DATA,
    TEST_DEFAULT_RETPATH,
    TEST_DISPLAY_NAME_DATA,
    TEST_DOMAIN_ID,
    TEST_HOST,
    TEST_LOGIN,
    TEST_MAIL_SERVICE,
    TEST_MAIL_SID,
    TEST_PDD_ACCOUNT_DOMAIN_DATA,
    TEST_PDD_LOGIN,
    TEST_RETPATH,
    TEST_SOCIAL_DISPLAY_NAME,
    TEST_SOCIAL_LOGIN,
    TEST_SUID,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.services import get_service
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import merge_dicts


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    PASSPORT_SUBDOMAIN='passport-test',
)
class SubscribeViewTestCase(BaseBundleTestViews):
    default_url = '/1/bundle/account/subscribe/?consumer=dev'
    http_method = 'post'
    http_query_args = dict(
        service=TEST_MAIL_SERVICE.slug,
        retpath=TEST_RETPATH,
    )
    http_headers = dict(
        host=TEST_HOST,
        user_agent=TEST_USER_AGENT,
        cookie=TEST_USER_COOKIE,
        user_ip=TEST_USER_IP,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'account': ['subscribe'],
                },
            ),
        )
        self.setup_bb_response()
        self.setup_statbox_templates()

    def setup_bb_response(self, account_data=None, serialize=False):
        account_data = merge_dicts(
            TEST_BLACKBOX_RESPONSE_ACCOUNT_DATA,
            account_data or {},
        )
        sessionid_data = blackbox_sessionid_multi_response(
            **account_data
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_data,
        )
        if serialize:
            self.env.db.serialize_sessionid(sessionid_data)

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='subscribe',
            consumer='dev',
        )
        self.env.statbox.bind_entry(
            'local_base',
            uid=str(TEST_UID),
            sid=str(TEST_MAIL_SID),
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
        )
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from=['local_base'],
            action='submitted',
        )
        self.env.statbox.bind_entry(
            'subscriptions',
            _inherit_from=['subscriptions', 'local_base'],
            _exclude=['mode'],
            consumer='-',
            operation='added',
            suid=str(TEST_SUID),
        )

    def get_response_data(self, account_kwargs=None, **kwargs):
        data = {'account': merge_dicts(TEST_ACCOUNT_DATA['account'], account_kwargs or {})}
        data.update(
            service=TEST_MAIL_SERVICE.slug,
            retpath=TEST_RETPATH,
        )
        return merge_dicts(data, kwargs)

    def assert_statbox_ok(self, exclude=None, fields=None, finished=True, with_check_cookies=False):
        fields = fields or {}
        sid = fields.get('sid', TEST_MAIL_SID)
        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(self.env.statbox.entry('submitted', sid=str(sid)))
        if finished:
            if sid == TEST_MAIL_SID:
                entries.append(
                    self.env.statbox.entry(
                        'local_base',
                        _exclude=['mode', 'sid'],
                        event='account_modification',
                        consumer='-',
                        operation='created',
                        entity='account.mail_status',
                        old='-',
                        new='active',
                    ),
                )
            entries.append(
                self.env.statbox.entry(
                    'subscriptions',
                    _exclude=exclude or [],
                    **fields
                ),
            )
        self.env.statbox.assert_has_written(entries)

    def assert_historydb_ok(self, service=TEST_MAIL_SERVICE, exclude=None, **event_lines):
        exclude = exclude or []
        expected_entries = {
            'action': 'subscribe',
            'user_agent': 'curl',
            'from': service.slug,
            'sid.add': str(service.sid),
        }
        expected_entries = dict(expected_entries, **event_lines)
        for line in exclude:
            expected_entries.pop(line)
        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_entries,
        )

    def check_db_alias(self, value=None, check_missing=False, central_count=1):
        alias_name = 'altdomain'
        value = value or '1/%s' % TEST_LOGIN
        table = 'aliases'
        db = 'passportdbcentral'
        self.env.db.check_query_counts(central=central_count)
        if check_missing:
            self.env.db.check_missing(table, alias_name, uid=TEST_UID, db=db)
        else:
            self.env.db.check(table, alias_name, value, db=db)

    def check_db_subscription(self, service_name='mail.host_id', value='1111', check_missing=False,
                              central_count=0, shard_count=1, subscription_attr=None):
        subscription_attr=subscription_attr or ('subscription.%s' % service_name)
        self.env.db.check_query_counts(central=central_count, shard=shard_count)
        if check_missing:
            self.env.db.check_db_attr_missing(uid=TEST_UID, attr_name=subscription_attr)
        else:
            self.env.db.check_db_attr(TEST_UID, subscription_attr, value)

    def test_subscribe_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=1),
        )
        resp = self.make_request()
        self.assert_ok_response(resp, **self.get_response_data())
        self.check_db_subscription(subscription_attr='subscription.mail.status', value='1', central_count=2, shard_count=1)
        self.assert_statbox_ok(with_check_cookies=True)
        self.assert_historydb_ok(**{
            'mail.add': '1',
            'info.mail_status': '1',
        })

    def test_subscribe_protected_error(self):
        service = get_service(slug='tune')
        resp = self.make_request(query_args={'service': service.slug})
        self.assert_error_response(
            resp,
            ['subscription.forbidden'],
            **self.get_response_data(service=service.slug)
        )
        self.check_db_subscription(
            service_name=service.slug,
            check_missing=True,
            shard_count=0,
        )
        self.assert_statbox_ok(finished=False, fields={'sid': str(service.sid)}, with_check_cookies=True)
        self.assert_events_are_empty(self.env.handle_mock)

    def test_subscribe_to_mail_with_occupied_login(self):
        # uid в ответе userinfo при поиске по логину для сида 2 не равен текущему, значит логин занят кем-то другим
        self.setup_bb_response(
            account_data=dict(
                login=TEST_LOGIN,
                display_name=TEST_DISPLAY_NAME_DATA,
                subscribed_to=[58],
                aliases={
                    'portal': TEST_LOGIN,
                    'mail': TEST_LOGIN + '_mail',
                },
            ),
        )
        expected_response = self.get_response_data(
            account_kwargs={
                'display_login': TEST_LOGIN,
                'login': TEST_LOGIN,
                'display_name': TEST_DISPLAY_NAME_DATA,
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=2),
        )
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['subscription.blocked'],
            **expected_response
        )
        userinfo_request = self.env.blackbox.requests[-1]
        userinfo_request.assert_post_data_contains({
            'method': 'userinfo',
            'login': TEST_LOGIN + '_mail',
        })
        self.check_db_subscription(subscription_attr='subscription.mail.status', value='1', check_missing=True, shard_count=0)
        self.assert_statbox_ok(finished=False, with_check_cookies=True)
        self.assert_events_are_empty(self.env.handle_mock)

    def test_subscribe_no_login_error(self):
        self.setup_bb_response(
            account_data=dict(
                display_name=TEST_SOCIAL_DISPLAY_NAME,
                login=TEST_SOCIAL_LOGIN,
                subscribed_to=[58],
                aliases={
                    'social': TEST_SOCIAL_LOGIN,
                },
            ),
        )
        expected_response = self.get_response_data(
            account_kwargs={
                'display_login': '',
                'login': TEST_SOCIAL_LOGIN,
                'display_name': TEST_SOCIAL_DISPLAY_NAME,
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=1),
        )
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['account.without_login'],
            **expected_response
        )
        self.check_db_subscription(subscription_attr='subscription.mail.status', value='1', check_missing=True, shard_count=0)
        self.assert_statbox_ok(finished=False, with_check_cookies=True)
        self.assert_events_are_empty(self.env.handle_mock)

    def test_subscribe_no_pwd_error(self):
        service = get_service(slug='balance')
        self.setup_bb_response(account_data=dict(have_password=False))
        resp = self.make_request(query_args={'service': service.slug})
        self.assert_error_response(
            resp,
            ['account.without_password'],
            **self.get_response_data(service=service.slug)
        )
        self.check_db_subscription(subscription_attr='subscription.mail.status', value='1', check_missing=True, shard_count=0)
        self.assert_statbox_ok(finished=False, fields={'sid': str(service.sid)}, with_check_cookies=True)
        self.assert_events_are_empty(self.env.handle_mock)

    def test_subscribe_with_2fa_ok(self):
        service = get_service(slug='balance')
        self.setup_bb_response(
            account_data=dict(
                attributes={
                    'account.2fa_on': '1',
                },
            ),
        )
        resp = self.make_request(query_args={'service': service.slug})
        self.assert_ok_response(
            resp,
            **self.get_response_data(
                account_kwargs={'is_2fa_enabled': True},
                service=service.slug,
            )
        )
        self.check_db_subscription(service_name=service.slug, value='1')
        self.assert_statbox_ok(exclude=['suid'], fields={'sid': str(service.sid)}, with_check_cookies=True)
        self.assert_historydb_ok(service=service)

    def test_subscribe_pdd_allowed_ok(self):
        service = get_service(slug='calendar')
        self.setup_bb_response(
            account_data=dict(
                login=TEST_PDD_LOGIN,
                domid=TEST_DOMAIN_ID,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
            ),
        )
        expected_response = self.get_response_data(
            account_kwargs={
                'display_login': TEST_PDD_LOGIN,
                'login': TEST_PDD_LOGIN,
                'domain': TEST_PDD_ACCOUNT_DOMAIN_DATA,
                'domain_id': TEST_DOMAIN_ID,
            },
            service=service.slug,
        )
        resp = self.make_request(query_args={'service': service.slug})
        self.assert_ok_response(resp, **expected_response)
        self.check_db_subscription(service_name=str(service.sid), value='1')
        self.assert_statbox_ok(exclude=['suid'], fields={'sid': str(service.sid)}, with_check_cookies=True)
        self.assert_historydb_ok(service=service)

    def test_subscribe_pdd_forbidden_error(self):
        service = get_service(slug='pi')
        self.setup_bb_response(
            account_data=dict(
                login=TEST_PDD_LOGIN,
                domid=1,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
            ),
        )
        expected_response = self.get_response_data(
            account_kwargs={
                'display_login': TEST_PDD_LOGIN,
                'login': TEST_PDD_LOGIN,
                'domain': TEST_PDD_ACCOUNT_DOMAIN_DATA,
                'domain_id': TEST_DOMAIN_ID,
            },
            service=service.slug,
        )
        resp = self.make_request(query_args={'service': service.slug})
        self.assert_error_response(
            resp,
            ['subscription.forbidden'],
            **expected_response
        )
        self.check_db_subscription(
            service_name=service.slug,
            check_missing=True,
            shard_count=0,
        )
        self.assert_statbox_ok(finished=False, fields={'sid': str(service.sid)}, with_check_cookies=True)
        self.assert_events_are_empty(self.env.handle_mock)

    def test_subscribe_unknown_service_ok(self):
        resp = self.make_request(query_args={'service': 'thug'})
        expected_resp = {
            'retpath': TEST_DEFAULT_RETPATH,
        }
        self.assert_ok_response(resp, **expected_resp)
        self.env.db.check_query_counts()
        self.env.statbox.assert_has_written([])
        self.assert_events_are_empty(self.env.handle_mock)

    def test_account_disabled_on_deletion_error(self):
        self.setup_bb_response(
            account_data=dict(
                enabled=False,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled_on_deletion'])
        self.env.db.check_query_counts()
        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')])
        self.assert_events_are_empty(self.env.handle_mock)

    def test_account_disabled_error(self):
        self.setup_bb_response(account_data=dict(enabled=False))
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled'])
        self.check_db_subscription(subscription_attr='subscription.mail.status', value='1', check_missing=True, shard_count=0)
        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')])
        self.assert_events_are_empty(self.env.handle_mock)

    def test_already_subscribed_ok(self):
        service = get_service(slug='afisha')
        self.setup_bb_response(
            account_data=dict(subscribed_to=[30]),
            serialize=True,
        )
        resp = self.make_request(query_args={'service': service.slug})
        self.assert_ok_response(resp, **self.get_response_data(service=service.slug))
        self.assert_statbox_ok(finished=False, fields={'sid': str(service.sid)}, with_check_cookies=True)
        self.check_db_subscription(
            service_name=str(service.sid),
            shard_count=0,
            value='1',
        )
        self.assert_events_are_empty(self.env.handle_mock)

    def test_already_subscribed_blocked_error(self):
        service = get_service(slug='jabber')
        self.setup_bb_response(
            account_data=dict(
                subscribed_to=[27],
                dbfields={
                    'subscription.login_rule.27': 0,
                },
            ),
            serialize=True,
        )
        resp = self.make_request(query_args={'service': service.slug})
        self.assert_error_response(
            resp,
            ['subscription.blocked'],
            **self.get_response_data(service=service.slug)
        )
        self.check_db_subscription(
            service_name=str(service.sid),
            shard_count=0,
            value='1',
        )
        self.assert_statbox_ok(finished=False, fields={'sid': str(service.sid)}, with_check_cookies=True)
        self.assert_events_are_empty(self.env.handle_mock)

    def test_galatasaray_already_subscribed_ok(self):
        service = get_service(slug='galatasaray')
        self.setup_bb_response(
            account_data=dict(
                aliases={
                    'portal': TEST_LOGIN,
                    'altdomain': 'login@galatasaray.net',
                },
            ),
            serialize=True,
        )
        resp = self.make_request(query_args={'service': service.slug})
        self.assert_ok_response(resp, **self.get_response_data(service=service.slug))
        self.check_db_alias(central_count=0)
        self.assert_statbox_ok(finished=False, fields={'sid': str(service.sid)}, with_check_cookies=True)
        self.assert_events_are_empty(self.env.handle_mock)

    def test_subscribe_galatasaray_ok(self):
        service = get_service(slug='galatasaray')
        resp = self.make_request(query_args={'service': service.slug})
        self.assert_ok_response(resp, **self.get_response_data(service=service.slug))
        self.check_db_alias()
        self.assert_statbox_ok(exclude=['suid'], fields={'sid': str(service.sid)}, with_check_cookies=True)
        self.assert_historydb_ok(
            service=service,
            exclude=['sid.add'],
            **{'alias.altdomain.add': '1/login'}
        )

    def test_subscribe_galatasaray_social_error(self):
        service = get_service(slug='galatasaray')
        self.setup_bb_response(
            account_data=dict(
                login=TEST_SOCIAL_LOGIN,
                aliases={
                    'social': TEST_SOCIAL_LOGIN,
                },
            ),
        )
        resp = self.make_request(query_args={'service': service.slug})
        expected_response = self.get_response_data(
            account_kwargs={
                'display_login': '',
                'login': TEST_SOCIAL_LOGIN,
            },
            service=service.slug,
        )
        self.assert_error_response(resp, ['subscription.forbidden'], **expected_response)
        self.check_db_alias(value='1/%s' % TEST_SOCIAL_LOGIN, check_missing=True, central_count=0)
        self.assert_statbox_ok(finished=False, fields={'sid': str(service.sid)}, with_check_cookies=True)
        self.assert_events_are_empty(self.env.handle_mock)
