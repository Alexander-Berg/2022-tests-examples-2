# pylint: disable=import-only-modules
import datetime
import socket

import pytest

from tests_crm_policy.utils import if_table_exists
from tests_crm_policy.utils import select_columns_from_table

HOST = socket.gethostname()
NUM_ROUND_TABLES = 10


async def send_bulk_n(taxi_crm_policy, middle_user, extra_users):
    count = extra_users
    tail = [{'experiment_group_id': '0_testing', 'entity_id': 'user1'}]
    tail.append({'experiment_group_id': '1_testing', 'entity_id': middle_user})
    for i in range(count):
        tail.append(
            {
                'experiment_group_id': '0_testing',
                'entity_id': 'user' + str(3 + i),
            },
        )

    response = await taxi_crm_policy.post(
        '/v1/check_update_send_message_bulk',
        json={
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
            'items': tail,
        },
    )
    return response


async def send_bulk(taxi_crm_policy, middle_user):
    result = await send_bulk_n(taxi_crm_policy, middle_user, 1)
    return result


def mock_crm_admin():
    return [
        {
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
            'valid_until': '2020-12-31T23:59:59+00:00',
            'experiment': {
                'experiment_id': 'crm:hub:push_transporting_seatbelts_poll',
                'groups': [
                    {
                        'group_id': '1_testing',
                        'channel': 'push',
                        'cooldown': 2 * 24 * 60 * 60,
                    },
                    {
                        'group_id': '0_testing',
                        'channel': 'push',
                        'cooldown': 1 * 24 * 60 * 60,
                    },
                ],
            },
        },
    ]


@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_partitioning(taxi_crm_policy, pgsql, mocked_time, mockserver):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        return mock_crm_admin()

    mocked_time.set(datetime.datetime(2019, 2, 1, 14, 0))

    await taxi_crm_policy.invalidate_caches(clean_update=False)
    assert _mock_crm_admin.times_called == 1

    response = await send_bulk(taxi_crm_policy, 'user2')
    assert response.json() == {'allowed': [True, True, True]}

    for _ in range(NUM_ROUND_TABLES):
        await taxi_crm_policy.post(
            'service/cron', json={'task_name': 'crm-policy-move-to-cold'},
        )
    # Check if history moved to messages_history_2_3 table
    result = select_columns_from_table(
        'crm_policy.messages_history_2_3',
        ['valid_till', 'send_at'],
        pgsql['crm_policy'],
    )
    valid_till = datetime.datetime(2019, 2, 3, 14, 0)

    assert result == [
        {
            'send_at': datetime.datetime(2019, 2, 1, 14, 0),
            'valid_till': valid_till,
        },
        {
            'send_at': datetime.datetime(2019, 2, 1, 14, 0),
            'valid_till': valid_till,
        },
        {
            'send_at': datetime.datetime(2019, 2, 1, 14, 0),
            'valid_till': valid_till,
        },
    ]

    # Check if messages_history_2_3 deleted after valid_till day passed
    mocked_time.set(datetime.datetime(2019, 2, 4, 14, 0))
    await taxi_crm_policy.post(
        'service/cron', json={'task_name': 'crm-policy-drop-tables'},
    )
    result = if_table_exists('messages_history_2_3', pgsql['crm_policy'])
    assert result == []

    # Check if old users and new one (in the middle of bulk) are allowed
    response = await send_bulk(taxi_crm_policy, 'user2')
    assert response.json() == {'allowed': [True, True, True]}


@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_get_new_entity_from_db(
        taxi_crm_policy, pgsql, mocked_time, mockserver,
):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        return mock_crm_admin()

    mocked_time.set(datetime.datetime(2019, 2, 1, 14, 0))

    await taxi_crm_policy.invalidate_caches(clean_update=False)
    assert _mock_crm_admin.times_called == 1

    response = await send_bulk(taxi_crm_policy, 'user2')
    mocked_time.set(datetime.datetime(2019, 2, 4, 14, 0))

    # Check if old users and new one (in the middle of bulk) are allowed
    response = await send_bulk(taxi_crm_policy, 'user4')
    assert response.json() == {'allowed': [True, True, True]}
    # Check entity_ids table
    result = select_columns_from_table(
        'crm_policy.entity_ids', ['id'], pgsql['crm_policy'],
    )
    assert sorted(result, key=lambda x: x['id']) == [
        {'id': 1},
        {'id': 2},
        {'id': 3},
        {'id': 4},
    ]


