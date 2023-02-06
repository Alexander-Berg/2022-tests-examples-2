# -*- coding: utf-8 -*-

from datetime import datetime
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.views.bundle.phone.controllers import CONFIRM_AND_BIND_SECURE_STATE
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
from passport.backend.core.models.phones.faker import (
    assert_secure_phone_bound,
    build_phone_being_bound,
    build_phone_bound,
    build_phone_secured,
    event_lines_phone_secured,
    event_lines_securify_operation_deleted,
)
from passport.backend.core.test.consts import TEST_SOCIAL_LOGIN1
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
    LITE_ACCOUNT_KWARGS,
    MAILISH_ACCOUNT_KWARGS,
    PDD_ACCOUNT_KWARGS,
    PHONISH_ACCOUNT_KWARGS,
    TEST_DOMAIN,
    TEST_EMAIL,
    TEST_FIRSTNAME,
    TEST_LOGIN,
    TEST_NOT_EXIST_PHONE_NUMBER,
    TEST_NOT_EXIST_PHONE_NUMBER_DUMPED,
    TEST_OPERATION_ID,
    TEST_PDD_USER_UID,
    TEST_PHONE_ID1,
    TEST_PHONE_NUMBER,
    TEST_SESSION_ID,
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
class TestConfirmAndBindSecureSubmitter(
        BaseConfirmSubmitterTestCase,
        ConfirmSubmitterAccountTestMixin,
        ConfirmSubmitterSendSmsTestMixin,
        ConfirmSubmitterSpecificTestMixin,
        ConfirmSubmitterLocalPhonenumberMixin,
        ConfirmSubmitterChangePasswordNewSecureNumberTestMixin,
        ConfirmSubmitterAlreadyConfirmedPhoneWithNewPhoneTestMixin):

    track_state = CONFIRM_AND_BIND_SECURE_STATE
    url = '/1/bundle/phone/confirm_and_bind_secure/submit/?consumer=dev'
    with_antifraud_score = True

    def setUp(self):
        super(TestConfirmAndBindSecureSubmitter, self).setUp()
        self.create_blackbox_userinfo_response_with_phone()
        self.additional_ok_response_params = dict(is_password_required=False)

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

    def create_blackbox_userinfo_response_with_phone(self, account_args=None, phone_args=None):
        if not account_args:
            account_args = dict(
                uid=TEST_UID,
                attributes={'password.encrypted': '1:testpassword'},
            )

        if not phone_args:
            phone_args = build_phone_bound(
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER.e164,
            )

        userinfo_args = deep_merge(account_args, phone_args)

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**userinfo_args),
        )

    def create_blackbox_sessionid_response(self, **kwargs):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**kwargs),
        )

    def assert_blackbox_is_called(self, number=1):
        eq_(self.env.blackbox._mock.request.call_count, number)

    def assert_code_generator_is_called(self):
        eq_(self._code_generator_faker.call_count, 1)

    def assert_yasms_sendsms_is_called(self, number=TEST_PHONE_NUMBER.e164, uid=TEST_UID):
        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        requests[0].assert_url_starts_with('http://localhost/sendsms')
        requests[0].assert_query_contains({
            'phone': number,
            'text': self.sms_text,
            'identity': 'confirm_and_bind_secure',
            'from_uid': str(uid),
            'caller': 'dev',
        })
        requests[0].assert_post_data_contains({
            'text_template_params': self.sms_text_template_params,
        })

    def assert_response_is_ok(self, rv, **kwargs):
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_send_code_response,
                self.additional_ok_response_params,
                kwargs,
            ),
        )

    def assert_response_is_error(self, rv, error, **kwargs):
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_submitter_response,
                {u'status': u'error', u'errors': [error]},
                kwargs,
            ),
        )

    def assert_track_is_ok(self, uid=TEST_UID):
        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)
        ok_(track.country is None)
        eq_(track.uid, str(uid))

    def assert_statbox_is_ok(self, uid=TEST_UID, with_check_cookies=False):
        kwargs = dict(uid=str(uid))
        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend([
            self.env.statbox.entry('antifraud_score_allow', uid=str(uid)),
            self.env.statbox.entry('send_code', **kwargs),
            self.env.statbox.entry('success', **kwargs),
        ])
        self.env.statbox.assert_has_written(entries)

    def assert_statbox_is_empty(self):
        self.env.statbox.assert_has_written([])

    def assert_statbox_check_cookies(self, check_cookies_count=1):
        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')] * check_cookies_count)

    def test_ok(self):
        rv = self.make_request()

        self.assert_response_is_ok(rv)
        self.assert_blackbox_is_called()
        self.assert_code_generator_is_called()
        self.assert_yasms_sendsms_is_called()
        self.assert_track_is_ok()
        self.assert_statbox_is_ok()

    def test_2fa_no_password_ok(self):
        self.create_blackbox_userinfo_response_with_phone(dict(
            uid=TEST_UID,
            attributes={
                'account.2fa_on': '1',
                'password.encrypted': '1:testpassword',
            },
        ))

        rv = self.make_request()

        self.assert_response_is_ok(rv)
        self.assert_blackbox_is_called()
        self.assert_code_generator_is_called()
        self.assert_yasms_sendsms_is_called()
        self.assert_track_is_ok()
        self.assert_statbox_is_ok()

    def test_ok_with_lite_account(self):
        kwargs = dict(LITE_ACCOUNT_KWARGS)
        kwargs['attributes'] = {'password.encrypted': '1:testpassword'}
        self.create_blackbox_userinfo_response_with_phone(account_args=kwargs)

        rv = self.make_request()

        self.assert_response_is_ok(rv)
        self.assert_blackbox_is_called()
        self.assert_code_generator_is_called()
        self.assert_yasms_sendsms_is_called()
        self.assert_track_is_ok()
        self.assert_statbox_is_ok()

    def test_ok_with_pdd_account(self):
        kwargs = dict(PDD_ACCOUNT_KWARGS)
        kwargs['domain'] = TEST_DOMAIN
        # Полноценный ПДД-пользователь - есть соглашение с pdd-EULA
        # и есть персональная информация + КВ/КО
        kwargs['subscribed_to'] = [102]
        kwargs['dbfields'] = {
            'userinfo_safe.hintq.uid': u'99:вопрос',
            'userinfo_safe.hinta.uid': u'ответ',
        }
        kwargs['attributes'] = {'password.encrypted': '1:testpassword'}
        self.create_blackbox_userinfo_response_with_phone(account_args=kwargs)

        rv = self.make_request()

        self.assert_response_is_ok(rv)
        self.assert_blackbox_is_called()
        self.assert_code_generator_is_called()
        self.assert_yasms_sendsms_is_called(uid=TEST_PDD_USER_UID)
        self.assert_track_is_ok(uid=TEST_PDD_USER_UID)
        self.assert_statbox_is_ok(uid=TEST_PDD_USER_UID)

    def test_ok_with_passwordless_account(self):
        account_kwargs = dict(
            aliases=dict(social=TEST_SOCIAL_LOGIN1),
            crypt_password=None,
            login=TEST_SOCIAL_LOGIN1,
        )
        self.create_blackbox_userinfo_response_with_phone(account_args=account_kwargs)

        rv = self.make_request()

        self.assert_response_is_ok(rv, is_password_required=False)
        self.assert_yasms_sendsms_is_called()
        self.assert_track_is_ok()

    def test_ok_by_sessionid(self):
        self.create_blackbox_sessionid_response(
            uid=TEST_UID,
            login_id='login-id',
            attributes={'password.encrypted': '1:testpassword'},
        )

        rv = self.make_request(self.query_params(sessionid=TEST_SESSION_ID, exclude=['uid']))

        self.assert_response_is_ok(rv)
        self.assert_blackbox_is_called()
        self.assert_code_generator_is_called()
        self.assert_yasms_sendsms_is_called()
        self.assert_track_is_ok()
        self.assert_statbox_is_ok(with_check_cookies=True)
        self.assert_antifraud_score_called(login_id='login-id')

    def test_invalid_sessionid(self):
        for status in [BLACKBOX_SESSIONID_EXPIRED_STATUS,
                       BLACKBOX_SESSIONID_NOAUTH_STATUS,
                       BLACKBOX_SESSIONID_INVALID_STATUS]:
            self.create_blackbox_sessionid_response(
                status=status,
            )

            rv = self.make_request(
                self.query_params(sessionid=TEST_SESSION_ID, exclude=['uid']),
            )

            self.assert_response_is_error(rv, u'sessionid.invalid')

        self.assert_blackbox_is_called(3)
        self.assert_statbox_check_cookies(3)

    def test_disabled_account_by_uid(self):
        self.create_blackbox_userinfo_response_with_phone(dict(
            uid=TEST_UID,
            enabled=False,
        ))

        rv = self.make_request()

        self.assert_response_is_error(rv, u'account.disabled')
        self.assert_blackbox_is_called()
        self.assert_statbox_is_empty()

    def test_disabled_on_deletion_account_by_uid(self):
        self.create_blackbox_userinfo_response_with_phone(dict(
            uid=TEST_UID,
            enabled=False,
            attributes={
                'account.is_disabled': '2',
            },
        ))

        rv = self.make_request()

        self.assert_response_is_error(rv, u'account.disabled_on_deletion')
        self.assert_blackbox_is_called()
        self.assert_statbox_is_empty()

    def test_disabled_account_by_sessionid(self):
        self.create_blackbox_sessionid_response(
            status=BLACKBOX_SESSIONID_DISABLED_STATUS,
        )

        rv = self.make_request(
            self.query_params(sessionid=TEST_SESSION_ID, exclude=['uid']),
        )

        self.assert_response_is_error(rv, u'account.disabled')
        self.assert_blackbox_is_called()
        self.assert_statbox_check_cookies()

    def test_disabled_on_deletion_account_by_sessionid(self):
        self.create_blackbox_sessionid_response(
            status=BLACKBOX_SESSIONID_DISABLED_STATUS,
            attributes={
                'account.is_disabled': '2',
            },
        )

        rv = self.make_request(
            self.query_params(sessionid=TEST_SESSION_ID, exclude=['uid']),
        )

        self.assert_response_is_error(rv, u'account.disabled_on_deletion')
        self.assert_blackbox_is_called()
        self.assert_statbox_check_cookies()

    def test_account_invalid_type_error(self):
        for account_kwargs in (
            PHONISH_ACCOUNT_KWARGS,
            MAILISH_ACCOUNT_KWARGS,
        ):
            self.create_blackbox_userinfo_response_with_phone(account_kwargs)

            rv = self.make_request()

        self.assert_response_is_error(rv, u'account.invalid_type')
        self.assert_blackbox_is_called(2)
        self.assert_statbox_is_empty()

    def test_with_bound_confirmed_secure_phone(self):
        self.create_blackbox_userinfo_response_with_phone(
            phone_args=build_phone_secured(
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER.e164,
            ),
        )

        rv = self.make_request()

        self.assert_response_is_error(rv, u'phone_secure.bound_and_confirmed')
        self.assert_blackbox_is_called()
        self.assert_statbox_is_empty()

    def test_with_bound_not_confirmed_not_secure_phone(self):
        self.create_blackbox_userinfo_response_with_phone(
            phone_args=build_phone_being_bound(
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER.e164,
                operation_id=TEST_OPERATION_ID,
            ),
        )

        rv = self.make_request()

        self.assert_response_is_ok(rv)
        self.assert_blackbox_is_called()
        self.assert_code_generator_is_called()
        self.assert_yasms_sendsms_is_called()
        self.assert_track_is_ok()
        self.assert_statbox_is_ok()

    def test_change_password_send_sms_only_on_secure_phone_number(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_password_change = True
            track.has_secure_phone_number = True
            track.secure_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request(
            self.query_params(number=TEST_NOT_EXIST_PHONE_NUMBER.e164),
        )

        self.assert_response_is_error(
            rv,
            u'number.invalid',
            number=TEST_NOT_EXIST_PHONE_NUMBER_DUMPED,
            global_sms_id=self.env.yasms_fake_global_sms_id_mock.return_value,
        )
        self.assert_statbox_is_empty()

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

        self.assert_response_is_error(
            rv,
            u'number.invalid',
            number=TEST_NOT_EXIST_PHONE_NUMBER_DUMPED,
            track_id=self.track_id,
            global_sms_id=self.env.yasms_fake_global_sms_id_mock.return_value,
        )
        self.assert_statbox_is_empty()

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

        self.assert_response_is_ok(
            rv,
            number=TEST_NOT_EXIST_PHONE_NUMBER_DUMPED,
            track_id=self.track_id,
        )

        self.assert_yasms_sendsms_is_called(number=TEST_NOT_EXIST_PHONE_NUMBER.e164)

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

        self.assert_response_is_ok(
            rv,
            number=TEST_NOT_EXIST_PHONE_NUMBER_DUMPED,
            track_id=self.track_id,
        )

        self.assert_yasms_sendsms_is_called(number=TEST_NOT_EXIST_PHONE_NUMBER.e164)

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
class TestConfirmAndBindSecureCommitter(BaseConfirmCommitterTestCase,
                                        ConfirmCommitterTestMixin,
                                        ConfirmCommitterSentCodeTestMixin,
                                        ConfirmCommitterLocalPhonenumberTestMixin):

    track_state = CONFIRM_AND_BIND_SECURE_STATE
    url = '/1/bundle/phone/confirm_and_bind_secure/commit/?consumer=dev'

    def setUp(self):
        super(TestConfirmAndBindSecureCommitter, self).setUp()
        self.create_blackbox_userinfo_response_with_phone(add_to_db=True)
        self.env.statbox.bind_entry(
            'phone_confirmed',
            _inherit_from=['phone_confirmed', 'local_base'],
            code_checks_count='0',
        )
        self.env.statbox.bind_entry(
            'phone_secured',
            _inherit_from=['phone_secured', 'local_base'],
        )

    def build_account_args(self):
        return dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            firstname=TEST_FIRSTNAME,
            attributes={'password.encrypted': '1:testpassword'},
            emails=[
                self.env.email_toolkit.create_native_email(
                    login=TEST_EMAIL.split(u'@')[0],
                    domain=TEST_EMAIL.split(u'@')[1],
                ),
            ],
        )

    def build_phone_args(self):
        return build_phone_bound(
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER.e164,
        )

    def create_blackbox_userinfo_response_with_phone(self, account_args=None, phone_args=None, add_to_db=False):
        account_args = account_args or self.build_account_args()
        phone_args = phone_args or self.build_phone_args()

        args = deep_merge(account_args, phone_args)

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**args),
        )
        if add_to_db:
            self.env.db.serialize(blackbox_userinfo_response(**args))

    def create_blackbox_phone_bindings_response(self, not_empty=True):
        if not_empty:
            phone_bindings = [
                dict(
                    bound=datetime.now(),
                    flags=0,
                    type='current',
                    number=TEST_PHONE_NUMBER.e164,
                    phone_id=TEST_PHONE_ID1,
                    uid=TEST_UID,
                ),
            ]
        else:
            phone_bindings = []

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response(phone_bindings),
        )

    def assert_response_is_ok(self, rv):
        eq_(rv.status_code, 200, rv.data)
        eq_(json.loads(rv.data), self.base_response)

    def assert_response_is_error(self, rv, error, **kwargs):
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [error]},
                kwargs,
            ),
        )

    def assert_blackbox_is_called(self, number=1):
        eq_(self.env.blackbox._mock.request.call_count, number)

    def assert_phone_is_securified(self, uid=TEST_UID, is_pdd=False):
        kwargs = dict()
        if is_pdd:
            kwargs['shard_db'] = u'passportdbshard2'
        assert_secure_phone_bound.check_db(
            self.env.db,
            uid,
            {'id': TEST_PHONE_ID1, 'secured': DatetimeNow(), 'confirmed': DatetimeNow()},
            **kwargs
        )

    def assert_historydb_ok(self, uid=TEST_UID):
        self.env.event_logger.assert_contains(
            event_lines_phone_secured(
                uid, TEST_PHONE_ID1, TEST_PHONE_NUMBER,
                action=u'confirm_and_bind_secure',
            ) +
            event_lines_securify_operation_deleted(
                uid=uid,
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER,
                operation_id=TEST_OPERATION_ID,
                action=u'confirm_and_bind_secure',
            ),
        )
        self.assert_account_history_parses_secure_phone_set(TEST_PHONE_NUMBER)

    def assert_track_is_ok(self, confirms_count=1):
        track = self.track_manager.read(self.track_id)
        ok_(track.phone_confirmation_is_confirmed)
        eq_(track.phone_confirmation_confirms_count.get(), confirms_count)
        ok_(not track.phone_confirmation_confirms_count_limit_reached)
        eq_(track.phone_confirmation_first_checked, TimeNow())
        eq_(track.phone_confirmation_last_checked, TimeNow())

    def assert_track_with_captcha_flags(self):
        track = self.track_manager.read(self.track_id)
        ok_(not track.is_captcha_recognized)
        ok_(not track.is_captcha_required)

    def assert_statbox_is_ok(self, uid=TEST_UID):
        kwargs = dict(uid=str(uid))
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('enter_code', **kwargs),
            self.env.statbox.entry('securify_operation_created', **kwargs),
            self.env.statbox.entry('account_phones_secure', **kwargs),
            self.env.statbox.entry('phone_confirmed', **kwargs),
            self.env.statbox.entry('phone_secured', **kwargs),
            self.env.statbox.entry('success', **kwargs),
        ])

    def assert_statbox_is_empty(self):
        self.env.statbox.assert_has_written([])

    def assert_user_notified_about_secure_phone_bound(self):
        assert_user_notified_about_secure_phone_bound(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=TEST_EMAIL,
            firstname=TEST_FIRSTNAME,
            login=TEST_LOGIN,
        )

    def query_params(self, **kwargs):
        base_params = {
            'code': self.confirmation_code,
            'track_id': self.track_id,
        }

        return merge_dicts(base_params, kwargs)

    def test_ok(self):
        self.setup_track_for_commit()
        self.create_blackbox_userinfo_response_with_phone()

        rv = self.make_request()

        self.assert_response_is_ok(rv)
        self.assert_blackbox_is_called()
        self.assert_phone_is_securified()
        self.assert_historydb_ok()
        self.assert_track_is_ok()
        self.assert_statbox_is_ok()
        self.assert_user_notified_about_secure_phone_bound()

    def test_ok_with_lite_account(self):
        self.setup_track_for_commit()

        kwargs = dict(LITE_ACCOUNT_KWARGS)
        kwargs['attributes'] = {'password.encrypted': '1:testpassword'}
        self.create_blackbox_userinfo_response_with_phone(account_args=kwargs)

        rv = self.make_request()

        self.assert_response_is_ok(rv)
        self.assert_blackbox_is_called()
        self.assert_phone_is_securified()
        self.assert_historydb_ok()
        self.assert_track_is_ok()
        self.assert_statbox_is_ok()

    def test_ok_with_pdd_account(self):
        self.setup_track_for_commit(uid=TEST_PDD_USER_UID)

        kwargs = dict(PDD_ACCOUNT_KWARGS)
        kwargs['domain'] = TEST_DOMAIN
        # Полноценный ПДД-пользователь - есть соглашение с pdd-EULA
        # и есть персональная информация + КВ/КО
        kwargs['subscribed_to'] = [102]
        kwargs['dbfields'] = {
            'userinfo_safe.hintq.uid': u'99:вопрос',
            'userinfo_safe.hinta.uid': u'ответ',
        }
        kwargs['attributes'] = {'password.encrypted': '1:testpassword'}
        self.create_blackbox_userinfo_response_with_phone(account_args=kwargs, add_to_db=True)
        self.create_blackbox_phone_bindings_response()

        rv = self.make_request()

        self.assert_response_is_ok(rv)
        self.assert_blackbox_is_called()
        self.assert_phone_is_securified(uid=TEST_PDD_USER_UID, is_pdd=True)
        self.assert_historydb_ok(uid=TEST_PDD_USER_UID)
        self.assert_track_is_ok()
        self.assert_statbox_is_ok(uid=TEST_PDD_USER_UID)

    def test_passwordless_account(self):
        self.setup_track_for_commit()

        account_args = dict(
            login=TEST_SOCIAL_LOGIN1,
            aliases=dict(social=TEST_SOCIAL_LOGIN1),
            crypt_password=None,
        )
        self.create_blackbox_userinfo_response_with_phone(account_args=account_args)

        rv = self.make_request()

        self.assert_response_is_ok(rv)
        self.assert_phone_is_securified()
        self.assert_track_is_ok()

    def test_with_bound_confirmed_secure_phone(self):
        self.setup_track_for_commit()
        self.create_blackbox_userinfo_response_with_phone(
            phone_args=build_phone_secured(
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER.e164,
            ),
        )

        rv = self.make_request()

        self.assert_response_is_error(rv, u'phone_secure.bound_and_confirmed')
        self.assert_blackbox_is_called()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('enter_code'),
        ])

    def test_already_confirmed(self):
        self.setup_track_for_commit(
            phone_confirmation_is_confirmed='1',
            phone_confirmation_confirms_count='1',
        )
        self.create_blackbox_userinfo_response_with_phone()

        rv = self.make_request()

        self.assert_response_is_ok(rv)
        self.assert_blackbox_is_called()
        self.assert_phone_is_securified()
        self.assert_historydb_ok()
        self.assert_track_is_ok(confirms_count=2)
        self.assert_statbox_is_ok()

    def test_account_not_found(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            json.dumps({'users': [{'id': '', 'uid': {}}]}),
        )

        self.setup_track_for_commit()

        rv = self.make_request()

        self.assert_response_is_error(rv, u'account.not_found')
        self.assert_blackbox_is_called()
        self.assert_statbox_is_empty()

    def test_disabled_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                enabled=False,
                uid=TEST_UID,
            ),
        )

        self.setup_track_for_commit()

        rv = self.make_request()

        self.assert_response_is_error(rv, u'account.disabled')
        self.assert_blackbox_is_called()
        self.assert_statbox_is_empty()

    def test_disabled_on_deletion_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                enabled=False,
                uid=TEST_UID,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )

        self.setup_track_for_commit()

        rv = self.make_request()

        self.assert_response_is_error(rv, u'account.disabled')
        self.assert_blackbox_is_called()
        self.assert_statbox_is_empty()

    def test_account_invalid_type_error(self):
        for account_kwargs in (
            PHONISH_ACCOUNT_KWARGS,
            MAILISH_ACCOUNT_KWARGS,
        ):
            self.setup_track_for_commit()
            self.create_blackbox_userinfo_response_with_phone(account_kwargs)
            self.create_blackbox_phone_bindings_response()

            rv = self.make_request()

            self.assert_response_is_error(rv, u'account.invalid_type')
