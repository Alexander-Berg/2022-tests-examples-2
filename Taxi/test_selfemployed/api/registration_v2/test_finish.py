import pytest

from testsuite.utils import http

from test_selfemployed import conftest


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
             initial_park_id, initial_contractor_id,
             created_park_id, created_contractor_id)
         VALUES
            ('PHONE_PD_ID', 'FINISHED', 'external_id',
             'address', '123',
             '1234567', '{"general": true, "gas_stations": false}',
             'inn_pd_id', 'RESIDENT',
             'salesforce_account_id', NULL,
             'parkid', 'contractorid',
             'newparkid', 'newcontractorid');
        """,
    ],
)
async def test_finish(se_client, mock_personal):
    park_id = 'parkid'
    driver_id = 'contractorid'
    phone = '+70123456789'

    @mock_personal('/v1/phones/retrieve')
    async def _retrieve_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': phone, 'id': 'PHONE_PD_ID'}

    response = await se_client.get(
        '/self-employment/fns-se/v2/finish',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': driver_id},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'is_phone_changed': True,
        'selfemployed': {
            'name': 'Работать на себя',
            'park_id': 'newparkid',
            'phone_number': phone,
        },
        'promocode_enabled': True,
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES
            ('selfreg', 'selfregid', 'PHONE_PD_ID');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id,
             address, apartment_number,
             postal_code, agreements,
             inn_pd_id, residency_state,
             salesforce_account_id, salesforce_requisites_case_id,
             initial_park_id, initial_contractor_id,
             created_park_id, created_contractor_id)
         VALUES
            ('PHONE_PD_ID', 'FINISHED', 'external_id',
             'address', '123',
             '1234567', '{"general": true, "gas_stations": false}',
             'inn_pd_id', 'RESIDENT',
             'salesforce_account_id', NULL,
             'selfreg', 'selfregid',
             'newparkid', 'newcontractorid');
        """,
    ],
)
@pytest.mark.parametrize(
    'get_profile_response, expect_code, expect_response',
    [
        pytest.param(
            {},
            500,
            None,
            marks=[
                pytest.mark.config(SELFEMPLOYED_MIXED_REFERRALS_ENABLED=False),
            ],
        ),
        pytest.param(
            {'rent_option': 'owncar'},
            200,
            {
                'new_driver': {
                    'park_id': 'newparkid',
                    'driver_id': 'newcontractorid',
                },
                'promocode_enabled': True,
            },
            marks=[
                pytest.mark.config(SELFEMPLOYED_MIXED_REFERRALS_ENABLED=False),
            ],
        ),
        pytest.param(
            {'rent_option': 'rent', 'referral_promocode': 'test'},
            200,
            {
                'new_driver': {
                    'park_id': 'newparkid',
                    'driver_id': 'newcontractorid',
                },
                'promocode_enabled': True,
            },
            marks=[
                pytest.mark.config(SELFEMPLOYED_MIXED_REFERRALS_ENABLED=False),
            ],
        ),
        pytest.param(
            {'rent_option': 'rent', 'referral_promocode': 'test'},
            200,
            {
                'new_driver': {
                    'park_id': 'newparkid',
                    'driver_id': 'newcontractorid',
                },
                'promocode_enabled': False,
            },
            marks=[
                pytest.mark.config(SELFEMPLOYED_MIXED_REFERRALS_ENABLED=True),
            ],
        ),
        pytest.param(
            {'rent_option': 'rent', 'park': {'name': 'park_for_rent'}},
            200,
            {
                'new_driver': {
                    'park_id': 'newparkid',
                    'driver_id': 'newcontractorid',
                },
                'park_to_visit': {
                    'name': 'park_for_rent',
                    'description': '',
                    'phone': '',
                    'documents': [],
                    'address': '',
                    'working_hours': '',
                },
                'promocode_enabled': True,
            },
            marks=[
                pytest.mark.config(SELFEMPLOYED_MIXED_REFERRALS_ENABLED=False),
            ],
        ),
    ],
)
async def test_finish_from_selfreg(
        se_client,
        mockserver,
        mock_driver_referrals,
        mock_personal,
        get_profile_response,
        expect_code,
        expect_response,
):
    selfreg_id = 'selfregid'
    phone = '+70123456789'

    @mock_personal('/v1/phones/retrieve')
    async def _retrieve_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': phone, 'id': 'PHONE_PD_ID'}

    @mock_driver_referrals('/service/save-invited-driver')
    async def _save_invited_driver(request: http.Request):
        return {}

    @mockserver.json_handler('/selfreg-api/get_profile')
    def _selfreg_get_profile(request: http.Request):
        assert request.method == 'POST'
        return get_profile_response

    response = await se_client.get(
        '/self-employment/fns-se/v2/finish',
        headers=conftest.DEFAULT_HEADERS,
        params={'selfreg_id': selfreg_id},
    )
    assert response.status == expect_code
    if expect_response is not None:
        content = await response.json()
        assert content == expect_response
