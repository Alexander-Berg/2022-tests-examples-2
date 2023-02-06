import pytest


_CARGO_POINT_COMMENT_FEATURES_MERGE_TAG = [
    {
        'consumer': 'cargo-orders/build-features-comment',
        'merge_method': 'dicts_recursive_merge',
        'tag': 'cargo_point_comment_features',
    },
    {
        'consumer': 'cargo-orders/build-point-comment',
        'merge_method': 'dicts_recursive_merge',
        'tag': 'cargo_point_comment_features',
    },
]


@pytest.fixture
async def exp_cargo_voiceforwarding(taxi_cargo_orders, experiments3):
    async def wrapper(*, enabled: bool = True, fallback_type: str = 'error'):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_orders_voiceforwarding',
            consumers=['cargo-orders/voiceforwarding'],
            clauses=[],
            default_value={
                'enabled': enabled,
                'fallback_type': fallback_type,
                'phone_ttl_sec': 1000,
            },
        )
        await taxi_cargo_orders.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='set_up_cargo_orders_performer_localization_exp')
async def _set_up_cargo_orders_performer_localization_exp(
        experiments3, taxi_cargo_orders,
):
    async def wrapper(
            *,
            enabled: bool = True,
            skip_on_error: bool = True,
            use_fullname: bool = True,
            use_uri: bool = True,
            shortname_no_entrance: bool = False,
            add_city_to_shortname: bool = False,
            warning_distance: int = 100,
            max_distance: int = None,
            check_shortname_building: bool = None,
            build_shortname: bool = None,
    ):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_orders_performer_localization',
            consumers=['cargo-orders/taximeter-api'],
            clauses=[],
            default_value={
                'enabled': enabled,
                'skip_on_error': skip_on_error,
                'use_fullname': use_fullname,
                'use_uri': use_uri,
                'shortname_no_entrance': shortname_no_entrance,
                'add_city_to_shortname': add_city_to_shortname,
                'max_distance': max_distance,
                'warning_distance': warning_distance,
                'check_shortname_building': check_shortname_building,
                'build_shortname': build_shortname,
            },
        )
        await taxi_cargo_orders.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='exp_cargo_orders_timers_settings')
async def _exp_cargo_orders_timers_settings(experiments3, taxi_cargo_orders):
    async def wrapper():
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_orders_timers_settings',
            consumers=['cargo-orders/build-actions'],
            clauses=[
                {
                    'title': 'clause',
                    'predicate': {
                        'init': {
                            'predicate': {
                                'init': {
                                    'arg_name': 'point_status',
                                    'arg_type': 'string',
                                    'value': 'pending',
                                },
                                'type': 'eq',
                            },
                        },
                        'type': 'not',
                    },
                    'value': {'hide_eta': True},
                },
            ],
            default_value={'hide_eta': False},
        )
        await taxi_cargo_orders.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='exp_cargo_orders_show_price_on_order_card')
async def _exp_cargo_orders_show_price_on_order_card(
        experiments3, taxi_cargo_orders,
):
    async def wrapper():
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_orders_show_price_on_order_card',
            consumers=['cargo-orders/price-showing-settings'],
            clauses=[],
            default_value={'hide_price': True},
        )
        await taxi_cargo_orders.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='exp_cargo_orders_post_payment_flow')
async def _exp_cargo_orders_post_payment_flow(experiments3, taxi_cargo_orders):
    async def wrapper(
            *,
            with_dropoff_title=True,
            on_point_comment='comment.point_post_payment',
    ):
        value = {
            'enabled': True,
            'title_tanker_key': 'actions.post_payment_flow.title',
            'service': 'cargo-payments',
        }
        if with_dropoff_title:
            value[
                'dropoff_title_tanker_key'
            ] = 'actions.post_payment_flow.title'
        if on_point_comment is not None:
            value['on_point_comment'] = on_point_comment
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_orders_post_payment_flow',
            consumers=[
                'cargo-claims/driver',
                'cargo-orders/build-features-comment',
            ],
            clauses=[],
            default_value=value,
        )
        await taxi_cargo_orders.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='exp_cargo_point_comment_features')
