import pytest

PARK_ID = 'park1'
MAPPED_PARK_ID = 'park1uber'

DEFAULT_LICENSE = 'FOOLICENSE'

TOKEN_OK_RENT = 'ok_token_rent'


async def get_profile_by_token(db, token, fields):
    profile = await db.selfreg_profiles.find_one(
        filter={'token': token}, projection=fields,
    )
    return profile


# Tests


@pytest.mark.parametrize(
    'token, rent_option, park_id, is_uberdriver, check_fleet_type, '
    'expect_code',
    [
        ('ok_token_owncar', 'owncar', PARK_ID, False, False, 200),
        ('ok_token_rent', 'rent', PARK_ID, False, False, 200),
        ('ok_token_owncar', None, PARK_ID, False, False, 200),
        ('ok_token_rent', None, PARK_ID, False, False, 200),
        ('ok_token_rent', None, 'excluded_park', False, False, 404),
        ('ok_token_rent', 'rent', MAPPED_PARK_ID, True, False, 200),
        ('ok_token_rent', 'rent', MAPPED_PARK_ID, True, True, 200),
    ],
)
async def test_selfreg_park_choose_ok(
        mockserver,
        mongo,
        mock_hiring_taxiparks_gambling,
        taxi_selfreg,
        taxi_config,
        mock_personal,
        mock_driver_profiles_maker,
        mock_fleet_vehicles_default,
        token,
        rent_option,
        park_id,
        is_uberdriver,
        check_fleet_type,
        expect_code,
        db,
):
    fixed_park_id = PARK_ID if is_uberdriver else park_id
    driver_profiles_mock = mock_driver_profiles_maker(
        expect_license=DEFAULT_LICENSE, park_id='excluded_park',
    )

    if is_uberdriver:

        @mockserver.json_handler('/fleet-synchronizer/v1/mapping/park')
        def _mock_park_mapping(request):
            return {
                'mapping': [
                    {'app_family': 'uberdriver', 'park_id': MAPPED_PARK_ID},
                    {'app_family': 'taximeter', 'park_id': PARK_ID},
                ],
            }

    taxi_config.set_values(
        {'SELFREG_CHECK_FLEET_TYPE_FROM_GAMBLING': check_fleet_type},
    )
    await taxi_selfreg.invalidate_caches()

    @mock_hiring_taxiparks_gambling('/taxiparks/verify')
    def _handler(request):
        assert request.method == 'POST'
        assert request.headers['X-External-Service'] == 'taximeter_selfreg'
        body = request.json
        assert body['db_id'] == fixed_park_id
        assert body['city'] == 'Москва'
        assert body['rent'] == (token == 'ok_token_rent')
        assert body['workflow_group'] == 'self_registration'
        response = {'db_id': fixed_park_id, 'relevant': True}
        return mockserver.make_response(status=200, json=response)

    data = {'park_id': park_id}
    params = {'token': token}
    if rent_option:
        params['rent_option'] = rent_option

    before_profile = await get_profile_by_token(db, token, ['park_id'])
    assert before_profile
    assert before_profile.get('park_id') is None

    response = await taxi_selfreg.post(
        '/selfreg/park/choose',
        json=data,
        params=params,
        headers={
            'Content-Type': 'application/json',
            **({'User-Agent': 'Taximeter-Uber 9.60'} if is_uberdriver else {}),
        },
    )
    assert response.status == expect_code
    after_profile = await get_profile_by_token(db, token, ['park_id'])

    if expect_code == 200:
        assert _handler.times_called == 1

        body = await response.json()
        assert body['park_id'] == fixed_park_id
        assert after_profile['park_id'] == fixed_park_id

        selfreg_user = await mongo.selfreg_profiles.find_one({'token': token})
        assert selfreg_user['registration_step'] == 'park'
    else:
        assert _handler.times_called == 0
        assert 'park_id' not in after_profile

    assert mock_personal.store_licenses.times_called == 1
    assert driver_profiles_mock.retrieve_by_license_handler.times_called == 1


