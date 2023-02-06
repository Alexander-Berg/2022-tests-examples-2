import pytest

from testsuite.utils import matching

# pylint: disable=invalid-name
pytestmark = [pytest.mark.usefixtures('set_up_alive_batch_exp')]


class AnyInteger:
    """Matches any string."""

    def __repr__(self):
        return '<AnyInteger>'

    def __eq__(self, other):
        return isinstance(other, int)


def extract_oldest_waybill(result, milliseconds=None):
    if milliseconds:
        assert result['stats']['oldest-waybill-lag-ms'] == milliseconds
    result['stats'].pop('oldest-waybill-lag-ms')


async def test_basic(
        mockserver,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        run_notify_orders,
        trigger_need_to_notify_orders,
        waybill_ref='waybill_fb_3',
):
    await trigger_need_to_notify_orders(waybill_ref)

    @mockserver.json_handler('/cargo-orders/v1/order/change-destination')
    def change_destination(request):
        assert request.json == {
            'order_id': matching.any_string,
            'dispatch_version': AnyInteger(),
            'claim_id': 'claim_seg3',
            'segment_id': 'seg3',
            'claim_point_id': AnyInteger(),
            'idempotency_token': 'waybill_fb_3_32_2',
        }
        return {}

    segment = happy_path_claims_segment_db.get_segment('seg3')
    segment.set_point_visit_status('p1', 'visited')

    await run_notify_orders()
    assert change_destination.times_called == 1


async def test_change_desination_error(
        mockserver,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        taxi_cargo_dispatch,
        run_notify_orders,
        taxi_cargo_dispatch_monitor,
        trigger_need_to_notify_orders,
        waybill_ref='waybill_fb_3',
):
    await trigger_need_to_notify_orders(waybill_ref)

    @mockserver.json_handler('/cargo-orders/v1/order/change-destination')
    def change_destination(request):
        assert request.json == {
            'order_id': matching.any_string,
            'dispatch_version': AnyInteger(),
            'claim_id': 'claim_seg3',
            'segment_id': 'seg3',
            'claim_point_id': AnyInteger(),
            'idempotency_token': 'waybill_fb_3_32_2',
        }
        return mockserver.make_response(
            status=400,
            json={
                'code': 'bad_state',
                'message': 'can not change destination',
            },
        )

    segment = happy_path_claims_segment_db.get_segment('seg3')
    segment.set_point_visit_status('p1', 'visited')

    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    await run_notify_orders()

    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-notify-orders',
    )
    assert stats['stats']['marked-as-resolved'] == 1
    assert change_destination.times_called == 1


async def test_cancelled(
        state_cancelled_resolved, run_notify_orders, mock_order_cancel,
):
    await run_notify_orders()
    assert mock_order_cancel.handler.times_called == 1


async def test_cancelled_v2(
        mock_order_cancel,
        happy_path_state_orders_created,
        happy_path_claims_segment_db,
        run_claims_segment_replication,
        run_notify_orders,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
):
    # prepare waybill
    happy_path_claims_segment_db.cancel_segment_by_user('seg3')
    result = await run_claims_segment_replication()
    assert result['stats']['updated-waybills'] == 1

    await taxi_cargo_dispatch.tests_control(reset_metrics=True)

    result = await run_notify_orders(expect_fail=False)
    assert result['stats']['waybills-for-handling'] == 1
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-notify-orders',
    )
    assert stats['stats']['marked-as-resolved'] == 1

    result = await run_notify_orders()
    assert result['stats']['waybills-for-handling'] == 1
    assert mock_order_cancel.handler.times_called == 1


async def test_revision(
        happy_path_state_orders_created,
        happy_path_claims_segment_db,
        run_claims_segment_replication,
        taxi_cargo_dispatch,
        run_notify_orders,
        mock_order_cancel,
        pgsql,
        testpoint,
        waybill_ref='waybill_fb_3',
):

    happy_path_claims_segment_db.cancel_segment_by_user('seg3')
    result = await run_claims_segment_replication()
    assert result['stats']['updated-waybills'] == 1

    @testpoint('notify-orders-change-revision')
    def testpoint_change_revision(data):
        cursor = pgsql['cargo_dispatch'].cursor()

        cursor.execute(
            """
            UPDATE cargo_dispatch.waybills
            SET revision = revision + 1
            WHERE external_ref = %s;
        """,
            (waybill_ref,),
        )
        return {'enable': True}

    await run_notify_orders(expect_fail=True)
    assert testpoint_change_revision.times_called == 1


