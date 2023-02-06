import pytest


PLACE_ID = 1
MOCK_NOW = '2021-09-30T06:00:00+03:00'
FORCE_UNAVAILABLE_UNTIL = '2021-09-30T18:00:00+03:00'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'fill_autodisabled_products.sql',
    ],
)
async def test_update_autodisable_info(pg_realdict_cursor, stq_runner):
    await stq_runner.eats_nomenclature_autodisable_info_update.call(
        task_id=str(PLACE_ID),
        args=[],
        kwargs={
            'place_id': PLACE_ID,
            'products_info': [
                {
                    # update unavailability further in future
                    'origin_id': 'item_origin_1',
                    'force_unavailable_until': FORCE_UNAVAILABLE_UNTIL,
                },
                {
                    # reset unavailability to now
                    'origin_id': 'item_origin_2',
                    'force_unavailable_until': MOCK_NOW,
                },
                {
                    # set unavailability
                    'origin_id': 'item_origin_3',
                    'force_unavailable_until': FORCE_UNAVAILABLE_UNTIL,
                },
            ],
        },
        expect_fail=False,
    )

    assert _sql_get_updated_autodisabled_products(pg_realdict_cursor) == [
        {
            'place_id': 1,
            'origin_id': 'item_origin_1',
            'last_disabled_at': MOCK_NOW,
            'need_recalculation': True,
            'force_unavailable_until': FORCE_UNAVAILABLE_UNTIL,
        },
        {
            'place_id': 1,
            'origin_id': 'item_origin_2',
            'last_disabled_at': MOCK_NOW,
            'need_recalculation': True,
            'force_unavailable_until': MOCK_NOW,
        },
        {
            'place_id': 1,
            'origin_id': 'item_origin_3',
            'last_disabled_at': MOCK_NOW,
            'need_recalculation': True,
            'force_unavailable_until': FORCE_UNAVAILABLE_UNTIL,
        },
    ]


def _sql_get_updated_autodisabled_products(pg_realdict_cursor):
    pg_realdict_cursor.execute(
        f"""
        select
            ap.place_id as place_id,
            pr.origin_id as origin_id,
            ap.last_disabled_at as last_disabled_at,
            ap.need_recalculation as need_recalculation,
            pp.force_unavailable_until as force_unavailable_until
        from eats_nomenclature.autodisabled_products ap
        join eats_nomenclature.places_products pp
          on ap.place_id = pp.place_id and ap.product_id = pp.product_id
        join eats_nomenclature.products pr on pp.product_id = pr.id
        where ap.need_recalculation
        """,
    )
    result = pg_realdict_cursor.fetchall()
    for row in result:
        if row['last_disabled_at']:
            row['last_disabled_at'] = row['last_disabled_at'].isoformat('T')
        if row['force_unavailable_until']:
            row['force_unavailable_until'] = row[
                'force_unavailable_until'
            ].isoformat('T')
    return sorted(result, key=lambda k: k['origin_id'])
