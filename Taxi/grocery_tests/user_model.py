APP_NAME = 'mobileweb_yango_android'
APP_INFO = f'app_name={APP_NAME}'

EATS_USER_ID = 'eats-user-id'
PERSONAL_PHONE_ID = 'personal-phone-id'
USER_INFO = (
    f'eats_user_id={EATS_USER_ID}, personal_phone_id={PERSONAL_PHONE_ID}'
)

IDEMPOTENCY_TOKEN = 'token'
YANDEX_UID = 'user-uid'
USER_IP = '1.1.1.1'
LOGIN_ID = 'login-id'

USER_ID = 'user-id'
DEFAULT_SESSION = 'taxi:' + USER_ID

PHONE_ID = 'phone-id'
APPMETRICA_DEVICE_ID = 'some_appmetrica'

DEFAULT_HEADERS = {
    'X-Request-Language': 'ru',
    'X-Request-Application': APP_INFO,
    'X-YaTaxi-User': USER_INFO,
    'X-Idempotency-Token': IDEMPOTENCY_TOKEN,
    'X-Yandex-UID': YANDEX_UID,
    'X-Remote-IP': USER_IP,
    'X-Login-Id': LOGIN_ID,
    'X-YaTaxi-Session': DEFAULT_SESSION,
    'X-YaTaxi-PhoneId': PHONE_ID,
    'X-AppMetrica-DeviceId': APPMETRICA_DEVICE_ID,
}


class GroceryUser:
    def __init__(self) -> None:
        pass

    def get_headers(self):
        return DEFAULT_HEADERS

    def get_location(self):
        return [37.371618, 55.840757]
