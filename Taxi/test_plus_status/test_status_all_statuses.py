import pytest


@pytest.mark.config(
    EATS_RESTAPP_PROMO_AVAILABLE_STATUS_SETTINGS={
        'enabled': False,
        'reason_message': {'code': 'region_without_plus', 'message': ''},
    },
)
@pytest.mark.config(
    EATS_RESTAPP_PROMO_REASON_MESSAGE={
        'low_rating': (
            'Рейтинг ресторана: {}.'
            ' Чтобы стать партнером Плюса, '
            'нужен рейтинг от {}.'
        ),
        'no_rating': (
            'У вашего ресторана нет рейтинга. '
            'Чтобы стать партнером Плюса, '
            'нужен рейтинг от {}.'
        ),
        'few_ratings': (
            'У вашего ресторана мало оценок. '
            'Чтобы стать партнером Плюса, '
            'нужно больше оценок и нужен '
            'рейтинг от {}.'
        ),
        'region_without_plus': (
            'В вашем регионе не' ' действует Яндекс Плюс.'
        ),
        'excluded_place': (
            'Для подключения к Яндекс Плюс'
            ' обратитесь к вашему'
            ' аккаунт-менеджеру.'
        ),
    },
)
@pytest.mark.config(
    EATS_RESTAPP_PROMO_PLUS_ACTIVATE_CONDITIONS={
        'min_rating': 4.0,
        'excluded_place_ids': [9, 10],
    },
)
@pytest.mark.now('2021-08-12T17:38:00.00')
@pytest.mark.eats_catalog_storage_cache(
    file='eats_catalog_storage_cache_data.json',
)
async def test_all_statuses_in_one_response(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/status',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [1, 2, 3, 4, 5, 6, 7, 8, 9]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'places': [
            {
                'place_id': 1,
                'statuses': [
                    {
                        'status': 'active',
                        'value': '5',
                        'starts': '2020-11-25T15:43:00+00:00',
                    },
                ],
            },
            {
                'place_id': 2,
                'statuses': [
                    {
                        'status': 'active',
                        'value': '6',
                        'starts': '2020-11-25T15:43:00+00:00',
                    },
                    {
                        'status': 'wait_to_start',
                        'value': '7',
                        'starts': '2022-11-25T15:43:00+00:00',
                    },
                ],
            },
            {
                'place_id': 3,
                'statuses': [
                    {
                        'starts': '2022-09-20T15:43:00+00:00',
                        'status': 'wait_to_start',
                        'value': '3',
                    },
                ],
            },
            {
                'place_id': 4,
                'statuses': [
                    {
                        'starts': '2021-09-20T18:43:00+00:00',
                        'status': 'activating',
                        'value': '10',
                    },
                ],
            },
            {
                'place_id': 5,
                'statuses': [
                    {
                        'starts': '2021-09-20T18:43:00+00:00',
                        'status': 'deactivating',
                        'value': '6',
                    },
                ],
            },
            {
                'place_id': 6,
                'statuses': [
                    {
                        'reasons': [
                            {
                                'code': 'region_without_plus',
                                'message': (
                                    'В вашем регионе '
                                    'не действует Яндекс Плюс.'
                                ),
                            },
                        ],
                        'status': 'can_not_be_activated',
                    },
                ],
            },
            {'place_id': 7, 'statuses': [{'status': 'can_be_activated'}]},
            {
                'place_id': 8,
                'statuses': [
                    {
                        'status': 'can_not_be_activated',
                        'reasons': [
                            {
                                'code': 'low_rating',
                                'message': (
                                    'Рейтинг ресторана: 2.9. '
                                    'Чтобы стать партнером Плюса, '
                                    'нужен рейтинг от 4.'
                                ),
                            },
                        ],
                    },
                ],
            },
            {
                'place_id': 9,
                'statuses': [
                    {
                        'reasons': [
                            {
                                'code': 'excluded_place',
                                'message': (
                                    'Для подключения к Яндекс Плюс '
                                    'обратитесь к вашему '
                                    'аккаунт-менеджеру.'
                                ),
                            },
                            {
                                'code': 'region_without_plus',
                                'message': (
                                    'В вашем регионе '
                                    'не действует Яндекс Плюс.'
                                ),
                            },
                            {
                                'code': 'low_rating',
                                'message': (
                                    'Рейтинг ресторана: 1.9. '
                                    'Чтобы стать партнером Плюса, '
                                    'нужен рейтинг от 4.'
                                ),
                            },
                        ],
                        'status': 'can_not_be_activated',
                    },
                ],
            },
        ],
    }


@pytest.mark.now('2021-08-12T17:38:00.00')
@pytest.mark.eats_catalog_storage_cache(
    file='eats_catalog_storage_cache_data.json',
)
async def test_all_statuses_in_one_response_config_enabled(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/status',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [1, 2, 3, 4, 5, 6, 7, 8, 9]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'places': [
            {
                'place_id': 1,
                'statuses': [
                    {
                        'status': 'active',
                        'value': '5',
                        'starts': '2020-11-25T15:43:00+00:00',
                    },
                ],
            },
            {
                'place_id': 2,
                'statuses': [
                    {
                        'status': 'active',
                        'value': '6',
                        'starts': '2020-11-25T15:43:00+00:00',
                    },
                    {
                        'status': 'wait_to_start',
                        'value': '7',
                        'starts': '2022-11-25T15:43:00+00:00',
                    },
                ],
            },
            {
                'place_id': 3,
                'statuses': [
                    {
                        'starts': '2022-09-20T15:43:00+00:00',
                        'status': 'wait_to_start',
                        'value': '3',
                    },
                ],
            },
            {
                'place_id': 4,
                'statuses': [
                    {
                        'starts': '2021-09-20T18:43:00+00:00',
                        'status': 'activating',
                        'value': '10',
                    },
                ],
            },
            {
                'place_id': 5,
                'statuses': [
                    {
                        'starts': '2021-09-20T18:43:00+00:00',
                        'status': 'deactivating',
                        'value': '6',
                    },
                ],
            },
            {
                'place_id': 6,
                'statuses': [
                    {
                        'reasons': [
                            {
                                'code': 'region_without_plus',
                                'message': (
                                    'В вашем регионе '
                                    'не действует Яндекс Плюс.'
                                ),
                            },
                        ],
                        'status': 'can_not_be_activated',
                    },
                ],
            },
            {
                'place_id': 7,
                'statuses': [
                    {
                        'reasons': [
                            {
                                'code': 'region_without_plus',
                                'message': 'Недоступно в вашем регионе.',
                            },
                        ],
                        'status': 'can_not_be_activated',
                    },
                ],
            },
            {
                'place_id': 8,
                'statuses': [
                    {
                        'status': 'can_not_be_activated',
                        'reasons': [
                            {
                                'code': 'low_rating',
                                'message': (
                                    'Рейтинг ресторана: 2.9. '
                                    'Чтобы стать партнером Плюса, '
                                    'нужен рейтинг от 4.'
                                ),
                            },
                        ],
                    },
                ],
            },
            {
                'place_id': 9,
                'statuses': [
                    {
                        'reasons': [
                            {
                                'code': 'region_without_plus',
                                'message': (
                                    'В вашем регионе '
                                    'не действует Яндекс Плюс.'
                                ),
                            },
                            {
                                'code': 'low_rating',
                                'message': (
                                    'Рейтинг ресторана: 1.9. '
                                    'Чтобы стать партнером Плюса, '
                                    'нужен рейтинг от 4.'
                                ),
                            },
                        ],
                        'status': 'can_not_be_activated',
                    },
                ],
            },
        ],
    }
