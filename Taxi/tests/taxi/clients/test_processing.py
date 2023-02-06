# pylint: disable=protected-access, redefined-outer-name
import pytest

from taxi import config
from taxi import discovery
from taxi.clients import processing
from taxi.clients import tvm

EXAMPLE_DATA = {
    'entries': [
        {
            'account': {
                'agreement_id': 'taxi/yandex_ride',
                'currency': 'RUB',
                'entity_external_id': 'taximeter_driver_id/7f74df/1086f4',
                'sub_account': 'promocode/compensation',
            },
            'amount': '-50.0',
            'created': '2019-09-13T13:01:00.000000+00:00',
            'details': {
                'alias_id': '300226c453c54b099f3f5aa64fbc1ac4',
                'reverse_entry_id': 11,
            },
            'doc_ref': None,
            'entry_id': 12,
            'event_at': '2019-09-13T13:00:00.000000+00:00',
        },
        {
            'account': {
                'agreement_id': 'taxi/yandex_ride',
                'currency': 'RUB',
                'entity_external_id': 'taximeter_driver_id/7f74df/1086f4',
                'sub_account': 'promocode/compensation',
            },
            'amount': '100.0',
            'created': '2019-09-13T13:01:00.000000+00:00',
            'details': {'alias_id': '300226c453c54b099f3f5aa64fbc1ac4'},
            'doc_ref': None,
            'entry_id': 13,
            'event_at': '2019-09-13T13:00:00.000000+00:00',
        },
    ],
}


@pytest.fixture
async def test_app(test_taxi_app):
    class Config(config.Config):
        PROCESSING_CLIENT_QOS = {
            '__default__': {'attempts': 1, 'timeout-ms': 1000},
        }

    config_ = Config()
    service = discovery.find_service('processing')
    test_taxi_app.processing_client = processing.ProcessingApiClient(
        session=test_taxi_app.session,
        service=service,
        tvm_client=tvm.TVMClient(
            service_name='test-service',
            secdist=test_taxi_app.secdist,
            config=config_,
            session=test_taxi_app.session,
        ),
        config=config_,
    )
    return test_taxi_app


@pytest.mark.parametrize(
    'item_id,scope,queue,data,expected_response',
    [
        (
            '123',
            'pro',
            'contractors_income',
            EXAMPLE_DATA,
            {'event_id': 'f47b5d12fb2f40c684b4365f65684728'},
        ),
    ],
)
async def test_processing_client(
        test_app,
        patch,
        response_mock,
        item_id,
        scope,
        queue,
        data,
        expected_response,
):
    @patch('aiohttp.ClientSession._request')
    async def _request(*args, **kwargs):
        return response_mock(json=expected_response)

    result = await test_app.processing_client.v1_scope_queue_create_event(
        item_id=item_id,
        x_idempotency_token=item_id,
        scope=scope,
        queue=queue,
        data=data,
    )
    assert result == expected_response
