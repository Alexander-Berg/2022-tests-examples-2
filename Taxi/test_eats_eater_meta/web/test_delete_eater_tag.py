# pylint: disable=too-many-lines


EATER = {
    'id': 'some_eater',
    'uuid': 'some_uuid',
    'created_at': '2021-11-09T22:11:00+03:00',
    'updated_at': '2021-11-09T22:13:00+03:00',
}


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
        assert 'remove' in request.json
        assert request.json['remove'] == [
            {
                'entity_type': 'user_id',
                'tags': [{'name': 'valid_tag', 'entity': EATER['id']}],
            },
        ]
        return {'status': 'ok'}

    response = await taxi_eats_eater_meta_web.post(
        '/v1/eaters/tags/delete',
        json={'eater_id': EATER['id'], 'tag': 'valid_tag'},
    )

    assert response.status == 200


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
        '/v1/eaters/tags/delete',
        json={'eater_id': 'non-existent eater', 'tag': 'valid_tag'},
    )

    assert response.status == 400
    data = await response.json()
    assert data['code'] == 'eater_not_found'


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
        '/v1/eaters/tags/delete',
        json={'eater_id': 'some_eater', 'tag': 'valid_tag'},
    )

    assert response.status == 500
    data = await response.json()
    assert data['code'] == 'eats_eaters_service_error'


async def test_eats_tags_service_error(
        # ---- fixtures ----
        mockserver,
        mock_eats_eaters,
        mock_eats_tags,
        taxi_eats_eater_meta_web,
):
    @mock_eats_eaters('/v1/eaters/find-by-id')
    def _mock_find_eaters_by_phone_id(request):
        assert request.json['id'] == EATER['id']
        return {'eater': EATER}

    @mock_eats_tags('/v2/upload')
    def _mock_upload_tags(request):
        return mockserver.make_response(status=500)

    response = await taxi_eats_eater_meta_web.post(
        '/v1/eaters/tags/delete',
        json={'eater_id': 'some_eater', 'tag': 'valid_tag'},
    )

    assert response.status == 500
    data = await response.json()
    assert data['code'] == 'eats_tags_service_error'
