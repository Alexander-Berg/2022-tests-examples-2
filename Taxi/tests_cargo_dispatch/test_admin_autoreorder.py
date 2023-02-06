import pytest

from testsuite.utils import matching


async def test_driver_changed(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        waybill_id='waybill_fb_3',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/autoreorder',
        json={
            'performer_info': {
                'driver_id': 'old_driver',
                'park_id': 'old_park',
            },
            'reason': 'Стоял на месте',
            'cancel_state': 'free',
        },
        params={'waybill_external_ref': waybill_id},
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'driver_already_changed',
        'message': 'Исполнитель уже изменился',
    }


async def test_some_point_visited(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        waybill_id='waybill_fb_3',
):
    segment = happy_path_claims_segment_db.get_segment('seg3')
    segment.set_point_visit_status('p1', 'visited')

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/autoreorder',
        json={
            'performer_info': {
                'driver_id': 'driver_id_1',
                'park_id': 'park_id_1',
            },
            'reason': 'Стоял на месте',
            'cancel_state': 'free',
        },
        params={'waybill_external_ref': waybill_id},
    )
    assert response.status_code == 409
    assert response.json() == {
        'message': 'Исполнитель уже забрал груз',
        'code': 'some_point_already_visited',
    }


async def test_no_performer_for_order(
        taxi_cargo_dispatch,
        happy_path_state_orders_created,
        mockserver,
        mock_order_cancel,
        waybill_id='waybill_fb_3',
):
    @mockserver.json_handler('/cargo-orders/v1/performers/bulk-info')
    async def _handler(request):
        return {'performers': []}

    mock_order_cancel.expected_request = {
        'order_id': matching.AnyString(),
        'cancel_state': 'free',
        'cancel_reason': 'admin_reorder_required',
    }

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/autoreorder',
        json={'reason': 'Стоял на месте', 'cancel_state': 'free'},
        params={'waybill_external_ref': waybill_id},
    )
    assert response.status_code == 200
    assert (
        response.json()['result']
        == 'Успех. Теперь будет создан новый маршрутный лист'
    )

    assert mock_order_cancel.handler.times_called == 1


async def test_cancel_taxi_order(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        mock_order_cancel,
        waybill_id='waybill_fb_3',
):
    mock_order_cancel.expected_request = {
        'order_id': matching.AnyString(),
        'cancel_state': 'free',
        'cancel_reason': 'admin_reorder_required',
    }

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/autoreorder',
        json={
            'performer_info': {
                'driver_id': 'driver_id_1',
                'park_id': 'park_id_1',
            },
            'reason': 'Стоял на месте',
            'cancel_state': 'free',
        },
        params={'waybill_external_ref': waybill_id},
    )
    assert response.status_code == 200
    assert (
        response.json()['result']
        == 'Успех. Теперь будет создан новый маршрутный лист'
    )

    assert mock_order_cancel.handler.times_called == 1


async def test_free_cancel_forbidden(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        mock_order_cancel,
        waybill_id='waybill_fb_3',
):
    mock_order_cancel.status_code = 409

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/autoreorder',
        json={
            'performer_info': {
                'driver_id': 'driver_id_1',
                'park_id': 'park_id_1',
            },
            'reason': 'Стоял на месте',
            'cancel_state': 'free',
        },
        params={'waybill_external_ref': waybill_id},
    )
    assert response.status_code == 409
    assert response.json() == {
        'message': 'Возможно, исполнителю придется оплатить ожидание',
        'code': 'free_cancel_forbidden',
    }


async def test_paid_cancel_error(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        mockserver,
        waybill_id='waybill_fb_3',
):
    @mockserver.json_handler('/cargo-orders/v1/order/cancel')
    def _mock(request):
        return mockserver.make_response(
            json={'code': '', 'message': ''}, status=409,
        )

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/autoreorder',
        json={
            'performer_info': {
                'driver_id': 'driver_id_1',
                'park_id': 'park_id_1',
            },
            'reason': 'Стоял на месте',
            'cancel_state': 'paid',
        },
        params={'waybill_external_ref': waybill_id},
    )
    assert response.status_code == 500


@pytest.mark.parametrize(
    'is_reorder_required',
    [
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    CARGO_DISPATCH_ADMIN_SEGMENT_REORDERS_ENABLED=True,
                ),
            ],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    CARGO_DISPATCH_ADMIN_SEGMENT_REORDERS_ENABLED=False,
                ),
            ],
        ),
    ],
)
async def test_admin_segment_reorders(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        mockserver,
        pgsql,
        is_reorder_required,
        waybill_id='waybill_smart_1',
        ticket='CHATTERBOX-22',
):
    reason_ids_chain = ['some_reason', 'some_details']

    cancel_request_token = None

    @mockserver.json_handler('/cargo-orders/v1/order/cancel')
    def _mock_order_cancel(request):
        if is_reorder_required:
            nonlocal cancel_request_token
            cancel_request_token = request.json['cancel_request_token']
            assert cancel_request_token is not None

        assert request.json['reason_ids_chain'] == reason_ids_chain
        return {'cancel_state': 'free'}

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/autoreorder',
        json={
            'performer_info': {
                'driver_id': 'driver_id_1',
                'park_id': 'park_id_1',
            },
            'reason': 'Стоял на месте',
            'cancel_state': 'free',
            'reason_ids_chain': reason_ids_chain,
            'ticket': ticket,
        },
        params={'waybill_external_ref': waybill_id},
    )
    assert response.status_code == 200
    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        """select segment_id, reason, ticket, source,
                  forced_action, cancel_request_token
           from cargo_dispatch.admin_segment_reorders
           where segment_id in ('seg1', 'seg2')
           order by segment_id
        """,
    )
    reason = '.'.join(reason_ids_chain)
    if is_reorder_required:
        assert list(cursor) == [
            (
                'seg1',
                reason,
                ticket,
                'waybill_autoreorder.autoreorder_unknown_service',
                None,
                cancel_request_token,
            ),
            (
                'seg2',
                reason,
                ticket,
                'waybill_autoreorder.autoreorder_unknown_service',
                None,
                None,
            ),
        ]
    else:
        assert not list(cursor)
