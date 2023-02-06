import datetime

import aiohttp

DEFAULT_YABANK_SESSION_UUID = 'session_uuid_1'
DEFAULT_YABANK_PHONE_ID = 'phone_id_1'
DEFAULT_NEW_PHONE_ID = 'phone_id_2'
DEFAULT_YANDEX_BUID = '67754336-d4d1-43c1-aadb-cabd06674ea6'
SESSION_STATUS_NOT_REGISTERED = 'not_registered'
TEST_ONE_YANDEX_BUID = 'TEST_ONE'
DEFAULT_YANDEX_UID = '111111111'
INITIATOR = {'initiator_type': 'BUID', 'initiator_id': DEFAULT_YANDEX_BUID}
USER_ID_TYPE_BUID = 'BUID'
TRACK_ID = 'some_track_id'
DEFAULT_IDEMPOTENCY_TOKEN = '67754336-d4d1-43c1-aadb-cabd06674ea6'
NOT_DEFAULT_IDEMPOTENCY_TOKEN = '7ed58d18-63aa-4838-9ec7-8dfbf9e9d6bb'
DEFAULT_LANGUAGE = 'ru'
SOME_IP = '127.0.0.1'
PASSPORT_CLIENT_SCHEME = 'https'
DEFAULT_PHONE = '+70001002020'
PASSPORT_PAGE_FORMAT = 'passport_page_{}'
AVATARS_IMAGE_URL = '/get-fintech-passports/{group_id}/{image_name}/'
OK = 'ok'
NOK = 'nok'
DEFAULT_USER_TICKET = 'user_ticket'
LAST_NAME = 'петров'
FIRST_NAME = 'петр'
MIDDLE_NAME = 'петрович'
PASSPORT_NUMBER = '4518710711'
BIRTHDAY = '1994-11-15'
SNILS = '08976857866'
INN = '088816660222'
STATUS_SUBMITTED = 'SUBMITTED'
STATUS_CREATED = 'CREATED'
STATUS_PROCESSING = 'PROCESSING'
STATUS_PENDING = 'PENDING'
STATUS_SUCCESS = 'SUCCESS'
STATUS_FAILED = 'FAILED'
STATUS_FINAL = 'FINAL'
STATUS_AGREEMENTS_ACCEPTED = 'AGREEMENTS_ACCEPTED'
STATUS_CORE_BANKING = 'CORE_BANKING'
STATUS_DRAFT_SAVED = 'DRAFT_SAVED'
STATUS_CANCELLED = 'CANCELLED'
SUPPORT_LOGIN = 'support-abc'
SUPPORT_TOKEN = (
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJzdWIiOiJzdXBwb3J0LWFiYyJ9.'
)
SUPPORT_INITIATOR = {
    'initiator_type': 'SUPPORT',
    'initiator_id': SUPPORT_LOGIN,
}
PRODUCT_WALLET = 'WALLET'
PRODUCT_PRO = 'PRO'
CORE_REQUEST_ID = 'some_javist_id'
VALID_ESIA_RAW_RESPONSE = 'valid_esia_raw_response'
INVALID_ESIA_RAW_RESPONSE = 'invalid_esia_raw_response'


def default_headers(locale=DEFAULT_LANGUAGE):
    return {
        'X-YaBank-SessionStatus': SESSION_STATUS_NOT_REGISTERED,
        'X-YaBank-SessionUUID': DEFAULT_YABANK_SESSION_UUID,
        'X-YaBank-PhoneID': DEFAULT_YABANK_PHONE_ID,
        'X-Yandex-BUID': DEFAULT_YANDEX_BUID,
        'X-Yandex-UID': DEFAULT_YANDEX_UID,
        'X-Request-Language': locale,
        'X-Remote-IP': SOME_IP,
        'X-Ya-User-Ticket': DEFAULT_USER_TICKET,
    }


def headers_with_idempotency(idempotency_token=DEFAULT_IDEMPOTENCY_TOKEN):
    default = default_headers()
    default['X-Idempotency-Token'] = idempotency_token
    return default


def headers_without_buid():
    default = default_headers()
    default.pop('X-Yandex-BUID')
    return default


def headers_without_uid():
    default = default_headers()
    default.pop('X-Yandex-UID')
    return default


def headers_wo_buid_w_idempotency(idempotency_token=DEFAULT_IDEMPOTENCY_TOKEN):
    default = default_headers()
    default['X-Idempotency-Token'] = idempotency_token
    default.pop('X-Yandex-BUID')
    return default


