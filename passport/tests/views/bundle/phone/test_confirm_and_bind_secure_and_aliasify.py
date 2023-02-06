# -*- coding: utf-8 -*-

from datetime import timedelta
import json
from unittest import skip

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.emails import (
    assert_user_notified_about_alias_as_login_and_email_enabled,
    assert_user_notified_about_alias_as_login_and_email_owner_changed,
)
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.views.bundle.phone.controllers import CONFIRM_AND_BIND_SECURE_AND_ALIASIFY_STATE
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_SESSIONID_DISABLED_STATUS,
    BLACKBOX_SESSIONID_EXPIRED_STATUS,
    BLACKBOX_SESSIONID_INVALID_STATUS,
    BLACKBOX_SESSIONID_NOAUTH_STATUS,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_phone_bindings_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.dbmanager.exceptions import DBError
from passport.backend.core.models.phones.faker import (
    assert_account_has_phonenumber_alias,
    assert_secure_phone_bound,
    build_phone_being_bound,
    build_phone_secured,
    build_secure_phone_being_bound,
    event_lines_secure_bind_operation_created,
    event_lines_secure_phone_bound,
)
from passport.backend.core.test.consts import (
    TEST_PASSWORD_HASH1,
    TEST_SOCIAL_LOGIN1,
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
from passport.backend.core.yasms.test.emails import assert_user_notified_about_secure_phone_bound
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
    ConfirmSubmitterAccountTestMixin,
    ConfirmSubmitterAlreadyConfirmedPhoneWithNewPhoneTestMixin,
    ConfirmSubmitterChangePasswordNewSecureNumberTestMixin,
    ConfirmSubmitterLocalPhonenumberMixin,
    ConfirmSubmitterSendSmsTestMixin,
    ConfirmSubmitterSpecificTestMixin,
    HEADERS_WITH_SESSIONID,
    LITE_ACCOUNT_KWARGS,
    MAILISH_ACCOUNT_KWARGS,
    PDD_ACCOUNT_KWARGS,
    PHONISH_ACCOUNT_KWARGS,
    SOCIAL_ACCOUNT_KWARGS,
    SUPER_LITE_ACCOUNT_KWARGS,
    TEST_LOGIN,
    TEST_NOT_EXIST_PHONE_NUMBER,
    TEST_NOT_EXIST_PHONE_NUMBER_DUMPED,
    TEST_OPERATION_ID,
    TEST_OTHER_LOGIN,
    TEST_PHONE_ID1,
    TEST_PHONE_ID2,
    TEST_PHONE_NUMBER,
    TEST_SESSION_ID,
    TEST_TAXI_APPLICATION,
    TEST_UID,
    TEST_USER_IP,
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
class TestConfirmAndBindSecureAndAliasifySubmitter(
    BaseConfirmSubmitterTestCase,
    ConfirmSubmitterAccountTestMixin,
    ConfirmSubmitterSendSmsTestMixin,
    ConfirmSubmitterSpecificTestMixin,
    ConfirmSubmitterLocalPhonenumberMixin,
    ConfirmSubmitterChangePasswordNewSecureNumberTestMixin,
    ConfirmSubmitterAlreadyConfirmedPhoneWithNewPhoneTestMixin,
    EmailTestMixin,
):

    track_state = CONFIRM_AND_BIND_SECURE_AND_ALIASIFY_STATE
    url = '/1/bundle/phone/confirm_and_bind_secure_and_aliasify/submit/?consumer=dev'
    with_antifraud_score = True

    def setUp(self):
        super(TestConfirmAndBindSecureAndAliasifySubmitter, self).setUp()
        self.additional_ok_response_params = dict(is_password_required=False)
        self.setup_account(setup_db=False)

    def setup_account(
        self,
        alias_type='portal',
        crypt_password=TEST_PASSWORD_HASH1,
        login=TEST_LOGIN,
        setup_db=True,
    ):
        userinfo_response = blackbox_userinfo_response(
            aliases={alias_type: login},
            crypt_password=crypt_password,
            login=login,
            uid=TEST_UID,
            emails=[
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )
        self.env.blackbox.set_response_value('userinfo', userinfo_response)

        if setup_db:
            self.env.db.serialize(userinfo_response)

    def query_params(self, exclude=None, **kwargs):
        base_params = {
            'number': TEST_PHONE_NUMBER.e164,
            'display_language': 'ru',
            'track_id': self.track_id,
            'uid': TEST_UID,
        }
        if exclude is not None:
            for key in exclude:
                del base_params[key]
        return merge_dicts(base_params, kwargs)

    def check_ok_track(
        self,
        track,
        used_gate_ids=None,
        phone_number=TEST_PHONE_NUMBER,
        enable_phonenumber_alias_as_email=True,
    ):
        super(TestConfirmAndBindSecureAndAliasifySubmitter, self).check_ok_track(
            track,
            used_gate_ids=used_gate_ids,
            phone_number=phone_number,
        )
        self.assertIs(track.enable_phonenumber_alias_as_email, enable_phonenumber_alias_as_email)

    def ok_response(self, **kwargs):
        return merge_dicts(
            self.base_send_code_response,
            self.additional_ok_response_params,
            kwargs,
        )

    def make_request_with_sessionid(self):
        return self.make_request(
            self.query_params(sessionid=TEST_SESSION_ID, exclude=['uid']),
        )

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(rv, **self.ok_response())

        eq_(self.env.blackbox._mock.request.call_count, 1)

        eq_(self._code_generator_faker.call_count, 1)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'identity': 'confirm_and_bind_secure_and_aliasify',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)
        ok_(track.country is None)
        eq_(track.uid, str(TEST_UID))

        self.assert_statbox_ok()

    def test_ok_by_sessionid(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login_id='login-id',
                attributes={'password.encrypted': '1:testpassword'},
                age=100500,
            ),
        )

        rv = self.make_request_with_sessionid()

        self.assert_ok_response(rv, **self.ok_response())

        eq_(self.env.blackbox._mock.request.call_count, 1)

        eq_(self._code_generator_faker.call_count, 1)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'identity': 'confirm_and_bind_secure_and_aliasify',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)
        ok_(track.country is None)
        eq_(track.uid, str(TEST_UID))

        self.assert_statbox_ok(with_check_cookies=True)
        self.assert_antifraud_score_called(login_id='login-id')

    def test_2fa_no_password_ok(self):
        """
        Проверяем, что пользователь с включенным 2FA и без установленного
        пароля все равно считается имеющим пароль.
        """
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                attributes={
                    'account.2fa_on': '1',
                    'password.encrypted': '',
                },
            ),
        )
        rv = self.make_request()

        self.assert_ok_response(rv, **self.ok_response())

        eq_(self.env.blackbox._mock.request.call_count, 1)

        eq_(self._code_generator_faker.call_count, 1)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            'phone': TEST_PHONE_NUMBER.e164,
            'text': self.sms_text,
            'identity': 'confirm_and_bind_secure_and_aliasify',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)
        ok_(track.country is None)
        eq_(track.uid, str(TEST_UID))

        self.assert_statbox_ok()

    def test_invalid_sessionid(self):
        for status in [BLACKBOX_SESSIONID_EXPIRED_STATUS,
                       BLACKBOX_SESSIONID_NOAUTH_STATUS,
                       BLACKBOX_SESSIONID_INVALID_STATUS]:
            self.env.blackbox.set_blackbox_response_value(
                'sessionid',
                blackbox_sessionid_multi_response(status=status),
            )

            rv = self.make_request_with_sessionid()

            eq_(rv.status_code, 200, rv.data)
            eq_(
                json.loads(rv.data),
                merge_dicts(
                    self.base_submitter_response,
                    {u'status': u'error', u'errors': [u'sessionid.invalid']},
                ),
            )

        eq_(self.env.blackbox._mock.request.call_count, 3)

        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')] * 3)

    def test_disabled_account_by_uid(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                enabled=False,
            ),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {u'status': u'error', u'errors': [u'account.disabled']},
            ),
        )

        eq_(self.env.blackbox._mock.request.call_count, 1)

        self.env.statbox.assert_has_written([])

    def test_disabled_account_by_sessionid_with_account_info(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=BLACKBOX_SESSIONID_DISABLED_STATUS,
            ),
        )

        rv = self.make_request_with_sessionid()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {u'status': u'error', u'errors': [u'account.disabled']},
            ),
        )

        eq_(self.env.blackbox._mock.request.call_count, 1)

        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')])

    def test_disabled_on_deletion_account_by_uid(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                enabled=False,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {u'status': u'error', u'errors': [u'account.disabled_on_deletion']},
            ),
        )

        eq_(self.env.blackbox._mock.request.call_count, 1)

        self.env.statbox.assert_has_written([])

    def test_disabled_on_deletion_account_by_sessionid_with_account_info(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=BLACKBOX_SESSIONID_DISABLED_STATUS,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )

        rv = self.make_request_with_sessionid()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {u'status': u'error', u'errors': [u'account.disabled_on_deletion']},
            ),
        )

        eq_(self.env.blackbox._mock.request.call_count, 1)

        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')])

    def test_account_invalid_type_error(self):
        for account_kwargs in (
            LITE_ACCOUNT_KWARGS,
            MAILISH_ACCOUNT_KWARGS,
            PDD_ACCOUNT_KWARGS,
            PHONISH_ACCOUNT_KWARGS,
            SOCIAL_ACCOUNT_KWARGS,
            SUPER_LITE_ACCOUNT_KWARGS,
        ):
            self.env.blackbox.set_blackbox_response_value(
                'userinfo',
                blackbox_userinfo_response(**account_kwargs),
            )

            rv = self.make_request()
            eq_(rv.status_code, 200, rv.data)
            eq_(
                json.loads(rv.data),
                merge_dicts(
                    self.base_submitter_response,
                    {u'status': u'error', u'errors': [u'account.invalid_type']},
                ),
            )

        self.env.statbox.assert_has_written([])

    def test_with_bound_confirmed_secure_phone(self):
        phone_args = build_phone_secured(
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER.e164,
        )
        phone_args['attributes']['password.encrypted'] = '1:testpassword'
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                **phone_args
            ),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {u'status': u'error', u'errors': [u'phone_secure.bound_and_confirmed']},
            ),
        )
        eq_(self.env.blackbox._mock.request.call_count, 1)

        self.env.statbox.assert_has_written([])

    def test_with_bound_not_confirmed_secure_phone(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                attributes={'password.encrypted': '1:testpassword'},
                **build_secure_phone_being_bound(
                    operation_id=TEST_OPERATION_ID,
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER.e164,
                )
            ),
        )

        rv = self.make_request()

        self.assert_ok_response(rv, **self.ok_response())

        eq_(self.env.blackbox._mock.request.call_count, 1)
        eq_(len(self.env.yasms.requests), 1)

        self.assert_statbox_ok()

    def test_with_bound_not_confirmed_not_secure_phone(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                attributes={'password.encrypted': '1:testpassword'},
                **build_phone_being_bound(
                    operation_id=TEST_OPERATION_ID,
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER.e164,
                )
            ),
        )

        rv = self.make_request()

        self.assert_ok_response(rv, **self.ok_response())

        eq_(self.env.blackbox._mock.request.call_count, 1)
        eq_(len(self.env.yasms.requests), 1)

        self.assert_statbox_ok()

    def test_with_alias_on_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                aliases={
                    'portal': 'test',
                    'phonenumber': TEST_PHONE_NUMBER.digital,
                },
                attributes={'password.encrypted': '1:testpassword'},
            ),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {u'status': u'error', u'errors': [u'phone_alias.exist']},
            ),
        )

        self.env.statbox.assert_has_written([])

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

        self.env.statbox.assert_has_written([])

    def test_force_change_password_send_sms_only_on_secure_phone_number_and_hint_not_passed(self):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
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

        self.env.statbox.assert_has_written([])

    def test_force_change_password_send_sms_only_on_secure_phone_number_and_hint_passed(self):
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
            **self.ok_response(
                track_id=self.track_id,
                number=TEST_NOT_EXIST_PHONE_NUMBER_DUMPED,
            )
        )

        requests = self.env.yasms.requests
        requests[0].assert_query_contains({
            'phone': TEST_NOT_EXIST_PHONE_NUMBER.e164,
            'from_uid': str(TEST_UID),
            'identity': 'confirm_and_bind_secure_and_aliasify',
        })

    def test_force_change_password_send_sms_only_on_secure_phone_number_and_short_form_passed(self):
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
            **self.ok_response(
                track_id=self.track_id,
                number=TEST_NOT_EXIST_PHONE_NUMBER_DUMPED,
            )
        )

        requests = self.env.yasms.requests
        requests[0].assert_query_contains({
            'phone': TEST_NOT_EXIST_PHONE_NUMBER.e164,
            'from_uid': str(TEST_UID),
            'identity': 'confirm_and_bind_secure_and_aliasify',
        })

    def test_enable_alias_as_email(self):
        rv = self.make_request(self.query_params(enable_alias_as_email='1'))

        self.assert_ok_response(rv, **self.ok_response())

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)

    def test_disable_alias_as_email(self):
        rv = self.make_request(self.query_params(enable_alias_as_email='0'))

        self.assert_ok_response(rv, **self.ok_response())

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track, enable_phonenumber_alias_as_email=False)

    def test_passwordless__enable_alias_as_email(self):
        self.setup_account(
            alias_type='social',
            login=TEST_SOCIAL_LOGIN1,
            crypt_password=None,
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {u'status': u'error', u'errors': [u'account.invalid_type']},
            ),
        )

    def test_passwordless__disable_alias_as_email(self):
        self.setup_account(
            alias_type='social',
            login=TEST_SOCIAL_LOGIN1,
            crypt_password=None,
        )

        rv = self.make_request(self.query_params(enable_alias_as_email='0'))

        self.assert_ok_response(
            rv,
            **self.ok_response(
                is_password_required=False,
            )
        )

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track, enable_phonenumber_alias_as_email=False)

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
    SMS_VALIDATION_MAX_CHECKS_COUNT=5,
    YASMS_URL='http://localhost/',
)
class TestConfirmAndBindSecureAndAliasifyCommitter(
    BaseConfirmCommitterTestCase,
    ConfirmCommitterTestMixin,
    EmailTestMixin,
    ConfirmCommitterSentCodeTestMixin,
    ConfirmCommitterLocalPhonenumberTestMixin,
):
    track_state = CONFIRM_AND_BIND_SECURE_AND_ALIASIFY_STATE
    url = '/1/bundle/phone/confirm_and_bind_secure_and_aliasify/commit/?consumer=dev'

    def setUp(self):
        super(TestConfirmAndBindSecureAndAliasifyCommitter, self).setUp()
        self.setup_account(setup_db=False)

    def setup_account(
        self,
        alias_type='portal',
        crypt_password=TEST_PASSWORD_HASH1,
        login='test',
        uid=TEST_UID,
        aliases=None,
        setup_db=True,
    ):
        userinfo_kwargs = dict(
            aliases=aliases or {alias_type: login},
            crypt_password=crypt_password,
            login=login,
            uid=uid,
            emails=[
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )
        userinfo_response = blackbox_userinfo_response(**userinfo_kwargs)
        self.env.blackbox.set_response_value('userinfo', userinfo_response)

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        if setup_db:
            self.env.db.serialize(userinfo_response)

    def setup_statbox_templates(self):
        super(TestConfirmAndBindSecureAndAliasifyCommitter, self).setup_statbox_templates()

        self.env.statbox.bind_entry(
            'phone_confirmed',
            _inherit_from=['phone_confirmed', 'local_base'],
            code_checks_count='0',
        )
        self.env.statbox.bind_entry(
            'secure_phone_bound',
            _inherit_from=['secure_phone_bound', 'local_base'],
        )

    def query_params(self, **kwargs):
        base_params = {
            'code': self.confirmation_code,
            'password': 'testpassword',
            'track_id': self.track_id,
        }

        return merge_dicts(base_params, kwargs)

    def assert_statbox_ok(self):
        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend([
            self.env.statbox.entry('enter_code'),
            self.env.statbox.entry('secure_bind_operation_created'),
            self.env.statbox.entry('phonenumber_alias_given_out', login='test'),
            self.env.statbox.entry('phonenumber_alias_added'),
            self.env.statbox.entry('account_phones_secure'),
            self.env.statbox.entry('local_account_modification', action='confirm_and_bind_secure_and_aliasify'),
            self.env.statbox.entry('phonenumber_alias_subscription_added', ip=TEST_USER_IP),
            self.env.statbox.entry('phonenumber_alias_search_enabled', ip=TEST_USER_IP),
            self.env.statbox.entry('phone_confirmed'),
            self.env.statbox.entry('secure_phone_bound'),
            self.env.statbox.entry('success'),
        ])
        self.env.statbox.assert_has_written(entries)

    def setup_track_for_commit(
        self,
        exclude=None,
        _defaults=None,
        **kwargs
    ):
        defaults = dict(
            enable_phonenumber_alias_as_email='1',
        )
        if _defaults:
            defaults.update(_defaults)

        super(TestConfirmAndBindSecureAndAliasifyCommitter, self).setup_track_for_commit(
            exclude=exclude,
            _defaults=defaults,
            **kwargs
        )

    def assert_account_has_phonenumber_alias(self, enable_search=True):
        assert_account_has_phonenumber_alias(
            db_faker=self.env.db,
            uid=TEST_UID,
            alias=TEST_PHONE_NUMBER.digital,
            enable_search=enable_search,
        )

    def test_ok(self):
        self.env.db.check_missing('aliases', 'phonenumber', uid=TEST_UID, db='passportdbcentral')

        self.setup_track_for_commit()

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(json.loads(rv.data), self.base_response)

        if 'Session_id' in self.build_headers().get('Ya-Client-Cookie', ''):
            eq_(len(self.env.blackbox.get_requests_by_method('sessionid')), 1)
            eq_(len(self.env.blackbox.get_requests_by_method('userinfo')), 1)
        else:
            eq_(len(self.env.blackbox.get_requests_by_method('userinfo')), 2)
        eq_(len(self.env.blackbox.get_requests_by_method('phone_bindings')), 2)

        self.env.db.check('aliases', 'phonenumber', TEST_PHONE_NUMBER.digital, uid=TEST_UID, db='passportdbcentral')
        self.assert_account_has_phonenumber_alias()
        assert_secure_phone_bound.check_db(
            db_faker=self.env.db,
            uid=TEST_UID,
            phone_attributes={'id': TEST_PHONE_ID1},
        )
        self.env.db.check_missing(
            'phone_operations',
            phone_id=TEST_PHONE_ID1,
            uid=TEST_UID,
            db='passportdbshard1',
        )

        self.env.event_logger.assert_contains(
            event_lines_secure_bind_operation_created(
                uid=TEST_UID,
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER,
                operation_id=TEST_OPERATION_ID,
                operation_ttl=timedelta(seconds=60),
            ) +
            event_lines_secure_phone_bound(
                action='confirm_and_bind_secure_and_aliasify',
                uid=TEST_UID,
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER,
            ),
        )

        track = self.track_manager.read(self.track_id)

        ok_(track.phone_confirmation_is_confirmed)
        eq_(track.phone_confirmation_confirms_count.get(), 1)
        ok_(not track.phone_confirmation_confirms_count_limit_reached)
        eq_(track.phone_confirmation_first_checked, TimeNow())
        eq_(track.phone_confirmation_last_checked, TimeNow())

        self.assert_statbox_ok()

    def test_ok_with_delete_alias(self):
        userinfo2 = blackbox_userinfo_response(
            **deep_merge(
                dict(
                    uid=2,
                    login=TEST_OTHER_LOGIN,
                    aliases={'portal': TEST_OTHER_LOGIN},
                ),
                build_phone_secured(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER.e164,
                    phone_confirmed=DatetimeNow(),
                    is_alias=True,
                ),
            )
        )
        if 'Session_id' in self.build_headers().get('Ya-Client-Cookie', ''):
            self.env.blackbox.set_response_side_effect('userinfo', [userinfo2])
        else:
            userinfo1 = dict(
                aliases={'portal': 'test'},
                crypt_password=TEST_PASSWORD_HASH1,
                login='test',
                uid=TEST_UID,
                emails=[
                    self.create_native_email(TEST_LOGIN, 'yandex.ru'),
                ],
            )
            userinfo1_response = blackbox_userinfo_response(**userinfo1)
            self.env.blackbox.set_response_side_effect('userinfo', [userinfo1_response, userinfo2])
        self.env.db.serialize(userinfo2)

        self.env.db.check_missing('aliases', 'phonenumber', uid=TEST_UID, db='passportdbcentral')
        self.env.db.check('aliases', 'phonenumber', TEST_PHONE_NUMBER.digital, uid=2, db='passportdbcentral')

        self.setup_track_for_commit()

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(json.loads(rv.data), self.base_response)

        self.env.db.check_missing('aliases', 'phonenumber', uid=2, db='passportdbcentral')
        self.env.db.check('removed_aliases', 'phonenumber', TEST_PHONE_NUMBER.digital, uid=2, db='passportdbcentral')
        self.env.db.check('aliases', 'phonenumber', TEST_PHONE_NUMBER.digital, uid=TEST_UID, db='passportdbcentral')

        assert_secure_phone_bound.check_db(
            db_faker=self.env.db,
            uid=TEST_UID,
            phone_attributes={'id': TEST_PHONE_ID1},
        )
        self.env.db.check_missing(
            'phone_operations',
            phone_id=TEST_PHONE_ID1,
            uid=TEST_UID,
            db='passportdbshard1',
        )

        self.env.event_logger.assert_contains(
            event_lines_secure_bind_operation_created(
                uid=TEST_UID,
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER,
                operation_id=TEST_OPERATION_ID,
                operation_ttl=timedelta(seconds=60),
            ) +
            event_lines_secure_phone_bound(
                action='confirm_and_bind_secure_and_aliasify',
                uid=TEST_UID,
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER,
            ),
        )
        self.assert_account_history_parses_secure_phone_set(TEST_PHONE_NUMBER)

        track = self.track_manager.read(self.track_id)

        ok_(track.phone_confirmation_is_confirmed)
        eq_(track.phone_confirmation_confirms_count.get(), 1)
        ok_(not track.phone_confirmation_confirms_count_limit_reached)
        eq_(track.phone_confirmation_first_checked, TimeNow())
        eq_(track.phone_confirmation_last_checked, TimeNow())

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend(
            [
                self.env.statbox.entry('enter_code'),
                self.env.statbox.entry('secure_bind_operation_created'),
            ]
        )
        entries.extend(self.dealiasify_statbox_values())
        entries.extend(
            [
                self.env.statbox.entry('phonenumber_alias_given_out', login='test', is_owner_changed='1'),
                self.env.statbox.entry('phonenumber_alias_added'),
                self.env.statbox.entry('account_phones_secure'),
                self.env.statbox.entry('local_account_modification', action='confirm_and_bind_secure_and_aliasify'),
                self.env.statbox.entry('phonenumber_alias_subscription_added', ip=TEST_USER_IP),
                self.env.statbox.entry('phonenumber_alias_search_enabled', ip=TEST_USER_IP),
                self.env.statbox.entry('phone_confirmed'),
                self.env.statbox.entry('secure_phone_bound'),
                self.env.statbox.entry('success'),
            ]
        )

        self.env.statbox.assert_has_written(entries)

    def check_ok_with_delete_and_emails(self, submit_language=None):
        userinfo1 = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            attributes={'password.encrypted': '1:testpassword'},
            emails=[
                self.create_native_email('user1', 'yandex.ru'),
            ],
        )
        userinfo2 = deep_merge(
            dict(
                uid=2,
                login=TEST_OTHER_LOGIN,
                aliases={'portal': TEST_OTHER_LOGIN},
                emails=[
                    self.create_native_email('user2', 'yandex.ru'),
                    self.create_validated_external_email('user2', 'gmail.com'),
                ],
            ),
            build_phone_secured(
                phone_id=TEST_PHONE_ID2,
                phone_number=TEST_PHONE_NUMBER.e164,
                phone_confirmed=DatetimeNow(),
                is_alias=True,
            ),
        )

        if 'Session_id' in self.build_headers().get('Ya-Client-Cookie', ''):
            self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_multi_response(**userinfo1))
            self.env.blackbox.set_response_side_effect('userinfo', [blackbox_userinfo_response(**userinfo2)])
        else:
            self.env.blackbox.set_response_side_effect('userinfo', [
                blackbox_userinfo_response(**userinfo1),
                blackbox_userinfo_response(**userinfo2),
            ])
        self.env.db.serialize(blackbox_userinfo_response(**userinfo2))

        self.setup_track_for_commit()

        language = 'ru'
        if submit_language:
            with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
                track.display_language = submit_language
            language = submit_language

        rv = self.make_request()
        eq_(rv.status_code, 200, rv.data)
        eq_(json.loads(rv.data), self.base_response)

        eq_(len(self.env.mailer.messages), 4)
        assert_user_notified_about_alias_as_login_and_email_owner_changed(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address='user2@gmail.com',
            firstname='\u0414',
            login=TEST_OTHER_LOGIN,
            portal_email=TEST_OTHER_LOGIN + '@yandex.ru',
            phonenumber_alias=TEST_PHONE_NUMBER.digital,
        )
        assert_user_notified_about_alias_as_login_and_email_owner_changed(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address='user2@yandex.ru',
            firstname='\u0414',
            login=TEST_OTHER_LOGIN,
            portal_email=TEST_OTHER_LOGIN + '@yandex.ru',
            phonenumber_alias=TEST_PHONE_NUMBER.digital,
        )
        assert_user_notified_about_alias_as_login_and_email_enabled(
            mailer_faker=self.env.mailer,
            language=language,
            email_address='user1@yandex.ru',
            firstname='\u0414',
            login=TEST_LOGIN,
            portal_email=TEST_LOGIN + '@yandex.ru',
            phonenumber_alias=TEST_PHONE_NUMBER.digital,
        )
        assert_user_notified_about_secure_phone_bound(
            mailer_faker=self.env.mailer,
            language=language,
            email_address='user1@yandex.ru',
            firstname='\u0414',
            login=TEST_LOGIN,
        )

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend(
            [
                self.env.statbox.entry('enter_code'),
                self.env.statbox.entry('secure_bind_operation_created'),
            ],
        )
        entries.extend(self.dealiasify_statbox_values())
        entries.extend(
            [
                self.env.statbox.entry('phonenumber_alias_given_out', login=TEST_LOGIN, is_owner_changed='1'),
                self.env.statbox.entry('phonenumber_alias_added'),
                self.env.statbox.entry('account_phones_secure'),
                self.env.statbox.entry(
                    'local_account_modification',
                    action='confirm_and_bind_secure_and_aliasify',
                    login=TEST_LOGIN,
                ),
                self.env.statbox.entry('phonenumber_alias_subscription_added', ip=TEST_USER_IP),
                self.env.statbox.entry('phonenumber_alias_search_enabled', ip=TEST_USER_IP),
                self.env.statbox.entry('phone_confirmed'),
                self.env.statbox.entry('secure_phone_bound'),
                self.env.statbox.entry('success'),
            ],
        )

        self.env.statbox.assert_has_written(entries)

    def test_ok_with_delete_and_emails(self):
        self.check_ok_with_delete_and_emails()

    def test_ok_with_delete_and_emails_in_custom_display_language(self):
        self.check_ok_with_delete_and_emails(submit_language='en')

    def test_with_bound_confirmed_secure_phone(self):
        self.setup_track_for_commit()
        phone_args = build_phone_secured(
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER.e164,
        )
        phone_args['attributes']['password.encrypted'] = '1:testpassword'
        userinfo = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            **phone_args
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**userinfo),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**userinfo),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'phone_secure.bound_and_confirmed']},
            ),
        )
        if 'Session_id' in self.build_headers().get('Ya-Client-Cookie', ''):
            eq_(len(self.env.blackbox.get_requests_by_method('sessionid')), 1)
        else:
            eq_(len(self.env.blackbox.get_requests_by_method('userinfo')), 1)


        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(self.env.statbox.entry('enter_code'))
        self.env.statbox.assert_has_written(entries)

    def test_with_alias_on_account(self):
        self.setup_track_for_commit()
        phone_args = build_phone_secured(
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER.e164,
        )
        phone_args['attributes']['password.encrypted'] = '1:testpassword'
        userinfo = dict(
            uid=TEST_UID,
            aliases={
                'portal': TEST_LOGIN,
                'phonenumber': TEST_PHONE_NUMBER.digital,
            },
            **phone_args
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**userinfo),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**userinfo),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'phone_alias.exist']},
            ),
        )

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(self.env.statbox.entry('enter_code'))

        self.env.statbox.assert_has_written(entries)

    def test_already_confirmed(self):
        self.setup_track_for_commit(phone_confirmation_is_confirmed='1')

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), self.base_response)

        if 'Session_id' in self.build_headers().get('Ya-Client-Cookie', ''):
            eq_(len(self.env.blackbox.get_requests_by_method('sessionid')), 1)
            eq_(len(self.env.blackbox.get_requests_by_method('userinfo')), 1)
        else:
            eq_(len(self.env.blackbox.get_requests_by_method('userinfo')), 2)
        eq_(len(self.env.blackbox.get_requests_by_method('phone_bindings')), 2)

        self.env.db.check('aliases', 'phonenumber', TEST_PHONE_NUMBER.digital, uid=TEST_UID, db='passportdbcentral')
        eq_(self.env.db.query_count('passportdbshard1'), 10)

        self.assert_statbox_ok()

    def test_account_not_found(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            json.dumps({'users': [{'id': '', 'uid': {}}]}),
        )

        self.setup_track_for_commit()

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'account.not_found']},
            ),
        )

        eq_(len(self.env.blackbox.get_requests_by_method('userinfo')), 1)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        self.env.statbox.assert_has_written([])

    def test_disabled_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                enabled=False,
                uid=TEST_UID,
            ),
        )
        sessionid_response = blackbox_sessionid_multi_response(
            uid=TEST_UID,
            enabled=False,
            status=BLACKBOX_SESSIONID_DISABLED_STATUS,
        )
        self.env.blackbox.set_response_value('sessionid', sessionid_response)
        self.setup_track_for_commit()

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'account.disabled']},
            ),
        )
        if 'Session_id' in self.build_headers().get('Ya-Client-Cookie', ''):
            eq_(len(self.env.blackbox.get_requests_by_method('sessionid')), 1)
        else:
            eq_(len(self.env.blackbox.get_requests_by_method('userinfo')), 1)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))

        self.env.statbox.assert_has_written(entries)

    def test_disabled_on_deletion_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                enabled=False,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        sessionid_response = blackbox_sessionid_multi_response(uid=TEST_UID, enabled=False, status=BLACKBOX_SESSIONID_DISABLED_STATUS)
        self.env.blackbox.set_response_value('sessionid', sessionid_response)

        self.setup_track_for_commit()

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'account.disabled']},
            ),
        )
        if 'Session_id' in self.build_headers().get('Ya-Client-Cookie', ''):
            eq_(len(self.env.blackbox.get_requests_by_method('sessionid')), 1)
        else:
            eq_(len(self.env.blackbox.get_requests_by_method('userinfo')), 1)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))

        self.env.statbox.assert_has_written(entries)

    def test_dberror_on_delete_alias(self):
        blackbox_response_with_alias = blackbox_userinfo_response(
            uid='2',
            login=TEST_OTHER_LOGIN,
            aliases={
                'portal': TEST_OTHER_LOGIN,
                'phonenumber': TEST_PHONE_NUMBER.digital,
            },
            attributes={'account.enable_search_by_phone_alias': '1'},
        )
        self.env.db.serialize(blackbox_response_with_alias)

        self.env.db.check_missing('aliases', 'phonenumber', uid=TEST_UID, db='passportdbcentral')
        self.env.db.check('aliases', 'phonenumber', TEST_PHONE_NUMBER.digital, uid=2, db='passportdbcentral')

        self.setup_track_for_commit()

        self.env.db.set_side_effect_for_db('passportdbcentral', DBError)
        self.env.db.set_side_effect_for_db('passportdbshard1', DBError)

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {
                    'status': 'error',
                    'errors': ['backend.database_failed'],
                },
            ),
        )

        if 'Session_id' in self.build_headers().get('Ya-Client-Cookie', ''):
            eq_(len(self.env.blackbox.get_requests_by_method('sessionid')), 1)
            eq_(len(self.env.blackbox.get_requests_by_method('userinfo')), 1)
        else:
            eq_(len(self.env.blackbox.get_requests_by_method('userinfo')), 2)
        eq_(len(self.env.blackbox.get_requests_by_method('phone_bindings')), 1)

        eq_(self.env.db.query_count('passportdbcentral'), 1)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(self.env.statbox.entry('enter_code'))

        self.env.statbox.assert_has_written(entries)

    def test_dberror_on_create_alias(self):
        self.env.db.check_missing('aliases', 'phonenumber', uid=TEST_UID, db='passportdbcentral')

        self.setup_track_for_commit()

        self.env.db.set_side_effect_for_db('passportdbcentral', DBError)
        self.env.db.set_side_effect_for_db('passportdbshard1', DBError)

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {
                    'status': 'error',
                    'errors': ['backend.database_failed'],
                },
            ),
        )

        eq_(self.env.db.query_count('passportdbcentral'), 1)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(self.env.statbox.entry('enter_code'))
        self.env.statbox.assert_has_written(entries)

    def test_account_invalid_type_error(self):
        for account_kwargs in (
            PDD_ACCOUNT_KWARGS,
            LITE_ACCOUNT_KWARGS,
            PHONISH_ACCOUNT_KWARGS,
            SOCIAL_ACCOUNT_KWARGS,
            MAILISH_ACCOUNT_KWARGS,
        ):
            self.setup_track_for_commit(uid=account_kwargs['uid'])
            self.setup_account(**account_kwargs)

            rv = self.make_request()
            eq_(rv.status_code, 200, rv.data)
            eq_(
                json.loads(rv.data),
                merge_dicts(
                    self.base_response,
                    {u'status': u'error', u'errors': [u'account.invalid_type']},
                ),
            )

    def test_alias_as_email_disabled(self):
        self.setup_track_for_commit(enable_phonenumber_alias_as_email='0')

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(json.loads(rv.data), self.base_response)

        self.assert_account_has_phonenumber_alias(enable_search=False)

    def test_passwordless__alias_as_email_enabled(self):
        self.setup_account(
            alias_type='social',
            login=TEST_SOCIAL_LOGIN1,
            crypt_password=None,
        )
        self.setup_track_for_commit()

        rv = self.make_request(self.query_params(password=None))

        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                dict(
                    status='error',
                    errors=['account.invalid_type'],
                ),
            ),
        )

    def test_passwordless__alias_as_email_disabled(self):
        self.setup_account(
            alias_type='social',
            login=TEST_SOCIAL_LOGIN1,
            crypt_password=None,
        )
        self.setup_track_for_commit(enable_phonenumber_alias_as_email='0')

        rv = self.make_request(self.query_params(password=None))

        eq_(rv.status_code, 200, rv.data)
        eq_(json.loads(rv.data), self.base_response)

        self.assert_account_has_phonenumber_alias(enable_search=False)


