import pytest


@pytest.mark.parametrize('exclude_by_shift_id', [True, False])
async def test_grocery_shifts_queue_info_basic(
        taxi_grocery_checkins, pgsql, taxi_config, exclude_by_shift_id,
):
    taxi_config.set(
        GROCERY_CHECKINS_QUEUE_EXCLUDE_BY_SHIFT_ID=exclude_by_shift_id,
    )

    courier_id = 'courier_id_1'
    logistic_group = 'depot_id_1'
    started_at = '2021-01-24T17:19:00+00:00'

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
    await taxi_grocery_checkins.invalidate_caches()

    response = await taxi_grocery_checkins.post(
        '/internal/checkins/v1/grocery-shifts/queue-info',
        json={'depot_id': logistic_group},
    )

    assert response.status_code == 200
    assert response.json() == {
        'couriers': [
            {'courier_id': courier_id, 'checkin_timestamp': started_at},
        ],
    }


@pytest.mark.parametrize('exclude_by_shift_id', [True, False])
@pytest.mark.parametrize('shift_status', ['closed', 'paused'])
async def test_grocery_shifts_queue_info_skips_not_in_progress(
        taxi_grocery_checkins,
        pgsql,
        shift_status,
        taxi_config,
        exclude_by_shift_id,
):
    taxi_config.set(
        GROCERY_CHECKINS_QUEUE_EXCLUDE_BY_SHIFT_ID=exclude_by_shift_id,
    )

    courier_id = 'courier_id_1'
    logistic_group = 'depot_id_1'
    started_at = '2021-01-24T17:19:00+00:00'

    db = pgsql['grocery_checkins']
    cursor = db.cursor()
    if shift_status == 'closed':
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
            '2021-01-24T17:19:00+00:00'),
            ('should_be_skipped', 'shift_id_2', 'depot_id_1',
            'closed', '2021-01-24T17:19:00+00:00',
            '2021-01-24T17:19:00+00:00');
            """,
        )
    else:
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
            '2021-01-24T17:19:00+00:00'),
            ('should_be_skipped', 'shift_id_2', 'depot_id_1',
            'paused', '2021-01-24T17:19:00+00:00',
            '2021-01-24T17:19:00+00:00');
            """,
        )

    cursor.close()
    await taxi_grocery_checkins.invalidate_caches()

    response = await taxi_grocery_checkins.post(
        '/internal/checkins/v1/grocery-shifts/queue-info',
        json={'depot_id': logistic_group},
    )

    assert response.status_code == 200
    assert response.json() == {
        'couriers': [
            {'courier_id': courier_id, 'checkin_timestamp': started_at},
        ],
    }


async def test_grocery_shifts_queue_info_no_logistic_group(
        taxi_grocery_checkins,
):
    response = await taxi_grocery_checkins.post(
        '/internal/checkins/v1/grocery-shifts/queue-info',
        json={'depot_id': 'depot_id_2'},
    )
    assert response.status_code == 200
    assert response.json() == {'couriers': []}


@pytest.mark.parametrize('exclude_by_shift_id', [True, False])
@pytest.mark.parametrize('same_shift_id_at_db', [True, False])
async def test_grocery_shifts_queue_info_excluded_from_queue(
        taxi_grocery_checkins,
        pgsql,
        couriers_db,
        taxi_config,
        exclude_by_shift_id,
        same_shift_id_at_db,
):
    taxi_config.set(
        GROCERY_CHECKINS_QUEUE_EXCLUDE_BY_SHIFT_ID=exclude_by_shift_id,
    )

    courier_id = 'courier_id_1'
    logistic_group = 'depot_id_1'
    started_at = '2021-01-24T17:19:00+00:00'
    shift_id = 'shift_id'
    legacy_depot_id = '345'

    couriers_db.add_entry(
        courier_id,
        logistic_group,
        started_at,
        True,
        legacy_depot_id,
        shift_id if same_shift_id_at_db else (shift_id + '123'),
    )

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
        VALUES ('courier_id_1', 'shift_id', '345',
        'in_progress', '2021-01-24T17:19:00+00:00',
        '2021-01-24T17:19:00+00:00');
        """,
    )
    cursor.close()
    await taxi_grocery_checkins.invalidate_caches()

    response = await taxi_grocery_checkins.post(
        '/internal/checkins/v1/grocery-shifts/queue-info',
        json={'depot_id': legacy_depot_id},
    )

    assert response.status_code == 200
    if exclude_by_shift_id and not same_shift_id_at_db:
        assert response.json() == {
            'couriers': [
                {'courier_id': courier_id, 'checkin_timestamp': started_at},
            ],
        }
    else:
        assert response.json() == {'couriers': []}
