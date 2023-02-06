EATS_USER_ID = 'eats-user-id'
PERSONAL_PHONE_ID = 'personal-phone-id'
PERSONAL_EMAIL_ID = 'personal-email-id'
APP_NAME = 'mobileweb_yango_android'
APP_INFO = f'app_name={APP_NAME}'
USER_INFO = (
    f'eats_user_id={EATS_USER_ID},'
    f' personal_phone_id={PERSONAL_PHONE_ID},'
    f' personal_email_id={PERSONAL_EMAIL_ID}'
)
YANDEX_UID = '12345678'
USER_IP = '1.1.1.1'
LOGIN_ID = 'login-id'
USER_ID = 'user-id'
DEFAULT_SESSION = 'taxi:' + USER_ID
PHONE_ID = 'phone-id'
APPMETRICA_DEVICE_ID = 'some_appmetrica'
HEADER_APP_INFO_YANGO = {'X-Request-Application': 'app_name=yango_android'}
LOCALE = 'ru'


DEFAULT_HEADERS = {
    'X-Request-Language': LOCALE,
    'X-Request-Application': APP_INFO,
    'X-YaTaxi-User': USER_INFO,
    'X-Yandex-UID': YANDEX_UID,
    'X-Remote-IP': USER_IP,
    'X-Login-Id': LOGIN_ID,
    'X-YaTaxi-Session': DEFAULT_SESSION,
    'X-YaTaxi-PhoneId': PHONE_ID,
    'X-AppMetrica-DeviceId': APPMETRICA_DEVICE_ID,
}
