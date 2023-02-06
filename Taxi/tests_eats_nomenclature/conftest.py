import base64
import copy
import datetime as dt
import json

import pytest
import pytz

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=too-many-lines
from eats_nomenclature_plugins import *  # noqa: F403 F401

ISO_FORMAT_FOR_TASK_ID = '%Y%m%dT%H%M%S'
ISO_FORMAT_WITH_TZ = '%Y-%m-%dT%H:%M:%S+00:00'

S3_BRAND_NOMENCLATURE_PATH = '/some/path/brand_nomenclature.json'
S3_AVAILABILITY_PATH = 'availability/availability_1.json'
S3_PRICES_PATH = 'prices/prices_1.json'
S3_STOCKS_PATH = 'stocks/stocks_1.json'
TEST_DATETIME = '2021-03-01T10:45:00+03:00'


@pytest.fixture(name='to_utc_datetime')
def _to_utc_datetime():
    def do_to_utc_datetime(stamp):
        if not isinstance(stamp, dt.datetime):
            stamp = dt.datetime.fromisoformat(stamp)
        if stamp.tzinfo is not None:
            stamp = stamp.astimezone(pytz.UTC)
        return stamp

    return do_to_utc_datetime


@pytest.fixture(name='get_cursor')
def _get_cursor(pgsql):
    def create_cursor():
        return pgsql['eats_nomenclature'].dict_cursor()

    return create_cursor


@pytest.fixture(name='brand_task_enqueue')
def _brand_task_enqueue(
        stq_runner,
        stq,
        stq_call_forward,
        put_brand_nomenclature_to_s3,
        load_json,
):
    async def enqueue(
            task_id='1',
            brand_id='777',
            s3_path=S3_BRAND_NOMENCLATURE_PATH,
            file_datetime=TEST_DATETIME,
            place_ids=None,
            brand_nomenclature=None,
            expect_fail=False,
            call_transform_assortment=True,
    ):
        if not brand_nomenclature:
            brand_nomenclature = load_json('s3_brand_nomenclature.json')

        task_kwargs = {
            'brand_id': brand_id,
            's3_path': s3_path,
            'file_datetime': file_datetime,
        }

        if place_ids is not None:
            brand_nomenclature['place_ids'] = place_ids
            task_kwargs['place_ids'] = place_ids
        elif 'place_ids' not in brand_nomenclature:
            brand_nomenclature['place_ids'] = ['1']

        await put_brand_nomenclature_to_s3(brand_nomenclature, s3_path=s3_path)
        await stq_runner.eats_nomenclature_brand_processing.call(
            task_id=task_id,
            args=[],
            kwargs=task_kwargs,
            expect_fail=expect_fail,
        )
        if call_transform_assortment:
            times_called = (
                stq.eats_nomenclature_transform_assortment.times_called
            )
            for _ in range(times_called):
                task_info = (
                    stq.eats_nomenclature_transform_assortment.next_call()
                )
                await stq_call_forward(task_info)

    return enqueue


@pytest.fixture(name='upload_verified_nomenclature_to_s3')
def _upload_verified_nomenclature_to_s3(brand_task_enqueue):
    async def upload(
            task_id='1',
            brand_id='777',
            s3_path=S3_BRAND_NOMENCLATURE_PATH,
            file_datetime=TEST_DATETIME,
            place_ids=None,
            brand_nomenclature=None,
            expect_fail=False,
    ):
        # eats_nomenclature_brand_processing verifies and
        # uploads nomenclature to s3 and after that
        # it calls transform_assortment.
        # This method will only upload verified nomenclature to db.
        await brand_task_enqueue(
            task_id=task_id,
            brand_id=brand_id,
            place_ids=place_ids,
            file_datetime=file_datetime,
            s3_path=s3_path,
            brand_nomenclature=brand_nomenclature,
            expect_fail=expect_fail,
            call_transform_assortment=False,
        )

    return upload


@pytest.fixture(name='put_brand_nomenclature_to_s3_and_db', autouse=True)
def _put_brand_nomenclature_to_s3_and_db(
        stq_runner, stq, put_brand_nomenclature_to_s3, load_json, pgsql,
):
    async def put_to_s3_and_db(place_ids=None, brand_nomenclature=None):
        if not brand_nomenclature:
            brand_nomenclature = load_json('s3_brand_nomenclature.json')

        if place_ids:
            brand_nomenclature['place_ids'] = place_ids
        elif 'place_ids' not in brand_nomenclature:
            brand_nomenclature['place_ids'] = ['1']

        await put_brand_nomenclature_to_s3(brand_nomenclature)

    return put_to_s3_and_db


