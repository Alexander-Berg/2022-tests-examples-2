import pytest

# 1. эксперимент включен
# 1.1. роль оператор - 403
# 1.2. роль управляющий
# 1.2.1. обновление акции с типом gift - 200
# 1.2.2. обновление акции с типом discount - 200
# 1.2.3. обновление акции с типом one by one - 200
# 1.2.4. у пользователя другие рестораны в вендорке - 403
# 1.2.5. пользователь не найден в вендорке - 400
# 1.2.6. ошибка в вендорке - 500
# 1.2.7. входящие параметры невалидны в коре - 400
# 1.2.8. рестораны не найдены в коре - 404
# 1.2.9. ошибка в коре - 500
# 2. эксперимент выключен - 400
# 3. эксперимент не доступен - 400

TEST_PARTNER_ID = 1

TEST_PROMO_GIFT_REQUEST = 'promo_patch_gift.json'
TEST_PROMO_DISCOUNT_REQUEST = 'promo_patch_discount.json'
TEST_PROMO_ONE_PLUS_ONE_REQUEST = 'promo_patch_one_plus_one.json'
TEST_PROMO_RESPONSE = 'promo.json'

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

PROMO_INVALID_TYPE_RESPONSE = {'code': '403', 'message': 'Invalid promo type'}

THRESHOLD_FEEDBACKS = 10


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


@pytest.mark.experiments3(filename='promo_exp.json')
@pytest.mark.parametrize(
    'rating_response,'
    'auth_partner_response, core_response, expected_status,'
    'uservices_request, uservices_response, authorizer_response',
    [
        [
            get_rating_response(),
            AUTHORIZER_PARTNER_200_RESPONSE,
            TEST_PROMO_RESPONSE,
            200,
            TEST_PROMO_GIFT_REQUEST,
            TEST_PROMO_RESPONSE,
            AUTHORIZER_200_RESPONSE,
        ],
        [
            get_rating_response(),
            AUTHORIZER_PARTNER_200_RESPONSE,
            TEST_PROMO_RESPONSE,
            200,
            TEST_PROMO_DISCOUNT_REQUEST,
            TEST_PROMO_RESPONSE,
            AUTHORIZER_200_RESPONSE,
        ],
        [
            get_rating_response(),
            AUTHORIZER_PARTNER_200_RESPONSE,
            TEST_PROMO_RESPONSE,
            200,
            TEST_PROMO_ONE_PLUS_ONE_REQUEST,
            TEST_PROMO_RESPONSE,
            AUTHORIZER_200_RESPONSE,
        ],
        [
            get_rating_response(),
            AUTHORIZER_PARTNER_403_NOT_MANAGER,
            TEST_PROMO_RESPONSE,
            403,
            TEST_PROMO_GIFT_REQUEST,
            {
                'code': '403',
                'message': 'Error: no access to the place or no permissions',
            },
            AUTHORIZER_200_RESPONSE,
        ],
        [
            get_rating_response(),
            AUTHORIZER_PARTNER_403_DIFFERENT_PLACES,
            TEST_PROMO_RESPONSE,
            403,
            TEST_PROMO_GIFT_REQUEST,
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
            AUTHORIZER_PARTNER_400_RESPONSE,
            TEST_PROMO_RESPONSE,
            400,
            TEST_PROMO_GIFT_REQUEST,
            {'code': '400', 'message': 'Error: unable to authorize'},
            AUTHORIZER_200_RESPONSE,
        ],
        [
            get_rating_response(),
            AUTHORIZER_PARTNER_200_RESPONSE,
            CORE_PROMO_400_RESPONSE,
            400,
            TEST_PROMO_GIFT_REQUEST,
            {'code': '400', 'message': 'error message'},
            AUTHORIZER_200_RESPONSE,
        ],
        [
            get_rating_response(),
            AUTHORIZER_PARTNER_200_RESPONSE,
            CORE_PROMO_404_RESPONSE,
            404,
            TEST_PROMO_GIFT_REQUEST,
            {
                'code': '404',
                'message': (
                    'some of places=41,42,43 for partner with id=1 not found'
                ),
            },
            AUTHORIZER_200_RESPONSE,
        ],
        [
            get_rating_response(),
            AUTHORIZER_PARTNER_200_RESPONSE,
            CORE_PROMO_500_RESPONSE,
            500,
            TEST_PROMO_GIFT_REQUEST,
            {'code': '500', 'message': 'Internal Server Error'},
            AUTHORIZER_200_RESPONSE,
        ],
    ],
    ids=[
        'success_gift',
        'success_discount',
        'success_one_plus_one',
        'auth_partner_not_manager',
        'auth_partner_wrong_places',
        'auth_partner_400',
        'core_400',
        'core_404',
        'core_500',
    ],
)
async def test_promo_patch(
        taxi_config,
        request_proxy,
        mock_any_handler,
        auth_partner_response,
        core_response,
        expected_status,
        uservices_request,
        uservices_response,
        load_json,
        authorizer_response,
        rating_response,
):
    taxi_config.set_values(
        {
            'EATS_RESTAPP_MARKETING_HANDLERS_ROLES': [
                {'handler_code': 'promo', 'roles': ['ROLE_MANAGER']},
            ],
        },
    )

    await mock_any_handler(
        url='/eats-place-rating/eats/v1/eats-place-rating/v1'
        '/places-rating-info',
        response=rating_response,
    )

    await mock_any_handler(
        url='/eats-restapp-authorizer/v1/user-access/check',
        response=auth_partner_response,
    )

    if core_response == TEST_PROMO_RESPONSE:
        core_response = {'status': '200', 'json': load_json(core_response)}
    await mock_any_handler(
        url='/eats-core/v1/places/promo', response=core_response,
    )
    await mock_any_handler(
        url='/eats-restapp-authorizer/place-access/check',
        response=authorizer_response,
    )

    response = await request_proxy(
        'patch',
        '/4.0/restapp-front/marketing/v1/promo',
        load_json(uservices_request),
        TEST_PARTNER_ID,
    )

    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json() == load_json(uservices_response)
    else:
        assert response.json() == uservices_response


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_PROMO_LIST={
        'available': ['discount', 'gift', 'one_plus_one'],
        'enabled': [],
    },
)
async def test_promo_patch_experiment_has_no_enabled(
        request_proxy, mock_any_handler, load_json,
):
    auth_partner_handler = await mock_any_handler(
        url='/eats-restapp-authorizer/v1/user-access/check',
        response={'status': 400},
    )
    core_handler = await mock_any_handler(
        url='/eats-core/v1/places/promo', response={'status': 500},
    )

    response = await request_proxy(
        'patch',
        '/4.0/restapp-front/marketing/v1/promo',
        load_json(TEST_PROMO_ONE_PLUS_ONE_REQUEST),
        TEST_PARTNER_ID,
    )
    assert response.status_code == 403
    assert response.json() == PROMO_INVALID_TYPE_RESPONSE

    assert not auth_partner_handler.has_calls
    assert not core_handler.has_calls
