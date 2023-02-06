import pytest

from testsuite.utils import matching


@pytest.fixture(autouse=True)
async def enable_processing(set_up_processing_exp, get_default_corp_client_id):
    await set_up_processing_exp(
        processing_flow='enabled',
        corp_client_id=get_default_corp_client_id,
        recipient_phone='+72222222222',
    )


async def test_create_segment_200(
        taxi_cargo_claims,
        state_controller,
        get_default_corp_client_id,
        get_default_accept_language,
        get_default_headers,
        mock_create_event,
):

    claim_info = await state_controller.apply(target_status='accepted')
    create_event = mock_create_event(
        item_id=matching.any_string,
        idempotency_token=matching.any_string,
        queue='segment',
        event={
            'kind': 'created',
            'data': {
                'claim_uuid': claim_info.claim_id,
                'corp_client_id': get_default_corp_client_id,
            },
        },
    )

    response = await taxi_cargo_claims.post(
        '/v2/processing/segments/create',
        headers=get_default_headers(),
        params={'claim_id': claim_info.claim_id},
    )
    assert response.status_code == 200
    created_segments = response.json()['created_segments']
    segment_id = created_segments[0]['segment_id']
    assert len(created_segments) == 1
    assert segment_id == claim_info.claim_id
    assert create_event.times_called == 1

    response = await taxi_cargo_claims.post(
        '/v1/segments/info',
        headers=get_default_headers(),
        params={'segment_id': segment_id},
    )
    segment = response.json()
    assert response.status_code == 200
    assert segment['claim_id'] == claim_info.claim_id
    assert len(segment['points']) == len(
        claim_info.claim_full_response['route_points'],
    )
    assert segment['processing_flow'] == 'enabled'

    # test idempotency
    create_event = mock_create_event(
        item_id=segment_id,
        idempotency_token=segment_id,
        queue='segment',
        event={
            'kind': 'created',
            'data': {
                'claim_uuid': claim_info.claim_id,
                'corp_client_id': get_default_corp_client_id,
            },
        },
    )
    response = await taxi_cargo_claims.post(
        '/v2/processing/segments/create',
        headers=get_default_headers(),
        params={'claim_id': claim_info.claim_id},
    )
    assert response.status_code == 200
    assert create_event.times_called == 1

    response = await taxi_cargo_claims.post(
        '/v1/segments/info',
        headers=get_default_headers(),
        params={'segment_id': segment_id},
    )
    assert response.json() == segment


@pytest.mark.skip('TODO: fix in CARGODEV-11356')
async def test_create_segment_409(
        taxi_cargo_claims,
        state_controller,
        get_default_corp_client_id,
        get_default_accept_language,
        get_default_headers,
):
    claim_info = await state_controller.apply(target_status='performer_found')

    response = await taxi_cargo_claims.post(
        '/v2/processing/segments/create',
        headers=get_default_headers(),
        params={'claim_id': claim_info.claim_id},
    )
    assert response.status_code == 409


async def test_create_segment_404(
        taxi_cargo_claims,
        state_controller,
        get_default_corp_client_id,
        get_default_accept_language,
        get_default_headers,
):
    claim_info = await state_controller.apply(target_status='accepted')

    response = await taxi_cargo_claims.post(
        '/v2/processing/segments/create',
        headers=get_default_headers(),
        params={'claim_id': claim_info.claim_id[:-2] + 'xx'},
    )
    assert response.status_code == 404
