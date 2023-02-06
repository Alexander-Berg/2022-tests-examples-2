import pytest

TEST_PARTNER_ID = 1

PROMO_CHECK_REQUEST = {'place_ids': [41, 42, 43]}

PROMO_CHECK_RESPONSE_AVERAGE_RATING = {
    'places_passed': [
        {
            'place_id': 43,
            'passed_checks': [
                {
                    'code': 1,
                    'title': 'Рейтинг 5',
                    'description': (
                        'Создавать акции можно с рейтингом не менее 4.2'
                    ),
                },
            ],
        },
        {
            'place_id': 41,
            'passed_checks': [
                {
                    'code': 1,
                    'title': 'Рейтинг 5',
                    'description': (
                        'Создавать акции можно с рейтингом не менее 4.2'
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
                        'Рейтинг: 4.1. Для создания акций'
                        ' нужен рейтинг от 4.2.'
                    ),
                    'description': (
                        'Хорошие отзывы показывают, что вы заботитесь о '
                        'пользователях и операционных показателях'
                    ),
                },
            ],
        },
    ],
}

PROMO_CHECK_RESPONSE_CANCEL_RATING = {
    'places_passed': [
        {
            'place_id': 42,
            'passed_checks': [
                {
                    'code': 1,
                    'title': 'Рейтинг отмен 5',
                    'description': (
                        'Создавать акции можно с рейтингом отмен не менее '
                        '3.9'
                    ),
                },
            ],
        },
        {
            'place_id': 41,
            'passed_checks': [
                {
                    'code': 1,
                    'title': 'Рейтинг отмен 5',
                    'description': (
                        'Создавать акции можно с рейтингом отмен не менее '
                        '3.9'
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
                        'Рейтинг отмен: 3.8. Для создания акций'
                        ' нужен рейтинг от 3.9.'
                    ),
                    'description': (
                        'Отсутствие отмен показывает, что вы заботитесь о '
                        'пользователях и операционных показателях'
                    ),
                },
            ],
        },
    ],
}


PROMO_CHECK_RESPONSE_CANCEL_RATING_ZERO = {
    'places_failed': [],
    'places_passed': [
        {'passed_checks': [], 'place_id': 42},
        {'passed_checks': [], 'place_id': 43},
        {
            'passed_checks': [
                {
                    'code': 1,
                    'description': (
                        'Создавать акции можно с рейтингом отмен не менее 3.9'
                    ),
                    'title': 'Рейтинг отмен',
                },
            ],
            'place_id': 41,
        },
    ],
}


