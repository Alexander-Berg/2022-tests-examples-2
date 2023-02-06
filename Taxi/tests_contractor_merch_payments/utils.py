import dateutil.parser

TRANSLATIONS = {
    'error.some_error_occurred.text': {'en': 'some_error_occurred-tr'},
    'error.not_enough_money_on_drivers_balance.text': {
        'en': 'not_enough_money_on_drivers_balance-tr',
    },
    'error.driver_has_pending_purchases.text': {
        'en': 'driver_has_pending_purchases-tr',
    },
    'error.park_has_not_enough_money.text': {
        'en': 'park_has_not_enough_money-tr',
    },
    'error.billing_is_disabled_for_park.text': {
        'en': 'billing_is_disabled_for_park-tr',
    },
    'error.unsupported_country.text': {'en': 'unsupported_country-tr'},
    'error.balance_payments_is_disabled_for_park.text': {
        'en': 'balance_payments_is_disabled_for_park-tr',
    },
    'error.driver_not_self_employed.text': {
        'en': 'driver_not_self_employed-tr',
    },
    'error.contractor_has_pending_payments.text': {
        'en': 'contractor_has_pending_payments-tr',
    },
    'payment_description.text': {'en': 'Payment by QR code'},
    'refund_description.text': {'en': 'Refund'},
}


DEEP_LINK_PROXY = (
    'https://taximeter-core.tst.mobile.yandex.net/marketplace/v1/payment?id={}'
)


def get_headers(park_id, driver_profile_id, idempotency_token=''):
    return {
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': driver_profile_id,
        'X-Idempotency-Token': idempotency_token,
        'X-Request-Application': 'Taximeter',
        'X-Request-Application-Version': '9.90',
        'X-Request-Platform': 'android',
        'Accept-Language': 'en_GB',
    }


def cursor_to_dict(cursor):
    res = []
    for row in cursor.fetchall():
        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]
    return res


def get_payments_by_token(pgsql, idempotency_token):
    with pgsql['contractor_merch_payments'].cursor() as cursor:
        cursor.execute(
            f"""
            SELECT
                id,
                idempotency_token,

                park_id,
                contractor_id,
                merchant_id,

                price,
                status
            FROM
                contractor_merch_payments.payments
            WHERE
                idempotency_token='{idempotency_token}'
            """,
        )

        return [row for row in cursor]


def get_transaction_by_idempotency(pgsql, idempotency_token, fields):
    with pgsql['contractor_merch_payments'].cursor() as cursor:
        cursor.execute(
            f"""
            SELECT
                {fields}
            FROM
                contractor_merch_payments.transactions
            WHERE
                idempotency_token='{idempotency_token}'
            """,
        )

        transactions = cursor_to_dict(cursor)

        if not transactions:
            return None

        return transactions[0]


def get_transactions_by_payment_id(pgsql, payment_id, fields):
    with pgsql['contractor_merch_payments'].cursor() as cursor:
        cursor.execute(
            f"""
            SELECT
                {fields}
            FROM
                contractor_merch_payments.transactions
            WHERE
                payment_id='{payment_id}'
            """,
        )

        return cursor_to_dict(cursor)


def get_fields_by_payment_id(pgsql, payment_id, fields):
    fields = ',\t\n'.join(fields)

    with pgsql['contractor_merch_payments'].cursor() as cursor:
        cursor.execute(
            f"""
            SELECT
                {fields}
            FROM
                contractor_merch_payments.payments
            WHERE
                id='{payment_id}'
            """,
        )

        return [row for row in cursor][0]


def update_fields_by_payment_id(pgsql, payment_id, fields_to_update, values):
    update = [
        f'{pair[0]} = \'{pair[1]}\'' for pair in zip(fields_to_update, values)
    ]
    update = ',\t\n'.join(update)

    with pgsql['contractor_merch_payments'].cursor() as cursor:
        cursor.execute(
            f"""
            UPDATE
                contractor_merch_payments.payments
            SET
                {update}
            WHERE
                id='{payment_id}'
            """,
        )


def update_status(pgsql, payment_id, status):
    with pgsql['contractor_merch_payments'].cursor() as cursor:
        cursor.execute(
            f"""
            UPDATE
                contractor_merch_payments.payments
            SET
                status = '{status}',
                updated_at = NOW()
            WHERE
                id='{payment_id}'
            """,
        )


def pop_keys_impl(params, key):
    if len(key) == 1:
        params.pop(key[0])
    else:
        pop_keys_impl(params[key[0]], key[1:])


def pop_keys(params, keys_to_remove):
    params = dict(params)

    for key in keys_to_remove:
        if isinstance(key, str):
            params.pop(key)
        if isinstance(key, list):
            pop_keys_impl(params, key)

    return params


def date_parsed(x):
    if isinstance(x, str):
        try:
            return dateutil.parser.isoparse(x)
        except ValueError:
            return x
    if isinstance(x, list):
        return [date_parsed(y) for y in x]
    if isinstance(x, dict):
        return {k: date_parsed(v) for k, v in x.items()}
    return x


def to_composite_type(x, keys):
    if x is None:
        return None

    result = []
    for key in keys:
        value = x[key]

        if len(value.split()) == 1:
            result.append(value)
        else:
            result.append(f'"{value}"')

    return '({})'.format(','.join(result))
