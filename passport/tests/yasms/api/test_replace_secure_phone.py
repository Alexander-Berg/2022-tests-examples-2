# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)
from functools import partial

from nose_parameterized import parameterized
from passport.backend.api.env import APIEnvironment
from passport.backend.api.test.emails import (
    assert_user_notified_about_secure_phone_replacement_started_on_passwordless_account,
)
from passport.backend.api.yasms.api import ReplaceSecurePhone
from passport.backend.core import Undefined
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_phone_bindings_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.models.phones.faker import (
    assert_no_phone_in_db,
    assert_phone_unbound,
    assert_secure_phone_being_replaced,
    assert_secure_phone_bound,
    assert_simple_phone_being_bound_replace_secure,
    assert_simple_phone_bound,
    assert_simple_phone_replace_secure,
    build_account,
    build_phone_being_bound_replaces_secure_operations,
    build_phone_bound,
    build_phone_secured,
    build_phone_unbound,
    build_simple_replaces_secure_operations,
)
from passport.backend.core.models.phones.phones import OperationInapplicable
from passport.backend.core.runner.context_managers import UPDATE
from passport.backend.core.test.consts import (
    TEST_CONFIRMATION_CODE1,
    TEST_CONFIRMATION_CODE2,
    TEST_DATETIME1,
    TEST_PASSWORD_HASH1,
    TEST_SOCIAL_LOGIN1,
    TEST_USER_AGENT1,
    TEST_USER_IP1,
)
from passport.backend.core.test.events import EventCompositor
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.bit_vector import PhoneOperationFlags
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.core.yasms.test import (
    emails as email_notifications,
    sms as sms_notifications,
)
from passport.backend.utils.common import deep_merge

from .base import BaseYasmsTestCase
from .consts import (
    TEST_OPERATION_ID1,
    TEST_OPERATION_ID2,
)


_LOGIN1 = 'test-login'
_UID1 = 1313
_EMAIL1 = 'test-login@yandex.ru'

_LOGIN2 = 'test-login2'
_UID2 = 1314

_LOGIN3 = 'test-login3'
_UID3 = 1315

_LOGIN_PDD = u'test_login@яндекс.рф'
_UID_PDD = 1130000000000001

_FIRSTNAME1 = u'Андрей'

_PHONE_ID1 = 1
_PHONE_ID2 = 2
_PHONE_ID3 = 3
_PHONE_ID4 = 4

_PHONE_NUMBER1 = PhoneNumber.parse('+79010000001')
_PHONE_NUMBER2 = PhoneNumber.parse('+79020000002')

_ENV = APIEnvironment(user_ip=TEST_USER_IP1, user_agent=TEST_USER_AGENT1)

_ACTION = 'test_action'
_CONSUMER = 'dev'

_EXTERNAL_EVENTS = {
    'action': _ACTION,
    'consumer': _CONSUMER,
}

_MARK_OPERATION_TTL = timedelta(hours=1).total_seconds()
_PHONE_QUARANTINE_SECONDS = timedelta(hours=2).total_seconds()


