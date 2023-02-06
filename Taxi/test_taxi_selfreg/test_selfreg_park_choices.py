import pytest

# Constants and fixtures

DEFAULT_CONFIG = {'SELFREG_PARK_GAMBLING_SETTINGS': {'park_choices_limit': 3}}


DEFAULT_PARK = {
    '_id': 'someid',
    'db_id': 'someparkid',
    'city': 'Москва, Одинцово',
    'address': 'someaddr',
    'contact_phone': ['somephone'],
    'location': {'lat': 3.14, 'lon': 2.78},
}

FLEET_VEHICLES_RESPONSE = {
    'vehicles': [
        {
            'park_id_car_id': 'excluded_park_by_car_car_id',
            'data': {
                'park_id': 'excluded_park_by_car',
                'number_normalized': 'C00lC4R',
            },
        },
    ],
}

DEFAULT_LICENSE = 'FOOLICENSE'  # as in db_selfreg_profiles.json

SELFREG_TRANSLATIONS = {
    'selfreg_v2_parks_choices_error_no_parks_owncar_text': {
        'ru': 'Нет парков для водилы на тачиле',
    },
    'selfreg_v2_parks_choices_error_no_parks_rent_text': {
        'ru': 'Нет парков для водилы без тачилы',
    },
    'selfreg_v2_parks_choices_error_no_parks_uberdriver_text': {
        'ru': 'Нет парков для uberdriver',
    },
}
# Tests


@pytest.mark.config(**DEFAULT_CONFIG)
@pytest.mark.parametrize('expect_empty_lists', [True, False])
@pytest.mark.parametrize(
    'rent_option,handler_times_called,expect_response_fields,expect_code',
    [
        ('owncar', 1, ['owncar'], 200),
        ('rent', 1, ['rent'], 200),
        ('rent,owncar', 2, ['rent', 'owncar'], 200),
        ('owncar,rent', 2, ['rent', 'owncar'], 200),
    ],
)
async def test_selfreg_park_choices_ok(
        mockserver,
        mongo,
        mock_hiring_taxiparks_gambling,
        mock_personal,
        mock_driver_profiles_maker,
        mock_fleet_vehicles_default,
        taxi_selfreg,
        expect_empty_lists,
        rent_option,
        handler_times_called,
        expect_response_fields,
        expect_code,
):
    driver_profiles_mock = mock_driver_profiles_maker(
        DEFAULT_LICENSE, 'excluded_park',
    )

    @mock_hiring_taxiparks_gambling('/taxiparks/choose')
    def gambling_handler(request):
        assert request.method == 'POST'
        assert request.headers['X-External-Service'] == 'taximeter_selfreg'
        body = request.json
        is_rent = body.pop('rent')
        assert body == {
            'limit': 3,
            'city': 'Москва',
            'workflow_group': 'self_registration',
            'blacklisted_db_ids': ['excluded_park'],
            'deaf_relation': ['only_not_deaf', 'deaf_and_not_deaf'],
            'fleet_type': 'taximeter',
        }

        park_name = 'park_' + ('rent' if is_rent else 'owncar')
        return {
            'finished': False,
            'parks': (
                []
                if expect_empty_lists
                else [{**DEFAULT_PARK, 'taximeter_name': park_name}]
            ),
        }

    token = 'ok_token'
    params = {'token': token, 'rent_option': rent_option}
    response = await taxi_selfreg.get(
        '/selfreg/park/choices',
        params=params,
        headers={'Content-Type': 'application/json'},
    )
    assert response.status == expect_code
    assert gambling_handler.times_called == handler_times_called
    assert mock_personal.store_licenses.times_called == 1
    assert driver_profiles_mock.retrieve_by_license_handler.times_called == 1

    profile = await mongo.selfreg_profiles.find_one({'token': token})
    assert profile.get('registration_step') == (
        'park_choices' if not expect_empty_lists else None
    )

    body = await response.json()
    choices_by_type = body['park_choices_by_type']
    for rent_option_field in expect_response_fields:
        assert rent_option_field in choices_by_type
        choices = choices_by_type[rent_option_field]
        if expect_empty_lists:
            assert not choices
        else:
            assert len(choices) == 1
            park = choices[0]
            assert park['name'] == 'park_' + rent_option_field
            assert park['park_id'] == DEFAULT_PARK['db_id']
            assert park['address'] == DEFAULT_PARK['address']
            assert park['contact_phones'] == DEFAULT_PARK['contact_phone']
            assert park['location'] == DEFAULT_PARK['location']


