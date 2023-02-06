# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.common.phone import PhoneAntifraudFeatures
from passport.backend.api.common.phone_karma import PhoneKarma
from passport.backend.api.tests.views.bundle.mixins.account import GetAccountBySessionOrTokenMixin
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_AUTH_HEADER,
    TEST_DISPLAY_LANGUAGE,
    TEST_NOT_EXIST_PHONE_NUMBER,
    TEST_OAUTH_SCOPE,
    TEST_OPERATION_ID,
    TEST_OPERATION_ID2,
    TEST_OTHER_EXIST_PHONE_NUMBER,
    TEST_PASSWORD_HASH,
    TEST_PHONE_CREATED_DT,
    TEST_PHONE_NUMBER,
    TEST_PHONISH_LOGIN1,
    TEST_PORTAL_ALIAS_TYPE,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)
from passport.backend.api.views.bundle.phone.helpers import dump_number
from passport.backend.core.builders.antifraud import ScoreAction
from passport.backend.core.builders.antifraud.faker.fake_antifraud import antifraud_score_response
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_phone_bindings_response,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.builders.ufo_api.faker import ufo_api_phones_stats_response
from passport.backend.core.builders.yasms.faker import (
    yasms_error_xml_response,
    yasms_send_sms_response,
)
from passport.backend.core.conf import settings
from passport.backend.core.counters import sms_per_ip
from passport.backend.core.models.phones.faker import (
    assert_phonenumber_alias_missing,
    assert_secure_phone_being_aliasified,
    assert_secure_phone_being_bound,
    assert_secure_phone_being_dealiasified,
    assert_secure_phone_being_removed,
    assert_secure_phone_being_replaced,
    assert_simple_phone_being_bound_replace_secure,
    assert_simple_phone_being_securified,
    assert_simple_phone_replace_secure,
    build_account_from_session,
    build_current_phone_binding,
    build_mark_operation,
    build_phone_being_bound,
    build_phone_bound,
    build_phone_secured,
    build_remove_operation,
    build_secure_phone_being_bound,
    build_simple_replaces_secure_operations,
    event_lines_replace_secure_operation_created,
    PhoneIdGeneratorFaker,
    predict_next_operation_id,
)
from passport.backend.core.models.phones.phones import SECURITY_IDENTITY
from passport.backend.core.test.consts import TEST_NEOPHONISH_LOGIN1
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.bit_vector.bit_vector import PhoneOperationFlags
from passport.backend.core.yasms.test import sms as sms_notifications
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)
from passport.backend.utils.time import datetime_to_integer_unixtime

from .base import PhoneManageBaseTestCase
from .base_test_data import (
    LOCAL_TEST_REPLACEMENT_PHONE_NUMBER,
    TEST_CONFIRMATION_CODE,
    TEST_LOGIN,
    TEST_NON_EXISTENT_TRACK_ID,
    TEST_OPERATION_ID_EXTRA,
    TEST_PHONE_BOUND_DT,
    TEST_PHONE_ID,
    TEST_PHONE_ID_EXTRA,
    TEST_REPLACEMENT_PHONE_ID,
    TEST_REPLACEMENT_PHONE_NUMBER,
    TEST_SECURE_PHONE_ID,
    TEST_SECURE_PHONE_NUMBER,
    TEST_SOCIAL_LOGIN,
)


class SubmitBaseTestCase(PhoneManageBaseTestCase):
    step = 'submit'
    with_phone_karma_check = False

    def setUp(self):
        super(SubmitBaseTestCase, self).setUp()

        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )

        self.env.ufo_api.set_response_value(
            'phones_stats',
            ufo_api_phones_stats_response(TEST_PHONE_NUMBER),
        )

        self.env.antifraud_api.set_response_value('score', antifraud_score_response())

    def set_blackbox_response(self, account_attributes=None, phones=None,
                              operations=None, password_is_set=True,
                              login=TEST_LOGIN, alias_type=TEST_PORTAL_ALIAS_TYPE,
                              phonenumber_alias=None, phone_bindings=None, scope=TEST_OAUTH_SCOPE):
        alias_kwargs = {
            'aliases': {
                alias_type: login,
            },
        }
        if phonenumber_alias is not None:
            alias_kwargs['aliases']['phonenumber'] = phonenumber_alias
            account_attributes = account_attributes or dict()
            account_attributes['account.enable_search_by_phone_alias'] = '1'

        bb_kwargs = merge_dicts(
            {
                'login': login,
                'phones': phones,
                'phone_operations': operations,
                'attributes': account_attributes,
                'crypt_password': '1:pass' if password_is_set else None,
                'phone_bindings': phone_bindings,
                'login_id': 'login-id',
            },
            alias_kwargs,
        )
        bb_response = blackbox_sessionid_multi_response(
            have_password=password_is_set,
            **bb_kwargs
        )

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            bb_response,
        )

        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(scope=scope, **bb_kwargs),
        )

        self.env.db.serialize(bb_response)

    def assert_response_ok(self, rv, security_identity=1, code_sent=True):
        eq_(rv.status_code, 200)
        data = json.loads(rv.data)

        eq_(data['status'], 'ok')
        eq_(data['track_id'], self.track_id)
        if code_sent:
            eq_(data['code_length'], settings.SMS_VALIDATION_CODE_LENGTH)
        else:
            ok_('code_length' not in data)
        eq_(data['phone'], {
            'operation': {
                'id': 1,
                'security_identity': security_identity,
                'in_quarantine': False,
            },
            'number': dump_number(TEST_PHONE_NUMBER),
            'id': TEST_PHONE_ID,
        })
        ok_('account' in data)

    def assert_events_are_logged(self, op_type, is_secure=False,
                                 phoneid=TEST_PHONE_ID, number=TEST_PHONE_NUMBER,
                                 operation_id=TEST_OPERATION_ID,
                                 is_phone_created=True):
        phone_key = 'phone.%s.' % phoneid
        phone_operation_key = '%soperation.%s.' % (phone_key, operation_id)
        security_identity = '1' if is_secure else str(int(number))

        historydb_entries = {
            phone_operation_key + 'action': 'created',
            phone_operation_key + 'type': op_type,
            phone_operation_key + 'security_identity': security_identity,
            phone_operation_key + 'started': TimeNow(),
            phone_operation_key + 'finished': TimeNow(offset=settings.PHONE_QUARANTINE_SECONDS),
            phone_key + 'number': number.e164,
            'action': self.action,
            'consumer': 'dev',
            'user_agent': 'curl',
        }
        if is_phone_created:
            historydb_entries.update({
                phone_key + 'created': TimeNow(),
                phone_key + 'action': 'created',
            })
        super(SubmitBaseTestCase, self).assert_events_are_logged(self.env.handle_mock, historydb_entries)

    def _test_error_phone_already_exists_and_bound(self, with_check_cookies=False):
        """
        Проверяем, что невозможно начать процесс, если к аккаунту уже привязан указанный телефонный номер.
        """
        phone = {
            'id': 678,
            'number': TEST_PHONE_NUMBER.e164,
            'created': datetime(2001, 2, 3, 12, 34, 56),
            'bound': datetime(2001, 2, 3, 12, 34, 57),
        }
        self.set_blackbox_response(phones=[phone])

        rv = self.make_request()
        self.assert_error_response(rv, ['phone.bound'])
        entries = [self.env.statbox.entry('submitted', number=TEST_PHONE_NUMBER.masked_format_for_statbox)]
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        self.env.statbox.assert_has_written(entries)

    def _test_ok_phone_already_exists_not_bound(self, security_identity, with_check_cookies=False):
        """
        Проверяем, что возможно начать процесс, если на аккаунте уже есть номер, но он еще не привязан.
        """
        phone = {
            'id': 1,
            'number': TEST_PHONE_NUMBER.e164,
            'created': datetime(2001, 2, 3, 12, 34, 56),
        }
        self.set_blackbox_response(phones=[phone])

        rv = self.make_request()
        self.assert_response_ok(rv, security_identity=security_identity)

        self.assert_statbox_ok(
            with_check_cookies=with_check_cookies,
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
        )

    def _test_error_phone_not_bound(self):
        """
        Проверяем, что указание непривязанного телефона приведет к ошибке phone.not_found.
        """
        phone = {
            'id': 1,
            'number': TEST_PHONE_NUMBER.e164,
            'created': datetime(2001, 2, 3, 12, 34, 56),
        }
        self.set_blackbox_response(phones=[phone])

        rv = self.make_request()
        self.assert_error_response(rv, ['phone.not_found'])

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted', phone_id='1'),
            self.env.statbox.entry('check_cookies'),
        ])

    def _test_error_phone_already_exists_not_bound_has_operation(
        self, security_identity,
        with_check_cookies=False, **submitted_kw
    ):
        """
        Проверяем, что невозможно начать процесс, если на аккаунте уже есть непривязанный номер с операцией.
        """
        phone = {
            'id': 1,
            'number': TEST_PHONE_NUMBER.e164,
            'created': datetime(2001, 2, 3, 12, 34, 56),
        }
        operation = {
            'id': 100,
            'phone_id': 1,
            'type': 'bind',
            'security_identity': security_identity,
        }
        self.set_blackbox_response(phones=[phone], operations=[operation])

        rv = self.make_request()
        self.assert_error_response(rv, ['operation.exists'])
        entries = [self.env.statbox.entry('submitted', **submitted_kw)]
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        self.env.statbox.assert_has_written(entries)

    def _test_error_yasms_temporaryblock(self, with_check_cookies=False, **kwargs):
        self.set_blackbox_response()
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_error_xml_response('msg', code='LIMITEXCEEDED'),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['sms_limit.exceeded'])

        statbox_entries = [self.env.statbox.entry('submitted', **kwargs)]
        if with_check_cookies:
            statbox_entries.append(self.env.statbox.entry('check_cookies'))
        if self.with_phone_karma_check:
            statbox_entries.extend(
                [
                    self.env.statbox.entry('check_phone_karma', **kwargs),
                    self.env.statbox.entry('pharma_allowed', **kwargs),
                ],
            )
        statbox_entries.append(
            self.env.statbox.entry('send_code_error', **dict(kwargs, reason='yasms_phone_limit')),
        )
        self.env.statbox.assert_has_written(
            statbox_entries,
        )

    def _test_error_bad_phone_karma(self, number=TEST_PHONE_NUMBER, **kwargs):
        self.set_blackbox_response()
        self.env.ufo_api.set_response_value(
            'phones_stats',
            ufo_api_phones_stats_response(
                number,
                data={'phone_number_counter': 100},
            ),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['phone.compromised'])

        submitted_kwargs = dict(kwargs)
        if 'phone_id' not in kwargs:
            submitted_kwargs['number'] = number.masked_format_for_statbox

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted', **submitted_kwargs),
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry(
                'check_phone_karma',
                karma=str(PhoneKarma.black),
                number=number.masked_format_for_statbox,
                **kwargs
            ),
        ])

    def assert_statbox_ok(self, with_check_cookies=False, **kwargs):
        statbox_entries = [
            self.env.statbox.entry('submitted', **kwargs),
        ]
        if with_check_cookies:
            statbox_entries.append(self.env.statbox.entry('check_cookies'))
        if self.with_phone_karma_check:
            statbox_entries.extend(
                [
                    self.env.statbox.entry('check_phone_karma', **kwargs),
                    self.env.statbox.entry('pharma_allowed', **kwargs),
                ],
            )
        statbox_entries.extend([
            self.env.statbox.entry('phone_operation_created', operation_id=str(TEST_OPERATION_ID)),
            self.env.statbox.entry('code_sent', operation_id=str(TEST_OPERATION_ID), **kwargs),
        ])
        self.env.statbox.assert_has_written(
            statbox_entries,
        )

    def _assert_confirmation_code_sent(self, language='ru', phone_number=TEST_PHONE_NUMBER):
        identity = '%(mode)s.%(step)s.send_confirmation_code' % {'mode': self.mode, 'step': self.step}
        sms_notifications.assert_confirmation_code_sent(self.env.yasms, language, phone_number, identity, TEST_UID)

    def _test_secure_phone_has_operation(self):
        operations = build_remove_operation(TEST_OPERATION_ID, TEST_PHONE_ID)['phone_operations']
        self.set_blackbox_response(operations=operations)

        rv = self.make_request()

        self.assert_error_response(rv, ['operation.exists'])

    def _test_blackbox_args(self, code_sent=True):
        self.set_blackbox_response()

        rv = self.make_request()

        self.assert_response_ok(rv, code_sent=code_sent)

        requests = self.env.blackbox.requests
        eq_(len(requests), 1)

        requests[0].assert_query_contains({
            'method': 'sessionid',
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
            'aliases': 'all_with_hidden',
        })

        requests[0].assert_contains_attributes(
            {
                'account.is_disabled',
                'account.2fa_on',
                'password.encrypted',
            } |
            set(settings.BLACKBOX_PHONE_ATTRIBUTES),
        )

    def assert_ok_pharma_request(self, request):
        request_data = json.loads(request.post_args)
        features = PhoneAntifraudFeatures.default(
            sub_channel='dev',
            user_phone_number=TEST_PHONE_NUMBER,
        )
        features.external_id = 'track-{}'.format(self.track_id)
        features.phone_confirmation_method = 'by_sms'
        features.t = TimeNow(as_milliseconds=True)
        features.request_path = self.base_method_path
        features.scenario = 'authorize'
        features.add_headers_features(self.build_headers())
        features.login_id = 'login-id'
        assert request_data == features.as_score_dict()


