import unittest

import allure
from hamcrest import assert_that
from qa.test_user_service.tus_api.tests.system_tests.tests_client.settings import (
    DEFAULT_TUS_CONSUMER_FOR_TESTS,
    NON_DEFAULT_TUS_CONSUMER_FOR_TESTS,
    PASSPORT_ENVIRONMENT_FOR_TESTS,
)
from qa.test_user_service.tus_api.tests.system_tests.tests_client.steps import create_new_user
from qa.test_user_service.tus_api.tests.system_tests.tests_client.test_accounts import account_from_other_consumer
from qa.test_user_service.tus_api.tests.system_tests.tests_client.tus_response_matcher import (
    is_ok_response,
    is_tus_error,
)
from qa.test_user_service.tus_api.tests.system_tests.tests_client.views_requests import (
    GetAccount,
    RemoveAccount,
)


@allure.feature('Убираем из TUS сохранённый аккаунт')
@allure.story('/1/remove_account_from_tus/')
class RemoveAccountTestCase(unittest.TestCase):

    def setUp(self):
        self.env = PASSPORT_ENVIRONMENT_FOR_TESTS
        self.user = create_new_user(self.env)
        self.data = {
            'tus_consumer': DEFAULT_TUS_CONSUMER_FOR_TESTS,
            'env': self.env,
            'uid': self.user.uid,
        }

    @allure.title('Убираем аккаунт из TUS')
    def test_should_remove_account(self):
        tus_response = RemoveAccount(self.data).call()
        assert_that(tus_response, is_ok_response())
        tus_response = GetAccount(self.data).call()
        assert_that(tus_response, is_tus_error(
            'account.not_found',
            'No suitable account in TUS DB'
        ))

    @allure.title('Не убираем аккаунт, если аккаунт не сохранён в TUS')
    def test_should_not_remove_account_if_account_is_not_saved(self):
        tus_response = RemoveAccount(self.data).call()
        assert_that(tus_response, is_ok_response())
        tus_response = RemoveAccount(self.data).call()
        assert_that(tus_response, is_tus_error(
            'account.not_found',
            'No suitable account in TUS DB'
        ))

    @allure.title('Не убираем аккаунт, если аккаунт сохранён с другим окружением')
    def test_should_not_remove_account_with_other_environment(self):
        other_env = 'PROD' if self.env == 'TEST' else 'TEST'
        self.data['env'] = other_env
        tus_response = RemoveAccount(self.data).call()
        assert_that(tus_response, is_tus_error(
            'account.not_found',
            'No suitable account in TUS DB'
        ))
        self.data['env'] = self.env
        tus_response = GetAccount(self.data).call()
        assert_that(tus_response, is_ok_response())

    @allure.title('Не убираем аккаунт, если нет доступа к консьюмеру')
    def test_should_not_remove_account_from_consumer_with_no_access(self):
        self.data['uid'] = account_from_other_consumer(self.env)
        tus_response = RemoveAccount(self.data).call()
        assert_that(tus_response, is_tus_error(
            'tus_consumer.access_denied',
            "Requested account belongs to '{account_consumer}' consumer. "
            "Requested consumer: '{requested_consumer}'".format(
                account_consumer=NON_DEFAULT_TUS_CONSUMER_FOR_TESTS,
                requested_consumer=DEFAULT_TUS_CONSUMER_FOR_TESTS,
            )
        ))

    @allure.title('Не убираем аккаунт из пользовательского consumer-а, если consumer не передан')
    def test_should_not_remove_account_from_custom_consumer_without_consumer_parameter(self):
        del self.data['tus_consumer']
        tus_response = RemoveAccount(self.data).call()
        assert_that(tus_response, is_tus_error(
            'tus_consumer.access_denied',
            "Requested account belongs to '{account_consumer}' consumer. "
            "Requested consumer: '{requested_consumer}'".format(
                account_consumer=NON_DEFAULT_TUS_CONSUMER_FOR_TESTS,
                requested_consumer='tus_common',
            )
        ))

    @allure.title('Не убираем аккаунт, если uid не передан')
    def test_should_not_remove_account_without_uid(self):
        del self.data['uid']
        tus_response = RemoveAccount(self.data).call()
        assert_that(tus_response, is_tus_error(
            'request.invalid',
            'uid: Missing value'
        ))
