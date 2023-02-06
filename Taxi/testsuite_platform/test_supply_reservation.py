async def test_supply_reservation(rt_robot_execute, execute_pg_query):
    await rt_robot_execute('supply_reservation')
    station_tags_rows = execute_pg_query('select class_name, tag_name from station_tags WHERE object_id=\'2c20f2d5-2d02-46a9-9ca5-f5fb0e3c0d4f\' order by class_name',)
    assert station_tags_rows == [
        ['supply_promise_tag', 'yd_new_supply_promise'],
        ['supply_reservation_tag', 'yd_new_supply_promise_reservation'],
        ['supply_reservation_tag', 'yd_new_supply_promise_reservation'],
        ['supply_reservation_tag', 'yd_new_supply_promise_reservation'],
        ['supply_reservation_tag', 'yd_new_supply_promise_reservation'],
        ['supply_reservation_tag', 'yd_new_supply_promise_reservation'],
    ]