@with_settings_hosts()
class TestBindSimplePhoneSubmit(SubmitBaseTestCase,
                                GetAccountBySessionOrTokenMixin):
    base_method_path = '/1/bundle/phone/manage/bind_simple/submit/'
    base_request_args = {'number': TEST_PHONE_NUMBER.e164, 'display_language': TEST_DISPLAY_LANGUAGE}

    action = 'simple_bind_submit'
    mode = 'simple_bind'

    def _test_ok(self, by_token=False, alias_type=TEST_PORTAL_ALIAS_TYPE, login=TEST_LOGIN):
        auth_header = dict(authorization=TEST_AUTH_HEADER) if by_token else dict(cookie=TEST_USER_COOKIE)
        headers = self.build_headers(**auth_header)
        self.set_blackbox_response(alias_type=alias_type, login=login)
        rv = self.make_request(headers=headers)
        self.assert_response_ok(rv, security_identity=int(TEST_PHONE_NUMBER))
        self.assert_events_are_logged('bind', operation_id=1)

        self.check_db_phone_attr('number', TEST_PHONE_NUMBER.digital)
        self.check_db_phone_attr('created', TimeNow())

        self.check_db_phone_operation(dict(
            type='bind',
            code_send_count=1,
            security_identity=int(TEST_PHONE_NUMBER),
            code_last_sent=DatetimeNow(),
            code_value=TEST_CONFIRMATION_CODE,
            started=DatetimeNow(),
            finished=DatetimeNow() + timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
        ))

        self.assert_statbox_ok(with_check_cookies=not by_token, number=TEST_PHONE_NUMBER.masked_format_for_statbox)
        self.check_yasms_send_sms_request(self.env.yasms.requests[0])
        self.assert_blackbox_auth_method_ok(by_token)
        self.check_account_modification_push_not_sent()

    def test_ok_by_session(self):
        self._test_ok()

    def test_ok_by_token(self):
        self._test_ok(by_token=True)

    def test_ok_with_existing_track(self):
        self._test_ok_with_existing_track()

    def test_error_phone_already_exists_and_bound(self):
        self._test_error_phone_already_exists_and_bound(with_check_cookies=True)

    def test_ok_phone_already_exists_not_bound(self):
        self._test_ok_phone_already_exists_not_bound(
            with_check_cookies=True,
            security_identity=int(TEST_PHONE_NUMBER),
        )

    def test_error_account_disabled(self):
        self._test_error_account_disabled()

    def test_error_account_disabled_on_deletion(self):
        self._test_error_account_disabled_on_deletion()

    def test_error_yasms_temporaryblock(self):
        self._test_error_yasms_temporaryblock(
            with_check_cookies=True,
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
        )

    def test_error_phone_already_exists_not_bound_has_operation(self):
        self._test_error_phone_already_exists_not_bound_has_operation(
            int(TEST_PHONE_NUMBER),
            with_check_cookies=True,
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
        )

    def test_ok_account_without_password(self):
        self._test_ok_account_without_password()

    def test_phonish(self):
        self.set_blackbox_response(alias_type='phonish', login=TEST_PHONISH_LOGIN1)

        rv = self.make_request(
            headers=self.build_headers(authorization=TEST_AUTH_HEADER),
        )

        self.assert_error_response(rv, ['account.invalid_type'])

    def test_social_ok(self):
        self._test_ok(alias_type='social', login=TEST_SOCIAL_LOGIN)


@with_settings_hosts(
    PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
)
class TestBindSecurePhoneSubmit(SubmitBaseTestCase,
                                GetAccountBySessionOrTokenMixin):
    base_method_path = '/1/bundle/phone/manage/bind_secure/submit/'
    base_request_args = {'number': TEST_PHONE_NUMBER.e164, 'display_language': TEST_DISPLAY_LANGUAGE}

    action = 'secure_bind_submit'
    mode = 'secure_bind'
    with_phone_karma_check = True

    def _test_ok(self, by_token=False, alias_type=TEST_PORTAL_ALIAS_TYPE, login=TEST_LOGIN):
        auth_header = dict(authorization=TEST_AUTH_HEADER) if by_token else dict(cookie=TEST_USER_COOKIE)
        headers = self.build_headers(**auth_header)
        self.set_blackbox_response()
        rv = self.make_request(headers=headers)
        self.assert_response_ok(rv)

        self.check_db_phone_attr('number', TEST_PHONE_NUMBER.digital)
        self.check_db_phone_attr('created', TimeNow())

        self.check_db_phone_operation(dict(
            type='bind',
            code_send_count=1,
            security_identity=SECURITY_IDENTITY,
            code_last_sent=DatetimeNow(),
            code_value=TEST_CONFIRMATION_CODE,
            started=DatetimeNow(),
            finished=DatetimeNow() + timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
        ))

        self.assert_statbox_ok(with_check_cookies=not by_token, number=TEST_PHONE_NUMBER.masked_format_for_statbox)
        self.assert_events_are_logged('bind', is_secure=True, operation_id=TEST_OPERATION_ID)

        self.check_yasms_send_sms_request(self.env.yasms.requests[0])
        self.assert_blackbox_auth_method_ok(by_token)

        assert len(self.env.antifraud_api.requests) == 1
        self.assert_ok_pharma_request(self.env.antifraud_api.requests[0])
        self.check_account_modification_push_not_sent()

    def test_ok_by_session(self):
        self._test_ok()

    def test_ok_by_token(self):
        self._test_ok(by_token=True)

    def test_ok_with_existing_track(self):
        self._test_ok_with_existing_track()

    def test_error_bind_other_secure(self):
        build_account_from_session(
            db_faker=self.env.db,
            blackbox_faker=self.env.blackbox,
            uid=TEST_UID,
            crypt_password=TEST_PASSWORD_HASH,
            **build_secure_phone_being_bound(TEST_PHONE_ID_EXTRA, TEST_PHONE_NUMBER.e164, TEST_OPERATION_ID)
        )

        rv = self.make_request(data=dict(self.base_request_args, number=TEST_NOT_EXIST_PHONE_NUMBER.e164))

        self.assert_error_response(rv, ['operation.secure_operation_exists'])

    def test_error_secure_number_already_exists(self):
        self._test_error_secure_number_exists()

    def test_error_phone_already_exists_and_bound(self):
        self._test_error_phone_already_exists_and_bound(with_check_cookies=True)

    def test_ok_phone_already_exists_not_bound(self):
        self._test_ok_phone_already_exists_not_bound(SECURITY_IDENTITY, with_check_cookies=True)

    def test_error_account_disabled(self):
        self._test_error_account_disabled()

    def test_error_yasms_temporaryblock(self):
        self._test_error_yasms_temporaryblock(
            with_check_cookies=True,
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
        )

    def test_error_phone_already_exists_not_bound_has_operation(self):
        self._test_error_phone_already_exists_not_bound_has_operation(
            int(TEST_PHONE_NUMBER),
            with_check_cookies=True,
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
        )

    def test_error_bad_phone_karma(self):
        self._test_error_bad_phone_karma(
            number=TEST_PHONE_NUMBER,
        )

    def test_ok_account_without_password(self):
        self._test_ok_account_without_password()

    def test_aliasify(self):
        self.set_blackbox_response()

        rv = self.make_request(data=dict(self.base_request_args, is_alias=True))

        self.assert_response_ok(rv)

        flags = PhoneOperationFlags()
        flags.aliasify = True

        assert_secure_phone_being_bound.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID},
            {'flags': flags},
        )

    def test_dont_aliasify(self):
        self.set_blackbox_response()

        rv = self.make_request(data=dict(self.base_request_args, is_alias=False))

        self.assert_response_ok(rv)

        flags = PhoneOperationFlags()
        flags.aliasify = False

        assert_secure_phone_being_bound.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID},
            {'flags': flags},
        )

    def test_social_ok(self):
        self._test_ok(alias_type='social', login=TEST_SOCIAL_LOGIN)

    def test_passwordless_account(self):
        self.set_blackbox_response(
            alias_type='social',
            login=TEST_SOCIAL_LOGIN,
            password_is_set=False,
        )

        rv = self.make_request()

        self.assert_response_ok(rv)

        assert_secure_phone_being_bound.check_db(
            self.env.db,
            TEST_UID,
            phone_attributes=dict(
                id=TEST_PHONE_ID,
                number=TEST_PHONE_NUMBER.e164,
            ),
        )

        self.assert_statbox_ok(with_check_cookies=True, number=TEST_PHONE_NUMBER.masked_format_for_statbox)
        self.assert_events_are_logged('bind', is_secure=True, operation_id=TEST_OPERATION_ID)
        self.check_yasms_send_sms_request(self.env.yasms.requests[0])

    def test_aliasify__passwordless_account(self):
        self.set_blackbox_response(
            alias_type='social',
            login=TEST_SOCIAL_LOGIN,
            password_is_set=False,
        )

        rv = self.make_request(data=dict(self.base_request_args, is_alias=True))

        self.assert_response_ok(rv)

        flags = PhoneOperationFlags()
        flags.aliasify = True

        assert_secure_phone_being_bound.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID},
            {'flags': flags},
        )

    def test_pharma_denied(self):
        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response(action=ScoreAction.DENY)])
        self.set_blackbox_response()

        rv = self.make_request()

        self.assert_error_response(rv, ['sms_limit.exceeded'])

        entries = [self.env.statbox.entry('submitted', number=TEST_PHONE_NUMBER.masked_format_for_statbox)]
        entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend([
            self.env.statbox.entry('check_phone_karma'),
            self.env.statbox.entry('pharma_denied'),
        ])

        self.env.statbox.assert_equals(entries)

        assert len(self.env.antifraud_api.requests) == 1
        self.assert_ok_pharma_request(self.env.antifraud_api.requests[0])

        self.env.yasms_private_logger.assert_equals(
            [
                self.env.yasms_private_logger.entry('yasms_enqueued'),
                self.env.yasms_private_logger.entry('yasms_not_sent'),
            ],
        )


