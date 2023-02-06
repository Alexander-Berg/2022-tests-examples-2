# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.views.bundle.mixins.phone import (
    KOLMOGOR_COUNTER_CALLS_FAILED,
    KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG,
    KOLMOGOR_COUNTER_SESSIONS_CREATED,
)
from passport.backend.api.views.bundle.phone.helpers import format_code_by_3
from passport.backend.core.builders.antifraud.faker.fake_antifraud import antifraud_score_response
from passport.backend.core.builders.octopus.faker import octopus_response
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.types.phone_number.phone_number import (
    mask_for_statbox,
    mask_phone_number,
    PhoneNumber,
)

from .base import (
    BaseConfirmTestCase,
    FAKE_OCTOPUS_SESSION_ID_FOR_TEST_PHONES,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER_DUMPED,
)


TEST_PHONE_VALIDATION_MAX_CALLS_COUNT = 3
TEST_FAKE_NUMBER = PhoneNumber.parse('+70001000099')
TEST_FAKE_NUMBER_DUMPED = {
    u'international': TEST_FAKE_NUMBER.international,
    u'e164': TEST_FAKE_NUMBER.e164,
    u'original': TEST_FAKE_NUMBER.original,

    u'masked_original': mask_phone_number(TEST_FAKE_NUMBER.original),
    u'masked_international': mask_phone_number(TEST_FAKE_NUMBER.international),
    u'masked_e164': mask_phone_number(TEST_FAKE_NUMBER.e164),
}
TEST_KOLMOGOR_KEYSPACE_COUNTERS = 'octopus-calls-counters'
TEST_KOLMOGOR_KEYSPACE_FLAG = 'octopus-calls-flag'


