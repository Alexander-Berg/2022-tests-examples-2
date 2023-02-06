import pytest

from . import utils_v2


async def create_claim(state_controller):
    state_controller.use_create_version('v2')
    state_controller.handlers().finish_estimate.update_request = (
        _finish_estimate_request
    )
    return await state_controller.apply(target_status='ready_for_approval')


@pytest.mark.parametrize(
    'uri, method, response_getter',
    [
        (
            '/api/integration/v2/claims/info',
            'POST',
            utils_v2.get_default_response_v2,
        ),
        (
            '/api/integration/v2/claims/info',
            'POST',
            utils_v2.get_default_response_v2,
        ),
        ('/v2/claims/full', 'GET', utils_v2.get_default_response_v2_inner),
    ],
)
async def test_get_with_client_class(
        taxi_cargo_claims,
        get_default_headers,
        uri,
        method,
        response_getter,
        state_controller,
):
    claim_info = await create_claim(state_controller)
    internal = uri == '/v2/claims/full'

    response = await taxi_cargo_claims.request(
        method,
        f'{uri}?claim_id={claim_info.claim_id}',
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    cars = response.json()['matched_cars']
    assert len(cars) == 1
    if not internal:
        assert cars[0]['taxi_class'] == 'cargo'
        assert 'client_taxi_class' not in cars[0]
    else:
        assert cars[0]['taxi_class'] == 'cargocorp'
        assert cars[0]['client_taxi_class'] == 'cargo'


async def test_bulk_get(
        taxi_cargo_claims, state_controller, get_default_headers, pgsql,
):
    claim_info = await create_claim(state_controller)
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
            UPDATE cargo_claims.claims
            SET autocancel_reason=\'candidates_empty\',
            admin_cancel_reason=\'folder.reason\'
        """,
    )
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/bulk_info',
        headers=get_default_headers(),
        json={'claim_ids': [claim_info.claim_id]},
    )
    assert response.status_code == 200
    data = response.json()['claims'][0]
    cars = response.json()['claims'][0]['matched_cars']
    assert len(cars) == 1
    assert cars[0]['taxi_class'] == 'cargo'
    assert 'client_taxi_class' not in cars[0]
    assert data['autocancel_reason'] == 'candidates_empty'
    assert data['admin_cancel_reason'] == 'folder.reason'


def _finish_estimate_request(request):
    request['cars'][0]['taxi_class'] = 'cargocorp'
    request['cars'][0]['client_taxi_class'] = 'cargo'
