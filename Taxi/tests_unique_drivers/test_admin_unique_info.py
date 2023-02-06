import pytest

from tests_unique_drivers import utils


@pytest.mark.parametrize('is_id_scenario', [False, True])
@pytest.mark.parametrize(
    'requested_license, expected_code, expected_response',
    [
        ('LICENSE_001', 200, 'response_info.json'),
        ('LICENSE_000', 404, 'response_not_found.json'),
    ],
)
@pytest.mark.config(
    UNIQUE_DRIVERS_QC_MEDIA_SETTINGS={
        'is_enabled': True,
        'media': [
            {'exam': 'biometry', 'code': 'selfie'},
            {'exam': 'dkvu', 'code': 'selfie'},
        ],
    },
)
@pytest.mark.now('2021-03-01T00:00:00')
async def test_admin_unique_info(
        taxi_unique_drivers,
        load_json,
        is_id_scenario,
        requested_license,
        expected_code,
        expected_response,
):
    license_type = 'license'
    license_value = requested_license
    if is_id_scenario:
        license_type += '_pd_id'
        license_value += '_ID'

    response = await taxi_unique_drivers.post(
        '/admin/unique-drivers/v1/unique/info',
        headers={'X-Yandex-Login': 'user'},
        params={'consumer': 'admin'},
        json={license_type: license_value},
    )
    assert response.status_code == expected_code
    result = response.json()

    assert utils.ordered(result) == utils.ordered(
        load_json('responses/' + expected_response),
    )