class BaseReplaceSecurePhoneTestCase(BaseYasmsTestCase):
    def _ReplaceSecurePhone(self, **kwargs):
        kwargs.setdefault('consumer', _CONSUMER)
        kwargs.setdefault('env', _ENV)
        kwargs.setdefault('statbox', self._statbox)
        kwargs.setdefault('blackbox', self._blackbox_builder)
        kwargs.setdefault('yasms', self._yasms)
        kwargs.setdefault('yasms_builder', self._yasms_builder)
        return ReplaceSecurePhone(**kwargs)

    def _replace(self, account=None, **kwargs):
        replacer = self._ReplaceSecurePhone(account=account, **kwargs)
        replacer.submit()
        with UPDATE(account, _ENV, _EXTERNAL_EVENTS):
            replacer.commit()
        replacer.after_commit()

    def _given(
        self,
        is_pdd=False,
        is_being_replaced=False,
        is_replacement_bound=True,
        password=Undefined,
        is_social=False,
        has_phonenumber_alias=False,
    ):
        kwargs = {'firstname': _FIRSTNAME1}
        if is_pdd:
            kwargs.update(
                {
                    'uid': _UID_PDD,
                    'login': _LOGIN_PDD,
                    'aliases': dict(pdd=_LOGIN_PDD),
                },
            )
        elif is_social:
            kwargs.update(
                {
                    'uid': _UID1,
                    'login': TEST_SOCIAL_LOGIN1,
                    'aliases': dict(social=TEST_SOCIAL_LOGIN1),
                },
            )
        else:
            kwargs.update({
                'uid': _UID1,
                'login': _LOGIN1,
                'aliases': dict(portal=_LOGIN1),
                'emails': [
                    self.env.email_toolkit.create_native_email(
                        login=_EMAIL1.split('@')[0],
                        domain=_EMAIL1.split('@')[1],
                    ),
                ],
            })

        if password is Undefined:
            password = TEST_PASSWORD_HASH1
        kwargs.update(crypt_password=password)

        kwargs = deep_merge(
            kwargs,
            build_phone_secured(
                phone_id=_PHONE_ID1,
                phone_number=_PHONE_NUMBER1.e164,
                is_alias=has_phonenumber_alias,
            ),
        )

        if is_being_replaced and is_replacement_bound:
            kwargs = deep_merge(
                kwargs,
                build_phone_bound(
                    _PHONE_ID2,
                    _PHONE_NUMBER2.e164,
                ),
                build_simple_replaces_secure_operations(
                    secure_operation_id=TEST_OPERATION_ID1,
                    secure_phone_id=_PHONE_ID1,
                    simple_operation_id=TEST_OPERATION_ID2,
                    simple_phone_id=_PHONE_ID2,
                    simple_phone_number=_PHONE_NUMBER2.e164,
                ),
            )
        elif is_being_replaced and not is_replacement_bound:
            kwargs = deep_merge(
                kwargs,
                build_phone_unbound(
                    _PHONE_ID2,
                    _PHONE_NUMBER2.e164,
                ),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=TEST_OPERATION_ID1,
                    secure_phone_id=_PHONE_ID1,
                    being_bound_operation_id=TEST_OPERATION_ID2,
                    being_bound_phone_id=_PHONE_ID2,
                    being_bound_phone_number=_PHONE_NUMBER2.e164,
                ),
            )

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        return build_account(db_faker=self.env.db, **kwargs)

    def _setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'phone_replace_operation_created',
            _inherit_from=['base'],
            action='phone_operation_created',
            being_bound_number=_PHONE_NUMBER2.masked_format_for_statbox,
            being_bound_phone_id=str(_PHONE_ID2),
            consumer=_CONSUMER,
            ip=TEST_USER_IP1,
            operation_id='1',
            operation_type='replace_secure_phone_with_nonbound_phone',
            secure_number=_PHONE_NUMBER1.masked_format_for_statbox,
            secure_phone_id=str(_PHONE_ID1),
            uid=str(_UID1),
            user_agent=TEST_USER_AGENT1,
        )
        self.env.statbox.bind_entry(
            'user_notified_that_replacement_started_by_sms',
            _inherit_from=['base'],
            action='notify_user_by_sms_that_secure_phone_replacement_started.notification_sent',
            number=_PHONE_NUMBER1.masked_format_for_statbox,
            sms_id='1',
            uid=str(_UID1),
        )
        self.env.statbox.bind_entry(
            'account_modification_phones_secure_updated',
            _inherit_from=['base'],
            consumer=_CONSUMER,
            entity='phones.secure',
            event='account_modification',
            ip=TEST_USER_IP1,
            new=_PHONE_NUMBER2.masked_format_for_statbox,
            new_entity_id=str(_PHONE_ID2),
            old=_PHONE_NUMBER1.masked_format_for_statbox,
            old_entity_id=str(_PHONE_ID1),
            operation='updated',
            uid=str(_UID1),
            user_agent=TEST_USER_AGENT1,
        )
        self.env.statbox.bind_entry(
            'account_modification_karma_updated',
            _inherit_from=['base'],
            action=_ACTION,
            consumer=_CONSUMER,
            destination='frodo',
            entity='karma',
            event='account_modification',
            ip=TEST_USER_IP1,
            login=_LOGIN1,
            new='6000',
            old='0',
            registration_datetime='-',
            suid='-',
            uid=str(_UID1),
            user_agent=TEST_USER_AGENT1,
        )
        self.env.statbox.bind_entry(
            'phone_confirmed',
            _inherit_from=['base'],
            action='phone_confirmed',
            code_checks_count='0',
            confirmation_time=partial(DatetimeNow, convert_to_datetime=True),
            number=None,
            operation_id='1',
            phone_id=None,
            uid=str(_UID1),
        )
        self.env.statbox.bind_entry(
            'simple_phone_bound',
            _inherit_from=['base'],
            action='simple_phone_bound',
            number=_PHONE_NUMBER2.masked_format_for_statbox,
            operation_id='1',
            phone_id=str(_PHONE_ID2),
            uid=str(_UID1),
        )
        self.env.statbox.bind_entry(
            'secure_phone_replaced',
            _inherit_from=['base'],
            action='secure_phone_replaced',
            new_secure_number=_PHONE_NUMBER2.masked_format_for_statbox,
            new_secure_phone_id=str(_PHONE_ID2),
            old_secure_number=_PHONE_NUMBER1.masked_format_for_statbox,
            old_secure_phone_id=str(_PHONE_ID1),
            operation_id='1',
            uid=str(_UID1),
        )

    def _assert_secure_phone_bound(self, id=None, number=None):
        id = id or _PHONE_ID2
        number = number or _PHONE_NUMBER2
        assert_secure_phone_bound.check_db(
            self.env.db,
            _UID1,
            phone_attributes=dict(
                id=id,
                number=number.e164,
            ),
        )

    def _assert_no_old_secure_phone(self):
        assert_no_phone_in_db(self.env.db, _UID1, _PHONE_ID1, _PHONE_NUMBER1.e164)

    def _assert_no_phone_in_db(self, id, number):
        assert_no_phone_in_db(self.env.db, _UID1, id, number.e164)

    def _assert_user_notified_about_secure_phone_replaced_by_email(self):
        email_notifications.assert_user_notified_about_secure_phone_replaced(
            self.env.mailer,
            'ru',
            _EMAIL1,
            _FIRSTNAME1,
            _LOGIN1,
        )

    def _assert_user_notified_about_secure_phone_replacement_started_by_sms(self):
        sms_notifications.assert_user_notified_about_secure_phone_replacement_started(
            self.env.yasms,
            'ru',
            _PHONE_NUMBER1,
            _UID1,
        )

    def _assert_simple_phone_replaces_secure(
        self,
        number=None,
        in_quarantine=False,
        password_verified=Undefined,
    ):
        number = number or _PHONE_NUMBER2

        phone_operation_flags = PhoneOperationFlags()

        if in_quarantine:
            phone_operation_flags.in_quarantine = True

        if password_verified is Undefined:
            password_verified = DatetimeNow()

        assert_simple_phone_replace_secure.check_db(
            self.env.db,
            _UID1,
            dict(
                id=_PHONE_ID2,
                number=number.e164,
            ),
            dict(
                code_confirmed=DatetimeNow(),
                flags=phone_operation_flags,
                password_verified=password_verified,
            ),
        )

    def _assert_secure_phone_being_replaced(
        self,
        confirmation_code=Undefined,
        in_quarantine=False,
        password_verified=Undefined,
    ):
        if confirmation_code is Undefined:
            confirmation_code = None if in_quarantine else TEST_CONFIRMATION_CODE2

        phone_operation_flags = PhoneOperationFlags()

        if in_quarantine:
            phone_operation_flags.in_quarantine = True

        if password_verified is Undefined:
            password_verified = DatetimeNow()

        assert_secure_phone_being_replaced.check_db(
            self.env.db,
            _UID1,
            dict(
                id=_PHONE_ID1,
                number=_PHONE_NUMBER1.e164,
            ),
            dict(
                code_value=confirmation_code,
                code_confirmed=None,
                flags=phone_operation_flags,
                password_verified=password_verified,
            ),
        )

    def _assert_user_notified_about_secure_phone_replacement_started_by_email(self):
        email_notifications.assert_user_notified_about_secure_phone_replacement_started(
            self.env.mailer,
            'ru',
            _EMAIL1,
            _FIRSTNAME1,
            _LOGIN1,
        )

    def _assert_user_notified_about_secure_phone_replacement_started_on_passwordless_account_by_email(self):
        assert_user_notified_about_secure_phone_replacement_started_on_passwordless_account(
            self.env.mailer,
            'ru',
            _EMAIL1,
            _FIRSTNAME1,
            _LOGIN1,
        )

    def _assert_confirmation_code_sent_by_sms(self, number=None):
        sms_notifications.assert_confirmation_code_sent(
            self.env.yasms,
            'ru',
            number,
            'phone_secure_replace.submit.send_confirmation_code',
            _UID1,
        )

    def _assert_simple_phone_being_bound_replace_secure(
        self,
        code_confirmed=Undefined,
        id=None,
        number=None,
        password_verified=Undefined,
    ):
        if code_confirmed is Undefined:
            code_confirmed = DatetimeNow()

        id = id or _PHONE_ID2

        number = number or _PHONE_NUMBER2

        if password_verified is Undefined:
            password_verified = DatetimeNow()

        phone_operation_flags = PhoneOperationFlags()

        assert_simple_phone_being_bound_replace_secure.check_db(
            self.env.db,
            _UID1,
            dict(
                id=id,
                number=number.e164,
            ),
            dict(
                code_confirmed=code_confirmed,
                flags=phone_operation_flags,
                password_verified=password_verified,
            ),
        )

    def _given_another_phone_owners(self, another_owners):
        userinfo_args_list = list()
        for owner in another_owners:
            userinfo_args = deep_merge(
                dict(
                    login=owner['login'],
                    uid=owner['uid'],
                ),
                build_phone_bound(owner['phone_id'], _PHONE_NUMBER2.e164),
            )
            userinfo_args_list.append(userinfo_args)
            build_account(db_faker=self.env.db, **userinfo_args)

        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response_multiple(userinfo_args_list),
            ],
        )

        phone_bindings = list()
        for owner in another_owners:
            phone_bindings.append(
                dict(
                    type='current',
                    uid=owner['uid'],
                    phone_id=owner['phone_id'],
                    number=_PHONE_NUMBER2.e164,
                    bound=TEST_DATETIME1,
                ),
            )

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response(phone_bindings),
        )


