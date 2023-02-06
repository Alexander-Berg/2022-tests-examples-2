import json

from aiohttp import web
import pytest


def read_tests_data() -> dict:
    path = 'services/internal-b2b-automations/test_internal_b2b_automations/'
    filename = 'web/static/test_case_creating.json'
    full_filename = path + filename
    with open(full_filename, 'r') as file:
        tests = json.load(file)
    return tests


@pytest.fixture
def sf_creating_case_mock(mock_multi_salesforce):
    @mock_multi_salesforce(r'/services/data/v46.0/sobjects/(\w*)', regex=True)
    async def handler(request):
        tests = read_tests_data()
        test = tests[handler.counter][1]
        assert request.json == test
        handler.counter += 1
        return web.json_response(
            {'id': 0, 'success': 'true', 'errors': []}, status=201,
        )

    handler.counter = 0
    return handler


async def test_case_data_matches(
        web_app_client,
        mock_salesforce_auth,
        sf_creating_case_mock,  # pylint: disable=W0621
):
    tests = read_tests_data()
    test_number = len(tests)
    for test_i in range(test_number):
        response = await web_app_client.post(
            '/v1/create-case',
            headers={'token': 'auth_token'},
            json=tests[test_i][0],
        )
        assert response.status == 200


@pytest.fixture
def sf_not_creating_case_mock(mockserver):
    @mockserver.json_handler(
        r'/URL/services/data/v46.0/sobjects/(\w*)', regex=True,
    )
    async def handler(request):
        assert False

    return handler


async def test_case_authentification(
        web_app_client,
        mock_salesforce_auth,  # pylint: disable=W0621
        # sf_not_creating_case_mock,  # pylint: disable=W0621
):
    test_body = read_tests_data()[0][0]
    response = await web_app_client.post(
        '/v1/create-case',
        headers={'token': 'not_a_correct_token'},
        json=test_body,
    )
    assert response.status == 402
