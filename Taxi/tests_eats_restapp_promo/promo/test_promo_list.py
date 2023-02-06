# pylint: disable=too-many-lines

import pytest


PROMOS = {
    1: {
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
    2: {
        'bonuses': [{'cashback': [5.0]}],
        'description': (
            'Предложите повышенный кешбек' ' за заказ в мёртвые часы.'
        ),
        'ends_at': '2021-11-25T15:43:00+00:00',
        'id': 2,
        'name': 'Повышенный кешбэк в счастливые часы',
        'place_ids': [3, 4, 5],
        'requirements': [{'min_order_price': 50.5}],
        'starts_at': '2020-11-25T15:43:00+00:00',
        'status': 'new',
        'type': 'plus_happy_hours',
        'schedule': [
            {'day': 1, 'from': 0, 'to': 120},
            {'day': 3, 'from': 120, 'to': 220},
            {'day': 7, 'from': 120, 'to': 360},
        ],
    },
    3: {
        'bonuses': [{'cashback': [10.0]}],
        'description': (
            'Предложите повышенный кешбек' ' за заказ в мёртвые часы.'
        ),
        'ends_at': '2021-12-24T21:00:00+00:00',
        'id': 3,
        'name': 'Повышенный кешбэк в счастливые часы',
        'place_ids': [6, 7, 8, 9],
        'requirements': [{'min_order_price': 512.5}],
        'starts_at': '2021-08-24T21:00:00+00:00',
        'status': 'enabled',
        'type': 'plus_happy_hours',
    },
    4: {
        'bonuses': [{'cashback': [5.0]}],
        'description': (
            'Привлечь новых пользователей, '
            'предложив им повышенный кешбек за '
            'первые заказы.'
        ),
        'ends_at': '2022-09-30T21:00:00+00:00',
        'id': 4,
        'name': 'Повышенный кешбэк для новичков',
        'place_ids': [9],
        'requirements': [{'min_order_price': 123.321}],
        'starts_at': '2022-09-24T21:00:00+00:00',
        'status': 'disabled',
        'type': 'plus_first_orders',
    },
    5: {
        'bonuses': [],
        'description': 'Предложите бесплатную доставку.',
        'ends_at': '2021-12-24T21:00:00+00:00',
        'id': 5,
        'name': 'Бесплатная доставка',
        'place_ids': [10],
        'requirements': [{'order_numbers': [1]}],
        'starts_at': '2021-08-24T21:00:00+00:00',
        'status': 'enabled',
        'type': 'free_delivery',
    },
    6: {
        'bonuses': [{'cashback': [5.0]}],
        'description': 'Предложите повышенный кешбек за заказ в мёртвые часы.',
        'ends_at': '2021-11-25T15:43:00+00:00',
        'id': 6,
        'name': 'Повышенный кешбэк в счастливые часы',
        'place_ids': [11],
        'requirements': [{'min_order_price': 50.5}],
        'starts_at': '2020-11-24T15:43:00+00:00',
        'status': 'new',
        'type': 'plus_happy_hours',
        'schedule': [
            {'day': 1, 'from': 0, 'to': 120},
            {'day': 3, 'from': 120, 'to': 220},
            {'day': 7, 'from': 120, 'to': 360},
        ],
    },
}


def promos_response(*ids):
    return [PROMOS[id] for id in ids]


async def test_promo_list_autorization_403(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_403,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'after': 0, 'limit': 10},
        json={'place_ids': [1, 2, 3]},
    )

    assert response.status_code == 403
    response = response.json()
    assert response == {'code': '403', 'message': 'Permission Denied'}


async def test_promo_list_autorization_400(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_400,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'after': 0, 'limit': 10},
        json={'place_ids': [1, 2, 3]},
    )

    assert response.status_code == 400
    response = response.json()
    assert response == {'code': '400', 'message': 'Bad Request'}


async def test_promo_list_autorization_200(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'after': 0, 'limit': 10},
        json={'place_ids': [1231, 21235, 153453]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'meta': {'fetched': 0, 'total': 0},
        'payload': {'promos': []},
    }


async def test_promo_list_happy(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'after': 0, 'limit': 10},
        json={'place_ids': [1, 2, 3]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'meta': {'cursor': 1, 'fetched': 2, 'total': 2},
        'payload': {'promos': promos_response(2, 1)},
    }


