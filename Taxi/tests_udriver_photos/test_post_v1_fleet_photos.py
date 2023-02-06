from testsuite.utils import ordered_object


ENDPOINT = '/driver-photos/v1/fleet/photos'


async def test_one_driver_photo(mockserver, taxi_udriver_photos):
    request = {'unique_driver_ids': ['driver_id_1']}

    url = mockserver.base_url

    expected_response = {
        'actual_photos': [
            {
                'actual_photo': {
                    'avatar_url': (
                        url + 'mds_avatars/get-driver-photos/603/121/orig'
                    ),
                    'portrait_url': (
                        url + 'mds_avatars/get-driver-photos/603/122/orig'
                    ),
                },
                'unique_driver_id': 'driver_id_1',
            },
        ],
    }

    response = await taxi_udriver_photos.post(ENDPOINT, json=request)

    assert response.status_code == 200, response.text
    assert response.json() == expected_response


async def test_two_driver_photos(mockserver, taxi_udriver_photos):
    request = {'unique_driver_ids': ['driver_id_1', 'driver_id_2']}

    url = mockserver.base_url

    expected_response = {
        'actual_photos': [
            {
                'actual_photo': {
                    'avatar_url': (
                        url + 'mds_avatars/get-driver-photos/603/121/orig'
                    ),
                    'portrait_url': (
                        url + 'mds_avatars/get-driver-photos/603/122/orig'
                    ),
                },
                'unique_driver_id': 'driver_id_1',
            },
            {
                'actual_photo': {
                    'avatar_url': (
                        url + 'mds_avatars/get-driver-photos/603/221/orig'
                    ),
                    'portrait_url': (
                        url + 'mds_avatars/get-driver-photos/603/222/orig'
                    ),
                },
                'unique_driver_id': 'driver_id_2',
            },
        ],
    }

    response = await taxi_udriver_photos.post(ENDPOINT, json=request)

    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(), expected_response, ['actual_photos'],
    )


async def test_not_found_photos(mockserver, taxi_udriver_photos):
    request = {'unique_driver_ids': ['driver_id_3', 'driver_id_unknown']}

    expected_response = {'actual_photos': []}

    response = await taxi_udriver_photos.post(ENDPOINT, json=request)

    assert response.status_code == 200, response.text
    assert response.json() == expected_response
