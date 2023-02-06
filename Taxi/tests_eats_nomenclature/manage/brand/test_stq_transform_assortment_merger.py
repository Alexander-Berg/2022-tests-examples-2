import datetime as dt

import pytest


QUEUE_NAME = 'eats_nomenclature_transform_assortment'
OLD_NOMENCLATURE_CHUNK_SIZE = 1
CATEGORIES_QUERY = """
    select name, origin_id
    from eats_nomenclature.categories
"""


def timeouts_settings(assortment_enrichment_timeout):
    return {
        'EATS_NOMENCLATURE_PROCESSOR_TIMEOUTS': {
            'assortment_enrichment_timeout': assortment_enrichment_timeout,
        },
    }


@pytest.mark.parametrize('use_chunked_data', [False, True])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_categories_merge(
        taxi_config,
        stq_runner,
        pgsql,
        mocked_time,
        insert_enrichment_status,
        get_in_progress_assortment,
        get_active_assortment,
        brand_task_enqueue,
        get_uploaded_file_path,
        # parametrize params
        use_chunked_data,
):
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_BRAND_NOMENCLATURE_PROCESSING': {
                'split_old_nomenclature_into_chunks': use_chunked_data,
                'old_nomenclature_chunk_size': OLD_NOMENCLATURE_CHUNK_SIZE,
            },
        },
    )

    place_id = 1
    brand_id = 1
    await brand_task_enqueue(
        task_id='task', brand_id=str(brand_id), place_ids=[str(place_id)],
    )
    processed_path = get_uploaded_file_path(place_id)
    assert use_chunked_data == ('.json' not in processed_path)

    active_assortment_id = get_active_assortment(place_id)
    assortment_enrichment_timeout = 30
    taxi_config.set_values(timeouts_settings(assortment_enrichment_timeout))

    # Insert inactive assortment which is outdated.
    outdated_assortment_id = get_in_progress_assortment(place_id)
    insert_enrichment_status(
        outdated_assortment_id,
        mocked_time.now()
        - dt.timedelta(minutes=assortment_enrichment_timeout + 1),
    )

    await stq_runner.eats_nomenclature_transform_assortment.call(
        task_id=str(active_assortment_id),
        kwargs={'assortment_s3_url': processed_path, 'brand_id': brand_id},
        expect_fail=False,
    )
    in_progress_assortment_id = get_in_progress_assortment(place_id)

    assert (
        sql_read_data(
            pgsql,
            CATEGORIES_QUERY
            + f'where assortment_id = {in_progress_assortment_id}',
        )
        == {
            ('category_1', 'category_1_origin'),
            ('category_2', 'category_2_origin'),
            ('category_3', 'category_3_origin'),
            ('category_7', 'category_7_origin'),
            ('category_8', 'category_8_origin'),
            ('category_9', 'category_9_origin'),
        }
    )


@pytest.mark.parametrize('use_chunked_data', [False, True])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_categories_pictures_merge(
        taxi_config,
        stq_runner,
        pgsql,
        mocked_time,
        insert_enrichment_status,
        get_in_progress_assortment,
        get_active_assortment,
        brand_task_enqueue,
        get_uploaded_file_path,
        # parametrize params
        use_chunked_data,
):
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_BRAND_NOMENCLATURE_PROCESSING': {
                'split_old_nomenclature_into_chunks': use_chunked_data,
                'old_nomenclature_chunk_size': OLD_NOMENCLATURE_CHUNK_SIZE,
            },
        },
    )

    place_id = 1
    brand_id = 1

    await brand_task_enqueue(
        task_id='task', brand_id=str(brand_id), place_ids=[str(place_id)],
    )
    processed_path = get_uploaded_file_path(place_id)
    assert use_chunked_data == ('.json' not in processed_path)

    active_assortment_id = get_active_assortment(place_id)
    assortment_enrichment_timeout = 30
    taxi_config.set_values(timeouts_settings(assortment_enrichment_timeout))

    # Insert inactive assortment which is outdated.
    outdated_assortment_id = get_in_progress_assortment(place_id)
    insert_enrichment_status(
        outdated_assortment_id,
        mocked_time.now()
        - dt.timedelta(minutes=assortment_enrichment_timeout + 1),
    )

    await stq_runner.eats_nomenclature_transform_assortment.call(
        task_id=str(active_assortment_id),
        kwargs={'assortment_s3_url': processed_path, 'brand_id': brand_id},
        expect_fail=False,
    )

    in_progress_assortment_id = get_in_progress_assortment(place_id)

    categories_pictures_query = f"""
        select c.origin_id, p.url
        from eats_nomenclature.categories c
        join eats_nomenclature.category_pictures cp
        on c.id = cp.category_id
        join eats_nomenclature.pictures p
        on cp.picture_id = p.id
        where cp.assortment_id = {in_progress_assortment_id}
    """
    assert sql_read_data(pgsql, categories_pictures_query) == {
        ('category_1_origin', 'url_1'),
        ('category_2_origin', 'url_2'),
        ('category_3_origin', 'url_3'),
        ('category_7_origin', 'url_7'),
        ('category_8_origin', 'url_8'),
        ('category_9_origin', 'url_9'),
    }


