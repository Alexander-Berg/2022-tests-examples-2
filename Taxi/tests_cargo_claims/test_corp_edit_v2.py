import pytest

from . import utils_v2


NEW_ITEM = {
    'title': 'item title 3',
    'extra_id': '3',
    'size': {'length': 10.0, 'width': 5.8, 'height': 0.5},
    'cost_value': '53.00',
    'cost_currency': 'RUB',
    'weight': 3.7,
    'pickup_point': 1,
    'droppof_point': 4,
    'quantity': 1,
}

NEW_POINT = {
    'point_id': 4,
    'visit_order': 4,
    'address': {
        'fullname': '4',
        'coordinates': [37.8, 55.4],
        'country': '4',
        'city': '4',
        'street': '4',
        'building': '4',
    },
    'contact': {
        'phone': '+79999999994',
        'name': 'string',
        'email': '4@yandex.ru',
    },
    'type': 'destination',
}


async def create_claim_for_edit(state_controller, request: dict):
    state_controller.handlers().create.request = request
    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='new')
    return claim_info.claim_id


async def test_simple(
        taxi_cargo_claims,
        state_controller,
        get_default_headers,
        check_v2_response,
):
    create_request = utils_v2.get_create_request()
    create_request['items'].append(NEW_ITEM)
    create_request['route_points'][3] = NEW_POINT

    claim_id = await create_claim_for_edit(state_controller, create_request)

    # Edit claim
    request = utils_v2.get_create_request()
    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/edit',
        params={'claim_id': claim_id, 'version': 1},
        json=request,
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    new_claim_info = await state_controller.get_claim_info()

    check_v2_response(
        request=request, response=new_claim_info.claim_full_response,
    )

    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/edit',
        params={'claim_id': claim_id, 'version': 501},
        json=request,
        headers=get_default_headers(),
    )
    assert response.status_code == 400


async def test_unknow_zone_id(
        taxi_cargo_claims,
        get_default_headers,
        get_default_idempotency_token,
        state_controller,
        pgsql,
):

    create_request = utils_v2.get_create_request()
    claim_id = await create_claim_for_edit(state_controller, create_request)

    request = utils_v2.get_create_request()
    request['route_points'][0]['address']['coordinates'] = [1, 1]
    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/edit',
        params={'claim_id': claim_id, 'version': 1},
        json=request,
        headers=get_default_headers(),
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'unknown_zone',
        'message': 'Unknown zone for point A',
    }


async def test_without_coord(
        taxi_cargo_claims,
        state_controller,
        get_default_headers,
        get_default_idempotency_token,
        yamaps,
        load_json,
):
    yamaps_response = load_json('yamaps_response.json')
    coordinates = yamaps_response['geometry']

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects_callback(request):
        return [yamaps_response]

    create_request = utils_v2.get_create_request()
    claim_id = await create_claim_for_edit(state_controller, create_request)

    request = utils_v2.get_create_request()
    del request['route_points'][0]['address']['coordinates']

    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/edit',
        params={'claim_id': claim_id, 'version': 1},
        json=request,
        headers=get_default_headers(),
    )

    assert response.status_code == 200
    assert (
        response.json()['route_points'][0]['address']['coordinates']
        == coordinates
    )
    for i in range(1, 4):
        assert (
            response.json()['route_points'][i]['address']['coordinates']
            == request['route_points'][i]['address']['coordinates']
        )


async def test_undefined_address(
        taxi_cargo_claims,
        state_controller,
        get_default_headers,
        get_default_idempotency_token,
        yamaps,
):
    create_request = utils_v2.get_create_request()
    claim_id = await create_claim_for_edit(state_controller, create_request)

    request = utils_v2.get_create_request()
    del request['route_points'][0]['address']['coordinates']
    request['route_points'][0]['address']['fullname'] = 'abracadabra'

    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/edit',
        params={'claim_id': claim_id, 'version': 1},
        json=request,
        headers=get_default_headers(),
    )

    assert response.status_code == 400
    assert (
        response.json()['message']
        == 'Не удалось преобразовать адрес abracadabra в координаты: '
        'проверьте корректность адреса или попробуйте'
        ' указать координаты вручную'
    )


@pytest.mark.parametrize(
    'yamaps_precision, config_precision, code',
    [
        ('NUMBER', 'Number', 200),
        ('RANGE', 'Number', 400),
        ('NUMBER', 'Range', 200),
    ],
)
async def test_geocoder_precision(
        taxi_cargo_claims,
        state_controller,
        get_default_headers,
        get_default_idempotency_token,
        yamaps,
        load_json,
        taxi_config,
        yamaps_precision,
        config_precision,
        code,
):
    taxi_config.set_values(
        {'CARGO_CLAIMS_GEOCODER_PRECISION': {'precision': config_precision}},
    )

    yamaps_response = load_json('yamaps_response.json')
    yamaps_response['geocoder']['precision'] = yamaps_precision

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects_callback(request):
        return [yamaps_response]

    create_request = utils_v2.get_create_request()
    claim_id = await create_claim_for_edit(state_controller, create_request)

    request = utils_v2.get_create_request()
    del request['route_points'][0]['address']['coordinates']

    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/edit',
        params={'claim_id': claim_id, 'version': 1},
        json=request,
        headers=get_default_headers(),
    )

    assert response.status_code == code
