from testsuite.utils import http

from fleet_rent.entities import driver
from fleet_rent.generated.web import web_context as context_module


async def test_driver_info_service(
        web_context: context_module.Context, mock_driver_profiles,
):
    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _retrieve(request: http.Request):
        assert request.json == {'id_in_set': ['driver_park_id_driver_id']}
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'driver_park_id_driver_id',
                    'data': {
                        'uuid': 'driver_id',
                        'park_id': 'driver_park_id',
                        'full_name': {
                            'first_name': 'Водитель',
                            'last_name': 'Водителев',
                            'middle_name': 'Водителевич',
                        },
                    },
                },
            ],
        }

    driver_data = await web_context.external_access.driver.get_driver_info(
        park_id='driver_park_id', driver_id='driver_id',
    )

    assert driver_data == driver.Driver(
        id='driver_id',
        park_id='driver_park_id',
        full_name=driver.Driver.FullName(
            first_name='Водитель',
            last_name='Водителев',
            middle_name='Водителевич',
        ),
    )


async def test_is_driver_exists(
        web_context: context_module.Context, mock_driver_profiles,
):
    condition = True

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _retrieve(request: http.Request):
        assert request.json == {
            'id_in_set': ['park_id_driver_id'],
            'projection': ['data.uuid'],
        }
        response: dict = {
            'profiles': [{'park_driver_profile_id': 'park_id_driver_id'}],
        }
        if condition:
            response['profiles'][0]['data'] = {'uuid': 'driver_id'}
        return response

    driver_access = web_context.external_access.driver

    condition = True
    assert await driver_access.is_driver_exists('park_id', 'driver_id')

    condition = False
    assert not await driver_access.is_driver_exists('park_id', 'driver_id')


async def test_driver_app_service(
        web_context: context_module.Context, mock_driver_profiles,
):
    @mock_driver_profiles('/v1/driver/app/profiles/retrieve')
    async def _retrieve(request: http.Request):
        assert request.json == {'id_in_set': ['driver_park_id_driver_id']}
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'driver_park_id_driver_id',
                    'data': {'locale': 'en'},
                },
            ],
        }

    driver_data = await web_context.external_access.driver.get_app(
        park_id='driver_park_id', driver_id='driver_id',
    )
    assert driver_data == driver.DriverApp(
        id='driver_id', park_id='driver_park_id', locale='en',
    )

    locales = await web_context.external_access.driver.get_locales(
        park_id='driver_park_id', driver_id='driver_id',
    )
    assert locales == ['en', 'ru']


async def test_driver_app_not_found(
        web_context: context_module.Context, mock_driver_profiles,
):
    @mock_driver_profiles('/v1/driver/app/profiles/retrieve')
    async def _retrieve(request: http.Request):
        assert request.json == {'id_in_set': ['driver_park_id_driver_id']}
        return {
            'profiles': [
                {'park_driver_profile_id': 'driver_park_id_driver_id'},
            ],
        }

    driver_data = await web_context.external_access.driver.get_app(
        park_id='driver_park_id', driver_id='driver_id',
    )
    assert driver_data == driver.DriverApp(
        id='driver_id', park_id='driver_park_id', locale=None,
    )

    locales = await web_context.external_access.driver.get_locales(
        park_id='driver_park_id', driver_id='driver_id',
    )
    assert locales == ['ru']
