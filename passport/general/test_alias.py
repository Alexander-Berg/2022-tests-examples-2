from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.passport_api import PassportApi
from passport.backend.qa.autotests.base.helpers.account import with_portal_account
from passport.backend.qa.autotests.base.helpers.blackbox import check_blackbox_userinfo_by_uid
from passport.backend.qa.autotests.base.steps.account import set_alias
from passport.backend.qa.autotests.base.steps.cookie_steps import get_cookies
from passport.backend.qa.autotests.base.steps.phone import (
    bind_secure_phone,
    get_secure_phone_from_uid,
)
from passport.backend.qa.autotests.base.steps.registration_steps import register_portal_account
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)
from passport.backend.utils.phones import random_phone_number


def get_digital_phone_number(phone_number):
    return phone_number.replace('+', '')


def get_number_from_uid(uid):
    phone_number = get_secure_phone_from_uid(uid)
    return get_digital_phone_number(phone_number)


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /1/account/',
    story='/1/account/.../alias/',
)
class PassportAccountBankPhoneNumberAliasTestCase(BaseTestCase):

    @with_portal_account
    def test_create_bank_phonenumber_alias_with_bound_phone(self, account):
        account.cookies = get_cookies(account)

        bind_secure_phone(account, random_phone_number())
        phone_number = get_number_from_uid(account.uid)

        set_alias(account, 'bank_phonenumber', phone_number=phone_number)

        check_blackbox_userinfo_by_uid(
            uid=account.uid,
            aliases={'25': phone_number},
        )

    def test_create_bank_phonenumber_alias_with_not_available_phone(self):
        with register_portal_account(firstname='first', lastname='last') as user:
            user.cookies = get_cookies(user)

            bind_secure_phone(user, random_phone_number())
            phone_number = get_number_from_uid(user.uid)

            set_alias(user, 'bank_phonenumber', phone_number=phone_number)

            check_blackbox_userinfo_by_uid(
                uid=user.uid,
                aliases={'25': phone_number},
            )

            with register_portal_account() as account:
                rv = PassportApi().post(
                    path='/1/account/%s/alias/bank_phonenumber/' % account.uid,
                    form_params={'phone_number': phone_number},
                )

                self.assert_has_entries(rv, {'status': 'error'})

                check_blackbox_userinfo_by_uid(
                    uid=account.uid,
                    aliases={'25': None},
                )

    @with_portal_account
    def test_create_bank_phonenumber_alias_with_not_bound_phone(self, account):
        phone_number_e164 = random_phone_number()
        phone_number = get_digital_phone_number(phone_number_e164)

        set_alias(account, 'bank_phonenumber', phone_number=phone_number)

        check_blackbox_userinfo_by_uid(
            uid=account.uid,
            aliases={'25': phone_number},
            phone=phone_number,
        )
