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
         VALUES ('PHONE_PD_ID', 'FILLING', 'external_id');
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_reg_address(se_client, mockserver):
    park_id = 'parkid'
    contractor_id = 'contractorid'
    address = 'some address'
    apartment_number = '123'
    postal_code = '1234567'

    @mockserver.json_handler('/geocoder/yandsearch')
    async def _phones_pd(request: http.Request):
        assert dict(request.query) == {
            'results': '1',
            'type': 'geo',
            'text': address,
            'ms': 'json',
            'origin': 'taxi',
        }
        return {
            'features': [
                {
                    'properties': {
                        'GeocoderMetaData': {
                            'Address': {'postal_code': postal_code},
                        },
                    },
                },
            ],
        }

    response = await se_client.post(
        '/self-employment/fns-se/v2/reg-address',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={
            'step': 'address',
            'address': address,
            'apartment_number': apartment_number,
        },
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': 'permission',
        'step_count': 7,
        'step_index': 5,
    }

    response = await se_client.get(
        '/self-employment/fns-se/v2/reg-address',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'address': address,
        'apartment_number': apartment_number,
        'postal_code': postal_code,
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
async def test_incorrect_transition(se_client, mockserver):
    park_id = 'parkid'
    contractor_id = 'contractorid'
    address = 'other address'
    apartment_number = '1234'
    postal_code = '12345678'

    @mockserver.json_handler('/geocoder/yandsearch')
    async def _phones_pd(request: http.Request):
        assert dict(request.query) == {
            'results': '1',
            'type': 'geo',
            'text': address,
            'ms': 'json',
            'origin': 'taxi',
        }
        return {
            'features': [
                {
                    'properties': {
                        'GeocoderMetaData': {
                            'Address': {'postal_code': postal_code},
                        },
                    },
                },
            ],
        }

    response = await se_client.post(
        '/self-employment/fns-se/v2/reg-address',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={
            'step': 'address',
            'address': address,
            'apartment_number': apartment_number,
        },
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': 'requisites',
        'step_count': 7,
        'step_index': 6,
    }

    response = await se_client.get(
        '/self-employment/fns-se/v2/reg-address',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'address': 'address',
        'apartment_number': '123',
        'postal_code': '1234567',
    }
