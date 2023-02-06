from tests_cashback_int_api.utils import common


class BaseRequest:
    def __init__(self, taxi_cashback_int_api):
        self.client = taxi_cashback_int_api


class BindingCreate(BaseRequest):
    def request(self, *, yandex_uid, service='mango'):
        return (
            common.HttpRequest(self.client.post)
            .path('/4.0/cashback-int-api/v1/binding/create')
            .headers(yandex_uid=yandex_uid)
            .headers(service=service)
        )
