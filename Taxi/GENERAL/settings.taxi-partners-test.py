# -*- coding: utf-8 -*-

MONGO = {
    'taxi': {
        'connection_kwargs': {
            'host':
                'mongodb://mobile:vj,bkmybr@'
                'taxi-partners-test-mrs01h.mobile.yandex.net:27017,'
                'taxi-partners-test-mrs01e8.mobile.yandex.net:27017,'
                'taxi-partners-test-mrs01g.mobile.yandex.net:27017/dbtaxi',
            'socketTimeoutMS': 60000,
            'connectTimeoutMS': 10000,
            'waitQueueTimeoutMS': 10000,
        },
        'cursor_max_time_ms': 5000,
        'min_threads_free': 10,
    },
    'noncritical': {
        'connection_kwargs': {
            # Use `taxi` database
            'host':
                'mongodb://mobile:vj,bkmybr@'
                'taxi-partners-test-mrs01h.mobile.yandex.net:27017,'
                'taxi-partners-test-mrs01e8.mobile.yandex.net:27017,'
                'taxi-partners-test-mrs01g.mobile.yandex.net:27017/dbprocessing',
            'socketTimeoutMS': 60000,
            'connectTimeoutMS': 10000,
            'waitQueueTimeoutMS': 10000,
        },
        'cursor_max_time_ms': 5000,
        'min_threads_free': 30,
    },
    'archive': {
        'connection_kwargs': {
            'host':
                'mongodb://mobile:vj,bkmybr@'
                'taxi-partners-test-mrs01h.mobile.yandex.net:27017,'
                'taxi-partners-test-mrs01e8.mobile.yandex.net:27017,'
                'taxi-partners-test-mrs01g.mobile.yandex.net:27017/dbarchive',
            'socketTimeoutMS': 60000,
            'connectTimeoutMS': 10000,
            'waitQueueTimeoutMS': 10000,
        },
        'cursor_max_time_ms': 5000,
        'min_threads_free': 10,
    },
    'logs': {
        'connection_kwargs': {
            'host':
                'mongodb://mobile:vj,bkmybr@'
                'taxi-partners-test-logs-mrs01h.mobile.yandex.net:27017,'
                'taxi-partners-test-logs-mrs01e8.mobile.yandex.net:27017,'
                'taxi-partners-test-logs-mrs01g.mobile.yandex.net:27017/dblogs',
            'socketTimeoutMS': 60000,
            'connectTimeoutMS': 10000,
            'waitQueueTimeoutMS': 10000,
        },
        'cursor_max_time_ms': 5000,
        'min_threads_free': 50,
    },
    'pinstats': {
        'connection_kwargs': {
            'host':
                'mongodb://mobile:vj,bkmybr@'
                'taxi-partners-test-logs-mrs01h.mobile.yandex.net:27017,'
                'taxi-partners-test-logs-mrs01e8.mobile.yandex.net:27017,'
                'taxi-partners-test-logs-mrs01g.mobile.yandex.net:27017/dbpinstats',
            'socketTimeoutMS': 60000,
            'connectTimeoutMS': 10000,
            'waitQueueTimeoutMS': 10000,
        },
        'cursor_max_time_ms': 5000,
        'min_threads_free': 50,
    },
    'localizations': {
        'connection_kwargs': {
            'host':
                'mongodb://mobile:vj,bkmybr@'
                'localization-mrs01g.mobile.yandex.net:27017,'
                'localization-mrs01e8.mobile.yandex.net:27017,'
                'localization-mrs01f.mobile.yandex.net:27017/localizations',
            'socketTimeoutMS': 60000,
            'connectTimeoutMS': 10000,
            'waitQueueTimeoutMS': 10000,
        },
        'cursor_max_time_ms': 5000,
        'min_threads_free': 10,
    },
    'stats': {
        'connection_kwargs': {
            'host':
                'mongodb://mobile:vj,bkmybr@'
                'taxi-partners-test-mrs01h.mobile.yandex.net:27017,'
                'taxi-partners-test-mrs01e8.mobile.yandex.net:27017,'
                'taxi-partners-test-mrs01g.mobile.yandex.net:27017/dbstats',
            'socketTimeoutMS': 60000,
            'connectTimeoutMS': 10000,
            'waitQueueTimeoutMS': 10000,
        },
        'cursor_max_time_ms': 5000,
        'min_threads_free': 10,
    },
    'corp': {
        'connection_kwargs': {
            'host':
                'mongodb://mobile:vj,bkmybr@'
                'taxi-partners-test-mrs01h.mobile.yandex.net:27017,'
                'taxi-partners-test-mrs01e8.mobile.yandex.net:27017,'
                'taxi-partners-test-mrs01g.mobile.yandex.net:27017/dbcorp',
            'socketTimeoutMS': 60000,
            'connectTimeoutMS': 10000,
            'waitQueueTimeoutMS': 10000,
        },
        'cursor_max_time_ms': 5000,
        'min_threads_free': 10,
    },
    'insurance': {
        'connection_kwargs': {
            'host':
                'mongodb://mobile:vj,bkmybr@'
                'taxi-partners-test-mrs01h.mobile.yandex.net:27017,'
                'taxi-partners-test-mrs01e8.mobile.yandex.net:27017,'
                'taxi-partners-test-mrs01g.mobile.yandex.net:27017'
                '/dbinsurance',
            'socketTimeoutMS': 60000,
            'connectTimeoutMS': 10000,
            'waitQueueTimeoutMS': 10000,
        },
        'cursor_max_time_ms': 5000,
        'min_threads_free': 10,
    },
}