@with_settings_hosts(
    OCTOPUS_URL='http://localhost',
    OCTOPUS_TIMEOUT=2,
    OCTOPUS_RETRIES=1,
    OCTOPUS_AUTH_TOKEN='key',
    PHONE_CONFIRMATION_FLASH_CALL_COUNTRIES=('ru',),
    PHONE_VALIDATION_CODE_LENGTH=6,
    PHONE_DIGITAL_PREFIXES_BLACKLIST=['7999', '7954'],
    PHONE_VALIDATION_MAX_CALLS_COUNT=TEST_PHONE_VALIDATION_MAX_CALLS_COUNT,
    PHONE_VALIDATION_MAX_CALLS_CHECKS_COUNT=2,
    OCTOPUS_COUNTERS_MIN_COUNT=10,
    OCTOPUS_GATES_WORKING_THRESHOLD=0.9,
    KOLMOGOR_KEYSPACE_OCTOPUS_CALLS_COUNTERS=TEST_KOLMOGOR_KEYSPACE_COUNTERS,
    KOLMOGOR_KEYSPACE_OCTOPUS_CALLS_FLAG=TEST_KOLMOGOR_KEYSPACE_FLAG,
    KOLMOGOR_URL='http://localhost',
    KOLMOGOR_TIMEOUT=1,
    KOLMOGOR_RETRIES=1,
    PHONE_CONFIRM_CHECK_IP_BLACKLIST=True,
    PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
    PHONE_CONFIRM_MASK_ANTIFRAUD_DENIAL=True,
    **mock_counters()
)
class TestConfirmByCallIntegrationalTestCase(BaseConfirmTestCase):
    has_uid = False
    track_state = 'confirm'

    def setUp(self):
        super(TestConfirmByCallIntegrationalTestCase, self).setUp()
        self.env.grants.set_grants_return_value(mock_grants(grants={'phone_bundle': ['*'], 'phone_number': ['validate']}))
        self.confirmation_code = format_code_by_3(self.confirmation_code)
        self.env.octopus.set_response_value('create_session', octopus_response())
        self.env.kolmogor.set_response_value('inc', 'OK')
        self.env.antifraud_api.set_response_value('score', antifraud_score_response())
        self.flag = {
            KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 0,
        }
        self.counters = {
            KOLMOGOR_COUNTER_SESSIONS_CREATED: 5,
            KOLMOGOR_COUNTER_CALLS_FAILED: 0,
        }

    def validate(self, valid=True, consumer='dev', number=TEST_PHONE_NUMBER, dumped=None):
        self.env.kolmogor.set_response_side_effect('get', [self.flag, self.counters])
        dumped = dumped or TEST_PHONE_NUMBER_DUMPED
        self.url = '/1/bundle/validate/phone_number/?consumer=%s' % consumer

        query_params = {
            'phone_number': number.e164,
            'validate_for_call': 'true',
            'track_id': self.track_id,
        }
        rv = self.make_request(query_params)
        self.assert_ok_response(rv, phone_number=dumped, valid_for_call=valid, valid_for_flash_call=valid)

    def submit(self, calls_count=1, errors=None, consumer='dev', number=TEST_PHONE_NUMBER, dumped=None):
        self.env.kolmogor.set_response_side_effect('get', [self.flag, self.counters])
        dumped = dumped or TEST_PHONE_NUMBER_DUMPED
        self.url = '/1/bundle/phone/confirm/submit/?consumer=%s' % consumer

        query_params = {
            'confirm_method': 'by_call',
            'number': number.e164,
            'display_language': 'en',
            'track_id': self.track_id,
        }
        rv = self.make_request(query_params)

        if errors:
            self.assert_error_response(rv, errors, number=dumped, track_id=self.track_id)

        else:
            self.assert_ok_response(rv, number=dumped, track_id=self.track_id, code_length=6)

        track = self.track_manager.read(self.track_id)
        eq_(track.phone_confirmation_code, self.confirmation_code)
        eq_(track.phone_confirmation_phone_number, number.e164)
        ok_(not track.phone_confirmation_is_confirmed)

        ok_(not track.phone_confirmation_sms)
        ok_(not track.phone_confirmation_sms_count.get())
        ok_(not track.phone_confirmation_first_send_at)
        ok_(not track.phone_confirmation_last_send_at)

        eq_(track.phone_confirmation_calls_count.get(), calls_count)
        eq_(track.phone_confirmation_first_called_at, TimeNow())
        eq_(track.phone_confirmation_last_called_at, TimeNow())

    def commit(self, consumer='dev', number=TEST_PHONE_NUMBER, dumped=None):
        dumped = dumped or TEST_PHONE_NUMBER_DUMPED
        self.url = '/1/bundle/phone/confirm/commit/?consumer=%s' % consumer

        query_params = {
            'code': self.confirmation_code,
            'track_id': self.track_id,
        }
        rv = self.make_request(query_params)

        self.assert_ok_response(rv, number=dumped)
        track = self.track_manager.read(self.track_id)
        eq_(track.phone_confirmation_code, self.confirmation_code)
        eq_(track.phone_confirmation_phone_number, number.e164)
        ok_(track.phone_confirmation_is_confirmed)

    def test_ok(self):
        self.setup_antifraud_score_response()
        self.validate()
        self.submit()
        self.commit()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('sanitize_phone_number'),
            self.env.statbox.entry('antifraud_score_allow', step='submit'),
            self.env.statbox.entry('call_with_code', step='submit'),
            self.env.statbox.entry('success', step='submit'),
            self.env.statbox.entry('enter_code', step='commit'),
            self.env.statbox.entry('success', step='commit', confirm_method='by_call'),
        ])

    def test_check_validation_first_ok(self):
        for i in range(TEST_PHONE_VALIDATION_MAX_CALLS_COUNT):
            self.validate()
            self.submit(calls_count=i + 1)

        self.validate(valid=False)
        self.submit(calls_count=TEST_PHONE_VALIDATION_MAX_CALLS_COUNT, errors=['track.invalid_state'])

    def test_fake_ok(self):
        consumer = 'kopusha'
        self.env.grants.set_grants_return_value(
            mock_grants(consumer=consumer, grants={'phone_bundle': ['*'], 'phone_number': ['validate']}),
        )
        self.setup_antifraud_score_response()
        self.validate(consumer=consumer, number=TEST_FAKE_NUMBER, dumped=TEST_FAKE_NUMBER_DUMPED)
        self.submit(consumer=consumer, number=TEST_FAKE_NUMBER, dumped=TEST_FAKE_NUMBER_DUMPED)
        self.commit(consumer=consumer, number=TEST_FAKE_NUMBER, dumped=TEST_FAKE_NUMBER_DUMPED)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'sanitize_phone_number',
                sanitize_phone_result=mask_for_statbox(TEST_FAKE_NUMBER.e164),
            ),
            self.env.statbox.entry(
                'antifraud_score_allow',
                consumer='kopusha',
                step='submit',
                number=mask_for_statbox(TEST_FAKE_NUMBER.e164),
            ),
            self.env.statbox.entry(
                'call_with_code',
                step='submit',
                consumer='kopusha',
                number=mask_for_statbox(TEST_FAKE_NUMBER.e164),
                call_session_id=FAKE_OCTOPUS_SESSION_ID_FOR_TEST_PHONES,
            ),
            self.env.statbox.entry(
                'success',
                step='submit',
                consumer='kopusha',
                number=mask_for_statbox(TEST_FAKE_NUMBER.e164),
            ),
            self.env.statbox.entry(
                'enter_code',
                step='commit',
                consumer='kopusha',
                number=mask_for_statbox(TEST_FAKE_NUMBER.e164),
            ),
            self.env.statbox.entry(
                'success',
                step='commit',
                consumer='kopusha',
                number=mask_for_statbox(TEST_FAKE_NUMBER.e164),
                confirm_method='by_call',
            ),
        ])

    def test_antifraud_denial_masked(self):
        # Проверяем, что если антифрод отказал в звонке - мы звонить и не будем. Но при этом сценарий полностью
        # выглядит  как рабочий, можно попробовать ввести код (а если его угадать - то и телефон подтвердится)
        self.setup_antifraud_score_response(allow=False)
        self.validate()
        self.submit()
        self.commit()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('sanitize_phone_number'),
            self.env.statbox.entry('antifraud_score_deny', step='submit', mask_denial='1'),
            # нет записи про совершение звонка
            self.env.statbox.entry('success', step='submit'),
            self.env.statbox.entry('enter_code', step='commit'),
            self.env.statbox.entry('success', step='commit', confirm_method='by_call'),
        ])


