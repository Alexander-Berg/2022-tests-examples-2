# -*- coding: utf-8 -*-
import logging

from taxi.conf import settings

settings.SENTRY_CONFIG['DSN'] = ('http://c96f64985e6d48e3892f3a26c3b07b41'
                                 ':6d3ee8e3d0ad40629597d2c5a2fced9e'
                                 '@sentry.test.tools.yandex.net/103')

settings.SENTRY_CONFIG['async-DSN'] = (
    'twisted+' + settings.SENTRY_CONFIG['DSN'])

DEBUG = True
LOG_LEVEL = logging.DEBUG

DELAYED_API_HOST = 'http://delayed.taxi.tst.yandex.net'
AUTO_PRICE_HOST = 'https://apiauto.ru/1.0/stats/summary'
AGGLOMERATIONS_API_HOST = 'http://agglomerations.taxi.tst.yandex.net'
CORP_INTEGRATION_API_URL = 'http://corp-integration-api.taxi.tst.yandex.net'
CORP_TARIFFS_URL = 'http://corp-tariffs.taxi.tst.yandex.net'
CORP_CLIENTS_URL = 'http://corp-clients.taxi.tst.yandex.net'
CORP_USERS_URL = 'http://corp-users.taxi.tst.yandex.net'
GEOTRACKS_API_HOST = 'http://driver-trackstory.taxi.tst.yandex.net/legacy'
DISCOUNTS_API_HOST = 'http://discounts.taxi.tst.yandex.net'
GEOAREAS_API_HOST = 'http://geoareas.taxi.tst.yandex.net'
ROUTING_API_HOST = 'http://core-router-taxi.maps.yandex.net'
FEEDBACK_BASE_URL = 'http://feedback.taxi.tst.yandex.net'
PERSONAL_BASE_URL = 'http://personal.taxi.tst.yandex.net'
REPLICATION_BASE_URL = 'http://replication.taxi.tst.yandex.net'
STQ_AGENT_BASE_URL = 'http://stq-agent.taxi.tst.yandex.net'
USER_API_BASE_URL = 'http://user-api.taxi.tst.yandex.net'
QC_SERVICE_URL = 'http://quality-control.taxi.tst.yandex.net'
QC_CPP_SERVICE_URL = 'http://quality-control-cpp.taxi.tst.yandex.net'
TRACKING_API_HOST = 'http://tracker.taxi.tst.yandex.net/getvehicles_internal'
TAXI_LOOKUP_HOST = 'http://lookup.taxi.tst.yandex.net'
TRACKER_HOST = 'http://tracker.taxi.tst.yandex.net'
RIDEMATCH_HOST = 'http://ride-match.taxi.tst.yandex.net'
TRACKER_MAP_HOST = 'http://tracker.taxi.tst.yandex.net'
TRACKER_GRAPH_HOST = 'http://tracks-graph.taxi.tst.yandex.net'
DRIVER_TRACKSTORY_HOST = 'http://driver-trackstory.taxi.tst.yandex.net'
DRIVER_ROUTE_WATCHER_HOST = 'http://driver-route-watcher.taxi.tst.yandex.net'
DRIVER_ROUTE_RESPONDER_HOST = 'http://driver-route-responder.taxi.tst.yandex.net'
CARGO_CLAIMS_HOST = 'http://cargo-claims.taxi.tst.yandex.net'
CARGO_ORDERS_HOST = 'http://cargo-orders.taxi.tst.yandex.net'
ANTIFRAUD_API_HOST = 'http://antifraud.taxi.tst.yandex.net'
PHONE_API_HOST = 'http://phone-passport-test.yandex.ru'
LBS_API_HOST = 'http://api.lbs.yandex.net/geolocation'
MISSPELL_HOST = 'http://erratum-test3.yandex.ru:19036/misspell.json/check'
PASSENGER_TAGS_SERVICE_HOST = 'http://passenger-tags.taxi.tst.yandex.net'
TAGS_SERVICE_HOST = 'http://tags.taxi.tst.yandex.net'
DRIVER_TAGS_SERVICE_HOST = 'http://driver-tags.taxi.tst.yandex.net'
DRIVER_PROMOCODES_SERVICE_HOST = 'http://driver-promocodes.taxi.tst.yandex.net'
LOYALTY_SERVICE_HOST = 'http://loyalty.taxi.tst.yandex.net'
MAX_TARIFFS_URL = 'https://m.taxi.taxi.tst.yandex.ru/city-tariff/?city={}'
PARK_TARIFFS_URL = 'https://m.taxi.taxi.tst.yandex.ru/park-tariff/?parkid={}'
ZONE_TARIFFS_URL = 'https://m.taxi.taxi.tst.yandex.ru/zone-tariff/?id={}'
CHATTERBOX_API_URL = 'http://chatterbox.taxi.tst.yandex.net'
SUPPORTCHAT_API_URL = 'http://support-chat.taxi.tst.yandex.net'
SUPPORT_INFO_API_URL = 'http://support-info.taxi.tst.yandex.net'
BALANCE_API_HOST = 'https://balance-xmlrpc-tvm-tm.paysys.yandex.net:8004/xmlrpctvm'
BILLING_SERVICE_ID = 111  # Taxi's billing service_id
DRIVER_PARTNER_API_HOST = 'http://driver-partner.taxi.tst.yandex.net'
PARTNER_CONTRACTS_URL = 'http://partner-contracts.taxi.tst.yandex.net'
REPOSITION_SERVICE_HOST = 'http://reposition.taxi.tst.yandex.net'
CANDIDATES_BASE_URL = 'http://candidates.taxi.tst.yandex.net'
DEBTS_URL = 'http://debts-l7.taxi.tst.yandex.net'
FLEET_PAYOUTS_SERVICE_HOST = 'http://fleet-payouts.taxi.tst.yandex.net'
ORDER_FINES_SERVICE_HOST = 'http://order-fines.taxi.tst.yandex.net'

