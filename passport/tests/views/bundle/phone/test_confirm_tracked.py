# -*- coding: utf-8 -*-
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.views.bundle.mixins.phone import (
    format_for_android_sms_retriever,
    hash_android_package,
)
from passport.backend.api.views.bundle.phone.controllers import (
    CONFIRM_AND_UPDATE_TRACKED_SECURE_STATE,
    CONFIRM_STATE,
    CONFIRM_TRACKED_SECURE_STATE,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.dbmanager.exceptions import DBError
from passport.backend.core.models.phones.faker import (
    assert_secure_phone_bound,
    build_phone_bound,
    build_phone_secured,
    event_lines_phone_confirmed,
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
from passport.backend.core.types.phone_number.phone_number import mask_phone_number
from passport.backend.utils.common import merge_dicts

from .base import (
    BaseConfirmCommitterTestCase,
    BaseConfirmSubmitterTestCase,
    ConfirmCommitterSentCodeTestMixin,
    ConfirmCommitterTestMixin,
    ConfirmSubmitterAccountNoNumberTestMixin,
    ConfirmSubmitterSendSmsTestMixin,
    TEST_FAKE_CODE,
    TEST_FAKE_PHONE_NUMBER,
    TEST_FAKE_PHONE_NUMBER_DUMPED,
    TEST_LOGIN,
    TEST_OTHER_EXIST_PHONE_NUMBER,
    TEST_PHONE_ID1,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER_DIGITAL,
    TEST_SMS_RETRIEVER_TEXT,
    TEST_TAXI_APPLICATION,
    TEST_UID,
)


@with_settings_hosts(
    APP_ID_SPECIFIC_ROUTE_DENOMINATOR=1,
    APP_ID_TO_SMS_ROUTE={TEST_TAXI_APPLICATION: 'taxi'},
    PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
    PHONE_CONFIRM_MASK_ANTIFRAUD_DENIAL=False,
    SMS_VALIDATION_CODE_LENGTH=4,
    SMS_VALIDATION_MAX_SMS_COUNT=3,
    SMS_VALIDATION_RESEND_TIMEOUT=0,
    YASMS_URL='http://localhost',
    **mock_counters()
)
class ConfirmTrackedSecureSubmitterTestCase(
        BaseConfirmSubmitterTestCase,
        ConfirmSubmitterAccountNoNumberTestMixin,
        ConfirmSubmitterSendSmsTestMixin):

    track_state = CONFIRM_TRACKED_SECURE_STATE
    has_uid = True
    url = '/1/bundle/phone/confirm_tracked_secure/submit/?consumer=dev'
    with_antifraud_score = True

    def setUp(self):
        super(ConfirmTrackedSecureSubmitterTestCase, self).setUp()
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
            ),
        )
        self.setup_track(self.track_id)

    def setup_track(self, track_id, **kwargs):
        """Эта ручка ожидает трек с некоторыми флажками"""
        params = {
            'uid': TEST_UID,
            'secure_phone_number': TEST_PHONE_NUMBER.e164,
            'has_secure_phone_number': True,
        }
        if kwargs:
            params.update(kwargs)

        with self.track_manager.transaction(track_id).rollback_on_error() as track:
            for param, value in params.items():
                setattr(track, param, value)

    def query_params(self, **kwargs):
        base_params = {
            'display_language': 'ru',
            'track_id': self.track_id,
        }

        return merge_dicts(base_params, kwargs)

    def assert_send_sms_request_ok(self, request):
        request.assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'identity': 'confirm_tracked_secure',
        })
        request.assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

    def ok_case(self):
        rv = self.make_request()
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            self.base_send_code_response,
        )

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        self.assert_send_sms_request_ok(requests[0])

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)

        self.assert_statbox_ok()

    def test_ok(self):
        self.ok_case()

    def test_ok_by_3_dash(self):
        self.confirmation_code = '555-5'
        rv = self.make_request(self.query_params(code_format='by_3_dash'))
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            self.base_send_code_response,
        )

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        self.assert_send_sms_request_ok(requests[0])

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)

        self.assert_statbox_ok()

    def test_ok_for_social(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                aliases={'social': 'uid-xxx'},
                crypt_password=None,
            ),
        )
        self.ok_case()

    def test_ok_with_confirm_state(self):
        # Успешное прохождение ручки, если состояние трека CONFIRM_STATE
        self.setup_track(self.track_id, state=CONFIRM_STATE)
        self.ok_case()

    def test_no_secure_number_in_track__error(self):
        # Если в треке не хватает данных, бросит track.invalid_state
        self.setup_track(self.track_id, secure_phone_number='')

        rv = self.make_request()
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'track_id': self.track_id,
                u'errors': [u'track.invalid_state'],
            },
        )

    def test_no_secure_number_in_track_but_with_bank_phone__ok(self):
        # В треке нет секьюрного телефона, но есть банковский номер
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                aliases={
                    'bank_phonenumber': TEST_PHONE_NUMBER.digital,
                    'portal': TEST_LOGIN,
                },
                **build_phone_bound(TEST_PHONE_ID1, TEST_PHONE_NUMBER.e164)
            ),
        )
        self.setup_track(self.track_id, has_secure_phone_number=False, secure_phone_number='')

        rv = self.make_request()
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_send_code_response,
                {
                    u'number': merge_dicts(
                        self.base_send_code_response[u'number'],
                        {
                            u'original': TEST_PHONE_NUMBER_DIGITAL.original,
                            u'masked_original': mask_phone_number(TEST_PHONE_NUMBER_DIGITAL.original),
                        },
                    ),
                },
            ),
        )

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        self.assert_send_sms_request_ok(requests[0])

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track, phone_number=TEST_PHONE_NUMBER_DIGITAL)

        self.assert_statbox_ok()

    def test_account_disabled__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                enabled=False,
            ),
        )

        rv = self.make_request()

        response_data = merge_dicts(
            self.base_submitter_response,
            {u'status': u'error', u'errors': [u'account.disabled']},
        )
        del response_data[u'number']

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            response_data,
        )
        eq_(self.env.blackbox._mock.request.call_count, 1)
        eq_(len(self.env.yasms.requests), 0)

        self.env.statbox.assert_has_written([])

    def test_phone_confirmed_with_flash_call(self):
        self.setup_track(
            track_id=self.track_id,
            phone_confirmation_is_confirmed=True,
            phone_confirmation_method='by_flash_call',
            phone_confirmation_phone_number=TEST_PHONE_NUMBER.e164,
            phone_valid_for_flash_call=True,
        )

        rv = self.make_request()

        self.assert_ok_response(rv, check_all=False)

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)
        eq_(track.phone_confirmation_method, 'by_sms')

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        self.assert_send_sms_request_ok(requests[0])

    def test_antifraud_score_deny(self):
        self.setup_antifraud_score_response(False)

        rv = self.make_request(self.query_params())

        self.assert_error_response(rv, ['sms_limit.exceeded'], check_content=False)
        self.assert_antifraud_score_called(uid=TEST_UID)
        self.assert_statbox_antifraud_deny_ok()

    def test_antifraud_score_deny_masked(self):
        self.setup_antifraud_score_response(False)

        with settings_context(
            PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
            PHONE_CONFIRM_MASK_ANTIFRAUD_DENIAL=True,
        ):
            rv = self.make_request(self.query_params())

        self.assert_ok_response(rv, check_all=False)
        self.assert_antifraud_score_called(uid=TEST_UID)
        self.assert_statbox_antifraud_deny_ok(mask_denial=True)


