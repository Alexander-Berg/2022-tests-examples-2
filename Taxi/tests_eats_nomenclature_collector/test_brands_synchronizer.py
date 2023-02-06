import pytest

EATS_CORE_RETAIL_RESPONSE = {
    'brands': [
        {'id': '1', 'slug': '1_remain_unchanged', 'name': 'A.A'},
        {'id': '2', 'slug': '2_to_enable', 'name': 'Бе Бэ'},
        {'id': '4', 'slug': '4_new_slug', 'name': 'с Сс'},
        {'id': '5', 'slug': '5_new_brand', 'name': 'd Дд'},
        {'id': '7', 'slug': '7_changed_name', 'name': 'new f Фф'},
    ],
}
OLD_UPDATED_AT = '2021-01-01T00:45:00+00:00'


async def test_brands_synchronizer(
        mockserver,
        testpoint,
        taxi_eats_nomenclature_collector,
        pg_cursor,
        to_utc_datetime,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/eats-core-retail/v1/brands/retrieve')
    def eats_core_retail(request):
        return EATS_CORE_RETAIL_RESPONSE

    @testpoint('eats_nomenclature_collector::brands-synchronizer')
    def handle_finished(arg):
        pass

    _sql_fill_brands(pg_cursor)

    await taxi_eats_nomenclature_collector.run_distlock_task(
        'brands-synchronizer',
    )
    handle_finished.next_call()

    brands_from_db = _sql_get_brands_from_db(pg_cursor, to_utc_datetime)

    not_updated_item_ids = ['1', '6']
    old_date = to_utc_datetime(OLD_UPDATED_AT).strftime('%Y-%m-%dT%H:%M')

    expected_brands = _get_expected_brands()
    for updated_brand, expected_brand in zip(brands_from_db, expected_brands):
        assert (
            updated_brand['id'] == expected_brand['id']
            and updated_brand['slug'] == expected_brand['slug']
            and updated_brand['is_enabled'] == expected_brand['is_enabled']
        )
        if updated_brand['id'] in not_updated_item_ids:
            assert updated_brand['updated_at'] == old_date
        else:
            assert updated_brand['updated_at'] != old_date


@pytest.mark.pgsql('eats_nomenclature_collector', files=[])
async def test_periodic_metrics(mockserver, verify_periodic_metrics):
    @mockserver.json_handler('/eats-core-retail/v1/brands/retrieve')
    def _eats_core_retail(request):
        return EATS_CORE_RETAIL_RESPONSE

    await verify_periodic_metrics('brands-synchronizer', is_distlock=True)


def _get_expected_brands():
    return [
        {'id': '1', 'slug': '1_remain_unchanged', 'is_enabled': True},
        {'id': '2', 'slug': '2_to_enable', 'is_enabled': True},
        {'id': '3', 'slug': '3_to_disable', 'is_enabled': False},
        {'id': '4', 'slug': '4_new_slug', 'is_enabled': True},
        {'id': '5', 'slug': '5_new_brand', 'is_enabled': True},
        {'id': '6', 'slug': '6_remain_disable', 'is_enabled': False},
        {'id': '7', 'slug': '7_changed_name', 'is_enabled': True},
    ]


def _sql_get_brands_from_db(pg_cursor, to_utc_datetime):
    pg_cursor.execute(
        """
        select id, slug, is_enabled, updated_at
        from eats_nomenclature_collector.brands
        order by id
        """,
    )
    rows = list(pg_cursor)
    for row in rows:
        row['updated_at'] = to_utc_datetime(row['updated_at']).strftime(
            '%Y-%m-%dT%H:%M',
        )
    return rows


def _sql_fill_brands(pg_cursor, old_updated_at=OLD_UPDATED_AT):
    old_brands = [
        {'id': '1', 'slug': '1_remain_unchanged', 'is_enabled': True},
        {'id': '2', 'slug': '2_to_enable', 'is_enabled': False},
        {'id': '3', 'slug': '3_to_disable', 'is_enabled': True},
        {'id': '4', 'slug': '4_changed_slug', 'is_enabled': True},
        {'id': '6', 'slug': '6_remain_disable', 'is_enabled': False},
    ]
    for brand in old_brands:
        pg_cursor.execute(
            """
                insert into eats_nomenclature_collector.brands
                    (id, slug, is_enabled, created_at, updated_at)
                values (%s, %s, %s, %s, %s)
                """,
            (
                brand['id'],
                brand['slug'],
                brand['is_enabled'],
                old_updated_at,
                old_updated_at,
            ),
        )
