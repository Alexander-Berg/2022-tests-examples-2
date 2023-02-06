import typing as tp

import pytest

from testsuite.utils import http

# pylint: disable=redefined-outer-name
import pro_profiles_removal.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['pro_profiles_removal.generated.service.pytest_plugins']


TEST_NOW = '2022-01-01T12:00:00+0000'
TEST_PARK_ID = '7ad36bc7560449998acbe2c57a75c293'
TEST_DRIVER_ID_1 = '110982b584844dfcab07f29adf9661ab'
TEST_DRIVER_ID_2 = '120982b584844dfcab07f29adf9661ab'
TEST_DRIVER_ID_3 = '130982b584844dfcab07f29adf9661ab'
TEST_DRIVER_ID_4 = '140982b584844dfcab07f29adf9661ab'
TEST_DRIVER_ID_5 = '150982b584844dfcab07f29adf9661ab'
TEST_DRIVER_ID_6 = '160982b584844dfcab07f29adf9661ab'

TEST_HEADERS = {
    'X-Request-Application-Version': '10.21',
    'X-Request-Platform': 'android',
    'X-Request-Language': 'ru',
    'X-YaTaxi-Park-Id': TEST_PARK_ID,
    'X-Ya-Service-Ticket': 'tvm',
}


@pytest.fixture
async def fleet_parks(mock_fleet_parks):
    @mock_fleet_parks('/v1/parks/list')
    def _v1_parks_list(request: http.Request):
        return {
            'parks': [
                {
                    'id': 'parkid',
                    'login': 'login',
                    'name': 'Тестовый Парк',
                    'is_active': True,
                    'city_id': 'Москва',
                    'locale': 'locale',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'country_id': 'rus',
                    'demo_mode': False,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }


@pytest.fixture
def driver_ui_profile(mock_driver_ui_profile):
    @mock_driver_ui_profile('/v1/mode')
    def _v1_mode(request):
        return {
            'display_mode': 'display_mode',
            'display_profile': 'display_profile',
        }


@pytest.fixture
async def driver_profiles(mock_driver_profiles, load_json):
    class Context:
        def __init__(self, load_json) -> None:
            self.profiles = load_json('profiles.json')
            self.phones = load_json('profiles_by_phone.json')
            self.mock_profiles_retrieve: tp.Any = {}
            self.mock_profiles_retrieve_by_phone: tp.Any = {}

        def add_profile(self, park_id, driver_profile_id, phone_pd_id):
            key = f'{park_id}_{driver_profile_id}'
            profile_data = {
                'park_driver_profile_id': key,
                'data': {'phone_pd_ids': [{'pd_id': phone_pd_id}]},
            }
            phone_profile_data = {
                'park_driver_profile_id': key,
                'data': {'park_id': park_id, 'uuid': driver_profile_id},
            }
            if key in self.profiles:
                raise ValueError('profile already exists')

            self.profiles[key] = profile_data

            if phone_pd_id in self.phones:
                self.phones[phone_pd_id]['profiles'].append(phone_profile_data)
            else:
                self.phones[phone_pd_id] = {
                    'driver_phone': phone_pd_id,
                    'profiles': [phone_profile_data],
                }

    context = Context(load_json)

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    def _retrieve_by_id(request: http.Request):
        ids = request.json['id_in_set']
        result = [context.profiles[id] for id in ids if id in context.profiles]
        return {'profiles': result}

    @mock_driver_profiles('/v1/driver/profiles/retrieve_by_phone')
    def _retrieve_by_phone(request: http.Request):
        ids = request.json['driver_phone_in_set']
        result = [context.phones[id] for id in ids if id in context.phones]
        return {'profiles_by_phone': result}

    context.mock_profiles_retrieve = _retrieve_by_id
    context.mock_profiles_retrieve_by_phone = _retrieve_by_phone
    return context
