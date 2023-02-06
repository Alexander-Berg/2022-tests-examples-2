# pylint: disable=import-only-modules
import datetime

import pytest

from tests_crm_policy.utils import select_columns_from_table
from tests_crm_policy.utils import select_columns_from_table_order


@pytest.mark.pgsql(
    'crm_policy', files=['create_1_channel_1_communication.sql'],
)
async def test_allow_first_message(taxi_crm_policy, pgsql):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
        },
    )

    assert response.json() == {'allowed': True}


@pytest.mark.pgsql(
    'crm_policy', files=['create_1_channel_1_communication.sql'],
)
async def test_allow_first_forbid_second_message(taxi_crm_policy, pgsql):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
        },
    )

    assert response.json() == {'allowed': True}

    response2 = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
        },
    )

    assert response2.json() == {'allowed': False}


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.pgsql('crm_policy', files=['create_1_message.sql'])
async def test_forbid_second_message_by_last_sended_time_span(
        taxi_crm_policy, pgsql,
):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
        },
    )

    assert response.json() == {'allowed': False}


@pytest.mark.now('2019-02-01T14:00:01Z')
@pytest.mark.pgsql('crm_policy', files=['create_1_message.sql'])
async def test_forbid_second_message_by_communication_time_span(
        taxi_crm_policy, pgsql,
):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
        },
    )

    assert response.json() == {'allowed': False}


@pytest.mark.now('2020-09-28T22:12:47Z')
@pytest.mark.pgsql('crm_policy', files=['create_1_message_daily.sql'])
async def test_forbid_second_message_by_communication_time_span_daily(
        taxi_crm_policy, pgsql,
):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
        },
    )

    assert response.json() == {'allowed': False}


@pytest.mark.now('2019-02-01T14:00:01Z')
@pytest.mark.pgsql(
    'crm_policy', files=['create_broken_external_communication.sql'],
)
async def test_communication_have_no_specification(taxi_crm_policy, pgsql):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '100500',
        },
    )

    assert response.status == 400
    assert response.json() == {
        'code': '400',
        'message': 'Unregistered campaign_id: 100500',
    }


@pytest.mark.now('2019-02-01T14:00:01Z')
@pytest.mark.pgsql(
    'crm_policy',
    files=[
        'create_channels_default.sql',
        'create_1_message.sql',
        'create_communications_default.sql',
    ],
)
async def test_allow_second_message_by_another_communication(
        taxi_crm_policy, pgsql,
):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '100500',
        },
    )

    assert response.json() == {'allowed': True}


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.pgsql(
    'crm_policy',
    files=[
        'create_channels_default.sql',
        'create_1_message.sql',
        'create_communications_default.sql',
    ],
)
async def test_forbid_second_message_by_another_communication(
        taxi_crm_policy, pgsql,
):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '100500',
        },
    )

    assert response.json() == {'allowed': False}


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.pgsql(
    'crm_policy',
    files=['create_channels_default.sql', 'create_1_message.sql'],
)
async def test_disallow_second_message_by_another_channel_type(
        taxi_crm_policy, pgsql,
):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
        },
    )

    assert response.json() == {'allowed': False}


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.pgsql(
    'crm_policy',
    files=['create_channels_default.sql', 'dummy_message_history.sql'],
)
async def test_correct_select_with_distinct(taxi_crm_policy, pgsql):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
        },
    )

    assert response.json() == {'allowed': True}
    rows = select_columns_from_table_order(
        'crm_policy.messages_history',
        ['id', 'entity_id', 'communication_id', 'send_at'],
        'id DESC',
        pgsql['crm_policy'],
        2,
    )

    assert rows == [
        {
            'id': 4,
            'entity_id': 1,
            'communication_id': 1,
            'send_at': datetime.datetime(2019, 2, 1, 14, 0),
        },
        {
            'id': 3,
            'entity_id': 1,
            'communication_id': 1,
            'send_at': datetime.datetime(2019, 2, 1, 13, 50, 59),
        },
    ]


@pytest.mark.pgsql(
    'crm_policy',
    files=['create_channels_default.sql', 'create_communications_default.sql'],
)
@pytest.mark.parametrize(
    'testpoint_name,allowed',
    [
        ('BranchWithDataRaceEntityIdInsert', False),
        ('BranchWithDataRaceCommitChanges3', True),
    ],
)
async def test_data_race_on_communication_id(
        taxi_crm_policy, pgsql, testpoint, testpoint_name, allowed,
):
    is_data_race_inited = False

    @testpoint(testpoint_name)
    async def data_race_init_func(data):
        nonlocal is_data_race_inited
        if not is_data_race_inited:
            is_data_race_inited = True
            response2 = await taxi_crm_policy.get(
                '/v1/check_update_send_message',
                params={
                    'entity_id': 'test_reciever',
                    'entity_type': 'user_id',
                    'channel_type': 'fullscreen',
                    'campaign_id': '100500',
                },
            )
            assert response2.json() == {'allowed': not allowed}

    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '100500',
        },
    )

    entity_ids = select_columns_from_table(
        'crm_policy.runtime_entities_meta',
        ['id', 'fullscreen_last_message_id'],
        pgsql['crm_policy'],
        1000,
    )
    assert entity_ids == [{'id': 1, 'fullscreen_last_message_id': 1}]

    assert response.json() == {'allowed': allowed}
    await data_race_init_func.wait_call()


