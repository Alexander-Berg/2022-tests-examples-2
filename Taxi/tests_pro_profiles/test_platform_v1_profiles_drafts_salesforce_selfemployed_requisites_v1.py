import pytest


async def test_get(taxi_pro_profiles, mockserver):
    @mockserver.json_handler(
        '/salesforce/services/data/v46.0/sobjects/Case/CaseId',
    )
    async def _mock_get_case(request):
        request.headers['Authorization'] == 'Bearer access_token'
        return {
            'IBAN__c': '40817312312312312312',
            'SWIFT__c': '043123123',
            'Subject': 'Self-Employed Change Payment Details',
            'Status': 'Closed',
        }

    response = await taxi_pro_profiles.get(
        '/platform/v1/profiles/drafts/salesforce-selfemployed-requisites/v1',
        params={'sf_requisites_case_id': 'CaseId'},
        json={},
    )
    assert response.status_code == 200
    assert response.json() == {
        'status': 'success',
        'requisites': {
            'type': 'bank',
            'account': '40817312312312312312',
            'bik': '043123123',
        },
    }


async def test_get_error_from_sf(taxi_pro_profiles, mockserver):
    @mockserver.json_handler(
        '/salesforce/services/data/v46.0/sobjects/Case/CaseId',
    )
    async def _mock_get_case(request):
        return mockserver.make_response(status=500)

    response = await taxi_pro_profiles.get(
        '/platform/v1/profiles/drafts/salesforce-selfemployed-requisites/v1',
        params={'sf_requisites_case_id': 'CaseId'},
    )
    assert response.status_code == 502


async def test_post(taxi_pro_profiles, mockserver):
    @mockserver.json_handler('/salesforce/services/data/v46.0/sobjects/Case/')
    async def _mock_set_requisites(request):
        request.headers['Authorization'] == 'Bearer access_token'
        assert request.json == {
            'Origin': 'API',
            'Status': 'In Progress',
            'Subject': 'Self-Employed Change Payment Details',
            'RecordTypeId': '0123X000001GI7HQAW',
            'AccountId': 'AccountId',
            'IBAN__c': '40817312312312312312',
            'SWIFT__c': '043123123',
            'WithoutYandexBalance__c': True,
        }
        return {'id': 'CaseId'}

    response = await taxi_pro_profiles.post(
        '/platform/v1/profiles/drafts/salesforce-selfemployed-requisites/v1',
        params={'sf_requisites_case_id': 'CaseId'},
        json={
            'sf_account_id': 'AccountId',
            'requisites': {
                'type': 'bank',
                'account': '40817312312312312312',
                'bik': '043123123',
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {'sf_requisites_case_id': 'CaseId'}


async def test_post_error_from_sf(taxi_pro_profiles, mockserver):
    @mockserver.json_handler('/salesforce/services/data/v46.0/sobjects/Case/')
    async def _mock_set_requisites(request):
        return mockserver.make_response(status=500)

    response = await taxi_pro_profiles.post(
        '/platform/v1/profiles/drafts/salesforce-selfemployed-requisites/v1',
        json={
            'sf_account_id': 'AccountId',
            'requisites': {
                'type': 'bank',
                'account': '40817312312312312312',
                'bik': '043123123',
            },
        },
    )
    assert response.status_code == 502
