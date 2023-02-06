async def test_promo_get(
        taxi_eats_restapp_marketing,
        mockserver,
        mock_authorizer_allowed,
        mock_eats_core,
):
    @mockserver.json_handler('/eats-core/v1/places/promo')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=200,
            json={
                'id': 228,
                'status': 'disabled',
                'name': 'promo_name',
                'description': 'description',
                'place_ids': [41, 42, 43],
                'type': 'one_plus_one',
                'starts_at': '2020-08-28T15:11:25+03:00',
                'ends_at': '2020-08-28T15:11:25+03:00',
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
        )

    url = '/4.0/restapp-front/marketing/v1/promo?id=41'

    partner_id = 1
    headers = {
        'X-YaEda-PartnerId': str(partner_id),
        'Content-type': 'application/json',
    }
    extra = {'headers': headers}

    response = await taxi_eats_restapp_marketing.get(url, **extra)

    assert response.status_code == 200
    response = response.json()

    expected = {
        'id': 228,
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
    }

    assert response == expected


async def test_promo_get_404(
        taxi_eats_restapp_marketing,
        mockserver,
        mock_authorizer_allowed,
        mock_eats_core,
):
    @mockserver.json_handler('/eats-core/v1/places/promo')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=404,
            json={'isSuccess': False, 'statusCode': 404, 'type': 'error'},
        )

    url = '/4.0/restapp-front/marketing/v1/promo?id=41'

    partner_id = 1
    headers = {
        'X-YaEda-PartnerId': str(partner_id),
        'Content-type': 'application/json',
    }
    extra = {'headers': headers}

    response = await taxi_eats_restapp_marketing.get(url, **extra)

    assert response.status_code == 404


async def test_promo_get_403(
        taxi_eats_restapp_marketing,
        mockserver,
        mock_authorizer_forbidden,
        mock_eats_core,
):
    @mockserver.json_handler('/eats-core/v1/places/promo')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=403,
            json={
                'isSuccess': False,
                'statusCode': 403,
                'type': 'forbidden',
                'errors': [],
            },
        )

    url = '/4.0/restapp-front/marketing/v1/promo?id=28'

    partner_id = 1
    headers = {
        'X-YaEda-PartnerId': str(partner_id),
        'Content-type': 'application/json',
    }
    extra = {'headers': headers}

    response = await taxi_eats_restapp_marketing.get(url, **extra)

    assert response.status_code == 403