async def test_promo_free_delivery_happy(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'after': 0, 'limit': 10},
        json={'place_ids': [10]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'meta': {'cursor': 5, 'fetched': 1, 'total': 1},
        'payload': {'promos': promos_response(5)},
    }


@pytest.mark.parametrize(
    ['request_body', 'after', 'limit', 'expected_code', 'expected_response'],
    [
        pytest.param(
            {'place_ids': [1, 2, 3]},
            0,
            1,
            200,
            {
                'meta': {'cursor': 2, 'fetched': 1, 'total': 2},
                'payload': {'promos': promos_response(2)},
            },
            id='check limit filter',
        ),
        pytest.param(
            {'place_ids': [1, 2, 3]},
            2,
            2,
            200,
            {
                'meta': {'cursor': 1, 'fetched': 1, 'total': 2},
                'payload': {'promos': promos_response(1)},
            },
            id='check after filter',
        ),
        pytest.param(
            {'place_ids': [1, 3, 9], 'status': 'new'},
            0,
            10,
            200,
            {
                'meta': {'cursor': 1, 'fetched': 2, 'total': 2},
                'payload': {'promos': promos_response(2, 1)},
            },
            id='with status new',
        ),
        pytest.param(
            {'place_ids': [1, 3, 9], 'status': 'enabled'},
            0,
            10,
            200,
            {
                'meta': {'cursor': 3, 'fetched': 1, 'total': 1},
                'payload': {'promos': promos_response(3)},
            },
            id='with status enabled',
        ),
        pytest.param(
            {'place_ids': [1, 3, 9], 'type': 'plus_happy_hours'},
            0,
            10,
            200,
            {
                'meta': {'cursor': 2, 'fetched': 2, 'total': 2},
                'payload': {'promos': promos_response(3, 2)},
            },
            id='check type filter',
        ),
        pytest.param(
            {
                'place_ids': [1, 3, 9],
                'starts_at': '2022-09-23T21:00:00+00:00',
                'ends_at': '2022-11-01T21:00:00+00:00',
            },
            0,
            10,
            200,
            {
                'meta': {'cursor': 4, 'fetched': 1, 'total': 1},
                'payload': {'promos': promos_response(4)},
            },
            id='check start and end filter, promo within range',
        ),
        pytest.param(
            {
                'place_ids': [1, 3, 9],
                'starts_at': '2022-09-23T00:00:00+03:00',
                'ends_at': '2022-09-24T00:00:00+03:00',
            },
            0,
            10,
            200,
            {'meta': {'fetched': 0, 'total': 0}, 'payload': {'promos': []}},
            id='check start and end filter, promo after range',
        ),
        pytest.param(
            {
                'place_ids': [1, 3, 9],
                'starts_at': '2022-11-02T21:00:00+00:00',
                'ends_at': '2022-11-03T21:00:00+00:00',
            },
            0,
            10,
            200,
            {'meta': {'fetched': 0, 'total': 0}, 'payload': {'promos': []}},
            id='check start and end filter, promo before range',
        ),
        pytest.param(
            {
                'place_ids': [1, 3, 9],
                'starts_at': '2022-09-24T00:00:00+03:00',
                'ends_at': '2022-09-25T00:00:00+03:00',
            },
            0,
            10,
            200,
            {'meta': {'fetched': 0, 'total': 0}, 'payload': {'promos': []}},
            id='check start and end filter, promo starts at range end',
        ),
        pytest.param(
            {
                'place_ids': [1, 3, 9],
                'starts_at': '2022-09-24T00:00:00+03:00',
                'ends_at': '2022-09-26T00:00:00+03:00',
            },
            0,
            10,
            200,
            {
                'meta': {'cursor': 4, 'fetched': 1, 'total': 1},
                'payload': {'promos': promos_response(4)},
            },
            id='check start and end filter, promo starts within range',
        ),
        pytest.param(
            {
                'place_ids': [1, 3, 9],
                'starts_at': '2022-10-01T00:00:00+03:00',
                'ends_at': '2022-10-03T00:00:00+03:00',
            },
            0,
            10,
            200,
            {'meta': {'fetched': 0, 'total': 0}, 'payload': {'promos': []}},
            id='check start and end filter, promo ends at range start',
        ),
        pytest.param(
            {
                'place_ids': [1, 3, 9],
                'starts_at': '2022-09-30T00:00:00+03:00',
                'ends_at': '2022-10-03T00:00:00+03:00',
            },
            0,
            10,
            200,
            {
                'meta': {'cursor': 4, 'fetched': 1, 'total': 1},
                'payload': {'promos': promos_response(4)},
            },
            id='check start and end filter, promo ends within range',
        ),
        pytest.param(
            {
                'place_ids': [1, 3, 9],
                'starts_at': '2022-09-26T00:00:00+03:00',
                'ends_at': '2022-09-30T00:00:00+03:00',
            },
            0,
            10,
            200,
            {
                'meta': {'cursor': 4, 'fetched': 1, 'total': 1},
                'payload': {'promos': promos_response(4)},
            },
            id='check start and end filter, promo active during range',
        ),
    ],
)
async def test_promo_list_filters(
        taxi_eats_restapp_promo,
        mockserver,
        mock_authorizer_allowed,
        request_body,
        after,
        limit,
        expected_code,
        expected_response,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'after': after, 'limit': limit},
        json=request_body,
    )

    assert response.status_code == expected_code
    response = response.json()
    assert response == expected_response


