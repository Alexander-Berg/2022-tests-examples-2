import pytest

from .. import utils_v2


@pytest.mark.parametrize(
    ['config_enabled'],
    (
        pytest.param(
            True,
            marks=pytest.mark.config(
                CARGO_CLAIMS_DISTLOCK_PROCESSING_EVENTS_SETTINGS={
                    'enabled': True,
                    'sleep_ms': 50,
                    'new_event_chunk_size': 1,
                },
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                CARGO_CLAIMS_DISTLOCK_PROCESSING_EVENTS_SETTINGS={
                    'enabled': False,
                    'sleep_ms': 50,
                    'new_event_chunk_size': 1,
                },
            ),
        ),
    ),
)
@pytest.mark.parametrize('processing_flow', ['disabled', 'enabled'])
async def test_processing_flow(
        taxi_cargo_claims,
        state_controller,
        set_up_processing_exp,
        get_default_corp_client_id,
        get_default_accept_language,
        get_default_headers,
        mock_create_event,
        config_enabled,
        procaas_send_settings,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        check_processing_stats,
        pgsql,
        run_processing_events,
        testpoint,
        extract_oldest_event_lag,
        processing_flow: str,
):
    await procaas_send_settings()
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()

    await set_up_processing_exp(
        processing_flow=processing_flow,
        corp_client_id=get_default_corp_client_id,
        recipient_phone='+72222222222',
    )

    claim_info = await state_controller.apply(
        target_status='ready_for_approval',
    )
    mock_create_event()

    @testpoint('send-events-from-stq')
    def test_point(data):
        assert data['event_id']

    if processing_flow == 'enabled' and config_enabled:
        cursor = pgsql['cargo_claims'].cursor()
        cursor.execute(
            f"""
            SELECT id, payload FROM cargo_claims.processing_events
            WHERE item_id = '{claim_info.claim_id}'
            """,
        )

        data = list(cursor)
        assert len(data) == 3
        (new_index, new_payload) = data[0]
        assert new_index == 1
        assert new_payload == {
            'data': {
                'claim_uuid': claim_info.claim_id,
                'corp_client_id': '01234567890123456789012345678912',
                'claim_origin': 'api',
                'is_terminal': False,
                'skip_client_notify': False,
            },
            'kind': 'status-change-succeeded',
            'status': 'new',
        }
        result = await run_processing_events()
        extract_oldest_event_lag(result)
        await check_processing_stats(
            result,
            processed_in_stq=3,
            for_processing_cnt=1,
            failed_cnt=0,
            stq_success=1,
        )
        assert test_point.times_called == 3
        test_point.flush()

    create_event = mock_create_event(
        item_id=claim_info.claim_id,
        idempotency_token='accept_1',
        event={
            'kind': 'status-change-requested',
            'status': 'accepted',
            'data': {
                'claim_version': 1,
                'claim_origin': 'api',
                'accept_language': get_default_accept_language,
                'corp_client_id': get_default_corp_client_id,
                'accept_as_create_event': not config_enabled,
                'claim_revision': 3,
                'phoenix_claim': False,
                'is_terminal': False,
                'skip_client_notify': False,
                'claim_accepted': False,
                'notify_pricing_claim_accepted': False,
            },
        },
    )

    assert claim_info.claim_full_response['status'] == 'ready_for_approval'
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/accept',
        headers=get_default_headers(),
        params={'claim_id': claim_info.claim_id},
        json={'version': 1},
    )

    assert create_event.times_called == 0
    assert response.status_code == 200
    if processing_flow == 'enabled' and config_enabled:
        cursor = pgsql['cargo_claims'].cursor()
        cursor.execute(
            f"""
            SELECT id, payload FROM cargo_claims.processing_events
            WHERE item_id = '{claim_info.claim_id}' and is_stq_set IS NOT FALSE
            """,
        )

        data = list(cursor)
        assert len(data) == 1
        (accept_index, accept_payload) = data[0]
        assert accept_index == 4
        assert 'claim_revision' in accept_payload['data']
        del accept_payload['data']['claim_revision']
        assert accept_payload == {
            'data': {
                'corp_client_id': '01234567890123456789012345678912',
                'claim_origin': 'api',
                'claim_version': 1,
                'accept_as_create_event': False,
                'accept_language': 'en-US;q=1, ru;q=0.8',
                'is_terminal': False,
                'phoenix_claim': False,
                'skip_client_notify': False,
                'claim_accepted': False,
                'notify_pricing_claim_accepted': False,
            },
            'kind': 'status-change-requested',
            'status': 'accepted',
        }

        result = await run_processing_events()
        extract_oldest_event_lag(result)
        await check_processing_stats(
            result,
            processed_in_stq=1,
            for_processing_cnt=1,
            failed_cnt=0,
            stq_success=1,
        )
        assert test_point.times_called == 1


