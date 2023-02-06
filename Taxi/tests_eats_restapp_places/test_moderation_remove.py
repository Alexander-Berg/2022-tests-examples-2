PARTNER_ID = 1
PLACE_ID = 42
TASK_ID = '1234567890'


async def test_moderation_remove_getz(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_moderation_remove,
):
    response = await taxi_eats_restapp_places.delete(
        '/4.0/restapp-front/places/v1/moderation'
        '?place_id={}&task_id={}'.format(PLACE_ID, TASK_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 204


async def test_moderation_remove_authorizer_403_get(
        taxi_eats_restapp_places, mock_authorizer_forbidden,
):
    response = await taxi_eats_restapp_places.delete(
        '/4.0/restapp-front/places/v1/moderation'
        '?place_id={}&task_id={}'.format(PLACE_ID, TASK_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 403
    assert response.json() == {'code': '403', 'message': 'Forbidden'}


async def test_moderation_remove_400_get(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_moderation_remove_400,
):
    response = await taxi_eats_restapp_places.delete(
        '/4.0/restapp-front/places/v1/moderation'
        '?place_id={}&task_id={}'.format(PLACE_ID, TASK_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Error remove moderation task: error',
    }


async def test_moderation_remove_404_get(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_moderation_remove_404,
):
    response = await taxi_eats_restapp_places.delete(
        '/4.0/restapp-front/places/v1/moderation'
        '?place_id={}&task_id={}'.format(PLACE_ID, TASK_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'Moderation task not found',
    }
