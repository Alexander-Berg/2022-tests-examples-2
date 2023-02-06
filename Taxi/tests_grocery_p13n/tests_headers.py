HEADER_TAXI_SESSION = 'taxi:uuu'
HEADER_YANDEX_UID = '13579'
HEADER_EATS_ID = '97531'
PERSONAL_PHONE_ID = 'test_phone_id'
APPMETRICA_DEVICE_ID = 'device_id'
HEADERS = {
    'X-YaTaxi-Session': HEADER_TAXI_SESSION,
    'X-Yandex-UID': HEADER_YANDEX_UID,
    'X-AppMetrica-DeviceId': APPMETRICA_DEVICE_ID,
    'X-YaTaxi-User': (
        f'eats_user_id={HEADER_EATS_ID}, personal_phone_id={PERSONAL_PHONE_ID}'
    ),
    'X-Request-Application': 'app_name=android',
}
NO_UID_HEADERS = {
    'X-YaTaxi-Session': HEADER_TAXI_SESSION,
    'X-YaTaxi-User': f'eats_user_id={HEADER_EATS_ID}',
}
