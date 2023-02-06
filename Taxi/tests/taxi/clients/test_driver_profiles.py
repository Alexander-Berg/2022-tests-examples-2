# pylint: disable=protected-access, redefined-outer-name
import json

import pytest

from taxi import discovery
from taxi.clients import driver_profiles
from taxi.clients import tvm


@pytest.fixture
async def test_app(test_taxi_app):
    config_ = test_taxi_app.config
    service = discovery.find_service('driver-profiles')
    test_taxi_app.driver_profiles_client = (
        driver_profiles.DriverProfilesApiClient(
            session=test_taxi_app.session,
            service=service,
            tvm_client=tvm.TVMClient(
                service_name='test-service',
                secdist=test_taxi_app.secdist,
                config=config_,
                session=test_taxi_app.session,
            ),
            consumer='test',
        )
    )
    return test_taxi_app


@pytest.mark.parametrize(
    'driver_id,expected_response',
    [(1, [{'data': {'license': {'pd_id': 1}}}])],
)
async def test_driver_profile_retrieve(
        test_app, patch, response_mock, driver_id, expected_response,
):
    @patch('aiohttp.ClientSession._request')
    async def _request(*args, **kwargs):
        return response_mock(text=json.dumps(expected_response))

    result = await test_app.driver_profiles_client.retrieve(
        ids=[driver_id], projection=['data.license'],
    )
    assert result == expected_response


@pytest.mark.parametrize(
    'park_id,driver_profile_id,thermobag,thermopack,profi_courier',
    [
        ('1', '1', False, None, None),
        ('1', '1', None, True, None),
        ('1', '1', True, False, False),
        ('1', '1', None, None, True),
    ],
)
async def test_driver_profiles_delivery(
        test_app,
        patch,
        response_mock,
        park_id,
        driver_profile_id,
        thermobag,
        thermopack,
        profi_courier,
):
    @patch('aiohttp.ClientSession._request')
    async def _request(*args, **kwargs):
        assert kwargs['params'] == {
            'park_id': park_id,
            'driver_profile_id': driver_profile_id,
        }
        delivery = {}
        if thermobag is not None:
            delivery.update(thermobag=thermobag)
        if thermopack is not None:
            delivery.update(thermopack=thermopack)
        if profi_courier is not None:
            delivery.update(profi_courier=profi_courier)
        assert kwargs['json'] == {
            'delivery': delivery,
            'author': {
                'consumer': 'test',
                'identity': {
                    'driver_profile_id': driver_profile_id,
                    'type': 'driver',
                },
            },
        }
        return response_mock(text=json.dumps({}))

    await test_app.driver_profiles_client.delivery(
        park_id,
        driver_profile_id,
        thermobag,
        thermopack,
        profi_courier=profi_courier,
    )


@pytest.mark.parametrize(
    'park_id,driver_profile_id,is_enabled',
    [('1', '1', None), ('1', '1', True)],
)
async def test_driver_profiles_medical_card(
        test_app, patch, response_mock, park_id, driver_profile_id, is_enabled,
):
    @patch('aiohttp.ClientSession._request')
    async def _request(*args, **kwargs):
        assert kwargs['params'] == {
            'park_id': park_id,
            'driver_profile_id': driver_profile_id,
        }
        medical_card = {}
        if is_enabled is not None:
            medical_card.update(is_enabled=is_enabled)
        assert kwargs['json'] == {
            'medical_card': medical_card,
            'author': {
                'consumer': 'test',
                'identity': {
                    'driver_profile_id': driver_profile_id,
                    'type': 'driver',
                },
            },
        }
        return response_mock(text=json.dumps({}))

    await test_app.driver_profiles_client.medical_card(
        park_id, driver_profile_id, is_enabled,
    )
