# pylint: disable=redefined-outer-name
import pytest

import eats_integration_workers.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['eats_integration_workers.generated.service.pytest_plugins']


@pytest.fixture(name='metro_mocks')
def _metro_mocks(mockserver, mock_metro, load_json):
    def setup_mocks(testcase):
        @mockserver.handler('/test_get_token')
        def _get_test_get_token(request):
            requests = load_json('mock_requests.json')['token']
            result = (
                requests[testcase] if testcase in requests else requests['200']
            )
            return mockserver.make_response(json=result)

        @mock_metro(
            r'/mpos-selfservice/api/(?P<server_name>\w+)/articles/v3',
            regex=True,
        )
        async def _lookup(request, server_name):
            requests = load_json('mock_requests.json')['article_lookup']
            result = (
                requests[testcase] if testcase in requests else requests['200']
            )

            assert request.json == result

            responses = load_json('mock_responses.json')['article_lookup']

            response = (
                responses[testcase]
                if testcase in responses
                else responses['200']
            )
            return mockserver.make_response(
                json=response['body'], status=response['status'],
            )

        @mock_metro(
            r'/mpos-selfservice/api/(?P<server_name>\w+)/advicenotes',
            regex=True,
        )
        async def _create_order(request, server_name):
            requests = load_json('mock_requests.json')['create_order']
            result = (
                requests[testcase] if testcase in requests else requests['200']
            )

            assert request.json == result

            responses = load_json('mock_responses.json')['create_order']

            response = (
                responses[testcase]
                if testcase in responses
                else responses['200']
            )
            return mockserver.make_response(
                json=response['body'], status=response['status'],
            )

    return setup_mocks
