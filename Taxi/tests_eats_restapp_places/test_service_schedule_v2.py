async def request_proxy_service_schedule(
        taxi_eats_restapp_places, patner_id, place_id,
):
    url = '/4.0/restapp-front/places/v2/service-schedule?place_id={}'.format(
        place_id,
    )

    headers = {
        'X-YaEda-PartnerId': str(patner_id),
        'Content-type': 'application/json',
        'placeId': str(place_id),
    }
    extra = {'headers': headers}

    return await taxi_eats_restapp_places.get(url, **extra)


async def test_service_schedule_v2(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_service_schedule,
):
    place_id = 42
    partner_id = 1
    response = await request_proxy_service_schedule(
        taxi_eats_restapp_places, partner_id, place_id,
    )
    assert response.status_code == 200

    assert len(response.json()['default']) == 1
    assert response.json()['default'][0]['day'] == 1
    assert response.json()['default'][0]['from'] == 480
    assert response.json()['default'][0]['to'] == 540

    assert len(response.json()['redefined']) == 1
    assert response.json()['redefined'][0]['date'] == '2020-09-24'
    assert response.json()['redefined'][0]['from'] == 480
    assert response.json()['redefined'][0]['to'] == 960


async def test_service_schedule_v2_400(
        taxi_eats_restapp_places,
        mock_authorizer_400,
        mock_eats_service_schedule,
):
    place_id = 'Nan'
    partner_id = 1
    response = await request_proxy_service_schedule(
        taxi_eats_restapp_places, partner_id, place_id,
    )
    assert response.status_code == 400


async def test_service_schedule_v2_403(
        taxi_eats_restapp_places,
        mock_authorizer_forbidden,
        mock_eats_service_schedule,
):
    place_id = 47
    partner_id = 1
    response = await request_proxy_service_schedule(
        taxi_eats_restapp_places, partner_id, place_id,
    )
    assert response.status_code == 403


async def test_service_schedule_v2_404(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_service_schedule,
):
    place_id = 43
    partner_id = 1
    response = await request_proxy_service_schedule(
        taxi_eats_restapp_places, partner_id, place_id,
    )
    assert response.status_code == 404
