import datetime

import pytz


MOCK_TVM_SERVICE_NAME = 'mock'

# tvmknife unittest service -s 111 -d 2015665
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxCxg3s:T2aLiGOWHgjsT3SU0EJCV6mxU8cPZ_NOiQ'
    'BCBXHB4pUanPoImX1iol3yd8e0lfjwOMp0wzT0Mw0Jxh-mjm5hzLXRzpFnq0ZmUdwCtBX'
    'JWd0jslTwpNwJHAduHSPizejNXTOb3AnXDdssO7Ywto84D-CHGzw8JKows261-kF1W6A'
)

# tvmknife unittest service -s 2015665 -d 2002228
ORDERS_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IggIsYN7ELSaeg:DCWMykHRsyknf8rWDEk3Tc92IWiryyIr'
    '94PXlrb3iRaShMCLoaUEU90rq2sEZNuFyhsU62accnri44iom6e5xi_R30SM_bG188qR_6'
    'x51xTKRm9prx4w39SeIHcIZ9sx7yec33u-zk-JrQcTk8lvIUUu2tZ7-Eh4ZNaZQdO_a6U'
)

# tvmknife unittest user -d 54591353 -e test --scopes read,write
DISPATCHER_USER_TICKET = (
    '3:user:CA0Q__________9_GiEKBQj5_oMaEPn-gxoaBHJlYWQaBXdyaXRlIN'
    'KF2MwEKAE:BKP9e6YK4ZP5vZa-DYW2p_43EwFjTKxnhyPPvaIQx35PZxbW5B9'
    'lO98FoeiW9MNIygxXy_248Le8nBNlkzXLz2LnrKnkb5H1lfpc2hP_JhZK9-id'
    '8NAbix3GhfO5guBSAxT-rB0iYQ0Sl6wgcoCn0vY-RRKhdMni36eU8rb_4dg'
)

# tvmknife unittest user -d 1120000000083978 -e prod_yateam --scopes read,write
TECH_SUPPORT_USER_TICKET = (
    '3:user:CAwQ__________9_GikKCQiKkJ2RpdT-ARCKkJ2RpdT-ARoEcmVhZBoFd'
    '3JpdGUg0oXYzAQoAg:PDx7DnqrAKf22PaztpPe0gaVU3SQ9CG3IfMxzVhkKy4LTW'
    'KC5Wh4D29FOgVdwxlOs5llzccbvraC0TM5p3Dd2zDP_ARfTH7PbyUjHEyuneYheE'
    'gPy7GSf-_hQeA-wIOl0_zU9bUWsKwulSQScWE2DL3sR8dN0On8kCIakOpsuf8'
)

FLEET_API_CLIENT_ID = 'todua'
FLEET_API_KEY_ID = '13'
FLEET_API_HEADERS = {
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    'X-Fleet-API-Client-ID': FLEET_API_CLIENT_ID,
    'X-Fleet-API-Key-ID': FLEET_API_KEY_ID,
}

PLATFORM_HEADERS = {
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    'X-Ya-Service-Name': MOCK_TVM_SERVICE_NAME,
}

DISPATCHER_PASSPORT_UID = '54591353'
DISPATCHER_HEADERS = {
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    'X-Ya-User-Ticket': DISPATCHER_USER_TICKET,
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-UID': DISPATCHER_PASSPORT_UID,
}

TECH_SUPPORT_PASSPORT_UID = '1120000000083978'
TECH_SUPPORT_HEADERS = {
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    'X-Ya-User-Ticket': TECH_SUPPORT_USER_TICKET,
    'X-Ya-User-Ticket-Provider': 'yandex_team',
    'X-Yandex-UID': TECH_SUPPORT_PASSPORT_UID,
}


def make_request(driver_profile_ids, accrued_ats, groups, categories):
    return {
        'query': {
            'park': {
                'id': '7ad35b',
                **(
                    {}
                    if driver_profile_ids is None
                    else {'driver_profile': {'ids': driver_profile_ids}}
                ),
            },
            'balance': {
                'accrued_ats': accrued_ats,
                **({} if groups is None else {'group_ids': groups}),
                **({} if categories is None else {'category_ids': categories}),
            },
        },
    }


def select_park_category(pgsql, park_id, category_index):
    fields = ['category_name', 'idempotency_token', 'is_enabled']
    db = pgsql['fleet_transactions_api'].cursor()
    db.execute(
        'SELECT {} FROM fleet_transactions_api.park_transaction_categories '
        'WHERE park_id=\'{}\' AND category_index={}'.format(
            ','.join(fields), park_id, category_index,
        ),
    )
    db_categories = list(db)
    assert len(db_categories) == 1, db_categories
    return {k: v for (k, v) in zip(fields, db_categories[0])}


def filter_entity_balance(balance, groups, categories):
    if groups is not None:
        balance['groups'] = [
            x for x in balance['groups'] if x['group_id'] in groups
        ]
    else:
        balance.pop('groups')

    if categories is not None:
        balance['categories'] = [
            x for x in balance['categories'] if x['category_id'] in categories
        ]
    else:
        balance.pop('categories')

    return balance


def filter_entity_balances(entity, accrued_ats, groups, categories):
    entity['balances'] = [
        filter_entity_balance(x, groups, categories)
        for x in entity['balances']
        if x['accrued_at'] in accrued_ats
    ]
    return entity


def assert_is_now(value):
    value = value.replace(tzinfo=pytz.UTC)
    delta = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) - value
    assert datetime.timedelta() <= delta < datetime.timedelta(minutes=1), delta


# at top level only
def make_datetime_iso_str(obj):
    for key, value in obj.items():
        if isinstance(value, datetime.datetime):
            obj[key] = value.strftime('%Y-%m-%dT%H:%M:%S+00:00')
    return obj
