import collections

from tests_bank_applications import common
from tests_bank_applications import db_helpers

MOCK_NOW = '2021-09-28T19:31:00+00:00'

PersonalData = collections.namedtuple(
    'PersonalData',
    [
        'yandex_uid',
        'version',
        'idempotency_token',
        'last_name',
        'first_name',
        'middle_name',
        'passport_number',
        'birthday',
        'inn_or_snils',
    ],
)


def select_last_personal_data(pgsql, yandex_uid):
    sql = """
        SELECT yandex_uid, version, idempotency_token, last_name,
        first_name, middle_name, passport_number, birthday::TEXT, inn_or_snils
        FROM bank_applications.registration_applications_personal_data
        WHERE yandex_uid = %s
        ORDER BY version DESC LIMIT 1
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [yandex_uid])
    records = cursor.fetchall()
    if not records:
        return None
    assert len(records) == 1
    result_dict = PersonalData(*(records[0]))
    return result_dict


def find_personal_data(pgsql, idempotency_token):
    sql = """
        SELECT yandex_uid, version, idempotency_token, last_name,
        first_name, middle_name, passport_number, birthday::TEXT, inn_or_snils
        FROM bank_applications.registration_applications_personal_data
        WHERE idempotency_token = %s
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [idempotency_token])
    records = cursor.fetchall()
    if not records:
        return None
    assert len(records) == 1
    result_dict = PersonalData(*(records[0]))
    return result_dict


