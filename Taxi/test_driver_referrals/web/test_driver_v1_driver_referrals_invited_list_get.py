import pytest

from test_driver_referrals import conftest

PARKS_DRIVER = {
    'd2': {
        'first_name': 'Аа',
        'id': 'd2',
        'last_name': 'А',
        'phones': ['+70007198936'],
    },
    'd3': {
        'first_name': 'Ба',
        'id': 'd3',
        'last_name': 'Б',
        'phones': ['+70007198936'],
    },
    'd5': {
        'first_name': 'Га',
        'id': 'd5',
        'last_name': 'Г',
        'phones': ['+70007198936'],
    },
    'd4': {
        'first_name': 'Ва',
        'id': 'd4',
        'last_name': 'В',
        'phones': ['+70007198936'],
    },
    'd6': {
        'first_name': 'Да',
        'id': 'd6',
        'last_name': 'Д',
        'phones': ['+70007198936'],
    },
    'd7': {
        'first_name': 'Ее',
        'id': 'd7',
        'last_name': 'Е',
        'phones': ['+70007198936'],
    },
    'd8': {
        'first_name': 'Жж',
        'id': 'd8',
        'last_name': 'Ж',
        'phones': ['+70007198936'],
    },
    'd9': {
        'first_name': 'Зз',
        'id': 'd9',
        'last_name': 'З',
        'phones': ['+70007198936'],
    },
}


@pytest.mark.translations(
    taximeter_backend_driver_referrals=conftest.TRANSLATIONS,
)
@pytest.mark.translations(geoareas=conftest.TRANSLATIONS_GEOAREAS)
@pytest.mark.translations(tariff=conftest.TRANSLATIONS_TARIFF)
@pytest.mark.translations(notify=conftest.TRANSLATIONS_NOTIFY)
@pytest.mark.config(
    DRIVER_REFERRAL_WORDS_FOR_CODES_BY_COUNTRY={'__default__': ['ПРОМОКОД']},
    DRIVER_REFERRALS_PROXY_URLS_COUNTRY={
        '__default__': {'taxi': 'test/?{code}', 'eda': 'test/?{code}'},
    },
)
@pytest.mark.config(DRIVER_REFERRALS_USE_PERSONAL_DATA_COUNTRIES=['rus'])
@pytest.mark.pgsql('driver_referrals', files=['driver_with_invites.sql'])
@pytest.mark.now('2019-04-25 15:00:00')
async def test_driver_v1_driver_referrals_invited_list_get(
        web_app_client,
        mockserver,
        load_json,
        mock_get_query_positions_default,
        mock_fail_to_get_nearest_zone,
        mock_parks_driver_profiles_search,
):
    mock_parks_driver_profiles_search(PARKS_DRIVER)

    @mockserver.json_handler(
        '/udriver-photos/driver-photos/v1/last-not-rejected-photo',
    )
    async def _driver_photos(request):
        return mockserver.make_response(
            status=200,
            json={
                'actual_photo': {
                    'avatar_url': (
                        f'http://{request.query["driver_profile_id"]}'
                    ),
                    'portrait_url': (
                        f'http://{request.query["driver_profile_id"]}'
                    ),
                },
            },
        )

    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    async def _tariffs(request):
        return mockserver.make_response(
            json={
                'zones': [
                    {'name': 'moscow', 'time_zone': 'Moscow', 'country': 'ru'},
                ],
            },
        )

    response = await web_app_client.get(
        '/driver/v1/driver-referrals/invited/list',
        params={'status': 'all', 'limit': 10, 'offset': 0},
        headers={
            **conftest.COMMON_DRIVER_HEADERS,
            'X-YaTaxi-Park-Id': 'p1',
            'X-YaTaxi-Driver-Profile-Id': 'd1',
        },
    )
    assert response.status == 200

    content = await response.json()
    assert content == load_json('expected_invited_list.json')