@pytest.mark.parametrize(
    'use_smb_api_prefix,' 'expected_phoenix_claim_flag_in_procaas',
    [
        pytest.param(
            True,
            True,
            #
            id='phoenix_claim_for_smb_happy_path',
        ),
        pytest.param(
            False,
            False,
            #
            id='phoenix_claim_for_not_smb_happy_path',
        ),
    ],
)
async def test_cargo_phoenix_claim(
        taxi_cargo_claims,
        taxi_config,
        state_controller,
        set_up_processing_exp,
        get_default_corp_client_id,
        get_default_accept_language,
        get_default_headers,
        procaas_send_settings,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        mock_cargo_corp_up,
        mock_create_event,
        use_smb_api_prefix,
        expected_phoenix_claim_flag_in_procaas,
):
    await procaas_send_settings(is_async=False)
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()

    await set_up_processing_exp(
        processing_flow='enabled',
        corp_client_id=get_default_corp_client_id,
        recipient_phone='+72222222222',
    )
    await taxi_cargo_claims.invalidate_caches()

    if use_smb_api_prefix:
        create_handler = state_controller.handlers().create
        create_handler.headers = get_default_headers()
        create_handler.headers['X-B2B-Client-Storage'] = 'cargo'

    claim_info = await state_controller.apply(
        target_status='ready_for_approval',
    )
    event = {
        'kind': 'status-change-requested',
        'status': 'accepted',
        'data': {
            'claim_version': 1,
            'accept_language': get_default_accept_language,
            'corp_client_id': get_default_corp_client_id,
            'accept_as_create_event': False,
            'claim_revision': 3,
            'claim_origin': 'api',
            'is_terminal': False,
            'claim_accepted': False,
            'phoenix_claim': expected_phoenix_claim_flag_in_procaas,
            'skip_client_notify': False,
            'notify_pricing_claim_accepted': False,
        },
    }

    create_event = mock_create_event(
        item_id=claim_info.claim_id, idempotency_token='accept_1', event=event,
    )
    assert claim_info.claim_full_response['status'] == 'ready_for_approval'
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/accept',
        headers=get_default_headers(),
        params={'claim_id': claim_info.claim_id},
        json={'version': 1},
    )
    assert response.status_code == 200
    assert create_event.times_called == 1


async def test_accept_success(
        taxi_cargo_claims, state_controller, get_default_headers, now,
):
    claim_info = await state_controller.apply(
        target_status='ready_for_approval',
    )
    claim_id = claim_info.claim_id
    response = await taxi_cargo_claims.post(
        f'/v2/processing/update-status/accepted',
        params={'claim_id': claim_id},
        json={
            'version': 1,
            'accept_time': now.strftime('%Y-%m-%dT%H:%M:%S+00:00'),
        },
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    claim = await utils_v2.get_claim(claim_id, taxi_cargo_claims)
    assert claim['status'] == 'accepted'


async def test_accept_409(
        taxi_cargo_claims, state_controller, get_default_headers, now,
):
    claim_info = await state_controller.apply(
        target_status='ready_for_approval',
    )
    claim_id = claim_info.claim_id
    response = await taxi_cargo_claims.post(
        f'/v2/processing/update-status/accepted',
        params={'claim_id': claim_id},
        json={
            'version': 123456,
            'accept_time': now.strftime('%Y-%m-%dT%H:%M:%S+00:00'),
        },
        headers=get_default_headers(),
    )
    assert response.status_code == 409
    claim = await utils_v2.get_claim(claim_id, taxi_cargo_claims)
    assert claim['status'] == 'ready_for_approval'


async def test_idempotency(
        taxi_cargo_claims,
        state_controller,
        get_default_headers,
        now,
        mock_create_event,
        set_up_processing_exp,
        get_default_corp_client_id,
):
    # Claim already in status 'performer_draft'
    # And /accept returns 200 because of idempotency

    await set_up_processing_exp(
        processing_flow='enabled',
        corp_client_id=get_default_corp_client_id,
        recipient_phone='+72222222222',
    )
    create_event = mock_create_event()

    claim_info = await state_controller.apply(target_status='performer_draft')

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/accept',
        headers=get_default_headers(),
        params={'claim_id': claim_info.claim_id},
        json={'version': 1},
    )
    assert response.status_code == 200
    assert create_event.times_called == 0

    claim = await utils_v2.get_claim(claim_info.claim_id, taxi_cargo_claims)
    assert claim['status'] == 'performer_draft'
