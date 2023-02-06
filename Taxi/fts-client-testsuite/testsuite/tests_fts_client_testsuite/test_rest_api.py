# flake8: noqa
# pylint: disable=import-error,wildcard-import

import pytest


def set_default_mocks(mockserver):
    @mockserver.json_handler('/fleet-tracking-system/v1/position/store')
    def mock_pipeline(request):
        return mockserver.make_response(status=200)


@pytest.mark.parametrize('test_name', ['send_positions_1'])
async def test_rest_api(taxi_fts_client_testsuite, mockserver, test_name):

    set_default_mocks(mockserver)

    response = await taxi_fts_client_testsuite.get(f'launch/test/{test_name}')

    assert response.status_code == 200
