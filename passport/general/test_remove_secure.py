from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.passport_api import PassportApi
from passport.backend.qa.autotests.base.helpers.account import with_portal_account_and_track
from passport.backend.qa.autotests.base.helpers.blackbox import check_blackbox_userinfo_by_uid
from passport.backend.qa.autotests.base.steps.account import (
    _get_headers,
    set_alias,
)
from passport.backend.qa.autotests.base.steps.phone import bind_secure_phone
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)
from passport.backend.utils.phones import random_phone_number


def get_digital_phone_number(phone_number):
    return phone_number.replace('+', '')


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /1/bundle/phone/manage/',
    story='/1/bundle/phone/manage/remove_secure/',
)
class PassportRemoveSecurePhoneTestCase(BaseTestCase):

    @with_portal_account_and_track
    def test_remove_bank_phonenumber_fail(self, account, track_id):
        phone_number = random_phone_number()
        bank_phonenumber = get_digital_phone_number(phone_number)

        bind_secure_phone(account, phone_number)
        set_alias(account, 'bank_phonenumber', phone_number=phone_number)
        check_blackbox_userinfo_by_uid(
            account.uid,
            aliases={'25': bank_phonenumber},
        )

        rv = PassportApi().post(
            path='/1/bundle/phone/manage/remove_secure/submit/',
            form_params=dict(
                display_language='ru',
                does_user_admit_secure_number=1,
                track_id=track_id,
            ),
            headers={
                'Ya-Client-Cookie': account.cookies,
                **_get_headers(),
            }
        )
        self.assert_has_entries(rv, {
            'status': 'error',
            'errors': [
                'phone.is_bank_phonenumber_alias',
            ]
        })
