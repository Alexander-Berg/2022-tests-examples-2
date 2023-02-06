import pytest


@pytest.fixture
async def _cancel_request(taxi_cargo_claims, get_default_headers):
    async def wrapper(cancel_state, claim_id, corp_client_id=None, version=1):
        params = {'claim_id': claim_id}
        if corp_client_id:
            params['corp_client_id'] = corp_client_id

        return await taxi_cargo_claims.post(
            '/v1/admin/claims/cancel',
            params=params,
            json={
                'version': version,
                'cancel_state': cancel_state,
                'ticket': 'TICKET-1',
                'comment': 'Cancel this',
            },
            headers=get_default_headers(),
        )

    return wrapper


@pytest.mark.parametrize(
    'status', ['new', 'ready_for_approval', 'performer_lookup'],
)
async def test_free_cancel(
        mockserver, state_controller, _cancel_request, status: str,
):
    claim_info = await state_controller.apply(target_status=status)
    claim_id = claim_info.claim_id

    response = await _cancel_request('free', claim_id)
    assert response.status_code == 200
    assert response.json() == {'new_status': 'cancelled'}

    new_claim_info = await state_controller.get_claim_info()

    assert new_claim_info.current_state.status == 'cancelled'


async def test_wrong_corp_client_id(
        mockserver, state_controller, _cancel_request,
):
    claim_info = await state_controller.apply(target_status='new')
    claim_id = claim_info.claim_id

    response = await _cancel_request(
        'free', claim_id, corp_client_id='another_corp_client_id',
    )
    assert response.status_code == 404


async def test_audit_data_saved(
        taxi_cargo_claims, mockserver, state_controller, _cancel_request,
):
    claim_info = await state_controller.apply(target_status='new')
    claim_id = claim_info.claim_id

    response = await _cancel_request('free', claim_id)
    assert response.status_code == 200

    # check audit
    response = await taxi_cargo_claims.post(
        'v2/admin/claims/full', params={'claim_id': claim_id},
    )
    assert response.status_code == 200
    last_history = response.json()['history'][-1]

    assert last_history['comment'] == 'Cancel this'
    assert last_history['ticket'] == 'TICKET-1'


async def test_dragon_order(
        taxi_cargo_claims,
        create_segment_with_performer,
        get_db_segment_ids,
        _cancel_request,
):
    creator = await create_segment_with_performer()

    response = await _cancel_request('paid', creator.claim_id)
    assert response.status_code == 200

    segment_ids = await get_db_segment_ids()
    response = await taxi_cargo_claims.post(
        '/v1/segments/bulk-info',
        json={
            'segment_ids': [
                {'segment_id': segment_id} for segment_id in segment_ids
            ],
        },
    )
    assert response.status_code == 200

    for segment in response.json()['segments']:
        assert segment['status'] == 'cancelled'
        assert segment['resolution'] == 'cancelled_by_user'
        assert segment['points_user_version'] > 1

        for point in segment['points']:
            assert point['visit_status'] == 'skipped'
            assert point['resolution']['is_skipped']
            assert point['is_resolved']
            assert point['revision'] > 1


async def test_dragon_audit(
        taxi_cargo_claims,
        create_segment_with_performer,
        get_db_segment_ids,
        _cancel_request,
):
    creator = await create_segment_with_performer()

    response = await _cancel_request('paid', creator.claim_id)
    assert response.status_code == 200

    # check audit
    response = await taxi_cargo_claims.post(
        'v2/admin/claims/full', params={'claim_id': creator.claim_id},
    )
    assert response.status_code == 200
    last_history = response.json()['history'][-1]

    assert last_history['comment'] == 'Cancel this'
    assert last_history['ticket'] == 'TICKET-1'
