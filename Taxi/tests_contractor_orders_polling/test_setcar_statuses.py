import json

import pytest

from tests_contractor_orders_polling import utils


def sort_statuses(statuses: list) -> list:
    return sorted(statuses, key=lambda status: status['setcar_id'])


@pytest.mark.experiments3(
    name='driver_orders_common_hide_reasons_in_setcar_statuses',
    consumers=['driver-orders-common/contractor_park'],
    default_value={'default': False, 'enabled': True},
    clauses=[
        {
            'predicate': {'type': 'true'},
            'value': {'default': False, 'enabled': True},
        },
    ],
    is_config=True,
)
@pytest.mark.redis_store(
    [
        'set',
        'Order:Driver:CompleteRequest:MD5:999:888',
        'COMPLETE_REQUEST_ETAG',
    ],
    [
        'lpush',
        'Order:Driver:CompleteRequest:Items:999:888',
        'Order1',
        'Order2',
    ],
    ['set', 'Order:Driver:CancelRequest:MD5:999:888', 'CANCEL_REQUEST_ETAG'],
    [
        'lpush',
        'Order:Driver:CancelReason:Items:999:888',
        json.dumps(
            {
                'alias_id': 'Order3',
                'message': 'assigned_to_other_driver',
                'category': 'assigned_to_other_driver',
            },
        ),
        json.dumps(
            {
                'alias_id': 'Order4',
                'message': 'Why not?',
                'category': 'unknown',
            },
        ),
    ],
)
@pytest.mark.parametrize(
    'cancel_tag', ['CANCEL_REQUEST_ETAG', 'CANCEL_REQUEST_ETAG_BAD', '', None],
)
@pytest.mark.parametrize(
    'complete_tag',
    ['COMPLETE_REQUEST_ETAG', 'COMPLETE_REQUEST_ETAG_BAD', '', None],
)
@pytest.mark.parametrize('enabled', [False, True])
@pytest.mark.parametrize(
    'send_setcar_statuses_by_client_events', [False, True],
)
async def test_setcar_statuses(
        taxi_contractor_orders_polling,
        experiments3,
        cancel_tag,
        complete_tag,
        enabled,
        send_setcar_statuses_by_client_events,
):
    experiments3.add_config(
        name='setcar_statuses_enabled',
        match={'predicate': {'type': 'true'}, 'enabled': True},
        consumers=['contractor-orders-polling/setcar-statuses'],
        clauses=[],
        default_value={'enabled': enabled},
    )
    experiments3.add_config(
        name='driver_orders_common_use_client_events_for_send_fields',
        match={
            'predicate': {'type': 'true'},
            'enabled': send_setcar_statuses_by_client_events,
        },
        consumers=['driver-orders-common/contractor_park'],
        clauses=[],
        default_value={
            'enabled': send_setcar_statuses_by_client_events,
            'fields': ['setcar_statuses'],
        },
    )

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers=utils.HEADERS,
        params={
            'md5_cancelrequest': cancel_tag,
            'md5_completerequest': complete_tag,
        },
    )

    assert response.status_code == 200
    response_obj = response.json()
    response_obj['md5_cancelrequest'] = 'CANCEL_REQUEST_ETAG'
    response_obj['md5_completerequest'] = 'COMPLETE_REQUEST_ETAG'

    expected_setcar_statuses = []

    if complete_tag != 'COMPLETE_REQUEST_ETAG':
        expected_setcar_statuses.append(
            {'setcar_id': 'Order2', 'status': 'completed'},
        )
        expected_setcar_statuses.append(
            {'setcar_id': 'Order1', 'status': 'completed'},
        )

    if cancel_tag != 'CANCEL_REQUEST_ETAG':
        expected_setcar_statuses.append(
            {
                'setcar_id': 'Order3',
                'status': 'cancelled',
                'reason': {
                    'category': 'assigned_to_other_driver',
                    'message': 'Назначен на другого водителя',
                },
            },
        )

        expected_setcar_statuses.append(
            {
                'setcar_id': 'Order4',
                'status': 'cancelled',
                'reason': {'category': 'unknown', 'message': 'Заказ отменен'},
            },
        )

    if (
            not enabled
            or send_setcar_statuses_by_client_events
            or not expected_setcar_statuses
    ):
        assert response_obj.get('setcar_statuses') is None
    else:
        assert sort_statuses(
            response_obj.get('setcar_statuses'),
        ) == sort_statuses(expected_setcar_statuses)


