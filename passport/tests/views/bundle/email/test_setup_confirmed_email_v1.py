# -*- coding: utf-8 -*-
import json

from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.eav_type_mapping import (
    EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_NAME_MAPPING,
    EXTENDED_ATTRIBUTES_EMAIL_TYPE,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.email.email import mask_email_for_statbox

from .base_email_bundle import (
    BaseEmailBundleTestCase,
    TEST_EMAIL,
    TEST_EMAIL_ID,
    TEST_LOGIN,
    TEST_UID,
)


@with_settings_hosts()
class TestSetupConfirmedEmail(BaseEmailBundleTestCase):
    def setUp(self):
        super(TestSetupConfirmedEmail, self).setUp()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'email_bundle': ['base', 'modify_confirmed', 'create_confirmed'],
        }))

        self.env.statbox.bind_base(
            mode='email_bundle',
            action='setup_confirmed_email',
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'success',
            status='ok',
            email=mask_email_for_statbox(TEST_EMAIL),
            consumer='dev',
        )
        self.env.statbox.bind_entry(
            'error',
            status='error',
            error='email.validator_failed',
            email=mask_email_for_statbox(TEST_EMAIL),
            consumer='dev',
        )
        self.env.statbox.bind_entry(
            'get_key',
            mode='email_validation',
            action='get_key',
            email=mask_email_for_statbox(TEST_EMAIL),
            host='',
        )
        self.env.statbox.bind_entry(
            'confirm',
            mode='email_validation',
            action='confirmed',
        )
        self.env.statbox.bind_entry(
            'set_silent',
            mode='email_validation',
            action='set_silent',
            is_silent='1',
            email=mask_email_for_statbox(TEST_EMAIL),
        )

    def make_request(self, headers, post_data):
        return self.env.client.post(
            '/1/email/setup_confirmed/?consumer=dev',
            data=post_data,
            headers=headers,
        )

    def request_params(self, uid=TEST_UID, email=TEST_EMAIL, is_silent=None):
        return {
            'uid': uid,
            'email': email,
            'is_silent': is_silent,
        }

    def prepare_testone_address_response(self, address=TEST_EMAIL, native=False):
        response = {
            'users': [
                {
                    'address-list': [
                        {
                            'address': address,
                            'born-date': '2014-12-26 16:11:15',
                            'default': True,
                            'native': native,
                            'prohibit-restore': False,
                            'rpop': False,
                            'silent': False,
                            'unsafe': False,
                            'validated': True,
                        },
                    ],
                    'have_hint': False,
                    'have_password': True,
                    'id': str(TEST_UID),
                    'karma': {
                        'value': 0,
                    },
                    'karma_status': {
                        'value': 0,
                    },
                    'login': TEST_LOGIN,
                    'uid': {
                        'hosted': False,
                        'lite': False,
                        'value': str(TEST_UID),
                    },
                },
            ],
        }
        return json.dumps(response)

    def check_email_created(self, is_silent=None):
        expected = [
            ('address', TEST_EMAIL),
            ('created', TimeNow()),
            ('bound', TimeNow()),
            ('confirmed', TimeNow()),
        ]

        if is_silent:
            expected.append(('is_silent', '1'))

        for attr, value in expected:
            self.env.db.check(
                'extended_attributes',
                'value',
                value,
                uid=TEST_UID,
                type=EMAIL_NAME_MAPPING[attr],
                entity_type=EXTENDED_ATTRIBUTES_EMAIL_TYPE,
                db='passportdbshard1',
            )
        self.env.db.check(
            'email_bindings',
            'address',
            TEST_EMAIL,
            uid=TEST_UID,
            email_id=TEST_EMAIL_ID,
            db='passportdbshard1',
        )

    def test_error_account_not_found_fails(self):
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        resp = self.make_request(self.get_headers(), self.request_params())

        self.assert_error_response(resp, ['account.not_found'])

    def test_error_new_email_is_native(self):
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(uid=TEST_UID),
                self.prepare_testone_address_response(native=True),
            ],
        )

        resp = self.make_request(self.get_headers(), self.request_params())

        self.assert_error_response(
            resp,
            ['email.is_native'],
        )

    def test_error_existing_email_is_native(self):
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(uid=TEST_UID),
                self.prepare_testone_address_response(native=True),
            ],
        )
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_UID,
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_EMAIL,
                        EMAIL_NAME_MAPPING['created']: '1',
                    },
                },
            ],
        )
        self.env.db.serialize(blackbox_response)

        resp = self.make_request(self.get_headers(), self.request_params())

        self.assert_error_response(
            resp,
            ['email.is_native'],
        )

    def test_ok(self):
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(uid=TEST_UID),
                self.prepare_testone_address_response(native=False),
            ],
        )

        resp = self.make_request(self.get_headers(), self.request_params())

        self.assert_ok_response(resp)
        self.check_statbox_contents()
        self.check_email_created()
        self.check_blackbox_called()

    def test_ok_with_existing(self):
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_UID,
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_EMAIL,
                        EMAIL_NAME_MAPPING['created']: '1',
                    },
                },
            ],
        )
        self.env.db.serialize(blackbox_response)
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_response,
                self.prepare_testone_address_response(native=False),
            ],
        )

        resp = self.make_request(self.get_headers(), self.request_params())

        self.assert_ok_response(resp)
        current_datetime = DatetimeNow(convert_to_datetime=True)
        self.check_statbox_contents_modified(
            bound_at=current_datetime,
            confirmed_at=current_datetime,
            is_unsafe='1',
        )
        self.env.db.check_query_counts(
            central=0,
            shard=2,
        )
        self.check_blackbox_called()

    def test_emails_over_limit(self):
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_UID,
            email_attributes=[
                {
                    'id': i,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: 'some.email.{}@gmail.com'.format(i),
                        EMAIL_NAME_MAPPING['created']: '1',
                    },
                } for i in range(100)
            ],
        )
        self.env.db.serialize(blackbox_response)
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_response,
                self.prepare_testone_address_response(native=False),
            ],
        )

        resp = self.make_request(self.get_headers(), self.request_params())

        self.assert_error_response(
            resp,
            ['email.limit_per_profile_reached'],
        )

    def test_ok_with_existing_and_is_silent(self):
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_UID,
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_EMAIL,
                        EMAIL_NAME_MAPPING['created']: '1',
                    },
                },
            ],
        )
        self.env.db.serialize(blackbox_response)
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_response,
                self.prepare_testone_address_response(native=False),
            ],
        )

        resp = self.make_request(
            self.get_headers(),
            self.request_params(is_silent=True),
        )

        self.assert_ok_response(resp)
        current_datetime = DatetimeNow(convert_to_datetime=True)
        self.check_statbox_contents_modified(
            bound_at=current_datetime,
            confirmed_at=current_datetime,
            is_silent='1',
            is_unsafe='1',
        )
        self.env.db.check_query_counts(
            central=0,
            shard=2,
        )
        self.check_blackbox_called()

    def test_with_silent_flag_set_ok(self):
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(uid=TEST_UID),
                self.prepare_testone_address_response(native=False),
            ],
        )

        resp = self.make_request(
            self.get_headers(),
            self.request_params(is_silent=True),
        )

        self.assert_ok_response(resp)
        self.check_statbox_contents(is_silent='1')
        self.check_email_created()
        self.check_blackbox_called()

    def test_with_silent_flag_unset_ok(self):
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(uid=TEST_UID),
                self.prepare_testone_address_response(native=False),
            ],
        )

        resp = self.make_request(
            self.get_headers(),
            self.request_params(is_silent=False),
        )

        self.assert_ok_response(resp)
        self.check_statbox_contents(is_silent='0')
        self.check_email_created()
        self.check_blackbox_called()

    def check_statbox_contents(self, **kwargs):
        fields = {
            'email_id': str(TEST_EMAIL_ID),
            'entity': 'account.emails',
            'event': 'account_modification',
            'is_unsafe': '1',
            'operation': 'added',
            'new': mask_email_for_statbox(TEST_EMAIL),
            'old': '-',
            'user_agent': '-',
            'uid': str(TEST_UID),
            'created_at': DatetimeNow(convert_to_datetime=True),
            'bound_at': DatetimeNow(convert_to_datetime=True),
            'confirmed_at': DatetimeNow(convert_to_datetime=True),
            'consumer': '-',
            'is_suitable_for_restore': '0',
        }

        addendum = {}
        is_silent = kwargs.get('is_silent')
        if is_silent is not None:
            addendum['is_silent'] = is_silent
        fields.update(kwargs)

        entries = [
            self.env.statbox.entry(
                'account_modification',
                **fields
            ),
            self.env.statbox.entry(
                'success',
                **addendum
            ),
        ]
        self.env.statbox.assert_has_written(entries)

    def check_statbox_contents_modified(self, **kwargs):
        fields = {
            'email_id': str(TEST_EMAIL_ID),
            'entity': 'account.emails',
            'event': 'account_modification',
            'operation': 'updated',
            'new': mask_email_for_statbox(TEST_EMAIL),
            'old': mask_email_for_statbox(TEST_EMAIL),
            'user_agent': '-',
            'uid': str(TEST_UID),
            'consumer': '-',
            'is_suitable_for_restore': '0',
        }

        addendum = {}
        is_silent = kwargs.get('is_silent')
        if is_silent is not None:
            addendum['is_silent'] = is_silent
        fields.update(kwargs)

        entries = [
            self.env.statbox.entry(
                'account_modification',
                **fields
            ),
            self.env.statbox.entry(
                'success',
                **addendum
            ),
        ]

        self.env.statbox.assert_has_written(entries)
