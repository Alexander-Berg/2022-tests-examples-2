async def test_host_announcer(taxi_persey_core, pgsql):
    cursor = pgsql['persey_payments'].cursor()

    def _db_size():
        cursor.execute('SELECT 1 FROM persey_payments.persey_core_hosts')
        return len(cursor.fetchall())

    assert _db_size() == 0
    await taxi_persey_core.run_periodic_task('host_announce')
    assert _db_size() == 1