@with_settings_hosts(
    PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
)
class TestSecurifySubmit(SubmitBaseTestCase, GetAccountBySessionOrTokenMixin):
    base_method_path = '/1/bundle/phone/manage/securify/submit/'
    base_request_args = {'phone_id': TEST_PHONE_ID, 'display_language': TEST_DISPLAY_LANGUAGE}

    action = 'securify_submit'
    mode = 'securify'
    with_phone_karma_check = True

    def setUp(self):
        self.phone = {
            'number': TEST_PHONE_NUMBER.e164,
            'id': TEST_PHONE_ID,
            'created': TEST_PHONE_CREATED_DT,
            'bound': TEST_PHONE_BOUND_DT,
            'confirmed': TEST_PHONE_BOUND_DT,
        }
        self.phone_binding = build_current_phone_binding(
            TEST_PHONE_ID,
            TEST_PHONE_NUMBER.e164,
            TEST_PHONE_BOUND_DT,
        )
        super(TestSecurifySubmit, self).setUp()

    def set_blackbox_response(
        self,
        scope=TEST_OAUTH_SCOPE,
        account_attributes=None,
        phones=None,
        operations=None,
        password_is_set=True,
        phone_bindings=None,
        **kwargs
    ):
        super(TestSecurifySubmit, self).set_blackbox_response(
            account_attributes=account_attributes,
            phones=phones or [self.phone],
            phone_bindings=phone_bindings or [self.phone_binding],
            operations=operations,
            password_is_set=password_is_set,
            scope=scope,
        )

    def _test_ok(self, by_token=False):
        auth_header = dict(authorization=TEST_AUTH_HEADER) if by_token else dict(cookie=TEST_USER_COOKIE)
        headers = self.build_headers(**auth_header)
        self.set_blackbox_response()
        rv = self.make_request(headers=headers)
        self.assert_response_ok(rv)

        self.check_db_phone_attr('number', TEST_PHONE_NUMBER.digital)
        self.check_db_phone_attr('created', str(datetime_to_integer_unixtime(self.phone['created'])))
        self.check_db_phone_attr('bound', str(datetime_to_integer_unixtime(self.phone['bound'])))

        self.check_db_phone_operation(dict(
            type='securify',
            code_send_count=1,
            security_identity=SECURITY_IDENTITY,
            code_last_sent=DatetimeNow(),
            code_value=TEST_CONFIRMATION_CODE,
            started=DatetimeNow(),
            finished=DatetimeNow() + timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
        ))
        self.assert_statbox_ok(phone_id='1', with_check_cookies=not by_token)

        self.assert_events_are_logged(
            'securify',
            is_secure=True,
            operation_id=1,
            is_phone_created=False,
        )

        self.check_yasms_send_sms_request(self.env.yasms.requests[0])
        self.assert_blackbox_auth_method_ok(by_token)
        self.check_account_modification_push_not_sent()

    def test_ok_by_session(self):
        self._test_ok()

    def test_ok_by_token(self):
        self._test_ok(by_token=True)

    def test_error_secure_phone_being_bound(self):
        build_account_from_session(
            db_faker=self.env.db,
            blackbox_faker=self.env.blackbox,
            uid=TEST_UID,
            crypt_password=TEST_PASSWORD_HASH,
            **deep_merge(
                build_secure_phone_being_bound(TEST_PHONE_ID_EXTRA, TEST_PHONE_NUMBER.e164, TEST_OPERATION_ID),
                build_phone_bound(TEST_PHONE_ID, TEST_OTHER_EXIST_PHONE_NUMBER.e164),
            )
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['operation.secure_operation_exists'])

    def test_ok_with_existing_track(self):
        self._test_ok_with_existing_track()

    def test_error_secure_number_already_exists(self):
        self._test_error_secure_number_exists()

    def test_error_phone_not_bound(self):
        self._test_error_phone_not_bound()

    def test_error_account_disabled(self):
        self._test_error_account_disabled()

    def test_error_yasms_temporaryblock(self):
        self._test_error_yasms_temporaryblock(phone_id='1', with_check_cookies=True)

    def test_error_bad_phone_karma(self):
        self._test_error_bad_phone_karma(
            phone_id=str(TEST_PHONE_ID),
            number=TEST_PHONE_NUMBER,
        )

    def test_error_phone_already_exists_not_bound_has_operation(self):
        self._test_error_phone_already_exists_not_bound_has_operation(
            int(TEST_PHONE_NUMBER), phone_id='1',
            with_check_cookies=True,
        )

    def test_ok_account_without_password(self):
        self._test_ok_account_without_password()

    def test_passwordless_account(self):
        self.set_blackbox_response(
            alias_type='social',
            login=TEST_SOCIAL_LOGIN,
            password_is_set=False,
        )

        rv = self.make_request()

        self.assert_response_ok(rv)

        assert_simple_phone_being_securified.check_db(
            self.env.db,
            TEST_UID,
            phone_attributes=dict(
                id=TEST_PHONE_ID,
                number=TEST_PHONE_NUMBER.e164,
            ),
        )

    def test_pharma_denied(self):
        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response(action=ScoreAction.DENY)])
        self.set_blackbox_response()

        rv = self.make_request()

        self.assert_error_response(rv, ['sms_limit.exceeded'])

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('submitted', phone_id=str(TEST_PHONE_ID)),
                self.env.statbox.entry('check_cookies'),
                self.env.statbox.entry('check_phone_karma', phone_id=str(TEST_PHONE_ID)),
                self.env.statbox.entry('pharma_denied', phone_id=str(TEST_PHONE_ID)),
            ],
        )

        assert len(self.env.antifraud_api.requests) == 1
        self.assert_ok_pharma_request(self.env.antifraud_api.requests[0])

        self.env.yasms_private_logger.assert_equals(
            [
                self.env.yasms_private_logger.entry('yasms_enqueued'),
                self.env.yasms_private_logger.entry('yasms_not_sent'),
            ],
        )


