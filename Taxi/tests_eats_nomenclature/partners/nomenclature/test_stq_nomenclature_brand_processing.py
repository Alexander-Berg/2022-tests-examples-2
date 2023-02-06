import datetime as dt
import math

import pytest
import pytz

BRAND_ID = 777

S3_OLD_NOMENCLATURE_PATH = 'old_nomenclature/brand_nomenclature.json'
S3_OLD_NOMENCLATURE_PATH_TEMPLATE = 'old_nomenclature/{}'
TEST_DATETIME = '2021-06-02T14:35:44+03:00'
PARTNER_ASSORTMENT_DESTRUCTIVE_ERROR_TYPE = (
    'New partner assortment is potentially destructive'
)
ASSORTMENT_DESTRUCTIVE_ERROR_DETAILS = (
    'New assortment is potentially destructive: '
    '100% of category_products were removed '
    '(prev_assortment_id=4, prev_count=3, new_count=0)'
)
MOCK_NOW = dt.datetime(2021, 8, 13, 12, tzinfo=pytz.UTC)


def settings():
    return {'__default__': {'assortment_remove_limit_in_percent': 50}}


@pytest.mark.config(EATS_NOMENCLATURE_VERIFICATION=settings())
@pytest.mark.parametrize(
    'use_chunked_data',
    [
        pytest.param(False, id='full data'),
        pytest.param(True, id='chunked data'),
    ],
)
@pytest.mark.parametrize(
    'split_old_nomenclature_into_chunks',
    [
        pytest.param(False, id='full old data'),
        pytest.param(True, id='chunked old data'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_insert_nomenclature_to_s3(
        taxi_config,
        stq,
        stq_runner,
        load_json,
        assert_nomenclature_file_in_s3_and_db,
        put_brand_nomenclature_to_s3,
        # parametrize params
        use_chunked_data,
        split_old_nomenclature_into_chunks,
):
    place_id_1 = 1
    place_id_2 = 2
    place_id_3 = 10
    place_ids = [str(place_id_1), str(place_id_2), str(place_id_3)]

    s3_upload_path_root = '/s3/path/nomenclature'
    task_name = 'task_777_hash_3593178067297906555'

    data_to_upload = load_json('s3_brand_nomenclature.json')
    data_to_upload['place_ids'] = place_ids
    data_to_upload.pop('item_modifier_groups', None)

    old_nomenclature_chunk_size = 1
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_BRAND_NOMENCLATURE_PROCESSING': {
                'split_old_nomenclature_into_chunks': (
                    split_old_nomenclature_into_chunks
                ),
                'old_nomenclature_chunk_size': old_nomenclature_chunk_size,
            },
        },
    )

    # Prepare data for processing
    if use_chunked_data:
        category_data_to_upload = {
            'categories': data_to_upload['categories'],
            'items': [],
            'place_ids': data_to_upload['place_ids'],
        }

        item_separator_index = math.floor(len(data_to_upload['items']) / 2)
        item_data_to_upload_1 = {
            'categories': [],
            'items': data_to_upload['items'][:item_separator_index],
            'place_ids': data_to_upload['place_ids'],
        }
        item_data_to_upload_2 = {
            'categories': [],
            'items': data_to_upload['items'][item_separator_index:],
            'place_ids': data_to_upload['place_ids'],
        }

        s3_upload_path = f'{s3_upload_path_root}/{task_name}'
        await put_brand_nomenclature_to_s3(
            category_data_to_upload,
            s3_path=f'{s3_upload_path}/categories/categories.json',
        )
        await put_brand_nomenclature_to_s3(
            item_data_to_upload_1,
            s3_path=f'{s3_upload_path}/items/items_1.json',
        )
        await put_brand_nomenclature_to_s3(
            item_data_to_upload_2,
            s3_path=f'{s3_upload_path}/items/items_2.json',
        )
    else:
        s3_upload_path = f'{s3_upload_path_root}/{task_name}.json'
        await put_brand_nomenclature_to_s3(
            data_to_upload, s3_path=s3_upload_path,
        )

    # Run nomenclature processing
    await stq_runner.eats_nomenclature_brand_processing.call(
        task_id='1',
        args=[],
        kwargs={
            'brand_id': str(BRAND_ID),
            's3_path': s3_upload_path,
            'file_datetime': TEST_DATETIME,
        },
    )

    data_to_upload['place_ids'] = [str(place_id_1), str(place_id_2)]

    # Verify that files were saved to S3 and DB
    expected_file_path = (
        f'old_nomenclature/{task_name}'
        if split_old_nomenclature_into_chunks
        else f'old_nomenclature/{task_name}.json'
    )

    assert_nomenclature_file_in_s3_and_db(
        '1',
        expected_file_path,
        TEST_DATETIME,
        data_to_upload,
        expected_no_file=False,
        split_into_chunks=split_old_nomenclature_into_chunks,
        items_chunk_size=old_nomenclature_chunk_size,
    )

    assert_nomenclature_file_in_s3_and_db(
        '2',
        expected_file_path,
        TEST_DATETIME,
        data_to_upload,
        expected_no_file=False,
        split_into_chunks=split_old_nomenclature_into_chunks,
        items_chunk_size=old_nomenclature_chunk_size,
    )

    assortment_traits = set()
    expected_assortment_traits = {1, 2, 3, None}
    assert stq.eats_nomenclature_transform_assortment.times_called == len(
        expected_assortment_traits,
    )
    while stq.eats_nomenclature_transform_assortment.has_calls:
        task_info = stq.eats_nomenclature_transform_assortment.next_call()
        assert expected_file_path == task_info['kwargs']['assortment_s3_url']
        assert task_info['kwargs']['brand_id'] == BRAND_ID
        trait_id = (
            task_info['kwargs']['trait_id']
            if 'trait_id' in task_info['kwargs']
            else None
        )
        assortment_traits.add(trait_id)
        await stq_runner.eats_nomenclature_transform_assortment.call(
            task_id=task_info['id'], args=[], kwargs=task_info['kwargs'],
        )
    assert assortment_traits == expected_assortment_traits


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.config(EATS_NOMENCLATURE_VERIFICATION=settings())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_destructive_assortment(
        taxi_eats_nomenclature,
        brand_task_enqueue,
        activate_assortment,
        load_json,
        testpoint,
        assert_nomenclature_file_in_s3_and_db,
        get_active_assortment,
        sql_get_place_assortment_proc_last_status,
        sql_get_place_assortment_last_status_history,
):
    place_id = '1'

    @testpoint('assortment-is-potentially-destructive')
    def task_testpoint(param):
        pass

    # Fill old assortment.
    old_data_to_upload = load_json('s3_brand_nomenclature.json')
    await brand_task_enqueue(
        place_id,
        brand_nomenclature=old_data_to_upload,
        file_datetime=TEST_DATETIME,
    )

    new_availabilities = [
        {'origin_id': 'item_origin_4', 'available': True},
        {'origin_id': 'item_origin_5', 'available': True},
        {'origin_id': 'item_origin_6', 'available': True},
    ]
    new_stocks = [
        {'origin_id': 'item_origin_4', 'stocks': None},
        {'origin_id': 'item_origin_5', 'stocks': None},
        {'origin_id': 'item_origin_6', 'stocks': None},
    ]
    new_prices = [
        {'origin_id': 'item_origin_4', 'price': '1000', 'currency': 'RUB'},
        {'origin_id': 'item_origin_5', 'price': '1000', 'currency': 'RUB'},
        {'origin_id': 'item_origin_6', 'price': '1000', 'currency': 'RUB'},
    ]
    await activate_assortment(new_availabilities, new_stocks, new_prices)
    active_assortment = get_active_assortment(place_id)
    last_status = {
        'status': 'processed',
        'assortment_id': active_assortment,
        'task_error': None,
        'task_error_details': None,
        'task_warnings': None,
        'status_or_text_changed_at': MOCK_NOW,
    }
    expected_last_statuses = [last_status]
    assert sql_get_place_assortment_proc_last_status(place_id) == last_status
    assert (
        sql_get_place_assortment_last_status_history(place_id)
        == expected_last_statuses
    )

    # Try upload new nomenclature file.
    data_to_upload = load_json('s3_brand_nomenclature.json')
    data_to_upload['items'] = []
    await brand_task_enqueue(
        place_id,
        brand_nomenclature=data_to_upload,
        file_datetime=TEST_DATETIME,
        expect_fail=True,
    )

    assert task_testpoint.times_called == 1

    assert_nomenclature_file_in_s3_and_db(
        place_id,
        S3_OLD_NOMENCLATURE_PATH,
        TEST_DATETIME,
        old_data_to_upload,
        expected_no_file=False,
    )

    last_status = {
        'assortment_id': None,
        'status': 'failed',
        'task_error': PARTNER_ASSORTMENT_DESTRUCTIVE_ERROR_TYPE,
        'task_error_details': ASSORTMENT_DESTRUCTIVE_ERROR_DETAILS,
        'task_warnings': None,
        'status_or_text_changed_at': MOCK_NOW,
    }
    expected_last_statuses.append(last_status)
    assert sql_get_place_assortment_proc_last_status(place_id) == last_status
    assert (
        sql_get_place_assortment_last_status_history(place_id)
        == expected_last_statuses
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_task_with_not_found_file(pgsql, brand_task_enqueue):
    place_id = 1
    brand_id = 1
    wrong_path = 'wrong_path'
    await brand_task_enqueue(
        task_id='task',
        brand_id=str(brand_id),
        place_ids=[str(place_id)],
        s3_path=wrong_path,
        file_datetime=TEST_DATETIME,
        call_transform_assortment=True,
    )

    assert sql_get_errors(pgsql, place_id=place_id) == (
        'failed',
        'Brand nomenclature file is not found',
        'Brand nomenclature file is not found at path ' + wrong_path,
    )


def sql_get_errors(pgsql, place_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select status, task_error, task_error_details
        from eats_nomenclature.places_processing_last_status_v2
        where place_id = {place_id}
        """,
    )
    return cursor.fetchone()
