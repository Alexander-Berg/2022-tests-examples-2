# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.otp import forms
from passport.backend.core.grants.faker.grants import FakeGrants
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings
from passport.backend.utils.common import merge_dicts


TEST_LOGIN = 'test-login'
TEST_TRACK_ID = 'a' * 34


@with_settings
class ShortInfoFormTestCase(unittest.TestCase):

    def setUp(self):
        self.grants = FakeGrants()
        self.grants.start()
        self.grants.set_grants_return_value(mock_grants())

    def tearDown(self):
        self.grants.stop()
        del self.grants

    def test_short_info_form(self):
        invalid_cases = [
            ({}, ['consumer.empty', 'login.empty']),
            (
                {'consumer': 'dev', 'login': 'test-login', 'track_id': 'invalid-track-id'},
                ['track_id.invalid'],
            ),
            (
                {'consumer': 'passport', 'login': 'test-login', 'track_id': TEST_TRACK_ID},
                ['consumer.invalid'],
            ),
        ]

        empty_params = dict.fromkeys([
            'avatar_size',
            'am_version',
            'am_version_name',
            'app_id',
            'app_platform',
            'os_version',
            'manufacturer',
            'model',
            'app_version',
            'app_version_name',
            'uuid',
            'deviceid',
            'ifv',
            'device_name',
            'track_id',
            'device_id',
        ])

        valid_cases = [
            (
                {
                    'consumer': 'dev',
                    'login': TEST_LOGIN,
                },
                merge_dicts(
                    empty_params,
                    {
                        'consumer': 'dev',
                        'login': TEST_LOGIN,
                    },
                ),
            ),
            (
                {
                    'consumer': 'dev',
                    'login': TEST_LOGIN,
                    'track_id': TEST_TRACK_ID,
                    'avatar_size': 'test-avatar-size',
                    'am_version': 'am-version',
                    'am_version_name': 'am-version',
                    'app_id': 'test-id',
                    'app_platform': 'android',
                    'os_version': '5.0.1',
                    'manufacturer': 'samsung',
                    'model': 'galaxy',
                    'app_version': '1.2.3-4',
                    'app_version_name': '1.2.3-4',
                    'uuid': 'test-uuid',
                    'deviceid': 'test-dev-id',
                    'ifv': 'test-ifv',
                    'device_name': 'test-name',
                    'device_id': 'hello-im-device',
                },
                {
                    'consumer': 'dev',
                    'login': TEST_LOGIN,
                    'track_id': TEST_TRACK_ID,
                    'avatar_size': 'test-avatar-size',
                    'am_version': 'am-version',
                    'am_version_name': 'am-version',
                    'app_id': 'test-id',
                    'app_platform': 'android',
                    'os_version': '5.0.1',
                    'manufacturer': 'samsung',
                    'model': 'galaxy',
                    'app_version': '1.2.3-4',
                    'app_version_name': '1.2.3-4',
                    'uuid': 'test-uuid',
                    'deviceid': 'test-dev-id',
                    'ifv': 'test-ifv',
                    'device_name': 'test-name',
                    'device_id': 'hello-im-device',
                },
            ),
        ]

        check_form(forms.ShortInfoForm(), invalid_cases, valid_cases)
