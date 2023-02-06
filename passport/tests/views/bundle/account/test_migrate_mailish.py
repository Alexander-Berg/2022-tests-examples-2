# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.counters import migrate_mailish
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ANT
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_UID = 1
TEST_MAILISH_ID = 'onxw2zjnnfsa'
TEST_EMAIL = 'admin@google.ru'
TEST_OTHER_EMAIL = 'user@google.ru'
TEST_CONSUMER = 'dev'


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    **mock_counters(
        MIGRATE_MAILISH_PER_CONSUMER_COUNTER=(6, 10, 5),
    )
)
class MigrateMailishTestCase(BaseBundleTestViews):
    default_url = '/1/bundle/account/mailish/migrate/'
    http_method = 'POST'
    consumer = TEST_CONSUMER
    http_query_args = {
        'email': TEST_EMAIL,
        'mailish_id': TEST_MAILISH_ID,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['migrate_mailish']}))
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'migrated',
            mode='migrate_mailish',
            action='migrated',
            uid=str(TEST_UID),
            consumer='dev',
        )
        self.env.statbox.bind_entry(
            'alias_updated',
            event='account_modification',
            operation='updated',
            uid=str(TEST_UID),
            entity='aliases',
            type=str(ANT['mailish']),
            consumer='dev',
            ip='127.0.0.1',
            user_agent='-',
        )
        self.env.statbox.bind_entry(
            'display_name_updated',
            event='account_modification',
            uid=str(TEST_UID),
            entity='person.display_name',
            operation='updated',
            consumer='dev',
            ip='127.0.0.1',
            user_agent='-',
        )

    def setup_account(self, alias=TEST_EMAIL, alias_type='mailish', default_email=None, is_mailish_id_occupied=False):
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=alias,
            aliases={
                alias_type: alias,
            },
            attributes={
                'account.default_email': default_email,
            },
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                blackbox_response,
                blackbox_response if is_mailish_id_occupied else blackbox_userinfo_response(uid=None),
            ],
        )
        self.env.db.serialize(blackbox_response)

    def assert_db_ok(self, email=TEST_EMAIL):
        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check('aliases', 'mailish', TEST_MAILISH_ID, uid=TEST_UID, db='passportdbcentral')
        self.env.db.check('removed_aliases', 'mailish', TEST_EMAIL, uid=TEST_UID, db='passportdbcentral')
        self.env.db.check('attributes', 'account.default_email', email, uid=TEST_UID, db='passportdbshard1')
        self.env.db.check('attributes', 'account.display_name', 'p:%s' % email, uid=TEST_UID, db='passportdbshard1')

    def assert_historydb_ok(self, email=TEST_EMAIL, skip_email=False):
        entries = {
            'info.login': TEST_MAILISH_ID,
            'alias.mailish.change': TEST_MAILISH_ID,
            'info.display_name': 'p:%s' % email,
            'action': 'migrate_mailish',
            'consumer': 'dev',
        }
        if not skip_email:
            entries.update({'info.default_email': TEST_EMAIL})
        self.assert_events_are_logged(
            self.env.handle_mock,
            entries,
        )

    def assert_statbox_ok(self, email=TEST_EMAIL):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'alias_updated',
                old=TEST_EMAIL,
                new=TEST_MAILISH_ID,
            ),
            self.env.statbox.entry(
                'display_name_updated',
                old='',
                new='p:%s' % email,
            ),
            self.env.statbox.entry(
                'migrated',
                email=email,
                mailish_id=TEST_MAILISH_ID,
            ),
        ])

    def assert_blackbox_called(self):
        eq_(len(self.env.blackbox.requests), 2)
        self.env.blackbox.requests[0].assert_post_data_contains({
            'method': 'userinfo',
            'sid': 'mailish',
            'login': TEST_EMAIL,
        })
        ok_('regname' not in self.env.blackbox.requests[0].post_args)

    def test_ok(self):
        self.setup_account()
        rv = self.make_request()
        self.assert_ok_response(rv)
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.assert_statbox_ok()
        self.assert_blackbox_called()

    def test_already_has_email(self):
        self.setup_account(default_email=TEST_OTHER_EMAIL)
        rv = self.make_request()
        self.assert_ok_response(rv)
        self.assert_db_ok(email=TEST_OTHER_EMAIL)
        self.assert_historydb_ok(email=TEST_OTHER_EMAIL, skip_email=True)
        self.assert_statbox_ok(email=TEST_OTHER_EMAIL)
        self.assert_blackbox_called()

    def test_mailish_id_occupied(self):
        self.setup_account(is_mailish_id_occupied=True)
        rv = self.make_request()
        self.assert_error_response(rv, ['login.notavailable'])
        self.assert_blackbox_called()

    def test_invalid_account_type(self):
        self.setup_account(alias_type='lite')
        rv = self.make_request()
        self.assert_error_response(rv, ['account.invalid_type'])

    def test_rate_limit_exceeded(self):
        counter = migrate_mailish.get_per_consumer_counter()
        for _ in range(5):
            counter.incr(TEST_CONSUMER)

        rv = self.make_request()
        self.assert_error_response(rv, ['rate.limit_exceeded'])
