import copy
import datetime as dt
import json

import pytest


MOCK_NOW = '2021-03-03T09:00:00+00:00'
ISO_FORMAT_WITH_TZ = '%Y-%m-%dT%H:%M:%S+00:00'
MOCK_ORIGIN_ID = '77777777-7777-7777-7777-777777777777'


@pytest.mark.parametrize(
    'should_build_misc_category, should_deduplicate_assortments, data_prefix',
    [
        pytest.param(
            False,
            False,
            'without_misc_categories',
            id='no_misc_categories_no_deduplication',
        ),
        pytest.param(
            False,
            True,
            'without_misc_categories',
            id='no_misc_categories_with_deduplication',
        ),
        pytest.param(
            True,
            False,
            'with_misc_categories',
            id='with_misc_categories_no_deduplication',
        ),
        pytest.param(
            True,
            True,
            'with_misc_categories',
            id='with_misc_categories_with_deduplication',
        ),
    ],
)
@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql(
    'eats_nomenclature_collector', files=['fill_for_misc_categories.sql'],
)
async def test_misc_category(
        taxi_eats_nomenclature_collector,
        taxi_config,
        testpoint,
        stq,
        mds_s3_storage,
        get_integrations_data,
        get_expected_result,
        mockserver,
        to_utc_datetime,
        assert_added_stq_task,
        pg_cursor,
        # parametrize params
        should_build_misc_category,
        should_deduplicate_assortments,
        data_prefix,
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

    # pylint: disable=unused-variable
    @testpoint('eats_nomenclature_collector::brand-task-result-sender')
    def handle_finished(arg):
        pass

    @testpoint('eats_nomenclature_collector::generate-origin-id')
    def generate_origin_id(arg):
        mock_origin_id = MOCK_ORIGIN_ID[:-1] + chr(generate_origin_id.count)
        generate_origin_id.count += 1
        return {'mock_origin_id': mock_origin_id}

    generate_origin_id.count = ord('a')

    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_COLLECTOR_BRAND_TASK_RESULT_SENDER_SETTINGS': {
                'enabled': True,
                'period_in_sec': 5,
                'limit': 1000,
                'should_add_processed_tasks': False,
                'brands_with_deduplication': (
                    ['1'] if should_deduplicate_assortments else []
                ),
                'should_build_misc_category': should_build_misc_category,
                'misc_category_names': ['Прочее', 'Остальное', 'Разное'],
            },
        },
    )

    base_data = get_integrations_data(['integrations_data.json'])
    # all categories and all products
    data_1 = copy.deepcopy(base_data)
    # another order of categories and products
    data_2 = copy.deepcopy(base_data)
    _swap_elements_by_index(data_2['menu_items'], 0, 1)
    _swap_elements_by_index(data_2['menu_categories'], 0, 1)
    # all categories, but without some products
    data_3 = copy.deepcopy(base_data)
    _remove_by_origin_id(data_3['menu_items'], 'РН078099')

    base_expected_result = get_expected_result([data_prefix], [data_prefix])
    expected_1_2 = copy.deepcopy(base_expected_result)
    expected_3 = copy.deepcopy(base_expected_result)
    _remove_by_origin_id(expected_3['items'], 'РН078099')

    mds_s3_storage.put_object(
        'some_path/test1.json', json.dumps(data_1).encode('utf-8'),
    )
    mds_s3_storage.put_object(
        'some_path/test2.json', json.dumps(data_2).encode('utf-8'),
    )
    mds_s3_storage.put_object(
        'some_path/test3.json', json.dumps(data_3).encode('utf-8'),
    )

    await taxi_eats_nomenclature_collector.run_periodic_task(
        'eats-nomenclature-collector_brand-task-result-sender',
    )
    handle_finished.next_call()

    stq_times_called = stq.eats_nomenclature_brand_processing.times_called
    if should_deduplicate_assortments:
        assert stq_times_called == 1
    else:
        assert stq_times_called == 2

    brand_id = '1'
    brand_task_id = 'brand-task-1-finished'
    file_datetime = MOCK_NOW
    stq_delay_in_seconds = 5
    for _ in range(stq_times_called):
        task_info = stq.eats_nomenclature_brand_processing.next_call()
        result_json = json.loads(
            mds_s3_storage.storage[task_info['kwargs']['s3_path']].data,
        )
        if should_deduplicate_assortments:
            expected_place_ids = ['1', '2', '3']
            assert_added_stq_task(
                task_info,
                expected_brand_id=brand_id,
                expected_brand_task_id=brand_task_id,
                expected_place_ids=expected_place_ids,
                expected_result=base_expected_result,
                expected_file_datetime=file_datetime,
            )
        else:
            if result_json['place_ids'] == ['3']:
                assert_added_stq_task(
                    task_info,
                    expected_brand_id=brand_id,
                    expected_brand_task_id=brand_task_id,
                    expected_place_ids=['3'],
                    expected_result=expected_3,
                    expected_file_datetime=file_datetime,
                )
            else:
                # using existing misc origin_ids is checked here:
                # data for place_ids = [1, 2] is processed after
                # place_id = 3, so it uses the same misc origin_ids.
                expected_place_ids = ['1', '2']
                assert_added_stq_task(
                    task_info,
                    expected_brand_id=brand_id,
                    expected_brand_task_id=brand_task_id,
                    expected_place_ids=expected_place_ids,
                    expected_result=expected_1_2,
                    expected_file_datetime=file_datetime,
                )
        file_datetime = to_utc_datetime(file_datetime) + dt.timedelta(
            seconds=stq_delay_in_seconds,
        )
        file_datetime = file_datetime.strftime(ISO_FORMAT_WITH_TZ)

    expected_misc_categories = []
    if should_build_misc_category:
        expected_misc_categories = [
            {
                'brand_id': brand_id,
                'name': 'Прочее',
                'origin_id': '77777777-7777-7777-7777-77777777777a',
                'parent_origin_id': '0535c146-d00c-11ea-98c6-001e676a98dc',
            },
            {
                'brand_id': brand_id,
                'name': 'Остальное',
                'origin_id': '77777777-7777-7777-7777-77777777777b',
                'parent_origin_id': 'ab286be8-e833-4396-a91a-49e15ddb3f0d',
            },
        ]
    assert sql_get_misc_categories(pg_cursor) == expected_misc_categories


def _get_index_by_origin_id(elements, origin_id):
    for elem in elements:
        if elem['origin_id'] == origin_id:
            return elements.index(elem)
    return -1


def _remove_by_origin_id(elements, origin_id):
    item_index = _get_index_by_origin_id(elements, origin_id)
    del elements[item_index]


def _swap_elements_by_index(elements, index1, index2):
    elements[index1], elements[index2] = elements[index2], elements[index1]


def sql_get_misc_categories(pg_cursor):
    pg_cursor.execute(
        'select * from eats_nomenclature_collector.misc_categories;',
    )
    return pg_cursor.fetchall()
