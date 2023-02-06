MERCHANT_PROFILES_MERCHANTS = {
    'merchant-id-1': {
        'merchant_name': 'Vkusvill',
        'park_id': 'park-id-1',
        'payment_ttl_sec': 300,
        'payment_scheme': 'yandex_withhold',
        'enable_balance_check_on_pay': False,
        'enable_requisites_check_on_draft': True,
    },
    'merchant-id-2': {'merchant_name': 'Pyaterochka'},
}


def pg_response_to_dict(cursor):
    res = []
    for row in cursor.fetchall():
        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]
    return res


def get_park_offer_confirmation(cursor, billing_client_id):
    cursor.execute(
        f"""
            SELECT
                id,
                billing_client_id,
                approved_at
            FROM
                merchant_profiles.park_offer_confirmations
            WHERE
                billing_client_id='{billing_client_id}'
                AND
                withdrawn_at is NULL
        """,
    )
    return pg_response_to_dict(cursor)
