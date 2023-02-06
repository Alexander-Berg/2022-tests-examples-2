# -*- coding: utf-8 -*-

import json
import random
import time

import mock
from nose.tools import (
    eq_,
    istest,
    nottest,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.common.phone import (
    CONFIRM_METHOD_BY_CALL,
    CONFIRM_METHOD_BY_FLASH_CALL,
    CONFIRM_METHOD_BY_SMS,
)
from passport.backend.api.common.phone_karma import PhoneKarma
from passport.backend.api.common.processes import PROCESS_WEB_REGISTRATION
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_CALL_SESSION_ID,
    TEST_PDD_LOGIN,
    TEST_PDD_UID,
    TEST_PHONE_ID1,
    TEST_PHONE_NUMBER_DUMPED_MASKED,
    TEST_RETPATH,
    TEST_SMS_RETRIEVER_TEXT,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_IP,
)
from passport.backend.api.views.bundle.mixins.phone import (
    format_for_android_sms_retriever,
    hash_android_package,
    KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG,
)
from passport.backend.api.views.bundle.phone.controllers import (
    CONFIRM_STATE,
    CONFIRM_TRACKED_SECURE_STATE,
)
from passport.backend.api.views.bundle.phone.helpers import format_code_by_3
from passport.backend.core.builders.antifraud import BaseAntifraudApiError
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.builders.kolmogor import KolmogorPermanentError
from passport.backend.core.builders.octopus import OctopusPermanentError
from passport.backend.core.builders.octopus.faker import octopus_response
from passport.backend.core.builders.ufo_api.faker import ufo_api_phones_stats_response
from passport.backend.core.builders.yasms.exceptions import YaSmsTemporaryBlock
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.conf import settings
from passport.backend.core.counters import (
    calls_per_ip,
    calls_per_phone,
)
from passport.backend.core.models.phones.faker import (
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    TimeNow,
    TimeSpan,
)
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)

from .base import (
    BaseConfirmCommitterTestCase,
    BaseConfirmSubmitterTestCase,
    ConfirmCommitterLocalPhonenumberTestMixin,
    ConfirmCommitterSentCodeTestMixin,
    ConfirmCommitterTestMixin,
    ConfirmSubmitterAlreadyConfirmedPhoneWithNewPhoneTestMixin,
    ConfirmSubmitterChangePasswordNewSecureNumberTestMixin,
    ConfirmSubmitterLocalPhonenumberMixin,
    ConfirmSubmitterSendSmsTestMixin,
    FAKE_OCTOPUS_SESSION_ID_FOR_TEST_PHONES,
    TEST_FAKE_CODE,
    TEST_FAKE_PHONE_NUMBER,
    TEST_FAKE_PHONE_NUMBER_DUMPED,
    TEST_HOST,
    TEST_NOT_EXIST_PHONE_NUMBER,
    TEST_NOT_EXIST_PHONE_NUMBER_DUMPED,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER1,
    TEST_PHONE_NUMBER_DUMPED1,
    TEST_TAXI_APPLICATION,
)


TEST_KOLMOGOR_KEYSPACE_COUNTERS = 'octopus-calls-counters'
TEST_KOLMOGOR_KEYSPACE_FLAG = 'octopus-calls-flag'
TEST_CALLING_NUMBER_SUFFIX = '+11111110000'
TEST_CALLING_NUMBER_TEMPLATE = '+1 1111110000'
TEST_CALLING_NUMBER_TEMPLATE_HUMAN_READABLE = '+1 111111XXXX'

COMMON_SETTINGS = dict(
    YASMS_URL='http://localhost',
    OCTOPUS_URL='http://localhost',
    OCTOPUS_TIMEOUT=2,
    OCTOPUS_RETRIES=1,
    OCTOPUS_AUTH_TOKEN='key',
    SMS_VALIDATION_CODE_LENGTH=6,
    SMS_VALIDATION_RESEND_TIMEOUT=0,
    SMS_VALIDATION_MAX_SMS_COUNT=3,
    APP_ID_SPECIFIC_ROUTE_DENOMINATOR=1,
    PHONE_VALIDATION_MAX_CALLS_COUNT=2,
    PHONE_VALIDATION_MAX_CALLS_CHECKS_COUNT=2,
    APP_ID_TO_SMS_ROUTE={TEST_TAXI_APPLICATION: 'taxi'},
    OCTOPUS_COUNTERS_MIN_COUNT=10,
    OCTOPUS_GATES_WORKING_THRESHOLD=0.9,
    KOLMOGOR_KEYSPACE_OCTOPUS_CALLS_COUNTERS=TEST_KOLMOGOR_KEYSPACE_COUNTERS,
    KOLMOGOR_KEYSPACE_OCTOPUS_CALLS_FLAG=TEST_KOLMOGOR_KEYSPACE_FLAG,
    KOLMOGOR_URL='http://localhost',
    KOLMOGOR_TIMEOUT=1,
    KOLMOGOR_RETRIES=1,
    FLASH_CALL_NUMBERS=[TEST_CALLING_NUMBER_SUFFIX],
    PHONE_CONFIRM_CHECK_IP_BLACKLIST=True,
    PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
    PHONE_CONFIRM_MASK_ANTIFRAUD_DENIAL=False,
    PHONE_CONFIRM_SHOW_ANTIFRAUD_CAPTCHA_FOR_CONSUMERS=['dev'],
    **mock_counters()
)