@with_settings_hosts(
    YASMS_URL='http://localhost',
    SMS_VALIDATION_CODE_LENGTH=4,
    SMS_VALIDATION_RESEND_TIMEOUT=0,
    SMS_VALIDATION_MAX_SMS_COUNT=3,
    APP_ID_SPECIFIC_ROUTE_DENOMINATOR=1,
    APP_ID_TO_SMS_ROUTE={TEST_TAXI_APPLICATION: 'taxi'},
    ANDROID_PACKAGE_PREFIXES_WHITELIST={'com.yandex'},
    ANDROID_PACKAGE_PUBLIC_KEY_DEFAULT='public-key',
    ANDROID_PACKAGE_PREFIX_TO_KEY={},
    **mock_counters()
)
class ConfirmTrackedSecureSubmitterForSmsRetrieverTestCase(ConfirmTrackedSecureSubmitterTestCase):
    def setUp(self):
        super(ConfirmTrackedSecureSubmitterForSmsRetrieverTestCase, self).setUp()

        self.package_name = 'com.yandex.passport.testapp1'

        self.setup_statbox_templates(
            sms_retriever_kwargs=dict(
                gps_package_name=self.package_name,
                sms_retriever='1',
            ),
        )

        eq_(hash_android_package(self.package_name, 'public-key'), 'gNNu9q4gcSd')

    @property
    def sms_text(self):
        return format_for_android_sms_retriever(
            TEST_SMS_RETRIEVER_TEXT,
            'gNNu9q4gcSd',
        )

    def query_params(self, **kwargs):
        return super(ConfirmTrackedSecureSubmitterForSmsRetrieverTestCase, self).query_params(
            gps_package_name=self.package_name,
            **kwargs
        )


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    SMS_VALIDATION_MAX_CHECKS_COUNT=3,
    FAKE_CODE=TEST_FAKE_CODE,
    TEST_PHONE_NUMBERS_ACCEPTING_FAKE_CODE = (
        TEST_FAKE_PHONE_NUMBER.e164,
    ),
)
class ConfirmTrackedSecureCommitterTestCase(
        BaseConfirmCommitterTestCase,
        ConfirmCommitterTestMixin,
        ConfirmCommitterSentCodeTestMixin):

    track_state = CONFIRM_TRACKED_SECURE_STATE
    has_uid = True
    url = '/1/bundle/phone/confirm_tracked_secure/commit/?consumer=dev'

    def query_params(self, **kwargs):
        base_params = {
            'code': self.confirmation_code,
            'track_id': self.track_id,
        }

        return merge_dicts(base_params, kwargs)

    def test_ok(self):
        self.setup_track_for_commit()

        rv = self.make_request()
        eq_(rv.status_code, 200, rv.data)
        eq_(json.loads(rv.data), self.base_response)

        track = self.track_manager.read(self.track_id)

        ok_(track.phone_confirmation_is_confirmed)
        eq_(track.phone_confirmation_confirms_count.get(), 1)
        ok_(not track.phone_confirmation_confirms_count_limit_reached)
        eq_(track.phone_confirmation_first_checked, TimeNow())
        eq_(track.phone_confirmation_last_checked, TimeNow())

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('enter_code'),
            self.env.statbox.entry('success'),
        ])

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

    def test_fake_code_not_accepted_for_normal_number(self):
        self.setup_track_for_commit()

        rv = self.make_request(self.query_params(code='000-000'))
        self.assert_error_response(rv, ['code.invalid'], **self.number_response)

    def test_ok_for_social(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                aliases={'social': 'uid-xxx'},
                crypt_password=None,
            ),
        )
        self.setup_track_for_commit()

        rv = self.make_request()
        eq_(rv.status_code, 200, rv.data)
        eq_(json.loads(rv.data), self.base_response)

    def test_disabled_account__error(self):
        self.setup_track_for_commit()

        self.env.blackbox.set_blackbox_response_side_effect('userinfo', None)
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                enabled=False,
            ),
        )

        rv = self.make_request()
        eq_(rv.status_code, 200, rv.data)
        resp = json.loads(rv.data)
        eq_(resp['errors'], ['account.disabled'], resp)