@pytest.fixture(name='task_enqueue_v2')
def _task_enqueue_v2(
        stq_runner,
        stq,
        stq_call_forward,
        put_brand_nomenclature_to_s3,
        load_json,
):
    async def enqueue(queue, **kwargs):
        if queue == 'eats_nomenclature_brand_processing':
            if 'brand_nomenclature' not in kwargs:
                brand_nomenclature = load_json('s3_brand_nomenclature.json')
            else:
                brand_nomenclature = kwargs['brand_nomenclature']
            await put_brand_nomenclature_to_s3(brand_nomenclature)
            if 'kwargs' not in kwargs:
                kwargs['kwargs'] = {
                    'brand_id': '777',
                    's3_path': S3_BRAND_NOMENCLATURE_PATH,
                    'file_datetime': TEST_DATETIME,
                }
        elif queue == 'eats_nomenclature_edadeal_s3_uploader':
            brand_id = 777
            if 'kwargs' not in kwargs:
                kwargs['kwargs'] = {}
            if 'brand_id' not in kwargs['kwargs']:
                kwargs['kwargs']['brand_id'] = brand_id
            kwargs['task_id'] = str(kwargs['kwargs']['brand_id'])
            kwargs['kwargs']['upload_task_id'] = str(
                kwargs['kwargs']['brand_id'],
            )
        elif queue == 'eats_nomenclature_add_custom_assortment':
            if 'kwargs' not in kwargs:
                kwargs['kwargs'] = {'assortment_id': 1}
            kwargs['kwargs']['upload_task_id'] = kwargs['task_id']
        elif queue == 'eats_nomenclature_edadeal_tags_processing':
            task_id = int(kwargs['task_id'])
            kwargs['task_id'] = f'tags_processing_{task_id}'
            if 'kwargs' not in kwargs:
                kwargs['kwargs'] = {}
            kwargs['kwargs']['import_task_id'] = task_id
        elif queue == 'eats_nomenclature_edadeal_skus_processing':
            task_id = int(kwargs['task_id'])
            kwargs['task_id'] = f'skus_processing_{task_id}'
            if 'kwargs' not in kwargs:
                kwargs['kwargs'] = {}
            kwargs['kwargs']['import_task_id'] = task_id
        elif queue == 'eats_nomenclature_edadeal_yt_skus_processing':
            if 'force_update' not in kwargs['kwargs']:
                kwargs['kwargs']['force_update'] = False
            yt_path = kwargs['kwargs']['skus_yt_path']
            kwargs['task_id'] = f'{yt_path[:20]}'
        elif queue == 'eats_nomenclature_transform_assortment':
            if 'kwargs' not in kwargs:
                kwargs['kwargs'] = {
                    'assortment_s3_url': S3_BRAND_NOMENCLATURE_PATH,
                    'brand_id': 777,
                }
            kwargs['kwargs']['upload_task_id'] = kwargs['task_id']
        elif queue == 'eats_nomenclature_update_stocks':
            if 'kwargs' not in kwargs:
                kwargs['kwargs'] = {
                    'place_id': '1',
                    's3_path': 'some/path/stocks.json',
                    'file_datetime': TEST_DATETIME,
                }
            kwargs['kwargs']['upload_task_id'] = kwargs['task_id']
        elif queue == 'eats_nomenclature_update_prices':
            if 'kwargs' not in kwargs:
                kwargs['kwargs'] = {
                    'place_id': '1',
                    's3_path': S3_PRICES_PATH,
                    'file_datetime': TEST_DATETIME,
                }
            kwargs['kwargs']['upload_task_id'] = kwargs['task_id']
        elif queue == 'eats_nomenclature_update_availability':
            if 'kwargs' not in kwargs:
                kwargs['kwargs'] = {
                    'place_id': '1',
                    's3_path': 'some/path/availabilities.json',
                    'file_datetime': TEST_DATETIME,
                }
            kwargs['kwargs']['upload_task_id'] = kwargs['task_id']
        elif queue == 'eats_nomenclature_market_yt_full_place_products_sync':
            if 'kwargs' not in kwargs:
                kwargs['kwargs'] = {'place_id': '1'}
        elif queue == 'eats_nomenclature_market_yt_products_sync':
            if 'kwargs' not in kwargs:
                kwargs['kwargs'] = {'brand_id': '1'}

        if 'reschedule_counter' in kwargs:
            if 'exec_tries' not in kwargs:
                kwargs['exec_tries'] = kwargs['reschedule_counter']
            # exec_tries = reschedule_count + error_count
            assert kwargs['exec_tries'] >= kwargs['reschedule_counter']

        await getattr(stq_runner, queue).call(**kwargs)

        if queue == 'eats_nomenclature_brand_processing':
            times_called = (
                stq.eats_nomenclature_transform_assortment.times_called
            )
            for _ in range(times_called):
                task_info = (
                    stq.eats_nomenclature_transform_assortment.next_call()
                )
                await stq_call_forward(task_info)

    return enqueue


@pytest.fixture(name='stq_call_forward')
def _stq_call_forward(stq_runner):
    async def forward(stq_next_call, expect_fail=False):
        await getattr(stq_runner, stq_next_call['queue']).call(
            task_id=stq_next_call['id'],
            args=stq_next_call['args'],
            kwargs=stq_next_call['kwargs'],
            expect_fail=expect_fail,
        )

    return forward


@pytest.fixture(name='add_category_public_id_by_name')
def _add_category_public_id_by_name(pgsql):
    def do_add(category_public_id=1, category_name='category_1'):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            insert into eats_nomenclature.categories_dictionary(id, name)
            values ({category_public_id}, '{category_name}')
            on conflict do nothing
            """,
        )
        cursor.execute(
            f"""
            update eats_nomenclature.categories
            set public_id = {category_public_id}
            where name = '{category_name}'
            """,
        )

    return do_add


@pytest.fixture(name='sql_set_place_busy')
def _sql_set_place_busy(pgsql):
    def do_sql_set_place_busy(
            place_update_status_prefix, place_id, time_difference_in_ms=0,
    ):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            insert into eats_nomenclature.place_update_statuses
                (
                    place_id,
                    {place_update_status_prefix}_update_started_at,
                    {place_update_status_prefix}_update_in_progress
                )
                values (
                    {place_id},
                    now() - interval
                    '{int(time_difference_in_ms / 1000)} second',
                    true
                )
            on conflict (place_id) do update
            set
              {place_update_status_prefix}_update_in_progress =
                excluded.{place_update_status_prefix}_update_in_progress,
              {place_update_status_prefix}_update_started_at =
                excluded.{place_update_status_prefix}_update_started_at,
              updated_at = now()
            where eats_nomenclature.place_update_statuses.place_id = {place_id}
            """,
        )

    return do_sql_set_place_busy


@pytest.fixture(name='sql_is_place_busy')
def _sql_is_place_busy(pgsql):
    def do_sql_is_place_busy(place_update_status_prefix, place_id):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select {place_update_status_prefix}_update_in_progress
            from eats_nomenclature.place_update_statuses
            where place_id = {place_id}
            """,
        )
        return list(cursor)[0][0]

    return do_sql_is_place_busy


@pytest.fixture(name='sql_set_assortment_busy')
def _sql_set_assortment_busy(pgsql):
    def do_sql_set_assortment_busy(assortment_id, time_difference_in_min=0):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            insert into eats_nomenclature.assortment_enrichment_statuses (
                assortment_id,
                are_custom_categories_ready,
                enrichment_started_at
            )
            values (
                '{assortment_id}',
                false,
                now() - interval
                '{time_difference_in_min * 60} second'
            )
            on conflict (assortment_id)
            do update set
            are_custom_categories_ready = excluded.are_custom_categories_ready,
            enrichment_started_at = excluded.enrichment_started_at;
            """,
        )

    return do_sql_set_assortment_busy


