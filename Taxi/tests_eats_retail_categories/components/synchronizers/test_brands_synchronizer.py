from tests_eats_retail_categories import utils


PERIODIC_NAME = 'brands-synchronizer'

BRAND_IDS = [1, 12, 345]
DISABLED_IDS_COUNT = 1
BRANDS = [
    {'id': '1', 'slug': 'brand1', 'name': '0', 'scale': 'aspect_fit'},
    {'id': '12', 'slug': 'a', 'name': 'A.A'},
    {'id': '345', 'slug': 'bcd', 'name': 'Бе Бэ'},
]

BRANDS_UPDATE_SLUG = [
    {'id': '1', 'slug': 'super1', 'name': '0', 'scale': 'aspect_fit'},
    {'id': '12', 'slug': 'super2', 'name': 'A.A'},
    {'id': '345', 'slug': 'super3', 'name': 'Бе Бэ'},
]

BRANDS_UPDATE_PICTURE_SCALE = [
    {'id': '1', 'slug': 'brand1', 'name': '0', 'scale': 'aspect_fill'},
    {'id': '12', 'slug': 'super2', 'name': 'A.A', 'scale': None},
    {'id': '345', 'slug': 'super3', 'name': 'Бе Бэ', 'scale': None},
]


def sql_get_brand_infos(get_cursor):
    """Returns tuples (id, slug, is_enabled) for all brands"""

    cursor = get_cursor()
    cursor.execute(
        """
        SELECT id, slug, is_enabled
        FROM eats_retail_categories.brands
        ORDER BY id
        """,
    )
    return list(cursor)


def sql_get_brand_with_scale_infos(get_cursor):
    """Returns tuples (id, picture_scale) for all brands"""

    cursor = get_cursor()
    cursor.execute(
        """
        SELECT id, picture_scale
        FROM eats_retail_categories.brands
        ORDER BY id
        """,
    )
    return list(cursor)


def sql_get_brand_infos_short(get_cursor):
    """Returns pairs (id, is_enabled) for all brands"""

    rows = sql_get_brand_infos(get_cursor)
    return [(row[0], row[2]) for row in rows]


def sql_get_brand_ids(get_cursor):
    """Returns brand ids of all brands (enabled and disabled)"""

    rows = sql_get_brand_infos(get_cursor)
    return [row[0] for row in rows]


def sql_count_disabled_brands(get_cursor):
    """Returns count of disabled brands"""

    rows = sql_get_brand_infos(get_cursor)
    return sum(row[2] is False for row in rows)


async def test_brands_synchronizer_insert(
        taxi_eats_retail_categories, mockserver, get_cursor, pg_add_brand,
):
    # Проверяется, что при получении новые брендов они будут добавлены в БД,
    # а неактуальным выставлен флаг is_enabled = false
    pg_add_brand()

    @mockserver.json_handler(utils.Handlers.CORE_BRANDS)
    def _mock_eats_core_retail_mapping(request):
        return {'brands': BRANDS[1:]}

    await taxi_eats_retail_categories.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_ids(get_cursor) == BRAND_IDS
    assert sql_count_disabled_brands(get_cursor) == DISABLED_IDS_COUNT


async def test_brands_synchronizer_upsert(
        taxi_eats_retail_categories, mockserver, get_cursor, pg_add_brand,
):
    # Проверяется, что при получении брендов, которые уж есть в БД, они будут
    # обновлены, а неактуальным выставлен флаг is_enabled = false
    pg_add_brand()

    @mockserver.json_handler(utils.Handlers.CORE_BRANDS)
    def _mock_eats_core_retail_mapping(request):
        return {'brands': brands}

    brands = [BRANDS[1]]
    await taxi_eats_retail_categories.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_ids(get_cursor) == BRAND_IDS[0:2]
    assert sql_count_disabled_brands(get_cursor) == DISABLED_IDS_COUNT

    brands.append(BRANDS[2])
    await taxi_eats_retail_categories.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_ids(get_cursor) == BRAND_IDS
    assert sql_count_disabled_brands(get_cursor) == DISABLED_IDS_COUNT