@pytest.mark.parametrize(
    'token,rent_option,expect_code',
    [
        ('', None, 400),
        ('bad_token', 'rent', 401),
        # invalid contract: some fields missing in the profile
        ('ok_token_no_city', 'rent', 400),
        ('ok_token_no_phone', 'rent', 500),
        ('ok_token_empty_rent_option', 'rent', 400),
        # invalid contract: profile already committed
        ('ok_token_committed', 'rent', 401),
        # invalid contract: couriers not allowed
        ('ok_token_onfoot', 'rent', 400),
        # invalid contract: rent option does not match profile
        ('ok_token_owncar', 'rent', 400),
        ('ok_token_rent', 'owncar', 400),
    ],
)
async def test_selfreg_park_choose_errors(
        taxi_selfreg, token, rent_option, expect_code, db,
):
    data = {'park_id': PARK_ID}
    params = {'token': token, 'rent_option': rent_option}

    before_profile = await get_profile_by_token(db, token, ['park_id'])
    if before_profile:
        assert before_profile.get('park_id') is None

    response = await taxi_selfreg.post(
        '/selfreg/park/choose',
        json=data,
        params=params,
        headers={'Content-Type': 'application/json'},
    )
    assert response.status == expect_code
    after_profile = await get_profile_by_token(db, token, ['park_id'])

    if after_profile:
        assert after_profile.get('park_id') is None


@pytest.mark.parametrize(
    'gambling_response,expect_code',
    [(400, 404), (500, 500), ('timeout_error', 500), ('network_error', 500)],
)
async def test_selfreg_park_choose_errors_gambling(
        mockserver,
        mock_hiring_taxiparks_gambling,
        taxi_selfreg,
        mock_personal,
        mock_driver_profiles_maker,
        mock_fleet_vehicles_default,
        gambling_response,
        gambling_response_maker,
        expect_code,
):
    driver_profiles_mock = mock_driver_profiles_maker(
        expect_license=DEFAULT_LICENSE, park_id='excluded_park',
    )

    @mock_hiring_taxiparks_gambling('/taxiparks/verify')
    def _handler(request):
        return gambling_response_maker(gambling_response)

    data = {'park_id': PARK_ID}
    params = {'token': 'ok_token_rent', 'rent_option': 'rent'}

    response = await taxi_selfreg.post(
        '/selfreg/park/choose',
        json=data,
        params=params,
        headers={'Content-Type': 'application/json'},
    )
    assert response.status == expect_code
    if gambling_response == 400:
        assert _handler.times_called == 1
    else:
        assert _handler.times_called == 3
    assert driver_profiles_mock.retrieve_by_license_handler.times_called == 1
    assert mock_personal.store_licenses.times_called == 1


@pytest.mark.parametrize('paid_type', ['free', 'paid'])
@pytest.mark.config(SELFREG_ENABLE_PAID_ACQUISITION_EXP=True)
@pytest.mark.usefixtures('mock_personal', 'mock_fleet_vehicles_default')
async def test_paid_acquisition(
        mongo,
        mock_hiring_taxiparks_gambling,
        taxi_selfreg,
        mock_driver_profiles_maker,
        mock_hiring_data_markup,
        paid_type,
        load_json,
):
    mock_driver_profiles_maker(
        expect_license=DEFAULT_LICENSE, park_id='excluded_park',
    )

    @mock_hiring_taxiparks_gambling('/taxiparks/verify')
    def _handler(request):
        return {'db_id': PARK_ID, 'relevant': True}

    @mock_hiring_data_markup('/v1/experiments/perform')
    def _paid_acquisition_exp(request):
        return load_json('data_markup.json')[paid_type]

    await taxi_selfreg.post(
        '/selfreg/park/choose',
        json={'park_id': PARK_ID},
        params={'token': TOKEN_OK_RENT},
    )

    selfreg_user = await mongo.selfreg_profiles.find_one(
        {'token': TOKEN_OK_RENT},
    )
    assert selfreg_user['paid_acquisition_type'] == paid_type