@pytest.fixture(name='sql_is_assortment_busy')
def _sql_is_assortment_busy(pgsql):
    def do_sql_is_assortment_busy(
            assortment_id, assortment_enrichment_timeout_in_min,
    ):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select 1
            from eats_nomenclature.assortment_enrichment_statuses aes
            join eats_nomenclature.place_assortments pa
                on pa.in_progress_assortment_id = aes.assortment_id
            where aes.assortment_id = {assortment_id}
              and aes.enrichment_started_at > now()
                - interval '{assortment_enrichment_timeout_in_min} minutes'
            """,
        )
        result = list(cursor)
        return result and result[0][0]

    return do_sql_is_assortment_busy


@pytest.fixture(name='activate_assortment')
def _activate_assortment(
        availability_enqueue,
        prices_enqueue,
        put_availability_data_to_s3,
        put_prices_data_to_s3,
        put_stock_data_to_s3,
        stq,
        stq_call_forward,
        stocks_enqueue,
):
    async def activate(
            availabilities,
            stocks,
            prices,
            place_id=1,
            task_id='1',
            trait_id=None,
            expect_partner_fail=False,
            expect_custom_fail=False,
    ):
        assert stq.eats_nomenclature_add_custom_assortment.has_calls is True
        times_called = stq.eats_nomenclature_add_custom_assortment.times_called
        for _ in range(times_called):
            task_info = stq.eats_nomenclature_add_custom_assortment.next_call()
            stq_trait_id = (
                task_info['kwargs']['trait_id']
                if 'trait_id' in task_info['kwargs']
                else None
            )
            if stq_trait_id == trait_id:
                await stq_call_forward(task_info, expect_custom_fail)
            elif stq_trait_id is None:
                await stq_call_forward(task_info, expect_partner_fail)

        await put_availability_data_to_s3(
            availabilities, S3_AVAILABILITY_PATH, str(place_id),
        )
        await availability_enqueue(
            place_id, S3_AVAILABILITY_PATH, TEST_DATETIME, task_id,
        )

        await put_prices_data_to_s3(prices, S3_PRICES_PATH, str(place_id))
        await prices_enqueue(place_id, S3_PRICES_PATH, TEST_DATETIME, task_id)

        await put_stock_data_to_s3(stocks, S3_STOCKS_PATH, str(place_id))
        await stocks_enqueue(place_id, S3_STOCKS_PATH, TEST_DATETIME, task_id)

    return activate


@pytest.fixture(name='sql_mark_assortment_in_progress')
def _sql_mark_assortment_in_progress(pgsql):
    def do_mark_assortment_in_progress(
            assortment_id,
            enrichment_started_at=None,
            are_custom_categories_ready=False,
    ):
        if not enrichment_started_at:
            enrichment_started_at = dt.datetime.now()

        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            insert into eats_nomenclature.assortment_enrichment_statuses (
                assortment_id,
                enrichment_started_at,
                are_custom_categories_ready
            )
            values (
                {assortment_id},
                '{enrichment_started_at}',
                {are_custom_categories_ready}
            )
            on conflict (assortment_id)
            do update set
            enrichment_started_at = excluded.enrichment_started_at,
            are_custom_categories_ready = excluded.are_custom_categories_ready
            """,
        )

    return do_mark_assortment_in_progress


@pytest.fixture(name='sql_is_in_progress')
def _sql_is_in_progress(pgsql):
    def do_sql_is_in_progress(assortment_id):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select 1
            from eats_nomenclature.assortment_enrichment_statuses aes
            join eats_nomenclature.place_assortments pa
              on pa.in_progress_assortment_id = aes.assortment_id
            where aes.assortment_id = {assortment_id}
            """,
        )
        result = list(cursor)
        return result and result[0][0]

    return do_sql_is_in_progress


@pytest.fixture(name='sql_get_enrichment_status')
def _sql_get_enrichment_status(pgsql):
    def do_sql_get_enrichment_status(assortment_id):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select
                case when pa.in_progress_assortment_id is not null
                    then true else false end,
                aes.are_custom_categories_ready,
                aes.enrichment_started_at
            from eats_nomenclature.assortment_enrichment_statuses aes
            left join eats_nomenclature.place_assortments pa
              on pa.in_progress_assortment_id = aes.assortment_id
            where aes.assortment_id={assortment_id}
            """,
        )
        return list(cursor)[0]

    return do_sql_get_enrichment_status


@pytest.fixture(name='renew_in_progress_assortment')
def _renew_in_progress_assortment(pgsql):
    def do_renew_in_progress_assortment(place_id):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
                insert into eats_nomenclature.assortments
                default values
                returning id;
                """,
        )
        assortment_id = list(cursor)[0][0]
        cursor.execute(
            f"""
            insert into eats_nomenclature.place_assortments
            (place_id, in_progress_assortment_id)
            values ({place_id}, {assortment_id})
            on conflict (place_id, coalesce(trait_id, -1)) do update
            set
                in_progress_assortment_id = excluded.in_progress_assortment_id,
                updated_at = now();
            """,
        )
        return assortment_id

    return do_renew_in_progress_assortment


@pytest.fixture(name='insert_enrichment_status')
def _insert_enrichment_status(pgsql):
    def do_insert_enrichment_status(
            assortment_id,
            enrichment_started_at,
            are_custom_categories_ready=False,
    ):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            insert into eats_nomenclature.assortment_enrichment_statuses(
                assortment_id,
                enrichment_started_at,
                are_custom_categories_ready
            )
            values (
                '{assortment_id}',
                '{enrichment_started_at}',
                '{are_custom_categories_ready}'
            )
            on conflict (assortment_id) do update
            set
            enrichment_started_at = excluded.enrichment_started_at,
            are_custom_categories_ready = excluded.are_custom_categories_ready,
            updated_at = now();
            """,
        )

    return do_insert_enrichment_status


@pytest.fixture(name='get_sql_assortments_status')
def _get_sql_assortments_status(pgsql):
    def do_get_sql_assortments_status(place_id, trait_id=None):
        cursor = pgsql['eats_nomenclature'].cursor()
        trait_id_condition = (
            f'trait_id = {trait_id}' if trait_id else 'trait_id is null'
        )
        cursor.execute(
            f"""
            select place_id, assortment_id, in_progress_assortment_id
            from eats_nomenclature.place_assortments
            where place_id = {place_id} and {trait_id_condition}
            """,
        )
        row = list(cursor)[0]
        return {
            'place_id': row[0],
            'assortment_id': row[1],
            'in_progress_assortment_id': row[2],
        }

    return do_get_sql_assortments_status


