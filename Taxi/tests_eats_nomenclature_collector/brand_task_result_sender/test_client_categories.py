import json

import pytest


CLIENT_CATEGORIES_METRICS_NAME = 'merge-client-categories'
MOCK_NOW = '2021-03-03T09:00:00+00:00'
MOCK_ORIGIN_ID = '77777777-7777-7777-7777-777777777777'
CLIENT_CATEGORY_1 = {
    'id': '123',
    'name': 'Мясо свежайшее',
    'origin_id': '0535c142-d00c-11ea-98c6-001e676a98dc',
    'sort': 100,
    'level': 1,
    'images': [
        {
            'url': (
                'https:\\/\\/avatars.mds.yandex.net\\/get-eda'
                '\\/1962206\\/2e61b8d92449c08b11f7273d2ed49dda\\/orig'
            ),
            'hash': '123EEA35625616DBBF38AABC45EB031563A7C021DE',
        },
    ],
}
CLIENT_CATEGORY_1_NO_ORIGIN_ID = {**CLIENT_CATEGORY_1, **{'origin_id': None}}
CLIENT_CATEGORY_2 = {
    'id': '456',
    'parent_id': '123',
    'name': 'Говядина свежайшая',
    'origin_id': '0535c146-d00c-11ea-98c6-001e676a98dc',
    'sort': 200,
    'level': 2,
    'images': [
        {
            'url': (
                'https:\\/\\/avatars.mds.yandex.net\\/get-eda'
                '\\/1962207\\/2e61b8d92449c08b11f7273d2ed49dda\\/orig'
            ),
            'hash': '456EEA35625616DBBF38AABC45EB031563A7C021DE',
        },
        {
            'url': (
                'https:\\/\\/avatars.mds.yandex.net\\/get-eda'
                '\\/1962208\\/2e61b8d92449c08b11f7273d2ed49dda\\/orig'
            ),
            'hash': '789EEA35625616DBBF38AABC45EB031563A7C021DE',
        },
    ],
}
CLIENT_CATEGORY_2_NOT_EXISTING_PARENT = {
    **CLIENT_CATEGORY_2,
    **{'parent_id': '999'},
}
CLIENT_CATEGORY_3 = {
    'id': '789',
    'parent_id': '123',
    'name': 'Телятина свежайшая',
    'origin_id': 'a4f3de10-72cc-46c8-8d9c-a2d830ede59f',
    'sort': 300,
    'level': 2,
    'images': [
        {
            'url': (
                'https:\\/\\/avatars.mds.yandex.net\\/get-eda'
                '\\/1962209\\/2e61b8d92449c08b11f7273d2ed49dda\\/orig'
            ),
            'hash': '012EEA35625616DBBF38AABC45EB031563A7C021DE',
        },
    ],
}


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql(
    'eats_nomenclature_collector',
    files=['fill_for_merge_with_client_categories.sql'],
)
@pytest.mark.parametrize(
    'clients_categories_result, expected_categories, expected_products',
    [
        pytest.param(
            {
                'has_client_categories': False,
                'has_client_categories_synchronization': False,
                'client_categories': [],
            },
            ['base'],
            ['base'],
            id='no_client_categories',
        ),
        pytest.param(
            {
                'has_client_categories': True,
                'has_client_categories_synchronization': True,
                'client_categories': [
                    CLIENT_CATEGORY_1,
                    CLIENT_CATEGORY_2,
                    CLIENT_CATEGORY_3,
                ],
            },
            ['synchronized'],
            ['base'],
            id='synchronized',
        ),
        pytest.param(
            {
                'has_client_categories': True,
                'has_client_categories_synchronization': False,
                'client_categories': [
                    CLIENT_CATEGORY_1,
                    CLIENT_CATEGORY_2,
                    CLIENT_CATEGORY_3,
                ],
            },
            ['not_synchronized'],
            ['base'],
            id='not_synchronized',
        ),
        pytest.param('404', ['base'], ['base'], id='error_404'),
        pytest.param('500', ['base'], ['base'], id='error_500'),
        pytest.param('timeout', ['base'], ['base'], id='timeout'),
    ],
)
async def test_merge_with_client_categories(
        taxi_eats_nomenclature_collector,
        testpoint,
        pg_cursor,
        stq,
        mds_s3_storage,
        get_integrations_data,
        get_expected_result,
        mockserver,
        assert_added_stq_task,
        clients_categories_result,
        expected_categories,
        expected_products,
):
    brand_id_1 = '1'
    place_ids = ['1', '2', '3']

    base_data = get_integrations_data(['integrations_data.json'])
    expected_result = get_expected_result(
        expected_categories, expected_products,
    )
    dumped_base_data = json.dumps(base_data).encode('utf-8')

    mds_s3_storage.put_object('some_path/test1.json', dumped_base_data)
    mds_s3_storage.put_object('some_path/test2.json', dumped_base_data)
    mds_s3_storage.put_object('some_path/test3.json', dumped_base_data)

    @mockserver.json_handler(
        '/eats-core-retail/v1/place/client-categories/retrieve',
    )
    def _eats_core_retail(request):
        assert request.query['place_id'] in place_ids
        if clients_categories_result in ('404', '500'):
            result_status = int(clients_categories_result)
            return mockserver.make_response(
                status=result_status,
                json={'code': str(result_status), 'message': 'some error'},
            )
        if clients_categories_result == 'timeout':
            raise mockserver.TimeoutError()
        return clients_categories_result

    # pylint: disable=unused-variable
    @testpoint('eats_nomenclature_collector::brand-task-result-sender')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_periodic_task(
        'eats-nomenclature-collector_brand-task-result-sender',
    )
    handle_finished.next_call()

    if clients_categories_result in ('500', 'timeout'):
        # 2 attempts in EDA_CATALOG_CLIENT_QOS for each call
        # 1 additional call is made while generating nmn json
        assert _eats_core_retail.times_called == 8
    else:
        assert _eats_core_retail.times_called == 4

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


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql(
    'eats_nomenclature_collector',
    files=['fill_for_merge_with_client_categories.sql'],
)
@pytest.mark.parametrize(
    'clients_categories_result, expected_categories,'
    'expected_products, metrics_values',
    [
        pytest.param(
            {
                'has_client_categories': False,
                'has_client_categories_synchronization': False,
                'client_categories': [],
            },
            ['base', 'additional'],
            ['base', 'additional'],
            {
                'no_origin_id': 0,
                'not_existing_parent_client_category': 0,
                'no_client_category_for_origin_id': 0,
                'skipped_items_with_no_client_categories': 0,
            },
            id='no_client_categories',
        ),
        pytest.param(
            {
                'has_client_categories': True,
                'has_client_categories_synchronization': True,
                'client_categories': [
                    CLIENT_CATEGORY_1,
                    CLIENT_CATEGORY_2,
                    CLIENT_CATEGORY_3,
                ],
            },
            ['synchronized', 'additional'],
            ['base', 'additional'],
            {
                'no_origin_id': 0,
                'not_existing_parent_client_category': 0,
                # count metrics for each place
                'no_client_category_for_origin_id': 6,
                'skipped_items_with_no_client_categories': 0,
            },
            id='synchronized',
        ),
        pytest.param(
            {
                'has_client_categories': True,
                'has_client_categories_synchronization': False,
                'client_categories': [
                    CLIENT_CATEGORY_1,
                    CLIENT_CATEGORY_2,
                    CLIENT_CATEGORY_3,
                ],
            },
            ['not_synchronized'],
            ['base', 'metrics'],
            {
                'no_origin_id': 0,
                'not_existing_parent_client_category': 0,
                # count metrics for each place
                'no_client_category_for_origin_id': 6,
                'skipped_items_with_no_client_categories': 6,
            },
            id='not_synchronized',
        ),
        pytest.param(
            {
                'has_client_categories': True,
                'has_client_categories_synchronization': False,
                'client_categories': [
                    CLIENT_CATEGORY_1,
                    CLIENT_CATEGORY_2_NOT_EXISTING_PARENT,
                    CLIENT_CATEGORY_3,
                ],
            },
            ['not_existing_parent'],
            ['metrics'],
            {
                'no_origin_id': 0,
                # count metrics for each place
                'not_existing_parent_client_category': 3,
                'no_client_category_for_origin_id': 21,
                'skipped_items_with_no_client_categories': 21,
            },
            id='not_existing_parent',
        ),
    ],
)
async def test_client_categories_metrics(
        taxi_eats_nomenclature_collector,
        taxi_eats_nomenclature_collector_monitor,
        testpoint,
        pg_cursor,
        stq,
        mds_s3_storage,
        get_integrations_data,
        get_expected_result,
        mockserver,
        assert_added_stq_task,
        clients_categories_result,
        expected_categories,
        expected_products,
        metrics_values,
):
    brand_id_1 = '1'
    place_ids = ['1', '2', '3']

    base_data = get_integrations_data(
        [
            'integrations_data.json',
            'integrations_data_additional.json',
            'integrations_data_client_categories_metrics.json',
        ],
    )
    expected_result = get_expected_result(
        expected_categories, expected_products,
    )
    dumped_base_data = json.dumps(base_data).encode('utf-8')

    mds_s3_storage.put_object('some_path/test1.json', dumped_base_data)
    mds_s3_storage.put_object('some_path/test2.json', dumped_base_data)
    mds_s3_storage.put_object('some_path/test3.json', dumped_base_data)

    @mockserver.json_handler(
        '/eats-core-retail/v1/place/client-categories/retrieve',
    )
    def _eats_core_retail(request):
        assert request.query['place_id'] in place_ids
        return clients_categories_result

    # pylint: disable=unused-variable
    @testpoint('eats_nomenclature_collector::brand-task-result-sender')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.tests_control(reset_metrics=True)

    await taxi_eats_nomenclature_collector.run_periodic_task(
        'eats-nomenclature-collector_brand-task-result-sender',
    )
    handle_finished.next_call()

    assert _eats_core_retail.times_called == 4

    brand_task_id = 'uuid-3'

    assert stq.eats_nomenclature_brand_processing.times_called == 1
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

    metrics = await taxi_eats_nomenclature_collector_monitor.get_metrics()
    assert metrics[CLIENT_CATEGORIES_METRICS_NAME] == metrics_values


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'clients_categories_file, expected_result_prefix, metrics_values, '
    'type_of_test',
    [
        pytest.param(
            'root_category_has_origin_id.json',
            'root_category_has_origin_id',
            {
                'no_origin_id': 1,
                'not_existing_parent_client_category': 0,
                'no_client_category_for_origin_id': 4,
                'skipped_items_with_no_client_categories': 4,
            },
            'root_category_has_origin_id',
            id='root_category_has_origin_id',
        ),
        pytest.param(
            'root_category_mapped_in_db.json',
            'root_category_mapped_in_db',
            {
                'no_origin_id': 1,
                'not_existing_parent_client_category': 1,
                'no_client_category_for_origin_id': 4,
                'skipped_items_with_no_client_categories': 4,
            },
            'root_category_mapped_in_db',
            id='root_category_mapped_in_db',
        ),
        pytest.param(
            'root_category_mapped_to_partner.json',
            'root_category_mapped_to_partner',
            {
                'no_origin_id': 1,
                'not_existing_parent_client_category': 0,
                'no_client_category_for_origin_id': 4,
                'skipped_items_with_no_client_categories': 4,
            },
            'root_category_mapped_to_partner',
            id='root_category_mapped_to_partner',
        ),
        pytest.param(
            'root_category_should_be_generated.json',
            'root_category_should_be_generated',
            {
                'no_origin_id': 2,
                'not_existing_parent_client_category': 0,
                'no_client_category_for_origin_id': 4,
                'skipped_items_with_no_client_categories': 4,
            },
            'root_category_should_be_generated',
            id='root_category_should_be_generated',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature_collector', files=['fill_for_no_origin_id.sql'],
)
async def test_client_categories_no_origin_id(
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
        load_json,
        clients_categories_file,
        expected_result_prefix,
        metrics_values,
        type_of_test,
        to_utc_datetime,
        sql_get_place_tasks_last_status,
):
    brand_id_1 = '1'
    place_ids = ['1']

    base_data = get_integrations_data(
        ['integrations_data_for_no_origin_id.json'],
    )
    expected_result = get_expected_result(
        [expected_result_prefix], [expected_result_prefix],
    )
    dumped_base_data = json.dumps(base_data).encode('utf-8')

    mds_s3_storage.put_object('some_path/test1.json', dumped_base_data)

    @mockserver.json_handler(
        '/eats-core-retail/v1/place/client-categories/retrieve',
    )
    def _eats_core_retail(request):
        assert request.query['place_id'] in place_ids
        return load_json(clients_categories_file)

    # pylint: disable=unused-variable
    @testpoint('eats_nomenclature_collector::generate-origin-id')
    def generate_origin_id(arg):
        mock_origin_id = MOCK_ORIGIN_ID[:-1] + chr(generate_origin_id.count)
        generate_origin_id.count += 1
        return {'mock_origin_id': mock_origin_id}

    generate_origin_id.count = ord('a')

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
        if type_of_test == 'root_category_mapped_in_db':
            expected_last_status['task_warnings'] = (
                'No client category for origin id|'
                'Non existing parent client category|'
                'Client category without origin id|'
                'Skipped items with no client categories'
            )
        else:
            expected_last_status['task_warnings'] = (
                'No client category for origin id|'
                'Client category without origin id|'
                'Skipped items with no client categories'
            )

        assert expected_last_status == current_place_tasks_last_status

    metrics = await taxi_eats_nomenclature_collector_monitor.get_metrics()
    assert metrics[CLIENT_CATEGORIES_METRICS_NAME] == metrics_values


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql(
    'eats_nomenclature_collector', files=['fill_for_no_origin_id.sql'],
)
async def test_client_categories_with_cycle(
        taxi_eats_nomenclature_collector,
        testpoint,
        mds_s3_storage,
        get_integrations_data,
        mockserver,
        load_json,
):
    place_ids = ['1']

    base_data = get_integrations_data(
        ['integrations_data_for_no_origin_id.json'],
    )
    dumped_base_data = json.dumps(base_data).encode('utf-8')

    mds_s3_storage.put_object('some_path/test1.json', dumped_base_data)

    @mockserver.json_handler(
        '/eats-core-retail/v1/place/client-categories/retrieve',
    )
    def _eats_core_retail(request):
        assert request.query['place_id'] in place_ids
        return load_json('categories_with_cycle.json')

    # pylint: disable=unused-variable
    @testpoint('eats_nomenclature_collector::generate-origin-id')
    def generate_origin_id(arg):
        mock_origin_id = MOCK_ORIGIN_ID[:-1] + chr(generate_origin_id.count)
        generate_origin_id.count += 1
        return {'mock_origin_id': mock_origin_id}

    generate_origin_id.count = ord('a')

    # pylint: disable=unused-variable
    @testpoint('eats_nomenclature_collector::brand-task-result-sender')
    def handle_finished(arg):
        pass

    # pylint: disable=unused-variable
    @testpoint('traverse-client-categories-tree')
    def cycle_in_client_categories(arg):
        assert arg['category_id'] == '2222'

    await taxi_eats_nomenclature_collector.tests_control(reset_metrics=True)

    await taxi_eats_nomenclature_collector.run_periodic_task(
        'eats-nomenclature-collector_brand-task-result-sender',
    )
    handle_finished.next_call()

    assert cycle_in_client_categories.times_called == 1