PROMO_CORE_CHECK_RESPONSE = {
    'places_passed': [
        {'place_id': 42, 'passed_checks': []},
        {
            'place_id': 43,
            'passed_checks': [
                {'code': 1, 'title': 'title', 'description': 'description'},
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

AUTHORIZER_200_RESPONSE = {'status': '200'}

CORE_PROMO_CHECK_200_RESPONSE = {
    'status': '200',
    'json': {'is_success': True, 'payload': PROMO_CORE_CHECK_RESPONSE},
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
CORE_PROMO_500_RESPONSE = {'status': '500'}

PROMO_NO_ENABLED_RESPONSE = {'code': '403', 'message': 'No active promos'}


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


THRESHOLD_FEEDBACKS = 10


@pytest.mark.experiments3(filename='promo_exp.json')
@pytest.mark.parametrize(
    'rating_response,'
    'auth_partner_response, core_response, expected_status,'
    'uservices_response, authorizer_response',
    [
        [
            get_rating_response(THRESHOLD_FEEDBACKS),
            AUTHORIZER_PARTNER_200_RESPONSE,
            CORE_PROMO_CHECK_200_RESPONSE,
            200,
            PROMO_CHECK_RESPONSE_AVERAGE_RATING,
            AUTHORIZER_200_RESPONSE,
        ],
        [
            get_rating_response(THRESHOLD_FEEDBACKS - 1),
            AUTHORIZER_PARTNER_200_RESPONSE,
            CORE_PROMO_CHECK_200_RESPONSE,
            200,
            PROMO_CHECK_RESPONSE_CANCEL_RATING,
            AUTHORIZER_200_RESPONSE,
        ],
        [
            RATING_RESPONSE_ZERO_CANCELS,
            AUTHORIZER_PARTNER_200_RESPONSE,
            CORE_PROMO_CHECK_200_RESPONSE,
            200,
            PROMO_CHECK_RESPONSE_CANCEL_RATING_ZERO,
            AUTHORIZER_200_RESPONSE,
        ],
        [
            get_rating_response(),
            AUTHORIZER_PARTNER_403_NOT_MANAGER,
            CORE_PROMO_CHECK_200_RESPONSE,
            403,
            {
                'code': '403',
                'message': 'Error: no access to the place or no permissions',
            },
            AUTHORIZER_200_RESPONSE,
        ],
        [
            get_rating_response(),
            AUTHORIZER_PARTNER_400_RESPONSE,
            CORE_PROMO_CHECK_200_RESPONSE,
            400,
            {'code': '400', 'message': 'Error: unable to authorize'},
            AUTHORIZER_200_RESPONSE,
        ],
        [
            get_rating_response(),
            AUTHORIZER_PARTNER_403_DIFFERENT_PLACES,
            CORE_PROMO_CHECK_200_RESPONSE,
            403,
            {
                'code': '403',
                'message': 'Error: no access to the place or no permissions',
            },
            {
                'status': '403',
                'json': {
                    'code': '403',
                    'message': 'no rights to place with id=41',
                    'place_ids': [41],
                },
            },
        ],
        [
            get_rating_response(),
            AUTHORIZER_PARTNER_200_RESPONSE,
            CORE_PROMO_400_RESPONSE,
            400,
            {'code': '400', 'message': 'error message'},
            AUTHORIZER_200_RESPONSE,
        ],
        [
            get_rating_response(),
            AUTHORIZER_PARTNER_200_RESPONSE,
            CORE_PROMO_404_RESPONSE,
            404,
            {'code': '404', 'message': 'some of places=41,42,43 not found'},
            AUTHORIZER_200_RESPONSE,
        ],
    ],
    ids=[
        'success_rating',
        'success_cancel_rating',
        'zero_cancel_rating',
        'auth_partner_not_manager',
        'auth_partner_400',
        'auth_partner_wrong_places',
        'core_400',
        'core_404',
    ],
)
async def test_promo_check(
        request_proxy,
        mock_any_handler,
        rating_response,
        auth_partner_response,
        core_response,
        authorizer_response,
        expected_status,
        uservices_response,
):
    await mock_any_handler(
        url='/eats-restapp-authorizer/v1/user-access/check',
        response=auth_partner_response,
    )

    await mock_any_handler(
        url='/eats-core/v1/places/promo/check', response=core_response,
    )
    await mock_any_handler(
        url='/eats-restapp-authorizer/place-access/check',
        response=authorizer_response,
    )

    await mock_any_handler(
        url='/eats-place-rating/eats/v1/eats-place-rating/v1'
        '/places-rating-info',
        response=rating_response,
    )

    response = await request_proxy(
        'post',
        '/4.0/restapp-front/marketing/v1/promo/check',
        PROMO_CHECK_REQUEST,
        TEST_PARTNER_ID,
    )

    assert response.status_code == expected_status
    print(response.json())
    if uservices_response is not None:
        assert response.json() == uservices_response


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_PROMO_LIST={
        'available': ['discount', 'gift', 'one_plus_one'],
        'enabled': [],
    },
)
async def test_promo_experiment_has_no_enabled(
        request_proxy, mock_any_handler,
):
    auth_partner_handler = await mock_any_handler(
        url='/eats-restapp-authorizer/v1/user-access/check',
        response={'status': 400},
    )
    core_handler = await mock_any_handler(
        url='/eats-core/v1/places/promo/check', response={'status': 500},
    )

    response = await request_proxy(
        'post',
        '/4.0/restapp-front/marketing/v1/promo/check',
        PROMO_CHECK_REQUEST,
        TEST_PARTNER_ID,
    )
    assert response.status_code == 403
    assert response.json() == PROMO_NO_ENABLED_RESPONSE

    assert not auth_partner_handler.has_calls
    assert not core_handler.has_calls


@pytest.mark.experiments3(filename='promo_exp.json')
@pytest.mark.config(
    EATS_RESTAPP_MARKETING_PROMO_START={
        'integration_checker': {'enabled': True},
        'menu_pecrent_photo_checker': {'enabled': True, 'min_percent': 70},
        'rating_checker': {
            'cancel_rating': 3.9,
            'enabled': False,
            'rating': 4.2,
            'threshold_feedbacks': 10,
        },
    },
)
async def test_unable_rating_checks(
        request_proxy, mock_any_handler, mockserver,
):
    @mockserver.json_handler(
        '/eats-place-rating/eats/v1/eats-place-rating/v1'
        '/places-rating-info',
    )
    def mock_places_rating_info(data):
        pass

    await mock_any_handler(
        url='/eats-restapp-authorizer/v1/user-access/check',
        response=AUTHORIZER_PARTNER_200_RESPONSE,
    )

    await mock_any_handler(
        url='/eats-core/v1/places/promo/check',
        response=CORE_PROMO_CHECK_200_RESPONSE,
    )
    await mock_any_handler(
        url='/eats-restapp-authorizer/place-access/check',
        response=AUTHORIZER_200_RESPONSE,
    )

    response = await request_proxy(
        'post',
        '/4.0/restapp-front/marketing/v1/promo/check',
        PROMO_CHECK_REQUEST,
        TEST_PARTNER_ID,
    )

    assert response.status_code == 200
    assert mock_places_rating_info.times_called == 0
