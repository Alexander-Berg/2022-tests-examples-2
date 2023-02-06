async def test_stq(pgsql, stq_runner):
    cursor = pgsql['eats_retail_market_integration'].cursor()
    data_for_stq_without_conflicts = [('1', '1'), ('2', '1')]

    for data_piece in data_for_stq_without_conflicts:
        task_playload = {'order_nr': data_piece[0], 'eater_id': data_piece[1]}
        await call_stq_runner(stq_runner, [], task_playload)

    data_from_db = get_data_from_orders_table(cursor)
    assert sorted(data_from_db) == sorted(data_for_stq_without_conflicts)

    conflict_data_for_stq = [('1', '2')]

    for data_piece in conflict_data_for_stq:
        task_playload = {'order_nr': data_piece[0], 'eater_id': data_piece[1]}
        await call_stq_runner(stq_runner, [], task_playload)

    updated_data_from_db = get_data_from_orders_table(cursor)
    assert sorted(data_from_db) == sorted(updated_data_from_db)


def get_data_from_orders_table(cursor):
    cursor.execute(
        """
        select order_nr, eater_id
        from eats_retail_market_integration.orders
        """,
    )
    return list(cursor.fetchall()) if cursor else None


async def call_stq_runner(stq_runner, args, kwargs, expect_fail=False):
    await stq_runner.eats_retail_market_integration_core_orders.call(
        task_id=kwargs['order_nr'] + '|' + kwargs['eater_id'],
        args=args,
        kwargs=kwargs,
        expect_fail=expect_fail,
    )
