import pytest


CORE_RETAIL_SYNC_HANDLER = '/eats-core-retail/v1/brand/places/retrieve'

PERIODIC_NAME = 'core-sync-periodic'


@pytest.mark.pgsql('eats_nomenclature', files=['fill_dictionaries.sql'])
async def test_core_sync(
        pg_cursor,
        pg_realdict_cursor,
        mockserver,
        taxi_eats_nomenclature,
        taxi_eats_nomenclature_monitor,
):
    known_brand_ids = [5, 6, 7, 8]

    old_places = [
        {
            'brand_id': 5,
            'place_id': 1,
            'place_slug': '5_1_should_change_slug',
            'is_enabled': False,
            'has_active_assortment': True,
            'stock_reset_limit': 0,
        },
        {
            'brand_id': 5,
            'place_id': 2,
            'place_slug': '5_2_should_remain_unchanged',
            'is_enabled': False,
            'has_active_assortment': True,
            'stock_reset_limit': 0,
        },
        {
            'brand_id': 5,
            'place_id': 3,
            'place_slug': '5_3_should_change_brand',
            'is_enabled': False,
            'has_active_assortment': True,
            'stock_reset_limit': 0,
        },
        {
            'brand_id': 5,
            'place_id': 8,
            'place_slug': '5_8_unchanged_no_assortment',
            'is_enabled': True,
            'has_active_assortment': False,
            'stock_reset_limit': 0,
        },
        {
            'brand_id': 7,
            'place_id': 4,
            'place_slug': '7_4_should_be_disabled',
            'is_enabled': True,
            'has_active_assortment': True,
            'stock_reset_limit': 0,
        },
        {
            'brand_id': 8,
            'place_id': 81,
            'place_slug': '8_81_should_have_limit_changed',
            'is_enabled': True,
            'has_active_assortment': True,
            'stock_reset_limit': 10,
        },
        {
            'brand_id': 8,
            'place_id': 82,
            'place_slug': '8_82_should_have_limit_zeroed',
            'is_enabled': True,
            'has_active_assortment': True,
            'stock_reset_limit': 10,
        },
    ]
    old_places_dict = {i['place_id']: i for i in old_places}

    new_places = [
        {
            'brand_id': 5,
            'place_id': 1,
            'place_slug': '5_1_change_slug',
            'is_enabled': True,
            'has_active_assortment': True,
        },
        {
            'brand_id': 5,
            'place_id': 5,
            'place_slug': '5_5_new_enabled_place',
            'is_enabled': True,
            'has_active_assortment': True,
        },
        {
            'brand_id': 5,
            'place_id': 8,
            'place_slug': '5_8_unchanged_no_assortment',
            'is_enabled': True,
            'has_active_assortment': False,
        },
        {
            'brand_id': 6,
            'place_id': 3,
            'place_slug': '6_3_change_brand',
            'is_enabled': False,
            'has_active_assortment': True,
        },
        {
            'brand_id': 6,
            'place_id': 6,
            'place_slug': '6_6_new_disabled_place',
            'is_enabled': False,
            'has_active_assortment': True,
        },
        {
            'brand_id': 6,
            'place_id': 7,
            'place_slug': '6_7_new_disabled_place',
            'is_enabled': False,
            'has_active_assortment': True,
        },
        {
            'brand_id': 8,
            'place_id': 81,
            'place_slug': '8_81_should_have_limit_changed',
            'is_enabled': True,
            'has_active_assortment': True,
            'stock_reset_limit': 20,
        },
        {
            'brand_id': 8,
            'place_id': 82,
            'place_slug': '8_82_should_have_limit_zeroed',
            'is_enabled': True,
            'has_active_assortment': True,
        },
    ]
    new_places_dict = {i['place_id']: i for i in new_places}

    merged_places_dict = old_places_dict.copy()
    merged_places_dict.update(new_places_dict)
    for i in merged_places_dict.values():
        i['is_enabled'] = (
            i['place_id'] in new_places_dict
            and new_places_dict[i['place_id']]['is_enabled']
        )
    merged_places = list(merged_places_dict.values())

    @mockserver.json_handler(CORE_RETAIL_SYNC_HANDLER)
    def _mock_eats_core_retail_mapping(request):
        places = [
            place
            for place in new_places
            if str(place['brand_id']) == request.query['brand_id']
        ]
        return {
            'places': [
                {
                    'id': str(place['place_id']),
                    'slug': place['place_slug'],
                    'enabled': place['is_enabled'],
                    'parser_enabled': True,
                    'stock_reset_limit': place.get('stock_reset_limit'),
                }
                for place in places
            ],
            'meta': {'limit': len(places)},
        }

    _sql_set_brands(pg_cursor, known_brand_ids)
    _sql_set_places(pg_cursor, old_places)
    _sql_set_brand_places(pg_cursor, old_places)
    _sql_set_place_assortment(pg_cursor, old_places)

    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)

    # Verify brands

    sql_brand_ids = _sql_get_brands(pg_cursor)
    assert set(sql_brand_ids) == {i['brand_id'] for i in merged_places}

    # Verify places

    sql_places = _sql_get_places(pg_cursor)
    assert (
        sorted_by_place_id(
            [
                {
                    'place_id': i['place_id'],
                    'place_slug': i['place_slug'],
                    'is_enabled': i['is_enabled'],
                    'stock_reset_limit': i['stock_reset_limit'],
                }
                for i in sql_places
            ],
        )
        == sorted_by_place_id(
            [
                {
                    'place_id': i['place_id'],
                    'place_slug': i['place_slug'],
                    'is_enabled': i['is_enabled'],
                    'stock_reset_limit': i.get('stock_reset_limit', 0),
                }
                for i in merged_places
            ],
        )
    )

    # Verify brand places

    sql_brand_places = _sql_get_brand_places(pg_realdict_cursor)
    assert sorted_by_place_id(sql_brand_places) == sorted_by_place_id(
        [
            {'brand_id': i['brand_id'], 'place_id': i['place_id']}
            for i in merged_places
        ],
    )

    # Verify metrics

    places_without_assortments = sum(
        1
        for place in new_places
        if place['is_enabled']
        and (
            place['place_id'] not in old_places_dict
            or not place['has_active_assortment']
        )
    )

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    assert metrics[PERIODIC_NAME] == {
        'unsynced_place_count': places_without_assortments,
    }

    # Repeat to check that updated_at doesn't change for deleted places

    place_id_to_place_prev = {place['place_id']: place for place in sql_places}

    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)

    deleted_places = [
        place['place_id'] for place in old_places if place not in new_places
    ]
    sql_places = _sql_get_places(pg_cursor)

    for place in sql_places:
        if place['place_id'] in deleted_places:
            assert (
                place['updated_at']
                == place_id_to_place_prev[place['place_id']]['updated_at']
            )