def get_current_ts_with_shift(mocked_time, shift=0):
    return int(
        mocked_time.now().replace(tzinfo=datetime.timezone.utc).timestamp()
        + shift,
    )


def make_request_form(
        application_id,
        image_blob,
        page_number,
        avatars_mds_mock,
        group_id,
        image_name,
):
    avatars_mds_mock.set_group_id(group_id)
    avatars_mds_mock.set_image_name(image_name)

    with aiohttp.MultipartWriter('form-data') as data:
        payload = aiohttp.payload.StringPayload(application_id)
        payload.set_content_disposition('form-data', name='application_id')
        data.append_payload(payload)

        payload = aiohttp.payload.BytesPayload(
            image_blob, headers={'Content-Type': 'image/jpeg'},
        )
        payload.set_content_disposition('form-data', name='passport_photo')
        data.append_payload(payload)

        payload = aiohttp.payload.StringPayload(page_number)
        payload.set_content_disposition('form-data', name='page_number')
        data.append_payload(payload)

    headers = {
        'Content-Type': 'multipart/form-data; boundary=' + data.boundary,
    }
    return data, headers


def check_equal_without_add_params(
        pg_application_after, pg_application_before,
):
    assert (
        pg_application_before.application_id
        == pg_application_after.application_id
    )
    assert (
        pg_application_before.user_id_type == pg_application_after.user_id_type
    )
    assert pg_application_before.user_id == pg_application_after.user_id
    assert pg_application_before.type == pg_application_after.type
    assert (
        pg_application_before.multiple_success_status_allowed
        == pg_application_after.multiple_success_status_allowed
    )
    assert pg_application_before.initiator == pg_application_after.initiator


def get_image_url(host, group_id, image_name):
    return host + AVATARS_IMAGE_URL.format(
        group_id=group_id, image_name=image_name,
    )


def get_support_headers(token='allow'):
    result = {'X-Bank-Token': token}
    return result


def status_to_common(status):
    result = None
    if status in [STATUS_CREATED, STATUS_DRAFT_SAVED]:
        result = STATUS_CREATED
    elif status in [
        STATUS_AGREEMENTS_ACCEPTED,
        STATUS_SUBMITTED,
        STATUS_PROCESSING,
        STATUS_CORE_BANKING,
    ]:
        result = STATUS_PROCESSING
    elif status in [STATUS_SUCCESS]:
        result = STATUS_SUCCESS
    elif status in [STATUS_CANCELLED, STATUS_FAILED]:
        result = STATUS_FAILED
    assert result
    return result


def get_standard_form():
    return {
        'last_name': LAST_NAME,
        'first_name': FIRST_NAME,
        'middle_name': MIDDLE_NAME,
        'passport_number': PASSPORT_NUMBER,
        'birthday': BIRTHDAY,
        'inn_or_snils': SNILS,
    }


def get_standard_submitted_form():
    return {
        'last_name': LAST_NAME,
        'first_name': FIRST_NAME,
        'middle_name': MIDDLE_NAME,
        'passport_number': PASSPORT_NUMBER,
        'birthday': BIRTHDAY,
        'snils': SNILS,
    }


def get_standard_normalized_form():
    return {
        'last_name': LAST_NAME.capitalize(),
        'first_name': FIRST_NAME.capitalize(),
        'middle_name': MIDDLE_NAME.capitalize(),
        'passport_number': PASSPORT_NUMBER,
        'birthday': BIRTHDAY,
        'snils': SNILS,
    }


def get_kyc_standard_form():
    return {
        'last_name': LAST_NAME,
        'first_name': FIRST_NAME,
        'patronymic': MIDDLE_NAME,
        'id_doc_number': PASSPORT_NUMBER,
        'birthday': BIRTHDAY,
        'inn': INN,
        'snils': SNILS,
        'sex': 'M',
        'birth_place_info': {'country_code': 'RU', 'place': 'Москва'},
        'id_doc_issued': '2070-01-01',
        'id_doc_issued_by': 'МВД РФ',
        'id_doc_department_code': '110-630',
        'address_registration': {
            'country': 'Россия',
            'postal_code': '350000',
            'region': 'Московская обл.',
            'city': 'Москва',
            'area': 'Раменки',
            'street': 'ул. Пушкина',
            'house': 'Колотушкина',
            'building': '1',
            'flat': '1',
        },
        'address_actual': {
            'country': 'Россия',
            'postal_code': '350000',
            'region': 'Московская обл.',
            'city': 'Москва',
            'area': 'Раменки',
            'street': 'ул. Пушкина',
            'house': 'Колотушкина',
            'building': '1',
            'flat': '1',
        },
    }