class ReplaceSecurePhoneSubmitTestSet(object):
    def _test_user_does_admit_secure_number(self, by_token=False):
        # Пользователь хочет заменить номер и признаёт обладание телефонным
        # номером.
        auth_header = dict(authorization=TEST_AUTH_HEADER) if by_token else dict(cookie=TEST_USER_COOKIE)
        headers = self.build_headers(**auth_header)

        rv = self.make_request(headers=headers)

        self.assert_response_ok(rv)
        self.assert_blackbox_auth_method_ok(by_token)

        self._assert_events_ok()
        self._assert_db_ok()
        self._assert_statbox_ok(with_check_cookies=not by_token)

        requests_to_send_sms = self.env.yasms.get_requests_by_method(u'send_sms')
        eq_(len(requests_to_send_sms), 3)
        self._assert_confirmation_code_sent(phone_number=TEST_REPLACEMENT_PHONE_NUMBER)
        self._assert_confirmation_code_sent(phone_number=TEST_SECURE_PHONE_NUMBER)
        self._assert_notification_sms_sent(requests_to_send_sms[2])

        self._assert_track_ok()
        self.check_account_modification_push_not_sent()

    def _test_error_bad_phone_karma(self, with_check_cookies=False, number=TEST_REPLACEMENT_PHONE_NUMBER, **kwargs):
        self.set_blackbox_response()
        self.env.ufo_api.set_response_value(
            'phones_stats',
            ufo_api_phones_stats_response(
                number,
                data={'phone_number_counter': 100},
            ),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['phone.compromised'])

        entries = [self.env.statbox.entry('submitted')]
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))

        entries.extend([
            self.env.statbox.entry(
                'check_phone_karma',
                karma=str(PhoneKarma.black),
                number=number.masked_format_for_statbox,
                **kwargs
            ),
        ])

        self.env.statbox.assert_has_written(entries)

    def test_ok_by_session(self):
        self._test_user_does_admit_secure_number()

    def test_ok_by_token(self):
        self._test_user_does_admit_secure_number(by_token=True)

    def test_user_does_not_admit_secure_number(self):
        # Пользователь хочет заменить номер, но не признаёт обладание
        # телефонным номером.

        rv = self.make_request(does_user_admit_secure_number=False)

        self.assert_response_ok(rv)

        self._assert_events_ok()
        self._assert_db_ok(is_code_to_secure_number_sent=False)
        self._assert_statbox_ok(is_code_to_secure_number_sent=False, with_check_cookies=True)

        requests_to_send_sms = self.env.yasms.get_requests_by_method(u'send_sms')
        eq_(len(requests_to_send_sms), 1)
        self._assert_confirmation_code_sent(phone_number=TEST_REPLACEMENT_PHONE_NUMBER)

        self._assert_track_ok()

    def test_no_does_user_admit_secure_number_arg(self):
        rv = self.make_request(does_user_admit_secure_number=None)
        self.assert_error_response(rv, [u'does_user_admit_secure_number.empty'])

    def test_invalid_does_user_admit_secure_number_arg(self):
        rv = self.make_request(does_user_admit_secure_number=u'invalid')
        self.assert_error_response(rv, [u'does_user_admit_secure_number.invalid'])

    def test_english_display_language(self):
        # Пользователь понимает английский язык.
        rv = self.make_request(display_language=u'en')

        self.assert_response_ok(rv)

        self._assert_events_ok()
        self._assert_db_ok()
        self._assert_statbox_ok(with_check_cookies=True)

        requests_to_send_sms = self.env.yasms.get_requests_by_method(u'send_sms')
        eq_(len(requests_to_send_sms), 3)
        self._assert_confirmation_code_sent(phone_number=TEST_REPLACEMENT_PHONE_NUMBER, language=u'en')
        self._assert_confirmation_code_sent(phone_number=TEST_SECURE_PHONE_NUMBER, language=u'en')
        self._assert_notification_sms_sent(requests_to_send_sms[2], language=u'en')

        self._assert_track_ok(display_language=u'en')

    def test_no_display_language(self):
        rv = self.make_request(display_language=None)
        self.assert_error_response(rv, [u'display_language.empty'])

    def test_unknown_display_language(self):
        rv = self.make_request(display_language=u'01')
        self.assert_error_response(rv, [u'display_language.invalid'])

    def test_number_and_phone_id(self):
        rv = self.make_request(number=TEST_REPLACEMENT_PHONE_NUMBER.e164, phone_id=TEST_REPLACEMENT_PHONE_ID)
        self.assert_error_response(rv, [u'number_or_phone_id.invalid'])

    def test_neither_number_nor_phone_id(self):
        rv = self.make_request(number=None, phone_id=None)
        self.assert_error_response(rv, [u'number_or_phone_id.invalid'])

    def test_invalid_number(self):
        rv = self.make_request(number=u'02', phone_id=None)
        self.assert_error_response(rv, [u'number.invalid'])

    def test_local_number_and_country(self):
        # Пользователь ввёл местный номер и указал страну, которой номер
        # принадлежит.

        rv = self.make_request(number=LOCAL_TEST_REPLACEMENT_PHONE_NUMBER.original, phone_id=None, country=u'ru')

        self.assert_response_ok(rv, replacement_phone_number=LOCAL_TEST_REPLACEMENT_PHONE_NUMBER)

        self._assert_events_ok()
        self._assert_db_ok()
        self._assert_statbox_ok(with_check_cookies=True)

        requests_to_send_sms = self.env.yasms.get_requests_by_method(u'send_sms')
        eq_(len(requests_to_send_sms), 3)
        self._assert_confirmation_code_sent(phone_number=TEST_REPLACEMENT_PHONE_NUMBER)
        self._assert_confirmation_code_sent(phone_number=TEST_SECURE_PHONE_NUMBER)
        self._assert_notification_sms_sent(requests_to_send_sms[2])

        self._assert_track_ok()

    def test_local_number_and_unknown_country(self):
        rv = self.make_request(number=LOCAL_TEST_REPLACEMENT_PHONE_NUMBER.original, phone_id=None, country=u'01')
        self.assert_error_response(rv, [u'country.invalid'])

    def test_invalid_phone_id(self):
        rv = self.make_request(phone_id=u'invalid', number=None)
        self.assert_error_response(rv, [u'phone_id.invalid'])

    def test_no_operation_in_track(self):
        rv = self.make_request(track_id=self.track_id)
        self.assert_response_ok(rv)

    def test_replacement_phone_does_not_exist(self):
        rv = self.make_request(phone_id=3232, number=None)

        self.assert_error_response(rv, [u'phone.not_found'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted', _exclude=['number']),
            self.env.statbox.entry('check_cookies'),
        ])
        self.assert_events_are_logged(self.env.handle_mock, {})

    def test_replace_with_secure_phone_id(self):
        rv = self.make_request(phone_id=TEST_SECURE_PHONE_ID, number=None)

        self.assert_error_response(rv, [u'action.not_required'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted', _exclude=['number']),
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry(
                'check_phone_karma',
                number=TEST_SECURE_PHONE_NUMBER.masked_format_for_statbox,
            ),
        ])
        self.assert_events_are_logged(self.env.handle_mock, {})

    def test_replace_with_secure_phone_number(self):
        rv = self.make_request(number=TEST_SECURE_PHONE_NUMBER.e164, phone_id=None)

        self.assert_error_response(rv, [u'action.not_required'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted', _exclude=['number']),
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry(
                'check_phone_karma',
                number=TEST_SECURE_PHONE_NUMBER.masked_format_for_statbox,
            ),
        ])
        self.assert_events_are_logged(self.env.handle_mock, {})

    def test_hit_code_per_ip_limit(self):
        TEST_CODE_PER_IP_LIMIT = 2

        with settings_context(**mock_counters(PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(1, 300, TEST_CODE_PER_IP_LIMIT))):
            counter = sms_per_ip.get_counter(TEST_USER_IP)
            for _ in range(TEST_CODE_PER_IP_LIMIT):
                counter.incr(TEST_USER_IP)

            rv = self.make_request()

        self.assert_error_response(rv, ['sms_limit.exceeded'])
        self._assert_statbox_wrote_till_code_not_sent(
            'sms_limit.exceeded',
            with_check_cookies=True,
            reason='ip_limit',
            with_pharma=False,
        )
        self.assert_events_are_logged(self.env.handle_mock, {})

    def test_hit_code_per_phone_number_limit(self):
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_error_xml_response('LIMITEXCEEDED', 'LIMITEXCEEDED'),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['sms_limit.exceeded'])
        self._assert_statbox_wrote_till_code_not_sent(
            'sms_limit.exceeded',
            reason='yasms_phone_limit',
            with_check_cookies=True,
        )
        self.assert_events_are_logged(self.env.handle_mock, {})

    def test_hit_code_per_user_limit(self):
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_error_xml_response('UIDLIMITEXCEEDED', 'UIDLIMITEXCEEDED'),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['sms_limit.exceeded'])
        self._assert_statbox_wrote_till_code_not_sent(
            'sms_limit.exceeded',
            reason='yasms_uid_limit',
            with_check_cookies=True,
        )
        self.assert_events_are_logged(self.env.handle_mock, {})

    def test_send_sms_blocks_phone_number(self):
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_error_xml_response('PERMANENTBLOCK', 'PERMANENTBLOCK'),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['phone.blocked'])
        self._assert_statbox_wrote_till_code_not_sent('phone.blocked', with_check_cookies=True)
        self.assert_events_are_logged(self.env.handle_mock, {})

    def test_error_bad_phone_karma(self):
        self._test_error_bad_phone_karma(with_check_cookies=True)

    def test_send_sms_returns_unexpected_value(self):
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_error_xml_response('UNEXPECTED', 'UNEXPECTED'),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['exception.unhandled'])
        self._assert_statbox_wrote_till_code_not_sent('sms.isnt_sent', with_check_cookies=True)
        self.assert_events_are_logged(self.env.handle_mock, {})

    def test_pharma_denied(self):
        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response(action=ScoreAction.DENY)])
        self.set_blackbox_response()

        rv = self.make_request()

        self.assert_error_response(rv, ['sms_limit.exceeded'])

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('submitted'),
                self.env.statbox.entry('check_cookies'),
                self.env.statbox.entry('check_phone_karma'),
                self.env.statbox.entry('pharma_denied'),
            ],
        )

        assert len(self.env.antifraud_api.requests) == 1
        self.assert_ok_pharma_request(self.env.antifraud_api.requests[0])

        self.env.yasms_private_logger.assert_equals(
            [
                self.env.yasms_private_logger.entry('yasms_enqueued'),
                self.env.yasms_private_logger.entry('yasms_not_sent'),
            ],
        )


class BaseReplaceSecurePhoneTestCase(PhoneManageBaseTestCase):
    base_method_path = '/1/bundle/phone/manage/replace/submit/'
    mode = 'phone_secure_replace'
    step = 'submit'
    with_phone_karma_check = True

    def setUp(self):
        super(BaseReplaceSecurePhoneTestCase, self).setUp()
        self.env.yasms.set_response_value(u'send_sms', yasms_send_sms_response())
        self.env.blackbox.set_response_value(u'phone_bindings', blackbox_phone_bindings_response([]))
        self.env.ufo_api.set_response_value(
            'phones_stats',
            ufo_api_phones_stats_response(TEST_PHONE_NUMBER),
        )
        self.env.antifraud_api.set_response_value('score', antifraud_score_response())

    def make_request(self, headers=None, display_language=TEST_DISPLAY_LANGUAGE,
                     does_user_admit_secure_number=True, number=None,
                     country=None, phone_id=None, track_id=None):
        make_request = super(BaseReplaceSecurePhoneTestCase, self).make_request
        return make_request(
            headers=headers,
            data={
                u'display_language': display_language,
                u'does_user_admit_secure_number': does_user_admit_secure_number,
                u'number': number,
                u'country': country,
                u'phone_id': phone_id,
                u'track_id': track_id,
            },
        )

    def set_blackbox_response(self, scope=TEST_OAUTH_SCOPE, **kwargs):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(scope=scope, **kwargs),
        )

    def assert_response_ok(self, rv, replacement_phone_number=TEST_REPLACEMENT_PHONE_NUMBER):
        eq_(rv.status_code, 200)
        data = json.loads(rv.data)

        eq_(data[u'status'], u'ok')
        eq_(data[u'track_id'], self.track_id)
        eq_(
            data[u'secure_phone'],
            {
                u'id': TEST_SECURE_PHONE_ID,
                u'number': dump_number(TEST_SECURE_PHONE_NUMBER),
                u'operation': {
                    u'id': self._expected_secure_op_id,
                    u'security_identity': 1,
                    u'in_quarantine': False,
                },
            },
        )
        eq_(
            data[u'simple_phone'],
            {
                u'id': TEST_REPLACEMENT_PHONE_ID,
                u'number': dump_number(replacement_phone_number),
                u'operation': {
                    u'id': self._expected_simple_op_id,
                    u'security_identity': int(replacement_phone_number.e164),
                    u'in_quarantine': False,
                },
            },
        )
        ok_(u'account' in data)

    def _predict_operation_ids(self):
        """
        Предсказывает идентификаторы физических операций в логической операции
        замены.

        Необходимо вызывать после подготовки исходных данных в БД.
        """
        next_op_id = predict_next_operation_id(TEST_UID)
        self._expected_secure_op_id = next_op_id
        self._expected_simple_op_id = next_op_id + 1

    def _assert_simple_phone_being_bound_replace_secure(self):
        assert_simple_phone_being_bound_replace_secure.check_db(
            self.env.db,
            TEST_UID,
            {
                u'id': TEST_REPLACEMENT_PHONE_ID,
                u'number': TEST_REPLACEMENT_PHONE_NUMBER.e164,
                u'created': DatetimeNow(),
            },
            {
                u'id': self._expected_simple_op_id,
                u'started': DatetimeNow(),
                u'finished': DatetimeNow() + timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
                u'code_last_sent': DatetimeNow(),
                u'code_send_count': 1,
                u'phone_id2': TEST_SECURE_PHONE_ID,
            },
        )

    def _assert_secure_phone_being_replaced(self, is_code_sent):
        if is_code_sent:
            code_last_sent = DatetimeNow()
            code_send_count = 1
        else:
            code_last_sent = None
            code_send_count = 0
        assert_secure_phone_being_replaced.check_db(
            self.env.db,
            TEST_UID,
            {
                u'id': TEST_SECURE_PHONE_ID,
                u'number': TEST_SECURE_PHONE_NUMBER.e164,
            },
            {
                u'id': self._expected_secure_op_id,
                u'started': DatetimeNow(),
                u'finished': DatetimeNow() + timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
                u'code_last_sent': code_last_sent,
                u'code_send_count': code_send_count,
                u'phone_id2': TEST_REPLACEMENT_PHONE_ID,
            },
        )

    def _assert_notification_sms_sent(self, request_to_send_sms, language=u'ru'):
        sms_notifications.assert_user_notified_about_secure_phone_replacement_started(
            self.env.yasms,
            language,
            TEST_SECURE_PHONE_NUMBER,
            TEST_UID,
        )

    def _assert_track_ok(self, display_language=u'ru'):
        track = self.track_manager.read(self.track_id)
        eq_(track.display_language, display_language)

    def _assert_confirmation_code_sent(self, language='ru', phone_number=TEST_PHONE_NUMBER):
        identity = '%(mode)s.%(step)s.send_confirmation_code' % {'mode': self.mode, 'step': self.step}
        sms_notifications.assert_confirmation_code_sent(self.env.yasms, language, phone_number, identity, TEST_UID)

    def setup_statbox_templates(self):
        super(BaseReplaceSecurePhoneTestCase, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'pharma_allowed',
            _inherit_from=['pharma_allowed'],
            number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'pharma_denied',
            _inherit_from=['pharma_denied'],
            number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
        )
        self.env.yasms_private_logger.bind_entry(
            'yasms_enqueued',
            _inherit_from=['yasms_enqueued'],
            number=TEST_REPLACEMENT_PHONE_NUMBER.e164,
        )
        self.env.yasms_private_logger.bind_entry(
            'yasms_not_sent',
            _inherit_from=['yasms_not_sent'],
            number=TEST_REPLACEMENT_PHONE_NUMBER.e164,
        )
        self.env.statbox.bind_entry(
            'check_phone_karma',
            _inherit_from=['check_phone_karma'],
            number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
        )

    def assert_ok_pharma_request(self, request):
        request_data = json.loads(request.post_args)
        features = PhoneAntifraudFeatures.default(
            sub_channel='dev',
            user_phone_number=TEST_REPLACEMENT_PHONE_NUMBER,
        )
        features.external_id = 'track-{}'.format(self.track_id)
        features.phone_confirmation_method = 'by_sms'
        features.t = TimeNow(as_milliseconds=True)
        features.request_path = '/1/bundle/phone/manage/replace/submit/'
        features.scenario = 'authorize'
        features.add_headers_features(self.build_headers())
        assert request_data == features.as_score_dict()


