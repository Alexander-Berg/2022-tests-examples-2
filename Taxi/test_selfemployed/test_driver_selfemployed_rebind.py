import pytest

from testsuite.utils import http

from selfemployed.services import nalogru
from . import conftest


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings (phone_pd_id, inn_pd_id, status)
        VALUES ('PH1', 'INN1', 'COMPLETED');
        INSERT INTO se.finished_profiles
        (park_id, contractor_profile_id, phone_pd_id, inn_pd_id)
        VALUES ('1p', '1d', 'PH1', 'INN1');
        """,
    ],
)
@pytest.mark.parametrize(
    'park_id, driver_id, expected_response',
    [
        ['1p', '1d', {'success': True, 'text': 'Запрос отправлен'}],
        ['3p', '3d', {'success': False, 'text': 'Вы не СМЗ'}],
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_bind(
        se_client,
        se_web_context,
        mock_personal,
        patch,
        park_id,
        driver_id,
        expected_response,
):
    @mock_personal('/v1/tins/retrieve')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'id': 'INN1', 'primary_replica': False}
        return {'value': '01234567890', 'id': 'INN1'}

    @patch('selfemployed.services.nalogru.Service.bind_by_inn')
    async def _bind_by_inn(inn):
        assert inn == '01234567890'
        return 'request_id'

    response = await se_client.post(
        '/self-employment/fns-se/rebind',
        params={'park': park_id, 'driver': driver_id},
        json={},
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_response


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings (phone_pd_id, inn_pd_id, status)
        VALUES ('PH1', 'INN1', 'COMPLETED');
        INSERT INTO se.finished_profiles
        (park_id, contractor_profile_id, phone_pd_id, inn_pd_id)
        VALUES ('1p', '1d', 'PH1', 'INN1');
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_bind_unregistered(
        se_client, se_web_context, patch, mock_personal,
):
    @mock_personal('/v1/tins/retrieve')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'id': 'INN1', 'primary_replica': False}
        return {'value': '01234567890', 'id': 'INN1'}

    @patch('selfemployed.services.nalogru.Service.bind_by_inn')
    async def _bind_by_inn(inn):
        assert inn == '01234567890'
        raise nalogru.TaxpayerUnregistered()

    response = await se_client.post(
        '/self-employment/fns-se/rebind',
        params={'park': '1p', 'driver': '1d'},
        json={},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'success': False,
        'text': 'Встаньте на учет в Моем налоге',
    }
