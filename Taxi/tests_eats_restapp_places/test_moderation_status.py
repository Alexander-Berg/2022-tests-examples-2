PARTNER_ID = 1
PLACE_ID = 42
PLACE_ID2 = 43


async def test_moderation_status_get(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_moderation_count,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/moderation/status?place_id={},{}'.format(
            PLACE_ID, PLACE_ID2,
        ),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 200
    assert response.json() == {
        'moderation_status': [
            {
                'place_id': 42,
                'reject': {'place_hero_photo': 2, 'total': 2},
                'total': 2,
            },
            {
                'place_id': 43,
                'reject': {'place_hero_photo': 3, 'total': 3},
                'total': 3,
            },
        ],
        'total': 5,
    }


async def test_moderation_status_authorizer_400_get(
        taxi_eats_restapp_places, mock_authorizer_forbidden,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/moderation/status?place_id={},{}'.format(
            PLACE_ID, PLACE_ID2,
        ),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 403
    assert response.json() == {'code': '403', 'message': 'Forbidden'}


async def test_moderation_status_400_get(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_moderation_count_400,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/moderation/status?place_id={},{}'.format(
            PLACE_ID, PLACE_ID2,
        ),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Error get tasks count:error',
    }