@with_settings_hosts(
    PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
)
class TestReplaceWithNewPhoneSubmit(BaseReplaceSecurePhoneTestCase,
                                    ReplaceSecurePhoneSubmitTestSet,
                                    GetAccountBySessionOrTokenMixin):
    def setUp(self):
        super(TestReplaceWithNewPhoneSubmit, self).setUp()
        self._phone_id_generator_faker = PhoneIdGeneratorFaker()
        self._phone_id_generator_faker.start()
        self._phone_id_generator_faker.set_list([TEST_REPLACEMENT_PHONE_ID])
        self._build_account(**build_phone_secured(TEST_SECURE_PHONE_ID, TEST_SECURE_PHONE_NUMBER.e164))
        self._predict_operation_ids()

    def tearDown(self):
        self._phone_id_generator_faker.stop()
        del self._phone_id_generator_faker
        super(TestReplaceWithNewPhoneSubmit, self).tearDown()

    def make_request(self, headers=None, number=TEST_REPLACEMENT_PHONE_NUMBER.e164, **kwargs):
        make_request = super(TestReplaceWithNewPhoneSubmit, self).make_request
        return make_request(number=number, headers=headers, **kwargs)

    def _assert_events_ok(self):
        self.env.event_logger.assert_contains(
            event_lines_replace_secure_operation_created(
                uid=TEST_UID,
                replacement_phone_id=TEST_REPLACEMENT_PHONE_ID,
                replacement_phone_number=TEST_REPLACEMENT_PHONE_NUMBER,
                replacement_operation_id=self._expected_simple_op_id,
                secure_phone_id=TEST_SECURE_PHONE_ID,
                secure_phone_number=TEST_SECURE_PHONE_NUMBER,
                secure_operation_id=self._expected_secure_op_id,
            ),
        )

    def _assert_db_ok(self, is_code_to_secure_number_sent=True):
        self._assert_secure_phone_being_replaced(is_code_to_secure_number_sent)
        self._assert_simple_phone_being_bound_replace_secure()

    def _assert_statbox_ok(self, is_code_to_secure_number_sent=True, with_check_cookies=False):
        entries = [self.env.statbox.entry('submitted')]
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend([
            self.env.statbox.entry(
                'check_phone_karma',
                number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
            ),
            self.env.statbox.entry('pharma_allowed'),
        ])
        if is_code_to_secure_number_sent:
            entries += [
                self.env.statbox.entry('pharma_allowed', number=TEST_SECURE_PHONE_NUMBER.masked_format_for_statbox),
            ]
        entries += [
            self.env.statbox.entry(
                'phone_operation_created',
                _exclude=['number', 'phone_id'],
                operation_id='2',
                being_bound_number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
                being_bound_phone_id=str(TEST_REPLACEMENT_PHONE_ID),
                operation_type='replace_secure_phone_with_nonbound_phone',
                secure_number=TEST_SECURE_PHONE_NUMBER.masked_format_for_statbox,
                secure_phone_id=str(TEST_SECURE_PHONE_ID),
            ),
            self.env.statbox.entry(
                'code_sent',
                operation_id='2',
                number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
            ),
        ]
        if is_code_to_secure_number_sent:
            entries += [
                self.env.statbox.entry(
                    'code_sent',
                    operation_id='2',
                    number=TEST_SECURE_PHONE_NUMBER.masked_format_for_statbox,
                ),
                self.env.statbox.entry(
                    'notification_sent',
                    action='notify_user_by_sms_that_secure_phone_replacement_started.notification_sent',
                    number=TEST_SECURE_PHONE_NUMBER.masked_format_for_statbox,
                ),
            ]
        self.env.statbox.assert_has_written(entries)

    def _assert_statbox_wrote_till_code_not_sent(
        self, error, with_pharma=True,
        with_check_cookies=False, **error_kwargs
    ):
        entries = [self.env.statbox.entry('submitted', _exclude=['number'])]
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(self.env.statbox.entry(
                'check_phone_karma',
                number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
            ))
        if with_pharma:
            entries += [
                self.env.statbox.entry('pharma_allowed'),
            ]
        entries += [
            self.env.statbox.entry(
                'send_code_error',
                error=error,
                number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
                **error_kwargs
            ),
        ]
        self.env.statbox.assert_has_written(entries)


@with_settings_hosts(
    PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
)
class TestReplaceWithSimpleBoundPhoneSubmit(BaseReplaceSecurePhoneTestCase,
                                            ReplaceSecurePhoneSubmitTestSet,
                                            GetAccountBySessionOrTokenMixin):
    def setUp(self):
        super(TestReplaceWithSimpleBoundPhoneSubmit, self).setUp()
        self._build_account(
            **deep_merge(
                build_phone_secured(TEST_SECURE_PHONE_ID, TEST_SECURE_PHONE_NUMBER.e164),
                build_phone_bound(TEST_REPLACEMENT_PHONE_ID, TEST_REPLACEMENT_PHONE_NUMBER.e164),
            )
        )
        self._predict_operation_ids()

    def make_request(self, headers=None, phone_id=TEST_REPLACEMENT_PHONE_ID, **kwargs):
        make_request = super(TestReplaceWithSimpleBoundPhoneSubmit, self).make_request
        return make_request(headers=headers, phone_id=phone_id, **kwargs)

    def _assert_events_ok(self):
        self.env.event_logger.assert_contains(
            event_lines_replace_secure_operation_created(
                uid=TEST_UID,
                replacement_phone_id=TEST_REPLACEMENT_PHONE_ID,
                replacement_phone_number=TEST_REPLACEMENT_PHONE_NUMBER,
                replacement_operation_id=self._expected_simple_op_id,
                secure_phone_id=TEST_SECURE_PHONE_ID,
                secure_phone_number=TEST_SECURE_PHONE_NUMBER,
                secure_operation_id=self._expected_secure_op_id,
                is_replacement_phone_bound=True,
            ),
        )

    def _assert_db_ok(self, is_code_to_secure_number_sent=True):
        self._assert_secure_phone_being_replaced(is_code_to_secure_number_sent)
        assert_simple_phone_replace_secure.check_db(
            self.env.db,
            TEST_UID,
            {
                u'id': TEST_REPLACEMENT_PHONE_ID,
                u'number': TEST_REPLACEMENT_PHONE_NUMBER.e164,
            },
            {
                u'id': self._expected_simple_op_id,
                u'started': DatetimeNow(),
                u'finished': DatetimeNow() + timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
                u'code_last_sent': DatetimeNow(),
                u'code_send_count': 1,
                u'phone_id2': TEST_SECURE_PHONE_ID,
            },
        )

    def _assert_statbox_ok(self, is_code_to_secure_number_sent=True, with_check_cookies=False):
        entries = [self.env.statbox.entry('submitted')]
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend([
            self.env.statbox.entry(
                'check_phone_karma',
                number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
            ),
            self.env.statbox.entry('pharma_allowed'),
        ])
        if is_code_to_secure_number_sent:
            entries += [
                self.env.statbox.entry('pharma_allowed', number=TEST_SECURE_PHONE_NUMBER.masked_format_for_statbox),
            ]
        entries += [
            self.env.statbox.entry(
                'replace_secure_phone_operation_created',
                operation_id=str(self._expected_secure_op_id),
            ),
            self.env.statbox.entry(
                'code_sent',
                operation_id=str(self._expected_secure_op_id),
                number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
            ),
        ]
        if is_code_to_secure_number_sent:
            entries += [
                self.env.statbox.entry(
                    'code_sent',
                    operation_id=str(self._expected_secure_op_id),
                    number=TEST_SECURE_PHONE_NUMBER.masked_format_for_statbox,
                ),
                self.env.statbox.entry(
                    'notification_sent',
                    action='notify_user_by_sms_that_secure_phone_replacement_started.notification_sent',
                    number=TEST_SECURE_PHONE_NUMBER.masked_format_for_statbox,
                ),
            ]
        self.env.statbox.assert_has_written(entries)

    def _assert_statbox_wrote_till_code_not_sent(
        self, error,
        with_pharma=True,  with_check_cookies=False,
        **error_kwargs
    ):
        entries = [self.env.statbox.entry('submitted')]
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(
            self.env.statbox.entry(
                'check_phone_karma',
                number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
            )
        )
        if with_pharma:
            entries += [
                self.env.statbox.entry('pharma_allowed'),
            ]
        entries += [
            self.env.statbox.entry(
                'send_code_error',
                error=error,
                number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
                **error_kwargs
            ),
        ]
        self.env.statbox.assert_has_written(entries)


