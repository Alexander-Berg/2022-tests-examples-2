import pytest

from testsuite.utils import http

from test_selfemployed import conftest


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.parametrize(
    'park_id,contractor_id,expected_response_status,expected_response',
    [
        (
            'park_id',
            'contractor_id',
            200,
            conftest.PRO_FNS_SELFEMPLOYMENT_HELP_INFO_SETTINGS_NOT_SELFREG_DST,
        ),
        (
            'selfreg',
            'selfreg_id',
            200,
            conftest.PRO_FNS_SELFEMPLOYMENT_HELP_INFO_SETTINGS_SELFREG_DST,
        ),
    ],
)
@conftest.help_info_configs3
async def test_get_help_v2(
        se_client,
        mock_fleet_parks,
        mock_selfreg,
        park_id,
        contractor_id,
        expected_response_status,
        expected_response,
):
    @mock_fleet_parks('/v1/parks')
    async def _get_parks(request: http.Request):
        assert request.query['park_id'] == park_id
        return {
            'id': park_id,
            'city_id': 'Москва',
            'country_id': 'rus',
            'demo_mode': True,
            'is_active': True,
            'is_billing_enabled': True,
            'is_franchising_enabled': True,
            'locale': 'ru',
            'login': 'login',
            'name': 'name',
            'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
        }

    @mock_selfreg('/internal/selfreg/v2/profile')
    async def _get_selfreg_profile(request: http.Request):
        assert request.query == {'selfreg_id': contractor_id}
        return {
            'locale': 'ru',
            'reported_to_zendesk': True,
            'token': 'token',
            'city': 'Москва',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'license_issue_date': '2015-09-01 00:00:00',
            'license_expire_date': '0001-01-01 00:00:00',
            'license_pd_id': 'DL_PD_ID',
            'middle_name': 'Отчество',
            'rent_option': 'rent',
            'selfreg_version': 'v2',
            'passport_uid': 'passport_uid',
        }

    response = await se_client.get(
        '/self-employment/fns-se/v2/help',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
    )
    assert response.status == expected_response_status
    content = await response.json()
    assert content == expected_response


async def test_get_help_v2_unauthorized(se_client):
    response = await se_client.get(
        '/self-employment/fns-se/v2/help',
        headers=conftest.DEFAULT_HEADERS,
        params={
            'park': 'park_id',
            'driver': 'contractor_id',
            'selfreg_id': 'selfreg_id',
        },
    )
    assert response.status == 401
