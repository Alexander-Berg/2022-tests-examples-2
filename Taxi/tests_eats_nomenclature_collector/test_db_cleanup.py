import json

import pytest


CORE_INTEGRATIONS_HANDLER = (
    '/eats-core-integrations/integrations/nomenclature-collector/v1/tasks'
)
MOCK_NOW = '2021-10-21T09:00:00+00:00'


async def test_place_tasks_cleanup(
        taxi_eats_nomenclature_collector,
        testpoint,
        pgsql,
        mock_eats_core_integrations,
):
    mock_eats_core_integrations()

    @testpoint('eats_nomenclature_collector::db-cleanup-finished')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_distlock_task('db-cleanup')
    handle_finished.next_call()

    assert sql_get_tasks(pgsql, 'price_tasks') == {
        'task_id_started2',
        'task_id_created2',
        'task_id_finished2',
        'task_id_failed_new',
    }

    assert sql_get_tasks(pgsql, 'stock_tasks') == {
        'task_id_started3',
        'task_id_created3',
        'task_id_finished3',
        'task_id_creation_failed_new',
    }

    assert sql_get_tasks(pgsql, 'availability_tasks') == {
        'task_id_started4',
        'task_id_created4',
        'task_id_finished4',
        'task_id_cancelled_new',
    }


async def test_brand_tasks_cleanup(
        taxi_eats_nomenclature_collector,
        testpoint,
        pgsql,
        mock_eats_core_integrations,
):
    mock_eats_core_integrations()

    sql_set_brand_task_processed(pgsql, 'brand_task_id')

    @testpoint('eats_nomenclature_collector::db-cleanup-finished')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_distlock_task('db-cleanup')
    handle_finished.next_call()

    assert sql_get_tasks(pgsql, 'nomenclature_place_tasks') == set()

    assert sql_get_tasks(pgsql, 'nomenclature_brand_tasks') == {
        'brand_task_id2',
        'brand_task_id3',
    }


@pytest.mark.config(
    EATS_NOMENCLATURE_COLLECTOR_DB_CLEANUP_SETTINGS={
        'enabled': True,
        'lifetime_hours': 24,
        'limit': 1000,
        'period_in_min': 2,
        'statuses': ['processed', 'failed', 'creation_failed', 'cancelled'],
        'place_tasks_last_status_history_lifetime_hours': 1,
    },
)
@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql(
    'eats_nomenclature_collector',
    files=[
        'pg_eats_nomenclature_collector.sql',
        'place_tasks_last_status_history.sql',
    ],
)
async def test_place_tasks_last_status_history_cleanup(
        taxi_eats_nomenclature_collector,
        testpoint,
        pgsql,
        mock_eats_core_integrations,
):
    mock_eats_core_integrations()

    @testpoint('eats_nomenclature_collector::db-cleanup-finished')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_distlock_task('db-cleanup')
    handle_finished.next_call()

    assert sql_get_place_tasks_last_status_history(pgsql) == {3, 4}


def sql_get_tasks(pgsql, table_name):
    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
        select id
        from eats_nomenclature_collector.{table_name}
    """,
    )
    return {row[0] for row in cursor}


def sql_set_brand_task_processed(pgsql, brand_task_id):
    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
        update eats_nomenclature_collector.nomenclature_brand_tasks
        set status = 'processed',
            updated_at = now() - interval '1 month'
        where id = '{brand_task_id}'
        """,
    )


# pylint: disable=invalid-name
def sql_get_place_tasks_last_status_history(pgsql):
    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
        select id from
        eats_nomenclature_collector.place_tasks_last_status_history
        order by id asc;
        """,
    )
    return {row[0] for row in cursor}


async def test_periodic_metrics(
        verify_periodic_metrics, mock_eats_core_integrations,
):
    mock_eats_core_integrations()

    await verify_periodic_metrics('db-cleanup', is_distlock=True)


@pytest.fixture(name='mock_eats_core_integrations')
def _mock_eats_core_integrations(mockserver, load_json):
    def _inner():
        @mockserver.json_handler(CORE_INTEGRATIONS_HANDLER)
        def _handler(request):
            assert request.query['task_id'] not in {
                'brand_task_id',
                'brand_task_id1',
                'brand_task_id2',
                'brand_task_id3',
            }
            core_response = load_json('core_integrations_tasks.json')
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