@with_settings_hosts(
    PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
)
class TestReplaceWithBeingBoundPhoneSubmit(BaseReplaceSecurePhoneTestCase,
                                           ReplaceSecurePhoneSubmitTestSet,
                                           GetAccountBySessionOrTokenMixin):
    _SIMPLE_BIND_OPERATION_ID = 1

    def setUp(self):
        super(TestReplaceWithBeingBoundPhoneSubmit, self).setUp()
        self._build_account(
            **deep_merge(
                build_phone_secured(TEST_SECURE_PHONE_ID, TEST_SECURE_PHONE_NUMBER.e164),
                build_phone_being_bound(
                    TEST_REPLACEMENT_PHONE_ID,
                    TEST_REPLACEMENT_PHONE_NUMBER.e164,
                    self._SIMPLE_BIND_OPERATION_ID,
                ),
            )
        )
        self._predict_operation_ids()

    def setup_statbox_templates(self):
        super(TestReplaceWithBeingBoundPhoneSubmit, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'phone_operation_cancelled',
            _inherit_from=['phone_operation_cancelled'],
            _exclude=['number'],
            operation_id=str(self._SIMPLE_BIND_OPERATION_ID),
            operation_type='simple_bind',
        ),

    def make_request(self, headers=None, phone_id=TEST_REPLACEMENT_PHONE_ID, **kwargs):
        make_request = super(TestReplaceWithBeingBoundPhoneSubmit, self).make_request
        return make_request(headers=headers, phone_id=phone_id, **kwargs)

    def _assert_events_ok(self):
        self.env.event_logger.assert_contains(
            event_lines_replace_secure_operation_created(
                uid=TEST_UID,
                replacement_phone_id=TEST_REPLACEMENT_PHONE_ID,
                replacement_phone_number=TEST_REPLACEMENT_PHONE_NUMBER,
                replacement_operation_id=self._expected_simple_op_id,
                secure_phone_id=TEST_SECURE_PHONE_ID,
                secure_phone_number=TEST_SECURE_PHONE_NUMBER,
                secure_operation_id=self._expected_secure_op_id,
                old_bind_operation_id=self._SIMPLE_BIND_OPERATION_ID,
            ),
        )

    def _assert_db_ok(self, is_code_to_secure_number_sent=True):
        self._assert_secure_phone_being_replaced(is_code_to_secure_number_sent)
        self._assert_simple_phone_being_bound_replace_secure()

    def _assert_statbox_ok(self, is_code_to_secure_number_sent=True, with_check_cookies=False):
        entries = [self.env.statbox.entry('submitted')]
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend([
            self.env.statbox.entry(
                'check_phone_karma',
                number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
            ),
            self.env.statbox.entry('phone_operation_cancelled'),
            self.env.statbox.entry('pharma_allowed'),
        ])
        if is_code_to_secure_number_sent:
            entries += [
                self.env.statbox.entry('pharma_allowed', number=TEST_SECURE_PHONE_NUMBER.masked_format_for_statbox),
            ]
        entries += [
            self.env.statbox.entry(
                'phone_operation_created',
                _exclude=['number', 'phone_id'],
                operation_id=str(self._expected_secure_op_id),
                being_bound_number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
                being_bound_phone_id=str(TEST_REPLACEMENT_PHONE_ID),
                operation_type='replace_secure_phone_with_nonbound_phone',
                secure_number=TEST_SECURE_PHONE_NUMBER.masked_format_for_statbox,
                secure_phone_id=str(TEST_SECURE_PHONE_ID),
            ),
            self.env.statbox.entry(
                'code_sent',
                operation_id=str(self._expected_secure_op_id),
                number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
            ),
        ]
        if is_code_to_secure_number_sent:
            entries += [
                self.env.statbox.entry(
                    'code_sent',
                    operation_id=str(self._expected_secure_op_id),
                    number=TEST_SECURE_PHONE_NUMBER.masked_format_for_statbox,
                ),
                self.env.statbox.entry(
                    'notification_sent',
                    action='notify_user_by_sms_that_secure_phone_replacement_started.notification_sent',
                    number=TEST_SECURE_PHONE_NUMBER.masked_format_for_statbox,
                ),
            ]
        self.env.statbox.assert_has_written(entries)

    def _assert_statbox_wrote_till_code_not_sent(
        self, error,
        with_check_cookies=False, with_pharma=True,
        **error_kwargs
    ):
        entries = [self.env.statbox.entry('submitted')]
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend([
            self.env.statbox.entry(
                'check_phone_karma',
                number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
            ),
            self.env.statbox.entry('phone_operation_cancelled'),
        ])
        if with_pharma:
            entries += [
                self.env.statbox.entry('pharma_allowed'),
            ]
        entries += [
            self.env.statbox.entry(
                'code_sent',
                _exclude=['sms_count', 'operation_id', 'sms_id'],
                action='phone_secure_replace.submit.send_confirmation_code',
                error=error,
                number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
                **error_kwargs
            ),
        ]
        self.env.statbox.assert_has_written(entries)

    def test_pharma_denied(self):
        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response(action=ScoreAction.DENY)])
        self.set_blackbox_response()

        rv = self.make_request()

        self.assert_error_response(rv, ['sms_limit.exceeded'])

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('submitted'),
                self.env.statbox.entry('check_cookies'),
                self.env.statbox.entry('check_phone_karma'),
                self.env.statbox.entry('phone_operation_cancelled'),
                self.env.statbox.entry('pharma_denied'),
            ],
        )


@with_settings_hosts(
    PHONE_CONFIRM_CHECK_ANTIFRAUD_SCORE=True,
)
class TestReplaceSecurePhoneSubmit(BaseReplaceSecurePhoneTestCase, GetAccountBySessionOrTokenMixin):
    def setUp(self):
        super(TestReplaceSecurePhoneSubmit, self).setUp()
        self._phone_id_generator_faker = PhoneIdGeneratorFaker()
        self._phone_id_generator_faker.start()
        self._phone_id_generator_faker.set_list([TEST_REPLACEMENT_PHONE_ID])
        self._predict_operation_ids()

    def tearDown(self):
        self._phone_id_generator_faker.stop()
        del self._phone_id_generator_faker
        super(TestReplaceSecurePhoneSubmit, self).tearDown()

    def test_no_secure_phone(self):
        self._build_account()

        rv = self.make_request()

        self.assert_error_response(rv, ['phone_secure.not_found'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies'),
        ])
        self.assert_events_are_logged(self.env.handle_mock, {})

    def test_secure_phone_with_operation(self):
        self._build_account(
            **deep_merge(
                build_phone_secured(TEST_SECURE_PHONE_ID, TEST_SECURE_PHONE_NUMBER.e164),
                build_remove_operation(operation_id=3232, phone_id=TEST_SECURE_PHONE_ID),
            )
        )

        rv = self.make_request()

        self.assert_error_response(rv, [u'operation.exists'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies'),
        ])
        self.assert_events_are_logged(self.env.handle_mock, {})

    def test_replacement_phone_with_operation(self):
        self._build_account(
            **deep_merge(
                build_phone_secured(TEST_SECURE_PHONE_ID, TEST_SECURE_PHONE_NUMBER.e164),
                build_phone_bound(
                    phone_id=TEST_REPLACEMENT_PHONE_ID,
                    phone_number=TEST_REPLACEMENT_PHONE_NUMBER.e164,
                ),
                build_mark_operation(
                    operation_id=3232,
                    phone_number=TEST_REPLACEMENT_PHONE_NUMBER.e164,
                    phone_id=TEST_REPLACEMENT_PHONE_ID,
                ),
            )
        )

        rv = self.make_request()

        self.assert_error_response(rv, [u'operation.exists'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry(
                'check_phone_karma',
                number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
            ),
        ])
        self.assert_events_are_logged(self.env.handle_mock, {})

    def test_account_disabled(self):
        self._build_account(enabled=False)

        rv = self.make_request()

        self.assert_error_response(rv, ['account.disabled'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies'),
        ])
        self.assert_events_are_logged(self.env.handle_mock, {})

    def test_2fa_enabled(self):
        self._build_account(
            **deep_merge(
                dict(
                    crypt_password=None,
                    attributes={u'account.2fa_on': True},
                ),
                build_phone_secured(TEST_SECURE_PHONE_ID, TEST_SECURE_PHONE_NUMBER.e164),
            )
        )

        rv = self.make_request()

        self.assert_response_ok(rv)

    def test_operation_already_started(self):
        self._build_account(
            **deep_merge(
                build_phone_secured(TEST_SECURE_PHONE_ID, TEST_SECURE_PHONE_NUMBER.e164),
                build_phone_bound(
                    phone_id=TEST_REPLACEMENT_PHONE_ID,
                    phone_number=TEST_REPLACEMENT_PHONE_NUMBER.e164,
                ),
                build_simple_replaces_secure_operations(
                    secure_operation_id=TEST_OPERATION_ID2,
                    secure_phone_id=TEST_SECURE_PHONE_ID,
                    simple_operation_id=TEST_OPERATION_ID_EXTRA,
                    simple_phone_id=TEST_REPLACEMENT_PHONE_ID,
                    simple_phone_number=TEST_REPLACEMENT_PHONE_NUMBER.e164,
                ),
            )
        )

        rv = self.make_request()

        self.assert_error_response(rv, [u'operation.exists'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies'),
        ])
        self.assert_events_are_logged(self.env.handle_mock, {})

    def test_passwordless_account(self):
        self._build_account(
            **deep_merge(
                dict(
                    aliases=dict(social=TEST_SOCIAL_LOGIN),
                    crypt_password=None,
                    have_password=False,
                    login=TEST_SOCIAL_LOGIN,
                ),
                build_phone_secured(TEST_SECURE_PHONE_ID, TEST_SECURE_PHONE_NUMBER.e164),
            )
        )

        rv = self.make_request()

        self.assert_response_ok(rv)

    def test_neophonish_account(self):
        self._build_account(
            **deep_merge(
                dict(
                    aliases=dict(neophonish=TEST_NEOPHONISH_LOGIN1),
                    crypt_password=None,
                    have_password=False,
                    login=TEST_NEOPHONISH_LOGIN1,
                ),
                build_phone_secured(TEST_SECURE_PHONE_ID, TEST_SECURE_PHONE_NUMBER.e164),
            )
        )

        rv = self.make_request()

        self.assert_error_response(rv, [u'account.invalid_type'])

    def make_request(self, number=TEST_REPLACEMENT_PHONE_NUMBER.e164, **kwargs):
        make_request = super(TestReplaceSecurePhoneSubmit, self).make_request
        return make_request(number=number, **kwargs)


