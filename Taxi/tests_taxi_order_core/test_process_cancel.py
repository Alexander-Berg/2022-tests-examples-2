import copy
import datetime

import pytest

DEFAULT_RESPONSE = {
    'driver_cancel_statuses': [
        {
            'success': True,
            'driver': {
                'park_id': 'df98ffa680714291882343e7df1ca5ab',
                'driver_profile_id': '957600cda6b74ca58fe20963d61ff060',
                'alias_id': 'cf0ae5ed549457a081fe9dd0c4bb6fcb',
            },
        },
        {
            'success': True,
            'driver': {
                'park_id': 'df98ffa680714291882343e7df1ca5ac',
                'driver_profile_id': 'ca5ed75b30de4a748da0db193a7092a2',
                'alias_id': 'cf0ae5ed549457a081fe9dd0c4bb6fcc',
            },
        },
    ],
}

_ALIASES = [
    'cf0ae5ed549457a081fe9dd0c4bb6fcb',
    'cf0ae5ed549457a081fe9dd0c4bb6fcc',
]

_DRIVERS = [
    '957600cda6b74ca58fe20963d61ff060',
    'ca5ed75b30de4a748da0db193a7092a2',
]

_PARKS = [
    'df98ffa680714291882343e7df1ca5ab',
    'df98ffa680714291882343e7df1ca5ac',
]

_NOW = datetime.datetime.fromisoformat('2021-04-13T13:04:58.101')


@pytest.mark.parametrize(
    'order_id, reasons, cancelled',
    # every proc has 2 candidates
    [
        ('timeout_and_cancelled', {'user', 'offertimeout'}, {0, 1}),
        # do not cancel 2nd driver because order has not performer yet
        ('autoreorder', {'user'}, {0}),
        ('search_expire', {'assigned'}, {0, 1}),
        ('expire', {'assigned', 'offertimeout'}, {0, 1}),
        # 2nd driver successfully finished order
        ('reject_and_complete', {'assigned'}, {0}),
    ],
)
@pytest.mark.now(f'{_NOW.isoformat()}Z')
async def test_process_cancel_do_cancel(
        mockserver, stq_runner, mongodb, order_id, reasons, cancelled,
):
    @mockserver.json_handler(
        'driver-orders-app-api/internal/v2/order/cancel/user',
    )
    def mock_cancel_order(req):
        cancel_infos = req.json['driver_cancel_infos']
        for cancel_info in cancel_infos:
            results['aliases'].add(cancel_info['driver']['alias_id'])
            results['drivers'].add(cancel_info['driver']['driver_profile_id'])
            results['parks'].add(cancel_info['driver']['park_id'])
            results['reasons'].add(cancel_info['cancel_reason'])

        response = copy.deepcopy(DEFAULT_RESPONSE)
        response['driver_cancel_statuses'] = [
            x
            for x in response['driver_cancel_statuses']
            if x['driver']['alias_id'] in results['aliases']
        ]
        assert len(response['driver_cancel_statuses']) == len(cancel_infos)
        return response

    results = {
        'aliases': set(),
        'drivers': set(),
        'parks': set(),
        'reasons': set(),
    }

    args = [order_id]
    await stq_runner.process_cancel.call(task_id=order_id, args=args)

    proc = mongodb.order_proc.find_one({'_id': order_id})
    assert proc['updated'] >= _NOW
    assert results['aliases'] == {_ALIASES[i] for i in cancelled}
    assert results['drivers'] == {_DRIVERS[i] for i in cancelled}
    assert results['parks'] == {_PARKS[i] for i in cancelled}
    assert results['reasons'] == reasons

    for i in cancelled:
        assert proc['candidates'][i].get('cancel_status') == 'finished'
    assert mock_cancel_order.times_called == 1


@pytest.mark.parametrize(
    'order_id', ['assigned_no_need_to_cancel', 'already_cancelled'],
)
@pytest.mark.now(f'{_NOW.isoformat()}Z')
async def test_process_cancel_do_not_cancel(
        mockserver, stq_runner, mongodb, order_id,
):
    @mockserver.json_handler(
        'driver-orders-app-api/internal/v2/order/cancel/user',
    )
    def mock_cancel_order(req):
        response = copy.deepcopy(DEFAULT_RESPONSE)
        return response

    args = [order_id]
    await stq_runner.process_cancel.call(task_id=order_id, args=args)

    proc = mongodb.order_proc.find_one({'_id': order_id})
    assert proc['updated'] < _NOW

    assert not mock_cancel_order.times_called


@pytest.mark.config(
    DRIVER_ORDERS_APP_API_CLIENT_QOS={
        '__default__': {'attempts': 1, 'timeout-ms': 200},
    },
)
@pytest.mark.parametrize(
    'statuses, updated, expected_statuses',
    [
        # all failed
        ([500, 500], False, {None}),
        # one fail, but another still updated in proc
        ([200, 500], True, {None, 'finished'}),
    ],
)
@pytest.mark.now(f'{_NOW.isoformat()}Z')
async def test_process_cancel_errors(
        mockserver, stq_runner, mongodb, statuses, updated, expected_statuses,
):
    @mockserver.json_handler(
        'driver-orders-app-api/internal/v2/order/cancel/user',
    )
    def mock_cancel_order(req):
        response = copy.deepcopy(DEFAULT_RESPONSE)
        for index, status in enumerate(statuses):
            if status == 500:
                response['driver_cancel_statuses'][index]['success'] = False
        return response

    order_id = 'timeout_and_cancelled'  # cancel 2 drivers

    args = [order_id]
    await stq_runner.process_cancel.call(
        task_id=order_id, args=args, expect_fail=True,
    )

    proc = mongodb.order_proc.find_one({'_id': order_id})
    if updated:
        assert proc['updated'] >= _NOW
    else:
        assert proc['updated'] < _NOW
    cancel_statuses = {i.get('cancel_status') for i in proc['candidates']}
    assert cancel_statuses == expected_statuses
    assert mock_cancel_order.times_called == 1
