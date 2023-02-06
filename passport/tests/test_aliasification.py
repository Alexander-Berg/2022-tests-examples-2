# -*- coding: utf-8 -*-

from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.env import Environment
from passport.backend.core.mailer.faker import TemplateFakeMailer
from passport.backend.core.mailer.faker.mail_utils import create_native_email
from passport.backend.core.models.phones.faker import (
    build_account,
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.core.runner.context_managers import UPDATE
from passport.backend.core.test.consts import (
    TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
    TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
    TEST_CONSUMER1,
    TEST_DATETIME1,
    TEST_EMAIL1,
    TEST_EMAIL2,
    TEST_LOGIN1,
    TEST_LOGIN2,
    TEST_PHONE_ID1,
    TEST_PHONE_ID2,
    TEST_PHONE_NUMBER1,
    TEST_PHONISH_LOGIN1,
    TEST_UID1,
    TEST_UID2,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.types.bit_vector.bit_vector import PhoneBindingsFlags
from passport.backend.core.undefined import Undefined
from passport.backend.core.yasms.phonenumber_alias import Aliasification
from passport.backend.utils.common import deep_merge

from .base import TestCase
from .consts import (
    TEST_ALL_SUPPORTED_LANGUAGES,
    TEST_DISPLAY_LANGUAGES,
    TranslationSettings,
)


@with_settings_hosts(
    ALL_SUPPORTED_LANGUAGES=TEST_ALL_SUPPORTED_LANGUAGES,
    BLACKBOX_ATTRIBUTES=tuple(),
    BLACKBOX_URL='http://blackbox.url/',
    DISPLAY_LANGUAGES=TEST_DISPLAY_LANGUAGES,
    translations=TranslationSettings(),
)
class TestAliasification(TestCase):
    def setUp(self):
        super(TestAliasification, self).setUp()
        self._fake_mailer = TemplateFakeMailer().start()

    def tearDown(self):
        self._fake_mailer.stop()
        del self._fake_mailer
        super(TestAliasification, self).tearDown()

    def test_phonish_account__alias_not_allowed(self):
        account = self._build_phonish_account()

        with self.assertRaises(Aliasification.AliasNotAllowed):
            self._build_aliasification(account=account)

    def test_phonish_account__no_check___alias_not_allowed(self):
        account = self._build_phonish_account(is_phone_secure=True)
        self._blackbox_builder_faker.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        aliasification = self._build_aliasification(
            account=account,
            should_check_if_alias_allowed=False,
        )
        aliasification.get_owner()
        with self.assertRaises(Aliasification.AliasNotAllowed):
            aliasification.give_out()

    def test_new_ivory_coast_busy_phone_alias(self):
        self.check_ivory_coast_busy_phone_alias(
            new_alias_phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
            busy_alias_phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
        )

    def test_old_ivory_coast_busy_phone_alias(self):
        self.check_ivory_coast_busy_phone_alias(
            new_alias_phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
            busy_alias_phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
        )

    def check_ivory_coast_busy_phone_alias(self, new_alias_phone_number, busy_alias_phone_number):
        """
        Проверяем, что, включая ЦА на новом (старом) телефоне из Кот-Д'Ивуара,
        мы отключаем ЦА и на соответствующем старом (новом) телефоне.
        """
        alpha_account = self._build_alpha_account(phone_number=new_alias_phone_number)

        beta_account_descriptor = self._build_beta_account_descriptor(phone_number=busy_alias_phone_number)
        self._blackbox_builder_faker.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(uid=None),
                blackbox_userinfo_response(**beta_account_descriptor),
            ],
        )
        beta_account = build_account(db_faker=self._db_faker, **beta_account_descriptor)

        aliasification = self._build_aliasification(
            account=alpha_account,
            phone_number=new_alias_phone_number,
        )

        old_owner = aliasification.get_owner()
        self.assertEqual(old_owner.uid, beta_account.uid)

        with UPDATE(
            old_owner,
            Environment(),
            dict(action='phone_alias_delete', consumer=TEST_CONSUMER1),
            initiator_uid=alpha_account.uid,
        ):
            aliasification.take_away()

        self._assert_account_does_not_have_alias(old_owner)

        with UPDATE(
            alpha_account,
            Environment(),
            dict(action='phone_alias_create', consumer=TEST_CONSUMER1),
        ):
            aliasification.give_out()

        self._assert_account_has_alias(alpha_account, new_alias_phone_number)

        self._blackbox_builder_faker.requests[0].assert_post_data_contains(
            dict(
                method='userinfo',
                login=new_alias_phone_number.digital,
            ),
        )
        self._blackbox_builder_faker.requests[1].assert_post_data_contains(
            dict(
                method='userinfo',
                login=busy_alias_phone_number.digital,
            ),
        )

    def test_check_replace_old_ivory_coast_phone(self):
        self.check_replace_ivory_coast_phone(
            new_alias_phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
            busy_alias_phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
        )

    def test_check_replace_new_ivory_coast_phone(self):
        self.check_replace_ivory_coast_phone(
            new_alias_phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
            busy_alias_phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
        )

    def check_replace_ivory_coast_phone(self, new_alias_phone_number, busy_alias_phone_number):
        account_descriptor = self._build_alpha_account_descriptor(
            aliases=dict(
                phonenumber=busy_alias_phone_number.digital,
                portal=TEST_LOGIN1,
            ),
            phone_number=busy_alias_phone_number,
        )
        account = self._build_alpha_account(
            db_faker=self._db_faker,
            descriptor=account_descriptor,
        )

        self._blackbox_builder_faker.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(uid=None),
                blackbox_userinfo_response(**account_descriptor),
            ],
        )

        aliasification = self._build_aliasification(
            account=account,
            phone_number=new_alias_phone_number,
            should_check_secure_phone=False
        )

        self.assertIsNone(aliasification.get_owner())

        with UPDATE(
            account,
            Environment(),
            dict(action='acquire_phone', consumer=TEST_CONSUMER1),
        ):
            aliasification.take_old_alias_away()

        self._assert_account_does_not_have_alias(account)

        with UPDATE(
            account,
            Environment(),
            dict(action='phone_alias_create', consumer=TEST_CONSUMER1),
        ):
            account.phones.remove(account.phones.secure)
            self._phone_id_generator_faker.set_list([TEST_PHONE_ID2])
            account.phones.secure = account.phones.create(
                bound=TEST_DATETIME1,
                confirmed=TEST_DATETIME1,
                number=new_alias_phone_number,
                secured=TEST_DATETIME1,
            )
            aliasification.give_out()

        self._assert_account_has_alias(account, new_alias_phone_number)

        self._blackbox_builder_faker.requests[0].assert_post_data_contains(
            dict(
                method='userinfo',
                login=new_alias_phone_number.digital,
            ),
        )
        self._blackbox_builder_faker.requests[1].assert_post_data_contains(
            dict(
                method='userinfo',
                login=busy_alias_phone_number.digital,
            ),
        )

    def _build_aliasification(self, **kwargs):
        defaults = {
            'phone_number': TEST_PHONE_NUMBER1,
            'consumer': TEST_CONSUMER1,
            'blackbox': self._blackbox_builder,
            'statbox': self._statbox,
        }
        for key, value in defaults.items():
            kwargs.setdefault(key, value)
        return Aliasification(**kwargs)

    def _build_phonish_account(self, is_phone_secure=False):
        kwargs = {
            'uid': TEST_UID1,
            'login': TEST_PHONISH_LOGIN1,
            'aliases': {'phonish': TEST_PHONISH_LOGIN1},
        }

        if is_phone_secure:
            # Хоть у Phonish'ей и не бывает защищённых телефонов, но для теста
            # нужен недорегистрированный аккаунт с защищённым телефоном.
            kwargs = deep_merge(
                kwargs,
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                ),
            )
        else:
            binding_flags = PhoneBindingsFlags()
            binding_flags.should_ignore_binding_limit = True
            kwargs = deep_merge(
                kwargs,
                build_phone_bound(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                    binding_flags=binding_flags,
                ),
            )

        return build_account(db_faker=self._db_faker, **kwargs)

    def _build_alpha_account(
        self,
        blackbox_faker=None,
        db_faker=Undefined,
        descriptor=None,
        **kwargs
    ):
        if db_faker is Undefined:
            db_faker = self._db_faker
        if descriptor is None:
            descriptor = self._build_alpha_account_descriptor(**kwargs)
        return build_account(
            db_faker=db_faker,
            blackbox_faker=blackbox_faker,
            **descriptor
        )

    def _build_alpha_account_descriptor(
        self,
        login=TEST_LOGIN1,
        phone_number=None,
        **kwargs
    ):
        if 'emails' not in kwargs:
            mail = create_native_email(login=TEST_EMAIL1.split('@')[0], domain=TEST_EMAIL1.split('@')[1])
            kwargs.update(emails=[mail])

        if phone_number is None:
            phone_number = TEST_PHONE_NUMBER1

        return dict(
            uid=TEST_UID1,
            login=login,
            language='ru',
            firstname=TEST_LOGIN1,
            **deep_merge(
                build_phone_secured(TEST_PHONE_ID1, phone_number.e164),
                kwargs,
            )
        )

    def _build_beta_account(self, **kwargs):
        descriptor = self._build_beta_account_descriptor(**kwargs)
        return build_account(
            db_faker=self._db_faker,
            blackbox_faker=self._blackbox_builder_faker,
            **descriptor
        )

    def _build_beta_account_descriptor(self, phone_number=None, **kwargs):
        if phone_number is None:
            phone_number = TEST_PHONE_NUMBER1
        if 'emails' not in kwargs:
            mail = create_native_email(login=TEST_EMAIL2.split('@')[0], domain=TEST_EMAIL2.split('@')[1])
            kwargs.update(emails=[mail])
        return dict(
            uid=TEST_UID2,
            login=TEST_LOGIN2,
            firstname=TEST_LOGIN2,
            language='ru',
            aliases={
                'portal': TEST_LOGIN2,
                'phonenumber': phone_number.digital,
            },
            attributes={'account.enable_search_by_phone_alias': '1'},
            **kwargs
        )

    def _assert_account_does_not_have_alias(self, account):
        self.assertFalse(account.phonenumber_alias)
        self._db_faker.check_missing('aliases', 'phonenumber', uid=account.uid, db='passportdbcentral')

    def _assert_account_has_alias(self, account, phone_number=None):
        if phone_number is None:
            phone_number = TEST_PHONE_NUMBER1
        self.assertEqual(account.phonenumber_alias.alias, phone_number.digital)
        self._db_faker.check('aliases', 'phonenumber', phone_number.digital, uid=account.uid, db='passportdbcentral')
