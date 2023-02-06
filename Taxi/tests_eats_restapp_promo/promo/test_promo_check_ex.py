import pytest


PROMO_CHECK_RESPONSE_AVERAGE_RATING = {
    'check_result': [
        {
            'promo_type': 'discount',
            'places_passed': [
                {
                    'place_id': 41,
                    'passed_checks': [
                        {
                            'code': 1,
                            'title': 'Рейтинг 5',
                            'description': (
                                'Создавать акции можно с рей'
                                'тингом не менее 4.2'
                            ),
                        },
                    ],
                },
                {
                    'place_id': 43,
                    'passed_checks': [
                        {
                            'code': 1,
                            'title': 'Рейтинг 5',
                            'description': (
                                'Создавать акции можно с рей'
                                'тингом не менее 4.2'
                            ),
                        },
                    ],
                },
            ],
            'places_failed': [
                {
                    'place_id': 42,
                    'passed_checks': [],
                    'failed_checks': [
                        {
                            'code': 1,
                            'title': 'Рейтинг не менее 4.2',
                            'short_description': (
                                'Рейтинг: 4.1. Для соз'
                                'дания акций нужен рейтинг от 4.2.'
                            ),
                            'description': (
                                'Хорошие отзывы показывают, '
                                'что вы заботитесь о пользователях и операц'
                                'ионных показателях'
                            ),
                        },
                    ],
                },
            ],
        },
    ],
}

PROMO_CHECK_RESPONSE_CANCEL_RATING = {
    'check_result': [
        {
            'promo_type': 'discount',
            'places_passed': [
                {
                    'place_id': 41,
                    'passed_checks': [
                        {
                            'code': 1,
                            'title': 'Рейтинг отмен 5',
                            'description': (
                                'Создавать акции можно с рей'
                                'тингом отмен не менее 3.9'
                            ),
                        },
                    ],
                },
                {
                    'place_id': 42,
                    'passed_checks': [
                        {
                            'code': 1,
                            'title': 'Рейтинг отмен 5',
                            'description': (
                                'Создавать акции можно с рей'
                                'тингом отмен не менее 3.9'
                            ),
                        },
                    ],
                },
            ],
            'places_failed': [
                {
                    'place_id': 43,
                    'passed_checks': [],
                    'failed_checks': [
                        {
                            'code': 1,
                            'title': 'Рейтинг отмен не менее 3.9',
                            'short_description': (
                                'Рейтинг отмен: 3.8. Д'
                                'ля создания акций нужен рейтинг от 3.9.'
                            ),
                            'description': (
                                'Отсутствие отмен показывает'
                                ', что вы заботитесь о пользователях и опер'
                                'ационных показателях'
                            ),
                        },
                    ],
                },
            ],
        },
    ],
}

PROMO_CHECK_RESPONSE_CANCEL_RATING_ZERO = {
    'check_result': [
        {
            'promo_type': 'discount',
            'places_passed': [
                {
                    'place_id': 41,
                    'passed_checks': [
                        {
                            'code': 1,
                            'title': 'Рейтинг отмен',
                            'description': (
                                'Создавать акции можно с рей'
                                'тингом отмен не менее 3.9'
                            ),
                        },
                    ],
                },
                {'place_id': 42, 'passed_checks': []},
                {'place_id': 43, 'passed_checks': []},
            ],
            'places_failed': [],
        },
    ],
}

AUTHORIZER_PARTNER_200_RESPONSE = {'status': '200'}
AUTHORIZER_PARTNER_403_NOT_MANAGER = {
    'status': '403',
    'json': {
        'code': '403',
        'message': 'forbidden',
        'details': {
            'permissions': ['permission.restaurant.management'],
            'place_ids': [123],
        },
    },
}
AUTHORIZER_PARTNER_403_DIFFERENT_PLACES = {
    'status': '403',
    'json': {
        'code': '403',
        'message': 'forbidden',
        'details': {
            'permissions': ['permission.restaurant.functionality'],
            'place_ids': [123],
        },
    },
}
AUTHORIZER_PARTNER_400_RESPONSE = {
    'status': '400',
    'json': {'code': '400', 'message': 'bad request'},
}

CORE_PROMO_CHECK_200_RESPONSE = {
    'status': '200',
    'json': {
        'is_success': True,
        'payload': {
            'places_passed': [
                {'place_id': 42, 'passed_checks': []},
                {
                    'place_id': 43,
                    'passed_checks': [
                        {
                            'code': 1,
                            'title': 'title',
                            'description': 'description',
                        },
                    ],
                },
            ],
            'places_failed': [
                {
                    'place_id': 41,
                    'passed_checks': [],
                    'failed_checks': [
                        {
                            'code': 1,
                            'title': 'title',
                            'short_description': 'short_description',
                            'description': 'description',
                        },
                    ],
                },
            ],
        },
    },
}
CORE_PROMO_400_RESPONSE = {
    'status': '400',
    'json': {
        'isSuccess': False,
        'statusCode': 400,
        'type': 'validation error',
        'errors': [{'message': 'error message'}],
        'context': 'some context',
    },
}
CORE_PROMO_404_RESPONSE = {
    'status': '404',
    'json': {'isSuccess': False, 'statusCode': 404, 'type': 'not found'},
}

