import pytest


async def test_applied_keys_cleaner_periodic_empty(
        testpoint, taxi_eats_restapp_support_chat,
):
    @testpoint('applied_keys_cleaner::locked-periodic-finished')
    def handle_finished(arg):
        pass

    await taxi_eats_restapp_support_chat.run_periodic_task(
        'eats-restapp-support-chat-'
        'applied-keys-cleaner-periodic-task-periodic',
    )

    result = handle_finished.next_call()
    assert result == {'arg': {'rows': 0}}


@pytest.mark.now('2020-01-10T00:00:00+0000')
@pytest.mark.pgsql(
    'eats_restapp_support_chat', files=['insert_applied_keys_one.sql'],
)
async def test_applied_keys_cleaner_periodic_one(
        testpoint, taxi_eats_restapp_support_chat, pgsql,
):
    @testpoint('applied_keys_cleaner::locked-periodic-finished')
    def handle_finished(arg):
        pass

    # удаляется 1
    await taxi_eats_restapp_support_chat.run_periodic_task(
        'eats-restapp-support-chat-'
        'applied-keys-cleaner-periodic-task-periodic',
    )
    result = handle_finished.next_call()
    assert result == {'arg': {'rows': 1}}


@pytest.mark.now('2020-01-10T00:00:00+0000')
@pytest.mark.pgsql(
    'eats_restapp_support_chat', files=['insert_applied_keys_multi.sql'],
)
async def test_applied_keys_cleaner_periodic_multi(
        testpoint, taxi_eats_restapp_support_chat, pgsql,
):
    @testpoint('applied_keys_cleaner::locked-periodic-finished')
    def handle_finished(arg):
        pass

    # удаляется 3
    await taxi_eats_restapp_support_chat.run_periodic_task(
        'eats-restapp-support-chat-'
        'applied-keys-cleaner-periodic-task-periodic',
    )
    result = handle_finished.next_call()
    assert result == {'arg': {'rows': 3}}
