import datetime as dt

import pytest


TEST_CREATED_AT = '2021-01-15T00:00:00+00:00'


@pytest.mark.parametrize(
    'place_task_statuses,' 'expected_brand_task_status,',
    [
        pytest.param(
            ['finished', 'finished', 'finished'],
            'finished',
            id='all_finished',
        ),
        pytest.param(
            ['failed', 'finished', 'finished'], 'finished', id='some_failed',
        ),
        pytest.param(
            ['creation_failed', 'finished', 'finished'],
            'finished',
            id='some_creation_failed',
        ),
        pytest.param(
            ['failed', 'failed', 'failed'], 'failed', id='all_failed',
        ),
        pytest.param(
            ['failed', 'creation_failed', 'cancelled'],
            'failed',
            id='all_failed2',
        ),
        pytest.param(
            ['creation_failed', 'creation_failed', 'creation_failed'],
            'failed',
            id='all_creation_failed',
        ),
        pytest.param(
            ['cancelled', 'finished', 'finished'],
            'finished',
            id='some_cancelled',
        ),
        pytest.param(
            ['created', 'finished', 'finished'], 'created', id='some_created',
        ),
        pytest.param(
            ['started', 'finished', 'finished'], 'created', id='some_started',
        ),
        pytest.param([], 'failed', id='no_place_tasks'),
    ],
)
async def test_created_brand_tasks(
        taxi_eats_nomenclature_collector,
        testpoint,
        pgsql,
        place_task_statuses,
        expected_brand_task_status,
):
    now = dt.datetime.now()

    brand_task_id = 'brand_task_id'
    sql_insert_brand_task(pgsql, 'created', brand_task_id)
    place_id = 1
    for place_task_status in place_task_statuses:
        sql_insert_place(pgsql, str(place_id))
        sql_insert_place_task(
            pgsql,
            place_task_status,
            str(place_id),
            brand_task_id,
            str(place_id),
            now,
        )
        place_id += 1

    @testpoint('eats_nomenclature_collector::brand-task-status-checker')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_distlock_task(
        'brand-task-status-checker',
    )
    handle_finished.next_call()

    assert sql_get_brand_task_statuses(pgsql) == {
        (brand_task_id, expected_brand_task_status),
    }


@pytest.mark.parametrize('brand_task_creation_time_sec,', [10, 20])
async def test_outdated_creating_brand_tasks(
        taxi_eats_nomenclature_collector,
        taxi_config,
        testpoint,
        pgsql,
        brand_task_creation_time_sec,
):
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_COLLECTOR_TASK_STATUS_CHECKERS_SETTINGS': {
                'period_in_sec': 60,
                'limit': 100,
                'brand_period_in_sec': 60,
                'batch_size': 10000,
                'brand_task_creation_time_sec': brand_task_creation_time_sec,
            },
        },
    )
    now = dt.datetime.now()
    brand_task_creation_time = dt.timedelta(
        seconds=brand_task_creation_time_sec,
    )
    sql_insert_brand_task(pgsql, 'creating', 'brand_task_id1', now)
    sql_insert_brand_task(
        pgsql,
        'creating',
        'brand_task_id2',
        now - 2 * brand_task_creation_time,
    )
    sql_insert_brand_task(
        pgsql,
        'creating',
        'brand_task_id3',
        now - 3 * brand_task_creation_time,
    )

    @testpoint('eats_nomenclature_collector::brand-task-status-checker')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_distlock_task(
        'brand-task-status-checker',
    )
    handle_finished.next_call()

    assert sql_get_brand_task_statuses(pgsql) == {
        ('brand_task_id1', 'creating'),
        ('brand_task_id2', 'created'),
        ('brand_task_id3', 'created'),
    }


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(
        'brand-task-status-checker', is_distlock=True,
    )