PASSPORT_SMS_BASE_URL = 'http://sms-api.taxi.tst.yandex.net'
PASSPORT_BB_BASE_URL = 'http://pass-test.yandex.ru'
PASSPORT_BB_YATEAM_BASE_URL = 'http://blackbox.yandex-team.ru'
DRIVER_LESSONS_API_HOST = 'http://driver-lessons.taxi.tst.yandex.net'
PROCESSING_ANTIFRAUD_URL = 'http://processing-antifraud.taxi.tst.yandex.net'
USER_ANTIFRAUD_URL = 'http://uantifraud.taxi.tst.yandex.net'
DRIVER_METRICS_HOST_URL = 'http://driver-metrics.taxi.tst.yandex.net'
CARS_CATALOG_HOST_URL = 'http://cars-catalog.taxi.tst.yandex.net'
USER_STATISTICS_URL = 'http://user-statistics.taxi.tst.yandex.net'

STUB_SMS_CODE = '000'
STUB_COUPON = '000000000000'

DEFAULT_APP_NAME = 'ru.yandex.taxi'

BLOCK_FOR_ORDER_SPAM = 30  # секунд
MAX_UNFINISHED_ORDERS_TIME = 60  # 1 минута
TAXICOUNT_AIRPORT_LIMIT = 2
TAXICOUNT_LIMIT = 4

BLOCK_FOR_TRY = 30

ORDER_SEARCH_EXPIRATION = 6 * 60 + 15  # секунд

SEND_SMS = False

PARTNER_QA_CC_LIST = []
PARTNER_ADMIN_CC_LIST = []

BILLING_XMLRPC_SERVER = 'http://trust-payments-old-test.taxi.tst.yandex.net:8018/simple/xmlrpc'
BILLING_HTTPAPI_URL = 'http://greed-tm.paysys.yandex.ru:8002/httpapi/%s'

# No more than 2 /couponcheck requests in 1 second
COUPONCHECK_BAN_PERIOD_SECONDS = 1
COUPONCHECK_BAN_MAX_ATTEMPTS = 2

# No more than 1 /routestats requests in 1 second
ROUTESTATS_BAN_PERIOD_SECONDS = 1
ROUTESTATS_BAN_MAX_ATTEMPTS = 1

# No more than 1 3.0/email {action: set} request per second
SET_EMAIL_TIMEOUT_SECONDS = 1
SET_EMAIL_MAX_ATTEMPTS = 1

# No more than 1 confirmation link sent per second
SEND_CONF_LINK_TIMEOUT_SECONDS = 1
SEND_CONF_LINK_MAX_ATTEMPTS = 1

CRUTCH = True
GRAFANA_DASHBOARD_TITLE_POSTFIX = 'testing'

HOLDING_MAX_AGE = 1800  # 30 minutes
HOLDING_RETRY_TIME = 600  # 10 minutes
MAX_PARK_COMPENSATION = 3000
MAX_REFUND = 1000
TIME_BEFORE_CLEAR = 600  # 10 minutes
FAKE_RIDE_TIME = 20  # 20 seconds
TIME_BEFORE_TAKE_TIPS = 2 * 60  # 2 minutes
PROGRESSIVE_PAYMENT_INTERVAL = 30  # 30 seconds
CARD_CHECK_TIMEOUT = 60  # 1 minute

FEEDBACK_TIMEOUT = 30 * 60  # 30 minutes

BACKEND_HOST = 'tc.tst.mobile.yandex.net'
TAXI_PROTOCOL_HOST = 'http://taxi-protocol.taxi.tst.yandex.net'