@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_no_communication(taxi_crm_policy):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '100500',
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Unregistered campaign_id: 100500',
    }


@pytest.mark.pgsql(
    'crm_policy', files=['create_1_channel_1_communication.sql'],
)
async def test_allow_second_message_after_pause(taxi_crm_policy, mocked_time):
    mocked_time.set(datetime.datetime(2019, 2, 1, 14, 0))
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
        },
    )

    assert response.json() == {'allowed': True}
    await taxi_crm_policy.invalidate_caches(clean_update=True)
    mocked_time.sleep(1)

    response2 = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
        },
    )

    assert response2.json() == {'allowed': False}
    mocked_time.sleep(1)
    response3 = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
        },
    )

    assert response3.json() == {'allowed': True}


@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_missing_experiment_group_id(taxi_crm_policy):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '100500',
            'experiment_id': 'asdasd',
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'experiment_group_id is missing despite '
            'the experiment_id is specified'
            ', it can be used only simultaneously'
        ),
    }


@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_missing_experiment_id(taxi_crm_policy):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '100500',
            'experiment_group_id': 'asdasd',
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'experiment_id is missing despite '
            'the experiment_group_id is specified'
            ', it can be used only simultaneously'
        ),
    }


@pytest.mark.pgsql('crm_policy', files=['create_experiment_communication.sql'])
async def test_no_default_communication_timings(taxi_crm_policy):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'communication 1 has no default timings',
    }


@pytest.mark.pgsql('crm_policy', files=['create_experiment_communication.sql'])
async def test_no_specified_timings(taxi_crm_policy):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
            'experiment_id': 'FOO',
            'experiment_group_id': 'BAR',
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'communication 1 has no info about :"BAR"',
    }


@pytest.mark.pgsql('crm_policy', files=['create_experiment_communication.sql'])
async def test_experiment_timings(taxi_crm_policy, pgsql, mocked_time):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
            'experiment_id': 'AAA',
            'experiment_group_id': 'BBB',
        },
    )

    assert response.status_code == 200
    assert response.json() == {'allowed': True}

    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
            'experiment_id': 'AAA',
            'experiment_group_id': 'BBB',
        },
    )

    assert response.status_code == 200
    assert response.json() == {'allowed': False}

    mocked_time.sleep(90)

    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
            'experiment_id': 'AAA',
            'experiment_group_id': 'BBB',
        },
    )

    assert response.status_code == 200
    assert response.json() == {'allowed': False}

    mocked_time.sleep(11)

    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
            'experiment_id': 'AAA',
            'experiment_group_id': 'BBB',
        },
    )

    assert response.status_code == 200
    assert response.json() == {'allowed': True}


@pytest.mark.pgsql('crm_policy', files=['create_push_communication.sql'])
async def test_no_specified_channel_timings(taxi_crm_policy):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
            'experiment_id': 'AAA',
            'experiment_group_id': 'BBB',
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'Relax timings are not specified for channel_type fullscreen'
        ),
    }

    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'push',
            'campaign_id': '1',
            'experiment_id': 'AAA',
            'experiment_group_id': 'BBB',
        },
    )

    assert response.status_code == 200
    assert response.json() == {'allowed': True}


async def send_first_msg(taxi_crm_policy, pgsql):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID1',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
        },
    )
    return response


async def send_second_msg(taxi_crm_policy, pgsql):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID2',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
        },
    )
    return response


@pytest.mark.config(
    CRM_POLICY_QUOTAS_V2={'read': 1, 'write': 2, 'bulk_max_requests_count': 1},
)
@pytest.mark.pgsql(
    'crm_policy', files=['create_1_channel_1_communication.sql'],
)
async def test_forbid_by_quota_rd(taxi_crm_policy, pgsql, mocked_time):
    mocked_time.set(datetime.datetime(2019, 2, 1, 14, 0))
    await send_first_msg(taxi_crm_policy, pgsql)
    response = await send_first_msg(
        taxi_crm_policy, pgsql,
    )  # to increment read
    assert response.json() == {'allowed': False}

    response2 = await send_second_msg(taxi_crm_policy, pgsql)

    assert response2.status_code == 429
    assert response2.json() == {
        'code': '429',
        'message': 'Read Quota Exceeded',
    }


@pytest.mark.config(
    CRM_POLICY_QUOTAS_V2={'read': 2, 'write': 1, 'bulk_max_requests_count': 1},
)
@pytest.mark.pgsql(
    'crm_policy', files=['create_1_channel_1_communication.sql'],
)
async def test_forbid_by_quota_wr(taxi_crm_policy, pgsql, mocked_time):
    mocked_time.set(datetime.datetime(2019, 2, 1, 14, 1))
    await send_first_msg(taxi_crm_policy, pgsql)  # to increment write
    response2 = await send_second_msg(taxi_crm_policy, pgsql)

    assert response2.status_code == 429
    assert response2.json() == {
        'code': '429',
        'message': 'Write Quota Exceeded',
    }


