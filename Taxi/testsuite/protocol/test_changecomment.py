import dateutil.parser
import pytest

from notify_on_change_version_switch import NOTIFY_ON_CHANGE_VERSION_SWITCH
from order_core_switch_parametrize import PROTOCOL_SWITCH_TO_ORDER_CORE
from validate_stq_task import validate_notify_on_change_stq_task
from validate_stq_task import validate_process_update_stq_task


@pytest.mark.now('2017-07-19T17:15:15+0000')
@PROTOCOL_SWITCH_TO_ORDER_CORE
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_changecomment_empty_changes(
        taxi_protocol,
        mockserver,
        mock_order_core,
        mock_stq_agent,
        load,
        db,
        now,
        order_core_switch_on,
        notify_on_change_version_switch,
):
    """Change comment with empty changes"""
    created_time = dateutil.parser.parse('2017-07-19T17:15:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': '8c83b49edb274ce0992f337061047375',
        'created_time': created_time.isoformat(),
        'comment': 'some comment',
    }
    query = {'_id': request['orderid']}
    version = db.order_proc.find_one(query)['order']['version']
    assert db.order_proc.find_one(query) is not None
    # there is no changes in order_proc
    assert 'changes' not in db.order_proc.find_one(query)
    assert now > db.order_proc.find_one(query)['updated']

    response = taxi_protocol.post('3.0/changecomment', request)
    assert response.status_code == 200
    assert mock_order_core.get_fields_times_called == order_core_switch_on
    assert mock_order_core.set_fields_times_called == order_core_switch_on
    args = [mock_stq_agent, request['orderid'], 'comment']
    validate_process_update_stq_task(
        *args, exists=notify_on_change_version_switch,
    )
    validate_notify_on_change_stq_task(
        *args, exists=not notify_on_change_version_switch,
    )
    data = response.json()

    # validate response according to protocol
    assert data == {
        'change_id': data['change_id'],
        'status': 'success',
        'name': 'comment',
        'value': request['comment'],
    }
    # validate order_proc table
    order_proc = db.order_proc.find_one(query)
    assert order_proc['processing']['need_start'] is False
    assert order_proc['order_info']['need_sync'] is False
    assert order_proc['order']['request']['comment'] == request['comment']
    assert order_proc['order']['version'] == version + 1

    # there should be 2 items in the 'objects', according to protocol
    # we need to create one fake item
    assert order_proc['changes']['objects'] == [
        {
            'id': order_proc['changes']['objects'][0]['id'],
            'vl': 'wait-1000',
            's': 'applied',
            'ci': request['id'],
            'n': 'comment',
            'vr': version + 1,
            'c': now.replace(tzinfo=None, microsecond=0),
            't': created_time.replace(tzinfo=None, microsecond=0),
            'si': {'s': 'delivered', 'c': 0},
        },
        {
            'id': order_proc['changes']['objects'][1]['id'],
            'vl': request['comment'],
            's': 'applying',
            'ci': request['id'],
            'n': 'comment',
            'vr': version + 1,
            'c': now.replace(tzinfo=None, microsecond=0),
            't': created_time.replace(tzinfo=None, microsecond=0),
            'si': {'s': 'init', 'c': 0},
        },
    ]