class TestReplaceSecurePhone(BaseReplaceSecurePhoneTestCase):
    _DEFAULT_SETTINGS = dict(
        BaseYasmsTestCase._DEFAULT_SETTINGS,
        PHONE_QUARANTINE_SECONDS=_PHONE_QUARANTINE_SECONDS,
        YASMS_MARK_OPERATION_TTL=_MARK_OPERATION_TTL,
        YASMS_PHONE_BINDING_LIMIT=2,
    )

    def setUp(self):
        super(TestReplaceSecurePhone, self).setUp()

        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )

        self._phone_id_generator_faker.set_list([_PHONE_ID2])

        self.env.code_generator.set_response_side_effect(
            [
                TEST_CONFIRMATION_CODE1,
                TEST_CONFIRMATION_CODE2,
            ],
        )

        self._setup_statbox_templates()

    def test_pdd(self):
        account = self._given(is_pdd=True)

        replace_secure_phone = self._ReplaceSecurePhone(
            account=account,
            phone_number=_PHONE_NUMBER2,
            is_secure_phone_confirmed=True,
            is_simple_phone_confirmed=True,
            is_password_verified=True,
        )

        replace_secure_phone.submit()
        with UPDATE(account, _ENV, _EXTERNAL_EVENTS):
            replace_secure_phone.commit()
        replace_secure_phone.after_commit()

        assert_secure_phone_bound(
            account,
            {'id': _PHONE_ID2, 'number': _PHONE_NUMBER2.e164},
        )
        assert_secure_phone_bound.check_db(
            db_faker=self.env.db,
            uid=_UID_PDD,
            phone_attributes={'id': _PHONE_ID2, 'number': _PHONE_NUMBER2.e164},
            shard_db='passportdbshard2',
        )

        self.assertEqual(len(self.env.mailer.messages), 0)

    def test_phone_replaced__email_notification(self):
        account = self._given()

        replace_secure_phone = self._ReplaceSecurePhone(
            account=account,
            phone_number=_PHONE_NUMBER2,
            is_secure_phone_confirmed=True,
            is_simple_phone_confirmed=True,
            is_password_verified=True,
        )

        replace_secure_phone.submit()
        with UPDATE(account, _ENV, _EXTERNAL_EVENTS):
            replace_secure_phone.commit()

        self._assert_user_notified_about_secure_phone_replaced_by_email()

    def test_phone_replacement_started__email_notification(self):
        account = self._given()

        replace_secure_phone = self._ReplaceSecurePhone(
            account=account,
            phone_number=_PHONE_NUMBER2,
            does_user_admit_secure_number=False,
            is_simple_phone_confirmed=True,
            is_password_verified=True,
        )

        replace_secure_phone.submit()
        with UPDATE(account, _ENV, _EXTERNAL_EVENTS):
            replace_secure_phone.commit()

        self._assert_user_notified_about_secure_phone_replacement_started_by_email()

    def test_does_user_admit_secure_number_inconsistent_regression1(self):
        # Пользователь начинает замену защищённого номера и указывает, что он
        # ему доступен. Затем пользователь пробует восстановить свой аккаунт.
        # В процессе восстановления указывает, что ему недоступен защищённый
        # телефон.

        account = self._given(is_being_replaced=True)

        replace_secure_phone = self._ReplaceSecurePhone(
            account=account,
            phone_number=_PHONE_NUMBER2,
            does_user_admit_secure_number=False,
            is_simple_phone_confirmed=True,
            is_password_verified=True,
        )

        replace_secure_phone.submit()
        with UPDATE(account, _ENV, _EXTERNAL_EVENTS):
            replace_secure_phone.commit()
        replace_secure_phone.after_commit()

        assert_simple_phone_replace_secure(
            account,
            {'id': _PHONE_ID2, 'number': _PHONE_NUMBER2.e164},
            {
                'code_confirmed': DatetimeNow(),
                'password_verified': DatetimeNow(),
            },
        )

        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True
        assert_secure_phone_being_replaced(
            account,
            {'id': _PHONE_ID1, 'number': _PHONE_NUMBER1.e164},
            {
                'code_value': None,
                'code_confirmed': None,
                'password_verified': DatetimeNow(),
                'flags': phone_operation_flags,
            },
        )

    def test_does_user_admit_secure_number_inconsistent_regression2(self):
        # Пользователь начинает замену защищённого номера и указывает, что он
        # ему доступен. Затем пользователь пробует восстановить свой аккаунт.
        # В процессе восстановления указывает, что ему недоступен защищённый
        # телефон.
        # Номер ещё не привязан.

        account = self._given(is_being_replaced=True, is_replacement_bound=False)

        replace_secure_phone = self._ReplaceSecurePhone(
            account=account,
            phone_number=_PHONE_NUMBER2,
            does_user_admit_secure_number=False,
            is_simple_phone_confirmed=True,
            is_password_verified=True,
        )

        replace_secure_phone.submit()
        with UPDATE(account, _ENV, _EXTERNAL_EVENTS):
            replace_secure_phone.commit()
        replace_secure_phone.after_commit()

        assert_simple_phone_replace_secure(
            account,
            {'id': _PHONE_ID2, 'number': _PHONE_NUMBER2.e164},
            {
                'code_confirmed': DatetimeNow(),
                'password_verified': DatetimeNow(),
            },
        )

        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True
        assert_secure_phone_being_replaced(
            account,
            {'id': _PHONE_ID1, 'number': _PHONE_NUMBER1.e164},
            {
                'code_value': None,
                'code_confirmed': None,
                'password_verified': DatetimeNow(),
                'flags': phone_operation_flags,
            },
        )

    def test_wash_karma_with_never_met_before_phone(self):
        account = self._given(
            is_being_replaced=True,
            is_replacement_bound=False,
        )
        op = account.phones.secure.get_logical_operation(self._statbox)
        op.confirm_phone(phone_id=_PHONE_ID1, code=None, should_check_code=False)
        op.confirm_phone(phone_id=_PHONE_ID2, code=None, should_check_code=False)
        op.password_verified = datetime.now()
        account.karma.prefix = 3

        replacer = self._ReplaceSecurePhone(
            account=account,
            phone_number=_PHONE_NUMBER2,
        )
        replacer.submit()
        replacer.commit()

        self.assertEqual(account.phones.secure.id, _PHONE_ID2)
        self.assertEqual(account.karma.prefix, 6)

    def test_dont_wash_karma_if_karma_already_washed(self):
        account = self._given(
            is_being_replaced=True,
            is_replacement_bound=False,
        )
        op = account.phones.secure.get_logical_operation(self._statbox)
        op.confirm_phone(phone_id=_PHONE_ID1, code=None, should_check_code=False)
        op.confirm_phone(phone_id=_PHONE_ID2, code=None, should_check_code=False)
        op.password_verified = datetime.now()
        account.karma.prefix = 2

        replacer = self._ReplaceSecurePhone(
            account=account,
            phone_number=_PHONE_NUMBER2,
        )
        replacer.submit()
        replacer.commit()
        self.assertEqual(account.karma.prefix, 2)

    def test_dont_wash_karma_of_hardened_spammer(self):
        account = self._given(
            is_being_replaced=True,
            is_replacement_bound=False,
        )
        op = account.phones.secure.get_logical_operation(self._statbox)
        op.confirm_phone(phone_id=_PHONE_ID1, code=None, should_check_code=False)
        op.confirm_phone(phone_id=_PHONE_ID2, code=None, should_check_code=False)
        op.password_verified = datetime.now()
        account.karma.prefix = 1

        replacer = self._ReplaceSecurePhone(
            account=account,
            phone_number=_PHONE_NUMBER2,
        )
        replacer.submit()
        replacer.commit()

        self.assertEqual(account.phones.secure.id, _PHONE_ID2)
        self.assertEqual(account.karma.prefix, 1)

    def test_replace_fully_confirmed(self):
        account = self._given()

        self._replace(
            account=account,
            is_password_verified=True,
            is_secure_phone_confirmed=True,
            is_simple_phone_confirmed=True,
            phone_number=_PHONE_NUMBER2,
        )

        self._assert_secure_phone_bound(number=_PHONE_NUMBER2)
        self._assert_no_old_secure_phone()

        self.assertEqual(len(self.env.mailer.messages), 1)
        self._assert_user_notified_about_secure_phone_replaced_by_email()

        self.assertEqual(len(self.env.yasms.requests), 1)
        self._assert_user_notified_about_secure_phone_replacement_started_by_sms()

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('phone_replace_operation_created'),
                self.env.statbox.entry('user_notified_that_replacement_started_by_sms'),
                self.env.statbox.entry('account_modification_phones_secure_updated'),
                self.env.statbox.entry('account_modification_karma_updated'),
                self.env.statbox.entry(
                    'phone_confirmed',
                    number=_PHONE_NUMBER2.masked_format_for_statbox,
                    phone_id=str(_PHONE_ID2),
                ),
                self.env.statbox.entry(
                    'phone_confirmed',
                    number=_PHONE_NUMBER1.masked_format_for_statbox,
                    phone_id=str(_PHONE_ID1),
                ),
                self.env.statbox.entry('simple_phone_bound'),
                self.env.statbox.entry('secure_phone_replaced'),
            ],
        )

        phone_operation_finished = TimeNow(offset=_MARK_OPERATION_TTL)
        e = EventCompositor(uid=str(_UID1))

        with e.prefix('phone.%d.' % _PHONE_ID1):
            e('number', _PHONE_NUMBER1.e164)
            with e.prefix('operation.1.'):
                e('action', 'created')
                e('finished', phone_operation_finished)
                e('phone_id2', str(_PHONE_ID2))
                e('security_identity', '1')
                e('started', TimeNow())
                e('type', 'replace')

        with e.prefix('phone.%d.' % _PHONE_ID2):
            e('action', 'created')
            e('created', TimeNow())
            e('number', _PHONE_NUMBER2.e164)
            with e.prefix('operation.2.'):
                e('action', 'created')
                e('finished', phone_operation_finished)
                e('phone_id2', str(_PHONE_ID1))
                e('security_identity', _PHONE_NUMBER2.digital)
                e('started', TimeNow())
                e('type', 'bind')

        e('action', 'phone_secure_replace_submit')
        e('consumer', _CONSUMER)
        e('user_agent', TEST_USER_AGENT1)

        e('info.karma_prefix', '6')
        e('info.karma_full', '6000')

        with e.prefix('phone.%d.' % _PHONE_ID1):
            e('action', 'deleted')
            e('number', _PHONE_NUMBER1.e164)
            with e.prefix('operation.1.'):
                e('action', 'deleted')
                e('security_identity', '1')
                e('type', 'replace')

        with e.prefix('phone.%d.' % _PHONE_ID2):
            e('action', 'changed')
            e('bound', TimeNow())
            e('confirmed', TimeNow())
            e('number', _PHONE_NUMBER2.e164)
            with e.prefix('operation.2.'):
                e('action', 'deleted')
                e('security_identity', _PHONE_NUMBER2.digital)
                e('type', 'bind')
            e('secured', TimeNow())

        e('phones.secure', str(_PHONE_ID2))

        e('action', _ACTION)
        e('consumer', _CONSUMER)
        e('user_agent', TEST_USER_AGENT1)

        self.env.event_logger.assert_events_are_logged_with_order(e.to_lines())

    def test_replace_fully_confirmed__passwordless_account(self):
        account = self._given(password=None)

        self._replace(
            account=account,
            is_secure_phone_confirmed=True,
            is_simple_phone_confirmed=True,
            phone_number=_PHONE_NUMBER2,
        )

        self._assert_secure_phone_bound(number=_PHONE_NUMBER2)
        self._assert_no_old_secure_phone()

        self.assertEqual(len(self.env.mailer.messages), 1)
        self._assert_user_notified_about_secure_phone_replaced_by_email()

        self.assertEqual(len(self.env.yasms.requests), 1)
        self._assert_user_notified_about_secure_phone_replacement_started_by_sms()

    @parameterized.expand(
        [
            (None,),
            (True,),
        ],
    )
    def test_replace_totally_unconfirmed(self, does_user_admit_secure_number):
        account = self._given()

        replacer = self._ReplaceSecurePhone(
            does_user_admit_secure_number=does_user_admit_secure_number,
            account=account,
            phone_number=_PHONE_NUMBER2,
        )

        with self.assertRaises(OperationInapplicable) as assertion:
            replacer.submit()

        self._assert_secure_phone_bound(id=_PHONE_ID1, number=_PHONE_NUMBER1)

        self._assert_no_phone_in_db(id=_PHONE_ID2, number=_PHONE_NUMBER2)

        self.assertEqual(assertion.exception.need_password_verification, True)

        self.assertEqual(
            assertion.exception.need_confirmed_phones,
            {
                account.phones.by_id(_PHONE_ID1),
                account.phones.by_id(_PHONE_ID2),
            },
        )

        self.assertEqual(len(self.env.mailer.messages), 0)
        self.assertEqual(len(self.env.yasms.requests), 0)

    def test_replace_totally_unconfirmed_and_not_admitted_phone(self):
        account = self._given()

        replacer = self._ReplaceSecurePhone(
            does_user_admit_secure_number=False,
            account=account,
            phone_number=_PHONE_NUMBER2,
        )

        with self.assertRaises(OperationInapplicable):
            replacer.submit()

        self._assert_secure_phone_bound(id=_PHONE_ID1, number=_PHONE_NUMBER1)

        self._assert_no_phone_in_db(id=_PHONE_ID2, number=_PHONE_NUMBER2)

        self.assertEqual(len(self.env.mailer.messages), 0)
        self.assertEqual(len(self.env.yasms.requests), 0)

    def test_replace_fully_confirmed_but_not_admitted_phone(self):
        account = self._given()

        self._replace(
            account=account,
            does_user_admit_secure_number=False,
            is_password_verified=True,
            is_simple_phone_confirmed=True,
            phone_number=_PHONE_NUMBER2,
        )

        self._assert_simple_phone_replaces_secure(number=_PHONE_NUMBER2, in_quarantine=True)
        self._assert_secure_phone_being_replaced(in_quarantine=True)

        self.assertEqual(len(self.env.mailer.messages), 1)
        self._assert_user_notified_about_secure_phone_replacement_started_by_email()

        self.assertEqual(len(self.env.yasms.requests), 1)
        self._assert_user_notified_about_secure_phone_replacement_started_by_sms()

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('phone_replace_operation_created'),
                self.env.statbox.entry('user_notified_that_replacement_started_by_sms'),
                self.env.statbox.entry('account_modification_karma_updated'),
                self.env.statbox.entry(
                    'phone_confirmed',
                    number=_PHONE_NUMBER2.masked_format_for_statbox,
                    phone_id=str(_PHONE_ID2),
                ),
                self.env.statbox.entry('simple_phone_bound'),
            ],
        )

        phone_operation_finished = TimeNow(offset=_MARK_OPERATION_TTL)
        e = EventCompositor(uid=str(_UID1))

        with e.prefix('phone.%d.' % _PHONE_ID1):
            e('number', _PHONE_NUMBER1.e164)
            with e.prefix('operation.1.'):
                e('action', 'created')
                e('finished', phone_operation_finished)
                e('phone_id2', str(_PHONE_ID2))
                e('security_identity', '1')
                e('started', TimeNow())
                e('type', 'replace')

        with e.prefix('phone.%d.' % _PHONE_ID2):
            e('action', 'created')
            e('created', TimeNow())
            e('number', _PHONE_NUMBER2.e164)
            with e.prefix('operation.2.'):
                e('action', 'created')
                e('finished', phone_operation_finished)
                e('phone_id2', str(_PHONE_ID1))
                e('security_identity', _PHONE_NUMBER2.digital)
                e('started', TimeNow())
                e('type', 'bind')

        e('action', 'phone_secure_replace_submit')
        e('consumer', _CONSUMER)
        e('user_agent', TEST_USER_AGENT1)

        e('info.karma_prefix', '6')
        e('info.karma_full', '6000')

        quarantine_finished = TimeNow(offset=_PHONE_QUARANTINE_SECONDS)

        with e.prefix('phone.%d.' % _PHONE_ID1):
            e('number', _PHONE_NUMBER1.e164)
            with e.prefix('operation.1.'):
                e('action', 'changed')
                e('finished', quarantine_finished)
                e('password_verified', TimeNow())
                e('security_identity', '1')
                e('type', 'replace')

        with e.prefix('phone.%d.' % _PHONE_ID2):
            e('action', 'changed')
            e('bound', TimeNow())
            e('confirmed', TimeNow())
            e('number', _PHONE_NUMBER2.e164)

            with e.prefix('operation.2.'):
                e('action', 'deleted')
                e('security_identity', _PHONE_NUMBER2.digital)
                e('type', 'bind')

            with e.prefix('operation.3.'):
                e('action', 'created')
                e('code_confirmed', TimeNow())
                e('finished', quarantine_finished)
                e('password_verified', TimeNow())
                e('phone_id2', str(_PHONE_ID1))
                e('security_identity', _PHONE_NUMBER2.digital)
                e('started', TimeNow())
                e('type', 'mark')

        e('action', _ACTION)
        e('consumer', _CONSUMER)
        e('user_agent', TEST_USER_AGENT1)

        self.env.event_logger.assert_events_are_logged_with_order(e.to_lines())

    def test_replace_fully_confirmed_but_not_admitted_phone__passwordless_account(self):
        account = self._given(password=None)

        self._replace(
            account=account,
            does_user_admit_secure_number=False,
            is_secure_phone_confirmed=False,
            is_simple_phone_confirmed=True,
            phone_number=_PHONE_NUMBER2,
        )

        self._assert_simple_phone_replaces_secure(
            in_quarantine=True,
            number=_PHONE_NUMBER2,
            password_verified=None,
        )
        self._assert_secure_phone_being_replaced(in_quarantine=True, password_verified=None)

        self.assertEqual(len(self.env.mailer.messages), 1)
        self._assert_user_notified_about_secure_phone_replacement_started_on_passwordless_account_by_email()

    @parameterized.expand(
        [
            (None,),
            (True,),
        ],
    )
    def test_long_lived_replace_totally_unconfirmed(self, does_user_admit_secure_number):
        account = self._given()

        replacer = self._ReplaceSecurePhone(
            is_long_lived=True,
            does_user_admit_secure_number=does_user_admit_secure_number,
            account=account,
            phone_number=_PHONE_NUMBER2,
        )

        replacer.submit()

        self._assert_simple_phone_being_bound_replace_secure(
            code_confirmed=None,
            number=_PHONE_NUMBER2,
            password_verified=None,
        )

        self._assert_secure_phone_being_replaced(password_verified=None)

        self.assertEqual(len(self.env.mailer.messages), 0)

        self.assertEqual(len(self.env.yasms.requests), 3)

        self._assert_user_notified_about_secure_phone_replacement_started_by_sms()
        self._assert_confirmation_code_sent_by_sms(number=_PHONE_NUMBER1)
        self._assert_confirmation_code_sent_by_sms(number=_PHONE_NUMBER2)

        with self.assertRaises(OperationInapplicable) as assertion:
            replacer.commit()

        self.assertEqual(assertion.exception.need_password_verification, True)

        self.assertEqual(
            assertion.exception.need_confirmed_phones,
            {
                account.phones.by_id(_PHONE_ID1),
                account.phones.by_id(_PHONE_ID2),
            },
        )

    def test_long_lived_replace_totally_unconfirmed_and_not_admitted_phone(self):
        account = self._given()

        replacer = self._ReplaceSecurePhone(
            is_long_lived=True,
            does_user_admit_secure_number=False,
            account=account,
            phone_number=_PHONE_NUMBER2,
        )

        replacer.submit()

        self._assert_simple_phone_being_bound_replace_secure(
            code_confirmed=None,
            number=_PHONE_NUMBER2,
            password_verified=None,
        )

        self._assert_secure_phone_being_replaced(confirmation_code=None, password_verified=None)

        self.assertEqual(len(self.env.mailer.messages), 0)

        self.assertEqual(len(self.env.yasms.requests), 1)
        self._assert_confirmation_code_sent_by_sms(number=_PHONE_NUMBER2)

        with self.assertRaises(OperationInapplicable):
            replacer.commit()

    def test_old_phone_is_alias_on_social(self):
        account = self._given(
            has_phonenumber_alias=True,
            is_social=True,
            password=None,
        )

        self._replace(
            account=account,
            is_secure_phone_confirmed=True,
            is_simple_phone_confirmed=True,
            phone_number=_PHONE_NUMBER2,
        )

        self._assert_secure_phone_bound(number=_PHONE_NUMBER2)
        self._assert_no_old_secure_phone()

    def test_unbind_phone_from_other_accounts(self):
        account = self._given()

        self._given_another_phone_owners(
            [
                dict(
                    login=_LOGIN2,
                    phone_id=_PHONE_ID2,
                    uid=_UID2,
                ),
                dict(
                    login=_LOGIN3,
                    phone_id=_PHONE_ID3,
                    uid=_UID3,
                ),
            ],
        )

        self._phone_id_generator_faker.set_list([_PHONE_ID4])

        self.env.code_generator.set_response_value(TEST_CONFIRMATION_CODE1)

        self._replace(
            account=account,
            is_password_verified=True,
            is_secure_phone_confirmed=True,
            is_simple_phone_confirmed=True,
            phone_number=_PHONE_NUMBER2,
        )

        self._assert_secure_phone_bound(number=_PHONE_NUMBER2, id=_PHONE_ID4)
        self._assert_no_old_secure_phone()

        assert_phone_unbound.check_db(
            self.env.db,
            uid=_UID2,
            phone_attributes=dict(id=_PHONE_ID2),
        )
        assert_simple_phone_bound.check_db(
            self.env.db,
            uid=_UID3,
            phone_attributes=dict(id=_PHONE_ID3),
        )
