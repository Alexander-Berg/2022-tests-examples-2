import pytest

HEADERS = {'User-Agent': 'Taximeter 9.61 (1234)'}


@pytest.mark.config(
    TAXIMETER_SELFREG_SETTINGS={
        'enabled_countries': ['rus'],
        'enable_fns_selfemployment': True,
    },
)
@pytest.mark.parametrize(
    'expect_referral_enabled',
    [
        pytest.param(
            False,
            marks=pytest.mark.client_experiments3(
                file_with_default_response='referral_fallback_always_'
                'false.json',
            ),
            id='referral fallback set to always false',
        ),
        pytest.param(
            True,
            marks=pytest.mark.client_experiments3(
                file_with_default_response='referral_fallback_always_'
                'true.json',
            ),
            id='referral fallback set to always true',
        ),
    ],
)
async def test_city_choose_referral_fallback(
        mockserver,
        mock_personal,
        mock_hiring_forms_default,
        taxi_selfreg,
        expect_referral_enabled,
):
    @mockserver.json_handler(
        '/fleet-parks/v1/parks/driver-hirings/selfreg/types',
    )
    async def _hiring_types(request):
        return {'types': ['lease', 'private']}

    token = 'token1'
    response = await taxi_selfreg.post(
        '/selfreg/v1/cities/choose',
        headers=HEADERS,
        params={'token': token},
        json={'city_id': 'Москва'},
    )

    assert response.status == 200
    content = await response.json()
    assert content['referral_promocode_enabled'] == expect_referral_enabled


@pytest.mark.config(
    TAXIMETER_SELFREG_SETTINGS={
        'enabled_countries': ['rus'],
        'enable_fns_selfemployment': True,
    },
)
@pytest.mark.parametrize(
    'city_allowed, referral_cities, referral_enabled',
    [
        pytest.param(False, [], False, id='bad city'),
        pytest.param(True, [], False, id='city ok, no referrals anywhere'),
        pytest.param(
            True, ['Минск'], False, id='city ok, no referrals in city',
        ),
        pytest.param(True, ['Москва'], True, id='city ok, referrals enabled'),
    ],
)
async def test_city_choose(
        taxi_selfreg,
        mockserver,
        mock_personal,
        mock_hiring_forms_default,
        mock_driver_referrals,
        mongo,
        city_allowed,
        referral_cities,
        referral_enabled,
):
    token = 'token1'

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

    response = await taxi_selfreg.post(
        '/selfreg/v1/cities/choose',
        headers=HEADERS,
        params={'token': token},
        json={'city_id': 'Москва'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'available_to_register': city_allowed,
        'referral_promocode_enabled': referral_enabled,
    }

    profile = await mongo.selfreg_profiles.find_one({'token': token})
    assert profile['city'] == 'Москва'
    assert profile.get('registration_step') == (
        'city_allowed' if city_allowed else None
    )
    assert _hiring_types.times_called == 1
    assert mock_hiring_forms_default.regions_handler.times_called == 1
    assert _mock_referrals.times_called == (1 if city_allowed else 0)


async def test_city_not_found(taxi_selfreg):
    token = 'token1'

    response = await taxi_selfreg.post(
        '/selfreg/v1/cities/choose',
        headers=HEADERS,
        params={'token': token},
        json={'city_id': 'Houston'},
    )

    assert response.status == 400
    content = await response.json()
    assert content == {}
