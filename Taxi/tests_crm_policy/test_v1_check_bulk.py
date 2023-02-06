import copy

import pytest


async def send_bulk(
        taxi_crm_policy,
        channel,
        idempotency_token=None,
        second_user='user2',
        add_user_with_tag_segment=False,
):
    body = {
        'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
        'items': [
            {'experiment_group_id': '1_testing', 'entity_id': 'user1'},
            {'experiment_group_id': '0_testing', 'entity_id': second_user},
            {'entity_id': 'user3'},
        ],
    }

    if add_user_with_tag_segment:
        body['items'] += [
            {'entity_id': 'user4', 'segment_tag': 'test_segment'},
            # not known segment - should be treated same as user3
            {'entity_id': 'user5', 'segment_tag': 'not_known_segment'},
        ]

    if idempotency_token:
        body['idempotency_token'] = idempotency_token
    response = await taxi_crm_policy.post(
        '/v1/check_update_send_message_bulk', json=body,
    )
    return response


def return_admin_response(channel):
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


@pytest.mark.parametrize('channel', ['push'])
@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_check_bulk(
        taxi_crm_policy, mockserver, pgsql, mocked_time, channel, taxi_config,
):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        return return_admin_response(channel)

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    config_content = taxi_config.get('CRM_POLICY_CHANNEL_DEFAULTS_V7')
    config_content['test_segment'] = copy.deepcopy(
        config_content['__default__'],
    )
    config_content['test_segment']['dbid_uuid'][channel][
        'pause_time_default'
    ] = 500

    taxi_config.set_values({'CRM_POLICY_CHANNEL_DEFAULTS_V7': config_content})
    await taxi_crm_policy.invalidate_caches(clean_update=False)

    response = await send_bulk(
        taxi_crm_policy, channel, add_user_with_tag_segment=True,
    )
    assert response.status_code == 200
    assert response.json() == {
        'allowed': [True, True, True, True, True],
        'unrecognized_tags': ['not_known_segment'],
    }

    mocked_time.sleep(50)
    response = await send_bulk(
        taxi_crm_policy, channel, add_user_with_tag_segment=True,
    )
    assert response.status_code == 200
    assert response.json() == {
        'allowed': [True, False, False, False, False],
        'unrecognized_tags': ['not_known_segment'],
    }

    mocked_time.sleep(40)
    response = await send_bulk(
        taxi_crm_policy, channel, add_user_with_tag_segment=True,
    )
    assert response.status_code == 200
    assert response.json() == {
        'allowed': [True, False, True, False, True],
        'unrecognized_tags': ['not_known_segment'],
    }

    mocked_time.sleep(20)
    response = await send_bulk(
        taxi_crm_policy, channel, add_user_with_tag_segment=True,
    )
    assert response.status_code == 200
    assert response.json() == {
        'allowed': [True, True, False, False, False],
        'unrecognized_tags': ['not_known_segment'],
    }

    mocked_time.sleep(500)
    response = await send_bulk(
        taxi_crm_policy, channel, add_user_with_tag_segment=True,
    )
    assert response.status_code == 200
    assert response.json() == {
        'allowed': [True, True, True, True, True],
        'unrecognized_tags': ['not_known_segment'],
    }


@pytest.mark.config(CRM_POLICY_ENTITY_WHITE_LIST={'dbid_uuid': ['user2']})
@pytest.mark.parametrize('channel', ['push'])
@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_bulk_allowed_users(
        taxi_crm_policy, mockserver, pgsql, mocked_time, channel,
):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        return return_admin_response(channel)

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    response = await send_bulk(taxi_crm_policy, channel)
    # second request placed here intentionally
    response = await send_bulk(taxi_crm_policy, channel)
    assert response.json() == {'allowed': [False, True, False]}
    assert response.status_code == 200


@pytest.mark.parametrize('channel', ['push'])
@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_bulk_idempotency(
        taxi_crm_policy, mockserver, pgsql, mocked_time, channel,
):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        return return_admin_response(channel)

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    response = await send_bulk(taxi_crm_policy, channel, 'idemp_token_1')
    assert response.json() == {'allowed': [True, True, True]}
    # second message with same token should have same reply
    response = await send_bulk(taxi_crm_policy, channel, 'idemp_token_1')
    assert response.json() == {'allowed': [True, True, True]}
    assert response.status_code == 200


@pytest.mark.parametrize('channel', ['push'])
@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_bulk_idempotency_different(
        taxi_crm_policy, mockserver, pgsql, mocked_time, channel,
):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        return return_admin_response(channel)

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    response = await send_bulk(taxi_crm_policy, channel, 'idemp_token_1')
    assert response.json() == {'allowed': [True, True, True]}
    # second message with same token should have same reply
    response = await send_bulk(taxi_crm_policy, channel, 'idemp_token_2')
    assert response.json() == {'allowed': [False, False, False]}
    assert response.status_code == 200


@pytest.mark.parametrize('channel', ['push'])
@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_bulk_idempotency_no_match_users(
        taxi_crm_policy, mockserver, pgsql, mocked_time, channel,
):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        return return_admin_response(channel)

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    response = await send_bulk(taxi_crm_policy, channel, 'idemp_token_1')
    assert response.json() == {'allowed': [True, True, True]}
    # second message with same token should have same reply
    response = await send_bulk(
        taxi_crm_policy, channel, 'idemp_token_1', 'user_5',
    )
    assert response.status_code == 400


@pytest.mark.parametrize('channel', ['push'])
@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_bulk_idempotency_mix(
        taxi_crm_policy, mockserver, pgsql, mocked_time, channel,
):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        return return_admin_response(channel)

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    response = await send_bulk(
        taxi_crm_policy, channel, 'idemp_token_0', 'user_5',
    )
    response = await send_bulk(taxi_crm_policy, channel, 'idemp_token_1')
    assert response.json() == {'allowed': [False, True, False]}
    # second message with same token should have same reply
    response = await send_bulk(taxi_crm_policy, channel, 'idemp_token_1')
    assert response.json() == {'allowed': [False, True, False]}
    assert response.status_code == 200


@pytest.mark.parametrize('channel', ['push'])
@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_bulk_duplicates(
        taxi_crm_policy, mockserver, pgsql, mocked_time, channel,
):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        return return_admin_response(channel)

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    response = await send_bulk(
        taxi_crm_policy, channel, 'idemp_token_0', 'user1',
    )
    assert response.json() == {
        'code': '400',
        'message': 'entity_id user1 duplicated',
    }
    assert response.status_code == 400


@pytest.mark.parametrize('channel', ['push'])
@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_bulk_add_group(
        taxi_crm_policy, mockserver, pgsql, mocked_time, channel,
):
    add_group = False

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        if not add_group:
            return [
                {
                    'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
                    'valid_until': '2020-12-31T23:59:59+00:00',
                    'experiment': {
                        'experiment_id': (
                            'crm:hub:push_transporting_seatbelts_poll'
                        ),
                        'groups': [],
                    },
                },
            ]
        return return_admin_response(channel)

    await taxi_crm_policy.invalidate_caches(clean_update=False)
    add_group = True

    response = await send_bulk(taxi_crm_policy, channel)
    assert response.status_code == 200
    assert response.json() == {'allowed': [True, True, True]}
