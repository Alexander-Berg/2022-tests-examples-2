import json

import pytest


MOCK_NOW = '2021-03-03T09:00:00+00:00'


@pytest.fixture(name='assert_added_stq_task')
def _assert_added_stq_task(
        mds_s3_storage, get_nomenclature_with_chunks_from_s3,
):
    def do_assert_added_stq_task(
            task_info,
            expected_brand_id,
            expected_brand_task_id,
            expected_place_ids,
            expected_result,
            expected_file_datetime=MOCK_NOW,
            divide_into_chunks=False,
            items_chunk_size=None,
    ):
        brand_task_id, hash_value = task_info['id'].split('_')
        assert brand_task_id == expected_brand_task_id
        assert task_info['kwargs']['brand_id'] == expected_brand_id
        assert task_info['kwargs']['place_ids'] == expected_place_ids
        expected_s3_path = (
            f'nomenclature/task_{brand_task_id}_{hash_value}'
            if divide_into_chunks
            else f'nomenclature/task_{brand_task_id}_hash_{hash_value}.json'
        )
        assert task_info['kwargs']['s3_path'] == expected_s3_path
        assert task_info['kwargs']['file_datetime'] == expected_file_datetime
        if divide_into_chunks:
            result_json = get_nomenclature_with_chunks_from_s3(
                task_info['kwargs']['s3_path'],
                items_chunk_size=items_chunk_size,
            )
        else:
            result_json = json.loads(
                mds_s3_storage.storage[task_info['kwargs']['s3_path']].data,
            )
        assert result_json['place_ids'] == expected_place_ids
        assert _sorted_by_origin_id(
            result_json['categories'],
        ) == _sorted_by_origin_id(expected_result['categories'])
        assert result_json['items'] == expected_result['items']

    return do_assert_added_stq_task


@pytest.fixture(name='get_nomenclature_with_chunks_from_s3')
def _get_nomenclature_with_chunks_from_s3(mds_s3_storage):
    def get_nomenclature(s3_directory_path, items_chunk_size=None):
        result_json = json.loads(
            mds_s3_storage.storage[
                s3_directory_path + '/categories/categories.json'
            ].data,
        )
        items_files = mds_s3_storage.get_list(
            prefix=s3_directory_path + '/items',
        )
        for items_file in items_files['files']:
            items = json.loads(items_file.data)
            if items_chunk_size:
                assert len(items['items']) <= items_chunk_size
            result_json['items'] += items['items']
        return result_json

    return get_nomenclature


@pytest.fixture(name='get_integrations_data')
def _get_integrations_data(load_json, get_integrations_data_from_json):
    def do_get_integrations_data(filenames):
        return get_integrations_data_from_json(
            [load_json(filename) for filename in filenames],
        )

    return do_get_integrations_data


@pytest.fixture(name='get_integrations_data_from_json')
def _get_integrations_data_from_json(load_json):
    def do_smth(jsons):
        categories = []
        products = []
        for data in jsons:
            categories += data['menu_categories']
            products += data['menu_items']
        return {
            'menu_categories': categories,
            'menu_items': products,
            'place_id': '1',
        }

    return do_smth


@pytest.fixture(name='get_expected_result')
def _get_expected_result(load_json):
    def do_get_expected_result(categories_prefixes, products_prefixes):
        categories = []
        for categories_prefix in categories_prefixes:
            categories += load_json(
                f'{categories_prefix}_expected_categories.json',
            )['categories']
        products = []
        for products_prefix in products_prefixes:
            products += load_json(f'{products_prefix}_expected_products.json')[
                'items'
            ]
        return {
            'categories': _sorted_by_origin_id(categories),
            'items': _sorted_by_origin_id(products),
        }

    return do_get_expected_result


def _sorted_by_origin_id(elements):
    return sorted(elements, key=lambda elem: elem['origin_id'])
