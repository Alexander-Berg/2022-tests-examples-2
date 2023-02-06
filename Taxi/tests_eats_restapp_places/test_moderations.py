PARTNER_ID = 1
PLACE_ID = 42


async def test_moderation_list_get(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_moderation_list,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/moderations?place_id={}'.format(
            PLACE_ID,
        ),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'context': {
                    'place_id': 1,
                    'partner_id': 2,
                    'city': 'Saint-Petersburg',
                },
                'tag': 'tag2222',
                'task_id': 'task1111',
                'status': 'process',
                'payload': [{'field': 'qqq', 'value': 'www'}],
                'targetType': 'restapp_moderation_hero',
                'reasons': [],
            },
        ],
    }


async def test_moderation_list_authorizer_400_get(
        taxi_eats_restapp_places, mock_authorizer_forbidden,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/moderations?place_id={}'.format(
            PLACE_ID,
        ),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 403
    assert response.json() == {'code': '403', 'message': 'Forbidden'}


async def test_moderation_list_400_get(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_moderation_list_400,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/moderations?place_id={}'.format(
            PLACE_ID,
        ),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Error get moderation tasks list: error',
    }
