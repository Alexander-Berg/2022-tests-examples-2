AUTH_PARAMS = {'db': 'db_id1', 'session': 'session1'}
HEADERS = {'User-Agent': 'Taximeter 8.80 (562)', 'Accept-Language': 'ru'}
HEADERS_V2 = {
    'User-Agent': 'Taximeter 8.80 (562)',
    'Accept-Language': 'ru',
    'X-YaTaxi-Park-Id': 'db_id1',
    'X-YaTaxi-Driver-Profile-Id': 'uuid1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.77 (456)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}
UNAUTH_HEADERS_V2 = {
    'User-Agent': 'Taximeter 8.80 (562)',
    'Accept-Language': 'ru',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.77 (456)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}
V1_BANNERS_REDIRECT_URL = (
    'https://taximeter-core.tst.'
    'mobile.yandex.net/driver/pro'
    'file-view/v1/banners-redirect'
    '?id=test_with_auth&db={dbid}&'
    'session={session}'
)
V2_BANNERS_REDIRECT_URL = (
    'https://taximeter-core.tst.'
    'mobile.yandex.net/driver/v1/'
    'profile-view/v2/banners-redi'
    'rect?id=test_with_auth&db='
    '{dbid}&session={session}'
)
V1_COVID_BANNERS_URL = (
    'https://taximeter.yandex.rostaxi.org/'
    'driver/profile-view/v1/covid-permit-'
    'banner?db={dbid}&session={session}'
)
V2_COVID_BANNERS_URL = (
    'https://taximeter.yandex.rostaxi.org/'
    'driver/v1/profile-view/v2/covid-permit-'
    'banner?db={dbid}&session={session}'
)

ERROR_JSON = {'message': 'Server error', 'code': '500'}

DEFAULT_PARKS = [
    {
        'id': 'some_id',
        'login': 'some_login',
        'name': 'some_name',
        'is_active': True,
        'city_id': 'Дзержинский',
        'locale': 'ru',
        'is_billing_enabled': True,
        'is_franchising_enabled': True,
        'demo_mode': False,
        'country_id': 'rus',
        'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
    },
]

DEFAULT_RATING = {'rating': '5.0', 'unique_driver_id': 'unique_driver_id'}

DEFAULT_TARIFFS = [
    {'tariff_name': 'эконом', 'text_info': 'Доступен', 'is_blocked': False},
    {
        'tariff_name': 'бизнес',
        'text_info': 'Нужен экзамен',
        'is_blocked': True,
        'request_exam_pass': False,
    },
    {'tariff_name': 'Комфорт', 'text_info': 'Доступен', 'is_blocked': True},
]

DEFAULT_KARMA_POINTS = {
    'unique_driver_id': 'unique_driver_id',
    'disable_threshold': 5,
    'taxi_city': 'Москва',
    'value': 150,
    'warn_threshold': 10,
}

DEFAULT_EXAM_SCORE = 10.0
