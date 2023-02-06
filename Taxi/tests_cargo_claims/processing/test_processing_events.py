import pytest


@pytest.mark.pgsql('cargo_claims', files=['insert_events.sql'])
@pytest.mark.config(
    CARGO_CLAIMS_DISTLOCK_PROCESSING_EVENTS_SETTINGS={
        'enabled': True,
        'sleep_ms': 50,
        'new_event_chunk_size': 2,
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_procaas_claim_status_filter',
    consumers=['cargo-claims/procaas'],
    clauses=[],
    default_value={'enabled': True},
    is_config=True,
)
async def test_processing_events(
        mock_create_event,
        run_processing_events,
        check_processing_stats,
        extract_oldest_event_lag,
        procaas_event_kind_filter,
        procaas_claim_status_filter,
        pgsql,
):
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()
    mock_create_event()
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        SELECT
            ne.id,
            ne.is_stq_set
        FROM cargo_claims.processing_events as ne
        WHERE ne.is_stq_set is NULL
        ORDER BY ne.id
    """,
    )
    assert len(cursor.fetchall()) == 5
    result = await run_processing_events()
    extract_oldest_event_lag(result)
    await check_processing_stats(
        result,
        processed_in_stq=2,
        for_processing_cnt=2,
        failed_cnt=0,
        stq_success=1,
    )

    result = await run_processing_events()
    extract_oldest_event_lag(result)
    await check_processing_stats(
        result,
        processed_in_stq=2,
        for_processing_cnt=2,
        failed_cnt=0,
        stq_success=2,
    )

    result = await run_processing_events()
    extract_oldest_event_lag(result)
    await check_processing_stats(
        result,
        processed_in_stq=1,
        for_processing_cnt=1,
        failed_cnt=0,
        stq_success=1,
    )
    result = await run_processing_events()
    extract_oldest_event_lag(result)
    await check_processing_stats(
        result,
        processed_in_stq=0,
        for_processing_cnt=0,
        failed_cnt=0,
        stq_success=0,
    )


@pytest.mark.config(
    CARGO_CLAIMS_DISTLOCK_PROCESSING_EVENTS_SETTINGS={
        'enabled': True,
        'sleep_ms': 50,
        'new_event_chunk_size': 2,
    },
)
async def test_claim_processing_estimating_failed(
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        state_controller,
        taxi_cargo_claims,
        query_processing_events,
):
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()
    claim_info = await state_controller.apply(target_status='estimating')
    claim_id = claim_info.claim_id
    response = await taxi_cargo_claims.post(
        'v1/claims/finish-estimate',
        params={'claim_id': claim_id},
        json={'cars': []},
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': claim_id,
        'status': 'estimating',
        'skip_client_notify': False,
        'user_request_revision': '1',
        'version': 1,
    }

    events = query_processing_events(claim_id)
    assert len(events) == 3
    assert events[2].payload['data'].pop('claim_revision') > 0
    assert events[2].payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'phoenix_claim': False,
            'is_terminal': False,
            'current_point_id': 1,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': 'estimating_failed',
    }


@pytest.mark.skip(
    f"""TODO: fix in CARGODEV-11356
                    + after that rewrite on
                    processing_events with stq""",
)
@pytest.mark.config(
    CARGO_CLAIMS_DISTLOCK_PROCESSING_EVENTS_SETTINGS={
        'enabled': True,
        'sleep_ms': 50,
        'new_event_chunk_size': 2,
    },
)
async def test_claim_processing_performer_found(
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        state_controller,
        taxi_cargo_claims,
        query_processing_events,
):
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()
    claim_info = await state_controller.apply(target_status='performer_found')
    claim_id = claim_info.claim_id
    response = await taxi_cargo_claims.post(
        'v1/claims/mark/performer-lookup-drafted',
        params={'claim_id': claim_id},
        json={
            'taxi_order_id': 'taxi_order_id_1',
            'taxi_user_id': 'taxi_user_id_1',
            'lookup_version': 1,
        },
    )
    assert response.status_code == 200
    assert response.json() == {'id': claim_id, 'status': 'performer_draft'}

    response = await taxi_cargo_claims.post(
        'v1/claims/mark/taxi-order-performer-found',
        params={'claim_id': claim_id},
        json={
            'taxi_order_id': 'taxi_order_id_1',
            'order_alias_id': 'order_alias_id_1',
            'phone_pd_id': 'phone_pd_id2',
            'name': 'New Name',
            'driver_id': 'driver_id2',
            'park_id': 'park_id2',
            'car_id': 'car_id2',
            'car_number': 'car_number2',
            'car_model': 'KAMAZ2',
            'lookup_version': 2,
        },
    )
    assert response.status_code == 200
    assert response.json() == {'id': claim_id, 'status': 'performer_found'}

    events = query_processing_events(claim_id)
    assert len(events) == 7
    assert events[0].payload == {
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
    assert events[1].payload['data'].pop('claim_revision') > 0
    assert events[1].payload == {
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
    assert events[2].payload['data'].pop('claim_revision') > 0
    assert events[2].payload == {
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
    assert events[3].payload['data'].pop('claim_revision') > 0
    assert events[3].payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'phoenix_claim': False,
            'is_terminal': False,
            'current_point_id': 1,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': 'performer_lookup',
    }
    assert events[4].payload['data'].pop('claim_revision') > 0
    assert events[4].payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'driver_profile_id': 'driver_id1',
            'park_id': 'park_id1',
            'is_terminal': False,
            'current_point_id': 1,
            'phoenix_claim': False,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': 'performer_found',
    }
    assert events[5].payload['data'].pop('claim_revision') > 0
    assert events[5].payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'phoenix_claim': False,
            'is_terminal': False,
            'current_point_id': 1,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': 'performer_draft',
    }
    assert events[6].payload['data'].pop('claim_revision') > 0
    assert events[6].payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'driver_profile_id': 'driver_id2',
            'park_id': 'park_id2',
            'is_terminal': False,
            'current_point_id': 1,
            'phoenix_claim': False,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': 'performer_found',
    }


@pytest.mark.skip(
    f"""TODO: fix in CARGODEV-11356
                    + after that rewrite on
                    processing_events with stq""",
)
@pytest.mark.config(
    CARGO_CLAIMS_DISTLOCK_PROCESSING_EVENTS_SETTINGS={
        'enabled': True,
        'sleep_ms': 50,
        'new_event_chunk_size': 2,
    },
)
@pytest.mark.parametrize(
    (
        'current_status_index',
        'current_status',
        'expected_status',
        'resolution',
        'skip_client_notify',
        'point_2_status',
        'point_3_status',
    ),
    (
        (
            12,
            'delivered',
            'delivered_finish',
            'success',
            True,
            'visited',
            'skipped',
        ),  # noqa E501
        (
            14,
            'returned',
            'returned_finish',
            'failed',
            False,
            'skipped',
            'visited',
        ),  # noqa E501
    ),
)
async def test_claim_processing_event_statuses(
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        state_controller,
        taxi_cargo_claims,
        query_processing_events,
        current_status_index,
        current_status,
        expected_status,
        resolution,
        skip_client_notify,
        point_2_status,
        point_3_status,
):
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()
    state_controller.set_options(skip_client_notify=skip_client_notify)
    claim_info = await state_controller.apply(target_status=current_status)
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        'v1/claims/mark/taxi-order-complete',
        params={'claim_id': claim_id},
        json={
            'taxi_order_id': 'taxi_order_id',
            'reason': 'some_reason',
            'lookup_version': 1,
        },
    )
    assert response.status_code == 200
    assert response.json() == {'id': claim_id, 'status': expected_status}

    events = query_processing_events(claim_id)
    assert len(events) == current_status_index
    assert events[0].payload == {
        'data': {
            'claim_uuid': claim_id,
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'is_terminal': False,
            'skip_client_notify': skip_client_notify,
        },
        'kind': 'status-change-succeeded',
        'status': 'new',
    }
    assert events[1].payload['data'].pop('claim_revision') > 0
    assert events[1].payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'phoenix_claim': False,
            'is_terminal': False,
            'current_point_id': 1,
            'skip_client_notify': skip_client_notify,
        },
        'kind': 'status-change-succeeded',
        'status': 'estimating',
    }
    assert events[2].payload['data'].pop('claim_revision') > 0
    assert events[2].payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'phoenix_claim': False,
            'is_terminal': False,
            'current_point_id': 1,
            'skip_client_notify': skip_client_notify,
        },
        'kind': 'status-change-succeeded',
        'status': 'ready_for_approval',
    }
    assert events[3].payload['data'].pop('claim_revision') > 0
    assert events[3].payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'phoenix_claim': False,
            'is_terminal': False,
            'current_point_id': 1,
            'skip_client_notify': skip_client_notify,
        },
        'kind': 'status-change-succeeded',
        'status': 'performer_lookup',
    }
    assert events[4].payload['data'].pop('claim_revision') > 0
    assert events[4].payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'driver_profile_id': 'driver_id1',
            'park_id': 'park_id1',
            'is_terminal': False,
            'current_point_id': 1,
            'phoenix_claim': False,
            'skip_client_notify': skip_client_notify,
        },
        'kind': 'status-change-succeeded',
        'status': 'performer_found',
    }
    assert events[5].payload['data'].pop('claim_revision') > 0
    assert events[5].payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'phoenix_claim': False,
            'claim_origin': 'api',
            'is_terminal': False,
            'current_point_id': 1,
            'skip_client_notify': skip_client_notify,
        },
        'kind': 'status-change-succeeded',
        'status': 'pickup_arrived',
    }
    assert events[6].payload['data'].pop('claim_revision') > 0
    assert events[6].payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'phoenix_claim': False,
            'is_terminal': False,
            'current_point_id': 1,
            'skip_client_notify': skip_client_notify,
        },
        'kind': 'status-change-succeeded',
        'status': 'ready_for_pickup_confirmation',
    }
    assert events[7].payload['data'].pop('claim_revision') > 0
    assert events[7].payload == {
        'data': {
            'phoenix_claim': False,
            'is_terminal': False,
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'current_point_id': 1,
            'skip_client_notify': skip_client_notify,
        },
        'kind': 'status-change-succeeded',
        'status': 'pickuped',
    }
    assert events[8].payload['data'].pop('claim_revision') > 0
    assert events[8].payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'phoenix_claim': False,
            'is_terminal': False,
            'current_point_id': 2,
            'skip_client_notify': skip_client_notify,
        },
        'kind': 'status-change-succeeded',
        'status': 'delivery_arrived',
    }

    status = (
        'returning'
        if current_status == 'returned'
        else 'ready_for_delivery_confirmation'
    )
    assert events[9].payload['data'].pop('claim_revision') > 0
    assert events[9].payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'phoenix_claim': False,
            'is_terminal': False,
            'current_point_id': 2,
            'skip_client_notify': skip_client_notify,
        },
        'kind': 'status-change-succeeded',
        'status': status,
    }

    status = 'return_arrived' if current_status == 'returned' else 'delivered'
    assert events[10].payload['data'].pop('claim_revision') > 0
    assert events[10].payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'phoenix_claim': False,
            'is_terminal': False,
            'current_point_id': 3 if current_status == 'returned' else 2,
            'skip_client_notify': skip_client_notify,
        },
        'kind': 'status-change-succeeded',
        'status': status,
    }

    if current_status == 'returned':
        assert events[11].payload['data'].pop('claim_revision') > 0
        assert events[11].payload == {
            'data': {
                'corp_client_id': '01234567890123456789012345678912',
                'claim_origin': 'api',
                'phoenix_claim': False,
                'is_terminal': False,
                'current_point_id': 3,
                'skip_client_notify': skip_client_notify,
            },
            'kind': 'status-change-succeeded',
            'status': 'ready_for_return_confirmation',
        }
        assert events[12].payload['data'].pop('claim_revision') > 0
        assert events[12].payload == {
            'data': {
                'corp_client_id': '01234567890123456789012345678912',
                'claim_origin': 'api',
                'phoenix_claim': False,
                'is_terminal': False,
                'current_point_id': 3,
                'skip_client_notify': skip_client_notify,
            },
            'kind': 'status-change-succeeded',
            'status': 'returned',
        }

    assert (
        events[current_status_index - 1].payload['data'].pop('claim_revision')
        > 0
    )
    assert events[current_status_index - 1].payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'park_id': 'park_id1',
            'phoenix_claim': False,
            'is_terminal': True,
            'resolution': resolution,
            'route_points': [
                {
                    'claim_point_id': 1,
                    'id': 1000,
                    'coordinates': {'lat': 55.7, 'lon': 37.5},
                    'visit_status': 'visited',
                    'point_type': 'source',
                },
                {
                    'claim_point_id': 2,
                    'id': 1001,
                    'coordinates': {'lat': 55.6, 'lon': 37.6},
                    'visit_status': point_2_status,
                    'point_type': 'destination',
                },
                {
                    'claim_point_id': 3,
                    'id': 1002,
                    'coordinates': {'lat': 55.4, 'lon': 37.8},
                    'visit_status': point_3_status,
                    'point_type': 'return',
                },
            ],
            'driver_profile_id': 'driver_id1',
            'skip_client_notify': skip_client_notify,
        },
        'kind': 'status-change-succeeded',
        'status': expected_status,
    }


@pytest.mark.parametrize(
    'status_filter_default, status_filter_clauses',
    [
        (
            False,
            [
                {
                    'title': 'title',
                    'predicate': {
                        'type': 'eq',
                        'init': {
                            'value': 'accepted',
                            'arg_name': 'claim_status',
                            'arg_type': 'string',
                        },
                    },
                    'value': {'enabled': True},
                },
            ],
        ),
        (True, []),
    ],
)
@pytest.mark.config(
    CARGO_CLAIMS_DISTLOCK_PROCESSING_EVENTS_SETTINGS={
        'enabled': True,
        'sleep_ms': 50,
        'new_event_chunk_size': 1,
    },
)
@pytest.mark.parametrize('processing_flow', ['disabled', 'enabled'])
async def test_claim_processing_create_event_type(
        taxi_cargo_claims,
        state_controller,
        set_up_processing_exp,
        get_default_corp_client_id,
        get_default_accept_language,
        get_default_headers,
        mock_create_event,
        pgsql,
        procaas_send_settings,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        check_processing_stats,
        run_processing_events,
        taxi_config,
        now,
        status_filter_default,
        status_filter_clauses,
        processing_flow,
        extract_oldest_event_lag,
):
    await procaas_send_settings()
    await procaas_claim_status_filter(
        enabled=status_filter_default, clauses=status_filter_clauses,
    )
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

    if status_filter_default:
        result = await run_processing_events()
        extract_oldest_event_lag(result)
        await check_processing_stats(
            result,
            processed_in_stq=3,
            for_processing_cnt=1,
            failed_cnt=0,
            stq_success=1,
        )

        cursor = pgsql['cargo_claims'].cursor()
        cursor.execute(
            """
            SELECT processing_create_event FROM cargo_claims.claims
            WHERE uuid_id = %s
            """,
            (claim_info.claim_id,),
        )
        data = list(cursor)
        assert len(data) == 1
        processing_create_event = data[0][0]
        assert processing_create_event == 'create'

    mock_create_event(
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
                'accept_as_create_event': (not status_filter_default),
                'claim_revision': 3,
                'is_terminal': False,
                'phoenix_claim': False,
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
    assert response.status_code == 200

    if (
            status_filter_default or status_filter_clauses
    ) and processing_flow == 'enabled':
        result = await run_processing_events()
        extract_oldest_event_lag(result)
        await check_processing_stats(
            result,
            processed_in_stq=1,
            for_processing_cnt=1,
            failed_cnt=0,
            stq_success=1,
        )

    response = await taxi_cargo_claims.post(
        f'/v2/processing/update-status/accepted',
        params={'claim_id': claim_info.claim_id},
        json={
            'version': 1,
            'accept_time': now.strftime('%Y-%m-%dT%H:%M:%S+00:00'),
        },
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        """
        SELECT processing_create_event FROM cargo_claims.claims
        WHERE uuid_id = %s
        """,
        (claim_info.claim_id,),
    )
    data = list(cursor)
    assert len(data) == 1
    processing_create_event = data[0][0]

    if not status_filter_default:
        assert processing_create_event == 'accept'
    else:
        assert processing_create_event == 'create'


@pytest.mark.pgsql('cargo_claims', files=['insert_events.sql'])
@pytest.mark.config(
    CARGO_CLAIMS_DISTLOCK_PROCESSING_EVENTS_SETTINGS={
        'enabled': True,
        'sleep_ms': 50,
        'new_event_chunk_size': 2,
    },
)
@pytest.mark.now('2020-04-01T10:35:01+0000')
async def test_oldest_event_lag(
        mock_create_event,
        run_processing_events,
        pgsql,
        check_processing_stats,
        extract_oldest_event_lag,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
):
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        """
    UPDATE cargo_claims.processing_events
    SET created_ts='2020-04-01T10:35:00+0000'
        """,
    )
    mock_create_event(error_code=409)
    result = await run_processing_events()
    extract_oldest_event_lag(result, 1000)
    await check_processing_stats(
        result, processed_in_stq=2, for_processing_cnt=2, failed_cnt=0,
    )
