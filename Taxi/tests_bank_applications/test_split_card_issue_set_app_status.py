import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers


APPLICATION_ID = 'bb2b8cc1-3bfe-45be-b952-200238d96eff'


def default_json(application_id=APPLICATION_ID, status='PROCESSING'):
    return {'application_id': application_id, 'status': status}


def add_application(pgsql, common_status='CREATED', status='CREATED'):
    application_id = db_helpers.add_application(
        pgsql,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        'SPLIT_CARD_ISSUE',
        common_status,
        multiple_success_status_allowed=False,
    )
    db_helpers.add_split_card_issue_app(pgsql, application_id, status)
    return application_id


@pytest.mark.parametrize('field', ['application_id', 'status'])
async def test_no_required_field(taxi_bank_applications, pgsql, field):
    req_json = default_json()
    req_json.pop(field)
    response = await taxi_bank_applications.post(
        'applications-internal/v1/split_card_issue/set_application_status',
        headers=common.default_headers(),
        json=req_json,
    )

    assert response.status_code == 400


@pytest.mark.parametrize('application_id', ['', '1111', 'abc'])
async def test_invalid_appplication_id(
        taxi_bank_applications, pgsql, application_id,
):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/split_card_issue/set_application_status',
        headers=common.default_headers(),
        json=default_json(application_id),
    )

    assert response.status_code == 400


async def test_appplication_id_not_found(taxi_bank_applications, pgsql):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/split_card_issue/set_application_status',
        headers=common.default_headers(),
        json=default_json(),
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'NotFound',
        'message': 'Application not found',
    }


@pytest.mark.parametrize('status', ['', '1111', 'abc', 'CREATED', 'SUBMITTED'])
async def test_invalid_status(taxi_bank_applications, pgsql, status):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/split_card_issue/set_application_status',
        headers=common.default_headers(),
        json=default_json(status=status),
    )

    assert response.status_code == 400


@pytest.mark.parametrize('status', ['PROCESSING', 'SUCCESS', 'FAILED'])
async def test_ok(taxi_bank_applications, pgsql, status):
    application_id = add_application(pgsql)

    response = await taxi_bank_applications.post(
        'applications-internal/v1/split_card_issue/set_application_status',
        headers=common.default_headers(),
        json=default_json(application_id, status),
    )

    assert response.status_code == 200