async def test_notify_change_destination(
        happy_path_state_orders_created,
        happy_path_claims_segment_db,
        run_notify_orders,
        mock_order_change_destination,
        get_point_execution_by_visit_order,
        trigger_need_to_notify_orders,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        waybill_ref='waybill_smart_1',
):
    await trigger_need_to_notify_orders(waybill_ref)
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)

    # Confirm first point
    segment = happy_path_claims_segment_db.get_segment('seg1')
    segment.set_point_visit_status('p1', 'visited')

    result = await run_notify_orders()
    extract_oldest_waybill(result)
    assert result['stats'] == {
        'waybills-for-handling': 1,
        'resolved-notified': 0,
        'updated-entries': 1,
        'unresolved-fail': 0,
        'stq-fail': 0,
    }
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-notify-orders',
    )
    assert stats['stats']['marked-as-resolved'] == 0

    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=2,
    )
    assert mock_order_change_destination.times_called == 1
    assert mock_order_change_destination.next_call()['request'].json == {
        'order_id': matching.any_string,
        'dispatch_version': 2,
        'claim_id': 'claim_seg1',
        'segment_id': 'seg1',
        'claim_point_id': point['claim_point_id'],
        'idempotency_token': 'waybill_smart_1_12_2',
    }


async def test_waybill_state_error(
        happy_path_state_orders_created,
        run_notify_orders,
        trigger_need_to_notify_orders,
        mock_claims_bulk_info,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
):
    """
    Error while trying to build waybill_state
    Check that waybill will not be marked as resolved.
    Just retry on next job iteration
    """
    await trigger_need_to_notify_orders('waybill_smart_1')
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)

    # Do not return segment seg2 info to trigger fail
    mock_claims_bulk_info(segments_to_ignore=['seg2'])

    result = await run_notify_orders(expect_fail=True)
    extract_oldest_waybill(result)
    assert result['stats'] == {
        'waybills-for-handling': 1,
        'resolved-notified': 0,
        'updated-entries': 1,
        'unresolved-fail': 0,
        'stq-fail': 0,
    }
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-notify-orders',
    )
    assert stats['stats']['marked-as-resolved'] == 0


async def test_error_and_success(
        happy_path_state_orders_created,
        run_notify_orders,
        trigger_need_to_notify_orders,
        mock_claims_bulk_info,
        taxi_cargo_dispatch,
        stq_runner,
        taxi_cargo_dispatch_monitor,
):
    """
    Error while trying to build waybill_state for one segment
    But second waybill successfully processed
    """
    await trigger_need_to_notify_orders('waybill_smart_1')
    await trigger_need_to_notify_orders('waybill_fb_3')

    await taxi_cargo_dispatch.tests_control(reset_metrics=True)

    # Do not return segment seg2 info to trigger fail
    mock_claims_bulk_info(segments_to_ignore=['seg2'])

    result = await run_notify_orders(should_set_stq=False)
    extract_oldest_waybill(result)
    assert result['stats'] == {
        'waybills-for-handling': 2,
        'resolved-notified': 0,
        'updated-entries': 2,
        'unresolved-fail': 0,
        'stq-fail': 0,
    }

    await stq_runner.cargo_dispatch_notify_orders.call(
        task_id='test',
        kwargs={'waybill_ref': 'waybill_fb_3'},
        expect_fail=False,
    )
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-notify-orders',
    )
    assert stats['stats']['marked-as-resolved'] == 0

    await stq_runner.cargo_dispatch_notify_orders.call(
        task_id='test',
        kwargs={'waybill_ref': 'waybill_smart_1'},
        expect_fail=True,
    )


