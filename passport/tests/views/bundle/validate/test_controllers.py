# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    istest,
    nottest,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_DISPLAY_NAME,
    TEST_FIRSTNAME,
    TEST_LASTNAME,
    TEST_OAUTH_SCOPE,
    TEST_PUBLIC_ID,
    TEST_UID,
    TEST_USER_IP,
    TEST_USER_TICKET1,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_loginoccupation_response,
    blackbox_oauth_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.clean_web_api.clean_web_api import BaseCleanWebError
from passport.backend.core.builders.clean_web_api.faker.fake_clean_web_api import (
    clean_web_api_response_bad_verdicts,
    clean_web_api_simple_response,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import fake_user_ticket
from passport.backend.core.types.login.login import normalize_login


TEST_REQUEST_ID = 'TEST_REQUEST_ID'


@nottest
@with_settings_hosts(
    CLEAN_WEB_API_ENABLED=True,
    CLEAN_WEB_API_URL='http://localhost/',
    CLEAN_WEB_API_TIMEOUT=1,
    CLEAN_WEB_API_RETRIES=2,
)
class TestValidateViewCommon(BaseBundleTestViews):
    http_method = 'POST'
    consumer = 'dev'
    http_headers = {
        'user_ip': TEST_USER_IP,
        'other': {'X-Request-Id': TEST_REQUEST_ID},
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants=self.grants))
        self.env.clean_web_api.set_response_value('', clean_web_api_simple_response(True))

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_ok(self):
        rv = self.make_request(query_args=self.query_args)
        self.assert_ok_response(rv)
        eq_(len(self.env.clean_web_api.requests), 1)
        self.env.clean_web_api.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/',
            headers={'Content-Type': 'application/json'},
            json_data=(
                dict(
                    jsonrpc='2.0',
                    method='process',
                    id=1234,
                    params={
                        'type': 'user_data',
                        'service': 'passport',
                        'body': dict(
                            self.cw_request_values,
                            auto_only=True,
                        ),
                        'key': 'FAKE_KEY-{}'.format(TEST_REQUEST_ID),
                    },
                )
            )
        )

    def test_ok_clean_web_disabled(self):
        with settings_context(CLEAN_WEB_API_ENABLED=False):
            rv = self.make_request(query_args=self.query_args)
            self.assert_ok_response(rv)
            eq_(len(self.env.clean_web_api.requests), 0)

    def test_ok_clean_web_disabled_but_force(self):
        with settings_context(
            CLEAN_WEB_API_ENABLED=False,
            CLEAN_WEB_API_URL='http://localhost/',
            CLEAN_WEB_API_TIMEOUT=1,
            CLEAN_WEB_API_RETRIES=2,
        ):
            rv = self.make_request(query_args=dict(self.query_args, force_clean_web=True))
            self.assert_ok_response(rv)
            eq_(len(self.env.clean_web_api.requests), 1)

    def test_ok_with_clean_web_api_error(self):
        self.env.clean_web_api.set_response_value('', clean_web_api_simple_response(None))
        rv = self.make_request(query_args=self.query_args)
        self.assert_ok_response(rv)

    def test_ok_with_clean_web_api_failed(self):
        self.env.clean_web_api.set_response_side_effect('', BaseCleanWebError)
        rv = self.make_request(query_args=self.query_args)
        self.assert_ok_response(rv)

    def test_clean_web_api_bad(self):
        self.env.clean_web_api.set_response_value('', clean_web_api_response_bad_verdicts([self.cw_field_name]))
        rv = self.make_request(query_args=self.query_args)
        self.assert_error_response(rv, ['{}.invalid'.format(self.field_name)])


@nottest
class TestFraudMixin:
    def test_fraud(self):
        for field in self.query_args:
            resp = self.make_request(
                query_args=dict(
                    self.query_args,
                    is_from_variants=True,
                    **{
                        field: 's:1:fb:Заходи дорогой, www.yandex.ru',
                    }
                )
            )
            self.assert_error_response(resp, ['{}.invalid'.format(field)])
            eq_(len(self.env.clean_web_api.requests), 0)


@istest
class TestValidateDisplayNameView(TestValidateViewCommon, TestFraudMixin):
    default_url = '/1/bundle/validate/display_name/'
    field_name = 'display_name'
    cw_field_name = 'display_name'
    query_args = {'display_name': TEST_DISPLAY_NAME}
    grants = {'display_name': ['validate']}
    cw_request_values = {'display_name': TEST_DISPLAY_NAME}


