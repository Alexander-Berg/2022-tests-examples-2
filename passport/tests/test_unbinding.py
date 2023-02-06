# -*- coding: utf-8 -*-

from datetime import timedelta

from nose.tools import eq_
from passport.backend.core.builders.blackbox.exceptions import BlackboxTemporaryError
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_json_error_response,
    blackbox_phone_bindings_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.conf import settings
from passport.backend.core.dbmanager.exceptions import DBError
from passport.backend.core.mailer.faker import TemplateFakeMailer
from passport.backend.core.mailer.faker.mail_utils import create_native_email
from passport.backend.core.models.phones.faker import (
    assert_account_has_phonenumber_alias,
    assert_no_phone_in_db,
    assert_phone_unbound,
    assert_phonenumber_alias_removed,
    assert_secure_phone_bound,
    assert_simple_phone_being_securified,
    assert_simple_phone_bound,
    build_account,
    build_phone_bound,
    build_phone_secured,
    build_securify_operation,
    event_lines_phone_unbound,
    event_lines_phonenumber_alias_removed,
)
from passport.backend.core.test.consts import (
    TEST_PASSWORD_HASH1,
    TEST_PHONE_ID1,
    TEST_PHONE_ID2,
    TEST_PHONE_ID3,
)
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.types.bit_vector.bit_vector import PhoneBindingsFlags
from passport.backend.core.types.phone_number.phone_number import mask_phone_number
from passport.backend.core.yasms.unbinding import unbind_old_phone
from passport.backend.utils.common import deep_merge

from .base import TestCase
from .consts import (
    TEST_ALL_SUPPORTED_LANGUAGES,
    TEST_CONSUMER1,
    TEST_DISPLAY_LANGUAGES,
    TEST_ENVIRONMENT1,
    TEST_PHONE_NUMBER1,
    TEST_TIME1,
    TEST_UID1,
    TEST_UID2,
    TEST_UID3,
    TranslationSettings,
)


def get_first_phone(account):
    return list(account.phones.all().values())[0]


