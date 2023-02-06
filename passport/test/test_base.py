# -*- coding: utf-8 -*-
from datetime import datetime
import json
import time

from nose.tools import eq_
from passport.backend.api.common.processes import PROCESS_RESTORE
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD,
    TEST_DEFAULT_BIRTHDAY,
    TEST_DEFAULT_FIRSTNAME,
    TEST_DEFAULT_HINT_ANSWER,
    TEST_DEFAULT_HINT_QUESTION,
    TEST_DEFAULT_LASTNAME,
    TEST_DEFAULT_LOGIN,
    TEST_DEFAULT_REGISTRATION_DATETIME,
    TEST_DEFAULT_UID,
    TEST_EMAILS,
    TEST_HOST,
    TEST_IP,
    TEST_MAIL_DB_ID,
    TEST_MAIL_SUID,
    TEST_OLD_SERIALIZED_PASSWORD,
    TEST_OPERATION_ID1,
    TEST_OPERATION_ID2,
    TEST_PASSWORD_QUALITY,
    TEST_PASSWORD_QUALITY_VERSION,
    TEST_PDD_DOMAIN,
    TEST_PDD_LOGIN,
    TEST_PDD_UID,
    TEST_PHONE2,
    TEST_PHONE_ID,
    TEST_PHONE_ID2,
    TEST_PHONE_ID3,
    TEST_PHONE_MASKED_FOR_STATBOX,
    TEST_PHONE_OPERATION_START_DELTA,
    TEST_SOCIAL_LOGIN,
    TEST_USER_AGENT,
    TEST_USER_ENTERED_LOGIN,
    TEST_YANDEXUID_COOKIE,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_hosted_domains_response,
    blackbox_userinfo_response,
)
from passport.backend.core.counters import restore_counter
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.models.account import ACCOUNT_DISABLED_ON_DELETION
from passport.backend.core.models.phones.faker import (
    build_aliasify_secure_operation,
    build_phone_being_bound_replaces_secure_operations,
    build_phone_bound,
    build_phone_secured,
    build_phone_unbound,
    build_remove_operation,
    build_simple_replaces_secure_operations,
)
from passport.backend.core.support_link_types import (
    SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
    SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeSpan
from passport.backend.core.tracks.model import (
    RestoreTrack,
    TrackCounterField,
    TrackFlagField,
    TrackJsonSerializableField,
    TrackListField,
)
from passport.backend.core.tracks.serializer import LIST_ROOT
from passport.backend.utils.common import (
    deep_merge,
    remove_none_values,
)
from six import string_types


eq_ = iterdiff(eq_)


def remove_zero_values(dict_):
    return {key: value for (key, value) in dict_.items() if value != 0}


def assert_tracks_equal(track, other_track):
    eq_(track._data, other_track._data)
    eq_(track._counters, other_track._counters)
    eq_(track._lists, other_track._lists)


def set_track_values(track, params, is_created=False):
    for field, expected_value in params.items():
        field_object = getattr(RestoreTrack, field)
        if isinstance(field_object, TrackFlagField):
            track._data[field] = tskv_bool(expected_value)
        elif isinstance(field_object, TrackJsonSerializableField):
            track._data[field] = json.dumps(expected_value)
        elif isinstance(field_object, TrackCounterField):
            track._counters[field] = expected_value
        elif isinstance(field_object, TrackListField):
            if not expected_value and is_created:
                expected_value = [LIST_ROOT]
            track._lists[field] = expected_value
        else:
            track._data[field] = expected_value
    track._counters = remove_zero_values(track._counters)
    track._data = remove_none_values(track._data)


class RestoreTestUtilsMixin(object):
    def default_userinfo_response(self, login=TEST_DEFAULT_LOGIN, firstname=TEST_DEFAULT_FIRSTNAME,
                                  lastname=TEST_DEFAULT_LASTNAME, birthday=TEST_DEFAULT_BIRTHDAY,
                                  password=TEST_OLD_SERIALIZED_PASSWORD,
                                  registration_datetime=TEST_DEFAULT_REGISTRATION_DATETIME,
                                  password_creating_required=False, password_changing_required=False, language='ru',
                                  hintq=TEST_DEFAULT_HINT_QUESTION, hinta=TEST_DEFAULT_HINT_ANSWER,
                                  emails=TEST_EMAILS, emails_native=True, emails_validated=True,
                                  subscribed_to=None, with_password=True, password_quality=TEST_PASSWORD_QUALITY,
                                  phone=None, is_phone_secure=False, is_phone_bank=False,
                                  is_secure_phone_being_removed=False,
                                  is_simple_phone_replaces_secure=False, is_phone_being_bound_replaces_secure=False,
                                  is_secure_phone_being_aliasified=False,
                                  alias_type='portal', aliases=None, sms_2fa_on=False, **kwargs):
        params = dict(
            login=login,
            dbfields={
                'userinfo.reg_date.uid': registration_datetime,
            },
            attributes={
                'person.firstname': firstname,
                'person.lastname': lastname,
                'person.birthday': birthday,
                'person.language': language,
            },
            aliases={
                alias_type: login,
            },
        )
        if hinta and hintq:
            params['dbfields'].update({
                'userinfo_safe.hintq.uid': hintq,
                'userinfo_safe.hinta.uid': hinta,
            })
        if aliases is not None:
            params['aliases'] = aliases
        if with_password:
            params['dbfields'].update({
                'password_quality.quality.uid': password_quality,
                'password_quality.version.uid': TEST_PASSWORD_QUALITY_VERSION,
            })
            params['attributes']['password.encrypted'] = password
        if password_creating_required:
            params['dbfields'].update({
                'subscription.login_rule.100': 1,
                'subscription.suid.100': 1,
            })
        if emails is not None:
            params.update(
                emails=[
                    {
                        'address': address,
                        'native': emails_native,
                        'validated': emails_validated,
                    } if isinstance(address, string_types) else address for address in emails
                ],
            )
            if any(isinstance(email, string_types) for email in emails):
                # индекс @yandex.ru в https://a.yandex-team.ru/arc_vcs/passport/backend/api/tests/views/bundle/restore/test/base_test_data.py?rev=2b1fcd63026fab6f43b641f37ef770d2944b2821#L60
                params['emails'][2]['default'] = True

        params['subscribed_to'] = subscribed_to
        if subscribed_to is not None and 2 in subscribed_to:
            params['dbfields'].update({
                'hosts.db_id.2': TEST_MAIL_DB_ID,
                'subscription.suid.2': TEST_MAIL_SUID,
            })
        else:
            params['dbfields'].update({
                'hosts.db_id.2': None,
                'subscription.suid.2': None,
            })

        if sms_2fa_on:
            params['attributes'].update({
                'account.sms_2fa_on': '1',
                'account.forbid_disabling_sms_2fa': '1',  # этот атрибут не должен влиять на рестор
            })

        if phone:
            phone_builder = build_phone_secured if is_phone_secure else build_phone_bound
            phone = phone_builder(
                TEST_PHONE_ID,
                phone,
                is_default=False,
                is_bank=is_phone_bank,
            )
            kwargs = deep_merge(kwargs, phone)
            if is_secure_phone_being_removed:
                operation = build_remove_operation(
                    operation_id=TEST_OPERATION_ID1,
                    phone_id=TEST_PHONE_ID,
                    started=datetime.now() - TEST_PHONE_OPERATION_START_DELTA,
                )
                kwargs = deep_merge(kwargs, operation)
            if is_phone_being_bound_replaces_secure:
                extra_phone = build_phone_unbound(TEST_PHONE_ID2, TEST_PHONE2)
                operations = build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=TEST_OPERATION_ID1,
                    secure_phone_id=TEST_PHONE_ID,
                    being_bound_operation_id=TEST_OPERATION_ID2,
                    being_bound_phone_id=TEST_PHONE_ID2,
                    being_bound_phone_number=TEST_PHONE2,
                    started=datetime.now() - TEST_PHONE_OPERATION_START_DELTA,
                )
                kwargs = deep_merge(kwargs, extra_phone, operations)
            if is_simple_phone_replaces_secure:
                extra_phone = build_phone_bound(TEST_PHONE_ID2, TEST_PHONE2)
                operations = build_simple_replaces_secure_operations(
                    secure_operation_id=TEST_OPERATION_ID1,
                    secure_phone_id=TEST_PHONE_ID,
                    simple_operation_id=TEST_OPERATION_ID2,
                    simple_phone_id=TEST_PHONE_ID2,
                    simple_phone_number=TEST_PHONE2,
                    started=datetime.now() - TEST_PHONE_OPERATION_START_DELTA,
                )
                kwargs = deep_merge(kwargs, extra_phone, operations)
            if is_secure_phone_being_aliasified:
                operation = build_aliasify_secure_operation(
                    operation_id=TEST_OPERATION_ID1,
                    phone_id=TEST_PHONE_ID,
                )
                kwargs = deep_merge(kwargs, operation)

        params = deep_merge(params, kwargs)

        if password_changing_required:
            params['dbfields'].update({'subscription.login_rule.8': 4})
            params['attributes']['password.forced_changing_reason'] = '1'
        return blackbox_userinfo_response(**params)

    def assert_track_unchanged(self):
        new_track = self.track_manager.read(self.track_id)
        assert_tracks_equal(new_track, self.orig_track)

    def get_headers(self, host=None, user_ip=None, cookie=None, user_agent=None):
        return mock_headers(
            host=host or TEST_HOST,
            user_agent=user_agent or TEST_USER_AGENT,
            cookie=cookie or 'yandexuid=%s' % TEST_YANDEXUID_COOKIE,
            user_ip=user_ip or TEST_IP,
        )

    def set_counter_value(self, track, name, value):
        counter = getattr(track, name)
        counter.reset()
        for _ in range(value):
            counter.incr()

    def check_pin_check_counter(self, expected_value, db='passportdbshard1'):
        if expected_value == 0:
            self.env.db.check_missing(
                'attributes',
                'account.totp.failed_pin_checks_count',
                uid=TEST_DEFAULT_UID,
                db=db,
            )
        else:
            self.env.db.check(
                'attributes',
                'account.totp.failed_pin_checks_count',
                str(expected_value),
                uid=TEST_DEFAULT_UID,
                db=db,
            )

    def set_track_values(self, **params):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            set_track_values(track, params)
        self.orig_track = track.snapshot()

    def assert_track_updated(self, is_created=False, **params):
        """
        Общий метод проверки трека. Убеждаемся, что произошли заданные
        изменения и только они.
        """
        orig_track = self.orig_track
        set_track_values(orig_track, params, is_created=is_created)

        new_track = self.track_manager.read(self.track_id)
        assert_tracks_equal(new_track, orig_track)


