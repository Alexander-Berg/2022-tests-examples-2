def pg_response_to_dict(cursor):
    res = []
    for row in cursor.fetchall():
        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]
    return res


def get_orders(cursor):
    cursor.execute(
        f"""
        SELECT id, park_id, contractor_id, location_from, locations_to,
               created_at, client_booked_at, cancelled_at, processed_at,
               record_created_at, record_updated_at, source_park_id,
               zone_id, tariff_class, duration_estimate, address_from,
               addresses_to, driver_price, comment, distance, durations,
               event_index
        FROM fleet.guaranteed_order
        ORDER BY id
        """,
    )

    return pg_response_to_dict(cursor)


def get_reject_history(cursor):
    cursor.execute(
        f"""
        SELECT order_id, park_id, contractor_id, reject_ts
        FROM fleet.contractor_reject_history
        ORDER BY order_id
        """,
    )

    return pg_response_to_dict(cursor)


def get_candidates(cursor):
    cursor.execute(
        f"""
        SELECT order_id, candidates, updated_at
        FROM fleet.order_candidates
        ORDER BY order_id
        """,
    )

    return pg_response_to_dict(cursor)
