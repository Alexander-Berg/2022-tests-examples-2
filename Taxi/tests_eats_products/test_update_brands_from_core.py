from typing import List
from typing import Tuple

from tests_eats_products import utils


PERIODIC_NAME = 'update-brands-from-core'

BRAND_IDS = [1, 12, 345]  # ID:1 from pg_eats_products.sql
DISABLED_IDS_COUNT = (
    1  # we have one disabled item from pg_eats_products.sql after update
)
BRANDS = [
    {
        'id': '1',
        'slug': 'brand1',
        'name': '0',
        'scale': 'aspect_fit',
    },  # ID:1 from pg_eats_products.sql
    {'id': '12', 'slug': 'a', 'name': 'A.A'},
    {'id': '345', 'slug': 'bcd', 'name': 'Бе Бэ'},
]

BRANDS_UPDATE_SLUG = [
    {
        'id': '1',
        'slug': 'super1',
        'name': '0',
        'scale': 'aspect_fit',
    },  # ID:1 from pg_eats_products.sql
    {'id': '12', 'slug': 'super2', 'name': 'A.A'},
    {'id': '345', 'slug': 'super3', 'name': 'Бе Бэ'},
]

BRANDS_UPDATE_PICTURE_SCALE = [
    {
        'id': '1',
        'slug': 'brand1',
        'name': '0',
        'scale': 'aspect_fill',
    },  # ID:1 from pg_eats_products.sql
    {'id': '12', 'slug': 'super2', 'name': 'A.A', 'scale': None},
    {'id': '345', 'slug': 'super3', 'name': 'Бе Бэ', 'scale': None},
]


def sql_get_brand_infos(pgsql):
    """Returns tuples (id, slug, is_enabled) for all brands"""

    cursor = pgsql['eats_products'].cursor()
    cursor.execute(
        """
        SELECT brand_id, slug, is_enabled
        FROM eats_products.brand
        ORDER BY brand_id
        """,
    )
    return list(cursor)


def sql_get_brand_with_scale_infos(pgsql) -> List[Tuple[str, str]]:
    """Returns tuples (id, picture_scale) for all brands"""

    cursor = pgsql['eats_products'].cursor()
    cursor.execute(
        """
        SELECT brand_id, picture_scale
        FROM eats_products.brand
        ORDER BY brand_id
        """,
    )
    return list(cursor)


def sql_get_brand_infos_short(pgsql):
    """Returns pairs (id, is_enabled) for all brands"""

    rows = sql_get_brand_infos(pgsql)
    return [(row[0], row[2]) for row in rows]


def sql_get_brand_ids(pgsql):
    """Returns brand ids of all brands (enabled and disabled)"""

    rows = sql_get_brand_infos(pgsql)
    return [row[0] for row in rows]


def sql_count_disabled_brands(pgsql):
    """Returns count of disabled brands"""

    rows = sql_get_brand_infos(pgsql)
    return sum(row[2] is False for row in rows)


async def test_insert(taxi_eats_products, mockserver, pgsql):
    @mockserver.json_handler(utils.Handlers.CORE_BRANDS)
    def _mock_eats_core_retail_mapping(request):
        return {'brands': BRANDS[1:]}

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_ids(pgsql) == BRAND_IDS
    assert sql_count_disabled_brands(pgsql) == DISABLED_IDS_COUNT


async def test_upsert(taxi_eats_products, mockserver, pgsql):
    @mockserver.json_handler(utils.Handlers.CORE_BRANDS)
    def _mock_eats_core_retail_mapping(request):
        return {'brands': brands}

    brands = [BRANDS[1]]
    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_ids(pgsql) == BRAND_IDS[0:2]
    assert sql_count_disabled_brands(pgsql) == DISABLED_IDS_COUNT

    brands.append(BRANDS[2])
    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_ids(pgsql) == BRAND_IDS
    assert sql_count_disabled_brands(pgsql) == DISABLED_IDS_COUNT


async def test_disable(taxi_eats_products, mockserver, pgsql):
    @mockserver.json_handler(utils.Handlers.CORE_BRANDS)
    def _mock_eats_core_retail_mapping(request):
        return {'brands': brands}

    brands = [BRANDS[1]]
    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_ids(pgsql) == BRAND_IDS[0:2]
    assert sql_count_disabled_brands(pgsql) == DISABLED_IDS_COUNT

    brands = [BRANDS[2]]
    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_infos_short(pgsql) == [
        (BRAND_IDS[0], False),
        (BRAND_IDS[1], False),
        (BRAND_IDS[2], True),
    ]

    brands = []
    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_infos_short(pgsql) == [
        (BRAND_IDS[0], False),
        (BRAND_IDS[1], False),
        (BRAND_IDS[2], False),
    ]

    brands = [BRANDS[1]]
    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_infos_short(pgsql) == [
        (BRAND_IDS[0], False),
        (BRAND_IDS[1], True),
        (BRAND_IDS[2], False),
    ]

    brands = BRANDS[1:]
    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_ids(pgsql) == BRAND_IDS
    assert sql_count_disabled_brands(pgsql) == DISABLED_IDS_COUNT


async def test_update_slug(taxi_eats_products, mockserver, pgsql):
    @mockserver.json_handler(utils.Handlers.CORE_BRANDS)
    def _mock_eats_core_retail_mapping(request):
        return {'brands': BRANDS_UPDATE_SLUG}

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_infos(pgsql) == [
        (int(row['id']), row['slug'], True) for row in BRANDS_UPDATE_SLUG
    ]
    assert sql_count_disabled_brands(pgsql) == 0


async def test_update_picture_scale(taxi_eats_products, mockserver, pgsql):
    @mockserver.json_handler(utils.Handlers.CORE_BRANDS)
    def _mock_eats_core_retail_mapping(request):
        return {'brands': BRANDS_UPDATE_PICTURE_SCALE}

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_with_scale_infos(pgsql) == [
        (int(row['id']), row['scale']) for row in BRANDS_UPDATE_PICTURE_SCALE
    ]
    assert sql_count_disabled_brands(pgsql) == 0


async def test_invalid_id(taxi_eats_products, mockserver, pgsql):
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
    valid_id_brands = [
        {'id': str(valid_id), 'slug': 'e', 'name': 'E'}
        for valid_id in valid_ids
    ]
    invalid_id_brands = [
        {'id': invalid_id, 'slug': 'e', 'name': 'E'}
        for invalid_id in invalid_ids
    ]

    @mockserver.json_handler(utils.Handlers.CORE_BRANDS)
    def _mock_eats_core_retail_mapping(request):
        return {
            'brands': [
                valid_id_brands[1],
                invalid_id_brands[0],
                valid_id_brands[0],
                *invalid_id_brands[1:],
                *valid_id_brands[2:],
            ],
        }

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_ids(pgsql) == list(map(int, valid_ids))
    assert sql_count_disabled_brands(pgsql) == 0
