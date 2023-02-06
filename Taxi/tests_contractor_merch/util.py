import dateutil


ERROR_TRANSLATIONS = {
    'error.some_error_occured.text': {'en': 'some_error_occured-tr'},
    'error.not_enough_money_on_drivers_balance.text': {
        'en': 'not_enough_money_on_drivers_balance-tr',
    },
    'error.offer_changed_or_expired.text': {
        'en': 'offer_changed_or_expired-tr',
    },
    'error.one_offer_daily_limit_excceded.text': {
        'en': 'one_offer_daily_limit_excceded-tr',
    },
    'error.one_offer_total_limit_excceded.text': {
        'en': 'one_offer_total_limit_excceded-tr',
    },
    'error.one_offer_per_unique_driver_total_limit_excceded.text': {
        'en': 'one_offer_per_unique_driver_total_limit_excceded-tr',
    },
    'error.no_promocodes_left.text': {'en': 'no_promocodes_left-tr'},
    'error.driver_has_pending_purchases.text': {
        'en': 'driver_has_pending_purchases-tr',
    },
    'error.drivers_license_is_not_verified.text': {
        'en': 'drivers_license_is_not_verified-tr',
    },
    'error.park_has_not_enough_money.text': {
        'en': 'park_has_not_enough_money-tr',
    },
    'error.billing_is_disabled_for_park.text': {
        'en': 'billing_is_disabled_for_park-tr',
    },
    'error.marketplace_is_disabled_for_park.text': {
        'en': 'marketplace_is_disabled_for_park-tr',
    },
    'error.driver_already_has_priority.text': {
        'en': 'driver_already_has_priority',
    },
}

STQ_TRANSLATIONS = {
    'notification_v1.success.title': {'en': '%(offer_title)s: succ'},
    'notification_v1.success.text': {
        'en': 'Default text with number, here it is: %(promocode_value)s',
    },
    'notification_v1.success_with_barcode.text': {
        'en': 'Default text without number, nothing to show',
    },
    'notification_v1.success.linear_barcode_url_text': {'en': 'Your barcode'},
    'notification_v1.failure.title': {'en': '%(offer_title)s: failed'},
    'notification_v1.failure.text': {'en': 'Try again later'},
    'category.tire': {'en': 'tire category', 'ru_RU': 'Категория шины'},
    'category.washing': {'en': 'washing category', 'ru_RU': 'Категория мойка'},
    'category.washing.slider': {
        'en': 'washing slider',
        'ru_RU': 'Мойка слайдер',
    },
    **ERROR_TRANSLATIONS,
}

CUSTOM_MESSAGES_TRANSLATIONS = {
    'somecompany_v1.success.text': {'en': 'Why not?'},
    'timer.offer_expires_header.default': {'en': 'Discount available'},
    'timer.offer_expires_subheader.default': {
        'en': 'Offer is limited and will expire soon!',
    },
    'timer.tags.gold.blocked': {'en': 'Go drive!'},
    'notification_v1.success.promocodeless.text': {
        'en': 'Successful purchase of promocode without value',
    },
    'test-long-key-onegin': {
        'en': 'Successful purchase of promocode without value',
    },
}


def get_mock_query(mock_call):
    return {k: v for k, v in mock_call['request'].query.items()}


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


def pg_response_to_dict(cursor):
    res = []
    for row in cursor.fetchall():
        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]
    return res


def get_vouchers(cursor, with_created_at=False):
    cursor.execute(
        f"""
        SELECT
            id,
            park_id,
            driver_id,
            idempotency_token,
            feeds_admin_id,
            feed_id,
            promocode_id,
            price,
            currency,
            status,
            status_reason
            {', created_at' if with_created_at else ''}
        FROM contractor_merch.vouchers
        ORDER BY park_id, driver_id, idempotency_token
        """,
    )

    return pg_response_to_dict(cursor)


def get_voucher_by_idemp(
        cursor, park_id, driver_id, idempotency_token, with_created_at=False,
):
    cursor.execute(
        f"""
        SELECT
            id,
            park_id,
            driver_id,
            idempotency_token,
            feeds_admin_id,
            feed_id,
            promocode_id,
            price,
            currency,
            status,
            status_reason
            {', created_at' if with_created_at else ''}
        FROM contractor_merch.vouchers
        WHERE
            park_id=\'{park_id}\' AND
            driver_id=\'{driver_id}\' AND
            idempotency_token=\'{idempotency_token}\'
        """,
    )

    result = pg_response_to_dict(cursor)
    if not result:
        return None

    return result[0]


def get_feeds_history(cursor, feed_id, locale):
    cursor.execute(
        f"""
            SELECT
                feed_id,
                locale,
                feed_payload
            FROM
                contractor_merch.feed_payloads_history
            WHERE
                feed_id='{feed_id}'
                  AND
                locale='{locale}'
        """,
    )
    return pg_response_to_dict(cursor)


def get_headers(park_id, driver_profile_id, extra_headers=None):
    headers = {
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': driver_profile_id,
        'X-Request-Application': 'Taximeter',
        'X-Request-Application-Version': '9.90',
        'X-Request-Platform': 'android',
        'Accept-Language': 'en_GB',
    }

    if extra_headers is not None:
        headers = {**headers, **extra_headers}

    return headers


def get_expected_offer_response(load_json, with_meta=False):
    if with_meta:
        json_file = 'expected_offer_response_with_meta.json'
    else:
        json_file = 'expected_offer_response.json'

    return load_json(json_file)


def get_promocode(cursor, promocode_id):
    cursor.execute(
        f"""
        SELECT
            id,
            feeds_admin_id,
            status,
            number,
            created_at,
            updated_at
        FROM contractor_merch.promocodes
        WHERE
            id = \'{promocode_id}\'
        """,
    )

    result = pg_response_to_dict(cursor)
    if not result:
        return None

    return result[0]
