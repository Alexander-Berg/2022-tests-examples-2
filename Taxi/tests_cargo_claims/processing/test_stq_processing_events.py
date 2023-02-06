import pytest


async def insert_event(pgsql, event_id, claim_id, token):
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        """
        INSERT INTO
            cargo_claims.processing_events(id, item_id,
            queue, idempotency_token, payload,
            created_ts) VALUES(%s,
            %s,
            'claim',
            %s,
            '{  "kind":
                "status-change-requested",
                "status": "accepted",
                "data": {
                        "claim_version": 1,
                         "accept_language": "rus",
                         "corp_client_id": "corp"
                        }
            }'::jsonb,
            '2020-01-27T15:35:00+0000')
        """,
        (event_id, claim_id, token),
    )


async def set_job_config(taxi_config):
    taxi_config.set_values(
        dict(
            CARGO_CLAIMS_DISTLOCK_PROCESSING_EVENTS_SETTINGS={
                'enabled': True,
                'sleep_ms': 50,
                'new_event_chunk_size': 2,
            },
        ),
    )


@pytest.mark.pgsql('cargo_claims', files=['insert_events.sql'])
async def test_just_works(
        mock_create_event,
        run_processing_events,
        check_processing_stats,
        extract_oldest_event_lag,
        stq_runner,
        taxi_cargo_claims,
        taxi_config,
        procaas_event_kind_filter,
        procaas_claim_status_filter,
):
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()
    await set_job_config(taxi_config)

    await taxi_cargo_claims.invalidate_caches()

    mock_create_event()
    result = await run_processing_events()
    extract_oldest_event_lag(result)
    await check_processing_stats(
        result,
        processed_in_stq=2,
        for_processing_cnt=2,
        failed_cnt=0,
        stq_success=1,
    )


async def test_set_stq_after_new_event(
        mock_create_event,
        run_processing_events,
        check_processing_stats,
        extract_oldest_event_lag,
        stq_runner,
        taxi_cargo_claims,
        taxi_cargo_claims_monitor,
        taxi_config,
        pgsql,
        procaas_event_kind_filter,
        procaas_claim_status_filter,
):
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()
    await taxi_cargo_claims.tests_control(reset_metrics=True)
    await set_job_config(taxi_config)

    await taxi_cargo_claims.invalidate_caches()

    mock_create_event()
    await insert_event(pgsql, 11, '6c17a5dc8da44510adc1f10ca3ef5290', 'token1')
    await insert_event(pgsql, 12, '6c17a5dc8da44510adc1f10ca3ef5290', 'token2')

    # first iteration of job
    result = await run_processing_events(should_set_stq=False)
    extract_oldest_event_lag(result)
    await check_processing_stats(
        result,
        processed_in_stq=0,
        for_processing_cnt=2,
        failed_cnt=0,
        stq_success=1,
    )

    await insert_event(pgsql, 13, '6c17a5dc8da44510adc1f10ca3ef5290', 'token3')

    await stq_runner.cargo_claims_processing_events.call(
        task_id='test', kwargs={'item_id': '6c17a5dc8da44510adc1f10ca3ef5290'},
    )
    stats = await taxi_cargo_claims_monitor.get_metric(
        'cargo-claims-processing-events',
    )

    # stq catch all 3 events
    assert stats['stats']['processed-in-stq-events'] == 3

    # next iteration of job
    # event will not be cathed
    result = await run_processing_events(should_set_stq=False)
    extract_oldest_event_lag(result)
    await check_processing_stats(
        result,
        processed_in_stq=0,
        for_processing_cnt=0,
        failed_cnt=0,
        stq_success=0,
    )


@pytest.mark.parametrize(
    'kind_filter_default, kind_filter_clauses',
    [
        (
            False,
            [
                {
                    'predicate': {
                        'init': {
                            'predicates': [
                                {
                                    'init': {'arg_name': 'is_phoenix'},
                                    'type': 'bool',
                                },
                                {
                                    'init': {
                                        'value': 'status-change-requested',
                                        'arg_name': 'event_kind',
                                        'arg_type': 'string',
                                    },
                                    'type': 'eq',
                                },
                            ],
                        },
                        'type': 'all_of',
                    },
                    'title': 'is_phoenix',
                    'value': {'enabled': True},
                },
            ],
        ),
    ],
)
@pytest.mark.pgsql('cargo_claims', files=['insert_events.sql'])
@pytest.mark.config(
    CARGO_CLAIMS_DISTLOCK_PROCESSING_EVENTS_SETTINGS={
        'enabled': True,
        'sleep_ms': 50,
        'new_event_chunk_size': 5,
    },
)
async def test_processing_events_skip(
        run_processing_events,
        procaas_event_kind_filter,
        testpoint,
        check_processing_stats,
        extract_oldest_event_lag,
        mock_create_event,
        kind_filter_default,
        kind_filter_clauses,
        pgsql,
        procaas_claim_status_filter,
        claim_uuid='6c17a5dc8da44510adc1f10ca3ef5291',
):
    await procaas_claim_status_filter()
    await procaas_event_kind_filter(
        enabled=kind_filter_default, clauses=kind_filter_clauses,
    )

    mock_create_event()

    @testpoint('event-kind-for-send')
    def test_point(data):
        assert data['event_id']
        if data['item_id'] == claim_uuid:
            assert data['is_phoenix']
            assert data['enabled']
            return
        assert not data['is_phoenix']
        assert not data['enabled']

    result = await run_processing_events()
    extract_oldest_event_lag(result)

    # 5 events, but 4 different item_id, so set 4 stq.
    await check_processing_stats(
        result,
        processed_in_stq=5,
        for_processing_cnt=5,
        failed_cnt=0,
        stq_success=4,
    )
    assert test_point.times_called == 5


