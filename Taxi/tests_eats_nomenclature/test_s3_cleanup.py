import datetime as dt
import math


import pytest


MOCK_NOW = '2021-03-04T09:00:00+00:00'
PRICE_FILES_TABLE = 'price_files'
AVAILABILITY_FILES_TABLE = 'availability_files'
STOCK_FILES_TABLE = 'stock_files'
NOMENCLATURE_FILES_TABLE = 'nomenclature_files'
OLD_PRICES_PATH_PREFIX = 'old_prices'
OLD_AVAILABILITY_PATH_PREFIX = 'old_availability'
OLD_STOCKS_PATH_PREFIX = 'old_stocks'
OLD_NOMENCLATURE_PATH_PREFIX = 'old_nomenclature'
PERIODIC_NAME = 's3-cleanup-periodic'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
@pytest.mark.config(
    EATS_NOMENCLATURE_S3_CLEANUP={
        '__default__': {'interval_hours': 24, 'list_batch_size': 500},
    },
)
@pytest.mark.parametrize(
    'path_prefix, table_name',
    [
        (OLD_PRICES_PATH_PREFIX, PRICE_FILES_TABLE),
        (OLD_AVAILABILITY_PATH_PREFIX, AVAILABILITY_FILES_TABLE),
        (OLD_STOCKS_PATH_PREFIX, STOCK_FILES_TABLE),
        (OLD_NOMENCLATURE_PATH_PREFIX, NOMENCLATURE_FILES_TABLE),
    ],
)
async def test_s3_cleanup(
        taxi_eats_nomenclature,
        pgsql,
        testpoint,
        put_entity_file_to_s3,
        mds_s3_storage,
        path_prefix,
        table_name,
):
    @testpoint(f'{PERIODIC_NAME}-finished')
    def finished_testpoint(param):
        pass

    now = dt.datetime.fromisoformat(MOCK_NOW)
    total_files_count = 1200
    places_count = 3

    # before cleanup
    for i in range(1, total_files_count):
        place_id = (i % places_count) + 1
        should_split_into_chunks = (
            path_prefix == OLD_NOMENCLATURE_PATH_PREFIX and i % 2 == 0
        )
        if should_split_into_chunks:
            file_path = f'{path_prefix}/task_{i}'
        else:
            file_path = f'{path_prefix}/task_{i}.json'
        file_datetime = now - dt.timedelta(hours=i)
        await put_entity_file_to_s3(
            path_prefix,
            [],
            file_path,
            place_id,
            file_datetime,
            split_into_chunks=should_split_into_chunks,
        )
        if i in (1, 2, 27):
            # suppose we have only these tasks in db
            _insert_entity_file_in_db(
                pgsql, table_name, place_id, file_path, file_datetime,
            )

    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)

    # after cleanup
    assert finished_testpoint.times_called == 1
    for i in range(1, total_files_count):
        should_split_into_chunks = (
            path_prefix == OLD_NOMENCLATURE_PATH_PREFIX and i % 2 == 0
        )
        if should_split_into_chunks:
            file_path = f'{path_prefix}/task_{i}'
        else:
            file_path = f'{path_prefix}/task_{i}.json'
        if i <= 24 or i == 27:
            # all files younger than 24 hours
            # or that have record in DB should stay
            if should_split_into_chunks:
                assert mds_s3_storage.storage[
                    f'{file_path}/categories/categories.json'
                ].data
                assert mds_s3_storage.storage[
                    f'{file_path}/items/items_1.json'
                ].data
                assert mds_s3_storage.storage[
                    f'{file_path}/items/items_2.json'
                ].data
            else:
                assert mds_s3_storage.storage[file_path].data
        else:
            # all other files should be deleted
            if should_split_into_chunks:
                assert (
                    f'{file_path}/categories/categories.json'
                    not in mds_s3_storage.storage
                )
                assert (
                    f'{file_path}/items/items_1.json'
                    not in mds_s3_storage.storage
                )
                assert (
                    f'{file_path}/items/items_2.json'
                    not in mds_s3_storage.storage
                )
            else:
                assert file_path not in mds_s3_storage.storage


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
@pytest.mark.config(
    EATS_NOMENCLATURE_S3_CLEANUP={
        '__default__': {'interval_hours': 24, 'list_batch_size': 500},
    },
)
@pytest.mark.parametrize(
    'path_prefix, table_name, should_split_into_chunks',
    [
        (OLD_PRICES_PATH_PREFIX, PRICE_FILES_TABLE, False),
        (OLD_AVAILABILITY_PATH_PREFIX, AVAILABILITY_FILES_TABLE, False),
        (OLD_STOCKS_PATH_PREFIX, STOCK_FILES_TABLE, False),
        (OLD_NOMENCLATURE_PATH_PREFIX, NOMENCLATURE_FILES_TABLE, False),
        (OLD_NOMENCLATURE_PATH_PREFIX, NOMENCLATURE_FILES_TABLE, True),
    ],
)
async def test_delete_non_existing_file(
        taxi_eats_nomenclature,
        pgsql,
        testpoint,
        put_entity_file_to_s3,
        mds_s3_storage,
        # parametrize params
        path_prefix,
        table_name,
        should_split_into_chunks,
):
    now = dt.datetime.fromisoformat(MOCK_NOW)
    place_id = 1
    if (
            path_prefix == OLD_NOMENCLATURE_PATH_PREFIX
            and should_split_into_chunks
    ):
        file_path_1 = f'{path_prefix}/task_1'
        file_path_2 = f'{path_prefix}/task_2'
        file_path_3 = f'{path_prefix}/task_3'
        file_path_4 = f'{path_prefix}/task_4'
    else:
        file_path_1 = f'{path_prefix}/task_1.json'
        file_path_2 = f'{path_prefix}/task_2.json'
        file_path_3 = f'{path_prefix}/task_3.json'
        file_path_4 = f'{path_prefix}/task_4.json'
    file_datetime = now - dt.timedelta(hours=25)

    # existing file, will be deleted
    await put_entity_file_to_s3(
        path_prefix,
        [],
        file_path_1,
        place_id,
        file_datetime,
        split_into_chunks=should_split_into_chunks,
    )
    # non-existing file (will be deleted before delete request)
    await put_entity_file_to_s3(
        path_prefix,
        [],
        file_path_2,
        place_id,
        file_datetime,
        split_into_chunks=should_split_into_chunks,
    )
    # existing file, won't be deleted because of datetime
    await put_entity_file_to_s3(
        path_prefix,
        [],
        file_path_3,
        place_id,
        now - dt.timedelta(hours=1),
        split_into_chunks=should_split_into_chunks,
    )
    # existing file, won't be deleted because it has record in DB
    await put_entity_file_to_s3(
        path_prefix,
        [],
        file_path_4,
        place_id,
        file_datetime,
        split_into_chunks=should_split_into_chunks,
    )
    _insert_entity_file_in_db(
        pgsql, table_name, place_id, file_path_4, file_datetime,
    )

    @testpoint(f'{PERIODIC_NAME}-before-delete')
    def before_delete_testpoint(param):
        if param['file_path'].startswith(file_path_2):
            mds_s3_storage.delete_object(param['file_path'])

    @testpoint(f'{PERIODIC_NAME}-delete-files')
    def delete_files_testpoint(param):
        pass

    @testpoint(f'{PERIODIC_NAME}-finished')
    def finished_testpoint(param):
        pass

    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)

    assert finished_testpoint.times_called == 1
    assert delete_files_testpoint.times_called == 1
    delete_result = delete_files_testpoint.next_call()

    if (
            path_prefix == OLD_NOMENCLATURE_PATH_PREFIX
            and should_split_into_chunks
    ):
        assert before_delete_testpoint.times_called == 6
        # both folders are mentioned by s3 as deleted
        # though only one is really existing and was deleted
        assert delete_result['param'] == {'deleted': 6, 'failed': 0}
    else:
        assert before_delete_testpoint.times_called == 2
        # both files are mentioned by s3 as deleted
        # though only one is really existing and was deleted
        assert delete_result['param'] == {'deleted': 2, 'failed': 0}

    if (
            path_prefix == OLD_NOMENCLATURE_PATH_PREFIX
            and should_split_into_chunks
    ):
        assert (
            f'{file_path_1}/categories/categories.json'
            not in mds_s3_storage.storage
        )
        assert (
            f'{file_path_1}/items/items_1.json' not in mds_s3_storage.storage
        )
        assert (
            f'{file_path_1}/items/items_2.json' not in mds_s3_storage.storage
        )
        assert (
            f'{file_path_2}/categories/categories.json'
            not in mds_s3_storage.storage
        )
        assert (
            f'{file_path_2}/items/items_1.json' not in mds_s3_storage.storage
        )
        assert (
            f'{file_path_2}/items/items_2.json' not in mds_s3_storage.storage
        )
        assert mds_s3_storage.storage[
            f'{file_path_3}/categories/categories.json'
        ].data
        assert mds_s3_storage.storage[f'{file_path_3}/items/items_1.json'].data
        assert mds_s3_storage.storage[f'{file_path_3}/items/items_2.json'].data
        assert mds_s3_storage.storage[
            f'{file_path_4}/categories/categories.json'
        ].data
        assert mds_s3_storage.storage[f'{file_path_4}/items/items_1.json'].data
        assert mds_s3_storage.storage[f'{file_path_4}/items/items_2.json'].data
    else:
        assert file_path_1 not in mds_s3_storage.storage
        assert file_path_2 not in mds_s3_storage.storage
        assert mds_s3_storage.storage[file_path_3].data
        assert mds_s3_storage.storage[file_path_4].data


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
@pytest.mark.parametrize('max_files_to_delete', [1, 100, 1000])
async def test_s3_cleanup_max_files_to_delete(
        taxi_eats_nomenclature,
        taxi_config,
        testpoint,
        put_entity_file_to_s3,
        # parametrize
        max_files_to_delete,
):
    path_prefix = OLD_PRICES_PATH_PREFIX
    time_to_delete_after_in_hours = 24
    now = dt.datetime.fromisoformat(MOCK_NOW)
    total_files_count = 150
    places_count = 3

    taxi_config.set(
        EATS_NOMENCLATURE_S3_CLEANUP={
            '__default__': {
                'interval_hours': time_to_delete_after_in_hours,
                'max_files_to_delete': max_files_to_delete,
                'list_batch_size': 500,
            },
        },
    )

    @testpoint(f'{PERIODIC_NAME}-before-delete')
    def before_delete_testpoint(param):
        pass

    @testpoint(f'{PERIODIC_NAME}-finished')
    def finished_testpoint(param):
        pass

    for i in range(1, total_files_count + 1):
        place_id = (i % places_count) + 1
        file_path = f'{path_prefix}/task_{i}.json'
        file_datetime = now - dt.timedelta(
            hours=(time_to_delete_after_in_hours + i),
        )
        await put_entity_file_to_s3(
            path_prefix,
            [],
            file_path,
            place_id,
            file_datetime,
            split_into_chunks=False,
        )

    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)

    assert finished_testpoint.times_called == 1
    assert before_delete_testpoint.times_called == min(
        max_files_to_delete, total_files_count,
    )


