import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers

CORE_REQUEST_ID = 'some_javist_id'


def get_add_params(pgsql, application_id):
    sql = """
            SELECT additional_params 
            FROM bank_applications.applications
            WHERE application_id = %s
            UNION ALL
            SELECT additional_params 
            FROM bank_applications.registration_applications
            WHERE application_id = %s
        """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id, application_id])
    records = cursor.fetchall()
    return records


def get_status(pgsql, application_id):
    sql = """
            SELECT status::TEXT 
            FROM bank_applications.applications
            WHERE application_id = %s
            UNION ALL
            SELECT status_text as status 
            FROM bank_applications.registration_applications
            WHERE application_id = %s
        """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id, application_id])
    records = cursor.fetchall()
    return records


def update_add_params(pgsql, application_id):

    sql = """
            UPDATE bank_applications.applications
            SET additional_params=%s
            WHERE application_id=%s
        """
    sql2 = """
            UPDATE bank_applications.registration_applications
            SET additional_params=%s
            WHERE application_id=%s
        """
    add_par = '{"core_request_id":"' + CORE_REQUEST_ID + '"}'
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [add_par, application_id])
    cursor.execute(sql2, [add_par, application_id])


def delete_app(pgsql, application_id):
    sql = """
            DELETE 
            FROM bank_applications.registration_applications
            WHERE application_id=%s
        """
    sql2 = """
            DELETE 
            FROM bank_applications.applications
            WHERE application_id=%s
        """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id])
    cursor.execute(sql2, [application_id])


async def test_registration_set_core_request_id_ok(
        taxi_bank_applications, mockserver, pgsql,
):
    application_id = db_helpers.add_application_registration(
        pgsql, common.DEFAULT_YANDEX_UID, 'PROCESSING', '{}',
    )
    response = await taxi_bank_applications.post(
        'applications-internal/v1/registration/set_core_request_id',
        json={
            'application_id': application_id,
            'core_request_id': CORE_REQUEST_ID,
        },
    )

    assert response.status_code == 200
    records = get_add_params(pgsql, application_id)
    assert len(records) == 2
    assert records[0][0] == {'core_request_id': CORE_REQUEST_ID}
    assert records[1][0] == {'core_request_id': CORE_REQUEST_ID}


@pytest.mark.parametrize(
    'other_id, status_code', [('other_core', 500), (CORE_REQUEST_ID, 200)],
)
async def test_registration_set_core_request_id_race(
        taxi_bank_applications,
        mockserver,
        pgsql,
        testpoint,
        other_id,
        status_code,
):
    application_id = db_helpers.add_application_registration(
        pgsql, common.DEFAULT_YANDEX_UID, 'PROCESSING', '{}',
    )

    @testpoint('set_other_core_request_id')
    async def _set_other_core_request_id(data):
        update_add_params(pgsql, application_id)

    response = await taxi_bank_applications.post(
        'applications-internal/v1/registration/set_core_request_id',
        json={'application_id': application_id, 'core_request_id': other_id},
    )
    assert response.status_code == status_code
    records = get_add_params(pgsql, application_id)
    assert len(records) == 2
    assert records[0][0] == {'core_request_id': CORE_REQUEST_ID}
    assert records[1][0] == {'core_request_id': CORE_REQUEST_ID}


async def test_registration_set_core_request_id_race_application_deleted(
        taxi_bank_applications, mockserver, pgsql, testpoint,
):
    application_id = db_helpers.add_application_registration(
        pgsql, common.DEFAULT_YANDEX_UID, 'PROCESSING', '{}',
    )

    @testpoint('set_other_core_request_id')
    async def _set_other_core_request_id(data):
        delete_app(pgsql, application_id)

    response = await taxi_bank_applications.post(
        'applications-internal/v1/registration/set_core_request_id',
        json={
            'application_id': application_id,
            'core_request_id': CORE_REQUEST_ID,
        },
    )
    assert response.status_code == 500
    records = get_add_params(pgsql, application_id)
    assert not records


@pytest.mark.parametrize('status', ['SUCCESS', 'FAILED'])
async def test_registration_set_core_request_id_failed(
        taxi_bank_applications, mockserver, pgsql, status,
):
    application_id = db_helpers.add_application_registration(
        pgsql, common.DEFAULT_YANDEX_UID, status, '{}',
    )
    response = await taxi_bank_applications.post(
        'applications-internal/v1/registration/set_core_request_id',
        json={
            'application_id': application_id,
            'core_request_id': CORE_REQUEST_ID,
        },
    )

    assert response.status_code == 400
    records = get_add_params(pgsql, application_id)
    assert len(records) == 2
    assert records[0][0] == {}
    assert records[1][0] == {}


async def test_registration_set_core_request_id_happy_with_created_status(
        taxi_bank_applications, mockserver, pgsql,
):
    status = 'CREATED'
    application_id = db_helpers.add_application_registration(
        pgsql, common.DEFAULT_YANDEX_UID, status, '{}',
    )
    response = await taxi_bank_applications.post(
        'applications-internal/v1/registration/set_core_request_id',
        json={
            'application_id': application_id,
            'core_request_id': CORE_REQUEST_ID,
        },
    )

    assert response.status_code == 200
    records = get_add_params(pgsql, application_id)
    assert len(records) == 2
    assert records[0][0] == {'core_request_id': 'some_javist_id'}
    assert records[1][0] == {'core_request_id': 'some_javist_id'}

    records = get_status(pgsql, application_id)
    assert len(records) == 2
    assert records[0][0] == 'PROCESSING'
    assert records[1][0] == 'PROCESSING'


async def test_registration_set_core_request_id_set_other(
        taxi_bank_applications, mockserver, pgsql,
):
    application_id = db_helpers.add_application_registration(
        pgsql,
        common.DEFAULT_YANDEX_UID,
        'PROCESSING',
        '{"core_request_id":"' + CORE_REQUEST_ID + '"}',
    )
    response = await taxi_bank_applications.post(
        'applications-internal/v1/registration/set_core_request_id',
        json={
            'application_id': application_id,
            'core_request_id': 'other_request_id',
        },
    )
    assert response.status_code == 409
    records = get_add_params(pgsql, application_id)
    assert len(records) == 2
    assert records[0][0] == {'core_request_id': CORE_REQUEST_ID}
    assert records[1][0] == {'core_request_id': CORE_REQUEST_ID}


async def test_registration_set_core_request_id_not_found(
        taxi_bank_applications, mockserver,
):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/registration/set_core_request_id',
        json={
            'application_id': 'fb27372f-af3d-41ac-8930-7fa69333b387',
            'core_request_id': CORE_REQUEST_ID,
        },
    )

    assert response.status_code == 404
