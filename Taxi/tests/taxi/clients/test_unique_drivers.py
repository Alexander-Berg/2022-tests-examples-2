# pylint: disable=protected-access, redefined-outer-name
import pytest

from taxi import discovery
from taxi.clients import tvm
from taxi.clients import unique_drivers


@pytest.fixture
async def test_app(test_taxi_app):
    config_ = test_taxi_app.config
    service = discovery.find_service('unique-drivers')
    test_taxi_app.unique_drivers_client = (
        unique_drivers.UniqueDriversApiClient(
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
    'actual_request,actual_response,expected_response',
    [
        (
            ['1', '2', '2'],
            {
                'profiles': [
                    {
                        'data': [
                            {
                                'driver_profile_id': 'dp1',
                                'park_driver_profile_id': 'pp1',
                                'park_id': '1',
                            },
                        ],
                        'unique_driver_id': '1',
                    },
                    {
                        'data': [
                            {
                                'driver_profile_id': 'dp2',
                                'park_driver_profile_id': 'pp2',
                                'park_id': '2',
                            },
                        ],
                        'unique_driver_id': '1',
                    },
                    {
                        'data': [
                            {
                                'driver_profile_id': 'dp1',
                                'park_driver_profile_id': 'pp1',
                                'park_id': '1',
                            },
                        ],
                        'unique_driver_id': '2',
                    },
                    {
                        'data': [
                            {
                                'driver_profile_id': 'dp1',
                                'park_driver_profile_id': 'pp1',
                                'park_id': '1',
                            },
                        ],
                        'unique_driver_id': '3',
                    },
                ],
            },
            {
                '1': [
                    {
                        'driver_profile_id': 'dp1',
                        'park_driver_profile_id': 'pp1',
                        'park_id': '1',
                    },
                    {
                        'driver_profile_id': 'dp2',
                        'park_driver_profile_id': 'pp2',
                        'park_id': '2',
                    },
                ],
                '2': [
                    {
                        'driver_profile_id': 'dp1',
                        'park_driver_profile_id': 'pp1',
                        'park_id': '1',
                    },
                ],
                '3': [
                    {
                        'driver_profile_id': 'dp1',
                        'park_driver_profile_id': 'pp1',
                        'park_id': '1',
                    },
                ],
            },
        ),
    ],
)
async def test_get_driver_profile_ids_from_data(
        test_app,
        patch,
        response_mock,
        actual_request,
        actual_response,
        expected_response,
):
    @patch('aiohttp.ClientSession._request')
    async def _request(*args, **kwargs):
        return response_mock(json=actual_response)

    actual_response = (
        await test_app.unique_drivers_client.get_driver_profile_ids_from_data(
            actual_request,
        )
    )
    assert actual_response == expected_response