class TestConfirmAndBindSecureAndAliasifySubmitterV2(TestConfirmAndBindSecureAndAliasifySubmitter):
    url = '/2/bundle/phone/confirm_and_bind_secure_and_aliasify/submit/?consumer=dev'

    def make_request_with_sessionid(self):
        return self.make_request(
            data=self.query_params(exclude=['uid']),
            headers=self.build_headers(HEADERS_WITH_SESSIONID),
        )


class TestConfirmAndBindSecureAndAliasifyCommitterV2(TestConfirmAndBindSecureAndAliasifyCommitter):
    url = '/2/bundle/phone/confirm_and_bind_secure_and_aliasify/commit/?consumer=dev'
    with_check_cookies = True

    def setup_account(
        self,
        alias_type='portal',
        crypt_password=TEST_PASSWORD_HASH1,
        login='test',
        uid=TEST_UID,
        aliases=None,
        setup_db=True,
    ):
        account_kwargs = dict(
            aliases=aliases or {alias_type: login},
            crypt_password=crypt_password,
            login=login,
            uid=uid,
            emails=[
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )

        sessionid_response = blackbox_sessionid_multi_response(age=100500, **account_kwargs)
        self.env.blackbox.set_response_value('sessionid', sessionid_response)
        self.env.blackbox.set_response_value('userinfo', blackbox_userinfo_response(**account_kwargs))

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        if setup_db:
            userinfo_response = blackbox_userinfo_response(**account_kwargs)
            self.env.db.serialize(userinfo_response)

    def build_headers(self, headers=None):
        return super(TestConfirmAndBindSecureAndAliasifyCommitterV2, self).build_headers(
            merge_dicts(HEADERS_WITH_SESSIONID, headers or {}),
        )

    @skip('В sessionId методе нет такого ответа')
    def test_account_not_found(self):
        pass
