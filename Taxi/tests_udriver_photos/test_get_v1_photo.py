ENDPOINT = '/driver-photos/v1/photo'


async def test_approved(mockserver, taxi_udriver_photos, mock_unique_drivers):
    mock_unique_drivers('driver_id_1')

    params = {
        'park_id': 'park_id_1',
        'driver_profile_id': 'driver_id_1',
        'moderated_only': True,
    }
    response = await taxi_udriver_photos.get(ENDPOINT, params=params)

    expected_response = {
        'actual_photo': {
            'avatar_url': (
                mockserver.base_url
                + 'mds_avatars/get-driver-photos/603/121/orig'
            ),
            'portrait_url': (
                mockserver.base_url
                + 'mds_avatars/get-driver-photos/603/122/orig'
            ),
        },
    }

    assert response.status == 200, response.json()
    assert response.json() == expected_response

    params = {
        'park_id': 'park_id_1',
        'driver_profile_id': 'driver_id_1',
        'moderated_only': False,
    }
    response = await taxi_udriver_photos.get(ENDPOINT, params=params)

    assert response.status == 200, response.json()
    assert response.json() == expected_response


async def test_on_moderation(
        mockserver, taxi_udriver_photos, mock_unique_drivers,
):
    mock_unique_drivers('driver_id_2')

    params = {
        'park_id': 'park_id_2',
        'driver_profile_id': 'driver_id_2',
        'moderated_only': True,
    }
    response = await taxi_udriver_photos.get(ENDPOINT, params=params)

    expected_response = {
        'actual_photo': {
            'avatar_url': (
                mockserver.base_url
                + 'mds_avatars/get-driver-photos/603/221/orig'
            ),
            'portrait_url': (
                mockserver.base_url
                + 'mds_avatars/get-driver-photos/603/222/orig'
            ),
        },
    }

    assert response.status == 200, response.json()
    assert response.json() == {}

    params = {
        'park_id': 'park_id_2',
        'driver_profile_id': 'driver_id_2',
        'moderated_only': False,
    }
    response = await taxi_udriver_photos.get(ENDPOINT, params=params)

    assert response.status == 200, response.json()
    assert response.json() == expected_response


async def test_only_unique_driver_id_param_ok(
        mockserver, taxi_udriver_photos, mock_unique_drivers,
):
    mock_unique_drivers('driver_id_1')

    params = {
        'driver_profile_id': 'driver_profile_id_1',
        'unique_driver_id': 'driver_id_1',
        'moderated_only': True,
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
        'moderated_only': False,
    }

    response = await taxi_udriver_photos.get(ENDPOINT, params=params)

    assert response.status == 200, response.json()
    assert response.json() == {}


async def test_no_matching_unique_driver_id(
        taxi_udriver_photos, mock_unique_drivers,
):
    mock_unique_drivers(None)

    params = {
        'park_id': 'park_id_1',
        'driver_profile_id': 'park_id_2',
        'moderated_only': True,
    }

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