class UnbindOldPhoneTestCase(TestCase):
    def setUp(self):
        super(UnbindOldPhoneTestCase, self).setUp()
        self._fake_mailer = TemplateFakeMailer().start()
        self._setup_statbox()

    def tearDown(self):
        self._fake_mailer.stop()
        del self._fake_mailer
        settings.translations.reset()
        super(UnbindOldPhoneTestCase, self).tearDown()

    def _setup_statbox(self):
        self._statbox_faker.bind_entry(
            'phone_unbound',
            _exclude={'ip', 'consumer', 'user_agent'},
            number=TEST_PHONE_NUMBER1.masked_format_for_statbox,
        )
        self._statbox_faker.bind_entry(
            'phonenumber_alias_subscription_removed',
            ip=str(TEST_ENVIRONMENT1.user_ip),
        ),

    def _unbind_old_phone(self, phone, **kwargs):
        defaults = {
            'subject_phone': phone,
            'blackbox_builder': self._blackbox_builder,
            'statbox': self._statbox,
            'consumer': TEST_CONSUMER1,
            'event_timestamp': TEST_TIME1,
            'environment': TEST_ENVIRONMENT1,
        }
        for key, value in defaults.items():
            kwargs.setdefault(key, value)
        unbind_old_phone(**kwargs)

    def _build_other_accounts(
        self,
        args_list,
        setup_db=True,
        setup_blackbox_userinfo=True,
    ):
        BASE = 1921
        BASE_LOGIN = 'test_login'

        bindings = []
        userinfo_list = []
        for idx, args in enumerate(args_list):
            uid = phone_id = operation_id = BASE + idx
            login = BASE_LOGIN + str(uid)

            args.setdefault('uid', uid)
            args.setdefault('phone_id', phone_id)
            args.setdefault('operation_id', operation_id)
            args.setdefault('login', login)

            userinfo, binding = self._build_account_args(**args)
            userinfo_list.append(userinfo)

            if binding and binding.get('flags'):
                if not binding['flags'].should_ignore_binding_limit:
                    # Из ЧЯ запрашиваются только биндинги с
                    # should_ignore_binding_limit = False, поэтому в ответ не
                    # должны попадать другие.
                    bindings.append(binding)

        self._blackbox_builder_faker.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response(bindings),
        )

        if setup_blackbox_userinfo:
            self._blackbox_builder_faker.set_response_value(
                'userinfo',
                blackbox_userinfo_response_multiple(userinfo_list),
            )

        accounts = []
        for userinfo in userinfo_list:
            if setup_db:
                account = build_account(db_faker=self._db_faker, **userinfo)
            else:
                account = build_account(**userinfo)
            accounts.append(account)

        return accounts

    def _build_account_args(
        self,
        uid,
        phone_id,
        operation_id,
        login,
        phone_number=TEST_PHONE_NUMBER1,
        binding_time=None,
        in_operation=False,
        enabled_2fa=False,
        enabled_sms_2fa=False,
        phone_is_alias=False,
        confirmation_time=None,
        binding_flags=None,
        emails=None,
        crypt_password=TEST_PASSWORD_HASH1,
        alias_type='portal',
        is_phone_secure=False,
    ):
        emails = emails if emails is not None else [create_native_email(login, 'yandex.ru')]
        user_args = dict(
            uid=uid,
            login=login,
            aliases={alias_type: login},
            emails=emails,
            crypt_password=crypt_password,
        )
        if enabled_2fa:
            user_args = deep_merge(
                user_args,
                dict(attributes={'account.2fa_on': True}),
            )
        if enabled_sms_2fa:
            user_args = deep_merge(
                user_args,
                dict(attributes={'account.sms_2fa_on': True}),
            )

        if not phone_number:
            return user_args, None

        if binding_time is None and confirmation_time is None:
            binding_time = TEST_TIME1 - timedelta(hours=1)
        if binding_time is None:
            binding_time = confirmation_time
        if confirmation_time is None:
            confirmation_time = binding_time

        is_phone_secure = is_phone_secure or enabled_2fa or enabled_sms_2fa or phone_is_alias

        if binding_flags is None:
            binding_flags = PhoneBindingsFlags()

        binding = {
            'type': u'current',
            'uid': uid,
            'phone_id': phone_id,
            'number': phone_number.e164,
            'bound': binding_time,
            'flags': binding_flags,
        }

        if phone_is_alias:
            user_args = deep_merge(
                user_args,
                {
                    'aliases': {'phonenumber': phone_number.digital},
                    'attributes': {'account.enable_search_by_phone_alias': '1'},
                },
            )

        build_phone_args = {
            'phone_id': phone_id,
            'phone_number': phone_number.e164,
            'phone_created': binding_time,
            'phone_bound': binding_time,
            'phone_confirmed': confirmation_time,
        }
        if is_phone_secure:
            phone_args = build_phone_secured(
                phone_secured=binding_time,
                **build_phone_args
            )
        else:
            phone_args = build_phone_bound(
                binding_flags=binding_flags,
                **build_phone_args
            )
        if in_operation:
            if not is_phone_secure:
                phone_args = deep_merge(
                    phone_args,
                    build_securify_operation(
                        operation_id=operation_id,
                        phone_id=phone_id,
                    ),
                )
            else:
                raise NotImplementedError()  # pragma: no cover

        userinfo = deep_merge(user_args, phone_args)
        return userinfo, binding

    def _assert_phones_unbound(self, other_accounts, reason_account):
        self._check_phone(other_accounts, assert_phone_unbound)

        statbox_entries = []
        for other_account, other_phone in self._account_and_phone(other_accounts):
            statbox_entries.append(
                self._statbox_faker.entry(
                    'phone_unbound',
                    uid=str(other_account.uid),
                    phone_id=str(other_phone.id),
                ),
            )
        self._statbox_faker.assert_contains(statbox_entries)

        event_log_entries = tuple()
        for other_account, other_phone in self._account_and_phone(other_accounts):
            event_log_entries += event_lines_phone_unbound(
                uid=other_account.uid,
                phone_id=other_phone.id,
                phone_number=TEST_PHONE_NUMBER1,
                reason_uid=reason_account.uid,
            )
        self._event_log_faker.assert_contains(event_log_entries)

    def _assert_phonenumber_alias_removed(self, uid, phone_number, reason_uid):
        assert_phonenumber_alias_removed(
            db_faker=self._db_faker,
            uid=uid,
            alias=phone_number.digital,
        )
        self._statbox_faker.assert_contains([
            self._statbox_faker.entry(
                'phonenumber_alias_subscription_removed',
                uid=str(uid),
            ),
        ])
        self._event_log_faker.assert_contains(
            event_lines_phonenumber_alias_removed(
                action='unbind_phone_from_account',
                uid=uid,
                phone_number=phone_number,
                reason_uid=reason_uid,
                user_agent=None,
            ),
        )

        # Проверим, что написанное в historydb при отвязки телефона парсится парсером account history
        parsed_events = self._event_log_faker.parse_events()
        eq_(len(parsed_events), 1)
        parsed_event = parsed_events[0]
        eq_(parsed_event.event_type, 'secure_phone_unset')
        eq_(
            parsed_event.actions,
            [
                {
                    'type': 'secure_phone_unset',
                    'phone_unset': mask_phone_number(phone_number.international),
                    'reason_uid': reason_uid,
                },
            ],
        )

    def _check_phone(self, other_accounts, checker):
        for other_account, other_phone in self._account_and_phone(other_accounts):
            checker.check_db(
                db_faker=self._db_faker,
                uid=other_account.uid,
                phone_attributes={'id': other_phone.id},
            )

    def _account_and_phone(self, other_accounts):
        for other_account in other_accounts:
            yield other_account, get_first_phone(other_account)

    def _build_email(
        self,
        account,
        login=None,
        template_name=None,
    ):
        if template_name is None:
            template_name = 'mail/phone_unbound_simple.html'

        if login is None:
            login = account.login

        return dict(
            from_='email_sender_display_name',
            recipients=[account.login + '@yandex.ru'],
            subject='phone_unbound.email_subject',
            template_name=template_name,

            context=dict(
                FIRST_NAME=account.person.firstname,
                MASKED_LOGIN=login,
                PHONE=TEST_PHONE_NUMBER1.masked_format_for_challenge,
                feedback_key='feedback.robot',
                feedback_url_key='feedback_url.phone',
                language='ru',
                login=login,
                logo_url_key='logo_url',
                signature_key='signature.soulless_robot'
            ),
        )