async def test_periodic_metrics(mds_s3_storage, verify_periodic_metrics):
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


@pytest.fixture(name='put_entity_file_to_s3')
def _put_entity_file_to_s3(
        load_json,
        put_prices_data_to_s3,
        put_availability_data_to_s3,
        put_stock_data_to_s3,
        put_brand_nomenclature_to_s3,
):
    async def do_put_entity_file_to_s3(
            path_prefix,
            new_items,
            s3_path,
            place_id,
            file_datetime,
            split_into_chunks=False,
    ):
        if path_prefix == OLD_PRICES_PATH_PREFIX:
            await put_prices_data_to_s3(
                new_items, s3_path, place_id, file_datetime,
            )
        elif path_prefix == OLD_AVAILABILITY_PATH_PREFIX:
            await put_availability_data_to_s3(
                new_items, s3_path, place_id, file_datetime,
            )
        elif path_prefix == OLD_STOCKS_PATH_PREFIX:
            await put_stock_data_to_s3(
                new_items, s3_path, place_id, file_datetime,
            )
        else:
            data_to_upload = load_json('s3_brand_nomenclature.json')
            data_to_upload['place_ids'] = [place_id]
            if split_into_chunks:
                category_data_to_upload = {
                    'categories': data_to_upload['categories'],
                    'items': [],
                    'place_ids': data_to_upload['place_ids'],
                }

                item_separator_index = math.floor(
                    len(data_to_upload['items']) / 2,
                )
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

                await put_brand_nomenclature_to_s3(
                    category_data_to_upload,
                    f'{s3_path}/categories/categories.json',
                    file_datetime,
                )
                await put_brand_nomenclature_to_s3(
                    item_data_to_upload_1,
                    f'{s3_path}/items/items_1.json',
                    file_datetime,
                )
                await put_brand_nomenclature_to_s3(
                    item_data_to_upload_2,
                    f'{s3_path}/items/items_2.json',
                    file_datetime,
                )
            else:
                await put_brand_nomenclature_to_s3(
                    data_to_upload, s3_path, file_datetime,
                )

    return do_put_entity_file_to_s3


def _insert_entity_file_in_db(
        pgsql, table_name, place_id, file_path, file_datetime,
):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.{table_name}
        (place_id, file_path, file_datetime)
        values ({place_id}, '{file_path}', '{file_datetime}')
        """,
    )
