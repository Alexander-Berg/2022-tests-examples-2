import pytest

HEADERS = {'User-Agent': 'Taximeter 9.61 (1234)'}


@pytest.mark.config(
    TAXIMETER_FNS_SELF_EMPLOYMENT_PROMO_SETTINGS={
        'cities': ['Санкт-Петербург'],
        'countries': [],
        'dbs': [],
        'dbs_disable': [],
        'enable': True,
    },
)
@pytest.mark.config(
    TAXIMETER_SELFREG_SETTINGS={
        'enabled_countries': ['rus'],
        'enable_fns_selfemployment': True,
    },
)
async def test_available_flows_choose(
        taxi_selfreg,
        mockserver,
        mock_personal,
        mock_hiring_forms_default,
        mongo,
):
    token = 'token'

    @mockserver.json_handler(
        '/fleet-parks/v1/parks/driver-hirings/selfreg/types',
    )
    def _hiring_types(request):
        return {'types': ['lease', 'private']}

    profile = await mongo.selfreg_profiles.find_one({'token': token})
    assert 'chosen_flow' not in profile
    assert 'rent_option' not in profile
    assert 'registration_step' not in profile

    ##
    # First request
    ##
    response = await taxi_selfreg.post(
        '/selfreg/v1/available-flows/choose',
        params={'token': token},
        headers=HEADERS,
        json={'chosen_flow': 'driver-with-auto'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {}

    profile = await mongo.selfreg_profiles.find_one({'token': token})
    assert profile['chosen_flow'] == 'driver-with-auto'
    assert profile['rent_option'] == 'owncar'
    assert profile['registration_step'] == 'flow_selected'

    ##
    # Second request
    ##
    response = await taxi_selfreg.post(
        '/selfreg/v1/available-flows/choose',
        params={'token': token},
        headers=HEADERS,
        json={'chosen_flow': 'driver-without-auto'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {}

    profile = await mongo.selfreg_profiles.find_one({'token': token})
    assert profile['chosen_flow'] == 'driver-without-auto'
    assert profile['rent_option'] == 'rent'
    assert profile['registration_step'] == 'flow_selected'
    assert mock_hiring_forms_default.regions_handler.times_called == 1
    assert _hiring_types.times_called == 2


@pytest.mark.config(
    TAXIMETER_SELFREG_SETTINGS={
        'enabled_countries': ['rus'],
        'enable_fns_selfemployment': True,
    },
)
async def test_flow_not_enabled(
        taxi_selfreg,
        mockserver,
        mock_personal,
        mock_hiring_forms_default,
        mongo,
):
    @mockserver.json_handler(
        '/fleet-parks/v1/parks/driver-hirings/selfreg/types',
    )
    def _hiring_types(request):
        return {'types': ['private']}

    token = 'token'

    response = await taxi_selfreg.post(
        '/selfreg/v1/available-flows/choose',
        params={'token': token},
        headers=HEADERS,
        json={'chosen_flow': 'driver-with-auto'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}

    response = await taxi_selfreg.post(
        '/selfreg/v1/available-flows/choose',
        params={'token': token},
        headers=HEADERS,
        json={'chosen_flow': 'driver-without-auto'},
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'flow_disabled',
        'message': 'Flow disabled in city',
    }
    profile = await mongo.selfreg_profiles.find_one({'token': token})
    assert profile['chosen_flow'] == 'driver-with-auto'
    assert profile['rent_option'] == 'owncar'
    assert mock_hiring_forms_default.regions_handler.times_called == 1
    assert _hiring_types.times_called == 2
