# -*- coding: utf-8 -*-
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.phone_squatter import PhoneSquatterPermanentError
from passport.backend.core.builders.phone_squatter.faker import (
    phone_squatter_get_change_status_response,
    phone_squatter_start_tracking_response,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


TEST_PHONE_NUMBER = PhoneNumber.parse('+79261234567')


TEST_SETTINGS = dict(
    USE_NEW_SUGGEST_BY_PHONE=True,
    USE_PHONE_SQUATTER=True,
    PHONE_SQUATTER_DRY_RUN=False,
)


@with_settings_hosts(**TEST_SETTINGS)
class TestPhoneNumberValidate(BaseBundleTestViews):
    default_url = '/1/bundle/validate/phone_number/by_squatter/'
    http_query_args = {'phone_number': TEST_PHONE_NUMBER.e164}
    consumer = 'dev'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'phone_number': ['validate_by_squatter']}))
        self.env.phone_squatter.set_response_value('start_tracking', phone_squatter_start_tracking_response())
        self.env.phone_squatter.set_response_value('get_change_status', phone_squatter_get_change_status_response())

    def tearDown(self):
        self.env.stop()

    def test_register_ok(self):
        rv = self.make_request(query_args=dict(scenario='register'))
        self.assert_ok_response(rv, require_flow_with_fio=False)
        assert len(self.env.phone_squatter.get_requests_by_method('start_tracking')) == 1
        assert len(self.env.phone_squatter.get_requests_by_method('get_change_status')) == 0

    def test_auth_ok(self):
        rv = self.make_request(query_args=dict(scenario='auth'))
        self.assert_ok_response(rv, require_flow_with_fio=False)
        assert len(self.env.phone_squatter.get_requests_by_method('start_tracking')) == 0
        assert len(self.env.phone_squatter.get_requests_by_method('get_change_status')) == 1

    def test_ok_with_country(self):
        rv = self.make_request(query_args={'phone_number': '89261234567', 'country': 'ru'})
        self.assert_ok_response(rv, require_flow_with_fio=False)
        assert len(self.env.phone_squatter.get_requests_by_method('start_tracking')) == 1
        assert len(self.env.phone_squatter.get_requests_by_method('get_change_status')) == 0

    def test_phone_squatter_failed(self):
        self.env.phone_squatter.set_response_side_effect('start_tracking', PhoneSquatterPermanentError)

        rv = self.make_request()
        self.assert_ok_response(rv, require_flow_with_fio=True)
        assert len(self.env.phone_squatter.requests) == 1

    def test_phone_squatter_dry_run(self):
        self.env.phone_squatter.set_response_side_effect('start_tracking', PhoneSquatterPermanentError)

        with settings_context(**dict(TEST_SETTINGS, PHONE_SQUATTER_DRY_RUN=True)):
            rv = self.make_request()
        self.assert_ok_response(rv, require_flow_with_fio=False)
        assert len(self.env.phone_squatter.requests) == 1

    def test_phone_squatter_disabled(self):
        with settings_context(**dict(TEST_SETTINGS, USE_PHONE_SQUATTER=False)):
            rv = self.make_request()
        self.assert_ok_response(rv, require_flow_with_fio=False)
        assert len(self.env.phone_squatter.requests) == 0

    def test_new_flow_disabled(self):
        with settings_context(**dict(TEST_SETTINGS, USE_NEW_SUGGEST_BY_PHONE=False)):
            rv = self.make_request()
        self.assert_ok_response(rv, require_flow_with_fio=True)
        assert len(self.env.phone_squatter.requests) == 0

    def test_bad_phone_number(self):
        rv = self.make_request(query_args={'phone_number': '26726472346234'})
        self.assert_error_response(rv, ['phone_number.invalid'])
