import pytest

from testsuite.utils import matching

FALLBACK_ROUTER = 'fallback_router'
SMART_ROUTER = 'smart_router'
CHOOSE_ROUTERS_WORKER_NAME = 'cargo-dispatch-choose-routers'
CHOOSE_ROUTERS_EXPERIMENT3_NAME = 'segment_routers'

# pylint: disable=invalid-name
pytestmark = [pytest.mark.usefixtures('set_up_alive_batch_exp')]


async def test_admin_extra_routers_from_experiment(
        happy_path_state_first_import,
        experiments3,
        taxi_cargo_dispatch,
        run_choose_routers,
        get_admin_segment_info,
        segment_id='seg1',
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name=CHOOSE_ROUTERS_EXPERIMENT3_NAME,
        consumers=['cargo-dispatch/route_building_init'],
        clauses=[
            {
                'title': 'Clause #0',
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'segment_id',
                                    'set': [],  # nothing
                                    'set_elem_type': 'string',
                                },
                                'type': 'in_set',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {
                    'build_interval_seconds': 300,
                    'create_before_due_seconds': 1200,
                    'routers': [
                        {
                            'priority': 10,
                            'router_id': 'invalid_router',
                            'autoreorder_flow': 'invalid_flow',
                        },
                    ],
                },
            },
            {
                'title': 'Clause #1',
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'segment_id',
                                    'set': [
                                        'seg1',
                                        'seg2',
                                        'seg3',
                                        'seg5',
                                        'seg6',
                                    ],
                                    'set_elem_type': 'string',
                                },
                                'type': 'in_set',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {
                    'build_interval_seconds': 300,
                    'create_before_due_seconds': 1200,
                    'routers': [
                        {
                            'priority': 10,
                            'router_id': SMART_ROUTER,
                            'autoreorder_flow': 'newway',
                        },
                        {
                            'priority': 100,
                            'router_id': FALLBACK_ROUTER,
                            'autoreorder_flow': 'newway',
                        },
                    ],
                },
            },
        ],
        default_value={
            'build_interval_seconds': 300,
            'create_before_due_seconds': 1200,
            'routers': [
                {
                    'priority': 10,
                    'router_id': 'invalid_router',
                    'autoreorder_flow': 'invalid_flow',
                },
            ],
        },
    )
    await taxi_cargo_dispatch.invalidate_caches()

    await run_choose_routers()

    seginfo = await get_admin_segment_info(segment_id)
    assert seginfo['dispatch']['admin_extra']['routers'] == [
        {
            'autoreorder_flow': 'newway',
            'id': 'smart_router',
            'is_deleted': False,
            'matched_experiment': {
                'clause_index': '1',
                'name': 'segment_routers',
            },
            'priority': 10,
            'source': 'cargo-dispatch-choose-routers',
        },
        {
            'autoreorder_flow': 'newway',
            'id': 'fallback_router',
            'is_deleted': False,
            'matched_experiment': {
                'clause_index': '1',
                'name': 'segment_routers',
            },
            'priority': 100,
            'source': 'cargo-dispatch-choose-routers',
        },
    ]


async def test_admin_extra_routers_from_experiment_with_default_clause(
        happy_path_state_first_import,
        experiments3,
        taxi_cargo_dispatch,
        run_choose_routers,
        get_admin_segment_info,
        segment_id='seg1',
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name=CHOOSE_ROUTERS_EXPERIMENT3_NAME,
        consumers=['cargo-dispatch/route_building_init'],
        clauses=[],
        default_value={
            'build_interval_seconds': 300,
            'create_before_due_seconds': 1200,
            'routers': [
                {
                    'priority': 100,
                    'router_id': FALLBACK_ROUTER,
                    'autoreorder_flow': 'newway',
                },
            ],
        },
    )
    await taxi_cargo_dispatch.invalidate_caches()

    await run_choose_routers()

    seginfo = await get_admin_segment_info(segment_id)
    assert seginfo['dispatch']['admin_extra']['routers'] == [
        {
            'autoreorder_flow': 'newway',
            'id': 'fallback_router',
            'is_deleted': False,
            'matched_experiment': {
                'clause_index': 'default',
                'name': 'segment_routers',
            },
            'priority': 100,
            'source': 'cargo-dispatch-choose-routers',
        },
    ]


