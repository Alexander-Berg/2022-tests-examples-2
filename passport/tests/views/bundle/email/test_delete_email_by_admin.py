# -*- coding: utf-8 -*-
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.eav_type_mapping import EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_NAME_MAPPING
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.types.email.email import mask_email_for_statbox
from passport.backend.utils.time import (
    datetime_to_string,
    unixtime_to_datetime,
)

from .base_email_bundle import (
    BaseEmailBundleTestCase,
    TEST_ANOTHER_EMAIL,
    TEST_EMAIL,
    TEST_EMAIL_ID,
    TEST_IP,
    TEST_NATIVE_EMAIL,
    TEST_UID,
    TEST_USER_AGENT,
)


@with_settings_hosts()
class TestDeleteEmailByAdmin(BaseEmailBundleTestCase):
    default_url = '/1/bundle/email/delete_by_admin/?consumer=dev'
    http_query_args = {
        'uid': TEST_UID,
        'email': TEST_EMAIL,
        'admin_name': 'admin',
    }

    def setUp(self):
        super(TestDeleteEmailByAdmin, self).setUp()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'email_bundle': ['base', 'delete_by_admin'],
        }))
        self.setup_blackbox_response()
        self.setup_statbox_templates()

    def setup_blackbox_response(self):
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
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
                            EMAIL_NAME_MAPPING['confirmed']: '2',
                        },
                    },
                ],
            ),
        )

    def setup_statbox_templates(self):
        super(TestDeleteEmailByAdmin, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'delete_email',
            _inherit_from='account_modification',
            entity='account.emails',
            operation='deleted',
            old=mask_email_for_statbox(TEST_EMAIL),
            new='-',
            email_id=str(TEST_EMAIL_ID),
            is_unsafe='1',
            confirmed_at=datetime_to_string(unixtime_to_datetime(2)),
            uid=str(TEST_UID),
            ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
            consumer='dev',
            is_suitable_for_restore='0',
        )

    def test_account_not_found(self):
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.not_found'])

    def test_email_not_found(self):
        resp = self.make_request(query_args={'email': TEST_ANOTHER_EMAIL})
        self.assert_error_response(resp, ['email.not_found'])

    def test_email_is_native(self):
        resp = self.make_request(query_args={'email': TEST_NATIVE_EMAIL})
        self.assert_error_response(resp, ['email.is_native'])

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'action': 'delete_email_by_admin',
                'consumer': 'dev',
                'email.%d' % TEST_EMAIL_ID: 'deleted',
                'email.%d.address' % TEST_EMAIL_ID: TEST_EMAIL,
                'user_agent': TEST_USER_AGENT,
                'admin': 'admin',
            },
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('delete_email'),
        ])

    def test_ok_with_comment(self):
        resp = self.make_request(query_args={'comment': 'comment'})
        self.assert_ok_response(resp)
        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'action': 'delete_email_by_admin',
                'consumer': 'dev',
                'email.%d' % TEST_EMAIL_ID: 'deleted',
                'email.%d.address' % TEST_EMAIL_ID: TEST_EMAIL,
                'user_agent': TEST_USER_AGENT,
                'admin': 'admin',
                'comment': 'comment',
            },
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('delete_email'),
        ])
