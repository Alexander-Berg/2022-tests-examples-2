# pylint: disable=redefined-outer-name
import pytest
PARTNER_ID = 1
PARTNER_ID_2 = 2
PLACE_ID = 42
PLACE_ID_2 = 43
BRAND = 3
CONFIG = {
    'hero_off_premoderation_places': [PLACE_ID],
    'hero_off_premoderation_brands': [BRAND],
    'hero_off_premoderation_partners': [PARTNER_ID_2],
}


@pytest.fixture
def mock_eats_moderation_ml_off(mockserver, request):
    @mockserver.json_handler('eats-moderation/moderation/v1/task')
    def _mock_authorizer(request):
        assert request.json == {
            'context': '{"place_id":"42","partner_id":"1","city":"Москва"}',
            'payload': (
                '{"picture":"test_image_name.jpg",'
                '"identity":"1234567/test_image_name",'
                '"photo_url":"http://avatars.mds.yandex.net/get-eda'
                '/1234567/test_image_name/1600x1200",'
                '"current_identity":"fake_identity42",'
                '"send_to_ml":false}'
            ),
            'queue': 'restapp_moderation_hero',
            'scope': 'eda',
        }
        return mockserver.make_response(status=200, json={'task_id': '12qwas'})


@pytest.fixture
def mock_eats_moderation_ml_off_br(mockserver, request):
    @mockserver.json_handler('eats-moderation/moderation/v1/task')
    def _mock_authorizer(request):
        assert request.json == {
            'context': '{"place_id":"43","partner_id":"1","city":"Москва"}',
            'payload': (
                '{"picture":"test_image_name.jpg",'
                '"identity":"1234567/test_image_name",'
                '"photo_url":"http://avatars.mds.yandex.net/get-eda'
                '/1234567/test_image_name/1600x1200",'
                '"current_identity":"fake_identity43",'
                '"send_to_ml":false}'
            ),
            'queue': 'restapp_moderation_hero',
            'scope': 'eda',
        }
        return mockserver.make_response(status=200, json={'task_id': '12qwas'})


@pytest.fixture
def mock_eats_moderation_ml_off_pa(mockserver, request):
    @mockserver.json_handler('eats-moderation/moderation/v1/task')
    def _mock_authorizer(request):
        assert request.json == {
            'context': '{"place_id":"42","partner_id":"2","city":"Москва"}',
            'payload': (
                '{"picture":"test_image_name.jpg",'
                '"identity":"1234567/test_image_name",'
                '"photo_url":"http://avatars.mds.yandex.net/get-eda'
                '/1234567/test_image_name/1600x1200",'
                '"current_identity":"fake_identity42",'
                '"send_to_ml":false}'
            ),
            'queue': 'restapp_moderation_hero',
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


@pytest.fixture
def mock_eats_catalog_storage(mockserver, request):
    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    def _mock_eats_catalog_storage(request):
        assert request.json['projection'] == ['address', 'brand']
        assert request.json['place_ids'] in [[42], [43]]
        if request.json['place_ids'][0] == 43:
            return mockserver.make_response(
                status=200,
                json={
                    'places': [
                        {
                            'id': request.json['place_ids'][0],
                            'revision_id': 0,
                            'updated_at': '1970-01-02T00:00:00.000Z',
                            'address': {'city': 'Москва', 'short': 'qwerty'},
                            'brand': {
                                'id': 3,
                                'slug': 'brand',
                                'name': 'brandname',
                                'picture_scale_type': 'aspect_fit',
                            },
                        },
                    ],
                    'not_found_place_ids': [],
                },
            )
        return mockserver.make_response(
            status=200,
            json={
                'places': [
                    {
                        'id': request.json['place_ids'][0],
                        'revision_id': 0,
                        'updated_at': '1970-01-02T00:00:00.000Z',
                        'address': {'city': 'Москва', 'short': 'qwerty'},
                    },
                ],
                'not_found_place_ids': [],
            },
        )


@pytest.fixture
def mock_eats_catalog_storage_404(mockserver, request):
    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    def _mock_eats_catalog_storage_400(request):
        assert request.json == {
            'place_ids': [42],
            'projection': ['address', 'brand'],
        }
        return mockserver.make_response(
            status=200, json={'places': [], 'not_found_place_ids': [42]},
        )


async def test_set_hero_photo_happy_path(
        mockserver,
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_catalog_storage,
        mock_eats_moderation,
        mock_avatar_mds,
):
    @mockserver.json_handler(
        r'/avatars-mds/put-eda/(?P<imagename>\w+)', regex=True,
    )
    def _mock_authorizer(request, imagename):
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
        '/4.0/restapp-front/places/v1/set-hero-photo?place_id={}'.format(
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
        'urn': '1234567/test_image_name',
        'task_id': '12qwas',
    }

    imagename = _mock_authorizer.next_call()['imagename']
    # длина uuid4
    assert len(imagename) == 32


async def test_set_hero_photo_bad_ratio(
        mockserver,
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_catalog_storage,
        mock_eats_moderation,
        mock_avatar_mds,
):
    @mockserver.json_handler(
        r'/avatars-mds/put-eda/(?P<imagename>\w+)', regex=True,
    )
    def _mock_authorizer(request, imagename):
        return mockserver.make_response(
            status=200,
            json={
                'imagename': 'test_image_name',
                'group-id': 1234567,
                'meta': {'orig-format': 'jpeg'},
                'sizes': {'orig': {'width': 1600, 'height': 1300, 'path': ''}},
            },
        )

    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/set-hero-photo?place_id={}'.format(
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
        'message': 'Error: image ratio should be 4x3',
    }

    imagename = _mock_authorizer.next_call()['imagename']
    # длина uuid4
    assert len(imagename) == 32