@pytest.mark.config(
    EATS_RESTAPP_PROMO_LIST_CURSOR_SETTINGS={
        'enabled': True,
        'mode': 'eats-restapp-marketing',
    },
)
async def test_promo_list_eats_restapp_marketing(
        taxi_eats_restapp_promo,
        mockserver,
        mock_authorizer_allowed,
        load_json,
):
    # Тест проверяет обработку запроса который нужно полностью проксировать
    # в eats-restapp-marketing
    promos = load_json('eats_restapp_marketing_promos.json')

    @mockserver.json_handler(
        '/eats-restapp-marketing/4.0/restapp-front/marketing/v1/promo/list',
    )
    def _mock_eats_restapp_marketing(request):
        return promos

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'after': 0, 'limit': 10},
        json={'place_ids': [41, 2, 3]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == promos


@pytest.mark.config(
    EATS_RESTAPP_PROMO_LIST_CURSOR_SETTINGS={
        'enabled': True,
        'mode': 'eats-restapp-marketing',
    },
)
async def test_promo_list_eats_restapp_marketing_proxy_403(
        taxi_eats_restapp_promo,
        mockserver,
        mock_authorizer_allowed,
        load_json,
):
    # Тест проверяет, что возвращаем 403, если маркетинг вернул 403.

    @mockserver.json_handler(
        '/eats-restapp-marketing/4.0/restapp-front/marketing/v1/promo/list',
    )
    def _mock_eats_restapp_marketing(request):
        return mockserver.make_response(
            status=403, json={'code': '403', 'message': 'foo'},
        )

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'after': 0, 'limit': 10},
        json={'place_ids': [41, 2, 3]},
    )

    assert response.status_code == 403


@pytest.mark.config(
    EATS_RESTAPP_PROMO_LIST_CURSOR_SETTINGS={
        'enabled': True,
        'mode': 'eats-restapp-marketing',
    },
)
async def test_promo_list_eats_restapp_marketing_plus_type(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):
    # Тест проверяет обработку запроса который нужно полностью проксировать
    # в eats-restapp-marketing, но переданный фильтр type относится к сервису
    # eats-restapp-promo
    @mockserver.json_handler(
        '/eats-restapp-marketing/4.0/restapp-front/marketing/v1/promo/list',
    )
    def _mock_eats_restapp_marketing(request):
        assert False

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'after': 0, 'limit': 10},
        json={'place_ids': [41, 2, 3], 'type': 'plus_first_orders'},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'meta': {'fetched': 0, 'total': 0},
        'payload': {'promos': []},
    }


@pytest.mark.config(
    EATS_RESTAPP_PROMO_LIST_CURSOR_SETTINGS={
        'enabled': True,
        'mode': 'eats-restapp-promo',
    },
)
async def test_promo_list_eats_restapp_promo_not_plus_type(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):
    # Тест проверяет запрос в eats-restapp-promo с типом акции относящейся
    # к eats-restapp-marketing
    @mockserver.json_handler(
        '/eats-restapp-marketing/4.0/restapp-front/marketing/v1/promo/list',
    )
    def _mock_eats_restapp_marketing(request):
        assert False

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'after': 0, 'limit': 10},
        json={'place_ids': [1, 2, 3], 'type': 'gift'},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'meta': {'fetched': 0, 'total': 0},
        'payload': {'promos': []},
    }