async def test_admin_extra_routers_after_manual_assign(
        happy_path_state_first_import,
        taxi_cargo_dispatch,
        get_admin_segment_info,
        segment_id='seg1',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/assign-manually', params={'segment_id': segment_id},
    )
    assert response.status_code == 200
    assert response.json() == {}

    seginfo = await get_admin_segment_info(segment_id)
    assert seginfo['dispatch']['admin_extra']['routers'] == [
        {
            'id': 'fallback_router',
            'is_deleted': False,
            'priority': 0,
            'source': 'manual-assign',
        },
    ]


async def test_performer_cancel_reorders(
        happy_path_segment_after_reorder,
        taxi_cargo_dispatch,
        waybill_ref='waybill_fb_3',
        segment_id='seg3',
):
    seginfo = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/info', params={'segment_id': segment_id},
    )
    assert seginfo.status_code == 200

    reorders = seginfo.json()['dispatch']['admin_extra']['reorders']
    assert len(reorders) == 1
    assert reorders[0] == {
        'cargo_order_id': matching.AnyString(),
        'reordered_at': matching.AnyString(),
        'provider_order_id': matching.AnyString(),
        'reason': 'performer_cancel',
        'ticket': '',
        'source': 'mark_order_fail: autoreorder_unknown_service',
        'waybill_building_version': 1,
        'waybill_ref': waybill_ref,
        'order_fail_reason': 'performer_cancel',
    }


async def test_performer_cancel_reorders_with_cargo_reason(
        happy_path_segment_after_reorder,
        taxi_cargo_dispatch,
        mock_cargo_orders_bulk_info,
        waybill_ref='waybill_fb_3',
        segment_id='seg3',
):
    seginfo = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/info', params={'segment_id': segment_id},
    )
    assert seginfo.status_code == 200

    reorders = seginfo.json()['dispatch']['admin_extra']['reorders']
    assert len(reorders) == 1
    reorder = reorders[0]

    mock_cargo_orders_bulk_info(
        order_cancel_performer_reason=[
            {
                'taxi_order_id': reorder['provider_order_id'],
                'cargo_cancel_reason': 'cargo_reason',
                'taxi_cancel_reason': 'taxi_reason',
                'park_id': 'park',
                'driver_id': 'driver',
                'created_ts': '2021-05-31T19:00:00+00:00',
                'completed': True,
                'guilty': True,
                'need_reorder': True,
                'free_cancellations_limit_exceeded': False,
            },
        ],
    )

    seginfo = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/info', params={'segment_id': segment_id},
    )
    assert seginfo.status_code == 200

    reorders = seginfo.json()['dispatch']['admin_extra']['reorders']
    assert len(reorders) == 1
    assert reorders[0] == {
        'cargo_order_id': matching.AnyString(),
        'reordered_at': matching.AnyString(),
        'provider_order_id': matching.AnyString(),
        'reason': 'cargo_reason',
        'ticket': '',
        'source': 'mark_order_fail: autoreorder_unknown_service',
        'waybill_building_version': 1,
        'waybill_ref': waybill_ref,
        'order_fail_reason': 'performer_cancel',
    }


async def test_reorders_order_cancel_performer_reason(
        taxi_cargo_dispatch,
        happy_path_state_fallback_waybills_proposed,
        read_waybill_info,
        waybill_id='waybill_fb_3',
        segment_id='seg3',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json={
            'order_id': 'b66b2650-31b5-46d2-95dc-5ff80f865c6f',
            'waybill_id': waybill_id,
            'taxi_order_id': 'taxi-order',
            'reason': 'failed',
            'lookup_version': 0,
        },
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'resolved'

    seginfo = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/info', params={'segment_id': segment_id},
    )
    assert seginfo.status_code == 200
    assert not seginfo.json()['dispatch']['admin_extra']['reorders']


