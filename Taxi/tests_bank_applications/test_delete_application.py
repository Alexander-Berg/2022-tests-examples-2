import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers


@pytest.mark.parametrize('status', ['CREATED', 'SUCCESS', 'FAILED'])
async def test_delete_application_ok(
        taxi_bank_applications, mockserver, pgsql, status,
):
    application_id = db_helpers.add_application_registration(
        pgsql, common.DEFAULT_YANDEX_UID, status,
    )
    response = await taxi_bank_applications.post(
        'applications-internal/v1/delete_application',
        json={'application_id': application_id},
    )

    assert response.status_code == 200
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'SELECT * FROM bank_applications.applications '
        f'WHERE application_id=\'{application_id}\'',
    )
    records = cursor.fetchall()
    assert not records
    records = db_helpers.get_apps_by_id_in_history_reg(pgsql, application_id)
    assert len(records) == 1
    assert records[0][1] == common.DEFAULT_YANDEX_UID
    assert records[0][4] == status
    assert records[0][5] == 'DELETE'
    assert records[0][6] is not None  # operation_at


async def test_delete_processing_application(
        taxi_bank_applications, mockserver, pgsql,
):
    application_id = db_helpers.add_application_registration(
        pgsql, common.DEFAULT_YANDEX_UID, 'PROCESSING',
    )
    response = await taxi_bank_applications.post(
        'applications-internal/v1/delete_application',
        json={'application_id': application_id},
    )

    assert response.status_code == 400
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'SELECT * FROM bank_applications.applications '
        f'WHERE application_id=\'{application_id}\'',
    )
    records = cursor.fetchall()
    assert len(records) == 1


async def test_delete_application_not_found(
        taxi_bank_applications, mockserver,
):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/delete_application',
        json={'application_id': 'fb27372f-af3d-41ac-8930-7fa69333b387'},
    )

    assert response.status_code == 404
