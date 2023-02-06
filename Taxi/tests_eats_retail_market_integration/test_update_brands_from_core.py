import datetime as dt

import pytest

CORE_BRANDS_HANDLER = '/eats-core-retail/v1/brands/retrieve'
PERIODIC_NAME = 'update-brands-from-core-periodic'


@pytest.mark.config(
    EATS_RETAIL_MARKET_INTEGRATION_PERIODICS={
        PERIODIC_NAME: {'is_enabled': True, 'period_in_sec': 1800},
    },
)
async def test_updating_brands_from_core(
        taxi_eats_retail_market_integration,
        mockserver,
        pgsql,
        to_utc_datetime,
):
    old_brands = [
        {'id': '1', 'slug': '1_remain_unchanged', 'is_enabled': True},
        {'id': '2', 'slug': '2_to_enable', 'is_enabled': False},
        {'id': '3', 'slug': '3_to_disable', 'is_enabled': True},
        {'id': '4', 'slug': '4_changed_slug', 'is_enabled': True},
        {'id': '6', 'slug': '6_remain_disable', 'is_enabled': False},
    ]
    old_updated_at = '2021-01-01T00:45:00+00:00'
    _sql_insert_brands(pgsql, old_brands, old_updated_at)

    brands_from_core = [
        {'id': '1', 'slug': '1_remain_unchanged', 'name': 'A.A'},
        {'id': '2', 'slug': '2_to_enable', 'name': 'Бе Бэ'},
        {'id': '4', 'slug': '4_new_slug', 'name': 'с Сс'},
        {'id': '5', 'slug': '5_new_brand', 'name': 'd Дд'},
    ]

    @mockserver.json_handler(CORE_BRANDS_HANDLER)
    def _mock_eats_core_retail_mapping(request):
        return {'brands': brands_from_core}

    await taxi_eats_retail_market_integration.run_distlock_task(PERIODIC_NAME)

    now_date = dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M')
    old_date = to_utc_datetime(old_updated_at).strftime('%Y-%m-%dT%H:%M')
    expected_brands_info = [
        {
            'id': '1',
            'slug': '1_remain_unchanged',
            'is_enabled': True,
            'updated_at': old_date,
        },
        {
            'id': '2',
            'slug': '2_to_enable',
            'is_enabled': True,
            'updated_at': now_date,
        },
        {
            'id': '3',
            'slug': '3_to_disable',
            'is_enabled': False,
            'updated_at': now_date,
        },
        {
            'id': '4',
            'slug': '4_new_slug',
            'is_enabled': True,
            'updated_at': now_date,
        },
        {
            'id': '5',
            'slug': '5_new_brand',
            'is_enabled': True,
            'updated_at': now_date,
        },
        {
            'id': '6',
            'slug': '6_remain_disable',
            'is_enabled': False,
            'updated_at': old_date,
        },
    ]
    assert (
        _sql_get_brand_infos_as_json(pgsql, to_utc_datetime)
        == expected_brands_info
    )


async def test_periodic_metrics(mockserver, verify_periodic_metrics):
    @mockserver.json_handler(CORE_BRANDS_HANDLER)
    def _mock_eats_core_retail_mapping(request):
        return {'brands': []}

    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def _sql_get_brand_infos_as_json(pgsql, to_utc_datetime):
    cursor = pgsql['eats_retail_market_integration'].cursor()
    cursor.execute(
        """
        select id, slug, is_enabled, updated_at
        from eats_retail_market_integration.brands
        order by id
        """,
    )
    rows = list(cursor)
    return [
        {
            'id': row[0],
            'slug': row[1],
            'is_enabled': row[2],
            'updated_at': to_utc_datetime(row[3]).strftime('%Y-%m-%dT%H:%M'),
        }
        for row in rows
    ]


def _sql_insert_brands(pgsql, brands, updated_at):
    cursor = pgsql['eats_retail_market_integration'].cursor()
    for brand in brands:
        cursor.execute(
            """
                insert into eats_retail_market_integration.brands
                    (id, slug, is_enabled, created_at, updated_at)
                values (%s, %s, %s, %s, %s)
                """,
            (
                brand['id'],
                brand['slug'],
                brand['is_enabled'],
                updated_at,
                updated_at,
            ),
        )
