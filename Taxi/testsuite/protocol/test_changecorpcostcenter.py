import json

import dateutil.parser
import pytest

from notify_on_change_version_switch import NOTIFY_ON_CHANGE_VERSION_SWITCH
from order_core_switch_parametrize import PROTOCOL_SWITCH_TO_ORDER_CORE
from validate_stq_task import validate_notify_on_change_stq_task
from validate_stq_task import validate_process_update_stq_task

CHANGE_ID = 'b300bda7d41b4bae8d58dfa93221ef16'
ORDER_ID_NO_CHANGES = '8c83b49edb274ce0992f337061041111'
ORDER_ID_FINISHED = '8c83b49edb274ce0992f337061042222'
ORDER_ID_NON_CORP = '8c83b49edb274ce0992f337061043333'
ORDER_ID_WITH_OLD_CHANGES = '8c83b49edb274ce0992f337061044444'
ORDER_ID_WITH_NEW_CHANGES = '8c83b49edb274ce0992f337061045555'

CREATED_TIME = '2017-07-22T12:05:20+0000'
CREATED_TIME_EARLIER = '2017-07-22T12:15:20+0000'
CREATED_TIME_TOO_EARLY = '2017-07-22T12:10:00+0000'

OLD_COST_CENTER_PREV = 'corp-1'
OLD_COST_CENTER_SENT = 'corp-2'
OLD_CC_CHANGE_NAME = 'corp_cost_center'
NEW_CC_CHANGE_NAME = 'cost_centers'

NEW_COST_CENTERS_PREV = [
    {'id': 'cost_center', 'name': 'Центр затрат', 'value': 'старое значение'},
]
NEW_COST_CENTERS_SENT = [
    {'id': 'cost_center', 'title': 'Центр затрат', 'value': 'командировка'},
    {'id': 'ride_purpose', 'title': 'Цель поездки', 'value': 'из аэропорта'},
]
OLD_COST_CENTERS_NEW_FORMAT = [
    {'id': '', 'title': 'Центр затрат', 'value': 'командировка'},
]

OLD_COST_CENTER_EMPTY_UPD = {'corp_cost_center': ''}
OLD_COST_CENTER_UPD = {'corp_cost_center': OLD_COST_CENTER_SENT}
NEW_COST_CENTERS_UPD = {'cost_centers': NEW_COST_CENTERS_SENT}
OLD_COST_CENTERS_NEW_FORMAT_UPD = {'cost_centers': OLD_COST_CENTERS_NEW_FORMAT}
BOTH_OLD_AND_NEW_COST_CENTERS = dict(
    OLD_COST_CENTER_UPD, **NEW_COST_CENTERS_UPD,
)

REQUEST_PARAMS = {
    'id': CHANGE_ID,
    'orderid': ORDER_ID_NO_CHANGES,
    'created_time': CREATED_TIME,
}
OLD_CC_EMPTY_REQUEST = dict(REQUEST_PARAMS, **OLD_COST_CENTER_EMPTY_UPD)
OLD_CC_REQUEST = dict(REQUEST_PARAMS, **OLD_COST_CENTER_UPD)
NEW_CC_REQUEST = dict(REQUEST_PARAMS, **NEW_COST_CENTERS_UPD)
BOTH_CC_REQUEST = dict(REQUEST_PARAMS, **BOTH_OLD_AND_NEW_COST_CENTERS)
OLD_CC_NEW_FORMAT_REQUEST = dict(
    REQUEST_PARAMS, **OLD_COST_CENTERS_NEW_FORMAT_UPD,
)


def _mock_cost_centers_check_by_user_id(
        mockserver, request=None, order=None, can_use=True, reason=None,
):
    @mockserver.json_handler(
        '/corp_integration_api/cost_centers/check/by_user_id',
    )
    def mock_cost_centers_check_by_user_id(check_request):
        # check that cost_centers_check receive expected data
        if request:
            check_data = json.loads(check_request.get_data())
            assert (
                check_data['corp_user_id']
                == order['request']['corp']['user_id']
            )
            if 'cost_centers' in request:
                assert check_data['cost_centers'] == request['cost_centers']
            elif 'corp_cost_center' in request:
                assert check_data['cost_center'] == request['corp_cost_center']

        response = {'can_use': can_use}
        if reason:
            response['reason'] = reason

        return response

    return mock_cost_centers_check_by_user_id


