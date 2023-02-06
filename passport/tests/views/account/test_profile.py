# -*- coding: utf-8 -*-
from passport.backend.adm_api.test.utils import with_settings_hosts
from passport.backend.adm_api.test.views import BaseViewTestCase
from passport.backend.adm_api.tests.views.base_test_data import *
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_response
from passport.backend.core.builders.ufo_api import UfoApiTemporaryError
from passport.backend.core.builders.ufo_api.faker import (
    TEST_FRESH_ITEM,
    TEST_TIMEUUID,
    ufo_api_profile_item,
    ufo_api_profile_response,
)
from passport.backend.core.env_profile.profiles import UfoProfile


TEST_FULL_PROFILE = {'is_mobile_freq_1m': ['1', 10]}


@with_settings_hosts(
    UFO_API_URL='http://localhost',
)
class ProfileViewTestCase(BaseViewTestCase):

    path = '/1/account/profile/'

    def test_no_headers(self):
        resp = self.make_request(
            method='GET',
            path=self.path,
            params={'uid': TEST_UID},
        )
        self.check_response_error(resp, ['ip.empty', 'cookie.empty', 'host.empty'])

    def test_no_grants(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='looser'))
        resp = self.make_request(
            method='GET',
            path=self.path,
            params={'uid': TEST_UID},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['access.denied'])

    def test_ufo_api_failed(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.ufo_api.set_response_side_effect('profile', UfoApiTemporaryError)

        resp = self.make_request(
            method='GET',
            path=self.path,
            params={'uid': TEST_UID},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['backend.ufo_api_failed'])

    def test_ufo_api_invalid_item(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.ufo_api.set_response_value(
            'profile',
            ufo_api_profile_response(items=[{'id': 1, 'data': 'not-base-64'}]),
        )

        resp = self.make_request(
            method='GET',
            path=self.path,
            params={'uid': TEST_UID},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['exception.unhandled'])

    def test_profile_empty(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.ufo_api.set_response_value(
            'profile',
            ufo_api_profile_response(items=[]),
        )

        resp = self.make_request(
            method='POST',
            path=self.path,
            data={'uid': TEST_UID},
            headers=self.get_headers(),
        )
        self.check_response_ok(resp, profile=None, fresh=[])

    def test_with_only_fresh_profile(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.ufo_api.set_response_value(
            'profile',
            ufo_api_profile_response(items=[
                ufo_api_profile_item(),
                ufo_api_profile_item(),
            ]),
        )

        resp = self.make_request(
            method='POST',
            path=self.path,
            data={'uid': TEST_UID},
            headers=self.get_headers(),
        )
        self.check_response_ok(
            resp,
            profile=None,
            fresh=[
                {'id': TEST_TIMEUUID, 'data': TEST_FRESH_ITEM},
                {'id': TEST_TIMEUUID, 'data': TEST_FRESH_ITEM},
            ],
        )

    def test_with_full_profile(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.ufo_api.set_response_value(
            'profile',
            ufo_api_profile_response(items=[
                ufo_api_profile_item(timeuuid=UfoProfile.PROFILE_FAKE_UUID, data=TEST_FULL_PROFILE),
                ufo_api_profile_item(),
            ]),
        )

        resp = self.make_request(
            method='POST',
            path=self.path,
            data={'uid': TEST_UID},
            headers=self.get_headers(),
        )
        self.check_response_ok(
            resp,
            profile=TEST_FULL_PROFILE,
            fresh=[
                {'id': TEST_TIMEUUID, 'data': TEST_FRESH_ITEM},
            ],
        )
