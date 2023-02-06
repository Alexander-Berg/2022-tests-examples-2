# pylint: disable=import-only-modules
import pytest


@pytest.mark.pgsql('crm_policy', files=['create_channels.sql'])
@pytest.mark.parametrize(
    'channel',
    [
        'fullscreen',
        'push',
        'sms',
        'wall',
        'promo_fs',
        'promo_card',
        'promo_notification',
    ],
)
async def test_allow_first_message(taxi_crm_policy, pgsql, channel):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'user_id',
            'channel_type': channel,
            'campaign_id': channel,
        },
    )

    assert response.json() == {'allowed': True}

    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'user_id',
            'channel_type': channel,
            'campaign_id': channel,
        },
    )

    assert response.json() == {'allowed': False}


@pytest.mark.pgsql('crm_policy', files=['create_channels.sql'])
@pytest.mark.parametrize(
    'channel',
    ['push', 'sms', 'wall', 'promo_fs', 'promo_card', 'promo_notification'],
)
async def test_bulk_message(taxi_crm_policy, pgsql, channel, mockserver):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        return [
            {
                'campaign_id': '246',
                'valid_until': '2021-10-28T14:33:35.152528+03:00',
                'entity_type': 'user_id',
                'experiment': {
                    'experiment_id': '__default__',
                    'groups': [
                        {
                            'group_id': '518',
                            'channel': 'promo_fs',
                            'cooldown': 31536000,
                        },
                        {
                            'group_id': '519',
                            'channel': 'promo_fs',
                            'cooldown': 31536000,
                        },
                        {
                            'group_id': '517',
                            'channel': 'push',
                            'cooldown': 31536000,
                        },
                        {
                            'group_id': '516',
                            'channel': 'push',
                            'cooldown': 31536000,
                        },
                    ],
                },
            },
            {
                'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
                'valid_until': '2020-12-31T23:59:59+00:00',
                'experiment': {
                    'experiment_id': (
                        'crm:hub:push_transporting_seatbelts_poll'
                    ),
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
                    ],
                },
            },
        ]

    response = await taxi_crm_policy.post(
        '/v1/check_update_send_message_bulk',
        json={
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
            'items': [
                {'experiment_group_id': '1_testing', 'entity_id': 'user1'},
                {'experiment_group_id': '0_testing', 'entity_id': 'user2'},
            ],
        },
    )

    assert response.json() == {'allowed': [True, True]}

    response = await taxi_crm_policy.post(
        '/v1/check_update_send_message_bulk',
        json={
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
            'items': [
                {'experiment_group_id': '1_testing', 'entity_id': 'user1'},
                {'experiment_group_id': '0_testing', 'entity_id': 'user2'},
            ],
        },
    )

    assert response.json() == {'allowed': [False, False]}
