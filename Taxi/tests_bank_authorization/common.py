FPS_BANK_UID = 'a41a2ef0-2140-4037-85b5-ebaa12e34224'
FPS_REQUEST_ID = 'e47140c9-2843-4004-b8f2-4f6e2af06172'

BANK_UID1 = '2d84c907-d071-49b1-8c56-f107a7bb8592'
BANK_UID2 = '6273cf55-411a-4252-a953-a25bcddf3d1f'
PHONE_NUMBER1 = '+71234567890'
PHONE_NUMBER1_MASKED = '+71234****90'
PHONE_NUMBER2 = '+79876543210'
PHONE_NUMBER2_MASKED = '+79876****10'


def get_headers(buid, idem_token=None, language='ru'):
    result = {
        'X-YaBank-SessionUUID': 'session_uuid',
        'X-YaBank-PhoneID': 'phone_id',
        'X-Yandex-BUID': buid,
        'X-Yandex-UID': 'uid',
        'X-Ya-User-Ticket': 'user_ticket',
    }
    if idem_token is not None:
        result['X-Idempotency-Token'] = idem_token
    if language is not None:
        result['X-Request-Language'] = language
    return result


def get_support_headers(token='allow'):
    result = {'X-Bank-Token': token}
    return result
