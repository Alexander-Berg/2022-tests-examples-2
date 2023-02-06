PHONE_ID = 'phone-id'
PERSONAL_PHONE_ID = 'personal-phone-id'
LOGIN_ID = 'login-id'
USER_ID = 'user-id'
USER_INFO = f'personal_phone_id={PERSONAL_PHONE_ID}'

ANDROID_APP_NAME = 'lavka_android'
IPHONE_APP_NAME = 'lavka_iphone'

APP_INFO = f'app_name={IPHONE_APP_NAME}'
YANDEX_UID = '12345678990'
DEFAULT_SESSION = 'taxi:' + USER_ID
DEFAULT_IP = '192.168.1.0'
DEFAULT_LOCALE = 'ru'
DEFAULT_USER_INFO = {
    'user_ip': DEFAULT_IP,
    'yandex_uid': YANDEX_UID,
    'login_id': LOGIN_ID,
    'personal_phone_id': PERSONAL_PHONE_ID,
    'is_portal': False,
    'locale': DEFAULT_LOCALE,
}

X_YANDEX_UID = 'X-Yandex-UID'
DEFAULT_HEADERS = {
    'X-LOGIN-ID': LOGIN_ID,
    'X-Request-Language': DEFAULT_LOCALE,
    'X-Request-Application': APP_INFO,
    'X-YaTaxi-User': USER_INFO,
    X_YANDEX_UID: YANDEX_UID,
    'X-YaTaxi-Session': DEFAULT_SESSION,
    'X-YaTaxi-PhoneId': PHONE_ID,
    'X-Remote-IP': DEFAULT_IP,
}
