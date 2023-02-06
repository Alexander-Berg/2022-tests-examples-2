import pytest

from testsuite.utils import http

from selfemployed.services import nalogru
from test_selfemployed import conftest


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES ('parkid', 'contractorid', 'PHONE_PD_ID');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id)
         VALUES ('PHONE_PD_ID', 'INITIAL', 'external_id');
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_post_nalog_app(
        se_client, mock_personal, mock_driver_profiles, patch,
):
    park_id = 'parkid'
    contractor_id = 'contractorid'
    phone = '+70123456789'

    @mock_personal('/v1/phones/retrieve')
    async def _retrieve_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': phone, 'id': 'PHONE_PD_ID'}

    @patch('selfemployed.services.nalogru.Service.bind_by_phone')
    async def _bind(phone_normalized):
        assert phone_normalized == phone
        return 'request_id'

    response = await se_client.post(
        '/self-employment/fns-se/v2/nalog-app',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={'step': 'nalog_app'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': 'agreement',
        'step_count': 7,
        'step_index': 3,
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES
            ('parkid', 'contractorid', 'PHONE_PD_ID');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id,
             address, apartment_number,
             postal_code, agreements,
             inn_pd_id, residency_state,
             salesforce_account_id, salesforce_requisites_case_id,
             initial_park_id, initial_contractor_id)
         VALUES
            ('PHONE_PD_ID', 'FINISHED', 'external_id',
             'address', '123',
             '1234567', '{"general": true, "gas_stations": false}',
             'inn_pd_id', 'RESIDENT',
             'salesforce_account_id', NULL,
             'park_id', 'contractor_id');
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_incorrect_transition(
        se_client, mock_personal, mock_driver_profiles, patch,
):
    park_id = 'parkid'
    contractor_id = 'contractorid'
    phone = '+70123456789'

    @mock_personal('/v1/phones/retrieve')
    async def _retrieve_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': phone, 'id': 'PHONE_PD_ID'}

    @patch('selfemployed.services.nalogru.Service.bind_by_phone')
    async def _bind(phone_normalized):
        assert phone_normalized == phone
        return 'request_id'

    response = await se_client.post(
        '/self-employment/fns-se/v2/nalog-app',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={'step': 'nalog_app'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': 'requisites',
        'step_count': 7,
        'step_index': 6,
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES ('parkid', 'contractorid', 'PHONE_PD_ID');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id)
         VALUES ('PHONE_PD_ID', 'INITIAL', 'external_id');
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_post_nalog_app_unregisteged(
        se_client, mock_personal, mock_driver_profiles, patch,
):
    park_id = 'parkid'
    contractor_id = 'contractorid'
    phone = '+70123456789'

    @mock_personal('/v1/phones/retrieve')
    async def _retrieve_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': phone, 'id': 'PHONE_PD_ID'}

    @patch('selfemployed.services.nalogru.Service.bind_by_phone')
    async def _bind(phone_normalized):
        assert phone_normalized == phone
        raise nalogru.TaxpayerUnregistered()

    response = await se_client.post(
        '/self-employment/fns-se/v2/nalog-app',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={'step': 'nalog_app'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': 'phone_number',
        'step_count': 7,
        'step_index': 2,
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES ('selfreg', 'selfreg_id', 'PHONE_PD_ID');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id)
         VALUES ('PHONE_PD_ID', 'INITIAL', 'external_id');
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_post_nalog_app_selfreg_unregisteged(
        se_client, mock_personal, mock_driver_profiles, patch,
):
    @mock_personal('/v1/phones/retrieve')
    async def _retrieve_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': phone, 'id': 'PHONE_PD_ID'}

    @patch('selfemployed.services.nalogru.Service.bind_by_phone')
    async def _bind(phone_normalized):
        assert phone_normalized == phone
        raise nalogru.TaxpayerUnregistered()

    park_id = 'selfreg'
    contractor_id = 'selfreg_id'
    phone = '+70123456789'

    response = await se_client.post(
        '/self-employment/fns-se/v2/nalog-app',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={'step': 'nalog_app'},
    )

    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'TAXPAYER_UNREGISTERED',
        'text': 'Вы не являетесь самозанятым',
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES ('parkid', 'contractorid', 'PHONE_PD_ID');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id)
         VALUES ('PHONE_PD_ID', 'INITIAL', 'external_id');
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_post_nalog_app_unavailable(
        se_client, mock_personal, mock_driver_profiles, patch,
):
    park_id = 'parkid'
    contractor_id = 'contractorid'
    phone = '+70123456789'

    @mock_personal('/v1/phones/retrieve')
    async def _retrieve_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': phone, 'id': 'PHONE_PD_ID'}

    @patch('selfemployed.services.nalogru.Service.bind_by_phone')
    async def _bind(phone_normalized):
        assert phone_normalized == phone
        raise nalogru.FnsUnavailable()

    response = await se_client.post(
        '/self-employment/fns-se/v2/nalog-app',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={'step': 'nalog_app'},
    )

    assert response.status == 504
    content = await response.json()
    assert content == {
        'code': 'NALOGRU_UNAVALABLE',
        'text': 'Мой Налог временно недоступен',
    }
