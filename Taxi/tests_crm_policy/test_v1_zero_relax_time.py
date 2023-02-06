# pylint: disable=import-only-modules
import pytest


@pytest.mark.pgsql(
    'crm_policy', files=['create_1_channel_1_communication.sql'],
)
async def test_communication_filter_called(taxi_crm_policy, pgsql, testpoint):
    communication_filter_processed = False

    @testpoint('BranchCommunicationFilterCalled')
    async def _data_race_init_func(data):
        nonlocal communication_filter_processed
        communication_filter_processed = True

    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID',
            'entity_type': 'user_id',
            'channel_type': 'push',
            'campaign_id': '1',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'allowed': True}
    assert communication_filter_processed


@pytest.mark.pgsql(
    'crm_policy', files=['create_zero_relax_time_communication.sql'],
)
async def test_communication_filter_not_called(
        taxi_crm_policy, pgsql, testpoint,
):
    communication_filter_processed = False

    @testpoint('BranchCommunicationFilterCalled')
    async def _data_race_init_func(data):
        nonlocal communication_filter_processed
        communication_filter_processed = True

    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID',
            'entity_type': 'user_id',
            'channel_type': 'push',
            'campaign_id': '1',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'allowed': True}
    assert not communication_filter_processed
