import datetime

import pytest

from corp_users.generated.cron import run_cron

NOW = datetime.datetime(2020, 6, 11, 11, 00, 00)
EXPECTED_PROMOCODES = [
    {'user_id': 'user_add', 'status': 'add'},
    {'user_id': 'user_update_data', 'status': 'update_data'},
    {'user_id': 'user_update_data_upsert', 'status': 'update_data'},
    {'user_id': 'user_remove', 'status': 'remove'},
    {'user_id': 'user_expired', 'status': 'add'},
]
EXPECTED_USERS = [
    {'_id': 'user_add', 'services': {'drive': {}}},
    {
        '_id': 'user_update_data',
        'services': {'drive': {'drive_user_id': 'user_id_update_data'}},
    },
    {
        '_id': 'user_update_data_upsert',
        'services': {'drive': {'drive_user_id': 'user_id_update_data_upsert'}},
    },
    {'_id': 'user_remove', 'services': {'drive': {}}},
    {'_id': 'user_expired', 'services': {'drive': {}}},
]

EXPECTED_DRIVE_ACCOUNTS = [
    {
        '_id': 234,
        'user_id': 'user_update_data',
        'client_id': 'client1',
        'drive_user_id': 'user_id_update_data',
        'created': NOW,
    },
    {
        '_id': 235,
        'user_id': 'user_update_data_upsert',
        'client_id': 'client1',
        'drive_user_id': 'user_id_update_data_upsert',
        'created': NOW,
    },
]


@pytest.mark.now(NOW.isoformat())
async def test_sync_drive_groups(db, patch):
    @patch('taxi.clients.drive.DriveClient.promocode_links')
    async def _promocode_links(*args, **kwargs):
        return [
            {
                'promocode': 'promocode_add',
                'action': 'add',
                'event_id': 1,
                'user_id': 'user_id_add',
                'account_id': 123,
            },
            {
                'promocode': 'promocode_update_data',
                'action': 'update_data',
                'event_id': 22,
                'user_id': 'user_id_update_data',
                'account_id': 234,
            },
            {
                'promocode': 'promocode_update_data_upsert',
                'action': 'update_data',
                'event_id': 44,
                'user_id': 'user_id_update_data_upsert',
                'account_id': 235,
            },
            {
                'promocode': 'promocode_remove',
                'action': 'remove',
                'event_id': 33,
                'user_id': 'user_id_remove',
                'account_id': 345,
            },
            {
                'promocode': 'promocode_expired',
                'action': 'add',
                'event_id': 55,
                'user_id': 'user_id_expired',
                'account_id': 456,
            },
        ]

    module = 'corp_users.crontasks.sync_drive_promocodes'
    await run_cron.main([module, '-t', '0'])

    for promocode in EXPECTED_PROMOCODES:
        db_item = await db.corp_drive_promocodes.find_one(
            {'user_id': promocode['user_id']},
        )
        assert db_item['status'] == promocode['status']

    for user in EXPECTED_USERS:
        db_item = await db.corp_users.find_one({'_id': user['_id']})
        assert db_item['services'] == user['services']

    for drive_account in EXPECTED_DRIVE_ACCOUNTS:
        db_item = await db.corp_drive_accounts.find_one(
            {'_id': drive_account['_id']},
        )
        assert db_item == drive_account

    cursor = await db.corp_drive_promocode_cursor.find_one(
        {'_id': 'drive_promocode_cursor'},
    )
    assert cursor['last_id'] == 55
