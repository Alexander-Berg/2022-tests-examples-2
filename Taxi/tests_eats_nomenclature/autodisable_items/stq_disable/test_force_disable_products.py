import datetime as dt

import pytest


MOCK_NOW = '2021-09-30T15:00:00+03:00'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    EATS_NOMENCLATURE_AUTODISABLED_PRODUCTS={
        '__default__': {
            'disable_stages': [
                {
                    'not_picked_limit': 3,
                    'check_period_in_minutes': 720,
                    'disable_period_in_hours': 12,
                },
                {
                    'not_picked_limit': 3,
                    'check_period_in_minutes': 720,
                    'disable_period_in_hours': 36,
                },
                {
                    'not_picked_limit': 3,
                    'check_period_in_minutes': 720,
                    'disable_period_in_hours': 72,
                },
                {
                    'not_picked_limit': 3,
                    'check_period_in_minutes': 720,
                    'disable_period_in_hours': 300,
                },
            ],
        },
        '2': {
            'disable_stages': [
                {
                    'not_picked_limit': 10,
                    'check_period_in_minutes': 720,
                    'disable_period_in_hours': 12,
                },
            ],
        },
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
async def test_autodisabled_items(pg_realdict_cursor, stq_runner):
    await stq_runner.eats_picker_not_picked_items.call(
        task_id='1',
        args=[],
        kwargs={
            'place_id': '1',
            'not_picked_items': [
                {
                    'eats_item_id': 'item_origin_1',
                    'quantity': 7,
                    'quantity_picked': 3,
                },
                {
                    'eats_item_id': 'item_origin_2',
                    'quantity': 5,
                    'quantity_picked': 4,
                },
                {
                    'eats_item_id': 'item_origin_3',
                    'quantity': 10,
                    'quantity_picked': 1,
                },
                {
                    'eats_item_id': 'item_origin_4',
                    'quantity': 25,
                    'quantity_picked': 13,
                },
                {
                    'eats_item_id': 'item_origin_5',
                    'quantity': 3,
                    'quantity_picked': 0,
                },
                {
                    'eats_item_id': 'item_origin_6',
                    'quantity': 7,
                    'quantity_picked': 2,
                },
            ],
        },
    )
    assert sql_get_autodisabled_products(pg_realdict_cursor) == [
        {
            # not changing, because limit is not reached
            'place_id': 1,
            'product_id': 401,
            'disabled_count': 1,
            'last_disabled_at': '2021-09-29T17:00:00+03:00',
            'need_recalculation': False,
        },
        {
            # not changing, because limit is not reached
            'place_id': 1,
            'product_id': 402,
            'disabled_count': 2,
            'last_disabled_at': '2021-09-27T05:00:00+03:00',
            'need_recalculation': False,
        },
        {
            # disabled - limit is reached
            'place_id': 1,
            'product_id': 403,
            'disabled_count': 1,
            'last_disabled_at': MOCK_NOW,
            'need_recalculation': True,
        },
        {
            # disabled - limit is reached
            'place_id': 1,
            'product_id': 404,
            'disabled_count': 3,
            'last_disabled_at': MOCK_NOW,
            'need_recalculation': True,
        },
        {
            # disabled - limit is reached
            'place_id': 1,
            'product_id': 405,
            'disabled_count': 7,
            'last_disabled_at': MOCK_NOW,
            'need_recalculation': True,
        },
        {
            # not changing, because limit is not reached
            'place_id': 2,
            'product_id': 406,
            'disabled_count': 2,
            'last_disabled_at': '2020-01-01T00:00:00+03:00',
            'need_recalculation': False,
        },
        {
            # not changing, because no stq task was sent
            'place_id': 1,
            'product_id': 407,
            'disabled_count': 1,
            'last_disabled_at': '2020-01-01T00:00:00+03:00',
            'need_recalculation': False,
        },
    ]
    assert sql_get_places_products(pg_realdict_cursor) == [
        {
            # not changing, because limit is not reached
            'place_id': 1,
            'product_id': 401,
            'force_unavailable_until': '2021-09-30T05:00:00+03:00',
        },
        {
            # not changing, because limit is not reached
            'place_id': 1,
            'product_id': 402,
            'force_unavailable_until': '2021-09-30T05:00:00+03:00',
        },
        {
            # disabled - limit is reached (stage 0)
            'place_id': 1,
            'product_id': 403,
            'force_unavailable_until': get_time_with_delay(MOCK_NOW, hours=12),
        },
        {
            # disabled - limit is reached (stage 2)
            'place_id': 1,
            'product_id': 404,
            'force_unavailable_until': get_time_with_delay(MOCK_NOW, hours=72),
        },
        {
            # disabled - limit is reached (stage 3)
            'place_id': 1,
            'product_id': 405,
            'force_unavailable_until': get_time_with_delay(
                MOCK_NOW, hours=300,
            ),
        },
        {
            # not changing, because limit is not reached
            'place_id': 2,
            'product_id': 406,
            'force_unavailable_until': '2020-01-01T12:00:00+03:00',
        },
        {
            # not changing, because no stq task was sent
            'place_id': 1,
            'product_id': 407,
            'force_unavailable_until': '2020-01-01T12:00:00+03:00',
        },
    ]


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    EATS_NOMENCLATURE_YT_AUTODISABLE_PRODUCTS_SETTINGS={
        'enabled_place_ids': [1],
    },
    EATS_NOMENCLATURE_AUTODISABLED_PRODUCTS={
        '__default__': {
            'disable_stages': [
                {
                    'not_picked_limit': 1,
                    'check_period_in_minutes': 720,
                    'disable_period_in_hours': 12,
                },
                {
                    'not_picked_limit': 1,
                    'check_period_in_minutes': 720,
                    'disable_period_in_hours': 36,
                },
                {
                    'not_picked_limit': 1,
                    'check_period_in_minutes': 720,
                    'disable_period_in_hours': 72,
                },
                {
                    'not_picked_limit': 1,
                    'check_period_in_minutes': 720,
                    'disable_period_in_hours': 300,
                },
            ],
        },
    },
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data_for_test_ignore.sql'],
)
@pytest.mark.parametrize('yt_last_read_succeed', [True, False])
async def test_autodisabled_items_ignore(
        pg_realdict_cursor, stq_runner, yt_last_read_succeed,
):
    quantity_picked = 1
    quantity_requested = 10

    if not yt_last_read_succeed:
        sql_set_yt_processing_status(pg_realdict_cursor, '2021-09', 0, False)

    await stq_runner.eats_picker_not_picked_items.call(
        task_id='1',
        args=[],
        kwargs={
            'place_id': '1',
            'not_picked_items': [
                {
                    'eats_item_id': 'item_origin_1',
                    'quantity': quantity_requested,
                    'quantity_picked': quantity_picked,
                },
            ],
        },
    )
    await stq_runner.eats_picker_not_picked_items.call(
        task_id='2',
        args=[],
        kwargs={
            'place_id': '2',
            'not_picked_items': [
                {
                    'eats_item_id': 'item_origin_2',
                    'quantity': quantity_requested,
                    'quantity_picked': quantity_picked,
                },
            ],
        },
    )
    autodisabled_products_expected = [
        {
            'place_id': 2,
            'product_id': 402,
            'disabled_count': 1,
            'last_disabled_at': MOCK_NOW,
            'need_recalculation': True,
        },
    ]
    places_products_expected = [
        {'place_id': 1, 'product_id': 401, 'force_unavailable_until': None},
        {
            'place_id': 2,
            'product_id': 402,
            'force_unavailable_until': get_time_with_delay(MOCK_NOW, hours=12),
        },
    ]
    if not yt_last_read_succeed:
        # append to beginning, as getters from db sort output
        # with product_id asc
        autodisabled_products_expected.insert(
            0,
            {
                'place_id': 1,
                'product_id': 401,
                'disabled_count': 1,
                'last_disabled_at': MOCK_NOW,
                'need_recalculation': True,
            },
        )
        places_products_expected[0][
            'force_unavailable_until'
        ] = get_time_with_delay(MOCK_NOW, hours=12)

    assert (
        sql_get_autodisabled_products(pg_realdict_cursor)
        == autodisabled_products_expected
    )
    assert (
        sql_get_places_products(pg_realdict_cursor) == places_products_expected
    )
    assert sql_get_not_picked_items(pg_realdict_cursor) == [
        {
            'id': 1,
            'place_id': 1,
            'product_id': 401,
            'origin_id': 'item_origin_1',
            'quantity_requested': quantity_requested,
            'quantity_picked': quantity_picked,
        },
        {
            'id': 2,
            'place_id': 2,
            'product_id': 402,
            'origin_id': 'item_origin_2',
            'quantity_requested': quantity_requested,
            'quantity_picked': quantity_picked,
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


def get_time_with_delay(time, hours):
    return (
        dt.datetime.fromisoformat(time) + dt.timedelta(hours=hours)
    ).isoformat('T')


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


def sql_get_not_picked_items(pg_realdict_cursor):
    pg_realdict_cursor.execute(
        f"""
        select
            id,
            place_id,
            product_id,
            origin_id,
            quantity_requested,
            quantity_picked
        from eats_nomenclature.not_picked_items
        """,
    )
    result = pg_realdict_cursor.fetchall()
    return sorted(result, key=lambda k: k['product_id'])
