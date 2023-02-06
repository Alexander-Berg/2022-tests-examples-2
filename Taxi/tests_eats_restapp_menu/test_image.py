# pylint: disable=redefined-outer-name
PARTNER_ID = 1
PLACE_ID = 111
ORIGIN_ID = '123-456'


async def test_image_happy_path(mockserver, taxi_eats_restapp_menu):
    @mockserver.json_handler(
        r'/avatars-mds/put-eda/(?P<imagename>\w+)', regex=True,
    )
    def mock_avatars(request, imagename):
        return mockserver.make_response(
            status=200,
            json={
                'imagename': 'test_image_name',
                'group-id': 1234567,
                'meta': {'orig-format': 'jpeg'},
                'sizes': {'orig': {'width': 1600, 'height': 1200, 'path': ''}},
            },
        )

    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v1/image?place_id='
        + str(PLACE_ID)
        + '&origin_id='
        + ORIGIN_ID,
        headers={
            'X-YaEda-PartnerId': str(PARTNER_ID),
            'Content-Type': 'image/jpeg',
        },
        data='1234567890',
    )

    assert response.status_code == 200
    assert response.json() == {
        'url': ('https://eda.yandex/images/' '1234567/test_image_name.jpg'),
    }

    imagename = mock_avatars.next_call()['imagename']
    # длина uuid4
    assert len(imagename) == 32


async def test_image_avatar_400(taxi_eats_restapp_menu, mockserver):
    @mockserver.json_handler(
        r'/avatars-mds/put-eda/(?P<imagename>\w+)', regex=True,
    )
    def mock_avatars(request, imagename):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'error'},
        )

    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v1/image?place_id='
        + str(PLACE_ID)
        + '&origin_id='
        + ORIGIN_ID,
        headers={
            'X-YaEda-PartnerId': str(PARTNER_ID),
            'Content-Type': 'image/jpeg',
        },
        data='1234567890',
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Error: not upload image to avatar-mds',
    }
    imagename = mock_avatars.next_call()['imagename']
    # длина uuid4
    assert len(imagename) == 32


async def test_image_avatar_bad_ratio(taxi_eats_restapp_menu, mockserver):
    @mockserver.json_handler(
        r'/avatars-mds/put-eda/(?P<imagename>\w+)', regex=True,
    )
    def mock_avatars(request, imagename):
        return mockserver.make_response(
            status=200,
            json={
                'imagename': 'test_image_name',
                'group-id': 1234567,
                'meta': {'orig-format': 'jpeg'},
                'sizes': {'orig': {'width': 1600, 'height': 1300, 'path': ''}},
            },
        )

    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v1/image?place_id='
        + str(PLACE_ID)
        + '&origin_id='
        + ORIGIN_ID,
        headers={
            'X-YaEda-PartnerId': str(PARTNER_ID),
            'Content-Type': 'image/jpeg',
        },
        data='1234567890',
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Error: image ratio should be 4x3',
    }
    imagename = mock_avatars.next_call()['imagename']
    # длина uuid4
    assert len(imagename) == 32
