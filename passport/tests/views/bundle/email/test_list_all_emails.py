# -*- coding: utf-8 -*-
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_multi_response
from passport.backend.core.eav_type_mapping import EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_NAME_MAPPING
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .base_email_bundle import (
    BaseEmailBundleTestCase,
    TEST_ANOTHER_EMAIL,
    TEST_EMAIL,
    TEST_EMAIL_ID,
    TEST_LOGIN,
    TEST_NATIVE_EMAIL,
    TEST_UID,
)


@with_settings_hosts
class TestListAllEmails(BaseEmailBundleTestCase):
    default_url = '/1/bundle/email/list_all/?consumer=dev'

    def setUp(self):
        super(TestListAllEmails, self).setUp()
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                crypt_password='1:something',
                emails=[
                    {
                        'address': TEST_NATIVE_EMAIL,
                        'validated': True,
                        'default': True,
                        'rpop': False,
                        'silent': False,
                        'unsafe': False,
                        'native': True,
                    },
                ],
                email_attributes=[
                    {
                        'id': TEST_EMAIL_ID,
                        'attributes': {
                            EMAIL_NAME_MAPPING['address']: TEST_EMAIL,
                        },
                    },
                    {
                        'id': TEST_EMAIL_ID + 1,
                        'attributes': {
                            EMAIL_NAME_MAPPING['address']: TEST_ANOTHER_EMAIL,
                            EMAIL_NAME_MAPPING['is_rpop']: '1',
                            EMAIL_NAME_MAPPING['is_silent']: '1',
                            EMAIL_NAME_MAPPING['is_unsafe']: '1',
                            EMAIL_NAME_MAPPING['confirmed']: '1',
                        },
                    },
                    {
                        'id': TEST_EMAIL_ID + 2,
                        'attributes': {
                            EMAIL_NAME_MAPPING['address']: TEST_ANOTHER_EMAIL + '2',
                            EMAIL_NAME_MAPPING['is_rpop']: '1',
                        },
                    },
                    {
                        'id': TEST_EMAIL_ID + 3,
                        'attributes': {
                            EMAIL_NAME_MAPPING['address']: TEST_ANOTHER_EMAIL + '3',
                            EMAIL_NAME_MAPPING['is_unsafe']: '1',
                        },
                    },
                ],
            ),
        )

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(
            rv,
            emails={
                TEST_NATIVE_EMAIL: {
                    'native': True,
                    'default': True,
                    'confirmed': True,
                    'rpop': False,
                    'unsafe': False,
                    'silent': False,
                    'category': 'native',
                },
                TEST_EMAIL: {
                    'native': False,
                    'default': False,
                    'confirmed': False,
                    'rpop': False,
                    'unsafe': False,
                    'silent': False,
                    'category': 'for_restore',
                },
                TEST_ANOTHER_EMAIL: {
                    'native': False,
                    'default': False,
                    'confirmed': True,
                    'rpop': True,
                    'unsafe': True,
                    'silent': True,
                    'category': 'other',
                },
                TEST_ANOTHER_EMAIL + '2': {
                    'native': False,
                    'default': False,
                    'confirmed': False,
                    'rpop': True,
                    'unsafe': False,
                    'silent': False,
                    'category': 'rpop',
                },
                TEST_ANOTHER_EMAIL + '3': {
                    'native': False,
                    'default': False,
                    'confirmed': False,
                    'rpop': False,
                    'unsafe': True,
                    'silent': False,
                    'category': 'for_notifications',
                },
            },
        )

    def test_social_account_ok(self):
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                aliases={
                    'social': TEST_LOGIN,
                },
                email_attributes=[
                    {
                        'id': TEST_EMAIL_ID,
                        'attributes': {
                            EMAIL_NAME_MAPPING['address']: TEST_EMAIL,
                            EMAIL_NAME_MAPPING['is_unsafe']: '1',
                        },
                    },
                ],
            ),
        )

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            emails={
                TEST_EMAIL: {
                    'native': False,
                    'default': False,
                    'confirmed': False,
                    'rpop': False,
                    'unsafe': True,
                    'silent': False,
                    'category': 'for_notifications',
                },
            },
        )
