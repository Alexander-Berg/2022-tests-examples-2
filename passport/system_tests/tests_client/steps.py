import allure
from qa.test_user_service.tus_api.tests.system_tests.tests_client.settings import (
    DEFAULT_TUS_CONSUMER_FOR_TESTS,
    PASSPORT_ENVIRONMENT_FOR_TESTS,
)
from qa.test_user_service.tus_api.tests.system_tests.tests_client.utils import Account
from qa.test_user_service.tus_api.tests.system_tests.tests_client.views_requests import (
    CreateAccountPortal,
    RemoveAccount,
)


@allure.step('Создаём новый аккаунт')
def create_new_user(env=PASSPORT_ENVIRONMENT_FOR_TESTS, tus_consumer=DEFAULT_TUS_CONSUMER_FOR_TESTS):
    data = {
        'tus_consumer': tus_consumer,
        'env': env
    }
    return Account(**CreateAccountPortal(data).call()['account'])


@allure.step('Удаляем аккаунт из TUS')
def remove_account_from_tus(uid, env):
    data = {
        'tus_consumer': 'lexcorp-consumer',
        'uid': uid,
        'env': env
    }
    return RemoveAccount(data).call()
