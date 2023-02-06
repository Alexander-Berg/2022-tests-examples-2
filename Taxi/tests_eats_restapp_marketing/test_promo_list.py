async def test_promo_list(
        taxi_eats_restapp_marketing,
        mockserver,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_eats_core,
        load_json,
):
    promos = load_json('promo_list.json')

    @mockserver.json_handler('/eats-core/v1/places/promo/list')
    def _mock_sessions(req):
        return mockserver.make_response(status=200, json=promos)

    url = (
        '/4.0/restapp-front/marketing/v1/promo/list'
        + '?place_ids=41,42,43'
        + '&after=0'
        + '&limit=4'
        + '&status=new'
        + '&start_date=2020-08-28'
        + '&finish_date=2020-09-28'
        + '&type=gift'
    )

    partner_id = 1
    headers = {
        'X-YaEda-PartnerId': str(partner_id),
        'Content-type': 'application/json',
    }
    extra = {'headers': headers}

    response = await taxi_eats_restapp_marketing.get(url, **extra)

    assert response.status_code == 200

    response_promos = response.json()
    assert response_promos == promos


async def test_promo_list_404(
        taxi_eats_restapp_marketing,
        mockserver,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_eats_core,
):
    @mockserver.json_handler('/eats-core/v1/places/promo/list')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=404,
            json={'isSuccess': False, 'statusCode': 404, 'type': 'error'},
        )

    url = (
        '/4.0/restapp-front/marketing/v1/promo/list?'
        'place_ids=41&after=0&limit=4'
    )

    partner_id = 1
    headers = {
        'X-YaEda-PartnerId': str(partner_id),
        'Content-type': 'application/json',
    }
    extra = {'headers': headers}

    response = await taxi_eats_restapp_marketing.get(url, **extra)

    assert response.status_code == 404


async def test_promo_list_403(
        taxi_eats_restapp_marketing,
        mockserver,
        mock_auth_partner_not_manager,
        mock_authorizer_forbidden,
        mock_eats_core,
):
    url = (
        '/4.0/restapp-front/marketing/v1/promo/list?'
        'place_ids=28&after=0&limit=4'
    )
    partner_id = 1
    headers = {
        'X-YaEda-PartnerId': str(partner_id),
        'Content-type': 'application/json',
    }
    extra = {'headers': headers}

    response = await taxi_eats_restapp_marketing.get(url, **extra)

    assert response.status_code == 403
