import pytest


def get_promo_ends(cursor, *promo_ids):
    cursor.execute(
        """
        SELECT ends
        FROM eats_restapp_promo.promos
        WHERE promo_id = ANY(%s)
        ORDER BY promo_id
        """,
        (list(promo_ids),),
    )
    return [r[0] for r in cursor.fetchall()]


@pytest.mark.suspend_periodic_tasks('periodic-promo-status-update')
@pytest.mark.config(
    EATS_RESTAPP_PROMO_PROMO_STATUS_UPDATE_PERIODIC_SETTINGS={
        'enabled': True,
        'update_period_sec': 10,
    },
)
async def test_update_promo_status_periodic_from_enabled_to_completed(
        taxi_eats_restapp_promo, pgsql,
):
    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        """INSERT INTO eats_restapp_promo.promos (
        promo_id,
        place_ids,
        promo_type,
        status,
        starts,
        ends,
        requirements,
        bonuses,
        schedule,
        set_at,
        discount_task_id
        ) VALUES
        (1, array['1', '2'],
        'plus_first_orders',
        'enabled',
        current_timestamp - interval '5 day',
        current_timestamp - interval '1 day',
        '{"requirements":[{"min_order_price":50.5}]}',
        '{"bonuses":[{"cashback":[20,10,5]}]}',
        NULL,
        current_timestamp,
        '1')""",
    )
    prev_ends = get_promo_ends(cursor, 1)

    await taxi_eats_restapp_promo.run_periodic_task(
        'periodic-promo-status-update',
    )

    cursor.execute(
        """SELECT status FROM eats_restapp_promo.promos WHERE promo_id = 1""",
    )

    assert cursor.fetchone()[0] == 'completed'
    assert get_promo_ends(cursor, 1) == prev_ends


@pytest.mark.suspend_periodic_tasks('periodic-promo-status-update')
@pytest.mark.config(
    EATS_RESTAPP_PROMO_PROMO_STATUS_UPDATE_PERIODIC_SETTINGS={
        'enabled': True,
        'update_period_sec': 10,
    },
)
async def test_update_promo_status_periodic_from_approved_to_enabled(
        taxi_eats_restapp_promo, pgsql,
):
    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        """INSERT INTO eats_restapp_promo.promos (
        promo_id,
        place_ids,
        promo_type,
        status,
        starts,
        ends,
        requirements,
        bonuses,
        schedule,
        set_at,
        discount_task_id
        ) VALUES
        (2, array['1', '2'],
        'plus_first_orders',
        'approved',
        current_timestamp - interval '1 day',
        current_timestamp + interval '5 day',
        '{"requirements":[{"min_order_price":50.5}]}',
        '{"bonuses":[{"cashback":[20,10,5]}]}',
        NULL,
        current_timestamp,
        '1')""",
    )
    prev_ends = get_promo_ends(cursor, 2)

    await taxi_eats_restapp_promo.run_periodic_task(
        'periodic-promo-status-update',
    )

    cursor.execute(
        """SELECT status FROM eats_restapp_promo.promos WHERE promo_id = 2""",
    )

    assert cursor.fetchone()[0] == 'enabled'
    assert get_promo_ends(cursor, 2) == prev_ends


@pytest.mark.suspend_periodic_tasks('periodic-promo-status-update')
@pytest.mark.config(
    EATS_RESTAPP_PROMO_PROMO_STATUS_UPDATE_PERIODIC_SETTINGS={
        'enabled': True,
        'update_period_sec': 10,
    },
)
async def test_update_promo_status_periodic_from_new_to_approved(
        taxi_eats_restapp_promo, pgsql,
):
    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        """INSERT INTO eats_restapp_promo.promos (
        promo_id,
        place_ids,
        promo_type,
        status,
        starts,
        ends,
        requirements,
        bonuses,
        schedule,
        set_at,
        discount_task_id
        ) VALUES
        (3, array['1', '2'],
        'plus_first_orders',
        'new',
        current_timestamp + interval '1 day',
        current_timestamp + interval '5 day',
        '{"requirements":[{"min_order_price":50.5}]}',
        '{"bonuses":[{"cashback":[20,10,5]}]}',
        NULL,
        current_timestamp,
        'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa01')""",
    )
    prev_ends = get_promo_ends(cursor, 3)

    await taxi_eats_restapp_promo.run_periodic_task(
        'periodic-promo-status-update',
    )

    cursor.execute(
        """SELECT status, discount_ids
        FROM eats_restapp_promo.promos
        WHERE promo_id = 3""",
    )

    data = cursor.fetchone()
    assert data[0] == 'approved'
    assert data[1] == ['3']
    assert get_promo_ends(cursor, 3) == prev_ends


