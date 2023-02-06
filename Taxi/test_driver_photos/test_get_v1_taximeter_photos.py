import pytest


DRIVER_ID = '54256bf766d93ee2c902dcbd'
DRIVER_ID_NOT_APPROVED_PHOTO = '34256bf766d749fb905ff000'
PARK_ID = '7f74df331eb04ad78bc2ff25ff88a8f2'
DRIVER_PROFILE_ID = 'd226462b47a340bbbd7b5cc354d9e0c0'
CAR_ID = 'f45ec058aebb4edaaf373cc59f494cc3'

_PARK_ID = 'park_2'
_DRIVER_PROFILE_ID = 'driver_profile_2'


@pytest.mark.config(
    DRIVER_PHOTOS_USE_LOGIC_HIGH_CLASS=True,
    DRIVER_PHOTOS_GET_TARIFFS_FROM_TRACKER=False,
)
@pytest.mark.parametrize(
    [
        'park_id',
        'driver_profile_id',
        'unique_driver_id',
        'return_code',
        'is_premium',
        'expected_response',
    ],
    (
        pytest.param(
            _PARK_ID,
            _DRIVER_PROFILE_ID,
            DRIVER_ID,
            200,
            False,
            'response_get_photos.json',
            id='existing_unique_driver_id',
        ),
        pytest.param(
            _PARK_ID,
            _DRIVER_PROFILE_ID,
            DRIVER_ID,
            200,
            True,
            'response_get_photos.json',
            id='Premium tariff, admin photos',
        ),
        pytest.param(
            _PARK_ID,
            _DRIVER_PROFILE_ID,
            '34256bf766d749fb905ff442',
            404,
            True,
            None,
            id='Premium tariff, taximeter photos',
        ),
        pytest.param(
            _PARK_ID,
            _DRIVER_PROFILE_ID,
            '34256bf766d749fb905ff442',
            200,
            True,
            'expected_responses/driver_2_premium_check_disable.json',
            id='Premium tariff, taximeter photos, premium check disable',
            marks=pytest.mark.config(DRIVER_PHOTOS_USE_PREMIUM_CHECK=False),
        ),
        pytest.param(
            _PARK_ID,
            _DRIVER_PROFILE_ID,
            DRIVER_ID_NOT_APPROVED_PHOTO,
            200,
            False,
            'response_get_photos_not_approved.json',
            id='Not premium tariff, not approved photos',
        ),
        pytest.param(
            'WRONG_PARK_ID',
            'WRONG_DRIVER_PROFILE_ID',
            DRIVER_ID_NOT_APPROVED_PHOTO,
            404,
            False,
            None,
            id='Not premium tariff, not approved photos, wrong park+profile',
        ),
        pytest.param(
            _PARK_ID,
            _DRIVER_PROFILE_ID,
            None,
            404,
            False,
            None,
            id='no_matching_unique_driver_id',
        ),
        pytest.param(
            _PARK_ID,
            _DRIVER_PROFILE_ID,
            '000000f766d93ee2c9000000',  # not set in pg_driver_photos.sql
            404,
            False,
            None,
            id='no_photos_for_unique_driver_id',
        ),
        pytest.param(
            None,
            _DRIVER_PROFILE_ID,
            None,
            400,
            False,
            None,
            id='missing_park_id',
        ),
        pytest.param(
            _PARK_ID,
            None,
            None,
            400,
            False,
            None,
            id='missing_driver_profile_id',
        ),
        pytest.param(
            'park_3',
            'driver_profile_3',
            'unique_driver_3',
            200,
            False,
            'expected_responses/driver_3_park_and_profile.json',
            id='Last photos not approved with correct park and profile ids',
        ),
        pytest.param(
            'WRONG_PARK_ID',
            'WRONG_DRIVER_ID',
            'unique_driver_3',
            200,
            False,
            'expected_responses/driver_3_unique_driver_id_only.json',
            id='Last photos not approved with only correct unique driver id',
        ),
        pytest.param(
            'park_4',
            'driver_profile_4',
            'unique_driver_4',
            200,
            False,
            'expected_responses/driver_4_any.json',
            id='Has new photos; older photos have priority admin',
        ),
        pytest.param(
            'WRONG_PARK_ID',
            'WRONG_DRIVER_ID',
            'unique_driver_4',
            200,
            False,
            'expected_responses/driver_4_any.json',
            id='Has new photos wrong ids; older photos have priority admin',
        ),
    ),
)
async def test_get_taximeter_driver_photo(
        web_app_client,
        mock_unique_drivers,
        mock_driver_profiles,
        mock_driver_categories,
        load_json,
        park_id,
        driver_profile_id,
        unique_driver_id,
        return_code,
        is_premium,
        expected_response,
):
    mock_unique_drivers(unique_driver_id)
    mock_driver_profiles(CAR_ID)
    mock_driver_categories(is_premium)
    params = {'park_id': park_id, 'driver_profile_id': driver_profile_id}
    params = {k: v for k, v in params.items() if v is not None}
    target_url = '/driver-photos/v1/taximeter-photos/'
    response = await web_app_client.get(target_url, params=params)
    assert response.status == return_code
    if response.status != 200:
        return
    content = await response.json()
    assert content == load_json(expected_response)


@pytest.mark.config(
    DRIVER_PHOTOS_USE_LOGIC_HIGH_CLASS=True,
    DRIVER_PHOTOS_GET_TARIFFS_FROM_TRACKER=False,
)
@pytest.mark.parametrize(
    ['is_parks_error', 'is_categories_error'], ((True, False), (False, True)),
)
async def test_get_taximeter_photo_outer_service_500(
        web_app_client,
        mock_unique_drivers,
        mock_driver_profiles,
        mock_driver_categories,
        is_parks_error,
        is_categories_error,
):
    mock_unique_drivers(DRIVER_ID)
    mock_driver_profiles(CAR_ID, is_parks_error)
    mock_driver_categories(True, is_categories_error)

    response = await web_app_client.get(
        f'/driver-photos/v1/taximeter-photos/?park_id={PARK_ID}'
        f'&driver_profile_id={DRIVER_PROFILE_ID}',
    )
    assert response.status == 404
