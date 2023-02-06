# -*- coding: utf-8 -*-
import json

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.eav_type_mapping import EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_NAME_MAPPING
from passport.backend.core.models.persistent_track import TRACK_TYPE_EMAIL_CONFIRMATION_CODE
from passport.backend.core.test.consts import TEST_SOCIAL_LOGIN1
from passport.backend.core.test.fake_code_generator import CodeGeneratorFaker
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.core.types.login.login import masked_login

from .base_email_bundle import (
    BaseEmailBundleTestCase,
    PasswordProtectedNewEmailBundleTests,
    TEST_EMAIL,
    TEST_EMAIL_ID,
    TEST_LOGIN,
    TEST_PERSISTENT_TRACK_ID,
    TEST_RETPATH,
    TEST_SHORT_CODE,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_VALIDATION_URL,
    TEST_VALIDATOR_UI_URL,
)


@with_settings_hosts(
    EMAIL_VALIDATOR_SHORT_CODE_LENGTH=5,
)
class TestSendConfirmationEmail(BaseEmailBundleTestCase,
                                PasswordProtectedNewEmailBundleTests,
                                EmailTestMixin):
    default_url = '/1/bundle/email/send_confirmation_email/?consumer=dev'

    def setUp(self):
        super(TestSendConfirmationEmail, self).setUp()
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

        self.http_query_args = {
            'email': TEST_EMAIL,
            'language': 'ru',
            'retpath': TEST_RETPATH,
            'validator_ui_url': TEST_VALIDATOR_UI_URL,
            'track_id': self.track_id,
        }

        self.generate_track_id_mock = mock.Mock(return_value=TEST_PERSISTENT_TRACK_ID)
        self.generate_track_id_patch = mock.patch(
            'passport.backend.core.models.persistent_track.generate_track_id',
            self.generate_track_id_mock,
        )
        self.generate_track_id_patch.start()

        self.code_generator_faker = CodeGeneratorFaker(TEST_SHORT_CODE)
        self.code_generator_faker.start()

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:something',
            ),
        )
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:something',
            ),
        )

    def tearDown(self):
        self.code_generator_faker.stop()
        self.generate_track_id_patch.stop()
        self.track_id_generator.stop()
        del self.generate_track_id_mock
        del self.generate_track_id_patch
        del self.code_generator_faker
        del self.track_id_generator
        super(TestSendConfirmationEmail, self).tearDown()

    def build_email(self, address, is_native, login, firstname, code_only=False):
        login = login if is_native else masked_login(login)
        message = {
            'SHORT_CODE': TEST_SHORT_CODE,
            'MASKED_LOGIN': login,
        }
        message_key = 'emails.confirmation_email_short_sent.messagev2'
        if not code_only:
            message.update({
                'VALIDATION_URL': TEST_VALIDATION_URL,
            })
            message_key = 'emails.confirmation_email_sent.message'

        return {
            'language': 'ru',
            'addresses': [address],
            'subject': 'emails.confirmation_email_sent.subject',
            'tanker_keys': {
                'greeting.noname': {},
                message_key: message,
                'emails.confirmation_email_sent.dont_worry': {
                    'MASKED_LOGIN': login,
                },
                'feedback': {
                    'FEEDBACK_URL_BEGIN': '<a href=\'https://feedback2.yandex.ru/\'>',
                    'FEEDBACK_URL_END': '</a>',
                },
                'signature.secure': {},
            },
        }

    def prepare_testone_address_response(self, address=TEST_EMAIL, native=True):
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

    def check_email_sent(self, code_only=False, firstname=u'\\u0414', login=TEST_LOGIN):
        self.assert_emails_sent([
            self.build_email(
                address=TEST_EMAIL,
                is_native=False,
                code_only=code_only,
                login=login,
                firstname=firstname,
            ),
        ])

    def check_confirmation_track_created(self, db='passportdbshard1'):
        self.env.db.check(
            'tracks',
            'uid',
            TEST_UID,
            track_id=TEST_PERSISTENT_TRACK_ID,
            content='{"address": "%s", "short_code": "%s", "type": %d}' % (
                TEST_EMAIL,
                TEST_SHORT_CODE,
                TRACK_TYPE_EMAIL_CONFIRMATION_CODE,
            ),
            db=db,
        )

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(rv, track_id=self.track_id)
        self.check_confirmation_track_created()
        self.check_historydb_records([
            ('action', 'validator_send'),
            ('email.%d' % TEST_EMAIL_ID, 'created'),
            ('email.%d.address' % TEST_EMAIL_ID, TEST_EMAIL),
            ('email.%d.created_at' % TEST_EMAIL_ID, TimeNow()),
            ('email.%d.is_unsafe' % TEST_EMAIL_ID, '0'),
            ('user_agent', TEST_USER_AGENT),
        ])
        self.check_email_sent()

        track = self.track_manager.read(self.track_id)
        eq_(track.persistent_track_id, TEST_PERSISTENT_TRACK_ID)
        ok_(track.invalid_email_key_count.get() is None)

    def test_ok_for_unsafe(self):
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                age=100500,
            ),
        )

        rv = self.make_request(query_args={'is_safe': 'no'})

        self.assert_ok_response(rv, track_id=self.track_id)
        self.check_confirmation_track_created()
        self.check_historydb_records([
            ('action', 'validator_send'),
            ('email.%d' % TEST_EMAIL_ID, 'created'),
            ('email.%d.address' % TEST_EMAIL_ID, TEST_EMAIL),
            ('email.%d.created_at' % TEST_EMAIL_ID, TimeNow()),
            ('email.%d.is_unsafe' % TEST_EMAIL_ID, '1'),
            ('user_agent', TEST_USER_AGENT),
        ])
        self.check_email_sent()

        track = self.track_manager.read(self.track_id)
        eq_(track.persistent_track_id, TEST_PERSISTENT_TRACK_ID)
        ok_(track.invalid_email_key_count.get() is None)

    def test_ok_for_unsupported_language(self):
        rv = self.make_request(query_args={'language': 'tt'})

        self.assert_ok_response(rv, track_id=self.track_id)
        self.check_email_sent()

    def test_ok_unicode_retpath(self):
        rv = self.make_request(query_args={'retpath': u'https://yandex.com.tr/harita/115690/ataşehir/'})

        self.assert_ok_response(rv, track_id=self.track_id)

    def test_track_id_missing(self):
        rv = self.make_request(exclude_args=['track_id'])
        self.assert_error_response(rv, ['track_id.empty'])

    def test_is_native(self):
        self.env.blackbox.set_response_value(
            'userinfo',
            self.prepare_testone_address_response(),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['email.is_native'])

    def test_already_confirmed(self):
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                crypt_password='1:something',
                email_attributes=[
                    {
                        'id': TEST_EMAIL_ID,
                        'attributes': {
                            EMAIL_NAME_MAPPING['address']: TEST_EMAIL,
                            EMAIL_NAME_MAPPING['confirmed']: '1',
                        },
                    },
                ],
            ),
        )

        rv = self.make_request()
        self.assert_error_response(rv, ['email.already_confirmed'])

    def test_emails_over_limit(self):
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                crypt_password='1:something',
                email_attributes=[
                    {
                        'id': i,
                        'attributes': {
                            EMAIL_NAME_MAPPING['address']: 'some.email.{}@gmail.com'.format(i),
                            EMAIL_NAME_MAPPING['confirmed']: '1',
                        },
                    } for i in range(100)
                ],
            ),
        )

        rv = self.make_request()
        self.assert_error_response(rv, ['email.limit_per_profile_reached'])

    def test_code_only(self):
        rv = self.make_request(query_args={'code_only': '1'})
        self.assert_ok_response(rv, track_id=self.track_id)
        self.check_email_sent(code_only=True)

    def test_ok_by_token(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:something',
                scope='passport:bind_email',
            ),
        )
        rv = self.make_request(
            query_args={'is_safe': 'no'},
            headers={'authorization': 'OAuth foo'},
            exclude_headers=['cookie'],
        )
        self.assert_ok_response(rv, track_id=self.track_id)
        self.check_email_sent()

    def test_social_account_with_firstname(self):
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_SOCIAL_LOGIN1,
                aliases={'social': TEST_SOCIAL_LOGIN1},
                crypt_password='1:something',
                firstname='Afanasiy',
            ),
        )

        rv = self.make_request()

        self.assert_ok_response(rv, track_id=self.track_id)
        self.check_email_sent(login='Afanasify', firstname='Afanasiy')
