"""
WARNING
Do not set waybill resolution 'complete' in this job
"""
import pytest

from testsuite.utils import matching


def extract_oldest_segment(result, milliseconds=None):
    if milliseconds:
        assert result['stats']['oldest-segment-lag-ms'] == milliseconds
    result['stats'].pop('oldest-segment-lag-ms')


async def test_cancel_segment(
        happy_path_state_orders_created,
        mock_claim_bulk_update_state,
        run_notify_claims,
        taxi_cargo_dispatch_monitor,
        taxi_cargo_dispatch,
        mock_cargo_orders_bulk_info,
        stq_runner,
        read_waybill_info,
        experiments3,
        mockserver,
        waybill_id='waybill_smart_1',
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    mock_cargo_orders_bulk_info(transport_type='car')
    mock_claim_bulk_update_state.expected_request = {
        'segments': [
            {
                'id': 'seg1',
                'resolution': 'failed',
                'revision': 4,
                'taxi_order_id': matching.AnyString(),
                'cargo_order_id': matching.AnyString(),
                'router_id': 'smart_router',
                'autoreorder_flow': 'newway',
                'performer_info': {
                    'revision': 1,
                    'order_alias_id': '1234',
                    'phone_pd_id': '+70000000000_id',
                    'name': 'Kostya',
                    'driver_id': 'driver_id_1',
                    'park_id': 'park_id_1',
                    'park_clid': 'park_clid1',
                    'car_id': '123',
                    'car_number': 'А001АА77',
                    'car_model': 'KAMAZ',
                    'lookup_version': 1,
                    'taxi_class': 'cargo',
                    'park_name': 'some_park_name',
                    'park_org_name': 'some_park_org_name',
                    'transport_type': 'car',
                },
            },
        ],
    }

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json={
            'order_id': '6dac297a-33ed-42e7-9101-af81ddf59602',
            'waybill_id': waybill_id,
            'taxi_order_id': 'taxi-order',
            'reason': 'performer_cancel',
            'lookup_version': 0,
        },
    )
    assert response.status_code == 200

    # проверка на то, что ставится нужное количество stq-задач на исполнение
    result = await run_notify_claims(should_set_stq=False)
    extract_oldest_segment(result)
    assert result['stats'] == {
        'segments-count': 2,
        'segments-updated-count': 2,
        'stq-fail': 0,
        'stq-success': 2,
    }

    await stq_runner.cargo_dispatch_notify_claims.call(
        task_id='test1', kwargs={'segment_id': 'seg1'},
    )
    assert mock_claim_bulk_update_state.handler.times_called == 1
    assert mock_stq_reschedule.times_called == 0

    mock_claim_bulk_update_state.expected_request = {
        'segments': [
            {
                'id': 'seg2',
                'resolution': 'failed',
                'revision': 4,
                'taxi_order_id': matching.AnyString(),
                'cargo_order_id': matching.AnyString(),
                'router_id': 'smart_router',
                'autoreorder_flow': 'newway',
                'performer_info': {
                    'revision': 1,
                    'order_alias_id': '1234',
                    'phone_pd_id': '+70000000000_id',
                    'name': 'Kostya',
                    'driver_id': 'driver_id_1',
                    'park_id': 'park_id_1',
                    'park_clid': 'park_clid1',
                    'car_id': '123',
                    'car_number': 'А001АА77',
                    'car_model': 'KAMAZ',
                    'lookup_version': 1,
                    'taxi_class': 'cargo',
                    'park_name': 'some_park_name',
                    'park_org_name': 'some_park_org_name',
                    'transport_type': 'car',
                },
            },
        ],
    }
    await stq_runner.cargo_dispatch_notify_claims.call(
        task_id='test2', kwargs={'segment_id': 'seg2'},
    )
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-notify-claims',
    )
    assert stats['stats'] == {'segments-notified-count': 2}
    assert mock_claim_bulk_update_state.handler.times_called == 2
    assert mock_stq_reschedule.times_called == 0


