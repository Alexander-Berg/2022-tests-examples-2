# -*- coding: utf-8 -*-

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.common.processes import PROCESS_WEB_REGISTRATION
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.register.test.base_test_data import (
    TEST_ANOTHER_NON_NATIVE_EMAIL,
    TEST_EMAIL,
    TEST_NON_NATIVE_EMAIL,
    TEST_SHORT_CODE,
    TEST_USER_AGENT,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_hosted_domains_response
from passport.backend.core.counters import (
    register_email_per_email,
    register_email_per_ip,
)
from passport.backend.core.test.fake_code_generator import CodeGeneratorFaker
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.types.email.email import mask_email_for_statbox
from passport.backend.utils.time import get_unixtime


TEST_IP = '123.123.123.123'
TEST_YANDEXUID = 'yuid12345'
TEST_UNICODE_EMAIL = u'some.email@окна.рф'
TEST_PUNYCODE_EMAIL = 'some.email@xn--80atjc.xn--p1ai'


@with_settings_hosts(
    EMAIL_VALIDATOR_SHORT_CODE_LENGTH=5,
    ALLOWED_EMAIL_SHORT_CODE_FAILED_CHECK_COUNT=2,
    **mock_counters()
)
class TestSendRegistrationConfirmationEmail(BaseBundleTestViews, EmailTestMixin):
    track_type = 'register'
    http_method = 'POST'
    http_headers = {
        'user_agent': TEST_USER_AGENT,
        'user_ip': TEST_USER_IP,
        'cookie': 'yandexuid=' + TEST_YANDEXUID,
    }
    default_url = '/1/bundle/account/register/send_email/?consumer=dev'

    def setUp(self):
        super(TestSendRegistrationConfirmationEmail, self).setUp()

        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'account': ['register_mail'],
        }))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(self.track_type)

        self.code_generator_faker = CodeGeneratorFaker(TEST_SHORT_CODE)
        self.code_generator_faker.start()

        self.http_query_args = {
            'email': TEST_NON_NATIVE_EMAIL,
            'language': 'en',
            'track_id': self.track_id,
        }

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = PROCESS_WEB_REGISTRATION
            track.is_captcha_recognized = True
            track.is_captcha_checked = True

        self.setup_blackbox_response()

        self.env.statbox.bind_entry(
            'local_base',
            mode='register_by_email',
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            track_id=self.track_id,
            yandexuid=TEST_YANDEXUID,
        )
        self.env.statbox.bind_entry(
            'new_code',
            _inherit_from=['local_base'],
            action='new_code',
        )
        self.env.statbox.bind_entry(
            'send_email',
            _inherit_from=['local_base'],
            action='send_confirmation_email',
            confirmation_checks_count='0',
        )

    def tearDown(self):
        self.code_generator_faker.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.code_generator_faker
        super(TestSendRegistrationConfirmationEmail, self).tearDown()

    def setup_blackbox_response(self, is_domain_pdd=False):
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1 if is_domain_pdd else 0),
        )

    def build_email(self, address, short_code, human_readable_address=None, language='en'):
        return {
            'language': language,
            'addresses': [address],
            'subject': 'emails.registration_confirmation_email_sent.subject',
            'SHORT_CODE': short_code,
            'tanker_keys': {
                'emails.registration_confirmation_email_sent.message': {
                    'ADDRESS': human_readable_address or address,
                },
                'emails.registration_confirmation_email_sent.short_code_age': {},
                'emails.registration_confirmation_email_sent.dont_worry': {},
            },
        }

    def check_email_sent(self,
                         address=TEST_NON_NATIVE_EMAIL,
                         human_readable_address=None,
                         short_code=TEST_SHORT_CODE,
                         language='en'):
        self.assert_emails_sent([
            self.build_email(
                address=address,
                human_readable_address=human_readable_address,
                short_code=short_code,
                language=language,
            ),
        ])

    def test_no_process_name(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = None
        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])

    def test_invalid_process_name(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = PROCESS_WEB_REGISTRATION[::-1]
        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'])

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(rv)
        self.check_email_sent()

        track = self.track_manager.read(self.track_id)
        ok_(track.email_confirmation_checks_count.get() is None)
        ok_(not track.email_confirmation_passed_at)
        eq_(track.email_confirmation_address, TEST_NON_NATIVE_EMAIL)
        eq_(track.email_confirmation_code, TEST_SHORT_CODE)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'new_code',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
                is_address_changed='0',
                is_limit_reached='0',
            ),
            self.env.statbox.entry(
                'send_email',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
            ),
        ])
        counter = register_email_per_email.get_counter()
        eq_(counter.get(TEST_NON_NATIVE_EMAIL), 1)

    def test_ok_portal_language(self):
        rv = self.make_request(
            query_args={
                'email': TEST_NON_NATIVE_EMAIL,
                'language': 'ro',  # язык содержится в PORTAL_LANGUAGES, но не в DISPLAY_LANGUAGES
                'track_id': self.track_id,
            },
        )

        self.assert_ok_response(rv)
        self.check_email_sent(language='ru'),  # фоллбек на русский язык

    def test_ok_no_captcha_just_phone(self):
        # если каптча не пройдена, но телефон подтверждён, то всё нормально
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_recognized = False
            track.is_captcha_checked = False
            track.phone_confirmation_is_confirmed = True
        self.test_ok()

    def test_ok_uppercase(self):
        query_args = dict(self.http_query_args)
        ok_(query_args['email'].lower())
        query_args['email'] = query_args['email'].upper()

        rv = self.make_request(query_args=query_args)

        self.assert_ok_response(rv)
        self.check_email_sent()

        track = self.track_manager.read(self.track_id)
        ok_(track.email_confirmation_checks_count.get() is None)
        ok_(not track.email_confirmation_passed_at)
        eq_(track.email_confirmation_address, TEST_NON_NATIVE_EMAIL)
        eq_(track.email_confirmation_code, TEST_SHORT_CODE)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'new_code',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
                is_address_changed='0',
                is_limit_reached='0',
            ),
            self.env.statbox.entry(
                'send_email',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
            ),
        ])
        counter = register_email_per_email.get_counter()
        eq_(counter.get(TEST_NON_NATIVE_EMAIL), 1)

    def test_ok_punycode(self):
        rv = self.make_request(query_args={'email': TEST_PUNYCODE_EMAIL})

        self.assert_ok_response(rv)
        self.check_email_sent(address=TEST_PUNYCODE_EMAIL, human_readable_address=TEST_UNICODE_EMAIL)

    def test_ok__yandexuid_is_optional_in_statbox_log(self):
        rv = self.make_request(exclude_headers=['cookie'])

        self.assert_ok_response(rv)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'new_code',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
                is_address_changed='0',
                is_limit_reached='0',
                _exclude=['yandexuid'],
            ),
            self.env.statbox.entry(
                'send_email',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
                _exclude=['yandexuid'],
            ),
        ])

    def test_no_phone_no_captcha(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_recognized = False
            track.is_captcha_checked = False
            track.phone_confirmation_is_confirmed = False
        rv = self.make_request()
        self.assert_error_response(rv, ['user.not_verified'])

    def test_native_email_error(self):
        rv = self.make_request(query_args={'email': TEST_EMAIL})
        self.assert_error_response(rv, ['email.native'])

    def test_pdd_email_error(self):
        self.setup_blackbox_response(is_domain_pdd=True)
        rv = self.make_request(query_args={'email': TEST_NON_NATIVE_EMAIL})
        self.assert_error_response(rv, ['domain.invalid_type'])

    def test_send_per_ip_limit(self):
        counter = register_email_per_ip.get_counter(TEST_IP)
        for _ in range(counter.limit - 1):
            counter.incr(TEST_IP)

        rv = self.make_request(headers={'user_ip': TEST_IP})
        self.assert_ok_response(rv)
        self.check_email_sent()

        rv = self.make_request(headers={'user_ip': TEST_IP})
        self.assert_error_response(rv, error_codes=['email.send_limit_exceeded'])

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'new_code',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
                is_address_changed='0',
                is_limit_reached='0',
                ip=TEST_IP,
            ),
            self.env.statbox.entry(
                'send_email',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
                ip=TEST_IP,
            ),
        ])

    def test_send_per_email_limit(self):
        counter = register_email_per_email.get_counter()
        for _ in range(counter.limit - 1):
            counter.incr(TEST_NON_NATIVE_EMAIL)

        rv = self.make_request()
        self.assert_ok_response(rv)
        self.check_email_sent()

        rv = self.make_request()
        self.assert_error_response(rv, error_codes=['email.send_limit_exceeded'])

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'new_code',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
                is_address_changed='0',
                is_limit_reached='0',
            ),
            self.env.statbox.entry(
                'send_email',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
            ),
        ])

    def test_send_per_email_limit_ok(self):
        counter = register_email_per_email.get_counter()
        for _ in range(counter.limit):
            counter.incr(TEST_NON_NATIVE_EMAIL)

        rv = self.make_request()
        self.assert_error_response(rv, error_codes=['email.send_limit_exceeded'])

        rv = self.make_request(query_args={'email': TEST_ANOTHER_NON_NATIVE_EMAIL})
        self.assert_ok_response(rv)
        self.check_email_sent(TEST_ANOTHER_NON_NATIVE_EMAIL)

    def test_dont_send_email_to_confirmed_address(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.email_confirmation_passed_at = get_unixtime()

        rv = self.make_request()

        self.assert_error_response(rv, error_codes=['email.already_confirmed'])

    def test_confirmed_count_is_logged(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.email_confirmation_checks_count.incr()
            track.email_confirmation_address = TEST_NON_NATIVE_EMAIL
            track.email_confirmation_code = TEST_SHORT_CODE

        rv = self.make_request()
        self.assert_ok_response(rv)
        self.check_email_sent()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'send_email',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
                confirmation_checks_count='1',
            ),
        ])

    def test_new_code_is_not_generated_if_invalid_limit_is_not_reached(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.email_confirmation_address = TEST_NON_NATIVE_EMAIL
            track.email_confirmation_code = TEST_SHORT_CODE[::-1]

        rv = self.make_request()

        self.assert_ok_response(rv)
        self.check_email_sent(short_code=TEST_SHORT_CODE[::-1])

        track = self.track_manager.read(self.track_id)
        eq_(track.email_confirmation_address, TEST_NON_NATIVE_EMAIL)
        eq_(track.email_confirmation_code, TEST_SHORT_CODE[::-1])

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'send_email',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
            ),
        ])

    def test_new_code_is_generated_when_limit_is_reached(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.email_confirmation_code = TEST_SHORT_CODE[::-1]
            track.email_confirmation_address = TEST_NON_NATIVE_EMAIL
            track.email_confirmation_checks_count.incr()
            track.email_confirmation_checks_count.incr()

        eq_(track.email_confirmation_checks_count.get(), 2)

        rv = self.make_request()

        self.assert_ok_response(rv)
        self.check_email_sent()

        track = self.track_manager.read(self.track_id)
        ok_(track.email_confirmation_checks_count.get() is None)
        eq_(track.email_confirmation_address, TEST_NON_NATIVE_EMAIL)
        eq_(track.email_confirmation_code, TEST_SHORT_CODE)
        ok_(track.email_confirmation_passed_at is None)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'new_code',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
                is_address_changed='0',
                is_limit_reached='1',
            ),
            self.env.statbox.entry(
                'send_email',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
            ),
        ])

    def test_new_address_resets_code(self):
        rv = self.make_request()

        self.assert_ok_response(rv)
        self.check_email_sent()

        track = self.track_manager.read(self.track_id)
        ok_(track.email_confirmation_checks_count.get() is None)
        eq_(track.email_confirmation_address, TEST_NON_NATIVE_EMAIL)
        eq_(track.email_confirmation_code, TEST_SHORT_CODE)

        self.code_generator_faker.set_return_value(TEST_SHORT_CODE[::-1])

        rv = self.make_request(query_args={'email': TEST_ANOTHER_NON_NATIVE_EMAIL})

        self.assert_ok_response(rv)
        self.assert_emails_sent([
            self.build_email(
                address=TEST_NON_NATIVE_EMAIL,
                short_code=TEST_SHORT_CODE,
            ),
            self.build_email(
                address=TEST_ANOTHER_NON_NATIVE_EMAIL,
                short_code=TEST_SHORT_CODE[::-1],
            ),
        ])

        track = self.track_manager.read(self.track_id)
        ok_(track.email_confirmation_checks_count.get() is None)
        eq_(track.email_confirmation_address, TEST_ANOTHER_NON_NATIVE_EMAIL)
        eq_(track.email_confirmation_code, TEST_SHORT_CODE[::-1])
        ok_(track.email_confirmation_passed_at is None)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'new_code',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
                is_address_changed='0',
                is_limit_reached='0',
            ),
            self.env.statbox.entry(
                'send_email',
                address=mask_email_for_statbox(TEST_NON_NATIVE_EMAIL),
            ),
            self.env.statbox.entry(
                'new_code',
                address=mask_email_for_statbox(TEST_ANOTHER_NON_NATIVE_EMAIL),
                is_address_changed='1',
                is_limit_reached='0',
            ),
            self.env.statbox.entry(
                'send_email',
                address=mask_email_for_statbox(TEST_ANOTHER_NON_NATIVE_EMAIL),
            ),
        ])