@pytest.mark.config(**DEFAULT_CONFIG)
@pytest.mark.parametrize(
    'token,rent_option,expect_code',
    [
        ('', None, 400),
        ('bad_token', 'rent', 401),
        # some fields missing in the profile, return empty list
        ('ok_token_no_city', 'rent', 200),
        ('ok_token_no_phone', 'rent', 500),
        # invalid contract: profile already committed
        ('ok_token_committed', 'rent', 401),
    ],
)
async def test_selfreg_park_choices_errors(
        taxi_selfreg, token, rent_option, expect_code, mock_personal,
):
    params = {'token': token, 'rent_option': rent_option}
    response = await taxi_selfreg.get(
        '/selfreg/park/choices',
        params=params,
        headers={'Content-Type': 'application/json'},
    )

    assert response.status == expect_code
    assert mock_personal.store_licenses.times_called == 0
    if expect_code == 200:
        assert await response.json() == {
            'park_choices_by_type': {'rent': [], 'owncar': []},
        }


@pytest.mark.config(**DEFAULT_CONFIG)
@pytest.mark.parametrize(
    'gambling_response,expect_code',
    [(400, 200), (500, 200), ('timeout_error', 200), ('network_error', 200)],
)
async def test_selfreg_park_choices_errors_gambling(
        mockserver,
        mock_hiring_taxiparks_gambling,
        mock_personal,
        mock_driver_profiles_maker,
        taxi_selfreg,
        gambling_response,
        gambling_response_maker,
        expect_code,
):
    driver_profiles_mock = mock_driver_profiles_maker(
        DEFAULT_LICENSE, 'excluded_park',
    )

    @mock_hiring_taxiparks_gambling('/taxiparks/choose')
    def _handler(request):
        return gambling_response_maker(gambling_response)

    params = {'token': 'ok_token', 'rent_option': 'rent'}
    response = await taxi_selfreg.get(
        '/selfreg/park/choices',
        params=params,
        headers={'Content-Type': 'application/json'},
    )
    assert response.status == expect_code
    response_body = await response.json()
    assert response_body == {
        'park_choices_by_type': {'rent': [], 'owncar': []},
    }

    assert mock_personal.store_licenses.times_called == 1
    assert driver_profiles_mock.retrieve_by_license_handler.times_called == 1
    if gambling_response == 400:
        assert _handler.times_called == 1
    else:
        assert _handler.times_called == 3


@pytest.mark.config(**DEFAULT_CONFIG)
@pytest.mark.parametrize(
    'gambling_response', [400, 500, 'timeout_error', 'network_error'],
)
async def test_selfreg_park_choices_errors_partial(
        mockserver,
        mock_hiring_taxiparks_gambling,
        mock_personal,
        mock_driver_profiles_maker,
        taxi_selfreg,
        gambling_response,
        gambling_response_maker,
):
    """
    В этом тесте запрос 'rent' успешен, а 'owncar' - фейлится.
    В ответе должен быть только 'rent', а 'owncar' - будет пуст.
    """
    driver_profiles_mock = mock_driver_profiles_maker(
        DEFAULT_LICENSE, 'excluded_park',
    )

    @mock_hiring_taxiparks_gambling('/taxiparks/choose')
    def _handler(request):
        body = request.json
        if body['rent']:
            return {
                'finished': False,
                'parks': [{**DEFAULT_PARK, 'taximeter_name': 'park_rent'}],
            }
        return gambling_response_maker(gambling_response)

    params = {'token': 'ok_token', 'rent_option': 'rent,owncar'}
    response = await taxi_selfreg.get(
        '/selfreg/park/choices',
        params=params,
        headers={'Content-Type': 'application/json'},
    )
    assert response.status == 200
    if gambling_response == 400:
        # 1 call for 'rent' - success, 1 call for 'owncar' - failed
        assert _handler.times_called == 2
    else:
        # 1 call for 'rent' - success, 3 retries for 'owncar' - failed
        assert _handler.times_called == 4
    assert mock_personal.store_licenses.times_called == 1
    assert driver_profiles_mock.retrieve_by_license_handler.times_called == 1
    body = await response.json()
    choices_by_type = body['park_choices_by_type']
    assert list(choices_by_type.keys()) == ['rent', 'owncar']
    assert choices_by_type['owncar'] == []
    choices = choices_by_type['rent']
    assert len(choices) == 1
    park = choices[0]
    assert park['name'] == 'park_rent'