@with_settings_hosts(
    ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD=TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD,
)
class RestoreBaseTestCase(BaseBundleTestViews, RestoreTestUtilsMixin):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value(mock_grants(grants={'restore': ['base']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('restore')
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def make_request(self, data, headers=None):
        if 'track_id' not in data:
            data.update(track_id=self.track_id)
        return self.env.client.post(
            self.default_url + '?consumer=dev',
            data=data,
            headers=headers,
        )

    def setup_statbox_templates(self, sms_retriever_kwargs=None):
        # записи, которые относятся к форматированию SMS под SmsRetriever в Андроиде
        sms_retriever_kwargs = sms_retriever_kwargs or {}

        self.env.statbox.bind_entry(
            'local_base',
            mode='restore',
            track_id=self.track_id,
            ip=TEST_IP,
            host=TEST_HOST,
            user_agent=TEST_USER_AGENT,
            consumer='dev',
            login=TEST_DEFAULT_LOGIN,
            is_suggested_login='0',
            uid=str(TEST_DEFAULT_UID),
            yandexuid=TEST_YANDEXUID_COOKIE,
            step=self.restore_step,
            selected_methods_order='',
        )
        self.env.statbox.bind_entry(
            'password_validation_error',
            action='password_validation_error',
            track_id=self.track_id,
        )
        self.env.statbox.bind_entry(
            'finished_with_state',
            _inherit_from='local_base',
            action='finished_with_state',
            state='complete_pdd',
        )
        self.env.statbox.bind_entry(
            'finished_with_error',
            _inherit_from='local_base',
            action='finished_with_error',
            error='account.not_found',
        )
        self.env.statbox.bind_entry(
            'finished_with_error_with_sms',
            _inherit_from='finished_with_error',
            error='phone.blocked',
        )
        self.env.statbox.bind_entry(
            'passed',
            _inherit_from='local_base',
            action='passed',
        )
        self.env.statbox.bind_entry(
            'passed_with_sms',
            _inherit_from='passed',
            sms_id='1',
            sms_count='1',
            **sms_retriever_kwargs
        )
        self.env.statbox.bind_entry(
            'call_with_code',
            _inherit_from='local_base',
            action='call_with_code',
            calls_count='1',
            call_session_id='123',
            operation='confirm',
        )
        self.env.statbox.bind_entry(
            'account_modification',
            event='account_modification',
            operation=None,
            consumer='dev',
            ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
        )
        self.env.statbox.bind_entry(
            'save_phone',
            _inherit_from='local_base',
            operation='save',
        )
        self.env.statbox.bind_entry(
            'phone_operation_created',
            action='phone_operation_created',
            number=TEST_PHONE_MASKED_FOR_STATBOX,
            phone_id=str(TEST_PHONE_ID),
            operation_id=str(TEST_OPERATION_ID1),
            ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
            consumer='dev',
        )
        self.env.statbox.bind_entry(
            'phone_operation_cancelled',
            _inherit_from='local_base',
            action='phone_operation_cancelled',
            operation_id=str(TEST_OPERATION_ID1),
        )
        self.env.statbox.bind_entry(
            'phone_confirmed',
            _inherit_from='local_base',
            action='phone_confirmed',
            number=TEST_PHONE_MASKED_FOR_STATBOX,
            phone_id=str(TEST_PHONE_ID),
            operation_id=str(TEST_OPERATION_ID1),
        )
        self.env.statbox.bind_entry(
            'phone_confirmed_by_call',
            _inherit_from='local_base',
            action='enter_code',
            operation='confirm',
            good='1',
            time_passed=TimeSpan(value=1),
        )
        self.env.statbox.bind_entry(
            'secure_phone_bound',
            _inherit_from='local_base',
            action='secure_phone_bound',
            number=TEST_PHONE_MASKED_FOR_STATBOX,
            phone_id=str(TEST_PHONE_ID),
            operation_id=str(TEST_OPERATION_ID1),
        )
        self.env.statbox.bind_entry(
            'simple_phone_bound',
            _inherit_from='local_base',
            action='simple_phone_bound',
            number=TEST_PHONE_MASKED_FOR_STATBOX,
            phone_id=str(TEST_PHONE_ID3),
            operation_id=str(TEST_OPERATION_ID2),
        )
        self.env.statbox.bind_entry(
            'sms_notification_sent',
            _inherit_from='local_base',
            action='notify_user_by_sms_that_secure_phone_replacement_started.notification_sent',
            number=TEST_PHONE_MASKED_FOR_STATBOX,
            sms_id='1',
        )
        self.env.statbox.bind_entry(
            'email_validator_deleted_all',
            action='deleted_all',
            uid=str(TEST_DEFAULT_UID),
            mode='email_validation',
        )

    def set_track_values(self, process_name=PROCESS_RESTORE, uid=TEST_DEFAULT_UID,
                         login=TEST_DEFAULT_LOGIN, user_entered_login=TEST_USER_ENTERED_LOGIN,
                         is_captcha_checked=True, is_captcha_recognized=True, **params):
        params.update(
            process_name=process_name,
            login=login,
            user_entered_login=user_entered_login,
            is_captcha_checked=is_captcha_checked,
            is_captcha_recognized=is_captcha_recognized,
        )
        if uid:
            params['uid'] = str(uid)
        params = remove_none_values(params)
        super(RestoreBaseTestCase, self).set_track_values(**params)

    def assert_blackbox_userinfo_called(self, uid=str(TEST_DEFAULT_UID), call_index=0):
        self.env.blackbox.get_requests_by_method('userinfo')[call_index].assert_post_data_contains(
            {
                'method': 'userinfo',
                'uid': uid,
                'emails': 'getall',
                'getphones': 'all',
                'getphoneoperations': '1',
                'getphonebindings': 'all',
                'aliases': 'all_with_hidden',
            },
        )
        self.env.blackbox.get_requests_by_method('userinfo')[call_index].assert_contains_attributes({
            'phones.default',
            'phones.secure',
            'account.deletion_operation_started_at',
        })

    def base_expected_response(self, user_entered_login=TEST_USER_ENTERED_LOGIN, with_track=True, **kwargs):
        kwargs['user_entered_login'] = user_entered_login
        if with_track:
            kwargs['track_id'] = self.track_id
        return kwargs


class CommonTestsMixin(object):
    """
    Общие тесты для всех ручек автоматического восстановления, кроме submit
    """
    def test_invalid_track_type_fails(self):
        """Работаем только с restore-треком"""
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(resp, ['track.invalid_state'])

    def track_invalid_state_case(self, extra_response_params=None, **track_kwargs):
        """Общий случай невалидного состояния трека правильного типа"""
        self.set_track_values(**track_kwargs)

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(resp, ['track.invalid_state'], **(extra_response_params or {}))
        self.assert_track_unchanged()

    def test_invalid_no_process_name_fails(self):
        """Трек без заданного процесса не принимаем"""
        self.track_invalid_state_case(process_name=None)

    def test_invalid_process_name_fails(self):
        """Неподдерживаемый процесс в треке не принимаем"""
        self.track_invalid_state_case(process_name='unknown_process')

    is_uid_preset_in_track = True

    def test_no_uid_in_track_fails(self):
        """Трек без UID не принимаем, почти во всех ручках"""
        if self.is_uid_preset_in_track:
            self.track_invalid_state_case(uid=None)

    def test_unexpected_restore_state_fails(self):
        """Трек с неожиданным состоянием восстановления не принимаем"""
        self.track_invalid_state_case(restore_state='bad state')


class AccountValidityTestsMixin(object):
    """
    Тесты проверки применимости аккаунта для автоматического восстановления
    """

    account_validity_tests_extra_statbox_params = {}
    account_validity_tests_excluded_statbox_params = []
    is_uid_preset_in_track = True  # UID предустановлен в треке до вызова
    is_track_or_key_used = True  # Ручка работает с треком или существующим ключом восстановления
    test_invalid_support_link_types = True  # Можно ли тестировать обработку невалидных для аккаунта саппортских ссылок
    require_enabled_account = True
    allow_missing_password_with_portal_alias = False

    def make_statbox_entry(self, error=None, state=None, **kwargs):
        exclude = self.account_validity_tests_excluded_statbox_params + kwargs.pop('_exclude', [])
        if error:
            entry = self.env.statbox.entry('finished_with_error', error=error, _exclude=exclude, **kwargs)
        else:
            entry = self.env.statbox.entry('finished_with_state', state=state, _exclude=exclude, **kwargs)
        current_restore_method = self.track_manager.read(self.track_id).current_restore_method
        if current_restore_method:
            entry['current_restore_method'] = current_restore_method
        entry.update(self.account_validity_tests_extra_statbox_params)
        return entry

    def test_account_not_found_fails(self):
        """Аккаунт не найден"""
        self.env.blackbox.set_response_value(
            'userinfo',
            self.default_userinfo_response(uid=None),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['account.not_found'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        extra_params = {}
        if not self.is_uid_preset_in_track:
            # Хак для случая, когда известен только логин, введенный пользователем
            extra_params = {'login': TEST_USER_ENTERED_LOGIN, '_exclude': ['uid']}
        if not self.is_track_or_key_used:
            extra_params = {'_exclude': ['login']}
        entry = self.make_statbox_entry(error='account.not_found', **extra_params)
        self.env.statbox.assert_has_written([entry])

    def test_account_disabled_fails(self):
        """Аккаунт отключен"""
        if not self.require_enabled_account:
            return
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(enabled=False),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(
            resp,
            ['account.disabled'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        entry = self.make_statbox_entry(error='account.disabled')
        self.env.statbox.assert_has_written([entry])

    def test_account_disabled_on_deletion_too_long_ago_fails(self):
        """Аккаунт заблокирован при удалении, время карантина вышло"""
        if not self.require_enabled_account:
            return
        deletion_started_at = time.time() - TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD.total_seconds()
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                attributes={
                    'account.deletion_operation_started_at': deletion_started_at,
                    'account.is_disabled': str(ACCOUNT_DISABLED_ON_DELETION),
                },
            ),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(
            resp,
            ['account.disabled'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        entry = self.make_statbox_entry(error='account.disabled')
        self.env.statbox.assert_has_written([entry])

    def test_pdd_account_disabled_on_deletion_recently__domain_disabled__fails(self):
        """ПДД-аккаунт недавно заблокирован при удалении, но его домен заблокирован и восстановление невозможно"""
        if not self.require_enabled_account:
            return
        deletion_started_at = time.time() - TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD.total_seconds() + 100
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                subscribed_to=[102],
                attributes={
                    'account.deletion_operation_started_at': deletion_started_at,
                    'account.is_disabled': str(ACCOUNT_DISABLED_ON_DELETION),
                },
                domain_enabled=False,
            ),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(
            resp,
            ['account.disabled'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        entry = self.make_statbox_entry(
            error='account.disabled',
            login=TEST_PDD_LOGIN,
            uid=str(TEST_PDD_UID),
        )
        self.env.statbox.assert_has_written([entry])

    def test_account_disabled_on_deletion_with_no_operation_fails(self):
        """Аккаунт заблокирован при удалении, операции в базе нет"""
        if not self.require_enabled_account:
            return
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                attributes={
                    'account.is_disabled': str(ACCOUNT_DISABLED_ON_DELETION),
                },
            ),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(
            resp,
            ['account.disabled'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        entry = self.make_statbox_entry(error='account.disabled')
        self.env.statbox.assert_has_written([entry])

    def test_incomplete_pdd_redirect(self):
        """Недорегистрированный пользователь ПДД получает приглашение дорегистрироваться"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(login=TEST_PDD_LOGIN, uid=TEST_PDD_UID, alias_type='pdd'),
        )
        self.set_track_values(user_entered_login=TEST_PDD_LOGIN)

        resp = self.make_request(self.query_params(login=TEST_PDD_LOGIN), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.base_expected_response(state='complete_pdd', user_entered_login=TEST_PDD_LOGIN)
        )
        self.assert_track_unchanged()
        entry = self.make_statbox_entry(
            state='complete_pdd',
            login=TEST_PDD_LOGIN,
            uid=str(TEST_PDD_UID),
        )
        self.env.statbox.assert_has_written([entry])

    def test_pdd_cannot_change_password_ok(self):
        """Пользователь ПДД с запретом смены пароля не может воспользоваться восстановлением"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                login=TEST_PDD_LOGIN,
                uid=TEST_PDD_UID,
                subscribed_to=[102],
                alias_type='pdd',
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, can_users_change_password='0', domain=TEST_PDD_DOMAIN),
        )
        self.set_track_values(user_entered_login=TEST_PDD_LOGIN)

        resp = self.make_request(self.query_params(login=TEST_PDD_LOGIN), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.base_expected_response(state='password_change_forbidden', user_entered_login=TEST_PDD_LOGIN)
        )
        self.assert_track_unchanged()
        entry = self.make_statbox_entry(
            state='password_change_forbidden',
            login=TEST_PDD_LOGIN,
            uid=str(TEST_PDD_UID),
        )
        self.env.statbox.assert_has_written([entry])

    def test_password_not_set_fails(self):
        """У обычного пользователя не установлен пароль"""
        if self.allow_missing_password_with_portal_alias:
            return
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(password=''),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(
            resp,
            ['account.without_password'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        entry = self.make_statbox_entry(error='account.without_password')
        self.env.statbox.assert_has_written([entry])

    def test_pdd_password_not_set_fails(self):
        """У ПДД-пользователя не установлен пароль"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                login=TEST_PDD_LOGIN,
                uid=TEST_PDD_UID,
                subscribed_to=[102],
                alias_type='pdd',
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, can_users_change_password='1', domain=TEST_PDD_DOMAIN),
        )
        self.set_track_values(user_entered_login=TEST_PDD_LOGIN)

        resp = self.make_request(self.query_params(login=TEST_PDD_LOGIN), self.get_headers())

        self.assert_error_response(
            resp,
            ['account.without_password'],
            **self.base_expected_response(user_entered_login=TEST_PDD_LOGIN)
        )
        self.assert_track_unchanged()
        entry = self.make_statbox_entry(
            error='account.without_password',
            login=TEST_PDD_LOGIN,
            uid=str(TEST_PDD_UID),
        )
        self.env.statbox.assert_has_written([entry])

    def test_social_password_not_set_ok(self):
        """У социального пользователя не установлен пароль"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                login=TEST_SOCIAL_LOGIN,
                alias_type='social',
                password='',
            ),
        )
        self.set_track_values(user_entered_login=TEST_SOCIAL_LOGIN)

        resp = self.make_request(self.query_params(login=TEST_SOCIAL_LOGIN), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.base_expected_response(state='complete_social', user_entered_login=TEST_SOCIAL_LOGIN)
        )
        self.assert_track_unchanged()
        entry = self.make_statbox_entry(state='complete_social', login=TEST_SOCIAL_LOGIN)
        self.env.statbox.assert_has_written([entry])

    def test_with_portal_and_social_aliases_password_not_set_ok(self):
        """У пользователя, имеющего и портальный, и социальный алиасы, не установлен пароль"""
        if self.allow_missing_password_with_portal_alias:
            return
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                password='',
                aliases={
                    'portal': TEST_DEFAULT_LOGIN,
                    'social': TEST_SOCIAL_LOGIN,
                },
            ),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.base_expected_response(state='complete_social')
        )
        self.assert_track_unchanged()
        entry = self.make_statbox_entry(state='complete_social')
        self.env.statbox.assert_has_written([entry])

    def test_autoregistered_password_changing_required_redirect(self):
        """Автозарегистрированный пользователь с требованием смены пароля"""
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(password_creating_required=True, subscribed_to=[100]),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_ok_response(
            resp,
            **self.base_expected_response(state='complete_autoregistered')
        )
        self.assert_track_unchanged()
        entry = self.make_statbox_entry(state='complete_autoregistered')
        self.env.statbox.assert_has_written([entry])

    def test_restoration_key_older_than_logout_fails(self):
        """Использован ключ восстановления, который был создан до момента логаута"""
        if not self.is_track_or_key_used:
            return
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                attributes={
                    'revoker.web_sessions': int(time.time()),
                },
            ),
        )
        self.set_track_values(
            restoration_key_created_at=str(int(time.time() - 2 * 60 * 60)),
        )

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['account.global_logout'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        entry = self.make_statbox_entry(error='account.global_logout')
        self.env.statbox.assert_has_written([entry])

    def test_track_older_than_logout_fails(self):
        """Использован трек, который был создан до момента логаута"""
        if not self.is_track_or_key_used:
            return
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                attributes={
                    'revoker.web_sessions': int(time.time() + 60 * 60),
                },
            ),
        )
        self.set_track_values()

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['account.global_logout'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        entry = self.make_statbox_entry(error='account.global_logout')
        self.env.statbox.assert_has_written([entry])

    def test_support_link_force_hint_restoration_not_available_for_2fa_fails(self):
        """Нельзя использовать ссылку для восстановления по КВ/КО для 2ФА пользователя"""
        if not self.test_invalid_support_link_types:
            return
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(
                with_password=False,
                attributes={
                    'account.2fa_on': '1',
                },
            ),
        )
        self.set_track_values(support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION)

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(
            resp,
            ['account.invalid_type'],
            **self.base_expected_response()
        )
        entry = self.make_statbox_entry(
            error='account.invalid_type',
            support_link_type=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
        )
        self.env.statbox.assert_has_written([entry])

    def test_support_link_force_phone_restoration_not_available_for_non_2fa_fails(self):
        """Нельзя использовать ссылку для восстановления исключительно по телефону для не-2ФА пользователя"""
        if not self.test_invalid_support_link_types:
            return
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(),
        )
        self.set_track_values(support_link_type=SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION)

        resp = self.make_request(self.query_params(), self.get_headers())

        self.assert_error_response(
            resp,
            ['account.invalid_type'],
            **self.base_expected_response()
        )
        entry = self.make_statbox_entry(
            error='account.invalid_type',
            support_link_type=SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION,
        )
        self.env.statbox.assert_has_written([entry])


class CommonMethodTestsMixin(object):
    common_tests_mixin_extra_statbox_context = {}

    def global_counter_overflow_case(self, method):
        """Глобальный счетчик попыток восстановления переполнен"""
        self.set_track_values()
        counter = restore_counter.get_per_ip_buckets()
        for _ in range(counter.limit):
            counter.incr(TEST_IP)
        eq_(counter.get(TEST_IP), counter.limit)

        resp = self.make_request(self.query_params(), headers=self.get_headers())

        self.assert_error_response(
            resp,
            ['rate.limit_exceeded'],
            **self.base_expected_response()
        )
        self.assert_track_unchanged()
        eq_(counter.get(TEST_IP), counter.limit)  # счетчик не увеличивается
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'finished_with_error',
                error='rate.limit_exceeded',
                current_restore_method=method,
                **self.common_tests_mixin_extra_statbox_context
            ),
        ])
