import pytest


@pytest.mark.config(
    SHUTTLE_CONTROL_BILLING_SETTINGS={
        'enabled': True,
        'requests_bulk_size': 20,
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_main(taxi_shuttle_control, stq):
    response = await taxi_shuttle_control.post(
        'service/cron', json={'task_name': 'shuttle-billing-processor'},
    )
    assert response.status_code == 200

    assert stq.shuttle_send_driver_billing_data.times_called == 2

    stq_data = stq.shuttle_send_driver_billing_data.next_call()
    assert stq_data['queue'] == 'shuttle_send_driver_billing_data'
    del stq_data['kwargs']['log_extra']
    assert stq_data['kwargs'] == {'request_ids': [1]}

    stq_data = stq.shuttle_send_driver_billing_data.next_call()
    del stq_data['kwargs']['log_extra']
    assert stq_data['kwargs'] == {'request_ids': [2]}