@with_settings_hosts(
    ALL_SUPPORTED_LANGUAGES=TEST_ALL_SUPPORTED_LANGUAGES,
    BLACKBOX_ATTRIBUTES=tuple(),
    BLACKBOX_MAX_UIDS_PER_REQUEST=100,
    BLACKBOX_PHONE_EXTENDED_ATTRIBUTES=tuple(),
    BLACKBOX_URL='http://blackbox.url/',
    DISPLAY_LANGUAGES=TEST_DISPLAY_LANGUAGES,
    translations=TranslationSettings(),
    # Лимит привязки 2, чтобы не усложнять тесты циклами
    YASMS_PHONE_BINDING_LIMIT=2,
)
class TestUnbindOldPhone(UnbindOldPhoneTestCase):
    def test_limit_exceeded_single(self):
        accounts = [
            # Телефон привязали к ещё одному аккаунту
            dict(
                binding_time=TEST_TIME1 + timedelta(hours=1),
                confirmation_time=TEST_TIME1 + timedelta(hours=1),
            ),

            # Телефон был привязан к двум другим аккаунтам
            dict(
                # Время привязки одинаковое
                binding_time=TEST_TIME1,
                confirmation_time=TEST_TIME1 + timedelta(hours=3),
            ),
            dict(
                binding_time=TEST_TIME1,
                # Время подтверждения на этом аккаунте раньше
                confirmation_time=TEST_TIME1,
            ),
        ]
        accounts = self._build_other_accounts(accounts)

        self._unbind_old_phone(get_first_phone(accounts[0]))

        self._check_phone(accounts[:2], assert_simple_phone_bound)
        self._assert_phones_unbound([accounts[2]], accounts[0])

        self.assertEqual(len(self._blackbox_builder_faker.requests), 2)

        self._blackbox_builder_faker.requests[0].assert_query_equals(
            dict(
                format='json',
                ignorebindlimit='0',
                method='phone_bindings',
                numbers=TEST_PHONE_NUMBER1.e164,
                type='current',
            ),
        )

        self._blackbox_builder_faker.requests[1].assert_post_data_contains(
            dict(
                aliases='all_with_hidden',
                emails='getall',
                getphonebindings='all',
                getphoneoperations='1',
                getphones='all',
                method='userinfo',
                uid=','.join(map(str, [a.uid for a in accounts[1:]])),

                # Настоящий ip не передаётся, потому что запрашивается
                # информация о чужих аккаунтах.
                userip='127.0.0.1',
            ),
        )
        self._blackbox_builder_faker.requests[1].assert_contains_attributes(
            {
                'phones.default',
                'phones.secure',
            },
        )

        self.assertEqual(
            self._fake_mailer.messages,
            [
                self._build_email(accounts[2]),
            ],
        )

    def test_limit_exceeded_many(self):
        accounts = [
            # Телефон привязали к ещё одному аккаунту
            dict(
                confirmation_time=TEST_TIME1 + timedelta(hours=1),
            ),

            # Время подтвеждения у всех одинаковое
            dict(confirmation_time=TEST_TIME1),
            dict(confirmation_time=TEST_TIME1),
            dict(confirmation_time=TEST_TIME1),
        ]
        accounts = self._build_other_accounts(accounts)

        # Получилось, что телефон привязан к 4 аккаунтом, а можно только к 2,
        # поэтому отвязка по лимиту, должна уметь отвязывать телефон не только
        # от одного аккаунта, но и от нескольких.

        self._unbind_old_phone(get_first_phone(accounts[0]))

        self._check_phone([accounts[0]], assert_simple_phone_bound)

        # У старых аккаунтов одинаковое время подтверждения телефона, поэтому
        # выбираем для отвязки телефоны с наименьшим идентификатором, потому
        # что они привязаны раньше.
        self._assert_phones_unbound(accounts[1:3], accounts[0])
        phone_ids = [get_first_phone(a).id for a in accounts]
        self.assertTrue(all(i < phone_ids[3] for i in phone_ids[1:3]))

        self._check_phone([accounts[3]], assert_simple_phone_bound)

    def test_unbind_phonenumber_alias(self):
        accounts = [
            dict(binding_time=TEST_TIME1 + timedelta(hours=1)),

            dict(
                binding_time=TEST_TIME1,
                phone_is_alias=True,
            ),
            dict(binding_time=TEST_TIME1),
        ]
        accounts = self._build_other_accounts(accounts)

        assert_account_has_phonenumber_alias(
            db_faker=self._db_faker,
            uid=accounts[1].uid,
            alias=TEST_PHONE_NUMBER1.digital,
        )

        self._unbind_old_phone(get_first_phone(accounts[0]))

        self._assert_phones_unbound([accounts[1]], accounts[0])

        self._assert_phonenumber_alias_removed(
            uid=accounts[1].uid,
            phone_number=TEST_PHONE_NUMBER1,
            reason_uid=accounts[0].uid,
        )

        self.assertEqual(len(self._fake_mailer.messages), 2)
        self.assertEqual(
            self._fake_mailer.messages[0]['subject'],
            'phone_alias.as_login_disabled_subject',
        )
        self.assertEqual(
            self._fake_mailer.messages[1],
            self._build_email(
                accounts[1],
                template_name='mail/phone_unbound_secure.html',
            ),
        )

    def test_limit_not_exceeded(self):
        accounts = [
            dict(binding_time=TEST_TIME1 + timedelta(hours=1)),
            dict(binding_time=TEST_TIME1),
        ]
        accounts = self._build_other_accounts(accounts)

        self._unbind_old_phone(get_first_phone(accounts[0]))

        self._check_phone(accounts, assert_simple_phone_bound)

    def test_ignore_binding(self):
        flags = PhoneBindingsFlags()
        flags.should_ignore_binding_limit = True

        accounts = [
            dict(
                # Новый телефон привязывается с флагом should_ignore_binding_limit,
                # т.е. он не должен триггерить отвязку телефона от других
                # аккаунтов.
                binding_flags=flags,
                binding_time=TEST_TIME1 + timedelta(hours=1),
            ),

            dict(binding_time=TEST_TIME1),
            dict(binding_time=TEST_TIME1),
        ]
        accounts = self._build_other_accounts(accounts)

        self._unbind_old_phone(get_first_phone(accounts[0]))

        self._check_phone(accounts, assert_simple_phone_bound)

    def test_bound_later(self):
        accounts = [
            dict(
                binding_time=TEST_TIME1 - timedelta(seconds=1),
            ),

            dict(binding_time=TEST_TIME1),
            dict(binding_time=TEST_TIME1),
        ]
        accounts = self._build_other_accounts(accounts)

        self._unbind_old_phone(get_first_phone(accounts[0]))

        self._check_phone(accounts, assert_simple_phone_bound)

    def test_dont_count_in_operation(self):
        accounts = [
            dict(
                binding_time=TEST_TIME1 + timedelta(hours=1),
            ),

            dict(binding_time=TEST_TIME1),
            dict(
                binding_time=TEST_TIME1,
                in_operation=True,
            ),
        ]
        accounts = self._build_other_accounts(accounts)

        self._unbind_old_phone(get_first_phone(accounts[0]))

        self._check_phone(accounts[:2], assert_simple_phone_bound)
        self._check_phone([accounts[2]], assert_simple_phone_being_securified)

    def test_dont_unbind_in_operation(self):
        accounts = [
            dict(
                binding_time=TEST_TIME1 + timedelta(hours=1),
            ),

            dict(binding_time=TEST_TIME1),
            dict(
                binding_time=TEST_TIME1,
                in_operation=True,
            ),
            dict(binding_time=TEST_TIME1),
        ]
        accounts = self._build_other_accounts(accounts)

        self._unbind_old_phone(get_first_phone(accounts[0]))

        self._check_phone([accounts[0]], assert_simple_phone_bound)
        self._assert_phones_unbound([accounts[1]], accounts[0])
        self._check_phone([accounts[2]], assert_simple_phone_being_securified)
        self._check_phone([accounts[3]], assert_simple_phone_bound)

    def test_dont_count_2fa(self):
        accounts = [
            dict(
                binding_time=TEST_TIME1 + timedelta(hours=1),
            ),

            dict(binding_time=TEST_TIME1),
            dict(
                binding_time=TEST_TIME1,
                enabled_2fa=True,
            ),
        ]
        accounts = self._build_other_accounts(accounts)

        self._unbind_old_phone(get_first_phone(accounts[0]))

        self._check_phone(accounts[:2], assert_simple_phone_bound)
        self._check_phone([accounts[2]], assert_secure_phone_bound)

    def test_dont_unbind_2fa_and_sms_2fa(self):
        accounts = [
            dict(
                binding_time=TEST_TIME1 + timedelta(hours=1),
            ),

            dict(binding_time=TEST_TIME1),
            dict(binding_time=TEST_TIME1),
            dict(
                binding_time=TEST_TIME1,
                enabled_2fa=True,
            ),
            dict(
                binding_time=TEST_TIME1,
                enabled_sms_2fa=True,
            ),
        ]
        accounts = self._build_other_accounts(accounts)

        self._unbind_old_phone(get_first_phone(accounts[0]))

        self._check_phone([accounts[0]], assert_simple_phone_bound)
        self._assert_phones_unbound([accounts[1]], accounts[0])
        self._check_phone([accounts[2]], assert_simple_phone_bound)
        self._check_phone([accounts[3]], assert_secure_phone_bound)

    def test_unbind_secure_from_passwordless(self):
        accounts = [
            dict(binding_time=TEST_TIME1 + timedelta(hours=1)),

            dict(
                alias_type='social',
                binding_time=TEST_TIME1,
                crypt_password=None,
            ),
            dict(binding_time=TEST_TIME1),
        ]
        accounts = self._build_other_accounts(accounts)

        self._unbind_old_phone(get_first_phone(accounts[0]))

        self._assert_phones_unbound([accounts[1]], accounts[0])

        self.assertEqual(
            self._fake_mailer.messages,
            [
                self._build_email(
                    accounts[1],
                    login=accounts[1].person.firstname,
                ),
            ],
        )

    def test_db_error(self):
        accounts = [
            dict(
                binding_time=TEST_TIME1 + timedelta(hours=1),
            ),

            dict(binding_time=TEST_TIME1),
            dict(binding_time=TEST_TIME1),
        ]
        accounts = self._build_other_accounts(accounts)

        self._db_faker.set_side_effect_for_db('passportdbshard1', DBError())

        self._unbind_old_phone(get_first_phone(accounts[0]))

        self._check_phone(accounts, assert_simple_phone_bound)
        self.assertEqual(self._mailer_faker.messages, list())

    def test_blackbox_phone_bindings_fail(self):
        accounts = [
            dict(
                binding_time=TEST_TIME1 + timedelta(hours=1),
            ),

            dict(binding_time=TEST_TIME1),
            dict(binding_time=TEST_TIME1),
        ]
        accounts = self._build_other_accounts(accounts)

        self._blackbox_builder_faker.set_response_value(
            'phone_bindings',
            blackbox_json_error_response('DB_FETCHFAILED'),
        )

        with self.assertRaises(BlackboxTemporaryError):
            self._unbind_old_phone(get_first_phone(accounts[0]))

        self._check_phone(accounts, assert_simple_phone_bound)

    def test_blackbox_userinfo_fail(self):
        accounts = [
            dict(
                binding_time=TEST_TIME1 + timedelta(hours=1),
            ),

            dict(binding_time=TEST_TIME1),
            dict(binding_time=TEST_TIME1),
        ]
        accounts = self._build_other_accounts(accounts)

        self._blackbox_builder_faker.set_response_value(
            'userinfo',
            blackbox_json_error_response('DB_FETCHFAILED'),
        )

        with self.assertRaises(BlackboxTemporaryError):
            self._unbind_old_phone(get_first_phone(accounts[0]))

        self._check_phone(accounts, assert_simple_phone_bound)

    def test_race_phone_bindings_and_get_accounts(self):
        """
        Ручка phone_bindings сообщила, что номер привязан к учётной записи, а
        ручка userinfo сообщила, что номера нет.
        """
        self._build_other_accounts(
            [
                dict(
                    confirmation_time=TEST_TIME1 + timedelta(hours=1),
                ),

                dict(
                    confirmation_time=TEST_TIME1,
                ),
                dict(
                    phone_number=None,
                ),
            ],
        )

        # Переопределяем phone_bindings
        accounts = self._build_other_accounts(
            [
                dict(
                    confirmation_time=TEST_TIME1 + timedelta(hours=1),
                ),

                dict(
                    confirmation_time=TEST_TIME1,
                ),
                dict(
                    confirmation_time=TEST_TIME1,
                ),
            ],
            setup_blackbox_userinfo=False,
            setup_db=False,
        )

        self._unbind_old_phone(get_first_phone(accounts[0]))

        self._check_phone([accounts[0], accounts[1]], assert_simple_phone_bound)

        assert_no_phone_in_db(
            self._db_faker,
            accounts[2].uid,
            get_first_phone(accounts[2]).id,
            TEST_PHONE_NUMBER1,
        )

    def test_phone_bindings_does_not_know_about_new_binding(self):
        """
        ЧЯ не знает о созданной связке

        Очень вероятный сценарий, т.к. мы пишем в мастер, а ЧЯ читает из
        реплики.
        """
        # На самом деле в БД уже три телефона
        accounts = self._build_other_accounts(
            [
                dict(
                    confirmation_time=TEST_TIME1 + timedelta(hours=1),
                    phone_id=TEST_PHONE_ID1,
                    uid=TEST_UID1,
                ),

                dict(
                    confirmation_time=TEST_TIME1,
                    phone_id=TEST_PHONE_ID2,
                    uid=TEST_UID2,
                ),
                dict(
                    confirmation_time=TEST_TIME1,
                    phone_id=TEST_PHONE_ID3,
                    uid=TEST_UID3,
                ),
            ],
        )

        # ЧЯ пока знает только о двух телефонах
        self._build_other_accounts(
            [
                dict(
                    confirmation_time=TEST_TIME1,
                    phone_id=TEST_PHONE_ID2,
                    uid=TEST_UID2,
                ),
                dict(
                    confirmation_time=TEST_TIME1,
                    phone_id=TEST_PHONE_ID3,
                    uid=TEST_UID3,
                ),
            ],
            setup_db=False,
        )

        self._unbind_old_phone(get_first_phone(accounts[0]))

        self._check_phone([accounts[0], accounts[2]], assert_simple_phone_bound)
        self._assert_phones_unbound([accounts[1]], accounts[0])


