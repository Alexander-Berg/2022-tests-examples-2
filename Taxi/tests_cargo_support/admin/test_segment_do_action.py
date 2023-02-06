import pytest

from tests_cargo_support import utils_waybill_info


DEFAULT_REASON_FOR_ACTION = {
    'long_wait': 'long_wait__invalid_status',
    'cancel_order': 'cancel_order__invalid_status',
    'cancel_order_paid': 'cancel_order_paid__sender_does_not_answer',
    'fake_return': 'fake_return__invalid_status',
    'real_return': 'real_return__receiver_does_not_want_order',
    'delivered': 'delivered__invalid_status',
}


@pytest.mark.parametrize(
    'action_type', ['long_wait', 'fake_return', 'real_return', 'delivered'],
)
async def test_empty_point_id(taxi_cargo_support, action_type):
    response = await taxi_cargo_support.post(
        '/v1/admin/segment/do-action',
        params={'waybill_external_ref': 'wb_1'},
        headers={'X-Yandex-Login': 'login_1'},
        json={
            'park_id': 'park_id_1',
            'driver_id': 'driver_id_1',
            'action': action_type,
            'reason': DEFAULT_REASON_FOR_ACTION[action_type],
            'is_reorder_disabled': False,
            'ticket': 'ticket_1',
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'empty_point_id',
        'message': 'Неправильный параметр',
    }


async def test_unmatched_reason(taxi_cargo_support):
    response = await taxi_cargo_support.post(
        '/v1/admin/segment/do-action',
        params={'waybill_external_ref': 'wb_1'},
        headers={'X-Yandex-Login': 'login_1'},
        json={
            'park_id': 'park_id_1',
            'driver_id': 'driver_id_1',
            'point_id': 12345,
            'action': 'long_wait',
            'reason': DEFAULT_REASON_FOR_ACTION['delivered'],
            'is_reorder_disabled': False,
            'ticket': 'ticket_1',
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'reason_does_not_match_action',
        'message': 'Неправильный параметр',
    }


@pytest.mark.parametrize(
    'action_type',
    [
        'long_wait',
        'cancel_order',
        'cancel_order_paid',
        'fake_return',
        'real_return',
        'delivered',
    ],
)
async def test_unknown_point_id(
        taxi_cargo_support, mockserver, load_json, action_type,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _mock_waybill_info(request):
        return mockserver.make_response(
            status=200,
            json=load_json('cargo-dispatch/waybill_info_minimal.json'),
        )

    response = await taxi_cargo_support.post(
        '/v1/admin/segment/do-action',
        params={'waybill_external_ref': 'wb_1'},
        headers={'X-Yandex-Login': 'login_1'},
        json={
            'park_id': 'park_id_1',
            'driver_id': 'driver_id_1',
            'point_id': 12345,
            'action': action_type,
            'reason': DEFAULT_REASON_FOR_ACTION[action_type],
            'is_reorder_disabled': False,
            'ticket': 'ticket_1',
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'point_not_found',
        'message': 'Объект не найден',
    }


@pytest.mark.parametrize('action_type', ['cancel_order', 'cancel_order_paid'])
async def test_resolved_points(
        taxi_cargo_support, mockserver, load_json, action_type,
):
    waybill_info = load_json(
        'cargo-dispatch/waybill_info_with_order_and_segment.json',
    )
    waybill_ref = waybill_info['waybill']['external_ref']
    segment_id = waybill_info['segments'][0]['id']
    park_id = waybill_info['execution']['taxi_order_info']['performer_info'][
        'park_id'
    ]
    driver_id = waybill_info['execution']['taxi_order_info']['performer_info'][
        'driver_id'
    ]

    utils_waybill_info.add_point_execution(
        waybill_info,
        'source',
        'visited',
        'point_id_1',
        1,
        is_resolved=True,
        segment_id=segment_id,
    )
    utils_waybill_info.add_point_execution(
        waybill_info,
        'destination',
        'visited',
        'point_id_2',
        2,
        is_resolved=True,
        segment_id=segment_id,
    )
    utils_waybill_info.add_point_execution(
        waybill_info,
        'return',
        'skipped',
        'point_id_3',
        3,
        is_resolved=False,
        segment_id=segment_id,
    )

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _mock_waybill_info(request):
        return mockserver.make_response(status=200, json=waybill_info)

    response = await taxi_cargo_support.post(
        '/v1/admin/segment/do-action',
        params={'waybill_external_ref': waybill_ref},
        headers={'X-Yandex-Login': 'login_1'},
        json={
            'park_id': park_id,
            'driver_id': driver_id,
            'action': action_type,
            'reason': DEFAULT_REASON_FOR_ACTION[action_type],
            'is_reorder_disabled': False,
            'ticket': 'ticket_1',
        },
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'points_are_resolved',
        'message': 'Обновите страницу',
    }


@pytest.mark.parametrize(
    'action_type', ['long_wait', 'cancel_order', 'cancel_order_paid'],
)
@pytest.mark.parametrize(
    ['point_type', 'point_status'],
    [
        ('source', 'pending'),
        # ('source', 'arrived'), - the only expected state
        ('source', 'visited'),
        ('source', 'partial_delivery'),
        ('source', 'skipped'),
        ('destination', 'pending'),
        ('destination', 'arrived'),
        ('destination', 'visited'),
        ('destination', 'partial_delivery'),
        ('destination', 'skipped'),
        ('return', 'pending'),
        ('return', 'arrived'),
        ('return', 'visited'),
        ('return', 'partial_delivery'),
        ('return', 'skipped'),
    ],
)
async def test_not_arrived_point_a(
        taxi_cargo_support,
        mockserver,
        load_json,
        action_type,
        point_type,
        point_status,
):
    waybill_info = load_json(
        'cargo-dispatch/waybill_info_with_order_and_segment.json',
    )
    waybill_ref = waybill_info['waybill']['external_ref']
    segment_id = waybill_info['segments'][0]['id']
    park_id = waybill_info['execution']['taxi_order_info']['performer_info'][
        'park_id'
    ]
    driver_id = waybill_info['execution']['taxi_order_info']['performer_info'][
        'driver_id'
    ]

    utils_waybill_info.add_point_execution(
        waybill_info,
        point_type,
        point_status,
        'point_id_1',
        1,
        segment_id=segment_id,
    )

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _mock_waybill_info(request):
        return mockserver.make_response(status=200, json=waybill_info)

    response = await taxi_cargo_support.post(
        '/v1/admin/segment/do-action',
        params={'waybill_external_ref': waybill_ref},
        headers={'X-Yandex-Login': 'login_1'},
        json={
            'park_id': park_id,
            'driver_id': driver_id,
            'point_id': 1,
            'action': action_type,
            'reason': DEFAULT_REASON_FOR_ACTION[action_type],
            'is_reorder_disabled': False,
            'ticket': 'ticket_1',
        },
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'invalid_point_state',
        'message': 'Обновите страницу',
    }


@pytest.mark.parametrize(
    'action_type', ['fake_return', 'real_return', 'delivered'],
)
@pytest.mark.parametrize(
    ['point_type', 'point_status'],
    [
        ('source', 'pending'),
        ('source', 'arrived'),
        ('source', 'visited'),
        ('source', 'partial_delivery'),
        ('source', 'skipped'),
        ('destination', 'pending'),
        # ('destination', 'arrived'), - the only expected state
        ('destination', 'visited'),
        ('destination', 'partial_delivery'),
        ('destination', 'skipped'),
        ('return', 'pending'),
        ('return', 'arrived'),
        ('return', 'visited'),
        ('return', 'partial_delivery'),
        ('return', 'skipped'),
    ],
)
async def test_not_arrived_point_b(
        taxi_cargo_support,
        mockserver,
        load_json,
        action_type,
        point_type,
        point_status,
):
    waybill_info = load_json(
        'cargo-dispatch/waybill_info_with_order_and_segment.json',
    )
    waybill_ref = waybill_info['waybill']['external_ref']
    segment_id = waybill_info['segments'][0]['id']
    park_id = waybill_info['execution']['taxi_order_info']['performer_info'][
        'park_id'
    ]
    driver_id = waybill_info['execution']['taxi_order_info']['performer_info'][
        'driver_id'
    ]

    utils_waybill_info.add_point_execution(
        waybill_info,
        point_type,
        point_status,
        'point_id_1',
        1,
        segment_id=segment_id,
    )

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _mock_waybill_info(request):
        return mockserver.make_response(status=200, json=waybill_info)

    response = await taxi_cargo_support.post(
        '/v1/admin/segment/do-action',
        params={'waybill_external_ref': waybill_ref},
        headers={'X-Yandex-Login': 'login_1'},
        json={
            'park_id': park_id,
            'driver_id': driver_id,
            'point_id': 1,
            'action': action_type,
            'reason': DEFAULT_REASON_FOR_ACTION[action_type],
            'is_reorder_disabled': False,
            'ticket': 'ticket_1',
        },
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'invalid_point_state',
        'message': 'Обновите страницу',
    }


async def test_performer_changed(
        taxi_cargo_support, mockserver, load_json, action_type='long_wait',
):
    waybill_info = load_json(
        'cargo-dispatch/waybill_info_with_order_and_segment.json',
    )
    waybill_ref = waybill_info['waybill']['external_ref']
    segment_id = waybill_info['segments'][0]['id']

    utils_waybill_info.add_point_execution(
        waybill_info,
        'source',
        'arrived',
        'point_id_1',
        1,
        segment_id=segment_id,
    )

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _mock_waybill_info(request):
        return mockserver.make_response(status=200, json=waybill_info)

    response = await taxi_cargo_support.post(
        '/v1/admin/segment/do-action',
        params={'waybill_external_ref': waybill_ref},
        headers={'X-Yandex-Login': 'login_1'},
        json={
            'park_id': 'park_id_another',
            'driver_id': 'driver_id_another',
            'point_id': 1,
            'action': action_type,
            'reason': DEFAULT_REASON_FOR_ACTION[action_type],
            'is_reorder_disabled': False,
            'ticket': 'ticket_1',
        },
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'performer_changed',
        'message': 'Обновите страницу',
    }


@pytest.mark.experiments3(
    name='cargo_support_admin_actions_execution',
    consumers=['cargo-support/admin-actions-execution'],
    is_config=True,
    default_value={
        'reorder_or_cancel_type': 'reorder',
        'cancel_paid_arriving': False,
        'cancel_paid_waiting': True,
        'fine': False,
    },
    clauses=[],
)
@pytest.mark.parametrize(
    ['action_type', 'point_type'],
    [
        ('long_wait', 'source'),
        ('cancel_order', 'source'),
        ('cancel_order_paid', 'source'),
        ('fake_return', 'destination'),
        ('real_return', 'destination'),
        ('delivered', 'destination'),
    ],
)
async def test_happy_path(
        taxi_cargo_support,
        mockserver,
        stq,
        load_json,
        action_type,
        point_type,
):
    waybill_info = load_json(
        'cargo-dispatch/waybill_info_with_order_and_segment.json',
    )
    waybill_ref = waybill_info['waybill']['external_ref']

    segment_id = waybill_info['segments'][0]['id']
    zone_id = waybill_info['segments'][0]['zone_id']
    corp_client_id = waybill_info['segments'][0]['corp_client_id']

    claim_id = waybill_info['execution']['segments'][0]['claim_id']
    cargo_order_id = waybill_info['execution']['cargo_order_info']['order_id']
    taxi_order_id = waybill_info['execution']['taxi_order_info']['order_id']
    park_id = waybill_info['execution']['taxi_order_info']['performer_info'][
        'park_id'
    ]
    driver_id = waybill_info['execution']['taxi_order_info']['performer_info'][
        'driver_id'
    ]

    reason = DEFAULT_REASON_FOR_ACTION[action_type]

    utils_waybill_info.add_point_execution(
        waybill_info,
        point_type,
        'arrived',
        'point_id_1',
        1,
        segment_id=segment_id,
    )

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _mock_waybill_info(request):
        assert request.query['waybill_external_ref'] == waybill_ref
        return mockserver.make_response(status=200, json=waybill_info)

    response = await taxi_cargo_support.post(
        '/v1/admin/segment/do-action',
        params={'waybill_external_ref': waybill_ref},
        headers={'X-Yandex-Login': 'login_1'},
        json={
            'park_id': park_id,
            'driver_id': driver_id,
            'point_id': 1,
            'action': action_type,
            'reason': reason,
            'is_reorder_disabled': True,
            'ticket': 'ticket_1',
            'text_reason': 'text reason 1',
        },
    )
    assert response.status_code == 200

    assert stq.cargo_support_admin_segment_action.times_called == 1
    task = stq.cargo_support_admin_segment_action.next_call()
    assert task['id'] == f'{waybill_ref}_1_{action_type}'

    assert task['kwargs']['waybill_ref'] == waybill_ref
    assert task['kwargs']['claim_point_id'] == 1
    assert task['kwargs']['claim_id'] == claim_id
    assert task['kwargs']['taxi_order_id'] == taxi_order_id
    assert task['kwargs']['cargo_order_id'] == cargo_order_id
    assert task['kwargs']['segment_id'] == segment_id
    assert task['kwargs']['zone_id'] == zone_id
    assert task['kwargs']['corp_client_id'] == corp_client_id
    assert task['kwargs']['park_id'] == park_id
    assert task['kwargs']['driver_id'] == driver_id
    assert task['kwargs']['action_type'] == action_type
    assert task['kwargs']['reason_type'] == reason
    assert task['kwargs']['admin_login'] == 'login_1'
    assert task['kwargs']['is_reorder_disabled_by_admin']
    assert task['kwargs']['reorder_or_cancel_type'] == 'cancel'
    assert not task['kwargs']['is_cancelled_paid_arriving']
    assert task['kwargs']['is_cancelled_paid_waiting']
    assert not task['kwargs']['is_fine_required']
    assert task['kwargs']['ticket'] == 'ticket_1'
    assert task['kwargs']['text_reason'] == 'text reason 1'
