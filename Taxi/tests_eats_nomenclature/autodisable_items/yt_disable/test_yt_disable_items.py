import pytest


MOCK_NOW = '2021-09-20T15:00:00+03:00'
PERIODIC_NAME = 'yt-disable-products-periodic'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    EATS_NOMENCLATURE_YT_AUTODISABLE_PRODUCTS_SETTINGS={
        'enabled_place_ids': [1],
        'yt_path_prefix': '//nomenclature_hide_info/',
    },
    EATS_NOMENCLATURE_PERIODICS={
        '__default__': {'is_enabled': True, 'period_in_sec': 60},
    },
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'fill_autodisabled_products.sql',
    ],
)
@pytest.mark.yt(
    schemas=['yt_disable_schema.yaml'],
    static_table_data=['yt_disable_data.yaml'],
)
@pytest.mark.parametrize(
    'yt_processing_status_state', ['empty', 'outdated', 'up-to-date'],
)
async def test_yt_disabled_items(
        taxi_eats_nomenclature,
        testpoint,
        pg_realdict_cursor,
        yt_apply,
        yt_processing_status_state,
):
    @testpoint('yt-disable-products-periodic-finished')
    def periodic_end_run(param):
        pass

    if yt_processing_status_state == 'outdated':
        sql_set_yt_processing_status(pg_realdict_cursor, '2021-08', 0, True)
    elif yt_processing_status_state == 'up-to-date':
        sql_set_yt_processing_status(pg_realdict_cursor, '2021-09', 0, True)

    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)
    assert periodic_end_run.times_called == 1

    if yt_processing_status_state == 'outdated':
        # need to launch periodic once more to start read new table
        await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)
        assert periodic_end_run.times_called == 2

    assert sql_get_yt_processing_status(pg_realdict_cursor) == [
        {
            'last_read_table_name': '2021-09',
            'row_to_read_from': 5,
            'last_read_succeed': True,
        },
    ]

    assert sql_get_autodisabled_products(pg_realdict_cursor) == [
        # 1632132000000: 2021.09.20 10:00:00 UTC - old start_time
        # 1632135600000: 2021.09.20 11:00:00 UTC - time of YT updating
        # 1632139200000: 2021.09.20 12:00:00 UTC = NOW
        {
            'disabled_count': 0,
            'last_disabled_at': MOCK_NOW,
            'need_recalculation': True,
            'place_id': 1,
            'product_id': 401,
        },
        {
            'disabled_count': 0,
            'last_disabled_at': MOCK_NOW,
            'need_recalculation': True,
            'place_id': 1,
            'product_id': 402,
        },
        {
            'disabled_count': 2,
            'last_disabled_at': '2020-01-01T00:00:00+03:00',
            'need_recalculation': False,
            'place_id': 1,
            'product_id': 404,
        },
        {
            'disabled_count': 2,
            'last_disabled_at': '2020-01-01T00:00:00+03:00',
            'need_recalculation': False,
            'place_id': 2,
            'product_id': 406,
        },
    ]
    assert sql_get_places_products(pg_realdict_cursor) == [
        {
            'force_unavailable_until': '2021-09-20T16:00:00+03:00',
            'place_id': 1,
            'product_id': 401,
        },
        {
            'force_unavailable_until': '2021-09-20T15:00:00+03:00',
            'place_id': 1,
            'product_id': 402,
        },
        {'force_unavailable_until': None, 'place_id': 1, 'product_id': 403},
        {
            'force_unavailable_until': '2020-01-04T00:00:00+03:00',
            'place_id': 1,
            'product_id': 404,
        },
        {'force_unavailable_until': None, 'place_id': 1, 'product_id': 405},
        {
            'force_unavailable_until': '2020-01-01T12:00:00+03:00',
            'place_id': 2,
            'product_id': 406,
        },
    ]


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    EATS_NOMENCLATURE_YT_AUTODISABLE_PRODUCTS_SETTINGS={
        'enabled_place_ids': [1],
        'yt_path_prefix': '//nomenclature_hide_info/',
    },
    EATS_NOMENCLATURE_PERIODICS={
        '__default__': {'is_enabled': True, 'period_in_sec': 60},
    },
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'fill_autodisabled_products.sql',
    ],
)
@pytest.mark.yt(
    schemas=['yt_disable_schema.yaml'],
    static_table_data=['yt_disable_data_outdated_table.yaml'],
)
async def test_yt_disabled_items_from_outdated_table(
        taxi_eats_nomenclature, testpoint, pg_realdict_cursor, yt_apply,
):
    @testpoint('yt-disable-products-periodic-finished')
    def periodic_end_run(param):
        pass

    sql_set_yt_processing_status(pg_realdict_cursor, '2021-08', 0, True)

    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)

    assert periodic_end_run.times_called == 1

    assert sql_get_yt_processing_status(pg_realdict_cursor) == [
        {
            'last_read_table_name': '2021-09',
            'row_to_read_from': 0,
            'last_read_succeed': True,
        },
    ]

    assert sql_get_autodisabled_products(pg_realdict_cursor) == [
        # 1632132000000: 2021.09.20 10:00:00 UTC - old start_time
        # 1632135600000: 2021.09.20 11:00:00 UTC - time of YT updating
        # 1632139200000: 2021.09.20 12:00:00 UTC = NOW
        {
            'disabled_count': 0,
            'last_disabled_at': MOCK_NOW,
            'need_recalculation': True,
            'place_id': 1,
            'product_id': 401,
        },
        {
            'disabled_count': 0,
            'last_disabled_at': MOCK_NOW,
            'need_recalculation': True,
            'place_id': 1,
            'product_id': 402,
        },
        {
            'disabled_count': 2,
            'last_disabled_at': '2020-01-01T00:00:00+03:00',
            'need_recalculation': False,
            'place_id': 1,
            'product_id': 404,
        },
        {
            'disabled_count': 2,
            'last_disabled_at': '2020-01-01T00:00:00+03:00',
            'need_recalculation': False,
            'place_id': 2,
            'product_id': 406,
        },
    ]
    assert sql_get_places_products(pg_realdict_cursor) == [
        {
            'force_unavailable_until': '2021-09-20T16:00:00+03:00',
            'place_id': 1,
            'product_id': 401,
        },
        {
            'force_unavailable_until': '2021-09-20T15:00:00+03:00',
            'place_id': 1,
            'product_id': 402,
        },
        {'force_unavailable_until': None, 'place_id': 1, 'product_id': 403},
        {
            'force_unavailable_until': '2020-01-04T00:00:00+03:00',
            'place_id': 1,
            'product_id': 404,
        },
        {'force_unavailable_until': None, 'place_id': 1, 'product_id': 405},
        {
            'force_unavailable_until': '2020-01-01T12:00:00+03:00',
            'place_id': 2,
            'product_id': 406,
        },
    ]


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    EATS_NOMENCLATURE_YT_AUTODISABLE_PRODUCTS_SETTINGS={
        'enabled_place_ids': [1],
        'yt_path_prefix': '//nomenclature_hide_info/',
    },
    EATS_NOMENCLATURE_PERIODICS={
        '__default__': {'is_enabled': True, 'period_in_sec': 60},
    },
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'fill_autodisabled_products.sql',
    ],
)
async def test_yt_disabled_items_when_yt_fails(
        taxi_eats_nomenclature, testpoint, pg_realdict_cursor,
):
    @testpoint('yt-disable-products-periodic-finished')
    def periodic_end_run(param):
        pass

    @testpoint('BatchReadTableFrom::fail')
    def yt_read_fail_testpoint(param):
        return {'inject_failure': True}

    sql_set_yt_processing_status(pg_realdict_cursor, '2021-09', 0, True)

    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)

    assert periodic_end_run.times_called == 0
    assert yt_read_fail_testpoint.has_calls

    assert sql_get_yt_processing_status(pg_realdict_cursor) == [
        {
            'last_read_table_name': '2021-09',
            'row_to_read_from': 0,
            'last_read_succeed': False,
        },
    ]

    assert sql_get_autodisabled_products(pg_realdict_cursor) == [
        # 1632132000000: 2021.09.20 10:00:00 UTC - old start_time
        # 1632135600000: 2021.09.20 11:00:00 UTC - time of YT updating
        # 1632139200000: 2021.09.20 12:00:00 UTC = MOCK_NOW
        {
            'disabled_count': 1,
            'last_disabled_at': '2021-09-29T17:00:00+03:00',
            'need_recalculation': False,
            'place_id': 1,
            'product_id': 401,
        },
        {
            'disabled_count': 2,
            'last_disabled_at': '2021-09-27T05:00:00+03:00',
            'need_recalculation': False,
            'place_id': 1,
            'product_id': 402,
        },
        {
            'disabled_count': 2,
            'last_disabled_at': '2020-01-01T00:00:00+03:00',
            'need_recalculation': False,
            'place_id': 1,
            'product_id': 404,
        },
        {
            'disabled_count': 2,
            'last_disabled_at': '2020-01-01T00:00:00+03:00',
            'need_recalculation': False,
            'place_id': 2,
            'product_id': 406,
        },
    ]
    assert sql_get_places_products(pg_realdict_cursor) == [
        {
            'force_unavailable_until': '2021-08-30T05:00:00+03:00',
            'place_id': 1,
            'product_id': 401,
        },
        {
            'force_unavailable_until': '2021-08-30T05:00:00+03:00',
            'place_id': 1,
            'product_id': 402,
        },
        {'force_unavailable_until': None, 'place_id': 1, 'product_id': 403},
        {
            'force_unavailable_until': '2020-01-04T00:00:00+03:00',
            'place_id': 1,
            'product_id': 404,
        },
        {'force_unavailable_until': None, 'place_id': 1, 'product_id': 405},
        {
            'force_unavailable_until': '2020-01-01T12:00:00+03:00',
            'place_id': 2,
            'product_id': 406,
        },
    ]


