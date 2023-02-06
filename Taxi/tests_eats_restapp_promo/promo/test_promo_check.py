import pytest


def invariant_sort(resp):
    if 'check_result' in resp:
        resp['check_result'].sort(key=lambda x: x['promo_type'])
        for promo in resp['check_result']:
            promo['places_failed'].sort(key=lambda x: x['place_id'])
            promo['places_passed'].sort(key=lambda x: x['place_id'])
            for place in promo['places_failed']:
                place['failed_checks'].sort(key=lambda x: x['code'])
                place['passed_checks'].sort(key=lambda x: x['code'])
            for place in promo['places_passed']:
                place['passed_checks'].sort(key=lambda x: x['code'])
    return resp


async def test_promo_check_autorization_403(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_403,
):
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/check',
        headers={'X-YaEda-PartnerId': '1'},
        json={'type': 'plus_first_orders', 'place_ids': [1, 5]},
    )

    assert response.status_code == 403
    response = response.json()
    assert response == {'code': '403', 'message': 'Permission Denied'}


async def test_promo_check_autorization_400(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_400,
):
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/check',
        headers={'X-YaEda-PartnerId': '1'},
        json={'type': 'plus_first_orders', 'place_ids': [1, 5]},
    )

    assert response.status_code == 400
    response = response.json()
    assert response == {'code': '400', 'message': 'Bad Request'}


@pytest.mark.experiments3(filename='promos_checks_settings.json')
async def test_promo_check_autorization_200(
        taxi_eats_restapp_promo,
        mockserver,
        mock_authorizer_allowed,
        mock_partners_info_200,
):
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/check',
        headers={'X-YaEda-PartnerId': '1'},
        json={'type': 'plus_first_orders', 'place_ids': [1, 5]},
    )

    assert response.status_code == 200


@pytest.mark.experiments3(filename='promos_checks_settings.json')
async def test_promo_check_happy(
        taxi_eats_restapp_promo,
        mockserver,
        mock_authorizer_allowed,
        mock_partners_info_200,
):
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/check',
        headers={'X-YaEda-PartnerId': '1'},
        json={'type': 'plus_first_orders', 'place_ids': [1, 5]},
    )

    assert response.status_code == 200
    assert response.json() == {
        'check_result': [
            {
                'promo_type': 'plus_first_orders',
                'places_failed': [
                    {
                        'failed_checks': [
                            {
                                'code': 0,
                                'description': 'Подключитесь к Яндекс Плюс.',
                                'short_description': (
                                    'Ресторан не участвует в программе Плюса.'
                                ),
                                'title': (
                                    'Ресторан не подключен к Яндекс Плюс.'
                                ),
                            },
                        ],
                        'passed_checks': [],
                        'place_id': 5,
                    },
                ],
                'places_passed': [
                    {
                        'passed_checks': [
                            {
                                'code': 0,
                                'description': (
                                    'Ресторан подключен к '
                                    'Яндекс Плюс. Вы можете '
                                    'включить акцию.'
                                ),
                                'title': 'Ресторан подключен к Яндекс Плюс.',
                            },
                        ],
                        'place_id': 1,
                    },
                ],
            },
        ],
    }


