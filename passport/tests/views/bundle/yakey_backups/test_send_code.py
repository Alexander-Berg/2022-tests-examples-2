# -*- coding: utf-8 -*-

import json

import mock
from nose.tools import eq_
from passport.backend.api.common.phone import PhoneAntifraudFeatures
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_CONFIRMATION_CODE,
    TEST_CONFIRMATION_CODE_1,
    TEST_COUNTRY_CODE,
    TEST_DISPLAY_LANGUAGE,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER1,
    TEST_PHONE_NUMBER_DUMPED,
    TEST_PHONE_NUMBER_DUMPED1,
    TEST_USER_IP,
)
from passport.backend.core.builders.antifraud import ScoreAction
from passport.backend.core.builders.antifraud.faker.fake_antifraud import antifraud_score_response
from passport.backend.core.counters import (
    sms_per_ip,
    sms_per_phone,
)
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.utils.time import datetime_to_integer_unixtime

from .base import BaseYaKeyBackupTestView


@with_settings_hosts(
    ALL_SUPPORTED_LANGUAGES={
        'all': ['ru', 'en', 'uk'],
        'default': 'ru',
    },
    DISPLAY_LANGUAGES=['en', 'ru'],
    PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
    SMS_VALIDATION_RESEND_TIMEOUT=0,
    **mock_counters(
        PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(1, 30, 2),
        UNTRUSTED_PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(1, 30, 2),
    )
)
class TestSendCodeTestCase(BaseYaKeyBackupTestView):
    default_url = '/1/bundle/yakey_backup/send_code/?consumer=mobileproxy'
    http_method = 'post'
    http_query_args = {
        'number': TEST_PHONE_NUMBER.e164,
        'country': TEST_COUNTRY_CODE,
        'display_language': TEST_DISPLAY_LANGUAGE,
    }

    step = 'send_code'

    def setUp(self):
        super(TestSendCodeTestCase, self).setUp()
        self.env.antifraud_api.set_response_value('score', antifraud_score_response())

    def get_expected_response(self):
        return {
            'track_id': self.track_id,
            'number': TEST_PHONE_NUMBER_DUMPED,
        }

    def setup_statbox_templates(self):
        super(TestSendCodeTestCase, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'send_code_error',
            _inherit_from=['local_base'],
            action='send_confirmation_code',
            error='sms_limit.exceeded',
        )
        self.env.statbox.bind_entry(
            'base_pharma',
            _inherit_from=['local_base'],
            action='send_confirmation_code',
            antifraud_reason='some-reason',
            antifraud_tags='',
            scenario='register',
        )
        self.env.statbox.bind_entry(
            'pharma_allowed',
            _inherit_from=['base_pharma'],
            antifraud_action='ALLOW',
        )
        self.env.statbox.bind_entry(
            'pharma_denied',
            _inherit_from=['base_pharma'],
            antifraud_action='DENY',
            error='antifraud_score_deny',
            mask_denial='0',
            status='error',
        )

    def assert_ok_pharma_request(self, request):
        request_data = json.loads(request.post_args)
        features = PhoneAntifraudFeatures.default(
            sub_channel='mobileproxy',
            user_phone_number=TEST_PHONE_NUMBER,
        )
        features.external_id = 'track-{}'.format(self.track_id)
        features.phone_confirmation_method = 'by_sms'
        features.t = TimeNow(as_milliseconds=True)
        features.request_path = '/1/bundle/yakey_backup/send_code/'
        features.scenario = 'register'
        features.add_headers_features(mock_headers(**self.http_headers))
        assert request_data == features.as_score_dict()

    def test_send_ok(self):
        resp = self.make_request(
            query_args=dict(
                display_language='fr',
            ),
        )
        self.assert_ok_response(resp, **self.get_expected_response())
        track = self.track_manager.read(self.track_id)
        eq_(track.phone_confirmation_code, TEST_CONFIRMATION_CODE)
        eq_(track.phone_confirmation_last_send_at, TimeNow())
        eq_(track.phone_confirmation_is_confirmed, False)
        eq_(track.phone_confirmation_sms_count.get(default=0), 1)
        eq_(track.phone_confirmation_confirms_count.get(default=0), 0)
        eq_(track.phone_confirmation_phone_number_original, TEST_PHONE_NUMBER.original)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pharma_allowed'),
            self.env.statbox.entry('succeeded'),
        ])

    def test_invalid_form(self):
        resp = self.make_request(
            query_args=dict(
                number='',
                display_language='fyr-fyr',
            ),
        )
        self.assert_error_response(resp, ['number.empty'])
        self.assert_sms_not_sent()
        self.env.statbox.assert_has_written([])

    def test_wrong_process(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.process_name = 'restore'

        resp = self.make_request(query_args={'track_id': self.track_id})
        self.assert_error_response(resp, ['track.invalid_state'])
        self.assert_sms_not_sent()
        self.env.statbox.assert_has_written([])

    def test_already_confirmed(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.process_name = 'yakey_backup'
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number_original = TEST_PHONE_NUMBER.original

        resp = self.make_request(query_args={'track_id': self.track_id})
        self.assert_error_response(resp, ['phone.confirmed'], **self.get_expected_response())
        self.assert_sms_not_sent()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('send_code_error', error='phone.confirmed'),
            ],
        )

    def test_reconfirmation_limit_exceeded(self):
        with settings_context(SMS_VALIDATION_RESEND_TIMEOUT=30):
            with self.track_manager.transaction(self.track_id).commit_on_error() as track:
                track.process_name = 'yakey_backup'
                track.phone_confirmation_last_send_at = datetime_to_integer_unixtime(DatetimeNow())

            resp = self.make_request(query_args={'track_id': self.track_id})
            self.assert_error_response(resp, ['sms_limit.exceeded'], **self.get_expected_response())
            self.assert_sms_not_sent()
            self.env.statbox.assert_equals(
                [
                    self.env.statbox.entry('send_code_error', reason='rate_limit'),
                ],
            )

    def test_ip_limit_exceeded(self):
        counter = sms_per_ip.get_counter(TEST_USER_IP)
        for _ in range(counter.limit):
            counter.incr(TEST_USER_IP)
        resp = self.make_request()
        self.assert_error_response(resp, ['sms_limit.exceeded'], **self.get_expected_response())
        self.assert_sms_not_sent()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('send_code_error', reason='ip_limit'),
            ],
        )

    def test_phone_limit_exceeded(self):
        counter = sms_per_phone.get_per_phone_buckets()
        for _ in range(counter.limit):
            counter.incr(TEST_PHONE_NUMBER.digital)
        resp = self.make_request()
        self.assert_error_response(resp, ['sms_limit.exceeded'], **self.get_expected_response())
        self.assert_sms_not_sent()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('pharma_allowed'),
                self.env.statbox.entry('send_code_error'),
            ],
        )

    def test_no_process_name_error(self):
        resp = self.make_request(query_args={'track_id': self.track_id})
        self.assert_error_response(resp, ['track.invalid_state'])
        self.env.statbox.assert_has_written([])

    def test_different_code_with_different_numbers_ok(self):
        with mock.patch(
                'passport.backend.utils.common._generate_random_code',
                mock.Mock(side_effect=[
                    TEST_CONFIRMATION_CODE,
                    TEST_CONFIRMATION_CODE_1,
                ]),
        ):
            resp1 = self.make_request()
            self.assert_ok_response(resp1, **self.get_expected_response())
            track = self.track_manager.read(self.track_id)
            eq_(track.phone_confirmation_code, TEST_CONFIRMATION_CODE)
            eq_(track.phone_confirmation_last_send_at, TimeNow())
            eq_(track.phone_confirmation_is_confirmed, False)
            eq_(track.phone_confirmation_sms_count.get(default=0), 1)
            eq_(track.phone_confirmation_confirms_count.get(default=0), 0)
            eq_(track.phone_confirmation_phone_number_original, TEST_PHONE_NUMBER.original)

            resp2 = self.make_request(
                query_args={
                    'number': TEST_PHONE_NUMBER1.e164,
                    'track_id': self.track_id,
                },
            )
            expected_response = self.get_expected_response()
            expected_response.update(number=TEST_PHONE_NUMBER_DUMPED1)
            self.assert_ok_response(resp2, **expected_response)
            track = self.track_manager.read(self.track_id)
            eq_(track.phone_confirmation_code, TEST_CONFIRMATION_CODE_1)
            eq_(track.phone_confirmation_last_send_at, TimeNow())
            eq_(track.phone_confirmation_is_confirmed, False)
            eq_(track.phone_confirmation_sms_count.get(default=0), 1)
            eq_(track.phone_confirmation_confirms_count.get(default=0), 0)
            eq_(track.phone_confirmation_phone_number_original, TEST_PHONE_NUMBER1.original)

    def test_track_state_updated_on_phone_change_with_sending_error(self):
        with settings_context(SMS_VALIDATION_RESEND_TIMEOUT=30), mock.patch(
                'passport.backend.utils.common._generate_random_code',
                mock.Mock(side_effect=[
                    TEST_CONFIRMATION_CODE,
                    TEST_CONFIRMATION_CODE_1,
                ]),
        ):
            resp1 = self.make_request()
            self.assert_ok_response(resp1, **self.get_expected_response())
            track = self.track_manager.read(self.track_id)
            eq_(track.phone_confirmation_code, TEST_CONFIRMATION_CODE)
            eq_(track.phone_confirmation_last_send_at, TimeNow())
            eq_(track.phone_confirmation_is_confirmed, False)
            eq_(track.phone_confirmation_sms_count.get(default=0), 1)
            eq_(track.phone_confirmation_confirms_count.get(default=0), 0)
            eq_(track.phone_confirmation_phone_number_original, TEST_PHONE_NUMBER.original)

            resp2 = self.make_request(
                query_args={
                    'number': TEST_PHONE_NUMBER1.e164,
                    'track_id': self.track_id,
                },
            )
            expected_response = self.get_expected_response()
            expected_response.update(number=TEST_PHONE_NUMBER_DUMPED1)
            self.assert_error_response(resp2, ['sms_limit.exceeded'], **expected_response)
            track = self.track_manager.read(self.track_id)
            # Сбросили код
            eq_(track.phone_confirmation_code, None)
            eq_(track.phone_confirmation_last_send_at, TimeNow())
            eq_(track.phone_confirmation_is_confirmed, False)
            eq_(track.phone_confirmation_sms_count.get(default=0), 0)
            eq_(track.phone_confirmation_confirms_count.get(default=0), 0)
            eq_(track.phone_confirmation_phone_number_original, TEST_PHONE_NUMBER1.original)

    def test_pharma_denied(self):
        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response(action=ScoreAction.DENY)])

        resp = self.make_request()

        self.assert_error_response(resp, ['sms_limit.exceeded'], **self.get_expected_response())
        self.assert_sms_not_sent()
        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry('pharma_denied'),
            ],
        )

        assert len(self.env.antifraud_api.requests) == 1
        self.assert_ok_pharma_request(self.env.antifraud_api.requests[0])
