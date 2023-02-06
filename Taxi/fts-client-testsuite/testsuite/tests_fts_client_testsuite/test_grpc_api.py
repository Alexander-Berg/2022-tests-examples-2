# flake8: noqa
# pylint: disable=import-error,wildcard-import

import pytest
import sys

from google.protobuf import empty_pb2


@pytest.mark.parametrize('test_name', ['send_positions_1'])
async def test_grpc_api(taxi_fts_client_testsuite, fts_mock, test_name):
    @fts_mock.mock_send_positions
    def mock_send_positions(request, context):
        return empty_pb2.Empty()

    response = await taxi_fts_client_testsuite.get(f'launch/test/{test_name}')

    assert response.status_code == 200
    assert mock_send_positions.times_called > 0