IMAGES_URL_TEMPLATE = 'https://%s/static/test-images/{}' % BACKEND_HOST

MDS_UPLOAD_HOST = 'storage-int.mdst.yandex.net:1111'
MDS_GET_HOST = 'storage-int.mdst.yandex.net:80'

REFERRAL_URL = 'https://taxi.taxi.tst.yandex.ru/?ref={}'

PARK_IMPORT_VERIFY = False

PASSPORT_TIMEOUT = 5

# Delayed sms sending
DELAYED_SMS_PER_GROUP = 10
DELAYED_SMS_PER_CHUNK = 3
DELAYED_SMS_FAILED_BOUNDARY = 5
DELAYED_SMS_TIMEOUT = PASSPORT_TIMEOUT + 1
DELAYED_SMS_SENDING_TASK_TIMEOUTS = [5, 10]
DELAYED_SMS_SENDING_TASK_RETRIES_LIMIT = 10
DELAYED_SMS_SENDING_TASK_TIMEOUT = DELAYED_SMS_PER_CHUNK * DELAYED_SMS_TIMEOUT

# TAXIBACKEND-2742: Default to N = 2 hours
FIRST_LIMIT_DEVICE_REUSE_SECONDS = 2 * 60 * 60

EXPIRE_SOON_AFTER_CREATED = 180  # 3 minutes

AUTOREORDER_STILL_SEARCH_NOTIFICATION_TIME = 20  # 20 seconds
AUTOREORDER_OVERDUE = 2 * 60  # 2 minutes

EXACT5_MIN_ORDERS_COUNT = 1  # minimum number of orders completed by driver

SHOW_DRIVER_POSITION_PERIOD = 3600  # 1 hour

ROUTE_SHARING_URL_TEMPLATE = 'https://taxi.taxi.tst.yandex.ru/route-enter/%(key)s'

# TAXIBACKEND-2846: Clear route sharing URL 5 mins after ride is complete
ROUTE_SHARING_CLEARANCE_DELAY = 300  # seconds

# TAXIBACKEND-2520 report generation delay: 30 seconds
ORDER_FEEDBACK_OTRS_DELAY = 30  # seconds

# Don't spam the support team with feedback for our fake orders
ORDER_FEEDBACK_MAIL_TO = {
    'corp': 'taxi-test-feedback+corp@yandex-team.ru',
    'general': 'taxi-test-feedback@yandex-team.ru',
    'vip': 'taxi-test-feedback+vip@yandex-team.ru',
}

PROMOTIONS_MAX_AGE = 60  # seconds

YT_CONFIG_ENV_PREFIX = 'testing'
YT_MONITORING_ACCOUNTS = ['taxi-dev']

VIP_USER_ORDER_AMOUNT_CACHE_TIME = 5 * 60

ADJUST_API = 'http://s2s.adjust.com/event'
ADJUST_SETTING_CACHE_TIME = 60  # 1 min

USERSTATS_API_URL = 'http://userstats.taxi.tst.yandex.net/1.0/stats'

LOOKUP_SPEED_THRESHOLD_CACHE_TIME = 60  # 1 min

STAFF_API_URL = 'https://staff-api.test.yandex-team.ru'

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

START_EXTENDING_PHONE_DOC_AT = (2016, 6, 1)  # no need for migration

REFERRAL_PROMOCODES_URL_TEMPLATE = 'https://m.taxi.taxi.tst.yandex.ru/invite/{}'

# TAXIBACKEND-3867
SUPPORT_PAGE_URL = 'https://m.taxi.taxi.tst.yandex.ru/help'

ELASTIC_LOG_SERVERS = [
    'http://taxi-elastic-logs.taxi.tst.yandex.net:9200',
]
EVLOG_ADJUST_TSKV_FORMAT = 'yandex-taxi-adjust-test-ev-log'

TAXIMETER_URL = 'https://taximeter-xservice.taxi.tst.yandex.net/xservice/yandex'

COMMUNICATIONS_URL = 'http://communications.taxi.tst.yandex.net'
UCOMMUNICATIONS_URL = 'http://ucommunications.taxi.tst.yandex.net'
DRIVER_WALL_URL = 'http://driver-wall.taxi.tst.yandex.net'

TAXI_SECDIST_SETTINGS = '/etc/yandex/taxi-secdist/taxi.json'

