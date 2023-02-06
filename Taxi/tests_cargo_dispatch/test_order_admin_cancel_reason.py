import pytest


@pytest.mark.parametrize(
    'enabled, activity_remove_tanker_key, need_autoreorder_tanker_key',
    [
        (False, None, None),
        (False, None, 'need_autoreorder_tanker_key'),
        (False, 'activity_remove_tanker_key', None),
        (False, 'activity_remove_tanker_key', 'need_autoreorder_tanker_key'),
        (True, None, None),
        (True, None, 'need_autoreorder_tanker_key'),
        (True, 'activity_remove_tanker_key', None),
        (True, 'activity_remove_tanker_key', 'need_autoreorder_tanker_key'),
    ],
)
@pytest.mark.parametrize('admin_cancel_reason', ['folder_id.reason_id', None])
@pytest.mark.parametrize(
    'fail_reason, is_old_reorder_required',
    [
        ('performer_cancel', True),
        ('admin_reorder', True),
        ('admin_reorder', False),
    ],
)
async def test_order_admin_cancel_reason(
        happy_path_state_orders_created,
        set_up_cargo_dispatch_reorder_exp,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        mock_cargo_orders_bulk_info,
        mockserver,
        run_notify_claims,
        taxi_config,
        testpoint,
        pgsql,
        enabled: bool,
        activity_remove_tanker_key: str,
        need_autoreorder_tanker_key: str,
        admin_cancel_reason: str,
        fail_reason: str,
        is_old_reorder_required: bool,
        waybill_id='waybill_smart_1',
):
    await set_up_cargo_dispatch_reorder_exp(
        fail_reason=fail_reason,
        is_reorder_required=is_old_reorder_required,
        admin_cancel_reason_null=True,
    )
    childs = [{'id': 'reason_id', 'menu_item_tanker_key': 'reason_tanker_key'}]
    if activity_remove_tanker_key:
        childs[-1]['activity_remove_tanker_key'] = activity_remove_tanker_key
    if need_autoreorder_tanker_key:
        childs[-1]['need_autoreorder_tanker_key'] = need_autoreorder_tanker_key
    taxi_config.set(
        CARGO_DISPATCH_ORDER_ADMIN_CANCEL_MENU_V2={
            'enabled': enabled,
            'cancel_button_tanker_key': 'order_cancel',
            'cancel_reason_tree': [
                {
                    'childs': childs,
                    'id': 'folder_id',
                    'menu_item_tanker_key': 'folder_tanker_key',
                },
            ],
        },
    )
    await taxi_cargo_dispatch.invalidate_caches()

    mock_cargo_orders_bulk_info(admin_cancel_reason=admin_cancel_reason)

    @mockserver.json_handler(
        '/cargo-claims/v1/segments/dispatch/bulk-update-state',
    )
    def bulk_update_handler(request):
        if request.json['segments'][0]['id'] == 'seg2' and (
                not need_autoreorder_tanker_key
                and not is_old_reorder_required
                or not is_old_reorder_required
                and admin_cancel_reason is None
        ):
            assert request.json['segments'][0]['resolution'] == 'failed'
            if admin_cancel_reason:
                assert (
                    request.json['segments'][0]['admin_cancel_reason']
                    == admin_cancel_reason
                )
        return {
            'processed_segment_ids': [
                seg['id'] for seg in request.json['segments']
            ],
        }

    @testpoint('order-fail::is_reorder_required')
    def _is_reorder_required(data):
        assert data['is_reorder_required'] == (
            (
                enabled
                and need_autoreorder_tanker_key is not None
                and admin_cancel_reason is not None
            )
            or (admin_cancel_reason is None and is_old_reorder_required)
        )

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json={
            'order_id': '6dac297a-33ed-42e7-9101-af81ddf59602',
            'waybill_id': waybill_id,
            'taxi_order_id': 'taxi-order',
            'reason': fail_reason,
            'admin_cancel_reason': admin_cancel_reason,
            'lookup_version': 0,
        },
    )
    assert response.status_code == 200

    if admin_cancel_reason is None and is_old_reorder_required:
        cursor = pgsql['cargo_dispatch'].cursor()
        cursor.execute(
            f"""select segment_id, reason, ticket, source
                from cargo_dispatch.admin_segment_reorders""",
        )
        reorders = list(cursor)
        assert reorders
        for reorder in reorders:
            assert reorder[1] == fail_reason

    result = await run_notify_claims()
    result['stats'].pop('oldest-segment-lag-ms')
    assert result['stats'] == {
        'segments-count': 2,
        'segments-updated-count': 2,
        'stq-fail': 0,
        'stq-success': 2,
    }
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-notify-claims',
    )
    assert stats['stats'] == {'segments-notified-count': 2}
    assert bulk_update_handler.times_called == 2
