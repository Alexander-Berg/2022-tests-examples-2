PARTNER_ID = 2
PLACE_ID = 1
TASK_ID = '1234567890'


async def test_moderation_get(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_moderation_get,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/moderation'
        '?place_id={}&task_id={}'.format(PLACE_ID, TASK_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 200
    assert response.json() == {
        'context': {
            'place_id': 1,
            'partner_id': 2,
            'city': 'Saint-Petersburg',
        },
        'payload': [{'field': 'qqq', 'value': 'www'}],
        'status': 'process',
        'tag': 'tag2222',
        'task_id': 'task1111',
        'targetType': 'restapp_moderation_hero',
        'reasons': [],
    }


async def test_moderation_authorizer_403_get(
        taxi_eats_restapp_places, mock_authorizer_forbidden,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/moderation'
        '?place_id={}&task_id={}'.format(PLACE_ID, TASK_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 403
    assert response.json() == {'code': '403', 'message': 'Forbidden'}


async def test_moderation_400_get(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_moderation_get_400,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/moderation'
        '?place_id={}&task_id={}'.format(PLACE_ID, TASK_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Error get moderation task status: error',
    }


async def test_moderation_404_get(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_moderation_get_404,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/moderation'
        '?place_id={}&task_id={}'.format(PLACE_ID, TASK_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'Moderation task not found',
    }
