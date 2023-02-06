# -*- coding: utf-8 -*-
import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.register.test import StatboxTestMixin
from passport.backend.api.tests.views.bundle.register.test.base_test_data import (
    TEST_DEVICE_NAME,
    TEST_HOST,
    TEST_UID,
    TEST_USER_IP,
)
from passport.backend.api.tests.views.bundle.test_base_data import TEST_AUTH_HEADER
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_loginoccupation_response,
    blackbox_oauth_response,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.builders.oauth.faker import (
    oauth_bundle_error_response,
    oauth_bundle_successful_response,
)
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ANT
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)


eq_ = iterdiff(eq_)

TEST_KOLONKISH_LOGIN = 'kolonkish-123'
TEST_KOLONKA_CLIENT_ID = 'id'
TEST_KOLONKA_CLIENT_SECRET = 'secret'

TEST_CREATOR_UID = TEST_UID * 2
TEST_CREATOR_LOGIN = 'vasya.pupkin'

TEST_CODE = 'code' * 4
TEST_SCOPE = 'kolonka:scope'

TEST_DEVICE_ID = 'foobar'


class BaseAccountRegisterKolonkish(BaseBundleTestViews, StatboxTestMixin):
    consumer = 'dev'
    default_url = '/1/bundle/account/register/kolonkish/'
    http_method = 'POST'
    http_query_args = {
        'device_id': TEST_DEVICE_ID,
        'device_name': TEST_DEVICE_NAME,
    }
    http_headers = {
        'user_ip': TEST_USER_IP,
        'authorization': TEST_AUTH_HEADER,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.patches.append(
            mock.patch('passport.backend.core.types.login.login.generate_kolonkish_login', mock.Mock(return_value=TEST_KOLONKISH_LOGIN)),
        )
        self.env.start()
        self.env.grants.set_grants_return_value(
            mock_grants(grants={'account': ['register_kolonkish']}),
        )
        self.setup_statbox_templates()
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_KOLONKISH_LOGIN: 'free'}),
        )
        self.env.oauth.set_response_value(
            'issue_authorization_code',
            oauth_bundle_successful_response(code=TEST_CODE, expires_in=600),
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(uid=TEST_CREATOR_UID, login=TEST_CREATOR_LOGIN, scope=TEST_SCOPE),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(uid=TEST_CREATOR_UID, login=TEST_CREATOR_LOGIN),
        )

    def tearDown(self):
        self.env.stop()
        del self.env

    def assert_db_empty(self, shard='passportdbshard1'):
        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count(shard), 0)

    def assert_db_ok(self, uid=TEST_UID, creator_uid=str(TEST_CREATOR_UID), display_name=None, shard='passportdbshard1'):
        time_now = TimeNow()

        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count(shard), 1)

        self.env.db.check('aliases', 'kolonkish', TEST_KOLONKISH_LOGIN, uid=uid, db='passportdbcentral')
        self.env.db.check('attributes', 'account.registration_datetime', time_now, uid=uid, db=shard)
        self.env.db.check('attributes', 'account.creator_uid', creator_uid, uid=uid, db=shard)

        for attribute in ('person.firstname', 'person.lastname', 'person.gender', 'person.city',
                          'person.birthday', 'person.country', 'person.language', 'person.timezone'):
            self.env.db.check_missing('attributes', attribute, uid=uid, db=shard)

        if display_name is not None:
            self.env.db.check('attributes', 'account.display_name', display_name, uid=uid, db=shard)
        else:
            self.env.db.check_missing('attributes', 'account.display_name', uid=uid, db=shard)

        self.env.db.check_missing('attributes', 'password.quality', uid=uid, db=shard)
        self.env.db.check_missing('attributes', 'password.encrypted', uid=uid, db=shard)
        self.env.db.check_missing('attributes', 'password.update_datetime', uid=uid, db=shard)

        self.env.db.check_missing('attributes', 'karma.value', uid=uid, db=shard)

    def assert_historydb_empty(self):
        self.assert_events_are_empty(self.env.handle_mock)

    def assert_historydb_ok(self, display_name=None):
        events = {
            'info.login': TEST_KOLONKISH_LOGIN,
            'info.ena': '1',
            'info.disabled_status': '0',
            'info.reg_date': DatetimeNow(convert_to_datetime=True),
            'info.karma_prefix': '0',
            'info.karma_full': '0',
            'info.karma': '0',
            'alias.kolonkish.add': TEST_KOLONKISH_LOGIN,
            'account.creator_uid': str(TEST_CREATOR_UID),
            'action': 'account_register_kolonkish',
            'consumer': 'dev',
        }
        if display_name is not None:
            events['info.display_name'] = display_name
        self.assert_events_are_logged(
            self.env.handle_mock,
            events,
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='account_register_kolonkish',
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'account_modification_base',
            event='account_modification',
            uid=str(TEST_UID),
            consumer='dev',
            ip=TEST_USER_IP,
            user_agent='-',
        )
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from='local_base',
            _exclude=['uid'],
            action='submitted',
        )
        self.env.statbox.bind_entry(
            'disabled_status_set',
            _inherit_from='account_modification_base',
            _exclude=['mode'],
            entity='account.disabled_status',
            operation='created',
            old='-',
            new='enabled',
        )
        self.env.statbox.bind_entry(
            'display_name_set',
            _inherit_from='account_modification_base',
            _exclude=['mode'],
            entity='person.display_name',
            operation='created',
            old='-',
        )
        self.env.statbox.bind_entry(
            'kolonkish_alias_added',
            _inherit_from='account_modification_base',
            _exclude=['old', 'mode'],
            entity='aliases',
            operation='added',
            type=str(ANT['kolonkish']),
            value=TEST_KOLONKISH_LOGIN,
        )
        self.env.statbox.bind_entry(
            'account_modification_karma',
            _inherit_from='account_modification_base',
            _exclude=['mode'],
            entity='karma',
            action='account_register_kolonkish',
            destination='frodo',
            old='-',
            new='0',
            suid='-',
            login=TEST_KOLONKISH_LOGIN,
            registration_datetime=DatetimeNow(convert_to_datetime=True),
        )
        self.env.statbox.bind_entry(
            'account_created',
            _inherit_from='local_base',
            action='account_created',
            login=TEST_KOLONKISH_LOGIN,
        )
        self.env.statbox.bind_entry(
            'oauth_code_issued',
            _inherit_from='local_base',
            action='oauth_code_issued',
            uid=str(TEST_UID),
            client_id=TEST_KOLONKA_CLIENT_ID,
        )

    def assert_statbox_empty(self):
        self.env.statbox.assert_has_written([])

    def assert_statbox_ok(
        self, display_name=None,
        token_created=True, with_extra_params=True,
        with_check_cookies=False
    ):
        events = [self.env.statbox.entry('submitted')]
        if with_check_cookies:
            events.append(self.env.statbox.entry('check_cookies', host='yandex.ru'))
        events.extend(
            [
                self.env.statbox.entry('disabled_status_set'),
                self.env.statbox.entry('kolonkish_alias_added'),
            ]
        )
        if display_name is not None:
            events.append(self.env.statbox.entry('display_name_set', new=display_name))
        events += [
            self.env.statbox.entry('account_modification_karma'),
            self.env.statbox.entry('account_created'),
        ]
        if token_created:
            if with_extra_params:
                events.append(
                    self.env.statbox.entry(
                        'oauth_code_issued',
                        device_id=TEST_DEVICE_ID,
                        device_name=TEST_DEVICE_NAME,
                    ),
                )
            else:
                events.append(
                    self.env.statbox.entry('oauth_code_issued'),
                )
        self.env.statbox.assert_has_written(events)

    def assert_oauth_not_called(self):
        ok_(not self.env.oauth.requests)

    def assert_oauth_called(self, with_extra_params=True):
        expected_post = {
            'consumer': 'passport',
            'code_strength': 'long',
            'ttl': 600,
            'require_activation': '0',
            'uid': str(TEST_UID),
            'by_uid': '1',
            'client_id': TEST_KOLONKA_CLIENT_ID,
            'client_secret': TEST_KOLONKA_CLIENT_SECRET,
        }
        expected_query = {'user_ip': TEST_USER_IP}
        if with_extra_params:
            expected_query['device_id'] = TEST_DEVICE_ID
            expected_query['device_name'] = TEST_DEVICE_NAME

        self.env.oauth.requests[0].assert_post_data_equals(expected_post)
        self.env.oauth.requests[0].assert_query_equals(expected_query)