@with_settings_hosts
class TestRemoveSecureSubmit(SubmitBaseTestCase, GetAccountBySessionOrTokenMixin):
    base_method_path = '/1/bundle/phone/manage/remove_secure/submit/'
    base_request_args = {'display_language': TEST_DISPLAY_LANGUAGE, 'does_user_admit_secure_number': True}

    action = 'remove_secure_submit'
    mode = 'remove_secure'

    def _test_with_track(self, by_token=False):
        auth_header = dict(authorization=TEST_AUTH_HEADER) if by_token else dict(cookie=TEST_USER_COOKIE)
        headers = self.build_headers(**auth_header)
        self._build_account(**build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164))

        rv = self.make_request(
            headers=headers,
            data=dict(
                self.base_request_args,
                display_language='en',
                track_id=self.track_id,
            ),
        )

        self.assert_response_ok(rv)

        self._assert_phone_data_asked_from_blackbox(self.env.blackbox.requests[0], by_token=by_token)
        self._assert_confirmation_code_sent(language='en')
        self._assert_notification_sms_sent(self.env.yasms.requests[1], 'en')

        assert_secure_phone_being_removed.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID},
            {
                'code_send_count': 1,
                'code_checks_count': 0,
                'code_confirmed': None,
                'code_last_sent': DatetimeNow(),
            },
        )

        entries = [self.env.statbox.entry('submitted')]
        if not by_token:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend([
            self.env.statbox.entry(
                'remove_secure_operation_created',
                operation_id=str(TEST_OPERATION_ID),
            ),
            self.env.statbox.entry(
                'notification_sent',
                action='notify_user_by_sms_that_secure_phone_removal_started.notification_sent',
            ),
            self.env.statbox.entry('code_sent'),
        ])

        self.env.statbox.assert_has_written(entries)

        self.assert_events_are_logged(u'remove', is_secure=True, operation_id=1, is_phone_created=False)

        track = self.track_manager.read(self.track_id)
        eq_(track.display_language, 'en')
        self.assert_blackbox_auth_method_ok(by_token)
        self.check_account_modification_push_not_sent()

    def _test_without_track(self, by_token=False):
        auth_header = dict(authorization=TEST_AUTH_HEADER) if by_token else dict(cookie=TEST_USER_COOKIE)
        headers = self.build_headers(**auth_header)
        self._build_account(**build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164))

        rv = self.make_request(headers=headers, with_track_id=False)

        self.assert_response_ok(rv)

        self._assert_phone_data_asked_from_blackbox(self.env.blackbox.requests[0], by_token=by_token)
        self._assert_confirmation_code_sent(language=TEST_DISPLAY_LANGUAGE)
        self._assert_notification_sms_sent(self.env.yasms.requests[1], TEST_DISPLAY_LANGUAGE)

        assert_secure_phone_being_removed.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID},
            {
                'code_send_count': 1,
                'code_checks_count': 0,
                'code_confirmed': None,
                'code_last_sent': DatetimeNow(),
            },
        )

        entries = [self.env.statbox.entry('submitted')]
        if not by_token:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend([
            self.env.statbox.entry(
                'remove_secure_operation_created',
                operation_id=str(TEST_OPERATION_ID),
            ),
            self.env.statbox.entry(
                'notification_sent',
                action='notify_user_by_sms_that_secure_phone_removal_started.notification_sent',
            ),
            self.env.statbox.entry('code_sent'),
        ])

        self.env.statbox.assert_has_written(entries)

        self.assert_events_are_logged(u'remove', is_secure=True, operation_id=1, is_phone_created=False)

        track = self.track_manager.read(self.track_id)
        eq_(track.display_language, 'ru')
        self.assert_blackbox_auth_method_ok(by_token)
        self.check_account_modification_push_not_sent()

    def test_ok_by_session_with_track(self):
        self._test_with_track()

    def test_ok_by_token_with_track(self):
        self._test_with_track(by_token=True)

    def test_ok_by_session_without_track(self):
        self._test_without_track()

    def test_ok_by_token_without_track(self):
        self._test_without_track(by_token=True)

    def test_user_does_not_admit_secure_phone(self):
        self._build_account(**build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164))

        rv = self.make_request(data=dict(self.base_request_args, does_user_admit_secure_number=False))

        self.assert_response_ok(rv, code_sent=False)

        # Никого не уведомляем пока операция не попала в карантин
        eq_(len(self.env.yasms.requests), 0)

        assert_secure_phone_being_removed.check_db(
            self.env.db,
            TEST_UID,
            {'id': TEST_PHONE_ID},
            {
                'code_send_count': 0,
                'code_checks_count': 0,
                'code_confirmed': None,
                'code_last_sent': None,
            },
        )

    def test_no_secure_phone(self):
        build_account_from_session(
            blackbox_faker=self.env.blackbox,
            db_faker=self.env.db,
            uid=TEST_UID,
            login=TEST_LOGIN,
            crypt_password=TEST_PASSWORD_HASH,
            **build_phone_bound(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164)
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['phone_secure.not_found'])

    def test_phone_has_operation(self):
        build_account_from_session(
            blackbox_faker=self.env.blackbox,
            db_faker=self.env.db,
            uid=TEST_UID,
            login=TEST_LOGIN,
            crypt_password=TEST_PASSWORD_HASH,
            **deep_merge(
                build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164),
                build_remove_operation(TEST_OPERATION_ID, TEST_PHONE_ID),
            )
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['operation.exists'])

    def test_invalid_display_language(self):
        rv = self.make_request(data=dict(self.base_request_args, display_language='invalid'))
        self.assert_error_response(rv, ['display_language.invalid'])

    def test_track_not_found(self):
        rv = self.make_request(data=dict(self.base_request_args, track_id=TEST_NON_EXISTENT_TRACK_ID))
        self.assert_error_response(rv, ['track.not_found'])

    def test_2fa_enabled(self):
        build_account_from_session(
            blackbox_faker=self.env.blackbox,
            db_faker=self.env.db,
            uid=TEST_UID,
            login=TEST_LOGIN,
            crypt_password=None,
            **deep_merge(
                dict(attributes={u'account.2fa_on': True}),
                build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164)
            )
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['account.2fa_enabled'])

    def test_sms_2fa_enabled(self):
        build_account_from_session(
            blackbox_faker=self.env.blackbox,
            db_faker=self.env.db,
            uid=TEST_UID,
            login=TEST_LOGIN,
            crypt_password=TEST_PASSWORD_HASH,
            **deep_merge(
                dict(attributes={u'account.sms_2fa_on': True}),
                build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164)
            )
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['account.sms_2fa_enabled'], can_disable_sms_2fa=True)

    def test_error_account_disabled(self):
        self._test_error_account_disabled()

    def test_error_yasms_permanentblock(self):
        self._build_account(**build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164))
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_error_xml_response('msg', code='PERMANENTBLOCK'),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['phone.blocked'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry(
                'send_code_error',
                error='phone.blocked',
            ),
        ])

    def test_passwordless_account(self):
        self._build_account(
            **deep_merge(
                dict(
                    uid=TEST_UID,
                    aliases=dict(social=TEST_SOCIAL_LOGIN),
                    login=TEST_SOCIAL_LOGIN,
                    have_password=False,
                    crypt_password=None,
                ),
                build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164),
            )
        )

        rv = self.make_request()

        self.assert_response_ok(rv)

        assert_secure_phone_being_removed.check_db(
            self.env.db,
            TEST_UID,
            phone_attributes=dict(id=TEST_PHONE_ID),
            operation_attributes=dict(
                code_confirmed=None,
                password_verified=None,
            ),
        )

        self._assert_confirmation_code_sent()
        self._assert_notification_sms_sent(self.env.yasms.requests[1], 'ru')

    def test_user_not_admit_secure_phone__passwordless_account(self):
        self._build_account(
            **deep_merge(
                dict(
                    uid=TEST_UID,
                    aliases=dict(social=TEST_SOCIAL_LOGIN),
                    login=TEST_SOCIAL_LOGIN,
                    have_password=False,
                    crypt_password=None,
                ),
                build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164),
            )
        )

        rv = self.make_request(
            data=dict(
                self.base_request_args,
                does_user_admit_secure_number=False,
            ),
        )

        self.assert_response_ok(rv, code_sent=False)

        assert_secure_phone_being_removed.check_db(
            self.env.db,
            TEST_UID,
            phone_attributes=dict(id=TEST_PHONE_ID),
            operation_attributes=dict(
                code_confirmed=None,
                code_send_count=0,
                password_verified=None,
                # Нет флага начала карантина, карантин нужно начинать только
                # после вызова commit.
                flags=PhoneOperationFlags(),
            ),
        )

        eq_(len(self.env.yasms.requests), 0)
        eq_(len(self.env.mailer.messages), 0)

    def test_neophonish_account(self):
        self._build_account(
            **deep_merge(
                dict(
                    uid=TEST_UID,
                    aliases=dict(neophonish=TEST_NEOPHONISH_LOGIN1),
                    login=TEST_NEOPHONISH_LOGIN1,
                    have_password=False,
                    crypt_password=None,
                ),
                build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164),
            )
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['account.invalid_type'])

    def _assert_phone_data_asked_from_blackbox(self, request, by_token=False):
        method = 'oauth' if by_token else 'sessionid'
        request.assert_query_contains({
            'method': method,
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
        })
        request.assert_contains_attributes({'phones.secure', 'account.2fa_on', 'account.is_disabled'})

    def _assert_notification_sms_sent(self, request, language):
        sms_notifications.assert_user_notified_about_secure_phone_removal_started(
            self.env.yasms,
            language,
            TEST_PHONE_NUMBER,
            TEST_UID,
        )