@pytest.mark.now('2021-10-06T12:00:00+0300')
@pytest.mark.eats_catalog_storage_cache(
    file='eats_catalog_storage_cache_data.json',
)
@pytest.mark.experiments3(filename='promos_settings_full.json')
@pytest.mark.experiments3(filename='promos_checks_settings.json')
async def test_promo_check_free_delivery_and_other(
        taxi_eats_restapp_promo,
        mockserver,
        mock_authorizer_allowed,
        pgsql,
        mock_partners_info_200,
):
    core_response = {
        'places_passed': [
            {
                'place_id': 1,
                'passed_checks': [
                    {
                        'code': 2,
                        'title': 'title',
                        'description': 'description',
                    },
                ],
            },
        ],
        'places_failed': [],
    }

    @mockserver.json_handler('/eats-core/v1/places/promo/check')
    def _core_check_handler(request):
        return {'is_success': True, 'payload': core_response}

    @mockserver.json_handler(
        '/eats-place-rating/eats/v1/eats-place-rating/v1/places-rating-info',
    )
    def _rating_info_handler(request):
        return {'places_rating_info': []}

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/check',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [1]},
    )

    assert response.status_code == 200
    assert response.json() == {
        'check_result': [
            {
                'promo_type': 'discount',
                'places_passed': [
                    {
                        'place_id': 1,
                        'passed_checks': [
                            {
                                'code': 2,
                                'title': 'title',
                                'description': 'description',
                            },
                        ],
                    },
                ],
                'places_failed': [],
            },
            {
                'promo_type': 'free_delivery',
                'places_passed': [
                    {
                        'place_id': 1,
                        'passed_checks': [
                            {
                                'code': 2,
                                'title': 'title',
                                'description': 'description',
                            },
                            {
                                'code': 4,
                                'title': 'Доставка native',
                                'description': (
                                    'Проверка типа ресторана прошла успешно'
                                ),
                            },
                            {
                                'code': 5,
                                'title': 'Ресторан',
                                'description': (
                                    'Проверка типа заведения прошла успешно'
                                ),
                            },
                        ],
                    },
                ],
                'places_failed': [],
            },
            {
                'promo_type': 'gift',
                'places_passed': [
                    {
                        'place_id': 1,
                        'passed_checks': [
                            {
                                'code': 2,
                                'title': 'title',
                                'description': 'description',
                            },
                        ],
                    },
                ],
                'places_failed': [],
            },
            {
                'promo_type': 'one_plus_one',
                'places_passed': [
                    {
                        'place_id': 1,
                        'passed_checks': [
                            {
                                'code': 2,
                                'title': 'title',
                                'description': 'description',
                            },
                        ],
                    },
                ],
                'places_failed': [],
            },
            {
                'promo_type': 'plus_first_orders',
                'places_passed': [
                    {
                        'place_id': 1,
                        'passed_checks': [
                            {
                                'code': 0,
                                'title': 'Ресторан подключен к Яндекс Плюс.',
                                'description': (
                                    'Ресторан подключен к Яндекс'
                                    ' Плюс. Вы можете включить акцию.'
                                ),
                            },
                        ],
                    },
                ],
                'places_failed': [],
            },
            {
                'promo_type': 'plus_happy_hours',
                'places_passed': [
                    {
                        'place_id': 1,
                        'passed_checks': [
                            {
                                'code': 0,
                                'title': 'Ресторан подключен к Яндекс Плюс.',
                                'description': (
                                    'Ресторан подключен к Яндекс'
                                    ' Плюс. Вы можете включить акцию.'
                                ),
                            },
                        ],
                    },
                ],
                'places_failed': [],
            },
        ],
    }


