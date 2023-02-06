# -*- coding: utf-8 -*-
from django.urls import reverse_lazy
from nose.tools import eq_
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_oauth_response
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.oauth.tvm_api.tvm_api.db.tvm_client import TVMClient

from .base import (
    BaseTvmAbcTestcaseWithCookieOrToken,
    CommonRobotAuthTests,
    CommonRoleTests,
    TEST_OTHER_UID,
    TEST_ROBOT_UID,
)


class EditClientV1Testcase(BaseTvmAbcTestcaseWithCookieOrToken, CommonRobotAuthTests, CommonRoleTests):
    default_url = reverse_lazy('tvm_abc_edit_client_v1')
    http_method = 'POST'

    def setUp(self):
        super(EditClientV1Testcase, self).setUp()
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_ROBOT_UID,
                scope='login:info',
            ),
        )

    def default_params(self):
        return dict(
            super(EditClientV1Testcase, self).default_params(),
            client_id=self.test_client.id,
            name='Test Test',
        )

    def default_headers(self):
        headers = super(EditClientV1Testcase, self).default_headers()
        headers.pop('HTTP_YA_CLIENT_COOKIE')
        headers.update({'HTTP_YA_CONSUMER_AUTHORIZATION': 'OAuth token'})
        return headers

    def test_ok(self):
        rv = self.make_request()
        self.assert_status_ok(rv)

        client = TVMClient.by_id(self.test_client.id)
        eq_(client.name, 'Test Test')
        eq_(client.modified, DatetimeNow())

    def test_client_not_found(self):
        rv = self.make_request(client_id=42)
        self.assert_status_error(rv, ['client.not_found'])

    def test_unknown_uid(self):
        rv = self.make_request(uid=TEST_OTHER_UID)
        self.assert_status_error(rv, ['abc_team.member_required'])
