# coding=utf-8
import unittest

import allure
from hamcrest import (
    assert_that,
    matches_regexp,
)
from qa.test_user_service.tus_api.tests.system_tests.tests_client.settings import (
    DEFAULT_TUS_CONSUMER_FOR_TESTS,
    LOGIN_FOR_OAUTH_TOKEN,
    NON_DEFAULT_TUS_CONSUMER_FOR_TESTS,
    PASSPORT_ENVIRONMENT_FOR_TESTS,
)
from qa.test_user_service.tus_api.tests.system_tests.tests_client.steps import create_new_user
from qa.test_user_service.tus_api.tests.system_tests.tests_client.test_accounts import (
    account_from_other_consumer,
    account_with_different_password,
    deleted_account,
)
from qa.test_user_service.tus_api.tests.system_tests.tests_client.tus_response_matcher import (
    is_ok_response,
    is_tus_error,
)
from qa.test_user_service.tus_api.tests.system_tests.tests_client.utils import get_passport_environment_for_env
from qa.test_user_service.tus_api.tests.system_tests.tests_client.views_requests import (
    BindPhone,
    RemoveAccount,
)


VALID_PHONE = '+70001234567'
INVALID_TEST_PHONE = '+7000123456790'  # префикс совпадает, но номер слишком длинный
NOT_TEST_PHONE = '+71234567890'


