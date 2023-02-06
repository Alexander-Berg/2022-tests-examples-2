# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.yasms import grants
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.builders.yasms.faker import (
    yasms_error_xml_response,
    yasms_register_response,
    yasms_send_sms_response,
)
from passport.backend.core.conf import settings
from passport.backend.core.dbmanager.exceptions import DBError
from passport.backend.core.models.phones.faker import (
    assert_no_phone_in_db,
    assert_phone_unbound,
    assert_phonenumber_alias_removed,
    assert_secure_phone_being_bound,
    assert_secure_phone_being_replaced,
    assert_secure_phone_bound,
    assert_simple_phone_being_bound,
    assert_simple_phone_bound,
    assert_simple_phone_replace_secure,
    build_phone_being_bound,
    build_phone_being_bound_replaces_secure_operations,
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.bit_vector.bit_vector import (
    PhoneBindingsFlags,
    PhoneOperationFlags,
)
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.core.xml.test_utils import assert_xml_response_equals
from passport.backend.utils.common import deep_merge
from passport.backend.utils.time import datetime_to_integer_unixtime as to_unixtime

from .base import BaseTestCase


UID = 4814
CONFIRMATION_CODE = u'3232'
RUSSIAN_CONFIRMATION_MESSAGE = u'Ваш код подтверждения: {{code}}. Наберите его в поле ввода.'
ENGLISH_CONFIRMATION_MESSAGE = u'Your confirmation code is {{code}}. Please enter it in the text field.'
TEST_DATE = datetime(2005, 1, 12, 4, 2, 10)
FIRSTNAME = u'Андрей'
LOGIN = u'andrey1931'
EMAIL = u'%s@yandex-team.ru' % LOGIN
ALIAS_SID = 65
PHONISH_LOGIN = u'phne-login'

PHONE_NUMBER = u'+79000000001'
PHONE_NUMBER_MASKED = PhoneNumber.parse(PHONE_NUMBER).masked_format_for_statbox
PHONE_NUMBER_INTERNATIONAL = PhoneNumber.parse(PHONE_NUMBER).international
PHONE_NUMBER_DIGITAL = PhoneNumber.parse(PHONE_NUMBER).digital
PHONE_ID = 9944
OPERATION_ID = 5502

PHONE_NUMBER_EXTRA = u'+79000000002'
PHONE_NUMBER_EXTRA_MASKED = PhoneNumber.parse(PHONE_NUMBER_EXTRA).masked_format_for_statbox
PHONE_NUMBER_EXTRA_INTERNATIONAL = PhoneNumber.parse(PHONE_NUMBER_EXTRA).international
PHONE_ID_EXTRA = 4949
OPERATION_ID_EXTRA = 2505

UID_EXTRA = 1000
USER_AGENT = u'curl'


class BaseRegisterViewBlackboxTestCase(BaseTestCase):
    default_headers = {
        u'Ya-Client-User-Agent': USER_AGENT,
    }

    def setUp(self):
        super(BaseRegisterViewBlackboxTestCase, self).setUp()
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_send_sms_response(sms_id=1),
        )
        self._phone_id_generator_faker.set_list([PHONE_ID])
        self.env.code_generator.set_return_value(CONFIRMATION_CODE)

        self.env.blackbox.set_response_value(
            u'phone_bindings',
            # Для обеления
            blackbox_phone_bindings_response([]),
        )
        self._setup_statbox_entries()

    def _given_account(self, **kwargs):
        kwargs = self._build_account_args(**kwargs)
        user_info = blackbox_userinfo_response(**kwargs)
        self.env.blackbox.set_response_value(u'userinfo', user_info)
        self.env.db.serialize(user_info)

    def _build_account_args(self, **kwargs):
        kwargs.setdefault(u'uid', UID)
        kwargs.setdefault(u'firstname', FIRSTNAME)
        kwargs.setdefault(u'login', LOGIN)
        kwargs = deep_merge({'aliases': {'portal': LOGIN}}, kwargs)
        kwargs.setdefault(u'language', u'ru')
        kwargs.setdefault(
            u'emails',
            [
                self.env.email_toolkit.create_native_email(
                    login=EMAIL.split(u'@')[0],
                    domain=EMAIL.split(u'@')[1],
                ),
            ],
        )
        # Есть пароль
        kwargs.setdefault(
            u'crypt_password',
            u'1:password',
        )
        return kwargs

    def _assert_response_ok(self, response, uid=UID, phone_number=PHONE_NUMBER,
                            phone_id=PHONE_ID, revalidated=False):
        eq_(response.status_code, 200)
        assert_xml_response_equals(
            response,
            yasms_register_response(
                uid,
                phone_number,
                phone_id,
                revalidated,
                u'utf-8',
            ),
        )

    def _setup_statbox_entries(self):
        self.env.statbox.bind_base(
            ip=u'7.2.5.5',
            consumer=u'hunter',
        )
        self.env.statbox.bind_entry(
            u'simple_bind_operation_created',
            action=u'phone_operation_created',
            uid=str(UID),
            phone_id=str(PHONE_ID),
        )
        self.env.statbox.bind_entry(
            u'secure_bind_operation_created',
            action=u'phone_operation_created',
            uid=str(UID),
            phone_id=str(PHONE_ID),
        )
        self.env.statbox.bind_entry(
            u'code_sent',
            action=u'register.register.send_confirmation_code.code_sent',
            uid=str(UID),
        )
        self.env.statbox.bind_entry(
            u'phone_unbound',
            action=u'register.phone_unbound',
        )
        self.env.statbox.bind_entry(
            u'phone_confirmed',
            action=u'register.register.phone_confirmed',
            uid=str(UID),
            phone_id=str(PHONE_ID),
        )
        self.env.statbox.bind_entry(
            u'simple_phone_bound',
            action=u'register.register.simple_phone_bound',
            uid=str(UID),
            phone_id=str(PHONE_ID),
        )
        self.env.statbox.bind_entry(
            u'secure_phone_bound',
            action=u'register.register.secure_phone_bound',
            uid=str(UID),
            phone_id=str(PHONE_ID),
        )
        self.env.statbox.bind_entry(
            u'phone_operation_replaced',
            action=u'register.register.phone_operation_replaced',
            uid=str(UID),
            phone_id=str(PHONE_ID),
        )
        self.env.statbox.bind_entry(
            u'frodo_karma',
            action=u'register',
            uid=str(UID),
            login=LOGIN,
            registration_datetime=u'-',
        )

    def make_request(self, sender=u'dev', uid=UID, number=PHONE_NUMBER,
                     secure=None, lang=None, withoutsms=None, ts=None,
                     revalidate=None, ignore_bindlimit=None, headers=None):
        self.response = self.env.client.get(
            u'/yasms/register',
            query_string={
                u'sender': sender,
                u'uid': uid,
                u'number': number,
                u'secure': secure,
                u'lang': lang,
                u'withoutsms': withoutsms,
                u'ts': ts,
                u'revalidate': revalidate,
                u'ignore_bindlimit': ignore_bindlimit,
            },
            headers=headers or self.default_headers,
        )
        return self.response