@with_settings_hosts(
    OAUTH_URL='http://oauth.localhost',
    OAUTH_KOLONKA_KOLONKISH_SCOPE=TEST_SCOPE,
    OAUTH_KOLONKA_CODE_TTL=600,
    OAUTH_APPLICATION_KOLONKA={
        'client_id': TEST_KOLONKA_CLIENT_ID,
        'client_secret': TEST_KOLONKA_CLIENT_SECRET,
    },
    **mock_counters(
        REGISTRATION_KOLONKISH_PER_CREATOR_UID_SHORT_TERM=(1, 300, 1),  # проверяем этот счётчик
        REGISTRATION_KOLONKISH_PER_CREATOR_UID_LONG_TERM=(1, 300, 1000),  # а этот нет, поэтому значение 1000
    )
)
class AccountRegisterKolonkishShortTermCounterTestViews(BaseAccountRegisterKolonkish):
    def test_hit_short_term_limit(self):
        rv = self.make_request()

        self.assert_ok_response(rv, uid=1, code=TEST_CODE, login=TEST_KOLONKISH_LOGIN)
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.assert_statbox_ok()
        self.assert_oauth_called()

        # повторяем запрос, но ожидаем перегрева счётчиков
        rv = self.make_request()

        self.assert_error_response(rv, ['rate.limit_exceeded'])