RATING_RESPONSE_ZERO_CANCELS = {
    'status': '200',
    'json': {
        'places_rating_info': [
            {
                'place_id': 41,
                'average_rating': 5.0,
                'user_rating': 5.0,
                'cancel_rating': 0,
                'show_rating': True,
                'calculated_at': '2019-01-01',
                'feedbacks_count': 9,
            },
        ],
    },
}


def get_rating_response(feedbacks_count=1):
    return {
        'status': '200',
        'json': {
            'places_rating_info': [
                {
                    'place_id': 41,
                    'average_rating': 5.0,
                    'user_rating': 5.0,
                    'cancel_rating': 5.0,
                    'show_rating': True,
                    'calculated_at': '2019-01-01',
                    'feedbacks_count': feedbacks_count,
                },
                {
                    'place_id': 42,
                    'average_rating': 4.1,
                    'user_rating': 5.0,
                    'cancel_rating': 5.0,
                    'show_rating': True,
                    'calculated_at': '2019-01-01',
                    'feedbacks_count': feedbacks_count,
                },
                {
                    'place_id': 43,
                    'average_rating': 5.0,
                    'user_rating': 5.0,
                    'cancel_rating': 3.8,
                    'show_rating': True,
                    'calculated_at': '2019-01-01',
                    'feedbacks_count': feedbacks_count,
                },
            ],
        },
    }


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


@pytest.mark.experiments3(filename='promos_settings_full.json')
@pytest.mark.experiments3(filename='promos_checks_settings.json')
@pytest.mark.parametrize(
    'rating_response,'
    'auth_partner_response, core_response, expected_status,'
    'uservices_response',
    [
        pytest.param(
            get_rating_response(10),
            AUTHORIZER_PARTNER_200_RESPONSE,
            CORE_PROMO_CHECK_200_RESPONSE,
            200,
            PROMO_CHECK_RESPONSE_AVERAGE_RATING,
            id='success_rating',
        ),
        pytest.param(
            get_rating_response(9),
            AUTHORIZER_PARTNER_200_RESPONSE,
            CORE_PROMO_CHECK_200_RESPONSE,
            200,
            PROMO_CHECK_RESPONSE_CANCEL_RATING,
            id='success_cancel_rating',
        ),
        pytest.param(
            RATING_RESPONSE_ZERO_CANCELS,
            AUTHORIZER_PARTNER_200_RESPONSE,
            CORE_PROMO_CHECK_200_RESPONSE,
            200,
            PROMO_CHECK_RESPONSE_CANCEL_RATING_ZERO,
            id='zero_cancel_rating',
        ),
        pytest.param(
            get_rating_response(),
            AUTHORIZER_PARTNER_403_NOT_MANAGER,
            CORE_PROMO_CHECK_200_RESPONSE,
            403,
            {'code': '403', 'message': 'Permission Denied'},
            id='auth_partner_not_manager',
        ),
        pytest.param(
            get_rating_response(),
            AUTHORIZER_PARTNER_400_RESPONSE,
            CORE_PROMO_CHECK_200_RESPONSE,
            400,
            {'code': '400', 'message': 'Bad Request'},
            id='auth_partner_400',
        ),
        pytest.param(
            get_rating_response(),
            AUTHORIZER_PARTNER_403_DIFFERENT_PLACES,
            CORE_PROMO_CHECK_200_RESPONSE,
            403,
            {'code': '403', 'message': 'Permission Denied'},
            id='auth_partner_wrong_places',
        ),
        pytest.param(
            get_rating_response(),
            AUTHORIZER_PARTNER_200_RESPONSE,
            CORE_PROMO_400_RESPONSE,
            400,
            {'code': '400', 'message': 'Validation error'},
            id='core_400',
        ),
        pytest.param(
            get_rating_response(),
            AUTHORIZER_PARTNER_200_RESPONSE,
            CORE_PROMO_404_RESPONSE,
            404,
            {'code': '404', 'message': 'Some places not found'},
            id='core_404',
        ),
    ],
)
async def test_promo_check_ex(
        taxi_eats_restapp_promo,
        mockserver,
        rating_response,
        auth_partner_response,
        core_response,
        expected_status,
        uservices_response,
        mock_partners_info_200,
):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _user_access_check(request):
        return mockserver.make_response(**auth_partner_response)

    @mockserver.json_handler('/eats-core/v1/places/promo/check')
    def _core_promo_check(request):
        return mockserver.make_response(**core_response)

    @mockserver.json_handler(
        '/eats-place-rating/eats/v1/eats-place-rating/v1/places-rating-info',
    )
    def _rating_info_handler(request):
        return mockserver.make_response(**rating_response)

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/check',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [41, 42, 43], 'type': 'discount'},
    )

    assert response.status_code == expected_status
    if uservices_response is not None:
        assert invariant_sort(response.json()) == uservices_response
