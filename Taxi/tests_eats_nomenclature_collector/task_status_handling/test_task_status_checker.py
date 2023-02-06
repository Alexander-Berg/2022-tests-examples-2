import json

import pytest


CORE_INTEGRATIONS_HANDLER = (
    '/eats-core-integrations/integrations/nomenclature-collector/v1/tasks'
)
MOCK_OLD_DATETIME = '2021-01-15T00:00:00+00:00'
MOCK_NOW = '2021-04-01T00:00:00+00:00'


def get_tasks_not_to_update(i):
    return [
        f'task_id_failed{i}',
        f'task_id_cancelled{i}',
        f'task_id_creation_failed{i}',
        f'task_id_finished{i}',
    ]


@pytest.mark.now(MOCK_NOW)
async def test_task_status_checker(
        taxi_eats_nomenclature_collector,
        load_json,
        mock_eats_core_integrations,
        testpoint,
        pgsql,
        assert_tasks_synchronized,
):
    core_response = load_json('core_integrations_tasks.json')
    mock_eats_core_integrations(core_response)

    @testpoint('eats_nomenclature_collector::task-status-checker')
    def handle_finished(arg):
        pass

    assert_tasks_synchronized(
        'nomenclature_place_tasks',
        ['task_id1', 'task_id2'],
        MOCK_OLD_DATETIME,
    )
    assert_tasks_synchronized(
        'price_tasks', ['task_id3', 'task_id4'], MOCK_OLD_DATETIME,
    )
    assert_tasks_synchronized(
        'stock_tasks', ['task_id5', 'task_id6'], MOCK_OLD_DATETIME,
    )
    assert_tasks_synchronized(
        'availability_tasks', ['task_id7', 'task_id8'], MOCK_OLD_DATETIME,
    )
    assert_tasks_synchronized(
        'nomenclature_place_tasks',
        get_tasks_not_to_update(1),
        MOCK_OLD_DATETIME,
    )
    assert_tasks_synchronized(
        'price_tasks', get_tasks_not_to_update(2), MOCK_OLD_DATETIME,
    )
    assert_tasks_synchronized(
        'stock_tasks', get_tasks_not_to_update(3), MOCK_OLD_DATETIME,
    )
    assert_tasks_synchronized(
        'availability_tasks', get_tasks_not_to_update(4), MOCK_OLD_DATETIME,
    )

    await taxi_eats_nomenclature_collector.run_distlock_task(
        'task-status-checker',
    )
    handle_finished.next_call()

    # check final statuses are synchronized
    assert_tasks_synchronized(
        'nomenclature_place_tasks', ['task_id1', 'task_id2'], MOCK_NOW,
    )
    assert_tasks_synchronized(
        'price_tasks', ['task_id3', 'task_id4'], MOCK_NOW,
    )
    assert_tasks_synchronized(
        'stock_tasks', ['task_id5', 'task_id6'], MOCK_NOW,
    )
    assert_tasks_synchronized(
        'availability_tasks', ['task_id7', 'task_id8'], MOCK_NOW,
    )
    # check not final statuses are not synchronized
    assert_tasks_synchronized(
        'nomenclature_place_tasks',
        get_tasks_not_to_update(1),
        MOCK_OLD_DATETIME,
    )
    assert_tasks_synchronized(
        'price_tasks', get_tasks_not_to_update(2), MOCK_OLD_DATETIME,
    )
    assert_tasks_synchronized(
        'stock_tasks', get_tasks_not_to_update(3), MOCK_OLD_DATETIME,
    )
    assert_tasks_synchronized(
        'availability_tasks', get_tasks_not_to_update(4), MOCK_OLD_DATETIME,
    )

    assert sql_get_task_statuses(pgsql, 'nomenclature_place_tasks') == {
        'task_id1': (
            'finished',
            'https:\\/\\/eda-integration.s3.mdst.yandex.net\\/'
            'some_path\\/test1.json',
        ),
        'task_id2': ('created', None),
        'task_id_failed1': ('failed', None),
        'task_id_cancelled1': ('cancelled', None),
        'task_id_creation_failed1': ('creation_failed', None),
        'task_id_finished1': (
            'finished',
            'https:\\/\\/eda-integration.s3.mdst.yandex.net\\/'
            'some_path\\/task_id_finished1.json',
        ),
    }
    assert_price_tasks(pgsql)
    assert_stock_tasks(pgsql)
    assert_availability_tasks(pgsql)


