# -*- coding: utf-8 -*-
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_multi_response
from passport.backend.core.eav_type_mapping import EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_NAME_MAPPING
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .base_email_bundle import (
    BaseEmailBundleTestCase,
    PasswordProtectedNewEmailBundleTests,
    TEST_EMAIL,
    TEST_EMAIL_ID,
    TEST_NATIVE_EMAIL,
    TEST_UID,
    TEST_USER_AGENT,
)


@with_settings_hosts
class TestSetupConfirmedEmail(BaseEmailBundleTestCase,
                              PasswordProtectedNewEmailBundleTests):
    default_url = '/1/bundle/email/setup_confirmed/?consumer=dev'
    http_query_args = {'email': TEST_EMAIL, 'is_safe': '1'}

    def setUp(self):
        super(TestSetupConfirmedEmail, self).setUp()
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
                            EMAIL_NAME_MAPPING['is_unsafe']: '1',
                            EMAIL_NAME_MAPPING['confirmed']: '1',
                        },
                    },
                ],
            ),
        )

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(rv)
        self.check_historydb_records([
            ('action', 'validator_setup'),
            ('email.%d' % TEST_EMAIL_ID, 'updated'),
            ('email.%d.address' % TEST_EMAIL_ID, TEST_EMAIL),
            ('email.%d.is_unsafe' % TEST_EMAIL_ID, '0'),
            ('user_agent', TEST_USER_AGENT),
        ])

    def test_email_not_found(self):
        rv = self.make_request(query_args={'email': 'blabla@yandex.ru'})

        self.assert_error_response(rv, ['email.not_found'])

    def test_email_is_native(self):
        rv = self.make_request(query_args={'email': TEST_NATIVE_EMAIL})

        self.assert_error_response(rv, ['email.is_native'])
