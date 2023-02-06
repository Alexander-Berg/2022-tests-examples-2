PHONE_ID = 'phone-id'
USER_ID = 'user-id'
USER_INFO = f'personal_phone_id={PHONE_ID}'
IDEMPOTENCY_TOKEN = 'token'
APP_INFO = 'app_name=android'
YANDEX_UID = 'user-uid'
DEFAULT_SESSION = 'taxi:' + USER_ID

DEFAULT_HEADERS = {
    'X-Request-Language': 'ru',
    'X-Request-Application': APP_INFO,
    'X-YaTaxi-User': USER_INFO,
    'X-Idempotency-Token': IDEMPOTENCY_TOKEN,
    'X-Yandex-UID': YANDEX_UID,
    'X-YaTaxi-Session': DEFAULT_SESSION,
}
