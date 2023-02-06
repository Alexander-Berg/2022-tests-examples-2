import pytest

TEST_PARTNER_ID = 1

TEST_PROMO_GIFT_REQUEST = 'promo_patch_gift.json'
TEST_PROMO_DISCOUNT_REQUEST = 'promo_patch_discount.json'
TEST_PROMO_ONE_PLUS_ONE_REQUEST = 'promo_patch_one_plus_one.json'
TEST_PROMO_RESPONSE = 'promo.json'


@pytest.mark.parametrize(
    'expected_status,uservices_request,uservices_response',
    [
        [200, TEST_PROMO_GIFT_REQUEST, TEST_PROMO_RESPONSE],
        [200, TEST_PROMO_DISCOUNT_REQUEST, TEST_PROMO_RESPONSE],
        [200, TEST_PROMO_ONE_PLUS_ONE_REQUEST, TEST_PROMO_RESPONSE],
        [
            403,
            TEST_PROMO_GIFT_REQUEST,
            {
                'code': '403',
                'message': 'Error: no access to the place or no permissions',
            },
        ],
        [
            403,
            TEST_PROMO_GIFT_REQUEST,
            {
                'code': '403',
                'message': 'Error: no access to the place or no permissions',
            },
        ],
        [
            400,
            TEST_PROMO_GIFT_REQUEST,
            {'code': '400', 'message': 'Error: unable to authorize'},
        ],
        [
            400,
            TEST_PROMO_GIFT_REQUEST,
            {'code': '400', 'message': 'error message'},
        ],
        [
            404,
            TEST_PROMO_GIFT_REQUEST,
            {
                'code': '404',
                'message': (
                    'some of places=41,42,43 for partner with id=1 not found'
                ),
            },
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
    ],
)
async def test_promo_patch(
        taxi_eats_restapp_promo,
        mockserver,
        expected_status,
        uservices_request,
        uservices_response,
        load_json,
):
    @mockserver.json_handler(
        '/eats-restapp-marketing/4.0' '/restapp-front/marketing/v1/promo',
    )
    def _marketing_response(request):
        assert request.json == load_json(uservices_request)
        if expected_status != 200:
            return mockserver.make_response(
                json=uservices_response, status=expected_status,
            )
        return load_json(uservices_response)

    response = await taxi_eats_restapp_promo.patch(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': f'{TEST_PARTNER_ID}'},
        json=load_json(uservices_request),
    )

    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json() == load_json(uservices_response)
    else:
        assert response.json() == uservices_response


@pytest.mark.experiments3(filename='switching_to_new_platform.json')
@pytest.mark.parametrize(
    'expected_status, uservices_request',
    [
        [500, TEST_PROMO_GIFT_REQUEST],
        [500, TEST_PROMO_DISCOUNT_REQUEST],
        [200, TEST_PROMO_ONE_PLUS_ONE_REQUEST],
    ],
)
async def test_switching_to_new_platform(
        taxi_eats_restapp_promo,
        mockserver,
        expected_status,
        uservices_request,
        load_json,
        mock_authorizer_allowed,
):
    response = await taxi_eats_restapp_promo.patch(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': f'{TEST_PARTNER_ID}'},
        json=load_json(uservices_request),
    )

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'promo_type, expected_code',
    [
        ['plus_first_orders', 404],
        ['plus_happy_hours', 404],
        ['free_delivery', 400],  # not in api
    ],
)
async def test_not_supported_type_of_promo(
        taxi_eats_restapp_promo,
        mockserver,
        promo_type,
        expected_code,
        load_json,
):
    response = await taxi_eats_restapp_promo.patch(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': f'{TEST_PARTNER_ID}'},
        json={'type': promo_type, 'id': 1},
    )

    assert response.status_code == expected_code
