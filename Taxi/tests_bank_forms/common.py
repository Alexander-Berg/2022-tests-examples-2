import dataclasses


KYC_FIELDS = [
    'form_id',
    'bank_uid',
    'phone',
    'birthday',
    'first_name',
    'inn_or_snils',
    'last_name',
    'middle_name',
    'passport_date',
    'passport_issue_place',
    'passport_number',
    'passport_subdivision_code',
    'place_of_birth',
    'registration_address',
    'passport_info_changed_by',
]


DEFAULT_YABANK_SESSION_UUID = 'session_uuid_1'
DEFAULT_YABANK_PHONE_ID = 'phone_id_1'
DEFAULT_YANDEX_BUID = 'buid_1'
TEST_ONE_YANDEX_BUID = 'TEST_ONE'
DEFAULT_YANDEX_UID = 'uid_1'
DEFAULT_USER_TICKET = 'user_ticket_1'
TRACK_ID = 'some_track_id'
DEFAULT_IDEMPOTENCY_TOKEN = '67754336-d4d1-43c1-aadb-cabd06674ea6'
DEFAULT_LANGUAGE = 'ru'
SOME_IP = '127.0.0.1'
PASSPORT_CLIENT_SCHEME = 'https'
DEFAULT_YANDEX_PHONE = '88005552018'
DEFAULT_YANDEX_LAST_NAME = 'Петров'
DEFAULT_YANDEX_FIRST_NAME = 'Петр'
DEFAULT_YANDEX_MIDDLE_NAME = 'Петрович'
DEFAULT_YANDEX_BIRTHDAY = '1973-01-20'
DEFAULT_YANDEX_PASSPORT_NUMBER = '4518710759'
DEFAULT_YANDEX_INN_OR_SNILS = 'inn'
DEFAULT_YANDEX_PASSPORT_DATE = '2018-01-28'
DEFAULT_YANDEX_PASSPORT_ISSUE_PLACE = 'Г.Москва'
DEFAULT_YANDEX_PASSPORT_SUBDIVISION_CODE = '111-111'
DEFAULT_YANDEX_PLACE_OF_BIRTH = 'Москва'
DEFAULT_YANDEX_REGISTRATION_ADDRESS = 'Москва улица пушкина, дом колотушкина'
DEFAULT_YANDEX_PASSPORT_INFO_CHANGED_BY = 'yandex'


@dataclasses.dataclass
class DefaultKycParams:
    bank_uid: str = DEFAULT_YANDEX_BUID
    phone: str = DEFAULT_YANDEX_PHONE
    last_name: str = DEFAULT_YANDEX_LAST_NAME
    first_name: str = DEFAULT_YANDEX_FIRST_NAME
    middle_name: str = DEFAULT_YANDEX_MIDDLE_NAME
    birthday: str = DEFAULT_YANDEX_BIRTHDAY
    passport_number: str = DEFAULT_YANDEX_PASSPORT_NUMBER
    inn_or_snils: str = DEFAULT_YANDEX_INN_OR_SNILS
    passport_date: str = DEFAULT_YANDEX_PASSPORT_DATE
    passport_issue_place: str = DEFAULT_YANDEX_PASSPORT_ISSUE_PLACE
    passport_subdivision_code: str = DEFAULT_YANDEX_PASSPORT_SUBDIVISION_CODE
    place_of_birth: str = DEFAULT_YANDEX_PLACE_OF_BIRTH
    registration_address: str = DEFAULT_YANDEX_REGISTRATION_ADDRESS
    passport_info_changed_by: str = DEFAULT_YANDEX_PASSPORT_INFO_CHANGED_BY


def default_headers():
    return {
        'X-YaBank-SessionUUID': DEFAULT_YABANK_SESSION_UUID,
        'X-YaBank-PhoneID': DEFAULT_YABANK_PHONE_ID,
        'X-Yandex-BUID': DEFAULT_YANDEX_BUID,
        'X-Yandex-UID': DEFAULT_YANDEX_UID,
        'X-Request-Language': DEFAULT_LANGUAGE,
        'X-Remote-IP': SOME_IP,
        'X-Ya-User-Ticket': DEFAULT_USER_TICKET,
    }


