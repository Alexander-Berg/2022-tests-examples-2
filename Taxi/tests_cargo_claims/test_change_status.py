import pytest

DEFAULT_REQUEST_JSON = {'version': 1}

CANCEL_REQUEST_JSON = {'version': 1, 'cancel_state': 'free'}

TAXI_ORDER_ID_REQUEST_JSON = {
    'taxi_order_id': 'taxi_order_id_1',
    'taxi_user_id': 'taxi_user_id_1',
}

MARK_CANCEL_BY_TAXI_REQUEST = {
    'taxi_order_id': 'taxi_order_id_1',
    'reason': 'some_reason',
    'lookup_version': 1,
}


@pytest.mark.parametrize(
    'handle,expected_status,status,json,skip_emergency_notify',
    [
        (
            'api/integration/v2/claims/accept',
            'accepted',
            'ready_for_approval',
            DEFAULT_REQUEST_JSON,
            False,
        ),
        (
            'api/integration/v2/claims/cancel',
            'cancelled',
            'new',
            CANCEL_REQUEST_JSON,
            False,
        ),
        (
            'api/integration/v2/claims/cancel',
            'cancelled',
            'new',
            CANCEL_REQUEST_JSON,
            False,
        ),
        (
            'api/integration/v2/claims/accept',
            'accepted',
            'ready_for_approval',
            DEFAULT_REQUEST_JSON,
            False,
        ),
        (
            'api/integration/v2/claims/cancel',
            'cancelled',
            'new',
            CANCEL_REQUEST_JSON,
            False,
        ),
        (
            'api/integration/v2/claims/cancel',
            'cancelled',
            'new',
            CANCEL_REQUEST_JSON,
            False,
        ),
        (
            'v1/claims/mark/estimate-start',
            'estimating',
            'new',
            DEFAULT_REQUEST_JSON,
            False,
        ),
    ],
)
async def test_change(
        taxi_cargo_claims,
        stq,
        state_controller,
        get_default_headers,
        pgsql,
        mock_create_event,
        skip_emergency_notify: bool,
        handle: str,
        expected_status: str,
        status: str,
        json: dict,
):
    mock_create_event()
    state_controller.set_options(skip_emergency_notify=skip_emergency_notify)
    claim_info = await state_controller.apply(target_status=status)
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        '%s?claim_id=%s' % (handle, claim_id),
        json=json,
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    new_claim_info = await state_controller.get_claim_info()
    assert new_claim_info.current_state.status == expected_status

    if handle in (
            'api/integration/v2/claims/accept',
            'api/integration/v2/claims/accept',
    ):
        response = await taxi_cargo_claims.post(
            '%s?claim_id=%s' % (handle, claim_id),
            json=json,
            headers=get_default_headers(),
        )
        assert response.status_code == 200
    elif status != 'performer_found':
        assert stq.cargo_claims_documents_store.times_called == 0
    elif status != 'cancelled':
        assert stq.cargo_claims_send_cancel_sms.times_called == 0


# TODO(umed): fix as part of https://st.yandex-team.ru/CARGODEV-10906
@pytest.mark.parametrize(
    'handle, extra_kwargs',
    [
        ('api/integration/v2/claims/accept', {}),
        # ('api/integration/v2/claims/cancel', {'cancel_state': 'free'}),
        ('api/integration/v2/claims/accept', {}),
        # ('api/integration/v2/claims/cancel', {'cancel_state': 'free'}),
        ('v1/claims/mark/estimate-start', {}),
    ],
)
async def test_old_version(
        taxi_cargo_claims,
        create_default_claim,
        get_default_request,
        get_default_headers,
        mock_create_event,
        handle,
        extra_kwargs,
):
    mock_create_event()
    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/edit',
        params={'claim_id': create_default_claim.claim_id, 'version': 1},
        json=get_default_request(),
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    response = await taxi_cargo_claims.post(
        '%s?claim_id=%s' % (handle, create_default_claim.claim_id),
        json={'version': 1, **extra_kwargs},
        headers=get_default_headers(),
    )
    assert response.status_code == 409


@pytest.mark.parametrize(
    'handle,status,json',
    [
        (
            'api/integration/v2/claims/accept',
            'estimating',
            DEFAULT_REQUEST_JSON,
        ),
        (
            'api/integration/v2/claims/accept',
            'estimating',
            DEFAULT_REQUEST_JSON,
        ),
        ('v1/claims/mark/estimate-start', 'accepted', DEFAULT_REQUEST_JSON),
    ],
)
async def test_version_inappropriate_status(
        taxi_cargo_claims,
        state_controller,
        get_default_headers,
        mock_create_event,
        pgsql,
        handle: str,
        status: str,
        json: dict,
):
    mock_create_event()
    claim_info = await state_controller.apply(target_status=status)
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        '%s?claim_id=%s' % (handle, claim_id),
        json=json,
        headers=get_default_headers(),
    )
    assert response.status_code == 409


# TODO(umed): fix as part of https://st.yandex-team.ru/CARGODEV-10906
@pytest.mark.parametrize(
    'handle, extra_kwargs',
    [
        ('api/integration/v2/claims/accept', {}),
        # ('api/integration/v2/claims/cancel', {'cancel_state': 'free'}),
        ('api/integration/v2/claims/accept', {}),
        # ('api/integration/v2/claims/cancel', {'cancel_state': 'free'}),
    ],
)
async def test_wrong_corp_client_id(
        taxi_cargo_claims,
        state_controller,
        get_default_headers,
        handle,
        extra_kwargs,
):
    claim_info = await state_controller.apply(target_status='estimating')
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        '%s?claim_id=%s' % (handle, claim_id),
        json={'version': 1, **extra_kwargs},
        headers=get_default_headers('01234567890123456789012345678999'),
    )
    assert response.status_code == 404
