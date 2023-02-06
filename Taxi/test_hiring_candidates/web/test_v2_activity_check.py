import typing

import pytest

from test_hiring_candidates import conftest

CLICKHOUSE_REQUESTS_FILE = 'mock_chyt.json'
REQUESTS_FILE = 'requests.json'
ROUTE = '/v2/activity-check/driver'


@pytest.mark.now('2022-01-01T15:00:00+03:00')
@pytest.mark.parametrize(
    'request_name',
    [
        'check_by_car',
        'check_by_phone',
        'check_by_license',
        'phone_not_found',
        'request_with_interval',
    ],
)
@conftest.main_configuration
async def test_activity_check_valid(
        request_name, load_json, web_app_client, patch,
):
    # arrange
    data = load_json(REQUESTS_FILE)[request_name]
    request_body = data['body']
    expected_response = data['expected_response']
    chyt_data = load_json(CLICKHOUSE_REQUESTS_FILE)[request_name]
    chyt_query = chyt_data['query']
    chyt_response = chyt_data['response']

    @patch('client_chyt.components.AsyncChytClient.execute')
    # pylint: disable=W0612
    async def execute(query: str) -> typing.List[dict]:
        return chyt_response

    # act
    response = await web_app_client.post(ROUTE, json=request_body)

    # assert
    assert execute.calls == [{'query': chyt_query}]
    assert response.status == data['status']
    response_body = await response.json()
    assert response_body == expected_response


@pytest.mark.now('2022-01-01T15:00:00+03:00')
@pytest.mark.parametrize('request_name', ['invalid_request'])
@conftest.main_configuration
async def test_activity_check_invalid(request_name, load_json, web_app_client):
    # arrange
    data = load_json(REQUESTS_FILE)
    request_body = data[request_name]['body']
    expected_response = data[request_name]['expected_response']

    # act
    response = await web_app_client.post(ROUTE, json=request_body)

    # assert
    assert response.status == data[request_name]['status']
    response_body = await response.json()
    assert response_body == expected_response