@pytest.mark.suspend_periodic_tasks('periodic-promo-status-update')
@pytest.mark.config(
    EATS_RESTAPP_PROMO_PROMO_STATUS_UPDATE_PERIODIC_SETTINGS={
        'enabled': True,
        'update_period_sec': 10,
    },
)
async def test_update_promo_status_periodic_from_new_to_enabled(
        taxi_eats_restapp_promo, pgsql, mockserver,
):
    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        """INSERT INTO eats_restapp_promo.promos (
        promo_id,
        place_ids,
        promo_type,
        status,
        starts,
        ends,
        requirements,
        bonuses,
        schedule,
        set_at,
        discount_task_id
        ) VALUES
        (4, array['1', '2'],
        'plus_first_orders',
        'new',
        current_timestamp - interval '1 day',
        current_timestamp + interval '5 day',
        '{"requirements":[{"min_order_price":50.5}]}',
        '{"bonuses":[{"cashback":[20,10,5]}]}',
        NULL,
        current_timestamp,
        'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa01')""",
    )
    prev_ends = get_promo_ends(cursor, 4)

    await taxi_eats_restapp_promo.run_periodic_task(
        'periodic-promo-status-update',
    )

    cursor.execute(
        """SELECT status, discount_ids
        FROM eats_restapp_promo.promos
        WHERE promo_id = 4""",
    )

    data = cursor.fetchone()
    assert data[0] == 'enabled'
    assert data[1] == ['3']
    assert get_promo_ends(cursor, 4) == prev_ends


@pytest.mark.suspend_periodic_tasks('periodic-promo-status-update')
@pytest.mark.config(
    EATS_RESTAPP_PROMO_PROMO_STATUS_UPDATE_PERIODIC_SETTINGS={
        'enabled': True,
        'update_period_sec': 10,
    },
)
async def test_update_promo_status_periodic_from_new_to_completed(
        taxi_eats_restapp_promo, pgsql, mockserver,
):
    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        """INSERT INTO eats_restapp_promo.promos (
        promo_id,
        place_ids,
        promo_type,
        status,
        starts,
        ends,
        requirements,
        bonuses,
        schedule,
        set_at,
        discount_task_id
        ) VALUES
        (5, array['1', '2'],
        'plus_first_orders',
        'new',
        current_timestamp - interval '5 day',
        current_timestamp - interval '2 day',
        '{"requirements":[{"min_order_price":50.5}]}',
        '{"bonuses":[{"cashback":[20]}]}',
        NULL,
        current_timestamp,
        'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa01')""",
    )
    prev_ends = get_promo_ends(cursor, 5)

    await taxi_eats_restapp_promo.run_periodic_task(
        'periodic-promo-status-update',
    )

    cursor.execute(
        """SELECT status, discount_ids
        FROM eats_restapp_promo.promos
        WHERE promo_id = 5""",
    )

    data = cursor.fetchone()
    assert data[0] == 'completed'
    assert data[1] == ['3']
    assert get_promo_ends(cursor, 5) == prev_ends


@pytest.mark.suspend_periodic_tasks('periodic-promo-status-update')
@pytest.mark.config(
    EATS_RESTAPP_PROMO_PROMO_STATUS_UPDATE_PERIODIC_SETTINGS={
        'enabled': True,
        'update_period_sec': 10,
    },
)
async def test_update_promo_status_periodic_set_cashback_discount_id(
        taxi_eats_restapp_promo, pgsql, mockserver,
):
    @mockserver.json_handler(
        '/eats-discounts/v1/partners/discounts/get-tasks-status',
    )
    def _mock_eats_discounts_task_statuses(request):
        return mockserver.make_response(
            status=200,
            json={
                'tasks_status': [
                    {
                        'status': 'finished',
                        'task_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa01',
                        'task_result': {
                            'create_discounts': {
                                'affected_discount_ids': ['666666'],
                                'inserted_discount_ids': ['123345'],
                            },
                        },
                        'time': '2021-01-02T00:00:00+00:00',
                    },
                    {
                        'status': 'failed',
                        'task_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa02',
                        'time': '2021-01-02T00:00:00+00:00',
                    },
                    {
                        'status': 'planned',
                        'task_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa03',
                        'time': '2021-01-02T00:00:00+00:00',
                    },
                    {
                        'status': 'started',
                        'task_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa03',
                        'time': '2021-01-02T00:00:00+00:00',
                    },
                ],
            },
        )

    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        """INSERT INTO eats_restapp_promo.active_cashback_settings
        (
            id,
            place_id,
            cashback,
            starts,
            ends,
            type,
            discount_task_id
        )
        VALUES
        (1, '1', '5.0', '2020-11-25 18:43:00 +03:00',
        NULL, 'place', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa01'),
        (2, '1', '5.0', '2020-11-25 18:43:00 +03:00',
        NULL, 'yandex', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa02'),
        (3, '2', '5.0', '2020-11-25 18:43:00 +03:00',
        NULL, 'place', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa03'),
        (4, '2', '5.0', '2020-11-25 18:43:00 +03:00',
        NULL, 'yandex', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa04');""",
    )
    prev_ends = get_promo_ends(cursor, 1, 2, 3, 4)

    await taxi_eats_restapp_promo.run_periodic_task(
        'periodic-promo-status-update',
    )

    cursor.execute(
        """SELECT discount_task_id, discount_id
        FROM eats_restapp_promo.active_cashback_settings
        ORDER BY id""",
    )

    cashback_settings = cursor.fetchall()
    assert len(cashback_settings) == 3
    assert cashback_settings[0] == (
        'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa01',
        '123345',
    )
    assert cashback_settings[1] == (
        'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa03',
        None,
    )
    assert cashback_settings[2] == (
        'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa04',
        None,
    )
    assert get_promo_ends(cursor, 1, 2, 3, 4) == prev_ends
