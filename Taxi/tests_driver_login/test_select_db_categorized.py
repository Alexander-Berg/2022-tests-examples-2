import pytest


HEADERS = {
    'X-Remote-IP': '1.1.1.1',
    'Accept-Language': 'ru_RU',
    'User-Agent': 'Taximeter 9.25 (2222)',
}

TRANSLATIONS = {
    'Login_ParkList_ScreenTitle': {'ru': 'Вид деятельности'},
    'Login_Driver_Partner_Park_Name': {'ru': 'Самозанятый'},
    'Login_ParkList_Groups_TaxiDelivery_Title': {'ru': 'Такси и Доставка'},
    'Login_ParkList_Groups_TaxiDelivery_Subtitle': {
        'ru': 'Выберите парк или партнера',
    },
    'Login_ParkList_Groups_EatsLavka_Title': {'ru': 'Еда и Лавка'},
    'Login_ParkList_Categories_Taxi_Title': {'ru': 'Такси'},
    'Login_ParkList_Categories_Delivery_Title': {'ru': 'Доставка'},
    'Login_ParkList_Categories_EatsCourier_Title': {
        'ru': 'Стать курьером Еды',
    },
}

PHONE = '+79991112233'

DATA = {'phone': PHONE, 'step': 'sms_code', 'sms_code': '0000'}

