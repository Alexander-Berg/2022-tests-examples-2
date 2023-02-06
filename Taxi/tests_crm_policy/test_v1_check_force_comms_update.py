import pytest


@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_inline_failed(taxi_crm_policy):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'user_id',
            'channel_type': 'push',
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
        },
    )

    assert response.json() == {
        'code': '400',
        'message': (
            'Unregistered campaign_id: 8a457abd-c10d-4450-a3ab-199f43ed44bc'
        ),
    }


@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_inline_request_updated(taxi_crm_policy, mockserver):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'user_id',
            'channel_type': 'push',
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
        },
    )

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        return []

    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'user_id',
            'channel_type': 'push',
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
        },
    )

    assert _mock_crm_admin.times_called == 1

    assert response.json() == {
        'code': '400',
        'message': (
            'Unregistered campaign_id: 8a457abd-c10d-4450-a3ab-199f43ed44bc'
        ),
    }

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


@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_force_update_call_admin(
        taxi_crm_policy, mockserver, pgsql, mocked_time,
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
                            'group_id': '__default__',
                            'channel': 'push',
                            'cooldown': 80,
                        },
                    ],
                },
            },
        ]
        return resp

    assert _mock_crm_admin.times_called == 0

    response = await taxi_crm_policy.post(
        '/v1/force_update_communications', json={},
    )
    assert response.status_code == 200
    assert _mock_crm_admin.times_called == 1

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


@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_forbid_first_allow_second_message(taxi_crm_policy, pgsql, load):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'user_id',
            'channel_type': 'push',
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
        },
    )

    assert response.json() == {
        'code': '400',
        'message': (
            'Unregistered campaign_id: 8a457abd-c10d-4450-a3ab-199f43ed44bc'
        ),
    }

    pgsql['crm_policy'].cursor().execute(
        load('create_external_communication.sql'),
    )
    await taxi_crm_policy.invalidate_caches(clean_update=False)

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


@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_not_delete_all_on_update(
        taxi_crm_policy, mockserver, pgsql, mocked_time, load,
):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin1(request):
        return []

    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'user_id',
            'channel_type': 'push',
            'campaign_id': '4a457abd-c10d-4450-a3ab-199f43ed44bc',
        },
    )

    assert response.json() == {
        'code': '400',
        'message': (
            'Unregistered campaign_id: 4a457abd-c10d-4450-a3ab-199f43ed44bc'
        ),
    }

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        resp = [
            {
                'campaign_id': '4a457abd-c10d-4450-a3ab-199f43ed44bc',
                'valid_until': '2020-12-31T23:59:59+00:00',
                'experiment': {
                    'experiment_id': (
                        'crm:hub:push_transporting_seatbelts_poll'
                    ),
                    'groups': [
                        {
                            'group_id': '__default__',
                            'channel': 'push',
                            'cooldown': 345700,
                        },
                    ],
                },
            },
        ]
        return resp

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    assert _mock_crm_admin.times_called == 1

    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'user_id',
            'channel_type': 'push',
            'campaign_id': '4a457abd-c10d-4450-a3ab-199f43ed44bc',
        },
    )

    assert response.json() == {'allowed': True}

    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID4',
            'entity_type': 'user_id',
            'channel_type': 'push',
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
        },
    )
    assert response.json() == {
        'code': '400',
        'message': (
            'Unregistered campaign_id: 8a457abd-c10d-4450-a3ab-199f43ed44bc'
        ),
    }

    response = await taxi_crm_policy.post(
        '/v1/force_update_communications', json={},
    )
    assert response.status_code == 200
    assert _mock_crm_admin.times_called == 3

    pgsql['crm_policy'].cursor().execute(
        load('create_external_communication.sql'),
    )

    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID4',
            'entity_type': 'user_id',
            'channel_type': 'push',
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
        },
    )

    assert response.json() == {'allowed': True}

    mocked_time.sleep(345800)

    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'user_id',
            'channel_type': 'push',
            'campaign_id': '4a457abd-c10d-4450-a3ab-199f43ed44bc',
        },
    )

    assert response.json() == {'allowed': True}
    assert _mock_crm_admin.times_called == 3
