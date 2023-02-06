CORE_BRANDS_HANDLER = '/eats-core-retail/v1/brands/retrieve'

PERIODIC_NAME = 'update-brands-from-core-periodic'

BRAND_IDS = [12, 345]
BRANDS_INFO = [
    {'id': 12, 'is_enabled': True, 'name': 'A.A', 'slug': 'a'},
    {'id': 345, 'is_enabled': True, 'name': 'Бе Бэ', 'slug': 'bcd'},
]

BRANDS = [
    {'id': '12', 'slug': 'a', 'name': 'A.A'},
    {'id': '345', 'slug': 'bcd', 'name': 'Бе Бэ'},
]


def sql_get_brand_infos(pgsql):
    """Returns (id, is_enabled, slug, name) for all brands"""

    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
        select id, is_enabled, slug, name, updated_at
        from eats_nomenclature.brands
        order by id
        """,
    )
    return list(cursor)


def sql_get_brand_ids(pgsql):
    """Returns brand ids of all brands (enabled and disabled)"""

    rows = sql_get_brand_infos(pgsql)
    return [row[0] for row in rows]


def get_brand_ids_to_updated_at(brands):
    return {brand['id']: brand['updated_at'] for brand in brands}


def sql_get_brand_infos_as_json(pgsql, include_updated_at=False):
    """Returns (id, is_enabled, slug, name) of all brands in json array"""
    rows = sql_get_brand_infos(pgsql)
    if include_updated_at:
        return [
            {
                'id': row[0],
                'is_enabled': row[1],
                'slug': row[2],
                'name': row[3],
                'updated_at': row[4],
            }
            for row in rows
        ]
    return [
        {'id': row[0], 'is_enabled': row[1], 'slug': row[2], 'name': row[3]}
        for row in rows
    ]


def sql_count_disabled_brands(pgsql):
    """Returns count of disabled brands"""

    rows = sql_get_brand_infos(pgsql)
    return sum(row[1] is False for row in rows)


def sql_insert_disabled_brand(pgsql, brand_id, slug, name):
    """Inserts a new disabled brand with slug and name from params"""
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
            insert into eats_nomenclature.brands (id, is_enabled, slug, name)
            values (%s, false, %s, %s)
            """,
        (brand_id, slug, name),
    )


async def test_insert(taxi_eats_nomenclature, mockserver, pgsql):
    @mockserver.json_handler(CORE_BRANDS_HANDLER)
    def _mock_eats_core_retail_mapping(request):
        return {'brands': BRANDS}

    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_ids(pgsql) == BRAND_IDS
    assert sql_count_disabled_brands(pgsql) == 0
    assert sql_get_brand_infos_as_json(pgsql) == BRANDS_INFO


async def test_upsert(taxi_eats_nomenclature, mockserver, pgsql):
    @mockserver.json_handler(CORE_BRANDS_HANDLER)
    def _mock_eats_core_retail_mapping(request):
        return {'brands': brands}

    brands = [BRANDS[0]]
    sql_insert_disabled_brand(pgsql, brands[0]['id'], slug=None, name=None)

    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_ids(pgsql) == [BRAND_IDS[0]]
    assert sql_count_disabled_brands(pgsql) == 0

    brands.append(BRANDS[1])
    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_ids(pgsql) == BRAND_IDS
    assert sql_count_disabled_brands(pgsql) == 0


async def test_disable(taxi_eats_nomenclature, mockserver, pgsql):
    @mockserver.json_handler(CORE_BRANDS_HANDLER)
    def _mock_eats_core_retail_mapping(request):
        return {'brands': brands}

    brands = [BRANDS[0]]
    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_ids(pgsql) == [BRAND_IDS[0]]
    assert sql_count_disabled_brands(pgsql) == 0

    brands = [BRANDS[1]]
    expected_infos = BRANDS_INFO
    expected_infos[0]['is_enabled'] = False
    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_infos_as_json(pgsql) == expected_infos

    brands = []
    expected_infos[1]['is_enabled'] = False
    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_infos_as_json(pgsql) == expected_infos

    brands = [BRANDS[0]]
    expected_infos[0]['is_enabled'] = True
    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_infos_as_json(pgsql) == expected_infos

    brands = BRANDS
    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_ids(pgsql) == BRAND_IDS
    assert sql_count_disabled_brands(pgsql) == 0


async def test_not_update_deleted_brands(
        taxi_eats_nomenclature, mockserver, pgsql,
):
    @mockserver.json_handler(CORE_BRANDS_HANDLER)
    def _mock_eats_core_retail_mapping(request):
        return {'brands': brands}

    brands = [BRANDS[0]]
    expected_infos = [BRANDS[0]]
    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)
    assert sql_count_disabled_brands(pgsql) == 0

    brands = []
    expected_infos[0]['is_enabled'] = False
    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)
    sql_brands = sql_get_brand_infos_as_json(pgsql, include_updated_at=True)
    brand_id_to_updated_at_prev = get_brand_ids_to_updated_at(sql_brands)

    brands = []
    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)
    brand_id_to_updated_at_new = get_brand_ids_to_updated_at(
        sql_get_brand_infos_as_json(pgsql, include_updated_at=True),
    )
    assert brand_id_to_updated_at_prev == brand_id_to_updated_at_new


async def test_invalid_id(taxi_eats_nomenclature, mockserver, pgsql):
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

    @mockserver.json_handler(CORE_BRANDS_HANDLER)
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

    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)
    assert sql_get_brand_ids(pgsql) == list(map(int, valid_ids))
    assert sql_count_disabled_brands(pgsql) == 0


async def test_periodic_metrics(mockserver, verify_periodic_metrics):
    @mockserver.json_handler(CORE_BRANDS_HANDLER)
    def _mock_eats_core_retail_mapping(request):
        return {'brands': []}

    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)
