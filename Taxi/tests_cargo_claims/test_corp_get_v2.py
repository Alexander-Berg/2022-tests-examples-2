import pytest

from . import utils_v2


async def test_get_not_found(taxi_cargo_claims, get_default_headers):
    response = await taxi_cargo_claims.post(
        'api/integration/v2/claims/info?claim_id=some_not_found',
        headers=get_default_headers(),
    )
    assert response.status_code == 404


async def test_bad_corp_client(
        taxi_cargo_claims, get_default_headers, state_controller,
):
    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(
        target_status='new', next_point_order=1,
    )

    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/info?claim_id={claim_info.claim_id}',
        headers=get_default_headers('other_corp_id0123456789012345678'),
    )
    assert response.status_code == 404


async def test_info_v2(
        taxi_cargo_claims, get_default_headers, state_controller, remove_dates,
):
    state_controller.use_create_version('v2')

    request = utils_v2.get_create_request()
    state_controller.handlers().create.request = request
    claim_info = await state_controller.apply(
        target_status='ready_for_approval',
    )

    claim_id = claim_info.claim_id
    point_ids = utils_v2.get_point_id_to_claim_point_id(
        request, claim_info.claim_full_response,
    )

    expected_response = utils_v2.get_default_response_v2(
        claim_id, point_ids, with_offer=True,
    )

    expected_response['status'] = 'ready_for_approval'
    expected_response['initiator_yandex_login'] = 'abacaba'

    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/info?claim_id={claim_id}',
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    json = response.json()
    remove_dates(json)
    assert json == expected_response


async def test_same_day_data(
        taxi_cargo_claims,
        get_default_headers,
        state_controller,
        remove_dates,
        mock_sdd_delivery_intervals,
):
    state_controller.use_create_version('v2')

    request = utils_v2.get_create_request()
    del request['client_requirements']
    interval = mock_sdd_delivery_intervals.response['available_intervals'][0]
    request['same_day_data'] = {'delivery_interval': interval}
    state_controller.handlers().create.request = request
    claim_info = await state_controller.apply(
        target_status='ready_for_approval',
    )

    claim_id = claim_info.claim_id
    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/info?claim_id={claim_id}',
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    json = response.json()
    assert json['same_day_data'] == {'delivery_interval': interval}


async def test_same_day_without_client_requirements(
        taxi_cargo_claims,
        get_default_headers,
        state_controller,
        remove_dates,
        mock_sdd_delivery_intervals,
):
    state_controller.use_create_version('v2')

    request = utils_v2.get_create_request()
    del request['client_requirements']
    interval = mock_sdd_delivery_intervals.response['available_intervals'][0]
    request['same_day_data'] = {'delivery_interval': interval}
    state_controller.handlers().create.request = request
    claim_info = await state_controller.apply(
        target_status='ready_for_approval',
    )

    claim_id = claim_info.claim_id
    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/info?claim_id={claim_id}',
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    json = response.json()
    assert json['same_day_data'] == {'delivery_interval': interval}


@pytest.mark.translations(color={'040001': {'en': 'black!'}})
@pytest.mark.config(CARGO_CLAIMS_LOCALIZE_PERFORMER_CAR_COLOR=True)
async def test_localize_car_color(
        taxi_cargo_claims, get_default_headers, state_controller, remove_dates,
):
    state_controller.use_create_version('v2')
    state_controller.set_options(car_color='черный', car_color_hex='040001')

    request = utils_v2.get_create_request()
    state_controller.handlers().create.request = request
    claim_info = await state_controller.apply(target_status='performer_found')

    claim_id = claim_info.claim_id
    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/info?claim_id={claim_id}',
        headers={**get_default_headers(), 'Accept-Language': 'en'},
    )
    assert response.status_code == 200

    json = response.json()
    assert json['performer_info']['car_color'] == 'black!'
