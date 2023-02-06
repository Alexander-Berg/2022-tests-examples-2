import datetime


UTC_TZ = datetime.timezone.utc
NOW = '2020-03-13T07:19:00+00:00'
NOW_DT = datetime.datetime(2020, 3, 13, 7, 19, 00, tzinfo=UTC_TZ)

APP_IPHONE = 'lavka_iphone'
APP_WEB = 'web'
DELI_IPHONE = 'yangodeli_iphone'
DELI_ANDROID = 'yangodeli_android'
YANGO_IPHONE = 'mobileweb_yango_iphone'
YANGO_ANDROID = 'mobileweb_yango_android'
EDA_IPHONE = 'eda_webview_iphone'
EDA_ANDROID = 'eda_webview_android'

MARKET_ANDROID = 'mobileweb_market_android'
MARKET_IPHONE = 'mobileweb_market_iphone'
MARKET_ANDROID_NATIVE = 'market_android'
MARKET_IPHONE_NATIVE = 'market_iphone'
MARKET_ANDROID_V2 = 'mobileweb_market_lavka_android'
MARKET_IPHONE_V2 = 'mobileweb_market_lavka_iphone'

ORDER_ID = '319023123123r23-grocery'
SHORT_ORDER_ID = '32131-321-3412341'
TAXI_USER_ID = 'taxi:213u9dm912e321d'
EATS_USER_ID = 'test_eats_id'
PERSONAL_PHONE_ID = '1273o182j3e9w'
DEPOT_ID = '12345'
YANDEX_UID = 'test_uid'
COUNTRY_ISO3 = 'RUS'
REGION_ID = 213

STATUS_CHANGE_CODES = [
    'ready_for_pickup',
    'accepted',
    'assembling',
    'common_failure',
    'money_failure',
    'ready_for_dispatch',
    'delivering',
    'delivered',
]

LAVKA_TRACKING_DEEPLINK_PREFIX = (
    'yandexlavka://external?service=grocery&href=/order/'
)
YANGODELI_TRACKING_DEEPLINK_PREFIX = (
    'yangodeli://external?service=grocery&href=/order/'
)
