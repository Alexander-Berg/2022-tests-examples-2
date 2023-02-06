import datetime

import pytest


HEADERS = {'Accept-Language': 'ru_RU', 'User-Agent': 'Taximeter 9.61 (1234)'}

DEFAULT_LICENSE = '44ББ112233'

REQUEST = {
    'city': 'Санкт-Петербург',
    'first_name': 'John',
    'last_name': 'Doe',
    'middle_name': 'Howard',
    'license_country': 'RU',
    'license_number': '112233',
    'license_series': '44ББ',
    'license_issue_date': '2000-01-01',
    'license_expire_date': '2100-01-01',
}

EXP3_SELF_EMPLOYMENT = (
    'exp3_selfreg_driver_license_settings_self_employment.json'
)

EXP3_PARK_EMPLOYMENT = (
    'exp3_selfreg_driver_license_settings_park_employment.json'
)


@pytest.fixture
def _mock_driver_profiles_maker(mockserver, mock_driver_profiles):
    def context(expect_license, has_profiles, work_status):
        class CallContext:
            @mock_driver_profiles('/v1/driver/profiles/retrieve_by_license')
            @staticmethod
            def retrieve_by_license_handler(request):
                assert request.method == 'POST'
                body = request.json
                default_license_pd_id = f'personal_{expect_license}'
                assert body['projection'] == ['data.work_status']
                profile_data = (
                    {
                        'data': {'work_status': work_status},
                        'park_driver_profile_id': 'uuid_dbid',
                    }
                    if work_status
                    else None
                )
                profiles = (
                    [profile_data] if has_profiles and work_status else []
                )
                response_data = {
                    'profiles_by_license': [
                        {
                            'driver_license': default_license_pd_id,
                            'profiles': profiles,
                        },
                    ],
                }
                return mockserver.make_response(status=200, json=response_data)

        return CallContext()

    return context


@pytest.mark.config(
    TAXIMETER_SELFREG_SETTINGS={
        'enabled_countries': ['rus', 'fin'],
        'enable_fns_selfemployment': True,
        'check_licence_for_existing_drivers': True,
    },
)
@pytest.mark.parametrize('has_parks', [True, False])
@pytest.mark.parametrize('has_profiles', [True, False])
@pytest.mark.parametrize(
    'work_status', [None, 'not_working', 'working', 'fired'],
)
async def test_ok(
        taxi_selfreg,
        mockserver,
        mongo,
        mock_personal,
        _mock_driver_profiles_maker,
        has_parks,
        has_profiles,
        work_status,
):
    @mockserver.json_handler(
        '/fleet-parks/v1/parks/driver-hirings/selfreg/types',
    )
    async def _hiring_types(request):
        return {'types': [] if not has_parks else ['lease', 'private']}

    _mock_driver_profiles_maker(DEFAULT_LICENSE, has_profiles, work_status)

    before_profile = await mongo.selfreg_profiles.find_one({'token': 'token1'})
    assert 'first_name' not in before_profile
    assert 'last_name' not in before_profile
    assert 'middle_name' not in before_profile
    assert 'license_country_id' not in before_profile
    assert 'license_number' not in before_profile
    assert 'license_series' not in before_profile
    assert 'license_issue_date' not in before_profile
    assert 'license_expire_date' not in before_profile

    response = await taxi_selfreg.post(
        '/selfreg/v1/driver-license',
        params={'token': 'token1'},
        json=REQUEST,
        headers=HEADERS,
    )

    assert response.status == 200
    content = await response.json()
    driver_status = (
        {
            None: 'not_exists',
            'not_working': 'not_active',
            'working': 'active',
            'fired': 'not_active',
        }[work_status]
        if has_profiles
        else 'not_exists'
    )
    assert content == {
        'available_options': ['rent', 'owncar'] if has_parks else [],
        'driver_status': driver_status,
    }
    profile = await mongo.selfreg_profiles.find_one({'token': 'token1'})
    if not has_profiles or work_status != 'working':
        assert profile.pop('city') == REQUEST['city']
        assert profile.pop('first_name') == REQUEST['first_name']
        assert profile.pop('last_name') == REQUEST['last_name']
        assert profile.pop('middle_name') == REQUEST['middle_name']
        assert profile.pop('license_country_id') == 'rus'
        assert profile.pop('license_number') == DEFAULT_LICENSE
        assert profile.pop('license_series') == ''
        assert profile.pop('license_pd_id') == f'personal_{DEFAULT_LICENSE}'
        assert profile.pop(
            'license_issue_date',
        ) == datetime.datetime.fromisoformat(REQUEST['license_issue_date'])
        assert profile.pop(
            'license_expire_date',
        ) == datetime.datetime.fromisoformat(REQUEST['license_expire_date'])
        assert profile.pop('registration_step') == 'license'
    else:
        assert 'first_name' not in profile
        assert 'last_name' not in profile
        assert 'middle_name' not in profile
        assert 'license_country_id' not in profile
        assert 'license_number' not in profile
        assert 'license_series' not in profile
        assert 'license_issue_date' not in profile
        assert 'license_expire_date' not in profile
        assert 'license_pd_id' not in profile


