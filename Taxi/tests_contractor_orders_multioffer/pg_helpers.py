import datetime
import json

import pytz


MULTIOFFER_BID_FIELDS = [
    'id',
    'multioffer_id',
    'status',
    'reason',
    'park_id',
    'driver_profile_id',
    'created_at',
    'updated_at',
    'price',
    'auction',
]


MULTIOFFER_DRIVERS_FIELDS = [
    'offer_status',
    'answer',
    'reason',
    'answer_received_at',
    'seen_data',
    'candidate_json',
    'enriched_json',
]

MULTIOFFER_DRIVER_ID_FIELDS = [
    'driver_profile_id',
    'park_id',
    'score',
    'offer_status',
    'auction',
]

MULTIOFFER_FIELDS = [
    'id',
    'status',
    'completed_at',
    'lookup_request',
    'settings',
    'wave',
    'auction',
]

TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

ALL_FILES = [
    'multioffer_empty.sql',
    'multioffer_irrelevant.sql',
    'multioffer_multi_accept.sql',
    'multioffer_multi_completed_has_winner.sql',
    'multioffer_multi_no_answer.sql',
    'multioffer_multi_no_answer_with_seen.sql',
    'multioffer_multi_reject.sql',
    'multioffer_single_accept.sql',
]


def _row_to_dict(row, fields):
    result = {}
    if row:
        for i, field in enumerate(fields):
            if row[i] is not None:
                if isinstance(row[i], datetime.datetime):
                    result[field] = (
                        row[i].astimezone(pytz.UTC).strftime(TIMESTAMP_FORMAT)
                    )
                else:
                    result[field] = row[i]
    return result


def execute(pgsql, sql):
    cursor = pgsql['contractor_orders_multioffer'].cursor()
    cursor.execute(sql)


def select_driver(pgsql, park_id, driver_profile_id):
    cursor = pgsql['contractor_orders_multioffer'].cursor()
    cursor.execute(
        f"""
    SELECT {", ".join(MULTIOFFER_DRIVERS_FIELDS)}
    FROM  multioffer.multioffer_drivers
    WHERE driver_profile_id = '{driver_profile_id}'
    AND park_id = '{park_id}';
    """,
    )
    return _row_to_dict(cursor.fetchone(), MULTIOFFER_DRIVERS_FIELDS)


def select_multioffer_driver(pgsql, multioffer_id, driver_id, park_id):
    cursor = pgsql['contractor_orders_multioffer'].cursor()
    cursor.execute(
        f"""
        SELECT {", ".join(MULTIOFFER_DRIVERS_FIELDS)}
        FROM  multioffer.multioffer_drivers
        WHERE multioffer_id = '{multioffer_id}'
        AND driver_profile_id = '{driver_id}'
        AND park_id = '{park_id}';
        """,
    )
    return _row_to_dict(cursor.fetchone(), MULTIOFFER_DRIVERS_FIELDS)


def select_multioffer_drivers(pgsql, multioffer_id):
    cursor = pgsql['contractor_orders_multioffer'].cursor()
    cursor.execute(
        f"""
    SELECT {", ".join(MULTIOFFER_DRIVER_ID_FIELDS)}
    FROM  multioffer.multioffer_drivers
    WHERE multioffer_id = '{multioffer_id}'
    ORDER BY score ASC;
    """,
    )
    rows = cursor.fetchall()

    return [_row_to_dict(row, MULTIOFFER_DRIVER_ID_FIELDS) for row in rows]


def select_recent_multioffer(pgsql):
    cursor = pgsql['contractor_orders_multioffer'].cursor()
    cursor.execute(
        f"""
    SELECT {", ".join(MULTIOFFER_FIELDS)}
    FROM  multioffer.multioffers
    ORDER BY created_at DESC
    LIMIT 1
    """,
    )

    return _row_to_dict(cursor.fetchone(), MULTIOFFER_FIELDS)


def select_multioffer(pgsql, multioffer_id):
    cursor = pgsql['contractor_orders_multioffer'].cursor()
    cursor.execute(
        f"""
    SELECT {", ".join(MULTIOFFER_FIELDS)}
    FROM  multioffer.multioffers
    WHERE id = '{multioffer_id}'
    """,
    )

    return _row_to_dict(cursor.fetchone(), MULTIOFFER_FIELDS)


def update_callback_url(pgsql, multioffer_id, new_callback):
    cb_json = json.dumps(new_callback)
    cursor = pgsql['contractor_orders_multioffer'].cursor()
    path = '{callback}'
    cursor.execute(
        f"""
    UPDATE multioffer.multioffers
    SET lookup_request = jsonb_set(lookup_request, '{path}', '{cb_json}')
    WHERE id = '{multioffer_id}'
    """,
    )


def check_paid_supply_drivers(pgsql, paid_supply_drivers, multioffer_id):
    drivers = select_multioffer_drivers(pgsql, multioffer_id)
    for driver in drivers:
        driver_value = select_multioffer_driver(
            pgsql,
            multioffer_id,
            driver['driver_profile_id'],
            driver['park_id'],
        )
        if 'in_extended_radius' in driver_value['candidate_json']:
            assert driver_value['candidate_json']['in_extended_radius'] == (
                driver['driver_profile_id'] in paid_supply_drivers
            )


def select_multioffer_bid(pgsql, multioffer_id, bid_id):
    cursor = pgsql['contractor_orders_multioffer'].cursor()
    cursor.execute(
        f"""
        SELECT {", ".join(MULTIOFFER_BID_FIELDS)}
        FROM  multioffer.multioffer_bids
        WHERE multioffer_id = '{multioffer_id}'
        AND id = '{bid_id}';
        """,
    )
    return _row_to_dict(cursor.fetchone(), MULTIOFFER_BID_FIELDS)


def select_multioffer_driver_bid(
        pgsql, multioffer_id, park_id, driver_profile_id, bid_status=None,
):
    cursor = pgsql['contractor_orders_multioffer'].cursor()
    query = f"""
        SELECT {", ".join(MULTIOFFER_BID_FIELDS)}
        FROM  multioffer.multioffer_bids
        WHERE multioffer_id = '{multioffer_id}'
        AND driver_profile_id = '{driver_profile_id}'
        AND park_id = '{park_id}'
    """

    if bid_status is not None:
        query += f""" AND status = '{bid_status}'"""

    query += f""";"""

    cursor.execute(query)

    return _row_to_dict(cursor.fetchone(), MULTIOFFER_BID_FIELDS)


def select_multioffer_bids(pgsql, multioffer_id):
    cursor = pgsql['contractor_orders_multioffer'].cursor()
    cursor.execute(
        f"""
        SELECT {", ".join(MULTIOFFER_BID_FIELDS)}
        FROM  multioffer.multioffer_bids
        WHERE multioffer_id = '{multioffer_id}';
        """,
    )
    rows = cursor.fetchall()

    return [_row_to_dict(row, MULTIOFFER_BID_FIELDS) for row in rows]
