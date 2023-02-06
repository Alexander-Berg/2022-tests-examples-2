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
    TEST_TOKEN,
    TEST_UID,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_loginoccupation_response
from passport.backend.core.builders.oauth.faker import token_response
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ANT
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)


eq_ = iterdiff(eq_)

TEST_LOGIN = 'yambot-bot'
TEST_YAMBOT_CLIENT_ID = 'id'
TEST_YAMBOT_CLIENT_SECRET = 'secret'


@with_settings_hosts(
    OAUTH_APPLICATION_YAMB={
        'client_id': TEST_YAMBOT_CLIENT_ID,
        'client_secret': TEST_YAMBOT_CLIENT_SECRET,
    },
)
class AccountRegisterYambotTestViews(BaseBundleTestViews, StatboxTestMixin):
    consumer = 'dev'
    default_url = '/1/bundle/account/register/yambot/'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_USER_IP,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.patches.append(
            mock.patch('passport.backend.core.types.login.login.generate_yambot_login', mock.Mock(return_value=TEST_LOGIN)),
        )
        self.env.start()
        self.env.grants.set_grants_return_value(
            mock_grants(grants={'account': ['register_yambot']}),
        )
        self.setup_statbox_templates()
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_LOGIN: 'free'}),
        )
        self.env.oauth.set_response_value(
            '_token',
            token_response(TEST_TOKEN),
        )

    def tearDown(self):
        self.env.stop()
        del self.env

    def assert_db_empty(self, shard='passportdbshard1'):
        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count(shard), 0)

    def assert_db_ok(self, uid=TEST_UID, shard='passportdbshard1'):
        time_now = TimeNow()

        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count(shard), 1)

        self.env.db.check('aliases', 'yambot', TEST_LOGIN, uid=uid, db='passportdbcentral')
        self.env.db.check('attributes', 'account.registration_datetime', time_now, uid=uid, db=shard)

        for attribute in ('person.firstname', 'person.lastname', 'person.gender', 'person.city',
                          'person.birthday', 'person.country', 'person.language', 'person.timezone'):
            self.env.db.check_missing('attributes', attribute, uid=uid, db=shard)

        self.env.db.check_missing('attributes', 'password.quality', uid=uid, db=shard)
        self.env.db.check_missing('attributes', 'password.encrypted', uid=uid, db=shard)
        self.env.db.check_missing('attributes', 'password.update_datetime', uid=uid, db=shard)

        self.env.db.check_missing('attributes', 'karma.value', uid=uid, db=shard)

    def assert_historydb_empty(self):
        self.assert_events_are_empty(self.env.handle_mock)

    def assert_historydb_ok(self):
        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'info.login': TEST_LOGIN,
                'info.ena': '1',
                'info.disabled_status': '0',
                'info.reg_date': DatetimeNow(convert_to_datetime=True),
                'info.karma_prefix': '0',
                'info.karma_full': '0',
                'info.karma': '0',
                'alias.yambot.add': TEST_LOGIN,
                'action': 'account_register_yambot',
                'consumer': 'dev',
            },
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='account_register_yambot',
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
            'yambot_alias_added',
            _inherit_from='account_modification_base',
            _exclude=['old', 'mode'],
            entity='aliases',
            operation='added',
            type=str(ANT['yambot']),
            value=TEST_LOGIN,
        )
        self.env.statbox.bind_entry(
            'account_modification_karma',
            _inherit_from='account_modification_base',
            _exclude=['mode'],
            entity='karma',
            action='account_register_yambot',
            destination='frodo',
            old='-',
            new='0',
            suid='-',
            login=TEST_LOGIN,
            registration_datetime=DatetimeNow(convert_to_datetime=True),
        )
        self.env.statbox.bind_entry(
            'account_created',
            _inherit_from='local_base',
            action='account_created',
            login=TEST_LOGIN,
        )
        self.env.statbox.bind_entry(
            'token_created',
            _inherit_from='local_base',
            action='token_created',
            client_id=TEST_YAMBOT_CLIENT_ID,
        )

    def assert_statbox_empty(self):
        self.env.statbox.assert_has_written([])

    def assert_statbox_ok(self, token_created=True):
        events = [
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('disabled_status_set'),
            self.env.statbox.entry('yambot_alias_added'),
            self.env.statbox.entry('account_modification_karma'),
            self.env.statbox.entry('account_created'),
        ]
        if token_created:
            events.append(
                self.env.statbox.entry('token_created'),
            )
        self.env.statbox.assert_has_written(events)

    def assert_oauth_not_called(self):
        ok_(not self.env.oauth.requests)

    def assert_oauth_called(self):
        request = self.env.oauth.get_requests_by_method('_token')[0]
        request.assert_post_data_contains(
            {
                'client_id': TEST_YAMBOT_CLIENT_ID,
                'client_secret': TEST_YAMBOT_CLIENT_SECRET,
                'grant_type': 'passport_assertion',
                'assertion': TEST_UID,
                'password_passed': False,
            },
        )
        request.assert_query_equals(
            {
                'user_ip': TEST_USER_IP,
            },
        )

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(rv, uid=1, oauth_token=TEST_TOKEN)
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.assert_statbox_ok()
        self.assert_oauth_called()

    def test_oauth_failed(self):
        self.env.oauth.set_response_value(
            '_token',
            {
                'error': 'invalid_grant',
                'error_description': 'User does not exist',
            },
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['backend.oauth_failed'])
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.assert_statbox_ok(token_created=False)
        self.assert_oauth_called()

    def test_user_ip_required(self):
        rv = self.make_request(exclude_headers=['user_ip'])

        self.assert_error_response(rv, ['ip.empty'])
        self.assert_db_empty()
        self.assert_historydb_empty()
        self.assert_statbox_empty()
        self.assert_oauth_not_called()
