import pytest


@pytest.mark.parametrize(
    'autocancel_reason',
    [
        'candidates_empty',
        'candidates_no_one_accepted',
        'performer_not_found_after_autoreorder',
        'performer_not_found_after_support_autoreorder',
    ],
)
async def test_get_order_autocancel_reason(
        happy_path_state_orders_created,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        mock_cargo_orders_bulk_info,
        mockserver,
        run_notify_claims,
        autocancel_reason: str,
        waybill_id='waybill_smart_1',
):
    mock_cargo_orders_bulk_info(autocancel_reason=autocancel_reason)

    @mockserver.json_handler(
        '/cargo-claims/v1/segments/dispatch/bulk-update-state',
    )
    def bulk_update_handler(request):
        assert len(request.json['segments']) == 1
        if request.json['segments'][0]['id'] == 'seg1':
            assert (
                request.json['segments'][0]['resolution']
                == 'performer_not_found'
            )
            assert (
                request.json['segments'][0]['autocancel_reason']
                == autocancel_reason
            )
        return {
            'processed_segment_ids': [
                seg['id'] for seg in request.json['segments']
            ],
        }

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json={
            'order_id': '6dac297a-33ed-42e7-9101-af81ddf59602',
            'waybill_id': waybill_id,
            'taxi_order_id': 'taxi-order',
            'reason': 'performer_not_found',
            'lookup_version': 0,
        },
    )
    assert response.status_code == 200

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