@pytest.mark.parametrize(
    ['error_code', 'need_retry'], [('bad_state', True), ('gone', False)],
)
async def test_retries(
        happy_path_state_orders_created,
        run_claims_segment_replication,
        run_notify_orders,
        happy_path_claims_segment_db,
        mock_claims_bulk_info,
        mock_order_cancel,
        taxi_cargo_dispatch_monitor,
        taxi_cargo_dispatch,
        error_code: str,
        need_retry: bool,
        segment_id='seg3',
        waybill_ref='waybill_fb_3',
):
    """
    Failed to commit taxi order (500),
    user tries to cancel it in the same time.

    Check order/cancel fail and retry later.
    (order/cancel will return 409 bad_state until draft is alive)
    """
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    mock_order_cancel.status_code = 409
    mock_order_cancel.error_code = error_code
    happy_path_claims_segment_db.cancel_segment_by_user(segment_id)
    result = await run_claims_segment_replication()
    assert result['stats']['updated-waybills'] == 1

    result = await run_notify_orders()
    assert result['stats']['waybills-for-handling'] == 1
    assert result['stats']['updated-entries'] == 1

    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-notify-orders',
    )
    assert stats['stats']['marked-as-resolved'] == 1

    # Check that waybill will be processed in next job iteration
    result = await run_notify_orders(expect_fail=need_retry)
    extract_oldest_waybill(result)
    assert result['stats']['waybills-for-handling'] == 1
    assert result['stats']['updated-entries'] == 1


@pytest.mark.parametrize(
    'enable_config, send_min_version', [(False, False), (True, True)],
)
async def test_segments_revision(
        happy_path_state_orders_created,
        run_notify_orders,
        mock_order_change_destination,
        happy_path_claims_segment_bulk_info_handler,
        taxi_cargo_dispatch,
        taxi_config,
        trigger_need_to_notify_orders,
        enable_config,
        send_min_version,
        waybill_ref='waybill_fb_3',
):
    taxi_config.set_values(
        dict(
            CARGO_DISPATCH_READ_SEGMENTS_WITH_REVISION={
                'choose_routers': enable_config,
                'fallback_router': enable_config,
                'create_orders': enable_config,
                'notify_orders': enable_config,
            },
        ),
    )
    await taxi_cargo_dispatch.invalidate_caches()
    happy_path_claims_segment_bulk_info_handler.flush()

    await trigger_need_to_notify_orders(waybill_ref)
    result = await run_notify_orders()

    extract_oldest_waybill(result)
    assert result['stats']['updated-entries'] == 1

    if send_min_version:
        assert (
            happy_path_claims_segment_bulk_info_handler.next_call()[
                'request'
            ].json['segment_ids'][0]['min_revision']
            == 1
        )
    else:
        assert (
            'min_revision'
            not in happy_path_claims_segment_bulk_info_handler.next_call()[
                'request'
            ].json['segment_ids'][0]
        )


async def test_change_destinations_token_for_alive_batch(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        happy_path_state_seg4_routers_chosen,
        waybill_from_segments,
        request_waybill_update_proposition,
        run_choose_waybills,
        mock_cargo_orders_bulk_info,
        read_waybill_info,
        run_notify_orders,
        mockserver,
        run_claims_segment_replication,
        happy_path_claims_segment_db,
        update_proposition_alive_batch_stq,
):
    """
    Alive batch
    Use new waybill ref in idempotency_token
    """

    # 1. Check that old waybill used to changedestination

    @mockserver.json_handler('/cargo-orders/v1/order/change-destination')
    def change_destination_1(request):
        assert request.json['idempotency_token'] == 'waybill_smart_1_12_2'
        return {}

    happy_path_claims_segment_db.set_segment_point_visit_status(
        'seg1', 'p1', 'visited', is_caused_by_user=True,
    )
    await run_claims_segment_replication()

    result = await run_notify_orders()
    assert result['stats']['waybills-for-handling'] == 1
    assert change_destination_1.times_called == 1

    # 2. Update waybill

    mock_cargo_orders_bulk_info(tariff_class='eda')
    proposition = await waybill_from_segments(
        'smart_router', 'new_waybill_ref', 'seg1', 'seg2', 'seg4',
    )
    response = await request_waybill_update_proposition(
        proposition, 'waybill_smart_1',
    )
    assert response.status_code == 200

    await run_choose_waybills()
    await update_proposition_alive_batch_stq(
        'new_waybill_ref', wait_testpoint=False, call=True,
    )

    # 3. Check that new waybill used to changedestination

    @mockserver.json_handler('/cargo-orders/v1/order/change-destination')
    def change_destination_2(request):
        assert request.json['idempotency_token'] == 'new_waybill_ref_21_3'
        return {}

    # Confirm first point
    segment = happy_path_claims_segment_db.get_segment('seg1')
    segment.set_point_visit_status('p2', 'visited')

    result = await run_notify_orders()
    assert result['stats']['waybills-for-handling'] == 1
    assert change_destination_2.times_called == 1
