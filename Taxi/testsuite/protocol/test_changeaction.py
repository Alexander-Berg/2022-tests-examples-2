import dateutil.parser
import pytest

from notify_on_change_version_switch import NOTIFY_ON_CHANGE_VERSION_SWITCH
from order_core_switch_parametrize import PROTOCOL_SWITCH_TO_ORDER_CORE
from validate_stq_task import validate_notify_on_change_stq_task
from validate_stq_task import validate_process_update_stq_task


@pytest.mark.parametrize(
    'orderid, code, error_text',
    [
        ('8c83b49edb274ce0992f337061041111', 404, 'order is finished'),
        (
            '8c83b49edb274ce0992f337061043333',
            409,
            'last change time stamp > current change time stamp',
        ),
        ('8c83b49edb274ce0992f337061042222', 406, 'bad_status'),
        (
            '8c83b49edb274ce0992f337061044444',
            409,
            'cannot commit processing state',
        ),
        ('00000000000000000000000000000000', 404, 'order_proc not found'),
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_return_code(
        db,
        testpoint,
        mock_order_core,
        orderid,
        code,
        taxi_protocol,
        order_core_switch_on,
        error_text,
):
    @testpoint('ChangeactionIncreaseOrderVersion')
    def increase_order_version(query):
        if query['_id'] == '8c83b49edb274ce0992f337061044444':
            query['_shard_id'] = 0
            db.order_proc.find_and_modify(
                query, {'$inc': {'order.version': 1}},
            )

    isocreated_time = dateutil.parser.parse('2017-07-19T13:16:04Z')
    body = {
        'orderid': orderid,
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'action': 'user_ready',
        'created_time': isocreated_time.isoformat(),
    }
    response = taxi_protocol.post('3.0/changeaction', json=body)
    assert response.status_code == code
    data = response.json()
    assert data['error']['text'] == error_text

    if orderid == '8c83b49edb274ce0992f337061044444':
        assert increase_order_version.times_called == 3
        assert (
            mock_order_core.get_fields_times_called == order_core_switch_on * 3
        )
        assert (
            mock_order_core.set_fields_times_called == order_core_switch_on * 3
        )
    else:
        assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.now('2017-07-19T17:15:15+0000')
@PROTOCOL_SWITCH_TO_ORDER_CORE
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_empty_change(
        taxi_protocol,
        mockserver,
        mock_order_core,
        mock_stq_agent,
        db,
        now,
        order_core_switch_on,
        notify_on_change_version_switch,
):
    order_id = '8c83b49edb274ce0992f337061047375'
    created_time = dateutil.parser.parse('2017-07-19T17:15:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': order_id,
        'created_time': created_time.isoformat(),
        'action': 'user_ready',
    }
    query = {'_id': order_id}
    proc = db.order_proc.find_one(query)
    assert proc is not None
    version = proc['order']['version']
    assert 'changes' not in proc
    assert now > proc['updated']
    response = taxi_protocol.post('3.0/changeaction', request)
    assert response.status_code == 200
    assert mock_order_core.get_fields_times_called == order_core_switch_on
    assert mock_order_core.set_fields_times_called == order_core_switch_on
    args = [mock_stq_agent, request['orderid'], 'user_ready']
    validate_process_update_stq_task(
        *args, exists=notify_on_change_version_switch,
    )
    validate_notify_on_change_stq_task(
        *args, exists=not notify_on_change_version_switch,
    )
    data = response.json()
    assert data == {
        'change_id': data['change_id'],
        'status': 'success',
        'name': 'user_ready',
        'value': True,
    }
    order_proc = db.order_proc.find_one(query)
    assert order_proc['processing']['need_start'] is False
    assert order_proc['order_info']['need_sync'] is False
    assert order_proc['order']['user_ready'] is True
    assert order_proc['order']['version'] == version + 1
    assert len(order_proc['changes']['objects']) == 2
    assert order_proc['changes']['objects'] == [
        {
            'id': order_proc['changes']['objects'][0]['id'],
            'vl': False,
            's': 'applied',
            'ci': request['id'],
            'n': 'user_ready',
            'vr': version + 1,
            'c': now.replace(tzinfo=None, microsecond=0),
            't': created_time.replace(tzinfo=None, microsecond=0),
            'si': {'s': 'delivered', 'c': 0},
        },
        {
            'id': order_proc['changes']['objects'][1]['id'],
            'vl': True,
            's': 'applying',
            'ci': request['id'],
            'n': 'user_ready',
            'vr': version + 1,
            'c': now.replace(tzinfo=None, microsecond=0),
            't': created_time.replace(tzinfo=None, microsecond=0),
            'si': {'s': 'init', 'c': 0},
        },
    ]


@pytest.mark.now('2017-07-19T17:15:15+0000')
@PROTOCOL_SWITCH_TO_ORDER_CORE
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_change_user_ready(
        taxi_protocol,
        mockserver,
        mock_order_core,
        mock_stq_agent,
        db,
        now,
        order_core_switch_on,
        notify_on_change_version_switch,
):
    order_id = '8c83b49edb274ce0992f337061043333'
    created_time = dateutil.parser.parse('2017-07-19T17:15:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': order_id,
        'created_time': created_time.isoformat(),
        'action': 'user_ready',
    }
    query = {'_id': order_id}
    proc = db.order_proc.find_one(query)
    version = proc['order']['version']
    assert proc is not None
    assert now > proc['updated']
    response = taxi_protocol.post('3.0/changeaction', request)
    assert response.status_code == 200
    assert mock_order_core.get_fields_times_called == order_core_switch_on
    assert mock_order_core.set_fields_times_called == order_core_switch_on
    args = [mock_stq_agent, request['orderid'], 'user_ready']
    validate_process_update_stq_task(
        *args, exists=notify_on_change_version_switch,
    )
    validate_notify_on_change_stq_task(
        *args, exists=not notify_on_change_version_switch,
    )
    data = response.json()
    assert data == {
        'change_id': data['change_id'],
        'status': 'success',
        'name': 'user_ready',
        'value': True,
    }
    order_proc = db.order_proc.find_one(query)
    assert order_proc['processing']['need_start'] is False
    assert order_proc['order_info']['need_sync'] is False
    assert order_proc['order']['user_ready'] is True
    assert order_proc['order']['version'] == version + 1
    assert len(order_proc['changes']['objects']) == 3
    assert order_proc['changes']['objects'][2] == {
        'id': order_proc['changes']['objects'][2]['id'],
        'vl': True,
        's': 'applying',
        'ci': request['id'],
        'n': 'user_ready',
        'vr': version + 1,
        'c': now.replace(tzinfo=None, microsecond=0),
        't': created_time.replace(tzinfo=None, microsecond=0),
        'si': {'s': 'init', 'c': 0},
    }


@pytest.mark.now('2017-07-19T17:15:15+0000')
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_wrong_action(
        taxi_protocol, mockserver, db, now, notify_on_change_version_switch,
):
    created_time = dateutil.parser.parse('2017-07-19T17:15:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': '8c83b49edb274ce0992f337061043333',
        'created_time': created_time.isoformat(),
        'action': 'action_not_user_ready',
    }
    response = taxi_protocol.post('3.0/changeaction', request)
    assert response.status_code == 400
