import pytest

EATS_RESTAPP_MARKETING_RESPONSES = {
    '3': {
        'id': 3,
        'status': 'disabled',
        'name': 'promo_name',
        'description': 'description',
        'place_ids': [41, 42, 43],
        'type': 'one_plus_one',
        'starts_at': '2020-08-28T12:11:25+00:00',
        'ends_at': '2020-08-28T12:11:25+00:00',
        'schedule': [
            {'day': 2, 'from': 60, 'to': 180},
            {'day': 7, 'from': 1000, 'to': 1030},
        ],
        'requirements': [
            {'category_ids': [1, 2, 3], 'item_ids': ['100', '105']},
            {'category_ids': [1, 2, 3]},
            {'item_ids': ['100']},
        ],
        'bonuses': [{'discount': 20}, {'item_id': 'item_id_1'}],
    },
    '4': {
        'id': 4,
        'status': 'enabled',
        'name': 'promo_name',
        'description': 'description',
        'place_ids': [41, 42, 43],
        'type': 'discount',
        'starts_at': '2020-08-28T12:11:25+00:00',
        'ends_at': '2020-08-28T12:11:25+00:00',
        'schedule': [
            {'day': 2, 'from': 60, 'to': 180},
            {'day': 7, 'from': 1000, 'to': 1030},
        ],
        'requirements': [
            {'category_ids': [1, 2, 3], 'item_ids': ['100', '105']},
            {'category_ids': [1, 2, 3]},
            {'item_ids': ['100']},
        ],
        'bonuses': [{'discount': 20}, {'item_id': 'item_id_1'}],
    },
    '5': {
        'id': 4,
        'status': 'new',
        'name': 'promo_name',
        'description': 'description',
        'place_ids': [41, 42, 43],
        'type': 'gift',
        'starts_at': '2020-08-28T12:11:25+00:00',
        'ends_at': '2020-08-28T12:11:25+00:00',
        'schedule': [
            {'day': 2, 'from': 60, 'to': 180},
            {'day': 7, 'from': 1000, 'to': 1030},
        ],
        'requirements': [
            {'category_ids': [1, 2, 3], 'item_ids': ['100', '105']},
            {'category_ids': [1, 2, 3]},
            {'item_ids': ['100']},
        ],
        'bonuses': [{'discount': 20}, {'item_id': 'item_id_1'}],
    },
}


async def test_promo_get_by_id_autorization_403(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_403,
):
    response = await taxi_eats_restapp_promo.get(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        params={'id': 1},
    )

    assert response.status_code == 403
    response = response.json()
    assert response == {'code': '403', 'message': 'Permission Denied'}


async def test_promo_get_by_id_autorization_400(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_400,
):

    response = await taxi_eats_restapp_promo.get(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        params={'id': 1},
    )

    assert response.status_code == 400
    response = response.json()
    assert response == {'code': '400', 'message': 'Bad Request'}


async def test_promo_get_by_id_autorization_500(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_500,
):

    response = await taxi_eats_restapp_promo.get(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        params={'id': 1},
    )

    assert response.status_code == 400
    response = response.json()
    assert response == {'code': '400', 'message': 'Bad Request'}


async def test_promo_get_dont_check_permissions(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_500,
):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_eats_discounts(request):
        return mockserver.make_response(
            status=403,
            json={
                'code': '403',
                'message': 'Forbidden',
                'details': {
                    'permissions': ['permission.promo.status'],
                    'place_ids': [],
                },
            },
        )

    response = await taxi_eats_restapp_promo.get(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        params={'id': 1},
    )

    assert response.status_code == 403