@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_round_table_increment(
        taxi_crm_policy, pgsql, mocked_time, mockserver,
):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        return mock_crm_admin()

    mocked_time.set(datetime.datetime(2019, 2, 1, 14, 0))

    await taxi_crm_policy.invalidate_caches(clean_update=False)
    assert _mock_crm_admin.times_called == 1

    response = await send_bulk(taxi_crm_policy, 'user2')
    assert response.status_code == 200

    result = select_columns_from_table(
        'crm_policy.messages_history_round0', ['id'], pgsql['crm_policy'],
    )
    assert result == [{'id': 1}, {'id': 2}, {'id': 3}]

    # After move-to-cold the next table should be used
    await taxi_crm_policy.post(
        'service/cron', json={'task_name': 'crm-policy-move-to-cold'},
    )
    response = await send_bulk(taxi_crm_policy, 'user10')
    assert response.status_code == 200
    result = select_columns_from_table(
        'crm_policy.messages_history_round1', ['id'], pgsql['crm_policy'],
    )
    assert result == [{'id': 4}]


@pytest.mark.parametrize(
    'initial_send_time',
    [
        datetime.datetime(2018, 1, 1, 0, 0),
        datetime.datetime(2018, 1, 5, 0, 0),
        datetime.datetime(2018, 1, 5, 23, 59),
        datetime.datetime(2018, 1, 6, 0, 0),
        datetime.datetime(2018, 1, 7, 12, 0),
        datetime.datetime(2018, 1, 8, 13, 59),
    ],
)
@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_weekly(
        taxi_crm_policy, pgsql, mocked_time, mockserver, initial_send_time,
):
    latest_cooldown_in_days = 107

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        return [
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
                            'channel': 'push',
                            'cooldown': (
                                (latest_cooldown_in_days - 7) * 24 * 60 * 60
                            ),
                        },
                        {
                            'group_id': '0_testing',
                            'channel': 'push',
                            'cooldown': latest_cooldown_in_days * 24 * 60 * 60,
                        },
                    ],
                },
            },
        ]

    mocked_time.set(initial_send_time)
    first_expired_time = initial_send_time + datetime.timedelta(
        days=latest_cooldown_in_days - 7,
    )
    valid_till = initial_send_time + datetime.timedelta(
        days=latest_cooldown_in_days,
    )
    week_table = 'messages_history_w2018_' + str(
        int(
            (
                (
                    (initial_send_time - datetime.datetime(2018, 1, 1)).days
                    + latest_cooldown_in_days
                )
                / 7
                + 1
            ),
        ),
    )

    await taxi_crm_policy.invalidate_caches(clean_update=False)
    assert _mock_crm_admin.times_called == 1

    response = await send_bulk(taxi_crm_policy, 'user2')
    assert response.json() == {'allowed': [True, True, True]}
    for _ in range(NUM_ROUND_TABLES):
        await taxi_crm_policy.post(
            'service/cron', json={'task_name': 'crm-policy-move-to-cold'},
        )
    # Check if history moved to messages_history_weekly table
    result = select_columns_from_table(
        'crm_policy.' + week_table, ['valid_till'], pgsql['crm_policy'],
    )

    assert result == [
        {'valid_till': valid_till},
        {'valid_till': valid_till},
        {'valid_till': valid_till},
    ]

    # Check if first user expired
    mocked_time.set(first_expired_time)
    response = await send_bulk(taxi_crm_policy, 'user2')
    assert response.json() == {'allowed': [False, True, False]}

    # Check if history not deleted from weekly at valid_till
    mocked_time.set(valid_till)
    await taxi_crm_policy.post(
        'service/cron', json={'task_name': 'crm-policy-drop-tables'},
    )
    result = if_table_exists(week_table, pgsql['crm_policy'])
    assert result == [{'bool': True}]

    # Check if history deleted from weekly at valid_till + 1 week
    mocked_time.set(valid_till + datetime.timedelta(weeks=1))
    await taxi_crm_policy.post(
        'service/cron', json={'task_name': 'crm-policy-drop-tables'},
    )
    result = if_table_exists(week_table, pgsql['crm_policy'])
    assert result == []
