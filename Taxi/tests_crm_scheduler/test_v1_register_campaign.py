# pylint: disable=import-only-modules
import datetime

import pytest

from tests_crm_scheduler.utils import select_columns_from_table


@pytest.mark.parametrize('channel', ['z_user_push', 'user_push'])
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
)
async def test_can_register_campaign_with_appropriate_time(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
        channel,
):
    now = datetime.datetime(2021, 12, 15, 11, 0)
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    response = await taxi_crm_scheduler.put(
        '/v1/register_communiction_to_send',
        params={
            'size': 12300,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            'channel_type': channel,
            'policy_enabled': True,
            'send_enabled': True,
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
        },
    )

    assert response.status == 200
    assert response.json() == {}

    sendings = select_columns_from_table(
        'crm_scheduler.sendings',
        [
            'campaign_id',
            'sending_id',
            'policy_enabled',
            'send_enabled',
            'size',
        ],
        pgsql['crm_scheduler'],
        1000,
    )

    assert sendings == [
        {
            'campaign_id': '123',
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'policy_enabled': True,
            'send_enabled': True,
            'size': 12300,
        },
    ]

    # Verify that channel is correct
    channel_id = select_columns_from_table(
        'crm_scheduler.sendings', ['channel_id'], pgsql['crm_scheduler'], 1000,
    )[0]['channel_id']

    channel_name = select_columns_from_table(
        'crm_scheduler.channels WHERE id = ' + str(channel_id),
        ['name'],
        pgsql['crm_scheduler'],
        1000,
    )[0]['name']

    assert channel_name == channel


@pytest.mark.parametrize('channel', ['z_user_push', 'user_push'])
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': False,
        'check_work_time_on_generation': True,
    },
)
async def test_can_register_campaign_with_expired_time_if_checking_disabled(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
        channel,
):
    now = datetime.datetime(2022, 12, 15, 11, 0)
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    response = await taxi_crm_scheduler.put(
        '/v1/register_communiction_to_send',
        params={
            'size': 12300,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            'channel_type': channel,
            'policy_enabled': True,
            'send_enabled': True,
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
        },
    )

    assert response.status == 200
    assert response.json() == {}

    sendings = select_columns_from_table(
        'crm_scheduler.sendings',
        [
            'campaign_id',
            'sending_id',
            'policy_enabled',
            'send_enabled',
            'size',
        ],
        pgsql['crm_scheduler'],
        1000,
    )

    assert sendings == [
        {
            'campaign_id': '123',
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'policy_enabled': True,
            'send_enabled': True,
            'size': 12300,
        },
    ]

    # Verify that channel is correct
    channel_id = select_columns_from_table(
        'crm_scheduler.sendings', ['channel_id'], pgsql['crm_scheduler'], 1000,
    )[0]['channel_id']

    channel_name = select_columns_from_table(
        'crm_scheduler.channels WHERE id = ' + str(channel_id),
        ['name'],
        pgsql['crm_scheduler'],
        1000,
    )[0]['name']

    assert channel_name == channel


@pytest.mark.parametrize('channel', ['z_user_push', 'user_push'])
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
)
async def test_cant_register_campaign_with_expired_time_if_checking_enabled(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
        channel,
):
    now = datetime.datetime(2022, 12, 15, 11, 0)
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    response = await taxi_crm_scheduler.put(
        '/v1/register_communiction_to_send',
        params={
            'size': 12300,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            'channel_type': channel,
            'policy_enabled': True,
            'send_enabled': True,
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
        },
    )
    assert response.status == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'Working time for communication with campaign=123 and group=456'
            ' has expired'
        ),
    }

    sendings = select_columns_from_table(
        'crm_scheduler.sendings',
        [
            'campaign_id',
            'sending_id',
            'policy_enabled',
            'send_enabled',
            'size',
        ],
        pgsql['crm_scheduler'],
        1000,
    )
    assert sendings == []