@pytest.mark.parametrize(
    'status_code, expect_fail, processed_in_stq',
    [(400, False, 1), (409, False, 1), (500, True, 0)],
)
async def test_processing_events_send_event_error(
        mock_create_event,
        run_processing_events,
        check_processing_stats,
        extract_oldest_event_lag,
        pgsql,
        taxi_cargo_claims,
        taxi_cargo_claims_monitor,
        stq_runner,
        taxi_config,
        procaas_event_kind_filter,
        procaas_claim_status_filter,
        status_code: int,
        expect_fail: bool,
        processed_in_stq: int,
):
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()
    await taxi_cargo_claims.tests_control(reset_metrics=True)

    await set_job_config(taxi_config)
    await taxi_cargo_claims.invalidate_caches()

    await insert_event(pgsql, 11, '6c17a5dc8da44510adc1f10ca3ef5290', 'token1')
    mock_create_event(error_code=status_code)
    result = await run_processing_events(should_set_stq=False)
    extract_oldest_event_lag(result)
    await check_processing_stats(
        result,
        processed_in_stq=0,
        for_processing_cnt=1,
        failed_cnt=0,
        stq_success=1,
    )
    await stq_runner.cargo_claims_processing_events.call(
        task_id='test',
        kwargs={'item_id': '6c17a5dc8da44510adc1f10ca3ef5290'},
        expect_fail=expect_fail,
    )

    stats = await taxi_cargo_claims_monitor.get_metric(
        'cargo-claims-processing-events',
    )
    assert stats['stats']['processed-in-stq-events'] == processed_in_stq

    # check that nothing in job
    result = await run_processing_events()
    extract_oldest_event_lag(result)
    await check_processing_stats(
        result,
        processed_in_stq=0,
        for_processing_cnt=0,
        failed_cnt=0,
        stq_success=0,
    )


async def test_stq_execute_too_fast(
        mock_create_event,
        run_processing_events,
        check_processing_stats,
        extract_oldest_event_lag,
        stq_runner,
        taxi_cargo_claims,
        taxi_config,
        testpoint,
        pgsql,
        procaas_event_kind_filter,
        procaas_claim_status_filter,
):
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()
    await set_job_config(taxi_config)
    await taxi_cargo_claims.invalidate_caches()

    @testpoint('processing-events-point-for-execute-stq')
    async def testpoint_callback(data):
        await stq_runner.cargo_claims_processing_events.call(
            task_id='test',
            kwargs={'item_id': '6c17a5dc8da44510adc1f10ca3ef5290'},
        )
        await insert_event(
            pgsql, 13, '6c17a5dc8da44510adc1f10ca3ef5290', 'token3',
        )
        return {'enable': True}

    mock_create_event()
    await insert_event(pgsql, 11, '6c17a5dc8da44510adc1f10ca3ef5290', 'token1')
    await insert_event(pgsql, 12, '6c17a5dc8da44510adc1f10ca3ef5290', 'token2')

    # first iteration of job
    result = await run_processing_events(should_set_stq=False)
    extract_oldest_event_lag(result)
    await check_processing_stats(
        result,
        processed_in_stq=2,
        for_processing_cnt=2,
        failed_cnt=0,
        stq_success=1,
    )

    assert testpoint_callback.times_called == 1

    @testpoint('processing-events-point-for-execute-stq')
    async def _testpoint_callback(data):
        return {'enable': False}

    # next iteration of job
    # new event not skipped
    result = await run_processing_events()
    extract_oldest_event_lag(result)
    await check_processing_stats(
        result,
        processed_in_stq=1,
        for_processing_cnt=1,
        failed_cnt=0,
        stq_success=1,
        skipped_events=0,
    )