async def test_promo_get_by_id_autorization_200(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.get(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        params={'id': 1},
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    ['promo_id', 'expected_code', 'expected_response'],
    [
        (
            1,
            200,
            {
                'bonuses': [{'cashback': [20.0, 10.0, 5.0]}],
                'description': (
                    'Привлечь новых пользователей, '
                    'предложив им повышенный кешбек '
                    'за первые заказы.'
                ),
                'ends_at': '2021-11-25T15:43:00+00:00',
                'id': 1,
                'name': 'Повышенный кешбэк для новичков',
                'place_ids': [1, 2],
                'requirements': [{'min_order_price': 50.5}],
                'starts_at': '2020-11-25T15:43:00+00:00',
                'status': 'approved',
                'type': 'plus_first_orders',
            },
        ),
        (
            2,
            200,
            {
                'bonuses': [{'cashback': [5.0]}],
                'description': (
                    'Предложите повышенный кешбек ' 'за заказ в мёртвые часы.'
                ),
                'ends_at': '2021-11-25T15:43:00+00:00',
                'id': 2,
                'name': 'Повышенный кешбэк в счастливые часы',
                'place_ids': [3, 4, 5],
                'requirements': [{'min_order_price': 50.5}],
                'schedule': [
                    {'day': 1, 'from': 0, 'to': 120},
                    {'day': 3, 'from': 120, 'to': 220},
                    {'day': 7, 'from': 120, 'to': 360},
                ],
                'starts_at': '2020-11-25T15:43:00+00:00',
                'status': 'new',
                'type': 'plus_happy_hours',
            },
        ),
        (
            3456,
            200,
            {
                'bonuses': [],
                'description': 'Предложите бесплатную доставку.',
                'ends_at': '2021-12-24T21:00:00+00:00',
                'id': 3456,
                'name': 'Бесплатная доставка',
                'place_ids': [8, 9],
                'requirements': [{'order_numbers': [1]}],
                'starts_at': '2021-08-24T21:00:00+00:00',
                'status': 'enabled',
                'type': 'free_delivery',
            },
        ),
        (
            4567,
            200,
            {
                'bonuses': [],
                'description': 'Предложите бесплатную доставку.',
                'ends_at': '2021-12-24T21:00:00+00:00',
                'id': 4567,
                'name': 'Бесплатная доставка',
                'place_ids': [8, 9],
                'requirements': [{'order_indexes': [3, 4, 5]}],
                'starts_at': '2021-09-24T21:00:00+00:00',
                'status': 'enabled',
                'type': 'free_delivery',
            },
        ),
    ],
)
async def test_promo_get_by_id_new_promos(
        taxi_eats_restapp_promo,
        mockserver,
        mock_authorizer_allowed,
        promo_id,
        expected_code,
        expected_response,
):

    response = await taxi_eats_restapp_promo.get(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        params={'id': promo_id},
    )

    assert response.status_code == expected_code
    response = response.json()
    assert response == expected_response


@pytest.mark.parametrize(
    ['promo_id', 'expected_code'], [(3, 200), (4, 200), (5, 200)],
)
async def test_promo_get_by_id_old_promos(
        taxi_eats_restapp_promo,
        mockserver,
        mock_authorizer_allowed,
        promo_id,
        expected_code,
):
    @mockserver.json_handler(
        '/eats-restapp-marketing/4.0/restapp-front/marketing/v1/promo',
    )
    def _mock_restapp_marketing(request):
        return mockserver.make_response(
            status=200, json=EATS_RESTAPP_MARKETING_RESPONSES[str(promo_id)],
        )

    response = await taxi_eats_restapp_promo.get(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        params={'id': promo_id},
    )

    assert response.status_code == expected_code
    response = response.json()
    assert response == EATS_RESTAPP_MARKETING_RESPONSES[str(promo_id)]

    assert _mock_restapp_marketing.times_called == 1


@pytest.mark.parametrize(
    ['promo_id', 'partner_id', 'expected_code', 'expected_response'],
    [
        (
            1234,
            '1',
            200,
            {
                'bonuses': [{'cashback': [20.0, 10.0, 5.0]}],
                'description': (
                    'Привлечь новых пользователей, '
                    'предложив им повышенный кешбек '
                    'за первые заказы.'
                ),
                'ends_at': '2021-11-25T15:43:00+00:00',
                'id': 1234,
                'name': 'Повышенный кешбэк для новичков',
                'place_ids': [1, 2],
                'requirements': [{'min_order_price': 50.5}],
                'starts_at': '2020-11-25T15:43:00+00:00',
                'status': 'approved',
                'type': 'plus_first_orders',
            },
        ),
        (2345, '2', 403, {'code': '403', 'message': 'Permission Denied'}),
        (2345, '3', 403, {'code': '403', 'message': 'Permission Denied'}),
        (
            2345,
            '4',
            200,
            {
                'bonuses': [{'cashback': [5.0]}],
                'description': (
                    'Предложите повышенный кешбек ' 'за заказ в мёртвые часы.'
                ),
                'ends_at': '2021-11-25T15:43:00+00:00',
                'id': 2345,
                'name': 'Повышенный кешбэк в счастливые часы',
                'place_ids': [2, 3],
                'requirements': [{'min_order_price': 50.5}],
                'schedule': [
                    {'day': 1, 'from': 0, 'to': 120},
                    {'day': 3, 'from': 120, 'to': 220},
                    {'day': 7, 'from': 120, 'to': 360},
                ],
                'starts_at': '2020-11-25T15:43:00+00:00',
                'status': 'new',
                'type': 'plus_happy_hours',
            },
        ),
    ],
)
async def test_promo_get_by_id_new_promos_with_partial_places_permissions(
        taxi_eats_restapp_promo,
        mockserver,
        promo_id,
        partner_id,
        expected_code,
        expected_response,
):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_authorizer(request):
        if request.json['partner_id'] == 1:
            details = {'permissions': [], 'place_ids': [2]}
        if request.json['partner_id'] == 2:
            details = {'permissions': [], 'place_ids': [2, 3]}
        if request.json['partner_id'] == 3:
            details = {'permissions': ['permissions'], 'place_ids': []}
        if request.json['partner_id'] == 4:
            details = {'permissions': [], 'place_ids': []}
        return mockserver.make_response(
            status=403,
            json={'code': '403', 'message': 'Forbidden', 'details': details},
        )

    response = await taxi_eats_restapp_promo.get(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': partner_id},
        params={'id': promo_id},
    )

    assert response.status_code == expected_code
    response = response.json()
    assert response == expected_response