async def test_admin_replaced_info(
        happy_path_state_performer_found,
        happy_path_state_seg4_routers_chosen,
        taxi_cargo_dispatch,
        run_choose_waybills,
        waybill_from_segments,
        request_waybill_update_proposition,
        mock_cargo_orders_bulk_info,
        update_proposition_alive_batch_stq,
):
    """
        fallback_router proposed waybill_fb_3 {seg3}.
        fallback_router proposed update waybill_on_seg3_seg4 {seg3, seg4}.

        Check for 'waybill_fb_3' in list of replaced waybills for 'seg3'.
    """
    mock_cargo_orders_bulk_info(tariff_class='eda')

    # Propose waybill update
    proposition = await waybill_from_segments(
        'fallback_router', 'waybill_on_seg3_seg4', 'seg3', 'seg4',
    )
    response = await request_waybill_update_proposition(
        proposition, 'waybill_fb_3',
    )
    assert response.status_code == 200

    await run_choose_waybills()
    await update_proposition_alive_batch_stq(
        'waybill_on_seg3_seg4', wait_testpoint=False, call=True,
    )

    seginfo = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/info', params={'segment_id': 'seg3'},
    )
    assert seginfo.status_code == 200

    assert seginfo.json()['dispatch']['admin_extra']['replaced_waybills'] == [
        {
            'replaced_at': matching.AnyString(),
            'waybill_building_version': 1,
            'waybill_ref': 'waybill_fb_3',
        },
    ]


async def test_admin_declined_info(
        happy_path_state_performer_found, taxi_cargo_dispatch,
):
    """
        fallback_router proposed waybill_fb_1 {seg1}.
        smart_router proposed update waybill_smart_1 {seg1, seg2}.
        smart_router won.

        Check for 'waybill_fb_1' in list of declined waybills for 'seg1'.
    """
    seginfo = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/info', params={'segment_id': 'seg1'},
    )
    assert seginfo.status_code == 200

    assert seginfo.json()['dispatch']['admin_extra']['declined_waybills'] == [
        {
            'declined_at': matching.AnyString(),
            'waybill_building_version': 1,
            'waybill_ref': 'waybill_fb_1',
            'router_id': 'fallback_router',
            'priority': 100,
            'created_at': matching.AnyString(),
        },
    ]


async def test_segment_info_admin(
        happy_path_state_first_import, get_segment_info, taxi_cargo_dispatch,
):
    seginfo_admin = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/info',
        params={'segment_id': 'seg1'},
        json={},
        headers={'Accept-Language': 'ru', 'X-Remote-Ip': '0.0.0.0'},
    )
    assert seginfo_admin.status_code == 200
    assert 'segment' in seginfo_admin.json()
    seginfo = await get_segment_info('seg1')
    assert seginfo['segment']['id'] == seginfo_admin.json()['segment']['id']


async def test_admin_segment_resolution(
        happy_path_state_first_import,
        taxi_cargo_dispatch,
        happy_path_claims_segment_db,
        segment_id='seg1',
):
    happy_path_claims_segment_db.cancel_segment_by_user(segment_id)

    seginfo = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/info', params={'segment_id': segment_id},
    )
    assert seginfo.status_code == 200

    assert seginfo.json()['segment']['resolution'] == 'cancelled_by_user'


async def test_admin_actions_when_order_created(
        happy_path_state_orders_created,
        taxi_cargo_dispatch,
        mockserver,
        segment_id='seg3',
):
    @mockserver.json_handler('/cargo-orders/v1/orders/bulk-info')
    async def _handler(request):
        return {'orders': []}

    seginfo = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/info', params={'segment_id': segment_id},
    )
    assert seginfo.status_code == 200
    assert seginfo.json()['actions'] == [
        {'action': 'assign_manually', 'title': 'Назначить вручную'},
    ]


