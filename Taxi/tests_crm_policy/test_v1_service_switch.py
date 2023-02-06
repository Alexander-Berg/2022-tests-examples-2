import socket

import pytest

HOST = socket.gethostname()


async def send_one(taxi_crm_policy, channel):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': channel,
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
            'experiment_id': 'crm:hub:push_transporting_seatbelts_poll',
            'experiment_group_id': '1_testing',
        },
    )
    return response


@pytest.mark.config(CRM_POLICY_SERVICE_ENABLED=False)
async def test_service_disabled(
        taxi_crm_policy, mockserver, pgsql, mocked_time,
):
    response = await send_one(taxi_crm_policy, 'push')
    assert response.status_code == 503
