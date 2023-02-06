from tests_grocery_payments_methods import models


EATS_USER_ID = 'eats-user-id'
PHONE_ID = 'phone-id'
PERSONAL_PHONE_ID = 'personal-phone-id'
PERSONAL_EMAIL_ID = 'personal-email-id'
USER_ID = 'user-id'
USER_INFO = (
    f'eats_user_id={EATS_USER_ID},'
    f' personal_phone_id={PERSONAL_PHONE_ID},'
    f' personal_email_id={PERSONAL_EMAIL_ID}'
)
APP_NAME = 'mobileweb_yango_android'
APP_INFO = f'app_name={APP_NAME}'
USER_IP = '1.1.1.1'
LOGIN_ID = 'login-id'
YANDEX_UID = '12345678'
DEFAULT_SESSION = 'taxi:' + USER_ID
APPMETRICA_DEVICE_ID = 'some_appmetrica'

DEFAULT_HEADERS = {
    'X-Request-Language': 'ru',
    'X-Request-Application': APP_INFO,
    'X-YaTaxi-User': USER_INFO,
    'X-Yandex-UID': YANDEX_UID,
    'X-Remote-IP': USER_IP,
    'X-Login-Id': LOGIN_ID,
    'X-YaTaxi-Session': DEFAULT_SESSION,
    'X-YaTaxi-PhoneId': PHONE_ID,
    'X-AppMetrica-DeviceId': APPMETRICA_DEVICE_ID,
}

VERIFICATION_RESPONSE = {
    'verification_id': 'verification_id',
    'purchase_token': 'purchase_token',
}

VERIFICATION_STATUS_RESPONSE = {
    'status': '3ds_required',
    'version': 123,
    'method': 'standard2_3ds',
    '3ds_url': '3ds_url',
    'finish_binding_url': 'finish_binding_url',
    'random_amount_tries_left': 5,
}

BINDING_RESPONSE = {
    'binding_id': 'binding_id',
    'verification': {
        'id': 'id',
        'method': 'method',
        'status': 'status',
        '3ds_url': '3ds_url',
        '3ds_method': '3ds_method',
        '3ds_params': '3ds_params',
        'random_amount_tries_left': 123,
        'finish_binding_url': 'finish_binding_url',
        'status_code': 'status_code',
        'error_message': 'error_message',
    },
}

SUCCESS_BINDING_STATUS = 'success'
FAIL_BINDING_STATUS = 'failure'
IN_PROGRESS_BINDING_STATUS = 'in_progress'

MERCHANT_ANDROID = 'merchant-android'
MERCHANT_IPHONE = 'merchant-iphone'

MERCHANTS = [MERCHANT_ANDROID, MERCHANT_IPHONE]

SERVICE_TOKEN = 'grocery_service_token'

METHODS_FALLBACK_NAME = 'some_fallback_name'

BANKS = [models.SbpBankInfo(bank_name=f'bank_name:{i}') for i in range(5)]

BANKS_META = [bank.to_exp_meta() for bank in BANKS]

BANKS_META[1]['priority'] = 1
BANKS_META[2]['priority'] = 2
BANKS_META[3]['priority'] = 1
BANKS_META[4]['enabled'] = False
