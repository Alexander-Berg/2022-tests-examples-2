# pylint: disable=protected-access, redefined-outer-name
import datetime
import json

import pytest

from taxi import discovery
from taxi.clients import parks_replica
from taxi.clients import tvm


@pytest.fixture
async def test_app(test_taxi_app):
    config_ = test_taxi_app.config
    service = discovery.find_service('parks-replica')
    test_taxi_app.parks_replica_client = parks_replica.ParksReplicaApiClient(
        session=test_taxi_app.session,
        service=service,
        tvm_client=tvm.TVMClient(
            service_name='test-service',
            secdist=test_taxi_app.secdist,
            config=config_,
            session=test_taxi_app.session,
        ),
        consumer='test',
    )
    return test_taxi_app


@pytest.mark.parametrize(
    'park_id,timestamp,expected_response',
    [(1, datetime.date(2019, 12, 31), {'billing_client_id': '12345678'})],
)
async def test_parks_replica_retrieve(
        test_app, patch, response_mock, park_id, timestamp, expected_response,
):
    @patch('aiohttp.ClientSession._request')
    async def _request(*args, **kwargs):
        return response_mock(text=json.dumps(expected_response))

    result = await test_app.parks_replica_client.retrieve(
        park_id=park_id, timestamp=timestamp,
    )
    assert result == expected_response
