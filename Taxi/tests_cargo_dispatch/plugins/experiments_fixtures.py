import pytest


@pytest.fixture(name='set_up_cargo_dispatch_reorder_exp')
async def _set_up_cargo_dispatch_reorder_exp(
        experiments3, taxi_cargo_dispatch,
):
    async def wrapper(
            *,
            reorder_times: int = 1,
            fail_reason: str = 'performer_cancel',
            with_seconds_since_first_lookup: bool = False,
            is_reorder_required: bool = True,
            admin_cancel_reason_null=None,
            performer_cancel_need_reorder=None,
    ):
        predicates = [
            {
                'init': {
                    'value': reorder_times,
                    'arg_name': 'reorder_times',
                    'arg_type': 'int',
                },
                'type': 'lt',
            },
            {
                'init': {
                    'value': fail_reason,
                    'arg_name': 'fail_reason',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
        ]
        if performer_cancel_need_reorder is not None:
            predicates.append(
                {
                    'init': {'arg_name': 'performer_cancel_need_reorder'},
                    'type': 'bool',
                },
            )
        if admin_cancel_reason_null:
            predicates.append(
                {
                    'init': {'arg_name': 'admin_cancel_reason'},
                    'type': (
                        'is_null' if admin_cancel_reason_null else 'not_null'
                    ),
                },
            )
        if with_seconds_since_first_lookup:
            # more than hour in future
            predicates.append(
                {
                    'init': {
                        'value': -3600,
                        'arg_name': 'seconds_since_first_lookup',
                        'arg_type': 'int',
                    },
                    'type': 'gt',
                },
            )

        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_dispatch_reorder',
            consumers=['cargo-dispatch/mark-order-fail'],
            clauses=[
                {
                    'title': 'clause',
                    'predicate': {
                        'init': {'predicates': predicates},
                        'type': 'all_of',
                    },
                    'value': {
                        'is_reorder_required': is_reorder_required,
                        'reason': 'matched_common_clause',
                    },
                },
            ],
            default_value={
                'is_reorder_required': False,
                'reason': 'no_clauses_matched',
            },
        )
        await taxi_cargo_dispatch.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='set_up_segment_routers_exp')
