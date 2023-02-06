import pytest

EXPORT_TASK_ID = 1
PROCCESSED_YT_PATH = '//edadeal_yt/proccessed/bystronom/2019-12-06'
QUEUE_NAME = 'eats_nomenclature_edadeal_skus_processing'

PRODUCT_PUBLIC_IDS = [
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    '33333333-3333-3333-3333-333333333333',
    '44444444-4444-4444-4444-444444444444',
    '44444444-4444-4444-4444-444444444445',
    '44444444-4444-4444-4444-444444444446',
    '44444444-4444-4444-4444-444444444447',
    '44444444-4444-4444-4444-444444444448',
    '55555555-5555-5555-5555-555555555555',
]


def settings(
        max_retries_on_error=3,
        max_retries_on_busy=3,
        max_busy_time_in_ms=100000,
        retry_on_busy_delay_ms=1000,
):
    return {
        '__default__': {
            'max_retries_on_error': max_retries_on_error,
            'max_retries_on_busy': max_retries_on_busy,
            'max_busy_time_in_ms': max_busy_time_in_ms,
            'retry_on_busy_delay_ms': retry_on_busy_delay_ms,
            'insert_batch_size': 1000,
            'lookup_batch_size': 1000,
        },
    }


def expected_product_skus():
    return [
        {
            'public_id': '11111111-1111-1111-1111-111111111111',
            'sku_uuid': None,
        },
        {
            'public_id': '22222222-2222-2222-2222-222222222222',
            'sku_uuid': None,
        },
        {
            'public_id': '33333333-3333-3333-3333-333333333333',
            'sku_uuid': 'f4e3f17d-607c-47a3-9235-3e883b048276',
        },
        {
            'public_id': '44444444-4444-4444-4444-444444444444',
            'sku_uuid': '8e11bc3f-37d2-44ae-8479-ae0d700c4ecd',
        },
        {
            'public_id': '44444444-4444-4444-4444-444444444445',
            'sku_uuid': None,
        },
        {
            'public_id': '44444444-4444-4444-4444-444444444446',
            'sku_uuid': '8e11bc3f-37d2-44ae-8479-ae0d700c4ec3',
        },
        {
            'public_id': '44444444-4444-4444-4444-444444444447',
            'sku_uuid': '8e11bc3f-37d2-44ae-8479-ae0d700c4ec3',
        },
        {
            'public_id': '44444444-4444-4444-4444-444444444448',
            'sku_uuid': '8e11bc3f-37d2-44ae-8479-ae0d700c4ec3',
        },
        {
            'public_id': '55555555-5555-5555-5555-555555555555',
            'sku_uuid': None,
        },
    ]


async def run_sku_task(task_enqueue_v2, get_edadeal_import_task):
    import_task = get_edadeal_import_task(
        task_type='sku', export_task_id=EXPORT_TASK_ID,
    )
    import_task_id = import_task['id']
    await task_enqueue_v2(QUEUE_NAME, task_id=import_task_id)


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data.sql', 'fill_sku.sql'],
)
@pytest.mark.yt(
    schemas=['yt_export_schema.yaml'],
    static_table_data=['yt_export_data.yaml'],
)
async def test_merge_on_empty(
        pgsql, task_enqueue_v2, yt_apply, get_edadeal_import_task,
):

    await run_sku_task(task_enqueue_v2, get_edadeal_import_task)

    new_product_skus = sql_get_product_skus(pgsql, PRODUCT_PUBLIC_IDS)

    assert sort_by_public_id(new_product_skus) == sort_by_public_id(
        expected_product_skus(),
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data.sql', 'fill_sku.sql'],
)
@pytest.mark.yt(
    schemas=['yt_export_schema.yaml'],
    static_table_data=['yt_export_data.yaml'],
)
async def test_merge_on_same_data(
        pgsql, task_enqueue_v2, yt_apply, get_edadeal_import_task,
):
    sql_set_product_skus(pgsql, expected_product_skus())

    await run_sku_task(task_enqueue_v2, get_edadeal_import_task)

    new_product_skus = sql_get_product_skus(pgsql, PRODUCT_PUBLIC_IDS)

    assert sort_by_public_id(new_product_skus) == sort_by_public_id(
        expected_product_skus(),
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data.sql', 'fill_sku.sql'],
)
@pytest.mark.yt(
    schemas=['yt_export_schema.yaml'],
    static_table_data=['yt_export_data.yaml'],
)
async def test_merge_on_different_data(
        pgsql, task_enqueue_v2, get_edadeal_import_task, yt_apply,
):
    sql_set_product_skus(
        pgsql,
        [
            {
                'public_id': '11111111-1111-1111-1111-111111111111',
                'sku_uuid': '8e11bc3f-37d2-44ae-8479-ae0d700c4ecd',
            },
            {
                'public_id': '22222222-2222-2222-2222-222222222222',
                'sku_uuid': 'f4e3f17d-607c-47a3-9235-3e883b048276',
            },
            {
                'public_id': '33333333-3333-3333-3333-333333333333',
                'sku_uuid': None,
            },
            {
                'public_id': '44444444-4444-4444-4444-444444444444',
                'sku_uuid': None,
            },
            {
                'public_id': '44444444-4444-4444-4444-444444444448',
                # SKU with a `merged_to` field
                'sku_uuid': '7e11bc3f-9012-5678-1234-ae0d700c4ec4',
            },
            {
                'public_id': '55555555-5555-5555-5555-555555555555',
                'sku_uuid': '8e11bc3f-37d2-44ae-8479-ae0d700c4ecd',
            },
        ],
    )

    await run_sku_task(task_enqueue_v2, get_edadeal_import_task)

    new_product_skus = sql_get_product_skus(pgsql, PRODUCT_PUBLIC_IDS)

    # Skus are never removed
    assert sort_by_public_id(new_product_skus) == sort_by_public_id(
        [
            {
                'public_id': '11111111-1111-1111-1111-111111111111',
                'sku_uuid': '8e11bc3f-37d2-44ae-8479-ae0d700c4ecd',
            },
            {
                'public_id': '22222222-2222-2222-2222-222222222222',
                'sku_uuid': 'f4e3f17d-607c-47a3-9235-3e883b048276',
            },
            {
                'public_id': '33333333-3333-3333-3333-333333333333',
                'sku_uuid': 'f4e3f17d-607c-47a3-9235-3e883b048276',
            },
            {
                'public_id': '44444444-4444-4444-4444-444444444444',
                'sku_uuid': '8e11bc3f-37d2-44ae-8479-ae0d700c4ecd',
            },
            {
                'public_id': '44444444-4444-4444-4444-444444444445',
                'sku_uuid': None,
            },
            {
                'public_id': '44444444-4444-4444-4444-444444444446',
                'sku_uuid': '8e11bc3f-37d2-44ae-8479-ae0d700c4ec3',
            },
            {
                'public_id': '44444444-4444-4444-4444-444444444447',
                'sku_uuid': '8e11bc3f-37d2-44ae-8479-ae0d700c4ec3',
            },
            {
                'public_id': '44444444-4444-4444-4444-444444444448',
                'sku_uuid': '8e11bc3f-37d2-44ae-8479-ae0d700c4ec3',
            },
            {
                'public_id': '55555555-5555-5555-5555-555555555555',
                'sku_uuid': '8e11bc3f-37d2-44ae-8479-ae0d700c4ecd',
            },
        ],
    )