@pytest.mark.config(**DEFAULT_CONFIG)
@pytest.mark.config(
    SELFREG_FILTER_REFERRAL_PARENT_PARK={
        'is_enabled': True,
        'force_disabled': {
            'selfreg_cities': ['Санкт-Петербург'],
            'parent_parks': ['park_parent_blacklist'],
        },
    },
)
@pytest.mark.parametrize(
    'token,referral_park,expect_blacklisted',
    [
        # Referral park filtered
        (
            'ok_token_promocode',
            'park_parent',
            ['excluded_park', 'park_parent'],
        ),
        # Promocode not found
        ('ok_token_promocode', None, ['excluded_park']),
        # Park blacklisted
        ('ok_token_promocode', 'park_parent_blacklist', ['excluded_park']),
        # City blacklisted
        ('ok_token_promocode_city_disabled', 'park_parent', ['excluded_park']),
    ],
)
async def test_selfreg_park_choices_referral_promocode(
        mockserver,
        mock_hiring_taxiparks_gambling,
        mock_personal,
        mock_driver_profiles_maker,
        taxi_selfreg,
        mock_driver_referrals,
        token,
        referral_park,
        expect_blacklisted,
):

    driver_profiles_mock = mock_driver_profiles_maker(
        DEFAULT_LICENSE, 'excluded_park',
    )

    @mock_driver_referrals('/service/check-promocode')
    def _check_promocode(request):
        if referral_park:
            assert request.json['promocode']
            return {
                'result': 'OK',
                'park_id': referral_park,
                'driver_id': 'driver_id',
            }
        return mockserver.make_response(
            status=400, json={'result': 'Not found'},
        )

    @mock_hiring_taxiparks_gambling('/taxiparks/choose')
    def _gambling_handler(request):
        blacklisted_parks = request.json['blacklisted_db_ids']
        assert set(blacklisted_parks) == set(expect_blacklisted)
        return {
            'finished': False,
            'parks': [{**DEFAULT_PARK, 'taximeter_name': 'default_park'}],
        }

    response = await taxi_selfreg.get(
        '/selfreg/park/choices',
        params={'token': token, 'rent_option': 'rent,owncar'},
        headers={'Content-Type': 'application/json'},
    )

    assert response.status == 200
    assert mock_personal.store_licenses.times_called == 1
    assert driver_profiles_mock.retrieve_by_license_handler.times_called == 1


