import pytest

from tests_bank_applications import common


APPLICATION_ID = 'bb2b8cc1-3bfe-45be-b952-200238d96eff'


def default_json(application_id=APPLICATION_ID, status='PROCESSING'):
    return {'application_id': application_id, 'status': status}


@pytest.mark.parametrize('field', ['application_id', 'status'])
async def test_kyc_no_required_field(taxi_bank_applications, pgsql, field):
    req_json = default_json()
    req_json.pop(field)
    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/set_application_status',
        headers=common.default_headers(),
        json=req_json,
    )

    assert response.status_code == 400


@pytest.mark.parametrize('application_id', ['', '1111', 'abc'])
async def test_kyc_invalid_appplication_id(
        taxi_bank_applications, application_id,
):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/set_application_status',
        headers=common.default_headers(),
        json=default_json(application_id),
    )

    assert response.status_code == 400


async def test_kyc_application_id_not_found(taxi_bank_applications, pgsql):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/set_application_status',
        headers=common.default_headers(),
        json=default_json(),
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'NotFound',
        'message': 'Application not found',
    }


@pytest.mark.parametrize(
    'status', ['', '1111', 'abc', 'CREATED', 'DRAFT_SAVED'],
)
async def test_kyc_invalid_status(taxi_bank_applications, pgsql, status):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/set_application_status',
        headers=common.default_headers(),
        json=default_json(status=status),
    )

    assert response.status_code == 400


@pytest.mark.experiments3(filename='bank_kyc_feature_experiments.json')
@pytest.mark.parametrize(
    'status',
    ['PROCESSING', 'AGREEMENTS_ACCEPTED', 'CORE_BANKING', 'SUCCESS', 'FAILED'],
)
async def test_kyc_ok(
        taxi_bank_applications,
        bank_agreements_mock,
        taxi_processing_mock,
        status,
):
    create_app_resp = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/create_application',
        json={'buid': common.DEFAULT_YANDEX_BUID},
        headers=common.default_headers(),
    )
    application_id = create_app_resp.json().get('application_id')

    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/set_application_status',
        headers=common.default_headers(),
        json=default_json(application_id, status),
    )

    assert response.status_code == 200