@pytest.mark.config(EATS_RESTAPP_PLACES_OFF_PREMODERATION=CONFIG)
async def test_set_hero_photo_ml_off_place(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_avatar_mds,
        mock_eats_catalog_storage,
        mock_eats_moderation_ml_off,
):

    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/set-hero-photo?place_id={}'.format(
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
        'urn': '1234567/test_image_name',
        'task_id': '12qwas',
    }


@pytest.mark.config(EATS_RESTAPP_PLACES_OFF_PREMODERATION=CONFIG)
async def test_set_hero_photo_ml_off_brand(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_avatar_mds,
        mock_eats_catalog_storage,
        mock_eats_moderation_ml_off_br,
):

    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/set-hero-photo?place_id={}'.format(
            PLACE_ID_2,
        ),
        headers={
            'X-YaEda-PartnerId': str(PARTNER_ID),
            'Content-Type': 'image/jpeg',
        },
        data='1234567890',
    )

    assert response.status_code == 201
    assert response.json() == {
        'urn': '1234567/test_image_name',
        'task_id': '12qwas',
    }


@pytest.mark.config(EATS_RESTAPP_PLACES_OFF_PREMODERATION=CONFIG)
async def test_set_hero_photo_ml_off_partner(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_avatar_mds,
        mock_eats_catalog_storage,
        mock_eats_moderation_ml_off_pa,
):

    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/set-hero-photo?place_id={}'.format(
            PLACE_ID,
        ),
        headers={
            'X-YaEda-PartnerId': str(PARTNER_ID_2),
            'Content-Type': 'image/jpeg',
        },
        data='1234567890',
    )

    assert response.status_code == 201
    assert response.json() == {
        'urn': '1234567/test_image_name',
        'task_id': '12qwas',
    }


async def test_set_hero_photo_forbinden(
        taxi_eats_restapp_places, mock_authorizer_forbidden,
):

    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/set-hero-photo?place_id={}'.format(
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


async def test_set_hero_photo_400(
        taxi_eats_restapp_places, mock_authorizer_400,
):

    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/set-hero-photo?place_id={}'.format(
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


async def test_set_hero_photo_avatar_400(
        taxi_eats_restapp_places, mock_authorizer_allowed, mock_avatar_mds_400,
):

    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/set-hero-photo?place_id={}'.format(
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


async def test_set_hero_photo_catalog_storage_404(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_avatar_mds,
        mock_eats_catalog_storage_404,
        mock_eats_moderation_no_info,
):

    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/set-hero-photo?place_id={}'.format(
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
        'urn': '1234567/test_image_name',
        'task_id': '12qwas',
    }


async def test_set_hero_photo_moderation_400(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_avatar_mds,
        mock_eats_catalog_storage,
        mock_eats_moderation_400,
):

    response = await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/set-hero-photo?place_id={}'.format(
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
        'message': 'Error: not added moderation task ',
    }