@with_settings_hosts(
    ALL_SUPPORTED_LANGUAGES=TEST_ALL_SUPPORTED_LANGUAGES,
    BLACKBOX_ATTRIBUTES=tuple(),
    BLACKBOX_MAX_UIDS_PER_REQUEST=100,
    BLACKBOX_PHONE_EXTENDED_ATTRIBUTES=tuple(),
    BLACKBOX_URL='http://blackbox.url/',
    DISPLAY_LANGUAGES=TEST_DISPLAY_LANGUAGES,
    translations=TranslationSettings(),
    YASMS_PHONE_BINDING_LIMIT=1,
)
class TestLimit1UnbindOldPhone(UnbindOldPhoneTestCase):
    def test(self):
        accounts = [
            dict(
                binding_time=TEST_TIME1 + timedelta(hours=1),
                confirmation_time=TEST_TIME1 + timedelta(hours=1),
            ),

            dict(
                binding_time=TEST_TIME1,
                confirmation_time=TEST_TIME1,
                is_phone_secure=True,
            ),
        ]
        accounts = self._build_other_accounts(accounts)

        self._unbind_old_phone(get_first_phone(accounts[0]))

        self._check_phone([accounts[0]], assert_simple_phone_bound)
        self._assert_phones_unbound([accounts[1]], accounts[0])