@pytest.mark.redis_store(
    [
        'set',
        'Order:Driver:CompleteRequest:MD5:999:888',
        'COMPLETE_REQUEST_ETAG',
    ],
    [
        'lpush',
        'Order:Driver:CompleteRequest:Items:999:888',
        'Order1',
        'Order2',
    ],
    ['set', 'Order:Driver:CancelRequest:MD5:999:888', 'CANCEL_REQUEST_ETAG'],
    [
        'lpush',
        'Order:Driver:CancelReason:Items:999:888',
        json.dumps(
            {
                'alias_id': 'Order3',
                'message': 'assigned_to_other_driver',
                'category': 'assigned_to_other_driver',
            },
        ),
        json.dumps(
            {
                'alias_id': 'Order4',
                'message': 'Why not?',
                'category': 'unknown',
            },
        ),
    ],
)
@pytest.mark.parametrize(
    'hide_reasons, except_reasons',
    [
        (False, ['assigned_to_other_driver']),
        (True, ['assigned_to_other_driver']),
        (True, None),
        (False, None),
    ],
    ids=['stay_all_except', 'hide_all_except', 'hide_all', 'stay_all'],
)
async def test_hide_cancel_reasons_by_config(
        taxi_contractor_orders_polling,
        experiments3,
        hide_reasons,
        except_reasons,
):
    experiments3.add_config(
        name='setcar_statuses_enabled',
        match={'predicate': {'type': 'true'}, 'enabled': True},
        consumers=['contractor-orders-polling/setcar-statuses'],
        clauses=[],
        default_value={'enabled': True},
    )
    config_value = {'default': hide_reasons, 'enabled': True}
    if except_reasons is not None:
        config_value['exceptions'] = except_reasons
    experiments3.add_config(
        name='driver_orders_common_hide_reasons_in_setcar_statuses',
        match={'predicate': {'type': 'true'}, 'enabled': True},
        consumers=['driver-orders-common/contractor_park'],
        default_value=config_value,
    )

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers=utils.HEADERS,
        params={
            'md5_cancelrequest': 'CANCEL_REQUEST_ETAG_BAD',
            'md5_completerequest': 'COMPLETE_REQUEST_ETAG_BAD',
        },
    )

    assert response.status_code == 200
    response_obj = response.json()
    response_obj['md5_cancelrequest'] = 'CANCEL_REQUEST_ETAG'
    response_obj['md5_completerequest'] = 'COMPLETE_REQUEST_ETAG'

    expected_setcar_statuses = []

    expected_setcar_statuses.append(
        {'setcar_id': 'Order2', 'status': 'completed'},
    )
    expected_setcar_statuses.append(
        {'setcar_id': 'Order1', 'status': 'completed'},
    )

    show_only_except = hide_reasons and except_reasons is not None
    show_all = not hide_reasons and except_reasons is None
    hide_only_except = not hide_reasons and except_reasons is not None

    if show_only_except and not hide_only_except or show_all:
        expected_setcar_statuses.append(
            {
                'setcar_id': 'Order3',
                'status': 'cancelled',
                'reason': {
                    'category': 'assigned_to_other_driver',
                    'message': 'Назначен на другого водителя',
                },
            },
        )
    if not hide_reasons:
        expected_setcar_statuses.append(
            {
                'setcar_id': 'Order4',
                'status': 'cancelled',
                'reason': {'category': 'unknown', 'message': 'Заказ отменен'},
            },
        )

    assert sort_statuses(response_obj.get('setcar_statuses')) == sort_statuses(
        expected_setcar_statuses,
    )
