import copy
import datetime as dt
import json

import pytest


MOCK_NOW = '2021-03-03T09:00:00+00:00'
ISO_FORMAT_WITH_TZ = '%Y-%m-%dT%H:%M:%S+00:00'


@pytest.mark.parametrize(
    'should_add_processed_tasks,'
    'brands_with_deduplication,'
    'divide_into_chunks',
    [
        pytest.param(False, [], False, id='no_processed_no_deduplication'),
        pytest.param(False, ['1'], False, id='no_processed_has_deduplication'),
        pytest.param(True, [], False, id='has_processed_no_deduplication'),
        pytest.param(True, ['1'], False, id='has_processed_has_deduplication'),
        pytest.param(
            False, [], True, id='no_processed_no_deduplication_w_chunks',
        ),
        pytest.param(
            False, ['1'], True, id='no_processed_has_deduplication_w_chunks',
        ),
        pytest.param(
            True, [], True, id='has_processed_no_deduplication_w_chunks',
        ),
        pytest.param(
            True, ['1'], True, id='has_processed_has_deduplication_w_chunks',
        ),
    ],
)
@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql(
    'eats_nomenclature_collector', files=['fill_for_nomenclature_hashing.sql'],
)
async def test_nomenclature_hashing(
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
        get_nomenclature_with_chunks_from_s3,
        # parametrize params
        should_add_processed_tasks,
        brands_with_deduplication,
        divide_into_chunks,
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

    items_chunk_size = 1
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_COLLECTOR_BRAND_TASK_RESULT_SENDER_SETTINGS': {
                'enabled': True,
                'period_in_sec': 5,
                'limit': 1000,
                'should_add_processed_tasks': should_add_processed_tasks,
                'brands_with_deduplication': brands_with_deduplication,
                'divide_assortment_into_chunks': divide_into_chunks,
                'items_chunk_size': items_chunk_size,
            },
        },
    )

    brand_id_1 = '1'
    brand_id_2 = '2'

    should_deduplicate_assortments = False
    if brand_id_1 in brands_with_deduplication:
        should_deduplicate_assortments = True

    base_data = get_integrations_data(
        ['integrations_data.json', 'integrations_data_additional.json'],
    )
    base_expected_result = get_expected_result(
        ['base', 'additional'], ['base', 'additional'],
    )

    # all categories and all products
    data_1 = copy.deepcopy(base_data)

    # different order of categories and products
    data_2 = copy.deepcopy(base_data)
    _swap_elements_by_index(data_2['menu_items'], 0, 1)
    _swap_elements_by_index(data_2['menu_categories'], 0, 1)

    # different price in some products
    data_3 = copy.deepcopy(base_data)
    data_3['menu_items'][0]['price'] = '121'

    # all categories, but without some products
    data_8 = copy.deepcopy(base_data)
    _remove_by_origin_id(data_8['menu_items'], 'РН078099')
    expected_8 = copy.deepcopy(base_expected_result)
    _remove_by_origin_id(expected_8['items'], 'РН078099')

    # all categories, but without some other products
    data_12 = copy.deepcopy(base_data)
    _remove_by_origin_id(data_12['menu_items'], 'РН109815')
    expected_12 = copy.deepcopy(base_expected_result)
    _remove_by_origin_id(expected_12['items'], 'РН109815')

    # changed name in one product
    mismatched_product_origin_id = 'РН076676'
    new_item_name_13 = 'Something different'
    data_13 = copy.deepcopy(base_data)
    _change_by_origin_id(
        data_13['menu_items'],
        mismatched_product_origin_id,
        'name',
        new_item_name_13,
    )
    expected_13 = copy.deepcopy(base_expected_result)
    _change_by_origin_id(
        expected_13['items'],
        mismatched_product_origin_id,
        'name',
        new_item_name_13,
    )

    expected_1_2_3_8_12_13 = copy.deepcopy(base_expected_result)
    _remove_by_origin_id(
        expected_1_2_3_8_12_13['items'], mismatched_product_origin_id,
    )

    # changed product category in one product
    # and removed another product
    new_item_category_4 = 'ab286be8-e833-4396-a91a-49e15ddb3f0d'
    data_4 = copy.deepcopy(base_data)
    _change_by_origin_id(
        data_4['menu_items'],
        'РН109815',
        'category_origin_id',
        new_item_category_4,
    )
    _remove_by_origin_id(data_4['menu_items'], 'РН078098')

    # changed product category in one product
    # and removed another product
    new_item_category_10 = '0535c146-d00c-11ea-98c6-001e676a98dc'
    data_10 = copy.deepcopy(base_data)
    _change_by_origin_id(
        data_10['menu_items'],
        'РН078098',
        'category_origin_id',
        new_item_category_10,
    )
    _remove_by_origin_id(data_10['menu_items'], 'РН109815')

    # results with deduplication (one hash):
    # - test4 has a different category for product РН109815
    #   and doesn't have product РН078098
    # - test10 has a different category for product РН078098
    #   and doesn't have product РН109815
    # so test4 and test10 results have the same hash
    expected_4_and_10 = copy.deepcopy(base_expected_result)
    _change_by_origin_id(
        expected_4_and_10['items'],
        'РН109815',
        'category_origin_ids',
        [new_item_category_4],
    )
    _change_by_origin_id(
        expected_4_and_10['items'],
        'РН078098',
        'category_origin_ids',
        [new_item_category_10],
    )
    if should_deduplicate_assortments:
        _remove_by_origin_id(
            expected_4_and_10['items'], mismatched_product_origin_id,
        )

    # results without deduplication (different hashes)
    expected_4 = copy.deepcopy(base_expected_result)
    _change_by_origin_id(
        expected_4['items'],
        'РН109815',
        'category_origin_ids',
        [new_item_category_4],
    )
    _remove_by_origin_id(expected_4['items'], 'РН078098')
    expected_10 = copy.deepcopy(base_expected_result)
    _change_by_origin_id(
        expected_10['items'],
        'РН078098',
        'category_origin_ids',
        [new_item_category_10],
    )
    _remove_by_origin_id(expected_10['items'], 'РН109815')

    # different product category in one product
    # but all other products are not changed
    # so hash is different from task4 and task10
    data_11 = copy.deepcopy(base_data)
    _change_by_origin_id(
        data_11['menu_items'],
        'РН078098',
        'category_origin_id',
        new_item_category_10,
    )
    expected_11 = copy.deepcopy(base_expected_result)
    _change_by_origin_id(
        expected_11['items'],
        'РН078098',
        'category_origin_ids',
        [new_item_category_10],
    )
    if should_deduplicate_assortments:
        _remove_by_origin_id(
            expected_11['items'], mismatched_product_origin_id,
        )

    # not all categories and products (changes hash)
    data_9 = get_integrations_data(['integrations_data.json'])
    expected_9 = get_expected_result(['base'], ['base'])
    if should_deduplicate_assortments:
        _remove_by_origin_id(expected_9['items'], mismatched_product_origin_id)

    # another brand
    data_5 = get_integrations_data(['integrations_data.json'])
    _remove_by_origin_id(data_5['menu_items'], 'РН078055')
    expected_5 = get_expected_result(['base'], ['base'])
    _remove_by_origin_id(expected_5['items'], 'РН078055')

    # put all files to s3

    mds_s3_storage.put_object(
        'some_path/test1.json', json.dumps(data_1).encode('utf-8'),
    )
    mds_s3_storage.put_object(
        'some_path/test2.json', json.dumps(data_2).encode('utf-8'),
    )  # the same hash as the first
    mds_s3_storage.put_object(
        'some_path/test3.json', json.dumps(data_3).encode('utf-8'),
    )  # the same hash as the first
    mds_s3_storage.put_object(
        'some_path/test8.json', json.dumps(data_8).encode('utf-8'),
    )  # the same hash as the first (if deduplication was enabled)
    mds_s3_storage.put_object(
        'some_path/test12.json', json.dumps(data_12).encode('utf-8'),
    )  # the same hash as the first (if deduplication was enabled)
    mds_s3_storage.put_object(
        'some_path/test13.json', json.dumps(data_13).encode('utf-8'),
    )  # the same hash as the first (if deduplication was enabled)

    mds_s3_storage.put_object(
        'some_path/test4.json', json.dumps(data_4).encode('utf-8'),
    )  # different by product categories
    mds_s3_storage.put_object(
        'some_path/test10.json', json.dumps(data_10).encode('utf-8'),
    )  # different by product categories (but same hash as 4)

    mds_s3_storage.put_object(
        'some_path/test11.json', json.dumps(data_11).encode('utf-8'),
    )  # different by only product РН078098

    mds_s3_storage.put_object(
        'some_path/test9.json', json.dumps(data_9).encode('utf-8'),
    )  # different by categories

    mds_s3_storage.put_object(
        'some_path/test5.json', json.dumps(data_5).encode('utf-8'),
    )  # another brand

    # pylint: disable=unused-variable
    @testpoint('eats_nomenclature_collector::brand-task-result-sender')
    def handle_finished(arg):
        pass

    # process all brand tasks
    for _ in range(2):
        await taxi_eats_nomenclature_collector.run_periodic_task(
            'eats-nomenclature-collector_brand-task-result-sender',
        )
        handle_finished.next_call()

    stq_times_called = stq.eats_nomenclature_brand_processing.times_called
    if should_deduplicate_assortments:
        assert stq_times_called == 5
    else:
        assert stq_times_called == 9

    hashes = set()
    file_datetime = MOCK_NOW
    stq_delay_in_seconds = 5
    for i in range(stq_times_called):
        task_info = stq.eats_nomenclature_brand_processing.next_call()
        if divide_into_chunks:
            result_json = get_nomenclature_with_chunks_from_s3(
                task_info['kwargs']['s3_path'],
                items_chunk_size=items_chunk_size,
            )
        else:
            result_json = json.loads(
                mds_s3_storage.storage[task_info['kwargs']['s3_path']].data,
            )
        if set(result_json['place_ids']).issubset({'4', '10'}):
            if should_deduplicate_assortments:
                assert_added_stq_task(
                    task_info,
                    expected_brand_id=brand_id_1,
                    expected_brand_task_id='brand-task-1-finished',
                    expected_place_ids=['4', '10'],
                    expected_result=expected_4_and_10,
                    expected_file_datetime=file_datetime,
                    divide_into_chunks=divide_into_chunks,
                    items_chunk_size=items_chunk_size,
                )
            else:
                if result_json['place_ids'] == ['4']:
                    assert_added_stq_task(
                        task_info,
                        expected_brand_id=brand_id_1,
                        expected_brand_task_id='brand-task-1-finished',
                        expected_place_ids=['4'],
                        expected_result=expected_4,
                        expected_file_datetime=file_datetime,
                        divide_into_chunks=divide_into_chunks,
                        items_chunk_size=items_chunk_size,
                    )
                else:
                    assert_added_stq_task(
                        task_info,
                        expected_brand_id=brand_id_1,
                        expected_brand_task_id='brand-task-1-finished',
                        expected_place_ids=['10'],
                        expected_result=expected_10,
                        expected_file_datetime=file_datetime,
                        divide_into_chunks=divide_into_chunks,
                        items_chunk_size=items_chunk_size,
                    )
        elif result_json['place_ids'] == ['11']:
            assert_added_stq_task(
                task_info,
                expected_brand_id=brand_id_1,
                expected_brand_task_id='brand-task-1-finished',
                expected_place_ids=['11'],
                expected_result=expected_11,
                expected_file_datetime=file_datetime,
                divide_into_chunks=divide_into_chunks,
                items_chunk_size=items_chunk_size,
            )
        elif result_json['place_ids'] == ['9']:
            assert_added_stq_task(
                task_info,
                expected_brand_id=brand_id_1,
                expected_brand_task_id='brand-task-1-finished',
                expected_place_ids=['9'],
                expected_result=expected_9,
                expected_file_datetime=file_datetime,
                divide_into_chunks=divide_into_chunks,
                items_chunk_size=items_chunk_size,
            )
        elif result_json['place_ids'] == ['5']:
            assert_added_stq_task(
                task_info,
                expected_brand_id=brand_id_2,
                expected_brand_task_id='brand-task-2-finished',
                expected_place_ids=['5'],
                expected_result=expected_5,
                # another brand is sent in parallel
                expected_file_datetime=MOCK_NOW,
                divide_into_chunks=divide_into_chunks,
                items_chunk_size=items_chunk_size,
            )
        else:
            if should_deduplicate_assortments:
                expected_place_ids = ['1', '2', '3', '8', '12', '13']
                if should_add_processed_tasks:
                    expected_place_ids.append('6')
                assert_added_stq_task(
                    task_info,
                    expected_brand_id=brand_id_1,
                    expected_brand_task_id='brand-task-1-finished',
                    expected_place_ids=expected_place_ids,
                    expected_result=expected_1_2_3_8_12_13,
                    expected_file_datetime=file_datetime,
                    divide_into_chunks=divide_into_chunks,
                    items_chunk_size=items_chunk_size,
                )
            else:
                if result_json['place_ids'] == ['8']:
                    assert_added_stq_task(
                        task_info,
                        expected_brand_id=brand_id_1,
                        expected_brand_task_id='brand-task-1-finished',
                        expected_place_ids=['8'],
                        expected_result=expected_8,
                        expected_file_datetime=file_datetime,
                        divide_into_chunks=divide_into_chunks,
                        items_chunk_size=items_chunk_size,
                    )
                elif result_json['place_ids'] == ['12']:
                    assert_added_stq_task(
                        task_info,
                        expected_brand_id=brand_id_1,
                        expected_brand_task_id='brand-task-1-finished',
                        expected_place_ids=['12'],
                        expected_result=expected_12,
                        expected_file_datetime=file_datetime,
                        divide_into_chunks=divide_into_chunks,
                        items_chunk_size=items_chunk_size,
                    )
                elif result_json['place_ids'] == ['13']:
                    assert_added_stq_task(
                        task_info,
                        expected_brand_id=brand_id_1,
                        expected_brand_task_id='brand-task-1-finished',
                        expected_place_ids=['13'],
                        expected_result=expected_13,
                        expected_file_datetime=file_datetime,
                        divide_into_chunks=divide_into_chunks,
                        items_chunk_size=items_chunk_size,
                    )
                else:
                    expected_place_ids = ['1', '2', '3']
                    if should_add_processed_tasks:
                        expected_place_ids.append('6')
                    assert_added_stq_task(
                        task_info,
                        expected_brand_id=brand_id_1,
                        expected_brand_task_id='brand-task-1-finished',
                        expected_place_ids=expected_place_ids,
                        expected_result=base_expected_result,
                        expected_file_datetime=file_datetime,
                        divide_into_chunks=divide_into_chunks,
                        items_chunk_size=items_chunk_size,
                    )
        hashes.add(_get_hash_from_task_info(task_info))
        file_datetime = to_utc_datetime(file_datetime) + dt.timedelta(
            seconds=stq_delay_in_seconds,
        )
        file_datetime = file_datetime.strftime(ISO_FORMAT_WITH_TZ)
    assert len(hashes) == stq_times_called


def _get_hash_from_task_info(task_info):
    _, hash_value = task_info['id'].split('_')
    return hash_value


def _get_index_by_origin_id(elements, origin_id):
    for elem in elements:
        if elem['origin_id'] == origin_id:
            return elements.index(elem)
    return -1


def _change_by_origin_id(elements, origin_id, field, new_value):
    item_index = _get_index_by_origin_id(elements, origin_id)
    elements[item_index][field] = new_value


def _remove_by_origin_id(elements, origin_id):
    item_index = _get_index_by_origin_id(elements, origin_id)
    del elements[item_index]


def _swap_elements_by_index(elements, index1, index2):
    elements[index1], elements[index2] = elements[index2], elements[index1]