async def test_bad_token(taxi_selfreg, mockserver):
    response = await taxi_selfreg.post(
        '/selfreg/v1/driver-license',
        params={'token': 'not_existent'},
        json=REQUEST,
        headers=HEADERS,
    )
    assert response.status == 401


async def test_empty_license(taxi_selfreg, mockserver, mock_personal):
    request = REQUEST.copy()
    request['license_series'] = ''
    request['license_number'] = ''
    response = await taxi_selfreg.post(
        '/selfreg/v1/driver-license',
        params={'token': 'token1'},
        json=request,
        headers=HEADERS,
    )
    assert response.status == 400
    content = await response.json()
    assert content == {'code': '400', 'message': 'empty license'}


async def test_empty_city(taxi_selfreg, mockserver):
    request = REQUEST.copy()
    request['city'] = ''
    response = await taxi_selfreg.post(
        '/selfreg/v1/driver-license',
        params={'token': 'token_no_city'},
        json=request,
        headers=HEADERS,
    )
    assert response.status == 400
    content = await response.json()
    assert content == {'code': '400', 'message': 'empty city'}


async def test_no_city_in_cache(taxi_selfreg, mockserver):
    request = REQUEST.copy()
    request['city'] = 'no_such_city'
    response = await taxi_selfreg.post(
        '/selfreg/v1/driver-license',
        params={'token': 'token_no_city'},
        json=request,
        headers=HEADERS,
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': '400',
        'message': 'no such city: `no_such_city`',
    }


@pytest.mark.config(
    TAXIMETER_SELFREG_SETTINGS={
        'enabled_countries': ['rus', 'fin'],
        'enable_fns_selfemployment': True,
        'check_licence_for_existing_drivers': False,
    },
)
async def test_invalid_country(taxi_selfreg, mockserver, mock_personal):
    @mockserver.json_handler(
        '/fleet-parks/v1/parks/driver-hirings/selfreg/types',
    )
    async def _hiring_types(request):
        return {'types': ['lease', 'private']}

    request = REQUEST.copy()
    request['license_country'] = 'FI'

    response = await taxi_selfreg.post(
        '/selfreg/v1/driver-license',
        params={'token': 'token1'},
        json=request,
        headers=HEADERS,
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'available_options': ['rent', 'owncar'],
        'driver_status': 'invalid_license_country',
    }


@pytest.mark.config(
    TAXIMETER_SELFREG_SETTINGS={
        'enabled_countries': ['rus', 'fin'],
        'enable_fns_selfemployment': True,
        'check_licence_for_existing_drivers': False,
    },
)
@pytest.mark.parametrize('has_city_in_request', [True, False])
async def test_empty_allowed_countries(
        taxi_selfreg, mockserver, mock_personal, has_city_in_request,
):
    @mockserver.json_handler(
        '/fleet-parks/v1/parks/driver-hirings/selfreg/types',
    )
    async def _hiring_types(request):
        return {'types': ['lease', 'private']}

    request = REQUEST.copy()
    request['city'] = 'Хельсинки'
    request['license_country'] = 'FI'
    if not has_city_in_request:
        del request['city']

    response = await taxi_selfreg.post(
        '/selfreg/v1/driver-license',
        params={'token': 'token_fin'},
        json=request,
        headers=HEADERS,
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'available_options': ['rent', 'owncar'],
        'driver_status': 'not_exists',
    }


@pytest.mark.config(
    TAXIMETER_SELFREG_SETTINGS={
        'enabled_countries': ['rus', 'fin'],
        'enable_fns_selfemployment': True,
        'check_licence_for_existing_drivers': False,
    },
)
async def test_invalid_license_number(taxi_selfreg, mockserver, mock_personal):
    @mockserver.json_handler(
        '/fleet-parks/v1/parks/driver-hirings/selfreg/types',
    )
    async def _hiring_types(request):
        return {'types': ['lease', 'private']}

    request = REQUEST.copy()
    request['license_series'] = 'no_such_'
    request['license_number'] = 'pattern'

    response = await taxi_selfreg.post(
        '/selfreg/v1/driver-license',
        params={'token': 'token1'},
        json=request,
        headers=HEADERS,
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'available_options': ['rent', 'owncar'],
        'driver_status': 'invalid_license_number',
    }


