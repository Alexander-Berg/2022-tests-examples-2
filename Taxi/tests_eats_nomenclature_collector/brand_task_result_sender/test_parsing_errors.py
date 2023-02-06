import copy
import json

import pytest

NOMENCLATURE_VALIDATION_METRICS_NAME = 'nomenclature-validation'
MOCK_NOW = '2021-03-03T09:00:00+00:00'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql(
    'eats_nomenclature_collector', files=['fill_for_parsing_errors.sql'],
)
async def test_parsing_errors(
        taxi_eats_nomenclature_collector,
        testpoint,
        pg_cursor,
        stq,
        mds_s3_storage,
        get_integrations_data,
        mockserver,
        sql_get_place_tasks_last_status,
        to_utc_datetime,
):
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

    data_with_no_categories = copy.deepcopy(base_data)
    data_with_no_categories['menu_categories'] = []

    data_with_no_products = copy.deepcopy(base_data)
    data_with_no_products['menu_items'] = []

    data_with_negative_weight = copy.deepcopy(base_data)
    data_with_negative_weight['menu_items'][0]['retail_info'][
        'measure_value'
    ] = -1

    mds_s3_storage.put_object(
        'some_path/test1.json',
        json.dumps(data_with_no_categories).encode('utf-8'),
    )
    mds_s3_storage.put_object(
        'some_path/test2.json',
        json.dumps(data_with_no_products).encode('utf-8'),
    )
    mds_s3_storage.put_object(
        'some_path/test3.json',
        json.dumps(data_with_negative_weight).encode('utf-8'),
    )

    # pylint: disable=unused-variable
    @testpoint('eats_nomenclature_collector::brand-task-result-sender')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_periodic_task(
        'eats-nomenclature-collector_brand-task-result-sender',
    )
    handle_finished.next_call()

    assert stq.eats_nomenclature_brand_processing.times_called == 0

    # brand tasks
    pg_cursor.execute(
        'select * from eats_nomenclature_collector.nomenclature_brand_tasks;',
    )
    rows = pg_cursor.fetchall()
    rows_by_id = {row['id']: row for row in rows}
    assert rows_by_id['brand1_task_id']['status'] == 'failed'
    assert (
        rows_by_id['brand1_task_id']['reason']
        == 'All nomenclature place tasks failed'
    )

    # place tasks
    pg_cursor.execute(
        'select * from eats_nomenclature_collector.nomenclature_place_tasks;',
    )
    rows = pg_cursor.fetchall()
    assert {row['id'] for row in rows if row['status'] == 'failed'} == {
        'nomenclature_task_id1',
        'nomenclature_task_id2',
        'nomenclature_task_id3',
    }
    rows_by_id = {row['id']: row for row in rows}
    assert (
        rows_by_id['nomenclature_task_id1']['reason']
        == 'No categories in nomenclature'
    )
    assert (
        rows_by_id['nomenclature_task_id2']['reason']
        == 'No products in nomenclature'
    )
    assert (
        rows_by_id['nomenclature_task_id3']['reason']
        == 'Negative weight in nomenclature'
    )
    # place_tasks_last_status table
    place_to_errors_messages = {
        1: 'No categories in nomenclature',
        2: 'No products in nomenclature',
        3: 'Negative weight in nomenclature',
    }
    for place_id in place_to_errors_messages:
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


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql(
    'eats_nomenclature_collector',
    files=['fill_for_items_with_incorrect_categories.sql'],
)
async def test_items_with_incorrect_categories(
        taxi_eats_nomenclature_collector,
        testpoint,
        pg_cursor,
        stq,
        mds_s3_storage,
        get_integrations_data,
        mockserver,
):
    @mockserver.json_handler(
        '/eats-core-retail/v1/place/client-categories/retrieve',
    )
    def _eats_core_retail(request):
        return {
            'has_client_categories': False,
            'has_client_categories_synchronization': False,
            'client_categories': [],
        }

    base_data = get_integrations_data(
        ['integrations_data_items_with_incorrect_categories.json'],
    )

    mds_s3_storage.put_object(
        'some_path/test1.json', json.dumps(base_data).encode('utf-8'),
    )

    # pylint: disable=unused-variable
    @testpoint('eats_nomenclature_collector::brand-task-result-sender')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_periodic_task(
        'eats-nomenclature-collector_brand-task-result-sender',
    )
    handle_finished.next_call()

    assert stq.eats_nomenclature_brand_processing.times_called == 0

    # brand tasks
    pg_cursor.execute(
        'select * from eats_nomenclature_collector.nomenclature_brand_tasks;',
    )
    rows = pg_cursor.fetchall()
    rows_by_id = {row['id']: row for row in rows}
    assert rows_by_id['brand1_task_id']['status'] == 'failed'
    assert (
        rows_by_id['brand1_task_id']['reason']
        == 'All nomenclature place tasks failed'
    )

    # place tasks
    pg_cursor.execute(
        'select * from eats_nomenclature_collector.nomenclature_place_tasks;',
    )
    rows = pg_cursor.fetchall()
    assert {row['id'] for row in rows if row['status'] == 'failed'} == {
        'nomenclature_task_id1',
    }
    rows_by_id = {row['id']: row for row in rows}
    assert (
        rows_by_id['nomenclature_task_id1']['reason']
        == 'No products in nomenclature'
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql(
    'eats_nomenclature_collector', files=['fill_for_no_origin_id.sql'],
)
@pytest.mark.parametrize(
    'integration_files, metrics_values, type_of_test',
    [
        pytest.param(
            ['integrations_data.json'],
            {
                'categories_with_not_existing_parent': 0,
                'items_with_not_existing_category': 0,
                'mismatched_items_with_same_origin_id': 0,
            },
            'no_incorrect_items',
            id='no_incorrect_items',
        ),
        pytest.param(
            [
                'integrations_data.json',
                'integrations_data_items_with_non_existing_categories.json',
            ],
            {
                'categories_with_not_existing_parent': 0,
                'items_with_not_existing_category': 2,
                'mismatched_items_with_same_origin_id': 0,
            },
            'has_incorrect_items',
            id='has_incorrect_items',
        ),
        pytest.param(
            [
                'integrations_data.json',
                'integrations_data_categories_with_non_existing_parents.json',
                'integrations_data_items_with_non_existing_categories.json',
            ],
            {
                'categories_with_not_existing_parent': 4,
                'items_with_not_existing_category': 2,
                'mismatched_items_with_same_origin_id': 0,
            },
            'has_incorrect_categories',
            id='has_incorrect_categories',
        ),
    ],
)
async def test_non_existing_categories(
        taxi_eats_nomenclature_collector,
        taxi_eats_nomenclature_collector_monitor,
        testpoint,
        pg_cursor,
        stq,
        mds_s3_storage,
        get_expected_result,
        get_integrations_data,
        mockserver,
        assert_added_stq_task,
        sql_get_place_tasks_last_status,
        to_utc_datetime,
        # parametrize params
        integration_files,
        metrics_values,
        type_of_test,
):
    brand_id_1 = '1'
    place_ids = ['1']

    base_data = get_integrations_data(integration_files)
    # no items with non-existing categories
    expected_result = get_expected_result(['base'], ['base'])
    dumped_base_data = json.dumps(base_data).encode('utf-8')

    mds_s3_storage.put_object('some_path/test1.json', dumped_base_data)

    @mockserver.json_handler(
        '/eats-core-retail/v1/place/client-categories/retrieve',
    )
    def _eats_core_retail(request):
        return {
            'has_client_categories': False,
            'has_client_categories_synchronization': False,
            'client_categories': [],
        }

    # pylint: disable=unused-variable
    @testpoint('eats_nomenclature_collector::brand-task-result-sender')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.tests_control(reset_metrics=True)

    await taxi_eats_nomenclature_collector.run_periodic_task(
        'eats-nomenclature-collector_brand-task-result-sender',
    )
    handle_finished.next_call()

    # 1 additional call is made while generating nmn json
    assert _eats_core_retail.times_called == 2

    assert stq.eats_nomenclature_brand_processing.times_called == 1

    brand_task_id = 'uuid-3'

    task_info = stq.eats_nomenclature_brand_processing.next_call()
    assert_added_stq_task(
        task_info,
        expected_brand_id=brand_id_1,
        expected_brand_task_id=brand_task_id,
        expected_place_ids=place_ids,
        expected_result=expected_result,
    )

    pg_cursor.execute(
        'select * from eats_nomenclature_collector.nomenclature_brand_tasks;',
    )
    rows = pg_cursor.fetchall()
    assert {row['id'] for row in rows if row['status'] == 'processed'} == {
        brand_task_id,
    }
    for place_id in place_ids:
        current_place_tasks_last_status = sql_get_place_tasks_last_status(
            pg_cursor, place_id, 'nomenclature',
        )
        expected_last_status = {
            'status': 'processed',
            'task_error': None,
            'task_warnings': None,
            'status_or_text_changed_at': to_utc_datetime(MOCK_NOW),
        }

        if type_of_test == 'has_incorrect_items':
            expected_last_status['task_warnings'] = (
                'Items with non existing category'
                '|No client category for origin id'
            )
        elif type_of_test == 'has_incorrect_categories':
            expected_last_status['task_warnings'] = (
                'Items with non existing category'
                '|No client category for origin id'
                '|Non existing parent client category'
            )

        assert expected_last_status == current_place_tasks_last_status

    metrics = await taxi_eats_nomenclature_collector_monitor.get_metrics()
    assert metrics[NOMENCLATURE_VALIDATION_METRICS_NAME] == metrics_values


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql(
    'eats_nomenclature_collector', files=['fill_for_no_origin_id.sql'],
)
async def test_mismatched_products(
        taxi_eats_nomenclature_collector,
        taxi_eats_nomenclature_collector_monitor,
        testpoint,
        pg_cursor,
        taxi_config,
        load_json,
        stq,
        mds_s3_storage,
        get_expected_result,
        get_integrations_data_from_json,
        mockserver,
        assert_added_stq_task,
        sql_get_place_tasks_last_status,
        to_utc_datetime,
):
    def _get_index_by_origin_id(elements, origin_id):
        for elem in elements:
            if elem['origin_id'] == origin_id:
                return elements.index(elem)
        return -1

    def _remove_by_origin_id(elements, origin_id):
        item_index = _get_index_by_origin_id(elements, origin_id)
        del elements[item_index]

    brand_id_1 = '1'
    place_ids = ['1', '2']
    mismatched_product_count = 2

    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_COLLECTOR_BRAND_TASK_RESULT_SENDER_SETTINGS': {
                'enabled': True,
                'period_in_sec': 5,
                'limit': 1000,
                'brands_with_deduplication': [brand_id_1],
                'brand_products_lookup_batch_size': 2,
            },
        },
    )

    base = load_json('integrations_data.json')
    json_1 = copy.deepcopy(base)
    json_2 = copy.deepcopy(base)
    json_2['place_id'] = 2
    for i in range(mismatched_product_count):
        json_2['menu_items'][i]['name'] = 'Something entirely different'

    for i, j_data in enumerate([json_1, json_2], start=1):
        data = get_integrations_data_from_json([j_data])
        dumped_data = json.dumps(data).encode('utf-8')
        mds_s3_storage.put_object(f'some_path/test{i}.json', dumped_data)

    brand_task_id = 'uuid-3'
    sql_add_place_task(
        pg_cursor,
        'uuid_99',
        '2',
        brand_task_id,
        'finished',
        'https://eda-integration.s3.mdst.yandex.net/some_path/test2.json',
    )

    expected_result = get_expected_result(['base'], ['base'])
    for i in range(mismatched_product_count):
        _remove_by_origin_id(
            expected_result['items'], base['menu_items'][1]['origin_id'],
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

    # pylint: disable=unused-variable
    @testpoint('eats_nomenclature_collector::brand-task-result-sender')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.tests_control(reset_metrics=True)

    await taxi_eats_nomenclature_collector.run_periodic_task(
        'eats-nomenclature-collector_brand-task-result-sender',
    )
    handle_finished.next_call()

    assert _eats_core_retail.times_called == 2

    assert stq.eats_nomenclature_brand_processing.times_called == 1

    task_info = stq.eats_nomenclature_brand_processing.next_call()
    assert_added_stq_task(
        task_info,
        expected_brand_id=brand_id_1,
        expected_brand_task_id=brand_task_id,
        expected_place_ids=place_ids,
        expected_result=expected_result,
    )

    metrics = await taxi_eats_nomenclature_collector_monitor.get_metrics()
    assert metrics[NOMENCLATURE_VALIDATION_METRICS_NAME] == {
        'categories_with_not_existing_parent': 0,
        'items_with_not_existing_category': 0,
        'mismatched_items_with_same_origin_id': mismatched_product_count,
    }

    for place_id in place_ids:
        current_place_tasks_last_status = sql_get_place_tasks_last_status(
            pg_cursor, place_id, 'nomenclature',
        )
        expected_last_status = {
            'status': 'processed',
            'task_error': None,
            'task_warnings': 'Mismatched items with same origin id',
            'status_or_text_changed_at': to_utc_datetime(MOCK_NOW),
        }

        assert expected_last_status == current_place_tasks_last_status


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