@pytest.mark.config(
    EATS_RESTAPP_PROMO_LIST_CURSOR_SETTINGS={'enabled': True, 'mode': 'both'},
)
async def test_promo_list_both_limit_one(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):
    # Тест проверяет запрос с походом в оба сервиса, но limit установлен в 1
    # должна обновиться meta, promo из eats-restapp-promo

    @mockserver.json_handler(
        '/eats-restapp-marketing/4.0/restapp-front/marketing/v1/promo/list',
    )
    def _mock_eats_restapp_marketing(request):
        return {
            'meta': {'cursor': 0, 'fetched': 0, 'total': 200},
            'payload': {'promos': []},
        }

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'after': 0, 'limit': 1},
        json={'place_ids': [1, 2, 3]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'meta': {'cursor': 2, 'fetched': 1, 'total': 202},
        'payload': {'promos': promos_response(2)},
    }


@pytest.mark.config(
    EATS_RESTAPP_PROMO_LIST_CURSOR_SETTINGS={'enabled': True, 'mode': 'both'},
)
async def test_promo_list_both_limit_three(
        taxi_eats_restapp_promo,
        mockserver,
        mock_authorizer_allowed,
        load_json,
):
    # Тест проверяет запрос с походом в оба сервиса, limit 3
    # должна обновиться meta, в список акций должна попадают все акции
    # из eats-restapp-promo и все что вернулось из eats-restapp-marketing
    promos = load_json('eats_restapp_marketing_promos.json')

    @mockserver.json_handler(
        '/eats-restapp-marketing/4.0/restapp-front/marketing/v1/promo/list',
    )
    def _mock_eats_restapp_marketing(request):
        return promos

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'after': 0, 'limit': 3},
        json={'place_ids': [1, 2, 3]},
    )

    promos['meta']['fetched'] = 3
    promos['meta']['total'] += 2
    promos['payload']['promos'] = (
        promos_response(2, 1) + promos['payload']['promos']
    )

    assert response.status_code == 200
    response = response.json()
    assert response == promos


@pytest.mark.config(
    EATS_RESTAPP_PROMO_LIST_CURSOR_SETTINGS={'enabled': True, 'mode': 'both'},
)
async def test_promo_list_both_last_request(
        taxi_eats_restapp_promo,
        mockserver,
        mock_authorizer_allowed,
        load_json,
):
    # Тест проверяет запрос с походом в оба сервиса,
    # выполнение последнего запроса, что вернулся курсор null
    promos = load_json('eats_restapp_marketing_promos.json')
    del promos['meta']['cursor']

    @mockserver.json_handler(
        '/eats-restapp-marketing/4.0/restapp-front/marketing/v1/promo/list',
    )
    def _mock_eats_restapp_marketing(request):
        return promos

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'after': 0, 'limit': 4},
        json={'place_ids': [1, 2, 3]},
    )

    promos['meta']['fetched'] = 3
    promos['meta']['total'] += 2
    promos['payload']['promos'] = (
        promos_response(2, 1) + promos['payload']['promos']
    )

    assert response.status_code == 200
    response = response.json()
    assert response == promos


@pytest.mark.config(
    EATS_RESTAPP_PROMO_LIST_CURSOR_SETTINGS={'enabled': True, 'mode': 'both'},
)
async def test_promo_list_both_marketing_403(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):
    # Тест проверяет запрос с походом в оба сервиса, но marketing вернул 403

    @mockserver.json_handler(
        '/eats-restapp-marketing/4.0/restapp-front/marketing/v1/promo/list',
    )
    def _mock_eats_restapp_marketing(request):
        return mockserver.make_response(
            status=403, json={'code': '403', 'message': 'foo'},
        )

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'after': 0, 'limit': 1},
        json={'place_ids': [1, 2, 3]},
    )

    assert response.status_code == 403
    assert response.json() == {'code': '403', 'message': 'foo'}


@pytest.mark.config(
    EATS_RESTAPP_PROMO_LIST_CURSOR_SETTINGS={'enabled': True, 'mode': 'both'},
)
async def test_promo_list_both_marketing_400(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):
    # Тест проверяет запрос с походом в оба сервиса, но marketing вернул 400

    @mockserver.json_handler(
        '/eats-restapp-marketing/4.0/restapp-front/marketing/v1/promo/list',
    )
    def _mock_eats_restapp_marketing(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'foo'},
        )

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'after': 0, 'limit': 1},
        json={'place_ids': [1, 2, 3]},
    )

    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'foo'}


