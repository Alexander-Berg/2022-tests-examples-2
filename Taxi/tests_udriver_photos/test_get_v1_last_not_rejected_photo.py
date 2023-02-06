import pytest


ENDPOINT = '/driver-photos/v1/last-not-rejected-photo'


@pytest.mark.parametrize(
    ['park_id', 'driver_profile_id', 'url_avatar', 'url_portrait'],
    (
        pytest.param(
            'park_id_1',
            'driver_id_1',
            'mds_avatars/get-driver-photos/603/121/orig',
            'mds_avatars/get-driver-photos/603/122/orig',
            id='approved',
        ),
        pytest.param(
            'park_id_2',
            'driver_id_2',
            'mds_avatars/get-driver-photos/603/221/orig',
            'mds_avatars/get-driver-photos/603/222/orig',
            id='on_moderation',
        ),
    ),
)
async def test_ok(
        mockserver,
        taxi_udriver_photos,
        mock_unique_drivers,
        park_id,
        driver_profile_id,
        url_avatar,
        url_portrait,
):
    mock_unique_drivers(driver_profile_id)

    params = {'park_id': park_id, 'driver_profile_id': driver_profile_id}

    response = await taxi_udriver_photos.get(ENDPOINT, params=params)

    url = mockserver.base_url
    expected_response = {
        'actual_photo': {
            'avatar_url': url + url_avatar,
            'portrait_url': url + url_portrait,
        },
    }
    assert response.status == 200, response.json()
    assert response.json() == expected_response


async def test_only_unique_driver_id_param_ok(
        mockserver, taxi_udriver_photos, mock_unique_drivers,
):
    mock_unique_drivers('driver_id_1')

    params = {
        'driver_profile_id': 'driver_profile_id_1',
        'unique_driver_id': 'driver_id_1',
    }

    response = await taxi_udriver_photos.get(ENDPOINT, params=params)

    url = mockserver.base_url
    expected_response = {
        'actual_photo': {
            'avatar_url': url + 'mds_avatars/get-driver-photos/603/121/orig',
            'portrait_url': url + 'mds_avatars/get-driver-photos/603/122/orig',
        },
    }
    assert response.status == 200, response.json()
    assert response.json() == expected_response


async def test_only_rejected(taxi_udriver_photos, mock_unique_drivers):
    mock_unique_drivers('driver_id_3')

    params = {
        'park_id': 'park_id_3',
        'driver_profile_id': 'driver_profile_id_3',
    }

    response = await taxi_udriver_photos.get(ENDPOINT, params=params)

    assert response.status == 200, response.json()
    assert response.json() == {}


async def test_no_matching_unique_driver_id(
        taxi_udriver_photos, mock_unique_drivers,
):
    mock_unique_drivers(None)

    params = {'park_id': 'park_id_1', 'driver_profile_id': 'park_id_2'}

    response = await taxi_udriver_photos.get(ENDPOINT, params=params)

    expected_response = {
        'code': '404',
        'message': 'unique driver id was not found',
    }
    assert response.status == 404
    assert response.json() == expected_response


async def test_empty_params(
        mockserver, taxi_udriver_photos, mock_unique_drivers,
):
    mock_unique_drivers('driver_id_1')

    params = {'park_id': 'park_id_1'}

    response = await taxi_udriver_photos.get(ENDPOINT, params=params)

    expected_response = {
        'code': '400',
        'message': (
            'either only park_id + driver_profile_id'
            ' or only unique_driver_id must be provided'
        ),
    }
    assert response.status == 400, response.json()
    assert response.json() == expected_response


async def test_all_params(
        mockserver, taxi_udriver_photos, mock_unique_drivers,
):
    mock_unique_drivers('driver_id_1')

    params = {
        'park_id': 'park_id_1',
        'driver_profile_id': 'driver_profile_id_1',
        'unique_driver_id': 'driver_id_1',
    }

    response = await taxi_udriver_photos.get(ENDPOINT, params=params)

    expected_response = {
        'code': '400',
        'message': (
            'either only park_id + driver_profile_id'
            ' or only unique_driver_id must be provided'
        ),
    }
    assert response.status == 400, response.json()
    assert response.json() == expected_response