@with_settings_hosts(
    SMS_VALIDATION_RESEND_TIMEOUT=5,
)
class TestRegisterView(BaseRegisterViewBlackboxTestCase):
    def test_local_ukrainian_phone_number(self):
        self.assign_all_grants()
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(uid=UID),
        )

        response = self.make_request(number=u'0953123456')

        eq_(response.status_code, 200)
        self.assert_response_is_error(u'Bad phone number format', u'BADNUMFORMAT')

    def test_account_not_found(self):
        """
        Учётная запись не найдена.
        """
        self.assign_grants([grants.REGISTRATOR])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        response = self.make_request()

        eq_(response.status_code, 200)
        self.assert_response_is_error(
            u'User not found',
            u'NOUSER',
        )

    def test_account_disabled__ok(self):
        """
        Учётная запись заблокирована.
        """
        self.assign_grants([grants.REGISTRATOR])
        self._given_account(
            uid=UID,
            enabled=False,
            phones=[],
            phone_operations=[],
        )

        response = self.make_request(uid=UID, number=PHONE_NUMBER)

        self._assert_response_ok(response)

    def test_bind_secure__account_does_not_have_password__fail(self):
        """
        На учётной записи не установлен пароль.
        """
        self.assign_grants([grants.REGISTRATOR])
        self._given_account(
            uid=UID,
            phones=[],
            phone_operations=[],
            dbfields={},
            crypt_password=None,
        )

        self.make_request(uid=UID, number=PHONE_NUMBER, secure=True)

        self.assert_response_is_xml_error(
            u'User without password cannot have secure number',
            u'CANT_HAVE_SECURE_NUMBER',
        )

    def test_bind_simple__phone_bound__fail(self):
        """
        С учётной записью уже связан данный номер.
        """
        self.assign_grants([grants.REGISTRATOR])
        self._given_account(
            uid=UID,
            **build_phone_bound(PHONE_ID, PHONE_NUMBER)
        )

        self.make_request(uid=UID, number=PHONE_NUMBER)

        self.assert_response_is_xml_error(
            u'Number already exists',
            u'NUMEXISTS',
        )

    def test_bind_secure__secure_phone_bound__fail(self):
        """
        С учётной записью уже связан защищённый номер.
        """
        self.assign_grants([grants.REGISTRATOR])
        self._given_account(
            uid=UID,
            **build_phone_secured(PHONE_ID, PHONE_NUMBER_EXTRA)
        )

        self.make_request(uid=UID, number=PHONE_NUMBER, secure=True)

        self.assert_response_is_xml_error(
            u'User already has valid secure number',
            u'SECURE_NUMBER_EXISTS',
        )

    def test_bind_simple__permanent_block__fail(self):
        """
        Номер заблокирован навсегда.
        """
        self.assign_grants([grants.REGISTRATOR])
        self._given_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_error_xml_response(u'PERMANENTBLOCK', u'PERMANENTBLOCK'),
        )

        self.make_request(uid=UID, number=PHONE_NUMBER)

        self.assert_response_is_xml_error(
            u'Number permanently blocked',
            u'PERMANENTBLOCK',
        )

    def test_bind_simple__temporary_block__fail(self):
        """
        Номер заблокирован временно.
        """
        self.assign_grants([grants.REGISTRATOR])
        self._given_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER,
                OPERATION_ID,
                code_last_sent=datetime.now(),
            )
        )

        self.make_request(uid=UID, number=PHONE_NUMBER)

        self.assert_response_is_xml_error(
            u'Number temporary blocked',
            u'TEMPORARYBLOCK',
        )

    def test_bind_simple__uid_limit_exceeded__fail(self):
        """
        Пользователь превысил лимиты на отправку сообщений.
        """
        self.assign_grants([grants.REGISTRATOR])
        self._given_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_error_xml_response(u'UIDLIMITEXCEEDED', u'UIDLIMITEXCEEDED'),
        )

        self.make_request(uid=UID, number=PHONE_NUMBER)

        self.assert_response_is_xml_error(
            u'Max validations exeeded',
            u'VALEXEEDED',
        )

    def test_rebind_simple__without_sms__ignore_bindlimit_initially__db(self):
        self.assign_grants([grants.REGISTRATOR, grants.AWESOME_REGISTRATOR])
        actual_flags = PhoneOperationFlags()
        actual_flags.should_ignore_binding_limit = True
        self._given_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER,
                OPERATION_ID,
                flags=actual_flags,
            )
        )

        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            withoutsms=True,
            ignore_bindlimit=False,
        )

        assert_simple_phone_bound.check_db(
            self.env.db,
            UID,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
        )
        expected_flags = PhoneBindingsFlags()
        expected_flags.should_ignore_binding_limit = True
        ok_(self.env.db.get(
            u'phone_bindings',
            uid=UID,
            number=int(PHONE_NUMBER_DIGITAL),
            phone_id=PHONE_ID,
            flags=int(expected_flags),
            db=u'passportdbshard1',
        ))

    def test_bind_simple__english__send_confirmation_code(self):
        self.assign_grants([grants.REGISTRATOR])
        self._given_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )

        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            lang=u'en',
        )

        requests = self.env.yasms.get_requests_by_method(u'send_sms')
        requests[0].assert_query_contains({
            u'phone': PHONE_NUMBER,
            u'text': ENGLISH_CONFIRMATION_MESSAGE,
        })
        requests[0].assert_post_data_contains({
            u'text_template_params': u'{"code": "%s"}' % CONFIRMATION_CODE,
        })

    def test_database_error(self):
        self.assign_all_grants()
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(uid=UID),
        )
        self.env.db.set_side_effect_for_db('passportdbshard1', DBError())

        response = self.make_request()

        eq_(response.status_code, 200)
        self.assert_response_is_error(u'Database error', u'INTERROR')

    def test_phonish(self):
        # К фонишу нельзя привязать больше одного номера

        self.assign_all_grants()

        flags = PhoneBindingsFlags()
        flags.should_ignore_binding_limit = True

        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                **deep_merge(
                    dict(
                        login=PHONISH_LOGIN,
                        aliases={u'phonish': PHONISH_LOGIN},
                    ),
                    build_phone_bound(
                        PHONE_ID,
                        PHONE_NUMBER_EXTRA,
                        binding_flags=flags,
                    ),
                )
            ),
        )

        response = self.make_request()

        eq_(response.status_code, 200)
        self.assert_response_is_error(
            u'Phonish must has exactly one phone',
            u'INTERROR',
        )


