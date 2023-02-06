# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.register.test.base_test_data import (
    TEST_DEVICE_ID,
    TEST_DEVICE_NAME,
    TEST_HOST,
    TEST_REFERER,
    TEST_TOKEN,
    TEST_TOKEN_TYPE,
    TEST_UID,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
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


TEST_UBER_ID = '123456faed.TEST'
TEST_UBER_NORMALIZED_ID = '123456faed-test'
TEST_UBER_CLIENT_ID = '1'
TEST_UBER_CLIENT_SECRET = 'pss'


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    OAUTH_APP_UBER_CLIENT_ID=TEST_UBER_CLIENT_ID,
    OAUTH_APP_UBER_CLIENT_SECRET=TEST_UBER_CLIENT_SECRET,
)
class TestGetOrCreateUberUser(BaseBundleTestViews):
    default_url = '/1/bundle/account/get_or_create/uber/?consumer=dev'
    http_method = 'post'
    http_query_args = dict(
        uber_id=TEST_UBER_ID,
        device_id=TEST_DEVICE_ID,
        device_name=TEST_DEVICE_NAME,
    )
    http_headers = dict(
        user_ip=TEST_USER_IP,
        host=TEST_HOST,
        referer=TEST_REFERER,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(
            grants={
                'account': [
                    'get_or_create_uber_user',
                ],
            },
        ))

        self.setup_blackbox_userinfo_response()
        self.env.oauth.set_response_value(
            '_token',
            {
                'access_token': TEST_TOKEN,
                'token_type': TEST_TOKEN_TYPE,
            },
        )
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_blackbox_userinfo_response(self, user_found=False):
        params = {'uid': None}

        if user_found:
            params.update({
                'uid': TEST_UID,
                'login': TEST_UBER_NORMALIZED_ID,
                'aliases': {
                    'uber': TEST_UBER_NORMALIZED_ID,
                },
            })
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**params),
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            _inherit_from='base',
            mode='account_get_or_create_uber_user',
        )
        self.env.statbox.bind_entry(
            'local_base_with_uid',
            _inherit_from='local_base',
            uid=str(TEST_UID),
            login=TEST_UBER_NORMALIZED_ID,
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
            action='submitted',
        )
        self.env.statbox.bind_entry(
            'account_modification_disabled_status',
            _inherit_from='account_modification_base',
            entity='account.disabled_status',
            operation='created',
            old='-',
            new='enabled',
        )
        self.env.statbox.bind_entry(
            'account_modification_alias_added',
            _inherit_from='account_modification_base',
            entity='aliases',
            operation='added',
            type=str(ANT['uber']),
            value=TEST_UBER_NORMALIZED_ID,
        )
        self.env.statbox.bind_entry(
            'account_modification_karma',
            _inherit_from='account_modification_base',
            entity='karma',
            action='account_register',
            destination='frodo',
            old='-',
            new='0',
            suid='-',
            login=TEST_UBER_NORMALIZED_ID,
            registration_datetime=DatetimeNow(convert_to_datetime=True),
        )
        self.env.statbox.bind_entry(
            'account_created',
            _inherit_from='local_base_with_uid',
            action='account_created',
        )
        self.env.statbox.bind_entry(
            'token_created',
            _inherit_from='local_base_with_uid',
            action='token_created',
            client_id='1',
        )

    def assert_db_ok(self, central_count=2, shard_count=1):
        eq_(self.env.db.query_count('passportdbcentral'), central_count)
        eq_(self.env.db.query_count('passportdbshard1'), shard_count)

        self.env.db.check_db_attr(TEST_UID, 'account.registration_datetime', TimeNow())

        self.env.db.check('aliases', 'uber', TEST_UBER_NORMALIZED_ID, uid=TEST_UID, db='passportdbcentral')
        self.env.db.check_missing('aliases', 'portal', uid=TEST_UID, db='passportdbcentral')

        self.env.db.check_db_attr_missing(TEST_UID, 'account.user_defined_login')
        self.env.db.check_db_attr_missing(TEST_UID, 'account.display_name')
        self.env.db.check_db_attr_missing(TEST_UID, 'person.gender')
        self.env.db.check_db_attr_missing(TEST_UID, 'person.birthday')
        self.env.db.check_db_attr_missing(TEST_UID, 'person.country')
        self.env.db.check_db_attr_missing(TEST_UID, 'person.city')
        self.env.db.check_db_attr_missing(TEST_UID, 'person.language')
        self.env.db.check_db_attr_missing(TEST_UID, 'person.timezone')
        self.env.db.check_db_attr_missing(TEST_UID, 'password.encrypted')

    def assert_db_clear(self, shard='passportdbshard1'):
        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count(shard), 0)

    def assert_historydb_ok(self):
        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'info.login': TEST_UBER_NORMALIZED_ID,
                'info.ena': '1',
                'info.disabled_status': '0',
                'info.reg_date': DatetimeNow(convert_to_datetime=True),
                'info.karma_prefix': '0',
                'info.karma_full': '0',
                'info.karma': '0',
                'alias.uber.add': str(TEST_UBER_NORMALIZED_ID),
                'action': 'account_register',
                'consumer': 'dev',
            },
        )

    def assert_oauth_called(self, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME):
        self.env.oauth.get_requests_by_method('_token')[0].assert_post_data_contains(
            {
                'client_id': TEST_UBER_CLIENT_ID,
                'client_secret': TEST_UBER_CLIENT_SECRET,
                'grant_type': 'passport_assertion',
                'assertion': TEST_UID,
                'password_passed': False,
            },
        )
        query = {'user_ip': TEST_USER_IP}
        if device_name is not None:
            query.update(device_name=device_name)
        if device_id is not None:
            query.update(device_id=device_id)
        self.env.oauth.get_requests_by_method('_token')[0].assert_query_equals(query)

    def assert_oauth_not_called(self):
        ok_(not self.env.oauth.requests)

    def test_form_invalid(self):
        resp = self.make_request(exclude_args=['uber_id'])

        self.assert_error_response(resp, ['uber_id.empty'])

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
        ])
        self.assert_db_clear()
        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_oauth_not_called()

    def test_invalid_oauth_credentials__error(self):
        self.env.oauth.set_response_value(
            '_token',
            {
                'status': 'error',
                'error': 'invalid_client',
                'error_description': 'Wrong client secret',
            },
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['oauth.client_auth_invalid'])

        self.assert_db_ok()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('account_modification_disabled_status'),
            self.env.statbox.entry('account_modification_alias_added'),
            self.env.statbox.entry('account_modification_karma'),
            self.env.statbox.entry('account_created'),
        ])
        self.assert_historydb_ok()
        self.assert_oauth_called()

    def test_created_ok(self):
        resp = self.make_request()

        self.assert_ok_response(resp, uid=TEST_UID, is_new_account=True, oauth_token=TEST_TOKEN)

        self.assert_db_ok()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('account_modification_disabled_status'),
            self.env.statbox.entry('account_modification_alias_added'),
            self.env.statbox.entry('account_modification_karma'),
            self.env.statbox.entry('account_created'),
            self.env.statbox.entry('token_created'),
        ])
        self.assert_historydb_ok()
        self.assert_oauth_called()

    def test_get_already_created_ok(self):
        self.setup_blackbox_userinfo_response(user_found=True)

        resp = self.make_request()

        self.assert_ok_response(resp, uid=TEST_UID, is_new_account=False, oauth_token=TEST_TOKEN)
        self.assert_db_clear()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('token_created'),
        ])
        self.assert_events_are_empty(self.env.handle_mock)
        self.assert_oauth_called()

    def test_with_empty_device_info(self):
        resp = self.make_request(query_args={'device_id': None, 'device_name': ' '})

        self.assert_ok_response(resp, uid=TEST_UID, is_new_account=True, oauth_token=TEST_TOKEN)

        self.assert_db_ok()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('account_modification_disabled_status'),
            self.env.statbox.entry('account_modification_alias_added'),
            self.env.statbox.entry('account_modification_karma'),
            self.env.statbox.entry('account_created'),
            self.env.statbox.entry('token_created'),
        ])
        self.assert_historydb_ok()
        self.assert_oauth_called(device_id=None, device_name=None)
