import pytest

from . import utils_v2


@pytest.mark.now('2020-01-01T00:00:00Z')
@pytest.mark.parametrize(
    'due,valid',
    [('2020-01-01T01:00:00Z', True), ('2020-02-01T00:00:00Z', False)],
)
async def test_create_due_too_long(
        taxi_cargo_claims,
        get_default_request,
        get_default_headers,
        get_create_request_v2,
        get_default_idempotency_token,
        due,
        valid,
):
    request = get_default_request()
    request['due'] = due
    response = await taxi_cargo_claims.post(
        '/api/integration/v1/claims/create',
        json=request,
        headers=get_default_headers(),
        params={'request_id': get_default_idempotency_token},
    )
    if valid:
        assert response.status_code == 200
    else:
        assert response.status_code == 400
        assert response.json() == {
            'code': 'delay_too_long',
            'message': (
                'Невозможно создать заявку, '
                'т.к. она отложена на слишком большой срок'
            ),
        }


@pytest.mark.now('2020-01-01T00:00:00Z')
@pytest.mark.parametrize(
    'due,valid',
    [('2020-01-01T01:00:00Z', True), ('2020-02-01T00:00:00Z', False)],
)
async def test_edit_due_too_long(
        taxi_cargo_claims,
        get_default_headers,
        get_default_idempotency_token,
        state_controller,
        due,
        valid,
):

    state_controller.handlers().create.request = utils_v2.get_create_request()
    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='new')

    request = utils_v2.get_create_request()
    request['due'] = due
    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/edit',
        params={'claim_id': claim_info.claim_id, 'version': 1},
        json=request,
        headers=get_default_headers(),
    )

    if valid:
        assert response.status_code == 200
    else:
        assert response.status_code == 400
        assert response.json() == {
            'code': 'delay_too_long',
            'message': (
                'Невозможно создать заявку, '
                'т.к. она отложена на слишком большой срок'
            ),
        }


@pytest.mark.now('2020-01-01T15:30:00Z')
@pytest.mark.parametrize(
    'due, valid',
    [('2020-01-01T15:35:00Z', True), ('2020-01-01T15:25:00Z', False)],
)
@pytest.mark.config(
    CARGO_CLAIMS_DELAYED_SETTINGS_BY_CLIENTS={
        '__default__': {
            'max_due_m': 4320,
            'max_active_claim_age_m': 8640,
            'allow_due_in_past': False,
        },
    },
)
async def test_create_due_in_past(
        taxi_cargo_claims,
        get_default_request,
        get_default_headers,
        get_create_request_v2,
        get_default_idempotency_token,
        due,
        valid,
):
    request = get_default_request()
    request['due'] = due
    response = await taxi_cargo_claims.post(
        '/api/integration/v1/claims/create',
        json=request,
        headers=get_default_headers(),
        params={'request_id': get_default_idempotency_token},
    )
    if valid:
        assert response.status_code == 200
    else:
        assert response.status_code == 400
        assert response.json() == {
            'code': 'due_in_past',
            'message': (
                'Невозможно создать заявку, '
                'т.к. указано время подачи курьера в прошлом'
            ),
        }


@pytest.mark.config(
    CARGO_CLAIMS_DELAYED_SETTINGS_BY_CLIENTS={
        '__default__': {
            'max_due_m': 4320,
            'max_active_claim_age_m': 8640,
            'allow_due_in_past': False,
        },
        '01234567890123456789012345678912': {
            'max_due_m': 4320000,
            'max_active_claim_age_m': 8640,
            'allow_due_in_past': False,
        },
    },
)
@pytest.mark.now('2020-01-01T00:00:00Z')
@pytest.mark.parametrize(
    'due,valid',
    [('2020-01-01T01:00:00Z', True), ('2020-01-10T00:00:00Z', True)],
)
async def test_redefine_settings_for_corp(
        taxi_cargo_claims,
        get_default_headers,
        get_default_idempotency_token,
        state_controller,
        due,
        valid,
):

    state_controller.handlers().create.request = utils_v2.get_create_request()
    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='new')

    request = utils_v2.get_create_request()
    request['due'] = due
    response = await taxi_cargo_claims.post(
        f'api/integration/v2/claims/edit',
        params={'claim_id': claim_info.claim_id, 'version': 1},
        json=request,
        headers=get_default_headers(),
    )

    if valid:
        assert response.status_code == 200
    else:
        assert response.status_code == 400
        assert response.json() == {
            'code': 'delay_too_long',
            'message': (
                'Невозможно создать заявку, '
                'т.к. она отложена на слишком большой срок'
            ),
        }
