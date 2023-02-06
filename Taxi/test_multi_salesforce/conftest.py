# pylint: disable=redefined-outer-name
from aiohttp import web
import pytest

import multi_salesforce.generated.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['multi_salesforce.generated.pytest_plugins']


@pytest.fixture
def mock_salesforce_auth(mock_multi_salesforce):
    @mock_multi_salesforce('/services/oauth2/token')
    async def _handler(request):
        return web.json_response(
            {
                'access_token': 'TOKEN',
                'instance_url': 'URL',
                'id': 'ID',
                'token_type': 'TYPE',
                'issued_at': '2019-01-01',
                'signature': 'SIGN',
            },
            status=400,
        )

    return _handler


@pytest.fixture
async def salesforce(mockserver):
    @mockserver.json_handler('/salesforce/services/oauth2/token')
    def auth(request):  # pylint: disable=W0612
        if request.form['client_id'] == 'b2b_client_id':
            data = {
                'access_token': 'b2b_access_token',
                'instance_url': '$mockserver/salesforce',
                'id': 'b2b_id',
                'token_type': 'b2b_token_type',
                'issued_at': 'b2b_issued_at',
                'signature': 'b2b_signature',
            }
        elif request.form['client_id'] == 'taxi_client_id':
            data = {
                'access_token': 'taxi_access_token',
                'instance_url': '$mockserver/salesforce',
                'id': 'taxi_id',
                'token_type': 'taxi_token_type',
                'issued_at': 'taxi_issued_at',
                'signature': 'taxi_signature',
            }
        return mockserver.make_response(json=data, status=200)

    @mockserver.json_handler(
        r'/salesforce/services/data/v46.0'
        r'/sobjects/(?P<sobject_type>\w+)/(?P<sobject_id>\w+)',
        regex=True,
    )  # pylint: disable=W0612
    def get_user(request, sobject_type, sobject_id):
        if request.headers['Authorization'] == 'Bearer b2b_access_token':
            data = {
                'Type': 'b2b',
                'City__c': 'Москва',
                'IBAN__c': 'account',
                'SWIFT__c': 'bik',
            }
        elif request.headers['Authorization'] == 'Bearer taxi_access_token':
            data = {
                'Type': 'taxi',
                'City__c': 'Москва',
                'IBAN__c': 'account',
                'SWIFT__c': 'bik',
            }
        return mockserver.make_response(json=data, status=200)

    @mockserver.json_handler(
        r'/salesforce/services/data/v46.0/sobjects/(?P<sobject_type>\w+)',
        regex=True,
    )  # pylint: disable=W0612
    def create_object(request, sobject_type):
        if sobject_type == 'Account':
            if request.headers['Authorization'] == 'Bearer b2b_access_token':
                data = {
                    'RecordTypeId': 'RecordTypeAccount',
                    'AccountId': 'b2b',
                    'Status': 'In Progress',
                    'Origin': 'API',
                    'IBAN__c': '1',
                    'SWIFT__c': '1',
                    'Subject': 'Self-Employed Change Payment Details',
                }
            elif (
                request.headers['Authorization'] == 'Bearer taxi_access_token'
            ):
                data = {
                    'RecordTypeId': 'RecordTypeAccount',
                    'AccountId': 'taxi',
                    'Status': 'In Progress',
                    'Origin': 'API',
                    'IBAN__c': '2',
                    'SWIFT__c': '2',
                    'Subject': 'Self-Employed Change Payment Details',
                }
        elif (
            sobject_type == 'Case'
            and request.headers['Authorization'] == 'Bearer taxi_access_token'
        ):
            data = {
                'RecordTypeId': 'RecordTypeCase',
                'AccountId': 'taxi',
                'Status': 'In Progress',
                'Origin': 'API',
                'IBAN__c': '3',
                'SWIFT__c': '3',
                'Subject': 'Self-Employed Change Payment Details',
            }
        return mockserver.make_response(json=data, status=201)

    @mockserver.json_handler(
        '/salesforce/services/data/v46.0/queryAll',
    )  # pylint: disable=W0612
    def get_query_all(request):
        return mockserver.make_response(
            json={
                'totalSize': 1,
                'records': [
                    {
                        'Id': 1,
                        'City__c': 'Moscow',
                        'FirstName': 'Danil',
                        'LastName': 'Yacenko',
                    },
                ],
            },
            status=200,
        )

    @mockserver.json_handler(
        r'/salesforce/services/data/v46.0'
        r'/query/(?P<query_id>\w+)-(?P<start_index>\w+)',
        regex=True,
    )  # pylint: disable=W0612
    def next_query(request, query_id, start_index):
        return mockserver.make_response(status=200)
