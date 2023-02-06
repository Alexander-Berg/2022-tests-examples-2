# -*- coding: utf-8 -*-
import json

from nose.tools import (
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.views.bundle.constants import BIND_PHONE_OAUTH_SCOPE
from passport.backend.api.views.bundle.phone.controllers import (
    CONFIRM_AND_BIND_SECURE_STATE,
    CONFIRM_AND_BIND_STATE,
)
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders.base.faker.fake_builder import (
    assert_builder_data_equals,
    assert_builder_url_contains_params,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_phone_bindings_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.models.phones.faker import (
    assert_no_phone_in_db,
    assert_phone_marked,
    assert_secure_phone_bound,
    assert_simple_phone_being_securified,
    assert_simple_phone_bound,
    assert_simple_phone_replace_secure,
    build_account_from_session,
    build_mark_operation,
    build_phone_bound,
    build_phone_secured,
    build_securify_operation,
    build_simple_replaces_secure_operations,
    TEST_DATE,
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
    BaseConfirmAndBindCommitterMixin,
    BaseConfirmAndBindSubmitterMixin,
    BaseConfirmCommitterTestCase,
    BaseConfirmSubmitterTestCase,
    CommonSubmitterCommitterTestMixin,
    ConfirmCommitterLocalPhonenumberTestMixin,
    ConfirmCommitterSentCodeTestMixin,
    ConfirmCommitterTestMixin,
    ConfirmSubmitterAlreadyConfirmedPhoneWithNewPhoneTestMixin,
    ConfirmSubmitterChangePasswordNewSecureNumberTestMixin,
    ConfirmSubmitterLocalPhonenumberMixin,
    ConfirmSubmitterSendSmsTestMixin,
    HEADERS,
    LITE_ACCOUNT_KWARGS,
    MAILISH_ACCOUNT_KWARGS,
    PDD_ACCOUNT_KWARGS,
    PHONISH_ACCOUNT_KWARGS,
    SOCIAL_ACCOUNT_KWARGS,
    TEST_AUTH_HEADER,
    TEST_DOMAIN,
    TEST_EMAIL,
    TEST_FIRSTNAME,
    TEST_LOGIN,
    TEST_NOT_EXIST_PHONE_NUMBER,
    TEST_NOT_EXIST_PHONE_NUMBER_DUMPED,
    TEST_OPERATION_ID,
    TEST_OPERATION_ID2,
    TEST_PHONE_ID1,
    TEST_PHONE_ID2,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER1,
    TEST_TAXI_APPLICATION,
    TEST_UID,
)


@with_settings_hosts(
    APP_ID_SPECIFIC_ROUTE_DENOMINATOR=1,
    APP_ID_TO_SMS_ROUTE={TEST_TAXI_APPLICATION: 'taxi'},
    SMS_VALIDATION_CODE_LENGTH=4,
    SMS_VALIDATION_MAX_SMS_COUNT=3,
    SMS_VALIDATION_RESEND_TIMEOUT=0,
    YASMS_URL='http://localhost',
    **mock_counters()
)
class TestConfirmAndBindSubmitterBase(BaseConfirmSubmitterTestCase):
    def setUp(self):
        super(TestConfirmAndBindSubmitterBase, self).setUp()
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                age=100500,
                uid=TEST_UID,
                attributes={'password.encrypted': '1:testpassword'},
                **build_phone_bound(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER.e164,
                )
            ),
        )
        self.base_headers = mock_headers(
            user_agent='curl',
            cookie='Session_id=0:old-session;yandexuid=testyandexuid;sessionid2=0:old-sslsession',
        )

    def query_params(self, **kwargs):
        base_params = {
            'number': TEST_PHONE_NUMBER.e164,
            'display_language': 'ru',
            'track_id': self.track_id,
        }
        return merge_dicts(base_params, kwargs)

    def assert_blackbox_sessionid_called(self):
        assert_builder_url_contains_params(
            self.env.blackbox,
            {
                'full_info': 'yes',
                'method': 'sessionid',
                'sessionid': '0:old-session',
                'sslsessionid': '0:old-sslsession',
            },
            callnum=0,
        )

    def assert_yasms_sent_code_confirmation_sms(
        self,
        request,
        number=TEST_PHONE_NUMBER.e164,
        uid=TEST_UID,
    ):
        request.assert_url_starts_with('http://localhost/sendsms')
        request.assert_query_contains({
            'phone': number,
            'text': self.sms_text,
            'identity': 'confirm_and_bind_secure',
            'from_uid': str(uid),
            'caller': 'dev',
        })


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
class TestConfirmAndBindSecureSubmitterV2(TestConfirmAndBindSubmitterBase,
                                          BaseConfirmAndBindSubmitterMixin,
                                          CommonSubmitterCommitterTestMixin,
                                          ConfirmSubmitterSendSmsTestMixin,
                                          ConfirmSubmitterLocalPhonenumberMixin,
                                          ConfirmSubmitterChangePasswordNewSecureNumberTestMixin,
                                          ConfirmSubmitterAlreadyConfirmedPhoneWithNewPhoneTestMixin):
    url = '/2/bundle/phone/confirm_and_bind_secure/submit/?consumer=dev'
    track_state = CONFIRM_AND_BIND_SECURE_STATE
    specific_grants = {'base', 'bind_secure'}
    with_antifraud_score = True
    with_check_cookies = True

    def setUp(self):
        super(TestConfirmAndBindSecureSubmitterV2, self).setUp()
        self.additional_ok_response_params = {'is_password_required': False}

    def test_ok(self):
        self._test_ok(with_check_cookies=True)

    def test_ok_password_not_required(self):
        """
        Кука свежая, пароль вводился недавно, говорим об этом
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                age=0,
                uid=TEST_UID,
                attributes={'password.encrypted': '1:testpassword'},
            ),
        )
        rv = self.make_request()
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_send_code_response,
                {
                    u'is_password_required': False,
                },
            ),
        )

    def test_passwordless_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                age=-1,
                aliases=dict(social=TEST_SOCIAL_LOGIN1),
                crypt_password=None,
                login=TEST_SOCIAL_LOGIN1,
                uid=TEST_UID,
            ),
        )

        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)

        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_send_code_response,
                {
                    u'is_password_required': False,
                },
            ),
        )

        track = self.track_manager.read(self.track_id)
        self.check_ok_track(track)

        eq_(len(self.env.yasms.requests), 1)
        self.assert_yasms_sent_code_confirmation_sms(self.env.yasms.requests[0])

    def test_with_bound_confirmed_secure_phone(self):
        phone_args = build_phone_secured(
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER.e164,
        )
        phone_args['attributes']['password.encrypted'] = '1:testpassword'
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                age=0,
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
        self.assert_blackbox_sessionid_called()

        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')])
        self.env.antifraud_logger.assert_has_written([])

    def test_with_bound_not_confirmed_not_secure_phone(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                age=0,
                uid=TEST_UID,
                attributes={'password.encrypted': '1:testpassword'},
                **build_phone_bound(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER.e164,
                )
            ),
        )

        rv = self.make_request()
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_send_code_response,
                self.additional_ok_response_params,
                {
                    u'is_password_required': False,
                },
            ),
        )
        self.assert_blackbox_sessionid_called()
        eq_(len(self.env.yasms.requests), 1)

        self.assert_statbox_ok(with_check_cookies=True)

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

        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')])

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

        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')])

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
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_send_code_response,
                {
                    'track_id': self.track_id,
                    'number': TEST_NOT_EXIST_PHONE_NUMBER_DUMPED,
                },
                self.additional_ok_response_params,
            ),
        )

        requests = self.env.yasms.requests
        requests[0].assert_query_contains({
            'phone': TEST_NOT_EXIST_PHONE_NUMBER.e164,
            'from_uid': str(TEST_UID),
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
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_send_code_response,
                {
                    'track_id': self.track_id,
                    'number': TEST_NOT_EXIST_PHONE_NUMBER_DUMPED,
                },
                self.additional_ok_response_params,
            ),
        )

        requests = self.env.yasms.requests
        requests[0].assert_query_contains({
            'phone': TEST_NOT_EXIST_PHONE_NUMBER.e164,
            'from_uid': str(TEST_UID),
        })

    @parameterized.expand([
        (PHONISH_ACCOUNT_KWARGS, ),
        (MAILISH_ACCOUNT_KWARGS, ),
    ])
    def test_account_invalid_type_error(self, account_kwargs):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **account_kwargs
            ),
        )

        rv = self.make_request()

        expected_response = merge_dicts(
            self.number_response,
            {'track_id': self.track_id},
        )

        self.assert_error_response(rv, ['account.invalid_type'], **expected_response)
        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')])

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

    def test_captcha_not_shown(self):
        with self.track_transaction() as track:
            track.is_captcha_required = True

        rv = self.make_request(self.query_params())

        self.assert_ok_response(rv, check_all=False)


class TestConfirmAndBindSimpleSubmitter(TestConfirmAndBindSubmitterBase,
                                        BaseConfirmAndBindSubmitterMixin,
                                        CommonSubmitterCommitterTestMixin,
                                        ConfirmSubmitterSendSmsTestMixin,
                                        ConfirmSubmitterLocalPhonenumberMixin,
                                        ConfirmSubmitterAlreadyConfirmedPhoneWithNewPhoneTestMixin):
    url = '/1/bundle/phone/confirm_and_bind/submit/?consumer=dev'
    track_state = CONFIRM_AND_BIND_STATE
    specific_grants = {'base'}
    with_check_cookies = True

    def test_ok(self):
        self._test_ok(with_check_cookies=True)

    def test_ok_with_social_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_sessionid_multi_response(
                age=100500,
                **SOCIAL_ACCOUNT_KWARGS
            ),
        )
        self._test_ok(with_check_cookies=True)

    def test_phone_is_bound_as_secure(self):
        phone_args = build_phone_secured(
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER.e164,
        )
        phone_args['attributes']['password.encrypted'] = '1:testpassword'
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                age=0,
                uid=TEST_UID,
                **phone_args
            ),
        )
        rv = self.make_request()
        self.assert_error_response(rv, ['phone_secure.bound_and_confirmed'], check_content=False)

    def test_error_with_invalid_oauth_scope(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                scope='foo:bar',
            ),
        )
        self.base_headers = merge_dicts(
            HEADERS,
            mock_headers(
                cookie=None,
                authorization=TEST_AUTH_HEADER,
            ),
        )
        rv = self.make_request()
        self.assert_error_response(rv, ['oauth_token.invalid'], check_content=False)

    def test_ok_with_oauth_bind_phone_scope(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=BIND_PHONE_OAUTH_SCOPE,
            ),
        )
        self.base_headers = merge_dicts(
            HEADERS,
            mock_headers(
                cookie=None,
                authorization=TEST_AUTH_HEADER,
            ),
        )
        rv = self.make_request()
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_send_code_response,
                self.additional_ok_response_params,
            ),
        )


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    SMS_VALIDATION_MAX_CHECKS_COUNT=5,
)
class TestConfirmAndBindCommitterBase(BaseConfirmCommitterTestCase):
    with_check_cookies = False

    def setUp(self):
        super(TestConfirmAndBindCommitterBase, self).setUp()
        userinfo_args = dict(
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
        userinfo = blackbox_userinfo_response(**userinfo_args)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                age=100500,
                **userinfo_args
            ),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.db.serialize(userinfo)
        self.base_headers = mock_headers(
            user_agent='curl',
            cookie='Session_id=0:old-session;yandexuid=testyandexuid;sessionid2=0:old-sslsession',
        )
        self.has_uid = True
        self.env.statbox.bind_entry(
            'phone_confirmed',
            _inherit_from=['phone_confirmed', 'local_base'],
            code_checks_count='0',
        )
        self.env.statbox.bind_entry(
            'secure_phone_bound',
            _inherit_from=['secure_phone_bound', 'local_base'],
        )

    def assert_blackbox_sessionid_called(self):
        assert_builder_url_contains_params(
            self.env.blackbox,
            {
                'full_info': 'yes',
                'method': 'sessionid',
                'sessionid': '0:old-session',
                'sslsessionid': '0:old-sslsession',
            },
            callnum=0,
        )

    def assert_blackbox_login_called(self, callnum=1):
        args = {
            'aliases': 'all_with_hidden',
            'authtype': authtypes.AUTH_TYPE_VERIFY,
            'emails': 'getall',
            'format': 'json',
            'full_info': 'yes',
            'get_badauth_counts': 'yes',
            'get_public_name': 'yes',
            'getphonebindings': 'all',
            'getphoneoperations': '1',
            'getphones': 'all',
            'is_display_name_empty': 'yes',
            'method': 'login',
            'password': 'testpassword',
            'phone_attributes': '1,2,3,4,5,6,109',
            'regname': 'yes',
            'uid': str(TEST_UID),
            'ver': '2',
        }
        assert_builder_data_equals(
            self.env.blackbox,
            args,
            callnum=callnum,
            exclude_fields=[
                'userip',  # возвращается инстансом внутреннего класса в libipreg
                'dbfields',
                'attributes',
            ],
        )

    def query_params(self, exclude=None, **kwargs):
        base_params = {
            'code': self.confirmation_code,
            'password': 'testpassword',
            'track_id': self.track_id,
        }
        if exclude is not None:
            for key in exclude:
                del base_params[key]
        if not self.secure:
            base_params.pop('password')
        return merge_dicts(base_params, kwargs)

    def check_ok(self, response,
                 password_verification_passed_at=None, is_notified=True):
        self.assert_response_ok(response)

        self.assert_blackbox_sessionid_called()

        self.assert_secure_phone_bound()

        self.assert_track_ok(password_verification_passed_at=password_verification_passed_at)

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))

        entries.extend(
            [
                self.env.statbox.entry('enter_code'),
                self.env.statbox.entry('secure_bind_operation_created'),
                self.env.statbox.entry('account_phones_secure'),
                self.env.statbox.entry('local_account_modification', action='confirm_and_bind_secure',
                                       login=TEST_LOGIN),
                self.env.statbox.entry('phone_confirmed'),
                self.env.statbox.entry('secure_phone_bound'),
                self.env.statbox.entry('success'),
            ],
        )

        self.env.statbox.assert_has_written(entries)

        if is_notified:
            assert_user_notified_about_secure_phone_bound(
                mailer_faker=self.env.mailer,
                language='ru',
                email_address=TEST_EMAIL,
                firstname=TEST_FIRSTNAME,
                login=TEST_LOGIN,
            )

    def assert_response_ok(self, response):
        eq_(response.status_code, 200, response.data)
        eq_(json.loads(response.data), self.base_response)

    def assert_secure_phone_bound(self):
        assert_secure_phone_bound.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID1, 'confirmed': DatetimeNow(), 'secured': DatetimeNow()},
        )

    def assert_track_ok(self, password_verification_passed_at=None):
        track = self.track_manager.read(self.track_id)
        ok_(track.phone_confirmation_is_confirmed)
        eq_(track.phone_confirmation_confirms_count.get(), 1)
        ok_(not track.phone_confirmation_confirms_count_limit_reached)
        eq_(track.phone_confirmation_first_checked, TimeNow())
        eq_(track.phone_confirmation_last_checked, TimeNow())
        eq_(track.password_verification_passed_at, password_verification_passed_at)


@with_settings_hosts(
    SMS_VALIDATION_MAX_CHECKS_COUNT=5,
    YASMS_URL='http://localhost/',
)
class TestConfirmAndBindSecureCommitterV2(TestConfirmAndBindCommitterBase,
                                          BaseConfirmAndBindCommitterMixin,
                                          CommonSubmitterCommitterTestMixin,
                                          ConfirmCommitterTestMixin,
                                          ConfirmCommitterSentCodeTestMixin,
                                          ConfirmCommitterLocalPhonenumberTestMixin):
    url = '/2/bundle/phone/confirm_and_bind_secure/commit/?consumer=dev'
    track_state = CONFIRM_AND_BIND_SECURE_STATE
    specific_grants = {'base', 'bind_secure'}
    secure = True
    with_check_cookies = True

    def test_ok(self):
        """
        Успешно проходим по сценарию, когда пароль был введен
        """
        self.setup_track_for_commit()

        rv = self.make_request()
        self.check_ok(rv)

    def test_ok_password_not_needed(self):
        """
        Успешно проходим по сценарию, когда пароль не был введен,
        но кука свеженькая и нас пропускают без пароля.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                attributes={'password.encrypted': '1:testpassword'},
                age=0,
            ),
        )
        self.setup_track_for_commit()

        rv = self.make_request(
            self.query_params(exclude=['password']),
        )

        self.check_ok(rv, is_notified=False)

    def test_ok_with_lite_account(self):
        self.setup_track_for_commit()
        kwargs = dict(LITE_ACCOUNT_KWARGS)
        kwargs['attributes'] = {'password.encrypted': '1:testpassword'}
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**kwargs),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                age=100500,
                **kwargs
            ),
        )
        rv = self.make_request()

        eq_(rv.status_code, 200, rv.data)
        eq_(json.loads(rv.data), self.base_response)

    def test_ok_with_pdd_account(self):
        kwargs = dict(PDD_ACCOUNT_KWARGS)
        self.setup_track_for_commit(uid=kwargs['uid'])
        kwargs['domain'] = TEST_DOMAIN
        # Полноценный ПДД-пользователь - есть соглашение с pdd-EULA
        # и есть персональная информация + КВ/КО
        kwargs['subscribed_to'] = [102]
        kwargs['dbfields'] = {
            'userinfo_safe.hintq.uid': u'99:вопрос',
            'userinfo_safe.hinta.uid': u'ответ',
        }
        kwargs['attributes'] = {'password.encrypted': '1:testpassword'}
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**kwargs),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                age=100500,
                **kwargs
            ),
        )
        with settings_context(
            YASMS_URL='http://localhost/',
            SMS_VALIDATION_MAX_CHECKS_COUNT=5,
            **mock_counters()
        ):
            rv = self.make_request()
            eq_(rv.status_code, 200, rv.data)
            eq_(json.loads(rv.data), self.base_response)

    def test_passwordless_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_SOCIAL_LOGIN1,
                aliases=dict(social=TEST_SOCIAL_LOGIN1),
                crypt_password=None,
                age=-1,
            ),
        )
        self.setup_track_for_commit()

        rv = self.make_request(
            self.query_params(exclude=['password']),
        )

        self.assert_response_ok(rv)

        eq_(len(self.env.blackbox.requests), 3)
        self.assert_blackbox_sessionid_called()

        self.assert_secure_phone_bound()

        self.assert_track_ok()

    def test_already_confirmed(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                attributes={'password.encrypted': '1:testpassword'},
            ),
        )

        self.setup_track_for_commit(
            phone_confirmation_is_confirmed='1',
            phone_confirmation_confirms_count='1',
        )

        rv = self.make_request()

        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), self.base_response)

        self.assert_blackbox_sessionid_called()

        entries = []
        if self.with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend(
            [
                self.env.statbox.entry('enter_code'),
                self.env.statbox.entry('secure_bind_operation_created'),
                self.env.statbox.entry('account_phones_secure'),
                self.env.statbox.entry('local_account_modification', action='confirm_and_bind_secure',
                                       login=TEST_LOGIN),
                self.env.statbox.entry('phone_confirmed'),
                self.env.statbox.entry('secure_phone_bound'),
                self.env.statbox.entry('success'),
            ],
        )

        self.env.statbox.assert_has_written(entries)

    def test_blackbox_login_disabled_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                enabled=False,
                uid=TEST_UID,
            ),
        )

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

        self.assert_blackbox_sessionid_called()
        eq_(len(self.env.yasms.requests), 0)

        self.env.statbox.assert_has_written([self.env.statbox.entry('check_cookies')])

    def test_with_bound_confirmed_secure_phone(self):
        self.setup_track_for_commit()
        phone_args = build_phone_secured(
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER.e164,
        )
        phone_args['attributes']['password.encrypted'] = '1:testpassword'
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                **phone_args
            ),
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
        self.assert_blackbox_sessionid_called()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('enter_code'),
        ])

    @parameterized.expand([
        (PHONISH_ACCOUNT_KWARGS, ),
        (MAILISH_ACCOUNT_KWARGS, ),
    ])
    def test_account_invalid_type_error(self, account_kwargs):
        self.setup_track_for_commit()
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**account_kwargs),
        )

        rv = self.make_request()
        eq_(rv.status_code, 200, rv.data)
        eq_(
            json.loads(rv.data),
            merge_dicts(
                self.base_response,
                {u'status': u'error', u'errors': [u'account.invalid_type']},
            ),
            account_kwargs,
        )


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    SMS_VALIDATION_MAX_CHECKS_COUNT=5,
)
class TestConfirmAndBindSimpleCommitter(BaseConfirmCommitterTestCase):
    url = '/1/bundle/phone/confirm_and_bind/commit/?consumer=dev'
    track_state = CONFIRM_AND_BIND_STATE
    specific_grants = {'base'}

    def setUp(self):
        super(TestConfirmAndBindSimpleCommitter, self).setUp()
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                age=100500,
                login=TEST_LOGIN,
            ),
        )
        self.base_headers = mock_headers(
            user_agent='curl',
            cookie='Session_id=0:old-session;yandexuid=testyandexuid;sessionid2=0:old-sslsession',
        )
        self.has_uid = True
        self.setup_track_for_commit()
        self.base_response['phone_id'] = TEST_PHONE_ID1

    def query_params(self, **kwargs):
        base_params = {
            'code': self.confirmation_code,
            'track_id': self.track_id,
        }
        return merge_dicts(base_params, kwargs)

    def check_ok(self, response):
        self.assert_ok_response(response, **self.base_response)
        self.assert_blackbox_sessionid_called()

        track = self.track_manager.read(self.track_id)
        ok_(track.phone_confirmation_is_confirmed)
        eq_(track.phone_confirmation_confirms_count.get(), 1)
        ok_(not track.phone_confirmation_confirms_count_limit_reached)
        eq_(track.phone_confirmation_first_checked, TimeNow())
        eq_(track.phone_confirmation_last_checked, TimeNow())

    def assert_blackbox_sessionid_called(self):
        assert_builder_url_contains_params(
            self.env.blackbox,
            {
                'full_info': 'yes',
                'method': 'sessionid',
                'sessionid': '0:old-session',
                'sslsessionid': '0:old-sslsession',
            },
            callnum=0,
        )

    def assert_historydb_ok(self):
        events = [
            {'uid': str(TEST_UID), 'name': 'phone.%d.action' % TEST_PHONE_ID1, 'value': 'changed'},
            {'uid': str(TEST_UID), 'name': 'action', 'value': 'confirm_and_bind'},
            {'uid': str(TEST_UID), 'name': 'phone.%d.number' % TEST_PHONE_ID1, 'value': TEST_PHONE_NUMBER.e164},
            {'uid': str(TEST_UID), 'name': 'phone.%d.confirmed' % TEST_PHONE_ID1, 'value': TimeNow()},
            {'uid': str(TEST_UID), 'name': 'consumer', 'value': 'dev'},
        ]
        self.env.event_logger.assert_contains(events)

    def _test_ok(self, login=TEST_LOGIN):
        assert_no_phone_in_db(self.env.db, TEST_UID, TEST_PHONE_ID1, TEST_PHONE_NUMBER.e164)
        rv = self.make_request()
        self.check_ok(rv)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('enter_code'),
            self.env.statbox.entry('local_simple_bind_operation_created'),
            self.env.statbox.entry('local_account_modification', login=login),
            self.env.statbox.entry('local_phone_confirmed'),
            self.env.statbox.entry('local_simple_phone_bound'),
            self.env.statbox.entry('success'),
        ])
        assert_simple_phone_bound.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID1, 'confirmed': DatetimeNow()},
        )
        self.assert_historydb_ok()

    def test_ok(self):
        self._test_ok()

    def test_social_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                age=100500,
                **SOCIAL_ACCOUNT_KWARGS
            ),
        )
        self._test_ok(login=SOCIAL_ACCOUNT_KWARGS['login'])

    def test_phone_is_already_bound_no_operations(self):
        build_account_from_session(
            db_faker=self.env.db,
            blackbox_faker=self.env.blackbox,
            uid=TEST_UID,
            **build_phone_bound(
                TEST_PHONE_ID1,
                TEST_PHONE_NUMBER.e164,
                phone_confirmed=TEST_DATE,
            )
        )
        assert_simple_phone_bound.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID1, 'confirmed': TEST_DATE},
        )

        rv = self.make_request()
        self.check_ok(rv)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('enter_code'),
            self.env.statbox.entry('local_phone_confirmed', _exclude=['operation_id']),
            self.env.statbox.entry('success'),
        ])
        assert_simple_phone_bound.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID1, 'confirmed': DatetimeNow()},
        )
        self.assert_historydb_ok()

    def test_phone_is_already_bound_with_operations(self):
        build_account_from_session(
            db_faker=self.env.db,
            blackbox_faker=self.env.blackbox,
            uid=TEST_UID,
            age=100500,
            **merge_dicts(
                build_phone_bound(TEST_PHONE_ID1, TEST_PHONE_NUMBER.e164, phone_confirmed=TEST_DATE),
                build_mark_operation(
                    TEST_OPERATION_ID,
                    TEST_PHONE_NUMBER.e164,
                    TEST_PHONE_ID1,
                ),
            )
        )
        assert_phone_marked.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID1, 'confirmed': TEST_DATE},
            {'id': 1, 'type': 'mark', 'phone_id': TEST_PHONE_ID1},
        )

        rv = self.make_request()
        self.check_ok(rv)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('enter_code'),
            self.env.statbox.entry('local_phone_confirmed', _exclude=['operation_id']),
            self.env.statbox.entry('success'),
        ])
        assert_phone_marked.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID1, 'confirmed': DatetimeNow()},
            {'id': 1, 'type': 'mark', 'phone_id': TEST_PHONE_ID1, 'confirmed': None},
        )
        self.assert_historydb_ok()

    def test_phone_is_bound_as_secure(self):
        build_account_from_session(
            db_faker=self.env.db,
            blackbox_faker=self.env.blackbox,
            uid=TEST_UID,
            age=100500,
            **build_phone_secured(TEST_PHONE_ID1, TEST_PHONE_NUMBER.e164, phone_confirmed=TEST_DATE)
        )
        assert_secure_phone_bound.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID1, 'confirmed': TEST_DATE},
        )
        rv = self.make_request()
        self.assert_error_response(rv, ['phone_secure.bound_and_confirmed'], check_content=False)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('enter_code'),
        ])
        assert_secure_phone_bound.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID1, 'confirmed': TEST_DATE},
        )
        self.env.event_logger.assert_events_are_logged([])

    def test_phone_is_bound_with_securify_operation(self):
        build_account_from_session(
            db_faker=self.env.db,
            blackbox_faker=self.env.blackbox,
            uid=TEST_UID,
            age=100500,
            **merge_dicts(
                build_phone_bound(TEST_PHONE_ID1, TEST_PHONE_NUMBER.e164, phone_confirmed=TEST_DATE),
                build_securify_operation(
                    TEST_OPERATION_ID,
                    TEST_PHONE_ID1,
                ),
            )
        )
        assert_simple_phone_being_securified.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID1, 'confirmed': TEST_DATE},
            {'id': TEST_OPERATION_ID, 'type': 'securify', 'phone_id': TEST_PHONE_ID1},
        )

        rv = self.make_request()
        self.check_ok(rv)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('enter_code'),
            self.env.statbox.entry('local_phone_confirmed', _exclude=['operation_id']),
            self.env.statbox.entry('success'),
        ])
        assert_simple_phone_being_securified.check_db(
            self.env.db,
            TEST_UID,
            dict(
                confirmed=DatetimeNow(),
                id=TEST_PHONE_ID1,
            ),
            dict(
                confirmed=None,
                id=TEST_OPERATION_ID,
                phone_id=TEST_PHONE_ID1,
                type='securify',
            ),
        )
        self.assert_historydb_ok()

    def test_account_invalid_type_error(self):
        for account_kwargs in (
            PHONISH_ACCOUNT_KWARGS,
            MAILISH_ACCOUNT_KWARGS,
        ):
            self.setup_track_for_commit()
            self.env.blackbox.set_blackbox_response_value(
                'sessionid',
                blackbox_sessionid_multi_response(
                    age=100500,
                    **account_kwargs
                ),
            )
            rv = self.make_request()

            self.assert_error_response(rv, ['account.invalid_type'], **self.number_response)

    def test_error_with_invalid_oauth_scope(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                scope='foo:bar',
            ),
        )
        self.base_headers = merge_dicts(
            HEADERS,
            mock_headers(
                cookie=None,
                authorization=TEST_AUTH_HEADER,
            ),
        )
        rv = self.make_request()
        self.assert_error_response(rv, ['oauth_token.invalid'], check_content=False)

    def test_ok_with_oauth_bind_phone_scope(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=BIND_PHONE_OAUTH_SCOPE,
            ),
        )
        self.base_headers = merge_dicts(
            HEADERS,
            mock_headers(
                cookie=None,
                authorization=TEST_AUTH_HEADER,
            ),
        )
        rv = self.make_request()
        self.assert_ok_response(rv, **self.base_response)

    def test_bound_phone_replacing_secure(self):
        build_account_from_session(
            blackbox_faker=self.env.blackbox,
            db_faker=self.env.db,
            uid=TEST_UID,
            **deep_merge(
                build_phone_bound(
                    TEST_PHONE_ID1,
                    TEST_PHONE_NUMBER.e164,
                    phone_confirmed=TEST_DATE,
                ),
                build_phone_secured(TEST_PHONE_ID2, TEST_PHONE_NUMBER1.e164),
                build_simple_replaces_secure_operations(
                    secure_operation_id=TEST_OPERATION_ID2,
                    secure_phone_id=TEST_PHONE_ID2,
                    simple_operation_id=TEST_OPERATION_ID,
                    simple_phone_id=TEST_PHONE_ID1,
                    simple_phone_number=TEST_PHONE_NUMBER.e164,
                ),
            )
        )

        rv = self.make_request()

        self.check_ok(rv)

        assert_simple_phone_replace_secure.check_db(
            self.env.db,
            TEST_UID,
            dict(
                id=TEST_PHONE_ID1,
                confirmed=DatetimeNow(),
            ),
            dict(
                confirmed=None,
                id=TEST_OPERATION_ID,
                phone_id=TEST_PHONE_ID1,
            ),
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('enter_code'),
            self.env.statbox.entry('local_phone_confirmed', _exclude=['operation_id']),
            self.env.statbox.entry('success'),
        ])

        self.assert_historydb_ok()