@pytest.mark.parametrize('nomenclature_tasks_timeout', [3600, 14400])
async def test_outdated_nomenclature_tasks(
        taxi_eats_nomenclature_collector,
        taxi_config,
        testpoint,
        pgsql,
        nomenclature_tasks_timeout,
):
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_COLLECTOR_TASK_STATUS_CHECKERS_SETTINGS': {
                'period_in_sec': 60,
                'limit': 100,
                'brand_period_in_sec': 60,
                'batch_size': 10000,
                'nomenclature_tasks_not_finishing_timeout_in_sec': (
                    nomenclature_tasks_timeout
                ),
            },
        },
    )
    now = dt.datetime.now()
    nomenclature_tasks_timedelta = dt.timedelta(
        seconds=nomenclature_tasks_timeout,
    )

    # some tasks will be switched
    sql_insert_brand_task(pgsql, 'created', 'brand_task_id1')
    sql_insert_place(pgsql, '1')
    sql_insert_place(pgsql, '2')
    sql_insert_place(pgsql, '3')
    sql_insert_place_task(
        pgsql, 'created', 'place_task_id1', 'brand_task_id1', '1', now,
    )
    sql_insert_place_task(
        pgsql,
        'created',
        'place_task_id2',
        'brand_task_id1',
        '2',
        now - 2 * nomenclature_tasks_timedelta,
    )
    sql_insert_place_task(
        pgsql,
        'created',
        'place_task_id3',
        'brand_task_id1',
        '3',
        now - 3 * nomenclature_tasks_timedelta,
    )

    # one task will be switched
    sql_insert_brand_task(pgsql, 'created', 'brand_task_id2')
    sql_insert_place(pgsql, '4')
    sql_insert_place(pgsql, '5')
    sql_insert_place_task(
        pgsql, 'created', 'place_task_id4', 'brand_task_id2', '4', now,
    )
    sql_insert_place_task(
        pgsql,
        'created',
        'place_task_id5',
        'brand_task_id2',
        '5',
        now - 2 * nomenclature_tasks_timedelta,
    )

    # no tasks will be switched
    sql_insert_brand_task(pgsql, 'created', 'brand_task_id3')
    sql_insert_place(pgsql, '6')
    sql_insert_place_task(
        pgsql, 'created', 'place_task_id6', 'brand_task_id3', '6', now,
    )

    # don't switch because no tasks would be left
    sql_insert_brand_task(pgsql, 'created', 'brand_task_id4')
    sql_insert_place(pgsql, '7')
    sql_insert_place_task(
        pgsql,
        'created',
        'place_task_id7',
        'brand_task_id4',
        '7',
        now - 2 * nomenclature_tasks_timedelta,
    )

    # don't switch because brand task is just created
    sql_insert_brand_task(pgsql, 'created', 'brand_task_id5', created_at=now)
    sql_insert_place(pgsql, '8')
    sql_insert_place(pgsql, '9')
    sql_insert_place_task(
        pgsql, 'created', 'place_task_id8', 'brand_task_id5', '8', now,
    )
    sql_insert_place_task(
        pgsql,
        'created',
        'place_task_id9',
        'brand_task_id5',
        '9',
        now - 2 * nomenclature_tasks_timedelta,
    )

    # switch outdated place tasks even if one place task is finished
    sql_insert_brand_task(pgsql, 'created', 'brand_task_id6')
    sql_insert_place(pgsql, '10')
    sql_insert_place(pgsql, '11')
    sql_insert_place(pgsql, '12')
    sql_insert_place(pgsql, '13')
    sql_insert_place(pgsql, '14')
    sql_insert_place(pgsql, '15')
    sql_insert_place_task(
        pgsql,
        'creating',
        'place_task_id15',
        'brand_task_id6',
        '15',
        now - 2 * nomenclature_tasks_timedelta,
    )
    sql_insert_place_task(
        pgsql,
        'created',
        'place_task_id10',
        'brand_task_id6',
        '10',
        now - 2 * nomenclature_tasks_timedelta,
    )
    sql_insert_place_task(
        pgsql,
        'started',
        'place_task_id11',
        'brand_task_id6',
        '11',
        now - 3 * nomenclature_tasks_timedelta,
    )
    sql_insert_place_task(
        pgsql, 'finished', 'place_task_id12', 'brand_task_id6', '12', now,
    )
    sql_insert_place_task(
        pgsql,
        'failed',
        'place_task_id13',
        'brand_task_id6',
        '13',
        now - 2 * nomenclature_tasks_timedelta,
    )
    sql_insert_place_task(
        pgsql,
        'processed',
        'place_task_id14',
        'brand_task_id6',
        '14',
        now - 2 * nomenclature_tasks_timedelta,
    )

    @testpoint('eats_nomenclature_collector::brand-task-status-checker')
    def handle_finished(arg):
        pass

    old_brand_tasks = {f'brand_task_id{i}' for i in range(1, 7)}

    await taxi_eats_nomenclature_collector.run_distlock_task(
        'brand-task-status-checker',
    )
    handle_finished.next_call()

    assert len(sql_get_brand_task_statuses(pgsql)) == 9

    place_to_brand_tasks = {
        row[0]: row[1] for row in sql_get_place_tasks(pgsql)
    }
    new_brand_task1 = place_to_brand_tasks['place_task_id2']
    assert place_to_brand_tasks['place_task_id3'] == new_brand_task1
    assert new_brand_task1 not in old_brand_tasks
    new_brand_task2 = place_to_brand_tasks['place_task_id5']
    assert new_brand_task2 not in old_brand_tasks
    assert new_brand_task2 != new_brand_task1

    new_brand_task3 = place_to_brand_tasks['place_task_id10']
    assert new_brand_task3 != new_brand_task2
    assert new_brand_task3 not in old_brand_tasks
    assert new_brand_task3 == place_to_brand_tasks['place_task_id11']
    assert new_brand_task3 == place_to_brand_tasks['place_task_id15']
    assert new_brand_task3 != place_to_brand_tasks['place_task_id12']

    assert place_to_brand_tasks['place_task_id1'] == 'brand_task_id1'
    assert place_to_brand_tasks['place_task_id4'] == 'brand_task_id2'
    assert place_to_brand_tasks['place_task_id6'] == 'brand_task_id3'
    assert place_to_brand_tasks['place_task_id7'] == 'brand_task_id4'
    assert place_to_brand_tasks['place_task_id12'] == 'brand_task_id6'
    assert place_to_brand_tasks['place_task_id13'] == 'brand_task_id6'
    assert place_to_brand_tasks['place_task_id14'] == 'brand_task_id6'