@pytest.mark.config(CARGO_DISPATCH_ENABLE_ADMIN_AUTOREORDER_BY_PERFORMER=True)
async def test_admin_actions_when_performer_found(
        happy_path_state_performer_found,
        taxi_cargo_dispatch,
        segment_id='seg3',
):
    seginfo = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/info', params={'segment_id': segment_id},
    )
    assert seginfo.status_code == 200
    assert seginfo.json()['actions'] == [
        {
            'action': 'autoreorder_by_service',
            'title': 'Отменить заказ по вине сервиса (автореордер без штрафа)',
        },
        {
            'action': 'autoreorder_by_performer',
            'title': 'Отменить заказ по вине водителя (автореордер)',
        },
    ]


@pytest.mark.config(
    CARGO_DISPATCH_ORDER_ADMIN_CANCEL_MENU_V2={
        'enabled': True,
        'cancel_button_tanker_key': 'order_cancel',
        'cancel_reason_tree': [
            {
                'childs': [
                    {
                        'activity_remove_tanker_key': (
                            'actions.segment.admin_performer_penalty_message'
                        ),
                        'id': 'reason_performer_blame',
                        'need_autoreorder_tanker_key': (
                            'actions.segment.admin_autoreorder_message'
                        ),
                        'menu_item_tanker_key': 'reason_performer_blame',
                    },
                ],
                'id': 'performer blame',
                'menu_item_tanker_key': 'performer_blame',
            },
        ],
    },
)
async def test_admin_actions_when_order_cancel_available(
        happy_path_state_performer_found,
        taxi_cargo_dispatch,
        segment_id='seg3',
):
    seginfo = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/info', params={'segment_id': segment_id},
    )
    assert seginfo.status_code == 200
    assert seginfo.json()['actions'] == [
        {'action': 'autoreorder', 'title': 'actions.segment.autoreorder'},
        {
            'action': 'order_cancel',
            'title': 'order_cancel',
            'menu': [
                {
                    'childs': [
                        {
                            'id': 'reason_performer_blame',
                            'title': 'reason_performer_blame',
                            'need_autoreorder_alert_message': (
                                'Будет выполнен автореордер'
                            ),
                            'activity_remove_alert_message': (
                                'Будет выписан штраф исполнителю'
                            ),
                            'action_type': 'autoreorder',
                        },
                    ],
                    'id': 'performer blame',
                    'title': 'performer_blame',
                    'action_type': 'cancel',
                },
            ],
        },
    ]


async def test_admin_actions_when_point_visited(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        taxi_cargo_dispatch,
        segment_id='seg3',
):
    segment = happy_path_claims_segment_db.get_segment(segment_id)
    segment.json['points'][0]['is_resolved'] = True

    seginfo = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/info', params={'segment_id': segment_id},
    )
    assert seginfo.status_code == 200
    assert seginfo.json()['actions'] == []


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
async def test_admin_segment_orders(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        get_admin_segment_info,
        waybill_mark_order_fail,
        mock_order_cancel,
        pgsql,
        is_reorder_required: bool,
        segment_id='seg1',
        waybill_id='waybill_smart_1',
        ticket='CHATTERBOX-22',
        fail_reason='performer_cancel',
):
    reason_ids_chain = ['some_reason', 'some_details']
    admin_cancel_reason = '.'.join(reason_ids_chain)
    reorder_reason = ': '.join(reason_ids_chain)

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

    await waybill_mark_order_fail(
        waybill_id,
        fail_reason,
        ticket=ticket,
        admin_cancel_reason=admin_cancel_reason,
        is_reorder_required=is_reorder_required,
    )

    segment_info_json = await get_admin_segment_info(segment_id)
    reorders = segment_info_json['dispatch']['admin_extra']['reorders']
    if is_reorder_required:
        assert len(reorders) == 1
        assert reorders[0] == {
            'cargo_order_id': matching.AnyString(),
            'reordered_at': matching.AnyString(),
            'provider_order_id': matching.AnyString(),
            'waybill_building_version': 1,
            'waybill_ref': waybill_id,
            'order_fail_reason': 'performer_cancel',
            'ticket': ticket,
            'reason': reorder_reason,
            'source': 'waybill_autoreorder: autoreorder_unknown_service',
        }
    else:
        assert not reorders


