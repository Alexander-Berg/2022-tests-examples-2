# coding=utf-8
import allure
from qa.test_user_service.tus_api.settings import SSL_CA_CERT
from qa.test_user_service.tus_api.tests.system_tests.tests_client.settings import (
    TUS_HOST_FOR_TESTS,
    TUS_OAUTH_TOKEN_FOR_TESTS,
)
import requests


class ApiMethod:
    def __init__(self, data=None):
        self.headers = {
            'Authorization': 'OAuth {token}'.format(token=TUS_OAUTH_TOKEN_FOR_TESTS),
        }
        self.data = data

    def call(self):
        raise NotImplementedError('Метод необходимо реализовать')


class CreateAccountPortal(ApiMethod):

    @allure.step('Вызываем ручку создания портального аккаунта')
    def call(self):
        tus_response = requests.post(
            url='https://{host}/1/create_account/portal/'.format(host=TUS_HOST_FOR_TESTS),
            data=self.data,
            headers=self.headers,
            verify=SSL_CA_CERT,
        )
        data = tus_response.json()
        return data


class GetAccount(ApiMethod):

    @allure.step('Вызываем ручку получения аккаунта')
    def call(self):
        tus_response = requests.get(
            url='https://{host}/1/get_account/'.format(host=TUS_HOST_FOR_TESTS),
            params=self.data,
            headers=self.headers,
            verify=SSL_CA_CERT,
        )
        return tus_response


class CreateTusConsumer(ApiMethod):

    @allure.step('Вызываем ручку создания tus_consumer')
    def call(self):
        tus_response = requests.get(
            url='https://{host}/1/create_tus_consumer/'.format(host=TUS_HOST_FOR_TESTS),
            params=self.data,
            headers=self.headers,
            verify=SSL_CA_CERT,
        )
        data = tus_response.json()
        return data


class BindPhone(ApiMethod):

    @allure.step('Вызываем ручку привязки телефона')
    def call(self):
        tus_response = requests.post(
            url='https://{host}/1/bind_phone/'.format(host=TUS_HOST_FOR_TESTS),
            data=self.data,
            headers=self.headers,
            verify=SSL_CA_CERT,
        )
        return tus_response


class SaveAccount(ApiMethod):

    @allure.step('Вызываем ручку сохранения аккаунта')
    def call(self):
        tus_response = requests.post(
            url='https://{host}/1/save_account/'.format(host=TUS_HOST_FOR_TESTS),
            data=self.data,
            headers=self.headers,
            verify=SSL_CA_CERT,
        )
        data = tus_response.json()
        return data


class RemoveAccount(ApiMethod):

    @allure.step('Вызываем ручку удалени аккаунта из TUS')
    def call(self):
        tus_response = requests.get(
            url='https://{host}/1/remove_account_from_tus/'.format(host=TUS_HOST_FOR_TESTS),
            params=self.data,
            headers=self.headers,
            verify=SSL_CA_CERT,
        )
        return tus_response
