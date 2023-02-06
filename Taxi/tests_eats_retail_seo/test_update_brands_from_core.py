import pytest

CORE_BRANDS_HANDLER = '/eats-core-retail/v1/brands/retrieve'
PERIODIC_NAME = 'update-brands-from-core-periodic'
MOCK_NOW = '2021-02-18T20:00:00+00:00'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    EATS_RETAIL_SEO_PERIODICS={
        '__default__': {'is_enabled': False, 'period_in_sec': 1800},
        PERIODIC_NAME: {'is_enabled': True, 'period_in_sec': 1800},
    },
)
async def test_update_brands_from_core(
        taxi_eats_retail_seo, mockserver, pgsql, to_utc_datetime,
):
    old_brands = [
        {
            'id': '1',
            'slug': '1_remain_unchanged',
            'name': 'A.A',
            'is_enabled': True,
        },
        {
            'id': '2',
            'slug': '2_to_enable',
            'name': 'Бе Бэ',
            'is_enabled': False,
        },
        {
            'id': '3',
            'slug': '3_to_disable',
            'name': 'disabled brand',
            'is_enabled': True,
        },
        {
            'id': '4',
            'slug': '4_changed_slug',
            'name': 'с Сс',
            'is_enabled': True,
        },
        {
            'id': '6',
            'slug': '6_remain_disable',
            'name': 'e Ее',
            'is_enabled': False,
        },
        {
            'id': '7',
            'slug': '7_changed_name',
            'name': 'f Фф',
            'is_enabled': True,
        },
    ]
    old_updated_at = '2021-01-01T00:45:00+00:00'
    _sql_insert_brands(pgsql, old_brands, old_updated_at)
    not_updated_item_ids = ['1', '6']

    brands_from_core = [
        {'id': '1', 'slug': '1_remain_unchanged', 'name': 'A.A'},
        {'id': '2', 'slug': '2_to_enable', 'name': 'Бе Бэ'},
        {'id': '4', 'slug': '4_new_slug', 'name': 'с Сс'},
        {'id': '5', 'slug': '5_new_brand', 'name': 'd Дд'},
        {'id': '7', 'slug': '7_changed_name', 'name': 'new f Фф'},
    ]

    @mockserver.json_handler(CORE_BRANDS_HANDLER)
    def _mock_eats_core_retail_mapping(request):
        return {'brands': brands_from_core}

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)

    old_date = to_utc_datetime(old_updated_at).strftime('%Y-%m-%dT%H:%M')
    expected_brands_info = [
        {
            'id': '1',
            'slug': '1_remain_unchanged',
            'name': 'A.A',
            'is_enabled': True,
        },
        {
            'id': '2',
            'slug': '2_to_enable',
            'name': 'Бе Бэ',
            'is_enabled': True,
        },
        {
            'id': '3',
            'slug': '3_to_disable',
            'name': 'disabled brand',
            'is_enabled': False,
        },
        {'id': '4', 'slug': '4_new_slug', 'name': 'с Сс', 'is_enabled': True},
        {'id': '5', 'slug': '5_new_brand', 'name': 'd Дд', 'is_enabled': True},
        {
            'id': '6',
            'slug': '6_remain_disable',
            'name': 'e Ее',
            'is_enabled': False,
        },
        {
            'id': '7',
            'slug': '7_changed_name',
            'name': 'new f Фф',
            'is_enabled': True,
        },
    ]

    expected_brands_info = sorted(
        expected_brands_info, key=lambda item: item['id'],
    )
    updated_brands_info = sorted(
        _sql_get_brand_infos_as_json(pgsql, to_utc_datetime),
        key=lambda item: item['id'],
    )
    for updated_brand, expected_brand in zip(
            updated_brands_info, expected_brands_info,
    ):
        assert (
            updated_brand['id'] == expected_brand['id']
            and updated_brand['slug'] == expected_brand['slug']
            and updated_brand['name'] == expected_brand['name']
            and updated_brand['is_enabled'] == expected_brand['is_enabled']
        )
        if updated_brand['id'] in not_updated_item_ids:
            assert updated_brand['updated_at'] == old_date
        else:
            assert updated_brand['updated_at'] != old_date


async def test_periodic_metrics(mockserver, verify_periodic_metrics):
    @mockserver.json_handler(CORE_BRANDS_HANDLER)
    def _mock_eats_core_retail_mapping(request):
        return {'brands': []}

    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def _sql_get_brand_infos_as_json(pgsql, to_utc_datetime):
    cursor = pgsql['eats_retail_seo'].cursor()
    cursor.execute(
        """
        select id, slug, name, is_enabled, updated_at
        from eats_retail_seo.brands
        order by id
        """,
    )
    rows = list(cursor)
    return [
        {
            'id': row[0],
            'slug': row[1],
            'name': row[2],
            'is_enabled': row[3],
            'updated_at': to_utc_datetime(row[4]).strftime('%Y-%m-%dT%H:%M'),
        }
        for row in rows
    ]


def _sql_insert_brands(pgsql, brands, updated_at):
    cursor = pgsql['eats_retail_seo'].cursor()
    for brand in brands:
        cursor.execute(
            """
                insert into eats_retail_seo.brands
                    (id, slug, name, is_enabled, created_at, updated_at)
                values (%s, %s, %s, %s, %s, %s)
                """,
            (
                brand['id'],
                brand['slug'],
                brand['name'],
                brand['is_enabled'],
                updated_at,
                updated_at,
            ),
        )
