import pytest


DEFAULT_CONFIG = {
    'enabled': False,
    'reason_message': {'code': 'region_without_plus', 'message': ''},
}


@pytest.mark.config(
    EATS_RESTAPP_PROMO_AVAILABLE_STATUS_SETTINGS=DEFAULT_CONFIG,
)
@pytest.mark.now('2021-08-12T17:38:00.00')
@pytest.mark.eats_catalog_storage_cache(
    file='eats_catalog_storage_cache_data.json',
)
async def test_available_activate(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/status',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [1]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'places': [
            {'place_id': 1, 'statuses': [{'status': 'can_be_activated'}]},
        ],
    }


@pytest.mark.now('2021-08-12T17:38:00.00')
@pytest.mark.eats_catalog_storage_cache(
    file='eats_catalog_storage_cache_data.json',
)
async def test_not_available_activate_because_no_plus(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/status',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [2]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'places': [
            {
                'place_id': 2,
                'statuses': [
                    {
                        'reasons': [
                            {
                                'code': 'region_without_plus',
                                'message': (
                                    'В вашем регионе не действует Яндекс Плюс.'
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
async def test_not_available_activate_because_no_rating(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/status',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [11]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'places': [
            {
                'place_id': 11,
                'statuses': [
                    {
                        'reasons': [
                            {
                                'code': 'no_rating',
                                'message': (
                                    'У вашего ресторана нет рейтинга. '
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
async def test_not_available_activate_because_rating_dont_show(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/status',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [12]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'places': [
            {
                'place_id': 12,
                'statuses': [
                    {
                        'reasons': [
                            {
                                'code': 'few_ratings',
                                'message': (
                                    'У вашего ресторана мало оценок. '
                                    'Чтобы стать партнером Плюса, '
                                    'нужно больше оценок и '
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
async def test_not_available_activate_because_low_rating(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/status',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [3]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'places': [
            {
                'place_id': 3,
                'statuses': [
                    {
                        'reasons': [
                            {
                                'code': 'low_rating',
                                'message': (
                                    'Рейтинг ресторана: 3.3. '
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
async def test_not_available_activate_because_low_rating_and_no_plus(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/status',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [4]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'places': [
            {
                'place_id': 4,
                'statuses': [
                    {
                        'reasons': [
                            {
                                'code': 'region_without_plus',
                                'message': (
                                    'В вашем регионе не действует Яндекс Плюс.'
                                ),
                            },
                            {
                                'code': 'low_rating',
                                'message': (
                                    'Рейтинг ресторана: 3.9. '
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
async def test_available_activate_config_enabled(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/status',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [1]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'places': [
            {
                'place_id': 1,
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
        ],
    }


@pytest.mark.config(
    EATS_RESTAPP_PROMO_PLUS_ACTIVATE_CONDITIONS={
        'min_rating': 4.0,
        'excluded_place_ids': [1, 2, 3],
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
@pytest.mark.now('2021-08-12T17:38:00.00')
@pytest.mark.eats_catalog_storage_cache(
    file='eats_catalog_storage_cache_data.json',
)
async def test_available_activate_excluded_place(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/status',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [1]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'places': [
            {
                'place_id': 1,
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
                        ],
                        'status': 'can_not_be_activated',
                    },
                ],
            },
        ],
    }