@pytest.mark.pgsql('eats_nomenclature', files=['fill_dictionaries.sql'])
async def test_periodic_metrics(mockserver, verify_periodic_metrics):
    @mockserver.json_handler(CORE_RETAIL_SYNC_HANDLER)
    def _mock_eats_core_retail_mapping(request):
        return {}

    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def sorted_by_place_id(places):
    return sorted(places, key=lambda item: item['place_id'])


def _sql_set_brands(pg_cursor, brand_ids):
    pg_cursor.execute(
        """
        insert into eats_nomenclature.brands (id, is_enabled)
        values (unnest(%s), true)
        """,
        (brand_ids,),
    )


def _sql_set_places(pg_cursor, places):
    for i in places:
        pg_cursor.execute(
            """
            insert into eats_nomenclature.places (
                id, slug, is_enabled, stock_reset_limit
            )
            values(
                %(place_id)s,
                %(place_slug)s,
                %(is_enabled)s,
                %(stock_reset_limit)s
            )
            """,
            i,
        )


def _sql_set_brand_places(pg_cursor, places):
    for i in places:
        pg_cursor.execute(
            """
            insert into eats_nomenclature.brand_places (
                brand_id, place_id
            )
            values(
                %(brand_id)s,
                %(place_id)s
            )
            """,
            i,
        )


def _sql_set_place_assortment(pg_cursor, places):
    pg_cursor.execute(
        """
        insert into eats_nomenclature.assortments
        default values
        returning id
        """,
    )
    assortment_id = pg_cursor.fetchone()[0]

    for place in places:
        pg_cursor.execute(
            """
            insert into eats_nomenclature.place_assortments
              (place_id, assortment_id)
            values (%s, %s)
            """,
            (
                place['place_id'],
                assortment_id if place['has_active_assortment'] else None,
            ),
        )


def _sql_get_brands(pg_cursor):
    pg_cursor.execute(
        """
        select id
        from eats_nomenclature.brands
        """,
    )
    return [i[0] for i in pg_cursor]


def _sql_get_places(pg_cursor):
    pg_cursor.execute(
        """
        select id, slug, is_enabled, updated_at, stock_reset_limit
        from eats_nomenclature.places
        """,
    )
    return [
        {
            'place_id': i[0],
            'place_slug': i[1],
            'is_enabled': i[2],
            'updated_at': i[3],
            'stock_reset_limit': i[4],
        }
        for i in pg_cursor
    ]


def _sql_get_brand_places(pg_realdict_cursor):
    pg_realdict_cursor.execute(
        f"""
        select brand_id, place_id
        from eats_nomenclature.brand_places
        """,
    )
    return pg_realdict_cursor.fetchall()
