from typing import Any
from typing import Dict

import pytest

from testsuite.utils import http

CONFIGS = {
    'PRO_PROFILES_SELFEMPLOYED_SALESFORCE_PROFESSION_MAPPING': {
        'market-courier': {
            'account_record_type_id': 'RecordTypeAccount',
            'account_type': 'Market Selfemployed',
            'opportunity_record_type_id': 'RecordTypeOpportunity',
            'opportunity_stage_name': 'Scoring Completed',
            'default_city': 'Москва',
            'agreements': [
                {'agreement_id': 'test', 'sf_field': 'TestAgreement'},
                {
                    'agreement_id': 'test_negate',
                    'sf_field': 'TestNegateAgreement',
                    'negate_value': True,
                },
            ],
        },
    },
    'PRO_PROFILES_LICENSE_PARAMS': {'country': 'rus'},
}

PARAMS = [
    pytest.param(
        {
            'park_id': 'park_id1',
            'contractor_profile_id': 'contractor_profile_id1',
            'profession': 'market-courier',
            'first_name': 'FN',
            'last_name': 'LN',
            'middle_name': 'MN',
            'inn_pd_id': 'INN_PD_ID',
            'phone_pd_id': 'PHONE_PD_ID',
            'selfemployed_id': 'selfemployed_id',
            'agreements': {'test': True, 'test_negate': False},
        },
        True,
        False,
        '000000000000',
        'CONSUMERD4AC1D65C093412FF053E9CE666EC998',
    ),
    pytest.param(
        {
            'park_id': 'park_id2',
            'contractor_profile_id': 'contractor_profile_id2',
            'profession': 'market-courier',
            'first_name': 'FN',
            'last_name': 'LN',
            'middle_name': 'MN',
            'inn_pd_id': 'INN_PD_ID',
            'phone_pd_id': 'PHONE_PD_ID',
            'selfemployed_id': 'selfemployed_id',
            'agreements': {'test': True, 'test_negate': False},
        },
        False,
        True,
        '000000000000',
        'CONSUMERFE9083177FD0DEB7F053E9CE666EC998',
    ),
]


@pytest.mark.parametrize(
    'sf_request,phone,passport_uid,inn,expected_license', PARAMS,
)
@pytest.mark.config(**CONFIGS)
@pytest.mark.pgsql('pro_profiles', files=['profiles.sql'])
@pytest.mark.now('2021-09-01T00:00:00+00:00')
async def test_salesforce_account_create(
        taxi_pro_profiles,
        mockserver,
        pgsql,
        sf_request,
        phone,
        passport_uid,
        inn,
        expected_license,
):
    @mockserver.json_handler('/personal/v1/tins/retrieve')
    async def _retrieve_inn_pd(request: http.Request):
        assert request.json == {'id': 'INN_PD_ID', 'primary_replica': False}
        return {'value': '000000000000', 'id': 'INN_PD_ID'}

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    async def _retrieve_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': '+70000000000', 'id': 'PHONE_PD_ID'}

    @mockserver.json_handler('/salesforce/services/data/v52.0/composite')
    async def _create_account(request: http.Request):
        expected_json: Dict[str, Any] = {
            'compositeRequest': [
                {
                    'method': 'POST',
                    'referenceId': 'NewAccount',
                    'url': '/services/data/v46.0/sobjects/Account/',
                    'body': {
                        'RecordTypeId': 'RecordTypeAccount',
                        'Type': 'Market Selfemployed',
                        'SelfemloyedId__c': 'selfemployed_id',
                        'City__c': 'Москва',
                        'DateOfIssuance__c': '2021-09-01T00:00:00+0000',
                        'DateOfExpiration__c': '2121-09-01T06:00:00+0000',
                        'DriverLicenceCountry__c': 'rus',
                        'DriverLicenceNumber__c': expected_license,
                        'FirstName': 'FN',
                        'LastName': 'LN',
                        'MiddleName': 'MN',
                        'Phone': '+70000000000',
                        'TIN__c': inn,
                        'Rent__c': False,
                        'ParkId__c': sf_request['park_id'],
                        'DriverId__c': sf_request['contractor_profile_id'],
                        'TestAgreement': True,
                        'TestNegateAgreement': True,
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
                        'CloseDate': '2021-09-01T00:00:00+0000',
                        'NeedToCreateBase__c': True,
                        'NeedToCreateCLID__c': True,
                        'NeedToCreateDriver__c': True,
                        'ProfessionId__c': 'market-courier',
                        'City__c': 'Москва',
                    },
                },
            ],
            'allOrNone': True,
        }
        if passport_uid:
            expected_json['compositeRequest'][0]['body'][
                'PassportId__c'
            ] = 'passport_uid'
        if phone:
            expected_json['compositeRequest'][0]['body'][
                'OtherPhone'
            ] = '+70000000000'

        assert request.json == expected_json
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

    response = await taxi_pro_profiles.post(
        '/platform/v1/profiles/drafts/salesforce-selfemployed-account/v1',
        json=sf_request,
    )

    assert response.status_code == 200
    assert response.json() == {'sf_account_id': '003R00000025R22IAE'}


