import allure
import mock
from nose_parameterized import parameterized
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.passport_api import PassportApi
from passport.backend.qa.autotests.base.helpers.account import with_portal_account
from passport.backend.qa.autotests.base.settings.common import (
    DEFAULT_USER_AGENT,
    PASSPORT_HOST,
)
from passport.backend.qa.autotests.base.steps.account import (
    add_question,
    set_options,
)
from passport.backend.qa.autotests.base.steps.blackbox import userinfo_by_uid
from passport.backend.qa.autotests.base.steps.registration_steps import (
    register_lite_account,
    register_portal_account,
)
from passport.backend.qa.autotests.base.test_env import test_env
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)
import yatest.common


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /1/bundle/account/reset/',
    story='/1/bundle/account/reset/',
)
class PassportAccountResetTestCase(BaseTestCase):
    @allure.step
    def setUp(self):
        super(PassportAccountResetTestCase, self).setUp()
        self.build_headers()

    def build_headers(self, cookies=None):
        self.default_headers = {
            'Ya-Client-Host': PASSPORT_HOST,
            'Ya-Client-User-Agent': DEFAULT_USER_AGENT,
            'Ya-Client-Cookie': cookies or '',
            'Ya-Consumer-Client-Ip': test_env.user_ip,
        }
        return self.default_headers

    def check_display_name(self, uid, reseted=False, name='Пользователь l.'):
        userinfo = userinfo_by_uid(
            uid,
            regname='yes',
        )
        if reseted:
            name = name
        else:
            name = userinfo['users'][0].get('login', '')
        self.assert_has_entries(
            userinfo['users'][0],
            {
                'display_name': {
                    'name': name,
                    'avatar': {'default': '0/0-0', 'empty': True}
                },
            },
        )

    @parameterized.expand(['full_name', 'public_name'])
    def test_can_reset_display_name_in_direct_order(self, query_arg_name):
        with register_portal_account(firstname='first', lastname='last') as user:
            rv = PassportApi().post(
                path='/1/bundle/account/reset/display_name/',
                form_params={
                    'uid': user.uid,
                    query_arg_name: ' '.join(['first', 'last']),
                },
                headers=self.default_headers,
            )

            self.assert_has_entries(rv, {'status': 'ok'})
            self.check_display_name(user.uid, True)

    def test_can_reset_display_name_in_reverse_order(self):
        with register_portal_account(firstname='first', lastname='last') as user:
            rv = PassportApi().post(
                path='/1/bundle/account/reset/display_name/',
                form_params={
                    'uid': user.uid,
                    'full_name': ' '.join(['last', 'first']),
                },
                headers=self.default_headers,
            )

            self.assert_has_entries(rv, {'status': 'ok'})
            self.check_display_name(user.uid, True)

    @parameterized.expand(['full_name', 'public_name'])
    def test_reset_display_name_error(self, query_arg_name):
        with register_portal_account(firstname='first', lastname='last') as user:
            rv = PassportApi().post(
                path='/1/bundle/account/reset/display_name/',
                form_params={
                    'uid': user.uid,
                    query_arg_name: 'kartoshka free',
                },
                headers=self.default_headers,
            )

            self.assert_has_entries(
                rv,
                {
                    'status': 'error',
                    'errors': ['action.impossible']
                },
            )
            self.check_display_name(user.uid)

    @parameterized.expand(['full_name', 'public_name'])
    def test_should_reset_display_name_for_user_with_other_language(self, query_arg_name):
        with register_portal_account(firstname='first', lastname='last', language='en') as user:
            rv = PassportApi().post(
                path='/1/bundle/account/reset/display_name/',
                form_params={
                    'uid': user.uid,
                    query_arg_name: ' '.join(['first', 'last']),
                },
                headers=self.default_headers,
            )

            self.assert_has_entries(rv, {'status': 'ok'})
            self.check_display_name(user.uid, True, 'User l.')

    @parameterized.expand(['full_name', 'public_name'])
    def test_should_reset_display_name_for_user_with_empty_lastname(self, query_arg_name):
        with register_portal_account(firstname='first', lastname=None) as user:
            rv = PassportApi().post(
                path='/1/bundle/account/reset/display_name/',
                form_params={
                    'uid': user.uid,
                    query_arg_name: 'first',
                },
                headers=self.default_headers,
            )

            self.assert_has_entries(rv, {'status': 'ok'})
            self.check_display_name(user.uid, True, 'Пользователь')

    @parameterized.expand(['full_name', 'public_name'])
    def test_should_reset_public_name_when_full_name_is_like_public_name(self, query_arg_name):
        with register_portal_account(firstname='first', lastname='last') as user:
            set_options(user, show_fio_in_public_name='1')

            rv_reset = PassportApi().post(
                path='/1/bundle/account/reset/display_name/',
                form_params={
                    'uid': user.uid,
                    query_arg_name: 'first last',
                },
                headers=self.default_headers,
            )

            self.assert_has_entries(rv_reset, {'status': 'ok'})
            self.check_display_name(user.uid, True)

    # TODO: Проверить CleanWeb при сбросе display_name невозможно, так как нельзя создать легально аккаунт с плохим ФИО
    # более подробно тут https://st.yandex-team.ru/PASSP-31157#6001ce452d39482e7a29f283

    def test_should_reset_question(self):
        with register_portal_account() as user:
            add_question(user.uid)

            rv_reset = PassportApi().post(
                path='/1/bundle/account/reset/question/',
                form_params={
                    'uid': user.uid,
                },
                headers=self.default_headers,
            )

            self.assert_has_entries(rv_reset, {'status': 'ok'})
            userinfo = userinfo_by_uid(
                user.uid,
            )
            self.assert_has_entries(
                userinfo['users'][0],
                {'have_hint': False},
            )

    def test_reset_question_without_question_error(self):
        with register_portal_account() as user:
            rv_reset = PassportApi().post(
                path='/1/bundle/account/reset/question/',
                form_params={
                    'uid': user.uid,
                },
                headers=self.default_headers,
            )

            self.assert_has_entries(
                rv_reset,
                {
                    'status': 'error',
                    'errors': ['action.impossible']
                },
            )

    def test_should_reset_phone(self):
        phone_number = '+70000012345'
        with register_portal_account() as user:
            # устанавливаем телефон
            PassportApi().post(
                path='/1/bundle/test/confirm_and_bind_phone/',
                form_params={
                    'uid': user.uid,
                    'password': user.password,
                    'number': phone_number,
                    'secure': '0',
                },
                headers={
                    **self.default_headers
                },
            )
            rv_reset = PassportApi().post(
                path='/1/bundle/account/reset/phone/',
                form_params={
                    'uid': user.uid,
                    'phone_number': phone_number,
                },
                headers=self.default_headers,
            )

            self.assert_has_entries(rv_reset, {'status': 'ok'})
            userinfo = userinfo_by_uid(
                user.uid,
                getphones='bound',
            )
            assert phone_number[1:] not in [phone['1'] for phone in userinfo['users'][0]['phones']]

    def test_should_reset_email(self):
        email = 'test@test.de'
        with register_portal_account(email=email) as user:
            rv_reset = PassportApi().post(
                path='/1/bundle/account/reset/email/',
                form_params={
                    'uid': user.uid,
                    'email': email,
                },
                headers=self.default_headers,
            )

            self.assert_has_entries(rv_reset, {'status': 'ok'})
            userinfo = userinfo_by_uid(
                user.uid,
                emails='getall'
            )
            assert email.lower() not in [addr['address'] for addr in userinfo['users'][0]['address-list']]

    def test_reset_email_nonexistent_email_error(self):
        with register_portal_account(email='test@test.de') as user:
            rv_reset = PassportApi().post(
                path='/1/bundle/account/reset/email/',
                form_params={
                    'uid': user.uid,
                    'email': 'stress@captcha.fr',
                },
                headers=self.default_headers,
            )

            self.assert_has_entries(
                rv_reset,
                {
                    'status': 'error',
                    'errors': ['action.impossible']
                },
            )

    def test_reset_email_lite_user_error(self):
        with register_lite_account() as user:
            rv_reset = PassportApi().post(
                path='/1/bundle/account/reset/email/',
                form_params={
                    'uid': user.uid,
                    'email': user.login,
                },
                headers=self.default_headers,
            )

            self.assert_has_entries(
                rv_reset,
                {
                    'status': 'error',
                    'errors': ['action.impossible']
                },
            )
            userinfo = userinfo_by_uid(
                user.uid,
                emails='getall'
            )
            assert user.login.lower() in [addr['address'] for addr in userinfo['users'][0]['address-list']]

    @with_portal_account
    def test_reset_avatar_ok(self, account):
        filename = 'passport/backend/qa/autotests/passport/v1/bundle/account/sample_avatar.png'
        with open(yatest.common.source_path(filename), 'rb') as avatar:
            rv = PassportApi().post(
                path='/2/change_avatar/',
                form_params={
                    'uid': account.uid,
                },
                files={
                    'file': avatar,
                },
                headers=self.build_headers(cookies=account.cookies),
            )

        self.assert_has_entries(rv, {'status': 'ok'})
        self.assert_has_keys(rv, ['avatar_url'])

        avatar_url = rv['avatar_url']
        avatar_key = avatar_url[avatar_url.index('get-yapic') + len('get-yapic/'):].rstrip('/normal')

        userinfo = userinfo_by_uid(account.uid, regname='yes')
        self.assert_has_entries(
            userinfo['users'][0],
            {
                'display_name': {
                    'name': mock.ANY,
                    'avatar': {'default': avatar_key, 'empty': False},
                },
            },
        )

        rv = PassportApi().post(
            path='/1/bundle/account/reset/avatar/',
            form_params={
                'uid': account.uid,
                'avatar_key': avatar_key
            },
        )
        self.assert_has_entries(rv, {'status': 'ok'})

        userinfo = userinfo_by_uid(account.uid, regname='yes')
        self.assert_has_entries(
            userinfo['users'][0],
            {
                'display_name': {
                    'name': mock.ANY,
                    'avatar': {'default': '0/0-0', 'empty': True},
                },
            },
        )

    @with_portal_account
    def test_reset_avatar__key_mismatch(self, account):
        filename = 'passport/backend/qa/autotests/passport/v1/bundle/account/sample_avatar.png'
        with open(yatest.common.source_path(filename), 'rb') as avatar:
            rv = PassportApi().post(
                path='/2/change_avatar/',
                form_params={
                    'uid': account.uid,
                },
                files={
                    'file': avatar,
                },
                headers=self.build_headers(cookies=account.cookies),
            )

        self.assert_has_entries(rv, {'status': 'ok'})
        self.assert_has_keys(rv, ['avatar_url'])

        avatar_url = rv['avatar_url']
        avatar_key = avatar_url[avatar_url.index('get-yapic') + len('get-yapic/'):].rstrip('/normal')

        userinfo = userinfo_by_uid(account.uid, regname='yes')
        self.assert_has_entries(
            userinfo['users'][0],
            {
                'display_name': {
                    'name': mock.ANY,
                    'avatar': {'default': avatar_key, 'empty': False},
                },
            },
        )

        rv = PassportApi().post(
            path='/1/bundle/account/reset/avatar/',
            form_params={
                'uid': account.uid,
                'avatar_key': '0/0-0',  # передаем не совпадающий avatar_key с тем, что записан в базу
            },
        )
        self.assert_has_entries(rv, {'status': 'ok'})

        userinfo = userinfo_by_uid(account.uid, regname='yes')
        self.assert_has_entries(
            userinfo['users'][0],
            {
                'display_name': {
                    'name': mock.ANY,
                    # ВНИМАНИЕ: аватарка не сбрасывается, потому что в ручку передан не тот avatar_key
                    'avatar': {'default': avatar_key, 'empty': False},
                },
            },
        )