async def test_task_not_found(
        taxi_eats_nomenclature_collector, mock_eats_core_integrations, pgsql,
):
    def sql_get_task_info(table_name, task_id):
        cursor = pgsql['eats_nomenclature_collector'].cursor()
        cursor.execute(
            f"""
            select id, status, file_path, reason
            from eats_nomenclature_collector.{table_name}
            where id = '{task_id}'
        """,
        )
        return {row[0]: (row[1], row[2], row[3]) for row in cursor}

    core_response = {
        'task_id1': {
            'id': 'task_id1',
            'place_id': '1',
            'status': 'finished',
            'type': 'nomenclature',
        },
    }
    mock_eats_core_integrations(core_response)

    await taxi_eats_nomenclature_collector.run_distlock_task(
        'task-status-checker',
    )
    expected_task_info = {'task_id2': ('failed', None, 'Task not found')}
    assert (
        sql_get_task_info('nomenclature_place_tasks', 'task_id2')
        == expected_task_info
    )


@pytest.mark.now(MOCK_NOW)
async def test_nomenclature_all_finished(
        taxi_eats_nomenclature_collector,
        load_json,
        mock_eats_core_integrations,
        testpoint,
        pgsql,
        assert_tasks_synchronized,
):
    core_response = load_json('core_integrations_tasks.json')
    mock_eats_core_integrations(core_response)

    @testpoint('eats_nomenclature_collector::task-status-checker')
    def handle_finished(arg):
        pass

    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
        update eats_nomenclature_collector.nomenclature_place_tasks
        set status = 'finished'
        where id in ('task_id1', 'task_id2')
        """,
    )

    await taxi_eats_nomenclature_collector.run_distlock_task(
        'task-status-checker',
    )
    handle_finished.next_call()

    # check final statuses are synchronized
    assert_tasks_synchronized(
        'price_tasks', ['task_id3', 'task_id4'], MOCK_NOW,
    )
    assert_tasks_synchronized(
        'stock_tasks', ['task_id5', 'task_id6'], MOCK_NOW,
    )
    assert_tasks_synchronized(
        'availability_tasks', ['task_id7', 'task_id8'], MOCK_NOW,
    )
    # check not final statuses are not synchronized
    assert_tasks_synchronized(
        'nomenclature_place_tasks',
        ['task_id1', 'task_id2'] + get_tasks_not_to_update(1),
        MOCK_OLD_DATETIME,
    )
    assert_tasks_synchronized(
        'price_tasks', get_tasks_not_to_update(2), MOCK_OLD_DATETIME,
    )
    assert_tasks_synchronized(
        'stock_tasks', get_tasks_not_to_update(3), MOCK_OLD_DATETIME,
    )
    assert_tasks_synchronized(
        'availability_tasks', get_tasks_not_to_update(4), MOCK_OLD_DATETIME,
    )

    # nomenclature tasks are not updated
    # because they are already finished
    assert_price_tasks(pgsql)
    assert_stock_tasks(pgsql)
    assert_availability_tasks(pgsql)


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql(
    'eats_nomenclature_collector',
    files=['pg_eats_nomenclature_collector_for_failed_tasks.sql'],
)
async def test_nomenclature_failed_tasks(
        taxi_eats_nomenclature_collector,
        load_json,
        mock_eats_core_integrations,
        testpoint,
        pgsql,
):
    core_response = load_json('core_integrations_failed_tasks.json')
    mock_eats_core_integrations(core_response)

    @testpoint('eats_nomenclature_collector::task-status-checker')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_distlock_task(
        'task-status-checker',
    )
    handle_finished.next_call()

    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
        select place_id, task_type, task_error, status
        from eats_nomenclature_collector.place_tasks_last_status
        """,
    )
    data_from_db = sorted(cursor.fetchall())
    expected_data_from_db = sorted(
        [
            ('1', 'nomenclature', 'Empty menu in place', 'failed'),
            ('1', 'price', 'Fetch menu fail', 'failed'),
            ('1', 'stock', '', 'failed'),
            ('2', 'stock', '', 'failed'),
            (
                '1',
                'availability',
                'Unsupported availability aggregator',
                'failed',
            ),
        ],
    )
    assert data_from_db == expected_data_from_db


