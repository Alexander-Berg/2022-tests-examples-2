import datetime

import bson.json_util
import pytest
import pytz

from replica_dbusers_switch_parametrize import (
    PROTOCOL_SWITCH_TO_REPLICA_DBUSERS,
)


def _transform_datetime(o):
    if isinstance(o, list):
        for idx in range(len(o)):
            o[idx] = _transform_datetime(o[idx])
    elif isinstance(o, dict):
        for k, v in o.items():
            o[k] = _transform_datetime(v)
    elif isinstance(o, datetime.datetime):
        return o.replace(tzinfo=pytz.UTC)
    return o


def load_json(path, load):
    r = bson.json_util.loads(load(path))
    _transform_datetime(r)
    return r


@pytest.mark.parametrize(
    'order_core_times_called',
    [
        pytest.param(0),
        pytest.param(
            1,
            marks=[
                pytest.mark.config(PROCESSING_BACKEND_CPP_SWITCH=['reorder']),
            ],
        ),
    ],
)
@PROTOCOL_SWITCH_TO_REPLICA_DBUSERS
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_reorder_basic(
        taxi_protocol,
        db,
        load,
        order_core_times_called,
        mock_order_core,
        testpoint,
        read_from_replica_dbusers,
):
    @testpoint('orderkit::GetUserById')
    def replica_dbusers_test_point(data):
        assert read_from_replica_dbusers == data['replica']

    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': 'd7072aed6f234fbe817d84354630ab95',
        'decision_id': '2b8bb60e76fc4efa96ae48729acb1674',
    }
    response = taxi_protocol.post('3.0/reorder', request)
    assert response.status_code == 200

    response_json = response.json()
    assert response_json['status'] == 'search'

    actual_order_proc = db.order_proc.find_one(
        {'_id': 'd7072aed6f234fbe817d84354630ab95'},
    )
    _transform_datetime(actual_order_proc)
    expected_order_proc = load_json('expected_orderproc.json', load)
    assert 'updated' in expected_order_proc
    del actual_order_proc['updated']
    del expected_order_proc['updated']
    assert actual_order_proc == expected_order_proc
    assert mock_order_core.post_event_times_called == order_core_times_called
    assert replica_dbusers_test_point.times_called == 1


@pytest.mark.parametrize(
    'order_core_times_called',
    [
        pytest.param(0),
        pytest.param(
            0,
            marks=[
                pytest.mark.config(PROCESSING_BACKEND_CPP_SWITCH=['reorder']),
            ],
        ),
    ],
)
def test_no_order(taxi_protocol, mock_order_core, order_core_times_called):
    # TODO Not found
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': 'not_found',
        'decision_id': 'decision_id',
    }
    response = taxi_protocol.post('3.0/reorder', request)
    assert response.status_code == 404
    assert mock_order_core.post_event_times_called == order_core_times_called


@pytest.mark.parametrize(
    'order_core_times_called',
    [
        pytest.param(0),
        pytest.param(
            0,
            marks=[
                pytest.mark.config(PROCESSING_BACKEND_CPP_SWITCH=['reorder']),
            ],
        ),
    ],
)
def test_driver_not_found(
        taxi_protocol, mock_order_core, order_core_times_called,
):
    # TODO in assigned status
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': 'assigned',
        'decision_id': 'decision_id',
    }
    response = taxi_protocol.post('3.0/reorder', request)
    assert response.status_code == 404
    assert mock_order_core.post_event_times_called == order_core_times_called
