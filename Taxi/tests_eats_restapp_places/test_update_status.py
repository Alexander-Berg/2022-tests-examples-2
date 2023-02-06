async def request_proxy_update_status(
        taxi_eats_restapp_places, partner_id, place_id,
):
    url = '/4.0/restapp-front/places/v1/update?place_id={}'.format(place_id)

    headers = {'X-YaEda-PartnerId': str(partner_id)}
    extra = {'headers': headers}

    return await taxi_eats_restapp_places.get(url, **extra)


async def test_get_update_status_ready(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_update_status_200,
):
    partner_id = 1
    place_id = 42

    response = await request_proxy_update_status(
        taxi_eats_restapp_places, partner_id, place_id,
    )

    assert response.status_code == 200
    assert response.json()['result'][0] == 'Place updating is not in progress'
    assert response.json()['status'] == 'ready'


async def test_get_update_status_progress(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_update_status_202,
):
    partner_id = 1
    place_id = 42

    response = await request_proxy_update_status(
        taxi_eats_restapp_places, partner_id, place_id,
    )

    assert response.status_code == 200
    assert response.json()['result'][0] == 'Place updating is in progress'
    assert response.json()['status'] == 'progress'


async def test_get_update_status_403(
        taxi_eats_restapp_places,
        mock_authorizer_forbidden,
        mock_eats_update_status_404,
):
    partner_id = 1
    place_id = 49

    response = await request_proxy_update_status(
        taxi_eats_restapp_places, partner_id, place_id,
    )

    assert response.status_code == 403
    assert response.json()['code'] == '403'


async def test_get_update_status_404(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_update_status_404,
):
    partner_id = 1
    place_id = 42

    response = await request_proxy_update_status(
        taxi_eats_restapp_places, partner_id, place_id,
    )

    assert response.status_code == 404
    assert response.json()['code'] == '404'


async def request_proxy_update_v2_status(
        taxi_eats_restapp_places, partner_id, place_id,
):
    url = '/4.0/restapp-front/places/v2/update?place_id={}'.format(place_id)

    headers = {'X-YaEda-PartnerId': str(partner_id)}
    extra = {'headers': headers}

    return await taxi_eats_restapp_places.get(url, **extra)


async def test_get_update_status_v2_ready(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_update_status_200,
):
    partner_id = 1
    place_id = 42

    response = await request_proxy_update_v2_status(
        taxi_eats_restapp_places, partner_id, place_id,
    )

    assert response.status_code == 200
    assert response.json()['result'][0] == 'Place updating is not in progress'
    assert response.json()['status'] == 'ready'


async def test_get_update_status_v2_progress(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_update_status_202,
):
    partner_id = 1
    place_id = 42

    response = await request_proxy_update_v2_status(
        taxi_eats_restapp_places, partner_id, place_id,
    )

    assert response.status_code == 200
    assert response.json()['result'][0] == 'Place updating is in progress'
    assert response.json()['status'] == 'progress'


async def test_get_update_status_v2_403(
        taxi_eats_restapp_places,
        mock_authorizer_forbidden,
        mock_eats_update_status_404,
):
    partner_id = 1
    place_id = 49

    response = await request_proxy_update_v2_status(
        taxi_eats_restapp_places, partner_id, place_id,
    )

    assert response.status_code == 403
    assert response.json()['code'] == '403'


async def test_get_update_status_v2_404(
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_eats_update_status_404,
):
    partner_id = 1
    place_id = 42

    response = await request_proxy_update_v2_status(
        taxi_eats_restapp_places, partner_id, place_id,
    )

    assert response.status_code == 404
    assert response.json()['code'] == '404'