@nottest
class CommonConfirmSubmitter(
        BaseConfirmSubmitterTestCase,
        ConfirmSubmitterSendSmsTestMixin,
        ConfirmSubmitterChangePasswordNewSecureNumberTestMixin,
        ConfirmSubmitterLocalPhonenumberMixin,
        ConfirmSubmitterAlreadyConfirmedPhoneWithNewPhoneTestMixin):

    track_state = CONFIRM_STATE
    has_uid = False
    url = '/1/bundle/phone/confirm/submit/?consumer=dev'
    with_antifraud_score = True

    def setUp(self):
        super(CommonConfirmSubmitter, self).setUp()
        self._random_faker = mock.Mock(wraps=random.SystemRandom)
        self._random_faker_patch = mock.patch(u'passport.backend.api.views.bundle.phone.helpers.random.SystemRandom', self._random_faker)
        self._random_faker_patch.start()

    def tearDown(self):
        self._random_faker_patch.stop()
        super(CommonConfirmSubmitter, self).tearDown()

    def query_params(self, **kwargs):
        base_params = {
            'display_language': 'ru',
            'track_id': self.track_id,
        }
        if not ('phone_id' in kwargs or 'number' in kwargs):
            base_params['number'] = TEST_PHONE_NUMBER.e164

        return merge_dicts(base_params, kwargs)

    def test_ok_without_country(self):
        rv = self.make_request()
        self.assert_ok_response(
            rv,
            **self.base_send_code_response
        )

        eq_(self._code_generator_faker.call_count, 1)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'identity': 'confirm',
            'caller': 'dev',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)
        ok_(track.country is None)

        self.assert_statbox_ok(with_antifraud_score=True)

    def test_registration_process_name_ok(self):
        self.env.ufo_api.set_response_value(
            'phones_stats',
            ufo_api_phones_stats_response(TEST_PHONE_NUMBER),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = PROCESS_WEB_REGISTRATION

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            **self.base_send_code_response
        )

        eq_(self._code_generator_faker.call_count, 1)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'identity': 'confirm',
            'caller': 'dev',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)
        ok_(track.country is None)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_phone_karma'),
            self.env.statbox.entry('antifraud_score_allow'),
            self.env.statbox.entry('send_code'),
            self.env.statbox.entry('success'),
        ])

    def test_registration_bad_phone_karma_error(self):
        self.env.ufo_api.set_response_value(
            'phones_stats',
            ufo_api_phones_stats_response(
                TEST_PHONE_NUMBER,
                {'phone_number_counter': 100},
            ),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = PROCESS_WEB_REGISTRATION

        rv = self.make_request()
        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        rv = json.loads(rv.data)
        eq_(rv['status'], 'error')
        eq_(rv['errors'], ['phone.compromised'])

        eq_(self._code_generator_faker.call_count, 0)

        requests = self.env.yasms.requests
        eq_(len(requests), 0)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_phone_karma', karma=str(PhoneKarma.black)),
        ])

    def test_unsupported_process_name(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = 'some-process-name'

        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['track.invalid_state'],
        )

    def test_ok_with_ios_code_format(self):
        with self.track_transaction(self.track_id) as track:
            track.device_os_id = 'iPhone'

        rv = self.make_request(
            headers={
                'Ya-Client-Host': TEST_HOST,
                'Ya-Consumer-Client-Ip': TEST_USER_IP,
                'Ya-Client-User-Agent': 'com.yandex.mobile.auth.sdk/4.211.238 (Apple iPhone8,1; iOS 11.2.5)',
            },
        )

        self.assert_ok_response(
            rv,
            **self.base_send_code_response
        )
        eq_(self._code_generator_faker.call_count, 1)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)

        self.confirmation_code = format_code_by_3(self.confirmation_code, delimiter='-')

        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'identity': 'confirm',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

    @parameterized.expand([('by_3'), ('by_3_dash')])
    def test_ok_with_code_format(self, code_format):
        rv = self.make_request(
            self.query_params(code_format=code_format),
        )
        if code_format == 'by_3':
            self.confirmation_code = format_code_by_3(self.confirmation_code)
        else:
            self.confirmation_code = format_code_by_3(self.confirmation_code, delimiter='-')

        self.assert_ok_response(
            rv,
            **self.base_send_code_response
        )

        eq_(self._code_generator_faker.call_count, 1)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'identity': 'confirm',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)

        self.assert_statbox_ok(with_antifraud_score=True)

    def test_ok_with_country(self):
        rv = self.make_request(
            self.query_params(country='ru'),
        )
        self.assert_ok_response(
            rv,
            **self.base_send_code_response
        )

        eq_(self._code_generator_faker.call_count, 1)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'identity': 'confirm',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)
        eq_(track.country, 'ru')

        self.assert_statbox_ok(with_antifraud_score=True)

    def test_ok_with_phone_id(self):
        with self.track_transaction() as track:
            track.uid = TEST_UID
        userinfo_kwargs = deep_merge(
            dict(uid=TEST_UID),
            build_phone_bound(phone_id=TEST_PHONE_ID1, phone_number=TEST_PHONE_NUMBER.e164),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**userinfo_kwargs),
        )

        rv = self.make_request(
            self.query_params(phone_id=TEST_PHONE_ID1),
        )
        self.assert_ok_response(
            rv,
            **merge_dicts(
                self.base_send_code_response,
                {'number': TEST_PHONE_NUMBER_DUMPED_MASKED},
            )
        )

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track, return_masked_number=True)

        self.assert_statbox_ok(uid=str(TEST_UID), with_antifraud_score=True)

    def test_ok_with_secured_phone_id(self):
        with self.track_transaction() as track:
            track.uid = TEST_UID
        userinfo_kwargs = deep_merge(
            dict(uid=TEST_UID),
            build_phone_secured(phone_id=TEST_PHONE_ID1, phone_number=TEST_PHONE_NUMBER.e164),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**userinfo_kwargs),
        )

        rv = self.make_request(
            self.query_params(phone_id=TEST_PHONE_ID1),
        )
        self.assert_ok_response(
            rv,
            **merge_dicts(
                self.base_send_code_response,
                {'number': TEST_PHONE_NUMBER_DUMPED_MASKED},
            )
        )

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track, return_masked_number=True)
        self.assert_antifraud_score_called(uid=TEST_UID, is_secure_phone=True)

        self.assert_statbox_ok(uid=str(TEST_UID), with_antifraud_score=True)

    def test_submit_with_invalid_phone_id(self):
        with self.track_transaction() as track:
            track.uid = TEST_UID
        userinfo_kwargs = deep_merge(
            dict(uid=TEST_UID),
            build_phone_bound(phone_id=TEST_PHONE_ID1, phone_number=TEST_PHONE_NUMBER.e164),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**userinfo_kwargs),
        )

        rv = self.make_request(
            self.query_params(phone_id=TEST_PHONE_ID1+1000),
        )

        self.assert_error_response(
            rv,
            ['phone.not_found'],
            track_id=self.track_id,
            global_sms_id=self.env.yasms_fake_global_sms_id_mock.return_value,
        )

    def test_ok_for_pdd(self):
        with self.track_transaction() as track:
            track.uid = TEST_PDD_UID
        userinfo_kwargs = deep_merge(
            dict(
                uid=TEST_PDD_UID,
                aliases={'pdd': TEST_PDD_LOGIN},
            ),
            build_phone_bound(phone_id=TEST_PHONE_ID1, phone_number=TEST_PHONE_NUMBER.e164),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**userinfo_kwargs),
        )

        rv = self.make_request(
            self.query_params(phone_id=TEST_PHONE_ID1),
        )
        self.assert_ok_response(
            rv,
            **merge_dicts(
                self.base_send_code_response,
                {'number': TEST_PHONE_NUMBER_DUMPED_MASKED},
            )
        )

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track, return_masked_number=True)

        self.assert_statbox_ok(uid=str(TEST_PDD_UID), with_antifraud_score=True)

    def test_ok_with_another_confirmation_method(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_method = 'by_call'
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_confirms_count.incr()
            track.phone_confirmation_calls_count.incr()
            track.phone_confirmation_last_called_at = time.time()

        rv = self.make_request(self.query_params())

        self.assert_ok_response(
            rv,
            **self.base_send_code_response
        )

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)

        self.assert_statbox_ok(with_antifraud_score=True)

    def test_change_password_send_sms_only_on_secure_phone_number(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_password_change = True
            track.has_secure_phone_number = True
            track.secure_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request(
            self.query_params(number=TEST_NOT_EXIST_PHONE_NUMBER.e164),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        rv = json.loads(rv.data)
        eq_(rv['status'], 'error')
        eq_(rv['errors'], ['number.invalid'])

        self.assert_statbox_no_send_entries(phone_number=TEST_NOT_EXIST_PHONE_NUMBER)

    def test_force_change_password_send_sms_only_on_secure_phone_number_and_hint_not_passed_with_phone_karma_check(self):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.env.ufo_api.set_response_value(
            'phones_stats',
            ufo_api_phones_stats_response(TEST_NOT_EXIST_PHONE_NUMBER),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_password_change = True
            track.is_force_change_password = True
            track.has_secure_phone_number = True
            track.secure_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request(
            self.query_params(number=TEST_NOT_EXIST_PHONE_NUMBER.e164),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        rv = json.loads(rv.data)
        eq_(rv['status'], 'error')
        eq_(rv['errors'], ['number.invalid'])

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'check_phone_karma',
                track_id=self.track_id,
                number=TEST_NOT_EXIST_PHONE_NUMBER.masked_format_for_statbox,
            ),
        ])

    def test_force_change_password_send_sms_only_on_secure_phone_number_and_hint_passed_with_phone_karma_check(self):
        self.env.ufo_api.set_response_value(
            'phones_stats',
            ufo_api_phones_stats_response(TEST_NOT_EXIST_PHONE_NUMBER),
        )
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_password_change = True
            track.is_force_change_password = True
            track.is_fuzzy_hint_answer_checked = True
            track.has_secure_phone_number = True
            track.secure_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request(
            self.query_params(number=TEST_NOT_EXIST_PHONE_NUMBER.e164),
        )
        self.assert_ok_response(
            rv,
            **merge_dicts(
                self.base_send_code_response,
                {
                    'track_id': self.track_id,
                    'number': TEST_NOT_EXIST_PHONE_NUMBER_DUMPED,
                },
            )
        )

        requests = self.env.yasms.requests
        requests[0].assert_query_contains({
            'phone': TEST_NOT_EXIST_PHONE_NUMBER.e164,
            'identity': 'confirm',
        })

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'check_phone_karma',
                track_id=self.track_id,
                number=TEST_NOT_EXIST_PHONE_NUMBER.masked_format_for_statbox,
            ),
            self.env.statbox.entry(
                'antifraud_score_allow',
                track_id=self.track_id,
                number=TEST_NOT_EXIST_PHONE_NUMBER.masked_format_for_statbox,
                scenario='authorize',
            ),
            self.env.statbox.entry(
                'send_code',
                track_id=self.track_id,
                number=TEST_NOT_EXIST_PHONE_NUMBER.masked_format_for_statbox,
            ),
            self.env.statbox.entry(
                'success',
                track_id=self.track_id,
                number=TEST_NOT_EXIST_PHONE_NUMBER.masked_format_for_statbox,
            ),
        ])

    def test_force_change_password_send_sms_only_on_secure_phone_number_and_short_form_passed_with_phone_karma_check(self):
        self.env.ufo_api.set_response_value(
            'phones_stats',
            ufo_api_phones_stats_response(TEST_NOT_EXIST_PHONE_NUMBER),
        )
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_password_change = True
            track.is_force_change_password = True
            track.is_short_form_factors_checked = True
            track.has_secure_phone_number = True
            track.secure_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request(
            self.query_params(number=TEST_NOT_EXIST_PHONE_NUMBER.e164),
        )
        self.assert_ok_response(
            rv,
            **merge_dicts(
                self.base_send_code_response,
                {
                    'track_id': self.track_id,
                    'number': TEST_NOT_EXIST_PHONE_NUMBER_DUMPED,
                },
            )
        )

        requests = self.env.yasms.requests
        requests[0].assert_query_contains({
            'phone': TEST_NOT_EXIST_PHONE_NUMBER.e164,
            'identity': 'confirm',
        })

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'check_phone_karma',
                track_id=self.track_id,
                number=TEST_NOT_EXIST_PHONE_NUMBER.masked_format_for_statbox,
            ),
            self.env.statbox.entry(
                'antifraud_score_allow',
                track_id=self.track_id,
                number=TEST_NOT_EXIST_PHONE_NUMBER.masked_format_for_statbox,
                scenario='authorize',
            ),
            self.env.statbox.entry(
                'send_code',
                track_id=self.track_id,
                number=TEST_NOT_EXIST_PHONE_NUMBER.masked_format_for_statbox,
            ),
            self.env.statbox.entry(
                'success',
                track_id=self.track_id,
                number=TEST_NOT_EXIST_PHONE_NUMBER.masked_format_for_statbox,
            ),
        ])

    def test_force_change_password_hint_passed_with_bad_phone_karma_error(self):
        self.env.ufo_api.set_response_value(
            'phones_stats',
            ufo_api_phones_stats_response(
                TEST_NOT_EXIST_PHONE_NUMBER,
                {'phone_number_counter': 100},
            ),
        )
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_password_change = True
            track.is_force_change_password = True
            track.is_fuzzy_hint_answer_checked = True
            track.has_secure_phone_number = True
            track.secure_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request(
            self.query_params(number=TEST_NOT_EXIST_PHONE_NUMBER.e164),
        )
        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        rv = json.loads(rv.data)
        eq_(rv['status'], 'error')
        eq_(rv['errors'], ['phone.compromised'])

        eq_(self._code_generator_faker.call_count, 0)

        requests = self.env.yasms.requests
        eq_(len(requests), 0)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'check_phone_karma',
                track_id=self.track_id,
                number=TEST_NOT_EXIST_PHONE_NUMBER.masked_format_for_statbox,
                karma=str(PhoneKarma.black),
            ),
        ])

    def test_no_sms_text_and_code_in_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_phone_number_original = TEST_PHONE_NUMBER.original

        rv = self.make_request(
            self.query_params(),
        )
        self.assert_ok_response(
            rv,
            **self.base_send_code_response
        )

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'identity': 'confirm',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

    def test_submit_with_confirm_tracked_secure_state_and_already_confirmed_phone_with_new_phone(self):
        self.setup_track_for_commit(
            state=CONFIRM_TRACKED_SECURE_STATE,
            exclude=['country'],
            is_successful_phone_passed=1,
            phone_confirmation_is_confirmed=1,
            phone_confirmation_sms_count=2,
            phone_confirmation_confirms_count=2,
        )

        rv = self.make_request(
            self.query_params(number=TEST_NOT_EXIST_PHONE_NUMBER.e164),
        )
        self.assert_ok_response(
            rv,
            **merge_dicts(
                self.base_send_code_response,
                {
                    u'number': {
                        u'international': u'+7 916 123-45-67',
                        u'e164': u'+79161234567',
                        u'original': u'+79161234567',

                        u'masked_international': u'+7 916 ***-**-67',
                        u'masked_e164': u'+7916*****67',
                        u'masked_original': u'+7916*****67',
                    },
                },
                self.additional_ok_response_params,
            )
        )

        eq_(self._code_generator_faker.call_count, 1)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_NOT_EXIST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'identity': 'confirm',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

        track = self.track_manager.read(self.track_id)

        eq_(track.phone_confirmation_phone_number, TEST_NOT_EXIST_PHONE_NUMBER.e164)
        eq_(track.phone_confirmation_phone_number_original, TEST_NOT_EXIST_PHONE_NUMBER.original)
        eq_(track.phone_confirmation_code, str(self.confirmation_code))
        eq_(track.phone_confirmation_first_send_at, TimeNow())
        eq_(track.phone_confirmation_last_send_at, TimeNow())
        eq_(track.phone_confirmation_sms_count.get(), 1)
        ok_(not track.phone_confirmation_is_confirmed)
        ok_(not track.phone_confirmation_send_count_limit_reached)
        ok_(not track.phone_confirmation_send_ip_limit_reached)
        eq_(track.phone_confirmation_confirms_count.get(), None)
        ok_(not track.is_successful_phone_passed)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'antifraud_score_allow',
                number=TEST_NOT_EXIST_PHONE_NUMBER.masked_format_for_statbox,
            ),
            self.env.statbox.entry(
                'send_code',
                number=TEST_NOT_EXIST_PHONE_NUMBER.masked_format_for_statbox,
            ),
            self.env.statbox.entry(
                'success',
                number=TEST_NOT_EXIST_PHONE_NUMBER.masked_format_for_statbox,
            ),
        ])

    def test_submit_from_blacklisted_ip(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164

        with mock.patch(
            'passport.backend.api.common.ip.is_ip_blacklisted',
            return_value=True,
        ):
            rv = self.make_request(dict(self.query_params(), confirm_method=CONFIRM_METHOD_BY_SMS))

        self.assert_ok_response(rv, check_all=False)

    @parameterized.expand([
        ('phone_valid_for_call', CONFIRM_METHOD_BY_CALL),
        ('phone_valid_for_flash_call', CONFIRM_METHOD_BY_FLASH_CALL),
        (None, CONFIRM_METHOD_BY_SMS),
    ])
    def test_submit_from_blacklisted_ip_whitelisted_consumer(self, phone_valid_for, confirm_method):
        self.env.octopus.set_response_value('create_session', octopus_response(123))
        self.env.octopus.set_response_value('create_flash_call_session', octopus_response(123))
        with self.track_manager.transaction(
                self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            if phone_valid_for:
                setattr(track, phone_valid_for, True)

        with mock.patch(
                'passport.backend.api.common.ip.is_ip_blacklisted',
                return_value=True,
        ):
            with settings_context(**dict(
                COMMON_SETTINGS,
                PHONE_WHITELISTED_CONSUMERS=['dev'],
            )):
                rv = self.make_request(
                    dict(self.query_params(), confirm_method=confirm_method))

        self.assert_ok_response(rv, check_all=False)

    def test_submit_by_call__ok(self):
        self.env.octopus.set_response_value('create_session', octopus_response(123))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_call = True

        rv = self.make_request(dict(self.query_params(), confirm_method='by_call'))
        self.assert_ok_response(
            rv,
            **dict(self.base_submitter_response, code_length=settings.SMS_VALIDATION_CODE_LENGTH)
        )
        self.assert_statbox_ok_with_call(
            call_session_id='123',
            with_antifraud_score=True,
        )

        first_code, second_code = format_code_by_3(self.confirmation_code).split()
        self.env.octopus.requests[0].assert_properties_equal(
            method='POST',
            json_data={
                'firstCode': int(first_code),
                'secondCode': int(second_code),
                'caller': settings.PASSPORT_CALLING_NUMBER,
                'callee': TEST_PHONE_NUMBER.e164,
                'locale': 'ru',
            },
        )

        track = self.track_manager.read(self.track_id)
        self.check_ok_track_by_call(track, call_session_id='123')
        self.check_ok_counters_by_call()
        self.assert_kolmogor_called(3)

    def test_submit_by_call_with_unsupported_language_ok(self):
        self.env.octopus.set_response_value('create_session', octopus_response(123))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_call = True

        rv = self.make_request(dict(self.query_params(display_language='tr'), confirm_method='by_call'))
        self.assert_ok_response(
            rv,
            **dict(self.base_submitter_response, code_length=settings.SMS_VALIDATION_CODE_LENGTH)
        )
        self.assert_statbox_ok_with_call(
            call_session_id='123',
            with_antifraud_score=True,
        )

        first_code, second_code = format_code_by_3(self.confirmation_code).split()
        self.env.octopus.requests[0].assert_properties_equal(
            method='POST',
            json_data={
                'firstCode': int(first_code),
                'secondCode': int(second_code),
                'caller': settings.PASSPORT_CALLING_NUMBER,
                'callee': TEST_PHONE_NUMBER.e164,
                'locale': 'en',
            },
        )

    def test_submit_by_call_again__ok(self):
        self.env.octopus.set_response_value('create_session', octopus_response(123))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_method = 'by_call'
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_call = True
            track.phone_confirmation_code = '321132'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request(dict(self.query_params(), confirm_method='by_call'))
        self.assert_ok_response(
            rv,
            **dict(self.base_submitter_response, code_length=6)
        )
        self.assert_statbox_ok_with_call(
            call_session_id='123',
            with_antifraud_score=True,
        )
        ok_(not self._code_generator_faker.call_count)

        track = self.track_manager.read(self.track_id)
        self.check_ok_track_by_call(track, call_session_id='123', code='321132')
        self.check_ok_counters_by_call()
        self.assert_kolmogor_called(3)

    def test_submit_by_call__track_no_validated_phone__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_valid_for_call = True

        rv = self.make_request(self.query_params(confirm_method='by_call'))
        self.assert_error_response(rv, ['track.invalid_state'], **self.base_error_kwargs)

        ok_(not self.env.octopus.requests)
        ok_(not self.env.kolmogor.requests)
        self.assert_statbox_no_send_entries()

    def test_submit_by_call__ip_limit_reached__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_call = True

        counter = calls_per_ip.get_counter(TEST_USER_IP)
        for _ in range(counter.limit):
            counter.incr(TEST_USER_IP)

        rv = self.make_request(self.query_params(confirm_method='by_call'))

        self.assert_error_response(rv, ['calls_limit.exceeded'], **self.base_error_kwargs)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('antifraud_score_allow'),
            self.env.statbox.entry(
                'call_with_code_error',
                error='calls_limit.exceeded',
            ),
        ])

        track = self.track_manager.read(self.track_id)
        ok_(track.phone_confirmation_calls_ip_limit_reached)

        ok_(not self.env.octopus.requests)
        self.assert_kolmogor_called(2, with_inc=False)

    def test_submit_by_call__ip_limit_reached_in_track__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_call = True
            track.phone_confirmation_calls_ip_limit_reached = True

        rv = self.make_request(self.query_params(confirm_method='by_call'))

        self.assert_error_response(rv, ['calls_limit.exceeded'], **self.base_error_kwargs)

        track = self.track_manager.read(self.track_id)
        ok_(track.phone_confirmation_calls_ip_limit_reached)

        ok_(not self.env.octopus.requests)
        self.assert_kolmogor_called(2, with_inc=False)

    def test_submit_by_call__call_count_limit__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_method = 'by_call'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_call = True
            for _ in range(10):
                track.phone_confirmation_calls_count.incr()

        rv = self.make_request(self.query_params(confirm_method='by_call'))

        self.assert_error_response(rv, ['calls_limit.exceeded'], **self.base_error_kwargs)

        track = self.track_manager.read(self.track_id)
        ok_(track.phone_confirmation_calls_count_limit_reached)

        ok_(not self.env.octopus.requests)
        self.assert_kolmogor_called(2, with_inc=False)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('antifraud_score_allow'),
            self.env.statbox.entry(
                'call_with_code_error',
                error='calls_limit.exceeded',
            ),
        ])

    def test_submit_by_call__phone_limit_reached__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_call = True

        counter = calls_per_phone.get_counter()
        for _ in range(counter.limit):
            counter.incr(TEST_PHONE_NUMBER.digital)

        rv = self.make_request(self.query_params(confirm_method='by_call'))

        self.assert_error_response(rv, ['calls_limit.exceeded'], **self.base_error_kwargs)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('antifraud_score_allow'),
            self.env.statbox.entry(
                'call_with_code_error',
                error='calls_limit.exceeded',
            ),
        ])

        track = self.track_manager.read(self.track_id)
        ok_(not track.phone_confirmation_calls_ip_limit_reached)
        ok_(track.phone_confirmation_calls_count_limit_reached)

        ok_(not self.env.octopus.requests)
        self.assert_kolmogor_called(2, with_inc=False)

    def test_submit_by_call__phone_limit_reached_is_set__error(self):
        # Отличие от предыдущего теста: флаг phone_confirmation_calls_count_limit_reached уже установлен в треке
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_method = 'by_call'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_call = True
            track.phone_confirmation_calls_count_limit_reached = True

        counter = calls_per_phone.get_counter()
        for _ in range(counter.limit):
            counter.incr(TEST_PHONE_NUMBER.digital)

        rv = self.make_request(self.query_params(confirm_method='by_call'))

        self.assert_error_response(rv, ['calls_limit.exceeded'], **self.base_error_kwargs)
        self.assert_statbox_no_send_entries(with_antifraud_score=True)

        track = self.track_manager.read(self.track_id)
        ok_(not track.phone_confirmation_calls_ip_limit_reached)
        ok_(track.phone_confirmation_calls_count_limit_reached)

        ok_(not self.env.octopus.requests)
        self.assert_kolmogor_called(2, with_inc=False)

    def test_submit_by_call__another_phone__phone_limit_reached__ok(self):
        self.env.octopus.set_response_value('create_session', octopus_response(TEST_CALL_SESSION_ID))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_method = 'by_call'
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER1.e164
            track.phone_valid_for_call = True
            track.phone_confirmation_calls_count_limit_reached = True

        counter = calls_per_phone.get_counter()
        for _ in range(counter.limit):
            counter.incr(TEST_PHONE_NUMBER1.digital)

        rv = self.make_request(self.query_params(
            confirm_method='by_call',
            number=TEST_PHONE_NUMBER.e164,
        ))

        self.assert_ok_response(
            rv,
            **dict(self.base_submitter_response, code_length=settings.SMS_VALIDATION_CODE_LENGTH)
        )
        self.assert_statbox_ok_with_call(
            action='call_with_code',
            with_antifraud_score=True,
        )

        track = self.track_manager.read(self.track_id)
        self.check_ok_track_by_call(track)
        self.check_ok_counters_by_call()
        self.assert_kolmogor_called(3)

    def test_submit_by_call__another_phone__ok(self):
        self.env.octopus.set_response_value('create_session', octopus_response(TEST_CALL_SESSION_ID))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER1.e164
            track.phone_valid_for_call = True
            track.phone_confirmation_confirms_count.incr()
            track.phone_confirmation_calls_count.incr()
            track.phone_confirmation_last_called_at = time.time()

        rv = self.make_request(self.query_params(
            confirm_method='by_call',
            number=TEST_PHONE_NUMBER.e164,
        ))

        self.assert_ok_response(
            rv,
            **dict(self.base_submitter_response, code_length=settings.SMS_VALIDATION_CODE_LENGTH)
        )
        self.assert_statbox_ok_with_call(
            action='call_with_code',
            with_antifraud_score=True,
        )

        track = self.track_manager.read(self.track_id)
        self.check_ok_track_by_call(track)
        self.check_ok_counters_by_call()
        self.assert_kolmogor_called(3)

    def test_submit_by_call__another_confirmation_method__ok(self):
        self.env.octopus.set_response_value('create_session', octopus_response(TEST_CALL_SESSION_ID))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_method = 'by_flash_call'
            track.phone_confirmation_is_confirmed = True
            track.phone_valid_for_call = True

        rv = self.make_request(self.query_params(
            confirm_method='by_call',
            number=TEST_PHONE_NUMBER.e164,
        ))

        self.assert_ok_response(
            rv,
            **dict(self.base_submitter_response, code_length=settings.SMS_VALIDATION_CODE_LENGTH)
        )
        self.assert_statbox_ok_with_call(
            action='call_with_code',
            with_antifraud_score=True,
        )

        track = self.track_manager.read(self.track_id)
        self.check_ok_track_by_call(track)
        self.check_ok_counters_by_call()
        self.assert_kolmogor_called(3)

    def test_submit_by_call__phone_confirmed__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_call = True
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_method = 'by_call'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request(self.query_params(confirm_method='by_call'))

        self.assert_error_response(rv, ['phone.confirmed'], **self.base_error_kwargs)
        self.assert_statbox_no_send_entries()

        ok_(not self.env.octopus.requests)
        self.assert_kolmogor_called(2, with_inc=False)

    def test_submit_by_call__shut_down__error(self):
        flag = {
            KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 1,
        }
        self.env.kolmogor.set_response_value('get', flag)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_call = True

        rv = self.make_request(self.query_params(confirm_method='by_call'))

        self.assert_error_response(rv, ['calls.shut_down'], **self.base_error_kwargs)
        self.assert_kolmogor_called(1, with_inc=False)

    def test_submit_by_call__inc_failed__ok(self):
        self.env.octopus.set_response_value('create_session', octopus_response(123))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_call = True

        self.env.kolmogor.set_response_side_effect('inc', KolmogorPermanentError)

        rv = self.make_request(dict(self.query_params(), confirm_method='by_call'))
        self.assert_ok_response(
            rv,
            **dict(self.base_submitter_response, code_length=settings.SMS_VALIDATION_CODE_LENGTH)
        )
        self.assert_statbox_ok_with_call(
            call_session_id='123',
            with_antifraud_score=True
        )

        track = self.track_manager.read(self.track_id)
        self.check_ok_track_by_call(track, call_session_id='123')
        self.check_ok_counters_by_call()
        self.assert_kolmogor_called(3)

    def test_submit_by_call__with_test_phone__ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_FAKE_PHONE_NUMBER.e164
            track.phone_valid_for_call = True

        rv = self.make_request(dict(self.query_params(number=TEST_FAKE_PHONE_NUMBER.e164), confirm_method='by_call'))
        self.assert_ok_response(
            rv,
            **dict(
                self.base_submitter_response,
                code_length=settings.SMS_VALIDATION_CODE_LENGTH,
                number=TEST_FAKE_PHONE_NUMBER_DUMPED,
            )
        )
        self.assert_statbox_ok_with_call(
            call_session_id=FAKE_OCTOPUS_SESSION_ID_FOR_TEST_PHONES,
            phone_number=TEST_FAKE_PHONE_NUMBER,
            with_antifraud_score=True,
        )
        eq_(len(self.env.octopus.requests), 0)

        track = self.track_manager.read(self.track_id)
        self.check_ok_track_by_call(track, call_session_id=FAKE_OCTOPUS_SESSION_ID_FOR_TEST_PHONES, phone_number=TEST_FAKE_PHONE_NUMBER)
        self.check_ok_counters_by_call(phone_number=TEST_FAKE_PHONE_NUMBER)
        self.assert_kolmogor_called(3)

    def test_submit_by_sms_with_used_gates_from_yasms(self):
        self.env.yasms.set_response_value('send_sms', yasms_send_sms_response(used_gate_ids=[1, 2, 3]))
        rv = self.make_request()
        self.assert_ok_response(
            rv,
            **self.base_send_code_response
        )

        eq_(self._code_generator_faker.call_count, 1)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'identity': 'confirm',
            'caller': 'dev',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track, used_gate_ids='1,2,3')
        ok_(track.country is None)

        self.assert_statbox_ok(with_antifraud_score=True)

    def test_sms_with_used_gates_in_track(self):
        self.env.yasms.set_response_value('send_sms', yasms_send_sms_response(used_gate_ids=[1, 2, 3]))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_used_gate_ids = '1,2'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request()
        self.assert_ok_response(rv, **self.base_send_code_response)

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track, used_gate_ids='1,2,3')

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'identity': 'confirm',
            'caller': 'dev',
            'previous_gates': '1,2',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

        self.assert_statbox_ok(with_antifraud_score=True)

    def test_sms_with_new_used_gates_after_number_changed(self):
        self.env.yasms.set_response_value('send_sms', yasms_send_sms_response(used_gate_ids=[4]))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_used_gate_ids = '1,2'

        rv = self.make_request(data=self.query_params(number=TEST_PHONE_NUMBER1.e164))
        self.assert_ok_response(
            rv,
            **merge_dicts(
                self.base_send_code_response,
                {'number': TEST_PHONE_NUMBER_DUMPED1},
            )
        )

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track, used_gate_ids='4', phone_number=TEST_PHONE_NUMBER1)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER1.e164,
            'text': self.sms_text,
            'identity': 'confirm',
            'caller': 'dev',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

        self.assert_statbox_ok(
            phone_number=TEST_PHONE_NUMBER1,
            with_antifraud_score=True,
        )

    def test_create_session_failed(self):
        self.env.octopus.set_response_side_effect('create_session', OctopusPermanentError())
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_call = True

        rv = self.make_request(dict(self.query_params(), confirm_method='by_call'))
        self.assert_error_response(rv, ['create_call.failed'], **self.base_error_kwargs)

        self.assert_kolmogor_called(3, keys='calls_failed')

        ok_(not len(self.env.yasms.requests))
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('antifraud_score_allow'),
            self.env.statbox.entry('call_with_code_error'),
        ])

    def test_submit_by_flash_call__ok(self):
        self.env.octopus.set_response_value('create_flash_call_session', octopus_response(123))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_flash_call = True

        rv = self.make_request(dict(self.query_params(), confirm_method='by_flash_call'))
        self.assert_ok_response(
            rv,
            **dict(
                self.base_submitter_response,
                code_length=4,
                calling_number_template=TEST_CALLING_NUMBER_TEMPLATE_HUMAN_READABLE,
            )
        )
        self.assert_statbox_ok_with_flash_call(
            call_session_id='123',
            with_antifraud_score=True,
        )
        self.env.octopus.requests[-1].assert_properties_equal(
            method='POST',
            url='http://localhost/v0/create-pinger-call',
            json_data={u'caller': u'+11111110000', 'callee': TEST_PHONE_NUMBER.e164},
        )
        ok_(self._random_faker.call_count)

        track = self.track_manager.read(self.track_id)
        self.check_ok_track_by_flash_call(track, call_session_id='123', code=TEST_CALLING_NUMBER_SUFFIX[-4:][-4:])
        self.check_ok_counters_by_call()
        self.assert_kolmogor_called(3)

    def test_submit_by_flash_call_again__ok(self):
        self.env.octopus.set_response_value('create_flash_call_session', octopus_response(123))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_method = 'by_flash_call'
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_flash_call = True
            track.phone_confirmation_code = '0000'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request(dict(self.query_params(), confirm_method='by_flash_call'))
        self.assert_ok_response(
            rv,
            **dict(
                self.base_submitter_response,
                code_length=4,
                calling_number_template=TEST_CALLING_NUMBER_TEMPLATE_HUMAN_READABLE,
            )
        )
        self.assert_statbox_ok_with_flash_call(call_session_id='123', with_antifraud_score=True)
        eq_(self._random_faker.call_count, 0)

        track = self.track_manager.read(self.track_id)
        self.check_ok_track_by_flash_call(track, call_session_id='123', code='0000')
        self.check_ok_counters_by_call()
        self.assert_kolmogor_called(3)

    def test_submit_by_flash_call_after_call__ok(self):
        self.env.octopus.set_response_value('create_flash_call_session', octopus_response(123))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_flash_call = True
            track.phone_valid_for_call = True
            track.phone_confirmation_code = '321132'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_method = 'by_call'

        rv = self.make_request(dict(self.query_params(), confirm_method='by_flash_call'))
        self.assert_ok_response(
            rv,
            **dict(
                self.base_submitter_response,
                code_length=4,
                calling_number_template=TEST_CALLING_NUMBER_TEMPLATE_HUMAN_READABLE,
            )
        )
        self.assert_statbox_ok_with_flash_call(call_session_id='123', with_antifraud_score=True)
        ok_(not self._code_generator_faker.call_count)
        ok_(self._random_faker.call_count)

        track = self.track_manager.read(self.track_id)
        self.check_ok_track_by_flash_call(track, call_session_id='123', code=TEST_CALLING_NUMBER_SUFFIX[-4:])
        self.check_ok_counters_by_call()
        self.assert_kolmogor_called(3)

    def test_submit_by_call_after_flash_call__ok(self):
        self.env.octopus.set_response_value('create_session', octopus_response(123))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_flash_call = True
            track.phone_valid_for_call = True
            track.phone_confirmation_code = '000'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_method = 'by_flash_call'

        rv = self.make_request(dict(self.query_params(), confirm_method='by_call'))
        self.assert_ok_response(
            rv,
            **dict(self.base_submitter_response, code_length=6)
        )
        self.assert_statbox_ok_with_call(
            call_session_id='123',
            with_antifraud_score=True,
        )
        ok_(self._code_generator_faker.call_count)
        ok_(not self._random_faker.call_count)

        track = self.track_manager.read(self.track_id)
        self.check_ok_track_by_call(track, call_session_id='123')
        self.check_ok_counters_by_call()
        self.assert_kolmogor_called(3)

    def test_submit_by_flash_call__track_no_validated_phone__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_valid_for_flash_call = True

        rv = self.make_request(self.query_params(confirm_method='by_flash_call'))
        self.assert_error_response(rv, ['track.invalid_state'], **self.base_error_kwargs)

        ok_(not self.env.octopus.requests)
        ok_(not self.env.kolmogor.requests)
        self.assert_statbox_no_send_entries()

    def test_submit_by_flash_call__ip_limit_reached__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_flash_call = True

        counter = calls_per_ip.get_counter(TEST_USER_IP)
        for _ in range(counter.limit):
            counter.incr(TEST_USER_IP)

        rv = self.make_request(self.query_params(confirm_method='by_flash_call'))

        self.assert_error_response(rv, ['calls_limit.exceeded'], **self.base_error_kwargs)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('antifraud_score_allow'),
            self.env.statbox.entry(
                'flash_call_error',
                error='calls_limit.exceeded',
            ),
        ])

        track = self.track_manager.read(self.track_id)
        ok_(track.phone_confirmation_calls_ip_limit_reached)

        ok_(not self.env.octopus.requests)
        self.assert_kolmogor_called(2, with_inc=False)

    def test_submit_by_flash_call__ip_limit_reached_in_track__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_flash_call = True
            track.phone_confirmation_calls_ip_limit_reached = True

        rv = self.make_request(self.query_params(confirm_method='by_flash_call'))

        self.assert_error_response(rv, ['calls_limit.exceeded'], **self.base_error_kwargs)

        track = self.track_manager.read(self.track_id)
        ok_(track.phone_confirmation_calls_ip_limit_reached)

        ok_(not self.env.octopus.requests)
        self.assert_kolmogor_called(2, with_inc=False)

    def test_submit_by_flash_call__call_count_limit__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_method = 'by_flash_call'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_flash_call = True
            for _ in range(10):
                track.phone_confirmation_calls_count.incr()

        rv = self.make_request(self.query_params(confirm_method='by_flash_call'))

        self.assert_error_response(rv, ['calls_limit.exceeded'], **self.base_error_kwargs)

        track = self.track_manager.read(self.track_id)
        ok_(track.phone_confirmation_calls_count_limit_reached)

        ok_(not self.env.octopus.requests)
        self.assert_kolmogor_called(2, with_inc=False)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('antifraud_score_allow'),
            self.env.statbox.entry(
                'flash_call_error',
                error='calls_limit.exceeded',
            ),
        ])

    def test_submit_by_flash_call__phone_limit_reached__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_flash_call = True

        counter = calls_per_phone.get_counter()
        for _ in range(counter.limit):
            counter.incr(TEST_PHONE_NUMBER.digital)

        rv = self.make_request(self.query_params(confirm_method='by_flash_call'))

        self.assert_error_response(rv, ['calls_limit.exceeded'], **self.base_error_kwargs)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('antifraud_score_allow'),
            self.env.statbox.entry(
                'flash_call_error',
                error='calls_limit.exceeded',
            ),
        ])

        track = self.track_manager.read(self.track_id)
        ok_(not track.phone_confirmation_calls_ip_limit_reached)
        ok_(track.phone_confirmation_calls_count_limit_reached)

        ok_(not self.env.octopus.requests)
        self.assert_kolmogor_called(2, with_inc=False)

    def test_submit_by_flash_call__phone_limit_reached_is_set__error(self):
        # Отличие от предыдущего теста: флаг phone_confirmation_calls_count_limit_reached уже установлен в треке
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_method = 'by_flash_call'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_flash_call = True
            track.phone_confirmation_calls_count_limit_reached = True

        counter = calls_per_phone.get_counter()
        for _ in range(counter.limit):
            counter.incr(TEST_PHONE_NUMBER.digital)

        rv = self.make_request(self.query_params(confirm_method='by_flash_call'))

        self.assert_error_response(rv, ['calls_limit.exceeded'], **self.base_error_kwargs)
        self.assert_statbox_no_send_entries(with_antifraud_score=True)

        track = self.track_manager.read(self.track_id)
        ok_(not track.phone_confirmation_calls_ip_limit_reached)
        ok_(track.phone_confirmation_calls_count_limit_reached)

        ok_(not self.env.octopus.requests)
        self.assert_kolmogor_called(2, with_inc=False)

    def test_submit_by_flash_call__another_phone__phone_limit_reached__ok(self):
        self.env.octopus.set_response_value('create_flash_call_session', octopus_response(TEST_CALL_SESSION_ID))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER1.e164
            track.phone_valid_for_flash_call = True
            track.phone_confirmation_calls_count_limit_reached = True

        counter = calls_per_phone.get_counter()
        for _ in range(counter.limit):
            counter.incr(TEST_PHONE_NUMBER1.digital)

        rv = self.make_request(self.query_params(
            confirm_method='by_flash_call',
            number=TEST_PHONE_NUMBER.e164,
        ))

        self.assert_ok_response(
            rv,
            **dict(
                self.base_submitter_response,
                code_length=4,
                calling_number_template=TEST_CALLING_NUMBER_TEMPLATE_HUMAN_READABLE,
            )
        )
        self.assert_statbox_ok_with_flash_call(
            action='flash_call',
            with_antifraud_score=True,
        )

        track = self.track_manager.read(self.track_id)
        self.check_ok_track_by_flash_call(track, code=TEST_CALLING_NUMBER_SUFFIX[-4:])
        self.check_ok_counters_by_call()
        self.assert_kolmogor_called(3)

    def test_submit_by_flash_call__another_phone__ok(self):
        self.env.octopus.set_response_value('create_flash_call_session', octopus_response(TEST_CALL_SESSION_ID))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER1.e164
            track.phone_valid_for_flash_call = True
            track.phone_confirmation_confirms_count.incr()
            track.phone_confirmation_calls_count.incr()
            track.phone_confirmation_last_called_at = time.time()

        rv = self.make_request(self.query_params(
            confirm_method='by_flash_call',
            number=TEST_PHONE_NUMBER.e164,
        ))

        self.assert_ok_response(
            rv,
            **dict(
                self.base_submitter_response,
                code_length=4,
                calling_number_template=TEST_CALLING_NUMBER_TEMPLATE_HUMAN_READABLE,
            )
        )
        self.assert_statbox_ok_with_flash_call(
            action='flash_call',
            with_antifraud_score=True,
        )

        track = self.track_manager.read(self.track_id)
        self.check_ok_track_by_flash_call(track, code=TEST_CALLING_NUMBER_SUFFIX[-4:])
        self.check_ok_counters_by_call()
        self.assert_kolmogor_called(3)

    def test_submit_by_flash_call__another_confirmation_method__ok(self):
        self.env.octopus.set_response_value('create_flash_call_session', octopus_response(TEST_CALL_SESSION_ID))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_method = 'by_call'
            track.phone_confirmation_is_confirmed = True
            track.phone_valid_for_flash_call = True

        rv = self.make_request(self.query_params(
            confirm_method='by_flash_call',
            number=TEST_PHONE_NUMBER.e164,
        ))

        self.assert_ok_response(
            rv,
            **dict(
                self.base_submitter_response,
                code_length=4,
                calling_number_template=TEST_CALLING_NUMBER_TEMPLATE_HUMAN_READABLE,
            )
        )
        self.assert_statbox_ok_with_flash_call(
            action='flash_call',
            with_antifraud_score=True,
        )

        track = self.track_manager.read(self.track_id)
        self.check_ok_track_by_flash_call(track, code=TEST_CALLING_NUMBER_SUFFIX[-4:])
        self.check_ok_counters_by_call()
        self.assert_kolmogor_called(3)

    def test_submit_by_flash_call__phone_confirmed__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_flash_call = True
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_method = 'by_flash_call'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request(self.query_params(confirm_method='by_flash_call'))

        self.assert_error_response(rv, ['phone.confirmed'], **self.base_error_kwargs)
        self.assert_statbox_no_send_entries()

        ok_(not self.env.octopus.requests)
        self.assert_kolmogor_called(2, with_inc=False)

    def test_submit_by_flash_call__shut_down__error(self):
        flag = {
            KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 1,
        }
        self.env.kolmogor.set_response_value('get', flag)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_flash_call = True

        rv = self.make_request(self.query_params(confirm_method='by_flash_call'))

        self.assert_error_response(rv, ['calls.shut_down'], **self.base_error_kwargs)
        self.assert_kolmogor_called(1, with_inc=False)

    def test_submit_by_flash_call__inc_failed__ok(self):
        self.env.octopus.set_response_value('create_flash_call_session', octopus_response(123))
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_flash_call = True

        self.env.kolmogor.set_response_side_effect('inc', KolmogorPermanentError)

        rv = self.make_request(dict(self.query_params(), confirm_method='by_flash_call'))
        self.assert_ok_response(
            rv,
            **dict(
                self.base_submitter_response,
                code_length=4,
                calling_number_template=TEST_CALLING_NUMBER_TEMPLATE_HUMAN_READABLE,
            )
        )
        self.assert_statbox_ok_with_flash_call(
            call_session_id='123',
            with_antifraud_score=True,
        )

        track = self.track_manager.read(self.track_id)
        self.check_ok_track_by_flash_call(track, call_session_id='123', code=TEST_CALLING_NUMBER_SUFFIX[-4:])
        self.check_ok_counters_by_call()
        self.assert_kolmogor_called(3)

    def test_create_flash_call_session_failed(self):
        self.env.octopus.set_response_side_effect('create_flash_call_session', OctopusPermanentError())
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_flash_call = True

        rv = self.make_request(dict(self.query_params(), confirm_method='by_flash_call'))
        self.assert_error_response(rv, ['create_call.failed'], **self.base_error_kwargs)

        self.assert_kolmogor_called(3, keys='calls_failed')

        ok_(not len(self.env.yasms.requests))
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('antifraud_score_allow'),
            self.env.statbox.entry('flash_call_error'),
        ])

    def test_submit_by_flash_call__with_test_phone__ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_validated_for_call = TEST_FAKE_PHONE_NUMBER.e164
            track.phone_valid_for_flash_call = True

        rv = self.make_request(dict(self.query_params(number=TEST_FAKE_PHONE_NUMBER.e164), confirm_method='by_flash_call'))
        self.assert_ok_response(
            rv,
            **dict(
                self.base_submitter_response,
                code_length=4,
                calling_number_template=TEST_CALLING_NUMBER_TEMPLATE_HUMAN_READABLE,
                number=TEST_FAKE_PHONE_NUMBER_DUMPED,
            )
        )
        self.assert_statbox_ok_with_flash_call(
            call_session_id=FAKE_OCTOPUS_SESSION_ID_FOR_TEST_PHONES,
            phone_number=TEST_FAKE_PHONE_NUMBER,
            with_antifraud_score=True,
        )
        eq_(len(self.env.octopus.requests), 0)
        ok_(self._random_faker.call_count)

        track = self.track_manager.read(self.track_id)
        self.check_ok_track_by_flash_call(track, call_session_id=FAKE_OCTOPUS_SESSION_ID_FOR_TEST_PHONES, code=TEST_CALLING_NUMBER_SUFFIX[-4:], phone_number=TEST_FAKE_PHONE_NUMBER)
        self.check_ok_counters_by_call(phone_number=TEST_FAKE_PHONE_NUMBER)
        self.assert_kolmogor_called(3)

    def test_ip_blacklist_disable(self):
        with mock.patch(
            'passport.backend.api.common.ip.is_ip_blacklisted',
            return_value=True,
        ):
            with settings_context(**dict(
                COMMON_SETTINGS,
                PHONE_CONFIRM_CHECK_IP_BLACKLIST=False,
            )):
                rv = self.make_request(self.query_params())

        self.assert_ok_response(rv, check_all=False)

    def test_yasms_error(self):
        self.env.yasms.set_response_side_effect('send_sms', YaSmsTemporaryBlock('error'))
        rv = self.make_request(self.query_params())

        self.assert_error_response(rv, ['phone.blocked'], check_content=False)
        self.assert_antifraud_score_called()
        self.env.yasms_private_logger.assert_equals([
            self.env.yasms_private_logger.entry(
                'yasms_enqueued',
                identity='yasms.phone_blocked',
            ),
            self.env.yasms_private_logger.entry(
                'yasms_not_sent',
                identity='yasms.phone_blocked',
            ),
        ])

    def test_antifraud_score_deny_sms(self):
        self.setup_antifraud_score_response(False)
        rv = self.make_request(self.query_params())

        self.assert_error_response(rv, ['sms_limit.exceeded'], check_content=False)
        eq_(json.loads(rv.data).get('global_sms_id'), self.env.yasms_fake_global_sms_id_mock.return_value)
        self.assert_antifraud_score_called()
        self.env.yasms_private_logger.assert_equals([
            self.env.yasms_private_logger.entry(
                'yasms_enqueued',
                identity='antifraud',
            ),
            self.env.yasms_private_logger.entry(
                'yasms_not_sent',
                identity='antifraud',
            ),
        ])
        self.assert_statbox_antifraud_deny_ok()

    def test_antifraud_score_deny_sms_masked(self):
        self.setup_antifraud_score_response(False)
        with settings_context(
            PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
            PHONE_CONFIRM_MASK_ANTIFRAUD_DENIAL=True,
        ):
            rv = self.make_request(self.query_params())

        self.assert_ok_response(rv, check_all=False)
        eq_(json.loads(rv.data).get('global_sms_id'), self.env.yasms_fake_global_sms_id_mock.return_value)
        self.assert_antifraud_score_called()
        self.env.yasms_private_logger.assert_equals([
            self.env.yasms_private_logger.entry(
                'yasms_enqueued',
                identity='antifraud',
            ),
            self.env.yasms_private_logger.entry(
                'yasms_not_sent',
                identity='antifraud',
            ),
        ])
        self.assert_statbox_antifraud_deny_ok(mask_denial=True)

    def test_antifraud_score_additional_fields(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.device_application = 'ru.yandex.test'
            track.retpath = TEST_RETPATH
            track.scenario = 'scn1'
            track.js_fingerprint = 'js-fingerprint'
            track.check_js_load = True
            track.check_css_load = False
            track.page_loading_info = 'hello darkness my old friend'
        self.setup_antifraud_score_response(False)
        rv = self.make_request(self.query_params())

        self.assert_error_response(rv, ['sms_limit.exceeded'], check_content=False)
        self.env.yasms_private_logger.assert_equals([
            self.env.yasms_private_logger.entry(
                'yasms_enqueued',
                identity='antifraud',
            ),
            self.env.yasms_private_logger.entry(
                'yasms_not_sent',
                identity='antifraud',
            ),
        ])
        self.assert_antifraud_score_called(
            app_id='ru.yandex.test',
            retpath=TEST_RETPATH,
            scenario='scn1',
            js_fingerprint='js-fingerprint',
        )
        self.assert_statbox_antifraud_deny_ok(scenario='scn1')

    def test_antifraud_score_captcha(self):
        self.setup_antifraud_score_response(allow=True, tags=['sms'])
        rv = self.make_request(self.query_params())

        self.assert_error_response(rv, ['captcha.required'], check_content=False)
        self.assert_antifraud_score_called()
        self.assert_statbox_antifraud_captcha_ok(antifraud_tags='sms')

        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)

    def test_antifraud_score_captcha__already_passed(self):
        with self.track_transaction() as track:
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        self.setup_antifraud_score_response(allow=True, tags=['sms'])
        rv = self.make_request(self.query_params())

        self.assert_ok_response(rv, check_all=False)
        self.assert_antifraud_score_called()

    def test_antifraud_score_captcha__consumer_not_allowed(self):
        self.setup_antifraud_score_response(allow=True, tags=['sms'])
        with settings_context(**dict(
            COMMON_SETTINGS,
            PHONE_CONFIRM_SHOW_ANTIFRAUD_CAPTCHA_FOR_CONSUMERS=[],
        )):
            rv = self.make_request(self.query_params())

        self.assert_ok_response(rv, check_all=False)
        self.assert_antifraud_score_called()

    def test_antifraud_score_disable(self):
        self.setup_antifraud_score_response(False)
        with settings_context(**dict(
            COMMON_SETTINGS,
            PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=False,
        )):
            rv = self.make_request(self.query_params())

        self.assert_antifraud_score_not_called()
        self.assert_ok_response(rv, check_all=False)

    def test_antifraud_score_request_error(self):
        self.env.antifraud_api.set_response_side_effect('score', BaseAntifraudApiError())
        rv = self.make_request(self.query_params())

        self.assert_ok_response(rv, check_all=False)

    def test_antifraud_score_deny_call(self):
        with self.track_transaction() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_call = True
        self.setup_antifraud_score_response(False)

        rv = self.make_request(dict(self.query_params(), confirm_method='by_call'))

        self.assert_error_response(rv, ['calls_limit.exceeded'], check_content=False)
        self.assert_antifraud_score_called(confirm_method='by_call', language='ru')
        self.env.yasms_private_logger.assert_equals(list())
        self.assert_statbox_antifraud_deny_ok()

    def test_antifraud_score_deny_call_masked(self):
        with self.track_transaction() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_call = True
        self.setup_antifraud_score_response(False)

        with settings_context(
            PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
            PHONE_CONFIRM_MASK_ANTIFRAUD_DENIAL=True,
        ):
            rv = self.make_request(dict(self.query_params(), confirm_method='by_call'))

        self.assert_ok_response(rv, check_all=False)
        self.assert_antifraud_score_called(confirm_method='by_call', phone_confirmation_language='ru')
        self.env.yasms_private_logger.assert_equals(list())
        self.assert_statbox_antifraud_deny_ok(mask_denial=True)

    def test_antifraud_score_deny_flash_call(self):
        with self.track_transaction() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_flash_call = True
        self.setup_antifraud_score_response(False)

        rv = self.make_request(dict(self.query_params(), confirm_method='by_flash_call'))

        self.assert_error_response(rv, ['calls_limit.exceeded'], check_content=False)
        self.assert_antifraud_score_called(confirm_method='by_flash_call', phone_confirmation_language='en')
        self.env.yasms_private_logger.assert_equals(list())
        self.assert_statbox_antifraud_deny_ok()

    def test_antifraud_score_deny_flash_call_masked(self):
        with self.track_transaction() as track:
            track.phone_validated_for_call = TEST_PHONE_NUMBER.e164
            track.phone_valid_for_flash_call = True
        self.setup_antifraud_score_response(False)

        with settings_context(
            PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
            PHONE_CONFIRM_MASK_ANTIFRAUD_DENIAL=True,
        ):
            rv = self.make_request(dict(self.query_params(), confirm_method='by_flash_call'))

        self.assert_ok_response(rv, check_all=False)
        self.assert_antifraud_score_called(confirm_method='by_flash_call', phone_confirmation_language='en')
        self.env.yasms_private_logger.assert_equals(list())
        self.assert_statbox_antifraud_deny_ok(mask_denial=True)

    def test_antifraud_score_track_type_is_default_scenario(self):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('restore')

        rv = self.make_request(self.query_params())

        self.assert_ok_response(rv, check_all=False)
        self.assert_antifraud_score_called(scenario='restore')

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'antifraud_score_allow',
                scenario='restore',
                track_id=self.track_id,
            ),
            self.env.statbox.entry('send_code', track_id=self.track_id),
            self.env.statbox.entry('success', track_id=self.track_id),
        ])

    def test_captcha_required_but_not_passed(self):
        with self.track_transaction() as track:
            track.is_captcha_required = True

        rv = self.make_request(self.query_params())

        self.assert_error_response(rv, ['captcha.required'], check_content=False)