@pytest.fixture(name='get_in_progress_assortment')
def _get_in_progress_assortment(pgsql):
    def do_get_in_progress_assortment(
            place_id, check_aes=False, trait_id=None,
    ):
        cursor = pgsql['eats_nomenclature'].cursor()
        trait_id_condition = (
            f'pa.trait_id = {trait_id}' if trait_id else 'trait_id is null'
        )
        if check_aes:
            cursor.execute(
                f"""
                select pa.in_progress_assortment_id
                from eats_nomenclature.place_assortments pa
                join eats_nomenclature.assortment_enrichment_statuses aes
                  on pa.in_progress_assortment_id = aes.assortment_id
                where pa.place_id = {place_id}
                  and {trait_id_condition}
                """,
            )
            result = list(cursor)
        else:
            cursor.execute(
                f"""
                select in_progress_assortment_id
                from eats_nomenclature.place_assortments pa
                where pa.place_id = {place_id} and {trait_id_condition}
                """,
            )
            result = list(cursor)
        if result:
            return result[0][0]
        return None

    return do_get_in_progress_assortment


@pytest.fixture(name='get_active_assortment')
def _get_active_assortment(pgsql):
    def do_get_active_assortment(place_id, trait_id=None):
        cursor = pgsql['eats_nomenclature'].cursor()
        trait_id_condition = (
            f'trait_id = {trait_id}' if trait_id else 'trait_id is null'
        )
        cursor.execute(
            f"""
            select assortment_id
            from eats_nomenclature.place_assortments
            where place_id = {place_id} and {trait_id_condition}
            """,
        )
        return list(cursor)[0][0]

    return do_get_active_assortment


@pytest.fixture(name='get_active_assortments')
def _get_active_assortments(pgsql):
    def do_get_active_assortments(place_id):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select assortment_id
            from eats_nomenclature.place_assortments
            where place_id = {place_id}
            """,
        )
        return [row[0] for row in list(cursor)]

    return do_get_active_assortments


@pytest.fixture(name='sql_update_all_places_categories')
def _sql_update_all_places_categories(pgsql):
    def do_smth(place_id, value):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            update eats_nomenclature.places_categories
            set active_items_count = {value}
            where place_id = {place_id}""",
        )

    return do_smth


@pytest.fixture(name='complete_enrichment_status')
def _complete_enrichment_status(pgsql, get_in_progress_assortment):
    def complete(place_id, options=None):
        if not options:
            options = {}

        set_custom_assortment = options.get('custom_assortment', True)
        set_availabilities = options.get('availabilities', True)
        set_stocks = options.get('stocks', True)
        set_prices = options.get('prices', True)

        in_progress_assortment_id = get_in_progress_assortment(place_id, True)

        _sql_complete_place_enrichment_status(
            pgsql,
            place_id,
            are_availabilities_ready=set_availabilities,
            are_stocks_ready=set_stocks,
            are_prices_ready=set_prices,
        )
        _sql_complete_assortment_enrichment_status(
            pgsql,
            in_progress_assortment_id,
            are_custom_categories_ready=set_custom_assortment,
        )

    return complete


@pytest.fixture(name='put_brand_nomenclature_to_s3')
def _put_brand_nomenclature_to_s3(mds_s3_storage):
    async def put(
            brand_nomenclature,
            s3_path=S3_BRAND_NOMENCLATURE_PATH,
            last_modified=None,
    ):
        mds_s3_storage.put_object(
            s3_path,
            json.dumps(brand_nomenclature).encode('utf-8'),
            last_modified,
        )

    return put


@pytest.fixture(name='put_availability_data_to_s3')
def _put_availability_data_to_s3(mds_s3_storage):
    async def put(
            new_availabilities,
            s3_path=S3_AVAILABILITY_PATH,
            place_id=1,
            last_modified=None,
    ):
        data = {
            'place_id': str(place_id),
            'items': new_availabilities,
            'modifiers': [],
        }
        mds_s3_storage.put_object(
            s3_path, json.dumps(data).encode('utf-8'), last_modified,
        )

    return put


@pytest.fixture(name='put_prices_data_to_s3')
def _put_prices_data_to_s3(mds_s3_storage):
    async def put(
            new_prices,
            s3_path=S3_PRICES_PATH,
            place_id='1',
            last_modified=None,
    ):
        data = {
            'place_id': str(place_id),
            'items': new_prices,
            'modifiers': [],
        }
        mds_s3_storage.put_object(
            s3_path, json.dumps(data).encode('utf-8'), last_modified,
        )

    return put


@pytest.fixture(name='put_stock_data_to_s3')
def _put_stock_data_to_s3(mds_s3_storage):
    async def put(
            new_stocks, s3_path=S3_STOCKS_PATH, place_id=1, last_modified=None,
    ):
        data = {
            'place_id': str(place_id),
            'items': new_stocks,
            'modifiers': [],
        }
        mds_s3_storage.put_object(
            s3_path, json.dumps(data).encode('utf-8'), last_modified,
        )

    return put


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


@pytest.fixture(name='assert_entity_file_in_s3_and_db')
def _assert_entity_file_in_s3_and_db(
        pg_realdict_cursor, mds_s3_storage, to_utc_datetime,
):
    def do_assert_entity_file(
            table_name,
            place_id,
            expected_file_path=None,
            expected_file_datetime=None,
            expected_file_items=None,
            expect_no_file=False,
    ):
        if expected_file_items is None:
            expected_file_items = []

        cursor = pg_realdict_cursor
        cursor.execute(
            f"""
            select place_id, file_path, file_datetime
            from eats_nomenclature.{table_name}
            where place_id = {place_id}
            """,
        )
        result = cursor.fetchall()
        if expect_no_file:
            assert not result
            return

        assert result
        row = result[0]
        assert row['file_path'] == expected_file_path
        assert row['file_datetime'] == to_utc_datetime(expected_file_datetime)

        result_json = json.loads(
            mds_s3_storage.storage[expected_file_path].data,
        )

        assert result_json['place_id'] == str(place_id)
        assert result_json['items'] == expected_file_items

    return do_assert_entity_file


@pytest.fixture(name='assert_price_file_in_s3_and_db')
def _assert_price_file_in_s3_and_db(assert_entity_file_in_s3_and_db):
    def do_assert_price_file(
            place_id,
            expected_file_path=None,
            expected_file_datetime=None,
            expected_file_prices=None,
            expect_no_file=False,
    ):
        assert_entity_file_in_s3_and_db(
            'price_files',
            place_id,
            expected_file_path,
            expected_file_datetime,
            expected_file_prices,
            expect_no_file,
        )

    return do_assert_price_file


