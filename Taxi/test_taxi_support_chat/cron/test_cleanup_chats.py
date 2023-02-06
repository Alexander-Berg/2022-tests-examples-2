import datetime

import pytest

from taxi_support_chat.generated.cron import run_cron


@pytest.mark.config(
    CLOSE_VISIBLE_CHATS_IN_PY2=False,
    CHAT_CLOSING_SETTINGS={
        'client_support': {
            'close': {
                'stats': 'close_visible_chats',
                'solved_delay': 240,
                'pending_delay': 10080,
            },
            'hide': {'stats': 'hide_closed_chats', 'delay': 1440},
        },
        'driver_support': {
            'close': {
                'stats': 'close_driver_chats',
                'solved_delay': 1440,
                'pending_delay': 1440,
                'hide': True,
            },
        },
        'eats_support': {
            'close': {
                'stats': 'close_eats_chats',
                'solved_delay': 240,
                'pending_delay': 240,
                'order_finished_delay': 240,
                'hide': True,
            },
        },
    },
)
@pytest.mark.now('2018-01-01T00:00:00')
async def test_cleanup_chats(cron_context, loop):
    await run_cron.main(
        ['taxi_support_chat.crontasks.cleanup_chats', '-t', '0'],
    )

    db = cron_context.mongo
    expected_chats = [
        {
            '_id': 'solved_recently_client_chat_id',
            'open': True,
            'visible': True,
        },
        {
            '_id': 'pending_recently_client_chat_id',
            'open': True,
            'visible': True,
        },
        {
            '_id': 'closed_recently_client_chat_id',
            'open': False,
            'visible': True,
        },
        {
            '_id': 'solved_long_ago_client_chat_id_with_unread',
            'open': False,
            'visible': True,
            'close_ticket': True,
        },
        {
            '_id': 'solved_long_long_ago_client_chat_id_with_unread',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'solved_long_ago_client_chat_id_nto',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'solved_long_ago_client_chat_id',
            'open': False,
            'visible': True,
            'close_ticket': True,
        },
        {
            '_id': 'pending_long_ago_client_chat_id_with_unread',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'pending_long_ago_client_chat_id',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'closed_long_ago_client_chat_id',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'solved_recently_driver_chat_id',
            'open': True,
            'visible': True,
        },
        {
            '_id': 'pending_recently_driver_chat_id',
            'open': True,
            'visible': True,
        },
        {
            '_id': 'solved_long_ago_driver_chat_id',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'pending_long_ago_driver_chat_id',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'solved_long_long_ago_eats_chat_id',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'solved_long_long_ago_eats_chat_id_with_pending_order',
            'open': True,
            'visible': True,
        },
        {
            '_id': 'solved_long_long_ago_eats_chat_id_with_missing_order',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'solved_long_ago_updated_now_client_chat_id',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'solved_long_ago_updated_ago_client_chat_id',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'solved_long_ago_updated_now_client_chat_id_unread',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
    ]
    chats = await db.user_chat_messages.find(
        {}, {'open': True, 'visible': True, 'close_ticket': True},
    ).to_list(None)

    def sort_by_id(chat):
        return chat['_id']

    assert sorted(expected_chats, key=sort_by_id) == sorted(
        chats, key=sort_by_id,
    )

    events = await db.event_stats.find({}, {'_id': False}).to_list(None)
    assert events == [
        {
            'name': 'user_support_chat_stats',
            'created': datetime.datetime(2018, 1, 1, 0, 0),
            'close_visible_chats': 9,
            'hide_closed_chats': 7,
            'close_driver_chats': 2,
            'close_eats_chats': 2,
        },
    ]


@pytest.mark.config(
    CLOSE_VISIBLE_CHATS_IN_PY2=False,
    CHAT_CLOSING_SETTINGS={
        'client_support': {
            'close': {
                'stats': 'close_visible_chats',
                'solved_delay': 240,
                'pending_delay': 10080,
                'unread_delay': 10080,
            },
            'hide': {'stats': 'hide_closed_chats', 'delay': 1440},
        },
        'driver_support': {
            'close': {
                'stats': 'close_driver_chats',
                'solved_delay': 1440,
                'pending_delay': 1440,
                'hide': True,
            },
        },
        'eats_support': {
            'close': {
                'stats': 'close_eats_chats',
                'solved_delay': 240,
                'pending_delay': 240,
                'order_finished_delay': 240,
                'hide': True,
            },
        },
    },
)
@pytest.mark.now('2018-01-01T00:00:00')
async def test_cleanup_chats_unread(cron_context, loop):
    await run_cron.main(
        ['taxi_support_chat.crontasks.cleanup_chats', '-t', '0'],
    )

    db = cron_context.mongo
    expected_chats = [
        {
            '_id': 'solved_recently_client_chat_id',
            'open': True,
            'visible': True,
        },
        {
            '_id': 'pending_recently_client_chat_id',
            'open': True,
            'visible': True,
        },
        {
            '_id': 'closed_recently_client_chat_id',
            'open': False,
            'visible': True,
        },
        {
            '_id': 'solved_long_ago_client_chat_id_with_unread',
            'open': True,
            'visible': True,
        },
        {
            '_id': 'solved_long_long_ago_client_chat_id_with_unread',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'solved_long_ago_client_chat_id',
            'open': False,
            'visible': True,
            'close_ticket': True,
        },
        {
            '_id': 'solved_long_ago_client_chat_id_nto',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'pending_long_ago_client_chat_id_with_unread',
            'open': True,
            'visible': True,
        },
        {
            '_id': 'pending_long_ago_client_chat_id',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'closed_long_ago_client_chat_id',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'solved_recently_driver_chat_id',
            'open': True,
            'visible': True,
        },
        {
            '_id': 'pending_recently_driver_chat_id',
            'open': True,
            'visible': True,
        },
        {
            '_id': 'solved_long_ago_driver_chat_id',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'pending_long_ago_driver_chat_id',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'solved_long_long_ago_eats_chat_id',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'solved_long_long_ago_eats_chat_id_with_pending_order',
            'open': True,
            'visible': True,
        },
        {
            '_id': 'solved_long_long_ago_eats_chat_id_with_missing_order',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'solved_long_ago_updated_now_client_chat_id',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'solved_long_ago_updated_ago_client_chat_id',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'solved_long_ago_updated_now_client_chat_id_unread',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
    ]
    chats = await db.user_chat_messages.find(
        {}, {'open': True, 'visible': True, 'close_ticket': True},
    ).to_list(None)

    def sort_by_id(chat):
        return chat['_id']

    assert sorted(expected_chats, key=sort_by_id) == sorted(
        chats, key=sort_by_id,
    )

    events = await db.event_stats.find({}, {'_id': False}).to_list(None)
    assert events == [
        {
            'name': 'user_support_chat_stats',
            'created': datetime.datetime(2018, 1, 1, 0, 0),
            'close_visible_chats': 7,
            'close_visible_chats_read': 5,
            'close_visible_chats_unread': 2,
            'hide_closed_chats': 6,
            'close_driver_chats': 2,
            'close_eats_chats': 2,
        },
    ]


@pytest.mark.config(
    CLOSE_VISIBLE_CHATS_IN_PY2=False,
    CHAT_CLOSING_SETTINGS={
        'client_support': {
            'close': {
                'stats': 'close_visible_chats',
                'solved_delay': 240,
                'pending_delay': 10080,
                'unread_delay': 10080,
                'time_to_read': 240,
            },
            'hide': {'stats': 'hide_closed_chats', 'delay': 1440},
        },
        'driver_support': {
            'close': {
                'stats': 'close_driver_chats',
                'solved_delay': 1440,
                'pending_delay': 1440,
                'hide': True,
            },
        },
        'eats_support': {
            'close': {
                'stats': 'close_eats_chats',
                'solved_delay': 240,
                'pending_delay': 240,
                'order_finished_delay': 240,
                'hide': True,
            },
        },
    },
)
@pytest.mark.now('2018-01-01T00:00:00')
async def test_cleanup_chats_time_to_read(cron_context, loop):
    await run_cron.main(
        ['taxi_support_chat.crontasks.cleanup_chats', '-t', '0'],
    )

    db = cron_context.mongo
    expected_chats = [
        {
            '_id': 'solved_recently_client_chat_id',
            'open': True,
            'visible': True,
        },
        {
            '_id': 'pending_recently_client_chat_id',
            'open': True,
            'visible': True,
        },
        {
            '_id': 'closed_recently_client_chat_id',
            'open': False,
            'visible': True,
        },
        {
            '_id': 'solved_long_ago_client_chat_id_with_unread',
            'open': True,
            'visible': True,
        },
        {
            '_id': 'solved_long_long_ago_client_chat_id_with_unread',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'solved_long_ago_client_chat_id',
            'open': False,
            'visible': True,
            'close_ticket': True,
        },
        {
            '_id': 'solved_long_ago_client_chat_id_nto',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'pending_long_ago_client_chat_id_with_unread',
            'open': True,
            'visible': True,
        },
        {
            '_id': 'pending_long_ago_client_chat_id',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'closed_long_ago_client_chat_id',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'solved_recently_driver_chat_id',
            'open': True,
            'visible': True,
        },
        {
            '_id': 'pending_recently_driver_chat_id',
            'open': True,
            'visible': True,
        },
        {
            '_id': 'solved_long_ago_driver_chat_id',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'pending_long_ago_driver_chat_id',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'solved_long_long_ago_eats_chat_id',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'solved_long_long_ago_eats_chat_id_with_pending_order',
            'open': True,
            'visible': True,
        },
        {
            '_id': 'solved_long_long_ago_eats_chat_id_with_missing_order',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'solved_long_ago_updated_now_client_chat_id',
            'open': True,
            'visible': True,
        },
        {
            '_id': 'solved_long_ago_updated_ago_client_chat_id',
            'open': False,
            'visible': False,
            'close_ticket': True,
        },
        {
            '_id': 'solved_long_ago_updated_now_client_chat_id_unread',
            'open': True,
            'visible': True,
        },
    ]
    chats = await db.user_chat_messages.find(
        {}, {'open': True, 'visible': True, 'close_ticket': True},
    ).to_list(None)

    def sort_by_id(chat):
        return chat['_id']

    assert sorted(expected_chats, key=sort_by_id) == sorted(
        chats, key=sort_by_id,
    )

    events = await db.event_stats.find({}, {'_id': False}).to_list(None)
    assert events == [
        {
            'name': 'user_support_chat_stats',
            'created': datetime.datetime(2018, 1, 1, 0, 0),
            'close_visible_chats': 5,
            'close_visible_chats_read': 4,
            'close_visible_chats_unread': 1,
            'hide_closed_chats': 4,
            'close_driver_chats': 2,
            'close_eats_chats': 2,
        },
    ]
