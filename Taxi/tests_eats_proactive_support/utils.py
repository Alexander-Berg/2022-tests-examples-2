import json


async def db_insert_order(
        pgsql,
        order_nr,
        order_status,
        now_stamp=None,
        park_id=None,
        driver_id=None,
        place_id='dummy_place_id',
):
    cursor = pgsql['eats_proactive_support'].cursor()
    payload = json.dumps(
        {'application': 'dummy_application', 'place_id': place_id},
    )
    created_at = 'NOW()' if now_stamp is None else now_stamp
    updated_at = 'NOW()' if now_stamp is None else now_stamp
    if driver_id and park_id:
        sql_script = f"""
            INSERT INTO eats_proactive_support.orders
                (order_nr, status, promised_at, order_type,
                delivery_type, shipping_type, park_id, driver_id, payload,
                created_at, updated_at)
            VALUES
                ('{order_nr}', '{order_status}', NOW(), 'dummy_order_type',
                'native', 'delivery', '{park_id}',
                '{driver_id}', '{payload}',
                '{created_at}', '{updated_at}');"""
    else:
        sql_script = f"""
            INSERT INTO eats_proactive_support.orders
                (order_nr, status, promised_at, order_type,
                delivery_type, shipping_type, payload,
                created_at, updated_at)
            VALUES
                ('{order_nr}', '{order_status}', NOW(), 'dummy_order_type',
                'native', 'delivery', '{payload}',
                '{created_at}',
                '{updated_at}');"""

    cursor.execute(sql_script)


async def db_insert_order_sensitive_data(
        pgsql,
        order_nr,
        eater_id='dummy_eater_id',
        eater_personal_phone_id='dummy_phone_id',
        eater_passport_uid='dummy_passport_uid',
        eater_device_id=None,
):
    cursor = pgsql['eats_proactive_support'].cursor()
    sql_script = f"""
        INSERT INTO eats_proactive_support.orders_sensitive_data
            (order_nr, eater_id, eater_personal_phone_id,
            eater_passport_uid, eater_device_id)
        VALUES
            ('{order_nr}', '{eater_id}', '{eater_personal_phone_id}',
            '{eater_passport_uid}', '{eater_device_id}');"""

    cursor.execute(sql_script)


async def db_insert_problem(pgsql, order_nr, problem_type):
    cursor = pgsql['eats_proactive_support'].cursor()
    cursor.execute(
        f"""
            INSERT INTO eats_proactive_support.problems
                (order_nr, type)
            VALUES
                ('{order_nr}', '{problem_type}')
            RETURNING id;""",
    )
    return cursor.fetchone()[0]


async def db_insert_action(
        pgsql,
        problem_id,
        order_nr,
        action_type,
        payload,
        state,
        mocked_time=None,
):
    cursor = pgsql['eats_proactive_support'].cursor()
    created_at = 'NOW()' if mocked_time is None else mocked_time
    updated_at = 'NOW()' if mocked_time is None else mocked_time

    sql_script = f"""
        INSERT INTO eats_proactive_support.actions
            (problem_id, order_nr, type, payload, state,
            created_at, updated_at)
        VALUES
            ('{problem_id}', '{order_nr}', '{action_type}',
            '{payload}', '{state}', '{created_at}',
            '{updated_at}')
        RETURNING id;"""
    cursor.execute(sql_script)

    return cursor.fetchone()[0]


async def db_get_action_state(pgsql, action_id):
    cursor = pgsql['eats_proactive_support'].cursor()
    cursor.execute(
        f"""SELECT state, skip_reason FROM eats_proactive_support.actions
            WHERE id = '{action_id}';""",
    )
    res = cursor.fetchone()
    return res[0], res[1]
