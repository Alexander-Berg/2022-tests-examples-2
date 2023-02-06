import pytest

URL = '/selfreg/v1/professions-allowed/choose'
HEADERS = {'User-Agent': 'Taximeter 9.61 (1234)'}
PARAMS = {'token': 'token1'}
REQUEST_JSON = {'city_id': 'Москва', 'chosen_flow': 'driver-without-auto'}


@pytest.mark.config(
    TAXIMETER_SELFREG_SETTINGS={
        'enabled_countries': ['rus'],
        'enable_fns_selfemployment': True,
    },
)
@pytest.mark.parametrize(
    'token,city_id,city_allowed,referral_cities,content_response,status_code',
    [
        pytest.param(
            'token1',
            'Метрополис',
            False,
            [],
            {'code': '400', 'message': 'Unknown city'},
            400,
            id='bad_city',
        ),
        pytest.param(
            'token1',
            'Москва',
            False,
            [],
            {'code': '400', 'message': 'Flow disabled in city'},
            400,
            id='city not allowed',
        ),
        pytest.param(
            'token1',
            'Москва',
            True,
            [],
            {'referral_promocode_enabled': False},
            200,
            id='city ok, no referrals anywhere',
        ),
        pytest.param(
            'token1',
            'Москва',
            True,
            ['Минск'],
            {'referral_promocode_enabled': False},
            200,
            id='city ok, no referrals in city',
        ),
        pytest.param(
            'token1',
            'Москва',
            True,
            ['Москва'],
            {'referral_promocode_enabled': True},
            200,
            id='city ok, referrals enabled',
        ),
        pytest.param(
            'token2',
            'Москва',
            True,
            ['Москва'],
            {'referral_promocode_enabled': False},
            200,
            id='city ok, city have referrals, disabled by park change',
        ),
    ],
)
async def test_allowed_profession_choose(
        taxi_selfreg,
        mockserver,
        mock_personal,
        mock_hiring_forms_default,
        mock_driver_referrals,
        mongo,
        token,
        city_allowed,
        referral_cities,
        status_code,
        content_response,
        city_id,
):
    @mockserver.json_handler(
        '/fleet-parks/v1/parks/driver-hirings/selfreg/types',
    )
    async def _hiring_types(request):
        return {'types': [] if not city_allowed else ['lease', 'private']}

    @mock_driver_referrals('/service/referral-settings')
    async def _mock_referrals(request):
        return {'cities': referral_cities}

    profile = await mongo.selfreg_profiles.find_one({'token': token})
    assert profile['city'] == 'Санкт-Петербург'
    assert profile['chosen_flow'] == 'driver-with-auto'

    response = await taxi_selfreg.post(
        URL,
        headers=HEADERS,
        params={'token': token},
        json={'city_id': city_id, 'chosen_flow': 'driver-without-auto'},
    )

    assert response.status == status_code
    content = await response.json()
    assert content == content_response

    if status_code == 200:
        profile = await mongo.selfreg_profiles.find_one({'token': token})
        assert profile['city'] == 'Москва'
        assert profile['chosen_flow'] == 'driver-without-auto'
        assert profile.get('registration_step') == (
            'flow_selected' if city_allowed else None
        )
        assert _hiring_types.times_called == 1
        assert mock_hiring_forms_default.regions_handler.times_called == 1
        assert _mock_referrals.times_called == (1 if city_allowed else 0)


@pytest.mark.config(
    TAXIMETER_SELFREG_SETTINGS={
        'enabled_countries': ['rus'],
        'enable_fns_selfemployment': True,
    },
)
@pytest.mark.parametrize(
    'expected_json',
    [
        pytest.param(
            {'referral_promocode_enabled': False, 'story_id': 'story_id'},
            marks=pytest.mark.client_experiments3(
                file_with_default_response='selfreg_stories_settings.json',
            ),
            id='with story id',
        ),
        pytest.param(
            {'referral_promocode_enabled': False}, id='without story id',
        ),
    ],
)
async def test_story_id(
        taxi_selfreg,
        mockserver,
        mock_personal,
        mock_hiring_forms_default,
        mock_driver_referrals,
        mock_fleet_parks,
        expected_json,
):
    @mock_fleet_parks('/v1/parks/driver-hirings/selfreg/types')
    async def _hiring_types(request):
        return {'types': ['lease', 'private']}

    @mock_driver_referrals('/service/referral-settings')
    async def _mock_referrals(request):
        return {'cities': []}

    response = await taxi_selfreg.post(
        URL, headers=HEADERS, params=PARAMS, json=REQUEST_JSON,
    )

    assert response.status == 200
    response_json = await response.json()
    assert response_json == expected_json
