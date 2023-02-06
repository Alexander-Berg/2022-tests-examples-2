import pytest


async def test_grocery_shifts_depots_basic(taxi_grocery_checkins, pgsql):
    logistic_group = 'depot_id_1'

    db = pgsql['grocery_checkins']
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO grocery_checkins.shifts
        (
        courier_id,
        shift_id,
        depot_id,
        status,
        started_at,
        updated_ts
        )
        VALUES ('courier_id_1', 'shift_id', 'depot_id_1',
        'in_progress', '2021-01-24T17:19:00+00:00',
        '2021-01-24T17:19:00+00:00');
        """,
    )
    cursor.close()

    response = await taxi_grocery_checkins.get(
        '/internal/checkins/v1/grocery-shifts/depots', json={},
    )

    assert response.status_code == 200
    depots = response.json()

    assert depots['depot_ids'] == [logistic_group]


async def test_grocery_shifts_depots_no_logistic_group(taxi_grocery_checkins):
    response = await taxi_grocery_checkins.get(
        '/internal/checkins/v1/grocery-shifts/depots', json={},
    )

    assert response.status_code == 200
    depots = response.json()

    assert depots['depot_ids'] == []


def _set_wms_shifts(grocery_wms, shifts):
    grocery_wms.set_couriers_shifts(shifts)


@pytest.mark.config(
    GROCERY_CHECKINS_WMS_SHIFTS_SYNC_SETTINGS={
        'update_freq': 120,
        'stop_elements_quantity': 100,
        'stop_last_update': 1,
    },
)
async def test_grocery_shifts_depots_cache_new(
        taxi_grocery_checkins, grocery_wms, taxi_config, pgsql,
):
    db = pgsql['grocery_checkins']
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO grocery_checkins.shifts
        (
        courier_id,
        shift_id,
        depot_id,
        status,
        updated_ts
        )
        VALUES ('courier_id_1', '12345', 'depot_id_1',
        'in_progress', '2021-01-24T17:19:00+00:00'),
        ('courier_id_3', '23545', 'depot_id_3',
        'waiting', '2021-01-24T17:19:00+00:00'),
        ('courier_id_4', '25234', 'depot_id_4',
        'paused', '2021-01-24T17:19:00+00:00'),
         ('courier_id_2', '54321', 'depot_id_2',
        'closed', '2021-01-24T17:19:00+00:00'); -- closed not includes in cache
        """,
    )
    cursor.close()

    response = await taxi_grocery_checkins.get(
        '/internal/checkins/v1/grocery-shifts/depots', json={},
    )

    assert response.status_code == 200
    depots = response.json()

    assert set(depots['depot_ids']) == set(
        ['depot_id_1', 'depot_id_3', 'depot_id_4'],
    )


@pytest.mark.config(
    GROCERY_CHECKINS_WMS_SHIFTS_SYNC_SETTINGS={
        'update_freq': 120,
        'stop_elements_quantity': 100,
        'stop_last_update': 1,
    },
)
async def test_grocery_shifts_depots_cache_new_full(
        taxi_grocery_checkins, pgsql, grocery_wms_full,
):
    await taxi_grocery_checkins.run_task('distlock/wms-shifts-sync')
    await taxi_grocery_checkins.invalidate_caches()

    db = pgsql['grocery_checkins']
    cursor = db.cursor()

    cursor.execute("""SELECT shift_id FROM grocery_checkins.shifts""")

    shifts_ids = [row[0] for row in cursor]

    cursor.close()

    assert set(shifts_ids) == set(
        [
            '17584449e1d6419a8e94c6a503229b09000400020001',
            '0cb4040bc615417d81451798f0e33e54000400020001',
            '2079cb174b254061a4982a331839452f000300020001',
            'c3a6450564b74ee7ac9c7554553b1388000300020001',
            '3d06a488830d4d1697160a47ff052712000200020001',
            'a908e024958448dca8d0beff6702f4a1000400020002',
            '7ff7efe553c1460589c6f6fa2a073ecc000300020002',
            'bef7c6512f284141a8ecb73087942ed2000400020002',
            'd6b559d518194288a683c052d2d48a62000300020002',
            '74fc45654ee7466b992ce842a039a5be000500020002',
            'd12785b7680747fc9d4ec0034af9355b000300020002',
            '535f30657d0b459681b35b3e9a67a050000100020000',
            'e8265b8cb66c4200ad473457e1c436ae000100020000',
            '55420a4cf82d487a82606fd8f3536b39000300020000',
            '39bb365e59dd4d79b538b21853193548000300020000',
            'eec216ac38f1432ba214ac69af75570e000200020000',
        ],
    )


@pytest.mark.config(
    GROCERY_CHECKINS_WMS_SHIFTS_SYNC_SETTINGS={
        'update_freq': 120,
        'stop_elements_quantity': 100,
        'stop_last_update': 1,
    },
)
async def test_grocery_shifts_depots_cache_new_null(
        taxi_grocery_checkins, pgsql, grocery_wms_null,
):
    await taxi_grocery_checkins.run_task('distlock/wms-shifts-sync')
    await taxi_grocery_checkins.invalidate_caches()

    db = pgsql['grocery_checkins']
    cursor = db.cursor()

    cursor.execute("""SELECT shift_id FROM grocery_checkins.shifts""")

    shifts_ids = [row[0] for row in cursor]

    cursor.close()

    assert set(shifts_ids) == set(
        [
            '17584449e1d6419a8e94c6a503229b09000400020001',
            '0cb4040bc615417d81451798f0e33e54000400020001',
            '2079cb174b254061a4982a331839452f000300020001',
            'c3a6450564b74ee7ac9c7554553b1388000300020001',
            '3d06a488830d4d1697160a47ff052712000200020001',
            'a908e024958448dca8d0beff6702f4a1000400020002',
            '7ff7efe553c1460589c6f6fa2a073ecc000300020002',
            'bef7c6512f284141a8ecb73087942ed2000400020002',
            'd6b559d518194288a683c052d2d48a62000300020002',
            '74fc45654ee7466b992ce842a039a5be000500020002',
            'd12785b7680747fc9d4ec0034af9355b000300020002',
            '535f30657d0b459681b35b3e9a67a050000100020000',
            'e8265b8cb66c4200ad473457e1c436ae000100020000',
            '55420a4cf82d487a82606fd8f3536b39000300020000',
            '39bb365e59dd4d79b538b21853193548000300020000',
            'eec216ac38f1432ba214ac69af75570e000200020000',
        ],
    )
