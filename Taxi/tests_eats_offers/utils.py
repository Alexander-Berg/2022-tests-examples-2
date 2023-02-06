import datetime

import pytz


def pg_to_plain(offer_item):
    if isinstance(offer_item, datetime.datetime):
        if offer_item.tzinfo is not None:
            offer_item = offer_item.astimezone(pytz.UTC).replace(tzinfo=None)
    return offer_item


def get_offer_count_from_pg(pgsql, session_id):
    cursor = pgsql['eats_offers'].cursor()
    cursor.execute(
        'SELECT session_id, location, delivery_time, '
        'request_time, expiration_time, '
        'prolong_count, payload '
        'FROM eats_offers.offers WHERE session_id = %s;',
        (session_id,),
    )
    offers = list(cursor)
    return len(offers)


def get_offer_from_pg_by_session_id(pgsql, session_id):
    cursor = pgsql['eats_offers'].cursor()
    cursor.execute(
        'SELECT session_id, location, delivery_time, '
        'request_time, expiration_time, '
        'prolong_count, payload '
        'FROM eats_offers.offers WHERE session_id = %s;',
        (session_id,),
    )
    offers = list(cursor)

    assert len(offers) == 1
    offer = offers[0]

    offer_fields_count = 7
    assert len(offer) == offer_fields_count

    result = {
        'session_id': offer[0],
        'location': offer[1],
        'delivery_time': offer[2],
        'request_time': offer[3],
        'expiration_time': offer[4],
        'prolong_count': offer[5],
        'payload': offer[6],
        'q': 1,
    }
    result = dict(map(lambda kv: (kv[0], pg_to_plain(kv[1])), result.items()))
    return result


def get_subdict(origin, keys):
    return {key: origin[key] for key in keys if key in origin}


STANDARD_HEADERS = {
    'X-Login-Id': '123',
    'X-Yandex-UID': 'uid1',
    'X-Eats-Session': 'sess1',
    'X-Eats-Session-Type': 'appclip',
    'X-YaTaxi-Pass-Flags': 'portal,no-login',
    'Cookie': 'PHPSESSID=123',
    'X-Remote-IP': '127.0.0.0',
    'X-Request-Language': 'ru',
    'X-Request-Application': (
        'x=y,app_name=xxx,app_ver1=1,app_ver2=2,app_brand=eats-clip'
    ),
}


def get_headers_with_user_id(user_id):
    result = STANDARD_HEADERS.copy()
    result['X-Eats-User'] = (
        'personal_phone_id=1,personal_email_id=2,user_id=' + user_id
    )
    return result


def get_headers_with_partner_id(user_id):
    result = STANDARD_HEADERS.copy()
    result['X-Eats-User'] = (
        'personal_phone_id=1,personal_email_id=2,partner_user_id=' + user_id
    )
    return result


SET_STATUS_NEW = 'NEW_OFFER_CREATED'
SET_STATUS_NO_CHANGES = 'NO_CHANGES'
SET_STATUS_PAYLOAD_UPDATED = 'PAYLOAD_UPDATED'

MATCH_STATUS_NO_CHANGES = 'NO_CHANGES'
MATCH_STATUS_PROLONGED = 'OFFER_PROLONGED'