@pytest.fixture(name='assert_nomenclature_file_in_s3_and_db')
def _assert_nomenclature_file_in_s3_and_db(
        pgsql,
        to_utc_datetime,
        mds_s3_storage,
        get_nomenclature_with_chunks_from_s3,
):
    def do_assert_nomenclature_file(
            place_id,
            expected_file_path=None,
            expected_file_datetime=None,
            expected_file_data=None,
            expected_no_file=True,
            split_into_chunks=False,
            items_chunk_size=None,
    ):
        def sorted_json_data(data):
            data['items'] = sorted(
                data['items'], key=lambda item: item['origin_id'],
            )
            return data

        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
                    select place_id, file_path, file_datetime
                    from eats_nomenclature.nomenclature_files
                    where place_id = {place_id}
                    """,
        )

        result = list(cursor)
        if expected_no_file:
            assert result == []
            return

        row = result[0]
        result_file_path = row[1]
        assert expected_file_path == result_file_path
        assert row[2] == to_utc_datetime(expected_file_datetime)

        if split_into_chunks:
            result_json = get_nomenclature_with_chunks_from_s3(
                result_file_path, items_chunk_size=items_chunk_size,
            )
        else:
            result_json = json.loads(
                mds_s3_storage.storage[result_file_path].data,
            )
        # don't modify argument
        sorted_expected_file_data = copy.deepcopy(expected_file_data)

        assert sorted_json_data(result_json) == sorted_json_data(
            sorted_expected_file_data,
        )

    return do_assert_nomenclature_file


@pytest.fixture(name='assert_stock_file_in_s3_and_db')
def _assert_stock_file_in_s3_and_db(assert_entity_file_in_s3_and_db):
    def do_assert_stock_file(
            place_id,
            expected_file_path=None,
            expected_file_datetime=None,
            expected_file_stocks=None,
            expect_no_file=False,
    ):
        assert_entity_file_in_s3_and_db(
            'stock_files',
            place_id,
            expected_file_path,
            expected_file_datetime,
            expected_file_stocks,
            expect_no_file,
        )

    return do_assert_stock_file


@pytest.fixture(name='assert_entities_stq_task')
def _assert_entities_stq_task(
        assert_entity_file_in_s3_and_db, to_utc_datetime,
):
    def do_assert_entities_stq_task(
            entity_prefix,
            task_info,
            expected_place_id,
            expected_file_path,
            expected_file_datetime,
            expected_file_items,
            call_at,
    ):
        dt_for_task_id = to_utc_datetime(expected_file_datetime).strftime(
            ISO_FORMAT_FOR_TASK_ID,
        )
        assert (
            task_info['id']
            == f'{entity_prefix}_{expected_place_id}_{dt_for_task_id}'
        )
        assert task_info['kwargs']['place_id'] == str(expected_place_id)
        assert task_info['kwargs']['s3_path'] == expected_file_path
        assert task_info['kwargs']['file_datetime'] == to_utc_datetime(
            expected_file_datetime,
        ).strftime(ISO_FORMAT_WITH_TZ)

        if call_at:
            call_at = call_at.replace(tzinfo=None)
            assert (
                call_at <= task_info['eta'] < call_at + dt.timedelta(minutes=1)
            )

        assert_entity_file_in_s3_and_db(
            f'{entity_prefix}_files',
            expected_place_id,
            expected_file_path,
            expected_file_datetime,
            expected_file_items,
        )

    return do_assert_entities_stq_task


@pytest.fixture(name='assert_and_call_entity_task')
def _assert_and_call_entity_task(assert_entities_stq_task, stq_call_forward):
    async def do_assert_and_call_entity_task(
            entity_prefix,
            processing_queue,
            place_id,
            expected_file_path,
            expected_file_datetime=TEST_DATETIME,
            expected_file_items=None,
            call_at=None,
    ):
        task_info = processing_queue.next_call()
        assert_entities_stq_task(
            entity_prefix=entity_prefix,
            task_info=task_info,
            expected_place_id=place_id,
            expected_file_path=expected_file_path,
            expected_file_datetime=expected_file_datetime,
            expected_file_items=expected_file_items,
            call_at=call_at,
        )
        await stq_call_forward(task_info)

    return do_assert_and_call_entity_task


@pytest.fixture(name='get_s3_availabilities_from')
def _get_s3_availabilities_from():
    def do_get_s3_availabilities_from(availabilities):
        now_ts = int(dt.datetime.now().timestamp())
        s3_availabilities = []
        for item in availabilities:
            available = False
            if item['available_from'] and item['available_from'] < now_ts:
                available = True
            s3_availabilities.append(
                {'origin_id': item['item_origin_id'], 'available': available},
            )
        return s3_availabilities

    return do_get_s3_availabilities_from


@pytest.fixture(name='get_s3_stocks_from')
def _get_s3_stocks_from():
    def do_get_s3_stocks_from(stocks):
        s3_stocks = []
        for item in stocks:
            result_item = {'origin_id': item['item_origin_id']}
            if 'value' in item and item['value']:
                result_item['stocks'] = str(item['value'])
            s3_stocks.append(result_item)
        return s3_stocks

    return do_get_s3_stocks_from


@pytest.fixture(name='availability_enqueue')
def _availability_enqueue(stq_runner):
    async def do_availability_enqueue(
            place_id=1,
            s3_path=S3_AVAILABILITY_PATH,
            file_datetime=TEST_DATETIME,
            task_id='1',
            expect_fail=False,
    ):
        await stq_runner.eats_nomenclature_update_availability.call(
            task_id=task_id,
            args=[],
            kwargs={
                'place_id': str(place_id),
                's3_path': s3_path,
                'file_datetime': file_datetime,
            },
            expect_fail=expect_fail,
        )

    return do_availability_enqueue


@pytest.fixture(name='stock_enqueue')
def _stock_enqueue(stq_runner):
    async def impl(
            place_id=1,
            s3_path=S3_STOCKS_PATH,
            file_datetime=TEST_DATETIME,
            task_id='1',
            expect_fail=False,
    ):
        await stq_runner.eats_nomenclature_update_stocks.call(
            task_id=task_id,
            args=[],
            kwargs={
                's3_path': s3_path,
                'place_id': str(place_id),
                'file_datetime': file_datetime,
            },
            expect_fail=expect_fail,
        )

    return impl


@pytest.fixture(name='enqueue_verified_availability')
def _enqueue_verified_availability(
        load_json, put_availability_data_to_s3, availability_enqueue,
):
    async def do_smth(
            place_id=1,
            s3_path=S3_AVAILABILITY_PATH,
            file_datetime=TEST_DATETIME,
            task_id='1',
            expect_fail=False,
    ):
        new_availabilities = load_json('s3_availability.json')
        await put_availability_data_to_s3(
            new_availabilities['items'], s3_path, str(place_id),
        )
        await availability_enqueue(
            place_id, s3_path, file_datetime, task_id, expect_fail=expect_fail,
        )

    return do_smth


@pytest.fixture(name='stocks_enqueue')
def _stocks_enqueue(stq_runner):
    async def do_stocks_enqueue(
            place_id=1,
            s3_path=S3_STOCKS_PATH,
            file_datetime=TEST_DATETIME,
            task_id='1',
            expect_fail=False,
    ):
        await stq_runner.eats_nomenclature_update_stocks.call(
            task_id=task_id,
            args=[],
            kwargs={
                'place_id': str(place_id),
                's3_path': s3_path,
                'file_datetime': file_datetime,
            },
            expect_fail=expect_fail,
        )

    return do_stocks_enqueue


@pytest.fixture(name='enqueue_verified_stocks')
def _enqueue_verified_stocks(load_json, put_stock_data_to_s3, stocks_enqueue):
    async def do_smth(
            place_id=1,
            s3_path=S3_STOCKS_PATH,
            file_datetime=TEST_DATETIME,
            task_id='1',
            expect_fail=False,
    ):
        new_stocks = load_json('s3_stocks.json')
        await put_stock_data_to_s3(new_stocks['items'], s3_path, str(place_id))
        await stocks_enqueue(
            place_id, s3_path, file_datetime, task_id, expect_fail=expect_fail,
        )

    return do_smth


@pytest.fixture(name='prices_enqueue')
def _prices_enqueue(stq_runner):
    async def do_prices_enqueue(
            place_id=1,
            s3_path=S3_PRICES_PATH,
            file_datetime=TEST_DATETIME,
            task_id='1',
            expect_fail=False,
    ):
        await stq_runner.eats_nomenclature_update_prices.call(
            task_id=task_id,
            args=[],
            kwargs={
                'place_id': str(place_id),
                's3_path': s3_path,
                'file_datetime': file_datetime,
            },
            expect_fail=expect_fail,
        )

    return do_prices_enqueue


@pytest.fixture(name='enqueue_verified_prices')
def _enqueue_verified_prices(load_json, put_prices_data_to_s3, prices_enqueue):
    async def do_smth(
            place_id=1,
            s3_path=S3_PRICES_PATH,
            file_datetime=TEST_DATETIME,
            task_id='1',
            expect_fail=False,
    ):
        new_prices = load_json('s3_prices.json')
        await put_prices_data_to_s3(
            new_prices['items'], s3_path, str(place_id),
        )
        await prices_enqueue(
            place_id, s3_path, file_datetime, task_id, expect_fail=expect_fail,
        )

    return do_smth


@pytest.fixture(name='sql_are_availabilities_ready')
def _sql_are_availabilities_ready(pgsql):
    def do_smth(place_id):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select are_availabilities_ready
            from eats_nomenclature.place_enrichment_statuses
            where place_id = {place_id};
            """,
        )
        result = list(cursor)
        return result and result[0][0]

    return do_smth