@pytest.mark.parametrize(
    'bulk_update_status, notify_count, expect_fail',
    [(200, 1, False), (500, 0, True)],
)
@pytest.mark.config(
    CARGO_CLAIMS_CLIENT_QOS={
        '__default__': {'attempts': 1, 'timeout-ms': 10000},
    },
)
async def test_performer_found(
        happy_path_state_performer_found,
        mock_claim_bulk_update_state,
        run_notify_claims,
        mock_cargo_orders_bulk_info,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        experiments3,
        bulk_update_status: int,
        notify_count: int,
        expect_fail: bool,
):
    mock_cargo_orders_bulk_info(transport_type='car')
    mock_claim_bulk_update_state.status_code = bulk_update_status
    mock_claim_bulk_update_state.expected_request = {
        'segments': [
            {
                'id': 'seg3',
                'revision': 4,
                'performer_info': {
                    'revision': 1,
                    'order_alias_id': '1234',
                    'phone_pd_id': '+70000000000_id',
                    'name': 'Kostya',
                    'driver_id': 'driver_id_1',
                    'park_id': 'park_id_1',
                    'park_clid': 'park_clid1',
                    'car_id': '123',
                    'car_number': 'А001АА77',
                    'car_model': 'KAMAZ',
                    'lookup_version': 1,
                    'taxi_class': 'cargo',
                    'park_name': 'some_park_name',
                    'park_org_name': 'some_park_org_name',
                    'transport_type': 'car',
                },
                'cargo_order_id': matching.AnyString(),
                'router_id': 'fallback_router',
                'taxi_order_id': matching.AnyString(),
                'autoreorder_flow': 'newway',
            },
        ],
    }

    # проверка на то, что ставится нужное количество stq-задач на исполнение
    result = await run_notify_claims(expect_fail=expect_fail)
    extract_oldest_segment(result)
    assert result['stats'] == {
        'segments-count': 1,
        'segments-updated-count': 1,
        'stq-fail': 0,
        'stq-success': 1,
    }
    assert mock_claim_bulk_update_state.handler.times_called == 1

    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-notify-claims',
    )
    assert stats['stats'] == {'segments-notified-count': notify_count}


async def test_notify_cancel_state(
        happy_path_cancelled_by_user,
        mock_claim_bulk_update_state,
        run_notify_claims,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        experiments3,
):
    # проверка на то, что ставится нужное количество stq-задач на исполнение
    result = await run_notify_claims()
    extract_oldest_segment(result)
    assert result['stats'] == {
        'segments-count': 1,
        'segments-updated-count': 1,
        'stq-fail': 0,
        'stq-success': 1,
    }
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-notify-claims',
    )
    assert stats['stats'] == {'segments-notified-count': 1}
    bulk_update_request = mock_claim_bulk_update_state.handler.next_call()[
        'request'
    ].json
    for segment in bulk_update_request['segments']:
        assert 'cancel_state' in segment


async def test_notify_after_reorder(
        happy_path_state_performer_found,
        mock_claim_bulk_update_state,
        run_notify_claims,
        reorder_waybill,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        mockserver,
        experiments3,
):
    # проверка на то, что ставится нужное количество stq-задач на исполнение
    result = await run_notify_claims()
    extract_oldest_segment(result)
    assert result['stats'] == {
        'segments-count': 1,
        'segments-updated-count': 1,
        'stq-fail': 0,
        'stq-success': 1,
    }
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-notify-claims',
    )
    assert stats['stats'] == {'segments-notified-count': 1}
    mock_claim_bulk_update_state.handler.next_call()

    await reorder_waybill('waybill_fb_3')
    # проверка на то, что ставится нужное количество stq-задач на исполнение
    result = await run_notify_claims()
    extract_oldest_segment(result)
    assert result['stats'] == {
        'segments-count': 1,
        'segments-updated-count': 1,
        'stq-fail': 0,
        'stq-success': 1,
    }
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-notify-claims',
    )
    assert stats['stats'] == {'segments-notified-count': 1}

    bulk_update_request = mock_claim_bulk_update_state.handler.next_call()[
        'request'
    ].json
    assert len(bulk_update_request['segments']) == 1
    assert bulk_update_request['segments'][0] == {'id': 'seg3', 'revision': 5}


async def test_router_autoreorder_flow(
        happy_path_state_first_import,
        happy_path_claims_segment_db,
        get_segment_info,
        propose_from_segments,
        run_choose_routers,
        run_choose_waybills,
        run_notify_claims,
        mock_claim_bulk_update_state,
        set_up_segment_routers_exp,
        stq_runner,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        experiments3,
):
    """
        autoreorder_flow is in segment_routers exp only now.
    """
    await run_choose_routers()
    await propose_from_segments(
        'smart_router', 'waybill_smart_1', 'seg1', 'seg2',
    )
    await run_choose_waybills()

    # проверка на то, что ставится нужное количество stq-задач на исполнение
    result = await run_notify_claims(should_set_stq=False)
    extract_oldest_segment(result)
    assert result['stats'] == {
        'segments-count': 2,
        'segments-updated-count': 2,
        'stq-fail': 0,
        'stq-success': 2,
    }

    await stq_runner.cargo_dispatch_notify_claims.call(
        task_id='test1', kwargs={'segment_id': 'seg2'},
    )
    assert mock_claim_bulk_update_state.last_request['segments'] == [
        {
            'id': 'seg2',
            'revision': 2,
            'autoreorder_flow': 'newway',
            'router_id': 'smart_router',
        },
    ]

    await stq_runner.cargo_dispatch_notify_claims.call(
        task_id='test1', kwargs={'segment_id': 'seg1'},
    )
    assert mock_claim_bulk_update_state.handler.times_called == 2

    assert mock_claim_bulk_update_state.last_request['segments'] == [
        {
            'id': 'seg1',
            'revision': 2,
            'autoreorder_flow': 'newway',
            'router_id': 'smart_router',
        },
    ]


