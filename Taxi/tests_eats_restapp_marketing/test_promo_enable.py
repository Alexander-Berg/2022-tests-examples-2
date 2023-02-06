async def test_promo_enable_204(
        taxi_eats_restapp_marketing, mockserver, mock_auth_partner,
):
    @mockserver.json_handler('/eats-core/v1/places/promo/enable')
    def _mock_sessions(req):
        return mockserver.make_response(status=200, json={'isSuccess': True})

    url = '/4.0/restapp-front/marketing/v1/promo/enable'
    body = {'id': 1}
    headers = {'X-YaEda-PartnerId': '1', 'Content-type': 'application/json'}
    extra = {'json': body, 'headers': headers}

    response = await taxi_eats_restapp_marketing.post(url, **extra)
    assert response.status_code == 204


async def test_promo_enable_404(
        taxi_eats_restapp_marketing, mockserver, mock_auth_partner,
):
    @mockserver.json_handler('/eats-core/v1/places/promo/enable')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=404,
            json={'isSuccess': False, 'statusCode': 404, 'type': 'error'},
        )

    url = '/4.0/restapp-front/marketing/v1/promo/enable'
    body = {'id': 1}
    headers = {'X-YaEda-PartnerId': '1', 'Content-type': 'application/json'}
    extra = {'json': body, 'headers': headers}

    response = await taxi_eats_restapp_marketing.post(url, **extra)
    assert response.status_code == 404


async def test_promo_enable_400(
        taxi_eats_restapp_marketing, mockserver, mock_auth_partner,
):
    url = '/4.0/restapp-front/marketing/v1/promo/enable'
    body = {'id': 1}
    headers = {'X-YaEda-PartnerId': '1', 'Content-type': 'application/json'}
    extra = {'json': body, 'headers': headers}

    @mockserver.json_handler('/eats-core/v1/places/promo/enable')
    def _mock_core(request):
        return mockserver.make_response(
            status=400,
            json={
                'isSuccess': False,
                'statusCode': 400,
                'type': 'validation error',
                'errors': [{'message': 'error message'}],
                'context': 'some context',
            },
        )

    response = await taxi_eats_restapp_marketing.post(url, **extra)
    assert response.status_code == 400
