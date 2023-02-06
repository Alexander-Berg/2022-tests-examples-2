import datetime

import pytest

from testsuite.utils import http

from selfemployed.entities import nalogru_binding
from selfemployed.fns import client_models
from selfemployed.generated.web import web_context


@pytest.mark.parametrize('lead_id', (None, '123'))
@pytest.mark.now('2020-01-01T12:00:00Z')
async def test_happy_path(
        se_web_context: web_context.Context,
        patch,
        mock_salesforce,
        mock_selfreg,
        mock_personal,
        mock_tags,
        mockserver,
        stq,
        lead_id,
):
    park_id = 'selfreg'
    contractor_id = 'selfreg_id'
    phone = '+70123456789'
    inn = '012345678901'
    driver_license = 'driver_license'
    new_park_id = 'new_park_id'
    new_contractor_id = 'new_contractor_id'
    external_id = 'external_id'

    @patch(
        'selfemployed.entities.ownpark_profile_form.'
        'CommonFormPart.make_external_id',
    )
    def _make_external_id():
        return external_id

    @mock_personal('/v1/phones/store')
    async def _store_phones_pd(request: http.Request):
        value: str = request.json['value']
        return {'value': value, 'id': 'PHONE_PD_ID'}

    @mock_personal('/v1/phones/retrieve')
    async def _retrieve_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': phone, 'id': 'PHONE_PD_ID'}

    @patch('selfemployed.services.nalogru.Service.bind_by_phone')
    async def _bind(phone_normalized):
        assert phone_normalized == phone
        return 'request_id'

    @mockserver.json_handler('/geocoder/yandsearch')
    async def _phones_pd(request: http.Request):
        assert dict(request.query) == {
            'results': '1',
            'type': 'geo',
            'text': 'address',
            'ms': 'json',
            'origin': 'taxi',
        }
        return {
            'features': [
                {
                    'properties': {
                        'GeocoderMetaData': {
                            'Address': {'postal_code': '1234567'},
                        },
                    },
                },
            ],
        }

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

    @mock_selfreg('/internal/selfreg/v2/profile')
    async def _get_selfreg_profile(request: http.Request):
        assert dict(request.query) == {'selfreg_id': 'selfreg_id'}
        profile_data = {
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
        if lead_id:
            profile_data['registration_parameters'] = [
                {'name': 'lead_id', 'value': lead_id},
            ]
        return profile_data

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
                        'SelfemloyedId__c': external_id,
                        'BillingPostalCode': '1234567',
                        'BillingStreet': '1234567, address',
                        'City__c': 'Москва',
                        'DateOfIssuance__c': '2015-09-01T00:00:00',
                        'DateOfExpiration__c': '2100-01-01T00:00:00',
                        'DriverLicenceCountry__c': 'rus',
                        'DriverLicenceNumber__c': driver_license,
                        'FirstName': 'Имий',
                        'LastName': 'Фамильев',
                        'MiddleName': 'Отчествович',
                        'Phone': phone,
                        'TIN__c': inn,
                        'Rent__c': True,
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
                        'LeadId__c': lead_id,
                    },
                },
            ],
            'allOrNone': True,
        }
        return {
            'compositeResponse': [
                {
                    'body': [
                        {
                            'message': (
                                'duplicate value found: SelfemloyedId__c '
                                'повторяет значение для записи '
                                'с кодом: 003R00000025R22'
                            ),
                            'errorCode': 'DUPLICATE_VALUE',
                            'fields': [],
                        },
                    ],
                    'httpHeaders': {},
                    'httpStatusCode': 400,
                    'referenceId': 'NewAccount',
                },
                {
                    'body': [
                        {
                            'errorCode': 'PROCESSING_HALTED',
                            'message': (
                                'The transaction was rolled back since '
                                'another operation in the same '
                                'transaction failed.'
                            ),
                        },
                    ],
                    'httpHeaders': {},
                    'httpStatusCode': 400,
                    'referenceId': 'NewOpportunity',
                },
            ],
        }

    @mock_salesforce(
        '/services/data/v46.0/sobjects/Account/SelfemloyedId__c/external_id',
    )
    async def _mock_get_account(request: http.Request):
        assert request.query == {'fields': 'Id'}
        return {'Id': '003R00000025R22IAE'}

    @mock_selfreg('/internal/selfreg/v1/new-contractor-callback')
    async def _selfreg_callback(request):
        assert request.json == {
            'selfreg_id': contractor_id,
            'park_id': new_park_id,
            'driver_profile_id': new_contractor_id,
            'source': 'selfemployed',
        }
        return {}

    @mock_tags('/v2/upload')
    async def _v2_upload(request):
        assert request.json == {
            'provider_id': 'selfemployed',
            'append': [
                {
                    'entity_type': 'park',
                    'tags': [{'name': 'selfemployed', 'entity': new_park_id}],
                },
            ],
        }
        return {}

    reg_service = se_web_context.services.ownpark_registration

    async with se_web_context.pg.main_master.acquire() as conn:
        await reg_service.ensure_initialized(
            park_id=park_id,
            contractor_id=contractor_id,
            phone_raw=phone,
            conn=conn,
        )
        await reg_service.bind_nalogru(
            park_id=park_id, contractor_id=contractor_id, conn=conn,
        )
        await reg_service.accept_agreements(
            park_id=park_id,
            contractor_id=contractor_id,
            general=True,
            gas_stations=False,
            conn=conn,
        )
        await reg_service.fill_billing_address(
            park_id=park_id,
            contractor_id=contractor_id,
            address='address',
            apartment_number='apartment_number',
            conn=conn,
        )
        await reg_service.start_park_creation(
            park_id=park_id,
            contractor_id=contractor_id,
            platform='ANDROID',
            conn=conn,
        )
        await reg_service.finish_park_creation(
            external_id=external_id,
            new_park_id=new_park_id,
            new_contractor_id=new_contractor_id,
            conn=conn,
        )

    assert stq.selfemployed_fns_tag_contractor.next_call() == {
        'args': [],
        'eta': datetime.datetime(1970, 1, 1, 0, 0),
        'id': (
            '57b385651c5baddd7031bb733f3c36f3d0c550192eaf83537aafaded50088e2b'
        ),
        'kwargs': {
            'contractor_id': 'new_contractor_id',
            'park_id': 'new_park_id',
            'trigger_id': 'ownpark_profile_created',
        },
        'queue': 'selfemployed_fns_tag_contractor',
    }

    pg_pool = se_web_context.pg.main_master

    form_contractor = _record_to_dict(
        await pg_pool.fetchrow(
            'SELECT * FROM se.ownpark_profile_forms_contractor',
        ),
    )
    assert form_contractor == {
        'initial_park_id': 'selfreg',
        'initial_contractor_id': 'selfreg_id',
        'phone_pd_id': 'PHONE_PD_ID',
        'is_phone_verified': True,
        'track_id': None,
        'increment': 1,
        'last_step': 'intro',
        'profession': 'taxi-driver',
    }

    form_common = _record_to_dict(
        await pg_pool.fetchrow(
            'SELECT * FROM se.ownpark_profile_forms_common',
        ),
    )
    assert form_common == {
        'phone_pd_id': 'PHONE_PD_ID',
        'state': 'FINISHED',
        'external_id': 'external_id',
        'address': 'address',
        'apartment_number': 'apartment_number',
        'postal_code': '1234567',
        'agreements': {'general': True, 'gas_stations': False},
        'inn_pd_id': 'INN_PD_ID',
        'residency_state': 'RESIDENT',
        'salesforce_account_id': '003R00000025R22IAE',
        'salesforce_requisites_case_id': None,
        'initial_park_id': 'selfreg',
        'initial_contractor_id': 'selfreg_id',
        'created_park_id': 'new_park_id',
        'created_contractor_id': 'new_contractor_id',
        'increment': 6,
    }

    binding = _record_to_dict(
        await pg_pool.fetchrow('SELECT * FROM se.nalogru_phone_bindings'),
    )
    assert binding == {
        'phone_pd_id': 'PHONE_PD_ID',
        'status': 'COMPLETED',
        'inn_pd_id': 'INN_PD_ID',
        'bind_request_id': None,
        'bind_requested_at': None,
        'exceeded_legal_income_year': None,
        'exceeded_reported_income_year': None,
        'increment': 4,
        'business_unit': 'taxi',
    }

    profile = _record_to_dict(
        await pg_pool.fetchrow('SELECT * FROM se.finished_profiles'),
    )
    assert profile == {
        'park_id': 'p1',
        'contractor_profile_id': 'd1',
        'phone_pd_id': 'PHONE_PD_ID',
        'inn_pd_id': 'INN_PD_ID',
        'do_send_receipts': True,
        'is_own_park': True,
        'increment': 1,
        'business_unit': 'taxi',
    }

    metadata = _record_to_dict(
        await pg_pool.fetchrow(
            'SELECT * FROM se.finished_ownpark_profile_metadata',
        ),
    )
    assert metadata == {
        'created_park_id': 'new_park_id',
        'created_contractor_id': 'new_contractor_id',
        'phone_pd_id': 'PHONE_PD_ID',
        'external_id': 'external_id',
        'initial_park_id': 'selfreg',
        'initial_contractor_id': 'selfreg_id',
        'salesforce_account_id': '003R00000025R22IAE',
        'salesforce_requisites_case_id': None,
        'increment': 1,
    }


def _record_to_dict(record) -> dict:
    result = dict(record)
    del result['created_at']
    del result['updated_at']
    return result
