import dateutil.parser
import pytest

from notify_on_change_version_switch import NOTIFY_ON_CHANGE_VERSION_SWITCH
from order_core_switch_parametrize import PROTOCOL_SWITCH_TO_ORDER_CORE
from validate_stq_task import validate_notify_on_change_stq_task
from validate_stq_task import validate_process_update_stq_task


@pytest.mark.parametrize('use_order_core', [False, True])
@pytest.mark.parametrize('client_geo_sharing_enabled', [True, False])
@pytest.mark.now('2017-07-19T17:15:15+0000')
@PROTOCOL_SWITCH_TO_ORDER_CORE
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_changeclientgeosharing(
        taxi_protocol,
        client_geo_sharing_enabled,
        db,
        now,
        config,
        use_order_core,
        mock_order_core,
        mock_stq_agent,
        order_core_switch_on,
        notify_on_change_version_switch,
):
    """Change comment with empty changes"""
    if use_order_core:
        config.set_values(
            dict(PROCESSING_BACKEND_CPP_SWITCH=['change-clientgeosharing']),
        )

    created_time = dateutil.parser.parse('2017-07-19T17:15:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': '8c83b49edb274ce0992f337061047375',
        'created_time': created_time.isoformat(),
        'client_geo_sharing_enabled': client_geo_sharing_enabled,
    }
    query = {'_id': request['orderid']}
    version = db.order_proc.find_one(query)['order']['version']
    assert db.order_proc.find_one(query) is not None
    # there is no changes in order_proc
    assert 'changes' not in db.order_proc.find_one(query)
    assert now > db.order_proc.find_one(query)['updated']

    response = taxi_protocol.post('3.0/changeclientgeosharing', request)
    assert response.status_code == 200
    assert mock_order_core.get_fields_times_called == order_core_switch_on
    assert mock_order_core.set_fields_times_called == order_core_switch_on
    args = [mock_stq_agent, request['orderid'], 'client_geo_sharing']
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
        'name': 'client_geo_sharing',
        'value': request['client_geo_sharing_enabled'],
    }
    # validate order_proc table
    order_proc = db.order_proc.find_one(query)
    assert order_proc['processing']['need_start'] is False
    assert order_proc['order_info']['need_sync'] is False
    assert order_proc['order']['client_geo_sharing_enabled'] == (
        request['client_geo_sharing_enabled']
    )
    assert order_proc['order']['version'] == version + 1

    # there should be 2 items in the 'objects', according to protocol
    # we need to create one fake item
    assert order_proc['changes']['objects'] == [
        {
            'id': order_proc['changes']['objects'][0]['id'],
            'vl': False,
            's': 'applied',
            'ci': request['id'],
            'n': 'client_geo_sharing',
            'vr': version + 1,
            'c': now.replace(tzinfo=None, microsecond=0),
            't': created_time.replace(tzinfo=None, microsecond=0),
            'si': {'s': 'delivered', 'c': 0},
        },
        {
            'id': order_proc['changes']['objects'][1]['id'],
            'vl': request['client_geo_sharing_enabled'],
            's': 'applying',
            'ci': request['id'],
            'n': 'client_geo_sharing',
            'vr': version + 1,
            'c': now.replace(tzinfo=None, microsecond=0),
            't': created_time.replace(tzinfo=None, microsecond=0),
            'si': {'s': 'init', 'c': 0},
        },
    ]
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
def test_changeclientgeosharing_parse_created_time(
        taxi_protocol,
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
        'client_geo_sharing_enabled': False,
    }
    response = taxi_protocol.post('3.0/changeclientgeosharing', request)
    assert response.status_code == expected_status
    data = response.json()
    assert data['error']['text'] == error_text


