import pytest

from test_taxi_driver_photos.stubs import driver_categories_response
from test_taxi_driver_photos.stubs import driver_position_response


DRIVER_ID = '54256bf766d93ee2c902dcbd'
DRIVER_ID_NOT_ADMIN_PHOTO = '34256bf766d749fb905ff442'
PARK_ID = '7f74df331eb04ad78bc2ff25ff88a8f2'
DRIVER_PROFILE_ID = 'd226462b47a340bbbd7b5cc354d9e0c0'
CAR_ID = 'f45ec058aebb4edaaf373cc59f494cc3'


@pytest.mark.config(
    DRIVER_PHOTOS_USE_LOGIC_HIGH_CLASS=True,
    DRIVER_PHOTOS_GET_TARIFFS_FROM_TRACKER=False,
)
@pytest.mark.parametrize(
    ['request_uri', 'is_premium', 'car_id', 'is_admin_photo'],
    (
        pytest.param(
            f'/driver-photos/v2/photos/?unique_driver_id={DRIVER_ID}',
            False,
            CAR_ID,
            True,
            id='Request with unique driver id',
        ),
        pytest.param(
            (
                f'/driver-photos/v2/photos/?park_id={PARK_ID}'
                f'&driver_profile_id={DRIVER_PROFILE_ID}'
            ),
            False,
            CAR_ID,
            True,
            id='Park and profile ids, not premium',
        ),
        pytest.param(
            (
                f'/driver-photos/v2/photos/?park_id={PARK_ID}'
                f'&driver_profile_id={DRIVER_PROFILE_ID}'
            ),
            True,
            CAR_ID,
            True,
            id='Park and profile ids, premium, admin photos',
        ),
        pytest.param(
            (
                f'/driver-photos/v2/photos/?park_id={PARK_ID}'
                f'&driver_profile_id={DRIVER_PROFILE_ID}'
            ),
            True,
            CAR_ID,
            False,
            id='Park and profile ids, premium, taximeter photos',
        ),
        pytest.param(
            (
                f'/driver-photos/v2/photos/?unique_driver_id={DRIVER_ID}&'
                f'park_id={PARK_ID}&driver_profile_id={DRIVER_PROFILE_ID}'
            ),
            False,
            CAR_ID,
            True,
            id='Request with all params',
        ),
    ),
)
async def test_get_driver_photo(
        web_app_client,
        load_json,
        mock_unique_drivers,
        mock_driver_profiles,
        mock_driver_categories,
        request_uri,
        is_premium,
        car_id,
        is_admin_photo,
):
    if is_admin_photo:
        mock_unique_drivers(DRIVER_ID)
    else:
        mock_unique_drivers(DRIVER_ID_NOT_ADMIN_PHOTO)
    mock_driver_profiles(car_id)
    mock_driver_categories(is_premium)

    response = await web_app_client.get(request_uri)
    if is_premium and not is_admin_photo:
        assert response.status == 404
        return
    assert response.status == 200
    content = await response.json()
    assert content == load_json('response_get_photos.json')


@pytest.mark.config(
    DRIVER_PHOTOS_USE_LOGIC_HIGH_CLASS=True,
    DRIVER_PHOTOS_GET_TARIFFS_FROM_TRACKER=True,
)
@pytest.mark.parametrize(
    ['request_uri', 'is_premium', 'car_id', 'is_admin_photo'],
    (
        pytest.param(
            f'/driver-photos/v2/photos/?unique_driver_id={DRIVER_ID}',
            False,
            CAR_ID,
            True,
            id='Request with unique driver id',
        ),
        pytest.param(
            (
                f'/driver-photos/v2/photos/?park_id={PARK_ID}'
                f'&driver_profile_id={DRIVER_PROFILE_ID}'
            ),
            False,
            CAR_ID,
            True,
            id='Park and profile ids, not premium',
        ),
        pytest.param(
            (
                f'/driver-photos/v2/photos/?park_id={PARK_ID}'
                f'&driver_profile_id={DRIVER_PROFILE_ID}'
            ),
            True,
            CAR_ID,
            True,
            id='Park and profile ids, premium, admin photos',
        ),
        pytest.param(
            (
                f'/driver-photos/v2/photos/?park_id={PARK_ID}'
                f'&driver_profile_id={DRIVER_PROFILE_ID}'
            ),
            True,
            CAR_ID,
            False,
            id='Park and profile ids, premium, taximeter photos',
        ),
        pytest.param(
            (
                f'/driver-photos/v2/photos/?unique_driver_id={DRIVER_ID}&'
                f'park_id={PARK_ID}&driver_profile_id={DRIVER_PROFILE_ID}'
            ),
            False,
            CAR_ID,
            True,
            id='Request with all params',
        ),
    ),
)
async def test_get_driver_photo_use_tracker(
        web_app_client,
        load_json,
        mock_unique_drivers,
        mock_driver_profiles,
        mock_driver_categories,
        mock,
        patch,
        request_uri,
        is_premium,
        car_id,
        is_admin_photo,
):
    if is_admin_photo:
        mock_unique_drivers(DRIVER_ID)
    else:
        mock_unique_drivers(DRIVER_ID_NOT_ADMIN_PHOTO)
    mock_driver_profiles(car_id)
    mock_driver_categories(is_premium)

    @mock
    @patch('taxi.clients.tracker.TrackerClient.driver_position')
    async def _patched_driver_position(dbid, uuid, log_extra):
        return driver_position_response()

    @mock
    @patch('taxi.clients.tracker.TrackerClient.driver_categories_by_uuid')
    async def _patched_driver_categories_by_uuid(dbid, uuid, point, log_extra):
        return driver_categories_response(is_premium)

    response = await web_app_client.get(request_uri)
    if is_premium and not is_admin_photo:
        assert response.status == 404
        return
    assert response.status == 200
    content = await response.json()
    assert content == load_json('response_get_photos.json')


@pytest.mark.config(
    DRIVER_PHOTOS_USE_LOGIC_HIGH_CLASS=True,
    DRIVER_PHOTOS_GET_TARIFFS_FROM_TRACKER=False,
)
async def test_get_driver_photo_404(web_app_client):
    response = await web_app_client.get(
        f'/photos?unique_driver_id=some_wrong_uuid',
    )
    assert response.status == 404