@pytest.fixture(name='sql_are_prices_ready')
def _sql_are_prices_ready(pgsql):
    def do_smth(place_id):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select are_prices_ready
            from eats_nomenclature.place_enrichment_statuses
            where place_id = {place_id};
            """,
        )
        result = list(cursor)
        return result and result[0][0]

    return do_smth


@pytest.fixture(name='sql_are_stocks_ready')
def _sql_are_stocks_ready(pgsql):
    def do_smth(place_id):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select are_stocks_ready
            from eats_nomenclature.place_enrichment_statuses
            where place_id = {place_id};
            """,
        )
        result = list(cursor)
        return result and result[0][0]

    return do_smth


@pytest.fixture(name='sql_are_custom_categories_ready')
def _sql_are_custom_categories_ready(pgsql):
    def do_smth(assortment_id):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
                select are_custom_categories_ready
                from eats_nomenclature.assortment_enrichment_statuses
                where assortment_id = '{assortment_id}';
                """,
        )
        result = list(cursor)
        return result and result[0][0]

    return do_smth


@pytest.fixture(name='get_uploaded_file_path')
def _get_uploaded_file_path(pgsql):
    def get_path(place_id):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select file_path
            from eats_nomenclature.nomenclature_files
            where place_id = {place_id}
            """,
        )

        return cursor.fetchone()[0]

    return get_path


@pytest.fixture(name='sql_upsert_place')
def _sql_upsert_place(pgsql):
    def do_sql_upsert_place(place_id, place_slug):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            insert into eats_nomenclature.places (id, slug)
            values ({place_id}, '{place_slug}')
            on conflict (id) do update
            set
            slug = excluded.slug,
            updated_at = now()
            """,
        )
        cursor.execute(
            f"""
            insert into eats_nomenclature.brand_places (brand_id, place_id)
            values (777, {place_id})
            on conflict (place_id) do nothing
            """,
        )

    return do_sql_upsert_place


def _sql_get_places_by_assortment(pgsql, in_progress_assortment_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select pa.place_id
        from eats_nomenclature.place_assortments pa
        join eats_nomenclature.assortment_enrichment_statuses aes
          on pa.in_progress_assortment_id = aes.assortment_id
        where pa.in_progress_assortment_id = {in_progress_assortment_id}
        """,
    )
    return [row[0] for row in list(cursor)]


def _sql_complete_place_enrichment_status(
        pgsql,
        place_id,
        are_availabilities_ready=True,
        are_stocks_ready=True,
        are_prices_ready=True,
):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.place_enrichment_statuses(
          place_id, are_availabilities_ready,
          are_stocks_ready, are_prices_ready
        )
        values (
            {place_id},
            {str(are_availabilities_ready).lower()},
            {str(are_stocks_ready).lower()},
            {str(are_prices_ready).lower()}
        )
        on conflict (place_id) do update
        set
          are_availabilities_ready = excluded.are_availabilities_ready,
          are_stocks_ready = excluded.are_stocks_ready,
          are_prices_ready = excluded.are_prices_ready;
        """,
    )


def _sql_complete_assortment_enrichment_status(
        pgsql, assortment_id, are_custom_categories_ready=True,
):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.assortment_enrichment_statuses(
          assortment_id, are_custom_categories_ready
        )
        values ({assortment_id}, {str(are_custom_categories_ready).lower()})
        on conflict (assortment_id) do update
        set are_custom_categories_ready = excluded.are_custom_categories_ready;
        """,
    )


