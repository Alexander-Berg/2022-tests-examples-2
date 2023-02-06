# pylint: disable=import-only-modules
import pytest

from tests_crm_scheduler.utils import select_columns_from_table

BASE_PARAMS_V1 = {
    'size': 12300,
    'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
    'campaign_id': '123',
    'channel_type': 'user_push',
    'group_id': '456',
    'policy_enabled': True,
    'send_enabled': True,
    'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
}


BASE_PARAMS_V2 = {
    'size': 123,
    'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
    'campaign_id': '123',
    'group_id': '456',
    'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
    'policy_step_channel': 'driver_wall',
    'steps': ['crm_policy', 'eda_push', 'driver_wall', 'logs'],
}


def map_channel_name_to_id(pgsql, channel_name):
    channel_id = select_columns_from_table(
        'crm_scheduler.channels WHERE name = \'' + channel_name + '\'',
        ['id'],
        pgsql['crm_scheduler'],
        1000,
    )[0]['id']
    return channel_id


@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_successful_register_two_campaigns_with_different_tokens(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
):
    channel = BASE_PARAMS_V1['channel_type']
    channel_id = map_channel_name_to_id(pgsql, channel)
    for token, sending_id in zip(
            ('A1B2C3D4', 'E5F6G7H8'),
            (
                '7d27b35a-0032-11ec-9a03-0242ac130003',
                '7d27b35a-0032-11ec-9a03-0242ac130004',
            ),
    ):
        headers = {'X-Idempotency-Token': token}
        params = dict(BASE_PARAMS_V1, sending_id=sending_id)
        response = await taxi_crm_scheduler.put(
            '/v1/register_communiction_to_send',
            params=params,
            headers=headers,
        )

    assert response.status == 200
    assert response.json() == {}

    sendings = select_columns_from_table(
        'crm_scheduler.sendings',
        [
            'campaign_id',
            'sending_id',
            'channel_id',
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
            'channel_id': channel_id,
            'policy_enabled': True,
            'send_enabled': True,
            'size': 12300,
        },
        {
            'campaign_id': '123',
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130004',
            'channel_id': channel_id,
            'policy_enabled': True,
            'send_enabled': True,
            'size': 12300,
        },
    ]


@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_successful_repeated_register_sending(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
):
    channel = BASE_PARAMS_V1['channel_type']
    channel_id = map_channel_name_to_id(pgsql, channel)
    headers = {'X-Idempotency-Token': 'Some-idempotency-token'}
    for _ in range(2):
        response = await taxi_crm_scheduler.put(
            '/v1/register_communiction_to_send',
            params=BASE_PARAMS_V1,
            headers=headers,
        )
    assert response.status == 200
    assert response.json() == {}

    sendings = select_columns_from_table(
        'crm_scheduler.sendings',
        [
            'campaign_id',
            'sending_id',
            'channel_id',
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
            'channel_id': channel_id,
            'policy_enabled': True,
            'send_enabled': True,
            'size': 12300,
        },
    ]


@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_unknown_issues_returns_500(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
        testpoint,
):
    @testpoint('register_communication_conditional_failure_point')
    async def _need_fail(data):
        return True

    headers = {'X-Idempotency-Token': 'Some-idempotency-token'}

    response = await taxi_crm_scheduler.put(
        '/v1/register_communiction_to_send',
        params=BASE_PARAMS_V1,
        headers=headers,
    )
    assert response.status == 500


@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_register_sendings_with_equal_ids_returns_400(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
):
    channel = BASE_PARAMS_V1['channel_type']
    channel_id = map_channel_name_to_id(pgsql, channel)
    for idempotency_token in ('First', 'Second'):
        headers = {'X-Idempotency-Token': idempotency_token}
        response = await taxi_crm_scheduler.put(
            '/v1/register_communiction_to_send',
            params=BASE_PARAMS_V1,
            headers=headers,
        )
    assert response.status == 400

    # First request had been accepted

    sendings = select_columns_from_table(
        'crm_scheduler.sendings',
        [
            'campaign_id',
            'sending_id',
            'channel_id',
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
            'channel_id': channel_id,
            'policy_enabled': True,
            'send_enabled': True,
            'size': 12300,
        },
    ]


@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 3,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_successful_register_two_campaigns_with_different_tokens_v2(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    json = dict(**BASE_PARAMS_V2)

    for idempotency_token, sending_id in zip(
            ('A1B2C3D4', 'E5F6G7H8'),
            (
                '7d27b35a-0032-11ec-9a03-0242ac130003',
                '7d27b35a-0032-11ec-9a03-0242ac130004',
            ),
    ):
        headers = {'X-Idempotency-Token': idempotency_token}
        json.update(sending_id=sending_id)
        response = await taxi_crm_scheduler.post(
            '/v2/register_communiction_to_send', json=json, headers=headers,
        )

    assert response.json() == {}
    sendings = select_columns_from_table(
        'crm_scheduler.sendings',
        [
            'campaign_id',
            'group_id',
            'channel_id',
            'sending_id',
            'dependency_uuid',
            'steps',
        ],
        pgsql['crm_scheduler'],
        1000,
    )

    assert sendings == [
        {
            'campaign_id': '123',
            'group_id': '456',
            'channel_id': -1,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'steps': ['crm_policy', 'eda_push', 'driver_wall', 'logs'],
        },
        {
            'campaign_id': '123',
            'group_id': '456',
            'channel_id': -1,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130004',
            'dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'steps': ['crm_policy', 'eda_push', 'driver_wall', 'logs'],
        },
    ]


@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 3,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_register_sendings_with_equal_ids_returns_400_v2(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    for token in ('A1B2C3D4', 'E5F6G7H8'):
        headers = {'X-Idempotency-Token': token}
        response = await taxi_crm_scheduler.post(
            '/v2/register_communiction_to_send',
            json=BASE_PARAMS_V2,
            headers=headers,
        )

    assert response.status == 400


@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 3,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_successful_repeated_register_sending_v2(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    for _ in range(2):
        headers = {'X-Idempotency-Token': 'Some-idempotency-token'}
        response = await taxi_crm_scheduler.post(
            '/v2/register_communiction_to_send',
            json=BASE_PARAMS_V2,
            headers=headers,
        )

    assert response.status == 200
    assert response.json() == {}
    sendings = select_columns_from_table(
        'crm_scheduler.sendings',
        [
            'campaign_id',
            'group_id',
            'channel_id',
            'sending_id',
            'dependency_uuid',
            'steps',
        ],
        pgsql['crm_scheduler'],
        1000,
    )

    assert sendings == [
        {
            'campaign_id': '123',
            'group_id': '456',
            'channel_id': -1,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'steps': ['crm_policy', 'eda_push', 'driver_wall', 'logs'],
        },
    ]


@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 3,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_unknown_issues_returns_500_v2(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
        testpoint,
):
    @testpoint('register_communication_conditional_failure_point')
    async def _need_fail(data):
        return True

    headers = {'X-Idempotency-Token': 'Some-idempotency-token'}
    response = await taxi_crm_scheduler.post(
        '/v2/register_communiction_to_send',
        json=BASE_PARAMS_V2,
        headers=headers,
    )
    assert response.status == 500
