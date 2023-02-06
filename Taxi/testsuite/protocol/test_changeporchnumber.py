import dateutil.parser
import pytest

from notify_on_change_version_switch import NOTIFY_ON_CHANGE_VERSION_SWITCH
from order_core_switch_parametrize import PROTOCOL_SWITCH_TO_ORDER_CORE
from validate_stq_task import validate_notify_on_change_stq_task
from validate_stq_task import validate_process_update_stq_task


@pytest.mark.parametrize(
    'orderid,expected_porchnumber',
    [
        ('8c83b49edb274ce0992f337061047375', '4'),
        ('8c83b49edb274ce0992f337061049999', '3'),
    ],
    ids=['empty source.porchnumber', 'not empty source.porchnumber'],
)
@pytest.mark.now('2017-07-19T17:15:15+0000')
@PROTOCOL_SWITCH_TO_ORDER_CORE
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_changeporchnumber_empty_changes(
        taxi_protocol,
        mockserver,
        mock_stq_agent,
        mock_order_core,
        load,
        db,
        now,
        orderid,
        expected_porchnumber,
        order_core_switch_on,
        notify_on_change_version_switch,
):
    """Change porchnumber with empty order_proc.changes"""
    created_time = dateutil.parser.parse('2017-07-19T17:15:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': orderid,
        'created_time': created_time.isoformat(),
        'porchnumber': '4',
    }
    query = {'_id': request['orderid']}
    order_proc = db.order_proc.find_one(query)
    assert order_proc is not None
    version = order_proc['order']['version']
    # there is no changes in order_proc
    assert 'changes' not in order_proc
    assert now > order_proc['updated']

    response = taxi_protocol.post('3.0/changeporchnumber', request)
    assert response.status_code == 200
    assert mock_order_core.get_fields_times_called == order_core_switch_on
    assert mock_order_core.set_fields_times_called == order_core_switch_on
    data = response.json()

    args = [mock_stq_agent, request['orderid'], 'porchnumber']
    validate_process_update_stq_task(
        *args, exists=notify_on_change_version_switch,
    )
    validate_notify_on_change_stq_task(
        *args, exists=not notify_on_change_version_switch,
    )

    # validate response according to protocol
    assert data == {
        'change_id': data['change_id'],
        'status': 'success',
        'name': 'porchnumber',
        'value': request['porchnumber'],
    }
    # validate order_proc table
    order_proc = db.order_proc.find_one(query)
    assert order_proc['processing']['need_start'] is False
    assert order_proc['order_info']['need_sync'] is False
    assert order_proc['order']['request']['source']['porchnumber'] == (
        request['porchnumber']
    )
    assert order_proc['order']['version'] == version + 1

    # there should be 2 items in the 'objects', according to protocol
    # we need to create one fake item
    expected_changes = [
        {
            'id': order_proc['changes']['objects'][0]['id'],
            'vl': expected_porchnumber,
            's': 'applied',
            'ci': request['id'],
            'n': 'porchnumber',
            'vr': version + 1,
            'c': now.replace(tzinfo=None, microsecond=0),
            't': created_time.replace(tzinfo=None, microsecond=0),
            'si': {'s': 'delivered', 'c': 0},
        },
        {
            'id': order_proc['changes']['objects'][1]['id'],
            'vl': request['porchnumber'],
            's': 'applying',
            'ci': request['id'],
            'n': 'porchnumber',
            'vr': version + 1,
            'c': now.replace(tzinfo=None, microsecond=0),
            't': created_time.replace(tzinfo=None, microsecond=0),
            'si': {'s': 'init', 'c': 0},
        },
    ]
    assert order_proc['changes']['objects'] == expected_changes


@pytest.mark.parametrize('use_order_core', [False, True])
@pytest.mark.now('2017-07-19T17:15:15+0000')
@PROTOCOL_SWITCH_TO_ORDER_CORE
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_changeporchnumber(
        taxi_protocol,
        load,
        db,
        now,
        mock_stq_agent,
        mock_order_core,
        use_order_core,
        config,
        order_core_switch_on,
        notify_on_change_version_switch,
):
    if use_order_core:
        config.set_values(
            dict(PROCESSING_BACKEND_CPP_SWITCH=['change-porchnumber']),
        )

    """Basic change porchnumber"""
    created_time = '2017-07-19T17:15:20+0000'
    created_time = dateutil.parser.parse('2017-07-19T17:15:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': '8c83b49edb274ce0992f337061043333',
        'created_time': created_time.isoformat(),
        'porchnumber': '4',
    }
    query = {'_id': request['orderid']}
    order_proc = db.order_proc.find_one(query)
    assert order_proc is not None
    version = order_proc['order']['version']
    assert now > order_proc['updated']

    response = taxi_protocol.post('3.0/changeporchnumber', request)
    assert response.status_code == 200
    assert mock_order_core.get_fields_times_called == order_core_switch_on
    assert mock_order_core.set_fields_times_called == order_core_switch_on
    data = response.json()

    args = [mock_stq_agent, request['orderid'], 'porchnumber']
    validate_process_update_stq_task(
        *args, exists=notify_on_change_version_switch,
    )
    validate_notify_on_change_stq_task(
        *args, exists=not notify_on_change_version_switch,
    )

    # validate response according to protocol
    assert data == {
        'change_id': data['change_id'],
        'status': 'success',
        'name': 'porchnumber',
        'value': request['porchnumber'],
    }
    # validate order_proc table
    order_proc = db.order_proc.find_one(query)
    assert order_proc['processing']['need_start'] is False
    assert order_proc['order_info']['need_sync'] is False
    assert order_proc['order']['request']['source']['porchnumber'] == (
        request['porchnumber']
    )
    assert order_proc['order']['version'] == version + 1

    # 'objects' already has 2 items, we add a new item
    assert len(order_proc['changes']['objects']) == 3
    last_change = order_proc['changes']['objects'][2]
    expected_last_change = {
        'id': order_proc['changes']['objects'][2]['id'],
        'vl': request['porchnumber'],
        's': 'applying',
        'ci': request['id'],
        'n': 'porchnumber',
        'vr': version + 1,
        'c': now.replace(tzinfo=None, microsecond=0),
        't': created_time.replace(tzinfo=None, microsecond=0),
        'si': {'s': 'init', 'c': 0},
    }
    assert last_change == expected_last_change
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
        'porchnumber': '4',
    }
    response = taxi_protocol.post('3.0/changeporchnumber', request)
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
        'porchnumber is already applied',
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
        'porchnumber': '4',
    }
    response = taxi_protocol.post('3.0/changeporchnumber', request)
    assert response.status_code == expected_status
    data = response.json()
    assert data['error']['text'] == error_text
