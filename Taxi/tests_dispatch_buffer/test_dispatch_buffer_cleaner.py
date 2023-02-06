import datetime

import pytest

JOB_NAME = 'cleanup_buffer_dispatch_psql_orders'


def get_orders_count(psql):
    cursor = psql.cursor()
    cursor.execute('SELECT COUNT(*) FROM dispatch_buffer.dispatch_meta;')
    orders_count = list(r for r in cursor)[0][0]

    cursor = psql.cursor()
    cursor.execute('SELECT COUNT(*) FROM dispatch_buffer.order_meta;')
    order_meta_count = list(r for r in cursor)[0][0]

    cursor = psql.cursor()
    cursor.execute(
        'SELECT COUNT(*) FROM dispatch_buffer.dispatched_performer;',
    )
    dispatched_performer_count = list(r for r in cursor)[0][0]

    assert orders_count == order_meta_count == dispatched_performer_count
    return orders_count


async def wait_workers(taxi_dispatch_buffer, testpoint):
    @testpoint(JOB_NAME + '-started')
    def worker_start(data):
        return

    @testpoint(JOB_NAME + '-finished')
    def worker_finished(data):
        return data

    await taxi_dispatch_buffer.enable_testpoints()
    await worker_start.wait_call()
    await worker_finished.wait_call()


@pytest.mark.pgsql('driver_dispatcher', files=['dispatch_meta_insert.sql'])
@pytest.mark.config(
    DISPATCH_BUFFER_PSQL_CLEANUP_ENABLED=True,
    DISPATCH_BUFFER_PSQL_CLEANUP_TTLS_V2={
        'idle': 60,
        'on_draw': 60,
        'dispatched': 30,
        'removed': 60,
    },
)
async def test_dispatch_buffer_cleanup(
        taxi_dispatch_buffer, pgsql, mocked_time,
):
    db = pgsql['driver_dispatcher']
    timestamp = datetime.datetime.utcnow()
    mocked_time.set(timestamp)
    await taxi_dispatch_buffer.tests_control(invalidate_caches=False)
    await taxi_dispatch_buffer.run_task('distlock/psql-cleaner')
    assert get_orders_count(db) == 4

    timestamp += datetime.timedelta(minutes=31)
    mocked_time.set(timestamp)
    await taxi_dispatch_buffer.tests_control(invalidate_caches=False)
    await taxi_dispatch_buffer.run_task('distlock/psql-cleaner')
    assert get_orders_count(db) == 2

    timestamp += datetime.timedelta(minutes=30)
    mocked_time.set(timestamp)
    await taxi_dispatch_buffer.tests_control(invalidate_caches=False)
    await taxi_dispatch_buffer.run_task('distlock/psql-cleaner')
    assert get_orders_count(db) == 1

    timestamp += datetime.timedelta(minutes=30)
    mocked_time.set(timestamp)
    await taxi_dispatch_buffer.tests_control(invalidate_caches=False)
    await taxi_dispatch_buffer.run_task('distlock/psql-cleaner')
    assert get_orders_count(db) == 0