@pytest.mark.config(CRM_POLICY_ENTITY_WHITE_LIST={'user_id': ['testKeyID1']})
@pytest.mark.pgsql(
    'crm_policy', files=['create_1_channel_1_communication.sql'],
)
async def test_allowed_user(taxi_crm_policy, mockserver, pgsql):
    response = await send_first_msg(taxi_crm_policy, pgsql)
    assert response.json() == {'allowed': True}
    assert response.status_code == 200
    response = await send_first_msg(taxi_crm_policy, pgsql)
    assert response.json() == {'allowed': True}
    assert response.status_code == 200


@pytest.mark.pgsql(
    'crm_policy', files=['create_1_message.sql', 'entity_ids_corrupted.sql'],
)
async def test_entity_ids_corrupted(taxi_crm_policy, pgsql):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
        },
    )
    assert response.json() == {'allowed': True}


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.pgsql(
    'crm_policy', files=['create_1_message.sql', 'entity_ids_updated.sql'],
)
async def test_entity_ids_updated(taxi_crm_policy, pgsql):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
        },
    )
    assert response.json() == {'allowed': False}


async def send_with_token(taxi_crm_policy):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1',
            'idempotency_token': 'token_one',
        },
    )
    return response


@pytest.mark.pgsql(
    'crm_policy', files=['create_1_channel_1_communication.sql'],
)
async def test_pass_with_token(taxi_crm_policy, pgsql):
    response = await send_with_token(taxi_crm_policy)
    assert response.json() == {'allowed': True}
    response = await send_with_token(taxi_crm_policy)
    assert response.json() == {'allowed': True}


async def send_message_for_rotate_test(taxi_crm_policy):
    await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '100500',
        },
    )


def get_entities_meta(pgsql, num):
    return select_columns_from_table(
        'crm_policy.runtime_entities_meta_round' + str(num),
        ['id', 'fullscreen_last_message_id'],
        pgsql['crm_policy'],
        1000,
    )


@pytest.mark.pgsql(
    'crm_policy',
    files=['create_channels_default.sql', 'create_communications_default.sql'],
)
async def test_rotate_entities(taxi_crm_policy, pgsql, mocked_time):
    await send_message_for_rotate_test(taxi_crm_policy)
    entity_ids = get_entities_meta(pgsql, 0)
    assert entity_ids == [{'id': 1, 'fullscreen_last_message_id': 1}]

    mocked_time.sleep(125)
    await taxi_crm_policy.post(
        'service/cron', json={'task_name': 'crm-policy-rotate-entities'},
    )

    await send_message_for_rotate_test(taxi_crm_policy)
    entity_ids = get_entities_meta(pgsql, 1)
    assert entity_ids == [{'id': 2, 'fullscreen_last_message_id': 2}]

    mocked_time.sleep(125)
    await taxi_crm_policy.post(
        'service/cron', json={'task_name': 'crm-policy-rotate-entities'},
    )

    await send_message_for_rotate_test(taxi_crm_policy)
    entity_ids = get_entities_meta(pgsql, 2)
    assert entity_ids == [{'id': 3, 'fullscreen_last_message_id': 3}]

    entity_ids = get_entities_meta(pgsql, 0)
    assert entity_ids == [{'id': 1, 'fullscreen_last_message_id': 1}]

    mocked_time.sleep(125)
    await taxi_crm_policy.post(
        'service/cron', json={'task_name': 'crm-policy-rotate-entities'},
    )

    entity_ids = get_entities_meta(pgsql, 0)
    assert entity_ids == []

    await send_message_for_rotate_test(taxi_crm_policy)
    entity_ids = get_entities_meta(pgsql, 0)
    assert entity_ids == [{'id': 4, 'fullscreen_last_message_id': 4}]


# ommiting string entity_type due to special case
@pytest.mark.parametrize(
    'entity_type',
    ['user_id', 'dbid_uuid', 'eda_user_id', 'lavka_user_id', 'geo_id'],
)
@pytest.mark.pgsql(
    'crm_policy',
    files=['create_channels_default.sql', 'fill_entity_types.sql'],
)
async def test_different_entity_types(
        taxi_crm_policy, mockserver, pgsql, mocked_time, entity_type,
):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        resp = [
            {
                'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
                'valid_until': '2020-12-31T23:59:59+00:00',
                'entity_type': entity_type,
                'experiment': {
                    'experiment_id': (
                        'crm:hub:push_transporting_seatbelts_poll'
                    ),
                    'groups': [
                        {
                            'group_id': '__default__',
                            'channel': 'push',
                            'cooldown': 1,
                        },
                    ],
                },
            },
        ]
        return resp

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': entity_type,
            'channel_type': 'push',
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
        },
    )

    assert response.json() == {'allowed': True}
