import json

import pytest


MOCK_NOW = '2021-03-03T09:00:00+00:00'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql(
    'eats_nomenclature_collector', files=['fill_for_status_in_progress.sql'],
)
async def test_task_status_in_progress(
        taxi_eats_nomenclature_collector,
        testpoint,
        pgsql,
        mds_s3_storage,
        get_integrations_data,
        mockserver,
        update_taxi_config,
):
    brand_task_id_1 = 'brand_1_task_1'
    brand_task_id_2 = 'brand_1_task_2'
    brand_task_timeout_in_min = 10

    update_taxi_config(
        'EATS_NOMENCLATURE_COLLECTOR_BRAND_TASK_RESULT_SENDER_SETTINGS',
        {'brand_processing_timeout_in_min': brand_task_timeout_in_min},
    )

    @mockserver.json_handler(
        '/eats-core-retail/v1/place/client-categories/retrieve',
    )
    def _eats_core_retail(request):
        return {
            'has_client_categories': False,
            'has_client_categories_synchronization': False,
            'client_categories': [],
        }

    def _reset_tasks():
        sql_set_brand_task_status(pgsql, brand_task_id_1, 'finished')
        sql_set_brand_task_status(pgsql, brand_task_id_2, 'finished')
        sql_set_place_task_status(pgsql, brand_task_id_1, 'finished')
        sql_set_place_task_status(pgsql, brand_task_id_2, 'finished')

    base_data = get_integrations_data(['integrations_data.json'])
    dumped_base_data = json.dumps(base_data).encode('utf-8')

    mds_s3_storage.put_object('some_path/test1.json', dumped_base_data)
    mds_s3_storage.put_object('some_path/test2.json', dumped_base_data)

    # pylint: disable=unused-variable
    @testpoint('eats_nomenclature_collector::brand-task-result-sender')
    def handle_finished(arg):
        pass

    # don't set anything, only brand_task_id_1 should be processed

    await taxi_eats_nomenclature_collector.run_periodic_task(
        'eats-nomenclature-collector_brand-task-result-sender',
    )
    handle_finished.next_call()

    assert sql_get_brand_task_status(pgsql, brand_task_id_1) == 'processed'
    assert sql_get_brand_task_status(pgsql, brand_task_id_2) == 'finished'
    assert not sql_is_brand_task_in_progress(pgsql, brand_task_id_1)
    assert not sql_is_brand_task_in_progress(pgsql, brand_task_id_2)

    _reset_tasks()

    # set in progress and not timed-out, brand_task_id_1 should be ignored

    sql_set_brand_task_in_progress(
        pgsql,
        brand_task_id_1,
        time_difference_in_sec=brand_task_timeout_in_min * 60 / 2,
    )

    await taxi_eats_nomenclature_collector.run_periodic_task(
        'eats-nomenclature-collector_brand-task-result-sender',
    )
    handle_finished.next_call()

    assert sql_get_brand_task_status(pgsql, brand_task_id_1) == 'finished'
    assert sql_get_brand_task_status(pgsql, brand_task_id_2) == 'processed'
    assert sql_is_brand_task_in_progress(pgsql, brand_task_id_1)
    assert not sql_is_brand_task_in_progress(pgsql, brand_task_id_2)

    _reset_tasks()

    # set in progress and timed-out, should be processed

    sql_set_brand_task_in_progress(
        pgsql,
        brand_task_id_1,
        time_difference_in_sec=brand_task_timeout_in_min * 60 * 2,
    )

    await taxi_eats_nomenclature_collector.run_periodic_task(
        'eats-nomenclature-collector_brand-task-result-sender',
    )
    handle_finished.next_call()

    assert sql_get_brand_task_status(pgsql, brand_task_id_1) == 'processed'
    assert sql_get_brand_task_status(pgsql, brand_task_id_2) == 'finished'
    assert not sql_is_brand_task_in_progress(pgsql, brand_task_id_1)
    assert not sql_is_brand_task_in_progress(pgsql, brand_task_id_2)


def sql_set_brand_task_status(pgsql, brand_task_id, status):
    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
        update eats_nomenclature_collector.nomenclature_brand_tasks
        set
          status = '{status}'
        where id = '{brand_task_id}'
        """,
    )


def sql_set_place_task_status(pgsql, brand_task_id, status):
    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
        update eats_nomenclature_collector.nomenclature_place_tasks
        set
          status = '{status}'
        where nomenclature_brand_task_id = '{brand_task_id}'
        """,
    )


def sql_get_brand_task_status(pgsql, brand_task_id):
    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
        select status
        from eats_nomenclature_collector.nomenclature_brand_tasks
        where id = '{brand_task_id}'
        """,
    )
    return cursor.fetchone()[0]


def sql_set_brand_task_in_progress(
        pgsql, brand_task_id, time_difference_in_sec=0,
):
    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature_collector.nomenclature_brand_task_update_statuses (
            task_id,
            sender_processing_started_at,
            sender_processing_is_in_progress
        )
        values ('{brand_task_id}', now() - interval '{int(time_difference_in_sec)} seconds', true)
        on conflict (task_id) do update
        set
          sender_processing_is_in_progress = true,
          sender_processing_started_at = now() - interval '{int(time_difference_in_sec)} seconds'
        """,  # noqa: E501,
    )


def sql_is_brand_task_in_progress(pgsql, brand_task_id):
    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
        select sender_processing_is_in_progress
        from eats_nomenclature_collector.nomenclature_brand_task_update_statuses
        where task_id = '{brand_task_id}'
        """,  # noqa: E501,
    )

    result = cursor.fetchone()
    return result[0] if result is not None else False