@with_settings_hosts(
    PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
    SMS_VALIDATION_CODE_LENGTH=4,
    SMS_VALIDATION_MAX_SMS_COUNT=3,
    SMS_VALIDATION_RESEND_TIMEOUT=0,
    YASMS_URL='http://localhost',
    **mock_counters()
)
class ConfirmAndUpdateTrackedSecureSubmitterTestCase(ConfirmTrackedSecureSubmitterTestCase):
    """Тест для ручки-копии"""
    track_state = CONFIRM_AND_UPDATE_TRACKED_SECURE_STATE
    url = '/1/bundle/phone/confirm_and_update_tracked_secure/submit/?consumer=dev'


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    SMS_VALIDATION_MAX_CHECKS_COUNT=3,
)
class ConfirmAndUpdateTrackedSecureCommitterTestCase(
        BaseConfirmCommitterTestCase,
        ConfirmCommitterTestMixin,
        ConfirmCommitterSentCodeTestMixin):

    track_state = CONFIRM_AND_UPDATE_TRACKED_SECURE_STATE
    has_uid = True
    url = '/1/bundle/phone/confirm_and_update_tracked_secure/commit/?consumer=dev'

    def setup_account(self, userinfo_args=None):
        userinfo_args = userinfo_args or dict(
            uid=TEST_UID,
            **build_phone_secured(
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER.e164,
            )
        )
        userinfo = blackbox_userinfo_response(**userinfo_args)

        if userinfo_args['uid']:
            self.env.db.serialize(userinfo)

        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)

    def query_params(self, **kwargs):
        base_params = {
            'code': self.confirmation_code,
            'track_id': self.track_id,
        }

        return merge_dicts(base_params, kwargs)

    def test_ok(self):
        self.setup_track_for_commit()
        self.setup_account()

        rv = self.make_request()
        eq_(rv.status_code, 200, rv.data)
        eq_(json.loads(rv.data), self.base_response)

        track = self.track_manager.read(self.track_id)

        ok_(track.phone_confirmation_is_confirmed)
        eq_(track.phone_confirmation_confirms_count.get(), 1)
        ok_(not track.phone_confirmation_confirms_count_limit_reached)
        eq_(track.phone_confirmation_first_checked, TimeNow())
        eq_(track.phone_confirmation_last_checked, TimeNow())

        assert_secure_phone_bound.check_db(self.env.db, TEST_UID, {'id': TEST_PHONE_ID1, 'confirmed': DatetimeNow()})

        self.env.event_logger.assert_contains(
            event_lines_phone_confirmed(
                action='confirm_and_update_tracked_secure',
                uid=TEST_UID,
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER,
            ),
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('enter_code'),
            self.env.statbox.entry('success'),
        ])

    def test_update_phone_dberror(self):
        self.setup_track_for_commit()
        self.setup_account()
        self.env.db.set_side_effect_for_db('passportdbshard1', DBError())

        rv = self.make_request()
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {
                    u'status': u'error',
                    u'errors': [u'backend.database_failed'],
                },
            ),
        )

        track = self.track_manager.read(self.track_id)

        ok_(track.phone_confirmation_is_confirmed)
        eq_(track.phone_confirmation_confirms_count.get(), 1)
        ok_(not track.phone_confirmation_confirms_count_limit_reached)
        eq_(track.phone_confirmation_first_checked, TimeNow())
        eq_(track.phone_confirmation_last_checked, TimeNow())

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('enter_code'),
        ])

    def replay_error(self, errors, bb_call_count=1, statbox_lines=None):
        rv = self.make_request()
        eq_(rv.status_code, 200, rv.data)
        resp = json.loads(rv.data)
        eq_(resp['errors'], errors, resp)

        eq_(self.env.blackbox._mock.request.call_count, bb_call_count)

        self.env.statbox.assert_has_written(statbox_lines or [])

    def test_no_secure_number__error(self):
        self.setup_track_for_commit()
        self.setup_account(dict(
            uid=TEST_UID,
            **build_phone_bound(
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER.e164,
            )
        ))

        self.replay_error(
            ['phone_secure.not_found'],
            statbox_lines=self.env.statbox.entry('enter_code'),
        )

    def test_secure_number_changed__error(self):
        self.setup_track_for_commit()
        self.setup_account(dict(
            uid=TEST_UID,
            **build_phone_secured(
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_OTHER_EXIST_PHONE_NUMBER.e164,
            )
        ))

        self.replay_error(
            ['phone_secure.not_found'],
            statbox_lines=self.env.statbox.entry('enter_code'),
        )