@pytest.mark.parametrize(
    'test_params',
    [
        # test order without prior changes: old cost_center format
        pytest.param(
            dict(
                prev_changes_count=0,
                request_params=OLD_CC_REQUEST,
                expected_response={
                    'status': 'success',
                    'name': OLD_CC_CHANGE_NAME,
                    'value': OLD_COST_CENTER_SENT,
                },
                expected_changes=[
                    # (items to be updated with variable data)
                    # there should be 2 items in the 'objects'
                    # (according to protocol)
                    # we need to create one fake item
                    {
                        'vl': OLD_COST_CENTER_PREV,
                        's': 'applied',
                        'ci': CHANGE_ID,
                        'n': OLD_CC_CHANGE_NAME,
                        'si': {'s': 'delivered', 'c': 0},
                    },
                    {
                        'vl': OLD_COST_CENTER_SENT,
                        's': 'applying',
                        'ci': CHANGE_ID,
                        'n': OLD_CC_CHANGE_NAME,
                        'si': {'s': 'init', 'c': 0},
                    },
                ],
            ),
            marks=pytest.mark.now('2017-07-22T12:05:10+0000'),
            id='old-cost-center-sent-no-changes-before',
        ),
        # test order without prior changes: old cost_center format, empty value
        pytest.param(
            dict(
                prev_changes_count=0,
                request_params=OLD_CC_EMPTY_REQUEST,
                expected_response={
                    'status': 'success',
                    'name': OLD_CC_CHANGE_NAME,
                    'value': '',
                },
                expected_changes=[
                    {
                        'vl': OLD_COST_CENTER_PREV,
                        's': 'applied',
                        'ci': CHANGE_ID,
                        'n': OLD_CC_CHANGE_NAME,
                        'si': {'s': 'delivered', 'c': 0},
                    },
                    {
                        'vl': '',
                        's': 'applying',
                        'ci': CHANGE_ID,
                        'n': OLD_CC_CHANGE_NAME,
                        'si': {'s': 'init', 'c': 0},
                    },
                ],
            ),
            marks=pytest.mark.now('2017-07-22T12:05:10+0000'),
            id='old-cost-center-empty-sent-no-changes-before',
        ),
        # test order without prior changes: old cost_centers in new format
        pytest.param(
            dict(
                prev_changes_count=0,
                request_params=OLD_CC_NEW_FORMAT_REQUEST,
                expected_response={
                    'status': 'success',
                    'name': NEW_CC_CHANGE_NAME,
                    'value': OLD_COST_CENTERS_NEW_FORMAT,
                },
                expected_changes=[
                    # (items to be updated with variable data)
                    # there should be 2 items in the 'objects'
                    # (according to protocol)
                    # we need to create one fake item
                    {
                        'vl': NEW_COST_CENTERS_PREV,
                        's': 'applied',
                        'ci': CHANGE_ID,
                        'n': NEW_CC_CHANGE_NAME,
                        'si': {'s': 'delivered', 'c': 0},
                    },
                    {
                        'vl': OLD_COST_CENTERS_NEW_FORMAT,
                        's': 'applying',
                        'ci': CHANGE_ID,
                        'n': NEW_CC_CHANGE_NAME,
                        'si': {'s': 'init', 'c': 0},
                    },
                ],
            ),
            marks=pytest.mark.now('2017-07-22T12:05:10+0000'),
            id='old-cost-centers-in-new-format-no-changes-before',
        ),
        # test order without prior changes: new cost_centers format
        pytest.param(
            dict(
                prev_changes_count=0,
                request_params=NEW_CC_REQUEST,
                expected_response={
                    'status': 'success',
                    'name': NEW_CC_CHANGE_NAME,
                    'value': NEW_COST_CENTERS_SENT,
                },
                expected_changes=[
                    # (items to be updated with variable data)
                    # there should be 2 items in the 'objects'
                    # (according to protocol)
                    # we need to create one fake item
                    {
                        'vl': NEW_COST_CENTERS_PREV,
                        's': 'applied',
                        'ci': CHANGE_ID,
                        'n': NEW_CC_CHANGE_NAME,
                        'si': {'s': 'delivered', 'c': 0},
                    },
                    {
                        'vl': NEW_COST_CENTERS_SENT,
                        's': 'applying',
                        'ci': CHANGE_ID,
                        'n': NEW_CC_CHANGE_NAME,
                        'si': {'s': 'init', 'c': 0},
                    },
                ],
            ),
            marks=pytest.mark.now('2017-07-22T12:05:10+0000'),
            id='new-cost-center-sent-no-changes-before',
        ),
        # test order without prior changes: both cost_centers formats
        # new one is considered, old one is ignored
        pytest.param(
            dict(
                prev_changes_count=0,
                request_params=BOTH_CC_REQUEST,
                expected_response={
                    'status': 'success',
                    'name': NEW_CC_CHANGE_NAME,
                    'value': NEW_COST_CENTERS_SENT,
                },
                expected_changes=[
                    # (items to be updated with variable data)
                    # there should be 2 items in the 'objects'
                    # (according to protocol)
                    # we need to create one fake item
                    {
                        'vl': NEW_COST_CENTERS_PREV,
                        's': 'applied',
                        'ci': CHANGE_ID,
                        'n': NEW_CC_CHANGE_NAME,
                        'si': {'s': 'delivered', 'c': 0},
                    },
                    {
                        'vl': NEW_COST_CENTERS_SENT,
                        's': 'applying',
                        'ci': CHANGE_ID,
                        'n': NEW_CC_CHANGE_NAME,
                        'si': {'s': 'init', 'c': 0},
                    },
                ],
            ),
            marks=pytest.mark.now('2017-07-22T12:05:10+0000'),
            id='both-cost-centers-sent-no-changes-before',
        ),
        # test order with prior changes: old cost_center format
        pytest.param(
            dict(
                prev_changes_count=2,
                request_params=dict(
                    OLD_CC_REQUEST,
                    orderid=ORDER_ID_WITH_OLD_CHANGES,
                    created_time=CREATED_TIME_EARLIER,
                ),
                expected_response={
                    'status': 'success',
                    'name': OLD_CC_CHANGE_NAME,
                    'value': OLD_COST_CENTER_SENT,
                },
                expected_changes=[
                    {
                        'vl': OLD_COST_CENTER_SENT,
                        's': 'applying',
                        'ci': CHANGE_ID,
                        'n': OLD_CC_CHANGE_NAME,
                        'si': {'s': 'init', 'c': 0},
                    },
                ],
            ),
            marks=pytest.mark.now('2017-07-22T12:15:15+0000'),
            id='old-cost-center-sent-with-changes-before',
        ),
        # test order with prior changes: old cost_center format, empty value
        pytest.param(
            dict(
                prev_changes_count=2,
                request_params=dict(
                    OLD_CC_EMPTY_REQUEST,
                    orderid=ORDER_ID_WITH_OLD_CHANGES,
                    created_time=CREATED_TIME_EARLIER,
                ),
                expected_response={
                    'status': 'success',
                    'name': OLD_CC_CHANGE_NAME,
                    'value': '',
                },
                expected_changes=[
                    {
                        'vl': '',
                        's': 'applying',
                        'ci': CHANGE_ID,
                        'n': OLD_CC_CHANGE_NAME,
                        'si': {'s': 'init', 'c': 0},
                    },
                ],
            ),
            marks=pytest.mark.now('2017-07-22T12:15:15+0000'),
            id='old-cost-center-empty-sent-with-changes-before',
        ),
        # test order with prior changes: old cost_centers in new format
        pytest.param(
            dict(
                prev_changes_count=2,
                request_params=dict(
                    OLD_CC_NEW_FORMAT_REQUEST,
                    orderid=ORDER_ID_WITH_NEW_CHANGES,
                    created_time=CREATED_TIME_EARLIER,
                ),
                expected_response={
                    'status': 'success',
                    'name': NEW_CC_CHANGE_NAME,
                    'value': OLD_COST_CENTERS_NEW_FORMAT,
                },
                expected_changes=[
                    {
                        'vl': OLD_COST_CENTERS_NEW_FORMAT,
                        's': 'applying',
                        'ci': CHANGE_ID,
                        'n': NEW_CC_CHANGE_NAME,
                        'si': {'s': 'init', 'c': 0},
                    },
                ],
            ),
            marks=pytest.mark.now('2017-07-22T12:15:15+0000'),
            id='old-cost-centers-in-new-format-with-changes-before',
        ),
        # test order with prior changes: new cost_center format
        pytest.param(
            dict(
                prev_changes_count=2,
                request_params=dict(
                    NEW_CC_REQUEST,
                    orderid=ORDER_ID_WITH_NEW_CHANGES,
                    created_time=CREATED_TIME_EARLIER,
                ),
                expected_response={
                    'status': 'success',
                    'name': NEW_CC_CHANGE_NAME,
                    'value': NEW_COST_CENTERS_SENT,
                },
                expected_changes=[
                    {
                        'vl': NEW_COST_CENTERS_SENT,
                        's': 'applying',
                        'ci': CHANGE_ID,
                        'n': NEW_CC_CHANGE_NAME,
                        'si': {'s': 'init', 'c': 0},
                    },
                ],
            ),
            marks=pytest.mark.now('2017-07-22T12:15:15+0000'),
            id='new-cost-center-sent-with-changes-before',
        ),
        # test order with prior changes: both cost_centers format
        # new one is considered, old one is ignored
        pytest.param(
            dict(
                prev_changes_count=2,
                request_params=dict(
                    BOTH_CC_REQUEST,
                    orderid=ORDER_ID_WITH_NEW_CHANGES,
                    created_time=CREATED_TIME_EARLIER,
                ),
                expected_response={
                    'status': 'success',
                    'name': NEW_CC_CHANGE_NAME,
                    'value': NEW_COST_CENTERS_SENT,
                },
                expected_changes=[
                    {
                        'vl': NEW_COST_CENTERS_SENT,
                        's': 'applying',
                        'ci': CHANGE_ID,
                        'n': NEW_CC_CHANGE_NAME,
                        'si': {'s': 'init', 'c': 0},
                    },
                ],
            ),
            marks=pytest.mark.now('2017-07-22T12:15:15+0000'),
            id='both-cost-centers-sent-with-changes-before',
        ),
    ],
)
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
@pytest.mark.parametrize('use_order_core', [False, True])
@PROTOCOL_SWITCH_TO_ORDER_CORE
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_changecorpcostcenter(
        taxi_protocol,
        mockserver,
        db,
        now,
        mock_order_core,
        mock_stq_agent,
        use_order_core,
        config,
        test_params,
        order_core_switch_on,
        notify_on_change_version_switch,
):
    if use_order_core:
        config.set_values(
            dict(PROCESSING_BACKEND_CPP_SWITCH=['change-corp-cost-center']),
        )

    """Basic change corp_cost_center"""
    request_params = test_params['request_params']
    created_time = dateutil.parser.parse(request_params['created_time'])
    request = dict(request_params, created_time=created_time.isoformat())

    query = {'_id': request['orderid']}
    proc_before = db.order_proc.find_one(query)
    assert proc_before is not None

    mock_cost_centers_check_by_user_id = _mock_cost_centers_check_by_user_id(
        mockserver, request=request, order=proc_before['order'],
    )

    version = proc_before['order']['version']

    # check changes in order before request
    prev_changes_count = test_params['prev_changes_count']
    if prev_changes_count > 0:
        assert 'changes' in proc_before
        assert len(proc_before['changes']['objects']) == prev_changes_count
    else:
        assert 'changes' not in proc_before
    assert now > db.order_proc.find_one(query)['updated']

    # make request
    response = taxi_protocol.post('3.0/changecorpcostcenter', request)
    assert response.status_code == 200
    assert mock_cost_centers_check_by_user_id.times_called == 1
    assert mock_order_core.get_fields_times_called == order_core_switch_on
    assert mock_order_core.set_fields_times_called == order_core_switch_on
    change_name = (
        'cost_centers' if 'cost_centers' in request else 'corp_cost_center'
    )
    args = [mock_stq_agent, request['orderid'], change_name]
    validate_process_update_stq_task(*args, exists=False)
    validate_notify_on_change_stq_task(
        *args, exists=not notify_on_change_version_switch,
    )
    data = response.json()

    # validate response according to protocol
    expected_data = dict(
        test_params['expected_response'], change_id=data['change_id'],
    )
    assert data == expected_data

    # validate order_proc table
    order_proc = db.order_proc.find_one(query)
    assert order_proc['processing']['need_start'] is False
    assert order_proc['order_info']['need_sync'] is False
    assert order_proc['order']['version'] == version + 1
    # check corp data
    assert 'corp' in order_proc['order']['request']
    corp_details = order_proc['order']['request']['corp']
    if 'cost_centers' in request:  # check new format first (from now on)
        assert corp_details['cost_centers'] == (request['cost_centers'])
    elif 'corp_cost_center' in request:
        assert corp_details['cost_center'] == (request['corp_cost_center'])

    # 'objects' may already have items, we add new item(s)
    proc_changes = order_proc['changes']['objects']
    expected_changes = test_params['expected_changes']
    assert len(proc_changes) == prev_changes_count + len(expected_changes)
    # prepare new changes only (update with variable data)
    new_proc_changes = proc_changes[prev_changes_count:]
    for (ex_ch, proc_ch) in zip(expected_changes, new_proc_changes):
        ex_ch.update(
            id=proc_ch['id'],
            vr=version + 1,
            c=now.replace(tzinfo=None, microsecond=0),
            t=created_time.replace(tzinfo=None, microsecond=0),
        )

    # finally compare changes
    assert new_proc_changes == expected_changes
    assert mock_order_core.post_event_times_called == 0


