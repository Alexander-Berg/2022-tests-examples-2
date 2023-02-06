from tests_bank_applications import common
from tests_bank_applications import db_helpers


HANDLE_URL = '/applications-internal/v1/get_application_data'


async def test_get_application_data_esia_app(
        taxi_bank_applications, mockserver, access_control_mock, pgsql,
):
    application_id = db_helpers.insert_simpl_esia_application(pgsql)

    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.default_headers(),
        json={'application_id': application_id},
    )
    assert response.status_code == 400
