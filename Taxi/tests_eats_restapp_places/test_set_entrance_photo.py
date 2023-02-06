# pylint: disable=redefined-outer-name
import pytest
PARTNER_ID = 1
PLACE_ID = 42


@pytest.fixture
def mock_eats_moderation(mockserver, request):
    @mockserver.json_handler('eats-moderation/moderation/v1/task')
    def _mock_authorizer(request):
        assert request.json == {
            'context': '{"place_id":"42","partner_id":"1"}',
            'payload': (
                '{"photo_url":"http://avatars.mds.yandex.net/get-eda'
                '/1234567/test_image_name/1600x1200"}'
            ),
            'queue': 'restapp_moderation_entrance',
            'scope': 'eda',
        }
        return mockserver.make_response(status=200, json={'task_id': '12qwas'})


@pytest.fixture
def mock_eats_moderation_400(mockserver, request):
    @mockserver.json_handler('eats-moderation/moderation/v1/task')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'error'},
        )


async def test_set_entrance_photo_happy_path(
        mockserver,
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_moderation,
        mock_avatar_mds,
):
    @mockserver.json_handler(
        r'/avatars-mds/put-eda/(?P<imagename>\w+)', regex=True,
    )
    def _mock_avatar(request, imagename):
        return mockserver.make_response(
            status=200,
            json={
                'imagename': 'test_image_name',
                'group-id': 1234567,
                'meta': {'orig-format': 'jpeg'},
                'sizes': {'orig': {'width': 1600, 'height': 1200, 'path': ''}},
            },
        )

    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/entrance-photo?place_id={}'.format(
            PLACE_ID,
        ),
        headers={
            'X-YaEda-PartnerId': str(PARTNER_ID),
            'Content-Type': 'image/jpeg',
        },
        data='1234567890',
    )

    assert response.status_code == 201
    assert response.json() == {
        'url': (
            'http://avatars.mds.yandex.net/get-eda/1234567/test_image_name'
            '/1600x1200'
        ),
        'task_id': '12qwas',
    }

    imagename = _mock_avatar.next_call()['imagename']
    # длина uuid4
    assert len(imagename) == 32

    response2 = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/entrance-photo?place_id={}'.format(
            PLACE_ID,
        ),
        headers={
            'X-YaEda-PartnerId': str(PARTNER_ID),
            'Content-Type': 'image/jpeg',
        },
        data='1234567890',
    )

    assert response2.status_code == 200
    assert response2.json() == {
        'entrances': [
            {
                'url': (
                    'http://avatars.mds.yandex.net/get-eda/1234567/'
                    'test_image_name/1600x1200'
                ),
                'status': 'uploaded',
                'use_entrance_photo': True,
                'weight': 50,
            },
        ],
    }

    response3 = await taxi_eats_restapp_places.delete(
        '/4.0/restapp-front/places/v1/entrance-photo?place_id={}'.format(
            PLACE_ID,
        ),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )
    assert response3.status_code == 204


async def test_set_entrance_photo_forbinden(
        taxi_eats_restapp_places, mock_authorizer_forbidden,
):

    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/entrance-photo?place_id={}'.format(
            PLACE_ID,
        ),
        headers={
            'X-YaEda-PartnerId': str(PARTNER_ID),
            'Content-Type': 'image/jpeg',
        },
        data='1234567890',
    )

    assert response.status_code == 403
    assert response.json() == {'code': '403', 'message': 'Forbidden'}

    response2 = await taxi_eats_restapp_places.delete(
        '/4.0/restapp-front/places/v1/entrance-photo?place_id={}'.format(
            PLACE_ID,
        ),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )
    assert response2.status_code == 403
    assert response2.json() == {'code': '403', 'message': 'Forbidden'}


async def test_set_entrance_photo_400(
        taxi_eats_restapp_places, mock_authorizer_400,
):

    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/entrance-photo?place_id={}'.format(
            PLACE_ID,
        ),
        headers={
            'X-YaEda-PartnerId': str(PARTNER_ID),
            'Content-Type': 'image/jpeg',
        },
        data='1234567890',
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Пользователь не найден',
    }

    response2 = await taxi_eats_restapp_places.delete(
        '/4.0/restapp-front/places/v1/entrance-photo?place_id={}'.format(
            PLACE_ID,
        ),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )
    assert response2.status_code == 400
    assert response2.json() == {
        'code': '400',
        'message': 'Пользователь не найден',
    }


async def test_set_entrance_photo_avatar_400(
        taxi_eats_restapp_places, mock_authorizer_allowed, mock_avatar_mds_400,
):

    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/entrance-photo?place_id={}'.format(
            PLACE_ID,
        ),
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


async def test_set_entrance_photo_moderation_400(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_avatar_mds,
        mock_eats_moderation_400,
):

    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/entrance-photo?place_id={}'.format(
            PLACE_ID,
        ),
        headers={
            'X-YaEda-PartnerId': str(PARTNER_ID),
            'Content-Type': 'image/jpeg',
        },
        data='1234567890',
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Error: not added moderation task',
    }
