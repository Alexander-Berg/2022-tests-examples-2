import pytest


async def test_promo_disable_204(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):
    @mockserver.json_handler('/eats-core/v1/places/promo/disable')
    def _mock_sessions(req):
        return mockserver.make_response(status=200, json={'isSuccess': True})

    url = '/4.0/restapp-front/promo/v1/promo/disable'
    body = {'id': 1}
    headers = {'X-YaEda-PartnerId': '1', 'Content-type': 'application/json'}
    extra = {'json': body, 'headers': headers}

    response = await taxi_eats_restapp_promo.post(url, **extra)
    assert response.status_code == 204


async def test_promo_disable_404_if_core_response_404(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):
    @mockserver.json_handler('/eats-core/v1/places/promo/disable')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=404,
            json={'isSuccess': False, 'statusCode': 404, 'type': 'error'},
        )

    url = '/4.0/restapp-front/promo/v1/promo/disable'
    body = {'id': 1}
    headers = {'X-YaEda-PartnerId': '1', 'Content-type': 'application/json'}
    extra = {'json': body, 'headers': headers}

    response = await taxi_eats_restapp_promo.post(url, **extra)
    assert response.status_code == 404


async def test_promo_disable_400_if_core_response_400(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):
    url = '/4.0/restapp-front/promo/v1/promo/disable'
    body = {'id': 1}
    headers = {'X-YaEda-PartnerId': '1', 'Content-type': 'application/json'}
    extra = {'json': body, 'headers': headers}

    @mockserver.json_handler('/eats-core/v1/places/promo/disable')
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

    response = await taxi_eats_restapp_promo.post(url, **extra)
    assert response.status_code == 400


@pytest.mark.experiments3(filename='switching_to_new_platform.json')
@pytest.mark.experiments3(filename='promos_checks_settings.json')
@pytest.mark.parametrize(
    'expected_status, promo_id',
    [
        pytest.param(400, 1, id='found'),
        pytest.param(403, 1, id='no access'),
        pytest.param(204, 1111, id='not_found, old path'),
    ],
)
async def test_promo_disable_new_platform(
        taxi_eats_restapp_promo, mockserver, expected_status, promo_id,
):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_user_access_check(request):
        if expected_status == 403:
            return mockserver.make_response(
                status=403,
                json={
                    'code': '403',
                    'message': 'Forbidden',
                    'place_ids': request.json['place_ids'],
                },
            )
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/eats-core/v1/places/promo/disable')
    def _mock_sessions(req):
        return mockserver.make_response(status=200, json={'isSuccess': True})

    url = '/4.0/restapp-front/promo/v1/promo/disable'
    body = {'id': promo_id}
    headers = {'X-YaEda-PartnerId': '1', 'Content-type': 'application/json'}
    extra = {'json': body, 'headers': headers}

    response = await taxi_eats_restapp_promo.post(url, **extra)
    assert response.status_code == expected_status


async def test_promo_disable_403_if_authorizer_response_403(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_403,
):
    url = '/4.0/restapp-front/promo/v1/promo/disable'
    body = {'id': 1}
    headers = {'X-YaEda-PartnerId': '1', 'Content-type': 'application/json'}
    extra = {'json': body, 'headers': headers}

    response = await taxi_eats_restapp_promo.post(url, **extra)
    assert response.status_code == 403


async def test_promo_disable_400_if_authorizer_response_error(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_400,
):
    url = '/4.0/restapp-front/promo/v1/promo/disable'
    body = {'id': 1}
    headers = {'X-YaEda-PartnerId': '1', 'Content-type': 'application/json'}
    extra = {'json': body, 'headers': headers}

    response = await taxi_eats_restapp_promo.post(url, **extra)
    assert response.status_code == 400