@pytest.mark.parametrize('use_chunked_data', [False, True])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_categories_products_merge(
        taxi_config,
        stq_runner,
        pgsql,
        mocked_time,
        insert_enrichment_status,
        get_in_progress_assortment,
        get_active_assortment,
        brand_task_enqueue,
        get_uploaded_file_path,
        # parametrize params
        use_chunked_data,
):
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_BRAND_NOMENCLATURE_PROCESSING': {
                'split_old_nomenclature_into_chunks': use_chunked_data,
                'old_nomenclature_chunk_size': OLD_NOMENCLATURE_CHUNK_SIZE,
            },
        },
    )

    place_id = 1
    brand_id = 1
    await brand_task_enqueue(
        task_id='task', brand_id=str(brand_id), place_ids=[str(place_id)],
    )
    processed_path = get_uploaded_file_path(place_id)
    assert use_chunked_data == ('.json' not in processed_path)

    active_assortment_id = get_active_assortment(place_id)
    assortment_enrichment_timeout = 30
    taxi_config.set_values(timeouts_settings(assortment_enrichment_timeout))

    # Insert inactive assortment which is outdated.
    outdated_assortment_id = get_in_progress_assortment(place_id)
    insert_enrichment_status(
        outdated_assortment_id,
        mocked_time.now()
        - dt.timedelta(minutes=assortment_enrichment_timeout + 1),
    )

    await stq_runner.eats_nomenclature_transform_assortment.call(
        task_id=str(active_assortment_id),
        kwargs={'assortment_s3_url': processed_path, 'brand_id': brand_id},
        expect_fail=False,
    )

    in_progress_assortment_id = get_in_progress_assortment(place_id)

    categories_products_query = f"""
        select c.origin_id, p.origin_id, cp.sort_order
        from eats_nomenclature.categories c
        join eats_nomenclature.categories_products cp
        on c.id = cp.category_id
        join eats_nomenclature.products p
        on cp.product_id = p.id
        where cp.assortment_id = {in_progress_assortment_id}
    """
    assert sql_read_data(pgsql, categories_products_query) == {
        ('category_1_origin', 'item_origin_1', 100),
        ('category_1_origin', 'item_origin_2', 50),
        ('category_3_origin', 'item_origin_3', 200),
        ('category_9_origin', 'item_origin_4', 300),
    }


@pytest.mark.parametrize('use_chunked_data', [False, True])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_categories_relations_merge(
        taxi_config,
        stq_runner,
        pgsql,
        mocked_time,
        insert_enrichment_status,
        get_in_progress_assortment,
        get_active_assortment,
        brand_task_enqueue,
        get_uploaded_file_path,
        # parametrize params
        use_chunked_data,
):
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_BRAND_NOMENCLATURE_PROCESSING': {
                'split_old_nomenclature_into_chunks': use_chunked_data,
                'old_nomenclature_chunk_size': OLD_NOMENCLATURE_CHUNK_SIZE,
            },
        },
    )

    place_id = 1
    brand_id = 1
    await brand_task_enqueue(
        task_id='task', brand_id=str(brand_id), place_ids=[str(place_id)],
    )
    processed_path = get_uploaded_file_path(place_id)
    assert use_chunked_data == ('.json' not in processed_path)

    active_assortment_id = get_active_assortment(place_id)
    assortment_enrichment_timeout = 30
    taxi_config.set_values(timeouts_settings(assortment_enrichment_timeout))

    # Insert inactive assortment which is outdated.
    outdated_assortment_id = get_in_progress_assortment(place_id)
    insert_enrichment_status(
        outdated_assortment_id,
        mocked_time.now()
        - dt.timedelta(minutes=assortment_enrichment_timeout + 1),
    )

    await stq_runner.eats_nomenclature_transform_assortment.call(
        task_id=str(active_assortment_id),
        kwargs={'assortment_s3_url': processed_path, 'brand_id': brand_id},
        expect_fail=False,
    )

    in_progress_assortment_id = get_in_progress_assortment(place_id)

    assert sql_read_categories_relations(pgsql, in_progress_assortment_id) == {
        ('category_7_origin', 'None', 100),
        ('category_3_origin', 'category_7_origin', 100),
        ('category_8_origin', 'category_7_origin', 100),
        ('category_9_origin', 'category_8_origin', 100),
        ('category_1_origin', 'category_8_origin', 100),
        ('category_2_origin', 'category_8_origin', 100),
    }


