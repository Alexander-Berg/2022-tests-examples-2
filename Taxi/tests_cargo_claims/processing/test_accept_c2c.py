import pytest


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
async def test_accept_processing_c2c(
        create_default_cargo_c2c_order,
        procaas_send_settings,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        mock_create_event,
        check_processing_stats,
        pgsql,
        run_processing_events,
        testpoint,
        extract_oldest_event_lag,
        config_enabled,
):
    await procaas_send_settings()
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()

    claim = await create_default_cargo_c2c_order()
    mock_create_event()

    @testpoint('send-events-from-stq')
    def test_point(data):
        assert data['event_id']

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
            SELECT id, payload FROM cargo_claims.processing_events
            WHERE item_id = '{claim.claim_id}'
        """,
    )

    data = list(cursor)
    assert len(data) == 3
    (index, payload) = data[0]
    assert index == 1
    assert payload == {
        'data': {
            'claim_uuid': claim.claim_id,
            'is_terminal': False,
            'skip_client_notify': False,
            'claim_origin': 'yandexgo',
        },
        'kind': 'status-change-succeeded',
        'status': 'new',
    }

    (index, payload) = data[2]
    assert index == 3
    assert payload == {
        'data': {
            'claim_version': 1,
            'phoenix_claim': False,
            'claim_revision': 1,
            'accept_language': 'ru',
            'accept_as_create_event': False,
            'is_terminal': False,
            'skip_client_notify': False,
            'claim_origin': 'yandexgo',
            'claim_accepted': True,
            'offer_id': 'cargo-pricing/v1/123',
            'notify_pricing_claim_accepted': True,
        },
        'kind': 'status-change-requested',
        'status': 'accepted',
    }

    if not config_enabled:
        return

    result = await run_processing_events()
    extract_oldest_event_lag(result)

    # 3 events, because stq process all unprocessed_events for item_id
    await check_processing_stats(
        result,
        processed_in_stq=3,
        for_processing_cnt=1,
        failed_cnt=0,
        stq_success=1,
    )
    assert test_point.times_called == 3


@pytest.mark.config(
    CARGO_CLAIMS_DISTLOCK_PROCESSING_EVENTS_SETTINGS={
        'enabled': True,
        'sleep_ms': 50,
        'new_event_chunk_size': 1,
    },
)
async def test_double_accept_processing_c2c(
        create_default_cargo_c2c_order,
        procaas_send_settings,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        mock_create_event,
        pgsql,
):
    await procaas_send_settings()
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()

    claim1 = await create_default_cargo_c2c_order()
    claim2 = await create_default_cargo_c2c_order()
    assert claim1.claim_id == claim2.claim_id
    mock_create_event()

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
            SELECT id, idempotency_token FROM cargo_claims.processing_events
            WHERE item_id = '{claim1.claim_id}'
        """,
    )

    data = list(cursor)
    assert len(data) == 4
    (index_first_accept, idempotency_first_accept) = data[2]
    (index_second_accept, idempotency_second_accept) = data[3]
    # between first and second accept event difference is 2
    # cuz create claim sql query try insert 'new' event to DB,
    # but failed, cuz not unique pkey, but id counter increased, it's ok
    assert index_first_accept == 3  # id for first accept event
    assert index_second_accept == 5  # id for second accept event
    assert idempotency_first_accept == idempotency_second_accept