async def test_admin_sdd_segment_info(
        mockserver,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        taxi_cargo_dispatch,
        segment_id='seg3',
):
    sdd_info = {
        'status': 'waybill_proposed',
        'status_description': 'waybill_proposed ru',
        'delivery_interval': {
            'from': '2020-01-01T00:00:00+00:00',
            'to': '2020-01-01T00:01:00+00:00',
        },
        'routing_task_id': 'task_id',
    }

    @mockserver.json_handler('/cargo-sdd/admin/v1/segment/status')
    async def _handler(request):
        assert request.headers['Accept-Language'] == 'ru'
        assert request.json['segment_id'] == segment_id
        return sdd_info

    segment = happy_path_claims_segment_db.get_segment(segment_id)
    segment.json['same_day_data'] = {
        'delivery_interval': {
            'from': '2020-01-01T00:00:00+00:00',
            'to': '2020-01-01T00:01:00+00:00',
        },
    }

    seginfo = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/info', params={'segment_id': segment_id},
    )
    assert seginfo.status_code == 200
    assert seginfo.json()['same_day'] == sdd_info


@pytest.mark.config(
    CARGO_DISPATCH_ORDER_ADMIN_CANCEL_MENU_V2={
        'enabled': True,
        'cancel_button_tanker_key': 'order_cancel',
        'cancel_reason_tree': [],
    },
)
async def test_monitoring_actions_happy_path(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        taxi_cargo_dispatch,
        set_up_admin_actions_execution_exp,
        set_up_admin_actions_exp,
        segment_id='seg3',
):
    await set_up_admin_actions_execution_exp()
    await set_up_admin_actions_exp()

    segment = happy_path_claims_segment_db.get_segment(segment_id)
    segment.set_point_visit_status('p1', 'arrived')

    seginfo = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/info', params={'segment_id': segment_id},
    )
    assert seginfo.status_code == 200
    assert seginfo.json()['actions'] == [
        {'action': 'autoreorder', 'title': 'actions.segment.autoreorder'},
        {
            'action': 'order_cancel',
            'title': 'order_cancel',
            'menu': [
                {
                    'action_type': 'cancel',
                    'id': 'cancel_order',
                    'title': 'ru cancel_order',
                    'childs': [
                        {
                            'action_type': 'autoreorder',
                            'activity_remove_alert_message': (
                                'Будет выполнена ' 'отмена'
                            ),
                            'allow_autoreorder_checkbox': 'Разрешить реордер',
                            'id': (
                                'cancel_order__order_ready_courier_not_arrived'
                            ),
                            'need_autoreorder_alert_message': (
                                'Будет выполнен ' 'автореордер'
                            ),
                            'title': 'Заказ готов. Курьер не приехал.',
                        },
                        {
                            'action_type': 'cancel',
                            'activity_remove_alert_message': (
                                'Будет выполнена ' 'отмена'
                            ),
                            'id': 'cancel_order__invalid_status',
                            'title': 'Курьер не прожал статус.',
                        },
                    ],
                },
            ],
        },
    ]


@pytest.mark.config(
    CARGO_DISPATCH_ORDER_ADMIN_CANCEL_MENU_V2={
        'enabled': True,
        'cancel_button_tanker_key': 'order_cancel',
        'cancel_reason_tree': [],
    },
)
async def test_monitoring_actions_not_arrived(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        taxi_cargo_dispatch,
        set_up_admin_actions_execution_exp,
        set_up_admin_actions_exp,
        segment_id='seg3',
):
    await set_up_admin_actions_execution_exp()
    await set_up_admin_actions_exp()

    segment = happy_path_claims_segment_db.get_segment(segment_id)
    segment.set_point_visit_status('p1', 'pending')

    seginfo = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/info', params={'segment_id': segment_id},
    )
    assert seginfo.status_code == 200
    assert seginfo.json()['actions'] == [
        {'action': 'autoreorder', 'title': 'actions.segment.autoreorder'},
        {'action': 'order_cancel', 'menu': [], 'title': 'order_cancel'},
    ]
