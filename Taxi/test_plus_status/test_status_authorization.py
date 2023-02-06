async def test_autorization_403(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_403,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/status',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [1, 2, 3, 4]},
    )

    assert response.status_code == 403
    response = response.json()
    assert response == {'code': '403', 'message': 'Permission Denied'}


async def test_autorization_400(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_400,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/status',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [1, 2, 3, 4]},
    )

    assert response.status_code == 400
    response = response.json()
    assert response == {'code': '400', 'message': 'Bad Request'}


async def test_autorization_200(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/status',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [17, 14]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'places': [
            {
                'place_id': 17,
                'statuses': [
                    {
                        'status': 'can_not_be_activated',
                        'reasons': [
                            {
                                'code': 'region_without_plus',
                                'message': (
                                    'В вашем регионе '
                                    'не действует Яндекс Плюс.'
                                ),
                            },
                            {
                                'code': 'no_rating',
                                'message': (
                                    'У вашего ресторана нет рейтинга. '
                                    'Чтобы стать партнером Плюса, '
                                    'нужен рейтинг от 4.'
                                ),
                            },
                        ],
                    },
                ],
            },
            {
                'place_id': 14,
                'statuses': [
                    {
                        'status': 'can_not_be_activated',
                        'reasons': [
                            {
                                'code': 'region_without_plus',
                                'message': (
                                    'В вашем регионе '
                                    'не действует Яндекс Плюс.'
                                ),
                            },
                            {
                                'code': 'no_rating',
                                'message': (
                                    'У вашего ресторана нет рейтинга. '
                                    'Чтобы стать партнером Плюса, '
                                    'нужен рейтинг от 4.'
                                ),
                            },
                        ],
                    },
                ],
            },
        ],
    }