@pytest.mark.parametrize('use_chunked_data', [False, True])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_places_categories_merge(
        taxi_config,
        stq_runner,
        pgsql,
        mocked_time,
        insert_enrichment_status,
        get_in_progress_assortment,
        get_active_assortment,
        brand_task_enqueue,
        get_uploaded_file_path,
        # parametrize params
        use_chunked_data,
):
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_BRAND_NOMENCLATURE_PROCESSING': {
                'split_old_nomenclature_into_chunks': use_chunked_data,
                'old_nomenclature_chunk_size': OLD_NOMENCLATURE_CHUNK_SIZE,
            },
        },
    )

    place_id = 1
    brand_id = 1
    await brand_task_enqueue(
        task_id='task', brand_id=str(brand_id), place_ids=[str(place_id)],
    )
    processed_path = get_uploaded_file_path(place_id)
    assert use_chunked_data == ('.json' not in processed_path)

    active_assortment_id = get_active_assortment(place_id)
    assortment_enrichment_timeout = 30
    taxi_config.set_values(timeouts_settings(assortment_enrichment_timeout))

    # Insert inactive assortment which is outdated.
    outdated_assortment_id = get_in_progress_assortment(place_id)
    insert_enrichment_status(
        outdated_assortment_id,
        mocked_time.now()
        - dt.timedelta(minutes=assortment_enrichment_timeout + 1),
    )

    await stq_runner.eats_nomenclature_transform_assortment.call(
        task_id=str(active_assortment_id),
        kwargs={'assortment_s3_url': processed_path, 'brand_id': brand_id},
        expect_fail=False,
    )
    in_progress_assortment_id = get_in_progress_assortment(place_id)

    places_categories_query = f"""
        select c.origin_id, pc.active_items_count
        from eats_nomenclature.categories c
        join eats_nomenclature.places_categories pc
        on c.id = pc.category_id
        where pc.assortment_id = {in_progress_assortment_id}
          and place_id = {place_id}
    """
    assert sql_read_data(pgsql, places_categories_query) == {
        ('category_7_origin', 0),
        ('category_3_origin', 0),
        ('category_8_origin', 0),
        ('category_9_origin', 0),
        ('category_1_origin', 0),
        ('category_2_origin', 0),
    }


@pytest.mark.parametrize('should_merge_non_assortment_entities', [False, True])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_non_assortment_entities_merge(
        stq,
        stq_runner,
        stq_call_forward,
        taxi_config,
        pgsql,
        load_json,
        put_brand_nomenclature_to_s3,
        get_in_progress_assortment,
        # parametrize params
        should_merge_non_assortment_entities,
):
    place_id = 1
    assortment_id = 2
    trait_id = 2
    old_non_assortment_data = sql_get_non_assortment_entities(pgsql)

    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_TEMPORARY_CONFIGS': {
                'should_merge_nmn_on_brand_sync': (
                    should_merge_non_assortment_entities
                ),
            },
        },
    )

    await enqueue_update_brand_assortments(
        load_json, put_brand_nomenclature_to_s3, stq_runner,
    )

    times_called = stq.eats_nomenclature_transform_assortment.times_called
    assert times_called > 0
    for _ in range(times_called):
        task_info = stq.eats_nomenclature_transform_assortment.next_call()
        await stq_call_forward(task_info)

    in_progress_assortment_id = get_in_progress_assortment(
        place_id, trait_id=trait_id,
    )

    assert (
        sql_read_data(
            pgsql, CATEGORIES_QUERY + f'where assortment_id = {assortment_id}',
        )
        == {
            ('category_1', 'category_1_origin'),
            ('category_2', 'category_2_origin'),
            ('category_3', 'category_3_origin'),
            ('category_7', 'category_7_origin'),
            ('category_8', 'category_8_origin'),
            ('category_9', 'category_9_origin'),
        }
    )
    if should_merge_non_assortment_entities:
        assert old_non_assortment_data != sql_get_non_assortment_entities(
            pgsql,
        )
    else:
        assert old_non_assortment_data == sql_get_non_assortment_entities(
            pgsql,
        )

    assert sql_get_category_products(pgsql, in_progress_assortment_id) == [
        ('category_1_origin', 'item_origin_1'),
        ('category_1_origin', 'item_origin_2'),
        ('category_3_origin', 'item_origin_3'),
        ('category_9_origin', 'item_origin_4'),
    ]


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_one_product.sql'],
)
async def test_merge_only_assortment_entities_unknown_product_id(
        stq,
        stq_runner,
        stq_call_forward,
        taxi_config,
        pgsql,
        load_json,
        put_brand_nomenclature_to_s3,
        get_in_progress_assortment,
):
    place_id = 1
    assortment_id = 1
    trait_id = 1
    old_non_assortment_data = sql_get_non_assortment_entities(pgsql)

    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_TEMPORARY_CONFIGS': {
                'should_merge_nmn_on_brand_sync': False,
            },
        },
    )

    await enqueue_update_brand_assortments(
        load_json,
        put_brand_nomenclature_to_s3,
        stq_runner,
        trait_id=1,
        file_path='s3_brand_nomenclature_with_unknown_product_id.json',
    )

    times_called = stq.eats_nomenclature_transform_assortment.times_called
    assert times_called > 0
    for _ in range(times_called):
        task_info = stq.eats_nomenclature_transform_assortment.next_call()
        await stq_call_forward(task_info)

    in_progress_assortment_id = get_in_progress_assortment(
        place_id, trait_id=trait_id,
    )

    assert sql_read_data(
        pgsql, CATEGORIES_QUERY + f'where assortment_id = {assortment_id}',
    ) == {('category_1', 'category_1_origin')}
    assert old_non_assortment_data == sql_get_non_assortment_entities(pgsql)

    assert sql_get_category_products(pgsql, in_progress_assortment_id) == [
        ('category_1_origin', 'item_origin_1'),
    ]


