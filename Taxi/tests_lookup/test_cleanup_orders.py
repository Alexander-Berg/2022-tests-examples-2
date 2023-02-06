import datetime

import pytest


@pytest.mark.config(LOOKUP_PGAAS_CALLBACKS_ENABLE=True)
async def test_cleanup_periodic(taxi_lookup, testpoint, pgsql, mocked_time):
    @testpoint('testpoint-cleanup-orders')
    def _cleanup_orders(data):
        return

    def get_count():
        cursor = pgsql['lookup'].cursor()
        cursor.execute('SELECT COUNT(1) FROM lookup.order')
        result = []
        for row in cursor:
            result = row[0]
            break
        cursor.close()
        return result

    def insert_users():
        series_old = 'generate_series(1000001, 1000000+99)'
        series_new = 'generate_series(1000001, 1000000+101)'
        cursor = pgsql['lookup'].cursor()
        commands = [
            'BEGIN',
            'INSERT INTO lookup.order('
            'id, generation, version, wave, updated'
            ') SELECT \'old:\' || ' + series_old + ', 1,1,1,'
            ' \'2020-02-20T14:00:00Z\' ;',
            'INSERT INTO lookup.order('
            'id, generation, version, wave, updated'
            ') SELECT \'new:\' || ' + series_new + ', 1,1,1,'
            ' \'2020-02-20T14:15:00Z\' ;',
            'COMMIT',
        ]
        for sql in commands:
            cursor.execute(sql)

    mocked_time.set(datetime.datetime(2020, 2, 20, 14, 0, 0))
    await taxi_lookup.enable_testpoints()

    assert get_count() == 0
    insert_users()
    assert get_count() == 200

    # 1min from start, no deletions are expected yet
    mocked_time.sleep(60)
    await taxi_lookup.tests_control(invalidate_caches=False)
    _cleanup_orders.flush()
    call = await _cleanup_orders.wait_call(timeout=5)
    assert (call['data'], get_count()) == ({'count': 0}, 200)

    # 11min from start, 'old:XXX' should be deleted
    mocked_time.sleep(600)  # 10 mins
    await taxi_lookup.tests_control(invalidate_caches=False)
    _cleanup_orders.flush()
    call = await _cleanup_orders.wait_call(timeout=5)
    assert (call['data'], get_count()) == ({'count': 99}, 101)

    # 21min from start, 'new:XXX' should be deleted
    mocked_time.sleep(1200)  # 20 mins
    await taxi_lookup.tests_control(invalidate_caches=False)
    _cleanup_orders.flush()
    call = await _cleanup_orders.wait_call(timeout=5)
    assert (call['data'], get_count()) == ({'count': 101}, 0)

    _cleanup_orders.flush()
    mocked_time.sleep(1000)
    await taxi_lookup.tests_control(invalidate_caches=False)
    call = await _cleanup_orders.wait_call(timeout=5)
    assert (call['data'], get_count()) == ({'count': 0}, 0)