@pytest.mark.parametrize(
    'created_time,expected_status,error_text',
    [
        (123, 400, 'Bad Request'),
        ('2017-07-22T12:05:10.123', 400, 'Bad Request'),
    ],
    ids=['created_time is not a string', 'wrong time format'],
)
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
@PROTOCOL_SWITCH_TO_ORDER_CORE
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_parse_created_time(
        taxi_protocol,
        mockserver,
        created_time,
        expected_status,
        error_text,
        order_core_switch_on,
        notify_on_change_version_switch,
):
    _mock_cost_centers_check_by_user_id(mockserver)
    request = {
        'id': CHANGE_ID,
        'orderid': '8c83b49edb274ce0992f337061043333',
        'created_time': created_time,
        'corp_cost_center': 'corp-2',
    }
    response = taxi_protocol.post('3.0/changecorpcostcenter', request)
    assert response.status_code == expected_status
    data = response.json()
    assert data['error']['text'] == error_text


WRONG_STAMP_ERROR = 'last change time stamp > current change time stamp'
COST_CENTER_REQUIRED_ERROR = 'Необходимо указать центр затрат'
COST_CENTER_WRONG_VALUE_ERROR = 'Неверный центр затрат'


@pytest.mark.parametrize(
    'request_data',
    [
        pytest.param(
            dict(
                id=CHANGE_ID,
                orderid=ORDER_ID_WITH_OLD_CHANGES,
                created_time=CREATED_TIME_TOO_EARLY,
                corp_cost_center=OLD_COST_CENTER_SENT,
            ),
            id='old-cost-center',
        ),
        pytest.param(
            dict(
                id=CHANGE_ID,
                orderid=ORDER_ID_WITH_NEW_CHANGES,
                created_time=CREATED_TIME_TOO_EARLY,
                cost_centers=NEW_COST_CENTERS_SENT,
            ),
            id='new-cost-centers',
        ),
    ],
)
@pytest.mark.parametrize(
    'test_params',
    [
        pytest.param(
            dict(
                orderid=ORDER_ID_FINISHED,
                expected_status=404,
                expected_error='order is finished',
            ),
            id='order is finished',
        ),
        pytest.param(
            dict(
                orderid='non_existent_order_id',
                expected_status=404,
                expected_error='order_proc not found',
            ),
            id='order does not exist',
        ),
        pytest.param(
            dict(
                orderid=ORDER_ID_NON_CORP,
                expected_status=406,
                expected_error='cant_change_cost_center_for_non_corp',
            ),
            id='is not corp client',
        ),
        pytest.param(
            dict(expected_status=409, expected_error=WRONG_STAMP_ERROR),
            id='corp_cost_center is already applied',
        ),
        pytest.param(
            dict(
                can_use=False,
                expected_status=406,
                reason=COST_CENTER_REQUIRED_ERROR,
                expected_error=COST_CENTER_REQUIRED_ERROR,
            ),
            id='no-cost-centers-sent-to-cost_centers_check_by_usr_id',
        ),
        pytest.param(
            dict(
                can_use=False,
                expected_status=406,
                reason=COST_CENTER_WRONG_VALUE_ERROR,
                expected_error=COST_CENTER_WRONG_VALUE_ERROR,
            ),
            id='wrong-cost-centers-sent-to-cost_centers_check_by_usr_id',
        ),
    ],
)
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
@PROTOCOL_SWITCH_TO_ORDER_CORE
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_errors(
        taxi_protocol,
        mockserver,
        request_data,
        test_params,
        order_core_switch_on,
        notify_on_change_version_switch,
):
    _mock_cost_centers_check_by_user_id(
        mockserver,
        can_use=test_params.get('can_use', True),
        reason=test_params.get('reason'),
    )
    orderid = test_params.get('orderid')
    if orderid is not None:
        request = dict(request_data, orderid=orderid)
    else:
        request = request_data
    response = taxi_protocol.post('3.0/changecorpcostcenter', request)

    data = response.json()
    response_code_text = (response.status_code, data['error']['text'])
    expected_code_text = (
        test_params['expected_status'],
        test_params['expected_error'],
    )
    assert response_code_text == expected_code_text
