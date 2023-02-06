SHIFTS_V2 = [
    {
        'store_id': '12345567',
        'store_external_id': 'depot_id_2',
        'courier_id': 'courier_id_2',
        'shift_id': '54321',
        'status': 'closed',
        'started_at': '2021-01-24T17:19:00+00:00',
        'closes_at': '2021-01-24T18:19:00+00:00',
        'updated_ts': '2021-01-24T17:19:00+00:00',
    },
    {
        'store_id': '12345567',
        'store_external_id': 'depot_id_2',
        'courier_id': None,
        'shift_id': '54325',
        'status': 'request',
        'started_at': '2021-01-24T17:19:00+00:00',
        'closes_at': '2021-01-24T18:19:00+00:00',
        'updated_ts': '2021-01-24T17:19:00+00:00',
    },
]


async def test_import_broken_wms_shifts(
        taxi_grocery_checkins, grocery_wms, pgsql,
):
    grocery_wms.set_couriers_shifts(SHIFTS_V2)
    await taxi_grocery_checkins.run_task('distlock/wms-shifts-sync')
    await taxi_grocery_checkins.invalidate_caches()
    db = pgsql['grocery_checkins']
    cursor = db.cursor()
    cursor.execute(
        f'SELECT courier_id, shift_id, depot_id, status'
        f' FROM grocery_checkins.shifts',
    )

    assert cursor.fetchall() == [
        ('courier_id_2', '54321', 'depot_id_2', 'closed'),
    ]
