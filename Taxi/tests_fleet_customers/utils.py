def pg_response_to_dict(cursor):
    res = []
    for row in cursor.fetchall():
        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]
    return res


def get_customer_by_id(pgsql, customer_id):
    cursor = pgsql['fleet_customers'].cursor()
    cursor.execute(
        f"""
        SELECT
            id,
            park_id,
            personal_phone_id,
            name,
            created_at,
            sms_enabled,
            invoice_enabled,
            comment
        FROM
            fleet_customers.customers
        WHERE
            id = '{customer_id}'
        """,
    )
    result = pg_response_to_dict(cursor)
    if not result:
        return None
    assert len(result) == 1
    return result[0]


def has_customers_with_phone_ids(pgsql, personal_phone_ids) -> bool:
    cursor = pgsql['fleet_customers'].cursor()
    sql = """
    SELECT EXISTS (
        SELECT
            id
        FROM
            fleet_customers.customers
        WHERE
            personal_phone_id IN (SELECT UNNEST(%s::varchar[]))
    );
    """
    cursor.execute(sql, (personal_phone_ids,))
    result = pg_response_to_dict(cursor)
    return result[0]['exists']