@with_settings_hosts
class TestRegisterNoPhone(BaseRegisterViewBlackboxTestCase):
    def setUp(self):
        super(TestRegisterNoPhone, self).setUp()
        self.assign_grants([grants.REGISTRATOR, grants.AWESOME_REGISTRATOR])
        self._given_account(
            uid=UID,
            phones=[],
            phone_operations=[],
        )

        self.env.blackbox.set_response_side_effect(
            u'phone_bindings',
            [
                # Для обеления
                blackbox_phone_bindings_response([]),
                # Для тестов с withoutsms=True
                blackbox_phone_bindings_response([
                    {
                        u'type': u'current',
                        u'number': PHONE_NUMBER,
                        u'phone_id': PHONE_ID,
                        u'uid': UID,
                        u'bound': datetime.now(),
                    },
                ]),
            ],
        )

    def test_bind_simple__response(self):
        response = self.make_request(uid=UID, number=PHONE_NUMBER)

        self._assert_response_ok(response)

    def test_bind_simple__db(self):
        self.make_request(uid=UID, number=PHONE_NUMBER)

        assert_simple_phone_being_bound.check_db(
            self.env.db,
            UID,
            {
                u'id': PHONE_ID,
                u'number': PHONE_NUMBER,
                u'created': DatetimeNow(),
                u'confirmed': None,
                u'admitted': None,
            },
            {
                u'id': 1,
                u'started': DatetimeNow(),
                u'finished': (
                    DatetimeNow() +
                    timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS)
                ),
                u'code_value': CONFIRMATION_CODE,
                u'code_send_count': 1,
                u'code_last_sent': DatetimeNow(),
                u'code_checks_count': 0,
                u'code_confirmed': None,
                u'flags': PhoneOperationFlags(),
            },
        )

    def test_bind_simple__ignore_bindlimit__db(self):
        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            ignore_bindlimit=True,
        )

        expected_flags = PhoneOperationFlags()
        expected_flags.should_ignore_binding_limit = True
        assert_simple_phone_being_bound.check_db(
            self.env.db,
            UID,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
            {u'flags': expected_flags},
        )

    def test_bind_simple__without_sms__response(self):
        response = self.make_request(uid=UID, number=PHONE_NUMBER, withoutsms=True)

        self._assert_response_ok(response)

    def test_bind_simple__without_sms__db(self):
        self.make_request(uid=UID, number=PHONE_NUMBER, withoutsms=True)

        assert_simple_phone_bound.check_db(
            self.env.db,
            UID,
            {
                u'id': PHONE_ID,
                u'number': PHONE_NUMBER,
                u'created': DatetimeNow(),
                u'bound': DatetimeNow(),
                u'confirmed': DatetimeNow(),
                u'admitted': None,
            },
        )
        ok_(self.env.db.get(
            u'phone_bindings',
            uid=UID,
            number=int(PHONE_NUMBER_DIGITAL),
            phone_id=PHONE_ID,
            flags=int(PhoneBindingsFlags()),
            db=u'passportdbshard1',
        ))

    def test_bind_simple__without_sms__timestamp__db(self):
        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            withoutsms=True,
            ts=to_unixtime(TEST_DATE),
        )

        assert_simple_phone_bound.check_db(
            self.env.db,
            UID,
            {
                u'id': PHONE_ID,
                u'number': PHONE_NUMBER,
                u'created': DatetimeNow(),
                u'bound': DatetimeNow(),
                u'confirmed': TEST_DATE,
                u'admitted': None,
            },
        )

    def test_bind_simple__without_sms__ignore_bindlimit__db(self):
        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            withoutsms=True,
            ignore_bindlimit=True,
        )

        expected_flags = PhoneBindingsFlags()
        expected_flags.should_ignore_binding_limit = True
        ok_(self.env.db.get(
            u'phone_bindings',
            uid=UID,
            number=int(PHONE_NUMBER_DIGITAL),
            phone_id=PHONE_ID,
            flags=int(expected_flags),
            db=u'passportdbshard1',
        ))

    def test_bind_simple__statbox(self):
        self.assign_grants(
            [grants.REGISTRATOR],
            consumer=u'old_yasms_grants_hunter',
        )

        self.make_request(
            uid=UID,
            number=u'+79215611231',
            sender=u'hunter',
            headers={
                u'Ya-Consumer-Client-Ip': u'7.2.5.5',
                u'Ya-Client-User-Agent': USER_AGENT,
            },
        )

        expected_request_env = {
            u'user_agent': USER_AGENT,
            u'ip': u'7.2.5.5',
            u'consumer': u'hunter',
        }

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'simple_bind_operation_created',
                number=u'+79215******',
                **expected_request_env
            ),
            self.env.statbox.entry(
                'code_sent',
                number=u'+79215******',
                **expected_request_env
            ),
        ])

    def test_bind_simple__without_sms__statbox(self):
        self.assign_grants(
            [grants.REGISTRATOR, grants.AWESOME_REGISTRATOR],
            consumer=u'old_yasms_grants_hunter',
        )

        self.make_request(
            uid=UID,
            number=u'+79215611231',
            withoutsms=True,
            sender=u'hunter',
            headers={
                u'Ya-Consumer-Client-Ip': u'7.2.5.5',
                u'Ya-Client-User-Agent': USER_AGENT,
            },
        )

        expected_request_env = {
            u'user_agent': USER_AGENT,
            u'ip': u'7.2.5.5',
            u'consumer': u'hunter',
        }

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                u'frodo_karma',
                new=u'6000',
                old=u'0',
                **expected_request_env
            ),
            self.env.statbox.entry(
                u'phone_confirmed',
                _exclude={u'operation_id'},
                number=u'+79215******',
                code_checks_count=u'1',
                without_sms=u'1',
                **expected_request_env
            ),
            self.env.statbox.entry(
                u'simple_phone_bound',
                _exclude={u'operation_id'},
                number=u'+79215******',
                without_sms=u'1',
                **expected_request_env
            ),
        ])

    def test_bind_simple__event_log(self):
        self.assign_grants(
            [grants.REGISTRATOR],
            consumer=u'old_yasms_grants_hunter',
        )

        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            sender=u'hunter',
        )

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                u'action': u'register',
                u'consumer': u'hunter',
                u'phone.%d.action' % PHONE_ID: u'created',
                u'phone.%d.number' % PHONE_ID: PHONE_NUMBER,
                u'phone.%d.created' % PHONE_ID: TimeNow(),
                u'phone.%d.operation.1.action' % PHONE_ID: u'created',
                u'phone.%d.operation.1.type' % PHONE_ID: u'bind',
                u'phone.%d.operation.1.security_identity' % PHONE_ID: str(int(PHONE_NUMBER)),
                u'phone.%d.operation.1.started' % PHONE_ID: TimeNow(),
                u'phone.%d.operation.1.finished' % PHONE_ID: TimeNow(
                    offset=settings.PHONE_QUARANTINE_SECONDS,
                ),
                u'user_agent': USER_AGENT,
            },
        )

    def test_bind_simple__without_sms__event_log(self):
        self.assign_grants(
            [grants.REGISTRATOR, grants.AWESOME_REGISTRATOR],
            consumer=u'old_yasms_grants_hunter',
        )

        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            withoutsms=True,
            sender=u'hunter',
        )

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                u'action': u'register',
                u'consumer': u'hunter',
                u'phone.%d.action' % PHONE_ID: u'created',
                u'phone.%d.number' % PHONE_ID: PHONE_NUMBER,
                u'phone.%d.created' % PHONE_ID: TimeNow(),
                u'phone.%d.bound' % PHONE_ID: TimeNow(),
                u'phone.%d.confirmed' % PHONE_ID: TimeNow(),
                u'info.karma_prefix': str(settings.KARMA_PREFIX_WASHED),
                u'info.karma_full': str(settings.KARMA_PREFIX_WASHED) + u'000',
                u'user_agent': USER_AGENT,
            },
        )

    def test_bind_secure__response(self):
        response = self.make_request(uid=UID, number=PHONE_NUMBER, secure=True)

        self._assert_response_ok(response)

    def test_bind_secure__db(self):
        self.make_request(uid=UID, number=PHONE_NUMBER, secure=True)

        assert_secure_phone_being_bound.check_db(
            self.env.db,
            UID,
            {
                u'id': PHONE_ID,
                u'number': PHONE_NUMBER,
                u'created': DatetimeNow(),
                u'confirmed': None,
                u'admitted': None,
            },
            {
                u'id': 1,
                u'started': DatetimeNow(),
                u'finished': (
                    DatetimeNow() +
                    timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS)
                ),
                u'code_value': CONFIRMATION_CODE,
                u'code_send_count': 1,
                u'code_last_sent': DatetimeNow(),
                u'code_checks_count': 0,
                u'code_confirmed': None,
                u'flags': PhoneOperationFlags(),
            },
        )

    def test_bind_secure__without_sms__response(self):
        response = self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            secure=True,
            withoutsms=True,
        )

        self._assert_response_ok(response)

    def test_bind_secure__without_sms__db(self):
        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            secure=True,
            withoutsms=True,
        )

        assert_secure_phone_bound.check_db(
            self.env.db,
            UID,
            {
                u'id': PHONE_ID,
                u'number': PHONE_NUMBER,
                u'created': DatetimeNow(),
                u'bound': DatetimeNow(),
                u'confirmed': DatetimeNow(),
                u'admitted': None,
            },
        )
        ok_(self.env.db.get(
            u'phone_bindings',
            uid=UID,
            number=int(PHONE_NUMBER_DIGITAL),
            phone_id=PHONE_ID,
            flags=int(PhoneBindingsFlags()),
            db=u'passportdbshard1',
        ))

    def test_bind_secure__without_sms__statbox(self):
        self.assign_grants(
            [grants.REGISTRATOR, grants.AWESOME_REGISTRATOR],
            consumer=u'old_yasms_grants_hunter',
        )

        self.make_request(
            uid=UID,
            number=u'+79215611231',
            secure=True,
            withoutsms=True,
            sender=u'hunter',
            headers={
                u'Ya-Consumer-Client-Ip': u'7.2.5.5',
                u'Ya-Client-User-Agent': USER_AGENT,
            },
        )

        expected_request_env = {
            u'user_agent': USER_AGENT,
            u'ip': u'7.2.5.5',
            u'consumer': u'hunter',
        }

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                u'account_modification',
                uid=str(UID),
                entity=u'phones.secure',
                operation=u'created',
                new=u'+79215******',
                new_entity_id=str(PHONE_ID),
                old='-',
                old_entity_id='-',
                **expected_request_env
            ),
            self.env.statbox.entry(
                u'frodo_karma',
                new=u'6000',
                old=u'0',
                **expected_request_env
            ),
            self.env.statbox.entry(
                u'phone_confirmed',
                _exclude={u'operation_id'},
                number=u'+79215******',
                code_checks_count=u'1',
                without_sms=u'1',
                **expected_request_env
            ),
            self.env.statbox.entry(
                u'secure_phone_bound',
                _exclude={u'operation_id': u'1'},
                number=u'+79215******',
                without_sms=u'1',
                **expected_request_env
            ),
        ])

    def test_bind_secure__event_log(self):
        self.assign_grants(
            [grants.REGISTRATOR],
            consumer=u'old_yasms_grants_hunter',
        )

        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            secure=True,
            sender=u'hunter',
        )

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                u'action': u'register',
                u'consumer': u'hunter',
                u'phone.%d.action' % PHONE_ID: u'created',
                u'phone.%d.number' % PHONE_ID: PHONE_NUMBER,
                u'phone.%d.created' % PHONE_ID: TimeNow(),
                u'phone.%d.operation.1.action' % PHONE_ID: u'created',
                u'phone.%d.operation.1.type' % PHONE_ID: u'bind',
                u'phone.%d.operation.1.security_identity' % PHONE_ID: u'1',
                u'phone.%d.operation.1.started' % PHONE_ID: TimeNow(),
                u'phone.%d.operation.1.finished' % PHONE_ID: TimeNow(
                    offset=settings.PHONE_QUARANTINE_SECONDS,
                ),
                u'user_agent': USER_AGENT,
            },
        )

    def test_bind_secure__without_sms__event_log(self):
        self.assign_grants(
            [grants.REGISTRATOR, grants.AWESOME_REGISTRATOR],
            consumer=u'old_yasms_grants_thompson',
        )

        self.make_request(
            uid=UID,
            number='+79026411724',
            secure=True,
            withoutsms=True,
            sender=u'thompson',
        )

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                u'action': u'register',
                u'consumer': u'thompson',
                u'phone.%d.action' % PHONE_ID: u'created',
                u'phone.%d.number' % PHONE_ID: u'+79026411724',
                u'phone.%d.created' % PHONE_ID: TimeNow(),
                u'phone.%d.bound' % PHONE_ID: TimeNow(),
                u'phone.%d.secured' % PHONE_ID: TimeNow(),
                u'phone.%d.confirmed' % PHONE_ID: TimeNow(),
                u'phones.secure': str(PHONE_ID),
                u'info.karma_prefix': str(settings.KARMA_PREFIX_WASHED),
                u'info.karma_full': str(settings.KARMA_PREFIX_WASHED) + u'000',
                u'user_agent': USER_AGENT,
            },
        )

    def test_bind_simple__send_confirmation_code(self):
        self.make_request(uid=UID, number=PHONE_NUMBER)

        requests = self.env.yasms.get_requests_by_method(u'send_sms')
        requests[0].assert_query_contains({
            u'phone': PHONE_NUMBER,
            u'text': RUSSIAN_CONFIRMATION_MESSAGE,
        })
        requests[0].assert_post_data_contains({
            u'text_template_params': u'{"code": "%s"}' % CONFIRMATION_CODE,
        })

    def test_bind_simple__dont_send_notification(self):
        self.make_request(uid=UID, number=PHONE_NUMBER)

        eq_(len(self.env.mailer.messages), 0)

    def test_bind_secure__send_confirmation_code(self):
        self.make_request(uid=UID, number=PHONE_NUMBER, secure=True)

        requests = self.env.yasms.get_requests_by_method(u'send_sms')
        requests[0].assert_query_contains({
            u'phone': PHONE_NUMBER,
            u'text': RUSSIAN_CONFIRMATION_MESSAGE,
        })
        requests[0].assert_post_data_contains({
            u'text_template_params': u'{"code": "%s"}' % CONFIRMATION_CODE,
        })

    def test_bind_secure__dont_send_notification(self):
        self.make_request(uid=UID, number=PHONE_NUMBER, secure=True)

        eq_(len(self.env.mailer.messages), 0)


