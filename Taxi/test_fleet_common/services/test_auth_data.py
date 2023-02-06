import aiohttp.web

from fleet_common.services import auth_data

PARK_ID = '7ad36bc7560449998acbe2c57a75c293'

PARK = {
    'parks': [
        {
            'id': PARK_ID,
            'name': 'park_name',
            'login': 'park_login',
            'is_active': True,
            'city_id': 'Москва',
            'tz_offset': 3,
            'locale': 'ru',
            'is_billing_enabled': True,
            'is_franchising_enabled': True,
            'country_id': 'rus',
            'demo_mode': False,
            'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
        },
    ],
}

USER_ID = '111'
USER_PASSPORT_UID = '123'

USER = {
    'limit': 1,
    'offset': 0,
    'users': [
        {
            'created_at': '2018-01-01T00:00+00:00',
            'id': USER_ID,
            'is_confirmed': True,
            'is_enabled': True,
            'is_superuser': True,
            'is_usage_consent_accepted': True,
            'park_id': '7ad36bc7560449998acbe2c57a75c293',
            'passport_uid': USER_PASSPORT_UID,
            'email': 'tarasalk@yandex.ru',
            'group_name': 'Администратор',
        },
    ],
}


async def test_get_fleet_park(library_context, mock_fleet_parks):
    @mock_fleet_parks('/v1/parks/list')
    async def _parks(request):
        return aiohttp.web.json_response(PARK)

    park = await auth_data.get_fleet_park(
        context=library_context, park_id=PARK_ID,
    )

    assert park.id == PARK_ID


async def test_get_dac_user(library_context, mock_dispatcher_access_control):
    @mock_dispatcher_access_control('/v1/parks/users/list')
    async def _users(request):
        return aiohttp.web.json_response(USER)

    user = await auth_data.get_dac_user(
        context=library_context,
        park_id=PARK_ID,
        passport_uid=USER_PASSPORT_UID,
    )

    assert user.id == USER_ID


async def test_get_park_and_user(
        library_context, mock_fleet_parks, mock_dispatcher_access_control,
):
    @mock_fleet_parks('/v1/parks/list')
    async def _parks(request):
        return aiohttp.web.json_response(PARK)

    @mock_dispatcher_access_control('/v1/parks/users/list')
    async def _users(request):
        return aiohttp.web.json_response(USER)

    park, user = await auth_data.get_park_and_user(
        context=library_context,
        park_id=PARK_ID,
        passport_uid=USER_PASSPORT_UID,
    )

    assert park.id == PARK_ID
    assert user.id == USER_ID