@istest
class TestValidateFirstnameView(TestValidateViewCommon, TestFraudMixin):
    default_url = '/1/bundle/validate/firstname/'
    field_name = 'firstname'
    cw_field_name = 'first_name'
    query_args = {'firstname': TEST_FIRSTNAME}
    grants = {'firstname': ['validate']}
    cw_request_values = {'first_name': TEST_FIRSTNAME}


@istest
class TestValidateLastnameView(TestValidateViewCommon, TestFraudMixin):
    default_url = '/1/bundle/validate/lastname/'
    field_name = 'lastname'
    cw_field_name = 'last_name'
    query_args = {'lastname': TEST_LASTNAME}
    grants = {'lastname': ['validate']}
    cw_request_values = {'last_name': TEST_LASTNAME}


@istest
class TestValidateFullnameView(TestValidateViewCommon, TestFraudMixin):
    default_url = '/1/bundle/validate/fullname/'
    field_name = 'lastname'
    query_args = {'firstname': TEST_FIRSTNAME, 'lastname': TEST_LASTNAME}
    grants = {'firstname': ['validate'], 'lastname': ['validate']}
    cw_request_values={
        'first_name': TEST_FIRSTNAME,
        'last_name': TEST_LASTNAME,
        'full_name': '{} {}'.format(TEST_FIRSTNAME, TEST_LASTNAME),
    }

    def test_clean_web_api_bad(self):
        for bad_fields, expected_errors in [
            (['full_name'], ['firstname.invalid', 'lastname.invalid']),
            (['first_name', 'last_name', 'full_name'], ['firstname.invalid', 'lastname.invalid']),
        ]:
            self.env.clean_web_api.set_response_value('', clean_web_api_response_bad_verdicts(bad_fields))
            rv = self.make_request(query_args=self.query_args)
            self.assert_error_response(rv, expected_errors)


@istest
class TestValidatePublicIdView(TestValidateViewCommon):
    default_url = '/1/bundle/validate/public_id/'
    field_name = 'public_id'
    cw_field_name = 'public_id'
    query_args = {'public_id': TEST_PUBLIC_ID, 'uid': TEST_UID}
    grants = {'public_id': ['validate']}
    cw_request_values = {'public_id': TEST_PUBLIC_ID}

    def setUp(self):
        super(TestValidatePublicIdView, self).setUp()
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({normalize_login(TEST_PUBLIC_ID): 'free'}),
        )
        self.setup_blackbox_responses_and_serialize()

    def setup_blackbox_responses_and_serialize(self, **kwargs):
        common_kwargs = {
            'uid': TEST_UID,
            'subscribed_to': None,
            'dbfields': {},
            'attributes': {},
        }
        common_kwargs.update(kwargs)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**common_kwargs),
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(scope=TEST_OAUTH_SCOPE, **common_kwargs),
        )
        userinfo_response = blackbox_userinfo_response(**common_kwargs)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

    def test_occupied_public_id(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response(
                {normalize_login(TEST_PUBLIC_ID): 'occupied'},
                {normalize_login(TEST_PUBLIC_ID): '12345'},
            ),
        )
        resp = self.make_request(query_args=self.query_args)
        self.assert_error_response(resp, ['public_id.not_available'])

    def test_occupied_by_self_public_id(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response(
                {normalize_login(TEST_PUBLIC_ID): 'occupied'},
                {normalize_login(TEST_PUBLIC_ID): str(TEST_UID)},
            ),
        )
        resp = self.make_request(query_args=self.query_args)
        self.assert_ok_response(resp)

    def test_authorize_by_session(self):
        resp = self.make_request(
            query_args=dict(public_id=TEST_PUBLIC_ID),
            headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'},
        )
        self.assert_ok_response(resp)

    def test_authorize_by_token(self):
        resp = self.make_request(
            query_args=dict(public_id=TEST_PUBLIC_ID),
            headers={'authorization': 'OAuth token'},
        )
        self.assert_ok_response(resp)

    def test_authorize_by_userticket(self):
        ticket = fake_user_ticket(
            default_uid=TEST_UID,
            scopes=['bb:sessionid'],
            uids=[TEST_UID],
        )
        self.env.tvm_ticket_checker.set_check_user_ticket_side_effect([ticket])
        resp = self.make_request(
            query_args=dict(public_id=TEST_PUBLIC_ID),
            headers={'user_ticket': TEST_USER_TICKET1},
        )
        self.assert_ok_response(resp)

    def test_unable_to_change(self):
        self.setup_blackbox_responses_and_serialize(
            aliases=dict(
                public_id='some.alias',
                portal='login',
                old_public_id=['some.alias'],
            )
        )
        rv = self.make_request(query_args=self.query_args)
        self.assert_error_response(rv, ['public_id.update_not_allowed'])