@with_settings_hosts
class TestRegisterSimplePhoneBeingBound(BaseRegisterViewBlackboxTestCase):
    def setUp(self):
        super(TestRegisterSimplePhoneBeingBound, self).setUp()
        self.assign_grants([grants.REGISTRATOR, grants.AWESOME_REGISTRATOR])
        self._old_time = datetime.now() - timedelta(hours=5)
        self._given_account(
            uid=UID,
            **build_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER,
                OPERATION_ID,
                phone_created=self._old_time,
                operation_started=self._old_time,
            )
        )

        self.env.blackbox.set_response_side_effect(
            u'phone_bindings',
            [
                # Для обеления
                blackbox_phone_bindings_response([]),
                # Для тестов с withoutsms=True
                blackbox_phone_bindings_response([
                    {
                        u'type': u'current',
                        u'number': PHONE_NUMBER,
                        u'phone_id': PHONE_ID,
                        u'uid': UID,
                        u'bound': datetime.now(),
                    },
                ]),
            ],
        )

    def test_bind_simple__response(self):
        response = self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            revalidate=True,
        )
        self._assert_response_ok(response, revalidated=True)

    def test_bind_simple__db(self):
        self.make_request(uid=UID, number=PHONE_NUMBER)

        assert_simple_phone_being_bound.check_db(
            self.env.db,
            UID,
            {
                u'id': PHONE_ID,
                u'number': PHONE_NUMBER,
                u'created': self._old_time,
            },
            {
                u'id': OPERATION_ID,
                u'started': self._old_time,
                u'finished': self._old_time + timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
            },
        )

    def test_bind_simple__statbox(self):
        self.assign_grants(
            [grants.REGISTRATOR],
            consumer=u'old_yasms_grants_plato',
        )

        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            sender=u'plato',
            headers={
                u'Ya-Consumer-Client-Ip': u'7.2.5.5',
                u'Ya-Client-User-Agent': USER_AGENT,
            },
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                u'code_sent',
                operation_id=str(OPERATION_ID),
                number=PHONE_NUMBER_MASKED,
                sms_count=u'2',
                consumer=u'plato',
                ip=u'7.2.5.5',
            ),
        ])

    def test_bind_simple__event_log(self):
        self.make_request(uid=UID, number=PHONE_NUMBER)

        self.assert_events_are_logged(self.env.handle_mock, {})

    def test_bind_simple__change_ignore_bindlimit__db(self):
        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            ignore_bindlimit=True,
        )

        assert_simple_phone_being_bound.check_db(
            self.env.db,
            UID,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
            {
                u'id': OPERATION_ID,
                u'flags': PhoneOperationFlags(),
            },
        )

    def test_bind_simple__without_sms__response(self):
        rv = self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            withoutsms=True,
        )

        self._assert_response_ok(rv)

    def test_bind_simple__without_sms__db(self):
        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            withoutsms=True,
        )

        assert_simple_phone_bound.check_db(
            self.env.db,
            UID,
            {
                u'id': PHONE_ID,
                u'number': PHONE_NUMBER,
                u'created': self._old_time,
                u'bound': DatetimeNow(),
                u'confirmed': DatetimeNow(),
            },
        )
        ok_(self.env.db.get(
            u'phone_bindings',
            uid=UID,
            number=int(PHONE_NUMBER_DIGITAL),
            phone_id=PHONE_ID,
            flags=int(PhoneBindingsFlags()),
            db=u'passportdbshard1',
        ))
        self.env.db.check_missing(
            u'phone_operations',
            id=OPERATION_ID,
            uid=UID,
            db=u'passportdbshard1',
        )

    def test_bind_simple__without_sms__statbox(self):
        self.assign_grants(
            [grants.REGISTRATOR, grants.AWESOME_REGISTRATOR],
            consumer=u'old_yasms_grants_hunter',
        )

        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            withoutsms=True,
            sender=u'hunter',
            headers={
                u'Ya-Consumer-Client-Ip': u'7.2.5.5',
                u'Ya-Client-User-Agent': USER_AGENT,
            },
        )

        expected_request_env = {
            u'consumer': u'hunter',
            u'ip': u'7.2.5.5',
        }

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                u'frodo_karma',
                new=u'6000',
                old=u'0',
                user_agent=USER_AGENT,
                **expected_request_env
            ),
            self.env.statbox.entry(
                u'phone_confirmed',
                _exclude={u'operation_id'},
                number=PHONE_NUMBER_MASKED,
                code_checks_count=u'1',
                without_sms=u'1',
                **expected_request_env
            ),
            self.env.statbox.entry(
                u'simple_phone_bound',
                _exclude={u'operation_id'},
                number=PHONE_NUMBER_MASKED,
                without_sms=u'1',
                **expected_request_env
            ),
        ])

    def test_bind_simple__without_sms__event_log(self):
        self.assign_grants(
            [grants.REGISTRATOR, grants.AWESOME_REGISTRATOR],
            consumer=u'old_yasms_grants_thompson',
        )

        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            withoutsms=True,
            sender=u'thompson',
        )

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                u'action': u'register',
                u'consumer': u'thompson',
                u'phone.%d.action' % PHONE_ID: u'changed',
                u'phone.%d.number' % PHONE_ID: PHONE_NUMBER,
                u'phone.%d.bound' % PHONE_ID: TimeNow(),
                u'phone.%d.confirmed' % PHONE_ID: TimeNow(),
                u'phone.%d.operation.%d.action' % (PHONE_ID, OPERATION_ID): u'deleted',
                u'phone.%d.operation.%d.type' % (PHONE_ID, OPERATION_ID): u'bind',
                u'phone.%d.operation.%d.security_identity' % (PHONE_ID, OPERATION_ID): str(int(PHONE_NUMBER)),
                u'info.karma_prefix': str(settings.KARMA_PREFIX_WASHED),
                u'info.karma_full': str(settings.KARMA_PREFIX_WASHED) + u'000',
                u'user_agent': USER_AGENT,
            },
        )

    def test_rebind_simple_to_secure__response(self):
        rv = self.make_request(uid=UID, number=PHONE_NUMBER, secure=True)

        self._assert_response_ok(rv)

    def test_rebind_simple_to_secure__db(self):
        self.make_request(uid=UID, number=PHONE_NUMBER, secure=True)

        assert_secure_phone_being_bound.check_db(
            self.env.db,
            UID,
            {
                u'id': PHONE_ID,
                u'number': PHONE_NUMBER,
                u'created': self._old_time,
            },
            {
                u'id': OPERATION_ID + 1,
                u'started': DatetimeNow(),
                u'finished': DatetimeNow() + timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
            },
        )
        self.env.db.check_missing(
            u'phone_operations',
            id=OPERATION_ID,
            uid=UID,
            db=u'passportdbshard1',
        )

    def test_rebind_simple_to_secure__statbox(self):
        self.assign_grants(
            [grants.REGISTRATOR],
            consumer=u'old_yasms_grants_plato',
        )

        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            secure=True,
            sender=u'plato',
            headers={
                u'Ya-Consumer-Client-Ip': u'7.2.5.5',
                u'Ya-Client-User-Agent': USER_AGENT,
            },
        )

        expected_request_env = {
            u'consumer': u'plato',
            u'ip': u'7.2.5.5',
            u'user_agent': USER_AGENT,
        }

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                u'secure_bind_operation_created',
                number=PHONE_NUMBER_MASKED,
                operation_id=str(OPERATION_ID + 1),
                **expected_request_env
            ),
            self.env.statbox.entry(
                u'phone_operation_replaced',
                number=PHONE_NUMBER_MASKED,
                old_operation_type=u'simple_bind',
                operation_type=u'secure_bind',
                old_operation_id=str(OPERATION_ID),
                operation_id=str(OPERATION_ID + 1),
                **expected_request_env
            ),
            self.env.statbox.entry(
                u'code_sent',
                number=PHONE_NUMBER_MASKED,
                sms_count=u'1',
                operation_id=str(OPERATION_ID + 1),
                **expected_request_env
            ),
        ])

    def test_rebind_simple_to_secure__event_log(self):
        self.assign_grants(
            [grants.REGISTRATOR],
            consumer=u'old_yasms_grants_plato',
        )

        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            secure=True,
            sender=u'plato',
        )

        old_op_fmt = u'phone.%d.operation.%d.' % (PHONE_ID, OPERATION_ID)
        new_op_fmt = u'phone.%d.operation.%d.' % (PHONE_ID, OPERATION_ID + 1)

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                u'action': u'register',
                u'consumer': u'plato',
                u'phone.%d.number' % PHONE_ID: PHONE_NUMBER,

                old_op_fmt + u'action': u'deleted',
                old_op_fmt + u'type': u'bind',
                old_op_fmt + u'security_identity': str(int(PHONE_NUMBER)),

                new_op_fmt + u'action': u'created',
                new_op_fmt + u'type': u'bind',
                new_op_fmt + u'security_identity': u'1',
                new_op_fmt + u'started': TimeNow(),
                new_op_fmt + u'finished': TimeNow(offset=settings.PHONE_QUARANTINE_SECONDS),
                u'user_agent': USER_AGENT,
            },
        )