@with_settings_hosts(
    OCTOPUS_URL='http://localhost',
    OCTOPUS_TIMEOUT=2,
    OCTOPUS_RETRIES=1,
    OCTOPUS_AUTH_TOKEN='key',
    PHONE_CONFIRMATION_FLASH_CALL_COUNTRIES=('ru',),
    PHONE_VALIDATION_CODE_LENGTH=6,
    PHONE_DIGITAL_PREFIXES_BLACKLIST=['7999', '7954'],
    PHONE_VALIDATION_MAX_CALLS_COUNT=TEST_PHONE_VALIDATION_MAX_CALLS_COUNT,
    PHONE_VALIDATION_MAX_CALLS_CHECKS_COUNT=2,
    OCTOPUS_COUNTERS_MIN_COUNT=10,
    OCTOPUS_GATES_WORKING_THRESHOLD=0.9,
    KOLMOGOR_KEYSPACE_OCTOPUS_CALLS_COUNTERS=TEST_KOLMOGOR_KEYSPACE_COUNTERS,
    KOLMOGOR_KEYSPACE_OCTOPUS_CALLS_FLAG=TEST_KOLMOGOR_KEYSPACE_FLAG,
    KOLMOGOR_URL='http://localhost',
    KOLMOGOR_TIMEOUT=1,
    KOLMOGOR_RETRIES=1,
    FLASH_CALL_NUMBERS=['+11111110000'],
    PHONE_CONFIRM_CHECK_IP_BLACKLIST=True,
    PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
    PHONE_CONFIRM_MASK_ANTIFRAUD_DENIAL=True,
    **mock_counters()
)
class TestConfirmByFlashCallIntegrationalTestCase(BaseConfirmTestCase):
    has_uid = False
    track_state = 'confirm'

    def setUp(self):
        super(TestConfirmByFlashCallIntegrationalTestCase, self).setUp()
        self.env.grants.set_grants_return_value(mock_grants(grants={'phone_bundle': ['*'], 'phone_number': ['validate']}))
        self.confirmation_code = '0000'
        self.env.octopus.set_response_value('create_flash_call_session', octopus_response())
        self.env.kolmogor.set_response_value('inc', 'OK')
        self.flag = {
            KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 0,
        }
        self.counters = {
            KOLMOGOR_COUNTER_SESSIONS_CREATED: 5,
            KOLMOGOR_COUNTER_CALLS_FAILED: 0,
        }

    def validate(self, valid=True, consumer='dev', number=TEST_PHONE_NUMBER, dumped=None):
        self.env.kolmogor.set_response_side_effect('get', [self.flag, self.counters])
        dumped = dumped or TEST_PHONE_NUMBER_DUMPED
        self.url = '/1/bundle/validate/phone_number/?consumer=%s' % consumer

        query_params = {
            'phone_number': number.e164,
            'validate_for_call': 'true',
            'track_id': self.track_id,
        }
        rv = self.make_request(query_params)
        self.assert_ok_response(rv, phone_number=dumped, valid_for_call=valid, valid_for_flash_call=valid)

    def submit(self, calls_count=1, errors=None, consumer='dev', number=TEST_PHONE_NUMBER, dumped=None):
        self.env.kolmogor.set_response_side_effect('get', [self.flag, self.counters])
        dumped = dumped or TEST_PHONE_NUMBER_DUMPED
        self.url = '/1/bundle/phone/confirm/submit/?consumer=%s' % consumer

        query_params = {
            'confirm_method': 'by_flash_call',
            'number': number.e164,
            'display_language': 'en',
            'track_id': self.track_id,
        }
        rv = self.make_request(query_params)

        if errors:
            self.assert_error_response(rv, errors, number=dumped, track_id=self.track_id)

        else:
            self.assert_ok_response(
                rv,
                number=dumped,
                track_id=self.track_id,
                code_length=4,
                calling_number_template='+1 111111XXXX',
            )

        track = self.track_manager.read(self.track_id)
        eq_(track.phone_confirmation_code, self.confirmation_code)
        eq_(track.phone_confirmation_phone_number, number.e164)
        ok_(not track.phone_confirmation_is_confirmed)

        ok_(not track.phone_confirmation_sms)
        ok_(not track.phone_confirmation_sms_count.get())
        ok_(not track.phone_confirmation_first_send_at)
        ok_(not track.phone_confirmation_last_send_at)

        eq_(track.phone_confirmation_calls_count.get(), calls_count)
        eq_(track.phone_confirmation_first_called_at, TimeNow())
        eq_(track.phone_confirmation_last_called_at, TimeNow())

    def commit(self, consumer='dev', number=TEST_PHONE_NUMBER, dumped=None):
        dumped = dumped or TEST_PHONE_NUMBER_DUMPED
        self.url = '/1/bundle/phone/confirm/commit/?consumer=%s' % consumer

        query_params = {
            'code': self.confirmation_code,
            'track_id': self.track_id,
        }
        rv = self.make_request(query_params)

        self.assert_ok_response(rv, number=dumped)
        track = self.track_manager.read(self.track_id)
        eq_(track.phone_confirmation_code, self.confirmation_code)
        eq_(track.phone_confirmation_phone_number, number.e164)
        ok_(track.phone_confirmation_is_confirmed)

    def test_ok(self):
        self.validate()
        self.submit()
        self.commit()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('sanitize_phone_number'),
            self.env.statbox.entry('antifraud_score_allow', step='submit'),
            self.env.statbox.entry('flash_call', step='submit'),
            self.env.statbox.entry('success', step='submit'),
            self.env.statbox.entry('enter_code', step='commit'),
            self.env.statbox.entry('success', step='commit', confirm_method='by_flash_call'),
        ])

    def test_check_validation_first_ok(self):
        for i in range(TEST_PHONE_VALIDATION_MAX_CALLS_COUNT):
            self.validate()
            self.submit(calls_count=i + 1)

        self.validate(valid=False)
        self.submit(calls_count=TEST_PHONE_VALIDATION_MAX_CALLS_COUNT, errors=['track.invalid_state'])

    def test_fake_ok(self):
        consumer = 'kopusha'
        self.env.grants.set_grants_return_value(
            mock_grants(consumer=consumer, grants={'phone_bundle': ['*'], 'phone_number': ['validate']}),
        )
        self.validate(consumer=consumer, number=TEST_FAKE_NUMBER, dumped=TEST_FAKE_NUMBER_DUMPED)
        self.submit(consumer=consumer, number=TEST_FAKE_NUMBER, dumped=TEST_FAKE_NUMBER_DUMPED)
        self.commit(consumer=consumer, number=TEST_FAKE_NUMBER, dumped=TEST_FAKE_NUMBER_DUMPED)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'sanitize_phone_number',
                sanitize_phone_result=mask_for_statbox(TEST_FAKE_NUMBER.e164),
            ),
            self.env.statbox.entry(
                'antifraud_score_allow',
                step='submit',
                consumer='kopusha',
                number=mask_for_statbox(TEST_FAKE_NUMBER.e164),
            ),
            self.env.statbox.entry(
                'flash_call',
                step='submit',
                consumer='kopusha',
                number=mask_for_statbox(TEST_FAKE_NUMBER.e164),
                call_session_id=FAKE_OCTOPUS_SESSION_ID_FOR_TEST_PHONES,
            ),
            self.env.statbox.entry(
                'success',
                step='submit',
                consumer='kopusha',
                number=mask_for_statbox(TEST_FAKE_NUMBER.e164),
            ),
            self.env.statbox.entry(
                'enter_code',
                step='commit',
                consumer='kopusha',
                number=mask_for_statbox(TEST_FAKE_NUMBER.e164),
            ),
            self.env.statbox.entry(
                'success',
                step='commit',
                consumer='kopusha',
                number=mask_for_statbox(TEST_FAKE_NUMBER.e164),
                confirm_method='by_flash_call',
            ),
        ])

    def test_antifraud_denial_masked(self):
        # Проверяем, что если антифрод отказал в звонке - мы звонить и не будем. Но при этом сценарий полностью
        # выглядит  как рабочий, можно попробовать ввести код (а если его угадать - то и телефон подтвердится)
        self.setup_antifraud_score_response(allow=False)
        self.validate()
        self.submit()
        self.commit()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('sanitize_phone_number'),
            self.env.statbox.entry('antifraud_score_deny', step='submit', mask_denial='1'),
            # нет записи про совершение звонка
            self.env.statbox.entry('success', step='submit'),
            self.env.statbox.entry('enter_code', step='commit'),
            self.env.statbox.entry('success', step='commit', confirm_method='by_flash_call'),
        ])