@pytest.mark.config(
    EATS_RESTAPP_PROMO_LIST_CURSOR_SETTINGS={'enabled': True, 'mode': 'both'},
)
async def test_both_promo_check_marketing_list_filters(
        taxi_eats_restapp_promo,
        mockserver,
        mock_authorizer_allowed,
        load_json,
):
    promos = load_json('eats_restapp_marketing_promos.json')

    @mockserver.json_handler(
        '/eats-restapp-marketing/4.0/restapp-front/marketing/v1/promo/list',
    )
    def _mock_eats_restapp_marketing(request):
        assert request.query == {
            'start_date': '2020-11-23',
            'status': 'new',
            'limit': '7',
            'finish_date': '2021-11-26',
            'after': '1000',
            'place_ids': '1,2,3,10,11',
        }
        return promos

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'after': 1000, 'limit': 10},
        json={
            'place_ids': [1, 2, 3, 10, 11],
            'status': 'new',
            'starts_at': '2020-11-23T21:00:00+00:00',
            'ends_at': '2021-11-26T21:00:00+00:00',
        },
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'payload': {
            'promos': promos_response(6, 2, 1) + [
                promos['payload']['promos'][0],
            ],
        },
        'meta': {'cursor': 5, 'fetched': 4, 'total': 203},
    }


@pytest.mark.config(
    EATS_RESTAPP_PROMO_LIST_CURSOR_SETTINGS={'enabled': True, 'mode': 'both'},
)
async def test_both_promo_dont_request_marketing_if_type_is_new(
        taxi_eats_restapp_promo,
        mockserver,
        mock_authorizer_allowed,
        load_json,
):
    @mockserver.json_handler(
        '/eats-restapp-marketing/4.0/restapp-front/marketing/v1/promo/list',
    )
    def _mock_eats_restapp_marketing(request):
        return {}

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'after': 1000, 'limit': 10},
        json={'place_ids': [1, 3, 9], 'type': 'plus_happy_hours'},
    )

    assert response.status_code == 200
    assert _mock_eats_restapp_marketing.times_called == 0


@pytest.mark.config(
    EATS_RESTAPP_PROMO_LIST_CURSOR_SETTINGS={'enabled': True, 'mode': 'both'},
)
@pytest.mark.parametrize(
    ['request_body', 'after', 'limit', 'expected_code', 'expected_response'],
    [
        pytest.param(
            {'place_ids': [1, 2, 3]},
            0,
            1,
            200,
            {
                'meta': {'cursor': 2, 'fetched': 1, 'total': 202},
                'payload': {'promos': promos_response(2)},
            },
            id='check limit filter',
        ),
        pytest.param(
            {'place_ids': [1, 2, 3]},
            2,
            1,
            200,
            {
                'meta': {'cursor': 1, 'fetched': 1, 'total': 202},
                'payload': {'promos': promos_response(1)},
            },
            id='check after filter',
        ),
        pytest.param(
            {'place_ids': [1, 3, 9], 'status': 'new'},
            0,
            1,
            200,
            {
                'meta': {'cursor': 2, 'fetched': 1, 'total': 202},
                'payload': {'promos': promos_response(2)},
            },
            id='check status filter',
        ),
        pytest.param(
            {'place_ids': [1, 3, 9], 'type': 'plus_happy_hours'},
            0,
            2,
            200,
            {
                'meta': {'cursor': 2, 'fetched': 2, 'total': 2},
                'payload': {'promos': promos_response(3, 2)},
            },
            id='check type filter',
        ),
        pytest.param(
            {
                'place_ids': [1, 3, 9],
                'starts_at': '2022-09-23T21:00:00+00:00',
                'ends_at': '2022-11-01T21:00:00+00:00',
            },
            0,
            1,
            200,
            {
                'meta': {'cursor': 4, 'fetched': 1, 'total': 201},
                'payload': {'promos': promos_response(4)},
            },
            id='check start and end filter',
        ),
    ],
)
async def test_promo_list_both_filters(
        taxi_eats_restapp_promo,
        mockserver,
        mock_authorizer_allowed,
        request_body,
        after,
        limit,
        expected_code,
        expected_response,
):
    @mockserver.json_handler(
        '/eats-restapp-marketing/4.0/restapp-front/marketing/v1/promo/list',
    )
    def _mock_eats_restapp_marketing(request):
        return {
            'meta': {'cursor': 0, 'fetched': 0, 'total': 200},
            'payload': {'promos': []},
        }

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'after': after, 'limit': limit},
        json=request_body,
    )

    assert response.status_code == expected_code
    response = response.json()
    assert response == expected_response


