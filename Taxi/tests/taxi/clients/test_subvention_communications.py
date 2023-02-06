import pytest

from taxi.clients import subvention_communications
from taxi.clients import tvm


@pytest.fixture(name='test_app')
async def make_test_app(test_taxi_app):
    config_ = test_taxi_app.config
    setattr(
        config_,
        'SUBVENTION_COMMUNICATIONS_CLIENT_QOS',
        {'__default__': {'attempts': 3, 'timeout-ms': 200}},
    )
    test_taxi_app.subvention_communications_client = (
        subvention_communications.Client(
            session=test_taxi_app.session,
            config=config_,
            tvm_client=tvm.TVMClient(
                service_name='test-service',
                secdist=test_taxi_app.secdist,
                config=config_,
                session=test_taxi_app.session,
            ),
        )
    )
    return test_taxi_app


async def test_v1_driver_fix(test_app, patch, response_mock):
    @patch('aiohttp.ClientSession._request')
    async def _request(*args, **kwargs):
        return response_mock(text='{}')

    client: subvention_communications.Client = (
        test_app.subvention_communications_client
    )
    await client.v1_driver_fix_block(
        subvention_communications.V1DriverFixBlockRequest(
            driver_info=subvention_communications.DriverInfo(
                'park_id', 'profile_id',
            ),
            idempotency_token='idempotency_token',
        ),
    )
    await client.v1_driver_fix_pay(
        subvention_communications.V1DriverFixPayRequest(
            doc_id=6,
            driver_info=subvention_communications.DriverInfo(
                'park_id', 'profile_id',
            ),
            idempotency_token='idempotency_token',
        ),
    )