USER_AGENT_UBER = 'Taximeter-Uber 9.22'
USER_AGENT_TAXIMETER = 'Taximeter 9.25 (2222)'
USER_AGENT_TURLA = 'Taximeter-TURLA 10.09 (1074153406)'
USER_AGENT_RIDA = 'Taximeter-rida 10.09 (1074153406)'


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.config(
    DRIVER_LOGIN_CLEAN_MAPPED_PARKS=True,
    EATS_COURIER_SERVICE_MAPPING={
        'service1': {'id2': 'dbid2'},
        'selfemployed': 'dbid3',
        'selfemployed_by_country': {'RU': 'dbid3'},
    },
    TAXIMETER_BRAND_TO_APP_FAMILY_MAPPING={
        'az': 'taximeter',
        'rida': 'rida',
        'turla': 'modus',
        'uber': 'uberdriver',
        'vezet': 'vezet',
        'yandex': 'taximeter',
        'yango': 'taximeter',
    },
)
@pytest.mark.parametrize(
    ('user_agent', 'parks_response', 'expected_response_json'),
    [
        pytest.param(
            USER_AGENT_TAXIMETER,
            'parks_response.json',
            'expected_response_happy_path.json',
            id='happy_path',
            marks=[pytest.mark.experiments3(filename='exp3_enabled.json')],
        ),
        pytest.param(
            USER_AGENT_TAXIMETER,
            'parks_response.json',
            'expected_response_happy_only_eda_parks.json',
            id='only eda parks',
            marks=[
                pytest.mark.experiments3(filename='exp3_enabled.json'),
                pytest.mark.config(
                    EATS_COURIER_SERVICE_MAPPING={
                        'service1': {
                            'id1': 'dbid1',
                            'id2': 'dbid2',
                            'id3': 'dbid3',
                            'id4': 'dbid4',
                            'id5': 'dbid5',
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            USER_AGENT_TAXIMETER,
            'parks_response.json',
            'expected_response_happy_only_taxi_parks.json',
            id='only taxi parks',
            marks=[
                pytest.mark.experiments3(filename='exp3_enabled.json'),
                pytest.mark.config(EATS_COURIER_SERVICE_MAPPING={}),
            ],
        ),
        pytest.param(
            USER_AGENT_TAXIMETER,
            'parks_response.json',
            'expected_response_happy_only_taxi_parks_no_button.json',
            id='only taxi parks',
            marks=[
                pytest.mark.experiments3(filename='exp3_without_button.json'),
                pytest.mark.config(EATS_COURIER_SERVICE_MAPPING={}),
            ],
        ),
        pytest.param(
            USER_AGENT_TAXIMETER,
            'parks_response_one_profile.json',
            'expected_response_one_profile_categorized.json',
            id='one profile, button enabled',
            marks=[pytest.mark.experiments3(filename='exp3_enabled.json')],
        ),
        pytest.param(
            USER_AGENT_TAXIMETER,
            'parks_response_one_profile.json',
            'expected_response_old_one_profile.json',
            id='one Eda profile, button enabled -> should not show',
            marks=[
                pytest.mark.experiments3(filename='exp3_enabled.json'),
                pytest.mark.config(
                    EATS_COURIER_SERVICE_MAPPING={
                        'selfemployed': 'dbid1',
                        'selfemployed_by_country': {'RU': 'dbid1'},
                    },
                ),
            ],
        ),
        pytest.param(
            USER_AGENT_TAXIMETER,
            'parks_response_one_profile.json',
            'expected_response_old_one_profile.json',
            id='one Eda profile, button disabled -> should not show',
            marks=[
                pytest.mark.experiments3(filename='exp3_disabled.json'),
                pytest.mark.config(
                    EATS_COURIER_SERVICE_MAPPING={
                        'selfemployed': 'dbid1',
                        'selfemployed_by_country': {'RU': 'dbid1'},
                    },
                ),
            ],
        ),
        pytest.param(
            USER_AGENT_TAXIMETER,
            'parks_response_one_profile.json',
            'expected_response_old_one_profile.json',
            id='one profile, button disabled',
            marks=[
                pytest.mark.experiments3(filename='exp3_without_button.json'),
            ],
        ),
        pytest.param(
            USER_AGENT_TAXIMETER,
            'parks_response_one_profile.json',
            'expected_response_old_one_profile.json',
            id='button enabled but no url',
            marks=[pytest.mark.experiments3(filename='exp3_without_url.json')],
        ),
        pytest.param(
            USER_AGENT_UBER,
            'parks_response.json',
            'expected_response_old.json',
            id='uberdriver - old behaviour',
            marks=[pytest.mark.experiments3(filename='exp3_enabled.json')],
        ),
        pytest.param(
            USER_AGENT_UBER,
            'parks_response.json',
            'expected_response_old.json',
            id='exp disabled',
            marks=[pytest.mark.experiments3(filename='exp3_disabled.json')],
        ),
        pytest.param(
            USER_AGENT_TURLA,
            'parks_response.json',
            'expected_response_turla.json',
            id='exp enabled turla',
            marks=[pytest.mark.experiments3(filename='exp3_enabled.json')],
        ),
        pytest.param(
            USER_AGENT_TURLA,
            'parks_response.json',
            'expected_response_turla.json',
            id='exp disabled turla',
            marks=[pytest.mark.experiments3(filename='exp3_disabled.json')],
        ),
        pytest.param(
            USER_AGENT_RIDA,
            'parks_response.json',
            'expected_response_rida.json',
            id='exp enabled rida',
            marks=[pytest.mark.experiments3(filename='exp3_enabled.json')],
        ),
        pytest.param(
            USER_AGENT_RIDA,
            'parks_response.json',
            'expected_response_rida.json',
            id='exp disabled rida',
            marks=[pytest.mark.experiments3(filename='exp3_disabled.json')],
        ),
    ],
)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_select_db_categorized(
        taxi_driver_login,
        redis_store,
        mockserver,
        load_json,
        mock_fleet_parks_list,
        fleet_synchronizer,
        user_agent,
        parks_response,
        expected_response_json,
):
    mock_fleet_parks_list.set_parks(load_json('fleet_parks_response.json'))

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/commit/',
    )
    def _confirm_commit(request):
        assert request.query == {'consumer': 'taxi-driver-login'}
        assert request.form == {'track_id': 'sms_track_id', 'code': '0000'}
        assert request.headers['Ya-Consumer-Client-Ip'] == '1.1.1.1'
        return {'status': 'ok'}

    @mockserver.json_handler('/parks/driver-profiles/search')
    def _driver_profiles_search(request):
        return load_json(parks_response)

    @mockserver.json_handler(
        '/parks-certifications/v1/parks/certifications/list',
    )
    def _parks_certifications(request):
        return {
            'certifications': [
                {'park_id': 'dbid1', 'is_certified': False},
                {'park_id': 'dbid2', 'is_certified': True},
                {'park_id': 'dbid3', 'is_certified': False},
            ],
        }

    redis_store.set(f'Driver:SMS:TrackId:{PHONE}', 'sms_track_id')

    headers = HEADERS.copy()
    headers['User-Agent'] = user_agent

    response = await taxi_driver_login.post(
        'v1/driver/login', headers=headers, data=DATA,
    )
    assert response.status_code == 200

    content = response.json()
    content.pop('token')
    assert content == load_json(expected_response_json)


@pytest.mark.parametrize(
    (
        'parks_response',
        'expected_response_under_limit_json',
        'expected_response_over_limit_json',
    ),
    [
        pytest.param(
            'parks_response_one_profile.json',
            'expected_response_one_profile_categorized.json',
            'expected_response_old_one_profile.json',
            id='one park - over limit should login right away',
        ),
        pytest.param(
            'parks_response.json',
            'expected_response_happy_only_taxi_parks.json',
            'expected_response_happy_only_taxi_parks_no_button.json',
            id='two parks',
        ),
    ],
)
@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.config(DRIVER_LOGIN_CLEAN_MAPPED_PARKS=True)
@pytest.mark.experiments3(filename='exp3_enabled_with_limit.json')
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_select_db_categorized_with_limit(
        taxi_driver_login,
        redis_store,
        mockserver,
        load_json,
        mock_fleet_parks_list,
        fleet_synchronizer,
        parks_response,
        expected_response_under_limit_json,
        expected_response_over_limit_json,
):
    mock_fleet_parks_list.set_parks(load_json('fleet_parks_response.json'))

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/commit/',
    )
    def _confirm_commit(request):
        return {'status': 'ok'}

    @mockserver.json_handler('/parks/driver-profiles/search')
    def _driver_profiles_search(request):
        return load_json(parks_response)

    @mockserver.json_handler(
        '/parks-certifications/v1/parks/certifications/list',
    )
    def _parks_certifications(request):
        return {
            'certifications': [
                {'park_id': 'dbid1', 'is_certified': False},
                {'park_id': 'dbid2', 'is_certified': True},
                {'park_id': 'dbid3', 'is_certified': False},
            ],
        }

    redis_store.set(f'Driver:SMS:TrackId:{PHONE}', 'sms_track_id')

    for expected_response in (
            expected_response_under_limit_json,
            expected_response_under_limit_json,
            expected_response_over_limit_json,
            expected_response_over_limit_json,
    ):
        response = await taxi_driver_login.post(
            'v1/driver/login', headers=HEADERS, data=DATA,
        )
        assert response.status_code == 200

        content = response.json()
        content.pop('token')
        assert content == load_json(expected_response)