async def _exp_cargo_point_comment_features(experiments3, taxi_cargo_orders):
    async def wrapper(*, post_payment_comment='comment.point_post_payment'):
        matched_common = {
            'extra_comments': [{'text_tanker_key': post_payment_comment}],
        }
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_orders_post_payment_flow',
            consumers=[
                'cargo-orders/build-features-comment',
                'cargo-orders/build-point-comment',
            ],
            clauses=[],
            default_value={'single_config': matched_common},
            merge_values_by=_CARGO_POINT_COMMENT_FEATURES_MERGE_TAG,
        )
        await taxi_cargo_orders.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='exp_cargo_orders_on_point_phones')
async def _exp_cargo_orders_on_point_phones(experiments3, taxi_cargo_orders):
    async def wrapper(
            phone_type='payment_on_delivery_support',
            tanker_key='yandex_pro.phones.payment_on_delivery_support',
            view='extra',
            overrides=None,
    ):
        if overrides is None:
            overrides = [
                {
                    'phone_type': phone_type,
                    'visible': {'tanker_key': tanker_key, 'view': view},
                },
            ]
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_orders_on_point_phones',
            consumers=['cargo-orders/build-point-comment'],
            clauses=[],
            default_value={'overrides': overrides},
        )
        await taxi_cargo_orders.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='exp_cargo_orders_payment_on_delivery_phone')
async def _exp_cargo_orders_payment_on_delivery_phone(
        experiments3, taxi_cargo_orders,
):
    async def wrapper(*, override_emergency=False):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_orders_payment_on_delivery_phone',
            consumers=['cargo-orders/voiceforwarding'],
            clauses=[],
            default_value={
                'support_phone': '+74449990000',
                'override_emergency': override_emergency,
            },
        )
        await taxi_cargo_orders.invalidate_caches()

    await wrapper()
    return wrapper


ROBOCALL_ACTIONS_VALUE = {
    'enabled': True,
    'config': {
        'tanker_keys': {
            'action_button': {
                'client_doesnt_answer': (
                    'actions.robocall.button.client_doesnt_answer'
                ),
                'robocall_in_progress': (
                    'actions.robocall.button.robocall_in_progress'
                ),
            },
            'dialog_in_progress': {
                'title': 'actions.robocall.dialog_in_progress.title',
                'button': 'actions.robocall.dialog_in_progress.button',
                'message': 'actions.robocall.dialog_in_progress.message',
            },
            'dialog_client_answered': {
                'title': 'actions.robocall.dialog_client_answered.title',
                'button': 'actions.robocall.dialog_client_answered.button',
                'message': 'actions.robocall.dialog_client_answered.message',
            },
            'dialog_order_cancelled': {
                'title': 'actions.robocall.dialog_order_cancelled.title',
                'button': 'actions.robocall.dialog_order_cancelled.button',
                'message': 'actions.robocall.dialog_order_cancelled.message',
            },
            'dialog_client_not_answered': {
                'title': 'actions.robocall.dialog_client_not_answered.title',
                'button': 'actions.robocall.dialog_client_not_answered.button',
                'message': (
                    'actions.robocall.dialog_client_not_answered.message'
                ),
            },
            'dialog_client_answered_long_ago': {
                'title': (
                    'actions.robocall.dialog_client_answered_long_ago.title'
                ),
                'button': (
                    'actions.robocall.dialog_client_answered_long_ago.button'
                ),
                'message': (
                    'actions.robocall.dialog_client_answered_long_ago.message'
                ),
            },
        },
        'client_contacts_courier_timeout_sec': 540,
        'robocall_timer_additional_time_sec': 60,
        'min_call_count': 1,
        'disable_robocall_if_courier_is_too_early_sec': 1200,
    },
}


