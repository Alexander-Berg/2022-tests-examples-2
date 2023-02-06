DEFAULT_YABANK_SESSION_UUID = 'session_uuid_1'
DEFAULT_YABANK_PHONE_ID = 'phone_id_1'
DEFAULT_YANDEX_BUID = 'buid_1'
DEFAULT_YANDEX_UID = 'uid_1'
DEFAULT_LANGUAGE = 'ru'
DEFAULT_USER_TICKET = 'user_ticket_1'

ACCEPTABLE_PAYMENT_SYSTEMS = ['VISA', 'MIR', 'MASTERCARD', 'AMERICAN_EXPRESS']


def default_headers():
    return {
        'X-YaBank-SessionUUID': DEFAULT_YABANK_SESSION_UUID,
        'X-YaBank-PhoneID': DEFAULT_YABANK_PHONE_ID,
        'X-Yandex-BUID': DEFAULT_YANDEX_BUID,
        'X-Yandex-UID': DEFAULT_YANDEX_UID,
        'X-Request-Language': DEFAULT_LANGUAGE,
        'X-Ya-User-Ticket': DEFAULT_USER_TICKET,
    }