@pytest.mark.parametrize(
    'sf_request,phone,passport_uid,inn,expected_license', PARAMS,
)
@pytest.mark.config(**CONFIGS)
@pytest.mark.pgsql('pro_profiles', files=['profiles.sql'])
@pytest.mark.now('2021-09-01T00:00:00+00:00')
async def test_salesforce_account_create_find_by_external(
        taxi_pro_profiles,
        mockserver,
        pgsql,
        sf_request,
        phone,
        passport_uid,
        inn,
        expected_license,
):
    @mockserver.json_handler('/personal/v1/tins/retrieve')
    async def _retrieve_inn_pd(request: http.Request):
        assert request.json == {'id': 'INN_PD_ID', 'primary_replica': False}
        return {'value': inn, 'id': 'INN_PD_ID'}

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    async def _retrieve_phone_pd(request: http.Request):
        assert request.json == {'id': 'PHONE_PD_ID', 'primary_replica': False}
        return {'value': '+70000000000', 'id': 'PHONE_PD_ID'}

    @mockserver.json_handler('/salesforce/services/data/v52.0/composite')
    async def _create_account(request: http.Request):
        expected_json: Dict[str, Any] = {
            'compositeRequest': [
                {
                    'method': 'POST',
                    'referenceId': 'NewAccount',
                    'url': '/services/data/v46.0/sobjects/Account/',
                    'body': {
                        'RecordTypeId': 'RecordTypeAccount',
                        'Type': 'Market Selfemployed',
                        'SelfemloyedId__c': 'selfemployed_id',
                        'City__c': 'Москва',
                        'DateOfIssuance__c': '2021-09-01T00:00:00+0000',
                        'DateOfExpiration__c': '2121-09-01T06:00:00+0000',
                        'DriverLicenceCountry__c': 'rus',
                        'DriverLicenceNumber__c': expected_license,
                        'FirstName': 'FN',
                        'LastName': 'LN',
                        'MiddleName': 'MN',
                        'Phone': '+70000000000',
                        'TIN__c': inn,
                        'Rent__c': False,
                        'ParkId__c': sf_request['park_id'],
                        'DriverId__c': sf_request['contractor_profile_id'],
                        'TestAgreement': True,
                        'TestNegateAgreement': True,
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
                        'CloseDate': '2021-09-01T00:00:00+0000',
                        'NeedToCreateBase__c': True,
                        'NeedToCreateCLID__c': True,
                        'NeedToCreateDriver__c': True,
                        'ProfessionId__c': 'market-courier',
                        'City__c': 'Москва',
                    },
                },
            ],
            'allOrNone': True,
        }
        if passport_uid:
            expected_json['compositeRequest'][0]['body'][
                'PassportId__c'
            ] = 'passport_uid'
        if phone:
            expected_json['compositeRequest'][0]['body'][
                'OtherPhone'
            ] = '+70000000000'

        assert request.json == expected_json
        return {
            'compositeResponse': [
                {
                    'body': [
                        {
                            'message': (
                                'duplicate value found: Exte '
                                'повторяет значение для записи '
                                'с кодом: 003R00000025R22IAE'
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

    @mockserver.json_handler(
        '/salesforce/services/data/v46.0/sobjects'
        '/Account/SelfemloyedId__c/selfemployed_id',
    )
    async def _find_by_external_id(request: http.Request):
        assert request.query == {'fields': 'Id'}
        return {'Id': '003R00000025R22IAE'}

    response = await taxi_pro_profiles.post(
        '/platform/v1/profiles/drafts/salesforce-selfemployed-account/v1',
        json=sf_request,
    )

    assert response.status_code == 200
    assert response.json() == {'sf_account_id': '003R00000025R22IAE'}