async def _set_up_segment_routers_exp(experiments3, taxi_cargo_dispatch):
    async def wrapper(
            *,
            recipient_phone: str = None,
            source_point: list = None,
            build_window_seconds: int = None,
            build_interval_for_due_segments: int = None,
            allow_alive_batch_v1: bool = None,
            allow_alive_batch_v2: bool = None,
            smart_router: str = 'smart_router',
            autoreorder_flow: str = 'newway',
            router_intent: str = None,
    ):
        predicates = [
            {
                'init': {
                    'arg_name': 'segment_id',
                    'set': ['seg1', 'seg2', 'seg4', 'seg6'],
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
        ]
        if recipient_phone is not None:
            predicates.append(
                {
                    'init': {
                        'value': recipient_phone,
                        'arg_name': 'recipients_phones',
                        'set_elem_type': 'string',
                    },
                    'type': 'contains',
                },
            )
        if source_point is not None:
            delta = 0.000001
            square = []
            square.append([source_point[0] - delta, source_point[1] - delta])
            square.append([source_point[0] + delta, source_point[1] - delta])
            square.append([source_point[0] + delta, source_point[1] + delta])
            square.append([source_point[0] - delta, source_point[1] + delta])

            predicates.append(
                {
                    'type': 'falls_inside',
                    'init': {
                        'arg_name': 'source_point',
                        'arg_type': 'linear_ring',
                        'value': square,
                    },
                },
            )
        if router_intent is not None:
            predicates.append(
                {
                    'init': {
                        'value': router_intent,
                        'arg_name': 'router_intent',
                        'arg_type': 'string',
                    },
                    'type': 'eq',
                },
            )

        matched_value = {
            'build_interval_seconds': 300,
            'create_before_due_seconds': 1200,
            'routers': [
                {
                    'priority': 10,
                    'router_id': smart_router,
                    'autoreorder_flow': autoreorder_flow,
                },
                {
                    'priority': 100,
                    'router_id': 'fallback_router',
                    'autoreorder_flow': autoreorder_flow,
                },
            ],
        }
        if build_window_seconds is not None:
            matched_value['build_window_seconds'] = build_window_seconds
        if build_interval_for_due_segments is not None:
            matched_value[
                'build_interval_for_due_segments_seconds'
            ] = build_interval_for_due_segments
        if allow_alive_batch_v1 is not None:
            matched_value['allow_alive_batch_v1'] = allow_alive_batch_v1
        if allow_alive_batch_v2 is not None:
            matched_value['allow_alive_batch_v2'] = allow_alive_batch_v2

        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='segment_routers',
            consumers=['cargo-dispatch/route_building_init'],
            clauses=[
                {
                    'title': 'clause',
                    'predicate': {
                        'init': {'predicates': predicates},
                        'type': 'all_of',
                    },
                    'value': matched_value,
                },
            ],
            default_value={
                'build_interval_seconds': 60,
                'create_before_due_seconds': 1200,
                'routers': [
                    {
                        'priority': 100,
                        'router_id': 'fallback_router',
                        'autoreorder_flow': autoreorder_flow,
                    },
                ],
            },
        )
        await taxi_cargo_dispatch.invalidate_caches()

    return wrapper


@pytest.fixture(name='exp_cargo_next_point_eta_settings')
async def _exp_cargo_next_point_eta_settings(
        experiments3, taxi_cargo_dispatch,
):
    async def wrapper(
            extra_eta_seconds=None, extra_eta_position_age_multiplier=None,
    ):
        result = {'enable': True, 'allow_no_eta_on_error': False}
        if extra_eta_seconds is not None:
            result['extra_eta_seconds'] = extra_eta_seconds
        if extra_eta_position_age_multiplier is not None:
            result[
                'extra_eta_position_age_multiplier'
            ] = extra_eta_position_age_multiplier
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_next_point_eta_settings',
            consumers=['cargo-dispatch/taximeter-actions'],
            clauses=[],
            default_value=result,
        )
        await taxi_cargo_dispatch.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='set_up_alive_batch_exp')
def _set_up_alive_batch_exp(load_json, experiments3):
    experiments_json = load_json('exp3_cargo_alive_batch_settings.json')
    experiments3.add_experiments_json(experiments_json)


def build_predicate_admin_actions(action_type, point_type, point_visit_status):
    return {
        'init': {
            'predicates': [
                {
                    'init': {
                        'value': action_type,
                        'arg_name': 'action_type',
                        'arg_type': 'string',
                    },
                    'type': 'eq',
                },
                {
                    'init': {
                        'value': point_type,
                        'arg_name': 'point_type',
                        'arg_type': 'string',
                    },
                    'type': 'eq',
                },
                {
                    'init': {
                        'value': point_visit_status,
                        'arg_name': 'point_visit_status',
                        'arg_type': 'string',
                    },
                    'type': 'eq',
                },
            ],
        },
        'type': 'all_of',
    }


