# pylint: disable=import-only-modules
import pytest

from tests_crm_policy.utils import select_columns_from_table


@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_uuid_form_wrong(taxi_crm_policy, mockserver):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        resp = [
            {
                'campaign_id': '8a457abdc10d4450a3ab199f43ed44bc',
                'valid_until': '2020-12-31T23:59:59+00:00',
                'experiment': {
                    'experiment_id': (
                        'crm:hub:push_transporting_seatbelts_poll'
                    ),
                    'groups': [
                        {
                            'group_id': '__default__',
                            'channel': 'push',
                            'cooldown': 80,
                        },
                    ],
                },
            },
        ]
        return resp

    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'user_id',
            'channel_type': 'push',
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
        },
    )

    assert response.json() == {'allowed': True}


@pytest.mark.pgsql(
    'crm_policy',
    files=[
        'create_channels_default.sql',
        'add_non_dash_uuid_communication.sql',
    ],
)
async def test_read_from_table_1(taxi_crm_policy, mockserver):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        resp = [
            {
                'campaign_id': '8a457abdc10d4450a3ab199f43ed44bc',
                'valid_until': '2020-12-31T23:59:59+00:00',
                'experiment': {
                    'experiment_id': (
                        'crm:hub:push_transporting_seatbelts_poll'
                    ),
                    'groups': [
                        {
                            'group_id': '__default__',
                            'channel': 'push',
                            'cooldown': 80,
                        },
                    ],
                },
            },
        ]
        return resp

    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'user_id',
            'channel_type': 'push',
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
        },
    )

    assert response.json() == {'allowed': True}


@pytest.mark.pgsql(
    'crm_policy',
    files=['create_channels_default.sql', 'add_dash_uuid_communication.sql'],
)
async def test_read_from_table_2(taxi_crm_policy, mockserver, pgsql):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        resp = [
            {
                'campaign_id': '8a457abdc10d4450a3ab199f43ed44bc',
                'valid_until': '2020-12-31T23:59:59+00:00',
                'experiment': {
                    'experiment_id': (
                        'crm:hub:push_transporting_seatbelts_poll'
                    ),
                    'groups': [
                        {
                            'group_id': '__default__',
                            'channel': 'push',
                            'cooldown': 80,
                        },
                    ],
                },
            },
        ]
        return resp

    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'dbid_uuid',
            'channel_type': 'push',
            'campaign_id': '8a457abdc10d4450a3ab199f43ed44bc',
        },
    )

    assert response.json() == {'allowed': True}

    response = await taxi_crm_policy.post(
        '/v1/check_update_send_message_bulk',
        json={
            'campaign_id': '8a457abdc10d4450a3ab199f43ed44bc',
            'items': [{'entity_id': 'testKeyID3'}, {'entity_id': 'user2'}],
        },
    )
    assert response.json() == {'allowed': [False, True]}

    saved_campaign = select_columns_from_table(
        'crm_policy.registered_external_communications',
        ['campaign_id'],
        pgsql['crm_policy'],
        1000,
    )

    assert saved_campaign == [
        {'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc'},
    ]
