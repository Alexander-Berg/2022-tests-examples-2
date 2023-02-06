import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers


APPLICATION_ID = 'bb2b8cc1-3bfe-45be-b952-200238d96eff'


def default_json(application_id=APPLICATION_ID, status='PROCESSING'):
    return {'application_id': application_id, 'status': status}


@pytest.mark.parametrize('field', ['application_id', 'status'])
async def test_no_required_field(taxi_bank_applications, pgsql, field):
    req_json = default_json()
    req_json.pop(field)
    response = await taxi_bank_applications.post(
        'applications-internal/v1/simplified_identification/set_application_status',  # noqa
        headers=common.default_headers(),
        json=req_json,
    )

    assert response.status_code == 400


@pytest.mark.parametrize('application_id', ['', '1111', 'abc'])
async def test_invalid_appplication_id(
        taxi_bank_applications, pgsql, application_id,
):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/simplified_identification/set_application_status',  # noqa
        headers=common.default_headers(),
        json=default_json(application_id),
    )

    assert response.status_code == 400


async def test_appplication_id_not_found(taxi_bank_applications, pgsql):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/simplified_identification/set_application_status',  # noqa
        headers=common.default_headers(),
        json=default_json(),
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'NotFound',
        'message': 'Application not found',
    }


@pytest.mark.parametrize(
    'status', ['', '1111', 'abc', 'CREATED', 'DRAFT_SAVED', 'SUBMITTED'],
)
async def test_invalid_status(taxi_bank_applications, pgsql, status):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/simplified_identification/set_application_status',  # noqa
        headers=common.default_headers(),
        json=default_json(status=status),
    )

    assert response.status_code == 400


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
@pytest.mark.parametrize(
    'status',
    ['PROCESSING', 'AGREEMENTS_ACCEPTED', 'CORE_BANKING', 'SUCCESS', 'FAILED'],
)
async def test_ok(
        taxi_bank_applications,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        pgsql,
        status,
):
    create_app_resp = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/create_application',
        headers=common.default_headers(),
    )
    application_id = create_app_resp.json().get('application_id')

    response = await taxi_bank_applications.post(
        'applications-internal/v1/simplified_identification/set_application_status',  # noqa
        headers=common.default_headers(),
        json=default_json(application_id, status),
    )

    assert response.status_code == 200


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
async def test_reason_in_db(
        taxi_bank_applications,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        pgsql,
):
    create_app_resp = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/create_application',
        headers=common.default_headers(),
    )
    application_id = create_app_resp.json().get('application_id')

    body = default_json(application_id, 'FAILED')
    body['errors'] = ['code:1', 'code:2']
    response = await taxi_bank_applications.post(
        'applications-internal/v1/simplified_identification'
        '/set_application_status',
        headers=common.default_headers(),
        json=body,
    )

    assert response.status_code == 200

    application = db_helpers.get_simpl_id_app(pgsql, application_id)
    assert application.reason == 'code:1;code:2;'
