import pytest

from tests_cargo_support import utils_pg


def build_stq_kwargs(
        waybill_ref,
        claim_point_id,
        action_type,
        reason_type,
        *,
        admin_login='admin_login_1',
        is_reorder_disabled_by_admin=False,
        is_cancelled_paid_arriving=False,
        is_cancelled_paid_waiting=False,
        is_fine_required=False,
        reorder_or_cancel_type=None,
):
    kwargs = {
        'waybill_ref': waybill_ref,
        'claim_point_id': claim_point_id,
        'cargo_order_id': '11111111-1111-1111-1111-111111111111',
        'claim_id': 'claim_id_1',
        'corp_client_id': 'corp_client_id_1',
        'taxi_order_id': 'taxi_order_id_1',
        'segment_id': 'segment_id_1',
        'zone_id': 'zone_id_1',
        'park_id': 'park_id_1',
        'driver_id': 'driver_id_1',
        'action_type': action_type,
        'reason_type': reason_type,
        'admin_login': admin_login,
        'is_reorder_disabled_by_admin': False,
        'is_cancelled_paid_arriving': False,
        'is_cancelled_paid_waiting': False,
        'is_fine_required': False,
        'ticket': 'ticket_1',
        'text_reason': 'text reason',
    }

    if reorder_or_cancel_type is not None:
        kwargs['reorder_or_cancel_type'] = reorder_or_cancel_type

    return kwargs


def check_point_action(
        point_action,
        waybill_ref,
        claim_point_id,
        action_type,
        reason_type,
        status,
        *,
        is_reorder_disabled_by_admin=False,
        is_cancelled_paid_arriving=False,
        is_cancelled_paid_waiting=False,
        is_fine_required=False,
        reorder_or_cancel_type=None,
):
    assert (
        point_action.cargo_order_id == '11111111-1111-1111-1111-111111111111'
    )
    assert point_action.taxi_order_id == 'taxi_order_id_1'
    assert point_action.waybill_ref == waybill_ref
    assert point_action.segment_id == 'segment_id_1'
    assert point_action.claim_point_id == claim_point_id
    assert point_action.claim_id == 'claim_id_1'
    assert point_action.corp_client_id == 'corp_client_id_1'
    assert point_action.zone_id == 'zone_id_1'
    assert point_action.park_id == 'park_id_1'
    assert point_action.driver_id == 'driver_id_1'
    assert point_action.action_type == action_type
    assert point_action.reason_type == reason_type
    assert point_action.admin_login == 'admin_login_1'
    assert point_action.ticket == 'ticket_1'
    assert point_action.text_reason == 'text reason'
    assert (
        point_action.is_reorder_disabled_by_admin
        == is_reorder_disabled_by_admin
    )
    assert point_action.reorder_or_cancel_type == reorder_or_cancel_type
    assert point_action.is_cancelled_paid_waiting == is_cancelled_paid_waiting
    assert (
        point_action.is_cancelled_paid_arriving == is_cancelled_paid_arriving
    )
    assert point_action.is_fine_required == is_fine_required
    assert point_action.status == status


@pytest.mark.pgsql('cargo_support')
async def test_no_action(pgsql, stq_runner):
    waybill_ref = 'waybill_ref_1'
    claim_point_id = 1
    action_type = 'long_wait'
    reason_type = 'long_wait__invalid_status'

    await stq_runner.cargo_support_admin_segment_action.call(
        task_id='task_id_1',
        kwargs=build_stq_kwargs(
            waybill_ref, claim_point_id, action_type, reason_type,
        ),
    )

    point_action = utils_pg.select_point_action(
        pgsql, waybill_ref, claim_point_id, action_type,
    )

    check_point_action(
        point_action,
        waybill_ref,
        claim_point_id,
        action_type,
        reason_type,
        'success',
    )


@pytest.mark.pgsql('cargo_support')
async def test_invalid_reason(pgsql, stq_runner):
    waybill_ref = 'waybill_ref_1'
    claim_point_id = 1
    action_type = 'long_wait'

    await stq_runner.cargo_support_admin_segment_action.call(
        task_id='task_id_1',
        kwargs=build_stq_kwargs(
            waybill_ref,
            claim_point_id,
            action_type,
            'delivered__invalid_status',
        ),
    )

    point_actions = utils_pg.select_point_actions(pgsql, waybill_ref)
    assert point_actions == []


