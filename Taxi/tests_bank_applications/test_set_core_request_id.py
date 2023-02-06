import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers

CORE_REQUEST_ID = 'some_javist_id'


async def test_set_core_request_id_ok(
        taxi_bank_applications, mockserver, pgsql,
):
    application_id = db_helpers.add_application(
        pgsql,
        'UID',
        common.DEFAULT_YANDEX_UID,
        'REGISTRATION',
        'PROCESSING',
        False,
        '{}',
    )
    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_core_request_id',
        json={
            'application_id': application_id,
            'core_request_id': CORE_REQUEST_ID,
        },
    )

    assert response.status_code == 200
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'SELECT additional_params FROM bank_applications.applications '
        f'WHERE application_id=\'{application_id}\'',
    )
    records = cursor.fetchall()
    assert len(records) == 1
    assert records[0][0] == {'core_request_id': CORE_REQUEST_ID}


@pytest.mark.parametrize(
    'other_id, status_code', [('other_core', 500), (CORE_REQUEST_ID, 200)],
)
async def test_set_core_request_id_race(
        taxi_bank_applications,
        mockserver,
        pgsql,
        testpoint,
        other_id,
        status_code,
):
    application_id = db_helpers.add_application(
        pgsql,
        'UID',
        common.DEFAULT_YANDEX_UID,
        'REGISTRATION',
        'PROCESSING',
        False,
        '{}',
    )

    @testpoint('set_other_core_request_id')
    async def _set_other_core_request_id(data):
        cursor_inner = pgsql['bank_applications'].cursor()
        cursor_inner.execute(
            'UPDATE bank_applications.applications '
            'SET additional_params=\'{"core_request_id":"'
            + CORE_REQUEST_ID
            + '"}\' '
            f'WHERE application_id=\'{application_id}\'',
        )

    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_core_request_id',
        json={'application_id': application_id, 'core_request_id': other_id},
    )
    assert response.status_code == status_code
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'SELECT additional_params FROM bank_applications.applications '
        f'WHERE application_id=\'{application_id}\'',
    )
    records = cursor.fetchall()
    assert len(records) == 1
    assert records[0][0] == {'core_request_id': CORE_REQUEST_ID}


async def test_set_core_request_id_race_application_deleted(
        taxi_bank_applications, mockserver, pgsql, testpoint,
):
    application_id = db_helpers.add_application(
        pgsql,
        'UID',
        common.DEFAULT_YANDEX_UID,
        'REGISTRATION',
        'PROCESSING',
        False,
        '{}',
    )

    @testpoint('set_other_core_request_id')
    async def _set_other_core_request_id(data):
        cursor_inner = pgsql['bank_applications'].cursor()
        cursor_inner.execute(
            'DELETE FROM bank_applications.applications '
            f'WHERE application_id=\'{application_id}\'',
        )

    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_core_request_id',
        json={
            'application_id': application_id,
            'core_request_id': CORE_REQUEST_ID,
        },
    )
    assert response.status_code == 500
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'SELECT additional_params FROM bank_applications.applications '
        f'WHERE application_id=\'{application_id}\'',
    )
    records = cursor.fetchall()
    assert not records


@pytest.mark.parametrize('status', ['CREATED', 'SUCCESS', 'FAILED'])
async def test_set_core_request_id_failed(
        taxi_bank_applications, mockserver, pgsql, status,
):
    application_id = db_helpers.add_application(
        pgsql,
        'UID',
        common.DEFAULT_YANDEX_UID,
        'REGISTRATION',
        status,
        False,
        '{}',
    )
    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_core_request_id',
        json={
            'application_id': application_id,
            'core_request_id': CORE_REQUEST_ID,
        },
    )

    assert response.status_code == 400
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'SELECT additional_params FROM bank_applications.applications '
        f'WHERE application_id=\'{application_id}\'',
    )
    records = cursor.fetchall()
    assert len(records) == 1
    assert records[0][0] == {}


async def test_set_core_request_id_set_other(
        taxi_bank_applications, mockserver, pgsql,
):
    application_id = db_helpers.add_application(
        pgsql,
        'UID',
        common.DEFAULT_YANDEX_UID,
        'REGISTRATION',
        'PROCESSING',
        False,
        '{"core_request_id":"' + CORE_REQUEST_ID + '"}',
    )
    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_core_request_id',
        json={
            'application_id': application_id,
            'core_request_id': 'other_request_id',
        },
    )
    assert response.status_code == 409
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'SELECT additional_params FROM bank_applications.applications '
        f'WHERE application_id=\'{application_id}\'',
    )
    records = cursor.fetchall()
    assert len(records) == 1
    assert records[0][0] == {'core_request_id': CORE_REQUEST_ID}


async def test_set_core_request_id_not_found(
        taxi_bank_applications, mockserver,
):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_core_request_id',
        json={
            'application_id': 'fb27372f-af3d-41ac-8930-7fa69333b387',
            'core_request_id': CORE_REQUEST_ID,
        },
    )

    assert response.status_code == 404
