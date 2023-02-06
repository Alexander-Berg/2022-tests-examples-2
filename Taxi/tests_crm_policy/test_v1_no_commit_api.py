import pytest


@pytest.mark.pgsql(
    'crm_policy', files=['create_1_channel_1_communication.sql'],
)
async def test_ignore_no_commit_result(taxi_crm_policy, pgsql):
    async def custom_request_api(api):
        response = await taxi_crm_policy.get(
            api,
            params={
                'entity_id': 'testKeyID3',
                'entity_type': 'user_id',
                'channel_type': 'fullscreen',
                'campaign_id': '1',
            },
        )
        return response

    response = await custom_request_api('/v1/check_send_message')
    assert response.json() == {'allowed': True}
    response = await custom_request_api('/v1/check_send_message')
    assert response.json() == {'allowed': True}
    response = await custom_request_api('/v1/check_update_send_message')
    assert response.json() == {'allowed': True}
    response = await custom_request_api('/v1/check_send_message')
    assert response.json() == {'allowed': False}
    response = await custom_request_api('/v1/check_update_send_message')
    assert response.json() == {'allowed': False}


@pytest.mark.pgsql(
    'crm_policy', files=['create_1_channel_1_communication.sql'],
)
async def test_ignore_no_commit_result2(taxi_crm_policy, pgsql):
    async def custom_request_api(api):
        response = await taxi_crm_policy.get(
            api,
            params={
                'entity_id': 'testKeyID3',
                'entity_type': 'user_id',
                'channel_type': 'fullscreen',
                'campaign_id': '1',
            },
        )
        return response

    response = await custom_request_api('/v1/check_send_message')
    assert response.json() == {'allowed': True}
    response = await custom_request_api('/v1/check_send_message')
    assert response.json() == {'allowed': True}
    response = await custom_request_api('/v1/check_update_send_message')
    assert response.json() == {'allowed': True}
    response = await custom_request_api('/v1/check_send_message')
    assert response.json() == {'allowed': False}
    response = await custom_request_api('/v1/check_update_send_message')
    assert response.json() == {'allowed': False}


async def send_bulk(taxi_crm_policy, channel):
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


async def send_bulk_no_commit(taxi_crm_policy, channel):
    response = await taxi_crm_policy.post(
        '/v1/check_send_message_bulk',
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


@pytest.mark.parametrize('channel', ['push'])
@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_check_bulk(
        taxi_crm_policy, mockserver, pgsql, mocked_time, channel,
):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        resp = [
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
                        {
                            'group_id': '__default__',
                            'channel': channel,
                            'cooldown': 80,
                        },
                    ],
                },
            },
        ]
        return resp

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    response = await send_bulk_no_commit(taxi_crm_policy, channel)
    assert response.json() == {'allowed': [True, True, True]}
    assert response.status_code == 200

    response = await send_bulk_no_commit(taxi_crm_policy, channel)
    assert response.json() == {'allowed': [True, True, True]}
    assert response.status_code == 200

    response = await send_bulk(taxi_crm_policy, channel)
    assert response.json() == {'allowed': [True, True, True]}
    assert response.status_code == 200

    mocked_time.sleep(50)

    response = await send_bulk_no_commit(taxi_crm_policy, channel)
    assert response.json() == {'allowed': [True, False, False]}
    assert response.status_code == 200

    response = await send_bulk(taxi_crm_policy, channel)
    assert response.status_code == 200
    assert response.json() == {'allowed': [True, False, False]}

    mocked_time.sleep(40)

    response = await send_bulk_no_commit(taxi_crm_policy, channel)
    assert response.json() == {'allowed': [True, False, True]}
    assert response.status_code == 200

    response = await send_bulk(taxi_crm_policy, channel)
    assert response.status_code == 200
    assert response.json() == {'allowed': [True, False, True]}

    mocked_time.sleep(20)

    response = await send_bulk_no_commit(taxi_crm_policy, channel)
    assert response.json() == {'allowed': [True, True, False]}
    assert response.status_code == 200

    response = await send_bulk(taxi_crm_policy, channel)
    assert response.status_code == 200
    assert response.json() == {'allowed': [True, True, False]}


@pytest.mark.config(CRM_POLICY_ENTITY_WHITE_LIST={'user_id': ['testKeyID3']})
@pytest.mark.pgsql(
    'crm_policy', files=['create_1_channel_1_communication.sql'],
)
async def test_no_commit_allowed(taxi_crm_policy, pgsql):
    async def custom_request_api(api):
        response = await taxi_crm_policy.get(
            api,
            params={
                'entity_id': 'testKeyID3',
                'entity_type': 'user_id',
                'channel_type': 'fullscreen',
                'campaign_id': '1',
            },
        )
        return response

    response = await custom_request_api('/v1/check_update_send_message')
    assert response.json() == {'allowed': True}
    response = await custom_request_api('/v1/check_send_message')
    assert response.json() == {'allowed': True}