def sql_get_brand_task_statuses(pgsql):
    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
        select id, status
        from eats_nomenclature_collector.nomenclature_brand_tasks
        """,
    )
    return set(cursor)


def sql_get_place_tasks(pgsql):
    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
        select id, nomenclature_brand_task_id
        from eats_nomenclature_collector.nomenclature_place_tasks
        """,
    )
    return set(cursor)


def sql_insert_place(pgsql, place_id='1'):
    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature_collector.places(
            id,
            slug,
            brand_id,
            place_group_id,
            is_enabled,
            is_parser_enabled
        )
        values (
            '{place_id}', '{place_id}', '1', '1',
            true, true
        )
        """,
    )


def sql_insert_place_task(
        pgsql,
        status,
        place_task_id='place_task_id',
        brand_task_id='brand_task_id',
        place_id='1',
        created_at=TEST_CREATED_AT,
):
    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature_collector.nomenclature_place_tasks(
            id, place_id, nomenclature_brand_task_id, status, created_at
        )
        values (
            '{place_task_id}', '{place_id}', '{brand_task_id}', '{status}',
            '{created_at}'
        );
        """,
    )


def sql_insert_brand_task(
        pgsql,
        status,
        brand_task_id='brand_task_id',
        updated_at=TEST_CREATED_AT,
        created_at=TEST_CREATED_AT,
        brand_id='1',
):
    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature_collector.nomenclature_brand_tasks(
            id, brand_id, status, updated_at, created_at
        )
        values (
            '{brand_task_id}',
            '{brand_id}',
            '{status}',
            '{updated_at}',
            '{created_at}'
        );
        """,
    )
