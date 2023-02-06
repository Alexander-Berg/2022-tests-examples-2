# pylint: disable=protected-access
# pylint: disable=redefined-outer-name
import datetime
import functools

import pytest

from taxi import discovery
import taxi.clients.driver_metrics_storage as dms
from taxi.clients.helpers import base as api_utils


TST_TIMESTAMP = datetime.datetime.utcnow()
TST_UDID = '0340020304010300430'
TST_ORDER_ALIAS_ID = 'unique_alias'
TST_ORDER_ID = 'order_id'
TST_DBID_UUID = '0203212s032_32c342fg3d3'

DMS_URL = discovery.find_service('driver_metrics_storage').url


@pytest.fixture
def dms_client(test_taxi_app):
    return dms.DriverMetricsStorageClient(
        test_taxi_app.session,
        test_taxi_app.config,
        'test_service',
        test_taxi_app.tvm,
    )


def mark_default_config(func):
    @functools.wraps(func)
    @pytest.mark.config(
        DRIVER_METRICS_STORAGE_CLIENT_SETTINGS={
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


@pytest.mark.config(
    DRIVER_METRICS_STORAGE_CLIENT_SETTINGS={
        '__default__': {
            '__default__': {
                'num_retries': 0,
                'retry_delay_ms': [50],
                'request_timeout_ms': 250,
            },
            'v1/wallet/accrual': {
                'num_retries': 2,
                'retry_delay_ms': [5, 7],
                'request_timeout_ms': 10,
            },
        },
        'test_service': {
            'v1/wallet/accrual': {
                'num_retries': 3,
                'retry_delay_ms': [5, 7],
                'request_timeout_ms': 10,
            },
        },
        'wallet': {
            '__default__': {
                'num_retries': 3,
                'retry_delay_ms': [5, 7],
                'request_timeout_ms': 10,
            },
        },
    },
)
def test_config(test_taxi_app, dms_client):

    res = dms_client._settings.get_request_params('wrong_one')
    assert res.num_retries == 0
    assert res.retry_delay_ms == [50]
    assert res.request_timeout_ms == 250

    res = dms_client._settings.get_request_params('v1/wallet/accrual')
    assert res.num_retries == 3
    assert res.retry_delay_ms == [5, 7]
    assert res.request_timeout_ms == 10

    dms_client = dms.DriverMetricsStorageClient(
        test_taxi_app.session,
        test_taxi_app.config,
        'wallet',
        test_taxi_app.tvm,
    )

    res = dms_client._settings.get_request_params('missing')
    assert res.num_retries == 3
    assert res.retry_delay_ms == [5, 7]
    assert res.request_timeout_ms == 10

    dms_client = dms.DriverMetricsStorageClient(
        test_taxi_app.session, test_taxi_app.config, '====', test_taxi_app.tvm,
    )

    res = dms_client._settings.get_request_params('v1/wallet/accrual')
    assert res.num_retries == 2
    assert res.retry_delay_ms == [5, 7]
    assert res.request_timeout_ms == 10

    assert dms_client._settings.fetch_delay(res.retry_delay_ms, 0) == 50
    assert dms_client._settings.fetch_delay(res.retry_delay_ms, 1) == 5
    assert dms_client._settings.fetch_delay(res.retry_delay_ms, 2) == 7
    assert dms_client._settings.fetch_delay(res.retry_delay_ms, 12) == 7


@pytest.mark.parametrize('with_additional_info', [True, False])
@mark_default_config
async def test_events_processed(
        dms_client, patch_aiohttp_session, response_mock, with_additional_info,
):
    @patch_aiohttp_session(DMS_URL, 'POST')
    def _patch_request(*args, **kwargs):
        data = kwargs['json']
        assert data.get('unique_driver_id') is not None
        events = [
            {
                'event': {
                    'event_id': 4,
                    'type': 'reposition',
                    'order_id': TST_ORDER_ID,
                    'order_alias': TST_ORDER_ALIAS_ID,
                    'park_driver_profile_id': TST_DBID_UUID,
                    'tariff_zone': 'bangladesh',
                    'extra_data': {
                        'descriptor': {'type': 'cancel', 'tags': []},
                    },
                    'datetime': api_utils.time_to_iso_string_or_none(
                        TST_TIMESTAMP,
                    ),
                },
                'reason': 'no reason',
            },
        ]
        if data['with_additional_info']:
            events[0].update({'activity_change': 3, 'loyalty_change': 1})
        return response_mock(json={'events': events})

    res = await dms_client.processed_events_v3(
        udid=TST_UDID,
        dbid_uuid=TST_DBID_UUID,
        timestamp_from=TST_TIMESTAMP,
        timestamp_to=TST_TIMESTAMP,
        with_additional_info=with_additional_info,
        order_ids=[],
    )

    assert _patch_request.calls
    assert len(res) == 1
    item = res[0]
    if with_additional_info:
        assert item.loyalty_change == 1
        assert item.activity_change == 3
    else:
        assert getattr(item, 'loyalty_change', 1) == 0
        assert getattr(item, 'activity_change', 3) == 0
    assert item.event.type == 'reposition'
    assert item.event.dbid_uuid == TST_DBID_UUID
