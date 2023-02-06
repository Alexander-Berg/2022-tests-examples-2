# pylint: disable=too-many-lines

import pytest


EATER = {
    'id': 'some_eater',
    'uuid': 'some_uuid',
    'created_at': '2021-11-09T22:11:00+03:00',
    'updated_at': '2021-11-09T22:13:00+03:00',
}


@pytest.mark.config(EATS_EATER_META_TAGS_WHITE_LIST=['valid_tag'])
async def test_green_flow(
        # ---- fixtures ----
        mock_eats_eaters,
        mock_eats_tags,
        taxi_eats_eater_meta_web,
):
    @mock_eats_eaters('/v1/eaters/find-by-id')
    def _mock_find_eater_by_id(request):
        assert request.json['id'] == EATER['id']
        return {'eater': EATER}

    @mock_eats_tags('/v2/upload')
    def _mock_upload_tags(request):
        assert 'append' in request.json
        assert request.json['append'] == [
            {
                'entity_type': 'user_id',
                'tags': [{'name': 'valid_tag', 'entity': EATER['id']}],
            },
        ]
        return {'status': 'ok'}

    response = await taxi_eats_eater_meta_web.post(
        '/v1/eaters/tags/add',
        json={'eater_id': EATER['id'], 'tag': 'valid_tag'},
    )

    assert response.status == 200


@pytest.mark.config(EATS_EATER_META_TAGS_WHITE_LIST=['valid_tag'])
async def test_invalid_tag(
        # ---- fixtures ----
        taxi_eats_eater_meta_web,
):
    response = await taxi_eats_eater_meta_web.post(
        '/v1/eaters/tags/add',
        json={'eater_id': 'some_eater', 'tag': 'invalid_tag'},
    )

    assert response.status == 400
    data = await response.json()
    assert data['code'] == 'invalid_tag'


@pytest.mark.config(EATS_EATER_META_TAGS_WHITE_LIST=['valid_tag'])
async def test_eater_not_found(
        # ---- fixtures ----
        mockserver,
        mock_eats_eaters,
        taxi_eats_eater_meta_web,
):
    @mock_eats_eaters('/v1/eaters/find-by-id')
    def _mock_find_eater_by_id(request):
        return mockserver.make_response(
            status=404,
            json={'code': 'eater_not_found', 'message': 'Итер не найден.'},
            headers={'X-YaTaxi-Error-Code': '404'},
        )

    response = await taxi_eats_eater_meta_web.post(
        '/v1/eaters/tags/add',
        json={'eater_id': 'non-existent eater', 'tag': 'valid_tag'},
    )

    assert response.status == 400
    data = await response.json()
    assert data['code'] == 'eater_not_found'


@pytest.mark.config(EATS_EATER_META_TAGS_WHITE_LIST=['valid_tag'])
async def test_eats_eaters_service_error(
        # ---- fixtures ----
        mockserver,
        mock_eats_eaters,
        taxi_eats_eater_meta_web,
):
    @mock_eats_eaters('/v1/eaters/find-by-id')
    def _mock_find_eater_by_id(request):
        return mockserver.make_response(status=500)

    response = await taxi_eats_eater_meta_web.post(
        '/v1/eaters/tags/add',
        json={'eater_id': 'some_eater', 'tag': 'valid_tag'},
    )

    assert response.status == 500
    data = await response.json()
    assert data['code'] == 'eats_eaters_service_error'


@pytest.mark.config(EATS_EATER_META_TAGS_WHITE_LIST=['valid_tag'])
async def test_eats_tags_service_error(
        # ---- fixtures ----
        mockserver,
        mock_eats_eaters,
        mock_eats_tags,
        taxi_eats_eater_meta_web,
):
    @mock_eats_eaters('/v1/eaters/find-by-id')
    def _mock_find_eater_by_id(request):
        assert request.json['id'] == EATER['id']
        return {'eater': EATER}

    @mock_eats_tags('/v2/upload')
    def _mock_upload_tags(request):
        return mockserver.make_response(status=500)

    response = await taxi_eats_eater_meta_web.post(
        '/v1/eaters/tags/add',
        json={'eater_id': 'some_eater', 'tag': 'valid_tag'},
    )

    assert response.status == 500
    data = await response.json()
    assert data['code'] == 'eats_tags_service_error'
