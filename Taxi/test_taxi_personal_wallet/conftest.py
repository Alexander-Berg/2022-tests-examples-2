import http
import json
import typing

from aiohttp import test_utils
import pytest

# pylint: disable=unused-wildcard-import,wildcard-import,line-too-long
# pylint: disable=line-too-long,redefined-outer-name
import taxi_personal_wallet.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['taxi_personal_wallet.generated.service.pytest_plugins']


TEST_APPLICATION = 'android'
REQUEST_APPLICATION_HEADER = (
    'app_name={app_name},app_brand=yataxi,app_ver1=1,app_ver2=2,app_ver3=3'
)


# https://docs.pytest.org/en/latest/example/parametrize.html
# a-quick-port-of-testscenarios
def pytest_generate_tests(metafunc):
    parametrize_scenario(metafunc)


def _update_dict(source: dict, **kwargs):
    for key, val in kwargs.items():
        if val is not None:
            source[key] = val
        else:
            source.pop(key, None)


class WalletClient:
    http_client: test_utils.TestClient

    def __init__(self, http_client: test_utils.TestClient) -> None:
        self.http_client = http_client

    @staticmethod
    def _get_ok_hdr():
        return {
            'Content-Type': 'application/json',
            'YaTaxi-Api-Key': 'passwallet_apikey',
        }

    async def request(
            self, url: str, req: dict, headers: typing.Optional[dict] = None,
    ):
        headers = headers or {}
        headers.update(WalletClient._get_ok_hdr())
        return await self.http_client.post(
            url, data=json.dumps(req), headers=headers,
        )

    async def available_accounts(
            self,
            service=None,
            headers=None,
            app_name: str = None,
            yandex_uid: str = '123',
            user_id: typing.Optional[str] = 'user_id',
            phone_id: typing.Optional[str] = 'phone_id',
            personal_phone_id: typing.Optional[str] = 'personal_phone_id',
            pass_flags: typing.Optional[
                str
            ] = 'portal,ya-plus,credentials=token-bearer',
    ):
        if app_name is None:
            app_name = TEST_APPLICATION
        application = REQUEST_APPLICATION_HEADER.format(app_name=app_name)
        x_ya_taxi_user = ''
        if personal_phone_id is not None:
            x_ya_taxi_user = f'personal_phone_id={personal_phone_id}'
        request_headers = {
            'X-Yandex-UID': yandex_uid,
            'X-YaTaxi-User': x_ya_taxi_user,
            'X-Request-Application': application,
            'Accept-Language': 'ru-RU',
        }

        if user_id is not None:
            request_headers['X-YaTaxi-UserId'] = user_id

        if phone_id is not None:
            request_headers['X-YaTaxi-PhoneId'] = phone_id

        if pass_flags is not None:
            request_headers['X-YaTaxi-Pass-Flags'] = pass_flags

        request_params = {}
        if service is not None:
            request_params['service'] = service

        if headers:
            _update_dict(request_headers, **headers)
        response = await self.http_client.get(
            '/v1/available-accounts',
            headers=request_headers,
            params=request_params,
        )
        assert response.status == http.HTTPStatus.OK
        response_data = await response.json()
        return response_data['available_accounts']

    async def get(self, *args, **kwargs):
        return await self.http_client.get(*args, **kwargs)

    async def post(self, *args, **kwargs):
        return await self.http_client.post(*args, **kwargs)


@pytest.fixture
def test_wallet_client(web_app_client) -> WalletClient:
    return WalletClient(web_app_client)


def parametrize_scenario(metafunc):
    if 'scenario' not in metafunc.fixturenames:
        return

    class Scenario:
        pass

    idlist = []
    argvalues = []
    for scenario in metafunc.cls.scenarios:
        idlist.append(scenario[0])
        items = scenario[1].items()
        scenario_object = Scenario()
        for item in items:
            setattr(scenario_object, item[0], item[1])
        argvalues.append(scenario_object)
    metafunc.parametrize('scenario', argvalues, ids=idlist, scope='function')


def ensure_desired_sensors(push_mock, desired_sensors):
    actual_sensors = []
    missing_sensors = []
    for call in push_mock.calls:
        push_data = call['data'].asdict()
        assert push_data['commonLabels']['application'] == 'personal_wallet'

        # There is only one common label at the moment. If you have added one,
        # increase expected value
        assert len(push_data['commonLabels']) == 1

        assert 'ts' in push_data

        actual_sensors.extend(push_data['sensors'])
    # we cannot guarantee order, we could sort but it is dangerous, so pop
    # every sensor that exists in actual call, at the end actual sensors should
    # be empty
    for sensor in desired_sensors:
        try:
            actual_sensors.remove(sensor)
        except ValueError:
            missing_sensors.append(sensor)
            continue
    assert not missing_sensors, 'some sensors are missing from actual_sensors'
    # there should be no sensors left
    assert not actual_sensors, 'actual_sensors contain excessive sensors'