def insert_kyc_sql(params=DefaultKycParams()):
    sql = """INSERT INTO bank_forms.kyc
    (bank_uid,
    """
    if params.phone is not None:
        sql += ' phone, '
    sql += f"""last_name,
        first_name,
        middle_name,
        birthday,
        passport_number,
        inn_or_snils,
        passport_date,
        passport_issue_place,
        passport_subdivision_code,
        place_of_birth,
        registration_address,
        passport_info_changed_by)
        VALUES ('{params.bank_uid}',
        """
    if params.phone is not None:
        sql += f"""'{params.phone}', """
    sql += f"""
        '{params.last_name}',
        '{params.first_name}',
        '{params.middle_name}',
        '{params.birthday}',
        '{params.passport_number}',
        '{params.inn_or_snils}',
        '{params.passport_date}',
        '{params.passport_issue_place}',
        '{params.passport_subdivision_code}',
        '{params.place_of_birth}',
        '{params.registration_address}',
        '{params.passport_info_changed_by}')
    """
    return sql


def insert_default_kyc_form(pgsql, params=DefaultKycParams()):
    cursor = pgsql['bank_forms'].cursor()
    sql = insert_kyc_sql(params)
    cursor.execute(sql)


def assert_default(resp, params=DefaultKycParams()):
    assert resp['phone'] == params.phone
    assert str(resp['birthday']) == str(params.birthday)
    assert resp['first_name'] == params.first_name
    assert resp['inn_or_snils'] == params.inn_or_snils
    assert resp['last_name'] == params.last_name
    assert resp['middle_name'] == params.middle_name
    assert str(resp['passport_date']) == str(params.passport_date)
    assert resp['passport_issue_place'] == params.passport_issue_place
    assert resp['passport_number'] == params.passport_number
    assert (
        resp['passport_subdivision_code'] == params.passport_subdivision_code
    )
    assert resp['place_of_birth'] == params.place_of_birth
    assert resp['registration_address'] == params.registration_address
    assert resp['passport_info_changed_by'] == params.passport_info_changed_by


def assert_default_without_phone(resp, params=DefaultKycParams()):
    assert 'phone' not in resp.keys()
    resp_copy = resp.copy()
    resp_copy['phone'] = ''
    params.phone = ''
    assert_default(resp_copy, params)


def kyc_sum_records(pgsql, bank_uid):
    cursor = pgsql['bank_forms'].cursor()
    cursor.execute(
        (
            'SELECT COUNT(*)'
            ' FROM bank_forms.kyc '
            f'WHERE bank_uid = \'{bank_uid}\''
        ),
    )
    return int(cursor.fetchall()[0][0])


def kyc_body():
    return {
        'form': {
            'bank_uid': DEFAULT_YANDEX_BUID,
            'phone': DEFAULT_YANDEX_PHONE,
            'birthday': DEFAULT_YANDEX_BIRTHDAY,
            'first_name': DEFAULT_YANDEX_FIRST_NAME,
            'inn_or_snils': DEFAULT_YANDEX_INN_OR_SNILS,
            'last_name': DEFAULT_YANDEX_LAST_NAME,
            'middle_name': DEFAULT_YANDEX_MIDDLE_NAME,
            'passport_date': DEFAULT_YANDEX_PASSPORT_DATE,
            'passport_issue_place': DEFAULT_YANDEX_PASSPORT_ISSUE_PLACE,
            'passport_number': DEFAULT_YANDEX_PASSPORT_NUMBER,
            'passport_subdivision_code': (
                DEFAULT_YANDEX_PASSPORT_SUBDIVISION_CODE
            ),
            'place_of_birth': DEFAULT_YANDEX_PLACE_OF_BIRTH,
            'registration_address': DEFAULT_YANDEX_REGISTRATION_ADDRESS,
            'passport_info_changed_by': (
                DEFAULT_YANDEX_PASSPORT_INFO_CHANGED_BY
            ),
        },
    }


def select_kyc_form_parameter(pgsql, bank_uid, parameter):
    cursor = pgsql['bank_forms'].cursor()
    cursor.execute(
        (
            'SELECT '
            f'{parameter}'
            ' FROM bank_forms.kyc '
            f'WHERE bank_uid = \'{bank_uid}\' '
            'ORDER BY form_id DESC '
            'LIMIT 1'
        ),
    )
    return cursor.fetchall()


def select_kyc_form(pgsql, bank_uid):
    result = dict()
    for field in KYC_FIELDS:
        value = select_kyc_form_parameter(pgsql, bank_uid, field)
        if value:
            result[field] = value[0][0]
    return result