@istest
@with_settings_hosts(**COMMON_SETTINGS)
class TestConfirmSubmitter(CommonConfirmSubmitter):
    """Тесты ручки /phone/confirm/submit/"""
    pass


@istest
@with_settings_hosts(
    ANDROID_PACKAGE_PREFIXES_WHITELIST={'com.yandex'},
    ANDROID_PACKAGE_PUBLIC_KEY_DEFAULT='public-key',
    ANDROID_PACKAGE_PREFIX_TO_KEY={},
    **COMMON_SETTINGS
)
class TestConfirmSubmitterForSmsRetriever(CommonConfirmSubmitter):
    """Тесты ручки /phone/confirm/submit/ с форматированием SMS под SmsRetriever в Андроиде"""
    def setUp(self):
        super(TestConfirmSubmitterForSmsRetriever, self).setUp()

        self.package_name = 'com.yandex.passport.testapp1'

        self.setup_statbox_templates(
            sms_retriever_kwargs=dict(
                gps_package_name=self.package_name,
                sms_retriever='1',
            ),
        )

        eq_(hash_android_package(self.package_name, 'public-key'), 'gNNu9q4gcSd')

        self.normal_sms_text = self.sms_text

    @property
    def sms_text(self):
        return format_for_android_sms_retriever(
            TEST_SMS_RETRIEVER_TEXT,
            'gNNu9q4gcSd',
        )

    def query_params(self, **kwargs):
        base_params = {
            'display_language': 'ru',
            'track_id': self.track_id,
            'gps_package_name': self.package_name,
        }

        if not ('phone_id' in kwargs or 'number' in kwargs):
            base_params['number'] = TEST_PHONE_NUMBER.e164

        return merge_dicts(base_params, kwargs)


