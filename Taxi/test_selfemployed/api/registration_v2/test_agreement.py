import pytest

from testsuite.utils import http

from test_selfemployed import conftest


@pytest.mark.parametrize(
    'request_body, selfreg_profile, driver_profile, expected_response',
    [
        # selfreg, courier
        (
            {'selfreg_id': 'selfregid'},
            {'license_pd_id': None},
            None,
            conftest.AGREEMENT_DEFAULT_RESPONSE,
        ),
        # selfreg, driver
        (
            {'selfreg_id': 'selfregid'},
            {'license_pd_id': 'license_id_driver'},
            None,
            conftest.AGREEMENT_WITH_DRIVER_LICENSE_RESPONSE,
        ),
        # from park, courier
        (
            {'park': 'parkid', 'driver': 'contractorid'},
            None,
            {'license': {'pd_id': 'license_id_courier'}},
            conftest.AGREEMENT_DEFAULT_RESPONSE,
        ),
        # from park, driver
        (
            {'park': 'parkid', 'driver': 'contractorid'},
            None,
            {'license': {'pd_id': 'license_id_driver'}},
            conftest.AGREEMENT_WITH_DRIVER_LICENSE_RESPONSE,
        ),
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@conftest.agreement_configs3
async def test_get_v2_agreement(
        se_client,
        mock_driver_profiles,
        mockserver,
        mock_personal,
        request_body,
        selfreg_profile,
        driver_profile,
        expected_response,
):
    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    def _driver_profiles_retrieve(request: http.Request):
        assert request.json['id_in_set'] == ['parkid_contractorid']
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'parkid_contractorid',
                    'data': driver_profile,
                },
            ],
        }

    @mockserver.json_handler('/selfreg-api/get_profile')
    def _selfreg_get_profile(request):
        assert request.method == 'POST'
        return selfreg_profile

    @mock_personal('/v1/driver_licenses/retrieve')
    def _license_retrieve(request):
        value = None
        if request.json['id'] == 'license_id_driver':
            value = '12345678'
        elif request.json['id'] == 'license_id_courier':
            value = 'COURIER38288'
        return {'id': request.json['id'], 'value': value}

    response = await se_client.get(
        '/self-employment/fns-se/v3/agreement',
        headers=conftest.DEFAULT_HEADERS,
        params=request_body,
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_response


@pytest.mark.config(GAS_STATIONS_OFFER_URL=conftest.GAS_STATIONS_OFFER_URL)
@pytest.mark.parametrize(
    'accepted_agreements,expected_response_code,'
    'expected_response,expected_agreements',
    [
        # not all required agreements accepted
        (
            [
                'agreement_taxi_offer_checkbox',
                'agreement_taxi_marketing_offer_checkbox',
            ],
            400,
            {
                'code': 'REQUIRED_AGREEMENTS_ERROR',
                'text': 'Требуемые соглашения не принимаются',
            },
            None,
        ),
        # all required accepted, no gas stations
        (
            [
                'agreement_taxi_offer_checkbox',
                'agreement_taxi_marketing_offer_checkbox',
                'agreement_confidential_checkbox',
                'some_not_existing_agreement',
            ],
            200,
            {'next_step': 'address', 'step_count': 7, 'step_index': 4},
            '{"general": true, "gas_stations": false}',
        ),
        # all accepted, including gas stations
        (
            [
                'agreement_taxi_offer_checkbox',
                'agreement_taxi_marketing_offer_checkbox',
                'agreement_confidential_checkbox',
                'agreement_taxi_transfer_to_third_party_checkbox',
                'agreement_taxi_gas_stations_checkbox',
            ],
            200,
            {'next_step': 'address', 'step_count': 7, 'step_index': 4},
            '{"general": true, "gas_stations": true}',
        ),
        # one out of two gas stations offers accepted
        (
            [
                'agreement_taxi_offer_checkbox',
                'agreement_taxi_marketing_offer_checkbox',
                'agreement_confidential_checkbox',
                'agreement_taxi_gas_stations_checkbox',
            ],
            200,
            {'next_step': 'address', 'step_count': 7, 'step_index': 4},
            '{"general": true, "gas_stations": false}',
        ),
    ],
)
@conftest.agreement_configs3
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES ('parkid', 'contractorid', 'PHONE_PD_ID');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id)
         VALUES ('PHONE_PD_ID', 'FILLING', 'external_id');
        """,
    ],
)
async def test_post_v2_agreement_some_agreements_accepted(
        se_client,
        se_web_context,
        mock_driver_profiles,
        mock_personal,
        accepted_agreements,
        expected_response_code,
        expected_response,
        expected_agreements,
):
    park_id = 'parkid'
    driver_id = 'contractorid'
    license_id = 'license_pd_id_1'
    license_value = '12345678'

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    def _driver_profiles_retrieve(request):
        assert request.json['id_in_set'] == [f'{park_id}_{driver_id}']
        return {
            'profiles': [
                {
                    'park_driver_profile_id': f'{park_id}_{driver_id}',
                    'data': {'license': {'pd_id': license_id}},
                },
            ],
        }

    @mock_personal('/v1/driver_licenses/retrieve')
    def _license_retrieve(request):
        assert request.json['id'] == license_id
        return {'id': license_id, 'value': license_value}

    request_json = {
        'step': 'agreement',
        'agreements': [
            {'id': x, 'state': 'accepted'} for x in accepted_agreements
        ],
    }

    params = {'park': park_id, 'driver': driver_id}
    response = await se_client.post(
        '/self-employment/fns-se/v3/agreement',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=request_json,
    )

    assert response.status == expected_response_code
    assert await response.json() == expected_response

    agreements_raw = await se_web_context.pg.main_master.fetchval(
        """
        SELECT agreements FROM se.ownpark_profile_forms_common
        WHERE phone_pd_id = $1
        """,
        'PHONE_PD_ID',
    )
    assert agreements_raw == expected_agreements


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
@conftest.agreement_configs3
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_incorrect_transition(
        se_client, mock_driver_profiles, mock_personal,
):
    park_id = 'parkid'
    driver_id = 'contractorid'
    license_id = 'license_pd_id_1'
    license_value = '12345678'
    accepted_agreements = [
        'agreement_taxi_offer_checkbox',
        'agreement_taxi_marketing_offer_checkbox',
        'agreement_confidential_checkbox',
        'some_not_existing_agreement',
    ]
    request_json = {
        'step': 'agreement',
        'agreements': [
            {'id': x, 'state': 'accepted'} for x in accepted_agreements
        ],
    }
    params = {'park': park_id, 'driver': driver_id}

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    def _driver_profiles_retrieve(request):
        assert request.json['id_in_set'] == [f'{park_id}_{driver_id}']
        return {
            'profiles': [
                {
                    'park_driver_profile_id': f'{park_id}_{driver_id}',
                    'data': {'license': {'pd_id': license_id}},
                },
            ],
        }

    @mock_personal('/v1/driver_licenses/retrieve')
    def _license_retrieve(request):
        assert request.json['id'] == license_id
        return {'id': license_id, 'value': license_value}

    response = await se_client.post(
        '/self-employment/fns-se/v3/agreement',
        headers=conftest.DEFAULT_HEADERS,
        params=params,
        json=request_json,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': 'requisites',
        'step_count': 7,
        'step_index': 6,
    }
