import json
import logging

from aiohttp import web
import pytest


logger = logging.getLogger(__name__)


@pytest.fixture
def mock_st(request, patch, load_json):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(*args, **kwargs):  # pylint: disable=W0612
        responses = load_json('tracker_responses.json')
        assert kwargs['text'] == responses.get(kwargs['ticket'])


@pytest.fixture
def mock_sf_auth(mock_salesforce):
    @mock_salesforce('/services/oauth2/token')
    async def auth(request):  # pylint: disable=W0612
        return web.json_response(
            {
                'access_token': 'TOKEN',
                'instance_url': 'URL',
                'id': 'ID',
                'token_type': 'TYPE',
                'issued_at': '2019-01-01',
                'signature': 'SIGN',
            },
            status=200,
        )


@pytest.fixture
def mock_sf_case(mock_salesforce, load_json):
    @mock_salesforce('/services/data/v46.0/sobjects/Case/')
    async def create_case(request):  # pylint: disable=W0612
        response = load_json('salesforce_create_case_responses.json').get(
            request.json['LinktoTicket__c'],
        )
        return web.json_response(response['data'], status=response['status'])


@pytest.fixture
def mock_sf_query(mock_salesforce, load_json):
    @mock_salesforce('/services/data/v50.0/query/')
    async def make_query(request):  # pylint: disable=W0612
        response = load_json('salesforce_query_responses.json').get(
            request.query['q'],
        )
        return web.json_response(response['data'], status=response['status'])


@pytest.mark.servicetest
@pytest.mark.usefixtures(
    'mock_sf_auth', 'mock_st', 'mock_sf_query', 'mock_sf_case',
)
@pytest.mark.parametrize(
    'assignee, issue_key, status',
    [
        ('Робот1', 'TRACKERISSUE-1', 201),
        ('Робот2', 'TRACKERISSUE-2', 500),
        ('Робот3', 'TRACKERISSUE-3', 500),
        ('Робот1', 'TRACKERISSUE-4', 500),
    ],
)
async def test_create_case2(web_app_client, assignee, issue_key, status):
    data = {
        'issue_key': issue_key,
        'assignee': assignee,
        'db_id': '58ff6f75bbe84187ad1407599f4f79bf',
        'subject': 'some_subject',
        'description': 'some_description',
    }
    response = await web_app_client.post(
        '/v1/salesforce/tracker/create-case', data=json.dumps(data),
    )

    assert response.status == status