@pytest.fixture(name='set_up_admin_actions_exp')
async def _set_up_admin_actions_exp(experiments3, taxi_cargo_dispatch):
    async def wrapper():
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_dispatch_admin_actions',
            consumers=['cargo-dispatch/admin-actions'],
            clauses=[
                {
                    'title': 'clause1',
                    'predicate': build_predicate_admin_actions(
                        'long_wait', 'pickup', 'arrived',
                    ),
                    'value': {
                        'action': {
                            'action_type': 'long_wait',
                            'action_title_key': 'actions.long_wait',
                            'reason_order_will_be_ready_before_timeout': {
                                'reason_title_key': (
                                    'actions.long_wait.reason'
                                    + '.order_will_be_ready_before_timeout'
                                ),
                            },
                            'reason_invalid_status': {
                                'reason_title_key': (
                                    'actions.long_wait.reason.invalid_status'
                                ),
                            },
                        },
                    },
                },
                {
                    'title': 'clause2',
                    'predicate': build_predicate_admin_actions(
                        'cancel_order', 'pickup', 'arrived',
                    ),
                    'value': {
                        'action': {
                            'action_type': 'cancel_order',
                            'action_title_key': 'actions.cancel_order',
                            'reason_order_ready_courier_not_arrived': {
                                'reason_title_key': (
                                    'actions.cancel_order.reason'
                                    + '.order_ready_courier_not_arrived'
                                ),
                                'cancel_message_key': (
                                    'actions.segment.admin_cancel_message'
                                ),
                                'reorder_message_key': (
                                    'actions.segment.admin_autoreorder_message'
                                ),
                                'reorder_checkbox_key': (
                                    'actions.segment.admin_reorder_checkbox'
                                ),
                            },
                            'reason_invalid_status': {
                                'reason_title_key': (
                                    'actions.cancel_order.reason'
                                    + '.invalid_status'
                                ),
                                'cancel_message_key': (
                                    'actions.segment.admin_cancel_message'
                                ),
                            },
                        },
                    },
                },
                {
                    'title': 'clause3',
                    'predicate': build_predicate_admin_actions(
                        'fake_return', 'pickup', 'arrived',
                    ),
                    'value': {
                        'action': {
                            'action_type': 'fake_return',
                            'action_title_key': 'actions.fake_return',
                            'reason_receiver_answered': {
                                'reason_title_key': (
                                    'actions.fake_return.reason'
                                    + '.receiver_answered'
                                ),
                            },
                            'reason_invalid_status': {
                                'reason_title_key': (
                                    'actions.fake_return.reason.invalid_status'
                                ),
                            },
                        },
                    },
                },
            ],
            default_value={},
        )
        await taxi_cargo_dispatch.invalidate_caches()

    return wrapper


def build_clause_actions_execution(
        reason_type,
        reorder_or_cancel_type,
        cancel_paid_arriving,
        cancel_paid_waiting,
        fine,
):
    return {
        'title': 'clause_' + reason_type,
        'predicate': {
            'init': {
                'value': reason_type,
                'arg_name': 'reason_type',
                'arg_type': 'string',
            },
            'type': 'eq',
        },
        'value': {
            'reorder_or_cancel_type': reorder_or_cancel_type,
            'cancel_paid_arriving': cancel_paid_arriving,
            'cancel_paid_waiting': cancel_paid_waiting,
            'fine': fine,
        },
    }


@pytest.fixture(name='set_up_admin_actions_execution_exp')
async def _set_up_admin_actions_execution_exp(
        experiments3, taxi_cargo_dispatch,
):
    async def wrapper():
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_support_admin_actions_execution',
            consumers=['cargo-dispatch/admin-actions-execution'],
            clauses=[
                build_clause_actions_execution(
                    'long_wait__order_will_be_ready_before_timeout',
                    'none',
                    False,
                    False,
                    False,
                ),
                build_clause_actions_execution(
                    'long_wait__invalid_status', 'none', False, True, True,
                ),
                build_clause_actions_execution(
                    'cancel_order__order_ready_courier_not_arrived',
                    'reorder',
                    True,
                    True,
                    True,
                ),
                build_clause_actions_execution(
                    'cancel_order__invalid_status', 'cancel', True, True, True,
                ),
            ],
            default_value={
                'reorder_or_cancel_type': 'none',
                'cancel_paid_arriving': False,
                'cancel_paid_waiting': False,
                'fine': False,
            },
        )
        await taxi_cargo_dispatch.invalidate_caches()

    return wrapper