async def test_update_state_reschedule(
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        happy_path_state_orders_created,
        mockserver,
        run_notify_claims,
        default_order_fail_request,
        stq_runner,
        stq,
        experiments3,
        waybill_id='waybill_fb_3',
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json=default_order_fail_request(waybill_id, 'performer_not_found'),
    )
    assert response.status_code == 200

    @mockserver.json_handler(
        '/cargo-claims/v1/segments/dispatch/bulk-update-state',
    )
    def bulk_update_handler(request):
        assert len(request.json['segments']) == 1
        assert request.json['segments'][0]['id'] == 'seg3'
        assert (
            request.json['segments'][0]['resolution'] == 'performer_not_found'
        )
        return {'processed_segment_ids': []}

    # проверка на то, что ставится нужное количество stq-задач на исполнение
    result = await run_notify_claims(should_set_stq=False)
    extract_oldest_segment(result)
    assert result['stats'] == {
        'segments-count': 1,
        'segments-updated-count': 1,
        'stq-fail': 0,
        'stq-success': 1,
    }

    await stq_runner.cargo_dispatch_notify_claims.call(
        task_id='test1', kwargs={'segment_id': 'seg3'},
    )
    assert bulk_update_handler.times_called == 1
    assert mock_stq_reschedule.times_called == 1
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-notify-claims',
    )
    assert stats['stats'] == {'segments-notified-count': 0}

    @mockserver.json_handler(
        '/cargo-claims/v1/segments/dispatch/bulk-update-state',
    )
    def bulk_update_handler_new(request):
        assert len(request.json['segments']) == 1
        assert request.json['segments'][0]['id'] == 'seg3'
        assert (
            request.json['segments'][0]['resolution'] == 'performer_not_found'
        )
        return {'processed_segment_ids': ['seg3']}

    await stq_runner.cargo_dispatch_notify_claims.call(
        task_id='test1', kwargs={'segment_id': 'seg3'},
    )
    assert bulk_update_handler_new.times_called == 1
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-notify-claims',
    )
    assert stats['stats'] == {'segments-notified-count': 1}


@pytest.mark.config(
    CARGO_DISPATCH_READ_SEGMENTS_WITH_REVISION={
        'choose_routers': False,
        'fallback_router': False,
        'notify_claims': True,
    },
)
async def test_send_segment_revision(
        happy_path_state_performer_found,
        mock_claim_bulk_update_state,
        run_notify_claims,
        taxi_cargo_dispatch_monitor,
        taxi_cargo_dispatch,
        experiments3,
):
    # проверка на то, что ставится нужное количество stq-задач на исполнение
    result = await run_notify_claims()
    extract_oldest_segment(result)
    assert result['stats'] == {
        'segments-count': 1,
        'segments-updated-count': 1,
        'stq-fail': 0,
        'stq-success': 1,
    }
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-notify-claims',
    )
    assert stats['stats'] == {'segments-notified-count': 1}
    assert mock_claim_bulk_update_state.handler.times_called == 1
    bulk_update_request = mock_claim_bulk_update_state.handler.next_call()[
        'request'
    ].json
    assert bulk_update_request['segments'][0]['claims_segment_revision'] == 1


@pytest.mark.now('2020-04-01T10:35:01+0000')
async def test_oldest_segment_lag(
        taxi_cargo_dispatch,
        happy_path_state_orders_created,
        mockserver,
        run_notify_claims,
        pgsql,
        default_order_fail_request,
        taxi_cargo_dispatch_monitor,
):
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    waybill_id = 'waybill_fb_3'
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json=default_order_fail_request(waybill_id, 'performer_not_found'),
    )
    assert response.status_code == 200

    @mockserver.json_handler(
        '/cargo-claims/v1/segments/dispatch/bulk-update-state',
    )
    def _handler(request):
        assert len(request.json['segments']) == 1
        assert request.json['segments'][0]['id'] == 'seg3'
        assert (
            request.json['segments'][0]['resolution'] == 'performer_not_found'
        )
        return {'processed_segment_ids': []}

    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        """
    UPDATE cargo_dispatch.segments
    SET updated_ts='2020-04-01T10:35:00+0000'
        """,
    )

    result = await run_notify_claims(should_set_stq=False)
    extract_oldest_segment(result, 1000)
    assert result['stats'] == {
        'segments-count': 1,
        'segments-updated-count': 1,
        'stq-fail': 0,
        'stq-success': 1,
    }


