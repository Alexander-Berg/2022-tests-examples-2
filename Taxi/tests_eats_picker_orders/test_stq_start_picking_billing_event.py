import pytest


@pytest.mark.parametrize(
    'response_status, expect_fail', [[200, False], [409, False], [401, True]],
)
async def test_stq_start_picking_billing_event(
        stq_runner, mockserver, response_status, expect_fail,
):
    @mockserver.json_handler('/eats-billing-storage/billing-storage/create')
    def _mock_eats_billing_storage(request):
        assert request.json['service'] == 'eats-picker-orders'
        assert request.json['status'] == 'new'
        assert request.json['kind'] == 'StartPickerOrderEvent'
        assert (
            request.json['external_event_ref'] == 'StartPickerOrderEvent/122'
        )
        assert request.json['external_obj_id'] == '999'
        assert request.json['service_user_id'] == '123-456'
        assert request.json['event_at'] == '2020-06-01T00:00:00'
        assert request.json['tags'] == []
        assert request.json['journal_entries'] == []

        assert request.json['data'] == {
            'picker_id': '123-456',
            'start_picker_order_at': '2020-06-01T00:00:00',
        }
        return mockserver.make_response(
            json={'message': 'OK', 'status': 'success'},
            status=response_status,
        )

    await stq_runner.send_start_picking_billing_event.call(
        task_id='sample_task',
        kwargs={
            'order_id': 122,
            'eats_id': '999',
            'picker_id': '123-456',
            'start_picking_at': '2020-06-01T00:00:00',
        },
        expect_fail=expect_fail,
    )