def build_robocall_actions_value(time_after_signed_offset_sec):
    value = ROBOCALL_ACTIONS_VALUE

    if time_after_signed_offset_sec is not None:
        value['config'][
            'condition_time_after_signed_offset_sec'
        ] = time_after_signed_offset_sec

    return value


@pytest.fixture(name='exp_cargo_orders_robocall_actions')
async def _exp_cargo_orders_robocall_actions(experiments3, taxi_cargo_orders):
    async def wrapper(
            *,
            robocall_reason='client_not_responding',
            time_after_signed_offset_sec=None,
    ):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_orders_robocall_actions',
            consumers=['cargo-orders/build-robocall-actions'],
            clauses=[
                {
                    'title': 'Point status',
                    'value': build_robocall_actions_value(
                        time_after_signed_offset_sec,
                    ),
                    'predicate': {
                        'init': {
                            'predicates': [
                                {
                                    'init': {
                                        'set': [
                                            'delivery_arrived',
                                            'ready_for_delivery_confirmation',
                                            'pay_waiting',
                                        ],
                                        'arg_name': 'claim_status',
                                        'set_elem_type': 'string',
                                    },
                                    'type': 'in_set',
                                },
                                {
                                    'init': {
                                        'value': robocall_reason,
                                        'arg_name': 'robocall_reason',
                                        'arg_type': 'string',
                                    },
                                    'type': 'eq',
                                },
                            ],
                        },
                        'type': 'all_of',
                    },
                },
            ],
            default_value={'enabled': False},
        )
        await taxi_cargo_orders.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture
async def exp_cargo_preparation_late(taxi_cargo_orders, experiments3):
    async def wrapper(*, enabled: bool = True, additional_time_sec: int = 600):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_orders_preparation_late',
            consumers=['cargo-orders/preparation-late'],
            clauses=[],
            default_value={
                'enabled': enabled,
                'config': {
                    'dialog_show_mode': 'notification_and_dialog',
                    'wait_additional_time_sec': additional_time_sec,
                    'support_url': 'https://url',
                    'tanker_keys': {
                        'dialog_title': (
                            'actions.order_preparation_late.dialog_title'
                        ),
                        'dialog_message': (
                            'actions.order_preparation_late.dialog_message'
                        ),
                        'notification_title': (
                            'actions.order_preparation_late.'
                            + 'notification_title'
                        ),
                        'notification_message': (
                            'actions.order_preparation_late.'
                            + 'notification_message'
                        ),
                        'dialog_button_ok': (
                            'actions.order_preparation_late.dialog_button_ok'
                        ),
                        'dialog_button_support': (
                            'actions.order_preparation_late.'
                            + 'dialog_button_support'
                        ),
                        'screen_title': (
                            'actions.order_preparation_late.screen_title'
                        ),
                    },
                },
            },
        )
        await taxi_cargo_orders.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture
async def exp_cargo_client_notification(taxi_cargo_orders, experiments3):
    async def wrapper(*, enabled: bool = True):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_orders_client_notification',
            consumers=['cargo-orders/client-notification'],
            clauses=[],
            default_value={
                'enabled': enabled,
                'config': {
                    'type': 'eats_core',
                    'code': 'notification_code',
                    'channels': ['push', 'sms'],
                },
            },
        )
        await taxi_cargo_orders.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='exp_cargo_orders_use_performer_fines_service')
async def _exp_cargo_orders_use_performer_fines_service(
        experiments3, taxi_cargo_orders,
):
    async def wrapper():
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_orders_use_performer_fines_service',
            consumers=['cargo-orders/performer-cancellation-lite'],
            clauses=[],
            default_value={'enabled': True},
        )
        await taxi_cargo_orders.invalidate_caches()

    await wrapper()
    return wrapper
