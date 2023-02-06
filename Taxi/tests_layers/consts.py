DEFAULT_APPLICATION = (
    'app_name=iphone,app_ver1=3,app_ver2=2,app_ver3=4,app_brand=yataxi'
)

USER_ID = '12345678901234567890123456789012'

NOT_AUTHORIZED_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-Request-Application': DEFAULT_APPLICATION,
    'X-Request-Language': 'ru',
    'X-AppMetrica-DeviceId': 'DeviceId',
    'X-AppMetrica-UUID': 'UUID',
}

AUTHORIZED_HEADERS = {
    **NOT_AUTHORIZED_HEADERS,
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '400000000',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-YaTaxi-Bound-Uids': '834149473,834149474',
}