@with_settings_hosts
class TestRegisterPhoneBeingBoundToReplaceSecure(BaseRegisterViewBlackboxTestCase):
    def setUp(self):
        super(TestRegisterPhoneBeingBoundToReplaceSecure, self).setUp()
        self.assign_grants([grants.REGISTRATOR, grants.AWESOME_REGISTRATOR])

        self.env.blackbox.set_response_side_effect(
            u'phone_bindings',
            [
                # Для обеления
                blackbox_phone_bindings_response([]),
                # Для тестов с withoutsms=True
                blackbox_phone_bindings_response([
                    {
                        u'type': u'current',
                        u'number': PHONE_NUMBER,
                        u'phone_id': PHONE_ID,
                        u'uid': UID,
                        u'bound': datetime.now(),
                    },
                ]),
            ],
        )
        self.env.statbox.bind_entry(
            u'replace_secure_phone_with_bound_phone_operation_created',
            action=u'phone_operation_created',
            uid=str(UID),
            secure_phone_id=str(PHONE_ID_EXTRA),
            secure_number=PHONE_NUMBER_EXTRA_MASKED,
            simple_number=PHONE_NUMBER_MASKED,
            simple_phone_id=str(PHONE_ID),
        )
        self.env.statbox.bind_entry(
            u'secure_phone_replaced',
            action=u'register.register.secure_phone_replaced',
            uid=str(UID),
            old_secure_number=PHONE_NUMBER_EXTRA_MASKED,
            old_secure_phone_id=str(PHONE_ID_EXTRA),
            new_secure_number=PHONE_NUMBER_MASKED,
            new_secure_phone_id=str(PHONE_ID),
        )

    def _given_phone_being_bound_to_replace_secure(self,
                                                   secure_code_confirmed=None,
                                                   is_secure_aliased=False):
        self._given_account(
            uid=UID,
            **deep_merge(
                build_phone_secured(
                    PHONE_ID_EXTRA,
                    PHONE_NUMBER_EXTRA,
                    is_default=True,
                    is_alias=is_secure_aliased,
                ),
                dict(phones=[dict(
                    id=PHONE_ID,
                    number=PHONE_NUMBER,
                    created=TEST_DATE,
                    bound=None,
                    confirmed=None,
                    secured=None,
                )]),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=OPERATION_ID_EXTRA,
                    secure_phone_id=PHONE_ID_EXTRA,
                    secure_code_confirmed=secure_code_confirmed,
                    being_bound_operation_id=OPERATION_ID,
                    being_bound_phone_id=PHONE_ID,
                    being_bound_phone_number=PHONE_NUMBER,
                ),
            )
        )

    def test_without_sms__response(self):
        self._given_phone_being_bound_to_replace_secure()

        response = self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            withoutsms=True,
        )

        self._assert_response_ok(response)

    def test_without_sms__secure_not_confirmed__db(self):
        self._given_phone_being_bound_to_replace_secure()

        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            withoutsms=True,
        )

        assert_simple_phone_replace_secure.check_db(
            self.env.db,
            UID,
            {
                u'id': PHONE_ID,
                u'number': PHONE_NUMBER,
                u'created': TEST_DATE,
                u'bound': DatetimeNow(),
                u'confirmed': DatetimeNow(),
            },
            {
                u'id': OPERATION_ID + 1,
                u'code_confirmed': DatetimeNow(),
                u'phone_id2': PHONE_ID_EXTRA,
            },
        )
        self.env.db.check_missing(
            u'phone_operations',
            id=OPERATION_ID,
            uid=UID,
            db=u'passportdbshard1',
        )
        assert_secure_phone_being_replaced.check_db(
            self.env.db,
            UID,
            {u'id': PHONE_ID_EXTRA, u'number': PHONE_NUMBER_EXTRA},
            {
                u'id': OPERATION_ID_EXTRA,
                u'phone_id2': PHONE_ID,
                u'code_confirmed': None,
            },
        )

    def test_without_sms__secure_confirmed__db(self):
        self._given_phone_being_bound_to_replace_secure(
            secure_code_confirmed=TEST_DATE,
        )

        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            withoutsms=True,
        )

        assert_secure_phone_bound.check_db(
            self.env.db,
            UID,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
        )
        assert_no_phone_in_db(
            self.env.db,
            UID,
            PHONE_ID_EXTRA,
            PHONE_NUMBER_EXTRA,
        )
        self.env.db.check_missing(
            u'phone_operations',
            id=OPERATION_ID,
            uid=UID,
            db=u'passportdbshard1',
        )
        self.env.db.check_missing(
            u'phone_operations',
            id=OPERATION_ID_EXTRA,
            uid=UID,
            db=u'passportdbshard1',
        )

    def test_without_sms__aliased__secure_confirmed__response(self):
        self._given_phone_being_bound_to_replace_secure(
            is_secure_aliased=True,
            secure_code_confirmed=TEST_DATE,
        )

        response = self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            withoutsms=True,
        )

        self._assert_response_ok(response)

    def test_without_sms__aliased__secure_confirmed__event_log(self):
        self.assign_grants(
            [grants.REGISTRATOR, grants.AWESOME_REGISTRATOR],
            consumer=u'old_yasms_grants_hunter',
        )
        self._given_phone_being_bound_to_replace_secure(
            is_secure_aliased=True,
            secure_code_confirmed=TEST_DATE,
        )

        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            withoutsms=True,
            sender=u'hunter',
        )

        op_prefix = u'phone.%d.operation.%d' % (PHONE_ID, OPERATION_ID)
        extra_op_prefix = u'phone.%d.operation.%d' % (PHONE_ID_EXTRA, OPERATION_ID_EXTRA)
        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                u'action': u'register',
                u'consumer': u'hunter',

                u'phone.%d.action' % PHONE_ID: u'changed',
                u'phone.%d.number' % PHONE_ID: PHONE_NUMBER,
                u'phone.%d.bound' % PHONE_ID: TimeNow(),
                u'phone.%d.confirmed' % PHONE_ID: TimeNow(),
                u'phone.%d.secured' % PHONE_ID: TimeNow(),

                u'%s.action' % op_prefix: u'deleted',
                u'%s.type' % op_prefix: u'bind',
                u'%s.security_identity' % op_prefix: str(int(PHONE_NUMBER)),

                u'phone.%d.action' % PHONE_ID_EXTRA: u'deleted',
                u'phone.%d.number' % PHONE_ID_EXTRA: PHONE_NUMBER_EXTRA,

                u'%s.action' % extra_op_prefix: u'deleted',
                u'%s.type' % extra_op_prefix: u'replace',
                u'%s.security_identity' % extra_op_prefix: u'1',

                u'phones.secure': str(PHONE_ID),
                u'phones.default': '0',
                u'alias.phonenumber.rm': PHONE_NUMBER_EXTRA_INTERNATIONAL,

                u'info.karma_prefix': str(settings.KARMA_PREFIX_WASHED),
                u'info.karma_full': str(settings.KARMA_PREFIX_WASHED) + u'000',
                u'user_agent': USER_AGENT,
            },
        )

    def test_without_sms__aliased__secure_confirmed__statbox(self):
        self.assign_grants(
            [grants.REGISTRATOR, grants.AWESOME_REGISTRATOR],
            consumer=u'old_yasms_grants_hunter',
        )
        self._given_phone_being_bound_to_replace_secure(
            is_secure_aliased=True,
            secure_code_confirmed=TEST_DATE,
        )

        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            withoutsms=True,
            sender=u'hunter',
            headers={
                u'Ya-Consumer-Client-Ip': u'7.2.5.5',
                u'Ya-Client-User-Agent': USER_AGENT,
            },
        )

        expected_request_env = {
            u'ip': u'7.2.5.5',
            u'consumer': u'hunter',
            u'user_agent': USER_AGENT,
        }

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                u'phonenumber_alias_removed',
                uid=str(UID),
                **expected_request_env
            ),
            self.env.statbox.entry(
                u'account_modification',
                uid=str(UID),
                entity=u'phones.secure',
                operation='updated',
                new=PHONE_NUMBER_MASKED,
                new_entity_id=str(PHONE_ID),
                old=PHONE_NUMBER_EXTRA_MASKED,
                old_entity_id=str(PHONE_ID_EXTRA),
                **expected_request_env
            ),
            self.env.statbox.entry(
                u'frodo_karma',
                new=u'6000',
                old=u'0',
                **expected_request_env
            ),
            self.env.statbox.entry(
                u'subscriptions',
                operation=u'removed',
                uid=str(UID),
                sid=str(ALIAS_SID),
                **expected_request_env
            ),
            self.env.statbox.entry(
                u'phone_confirmed',
                _exclude={u'operation_id'},
                number=PHONE_NUMBER_MASKED,
                code_checks_count=u'1',
                without_sms=u'1',
                **expected_request_env
            ),
            self.env.statbox.entry(
                'simple_phone_bound',
                _exclude={u'operation_id'},
                number=PHONE_NUMBER_MASKED,
                without_sms=u'1',
                **expected_request_env
            ),
            self.env.statbox.entry(
                u'secure_phone_replaced',
                _exclude={u'operation_id'},
                without_sms=u'1',
                **expected_request_env
            ),
        ])

    def test_without_sms__aliased__secure_confirmed__db(self):
        self._given_phone_being_bound_to_replace_secure(
            is_secure_aliased=True,
            secure_code_confirmed=TEST_DATE,
        )

        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            withoutsms=True,
        )

        assert_secure_phone_bound.check_db(
            self.env.db,
            UID,
            {
                u'id': PHONE_ID,
                u'number': PHONE_NUMBER,
                u'confirmed': DatetimeNow(),
                u'bound': DatetimeNow(),
                u'secured': DatetimeNow(),
            },
        )
        assert_no_phone_in_db(
            self.env.db,
            UID,
            PHONE_ID_EXTRA,
            PHONE_NUMBER_EXTRA,
        )
        self.env.db.check_missing(
            u'phone_operations',
            id=OPERATION_ID,
            uid=UID,
            db=u'passportdbshard1',
        )
        self.env.db.check_missing(
            u'phone_operations',
            id=OPERATION_ID_EXTRA,
            uid=UID,
            db=u'passportdbshard1',
        )
        assert_phonenumber_alias_removed(
            self.env.db,
            UID,
            str(int(PHONE_NUMBER_EXTRA)),
        )


