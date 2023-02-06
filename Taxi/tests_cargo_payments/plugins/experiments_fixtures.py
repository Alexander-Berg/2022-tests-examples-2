"""
    Describe here experiments3.0 fixtures.
"""
import pytest


@pytest.fixture(name='exp_cargo_payments_post_payment_state', autouse=True)
async def _exp_cargo_payments_post_payment_state(
        experiments3, taxi_cargo_payments,
):
    async def wrapper():
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_payments_post_payment_state',
            consumers=['cargo-payments/state'],
            clauses=[
                {
                    'title': 'clause',
                    'predicate': {
                        'init': {
                            'set': ['new', 'confirmed', 'canceled'],
                            'arg_name': 'payment_status',
                            'set_elem_type': 'string',
                        },
                        'type': 'in_set',
                    },
                    'value': {
                        'payment_ui': {
                            'header_tanker_key': (
                                'post_payment.state.init_pay_header'
                            ),
                            'title_tanker_key': (
                                'post_payment.state.init_pay_title'
                            ),
                        },
                        'taximeter_polling_delay_ms': 1000,
                    },
                },
            ],
            default_value={
                'payment_ui': {
                    'header_tanker_key': 'post_payment.state.paid_header',
                    'title_tanker_key': 'post_payment.state.paid_title',
                },
                'taximeter_polling_delay_ms': 1000,
            },
        )
        await taxi_cargo_payments.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='exp_cargo_payments_agent_creator')
async def _exp_cargo_payments_agent_creator(experiments3, taxi_cargo_payments):
    async def wrapper(*, virtual_client_id, min_diagnostics_user_agent='9.40'):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_payments_agent_creator',
            consumers=[
                'cargo-payments/upsert-agent',
                'cargo-payments/diagnostics-confirm',
            ],
            clauses=[],
            default_value={
                'secret_key_length': 9,
                'login_length': 12,
                'login_suffix': 'go.ya',
                'virtual_client_id': virtual_client_id,
                'min_diagnostics_user_agent': min_diagnostics_user_agent,
            },
        )
        await taxi_cargo_payments.invalidate_caches()

    return wrapper


@pytest.fixture(name='exp_cargo_payments_diagnostics_tags', autouse=True)
async def _exp_cargo_payments_diagnostics_tags(
        experiments3, taxi_cargo_payments,
):
    async def wrapper(
            *, ttl=None, upload_tags_only_on_changes=True, enabled=True,
    ):
        postpayment_diagnostics_record = {'name': 'postpayment_diagnostics'}
        if ttl is not None:
            postpayment_diagnostics_record['ttl'] = ttl
        if enabled:
            tags = [postpayment_diagnostics_record]
        else:
            tags = []

        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_payments_diagnostics_tags',
            consumers=[
                'cargo-payments/diagnostics-confirm',
                'cargo-payments/update-driver-tags',
            ],
            clauses=[
                {
                    'title': 'diagnostics_passed',
                    'predicate': {
                        'type': 'bool',
                        'init': {'arg_name': 'is_diagnostics_passed'},
                    },
                    'value': {
                        'allow_card': True,
                        'append_tags': tags,
                        'remove_tags': [],
                        'tags_provider_id': 'cargo_payments_provider',
                        'upload_tags_only_on_changes': (
                            upload_tags_only_on_changes
                        ),
                    },
                },
            ],
            default_value={
                'enabled': enabled,
                'allow_card': False,
                'append_tags': [],
                'remove_tags': tags,
                'tags_provider_id': 'cargo_payments_provider',
                'upload_tags_only_on_changes': upload_tags_only_on_changes,
            },
        )
        await taxi_cargo_payments.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='exp_cargo_payments_eats_callbacks')
