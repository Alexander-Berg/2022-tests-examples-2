from aiohttp import web
import pytest


REQUESTS_FILE = 'requests.json'
ROUTE = '/v1/infranaim-mongo/tickets'


@pytest.mark.parametrize('request_name', ['ok', 'error'])
async def test_get_mongo_tickets(
        mockserver, taxi_hiring_api_web, load_json, request_name,
):
    test_data = load_json(REQUESTS_FILE)[request_name]
    response_data = test_data['response_data']
    response_code = test_data['status_code']

    @mockserver.json_handler(
        '/hiring-candidates-py3/v1/infranaim-mongo/tickets',
    )
    async def _handler(_):
        return web.json_response(response_data, status=response_code)

    async def _make_request():
        headers = {'X-Consumer-Id': 'test_consumer'}
        response = await taxi_hiring_api_web.get(ROUTE, headers=headers)
        assert response.status == response_code
        return await response.json()

    result = await _make_request()
    assert result == response_data
