import pytest


@pytest.mark.config(
    FEEDS_REMOVE_UNUSED_IDEMPOTENCY_TOKEN_WORKER={
        'enable': True,
        'work_interval_sec': 1,
        'expire_interval_sec': 3600,
        'max_deleted_tokens': 100,
    },
)
@pytest.mark.pgsql('feeds-pg', files=['unused_tokens.sql'])
@pytest.mark.now('2020-01-01T00:30:00Z')
async def test_remove_unused_token_worker(taxi_feeds, pgsql, testpoint):
    @testpoint('remove-unused-idempotency-token-worker-finished')
    def end_remove(data):
        pass

    async with taxi_feeds.spawn_task(
            'distlock/remove-unused-idempotency-token-worker',
    ):
        await end_remove.wait_call()

        cursor = pgsql['feeds-pg'].cursor()
        query = (
            'SELECT idempotency_token, service_id '
            'FROM idempotency_token ORDER BY service_id'
        )
        cursor.execute(query)

        assert list(cursor) == [('token1', 1), ('token2', 2)]