@with_settings_hosts(
    YASMS_PHONE_BINDING_LIMIT=2,
)
class TestRegisterUnboundPhone(BaseRegisterViewBlackboxTestCase):
    def setUp(self):
        super(TestRegisterUnboundPhone, self).setUp()
        self.assign_grants([grants.REGISTRATOR, grants.AWESOME_REGISTRATOR])

    def _given_accounts(self, subject_account, extra_accounts):
        kwargs = self._build_account_args(**subject_account)
        subject_user_info = blackbox_userinfo_response(**kwargs)
        self.env.db.serialize(subject_user_info)

        extra_kwargs = []
        for extra_account in extra_accounts:
            kwargs = self._build_account_args(**extra_account)
            self.env.db.serialize(blackbox_userinfo_response(**kwargs))
            extra_kwargs.append(kwargs)

        self.env.blackbox.set_response_side_effect(
            u'userinfo',
            [
                subject_user_info,
                blackbox_userinfo_response_multiple(extra_kwargs),
            ],
        )

    def _setup_phone_bindings_response(self, subject_binding, extra_bindings):
        extra_phone_bindings = []
        for uid, phone_id in extra_bindings:
            extra_phone_bindings.append(
                {
                    u'type': u'current',
                    u'number': PHONE_NUMBER,
                    u'phone_id': phone_id,
                    u'uid': uid,
                    u'bound': TEST_DATE,
                },
            )

        self.env.blackbox.set_response_side_effect(
            u'phone_bindings',
            [
                blackbox_phone_bindings_response([]),
                blackbox_phone_bindings_response(
                    [{
                        u'type': u'current',
                        u'number': PHONE_NUMBER,
                        u'phone_id': subject_binding[1],
                        u'uid': subject_binding[0],
                        u'bound': datetime.now(),
                    }] + extra_phone_bindings,
                ),
            ],
        )

    def test_hit_limit__db(self):
        """
        Если до новой привязки был достигнут предел, нужно отвязать старые
        привязки.
        """
        self._given_accounts(
            subject_account=dict(
                uid=UID,
                phones=[],
                phone_operations=[],
            ),
            extra_accounts=[
                deep_merge(
                    dict(
                        uid=1000,
                        login=u'login1000',
                        aliases={u'portal': u'login1000'},
                    ),
                    build_phone_bound(1000, PHONE_NUMBER),
                ),
                deep_merge(
                    dict(
                        uid=1001,
                        login=u'login1001',
                        aliases={u'portal': u'login1001'},
                    ),
                    build_phone_bound(1001, PHONE_NUMBER),
                ),
            ],
        )
        self._setup_phone_bindings_response(
            subject_binding=(UID, PHONE_ID),
            extra_bindings=[
                (1000, 1000),
                (1001, 1001),
            ],
        )

        response = self.make_request(uid=UID, number=PHONE_NUMBER, withoutsms=True)

        self._assert_response_ok(response)

        assert_simple_phone_bound.check_db(
            self.env.db,
            UID,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
        )
        assert_phone_unbound.check_db(
            self.env.db,
            1000,
            {u'id': 1000, u'number': PHONE_NUMBER},
        )
        assert_simple_phone_bound.check_db(
            self.env.db,
            1001,
            {u'id': 1001, u'number': PHONE_NUMBER},
        )

    def test_hit_limit__past_timestamp__db(self):
        # Дано время привязки в прошлом.
        self._given_accounts(
            subject_account=dict(
                uid=UID,
                phones=[],
                phone_operations=[],
            ),
            extra_accounts=[
                deep_merge(
                    dict(
                        uid=1000,
                        login=u'login1000',
                        aliases={u'portal': u'login1000'},
                    ),
                    build_phone_bound(
                        1000,
                        PHONE_NUMBER,
                        phone_bound=datetime.now(),
                    ),
                ),
                deep_merge(
                    dict(
                        uid=1001,
                        login=u'login1001',
                        aliases={u'portal': u'login1001'},
                    ),
                    build_phone_bound(
                        1001,
                        PHONE_NUMBER,
                        phone_bound=datetime.now(),
                    ),
                ),
            ],
        )
        self._setup_phone_bindings_response(
            subject_binding=(UID, PHONE_ID),
            extra_bindings=[
                (1000, 1000),
                (1001, 1001),
            ],
        )

        self.make_request(
            uid=UID,
            number=PHONE_NUMBER,
            withoutsms=True,
            ts=to_unixtime(TEST_DATE - timedelta(hours=2)),
        )

        assert_simple_phone_bound.check_db(
            self.env.db,
            UID,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
        )
        assert_phone_unbound.check_db(
            self.env.db,
            1000,
            {u'id': 1000, u'number': PHONE_NUMBER},
        )
        assert_simple_phone_bound.check_db(
            self.env.db,
            1001,
            {u'id': 1001, u'number': PHONE_NUMBER},
        )
