from .. import utils_v2


async def test_failed_success(
        taxi_cargo_claims, state_controller, get_default_headers,
):
    claim_info = await state_controller.apply(
        target_status='ready_for_approval',
    )
    claim_id = claim_info.claim_id
    response = await taxi_cargo_claims.post(
        f'/v2/processing/update-status/failed',
        params={'claim_id': claim_id},
        json={},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    claim = await utils_v2.get_claim(claim_id, taxi_cargo_claims)
    assert claim['status'] == 'failed'


async def test_failed_409(
        taxi_cargo_claims, state_controller, get_default_headers,
):
    claim_info = await state_controller.apply(target_status='cancelled')
    claim_id = claim_info.claim_id
    response = await taxi_cargo_claims.post(
        f'/v2/processing/update-status/failed',
        params={'claim_id': claim_id},
        json={},
        headers=get_default_headers(),
    )
    assert response.status_code == 409
    claim = await utils_v2.get_claim(claim_id, taxi_cargo_claims)
    assert claim['status'] == 'cancelled'


async def test_failed_ignore_terminal(
        taxi_cargo_claims, state_controller, get_default_headers,
):
    claim_info = await state_controller.apply(target_status='cancelled')
    claim_id = claim_info.claim_id
    response = await taxi_cargo_claims.post(
        f'/v2/processing/update-status/failed',
        params={'claim_id': claim_id},
        json={'ignore_terminal': True},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    claim = await utils_v2.get_claim(claim_id, taxi_cargo_claims)
    assert claim['status'] == 'cancelled'


async def test_failed_terminal_status_procaas_event(
        taxi_cargo_claims,
        state_controller,
        get_default_headers,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        procaas_send_settings,
        pgsql,
        default_brand_id,
):
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()
    await procaas_send_settings()

    claim_info = await state_controller.apply(
        target_status='ready_for_approval',
    )
    claim_id = claim_info.claim_id
    response = await taxi_cargo_claims.post(
        f'/v2/processing/update-status/failed',
        params={'claim_id': claim_id},
        json={},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    claim = await utils_v2.get_claim(claim_id, taxi_cargo_claims)
    assert claim['status'] == 'failed'

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        SELECT id, payload FROM cargo_claims.processing_events
        WHERE item_id = '{claim_id}'
        """,
    )

    data = list(cursor)
    assert len(data) == 4
    (new_index, new_payload) = data[0]
    assert new_index == 1
    assert new_payload == {
        'data': {
            'claim_uuid': claim_id,
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'is_terminal': False,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': 'new',
    }

    (estim_index, estim_payload) = data[1]
    assert estim_index == 2
    assert 'claim_revision' in estim_payload['data']
    del estim_payload['data']['claim_revision']
    assert estim_payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'phoenix_claim': False,
            'is_terminal': False,
            'current_point_id': 1,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': 'estimating',
    }

    (roa_index, roa_payload) = data[2]
    assert roa_index == 3
    assert 'claim_revision' in roa_payload['data']
    del roa_payload['data']['claim_revision']
    assert roa_payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'phoenix_claim': False,
            'is_terminal': False,
            'current_point_id': 1,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': 'ready_for_approval',
    }

    (terminal_index, terminal_payload) = data[3]
    assert terminal_index == 4
    assert 'claim_revision' in terminal_payload['data']
    del terminal_payload['data']['claim_revision']
    assert terminal_payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'phoenix_claim': False,
            'is_terminal': True,
            'resolution': 'failed',
            'route_points': [],
            'current_point_id': 1,
            'skip_client_notify': False,
            'custom_context': {
                'brand_id': default_brand_id,
                'some_key1': 'some_value',
                'some_key2': 123,
            },
            'zone_id': 'moscow',
        },
        'kind': 'status-change-succeeded',
        'status': 'failed',
    }