@pytest.fixture(name='duplicate_assortment_data')
def _duplicate_assortment_data(pg_realdict_cursor):
    def duplicate(new_assortment_id, old_assortment_id):
        cursor = pg_realdict_cursor
        cursor.execute(
            """
            select *
            from eats_nomenclature.categories
            where assortment_id = %s
            """,
            (old_assortment_id,),
        )
        categories = cursor.fetchall()

        cursor.execute(
            """
            select *
            from eats_nomenclature.categories_products
            where assortment_id = %s
            """,
            (old_assortment_id,),
        )
        categories_products = cursor.fetchall()

        for i in categories + categories_products:
            i['assortment_id'] = new_assortment_id

        for category in categories:
            cursor.execute(
                """
                insert into eats_nomenclature.categories(
                    name,
                    origin_id,
                    assortment_id,
                    is_custom,
                    custom_category_id,
                    public_id
                )
                values (
                    %(name)s,
                    %(origin_id)s,
                    %(assortment_id)s,
                    %(is_custom)s,
                    %(custom_category_id)s,
                    %(public_id)s
                )
                returning id
                """,
                category,
            )
            new_id = cursor.fetchone()['id']
            for product in categories_products:
                if product['category_id'] == category['id']:
                    product['category_id'] = new_id

        for product in categories_products:
            cursor.execute(
                """
                insert into eats_nomenclature.categories_products(
                    assortment_id,
                    category_id,
                    product_id,
                    sort_order
                )
                values (
                    %(assortment_id)s,
                    %(category_id)s,
                    %(product_id)s,
                    %(sort_order)s
                )
                """,
                product,
            )

    return duplicate


@pytest.fixture(name='verify_periodic_metrics')
def _verify_periodic_metrics(
        taxi_eats_nomenclature, taxi_eats_nomenclature_monitor, testpoint,
):
    async def _verify(periodic_name, is_distlock):
        periodic_runner = (
            taxi_eats_nomenclature.run_distlock_task
            if is_distlock
            else taxi_eats_nomenclature.run_periodic_task
        )
        periodic_short_name = (
            periodic_name
            if is_distlock
            else periodic_name[len('eats_nomenclature-') :]
        )

        should_fail = False

        @testpoint(f'eats-nomenclature_{periodic_short_name}::fail')
        def _fail(param):
            return {'inject_failure': should_fail}

        @testpoint(f'eats-nomenclature_periodic-data::use-current-epoch')
        def _use_current_epoch(param):
            return {'use_current_epoch': True}

        await taxi_eats_nomenclature.tests_control(reset_metrics=True)

        await periodic_runner(periodic_name)
        assert _fail.has_calls

        metrics = await taxi_eats_nomenclature_monitor.get_metrics()
        data = metrics['periodic-data'][periodic_short_name]
        assert data['starts'] == 1
        assert data['oks'] == 1
        assert data['fails'] == 0
        assert data['execution-time']['min'] >= 0
        assert data['execution-time']['max'] >= 0
        assert data['execution-time']['avg'] >= 0

        should_fail = True
        try:
            await periodic_runner(periodic_name)
        except taxi_eats_nomenclature.PeriodicTaskFailed:
            pass
        assert _fail.has_calls

        metrics = await taxi_eats_nomenclature_monitor.get_metrics()
        data = metrics['periodic-data'][periodic_short_name]
        assert data['starts'] == 2
        assert data['oks'] == 1
        assert data['fails'] == 1
        assert data['execution-time']['min'] >= 0
        assert data['execution-time']['max'] >= 0
        assert data['execution-time']['avg'] >= 0

    return _verify


@pytest.fixture(name='sql_get_place_processing_last_status')
def _sql_get_place_processing_last_status(pg_realdict_cursor, to_utc_datetime):
    def do_smth(place_id, task_type):
        cursor = pg_realdict_cursor
        cursor.execute(
            f"""
            select
                status,
                task_error,
                task_error_details,
                task_warnings,
                status_or_text_changed_at
            from eats_nomenclature.places_processing_last_status_v2
            where place_id = {place_id} and task_type = '{task_type}'
            """,
        )
        result = cursor.fetchone()
        if result:
            result['status_or_text_changed_at'] = to_utc_datetime(
                result['status_or_text_changed_at'],
            )
        return result

    return do_smth


@pytest.fixture(name='sql_get_place_processing_last_status_history')
def _sql_get_place_processing_last_status_history(
        pg_realdict_cursor, to_utc_datetime,
):
    def do_smth(place_id, task_type):
        cursor = pg_realdict_cursor
        cursor.execute(
            f"""
            select
                id,
                status,
                task_error,
                task_error_details,
                task_warnings,
                status_or_text_changed_at
            from eats_nomenclature.places_processing_last_status_v2_history
            where place_id = {place_id} and task_type = '{task_type}'
            order by id
            """,
        )
        result = cursor.fetchall()
        for row in result:
            del row['id']
            row['status_or_text_changed_at'] = to_utc_datetime(
                row['status_or_text_changed_at'],
            )
        return result

    return do_smth


@pytest.fixture(name='sql_get_place_assortment_proc_last_status')
def _sql_get_place_assortment_proc_last_status(
        pg_realdict_cursor, to_utc_datetime,
):
    def do_smth(place_id, trait_id=None):
        trait_id_condition = (
            f'trait_id = {trait_id}' if trait_id else 'trait_id is null'
        )
        cursor = pg_realdict_cursor
        cursor.execute(
            f"""
            select
                assortment_id,
                status,
                task_error,
                task_error_details,
                task_warnings,
                status_or_text_changed_at
            from eats_nomenclature.place_assortments_processing_last_status
            where place_id = {place_id} and {trait_id_condition}
            """,
        )
        result = cursor.fetchone()
        if result:
            result['status_or_text_changed_at'] = to_utc_datetime(
                result['status_or_text_changed_at'],
            )
        return result

    return do_smth