@pytest.mark.translations(
    taximeter_backend_driver_referrals=conftest.TRANSLATIONS,
)
@pytest.mark.translations(geoareas=conftest.TRANSLATIONS_GEOAREAS)
@pytest.mark.translations(tariff=conftest.TRANSLATIONS_TARIFF)
@pytest.mark.translations(notify=conftest.TRANSLATIONS_NOTIFY)
@pytest.mark.config(
    DRIVER_REFERRAL_WORDS_FOR_CODES_BY_COUNTRY={'__default__': ['ПРОМОКОД']},
    DRIVER_REFERRALS_PROXY_URLS_COUNTRY={
        '__default__': {'taxi': 'test/?{code}', 'eda': 'test/?{code}'},
    },
)
@pytest.mark.config(DRIVER_REFERRALS_USE_PERSONAL_DATA_COUNTRIES=[])
@pytest.mark.pgsql('driver_referrals', files=['driver_with_invites.sql'])
@pytest.mark.now('2019-04-25 15:00:00')
async def test_driver_v1_driver_referrals_invited_list_get_no_pd(
        web_app_client,
        mockserver,
        load_json,
        mock_get_query_positions_default,
        mock_fail_to_get_nearest_zone,
        mock_parks_driver_profiles_search,
):
    mock_parks_driver_profiles_search(PARKS_DRIVER)

    @mockserver.json_handler(
        '/udriver-photos/driver-photos/v1/last-not-rejected-photo',
    )
    async def _driver_photos(request):
        return mockserver.make_response(
            status=200,
            json={
                'actual_photo': {
                    'avatar_url': (
                        f'http://{request.query["driver_profile_id"]}'
                    ),
                    'portrait_url': (
                        f'http://{request.query["driver_profile_id"]}'
                    ),
                },
            },
        )

    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    async def _tariffs(request):
        return mockserver.make_response(
            json={
                'zones': [
                    {'name': 'moscow', 'time_zone': 'Moscow', 'country': 'ru'},
                ],
            },
        )

    response = await web_app_client.get(
        '/driver/v1/driver-referrals/invited/list',
        params={'status': 'all', 'limit': 10, 'offset': 0},
        headers={
            **conftest.COMMON_DRIVER_HEADERS,
            'X-YaTaxi-Park-Id': 'p1',
            'X-YaTaxi-Driver-Profile-Id': 'd1',
        },
    )
    assert response.status == 200

    content = await response.json()
    assert content == load_json('expected_invited_list_not_pd.json')


@pytest.mark.translations(
    taximeter_backend_driver_referrals=conftest.TRANSLATIONS,
)
@pytest.mark.translations(geoareas=conftest.TRANSLATIONS_GEOAREAS)
@pytest.mark.translations(tariff=conftest.TRANSLATIONS_TARIFF)
@pytest.mark.translations(notify=conftest.TRANSLATIONS_NOTIFY)
@pytest.mark.config(
    DRIVER_REFERRAL_WORDS_FOR_CODES_BY_COUNTRY={'__default__': ['ПРОМОКОД']},
    DRIVER_REFERRALS_PROXY_URLS_COUNTRY={
        '__default__': {'taxi': 'test/?{code}', 'eda': 'test/?{code}'},
    },
)
@pytest.mark.config(DRIVER_REFERRALS_USE_PERSONAL_DATA_COUNTRIES=['rus'])
@pytest.mark.now('2019-04-25 15:00:00')
@pytest.mark.pgsql('driver_referrals', files=['pg_driver_referrals.sql'])
@pytest.mark.parametrize(
    'expected_response',
    (
        pytest.param(
            'expected_response_1.json',
            id='overshadowing + 3 rules',
            marks=[
                pytest.mark.pgsql(
                    'driver_referrals', files=['pg_driver_referrals_1.sql'],
                ),
            ],
        ),
        pytest.param(
            'expected_response_2.json',
            id='splitting of tariffs',
            marks=[
                pytest.mark.pgsql(
                    'driver_referrals', files=['pg_driver_referrals_2.sql'],
                ),
            ],
        ),
        pytest.param(
            'expected_response_3.json',
            id='same rewards for parks, different for selfemployed',
            marks=[
                pytest.mark.pgsql(
                    'driver_referrals', files=['pg_driver_referrals_3.sql'],
                ),
            ],
        ),
        pytest.param(
            'expected_response_4.json',
            id='expired',
            marks=[
                pytest.mark.pgsql(
                    'driver_referrals', files=['pg_driver_referrals_4.sql'],
                ),
            ],
        ),
        pytest.param(
            'expected_response_5.json',
            id='all tariffs, except ...',
            marks=[
                pytest.mark.pgsql(
                    'driver_referrals', files=['pg_driver_referrals_5.sql'],
                ),
            ],
        ),
        pytest.param(
            'expected_response_6.json',
            id='all tariffs',
            marks=[
                pytest.mark.pgsql(
                    'driver_referrals', files=['pg_driver_referrals_6.sql'],
                ),
            ],
        ),
    ),
)
async def test_driver_no_invites(
        web_app_client,
        mockserver,
        load_json,
        expected_response,
        mock_get_query_positions_default,
        mock_fail_to_get_nearest_zone,
):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    async def _tariffs(request):
        return mockserver.make_response(
            json={
                'zones': [
                    {'name': 'moscow', 'time_zone': 'Moscow', 'country': 'ru'},
                ],
            },
        )

    response = await web_app_client.get(
        '/driver/v1/driver-referrals/invited/list',
        headers={
            **conftest.COMMON_DRIVER_HEADERS,
            'X-YaTaxi-Park-Id': 'p',
            'X-YaTaxi-Driver-Profile-Id': 'd',
        },
        params={'type': 'all', 'limit': 10, 'offset': 0},
    )
    assert response.status == 200

    content = await response.json()
    assert content == load_json(expected_response)