def sql_read_data(pgsql, query):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(query)
    return {tuple(row) for row in cursor}


def sql_read_categories_relations(pgsql, assortment_id):
    category_ids_query = f"""
        select id, origin_id
        from eats_nomenclature.categories
        where assortment_id = {assortment_id}
    """
    categories = sql_read_data(pgsql, category_ids_query)
    id_to_origin_id = {c[0]: c[1] for c in categories}
    id_to_origin_id[None] = 'None'

    categories_relations_query = f"""
        select category_id, parent_category_id, sort_order
        from eats_nomenclature.categories_relations
        where assortment_id = {assortment_id}
    """
    categories_relations = sql_read_data(pgsql, categories_relations_query)
    return {
        (id_to_origin_id[cr[0]], id_to_origin_id[cr[1]], cr[2])
        for cr in categories_relations
    }


def sql_get_category_products(pgsql, assortment_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select cat.origin_id, pr.origin_id
        from eats_nomenclature.categories_products cp
        join eats_nomenclature.categories cat on cp.category_id = cat.id
        join eats_nomenclature.products pr on pr.id = cp.product_id
        where cp.assortment_id = {assortment_id}
        order by cat.origin_id, pr.origin_id
        """,
    )
    return cursor.fetchall()


def sql_get_non_assortment_entities(pgsql):
    non_assortment_data = {}
    tables = ['products', 'vendors', 'marking_types', 'pictures', 'barcodes']
    cursor = pgsql['eats_nomenclature'].cursor()
    for table in tables:
        cursor.execute(
            f"""
            select *
            from eats_nomenclature.{table}
            order by id
            """,
        )
        non_assortment_data[table] = cursor.fetchall()
    cursor.execute(
        f"""
        select *
        from eats_nomenclature.places_products
        order by place_id, product_id
        """,
    )
    non_assortment_data['places_products'] = cursor.fetchall()
    cursor.execute(
        f"""
        select *
        from eats_nomenclature.product_barcodes
        order by product_id, barcode_id
        """,
    )
    non_assortment_data['product_barcodes'] = cursor.fetchall()
    cursor.execute(
        f"""
        select *
        from eats_nomenclature.product_pictures
        order by product_id, picture_id
        """,
    )
    non_assortment_data['product_pictures'] = cursor.fetchall()
    return non_assortment_data


# pylint: disable=invalid-name
async def enqueue_update_brand_assortments(
        load_json,
        put_brand_nomenclature_to_s3,
        stq_runner,
        brand_id=1,
        trait_id=2,
        file_path=None,
):
    s3_brand_nomenclature_path = '/some/path/brand_nomenclature.json'
    brand_id = 1
    brand_nomenclature = load_json(
        's3_brand_nomenclature_with_changed_product_info.json'
        if file_path is None
        else file_path,
    )

    task_kwargs = {'brand_id': brand_id, 'trait_id': trait_id}

    await put_brand_nomenclature_to_s3(
        brand_nomenclature, s3_path=s3_brand_nomenclature_path,
    )

    await stq_runner.eats_nomenclature_update_brand_assortments.call(
        task_id='1', args=[], kwargs=task_kwargs, expect_fail=False,
    )