API_ADMIN_URL = 'http://taxi-api-admin.taxi.tst.yandex.net'
SCRIPTS_URL = 'http://scripts.taxi.tst.yandex.net'
AUDIT_URL = 'http://audit.taxi.tst.yandex.net'
TERRITORIES_API_URL = 'http://territories.taxi.tst.yandex.net'
ARCHIVE_API_URL = 'http://archive-api.taxi.tst.yandex.net'
ORDER_ARCHIVE_URL = 'http://order-archive.taxi.tst.yandex.net'
SUBVENTIONS_API_URL = 'http://billing-subventions.taxi.tst.yandex.net'
BILLING_ORDERS_API_URL = 'http://billing-orders.taxi.tst.yandex.net'
BILLING_COMMISSIONS_API_URL = 'http://billing-commissions.taxi.tst.yandex.net'
BILLING_DOCS_API_URL = 'http://billing-docs-l7.taxi.tst.yandex.net'
BILLING_REPORTS_API_URL = 'http://billing-reports.taxi.tst.yandex.net'
PLUS_WALLET_API_URL = 'http://plus-wallet.taxi.tst.yandex.net'

CONFIGS_API_HOST = 'http://configs.taxi.tst.yandex.net'
USE_CONFIGS_API = True

TAXIMETER_ADMIN_URL = 'https://taximeter-admin.taxi.tst.yandex-team.ru'

XIVA_API_HOST = 'https://push-sandbox.yandex.ru'

DEVREPLICA_SECDIST_PATH = '/etc/yandex/taxi-secdist/taxi-ro.json'

PROXY_URL_CONFIG_XIVA_FAKE_UUID = '9dda15673261477988574be31ad0326b'
PROXY_URL_CONFIG_GCM_TOPIC = '/topics/proxy_url_config_testing'
PROXY_URL_CONFIG_XIVA_USER = 'proxy.url.config.testing'

PARTNERS_REGISTRATION_MANAGER_UID = 389886597  # maslena@

TAXI_GEOFENCE_HOST = 'http://geofence.taxi.tst.yandex.net'
AMOCEM_NOTE_BILLING_TEXT = 'https://admin-balance.greed-tm.paysys.yandex-team.ru/invoices.xml?client_id={}'

TRACING_HOST = 'http://tracing.taxi.tst.yandex.net'

TAXI_EXP_URL = 'http://exp.taxi.tst.yandex.net'
TAXI_EXPERIMENTS3_URL = 'http://experiments3.taxi.tst.yandex.net'

TAXI_RENDERTEMPLATE_URL = 'http://render-template.taxi.tst.yandex.net'
TRANSACTIONS_API_URL = 'http://transactions.taxi.tst.yandex.net'

TIPS_API_URL = 'http://tips.taxi.tst.yandex.net'

PASSENGER_PROFILE_API_URL = 'http://passenger-profile.taxi.tst.yandex.net'

ORDERS_SHARDS_QUERIES_ENABLED = True

MDS_S3_EXTERNAL_URL_TEMPLATE = "https://{bucket_name}.s3.mds.yandex.net"

SHARED_PAYMENTS_URL = 'http://shared-payments.taxi.tst.yandex.net'

CARDSTORAGE_HOST = 'http://cardstorage.taxi.tst.yandex.net'

BILLING_REPLICATION_API_URL = 'http://billing-replication.taxi.tst.yandex.net'

VGW_API_HOST = 'http://vgw-api.taxi.tst.yandex.net'

# temporary: https://st.yandex-team.ru/TAXIBACKEND-21867
TAXI_TARIFFS_URL = 'http://tariffs.taxi.tst.yandex.net'

PROCESSING_HOST = 'http://processing.taxi.tst.yandex.net'

SAMSARA_API_URL = 'https://test-api.samsara.yandex-team.ru'

CRONS_HOST = 'http://crons.taxi.tst.yandex.net'

CANDIDATE_META_HOST = 'http://candidate-meta.taxi.tst.yandex.net'

STICKER_API_URL = 'http://sticker.taxi.tst.yandex.net'

PARKS_ACTIVATION_HOST = 'http://parks-activation.taxi.tst.yandex.net'

UNIQUE_DRIVERS_HOST = 'http://unique-drivers.taxi.tst.yandex.net'

DRIVER_PAYMENT_TYPES_HOST = 'http://driver-payment-types.taxi.tst.yandex.net'

DRIVER_PROFILES_HOST = 'http://driver-profiles.taxi.tst.yandex.net'

LOCALIZATIONS_REPLICA_HOST = 'http://localizations-replica.taxi.tst.yandex.net'

RECEIPT_FETCHING_URL = 'http://receipt-fetching.taxi.tst.yandex.net'
DRIVER_STATUS_HOST = 'http://driver-status.taxi.tst.yandex.net'

ORDER_CORE_API_URL = 'http://order-core.taxi.tst.yandex.net'

METADATA_STORAGE_HOST = 'http://metadata-storage.taxi.tst.yandex.net'

SUBVENTION_ORDER_CONTEXT_HOST = 'http://subvention-order-context.taxi.tst.yandex.net'
