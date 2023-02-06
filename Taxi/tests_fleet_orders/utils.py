def pg_response_to_dict(cursor):
    res = []
    for row in cursor.fetchall():
        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]
    return res


def get_park_order(cursor):
    cursor.execute(
        f"""
        SELECT park_id, id, last_order_alias_id, status, tariff_class,
          personal_phone_id, address_from, addresses_to,
          created_at, ended_at, is_creator, event_index,
          last_contractor_park_id, last_contractor_id, last_contractor_car_id,
          booked_at, number, record_created_at, record_updated_at, driving_at,
          geopoint_from,
          geopoints_to, forced_fixprice, client_booked_at, preorder_request_id,
          duration_estimate, source_park_id,
          update_seq_no
        FROM fleet.park_order
        ORDER BY park_id
        """,
    )

    return pg_response_to_dict(cursor)


def reset_update_number_seq(cursor, from_val):
    cursor.execute(
        f"""
        ALTER SEQUENCE fleet.seq_park_order_update_number
        RESTART {from_val};
        """,
    )
