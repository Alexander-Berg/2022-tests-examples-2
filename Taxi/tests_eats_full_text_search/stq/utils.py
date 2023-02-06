def get_all_places(cursor):
    cursor.execute(
        """
        SELECT
            place_id,
            place_slug,
            brand_id,
            enabled,
            updated_at
        FROM
            fts.place;
    """,
    )
    return list(cursor)


def get_brand_scale(cursor, brand_id):
    cursor.execute(
        """
        SELECT
            picture_scale
        FROM
            fts.brand
        WHERE
            brand_id = %s
        LIMIT 1;
    """,
        (brand_id,),
    )
    return list(cursor)[0]['picture_scale']


def get_items_mapping(cursor, place_id):
    cursor.execute(
        """
        SELECT
            core_id,
            core_parent_category_id,
            origin_id,
            updated_at
        FROM
            fts.items_mapping
        WHERE
            place_id = %s
        ORDER BY core_id;
    """,
        (place_id,),
    )
    return list(cursor)