@allure.feature('Привязываем телефон к аккаунту')
@allure.story('/1/bind_phone/')
class BindPhoneTestCase(unittest.TestCase):

    def setUp(self):
        self.env = PASSPORT_ENVIRONMENT_FOR_TESTS

    @allure.title('Привязываем телефон к аккаунту, не указывая номер')
    def test_should_bind_phone(self):
        self.user = create_new_user(self.env)
        data = {
            'uid': self.user.uid,
        }
        tus_response = BindPhone(data).call()
        assert_that(tus_response, is_ok_response(expected_entries={
            'passport_environment': get_passport_environment_for_env(self.env),
        }))
        assert_that(
            tus_response.json()['phone_number'],
            matches_regexp(r'^\+70000\d{6}$'),
            reason='Генерируем номера с 4-мя ведущими нулями'
        )

    @allure.title('Привязываем телефон к аккаунту, указывая номер')
    def test_should_bind_phone_with_phone_number(self):
        self.user = create_new_user(self.env)
        phone = VALID_PHONE
        data = {
            'phone_number': phone,
            'uid': self.user.uid,
        }
        tus_response = BindPhone(data).call()
        assert_that(tus_response, is_ok_response(expected_entries={
            'phone_number': phone,
            'passport_environment': get_passport_environment_for_env(self.env),
        }))

    @allure.title('Получаем ошибку, если номер некорректный')
    def test_should_not_bind_phone_with_bad_phone(self):
        self.user = create_new_user(self.env)
        data = {
            'phone_number': INVALID_TEST_PHONE,
            'uid': self.user.uid,
        }
        tus_response = BindPhone(data).call()
        assert_that(tus_response, is_tus_error(
            'passport.bind_phone_failed',
            'number.invalid'
        ))

    @allure.title('Получаем ошибку, если номер не тестовый')
    def test_should_not_bind_phone_with_not_test_phone(self):
        self.user = create_new_user(self.env)
        data = {
            'phone_number': NOT_TEST_PHONE,
            'uid': self.user.uid,
        }
        tus_response = BindPhone(data).call()
        assert_that(tus_response, is_tus_error(
            'request.invalid',
            'phone_number: Should start with \'+7000\'. TUS allows to bind only fake phone numbers'
        ))

    @allure.title('Получаем ошибку, если к аккаунту уже привязан номер')
    def test_should_not_bind_phone_to_account_with_bound_phone(self):
        self.user = create_new_user(self.env)
        data = {
            'uid': self.user.uid,
        }
        tus_response = BindPhone(data).call()
        assert_that(tus_response, is_ok_response())
        tus_response = BindPhone(data).call()
        assert_that(tus_response, is_tus_error(
            'passport.bind_phone_failed',
            'phone_secure.bound_and_confirmed'
        ))

    @allure.title('Получаем ошибку, если у аккаунта неверный пароль')
    def test_should_not_bind_phone_to_account_with_bound_phone(self):
        """Используем сохранённый в TUS аккаунт, которому поменяли пароль"""
        data = {
            'uid': account_with_different_password(self.env),
        }
        tus_response = BindPhone(data).call()
        assert_that(tus_response, is_tus_error(
            'passport.bind_phone_failed',
            'password.not_matched'
        ))

    @allure.title('Получаем ошибку, если аккаунт удалён')
    def test_should_not_bind_phone_with_deleted_uid(self):
        data = {
            'uid': deleted_account(self.env),
        }
        tus_response = BindPhone(data).call()
        assert_that(tus_response, is_tus_error(
            'passport.bind_phone_failed',
            'account.not_found'  # в проде какое-то время может быть account.disabled_on_deletion
        ))

    @allure.title('Получаем ошибку, если uid не сохранён в TUS')
    def test_should_not_bind_phone_to_not_saved_account(self):
        self.user = create_new_user(self.env)
        data = {
            'uid': self.user.uid,
        }
        tus_response = RemoveAccount({
            'uid': self.user.uid,
            'tus_consumer': DEFAULT_TUS_CONSUMER_FOR_TESTS,
        }).call()
        assert_that(tus_response, is_ok_response())
        tus_response = BindPhone(data).call()
        assert_that(tus_response, is_tus_error(
            'account.not_found',
            'No suitable account in TUS DB'
        ))

    @allure.title('Получаем ошибку, если к uid нет доступа')
    def test_should_not_bind_phone_to_account_from_other_consumer(self):
        data = {
            'uid': account_from_other_consumer(self.env),
        }
        tus_response = BindPhone(data).call()
        assert_that(tus_response, is_tus_error(
            'tus_consumer.access_denied',
            "Client with login '{login}' can't use consumer '{consumer}'. Request a role with IDM".format(
                login=LOGIN_FOR_OAUTH_TOKEN,
                consumer=NON_DEFAULT_TUS_CONSUMER_FOR_TESTS
            )
        ))

    @allure.title('Получаем ошибку, если передали uid и не соответсвующее ему окружение')
    def test_should_not_bind_phone_to_account_from_other_environment(self):
        self.user = create_new_user(self.env)
        other_env = 'PROD' if self.env == 'TEST' else 'TEST'
        data = {
            'uid': self.user.uid,
            'env': other_env,
        }
        tus_response = BindPhone(data).call()
        assert_that(tus_response, is_tus_error(
            'account.not_found',
            'No suitable account in TUS DB'
        ))

    @allure.title('Получаем ошибку, если uid не указан')
    def test_should_not_bind_phone_without_uid(self):
        tus_response = BindPhone().call()
        assert_that(tus_response, is_tus_error(
            'request.invalid',
            'uid: Missing value'
        ))

    @allure.title('Получаем ошибку, если uid некорректный')
    def test_should_not_bind_phone_with_invalid_uid(self):
        data = {
            'uid': 'wrong_uid',
        }
        tus_response = BindPhone(data).call()
        assert_that(tus_response, is_tus_error(
            'request.invalid',
            'uid: Please enter an integer value'
        ))

    @allure.title('Получаем ошибку, если uid нет в Паспорте')
    def test_should_not_bind_phone_with_too_long_uid(self):
        data = {
            'uid': '1111111111111111111111111'  # слишком длинный для настоящего
        }
        tus_response = BindPhone(data).call()
        assert_that(tus_response, is_tus_error(
            'request.invalid',
            'uid: Please enter a number that is 9223372036854775806 or smaller'
        ))

    @allure.title('Получаем ошибку, если language некорректный')
    def test_should_not_bind_phone_with_invalid_language(self):
        self.user = create_new_user(self.env)
        data = {
            'uid': self.user.uid,
            'language': 'elven',
        }
        tus_response = BindPhone(data).call()
        assert_that(tus_response, is_tus_error(
            'passport.bind_phone_failed',
            'display_language.invalid'
        ))
