import datetime
import functools

import pytest

from taxi import discovery
import taxi.clients.rider_metrics_storage as rms


TST_EVENT_TYPE = 'tst_event_type'
TST_TIMESTAMP = datetime.datetime.utcnow()
TST_USER_ID = '0340020304010300430'
TST_TOKEN = 'unique_token'
TST_ORDER_ID = 'order_id'
TST_EVENT_DESCRIPTOR = {'name': 'event_name', 'tags': ['event_tags']}

RMS_URL = discovery.find_service('rider_metrics_storage').url


@pytest.fixture
def rms_client(test_taxi_app):
    return rms.RiderMetricsStorageClient(
        test_taxi_app.session,
        test_taxi_app.config,
        'test_service',
        test_taxi_app.tvm,
    )


def mark_default_config(func):
    @functools.wraps(func)
    @pytest.mark.config(
        RIDER_METRICS_STORAGE_CLIENT_SETTINGS={
            '__default__': {
                '__default__': {
                    'num_retries': 0,
                    'retry_delay_ms': [50],
                    'request_timeout_ms': 250,
                },
            },
        },
    )
    async def _wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    return _wrapper


@mark_default_config
async def test_new_event(
        rms_client, patch_aiohttp_session, response_mock,
):  # noqa pylint: disable=redefined-outer-name
    @patch_aiohttp_session(RMS_URL, 'POST')
    def _patch_request(*args, **kwargs):
        data = kwargs['json']
        assert data['idempotency_token'] == TST_TOKEN
        assert data['user_id'] == TST_USER_ID
        assert 'eid' not in data
        assert len(data) == 6
        return response_mock(json={})

    await rms_client.new_event(
        idempotency_token=TST_TOKEN,
        event_type=TST_EVENT_TYPE,
        user_id=TST_USER_ID,
        created=TST_TIMESTAMP,
        descriptor=TST_EVENT_DESCRIPTOR,
        order_id=TST_ORDER_ID,
    )

    assert _patch_request.calls
