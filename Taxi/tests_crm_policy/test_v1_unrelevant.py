import socket

import pytest

HOST = socket.gethostname()


async def send_bulk(taxi_crm_policy):
    response = await taxi_crm_policy.post(
        '/v1/check_update_send_message_bulk',
        json={
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
            'items': [
                {'experiment_group_id': '1_testing', 'entity_id': 'user1'},
                {'experiment_group_id': '0_testing', 'entity_id': 'user2'},
                {'entity_id': 'user3'},
            ],
        },
    )
    return response


async def send_unrelevant(taxi_crm_policy):
    response = await taxi_crm_policy.post(
        '/v1/mark_unrelevant',
        json={
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
            'entities': ['user1', 'user3'],
        },
    )
    return response


def return_admin_response():
    channel = 'push'
    return [
        {
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
            'valid_until': '2020-12-31T23:59:59+00:00',
            'experiment': {
                'experiment_id': 'crm:hub:push_transporting_seatbelts_poll',
                'groups': [
                    {
                        'group_id': '0_testing',
                        'channel': channel,
                        'cooldown': 100,
                    },
                    {
                        'group_id': '1_testing',
                        'channel': channel,
                        'cooldown': 10,
                    },
                    {
                        'group_id': '__default__',
                        'channel': channel,
                        'cooldown': 80,
                    },
                ],
            },
        },
    ]


@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_check_unrelevant(
        taxi_crm_policy, mockserver, pgsql, mocked_time,
):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        return return_admin_response()

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    response = await send_bulk(taxi_crm_policy)
    assert response.json() == {'allowed': [True, True, True]}
    assert response.status_code == 200
    response = await send_bulk(taxi_crm_policy)
    assert response.json() == {'allowed': [False, False, False]}
    assert response.status_code == 200

    response = await send_unrelevant(taxi_crm_policy)
    assert response.json() == {'num_marked': 2}
    assert response.status_code == 200

    response = await send_bulk(taxi_crm_policy)
    assert response.json() == {'allowed': [True, False, True]}
    assert response.status_code == 200