@with_settings_hosts
class TestAliasifySecureSubmit(SubmitBaseTestCase, GetAccountBySessionOrTokenMixin):
    base_method_path = '/1/bundle/phone/manage/aliasify/submit/'
    base_request_args = {'display_language': TEST_DISPLAY_LANGUAGE}

    action = 'aliasify_secure_submit'
    mode = 'aliasify_secure'

    def set_blackbox_response(self, scope=TEST_OAUTH_SCOPE, account_attributes=None, phones=None,
                              phone_bindings=None, **kwargs):
        if phones is None:
            args = build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164)
            phones = args['phones']
            phone_bindings = args['phone_bindings']

            if account_attributes is None:
                account_attributes = {}
            account_attributes.update(args['attributes'])

        super(TestAliasifySecureSubmit, self).set_blackbox_response(
            account_attributes=account_attributes,
            phones=phones,
            phone_bindings=phone_bindings,
            scope=scope,
            **kwargs
        )

    def _assert_aliasify_secure_operation_created(self):
        assert_secure_phone_being_aliasified.check_db(self.env.db, TEST_UID, {'id': TEST_PHONE_ID})

        phone_fmt = 'phone.%d.' % TEST_PHONE_ID
        op_fmt = phone_fmt + 'operation.1.'
        self.env.event_logger.assert_contains([
            {'uid': str(TEST_UID), 'name': 'action', 'value': 'aliasify_secure_submit'},
            {'uid': str(TEST_UID), 'name': phone_fmt + 'number', 'value': TEST_PHONE_NUMBER.e164},
            {'uid': str(TEST_UID), 'name': op_fmt + 'action', 'value': 'created'},
            {'uid': str(TEST_UID), 'name': op_fmt + 'type', 'value': 'aliasify'},
            {'uid': str(TEST_UID), 'name': op_fmt + 'security_identity', 'value': str(SECURITY_IDENTITY)},
            {'uid': str(TEST_UID), 'name': op_fmt + 'started', 'value': TimeNow()},
            {'uid': str(TEST_UID), 'name': op_fmt + 'finished', 'value': TimeNow(offset=settings.PHONE_QUARANTINE_SECONDS)},
            {'uid': str(TEST_UID), 'name': 'consumer', 'value': 'dev'},
            {'uid': str(TEST_UID), 'name': 'user_agent', 'value': TEST_USER_AGENT},
        ])

    def test_error_account_disabled(self):
        self._test_error_account_disabled()

    def test_error_account_disabled_on_deletion(self):
        self._test_error_account_disabled_on_deletion()

    def test_display_name__ru(self):
        self.set_blackbox_response()

        rv = self.make_request(data=dict(self.base_request_args, display_language='ru'))

        self.assert_response_ok(rv)
        self._assert_confirmation_code_sent(language='ru')

        track = self.track_manager.read(self.track_id)
        eq_(track.display_language, 'ru')

        self.assert_statbox_ok(with_check_cookies=True)
        self.check_account_modification_push_not_sent()

    def test_display_name__en(self):
        self.set_blackbox_response()

        rv = self.make_request(data=dict(self.base_request_args, display_language='en'))

        self.assert_response_ok(rv)
        self._assert_confirmation_code_sent(language='en')

        track = self.track_manager.read(self.track_id)
        eq_(track.display_language, 'en')

    def _test_normal_account(self, by_token=False):
        auth_header = dict(authorization=TEST_AUTH_HEADER) if by_token else dict(cookie=TEST_USER_COOKIE)
        headers = self.build_headers(**auth_header)
        self.set_blackbox_response()

        rv = self.make_request(headers=headers)

        self.assert_response_ok(rv)

        self._assert_aliasify_secure_operation_created()
        assert_phonenumber_alias_missing(self.env.db, TEST_UID)

        track = self.track_manager.read(self.track_id)
        eq_(track.display_language, 'ru')

        self._assert_confirmation_code_sent()
        self.assert_blackbox_auth_method_ok(by_token)

        entries = [self.env.statbox.entry('submitted')]
        if not by_token:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend([
            self.env.statbox.entry('aliasify_secure_operation_created'),
            self.env.statbox.entry('code_sent'),
        ])

        self.env.statbox.assert_has_written(entries)

    def test_ok_by_session(self):
        self._test_normal_account()

    def test_ok_by_token(self):
        self._test_normal_account(by_token=True)

    def test_has_phonenumber_alias(self):
        self.set_blackbox_response(phonenumber_alias=TEST_PHONE_NUMBER.digital)

        rv = self.make_request()

        self.assert_error_response(rv, ['phone_alias.exist'])

    def test_no_secure_phone(self):
        self.set_blackbox_response(phones=[])

        rv = self.make_request()

        self.assert_error_response(rv, ['phone_secure.not_found'])

    def test_secure_phone_has_operation(self):
        self._test_secure_phone_has_operation()

    def test_without_track_id(self):
        self.set_blackbox_response()

        rv = self.make_request(with_track_id=False)

        self.assert_response_ok(rv)

    def test_blackbox_args(self):
        self._test_blackbox_args()

    def test_yasms_temporary_error(self):
        self.set_blackbox_response()
        self.env.yasms.set_response_value('send_sms', yasms_error_xml_response(message='INTERROR', code='INTERROR'))

        rv = self.make_request()

        self.assert_error_response(rv, ['backend.yasms_failed'])

    def test_ok_account_without_password(self):
        self._test_ok_account_without_password()

    def test_passwordless_account(self):
        self.set_blackbox_response(
            password_is_set=False,
            alias_type='social',
            login=TEST_SOCIAL_LOGIN,
        )

        rv = self.make_request()

        self.assert_response_ok(rv)
        self._assert_aliasify_secure_operation_created()


@with_settings_hosts
class TestDealiasifySecureSubmit(SubmitBaseTestCase,
                                 GetAccountBySessionOrTokenMixin):
    base_method_path = '/1/bundle/phone/manage/dealiasify/submit/'
    base_request_args = {'display_language': TEST_DISPLAY_LANGUAGE}

    action = 'dealiasify_secure_submit'
    mode = 'dealiasify_secure'

    def set_blackbox_response(self, scope=TEST_OAUTH_SCOPE, account_attributes=None, phones=None,
                              phonenumber_alias=None, phone_bindings=None, **kwargs):
        if phones is None:
            args = build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164, is_alias=True)
            phones = args['phones']
            phone_bindings = args['phone_bindings']

            if account_attributes is None:
                account_attributes = {}
            account_attributes.update(args['attributes'])

            if phonenumber_alias is None:
                phonenumber_alias = TEST_PHONE_NUMBER.digital

        super(TestDealiasifySecureSubmit, self).set_blackbox_response(
            scope=scope,
            account_attributes=account_attributes,
            phones=phones,
            phone_bindings=phone_bindings,
            phonenumber_alias=phonenumber_alias,
            **kwargs
        )

    def test_error_account_disabled(self):
        self._test_error_account_disabled()

    def test_error_account_disabled_on_deletion(self):
        self._test_error_account_disabled_on_deletion()

    def test_no_phonenumber_alias(self):
        args = build_phone_secured(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164, is_alias=True)
        self.set_blackbox_response(phones=args['phones'], account_attributes=args['attributes'])

        rv = self.make_request()

        self.assert_error_response(rv, ['phone_alias.not_found'])

    def test_secure_phone_has_operation(self):
        self._test_secure_phone_has_operation()

    def test_display_name__ru(self):
        self.set_blackbox_response()

        rv = self.make_request(data=dict(self.base_request_args, display_language='ru'))

        self.assert_response_ok(rv, code_sent=False)

        track = self.track_manager.read(self.track_id)
        eq_(track.display_language, 'ru')
        self.check_account_modification_push_not_sent()

    def test_display_name__en(self):
        self.set_blackbox_response()

        rv = self.make_request(data=dict(self.base_request_args, display_language='en'))

        self.assert_response_ok(rv, code_sent=False)

        track = self.track_manager.read(self.track_id)
        eq_(track.display_language, 'en')

    def test_without_track_id(self):
        self.set_blackbox_response()

        rv = self.make_request(with_track_id=False)

        self.assert_response_ok(rv, code_sent=False)

    def test_ok_account_without_password(self):
        self._test_ok_account_without_password()

    def _test_ok(self, by_token=False):
        auth_header = dict(authorization=TEST_AUTH_HEADER) if by_token else dict(cookie=TEST_USER_COOKIE)
        headers = self.build_headers(**auth_header)
        self.set_blackbox_response()

        rv = self.make_request(headers=headers)

        self.assert_response_ok(rv, code_sent=False)

        self._assert_dealiasify_secure_operation_created()

        track = self.track_manager.read(self.track_id)
        eq_(track.display_language, 'ru')
        self.assert_blackbox_auth_method_ok(by_token)

        entries = [self.env.statbox.entry('submitted')]
        if not by_token:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(self.env.statbox.entry('dealiasify_secure_operation_created'))

        self.env.statbox.assert_has_written(entries)

    def test_ok_by_session(self):
        self._test_ok()

    def test_ok_by_token(self):
        self._test_ok(by_token=True)

    def test_blackbox_args(self):
        self._test_blackbox_args(code_sent=False)

    def test_has_alias_but_no_secure_phone(self):
        # Это не согласованное состояние аккаунта, результат гонки.
        # central уже вернул алиас, а шард ещё не вернул телефоны
        # args = build_phone_bound(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164)
        self.set_blackbox_response(
            phones={},
            account_attributes={},
            phonenumber_alias=TEST_PHONE_NUMBER.digital,
        )
        rv = self.make_request()
        self.assert_error_response(rv, ['phone_secure.not_found'])

    def test_passwordless_account(self):
        self.set_blackbox_response(
            alias_type='social',
            login=TEST_SOCIAL_LOGIN,
            password_is_set=False,
        )

        rv = self.make_request()

        self.assert_response_ok(rv, code_sent=False)

        self._assert_dealiasify_secure_operation_created()

    def _assert_dealiasify_secure_operation_created(self):
        assert_secure_phone_being_dealiasified.check_db(self.env.db, TEST_UID, {'id': TEST_PHONE_ID})

        phone_fmt = 'phone.%d.' % TEST_PHONE_ID
        op_fmt = phone_fmt + 'operation.1.'
        self.env.event_logger.assert_contains([
            {'uid': str(TEST_UID), 'name': 'action', 'value': 'dealiasify_secure_submit'},
            {'uid': str(TEST_UID), 'name': phone_fmt + 'number', 'value': TEST_PHONE_NUMBER.e164},
            {'uid': str(TEST_UID), 'name': op_fmt + 'action', 'value': 'created'},
            {'uid': str(TEST_UID), 'name': op_fmt + 'type', 'value': 'dealiasify'},
            {'uid': str(TEST_UID), 'name': op_fmt + 'security_identity', 'value': str(SECURITY_IDENTITY)},
            {'uid': str(TEST_UID), 'name': op_fmt + 'started', 'value': TimeNow()},
            {'uid': str(TEST_UID), 'name': op_fmt + 'finished', 'value': TimeNow(offset=settings.PHONE_QUARANTINE_SECONDS)},
            {'uid': str(TEST_UID), 'name': 'consumer', 'value': 'dev'},
            {'uid': str(TEST_UID), 'name': 'user_agent', 'value': TEST_USER_AGENT},
        ])
