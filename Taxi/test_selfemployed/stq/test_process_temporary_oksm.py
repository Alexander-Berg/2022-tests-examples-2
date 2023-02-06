import datetime

import pytest

from taxi.stq import async_worker_ng as async_worker
from testsuite.utils import http

from selfemployed.entities import nalogru_binding
from selfemployed.fns import client_models
from selfemployed.stq import process_temporary_oksm
from test_selfemployed import conftest


@pytest.mark.config(
    SELFEMPLOYED_RESIDENCY_CHECK_SETTINGS={
        'residents': {'do_allow_anyone': False, 'allowed_oksm_codes': ['643']},
        'non_residents': {'do_allow_anyone': False, 'allowed_oksm_codes': []},
        'temporary_oksm_codes': [None],
    },
    SELFEMPLOYED_TEMPORARY_OKSM_PROCESSING_SETTINGS={
        'enabled': True,
        'retry_count': 120,
        'retry_delay_minutes': 60,
        'success_push': {
            'message_key': 'success_fns_temporary_registration',
            'data': {'code': 100},
        },
        'failure_push': {
            'message_key': 'failure_fns_temporary_registration',
            'data': {'code': 100},
        },
        'success_sms': {
            'message_key': 'success_fns_temporary_registration',
            'intent': 'test',
        },
        'failure_sms': {
            'message_key': 'failure_fns_temporary_registration',
            'intent': 'test',
        },
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
async def test_no_oksm(
        mock_fleet_parks,
        mock_driver_profiles,
        mock_personal,
        mock_fleet_vehicles,
        mock_client_notify,
        mock_ucommunications,
        patch,
        stq3_context,
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

    @mock_personal('/v1/phones/store')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'value': phone, 'validate': True}
        return {'value': phone, 'id': 'PHONE_PD_ID'}

    @mock_personal('/v1/phones/retrieve')
    async def _retrieve_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
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

    @mock_client_notify('/v2/push')
    async def _send_message(request: http.Request):
        assert request.json == {
            'intent': 'MessageNew',
            'service': 'taximeter',
            'client_id': f'{park_id}-{contractor_id}',
            'notification': {'text': 'Регистрация неуспешна'},
            'data': {'code': 100},
        }
        return {'notification_id': 'notification_id'}

    @mock_ucommunications('/user/sms/send')
    async def _send_sms(request):
        assert request.json == {
            'phone_id': 'PHONE_PD_ID',
            'text': 'Регистрация неуспешна',
            'intent': 'test',
        }
        return {'code': 'code', 'message': 'message'}

    await process_temporary_oksm.task(
        context=stq3_context,
        task_meta_info=async_worker.TaskInfo(
            id='external_id',
            exec_tries=0,
            reschedule_counter=120,
            queue='selfemployed_fns_process_temporary_oksm',
        ),
        initial_park_id=park_id,
        initial_contractor_id=contractor_id,
        platform='ANDROID',
    )

    assert not stq.selfemployed_fns_process_temporary_oksm.has_calls

    await process_temporary_oksm.task(
        context=stq3_context,
        task_meta_info=async_worker.TaskInfo(
            id='external_id',
            exec_tries=0,
            reschedule_counter=0,
            queue='selfemployed_fns_process_temporary_oksm',
        ),
        initial_park_id=park_id,
        initial_contractor_id=contractor_id,
        platform='ANDROID',
    )

    assert stq.selfemployed_fns_process_temporary_oksm.has_calls


@pytest.mark.config(
    SELFEMPLOYED_RESIDENCY_CHECK_SETTINGS={
        'residents': {'do_allow_anyone': False, 'allowed_oksm_codes': ['643']},
        'non_residents': {'do_allow_anyone': False, 'allowed_oksm_codes': []},
        'temporary_oksm_codes': [None],
    },
    SELFEMPLOYED_TEMPORARY_OKSM_PROCESSING_SETTINGS={
        'enabled': True,
        'retry_count': 120,
        'retry_delay_minutes': 60,
        'success_push': {
            'message_key': 'success_fns_temporary_registration',
            'data': {'code': 100},
        },
        'failure_push': {
            'message_key': 'failure_fns_temporary_registration',
            'data': {'code': 100},
        },
        'success_sms': {
            'message_key': 'success_fns_temporary_registration',
            'intent': 'test',
        },
        'failure_sms': {
            'message_key': 'failure_fns_temporary_registration',
            'intent': 'test',
        },
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
async def test_exception(
        mock_client_notify, mock_ucommunications, patch, stq3_context, stq,
):
    park_id = 'parkid'
    contractor_id = 'contractorid'

    @patch('selfemployed.services.nalogru.Service.check_binding_status')
    async def _check_binding(request_id: str):
        raise Exception('Something happened')

    @mock_client_notify('/v2/push')
    async def _send_message(request: http.Request):
        assert request.json == {
            'intent': 'MessageNew',
            'service': 'taximeter',
            'client_id': f'{park_id}-{contractor_id}',
            'notification': {'text': 'Регистрация неуспешна'},
            'data': {'code': 100},
        }
        return {'notification_id': 'notification_id'}

    @mock_ucommunications('/user/sms/send')
    async def _send_sms(request):
        assert request.json == {
            'phone_id': 'PHONE_PD_ID',
            'text': 'Регистрация неуспешна',
            'intent': 'test',
        }
        return {'code': 'code', 'message': 'message'}

    await process_temporary_oksm.task(
        context=stq3_context,
        task_meta_info=async_worker.TaskInfo(
            id='external_id',
            exec_tries=0,
            reschedule_counter=120,
            queue='selfemployed_fns_process_temporary_oksm',
        ),
        initial_park_id=park_id,
        initial_contractor_id=contractor_id,
        platform='ANDROID',
    )

    assert not stq.selfemployed_fns_process_temporary_oksm.has_calls

    await process_temporary_oksm.task(
        context=stq3_context,
        task_meta_info=async_worker.TaskInfo(
            id='external_id',
            exec_tries=0,
            reschedule_counter=0,
            queue='selfemployed_fns_process_temporary_oksm',
        ),
        initial_park_id=park_id,
        initial_contractor_id=contractor_id,
        platform='ANDROID',
    )

    assert stq.selfemployed_fns_process_temporary_oksm.has_calls


@pytest.mark.config(
    SELFEMPLOYED_RESIDENCY_CHECK_SETTINGS={
        'residents': {'do_allow_anyone': False, 'allowed_oksm_codes': ['643']},
        'non_residents': {'do_allow_anyone': False, 'allowed_oksm_codes': []},
        'temporary_oksm_codes': [None],
    },
    SELFEMPLOYED_TEMPORARY_OKSM_PROCESSING_SETTINGS={
        'enabled': True,
        'retry_count': 120,
        'retry_delay_minutes': 60,
        'success_push': {
            'message_key': 'success_fns_temporary_registration',
            'data': {'code': 100},
        },
        'failure_push': {
            'message_key': 'failure_fns_temporary_registration',
            'data': {'code': 100},
        },
        'success_sms': {
            'message_key': 'success_fns_temporary_registration',
            'intent': 'test',
        },
        'failure_sms': {
            'message_key': 'failure_fns_temporary_registration',
            'intent': 'test',
        },
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
async def test_resident_oksm(
        mock_fleet_parks,
        mock_driver_profiles,
        mock_personal,
        mock_fleet_vehicles,
        mock_salesforce,
        mock_client_notify,
        mock_ucommunications,
        patch,
        stq3_context,
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

    @mock_personal('/v1/phones/store')
    async def _store_phone_pd(request: http.Request):
        assert request.json == {'value': phone, 'validate': True}
        return {'value': phone, 'id': 'PHONE_PD_ID'}

    @mock_personal('/v1/phones/retrieve')
    async def _retrieve_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
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

    @mock_client_notify('/v2/push')
    async def _send_message(request: http.Request):
        assert request.json == {
            'intent': 'MessageNew',
            'service': 'taximeter',
            'client_id': f'{park_id}-{contractor_id}',
            'notification': {'text': 'Успешно зарегистрирован'},
            'data': {'code': 100},
        }
        return {'notification_id': 'notification_id'}

    @mock_ucommunications('/user/sms/send')
    async def _send_sms(request):
        assert request.json == {
            'phone_id': 'PHONE_PD_ID',
            'text': 'Успешно зарегистрирован',
            'intent': 'test',
        }
        return {'code': 'code', 'message': 'message'}

    await process_temporary_oksm.task(
        context=stq3_context,
        task_meta_info=async_worker.TaskInfo(
            id='external_id',
            exec_tries=0,
            reschedule_counter=0,
            queue='selfemployed_fns_process_temporary_oksm',
        ),
        initial_park_id=park_id,
        initial_contractor_id=contractor_id,
        platform='ANDROID',
    )

    assert not stq.selfemployed_fns_process_temporary_oksm.has_calls