@istest
@with_settings_hosts(
    ANDROID_PACKAGE_PREFIXES_WHITELIST={'com.yandex'},
    ANDROID_PACKAGE_PUBLIC_KEY_DEFAULT='public-key',
    ANDROID_PACKAGE_PREFIX_TO_KEY={},
    **COMMON_SETTINGS
)
class TestConfirmSubmitterForSmsRetrieverUnknownPackage(BaseConfirmSubmitterTestCase):
    """
    Тесты ручки /phone/confirm/submit/ с форматированием SMS под SmsRetriever в Андроиде.
    В запросе передаётся пакет, который не совпадает с белым списком у нас в настройках.
    Должна улетать SMS с обычным текстом.
    """

    track_state = CONFIRM_STATE
    has_uid = False
    url = '/1/bundle/phone/confirm/submit/?consumer=dev'

    def setUp(self):
        super(TestConfirmSubmitterForSmsRetrieverUnknownPackage, self).setUp()

        self.setup_statbox_templates(
            sms_retriever_kwargs=dict(
                gps_package_name='unknown.package',
                sms_retriever='0',
            ),
        )

        eq_(hash_android_package('com.yandex.passport.testapp1', 'public-key'), 'gNNu9q4gcSd')

    def query_params(self, **kwargs):
        base_params = {
            'display_language': 'ru',
            'track_id': self.track_id,
            'gps_package_name': 'unknown.package',
        }
        if not ('phone_id' in kwargs or 'number' in kwargs):
            base_params['number'] = TEST_PHONE_NUMBER.e164

        return merge_dicts(base_params, kwargs)

    def test_unknown_gps_package(self):
        rv = self.make_request()

        self.assert_ok_response(
            rv,
            **self.base_send_code_response
        )

        eq_(self._code_generator_faker.call_count, 1)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'identity': 'confirm',
            'caller': 'dev',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)
        ok_(track.country is None)

        self.assert_statbox_ok(with_antifraud_score=True)

    def test_unicode_gps_package_name(self):
        rv = self.make_request(
            data=self.query_params(
                gps_package_name=u'com.yandex.привет',
            ),
        )

        self.assert_error_response(rv, ['gps_package_name.invalid'])