@pytest.mark.parametrize(
    'orderid,expected_status,error_text',
    [
        ('8c83b49edb274ce0992f337061041111', 404, 'order is finished'),
        ('8c83b49edb274ce0992f337061040000', 404, 'order_proc not found'),
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
        'dont_call is already applied',
        'new time stamp less than old time stamp',
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_changeclientgeosharing_errors(
        taxi_protocol,
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
        'client_geo_sharing_enabled': False,
    }
    response = taxi_protocol.post('3.0/changeclientgeosharing', request)
    assert response.status_code == expected_status
    data = response.json()
    assert data['error']['text'] == error_text


@pytest.mark.parametrize(
    'order_id',
    [
        '8c83b49edb274ce0992f337061047375',
        '8c83b49edb274ce0992f337061043333',
        '8c83b49edb274ce0992f337061044444',
    ],
)
@pytest.mark.parametrize('new_client_geo_sharing', [True, False])
@pytest.mark.parametrize('not_update_same_value', [True, False])
@pytest.mark.now('2017-07-19T17:15:20+0000')
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_changeclientgeosharing_update_same_value(
        taxi_protocol,
        order_id,
        new_client_geo_sharing,
        not_update_same_value,
        now,
        db,
        config,
        mock_order_core,
        mock_stq_agent,
        notify_on_change_version_switch,
):
    config.set_values(
        dict(CLIENTGEOSHARING_NOT_UPDATE_SAME_VALUE=not_update_same_value),
    )

    query = {'_id': order_id}
    assert db.order_proc.find_one(query) is not None
    old_order_proc = db.order_proc.find_one(query).copy()
    old_order_params = old_order_proc['order']

    # Check that order contains two values and they are same
    # else old_client_geo_sharing = None
    old_client_geo_sharing = None
    if (
            'client_geo_sharing_enabled' in old_order_params
            and 'changes' in old_order_proc
            and old_order_proc['changes']['objects'][-1]['n']
            == 'client_geo_sharing'
            and old_order_params['client_geo_sharing_enabled']
            == old_order_proc['changes']['objects'][-1]['vl']
    ):
        old_client_geo_sharing = old_order_params['client_geo_sharing_enabled']

    # Request
    created_time = dateutil.parser.parse('2017-07-19T17:15:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': order_id,
        'created_time': created_time.isoformat(),
        'client_geo_sharing_enabled': new_client_geo_sharing,
    }
    response = taxi_protocol.post('3.0/changeclientgeosharing', request)
    assert response.status_code == 200

    # Check response
    data = response.json()
    assert data == {
        'change_id': data['change_id'],
        'status': 'success',
        'name': 'client_geo_sharing',
        'value': new_client_geo_sharing,
    }

    # Check order_proc after response
    order_proc = db.order_proc.find_one(query)
    assert (
        order_proc['order']['client_geo_sharing_enabled']
        == new_client_geo_sharing
    )

    last_change = order_proc['changes']['objects'][-1]
    assert last_change['n'] == 'client_geo_sharing'
    assert last_change['vl'] == new_client_geo_sharing

    # Compare new order_proc with old_order_proc
    version = order_proc['order']['version']
    if (
            not_update_same_value
            and old_client_geo_sharing == new_client_geo_sharing
    ):
        # If config == true and values are same
        assert old_order_proc == order_proc
        assert len(mock_stq_agent.get_tasks('client_geo_sharing')) == 0
    else:
        # If config == false or values aren't same
        assert version == old_order_params['version'] + 1
        if 'changes' in old_order_proc:
            assert len(order_proc['changes']['objects']) > len(
                old_order_proc['changes']['objects'],
            )
        assert order_proc['updated'] > old_order_proc['updated']
        assert last_change['t'] == created_time.replace(
            tzinfo=None, microsecond=0,
        )
        assert last_change['c'] == now.replace(tzinfo=None, microsecond=0)
        args = [mock_stq_agent, request['orderid'], 'client_geo_sharing']
        validate_process_update_stq_task(
            *args, exists=notify_on_change_version_switch,
        )
        validate_notify_on_change_stq_task(
            *args, exists=not notify_on_change_version_switch,
        )
