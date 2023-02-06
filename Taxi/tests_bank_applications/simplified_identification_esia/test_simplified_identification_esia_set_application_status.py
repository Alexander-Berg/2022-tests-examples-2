import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers


APPLICATION_ID = 'bb2b8cc1-3bfe-45be-b952-200238d96eff'


def default_json(
        application_id=APPLICATION_ID,
        status='PROCESSING',
        yandex_buid=common.DEFAULT_YANDEX_BUID,
):
    return {
        'application_id': application_id,
        'status': status,
        'yandex_buid': yandex_buid,
    }


@pytest.mark.parametrize('field', ['application_id', 'status', 'yandex_buid'])
async def test_no_required_field(taxi_bank_applications, pgsql, field):
    req_json = default_json()
    req_json.pop(field)
    response = await taxi_bank_applications.post(
        'applications-internal/v1/simplified_identification/esia/set_application_status',  # noqa
        headers=common.default_headers(),
        json=req_json,
    )

    assert response.status_code == 400


@pytest.mark.parametrize('application_id', ['', '1111', 'abc'])
async def test_invalid_appplication_id(
        taxi_bank_applications, pgsql, application_id,
):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/simplified_identification/esia/set_application_status',  # noqa
        headers=common.default_headers(),
        json=default_json(application_id),
    )

    assert response.status_code == 400


@pytest.mark.parametrize('buid', ['', '1111', 'abc'])
async def test_invalid_yandex_buid(taxi_bank_applications, pgsql, buid):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/simplified_identification/esia/set_application_status',  # noqa
        headers=common.default_headers(),
        json=default_json(yandex_buid=buid),
    )

    assert response.status_code == (400 if not buid else 404)


async def test_appplication_id_not_found(taxi_bank_applications, pgsql):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/simplified_identification/esia/set_application_status',  # noqa
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
        'applications-internal/v1/simplified_identification/esia/set_application_status',  # noqa
        headers=common.default_headers(),
        json=default_json(status=status),
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    'status', ['PROCESSING', 'CORE_BANKING', 'SUCCESS', 'FAILED'],
)
async def test_ok(taxi_bank_applications, pgsql, status):
    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=common.STATUS_CREATED,
        simpl_esia_status=common.STATUS_CREATED,
    )

    response = await taxi_bank_applications.post(
        'applications-internal/v1/simplified_identification/esia/set_application_status',  # noqa
        headers=common.default_headers(),
        json=default_json(application_id, status),
    )

    assert response.status_code == 200

    application = db_helpers.select_simpl_esia_app(pgsql, application_id)
    assert application.status == status

    application_history = db_helpers.select_simpl_esia_apps_hist(
        pgsql, application_id,
    )
    assert len(application_history) == 1


async def test_reason_in_db(
        taxi_bank_applications, taxi_processing_mock, pgsql,
):
    application_id = db_helpers.insert_simpl_esia_application(pgsql)

    body = default_json(application_id, 'FAILED')
    body['errors'] = ['code:1', 'code:2']
    response = await taxi_bank_applications.post(
        'applications-internal/v1/simplified_identification/esia/set_application_status',  # noqa
        headers=common.default_headers(),
        json=body,
    )

    assert response.status_code == 200

    application = db_helpers.select_simpl_esia_app(pgsql, application_id)
    assert application.status == common.STATUS_FAILED
    assert application.reason == 'code:1;code:2;'

    application_history = db_helpers.select_simpl_esia_apps_hist(
        pgsql, application_id,
    )
    assert len(application_history) == 1
