import pytest


@pytest.mark.parametrize('has_driver_info', [True, False])
async def test_exchange_init_success(
        taxi_cargo_claims,
        pgsql,
        create_segment_with_performer,
        get_db_segment_ids,
        get_segment,
        state_controller,
        get_current_claim_point,
        has_driver_info,
):
    await create_segment_with_performer()
    claim_info = await state_controller.apply(
        target_status='performer_found', fresh_claim=False,
    )

    current_claim_point = await get_current_claim_point(claim_info.claim_id)
    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]

    json = {
        'last_known_status': 'new',
        'point_id': current_claim_point,
        'idempotency_token': '100500',
    }
    if has_driver_info:
        json['driver'] = {
            'park_id': 'some_park',
            'driver_profile_id': 'some_driver',
            'taximeter_app': {
                'version': '9.09',
                'version_type': 'dev',
                'platform': 'android',
            },
        }
    response = await taxi_cargo_claims.post(
        '/v1/segments/exchange/init',
        params={'segment_id': segment_id},
        json=json,
        headers={'X-Real-IP': '12.34.56.78'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'new_status': 'pickup_confirmation',
        'new_claim_status': 'ready_for_pickup_confirmation',
    }

    segment = await get_segment(segment_id)
    assert segment['status'] == 'ready_for_pickup_confirmation'


async def test_exchange_init_bad_point(
        taxi_cargo_claims,
        create_segment,
        get_db_segment_ids,
        state_controller,
):
    await create_segment()
    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]
    await state_controller.apply(
        target_status='performer_found', fresh_claim=False,
    )

    response = await taxi_cargo_claims.post(
        '/v1/segments/exchange/init',
        params={'segment_id': segment_id},
        json={
            'last_known_status': 'new',
            'idempotency_token': '100500',
            'point_id': 1300,
            'driver': {
                'park_id': 'some_park',
                'driver_profile_id': 'some_driver',
                'taximeter_app': {
                    'version': '9.09',
                    'version_type': 'dev',
                    'platform': 'android',
                },
            },
        },
        headers={'X-Real-IP': '12.34.56.78'},
    )

    assert response.status_code == 409


@pytest.mark.parametrize(
    'last_known_status, expected_response_code',
    [('delivering', 409), (None, 200)],
)
async def test_no_last_known_status_validation_for_batch(
        taxi_cargo_claims,
        create_segment_with_performer,
        state_controller,
        get_current_claim_point,
        get_db_segment_ids,
        last_known_status,
        expected_response_code,
):
    await create_segment_with_performer()
    claim_info = await state_controller.apply(
        target_status='performer_found', fresh_claim=False,
    )
    current_claim_point = await get_current_claim_point(claim_info.claim_id)
    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]

    request_body = {
        'idempotency_token': '100500',
        'point_id': current_claim_point,
        'driver': {
            'park_id': 'some_park',
            'driver_profile_id': 'some_driver',
            'taximeter_app': {
                'version': '9.09',
                'version_type': 'dev',
                'platform': 'android',
            },
        },
    }
    if last_known_status:
        request_body['last_known_status'] = last_known_status
    response = await taxi_cargo_claims.post(
        '/v1/segments/exchange/init',
        params={'segment_id': segment_id},
        json=request_body,
        headers={'X-Real-IP': '12.34.56.78'},
    )
    assert response.status_code == expected_response_code


async def test_user_pickup_code(
        taxi_cargo_claims,
        pgsql,
        create_segment_with_performer,
        get_segment_id,
        get_segment,
        state_controller,
        get_current_claim_point,
        mockserver,
):
    await create_segment_with_performer(pickup_code='123456')
    claim_info = await state_controller.apply(
        target_status='performer_found', fresh_claim=False,
    )
    current_claim_point = await get_current_claim_point(claim_info.claim_id)

    @mockserver.json_handler('/esignature-issuer/v1/signatures/create')
    def signature_create(request):
        assert request.json['user_code'] == '123456'
        return mockserver.make_response('{}', status=200)

    segment_id = await get_segment_id()
    response = await taxi_cargo_claims.post(
        '/v1/segments/exchange/init',
        params={'segment_id': segment_id},
        json={
            'last_known_status': 'new',
            'point_id': current_claim_point,
            'idempotency_token': '100500',
            'driver': {
                'park_id': 'some_park',
                'driver_profile_id': 'some_driver',
                'taximeter_app': {
                    'version': '9.09',
                    'version_type': 'dev',
                    'platform': 'android',
                },
            },
        },
        headers={'X-Real-IP': '12.34.56.78'},
    )
    assert response.status_code == 200

    assert signature_create.times_called == 1
