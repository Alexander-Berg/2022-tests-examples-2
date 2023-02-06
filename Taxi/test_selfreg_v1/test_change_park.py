import pytest


URL = '/driver/v1/selfreg/v1/change-park'

HEADERS = 'basic_headers.json'
POSITION_MSK = {'lat': 55.735961, 'lon': 37.643216}

BASIC_RESPONSE = 'basic_response.json'
COURIER_RESPONSE = 'courier_response.json'
IS_ON_ORDER_RESPONSE = 'is_on_order_response.json'

EXPECTED_NEW_PROFILE = 'expected_new_profile.json'
EXPECTED_UPDATED_PROFILE = 'expected_updated_profile.json'

DOM_RESPONSE = 'driver_order_misc_response.json'
DRIVER_PROFILES_RESPONSE = 'driver_profiles_response.json'
FLEET_PARKS_RESPONSE = 'fleet_parks_response.json'
FLEET_VEHICLES_RESPONSE = 'fleet_vehicles_response.json'

NEAREST_CITY_OVERRIDE = {'Московская область': 'Москва'}
TRANSLATIONS = {'SelfRegErrorCode_IsOnOrder': {'ru': 'On order'}}


@pytest.fixture(autouse=True)
def _mocks(
        load_json,
        mock_driver_order_misc_create,
        mock_driver_profiles_create,
        mock_fleet_parks_create,
        mock_fleet_vehicles_create,
):
    return (
        mock_driver_order_misc_create(load_json(DOM_RESPONSE)),
        mock_driver_profiles_create(load_json(DRIVER_PROFILES_RESPONSE)),
        mock_fleet_vehicles_create(load_json(FLEET_VEHICLES_RESPONSE)),
        mock_fleet_parks_create(load_json(FLEET_PARKS_RESPONSE)),
    )


def make_expected_entry(expected_json, phone, passport_uid):
    additional_props = {
        'passport_uid': passport_uid,
        'phone_number': phone,
        'phone_pd_id': f'{phone}_id',
    }
    entry = {**expected_json, **additional_props}
    return {k: v for k, v in entry.items() if v is not None}


async def _find_profile(phone, passport_uid, mongo):
    search_expression = {'is_park_change': True, 'is_committed': {'$ne': True}}
    if passport_uid:
        search_expression['passport_uid'] = passport_uid
    else:
        search_expression['phone_number'] = phone
        search_expression['passport_uid'] = {'$exists': False}
    return await mongo.selfreg_profiles.find_one(search_expression)


@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
@pytest.mark.config(
    SELFREG_NEAREST_CITY_SUGGEST_OVERRIDES=NEAREST_CITY_OVERRIDE,
)
@pytest.mark.parametrize(
    'position,license_number,is_on_order,expected_status,expected_response',
    [
        pytest.param(
            POSITION_MSK,
            '001122334455',
            False,
            200,
            BASIC_RESPONSE,
            id='driver',
        ),
        pytest.param(
            POSITION_MSK,
            'COURIER12334',
            False,
            200,
            COURIER_RESPONSE,
            id='courier',
        ),
        pytest.param(
            POSITION_MSK,
            '001122334455',
            True,
            400,
            IS_ON_ORDER_RESPONSE,
            id='on order',
        ),
        pytest.param(
            {},
            '001122334455',
            False,
            200,
            BASIC_RESPONSE,
            id='position fallback',
        ),
    ],
)
async def test_response(
        taxi_selfreg,
        mockserver,
        load_json,
        mock_driver_profiles_create,
        mock_driver_order_misc_create,
        position,
        license_number,
        is_on_order,
        expected_status,
        expected_response,
):
    mock_driver_profiles_create(
        response=load_json(DRIVER_PROFILES_RESPONSE),
        license_number=license_number,
    )
    mock_driver_order_misc_create(load_json(DOM_RESPONSE), is_on_order)
    response = await taxi_selfreg.post(
        URL, headers=load_json(HEADERS), json=position,
    )

    assert response.status == expected_status
    json = await response.json()
    if json.get('token'):
        json.pop('token')
    assert json == load_json(expected_response)


@pytest.mark.config(
    SELFREG_NEAREST_CITY_SUGGEST_OVERRIDES=NEAREST_CITY_OVERRIDE,
)
@pytest.mark.parametrize(
    'phone, passport_uid',
    [
        pytest.param('+70001112233', None, id='new phone'),
        pytest.param('+70001112233', '777', id='new phone, new passport'),
        pytest.param('+70002222222', None, id='old phone, without passport'),
        pytest.param('+70002222222', '777', id='old phone, new passport'),
        pytest.param('+70003333333', None, id='skip committed'),
        pytest.param('+70004444444', None, id='skip not park change'),
    ],
)
async def test_create_profile(
        taxi_selfreg,
        mockserver,
        load_json,
        mongo,
        mock_driver_profiles_create,
        phone,
        passport_uid,
):
    before_profile = await _find_profile(phone, passport_uid, mongo)
    assert not before_profile

    mock_driver_profiles_create(
        response=load_json(DRIVER_PROFILES_RESPONSE),
        phone=phone,
        passport_uid=passport_uid,
    )

    response = await taxi_selfreg.post(
        URL, headers=load_json(HEADERS), json=POSITION_MSK,
    )

    json = await response.json()
    token = json['token']

    after_profile = await _find_profile(phone, passport_uid, mongo)
    assert after_profile
    after_profile.pop('created_date')
    after_profile.pop('modified_date')
    after_profile.pop('updated_ts')
    after_profile.pop('_id')
    assert token == after_profile.pop('token')
    assert after_profile == make_expected_entry(
        expected_json=load_json(EXPECTED_NEW_PROFILE),
        phone=phone,
        passport_uid=passport_uid,
    )
    assert response.status == 200


