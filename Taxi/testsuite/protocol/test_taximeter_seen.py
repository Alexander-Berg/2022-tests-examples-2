import datetime

import pytest

from order_core_switch_parametrize import PROTOCOL_SWITCH_TO_ORDER_CORE


DEFAULT_PARK_ID = '999011'
DEFAULT_API_KEY = '990eba5480384a608f5d586a8358b71a'


@pytest.mark.now('2018-06-20T10:30:00+0300')
@pytest.mark.driver_experiments('bad_position_reject')
@pytest.mark.parametrize(
    'bpq_enable,driver_id,percent,reject_reason, use_order_core',
    [
        (False, 'bad_id', 100, None, False),
        (True, 'bad_id', 0, None, False),
        (True, 'gud_id', 100, None, False),
        (True, 'old_id', 100, None, False),
        (True, 'bad_id', 101, 'bad_position', False),
        (True, 'not_id', 100, 'Gone', False),
        (True, 'not_id', 100, 'Gone', True),
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
@pytest.mark.config(SEEN_REJECT_RESTART_PROCESSING_DISABLED=True)
def test_taximeter_seen_bpq(
        taxi_protocol,
        config,
        bpq_enable,
        driver_id,
        percent,
        reject_reason,
        use_order_core,
        now,
        mock_order_core,
        order_core_switch_on,
):
    if use_order_core:
        config.set_values(
            dict(PROCESSING_BACKEND_CPP_SWITCH=['taxi-seen-reject']),
        )
    config.set_values(dict(BPQ_ENABLE=bpq_enable, BPQ_REJECT_PERCENT=percent))
    taxi_protocol.tests_control(now=now)
    response = taxi_protocol.post(
        '/1.x/seen',
        params={
            'uuid': driver_id,
            'orderid': ('b49cb5b99c0b41dba1a8393b3_%s' % driver_id),
            'reason': 'shown',
            'clid': DEFAULT_PARK_ID,
            'apikey': DEFAULT_API_KEY,
        },
    )
    if reject_reason is not None:
        assert response.status_code == 410
        assert response.json() == {'error': {'text': reject_reason}}
    else:
        assert response.status_code == 200
        assert response.content.decode() == ''

    if order_core_switch_on:
        expected_calls = int(reject_reason is None) + 1
        assert mock_order_core.get_fields_times_called == expected_calls
    else:
        assert mock_order_core.get_fields_times_called == 0


@pytest.mark.now('2018-06-20T10:30:00+0300')
@pytest.mark.parametrize(
    'seen_received_enabled',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.config(SEEN_RECEIVED_EVENT_ENABLED=True)],
        ),
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
@pytest.mark.config(SEEN_REJECT_RESTART_PROCESSING_DISABLED=True)
def test_seen_received(
        taxi_protocol,
        db,
        seen_received_enabled,
        mock_order_core,
        order_core_switch_on,
):
    driver_id = 'gud_id'
    response = taxi_protocol.post(
        '/1.x/seen',
        params={
            'uuid': driver_id,
            'orderid': f'b49cb5b99c0b41dba1a8393b3_{driver_id}',
            'reason': 'received',
            'clid': DEFAULT_PARK_ID,
            'apikey': DEFAULT_API_KEY,
        },
    )
    assert response.status_code == 200
    assert response.content == b''

    order = db.order_proc.find_one({'_id': '8a3eb6ba7fce4b17ac14cee0e3ab232b'})
    if seen_received_enabled:
        assert order['order_info']['statistics']['status_updates'] == [
            {
                'c': datetime.datetime(2018, 6, 20, 7, 30),
                'h': True,
                'q': 'seen_received',
                'i': 0,
            },
        ]
    else:
        assert 'statistics' not in order['order_info']
    assert mock_order_core.get_fields_times_called == int(order_core_switch_on)
