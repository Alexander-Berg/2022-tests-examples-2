from . import utils


async def stq_run(stq_runner, load_json, yamaps, pgsql, kwargs):
    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))
    await stq_runner.routehistory_drive_add.call(
        task_id=kwargs['order']['order_id'], kwargs=kwargs, expect_fail=False,
    )
    cursor = pgsql['routehistory'].cursor()
    utils.register_user_types(cursor)
    cursor.execute(
        'SELECT c FROM routehistory.drive_history c ORDER BY '
        'yandex_uid, created',
    )
    result = utils.convert_pg_result(cursor.fetchall())
    utils.decode_drive_orders(result)
    return result


async def test_stq_drive_add(stq_runner, load_json, yamaps, pgsql):
    kwargs = load_json('kwargs.json')
    result = await stq_run(stq_runner, load_json, yamaps, pgsql, kwargs)
    assert result == load_json('expected_db.json')


async def test_stq_drive_add_go(stq_runner, load_json, yamaps, pgsql):
    origin = 'go'
    kwargs = load_json('kwargs.json')
    kwargs['order']['origin'] = origin
    result = await stq_run(stq_runner, load_json, yamaps, pgsql, kwargs)
    assert result[0]['origin'] == 1
    cursor = pgsql['routehistory'].cursor()
    cursor.execute('SELECT c FROM routehistory.common_strings c ORDER BY id')
    strings = utils.convert_pg_result(cursor.fetchall())
    assert strings == ['(1,go)']