@pytest.mark.translations(
    taximeter_backend_driver_messages=SELFREG_TRANSLATIONS,
)
@pytest.mark.config(**DEFAULT_CONFIG)
@pytest.mark.parametrize('expect_num_parks', [0, 1, 2])
@pytest.mark.parametrize('random_park', [False, True])
@pytest.mark.parametrize(
    'token, is_rent, expect_code',
    [('ok_token_rent', True, 200), ('ok_token_owncar', False, 200)],
)
@pytest.mark.parametrize(
    'is_uberdriver, are_gambling_parks_ok, check_fleet_type',
    [(False, True, True), (True, True, True), (True, False, True)],
)
async def test_selfreg_v1_parks_choices_ok(
        mockserver,
        mongo,
        mock_hiring_taxiparks_gambling,
        mock_personal,
        mock_driver_profiles_maker,
        mock_fleet_vehicles_default,
        mock_fleet_synchronizer,
        taxi_selfreg,
        taxi_config,
        token,
        is_rent,
        expect_num_parks,
        random_park,
        expect_code,
        is_uberdriver,
        are_gambling_parks_ok,
        check_fleet_type,
):
    if is_uberdriver and are_gambling_parks_ok:
        for i in range(3):
            mock_fleet_synchronizer.add_mapping(f'originaldb{i}', f'db{i}')

    mock_fleet_vehicles_default.set_response(FLEET_VEHICLES_RESPONSE)
    taxi_config.set_values(
        {'SELFREG_CHECK_FLEET_TYPE_FROM_GAMBLING': check_fleet_type},
    )
    await taxi_selfreg.invalidate_caches()

    driver_profiles_mock = mock_driver_profiles_maker(
        DEFAULT_LICENSE, 'excluded_park',
    )
    park_suffix = '_rent' if is_rent else '_owncar'

    def make_park(idx, rent):
        return {
            '_id': 'someid',
            'city': 'Москва',
            'db_id': 'db' + str(idx),
            'taximeter_name': 'park' + str(idx) + park_suffix,
            'address': 'someaddr',
            'contact_phone': ['somephone'],
            'location': {'lat': 3.14, 'lon': 2.78},
        }

    @mock_hiring_taxiparks_gambling('/taxiparks/choose')
    def gambling_handler(request):
        assert request.method == 'POST'
        assert request.headers['X-External-Service'] == 'taximeter_selfreg'
        body = request.json
        expect_excluded_parks = ['excluded_park']
        if not is_rent:
            expect_excluded_parks.append('excluded_park_by_car')
        excluded_parks = set(body.pop('blacklisted_db_ids'))
        assert excluded_parks == set(expect_excluded_parks)
        assert body == {
            'rent': is_rent,
            'limit': 3,
            'city': 'Москва',
            'workflow_group': 'self_registration',
            'deaf_relation': ['only_not_deaf', 'deaf_and_not_deaf'],
            'fleet_type': 'uberdriver' if is_uberdriver else 'taximeter',
        }
        parks = [make_park(idx, is_rent) for idx in range(expect_num_parks)]
        return {'finished': False, 'parks': parks}

    params = {'token': token, 'random_park': random_park}

    response = await taxi_selfreg.get(
        '/selfreg/v1/parks/choices',
        params=params,
        headers={
            'Content-Type': 'application/json',
            'Accept-Language': 'ru_RU',
            **({'User-Agent': 'Taximeter-Uber 9.60'} if is_uberdriver else {}),
        },
    )

    assert gambling_handler.times_called == int(check_fleet_type)
    assert mock_fleet_vehicles_default.handler.times_called == (
        0 if is_rent else 1
    )
    assert mock_personal.store_licenses.times_called == 1
    assert driver_profiles_mock.retrieve_by_license_handler.times_called == 1

    profile = await mongo.selfreg_profiles.find_one({'token': token})

    if expect_num_parks == 0 or not are_gambling_parks_ok:
        assert profile.get('registration_step') is None
        assert response.status == 404
        body = await response.json()
        if is_uberdriver:
            assert body == {
                'code': 'no_parks_uberdriver',
                'message': 'Нет парков для uberdriver',
            }
        elif is_rent:
            assert body == {
                'code': 'no_parks_rent',
                'message': 'Нет парков для водилы без тачилы',
            }
        else:
            assert body == {
                'code': 'no_parks_owncar',
                'message': 'Нет парков для водилы на тачиле',
            }
    else:
        assert profile.get('registration_step') == 'park_choices'
        body = await response.json()
        assert response.status == expect_code
        assert body['chosen_flow'] == (
            'driver-without-auto' if is_rent else 'driver-with-auto'
        )
        expected_parks = [
            {
                'park_id': 'db0',
                'name': 'park0' + park_suffix,
                'address': 'someaddr',
                'contact_phones': ['somephone'],
                'location': {'lat': 3.14, 'lon': 2.78},
            },
        ]
        if expect_num_parks == 2:
            expected_parks.append(
                {
                    'park_id': 'db1',
                    'name': 'park1' + park_suffix,
                    'address': 'someaddr',
                    'contact_phones': ['somephone'],
                    'location': {'lat': 3.14, 'lon': 2.78},
                },
            )
        assert body['parks'] == expected_parks
        if random_park and expect_num_parks > 1:
            assert body['random_park'] == expected_parks[0]
        else:
            assert 'random_park' not in body


@pytest.mark.config(**DEFAULT_CONFIG)
@pytest.mark.parametrize(
    'fail_type, expect_status',
    [
        ('fail_personal', 500),
        ('fail_profiles', 500),
        ('fail_vehicles', 500),
        (None, 200),
    ],
)
async def test_selfreg_v1_parks_blacklist_errors(
        mockserver,
        mock_driver_profiles,
        mock_fleet_vehicles_default,
        mock_hiring_taxiparks_gambling,
        taxi_selfreg,
        fail_type,
        expect_status,
):
    # emulate errors from 'personal'
    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def _store_licenses(request):
        if fail_type == 'fail_personal':
            return mockserver.make_response(status=500)
        return {'id': 'license_pd_id', 'value': 'license'}

    @mock_driver_profiles('/v1/driver/profiles/retrieve_by_license')
    def _retrieve_by_license_handler(request):
        if fail_type == 'fail_profiles':
            return mockserver.make_response(status=500)
        return {
            'profiles_by_license': [
                {
                    'driver_license': 'license_pd_id',
                    'profiles': [
                        {
                            'data': {'park_id': 'park'},
                            'park_driver_profile_id': 'driver',
                        },
                    ],
                },
            ],
        }

    if fail_type == 'fail_vehicles':
        mock_fleet_vehicles_default.set_error(500)
    else:
        mock_fleet_vehicles_default.set_response(FLEET_VEHICLES_RESPONSE)

    @mock_hiring_taxiparks_gambling('/taxiparks/choose')
    def _gambling_handler(request):
        park = {**DEFAULT_PARK, 'taximeter_name': 'someparkname'}
        return {'finished': False, 'parks': [park]}

    response = await taxi_selfreg.get(
        '/selfreg/v1/parks/choices',
        params={'token': 'ok_token_owncar'},
        headers={
            'Content-Type': 'application/json',
            'Accept-Language': 'ru_RU',
        },
    )
    assert response.status == expect_status
