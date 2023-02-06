import pytest

from tests_bank_applications import common
from tests_bank_applications.product import db_helpers

MOCK_NOW = '2021-09-28T19:31:00+00:00'
HANDLE_STATUS_URL = '/applications-internal/v1/product/set_application_status'
HANDLE_REQUEST_URL = '/applications-internal/v1/product/set_core_request_id'


@pytest.mark.parametrize(
    'old_status, errors',
    [(None, None), (common.STATUS_CREATED, ['code:error', '0:1'])],
)
async def test_status_ok(taxi_bank_applications, pgsql, old_status, errors):
    application_id = db_helpers.insert_application(pgsql)
    headers = common.default_headers()
    response = await taxi_bank_applications.post(
        HANDLE_STATUS_URL,
        headers=headers,
        json={
            'application_id': application_id,
            'status': common.STATUS_PROCESSING,
            'old_status': old_status,
            'errors': errors,
        },
    )
    assert response.status_code == 200

    application = db_helpers.select_application(pgsql, application_id)
    assert application.status == common.STATUS_PROCESSING
    error_string = ';'.join(errors) if errors is not None else None
    assert application.reason == error_string
    history = db_helpers.select_applications_history(pgsql, application_id)
    assert len(history) == 1
    assert application == history[0]


@pytest.mark.parametrize('old_status', [None, common.STATUS_CREATED])
async def test_status_race(
        taxi_bank_applications, pgsql, testpoint, old_status,
):
    application_id = db_helpers.insert_application(pgsql)

    @testpoint('set_other_status')
    def _update_same_application(data):
        db_helpers.update_status(
            pgsql, application_id, common.STATUS_SUBMITTED,
        )

    headers = common.default_headers()
    response = await taxi_bank_applications.post(
        HANDLE_STATUS_URL,
        headers=headers,
        json={
            'application_id': application_id,
            'status': common.STATUS_PROCESSING,
            'old_status': old_status,
        },
    )
    if old_status is None:
        assert response.status_code == 200
    else:
        assert response.status_code == 500


async def test_status_no_application(taxi_bank_applications):
    headers = common.default_headers()
    response = await taxi_bank_applications.post(
        HANDLE_STATUS_URL,
        headers=headers,
        json={
            'application_id': '46fc6e3d-3ea1-4139-afee-a07ec2827b5b',
            'status': common.STATUS_PROCESSING,
        },
    )
    assert response.status_code == 404


async def test_status_already_current(taxi_bank_applications, pgsql):
    application_id = db_helpers.insert_application(
        pgsql, status=common.STATUS_PROCESSING,
    )
    headers = common.default_headers()
    response = await taxi_bank_applications.post(
        HANDLE_STATUS_URL,
        headers=headers,
        json={
            'application_id': application_id,
            'status': common.STATUS_PROCESSING,
        },
    )
    assert response.status_code == 200
    assert not db_helpers.select_applications_history(pgsql, application_id)


async def test_core_request_ok(taxi_bank_applications, pgsql):
    application_id = db_helpers.insert_application(pgsql)
    headers = common.default_headers()
    response = await taxi_bank_applications.post(
        HANDLE_REQUEST_URL,
        headers=headers,
        json={
            'application_id': application_id,
            'core_request_id': common.CORE_REQUEST_ID,
        },
    )
    assert response.status_code == 200

    application = db_helpers.select_application(pgsql, application_id)
    assert application.status == common.STATUS_CORE_BANKING
    assert application.core_request_id == common.CORE_REQUEST_ID
    history = db_helpers.select_applications_history(pgsql, application_id)
    assert len(history) == 1
    assert application == history[0]


async def test_core_request_race(taxi_bank_applications, pgsql, testpoint):
    application_id = db_helpers.insert_application(pgsql)

    @testpoint('set_other_core_request_id')
    def _update_same_application(data):
        db_helpers.update_core_request_id(
            pgsql, application_id, common.CORE_REQUEST_ID + '1',
        )

    headers = common.default_headers()
    response = await taxi_bank_applications.post(
        HANDLE_REQUEST_URL,
        headers=headers,
        json={
            'application_id': application_id,
            'core_request_id': common.CORE_REQUEST_ID,
        },
    )
    assert response.status_code == 500


async def test_core_request_no_application(taxi_bank_applications):
    headers = common.default_headers()
    response = await taxi_bank_applications.post(
        HANDLE_REQUEST_URL,
        headers=headers,
        json={
            'application_id': '46fc6e3d-3ea1-4139-afee-a07ec2827b5b',
            'core_request_id': common.CORE_REQUEST_ID,
        },
    )
    assert response.status_code == 404


async def test_core_request_already_current(taxi_bank_applications, pgsql):
    application_id = db_helpers.insert_application(
        pgsql, core_request_id=common.CORE_REQUEST_ID,
    )
    headers = common.default_headers()
    response = await taxi_bank_applications.post(
        HANDLE_REQUEST_URL,
        headers=headers,
        json={
            'application_id': application_id,
            'core_request_id': common.CORE_REQUEST_ID,
        },
    )
    assert response.status_code == 200
    assert not db_helpers.select_applications_history(pgsql, application_id)
