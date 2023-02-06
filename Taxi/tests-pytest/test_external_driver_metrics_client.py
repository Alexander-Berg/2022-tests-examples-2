import bson.json_util
import pytest
import logging

from taxi.core import arequests
from taxi.core import async
from taxi.conf import settings
from taxi.external import driver_metrics_client as dms


if settings.YT_CONFIG_ENV_PREFIX == 'development':
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())


TST_DRIVER_ACTIVITY_RESPONSE = {
    'activity': 90,
}
TST_ORDER_ID = 'tst_order_id'
TST_UDID = '5b05621ee6c22ea2654849c7'
TST_HISTORY_RESPONSE = {
    'id': '5b7b0c694f007eaf8578b531',
    'activity_value_change': -14,
    'activity_value_before': 100,
    'timestamp': '2018-08-21T08:50:36.230000Z',
    'driver_id': '999010_2eaf04fe6dec4330a6f29a6a7701c459',
    'db_id': '',
    'time_to_a': 300,
    'distance_to_a': 1000,
    'order_id': '1',
    'order_alias_id': 'alias_1',
    'zone': 'moscow',
    'event_type': 'order',
    'event_descriptor': {
        'name': 'auto_reorder',
        'tags': None
    },
}


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('mock_response', [
    200,
])
@pytest.inline_callbacks
def test_driver_activity_value(patch, mock_response):

    @patch('taxi.core.arequests.request')
    @async.inline_callbacks
    def request(method, url, **kwargs):
        if isinstance(mock_response, int):
            response = arequests.Response(
                status_code=mock_response,
                content=bson.json_util.dumps(TST_DRIVER_ACTIVITY_RESPONSE))
            yield async.return_value(response)
        else:
            raise mock_response('msg')

    res = yield dms.driver_activity_value(
        'lookup',
        'lookup',
        TST_UDID,
    )
    assert len(request.calls) == 1
    if mock_response != 200:
        assert not res
    else:
        assert res


@pytest.mark.config(
    TVM_ENABLED=False
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('mock_response', [
    200,
    500,
    400,
    arequests.TimeoutError,
])
@pytest.inline_callbacks
def test_history(patch, mock_response):

    @patch('taxi.core.arequests.request')
    @async.inline_callbacks
    def request(method, url, **kwargs):
        if isinstance(mock_response, int):
            response = arequests.Response(
                status_code=mock_response,
                content=bson.json_util.dumps({
                    'items': [TST_HISTORY_RESPONSE]
                }))
            yield async.return_value(response)
        else:
            raise mock_response('msg')

    res = yield dms.activity_history(
        'processing',
        TST_UDID,
        TST_ORDER_ID,
    )
    assert len(request.calls) == 1
    if mock_response != 200:
        assert not res
    else:
        assert res