@with_settings_hosts(
    OAUTH_URL='http://oauth.localhost',
    OAUTH_KOLONKA_KOLONKISH_SCOPE=TEST_SCOPE,
    OAUTH_KOLONKA_CODE_TTL=600,
    OAUTH_APPLICATION_KOLONKA={
        'client_id': TEST_KOLONKA_CLIENT_ID,
        'client_secret': TEST_KOLONKA_CLIENT_SECRET,
    },
    **mock_counters(
        REGISTRATION_KOLONKISH_PER_CREATOR_UID_LONG_TERM=(1, 300, 1),  # проверяем этот счётчик
        REGISTRATION_KOLONKISH_PER_CREATOR_UID_SHORT_TERM=(1, 300, 1000),  # а этот нет, поэтому значение 1000
    )
)
class AccountRegisterKolonkishLongTermCounterTestViews(BaseAccountRegisterKolonkish):
    def test_hit_long_term_limit(self):
        rv = self.make_request()

        self.assert_ok_response(rv, uid=1, code=TEST_CODE, login=TEST_KOLONKISH_LOGIN)
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.assert_statbox_ok()
        self.assert_oauth_called()

        # повторяем запрос, но ожидаем перегрева счётчиков
        rv = self.make_request()

        self.assert_error_response(rv, ['rate.limit_exceeded'])


@with_settings_hosts(
    OAUTH_URL='http://oauth.localhost',
    OAUTH_KOLONKA_KOLONKISH_SCOPE=TEST_SCOPE,
    OAUTH_KOLONKA_CODE_TTL=600,
    OAUTH_APPLICATION_KOLONKA={
        'client_id': TEST_KOLONKA_CLIENT_ID,
        'client_secret': TEST_KOLONKA_CLIENT_SECRET,
    },
    **mock_counters(
        REGISTRATION_KOLONKISH_PER_CREATOR_UID_SHORT_TERM=(1, 300, 1000),
        REGISTRATION_KOLONKISH_PER_CREATOR_UID_LONG_TERM=(1, 300, 1000),
    )
)
class AccountRegisterKolonkishTestViews(BaseAccountRegisterKolonkish):
    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(rv, uid=1, code=TEST_CODE, login=TEST_KOLONKISH_LOGIN)
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.assert_statbox_ok()
        self.assert_oauth_called()

    def test_with_cookie(self):
        rv = self.make_request(
            exclude_headers=['authorization'],
            headers={'cookie': 'Session_id=foo;', 'host': TEST_HOST},
        )

        self.assert_ok_response(rv, uid=1, code=TEST_CODE, login=TEST_KOLONKISH_LOGIN)
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.assert_statbox_ok(with_check_cookies=True)
        self.assert_oauth_called()

    def test_ok_no_device_id_and_name(self):
        rv = self.make_request(exclude_args=['device_id', 'device_name'])

        self.assert_ok_response(rv, uid=1, code=TEST_CODE, login=TEST_KOLONKISH_LOGIN)
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.assert_statbox_ok(with_extra_params=False)
        self.assert_oauth_called(with_extra_params=False)

    def test_ok_with_display_name(self):
        rv = self.make_request(query_args=dict(display_name='Vasya'))

        self.assert_ok_response(rv, uid=1, code=TEST_CODE, login=TEST_KOLONKISH_LOGIN)
        self.assert_db_ok(display_name='p:Vasya')
        self.assert_historydb_ok(display_name='p:Vasya')
        self.assert_statbox_ok(display_name='p:Vasya')
        self.assert_oauth_called()

    def test_oauth_failed(self):
        self.env.oauth.set_response_value(
            'issue_authorization_code',
            oauth_bundle_error_response('backend.failed'),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['backend.oauth_failed'])
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.assert_statbox_ok(token_created=False)
        self.assert_oauth_called()

    def test_invalid_account_type(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_CREATOR_UID,
                login=TEST_CREATOR_LOGIN,
                scope=TEST_SCOPE,
                aliases={
                    'phonish': 'phne-123',
                },
            ),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['account.invalid_type'])
        self.assert_db_empty()
        self.assert_historydb_empty()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
        ])
        self.assert_oauth_not_called()

    def test_user_ip_required(self):
        rv = self.make_request(exclude_headers=['user_ip'])

        self.assert_error_response(rv, ['ip.empty'])
        self.assert_db_empty()
        self.assert_historydb_empty()
        self.assert_statbox_empty()
        self.assert_oauth_not_called()
