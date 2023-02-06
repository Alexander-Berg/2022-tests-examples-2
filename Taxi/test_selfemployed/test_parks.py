# pylint: disable=redefined-outer-name,unused-variable
# TODO: move to tests/taxi/clients/
import pytest

import taxi.clients.parks as parks
from taxi.util import client_session


@pytest.fixture
async def client():
    class TvmMock:
        @staticmethod
        async def get_auth_headers(*args, **kwargs):
            return {}

    session = client_session.get_client_session()

    yield parks.ParksClient(
        session=session, base_url='http://test-parks-url', tvm_client=TvmMock,
    )

    await session.close()


@pytest.mark.parametrize(
    'parks_data,expected_phone',
    [
        ({}, []),
        ({'driver_profiles': []}, []),
        ({'driver_profiles': [{'driver_profile': {}}], 'parks': []}, []),
        (
            {
                'driver_profiles': [{'driver_profile': {'phones': []}}],
                parks: [],
            },
            [],
        ),
        (
            {
                'driver_profiles': [
                    {'driver_profile': {'phones': ['+7000', '+7111']}},
                ],
                'parks': [],
            },
            ['+7000', '+7111'],
        ),
    ],
)
async def test_parks(
        client,
        patch_aiohttp_session,
        response_mock,
        parks_data,
        expected_phone,
):
    @patch_aiohttp_session('http://test-parks-url', 'POST')
    def patch_request(method, url, **kwargs):
        assert kwargs['json'] == {
            'query': {'park': {'id': 'p', 'driver_profile': {'id': ['d']}}},
            'fields': {'driver_profile': ['phones']},
        }
        return response_mock(json=parks_data)

    phone = await client.get_driver_phone(driver_id='d', park_id='p')
    assert phone == expected_phone


async def test_parks_driver_info(client, patch_aiohttp_session, response_mock):
    driver_info = {
        'first_name': 'Алексей',
        'last_name': 'Антипов',
        'middle_name': 'Викторович',
        'license': {
            'birth_date': None,
            'country': 'rus',
            'expiration_date': '2027-01-01T00:00:00+0000',
            'issue_date': '2017-01-01T00:00:00+0000',
            'number': '',
            'normalized_number': '',
        },
        'license_number': '%^&*()',
        'license_series': '--!!$#@',
        'car_id': 'car',
    }

    driver_id = 'd'
    park_id = 'p'

    @patch_aiohttp_session('http://test-parks-url', 'POST')
    def patch_request(method, url, **kwargs):
        assert kwargs['json']['query'] == {
            'park': {'id': park_id, 'driver_profile': {'id': [driver_id]}},
        }
        assert set(kwargs['json']['fields']['driver_profile']) == {
            'first_name',
            'last_name',
            'middle_name',
            'license',
            'license_number',
            'license_series',
            'car_id',
            'license_experience',
            'medical_card',
            'delivery',
            'courier_type',
            'orders_provider',
        }
        assert kwargs['json']['fields']['park'] == ['city']
        return response_mock(
            json={
                'driver_profiles': [{'driver_profile': driver_info}],
                'parks': [{'city': 'Омск'}],
            },
        )

    data = await client.get_driver_info(
        driver_id='d',
        park_id='p',
        extra_fields=[
            'license_experience',
            'medical_card',
            'delivery',
            'courier_type',
            'orders_provider',
        ],
    )
    assert data == {**driver_info, 'park_city': 'Омск'}


async def test_parks_car_info(client, patch_aiohttp_session, response_mock):
    car_info = {
        'brand': 'Pagani',
        'color': 'Желтый',
        'id': 'c34137d6e51843f28f827990fb021770',
        'model': 'Huayra',
        'number': 'СОМЕОНЕ',
        'year': 2019,
    }
    car_id = 'car'
    park_id = 'park'

    @patch_aiohttp_session('http://test-parks-url', 'POST')
    def patch_request(method, url, **kwargs):
        assert kwargs['json'] == {
            'query': {'park': {'id': park_id, 'car': {'id': [car_id]}}},
            'fields': {'car': ['brand', 'color', 'model', 'number', 'year']},
        }
        return response_mock(json={'cars': [car_info]})

    data = await client.get_basic_car_info(park_id=park_id, car_id=car_id)
    assert data == car_info
