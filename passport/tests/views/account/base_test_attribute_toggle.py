from passport.backend.adm_api.tests.views.base_test_data import TEST_UID
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_response
from passport.backend.core.builders.passport.faker import (
    passport_bundle_api_error_response,
    passport_ok_response,
)


class BaseAccountAttributeToggleTestCase(object):
    path = ''
    param_name = ''

    def setUp(self):
        super(BaseAccountAttributeToggleTestCase, self).setUp()

        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.passport.set_response_value('account_options', passport_ok_response())

    def _params(self, value='true', **kwargs):
        return dict(
            {self.param_name: value},
            uid=TEST_UID,
            **kwargs
        )

    def _post_args(self, value, **kwargs):
        return dict(
            {self.param_name: value},
            **kwargs
        )

    def test_enable__ok(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=self._params(),
            headers=self.get_headers(),
        )
        self.check_response_ok(resp)
        self.env.passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://127.0.0.1:6000/2/account/{}/options/?consumer=adminka'.format(TEST_UID),
            post_args=self._post_args(
                1,
                admin_name='admin',
                comment='no comment',
            ),
        )

    def test_disable__ok(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=self._params('false'),
            headers=self.get_headers(),
        )
        self.check_response_ok(resp)
        self.env.passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://127.0.0.1:6000/2/account/{}/options/?consumer=adminka'.format(TEST_UID),
            post_args=self._post_args(
                0,
                admin_name='admin',
                comment='no comment',
            ),
        )

    def test_enable__with_comment__ok(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=self._params(comment='some comment'),
            headers=self.get_headers(),
        )
        self.check_response_ok(resp)
        self.env.passport.requests[0].assert_properties_equal(
            method='POST',
            url='http://127.0.0.1:6000/2/account/{}/options/?consumer=adminka'.format(TEST_UID),
            post_args=self._post_args(
                1,
                admin_name='admin',
                comment='some comment',
            ),
        )

    def test_no_attribute_parameter__form_invalid(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data={'uid': TEST_UID},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['{}.empty'.format(self.param_name)])

    def test_no_uid_parameter__form_invalid(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data={self.param_name: 'true'},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['uid.empty'])

    def test_disabled_account__error(self):
        self.env.passport.set_response_value(
            'account_options',
            passport_bundle_api_error_response('account.disabled'),
        )
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=self._params(),
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['account.disabled'])

    def test_account_not_found__error(self):
        self.env.passport.set_response_value(
            'account_options',
            passport_bundle_api_error_response('account.not_found'),
        )
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=self._params(),
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['account.not_found'])