@pytest.fixture(name='sql_get_place_assortment_last_status_history')
def _sql_get_place_assortment_last_status_history(
        pg_realdict_cursor, to_utc_datetime,
):
    def do_smth(place_id, trait_id=None):
        trait_id_condition = (
            f'trait_id = {trait_id}' if trait_id else 'trait_id is null'
        )
        cursor = pg_realdict_cursor
        cursor.execute(
            f"""
            select
                id,
                assortment_id,
                status,
                task_error,
                task_error_details,
                task_warnings,
                status_or_text_changed_at
            from
            eats_nomenclature.place_assortments_processing_last_status_history
            where place_id = {place_id} and {trait_id_condition}
            order by id
            """,
        )
        result = cursor.fetchall()
        for row in result:
            del row['id']
            row['status_or_text_changed_at'] = to_utc_datetime(
                row['status_or_text_changed_at'],
            )
        return result

    return do_smth


@pytest.fixture(name='sql_set_place_assortment_proc_last_status')
def _sql_set_place_assortment_proc_last_status(pg_realdict_cursor):
    def do_smth(
            place_id,
            assortment_id,
            trait_id,
            status,
            status_or_text_changed_at,
    ):
        cursor = pg_realdict_cursor
        cursor.execute(
            f"""
            insert into
              eats_nomenclature.place_assortments_processing_last_status(
                place_id, assortment_id, trait_id, status,
                status_or_text_changed_at
            ) values
            (
                {place_id},
                {assortment_id},
                {trait_id if trait_id else 'null'},
                '{status}',
                '{status_or_text_changed_at}'
            )
            """,
        )
        cursor.execute(
            f"""
            insert into
              eats_nomenclature.place_assortments_processing_last_status_history(
                place_id, assortment_id, trait_id,
                status, status_or_text_changed_at
            ) values
            (
                {place_id},
                {assortment_id},
                {trait_id if trait_id else 'null'},
                '{status}',
                '{status_or_text_changed_at}'
            )
            """,
        )

    return do_smth


@pytest.fixture(name='sql_get_assortment_trait_id')
def _sql_get_assortment_trait_id(pgsql):
    def do_smth(brand_id, assortment_name, insert_if_missing=False):
        if not assortment_name:
            assortment_name = 'default_assortment'

        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            select id
            from eats_nomenclature.assortment_traits
            where brand_id = %s and assortment_name = %s
            """,
            (brand_id, assortment_name),
        )
        result = cursor.fetchone()
        if result or not insert_if_missing:
            return result[0]

        cursor.execute(
            f"""
            insert into eats_nomenclature.assortment_traits(
                brand_id,
                assortment_name
            )
            values(%s, %s)
            returning id
            """,
            (brand_id, assortment_name),
        )
        return cursor.fetchone()[0]

    return do_smth


@pytest.fixture(name='sql_get_assortment_trait')
def _sql_get_assortment_trait(pg_realdict_cursor):
    def do_smth(trait_id):
        cursor = pg_realdict_cursor
        cursor.execute(
            f"""
            select assortment_name, brand_id
            from eats_nomenclature.assortment_traits
            where id = %s
            """,
            (trait_id,),
        )
        return cursor.fetchone()

    return do_smth


@pytest.fixture(name='sql_remove_default_assortment_trait')
def _sql_remove_default_assortment_trait(pg_realdict_cursor):
    def do_smth(brand_id):
        cursor = pg_realdict_cursor
        cursor.execute(
            """
            select id
            from eats_nomenclature.assortment_traits
            where brand_id = %s
              and assortment_name='default_assortment'
            """,
            (brand_id,),
        )
        if not cursor.rowcount:
            return

        trait_id = cursor.fetchone()['id']
        cursor.execute(
            """
            delete
            from eats_nomenclature.brands_custom_categories_groups
            where brand_id = %s
              and trait_id = %s
            """,
            (brand_id, trait_id),
        )
        cursor.execute(
            """
            delete
            from eats_nomenclature.assortment_traits
            where id = %s
            """,
            (trait_id,),
        )

    return do_smth


@pytest.fixture(name='sql_del_default_assortments')
def _sql_del_default_assortments(pgsql):
    def do_smth(brand_id=1, place_id=1):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            delete from eats_nomenclature.place_default_assortments
            where place_id = {place_id}
            """,
        )
        cursor.execute(
            f"""
            delete from eats_nomenclature.brand_default_assortments
            where brand_id = {brand_id}
            """,
        )

    return do_smth


@pytest.fixture(name='sql_set_place_default_assortment')
def _sql_set_place_default_assortment(pgsql):
    def do_smth(place_id=1, trait_id=1):
        trait_id = trait_id if trait_id else 'null'
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            insert into eats_nomenclature.place_default_assortments(
                place_id, trait_id
            ) values({place_id}, {trait_id})
            on conflict (place_id) do update
            set trait_id = excluded.trait_id
            """,
        )

    return do_smth


@pytest.fixture(name='sql_set_brand_default_assortment')
def _sql_set_brand_default_assortment(pgsql):
    def do_smth(brand_id=1, trait_id=1):
        trait_id = trait_id if trait_id else 'null'
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            insert into eats_nomenclature.brand_default_assortments(
                brand_id, trait_id
            ) values({brand_id}, {trait_id})
            on conflict (brand_id) do update
            set trait_id = excluded.trait_id
            """,
        )

    return do_smth


@pytest.fixture(name='sql_set_brand_fallback')
def _sql_set_brand_fallback(pgsql):
    def do_smth(
            brand_id,
            fallback_to_product_picture=False,
            fallback_to_product_vendor=False,
    ):
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            update brands
            set
                fallback_to_product_picture = {fallback_to_product_picture},
                fallback_to_product_vendor = {fallback_to_product_vendor}
            where id = {brand_id};
            """,
        )

    return do_smth


@pytest.fixture(name='base64_encode')
def _base64_encode():
    def do_smth(data):
        return base64.b64encode(str(data).encode()).decode()

    return do_smth


@pytest.fixture
def exp_set_sku_data(experiments3, load_json, taxi_eats_nomenclature):
    async def impl(is_enabled, excluded_brand_ids=None):
        excluded_brand_ids = excluded_brand_ids or []

        experiment_data = load_json('sku_experiment.json')
        experiment_data['experiments'][0]['match']['predicate']['type'] = str(
            is_enabled,
        ).lower()
        experiment_data['experiments'][0]['clauses'][0]['value'][
            'excluded_brand_ids'
        ] = [str(i) for i in excluded_brand_ids]
        experiments3.add_experiments_json(experiment_data)

        await taxi_eats_nomenclature.invalidate_caches()

    return impl