@pytest.mark.config(
    EATS_NOMENCLATURE_PROCESSING=settings(max_retries_on_error=2),
)
@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_bad_data.sql'],
)
async def test_stq_error_limit(
        task_enqueue_v2,
        taxi_config,
        pgsql,
        yt_apply_force,
        get_edadeal_import_task,
):

    max_retries_on_error = taxi_config.get('EATS_NOMENCLATURE_PROCESSING')[
        '__default__'
    ]['max_retries_on_error']

    # These tasks will fail, because no YT tables were loaded

    import_task = get_edadeal_import_task(
        task_type='sku', export_task_id=EXPORT_TASK_ID,
    )
    import_task_id = import_task['id']

    for i in range(max_retries_on_error):
        await task_enqueue_v2(
            QUEUE_NAME, task_id=import_task_id, expect_fail=True, exec_tries=i,
        )

    # should succeed because of the error limit
    await task_enqueue_v2(
        QUEUE_NAME,
        task_id=import_task_id,
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data.sql', 'fill_sku.sql'],
)
@pytest.mark.yt(
    schemas=['yt_export_schema.yaml'],
    static_table_data=['yt_export_data.yaml'],
)
async def test_task_status(
        task_enqueue_v2,
        get_edadeal_import_task,
        get_import_task_status_history,
        yt_apply,
):
    # Before

    import_task = get_edadeal_import_task(
        task_type='sku', export_task_id=EXPORT_TASK_ID,
    )
    assert import_task['status'] == 'new'

    import_task_id = import_task['id']

    await task_enqueue_v2(QUEUE_NAME, task_id=import_task_id)

    # After

    task_statuses = get_import_task_status_history(
        task_type='sku', import_task_id=import_task_id,
    )
    assert len(task_statuses) == 2

    import_task = get_edadeal_import_task(
        task_type='sku', export_task_id=EXPORT_TASK_ID,
    )
    assert import_task['status'] == 'done'


def sql_set_product_skus(pgsql, product_skus):
    skus = sql_get_skus_raw(pgsql)
    skus_dict = {i['sku_uuid']: i['sku_id'] for i in skus}

    for i in product_skus:
        cursor = pgsql['eats_nomenclature'].cursor()
        cursor.execute(
            f"""
            update eats_nomenclature.products p
            set
                sku_id =
                  {skus_dict[i['sku_uuid']] if i['sku_uuid'] else 'null'}
            where
                p.public_id = '{i['public_id']}'::uuid;
            """,
        )


def sql_get_product_skus_raw(pgsql, public_ids):
    public_ids_wrapped = [f'\'{i}\'' for i in public_ids]

    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select sku_id, public_id
        from eats_nomenclature.products
        where public_id::text = any(array[{','.join(public_ids_wrapped)}])
        """,
    )

    return [{'sku_id': i[0], 'public_id': i[1]} for i in list(cursor)]


def sql_get_skus_raw(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select
          id,
          uuid
        from eats_nomenclature.sku
        """,
    )

    return [{'sku_id': i[0], 'sku_uuid': i[1]} for i in list(cursor)]


def sql_get_product_skus(pgsql, public_ids):
    product_skus_raw = sql_get_product_skus_raw(pgsql, public_ids)
    skus = sql_get_skus_raw(pgsql)
    skus_dict = {i['sku_id']: i['sku_uuid'] for i in skus}

    product_skus = []
    for i in product_skus_raw:
        product_skus.append(
            {
                'public_id': i['public_id'],
                'sku_uuid': skus_dict[i['sku_id']] if i['sku_id'] else None,
            },
        )

    return product_skus


def sort_by_public_id(data):
    return sorted(data, key=lambda k: k['public_id'])