ROUTING_API_HOST = 'http://core-router-taxi.maps.yandex.net'
TRACKING_API_HOST = 'http://taxi-partners-test-tracks.mobile.yandex.net/getvehicles_internal'
TRACKER_HOST = 'http://tracker.taxi.tst.yandex.net'
RIDEMATCH_HOST = 'http://ride-match.taxi.tst.yandex.net'
TRACKER_MAP_HOST = 'http://tracker.taxi.tst.yandex.net'
CARGO_CLAIMS_HOST = 'http://cargo-claims.taxi.tst.yandex.net'
CARGO_ORDERS_HOST = 'http://cargo-orders.taxi.tst.yandex.net'
PHONE_API_HOST = 'http://sms.passport.yandex.ru'
LBS_API_HOST = 'http://api.lbs.yandex.net/geolocation'
MISSPELL_HOST = 'http://misc-spell.yandex.net:19036/misspell.json/check'
AUTO_PRICE_HOST = 'https://apiauto.ru/1.0/stats/summary'

PASSPORT_SMS_BASE_URL = 'http://sms.passport.yandex.ru'
PASSPORT_BB_BASE_URL = 'http://blackbox.yandex.net'

MAX_ACTIVE_ORDERS = 100
MAX_ACTIVE_ORDERS_LOYAL = 100
MAX_UNFINISHED_ORDERS = 100
MAX_UNFINISHED_ORDERS_TIME = 30  # секунд
BLOCK_FOR_ORDER_SPAM = 30        # секунд
DELAY_BETWEEN_ORDERS = 5         # секунд

ORDER_EXACT_ONLY = True

BLOCK_FOR_TRY = 30

PARTNER_QA_CC_LIST = []
PARTNER_ADMIN_CC_LIST = []

SEND_SMS = False

BILLING_XMLRPC_SERVER = 'http://balance-simple.yandex.net:8018/simple/xmlrpc'
BILLING_HTTPAPI_URL = 'http://balance-xmlrpc.yandex.net:8002/httpapi/%s'

CRUTCH = True

MAX_TARIFFS_URL = 'https://m.taxi-partners.yandex.ru/city-tariff/?city={}'
PARK_TARIFFS_URL = 'https://m.taxi-partners.yandex.ru/park-tariff/?parkid={}'
ZONE_TARIFFS_URL = 'https://m.taxi-partners.yandex.ru/zone-tariff/?id={}'

BACKEND_HOST = 'tc.taxi-partners-test.mobile.yandex.net'
TAXI_PROTOCOL_HOST = 'http://taxi-protocol.taxi.tst.yandex.net'

IMAGES_URL_TEMPLATE = 'https://%s/static/images/{}' % BACKEND_HOST

MDS_UPLOAD_HOST = 'storage-int.mds.yandex.net:1111'
MDS_GET_HOST = 'storage-int.mds.yandex.net:80'

# TAXIBACKEND-2742: Default to N = 90 days
FIRST_LIMIT_DEVICE_REUSE_SECONDS = 90 * 86400

# Zendesk authorization settings
ZENDESK_JWT_PROFILE_DEFAULT = 'yataxi'
ZENDESK_JWT_PROFILES = {
    'yataxi': {
        'oauth_client_id': '1efc87845b61455d8f644d9b044b5208',
        'oauth_client_secret': 'b2497728bd0c4d04985249d7d399fb7a',
        'jwt_secret': 't3gw6cKMpbRmlPVS5UCRJigp45qajSGEzmatwrh40U3ba3gW',
        'redirect_url': (
            'https://yataxi1461234887.zendesk.com/access/jwt?jwt={jwt}'
        ),
    },
}

# TAXIBACKEND-3867
SUPPORT_PAGE_URL = 'https://m.taxi.yandex.ru/help'

XIVA_API_HOST = 'https://push-sandbox.yandex.ru'
