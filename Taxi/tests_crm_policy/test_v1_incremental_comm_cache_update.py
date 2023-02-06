# pylint: disable=import-only-modules
import datetime

import pytest

from testsuite.utils import http

from tests_crm_policy.utils import select_columns_from_table


@pytest.mark.pgsql(
    'crm_policy', files=['create_1_channel_1_communication.sql'],
)
async def test_read_from_table(taxi_crm_policy, pgsql):
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


@pytest.mark.parametrize(
    'channel',
    [
        'sms',
        'push',
        'wall',
        'promo_fs',
        'promo_card',
        'promo_notification',
        'email',
    ],
)
@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_cache_update(
        taxi_crm_policy, pgsql, mocked_time, mockserver, channel,
):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin1(request):
        return []

    mocked_time.set(datetime.datetime(2019, 2, 1, 14, 0))

    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'user_id',
            'channel_type': channel,
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
            'experiment_id': 'crm:hub:push_transporting_seatbelts_poll',
            'experiment_group_id': '1_testing',
        },
    )

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
                            'group_id': '1_testing',
                            'channel': channel,
                            'cooldown': 100,
                        },
                    ],
                },
            },
        ]
        return resp

    updated_ts = select_columns_from_table(
        'crm_policy.external_communications_groups',
        ['external_communication_id', 'update_timestamp'],
        pgsql['crm_policy'],
    )
    assert updated_ts == []

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    updated_ts = select_columns_from_table(
        'crm_policy.external_communications_groups',
        ['external_communication_id', 'update_timestamp'],
        pgsql['crm_policy'],
    )

    assert updated_ts == [
        {
            'external_communication_id': 1,
            'update_timestamp': datetime.datetime(2019, 2, 1, 13, 57),
        },
    ]

    updated_ts = select_columns_from_table(
        'crm_policy.external_communications_groups',
        ['external_communication_id', 'update_timestamp'],
        pgsql['crm_policy'],
    )

    assert updated_ts == [
        {
            'external_communication_id': 1,
            'update_timestamp': datetime.datetime(2019, 2, 1, 13, 57),
        },
    ]

    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'user_id',
            'channel_type': channel,
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
            'experiment_id': 'crm:hub:push_transporting_seatbelts_poll',
            'experiment_group_id': '1_testing',
        },
    )

    assert response.json() == {'allowed': True}


async def send_one(taxi_crm_policy, channel):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': channel,
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
            'experiment_id': 'crm:hub:push_transporting_seatbelts_poll',
            'experiment_group_id': '1_testing',
        },
    )
    return response


@pytest.mark.parametrize(
    'channel',
    [
        {'type': 'sms', 'relax_time': 345600},
        {'type': 'wall', 'relax_time': 600},
        {'type': 'push', 'relax_time': 345600},
    ],
)
@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_new_communications_timings_applied_many(
        taxi_crm_policy, mockserver, pgsql, mocked_time, channel,
):
    first_time = True

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        resp = [{}]
        nonlocal first_time
        if first_time:
            first_time = False
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
                                'group_id': '2_testing',
                                'channel': 'sms',
                                'cooldown': 10000,
                            },
                            {
                                'group_id': '3_testing',
                                'channel': 'wall',
                                'cooldown': 10000,
                            },
                            {
                                'group_id': '0_testing',
                                'channel': channel['type'],
                                'cooldown': channel['relax_time'],
                            },
                        ],
                    },
                },
            ]
        else:
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
                                'group_id': '4_testing',
                                'channel': 'sms',
                                'cooldown': 10000,
                            },
                            {
                                'group_id': '5_testing',
                                'channel': 'sms',
                                'cooldown': 10000,
                            },
                            {
                                'group_id': '1_testing',
                                'channel': channel['type'],
                                'cooldown': channel['relax_time'],
                            },
                            {
                                'group_id': '0_testing',
                                'channel': channel['type'],
                                'cooldown': channel['relax_time'],
                            },
                        ],
                    },
                },
            ]
        return resp

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    response = await send_one(taxi_crm_policy, channel['type'])

    assert response.status_code == 400
    mocked_time.sleep(61)

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    response = await send_one(taxi_crm_policy, channel['type'])
    assert response.json() == {'allowed': True}
    assert response.status_code == 200

    mocked_time.sleep(channel['relax_time'] - 100)

    response = await send_one(taxi_crm_policy, channel['type'])
    assert response.status_code == 200
    assert response.json() == {'allowed': False}

    mocked_time.sleep(200)

    response = await send_one(taxi_crm_policy, channel['type'])
    assert response.status_code == 200
    assert response.json() == {'allowed': True}


@pytest.mark.parametrize(
    'channel',
    [
        {'type': 'sms', 'relax_time': 345600},
        {'type': 'wall', 'relax_time': 600},
        {'type': 'push', 'relax_time': 345600},
    ],
)
@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_new_communications_timings_applied2(
        taxi_crm_policy, mockserver, pgsql, mocked_time, channel,
):
    first_time = True

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        resp = [{}]
        nonlocal first_time
        if first_time:
            first_time = False
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
                                'group_id': '1_testing',
                                'channel': channel['type'],
                                'cooldown': channel['relax_time'] + 1000,
                            },
                        ],
                    },
                },
            ]
        else:
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
                                'group_id': '1_testing',
                                'channel': channel['type'],
                                'cooldown': channel['relax_time'] + 100,
                            },
                        ],
                    },
                },
            ]
        return resp

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    response = await send_one(taxi_crm_policy, channel['type'])
    assert response.json() == {'allowed': True}
    assert response.status_code == 200

    response = await send_one(taxi_crm_policy, channel['type'])
    assert response.json() == {'allowed': False}
    assert response.status_code == 200

    mocked_time.sleep(channel['relax_time'] + 500)

    response = await send_one(taxi_crm_policy, channel['type'])
    assert response.status_code == 200
    assert response.json() == {'allowed': False}

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    response = await send_one(taxi_crm_policy, channel['type'])
    assert response.status_code == 200
    assert response.json() == {'allowed': True}


@pytest.mark.parametrize('channel', ['push'])
@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_crm_admin_fallback(
        taxi_crm_policy, mockserver, pgsql, mocked_time, channel,
):
    mock_admin_count = 0

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        nonlocal mock_admin_count
        unset_timestamp = '1970-01-01T00:00:00+00:00'
        update_timestamp = request.args['update_timestamp']
        # update_timestamp shall be unset in first two runs
        if mock_admin_count < 2:
            assert update_timestamp == unset_timestamp

        # first response is not valid
        resp = [{}]
        if mock_admin_count > 0:
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
                                'group_id': '1_testing',
                                'channel': channel,
                                'cooldown': 100,
                            },
                        ],
                    },
                },
            ]
        mock_admin_count = mock_admin_count + 1
        return resp

    was_exception = False
    try:
        await taxi_crm_policy.invalidate_caches(clean_update=False)
    except http.HttpResponseError:
        was_exception = True
    assert was_exception

    response = await send_one(taxi_crm_policy, channel)
    assert response.status_code == 200
    assert response.json() == {'allowed': True}

    await taxi_crm_policy.invalidate_caches(clean_update=False)
    assert _mock_crm_admin.times_called == 3
