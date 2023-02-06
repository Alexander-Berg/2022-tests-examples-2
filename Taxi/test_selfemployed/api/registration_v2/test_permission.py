import datetime

import pytest

from testsuite.utils import http

from selfemployed.entities import nalogru_binding
from selfemployed.fns import client_models
from selfemployed.services import nalogru
from test_selfemployed import conftest


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, inn_pd_id, status,
             bind_request_id, bind_requested_at)
        VALUES ('PHONE_PD_ID', NULL, 'IN_PROGRESS',
                'request_id', NOW());
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES ('parkid', 'contractorid', 'PHONE_PD_ID');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id,
             address, apartment_number, postal_code,
             agreements)
        VALUES
            ('PHONE_PD_ID', 'FILLING', 'external_id',
             'address', '123', '1234567',
             '{"general": true, "gas_stations": false}');
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.now('2020-01-01T12:00:00Z')
async def test_permission(
        se_client,
        se_cron_context,
        mock_fleet_parks,
        mock_driver_profiles,
        mock_personal,
        mock_fleet_vehicles,
        mock_salesforce,
        patch,
):
    park_id = 'parkid'
    contractor_id = 'contractorid'
    inn = '012345678901'
    phone = '+70123456789'
    driver_license = 'driver_license'

    @patch('selfemployed.services.nalogru.Service.check_binding_status')
    async def _check_binding(request_id: str):
        assert request_id == 'request_id'
        return nalogru_binding.BindingStatus.COMPLETED, inn

    @mock_personal('/v1/tins/store')
    async def _store_inn_pd(request: http.Request):
        assert request.json == {'value': inn, 'validate': True}
        return {'value': inn, 'id': 'INN_PD_ID'}

    @mock_personal('/v1/tins/retrieve')
    async def _retrieve_inn_pd(request: http.Request):
        assert request.json == {'id': 'INN_PD_ID', 'primary_replica': False}
        return {'value': inn, 'id': 'INN_PD_ID'}

    @mock_personal('/v1/phones/retrieve')
    async def _retrieve_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': phone, 'id': 'PHONE_PD_ID'}

    @mock_personal('/v1/phones/store')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'value': phone, 'validate': True}
        return {'value': phone, 'id': 'PHONE_PD_ID'}

    @patch('selfemployed.fns.client.Client.get_taxpayer_status_v2')
    async def _get_taxpayer_status_v2(inn_normalized: str):
        assert inn_normalized == inn
        return 'MSG_ID'

    @patch('selfemployed.fns.client.Client.get_taxpayer_status_response_v2')
    async def _get_taxpayer_status_response_v2(msg_id: str):
        assert msg_id == 'MSG_ID'
        return client_models.TaxpayerStatus(
            first_name='Имий',
            second_name='Фамильев',
            registration_time=datetime.datetime(2021, 1, 1),
            region_oktmo_code='46000000',
            phone=phone,
            oksm_code='643',
            middle_name='Отчествович',
        )

    @mock_fleet_parks('/v1/parks')
    async def _get_parks(request: http.Request):
        assert request.query['park_id'] == 'parkid'
        return {
            'id': 'parkid',
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

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _get_profile(request: http.Request):
        assert request.json == {'id_in_set': ['parkid_contractorid']}
        print(request)
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'parkid_contractorid',
                    'data': {
                        'license': {'pd_id': 'DL_PD_ID', 'country': 'RUS'},
                        'license_expire_date': '2025-09-01 00:00:00',
                        'license_issue_date': '2021-09-01 00:00:00',
                        'car_id': 'carid',
                        'platform_uid': 'passport_uid',
                    },
                },
            ],
        }

    @mock_fleet_vehicles('/v1/vehicles/retrieve')
    async def _get_car(request: http.Request):
        assert request.json == {'id_in_set': ['parkid_carid']}
        return {
            'vehicles': [
                {
                    'park_id_car_id': 'parkid_carid',
                    'data': {
                        'brand': 'brand',
                        'model': 'model',
                        'number': 'number',
                        'number_normalized': 'number',
                        'color': 'color',
                        'year': '2020',
                    },
                },
            ],
        }

    @mock_personal('/v1/driver_licenses/retrieve')
    async def _retrieve_dl_pd(request: http.Request):
        assert request.json == {'id': 'DL_PD_ID', 'primary_replica': False}
        return {'value': driver_license, 'id': 'DL_PD_ID'}

    @mock_salesforce('/services/data/v52.0/composite')
    async def _create_account(request: http.Request):
        assert request.json == {
            'compositeRequest': [
                {
                    'method': 'POST',
                    'referenceId': 'NewAccount',
                    'url': '/services/data/v46.0/sobjects/Account/',
                    'body': {
                        'RecordTypeId': 'RecordTypeAccount',
                        'Type': 'Selfemployed',
                        'SelfemloyedId__c': 'external_id',
                        'BillingPostalCode': '1234567',
                        'BillingStreet': '1234567, address',
                        'City__c': 'Москва',
                        'DateOfIssuance__c': '2021-09-01T00:00:00',
                        'DateOfExpiration__c': '2025-09-01T00:00:00',
                        'DriverLicenceCountry__c': 'rus',
                        'DriverLicenceNumber__c': driver_license,
                        'FirstName': 'Имий',
                        'LastName': 'Фамильев',
                        'MiddleName': 'Отчествович',
                        'Phone': phone,
                        'TIN__c': inn,
                        'Rent__c': False,
                        'GasStationContract__c': False,
                        'PassportId__c': 'passport_uid',
                    },
                },
                {
                    'method': 'POST',
                    'referenceId': 'NewOpportunity',
                    'url': '/services/data/v46.0/sobjects/Opportunity/',
                    'body': {
                        'RecordTypeId': 'RecordTypeOpportunity',
                        'Name': inn,
                        'AccountId': '@{NewAccount.id}',
                        'StageName': 'Scoring Completed',
                        'CloseDate': '2020-01-08',
                        'City__c': 'Москва',
                        'Platform__c': 'ANDROID',
                        'LeadId__c': 'from_park',
                    },
                },
                {
                    'body': {
                        'Brand__c': 'brand',
                        'Colour__c': 'color',
                        'ManufacturingYear__c': 2020,
                        'Model__c': 'model',
                        'Name': 'brand model',
                        'OpportunityId__c': '@{NewOpportunity.id}',
                        'PlateNo__c': 'number',
                        'RecordTypeId': 'RecordTypeAsset',
                    },
                    'method': 'POST',
                    'referenceId': 'NewAsset',
                    'url': '/services/data/v46.0/sobjects/Asset/',
                },
            ],
            'allOrNone': True,
        }
        return {
            'compositeResponse': [
                {
                    'body': {
                        'id': '003R00000025R22IAE',
                        'success': True,
                        'errors': [],
                    },
                    'httpHeaders': {
                        'Location': '/services/data/v52.0/sobjects/Account/003R00000025R22IAE',  # noqa: E501
                    },
                    'httpStatusCode': 201,
                    'referenceId': 'NewAccount',
                },
                {
                    'body': {
                        'id': 'a00R0000000iN4gIAE',
                        'success': True,
                        'errors': [],
                    },
                    'httpHeaders': {
                        'Location': '/services/data/v52.0/sobjects/Opportunity/a00R0000000iN4gIAE',  # noqa: E501
                    },
                    'httpStatusCode': 201,
                    'referenceId': 'NewOpportunity',
                },
            ],
        }

    response = await se_client.post(
        '/self-employment/fns-se/v2/permission',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={'step': 'permission'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': 'await_own_park',
        'step_count': 7,
        'step_index': 5,
    }

    status_cache = await se_cron_context.pg.main_ro.fetchrow(
        """
        SELECT inn_pd_id, first_name, second_name, registration_time,
               region_oktmo_code, phone_pd_id, oksm_code, middle_name,
               unregistration_time, unregistration_reason, activities,
               email, account_number, update_time,
               registration_certificate_num, increment
        FROM se.taxpayer_status_cache
        """,
    )

    assert dict(status_cache) == dict(
        inn_pd_id='INN_PD_ID',
        first_name='Имий',
        second_name='Фамильев',
        registration_time=datetime.datetime(
            2020, 12, 31, 21, 0, tzinfo=datetime.timezone.utc,
        ),
        region_oktmo_code='46000000',
        phone_pd_id='PHONE_PD_ID',
        oksm_code='643',
        middle_name='Отчествович',
        unregistration_time=None,
        unregistration_reason=None,
        activities=None,
        email=None,
        account_number=None,
        update_time=None,
        registration_certificate_num=None,
        increment=1,
    )


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, inn_pd_id, status,
             bind_request_id, bind_requested_at)
        VALUES ('PHONE_PD_ID', NULL, 'IN_PROGRESS',
                'request_id', NOW());
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES ('parkid', 'contractorid', 'PHONE_PD_ID');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id,
             address, apartment_number, postal_code,
             agreements)
        VALUES
            ('PHONE_PD_ID', 'FILLING', 'external_id',
             'address', '123', '1234567',
             '{"general": true, "gas_stations": false}');
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.now('2020-01-01T12:00:00Z')
async def test_permission_unbound(se_client, patch, mock_personal):
    park_id = 'parkid'
    contractor_id = 'contractorid'

    @mock_personal('/v1/phones/retrieve')
    async def _retrieve_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': '+70123456789', 'id': 'PHONE_PD_ID'}

    @patch('selfemployed.services.nalogru.Service.check_binding_status')
    async def _check_binding(request_id: str):
        assert request_id == 'request_id'
        return nalogru_binding.BindingStatus.FAILED, None

    response = await se_client.post(
        '/self-employment/fns-se/v2/permission',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={'step': 'permission'},
    )

    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'BINDING_ERROR',
        'text': 'Для продолжения необходима привязка к ФНС',
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, inn_pd_id, status,
             bind_request_id, bind_requested_at)
        VALUES ('PHONE_PD_ID', NULL, 'IN_PROGRESS',
                'request_id', NOW());
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES ('parkid', 'contractorid', 'PHONE_PD_ID');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id,
             address, apartment_number, postal_code,
             agreements)
        VALUES
            ('PHONE_PD_ID', 'FILLING', 'external_id',
             'address', '123', '1234567',
             '{"general": true, "gas_stations": false}');
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.now('2020-01-01T12:00:00Z')
async def test_permission_fns_unavailable(se_client, patch, mock_personal):
    park_id = 'parkid'
    contractor_id = 'contractorid'

    @mock_personal('/v1/phones/retrieve')
    async def _retrieve_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': '+70123456789', 'id': 'PHONE_PD_ID'}

    @patch('selfemployed.services.nalogru.Service.check_binding_status')
    async def _check_binding(request_id: str):
        assert request_id == 'request_id'
        raise nalogru.FnsUnavailable()

    response = await se_client.post(
        '/self-employment/fns-se/v2/permission',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={'step': 'permission'},
    )

    assert response.status == 504
    content = await response.json()
    assert content == {
        'code': 'NALOGRU_UNAVALABLE',
        'text': 'Мой Налог временно недоступен',
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
async def test_incorrect_transition(se_client):
    park_id = 'parkid'
    contractor_id = 'contractorid'

    response = await se_client.post(
        '/self-employment/fns-se/v2/permission',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={'step': 'permission'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'next_step': 'requisites',
        'step_count': 7,
        'step_index': 6,
    }


@pytest.mark.config(
    SELFEMPLOYED_RESIDENCY_CHECK_SETTINGS={
        'residents': {'do_allow_anyone': False, 'allowed_oksm_codes': ['643']},
        'non_residents': {'do_allow_anyone': False, 'allowed_oksm_codes': []},
        'temporary_oksm_codes': [None],
    },
)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, inn_pd_id, status,
             bind_request_id, bind_requested_at)
        VALUES ('PHONE_PD_ID', NULL, 'IN_PROGRESS',
                'request_id', NOW());
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES ('parkid', 'contractorid', 'PHONE_PD_ID');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id,
             address, apartment_number, postal_code,
             agreements)
        VALUES
            ('PHONE_PD_ID', 'FILLING', 'external_id',
             'address', '123', '1234567',
             '{"general": true, "gas_stations": false}');
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.now('2020-01-01T12:00:00Z')
async def test_permission_no_oksm(
        se_web_context,
        se_client,
        mock_fleet_parks,
        mock_driver_profiles,
        mock_personal,
        mock_fleet_vehicles,
        patch,
        stq,
):
    park_id = 'parkid'
    contractor_id = 'contractorid'
    inn = '012345678901'
    phone = '+70123456789'
    driver_license = 'driver_license'

    @patch('selfemployed.services.nalogru.Service.check_binding_status')
    async def _check_binding(request_id: str):
        assert request_id == 'request_id'
        return nalogru_binding.BindingStatus.COMPLETED, inn

    @mock_personal('/v1/tins/store')
    async def _store_inn_pd(request: http.Request):
        assert request.json == {'value': inn, 'validate': True}
        return {'value': inn, 'id': 'INN_PD_ID'}

    @mock_personal('/v1/tins/retrieve')
    async def _retrieve_inn_pd(request: http.Request):
        assert request.json == {'id': 'INN_PD_ID', 'primary_replica': False}
        return {'value': inn, 'id': 'INN_PD_ID'}

    @mock_personal('/v1/phones/retrieve')
    async def _retrieve_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': phone, 'id': 'PHONE_PD_ID'}

    @mock_personal('/v1/phones/store')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'value': phone, 'validate': True}
        return {'value': phone, 'id': 'PHONE_PD_ID'}

    @patch('selfemployed.fns.client.Client.get_taxpayer_status_v2')
    async def _get_taxpayer_status_v2(inn_normalized: str):
        assert inn_normalized == inn
        return 'MSG_ID'

    @patch('selfemployed.fns.client.Client.get_taxpayer_status_response_v2')
    async def _get_taxpayer_status_response_v2(msg_id: str):
        assert msg_id == 'MSG_ID'
        return client_models.TaxpayerStatus(
            first_name='Имий',
            second_name='Фамильев',
            registration_time=datetime.datetime(2021, 1, 1),
            region_oktmo_code='46000000',
            phone=phone,
            oksm_code=None,
            middle_name='Отчествович',
        )

    @mock_fleet_parks('/v1/parks')
    async def _get_parks(request: http.Request):
        assert request.query['park_id'] == 'parkid'
        return {
            'id': 'parkid',
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

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _get_profile(request: http.Request):
        assert request.json == {'id_in_set': ['parkid_contractorid']}
        print(request)
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'parkid_contractorid',
                    'data': {
                        'license': {'pd_id': 'DL_PD_ID', 'country': 'RUS'},
                        'license_expire_date': '2025-09-01 00:00:00',
                        'license_issue_date': '2021-09-01 00:00:00',
                        'car_id': 'carid',
                        'platform_uid': 'passport_uid',
                    },
                },
            ],
        }

    @mock_fleet_vehicles('/v1/vehicles/retrieve')
    async def _get_car(request: http.Request):
        assert request.json == {'id_in_set': ['parkid_carid']}
        return {
            'vehicles': [
                {
                    'park_id_car_id': 'parkid_carid',
                    'data': {
                        'brand': 'brand',
                        'model': 'model',
                        'number': 'number',
                        'number_normalized': 'number',
                        'color': 'color',
                        'year': '2020',
                    },
                },
            ],
        }

    @mock_personal('/v1/driver_licenses/retrieve')
    async def _retrieve_dl_pd(request: http.Request):
        assert request.json == {'id': 'DL_PD_ID', 'primary_replica': False}
        return {'value': driver_license, 'id': 'DL_PD_ID'}

    response = await se_client.post(
        '/self-employment/fns-se/v2/permission',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={'step': 'permission'},
    )

    assert response.status == 409
    content = await response.json()
    assert content == {
        'code': 'FNS_TEMPORARY_REGISTRATION',
        'text': 'У вас временная регистрация',
    }
    assert stq.selfemployed_fns_process_temporary_oksm.next_call() == {
        'args': [],
        'eta': datetime.datetime(1970, 1, 1, 0, 0),
        'id': f'{park_id}_{contractor_id}',
        'kwargs': {
            'initial_park_id': park_id,
            'initial_contractor_id': contractor_id,
            'platform': 'ANDROID',
        },
        'queue': 'selfemployed_fns_process_temporary_oksm',
    }

    status_cache = await se_web_context.pg.main_ro.fetchrow(
        """
        SELECT inn_pd_id, first_name, second_name, registration_time,
               region_oktmo_code, phone_pd_id, oksm_code, middle_name,
               unregistration_time, unregistration_reason, activities,
               email, account_number, update_time,
               registration_certificate_num, increment
        FROM se.taxpayer_status_cache
        """,
    )
    assert dict(status_cache) == dict(
        inn_pd_id='INN_PD_ID',
        first_name='Имий',
        second_name='Фамильев',
        registration_time=datetime.datetime(
            2020, 12, 31, 21, 0, tzinfo=datetime.timezone.utc,
        ),
        region_oktmo_code='46000000',
        phone_pd_id='PHONE_PD_ID',
        oksm_code=None,
        middle_name='Отчествович',
        unregistration_time=None,
        unregistration_reason=None,
        activities=None,
        email=None,
        account_number=None,
        update_time=None,
        registration_certificate_num=None,
        increment=1,
    )