async def _exp_cargo_payments_eats_callbacks(
        experiments3, taxi_cargo_payments,
):
    async def wrapper(*, eats_virtual_client_id):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_payments_eats_callbacks',
            consumers=['cargo-payments/status-callbacks'],
            clauses=[
                {
                    'title': 'only_eats_client',
                    'predicate': {
                        'type': 'eq',
                        'init': {
                            'value': eats_virtual_client_id,
                            'arg_name': 'virtual_client_id',
                            'arg_type': 'string',
                        },
                    },
                    'value': {'enabled': True},
                },
            ],
            default_value={'enabled': False},
        )
        await taxi_cargo_payments.invalidate_caches()

    return wrapper


@pytest.fixture(name='exp_cargo_payments_sync_performer_agent')
async def _exp_cargo_payments_sync_performer_agent(
        experiments3, taxi_cargo_payments,
):
    async def wrapper(*, enabled=True):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_payments_sync_performer_agent_settings',
            consumers=['cargo-payments/sync-performer-agent'],
            clauses=[],
            default_value={'enabled': enabled},
        )
        await taxi_cargo_payments.invalidate_caches()

    return wrapper


@pytest.fixture(name='exp_cargo_payments_nfc_callback', autouse=True)
async def _exp_cargo_payments_nfc_callback(experiments3, taxi_cargo_payments):
    async def wrapper(
            *,
            payment_confirmation_type='app',
            api_validation=False,
            api_validation_fallback='error',
    ):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_payments_nfc_callback',
            consumers=['cargo-payments/state'],
            clauses=[],
            default_value={
                'payment_confirmation_type': payment_confirmation_type,
                'api_validation': api_validation,
                'api_validation_fallback': api_validation_fallback,
            },
        )
        await taxi_cargo_payments.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='exp_cargo_payments_performer_diagnostics')
async def _exp_cargo_payments_performer_diagnostics(
        experiments3, taxi_cargo_payments,
):
    async def wrapper(
            *, tanker_key='cargo_payments.performer_status.not_allowed',
    ):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_payments_performer_diagnostics',
            consumers=['cargo-payments/admin-performer-info'],
            clauses=[],
            default_value={'post_payment_status_tanker_key': tanker_key},
        )
        await taxi_cargo_payments.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='exp_cargo_payments_2can_redirect_message')
async def _exp_cargo_payments_2can_redirect_message(
        experiments3, taxi_cargo_payments,
):
    async def wrapper(*, default_key=''):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_payments_2can_redirect_message',
            consumers=['cargo-payments/2can/link-status'],
            clauses=[
                {
                    'title': 'test',
                    'predicate': {
                        'init': {
                            'set': [402],
                            'arg_name': 'substate',
                            'set_elem_type': 'int',
                        },
                        'type': 'in_set',
                    },
                    'value': {
                        'has_error': False,
                        'tanker_key_message': (
                            'cargo_payments.2can_redirect.fail'
                        ),
                        'tanker_key_description': (
                            'cargo_payments.2can_redirect.400_description'
                        ),
                    },
                },
            ],
            default_value={
                'has_error': True,
                'tanker_key_message': (
                    'cargo_payments.2can_redirect.bad_redirect'
                ),
            },
        )
        await taxi_cargo_payments.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='exp_cargo_payments_link_generation')
async def _exp_cargo_payments_link_generation(
        experiments3, taxi_cargo_payments,
):
    async def wrapper(
            *,
            virtual_client_id,
            do_redirect=True,
            redirect_url='https://test.com',
    ):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_payments_link_generation',
            consumers=['cargo-payments/wait_payment'],
            clauses=[
                {
                    'title': 'match',
                    'predicate': {
                        'type': 'eq',
                        'init': {
                            'value': virtual_client_id,
                            'arg_name': 'virtual_client_id',
                            'arg_type': 'string',
                        },
                    },
                    'value': {
                        'do_redirect': do_redirect,
                        'redirect_url': redirect_url,
                    },
                },
            ],
            default_value={'do_redirect': False, 'redirect_url': redirect_url},
        )
        await taxi_cargo_payments.invalidate_caches()

    return wrapper
