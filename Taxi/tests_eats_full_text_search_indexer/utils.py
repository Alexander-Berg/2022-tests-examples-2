def add_place_state(cursor, place_id, place_slug, etag=None, enabled=True):
    cursor.execute(
        """
        INSERT INTO
            fts_indexer.place_state
            (place_id, place_slug, enabled, etag)
        VALUES
            (%s, %s, %s, %s )
    """,
        (place_id, place_slug, enabled, etag),
    )


def places_state_by_place_id(cursor, place_id):
    cursor.execute(
        """
        SELECT
            place_id,
            etag
        FROM
            fts_indexer.place_state
        WHERE place_id = %s
    """,
        (place_id,),
    )
    place_state_data = list(
        {'place_id': row[0], 'etag': row[1]} for row in cursor
    )
    return place_state_data
