import copy
import json


import pytest


NOMENCLATURE_VALIDATION_METRICS_NAME = 'nomenclature-validation'
MOCK_NOW = '2021-03-03T09:00:00+00:00'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql(
    'eats_nomenclature_collector',
    files=['fill_for_processed_and_failed_tasks.sql'],
)
@pytest.mark.parametrize(
    'parallel_json_parsing_limit',
    [
        pytest.param(1, id='only_one_parsing_at_a_time'),
        pytest.param(10, id='ten_parallel_parsing'),
        pytest.param(20, id='twenty_parallel_parsing'),
    ],
)
async def test_processed_and_failed_tasks(
        taxi_eats_nomenclature_collector,
        testpoint,
        pg_cursor,
        stq,
        mds_s3_storage,
        get_integrations_data,
        mockserver,
        sql_get_place_tasks_last_status,
        to_utc_datetime,
        update_taxi_config,
        parallel_json_parsing_limit,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_COLLECTOR_BRAND_TASK_RESULT_SENDER_SETTINGS',
        {'parallel_json_parsing_limit': parallel_json_parsing_limit},
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

    base_data = get_integrations_data(['integrations_data.json'])

    # data with incorrect value (integer instead of string)
    data_with_bad_price = copy.deepcopy(base_data)
    data_with_bad_price['menu_items'][0]['price'] = 121

    dumped_base_data = json.dumps(base_data).encode('utf-8')

    mds_s3_storage.put_object('some_path/test1.json', dumped_base_data)
    mds_s3_storage.put_object(
        'some_path/test2.json', dumped_base_data,
    )  # the same as first
    mds_s3_storage.put_object(
        'some_path/test3.json', dumped_base_data,
    )  # the same as first

    mds_s3_storage.put_object(
        'some_path/test5.json', dumped_base_data,
    )  # the same as first, but another brand

    mds_s3_storage.put_object(
        'some_path/test6.json',
        json.dumps(data_with_bad_price).encode('utf-8'),
    )  # the same as first by hash, but another brand
    mds_s3_storage.put_object(
        'some_path/test7.json', dumped_base_data,
    )  # the same as first, but another brand

    # pylint: disable=unused-variable
    @testpoint('eats_nomenclature_collector::brand-task-result-sender')
    def handle_finished(arg):
        pass

    # process all brand tasks
    for _ in range(4):
        await taxi_eats_nomenclature_collector.run_periodic_task(
            'eats-nomenclature-collector_brand-task-result-sender',
        )
        handle_finished.next_call()

    assert stq.eats_nomenclature_brand_processing.times_called == 3

    # brand tasks
    pg_cursor.execute(
        'select * from eats_nomenclature_collector.nomenclature_brand_tasks;',
    )
    rows = pg_cursor.fetchall()
    assert {row['id'] for row in rows if row['status'] == 'processed'} == {
        'brand_task_1_finished',
        'brand_task_2_finished',
        'brand_task_4_finished',
    }
    assert {row['id'] for row in rows if row['status'] == 'failed'} == {
        'brand_task_1_failed',
        'brand_task_3_will_fail_all_parsing',
    }
    rows_by_id = {row['id']: row for row in rows}
    assert (
        rows_by_id['brand_task_3_will_fail_all_parsing']['reason']
        == 'All nomenclature place tasks failed'
    )

    # place tasks
    pg_cursor.execute(
        'select * from eats_nomenclature_collector.nomenclature_place_tasks;',
    )
    rows = pg_cursor.fetchall()
    assert {row['id'] for row in rows if row['status'] == 'processed'} == {
        'place_task_1_finished',
        'place_task_2_finished',
        'place_task_3_finished',
        'place_task_5_finished',
        'place_task_8_finished',
    }
    assert {row['id'] for row in rows if row['status'] == 'failed'} == {
        'place_task_2_failed',
        'place_task_6_will_fail_unknown_path',
        'place_task_7_will_fail_parsing',
    }
    rows_by_id = {row['id']: row for row in rows}
    place_to_errors_messages = {
        6: (
            'Data file of nomenclature place task '
            'place_task_6_will_fail_unknown_path is not found at path '
            'path_unknown/test.json'
        ),
        7: (
            'Error occurred during parsing file some_path/test6.json '
            'of nomenclature place task place_task_7_will_fail_parsing: '
        ),
    }

    assert rows_by_id['place_task_6_will_fail_unknown_path']['reason'] == (
        place_to_errors_messages[6]
    )
    assert (
        place_to_errors_messages[7]
        in rows_by_id['place_task_7_will_fail_parsing']['reason']
    )

    places_without_fails = [1, 2, 3, 5, 8]
    for place_id in places_without_fails:
        current_place_tasks_last_status = sql_get_place_tasks_last_status(
            pg_cursor, place_id, 'nomenclature',
        )
        expected_last_status = {
            'status': 'processed',
            'task_error': None,
            'task_warnings': None,
            'status_or_text_changed_at': to_utc_datetime(MOCK_NOW),
        }
        assert current_place_tasks_last_status == expected_last_status

    place_id = 6
    current_place_tasks_last_status = sql_get_place_tasks_last_status(
        pg_cursor, place_id, 'nomenclature',
    )
    expected_last_status = {
        'status': 'failed',
        'task_error': place_to_errors_messages[place_id],
        'task_warnings': None,
        'status_or_text_changed_at': to_utc_datetime(MOCK_NOW),
    }
    assert current_place_tasks_last_status == expected_last_status


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(
        'eats-nomenclature-collector_brand-task-result-sender',
        is_distlock=False,
    )


def sql_add_place_task(
        pg_cursor,
        task_id,
        place_id,
        nomenclature_brand_task_id,
        status,
        file_path,
):
    pg_cursor.execute(
        """
        insert into eats_nomenclature_collector.nomenclature_place_tasks(
            id,
            place_id,
            nomenclature_brand_task_id,
            status,
            file_path
        )
        values (
            %s,
            %s,
            %s,
            %s,
            %s
        );
        """,
        (task_id, place_id, nomenclature_brand_task_id, status, file_path),
    )