def insert_personal_data(
        pgsql,
        yandex_uid,
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        last_name=common.LAST_NAME,
        first_name=common.FIRST_NAME,
        middle_name=common.MIDDLE_NAME,
        passport_number=common.PASSPORT_NUMBER,
        birthday=common.BIRTHDAY,
        inn_or_snils=common.SNILS,
):
    sql = """
        INSERT INTO bank_applications.registration_applications_personal_data(
            yandex_uid, idempotency_token, last_name, first_name, middle_name,
        passport_number, birthday, inn_or_snils)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        sql,
        [
            yandex_uid,
            idempotency_token,
            last_name,
            first_name,
            middle_name,
            passport_number,
            birthday,
            inn_or_snils,
        ],
    )


async def test_set_personal_data_ok(taxi_bank_applications, pgsql):
    application_id = db_helpers.add_application_registration(
        pgsql, common.DEFAULT_YANDEX_UID, common.STATUS_CREATED,
    )
    response = await taxi_bank_applications.post(
        '/applications/v1/registration/set_personal_data',
        headers={'X-Idempotency-Token': common.DEFAULT_IDEMPOTENCY_TOKEN},
        json={
            'yandex_uid': common.DEFAULT_YANDEX_UID,
            'last_name': common.LAST_NAME,
            'first_name': common.FIRST_NAME,
            'middle_name': common.MIDDLE_NAME,
            'passport_number': common.PASSPORT_NUMBER,
            'birthday': common.BIRTHDAY,
            'inn_or_snils': common.SNILS,
        },
    )

    assert response.status_code == 200
    personal_data = select_last_personal_data(pgsql, common.DEFAULT_YANDEX_UID)
    assert personal_data.yandex_uid == common.DEFAULT_YANDEX_UID
    assert personal_data.version == 1
    assert personal_data.idempotency_token == common.DEFAULT_IDEMPOTENCY_TOKEN
    assert personal_data.last_name == common.LAST_NAME
    assert personal_data.first_name == common.FIRST_NAME
    assert personal_data.middle_name == common.MIDDLE_NAME
    assert personal_data.passport_number == common.PASSPORT_NUMBER
    assert personal_data.birthday == common.BIRTHDAY
    assert personal_data.inn_or_snils == common.SNILS


async def test_set_personal_data_no_application(taxi_bank_applications, pgsql):
    response = await taxi_bank_applications.post(
        '/applications/v1/registration/set_personal_data',
        headers={'X-Idempotency-Token': common.DEFAULT_IDEMPOTENCY_TOKEN},
        json={
            'yandex_uid': common.DEFAULT_YANDEX_UID,
            'last_name': common.LAST_NAME,
            'first_name': common.FIRST_NAME,
            'middle_name': common.MIDDLE_NAME,
            'passport_number': common.PASSPORT_NUMBER,
            'birthday': common.BIRTHDAY,
            'inn_or_snils': common.SNILS,
        },
    )

    assert response.status_code == 200


async def test_set_personal_data_idempotency_200(
        taxi_bank_applications, pgsql,
):
    application_id = db_helpers.add_application_registration(
        pgsql, common.DEFAULT_YANDEX_UID, common.STATUS_CREATED,
    )
    insert_personal_data(pgsql, common.DEFAULT_YANDEX_UID)
    response = await taxi_bank_applications.post(
        '/applications/v1/registration/set_personal_data',
        headers={'X-Idempotency-Token': common.DEFAULT_IDEMPOTENCY_TOKEN},
        json={
            'yandex_uid': common.DEFAULT_YANDEX_UID,
            'last_name': common.LAST_NAME,
            'first_name': common.FIRST_NAME,
            'middle_name': common.MIDDLE_NAME,
            'passport_number': common.PASSPORT_NUMBER,
            'birthday': common.BIRTHDAY,
            'inn_or_snils': common.SNILS,
        },
    )
    assert response.status_code == 200


async def test_set_personal_data_idempotency_409(
        taxi_bank_applications, pgsql,
):
    application_id = db_helpers.add_application_registration(
        pgsql, common.DEFAULT_YANDEX_UID, common.STATUS_CREATED,
    )
    insert_personal_data(pgsql, common.DEFAULT_YANDEX_UID, middle_name=None)
    response = await taxi_bank_applications.post(
        '/applications/v1/registration/set_personal_data',
        headers={'X-Idempotency-Token': common.DEFAULT_IDEMPOTENCY_TOKEN},
        json={
            'yandex_uid': common.DEFAULT_YANDEX_UID,
            'last_name': common.LAST_NAME,
            'first_name': common.FIRST_NAME,
            'middle_name': common.MIDDLE_NAME,
            'passport_number': common.PASSPORT_NUMBER,
            'birthday': common.BIRTHDAY,
            'inn_or_snils': common.SNILS,
        },
    )
    assert response.status_code == 409


async def test_set_personal_data_second_version(taxi_bank_applications, pgsql):
    application_id = db_helpers.add_application_registration(
        pgsql, common.DEFAULT_YANDEX_UID, common.STATUS_CREATED,
    )
    insert_personal_data(
        pgsql, common.DEFAULT_YANDEX_UID, common.NOT_DEFAULT_IDEMPOTENCY_TOKEN,
    )
    response = await taxi_bank_applications.post(
        '/applications/v1/registration/set_personal_data',
        headers={'X-Idempotency-Token': common.DEFAULT_IDEMPOTENCY_TOKEN},
        json={
            'yandex_uid': common.DEFAULT_YANDEX_UID,
            'last_name': common.LAST_NAME,
            'first_name': common.FIRST_NAME,
            'middle_name': common.MIDDLE_NAME,
            'passport_number': common.PASSPORT_NUMBER,
            'birthday': common.BIRTHDAY,
            'inn_or_snils': common.SNILS,
        },
    )

    assert response.status_code == 200
    personal_data = select_last_personal_data(pgsql, common.DEFAULT_YANDEX_UID)
    assert personal_data.yandex_uid == common.DEFAULT_YANDEX_UID
    assert personal_data.version == 2
    assert personal_data.idempotency_token == common.DEFAULT_IDEMPOTENCY_TOKEN
    assert personal_data.last_name == common.LAST_NAME
    assert personal_data.first_name == common.FIRST_NAME
    assert personal_data.middle_name == common.MIDDLE_NAME
    assert personal_data.passport_number == common.PASSPORT_NUMBER
    assert personal_data.birthday == common.BIRTHDAY
    assert personal_data.inn_or_snils == common.SNILS


async def test_get_personal_data_ok(taxi_bank_applications, pgsql):
    application_id = db_helpers.add_application_registration(
        pgsql, common.DEFAULT_YANDEX_UID, common.STATUS_CREATED,
    )
    insert_personal_data(pgsql, common.DEFAULT_YANDEX_UID)
    response = await taxi_bank_applications.post(
        '/applications-internal/v1/registration/get_personal_data',
        json={'yandex_uid': common.DEFAULT_YANDEX_UID},
    )

    assert response.status_code == 200
    assert response.json() == {
        'last_name': common.LAST_NAME,
        'first_name': common.FIRST_NAME,
        'middle_name': common.MIDDLE_NAME,
        'passport_number': common.PASSPORT_NUMBER,
        'birthday': common.BIRTHDAY,
        'inn_or_snils': common.SNILS,
    }


async def test_get_personal_data_not_found(taxi_bank_applications):
    response = await taxi_bank_applications.post(
        '/applications-internal/v1/registration/get_personal_data',
        json={'yandex_uid': common.DEFAULT_YANDEX_UID},
    )

    assert response.status_code == 404
