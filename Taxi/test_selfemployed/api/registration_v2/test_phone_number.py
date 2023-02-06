import pytest

from testsuite.utils import http

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
async def test_phone_number(se_client, mock_personal):
    park_id = 'parkid'
    contractor_id = 'contractorid'

    @mock_personal('/v1/phones/retrieve')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': '+70123456789', 'id': 'PHONE_PD_ID'}

    response = await se_client.get(
        '/self-employment/fns-se/v2/phone-number',
        headers=conftest.DEFAULT_HEADERS,
        params={'driver': contractor_id, 'park': park_id},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'phone_number': '+70123456789',
        'sms_retry_timeout': 5000,
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
async def test_post_bind_known_phone(
        se_client, mock_personal, mock_driver_profiles, patch,
):
    park_id = 'parkid'
    contractor_id = 'contractorid'

    @mock_personal('/v1/phones/store')
    async def _phones_pd(request: http.Request):
        value: str = request.json['value']
        return {'value': value, 'id': 'PHONE_PD_ID_1'}

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _retrieve_profile(request: http.Request):
        assert request.json == {
            'id_in_set': ['parkid_contractorid'],
            'projection': ['data.phone_pd_ids'],
        }
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'parkid_contractorid',
                    'data': {'phone_pd_ids': [{'pd_id': 'PHONE_PD_ID_1'}]},
                },
            ],
        }

    @patch('selfemployed.services.nalogru.Service.bind_by_phone')
    async def _bind(phone_normalized):
        assert phone_normalized == '+70123456789'
        return 'request_id'

    response = await se_client.post(
        '/self-employment/fns-se/v2/bind',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={'step': 'phone_number', 'phone_number': '+70123456789'},
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
        VALUES ('parkid', 'contractorid', 'PHONE_PD_ID');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id)
         VALUES ('PHONE_PD_ID', 'INITIAL', 'external_id');
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_post_bind_unknown_phone(
        se_client, mock_personal, mock_driver_profiles, mockserver,
):
    park_id = 'parkid'
    contractor_id = 'contractorid'

    @mock_personal('/v1/phones/store')
    async def _phones_pd(request: http.Request):
        value: str = request.json['value']
        return {'value': value, 'id': 'PHONE_PD_ID_1'}

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _retrieve_profile(request: http.Request):
        assert request.json == {
            'id_in_set': ['parkid_contractorid'],
            'projection': ['data.phone_pd_ids'],
        }
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'parkid_contractorid',
                    'data': {'phone_pd_ids': [{'pd_id': 'PHONE_PD_ID'}]},
                },
            ],
        }

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    async def _submit(request: http.Request):
        assert request.form == {
            'number': '+70123456789',
            'display_language': 'ru',
            'route': 'taxi',
        }
        assert request.headers['Ya-Client-User-Agent'] == 'Taximeter 9.30'
        return {
            'deny_resend_until': 1618326242,
            'status': 'ok',
            'code_length': 6,
            'global_sms_id': '2070000508845559',
            'number': {
                'masked_e164': '+7012*****89',
                'e164': '+70123456789',
                'international': '+7 012 345-67-89',
                'masked_original': '+7012*****89',
                'original': '+70123456789',
                'masked_international': '+7 012 ***-**-89',
            },
            'track_id': 'sms_track_id',
        }

    response = await se_client.post(
        '/self-employment/fns-se/v2/bind',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={'step': 'phone_number', 'phone_number': '+70123456789'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'next_step': 'sms', 'step_count': 7, 'step_index': 2}


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
async def test_incorrect_transition(
        se_client, mock_personal, mock_driver_profiles, patch,
):
    park_id = 'parkid'
    contractor_id = 'contractorid'

    @mock_personal('/v1/phones/store')
    async def _phones_pd(request: http.Request):
        value: str = request.json['value']
        return {'value': value, 'id': 'PHONE_PD_ID_1'}

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _retrieve_profile(request: http.Request):
        assert request.json == {
            'id_in_set': ['parkid_contractorid'],
            'projection': ['data.phone_pd_ids'],
        }
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'parkid_contractorid',
                    'data': {'phone_pd_ids': [{'pd_id': 'PHONE_PD_ID_1'}]},
                },
            ],
        }

    @patch('selfemployed.services.nalogru.Service.bind_by_phone')
    async def _bind(phone_normalized):
        assert phone_normalized == '+70123456789'
        return 'request_id'

    response = await se_client.post(
        '/self-employment/fns-se/v2/bind',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={'step': 'phone_number', 'phone_number': '+70123456789'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': 'requisites',
        'step_count': 7,
        'step_index': 6,
    }