@pytest.mark.config(
    SELFREG_NEAREST_CITY_SUGGEST_OVERRIDES={'Московская область': 'Москва'},
)
@pytest.mark.parametrize(
    'phone, passport_uid',
    [
        pytest.param('+70001111111', None, id='old phone'),
        pytest.param('+70001112233', '222', id='new phone, old passport'),
        pytest.param('+70002222222', '222', id='old phone, old passport'),
    ],
)
async def test_update_profile(
        taxi_selfreg,
        mockserver,
        load_json,
        mongo,
        mock_driver_profiles_create,
        phone,
        passport_uid,
):
    before_profile = await _find_profile(phone, passport_uid, mongo)
    assert before_profile

    mock_driver_profiles_create(
        response=load_json(DRIVER_PROFILES_RESPONSE),
        phone=phone,
        passport_uid=passport_uid,
    )

    response = await taxi_selfreg.post(
        URL, headers=load_json(HEADERS), json=POSITION_MSK,
    )

    json = await response.json()
    token = json['token']

    after_profile = await _find_profile(phone, passport_uid, mongo)
    assert after_profile
    assert after_profile.get('_id') == before_profile.get('_id')
    assert after_profile.get('city') == before_profile.get('city')
    assert after_profile.get('token') != before_profile.get('token')
    after_profile.pop('created_date')
    after_profile.pop('modified_date')
    after_profile.pop('updated_ts')
    after_profile.pop('_id')
    assert token == after_profile.pop('token')
    assert after_profile == make_expected_entry(
        expected_json=load_json(EXPECTED_UPDATED_PROFILE),
        phone=phone,
        passport_uid=passport_uid,
    )
    assert response.status == 200


@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
@pytest.mark.config(
    SELFREG_NEAREST_CITY_SUGGEST_OVERRIDES=NEAREST_CITY_OVERRIDE,
)
@pytest.mark.parametrize(
    'dp_response,fv_response,expected_response',
    [
        pytest.param(
            'driver_profiles_no_license_response.json',
            FLEET_VEHICLES_RESPONSE,
            'no_car_no_license_response.json',
            id='no license in dp',
        ),
        pytest.param(
            'driver_profiles_no_license_id_response.json',
            FLEET_VEHICLES_RESPONSE,
            'no_car_no_license_response.json',
            id='no license_pd_id in dp',
        ),
        pytest.param(
            'driver_profiles_no_license_country_response.json',
            FLEET_VEHICLES_RESPONSE,
            'no_car_no_license_response.json',
            id='no license_country in dp',
        ),
        pytest.param(
            'driver_profiles_no_license_issue_date_response.json',
            FLEET_VEHICLES_RESPONSE,
            'no_car_no_license_response.json',
            id='no license_issue_date in dp',
        ),
        pytest.param(
            'driver_profiles_no_license_expire_date_response.json',
            FLEET_VEHICLES_RESPONSE,
            'no_expire_date_response.json',
            id='no license_expire_date in dp',
        ),
        pytest.param(
            DRIVER_PROFILES_RESPONSE,
            'fleet_vehicles_no_brand_response.json',
            'no_car_response.json',
            id='no car brand in fv',
        ),
        pytest.param(
            DRIVER_PROFILES_RESPONSE,
            'fleet_vehicles_no_color_response.json',
            'no_car_response.json',
            id='no car color in fv',
        ),
        pytest.param(
            DRIVER_PROFILES_RESPONSE,
            'fleet_vehicles_no_model_response.json',
            'no_car_response.json',
            id='no car model in fv',
        ),
        pytest.param(
            DRIVER_PROFILES_RESPONSE,
            'fleet_vehicles_no_year_response.json',
            'no_car_response.json',
            id='no car year in fv',
        ),
        pytest.param(
            DRIVER_PROFILES_RESPONSE,
            'fleet_vehicles_no_number_normalized_response.json',
            'no_number_normalized_response.json',
            id='no number normalized in fv',
        ),
    ],
)
async def test_optional_fields_in_response(
        taxi_selfreg,
        mockserver,
        load_json,
        mock_driver_profiles_create,
        mock_fleet_vehicles_create,
        dp_response,
        fv_response,
        expected_response,
):
    mock_driver_profiles_create(response=load_json(dp_response))
    mock_fleet_vehicles_create(load_json(fv_response))

    response = await taxi_selfreg.post(
        URL, headers=load_json(HEADERS), json=POSITION_MSK,
    )

    assert response.status == 200
    json = await response.json()
    if json.get('token'):
        json.pop('token')
    assert json == load_json(expected_response)