async def test_brands_synchronizer_disable(
        taxi_eats_retail_categories, mockserver, get_cursor, pg_add_brand,
):
    # Проверяется, что брендам, которые уж есть в БД, но нет в ответе коры,
    # будет выставлен флаг is_enabled = false
    pg_add_brand()

    @mockserver.json_handler(utils.Handlers.CORE_BRANDS)
    def _mock_eats_core_retail_mapping(request):
        return {'brands': brands}

    brands = [BRANDS[1]]
    await taxi_eats_retail_categories.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_ids(get_cursor) == BRAND_IDS[0:2]
    assert sql_count_disabled_brands(get_cursor) == DISABLED_IDS_COUNT

    brands = [BRANDS[2]]
    await taxi_eats_retail_categories.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_infos_short(get_cursor) == [
        (BRAND_IDS[0], False),
        (BRAND_IDS[1], False),
        (BRAND_IDS[2], True),
    ]

    brands = []
    await taxi_eats_retail_categories.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_infos_short(get_cursor) == [
        (BRAND_IDS[0], False),
        (BRAND_IDS[1], False),
        (BRAND_IDS[2], False),
    ]

    brands = [BRANDS[1]]
    await taxi_eats_retail_categories.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_infos_short(get_cursor) == [
        (BRAND_IDS[0], False),
        (BRAND_IDS[1], True),
        (BRAND_IDS[2], False),
    ]

    brands = BRANDS[1:]
    await taxi_eats_retail_categories.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_ids(get_cursor) == BRAND_IDS
    assert sql_count_disabled_brands(get_cursor) == DISABLED_IDS_COUNT


async def test_brands_synchronizer_update_slug(
        taxi_eats_retail_categories, mockserver, get_cursor, pg_add_brand,
):
    # Проверяется, что у брендов, которые уж есть в БД, будет обновлен slug
    pg_add_brand()

    @mockserver.json_handler(utils.Handlers.CORE_BRANDS)
    def _mock_eats_core_retail_mapping(request):
        return {'brands': BRANDS_UPDATE_SLUG}

    await taxi_eats_retail_categories.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_infos(get_cursor) == [
        (int(row['id']), row['slug'], True) for row in BRANDS_UPDATE_SLUG
    ]
    assert sql_count_disabled_brands(get_cursor) == 0


async def test_brands_synchronizer_update_picture_scale(
        taxi_eats_retail_categories, mockserver, get_cursor,
):
    # Проверяется, что у брендов, которые уж есть в БД, будет обновлен scale
    @mockserver.json_handler(utils.Handlers.CORE_BRANDS)
    def _mock_eats_core_retail_mapping(request):
        return {'brands': BRANDS_UPDATE_PICTURE_SCALE}

    await taxi_eats_retail_categories.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_with_scale_infos(get_cursor) == [
        (int(row['id']), row['scale']) for row in BRANDS_UPDATE_PICTURE_SCALE
    ]
    assert sql_count_disabled_brands(get_cursor) == 0


async def test_brands_synchronizer_invalid_id(
        taxi_eats_retail_categories, mockserver, get_cursor,
):
    # Проверяется, что бренды с невалидным id будут корректно обработаны
    # и не добавлены в БД
    valid_ids = ['0', '1', '200', '3456', '2147483647']
    invalid_ids = [
        '',
        '01',
        '-1',
        '+1',
        '0x1',
        '1.0',
        ' 1',
        '1 ',
        '1s',
        's',
        '2147483648',
    ]
    brands = [
        {'id': valid_id, 'slug': 'e', 'name': 'E'} for valid_id in valid_ids
    ]
    for invalid_id in invalid_ids:
        brands.append({'id': invalid_id, 'slug': 'e', 'name': 'E'})

    @mockserver.json_handler(utils.Handlers.CORE_BRANDS)
    def _mock_eats_core_retail_mapping(request):
        return {'brands': brands}

    await taxi_eats_retail_categories.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_ids(get_cursor) == list(map(int, valid_ids))
    assert sql_count_disabled_brands(get_cursor) == 0