@pytest.mark.experiments3(filename='promos_checks_settings.json')
@pytest.mark.now('2021-10-06T12:00:00+0300')
@pytest.mark.eats_catalog_storage_cache(
    file='eats_catalog_storage_cache_data.json',
)
async def test_promo_check_free_delivery_happy(
        taxi_eats_restapp_promo,
        mockserver,
        mock_authorizer_allowed,
        pgsql,
        mock_partners_info_200,
):
    core_response = {
        'places_passed': [
            {
                'place_id': 1,
                'passed_checks': [
                    {
                        'code': 2,
                        'title': 'title',
                        'description': 'description',
                    },
                ],
            },
        ],
        'places_failed': [
            {
                'place_id': 2,
                'passed_checks': [
                    {
                        'code': 2,
                        'title': 'title',
                        'description': 'description',
                    },
                ],
                'failed_checks': [
                    {
                        'code': 2,
                        'title': 'title',
                        'short_description': 'short_description',
                        'description': 'description',
                    },
                ],
            },
        ],
    }

    @mockserver.json_handler('/eats-core/v1/places/promo/check')
    def _core_check_handler(request):
        return {'is_success': True, 'payload': core_response}

    @mockserver.json_handler(
        '/eats-place-rating/eats/v1/eats-place-rating/v1/places-rating-info',
    )
    def _rating_info_handler(request):
        return {'places_rating_info': []}

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/check',
        headers={'X-YaEda-PartnerId': '1'},
        json={'type': 'free_delivery', 'place_ids': [1, 2]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'check_result': [
            {
                'places_failed': [
                    {
                        'failed_checks': [
                            {
                                'code': 2,
                                'description': 'description',
                                'short_description': 'short_description',
                                'title': 'title',
                            },
                            {
                                'code': 4,
                                'description': (
                                    'Проверка типа ресторана провалена'
                                ),
                                'short_description': (
                                    'Нельзя выбрать бесплатную доставку'
                                ),
                                'title': 'Доставка marketplace',
                            },
                            {
                                'code': 5,
                                'description': (
                                    'Проверка типа заведения провалена'
                                ),
                                'short_description': (
                                    'Доступно только для ресторанов'
                                ),
                                'title': 'Заведение не ресторан',
                            },
                        ],
                        'passed_checks': [
                            {
                                'code': 2,
                                'description': 'description',
                                'title': 'title',
                            },
                        ],
                        'place_id': 2,
                    },
                ],
                'places_passed': [
                    {
                        'passed_checks': [
                            {
                                'code': 2,
                                'description': 'description',
                                'title': 'title',
                            },
                            {
                                'code': 4,
                                'description': (
                                    'Проверка типа ресторана прошла успешно'
                                ),
                                'title': 'Доставка native',
                            },
                            {
                                'code': 5,
                                'title': 'Ресторан',
                                'description': (
                                    'Проверка типа заведения прошла успешно'
                                ),
                            },
                        ],
                        'place_id': 1,
                    },
                ],
                'promo_type': 'free_delivery',
            },
        ],
    }