@pytest.mark.pgsql('cargo_support')
async def test_existing_action(pgsql, stq_runner):
    waybill_ref = 'waybill_ref_1'
    claim_point_id = 1
    action_type = 'long_wait'
    reason_type = 'long_wait__invalid_status'

    utils_pg.insert_point_action(
        pgsql, waybill_ref, claim_point_id, action_type, reason_type,
    )

    await stq_runner.cargo_support_admin_segment_action.call(
        task_id='task_id_1',
        kwargs=build_stq_kwargs(
            waybill_ref,
            claim_point_id,
            action_type,
            # STQ arguments are ignored if point action already exists in DB.
            'long_wait__order_will_be_ready_before_timeout',
            admin_login='another_login',
            is_reorder_disabled_by_admin=True,
            is_cancelled_paid_arriving=True,
            is_cancelled_paid_waiting=True,
            is_fine_required=True,
            reorder_or_cancel_type='reorder',
        ),
    )

    point_action = utils_pg.select_point_action(
        pgsql, waybill_ref, claim_point_id, action_type,
    )

    check_point_action(
        point_action,
        waybill_ref,
        claim_point_id,
        action_type,
        reason_type,
        'success',
    )


@pytest.mark.pgsql('cargo_support')
@pytest.mark.parametrize(
    ['reorder_or_cancel_type', 'expected_forced_action'],
    [
        ('reorder', 'reorder_by_support_logics'),
        ('cancel', 'cancel_by_support_logics'),
    ],
)
@pytest.mark.parametrize(
    [
        'reorder_response_code',
        'reorder_response_body',
        'expected_action_status',
    ],
    [
        pytest.param(
            200, {'result': 'some text'}, 'success', id='reorder_200',
        ),
        pytest.param(
            404,
            {'code': '404', 'message': 'error 404'},
            'error',
            id='reorder_404',
        ),
        pytest.param(
            409,
            {'code': '409', 'message': 'error 409'},
            'conflict',
            id='reorder_409',
        ),
    ],
)
async def test_reorder(
        pgsql,
        mockserver,
        stq_runner,
        reorder_or_cancel_type,
        expected_forced_action,
        reorder_response_code,
        reorder_response_body,
        expected_action_status,
):
    waybill_ref = 'waybill_ref_1'
    claim_point_id = 1
    action_type = 'cancel_order'
    reason_type = 'cancel_order__order_ready_courier_not_arrived'

    @mockserver.json_handler('/cargo-dispatch/v1/admin/segment/autoreorder')
    def mock_autoreorder(request):
        assert request.query['corp_client_id'] == 'corp_client_id_1'
        assert request.query['claim_id'] == 'claim_id_1'
        assert request.json['performer_info']['park_id'] == 'park_id_1'
        assert request.json['performer_info']['driver_id'] == 'driver_id_1'
        assert request.json['reason'] == 'text reason'
        assert 'disable_batching' not in request.json
        assert request.json['reason_ids_chain'] == [action_type, reason_type]
        assert request.json['ticket'] == 'ticket_1'
        assert request.json['forced_action'] == expected_forced_action
        return mockserver.make_response(
            status=reorder_response_code, json=reorder_response_body,
        )

    await stq_runner.cargo_support_admin_segment_action.call(
        task_id='task_id_1',
        kwargs=build_stq_kwargs(
            waybill_ref,
            claim_point_id,
            action_type,
            reason_type,
            reorder_or_cancel_type=reorder_or_cancel_type,
        ),
    )

    point_action = utils_pg.select_point_action(
        pgsql, waybill_ref, claim_point_id, action_type,
    )

    check_point_action(
        point_action,
        waybill_ref,
        claim_point_id,
        action_type,
        reason_type,
        expected_action_status,
        reorder_or_cancel_type=reorder_or_cancel_type,
    )

    assert mock_autoreorder.times_called == 1