@pytest.mark.parametrize('use_order_core', [False, True])
@pytest.mark.now('2017-07-19T17:15:15+0000')
@PROTOCOL_SWITCH_TO_ORDER_CORE
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_changecomment(
        taxi_protocol,
        load,
        db,
        now,
        config,
        use_order_core,
        mock_order_core,
        mock_stq_agent,
        order_core_switch_on,
        notify_on_change_version_switch,
):
    if use_order_core:
        config.set_values(
            dict(PROCESSING_BACKEND_CPP_SWITCH=['change-comment']),
        )

    created_time = '2017-07-19T17:15:20+0000'
    """Basic change comment"""
    created_time = dateutil.parser.parse('2017-07-19T17:15:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': '8c83b49edb274ce0992f337061043333',
        'created_time': created_time.isoformat(),
        'comment': 'some comment',
    }
    query = {'_id': request['orderid']}
    version = db.order_proc.find_one(query)['order']['version']
    assert db.order_proc.find_one(query) is not None
    assert now > db.order_proc.find_one(query)['updated']

    response = taxi_protocol.post('3.0/changecomment', request)
    assert response.status_code == 200
    assert mock_order_core.get_fields_times_called == order_core_switch_on
    assert mock_order_core.set_fields_times_called == order_core_switch_on
    args = [mock_stq_agent, request['orderid'], 'comment']
    validate_process_update_stq_task(
        *args, exists=notify_on_change_version_switch,
    )
    validate_notify_on_change_stq_task(
        *args, exists=not notify_on_change_version_switch,
    )
    data = response.json()

    # validate response according to protocol
    assert data == {
        'change_id': data['change_id'],
        'status': 'success',
        'name': 'comment',
        'value': request['comment'],
    }
    # validate order_proc table
    order_proc = db.order_proc.find_one(query)
    assert order_proc['processing']['need_start'] is False
    assert order_proc['order_info']['need_sync'] is False
    assert order_proc['order']['request']['comment'] == request['comment']
    assert order_proc['order']['version'] == version + 1

    # 'objects' already has 2 items, we add a new item
    assert len(order_proc['changes']['objects']) == 3
    last_change = order_proc['changes']['objects'][2]
    assert last_change == {
        'id': order_proc['changes']['objects'][2]['id'],
        'vl': request['comment'],
        's': 'applying',
        'ci': request['id'],
        'n': 'comment',
        'vr': version + 1,
        'c': now.replace(tzinfo=None, microsecond=0),
        't': created_time.replace(tzinfo=None, microsecond=0),
        'si': {'s': 'init', 'c': 0},
    }
    assert mock_order_core.post_event_times_called == 0


@pytest.mark.parametrize(
    'created_time,expected_status,error_text',
    [
        (123, 400, 'Bad Request'),
        ('2013-03-13T08:57:22.123', 400, 'Bad Request'),
    ],
    ids=['created_time is not a string', 'wrong time format'],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_parse_created_time(
        taxi_protocol,
        load,
        created_time,
        expected_status,
        error_text,
        order_core_switch_on,
        notify_on_change_version_switch,
):
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': '123456789',
        'created_time': created_time,
        'comment': 'text comment',
    }
    response = taxi_protocol.post('3.0/changecomment', request)
    assert response.status_code == expected_status
    data = response.json()
    assert data['error']['text'] == error_text


@pytest.mark.parametrize(
    'orderid,expected_status,error_text',
    [
        ('8c83b49edb274ce0992f337061041111', 404, 'order is finished'),
        ('8c83b49edb274ce0992f337061040000', 404, 'order_proc not found'),
        ('8c83b49edb274ce0992f337061042222', 406, 'bad_status'),
        (
            '8c83b49edb274ce0992f337061043333',
            409,
            'last change time stamp > current change time stamp',
        ),
        (
            '8c83b49edb274ce0992f337061043333',
            409,
            'last change time stamp > current change time stamp',
        ),
    ],
    ids=[
        'order is finished',
        'order does not exist',
        'is not before transporting',
        'comment is already applied',
        'new time stamp less than old time stamp',
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_errors(
        taxi_protocol,
        load,
        orderid,
        expected_status,
        error_text,
        order_core_switch_on,
        notify_on_change_version_switch,
):
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': orderid,
        'created_time': '2017-07-19T17:00:00+0000',
        'comment': 'text comment',
    }
    response = taxi_protocol.post('3.0/changecomment', request)
    assert response.status_code == expected_status
    data = response.json()
    assert data['error']['text'] == error_text