@pytest.mark.parametrize(
    'token,city,license_country,suggested_employment_type',
    [
        pytest.param(
            'token1',
            'Санкт-Петербург',
            'RU',
            'self_employment',
            id='self+parks, suggest self_employment',
            marks=pytest.mark.client_experiments3(
                file_with_default_response=EXP3_SELF_EMPLOYMENT,
            ),
        ),
        pytest.param(
            'token1',
            'Санкт-Петербург',
            'RU',
            'park_employment',
            id='self+parks, suggest park_employment',
            marks=pytest.mark.client_experiments3(
                file_with_default_response=EXP3_PARK_EMPLOYMENT,
            ),
        ),
        pytest.param(
            'token1',
            'Санкт-Петербург',
            'RU',
            None,
            id='self+parks, no suggestion',
        ),
        pytest.param(
            'token_fin',
            'Хельсинки',
            'FI',
            None,
            id='parks, no suggestion',
            marks=pytest.mark.client_experiments3(
                file_with_default_response=EXP3_SELF_EMPLOYMENT,
            ),
        ),
        pytest.param(
            'token1',
            'Санкт-Петербург',
            'KZ',
            None,
            id='self+parks, not a resident',
            marks=pytest.mark.client_experiments3(
                file_with_default_response=EXP3_SELF_EMPLOYMENT,
            ),
        ),
    ],
)
@pytest.mark.config(
    TAXIMETER_SELFREG_SETTINGS={
        'enabled_countries': ['rus', 'fin'],
        'enable_fns_selfemployment': True,
        'check_licence_for_existing_drivers': False,
    },
    TAXIMETER_FNS_SELF_EMPLOYMENT_PROMO_SETTINGS={
        'cities': 'Санкт-Петербург',
        'countries': [],
        'dbs': [],
        'dbs_disable': [],
        'enable': True,
    },
)
async def test_suggested_employment_type(
        taxi_selfreg,
        mockserver,
        mock_personal,
        token,
        city,
        license_country,
        suggested_employment_type,
):
    @mockserver.json_handler(
        '/fleet-parks/v1/parks/driver-hirings/selfreg/types',
    )
    async def _hiring_types(request):
        return {'types': ['lease', 'private']}

    request = REQUEST.copy()
    request['city'] = city
    request['license_country'] = license_country

    response = await taxi_selfreg.post(
        '/selfreg/v1/driver-license',
        params={'token': token},
        json=request,
        headers=HEADERS,
    )

    assert response.status == 200
    expected_content = {
        'available_options': ['rent', 'owncar'],
        'driver_status': 'not_exists',
    }
    if suggested_employment_type:
        expected_content[
            'suggested_employment_type'
        ] = suggested_employment_type
    content = await response.json()
    assert content == expected_content


@pytest.mark.config(
    TAXIMETER_SELFREG_SETTINGS={
        'enabled_countries': ['rus', 'fin'],
        'enable_fns_selfemployment': True,
        'check_licence_for_existing_drivers': False,
    },
)
@pytest.mark.parametrize('is_absent', [True, False])
async def test_no_optional_params(
        taxi_selfreg, mockserver, mongo, mock_personal, is_absent,
):
    @mockserver.json_handler(
        '/fleet-parks/v1/parks/driver-hirings/selfreg/types',
    )
    async def _hiring_types(request):
        return {'types': ['lease', 'private']}

    request = REQUEST.copy()
    request['city'] = None
    request['license_expire_date'] = None
    request['license_series'] = None
    request['middle_name'] = None
    license_number = '1112223344'
    request['license_number'] = license_number
    if is_absent:
        del request['city']
        del request['license_expire_date']
        del request['license_series']
        del request['middle_name']

    before_profile = await mongo.selfreg_profiles.find_one({'token': 'token1'})
    assert 'first_name' not in before_profile
    assert 'last_name' not in before_profile
    assert 'middle_name' not in before_profile
    assert 'license_country_id' not in before_profile
    assert 'license_number' not in before_profile
    assert 'license_series' not in before_profile
    assert 'license_issue_date' not in before_profile
    assert 'license_expire_date' not in before_profile

    response = await taxi_selfreg.post(
        '/selfreg/v1/driver-license',
        params={'token': 'token1'},
        json=request,
        headers=HEADERS,
    )

    assert response.status == 200

    profile = await mongo.selfreg_profiles.find_one({'token': 'token1'})
    assert profile.pop('first_name') == REQUEST['first_name']
    assert profile.pop('last_name') == REQUEST['last_name']
    assert profile.pop('middle_name') is None
    assert profile.pop('license_country_id') == 'rus'
    assert profile.pop('license_number') == license_number
    assert profile.pop('license_series') == ''
    assert profile.pop('license_pd_id') == f'personal_{license_number}'
    assert profile.pop(
        'license_issue_date',
    ) == datetime.datetime.fromisoformat(REQUEST['license_issue_date'])
    assert profile.pop('license_expire_date') is None
    assert profile.pop('registration_step') == 'license'