@pytest.mark.pgsql('eats_nomenclature_collector', files=[])
async def test_periodic_metrics(
        load_json, verify_periodic_metrics, mock_eats_core_integrations,
):
    core_response = load_json('core_integrations_tasks.json')
    mock_eats_core_integrations(core_response)

    await verify_periodic_metrics('task-status-checker', is_distlock=True)


def sql_get_task_statuses(pgsql, table_name):
    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
        select id, status, file_path
        from eats_nomenclature_collector.{table_name}
    """,
    )
    return {row[0]: (row[1], row[2]) for row in cursor}


def assert_price_tasks(pgsql):
    assert sql_get_task_statuses(pgsql, 'price_tasks') == {
        'task_id3': (
            'finished',
            'https:\\/\\/eda-integration.s3.mdst.yandex.net\\/'
            'some_path\\/test2.json',
        ),
        'task_id4': ('started', None),
        'task_id_failed2': ('failed', None),
        'task_id_cancelled2': ('cancelled', None),
        'task_id_creation_failed2': ('creation_failed', None),
        'task_id_finished2': (
            'finished',
            'https:\\/\\/eda-integration.s3.mdst.yandex.net\\/'
            'some_path\\/task_id_finished2.json',
        ),
    }


def assert_stock_tasks(pgsql):
    assert sql_get_task_statuses(pgsql, 'stock_tasks') == {
        'task_id5': (
            'finished',
            'https:\\/\\/eda-integration.s3.mdst.yandex.net\\/'
            'some_path\\/test3.json',
        ),
        'task_id6': ('failed', None),
        'task_id_failed3': ('failed', None),
        'task_id_cancelled3': ('cancelled', None),
        'task_id_creation_failed3': ('creation_failed', None),
        'task_id_finished3': (
            'finished',
            'https:\\/\\/eda-integration.s3.mdst.yandex.net\\/'
            'some_path\\/task_id_finished3.json',
        ),
    }


def assert_availability_tasks(pgsql):
    assert sql_get_task_statuses(pgsql, 'availability_tasks') == {
        'task_id7': (
            'finished',
            'https:\\/\\/eda-integration.s3.mdst.yandex.net\\/'
            'some_path\\/test4.json',
        ),
        'task_id8': ('cancelled', None),
        'task_id_failed4': ('failed', None),
        'task_id_cancelled4': ('cancelled', None),
        'task_id_creation_failed4': ('creation_failed', None),
        'task_id_finished4': (
            'finished',
            'https:\\/\\/eda-integration.s3.mdst.yandex.net\\/'
            'some_path\\/task_id_finished4.json',
        ),
    }


@pytest.fixture(name='assert_tasks_synchronized')
def _assert_tasks_synchronized(pgsql, to_utc_datetime):
    def do_assert_tasks_synchronized(table_name, task_ids, timestamp):
        task_ids_str = ','.join(f'\'{task_id}\'' for task_id in task_ids)
        cursor = pgsql['eats_nomenclature_collector'].cursor()
        cursor.execute(
            f"""
            select distinct(status_synchronized_at)
            from eats_nomenclature_collector.{table_name}
            where id in ({task_ids_str})
            """,
        )
        result = list(cursor)
        assert len(result) == 1
        assert to_utc_datetime(result[0][0]).replace(
            microsecond=0,
        ) == to_utc_datetime(timestamp).replace(microsecond=0)

    return do_assert_tasks_synchronized


@pytest.fixture(name='mock_eats_core_integrations')
def _mock_eats_core_integrations(mockserver):
    def _inner(core_response):
        @mockserver.json_handler(CORE_INTEGRATIONS_HANDLER)
        def _handler(request):
            assert not request.query['task_id'].startswith('task_id_failed')
            assert not request.query['task_id'].startswith('task_id_cancelled')
            assert not request.query['task_id'].startswith(
                'task_id_creation_failed',
            )
            assert not request.query['task_id'].startswith('task_id_finished')
            if request.query['task_id'] not in core_response:
                return mockserver.make_response(
                    json.dumps(
                        {
                            'errors': [
                                {'code': '404', 'message': 'Task not found.'},
                            ],
                        },
                    ),
                    404,
                )
            return core_response[request.query['task_id']]

        return _handler

    return _inner