def sql_get_autodisabled_products(pg_realdict_cursor):
    pg_realdict_cursor.execute(
        f"""
        select
            place_id,
            product_id,
            disabled_count,
            last_disabled_at,
            need_recalculation
        from eats_nomenclature.autodisabled_products
        """,
    )
    result = pg_realdict_cursor.fetchall()
    for row in result:
        if row['last_disabled_at']:
            row['last_disabled_at'] = row['last_disabled_at'].isoformat('T')
    return sorted(result, key=lambda k: k['product_id'])


def sql_get_places_products(pg_realdict_cursor):
    pg_realdict_cursor.execute(
        f"""
        select
            place_id,
            product_id,
            force_unavailable_until
        from eats_nomenclature.places_products
        """,
    )
    result = pg_realdict_cursor.fetchall()
    for row in result:
        if row['force_unavailable_until']:
            row['force_unavailable_until'] = row[
                'force_unavailable_until'
            ].isoformat('T')
    return sorted(result, key=lambda k: k['product_id'])


def sql_get_yt_processing_status(pg_realdict_cursor):
    pg_realdict_cursor.execute(
        f"""
        select last_read_table_name, row_to_read_from, last_read_succeed
        from eats_nomenclature.yt_disabled_products_processing_status
        """,
    )
    result = pg_realdict_cursor.fetchall()
    return result


def sql_set_yt_processing_status(
        pg_realdict_cursor,
        last_read_table_name,
        row_to_read_from,
        last_read_succeed,
):
    pg_realdict_cursor.execute(
        f"""
        insert into eats_nomenclature.yt_disabled_products_processing_status
        (last_read_table_name, row_to_read_from, last_read_succeed)
        values (
          '{last_read_table_name}',
           {row_to_read_from},
           {last_read_succeed}
        )
        """,
    )