@pytest.mark.experiments3(filename='switching_to_new_platform.json')
@pytest.mark.config(
    EATS_RESTAPP_PROMO_LIST_CURSOR_SETTINGS={'enabled': True, 'mode': 'both'},
)
async def test_promo_list_switching_to_new_platform(
        taxi_eats_restapp_promo,
        mockserver,
        mock_authorizer_allowed,
        load_json,
):
    promos = load_json('eats_restapp_marketing_promos.json')

    @mockserver.json_handler(
        '/eats-restapp-marketing/4.0/restapp-front/marketing/v1/promo/list',
    )
    def _mock_eats_restapp_marketing(request):
        return promos

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'after': 0, 'limit': 3},
        json={'place_ids': [1, 2, 3]},
    )
    assert response.status_code == 200


@pytest.mark.experiments3(filename='switching_to_new_platform.json')
@pytest.mark.config(
    EATS_RESTAPP_PROMO_LIST_CURSOR_SETTINGS={'enabled': True, 'mode': 'both'},
)
async def test_promo_list_autorization_403_new_platform(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_403, testpoint,
):
    @testpoint('new_platform_access_checks')
    def new_platform_access_checks(data):
        pass

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'after': 0, 'limit': 10},
        json={'place_ids': [1, 2, 3]},
    )

    assert response.status_code == 403
    assert new_platform_access_checks.times_called == 1
    response = response.json()
    assert response == {'code': '403', 'message': 'Permission Denied'}


@pytest.mark.experiments3(filename='switching_to_new_platform.json')
@pytest.mark.pgsql(
    'eats_restapp_promo', files=('promos_in_both_services.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_PROMO_LIST_CURSOR_SETTINGS={'enabled': True, 'mode': 'both'},
)
@pytest.mark.parametrize(
    [
        'request_limit',
        'marketing_limit',
        'request_after',
        'marketing_after',
        'marketing_respone',
        'expected_promos',
    ],
    [
        pytest.param(
            '20',
            '19',
            '0',
            '0',
            'promos_in_both_services.json',
            [
                (1, 'Скидка на меню или некоторые позиции'),
                (2, 'Блюдо в подарок из eats-restapp-marketing'),
                (4, 'Блюдо в подарок'),
                (10000000005, 'Блюдо в подарок'),
            ],
            id='promos_from_marketing_are_replaced_by_promos_from_service',
        ),
        pytest.param(
            '20',
            '19',
            '0',
            '0',
            None,
            [(10000000005, 'Блюдо в подарок')],
            id='old_promos_not_in_list_if_marketins_promos_will_be_empty',
        ),
        pytest.param(
            '20',
            '20',
            '10000000005',
            '10000000005',
            'promos_in_both_services.json',
            [
                (1, 'Скидка на меню или некоторые позиции'),
                (2, 'Блюдо в подарок из eats-restapp-marketing'),
                (4, 'Блюдо в подарок'),
            ],
            id='all_promos_are_old',
        ),
        pytest.param(
            '1',
            '0',
            '0',
            '0',
            None,
            [(10000000005, 'Блюдо в подарок')],
            id='check_limit',
        ),
    ],
)
async def test_check_promos_list(
        taxi_eats_restapp_promo,
        mockserver,
        mock_authorizer_allowed,
        load_json,
        request_limit,
        marketing_limit,
        request_after,
        marketing_after,
        marketing_respone,
        expected_promos,
):
    if marketing_respone:
        promos = load_json('promos_in_both_services.json')
    else:
        promos = {
            'meta': {'cursor': 0, 'fetched': 0, 'total': 200},
            'payload': {'promos': []},
        }

    @mockserver.json_handler(
        '/eats-restapp-marketing/4.0/restapp-front/marketing/v1/promo/list',
    )
    def _mock_eats_restapp_marketing(request):
        assert request.query['limit'] == str(marketing_limit)
        assert request.query['after'] == str(marketing_after)
        return promos

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/list',
        headers={'X-YaEda-PartnerId': '1'},
        params={'after': request_after, 'limit': request_limit},
        json={'place_ids': [1, 2, 3]},
    )
    assert response.status_code == 200
    promos = [
        (promo['id'], promo['name'])
        for promo in response.json()['payload']['promos']
    ]
    sort_promos = sorted(promos)
    assert sort_promos == expected_promos

    assert _mock_eats_restapp_marketing.times_called == 1
