import datetime
import time
import typing
import uuid

import pytest
import requests


CARGO_API_PREFIX = 'api/b2b/cargo-claims'
DEFAULT_CORP_CLIENT_ID = '5e36732e2bc54e088b1466e08e31c486'


class HttpError(Exception):
    pass


class HttpNotFoundError(HttpError):
    pass


class HttpConflictError(HttpError):
    pass


HTTP_CODES = {404: HttpNotFoundError, 409: HttpConflictError}


class Headers:
    _internal_headers: typing.Dict[str, str] = {
        'X-B2B-Client-Id': DEFAULT_CORP_CLIENT_ID,
        'X-B2B-Client-Storage': 'cargo',
        'Accept-Language': 'ru',
        'X-Yandex-Login': 'test',
        'X-Yandex-UID': '123',
        'X-YaTaxi-Driver-Profile-Id': '1',
        'X-YaTaxi-Park-Id': '1',
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': '9.55',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'Content-Type': 'application/json',
        'X-Ya-Service-Ticket': '3:serv:test',
        'X-Real-Ip': '127.0.0.1',
        'X-Remote-Ip': '127.0.0.1',
    }

    @classmethod
    def get_internal_headers(cls):
        return cls._internal_headers


class BaseService:
    def __init__(self):
        self.host = None

    def set_host(self, host: str):
        self.host = host


class CargoOrdersService(BaseService):
    def __init__(self):
        super().__init__()
        self.host = 'http://cargo-orders.taxi.yandex.net'

    def ping(self) -> requests.Response:
        return requests.get(
            url=f'{self.host}/ping', headers=Headers.get_internal_headers(),
        )


class CargoDispatchService(BaseService):
    def __init__(self):
        super().__init__()
        self.host = 'http://cargo-dispatch.taxi.yandex.net'

    def ping(self) -> requests.Response:
        return requests.get(
            url=f'{self.host}/ping', headers=Headers.get_internal_headers(),
        )


class CargoClaimsService(BaseService):
    def __init__(self):
        super().__init__()
        self.host = 'http://cargo-claims.taxi.yandex.net'

    def ping(self) -> requests.Response:
        return requests.get(
            url=f'{self.host}/ping', headers=Headers.get_internal_headers(),
        )

    def create_claim(self, json: typing.Dict) -> requests.Response:
        return requests.post(
            url=f'{self.host}/{CARGO_API_PREFIX}/v2/claims/create',
            params={'request_id': uuid.uuid4().hex},
            headers=Headers.get_internal_headers(),
            json=json,
        )

    def accept_claim(self, claim_id: str) -> requests.Response:
        return requests.post(
            url=f'{self.host}/{CARGO_API_PREFIX}/v1/claims/accept',
            params={'claim_id': claim_id},
            headers=Headers.get_internal_headers(),
            json={'version': 1, 'corp_client_id': DEFAULT_CORP_CLIENT_ID},
        )

    def get_claim_status(self, claim_id: str) -> requests.Response:
        return requests.get(
            url=f'{self.host}/{CARGO_API_PREFIX}v1/claims/cut',
            headers=Headers.get_internal_headers(),
            params={'claim_id': claim_id},
        )

    def wait_for_claim_status(
            self, claim_id: str, statuses: typing.Iterable, wait=10,
    ) -> requests.Response:
        timer = datetime.datetime.now() + datetime.timedelta(seconds=wait)
        while True:
            try:
                claim_status = self.get_claim_status(claim_id)
            except HttpNotFoundError:
                continue
            if claim_status in statuses or datetime.datetime.now() > timer:
                return claim_status
            time.sleep(1)
            continue


@pytest.fixture
def cargo_orders():
    return CargoOrdersService()


@pytest.fixture
def cargo_dispatch():
    return CargoDispatchService()


@pytest.fixture
def cargo_claims():
    return CargoClaimsService()