@pytest.mark.parametrize(
    'quota, expected_segments_count', [(10, 1), (1, 1), (0, 0)],
)
async def test_rate_limit(
        happy_path_cancelled_by_user,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        run_notify_claims,
        rps_limiter,
        taxi_config,
        quota,
        expected_segments_count,
):
    taxi_config.set_values(
        {
            'CARGO_DISPATCH_NOTIFY_CLAIMS_SETTINGS': {
                'enabled': True,
                'limit': 1000,
                'rate_limit': {'limit': 10, 'interval': 1, 'burst': 20},
            },
        },
    )
    await taxi_cargo_dispatch.invalidate_caches()

    rps_limiter.set_budget('cargo-dispatch-notify-claims', quota)

    result = await run_notify_claims(should_set_stq=False)
    assert result['stats']['segments-count'] == expected_segments_count

    statistics = await taxi_cargo_dispatch_monitor.get_metric('rps-limiter')
    limiter = statistics['cargo-dispatch-distlocks-limiter']
    assert limiter['quota-requests-failed'] == 0

    resource = limiter['resource_stat']['cargo-dispatch-notify-claims']
    if quota == 0:
        # if client receives quota == 0, requests are considered rejected
        assert resource['decision']['rejected'] == 10
    else:
        assert resource['decision']['rejected'] == 0
    assert resource['quota-assigned'] == quota
    assert resource['limit'] == 10


@pytest.mark.parametrize(
    'cargo_order_id, route_id',
    [
        pytest.param(
            '535efa05-5373-4fd4-9807-b2d0d28822c5', '92125', id='Common case',
        ),
        pytest.param(
            '3061b811-9a69-41dc-bef9-858e3e6ec2db',
            '02683',
            id='Leading zeros',
        ),
        pytest.param(
            '71d47a97-b938-4a7b-9f13-708382e6b4c9',
            '34788',
            id='Redundant leading digits',
        ),
    ],
)
async def test_same_day_route_id(
        set_up_segment_routers_exp,
        happy_path_claims_segment_db,
        happy_path_state_first_import,
        run_choose_routers,
        propose_from_segments,
        run_choose_waybills,
        run_create_orders,
        run_notify_claims,
        mock_cargo_orders_bulk_info,
        mock_claim_bulk_update_state,
        set_waybill_cargo_order_id,
        read_waybill_info,
        cargo_order_id,
        route_id,
        router_id='cargo_same_day_delivery_router',
        waybill_ref='waybill_sdd_1',
        segment_id='seg1',
):
    await set_up_segment_routers_exp(smart_router=router_id)
    await run_choose_routers()
    await propose_from_segments(router_id, waybill_ref, segment_id)
    await run_choose_waybills()
    await run_create_orders()
    await set_waybill_cargo_order_id(waybill_ref, cargo_order_id)

    waybill = await read_waybill_info(waybill_ref)
    assert waybill['execution']['cargo_order_info']['route_id'] == route_id

    mock_cargo_orders_bulk_info(transport_type='car')
    mock_claim_bulk_update_state.expected_request = {
        'segments': [
            {
                'id': 'seg1',
                'revision': 3,
                'performer_info': {
                    'revision': 1,
                    'order_alias_id': '1234',
                    'phone_pd_id': '+70000000000_id',
                    'name': 'Kostya',
                    'driver_id': 'driver_id_1',
                    'park_id': 'park_id_1',
                    'park_clid': 'park_clid1',
                    'car_id': '123',
                    'car_number': 'А001АА77',
                    'car_model': 'KAMAZ',
                    'lookup_version': 1,
                    'taxi_class': 'cargo',
                    'park_name': 'some_park_name',
                    'park_org_name': 'some_park_org_name',
                    'transport_type': 'car',
                },
                'cargo_order_id': matching.AnyString(),
                'route_id': route_id,
                'router_id': router_id,
                'taxi_order_id': matching.AnyString(),
                'autoreorder_flow': 'newway',
            },
        ],
    }

    await run_notify_claims()
