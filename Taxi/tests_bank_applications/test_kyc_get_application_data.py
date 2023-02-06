import json

import pytest

from tests_bank_applications import common
from tests_bank_applications import kyc_db_helpers


LAST_NAME = 'иванов'
MIDDLE_NAME = 'иванович'
FIRST_NAME = 'иван'
PASSPORT_NUMBER = '1212654321'
BIRTHDAY = '2000-01-01'
SNILS = '08976857866'
INN = '123456789012'


@pytest.mark.experiments3(filename='bank_kyc_feature_experiments.json')
@pytest.mark.parametrize(
    'error_type, request_app_id, response_code',
    [
        ('none', 'later', 200),
        ('app_id_format', 'invalid', 400),
        ('404', '89389e2d-3291-4bc0-baa0-27aa91908650', 404),
    ],
)
async def test_kyc_get_application_data(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        pgsql,
        error_type,
        request_app_id,
        response_code,
):
    result_form = common.get_kyc_standard_form()
    form = json.dumps(result_form)
    application_id = kyc_db_helpers.insert_kyc_application(
        pgsql, submitted_form=form, agreement_version=2,
    )

    if error_type == 'none':
        request_app_id = application_id

    response = await taxi_bank_applications.post(
        '/applications-internal/v1/kyc/get_application_data',
        headers=common.default_headers(),
        json={'application_id': request_app_id},
    )
    assert response.status_code == response_code
    if error_type == 'none':
        assert response.json()['form'] == result_form
        assert response.json()['agreement_version'] == 2