@with_settings_hosts(
    CONSUMER_TO_SMS_ROUTE={'foo': 'nlo'},
    **mock_counters()
)
class TestConfirmSubmitterConsumerWithRoute(BaseConfirmSubmitterTestCase):
    def assign_all_grants(self, consumer):
        self.env.grants.set_grants_return_value(
            {
                consumer: dict(
                    grants={'phone_bundle': ['*']},
                    networks=['127.0.0.1'],
                ),
            },
        )

    def make_request(self, consumer):
        return self.env.client.post(
            '/1/bundle/phone/confirm/submit/',
            query_string={'consumer': consumer},
            data={
                'number': TEST_PHONE_NUMBER.e164,
                'display_language': 'ru',
            },
            headers={'Ya-Consumer-Client-Ip': '1.2.3.4', 'Ya-Client-User-Agent': TEST_USER_AGENT},
        )

    def assert_yasms_called_with_route(self, route):
        requests = self.env.yasms.requests
        requests[0].assert_query_contains(dict(route=route))

    def test_consumer_with_route(self):
        self.assign_all_grants('foo')
        rv = self.make_request(consumer='foo')

        self.assert_ok_response(rv, check_all=False)
        self.assert_yasms_called_with_route('nlo')

    def test_consumer_without_route(self):
        self.assign_all_grants('bar')
        rv = self.make_request(consumer='bar')

        self.assert_ok_response(rv, check_all=False)
        self.assert_yasms_called_with_route('validate')


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    SMS_VALIDATION_MAX_CHECKS_COUNT=3,
    PHONE_VALIDATION_MAX_CALLS_CHECKS_COUNT=2,
    FAKE_CODE=TEST_FAKE_CODE,
    TEST_PHONE_NUMBERS_ACCEPTING_FAKE_CODE=(
        TEST_FAKE_PHONE_NUMBER.e164,
    ),
)
class TestConfirmCommitter(
        BaseConfirmCommitterTestCase,
        ConfirmCommitterTestMixin,
        ConfirmCommitterSentCodeTestMixin,
        ConfirmCommitterLocalPhonenumberTestMixin):

    track_state = CONFIRM_STATE
    has_uid = False
    url = '/1/bundle/phone/confirm/commit/?consumer=dev'

    def query_params(self, **kwargs):
        base_params = {
            'code': self.confirmation_code,
            'track_id': self.track_id,
        }

        return merge_dicts(base_params, kwargs)

    def assert_statbox_ok(self, confirm_method='by_sms', time_passed=0, phone_number=TEST_PHONE_NUMBER):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'enter_code',
                time_passed=TimeSpan(time_passed),
                number=phone_number.masked_format_for_statbox,
            ),
            self.env.statbox.entry(
                'success',
                confirm_method=confirm_method,
                number=phone_number.masked_format_for_statbox,
            ),
        ])

    def assert_antifraud_log_ok(
        self,
        phone_confirmation_method='by_sms',
        user_phone=TEST_PHONE_NUMBER.e164,
    ):
        self.env.antifraud_logger.assert_has_written(
            [
                self.env.antifraud_logger.entry(
                    'base',
                    channel='pharma',
                    sub_channel='dev',
                    status='OK',
                    external_id='track-{}'.format(self.track_id),
                    scenario='register',
                    phone_confirmation_method=phone_confirmation_method,
                    request_path='/1/bundle/phone/confirm/commit/',
                    request='auth',
                    user_phone=user_phone,
                ),
            ],
        )

    def assert_ok(self, rv, **expected_response):
        self.assert_ok_response(
            rv,
            **(expected_response or self.base_response)
        )

        track = self.track_manager.read(self.track_id)

        ok_(track.phone_confirmation_is_confirmed)
        eq_(track.phone_confirmation_confirms_count.get(), 1)
        ok_(not track.phone_confirmation_confirms_count_limit_reached)
        eq_(track.phone_confirmation_first_checked, TimeNow())
        eq_(track.phone_confirmation_last_checked, TimeNow())

        self.assert_statbox_ok()
        self.assert_antifraud_log_ok()

    def test_ok(self):
        self.setup_track_for_commit()

        rv = self.make_request()
        self.assert_ok(rv)

    def test_formatted_code_in_request_ok(self):
        # Передан форматированный код в запросе. В треке не форматированный код.
        self.setup_track_for_commit()

        rv = self.make_request(self.query_params(code=format_code_by_3(self.confirmation_code)))
        self.assert_ok(rv)

    def test_formatted_code_in_track_ok(self):
        # Передан не форматированный код в запросе. В треке форматированный код.
        self.setup_track_for_commit(phone_confirmation_code=format_code_by_3(self.confirmation_code))

        rv = self.make_request()
        self.assert_ok(rv)

    def test_registration_process_name_ok(self):
        self.setup_track_for_commit()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = PROCESS_WEB_REGISTRATION

        rv = self.make_request()
        self.assert_ok(rv)

    def test_return_masked_number_ok(self):
        self.setup_track_for_commit()
        with self.track_transaction() as track:
            track.return_masked_number = True

        rv = self.make_request()
        self.assert_ok(
            rv,
            **{'status': 'ok',
               'number': TEST_PHONE_NUMBER_DUMPED_MASKED}
        )

    def test_fake_code_ok(self):
        self.setup_track_for_commit(
            phone_confirmation_phone_number=TEST_FAKE_PHONE_NUMBER.e164,
            phone_confirmation_phone_number_original=TEST_FAKE_PHONE_NUMBER.original,
        )

        rv = self.make_request(self.query_params(code='000-000'))
        self.assert_ok_response(
            rv,
            **dict(
                self.base_response,
                number=TEST_FAKE_PHONE_NUMBER_DUMPED,
            )
        )
        self.assert_statbox_ok(
            phone_number=TEST_FAKE_PHONE_NUMBER,
        )

    def test_fake_code_not_accepted_for_normal_number(self):
        self.setup_track_for_commit()

        rv = self.make_request(self.query_params(code='000-000'))
        self.assert_error_response(rv, ['code.invalid'], **self.number_response)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('code_invalid'),
        ])

    def test_unsupported_process_name(self):
        self.setup_track_for_commit()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = 'some-process-name'

        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['track.invalid_state'],
        )
        self.env.statbox.assert_has_written([])
        self.env.antifraud_logger.assert_has_written([])

    def test_empty_phone_confirmation_method(self):
        self.setup_track_for_commit(exclude=['phone_confirmation_method'])

        rv = self.make_request()
        self.assert_error_response(
            rv,
            ['track.invalid_state'],
            **self.number_response
        )
        self.env.statbox.assert_has_written([])
        self.env.antifraud_logger.assert_has_written([])

    def test_already_confirmed(self):
        self.setup_track_for_commit(phone_confirmation_is_confirmed=True)

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            **self.base_response
        )

        self.assert_statbox_ok()
        self.assert_antifraud_log_ok()

    def test_by_call_ok(self):
        self.setup_track_for_commit(
            exclude=[
                'phone_confirmation_sms_count',
                'phone_confirmation_first_send_at',
                'phone_confirmation_last_send_at',
            ],
            phone_confirmation_calls_count='1',
            phone_call_session_id=TEST_CALL_SESSION_ID,
            phone_confirmation_first_called_at=time.time(),
            phone_confirmation_last_called_at=time.time(),
            phone_confirmation_method='by_call',
        )

        rv = self.make_request()
        self.assert_ok_response(rv, **self.base_response)
        self.assert_statbox_ok(confirm_method='by_call')
        self.assert_antifraud_log_ok(phone_confirmation_method='by_call')

    def test_by_call_with_test_phone_ok(self):
        self.setup_track_for_commit(
            exclude=[
                'phone_confirmation_sms_count',
                'phone_confirmation_first_send_at',
                'phone_confirmation_last_send_at',
            ],
            phone_confirmation_calls_count='1',
            phone_call_session_id=FAKE_OCTOPUS_SESSION_ID_FOR_TEST_PHONES,
            phone_confirmation_first_called_at=time.time(),
            phone_confirmation_last_called_at=time.time(),
            phone_confirmation_method='by_call',
            phone_confirmation_phone_number=TEST_FAKE_PHONE_NUMBER.e164,
            phone_confirmation_phone_number_original=TEST_FAKE_PHONE_NUMBER.original,
        )

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            **dict(
                self.base_response,
                number=TEST_FAKE_PHONE_NUMBER_DUMPED,
            )
        )
        self.assert_statbox_ok(
            confirm_method='by_call',
            phone_number=TEST_FAKE_PHONE_NUMBER,
        )
        self.assert_antifraud_log_ok(
            phone_confirmation_method='by_call',
            user_phone=TEST_FAKE_PHONE_NUMBER.e164,
        )

    def test_by_call_not_made(self):
        self.setup_track_for_commit(
            exclude=[
                'phone_confirmation_sms_count',
                'phone_confirmation_first_send_at',
                'phone_confirmation_last_send_at',
            ],
            phone_call_session_id=TEST_CALL_SESSION_ID,
            phone_confirmation_first_called_at=time.time(),
            phone_confirmation_last_called_at=time.time(),
            phone_confirmation_method='by_call',
        )

        rv = self.make_request()
        self.assert_error_response(rv, ['call.not_made'], **self.number_response)
        self.env.statbox.assert_has_written([])
        self.env.antifraud_logger.assert_has_written([])

    def test_by_call_invalid_track(self):
        self.setup_track_for_commit(
            exclude=[
                'phone_confirmation_sms_count',
                'phone_confirmation_first_send_at',
                'phone_confirmation_last_send_at',
            ],
            phone_confirmation_calls_count='1',
            phone_confirmation_first_called_at=time.time(),
            phone_confirmation_last_called_at=time.time(),
            phone_confirmation_method='by_call',
        )

        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'], **self.number_response)
        self.env.statbox.assert_has_written([])
        self.env.antifraud_logger.assert_has_written([])

    def test_by_call_code_invalid(self):
        self.setup_track_for_commit(
            exclude=[
                'phone_confirmation_sms_count',
                'phone_confirmation_first_send_at',
                'phone_confirmation_last_send_at',
            ],
            phone_confirmation_calls_count='1',
            phone_call_session_id=TEST_CALL_SESSION_ID,
            phone_confirmation_first_called_at=time.time(),
            phone_confirmation_last_called_at=time.time(),
            phone_confirmation_code='notcode',
            phone_confirmation_method='by_call',
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['code.invalid'], **self.number_response)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('code_invalid'),
        ])
        self.env.antifraud_logger.assert_has_written([])

    def test_by_flash_call_ok(self):
        self.setup_track_for_commit(
            exclude=[
                'phone_confirmation_sms_count',
                'phone_confirmation_first_send_at',
                'phone_confirmation_last_send_at',
            ],
            phone_confirmation_calls_count='1',
            phone_call_session_id=TEST_CALL_SESSION_ID,
            phone_confirmation_first_called_at=time.time(),
            phone_confirmation_last_called_at=time.time(),
            phone_confirmation_method='by_flash_call',
        )

        rv = self.make_request()
        self.assert_ok_response(rv, **self.base_response)
        self.assert_statbox_ok(confirm_method='by_flash_call')
        self.assert_antifraud_log_ok(phone_confirmation_method='by_flash_call')

    def test_by_flash_call_with_test_phone_ok(self):
        self.setup_track_for_commit(
            exclude=[
                'phone_confirmation_sms_count',
                'phone_confirmation_first_send_at',
                'phone_confirmation_last_send_at',
            ],
            phone_confirmation_calls_count='1',
            phone_call_session_id=FAKE_OCTOPUS_SESSION_ID_FOR_TEST_PHONES,
            phone_confirmation_first_called_at=time.time(),
            phone_confirmation_last_called_at=time.time(),
            phone_confirmation_method='by_flash_call',
            phone_confirmation_phone_number=TEST_FAKE_PHONE_NUMBER.e164,
            phone_confirmation_phone_number_original=TEST_FAKE_PHONE_NUMBER.original,
        )

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            **dict(
                self.base_response,
                number=TEST_FAKE_PHONE_NUMBER_DUMPED,
            )
        )
        self.assert_statbox_ok(
            confirm_method='by_flash_call',
            phone_number=TEST_FAKE_PHONE_NUMBER,
        )
        self.assert_antifraud_log_ok(
            phone_confirmation_method='by_flash_call',
            user_phone=TEST_FAKE_PHONE_NUMBER.e164,
        )

    def test_by_flash_call_not_made(self):
        self.setup_track_for_commit(
            exclude=[
                'phone_confirmation_sms_count',
                'phone_confirmation_first_send_at',
                'phone_confirmation_last_send_at',
            ],
            phone_call_session_id=TEST_CALL_SESSION_ID,
            phone_confirmation_first_called_at=time.time(),
            phone_confirmation_last_called_at=time.time(),
            phone_confirmation_method='by_flash_call',
        )

        rv = self.make_request()
        self.assert_error_response(rv, ['call.not_made'], **self.number_response)
        self.env.statbox.assert_has_written([])

    def test_by_flash_call_invalid_track(self):
        self.setup_track_for_commit(
            exclude=[
                'phone_confirmation_sms_count',
                'phone_confirmation_first_send_at',
                'phone_confirmation_last_send_at',
            ],
            phone_confirmation_calls_count='1',
            phone_confirmation_first_called_at=time.time(),
            phone_confirmation_last_called_at=time.time(),
            phone_confirmation_method='by_flash_call',
        )

        rv = self.make_request()
        self.assert_error_response(rv, ['track.invalid_state'], **self.number_response)
        self.env.statbox.assert_has_written([])
        self.env.antifraud_logger.assert_has_written([])

    def test_by_flash_call_code_invalid(self):
        self.setup_track_for_commit(
            exclude=[
                'phone_confirmation_sms_count',
                'phone_confirmation_first_send_at',
                'phone_confirmation_last_send_at',
            ],
            phone_confirmation_calls_count='1',
            phone_call_session_id=TEST_CALL_SESSION_ID,
            phone_confirmation_first_called_at=time.time(),
            phone_confirmation_last_called_at=time.time(),
            phone_confirmation_code='notcode',
            phone_confirmation_method='by_flash_call',
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['code.invalid'], **self.number_response)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('code_invalid'),
        ])
        self.env.antifraud_logger.assert_has_written([])

    def test_sms_after_call(self):
        ts_called = time.time() - 600
        self.setup_track_for_commit(
            phone_confirmation_last_send_at=time.time() - 300,
            phone_confirmation_calls_count='1',
            phone_call_session_id=TEST_CALL_SESSION_ID,
            phone_confirmation_first_called_at=ts_called,
            phone_confirmation_last_called_at=ts_called,
        )
        rv = self.make_request()
        self.assert_ok_response(rv, **self.base_response)

        self.assert_statbox_ok(time_passed=300)
        self.assert_antifraud_log_ok()

    def test_sms_before_call(self):
        ts_sent = time.time() - 600
        self.setup_track_for_commit(
            phone_confirmation_last_send_at=ts_sent,
            phone_confirmation_calls_count='1',
            phone_call_session_id=TEST_CALL_SESSION_ID,
            phone_confirmation_first_called_at=time.time(),
            phone_confirmation_last_called_at=time.time(),
            phone_confirmation_method='by_call',
        )
        rv = self.make_request()
        self.assert_ok_response(rv, **self.base_response)

        self.assert_statbox_ok(confirm_method='by_call')
        self.assert_antifraud_log_ok(phone_confirmation_method='by_call')

    def test_sms_before_flash_call(self):
        ts_sent = time.time() - 600
        self.setup_track_for_commit(
            phone_confirmation_last_send_at=ts_sent,
            phone_confirmation_calls_count='1',
            phone_call_session_id=TEST_CALL_SESSION_ID,
            phone_confirmation_first_called_at=time.time(),
            phone_confirmation_last_called_at=time.time(),
            phone_confirmation_method='by_flash_call',
        )
        rv = self.make_request()
        self.assert_ok_response(rv, **self.base_response)

        self.assert_statbox_ok(confirm_method='by_flash_call')
        self.assert_antifraud_log_ok(phone_confirmation_method='by_flash_call')
