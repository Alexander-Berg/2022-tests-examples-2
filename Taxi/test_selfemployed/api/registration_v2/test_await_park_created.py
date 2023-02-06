import pytest

from testsuite.utils import http

from test_selfemployed import conftest


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.parametrize(
    'park_id,contractor_id,account_type,salesforce_account_id,'
    'expected_response_status,expected_response',
    [
        (
            'park_id',
            'contractor_id',
            'Selfemployed',
            'salesforce_account_id',
            200,
            conftest.PRO_FNS_SELFEMPLOYMENT_AWAIT_PARK_CREATED_SETTINGS_RESIDENT_DST,  # noqa: E501
        ),
        (
            'park_id',
            'contractor_id',
            'Non-Resident Selfemployed',
            'salesforce_account_id',
            200,
            conftest.PRO_FNS_SELFEMPLOYMENT_AWAIT_PARK_CREATED_SETTINGS_NOT_RESIDENT_DST,  # noqa: E501
        ),
    ],
)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES
            ('park_id', 'contractor_id', 'PHONE_PD_ID');
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
@conftest.await_park_created_configs3
async def test_get_await_park_created(
        se_client,
        mock_salesforce,
        park_id,
        contractor_id,
        account_type,
        salesforce_account_id,
        expected_response_status,
        expected_response,
):
    @mock_salesforce(
        f'/services/data/v46.0/sobjects/Account/{salesforce_account_id}',
    )
    def _auth_sf(request: http.Request):
        return {
            'City__c': 'Москва',
            'Type': f'{account_type}',
            'IBAN__c': '123456',
            'SWIFT__c': '123456',
        }

    response = await se_client.get(
        '/self-employment/fns-se/v2/await-park-created',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
    )
    assert response.status == expected_response_status
    content = await response.json()
    assert content == expected_response


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES
            ('park_id', 'contractor_id', 'PHONE_PD_ID');
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
             NULL, NULL,
             'park_id', 'contractor_id');
        """,
    ],
)
async def test_get_await_park_created_err(se_client):
    park_id = 'park_id'
    contractor_id = 'contractor_id'

    response = await se_client.get(
        '/self-employment/fns-se/v2/await-park-created',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
    )
    assert response.status == 400
    content = await response.json()
    assert content['code'] == 'PARK_CREATION_NOT_STARTED'
    assert content['text'] == 'Создание парка не начиналось'


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES
            ('park_id', 'contractor_id', 'PHONE_PD_ID');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id,
             address, apartment_number,
             postal_code, agreements,
             inn_pd_id, residency_state,
             created_park_id,
             salesforce_account_id, salesforce_requisites_case_id,
             initial_park_id, initial_contractor_id)
         VALUES
            ('PHONE_PD_ID', 'FINISHED', 'external_id',
             'address', '123',
             '1234567', '{"general": true, "gas_stations": false}',
             'inn_pd_id', 'RESIDENT',
             'created_park_id',
             NULL, NULL,
             'park_id', 'contractor_id');
        """,
    ],
)
async def test_post_await_park_created(se_client):
    park_id = 'park_id'
    contractor_id = 'contractor_id'

    response = await se_client.post(
        '/self-employment/fns-se/v2/await-park-created',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': 'requisites',
        'step_count': 7,
        'step_index': 6,
    }


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES
            ('park_id', 'contractor_id', 'PHONE_PD_ID');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id,
             address, apartment_number,
             postal_code, agreements,
             inn_pd_id, residency_state,
             created_park_id,
             salesforce_account_id, salesforce_requisites_case_id,
             initial_park_id, initial_contractor_id)
         VALUES
            ('PHONE_PD_ID', 'FINISHED', 'external_id',
             'address', '123',
             '1234567', '{"general": true, "gas_stations": false}',
             'inn_pd_id', 'RESIDENT',
             NULL,
             NULL, NULL,
             'park_id', 'contractor_id');
        """,
    ],
)
async def test_post_await_park_created_err(se_client):
    park_id = 'park_id'
    contractor_id = 'contractor_id'

    response = await se_client.post(
        '/self-employment/fns-se/v2/await-park-created',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
    )
    assert response.status == 400
    content = await response.json()
    assert content['code'] == 'PARK_CREATION_NOT_FINISHED'
    assert (
        content['text']
        == 'Создание парка ещё не закончено. Пожалуйста, подождите'
    )