@pytest.mark.experiments3(filename='promos_checks_settings.json')
@pytest.mark.parametrize(
    ['request_body', 'expected_code', 'expected_response'],
    [
        # plus_first_orders
        (
            {'type': 'plus_first_orders', 'place_ids': [2, 4, 5]},
            200,
            {
                'check_result': [
                    {
                        'promo_type': 'plus_first_orders',
                        'places_passed': [
                            {
                                'place_id': 2,
                                'passed_checks': [
                                    {
                                        'code': 0,
                                        'title': (
                                            'Ресторан подключен к Яндекс'
                                            ' Плюс.'
                                        ),
                                        'description': (
                                            'Ресторан подключ'
                                            'ен к Яндекс Плюс. Вы можете вкл'
                                            'ючить акцию.'
                                        ),
                                    },
                                ],
                            },
                        ],
                        'places_failed': [
                            {
                                'place_id': 5,
                                'passed_checks': [],
                                'failed_checks': [
                                    {
                                        'code': 0,
                                        'title': (
                                            'Ресторан не подключен '
                                            'к Яндекс Плюс.'
                                        ),
                                        'short_description': (
                                            'Ресторан н'
                                            'е участвует в программе Плюса.'
                                        ),
                                        'description': (
                                            'Подключитесь к Яндекс Плюс.'
                                        ),
                                    },
                                ],
                            },
                            {
                                'place_id': 4,
                                'passed_checks': [],
                                'failed_checks': [
                                    {
                                        'code': 0,
                                        'title': (
                                            'Ресторан не подключен '
                                            'к Яндекс Плюс.'
                                        ),
                                        'short_description': (
                                            'Ресторан н'
                                            'е участвует в программе Плюса.'
                                        ),
                                        'description': (
                                            'Подключитесь к Яндекс Плюс.'
                                        ),
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
        ),
        # plus_happy_hours
        (
            {'type': 'plus_happy_hours', 'place_ids': [2, 4, 5]},
            200,
            {
                'check_result': [
                    {
                        'promo_type': 'plus_happy_hours',
                        'places_passed': [
                            {
                                'place_id': 2,
                                'passed_checks': [
                                    {
                                        'code': 0,
                                        'title': (
                                            'Ресторан подключен к Яндекс'
                                            ' Плюс.'
                                        ),
                                        'description': (
                                            'Ресторан подключ'
                                            'ен к Яндекс Плюс. Вы можете вкл'
                                            'ючить акцию.'
                                        ),
                                    },
                                ],
                            },
                        ],
                        'places_failed': [
                            {
                                'place_id': 5,
                                'passed_checks': [],
                                'failed_checks': [
                                    {
                                        'code': 0,
                                        'title': (
                                            'Ресторан не подключен '
                                            'к Яндекс Плюс.'
                                        ),
                                        'short_description': (
                                            'Ресторан н'
                                            'е участвует в программе Плюса.'
                                        ),
                                        'description': (
                                            'Подключитесь к Яндекс Плюс.'
                                        ),
                                    },
                                ],
                            },
                            {
                                'place_id': 4,
                                'passed_checks': [],
                                'failed_checks': [
                                    {
                                        'code': 0,
                                        'title': (
                                            'Ресторан не подключен '
                                            'к Яндекс Плюс.'
                                        ),
                                        'short_description': (
                                            'Ресторан н'
                                            'е участвует в программе Плюса.'
                                        ),
                                        'description': (
                                            'Подключитесь к Яндекс Плюс.'
                                        ),
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
        ),
    ],
)
async def test_promo_check_filters(
        taxi_eats_restapp_promo,
        mockserver,
        mock_authorizer_allowed,
        request_body,
        expected_code,
        expected_response,
        mock_partners_info_200,
):
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/check',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == expected_code
    assert response.json() == expected_response


@pytest.mark.config(
    EATS_RESTAPP_PROMO_ACTIVATE_PROMO_SETTINGS={
        'enabled': False,
        'failed_checks_keys': {
            'code': 1,
            'title': 'promo_activation_disabled_failed_checks_title',
            'description': (
                'promo_activation_disabled_failed_checks_description'
            ),
            'short_description': (
                'promo_activation_disabled_failed_checks_short_description'
            ),
        },
    },
)
async def test_promo_activate_disabled(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/check',
        headers={'X-YaEda-PartnerId': '1'},
        json={'type': 'plus_first_orders', 'place_ids': [1, 2]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'check_result': [
            {
                'promo_type': 'plus_first_orders',
                'places_failed': [
                    {
                        'failed_checks': [
                            {
                                'code': 1,
                                'description': (
                                    'Создание акций '
                                    'временно недоступно. '
                                    'Приносим свои извинения.'
                                ),
                                'short_description': (
                                    'Создание акций временно недоступно.'
                                ),
                                'title': (
                                    'Создание акций временно' ' недоступно.'
                                ),
                            },
                        ],
                        'passed_checks': [],
                        'place_id': 1,
                    },
                    {
                        'failed_checks': [
                            {
                                'code': 1,
                                'description': (
                                    'Создание акций '
                                    'временно недоступно. '
                                    'Приносим свои извинения.'
                                ),
                                'short_description': (
                                    'Создание акций временно недоступно.'
                                ),
                                'title': (
                                    'Создание акций временно' ' недоступно.'
                                ),
                            },
                        ],
                        'passed_checks': [],
                        'place_id': 2,
                    },
                ],
                'places_passed': [],
            },
        ],
    }


@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.experiments3(filename='promos_checks_settings.json')
@pytest.mark.config(
    EATS_RESTAPP_PROMO_ACTIVATE_PROMO_SETTINGS={
        'enabled': False,
        'failed_checks_keys': {
            'code': 1,
            'title': 'test_title',
            'description': 'test_description',
            'short_description': 'test_short_description',
        },
    },
)
async def test_promo_activate_disabled_for_all(
        taxi_eats_restapp_promo,
        mock_authorizer_allowed,
        mock_partners_info_200,
):
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/check',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [1]},
    )

    failed_checks = {
        'places_failed': [
            {
                'failed_checks': [
                    {
                        'code': 1,
                        'description': 'test_description',
                        'short_description': 'test_short_description',
                        'title': 'test_title',
                    },
                ],
                'passed_checks': [],
                'place_id': 1,
            },
        ],
        'places_passed': [],
    }

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'check_result': [
            {'promo_type': 'gift', **failed_checks},
            {'promo_type': 'one_plus_one', **failed_checks},
            {'promo_type': 'plus_happy_hours', **failed_checks},
        ],
    }


@pytest.mark.experiments3(filename='promos_settings_both.json')
@pytest.mark.experiments3(filename='promos_checks_settings.json')
@pytest.mark.config(
    EATS_RESTAPP_PROMO_ACTIVATE_PROMO_SETTINGS={
        'enabled': True,
        'failed_checks_keys': {
            'code': 1,
            'title': 'test_title',
            'description': 'test_description',
            'short_description': 'test_short_description',
        },
    },
)
async def test_promo_check_both(
        taxi_eats_restapp_promo,
        mock_authorizer_allowed,
        mockserver,
        mock_partners_info_200,
):
    core_response = {
        'places_passed': [
            {
                'place_id': 28,
                'passed_checks': [
                    {
                        'code': 2,
                        'title': 'title',
                        'description': 'description',
                    },
                ],
            },
        ],
        'places_failed': [
            {
                'place_id': 1,
                'passed_checks': [
                    {
                        'code': 2,
                        'title': 'title',
                        'description': 'description',
                    },
                ],
                'failed_checks': [
                    {
                        'code': 2,
                        'title': 'title',
                        'short_description': 'short_description',
                        'description': 'description',
                    },
                ],
            },
        ],
    }

    @mockserver.json_handler('/eats-core/v1/places/promo/check')
    def _core_check_handler(request):
        return {'is_success': True, 'payload': core_response}

    @mockserver.json_handler(
        '/eats-place-rating/eats/v1/eats-place-rating/v1/places-rating-info',
    )
    def _rating_info_handler(request):
        return {'places_rating_info': []}

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/check',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [1, 28]},
    )

    failed_checks = {
        'places_passed': [
            {
                'place_id': 1,
                'passed_checks': [
                    {
                        'code': 0,
                        'title': 'Ресторан подключен к Яндекс Плюс.',
                        'description': (
                            'Ресторан подключен к Яндекс Плюс'
                            '. Вы можете включить акцию.'
                        ),
                    },
                ],
            },
        ],
        'places_failed': [
            {
                'place_id': 28,
                'passed_checks': [],
                'failed_checks': [
                    {
                        'code': 0,
                        'title': 'Ресторан не подключен к Яндекс Плюс.',
                        'short_description': (
                            'Ресторан не участвует в программе Плюса.'
                        ),
                        'description': 'Подключитесь к Яндекс Плюс.',
                    },
                ],
            },
        ],
    }

    assert response.status_code == 200
    assert response.json() == {
        'check_result': [
            {'promo_type': 'gift', **core_response},
            {'promo_type': 'plus_happy_hours', **failed_checks},
        ],
    }


@pytest.mark.now('2021-10-06T12:00:00+0300')
@pytest.mark.eats_catalog_storage_cache(
    file='eats_catalog_cache_integration.json',
)
@pytest.mark.experiments3(filename='promos_settings_full.json')
@pytest.mark.experiments3(filename='promos_checks_settings.json')
async def test_promo_check_free_delivery_integration(
        taxi_eats_restapp_promo,
        mockserver,
        mock_authorizer_allowed,
        pgsql,
        mock_partners_info_200,
        load_json,
):
    @mockserver.json_handler('/eats-core/v1/places/promo/check')
    def _core_check_handler(request):
        return load_json('core_response.json')

    @mockserver.json_handler(
        '/eats-place-rating/eats/v1/eats-place-rating/v1/places-rating-info',
    )
    def _rating_info_handler(request):
        return {
            'places_rating_info': [
                {
                    'place_id': 305733,
                    'average_rating': 0.0,
                    'user_rating': 0.0,
                    'cancel_rating': 5.0,
                    'show_rating': True,
                    'calculated_at': '2021-01-01',
                    'feedbacks_count': 5,
                },
            ],
        }

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/check',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [162, 7323, 7079, 305733, 475484]},
    )

    assert response.status_code == 200
    assert invariant_sort(response.json()) == load_json('promo_response.json')
