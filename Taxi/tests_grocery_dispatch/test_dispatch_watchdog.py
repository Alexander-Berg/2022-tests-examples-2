# pylint: disable=import-only-modules
import copy

import pytest

from tests_grocery_dispatch import configs
from tests_grocery_dispatch import constants as const
from tests_grocery_dispatch import models

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.now(const.NOW),
    configs.DISPATCH_CLAIM_CONFIG,
    configs.DISPATCH_GENERAL_CONFIG,
    configs.DISPATCH_WATCHDOG_CONFIG,
]


@configs.DISPATCH_PRIORITY_CONFIG_TEST
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_watchdog_started_when_dispatch_created(
        taxi_grocery_dispatch, stq,
):
    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response.status_code == 200
    assert 'dispatch_id' in response.json()

    assert stq.grocery_dispatch_watchdog.times_called == 1
    stq_args = stq.grocery_dispatch_watchdog.next_call()['kwargs']
    assert stq_args['dispatch_id'] == response.json()['dispatch_id']


@configs.DISPATCH_PRIORITY_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_watchdog_continue_itself(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
        logistic_dispatcher,
        stq_runner,
        stq,
        grocery_dispatch_pg,
        cargo_pg,
):
    experiments3.add_config(
        name='grocery_dispatch_watchdog',
        consumers=['grocery_dispatch/dispatch_watchdog'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={'interval': 60, 'is_enabled': True},
    )

    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name=const.DISPATCH_TYPE,
    )

    await stq_runner.grocery_dispatch_watchdog.call(
        task_id='dummy_task', kwargs={'dispatch_id': dispatch.dispatch_id},
    )

    assert stq.grocery_dispatch_watchdog.times_called == 1


@pytest.mark.skip(reason='Use reschedule v2 in following test')
@configs.DISPATCH_PRIORITY_CONFIG
async def test_watchdog_reschedule_dispatch(
        taxi_grocery_dispatch,
        pgsql,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
        logistic_dispatcher,
        stq_runner,
        grocery_dispatch_pg,
        cargo_pg,
        stq,
):
    experiments3.add_config(
        consumers=['grocery_dispatch/dispatch'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='grocery_dispatch_priority',
        default_value={'dispatches': [const.DISPATCH_TYPE]},
    )

    cargo.add_performer(
        claim_id=const.CLAIM_ID,
        eats_profile_id=const.PROFILE_ID,
        driver_id=const.DRIVER_ID,
        park_id=const.PARK_ID,
    )

    cargo.add_performer(
        claim_id=const.CLAIM_ID_2,
        eats_profile_id=const.PROFILE_ID,
        driver_id=const.DRIVER_ID,
        park_id=const.PARK_ID,
    )

    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name=const.DISPATCH_TYPE,
    )
    first_claim = cargo_pg.create_claim(
        dispatch_id=dispatch.dispatch_id, claim_id=const.CLAIM_ID,
    )
    assert first_claim.wave == 0

    cargo.set_data(
        items=cargo.convert_items(dispatch.order.items),
        new_claim=const.CLAIM_ID_2,
        delivered_eta_ts=const.DELIVERY_ETA_TS,
    )

    # will be checked at cargo mock
    cargo.custom_context = {
        'delivery_flags': {
            'is_forbidden_to_be_in_batch': False,
            'assign_rover': False,
        },
        'external_feature_prices': {'external_order_created_ts': const.NOW_TS},
        'depot_id': dispatch.order.depot_id,
        'lavka_has_market_parcel': False,
        'region_id': 213,
    }
    await stq_runner.grocery_dispatch_watchdog.call(
        task_id='dummy_task', kwargs={'dispatch_id': dispatch.dispatch_id},
    )

    second_claim = cargo_pg.get_claim(claim_id=const.CLAIM_ID_2)
    assert second_claim.wave == 1


@configs.DISPATCH_PRIORITY_CONFIG
async def test_watchdog_reschedule_dispatch_v2(
        taxi_grocery_dispatch,
        pgsql,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
        logistic_dispatcher,
        stq_runner,
        grocery_dispatch_pg,
        cargo_pg,
        stq,
):
    experiments3.add_config(
        consumers=['grocery_dispatch/dispatch'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='grocery_dispatch_priority',
        default_value={'dispatches': [const.DISPATCH_TYPE]},
    )

    cargo.add_performer(
        claim_id=const.CLAIM_ID,
        eats_profile_id=const.PROFILE_ID,
        driver_id=const.DRIVER_ID,
        park_id=const.PARK_ID,
    )

    cargo.add_performer(
        claim_id=const.CLAIM_ID_2,
        eats_profile_id=const.PROFILE_ID,
        driver_id=const.DRIVER_ID,
        park_id=const.PARK_ID,
    )

    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name=const.DISPATCH_TYPE,
    )
    first_claim = cargo_pg.create_claim(
        dispatch_id=dispatch.dispatch_id, claim_id=const.CLAIM_ID,
    )
    assert first_claim.wave == 0

    cargo.set_data(
        items=cargo.convert_items(dispatch.order.items),
        new_claim=const.CLAIM_ID_2,
        delivered_eta_ts=const.DELIVERY_ETA_TS,
    )

    # will be checked at cargo mock
    cargo.custom_context = {
        'delivery_flags': {
            'is_forbidden_to_be_in_batch': False,
            'assign_rover': False,
        },
        'external_feature_prices': {'external_order_created_ts': const.NOW_TS},
        'depot_id': dispatch.order.depot_id,
        'lavka_has_market_parcel': False,
        'region_id': 213,
    }
    await stq_runner.grocery_dispatch_watchdog.call(
        task_id='dummy_task', kwargs={'dispatch_id': dispatch.dispatch_id},
    )

    assert stq.grocery_dispatch_reschedule_executor.times_called == 1
    stq_args = stq.grocery_dispatch_reschedule_executor.next_call()['kwargs']
    assert stq_args['dispatch_id'] == dispatch.dispatch_id


@pytest.mark.parametrize(
    'dispatch_status', ['canceled', 'revoked', 'finished'],
)
async def test_stop_watchdog_on_dispatch_completed(
        stq_runner, grocery_dispatch_pg, dispatch_status, testpoint,
):
    @testpoint('stop-watchdog-completed')
    def on_stop(data):
        pass

    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name=const.DISPATCH_TYPE, status=dispatch_status,
    )

    await stq_runner.grocery_dispatch_watchdog.call(
        task_id='dummy_task', kwargs={'dispatch_id': dispatch.dispatch_id},
    )
    assert on_stop.times_called == 1


@pytest.mark.parametrize(
    'dispatch_intent',
    [
        'test',
        'cargo',
        'cargo_sync',
        'cargo_forced_performer',
        'cargo_taxi',
        'pending',
    ],
)
async def test_watchdog_reschedule_dispatch_v2_check_dipatch_intent_in_db(
        experiments3,
        stq_runner,
        grocery_dispatch_pg,
        grocery_reschedule_state_pg,
        dispatch_intent,
):
    experiments3.add_config(
        name='grocery_dispatch_watchdog',
        consumers=['grocery_dispatch/dispatch_watchdog'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={
            'interval': 60,
            'is_enabled': True,
            'reschedule_options': {'dispatch_intent': dispatch_intent},
        },
    )

    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name=const.DISPATCH_TYPE,
    )

    await stq_runner.grocery_dispatch_watchdog.call(
        task_id='dummy_task', kwargs={'dispatch_id': dispatch.dispatch_id},
    )

    state = grocery_reschedule_state_pg.get_state(
        dispatch_id=dispatch.dispatch_id,
    )
    assert state.options['dispatch_intent'] == dispatch_intent


async def test_watchdog_cancel_dispatch(
        experiments3, stq_runner, grocery_dispatch_pg,
):
    experiments3.add_config(
        name='grocery_dispatch_watchdog',
        consumers=['grocery_dispatch/dispatch_watchdog'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={
            'interval': 60,
            'is_enabled': True,
            'cancel_options': {'reason': 'test_cancel'},
        },
    )

    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name=const.DISPATCH_TYPE,
    )
    assert dispatch.status == 'idle'

    await stq_runner.grocery_dispatch_watchdog.call(
        task_id='dummy_task', kwargs={'dispatch_id': dispatch.dispatch_id},
    )
    assert dispatch.status == 'canceled'


@configs.DISPATCH_PRIORITY_CONFIG_TEST
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_check_dispatch_intent_kwargs(
        experiments3,
        stq,
        stq_runner,
        grocery_dispatch_pg,
        grocery_reschedule_state_pg,
):
    experiments3.add_config(
        name='grocery_dispatch_watchdog',
        consumers=['grocery_dispatch/dispatch_watchdog'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Depot timetable',
                'predicate': {
                    'init': {'arg_name': 'is_depot_available'},
                    'type': 'bool',
                },
                'value': {
                    'interval': 60,
                    'is_enabled': True,
                    'reschedule_options': {
                        'dispatch_intent': 'pending_timeout_exceeded',
                    },
                },
            },
        ],
    )

    exp3_recorder_watchdog = experiments3.record_match_tries(
        'grocery_dispatch_watchdog',
    )

    exp3_recorder_priority = experiments3.record_match_tries(
        'grocery_dispatch_priority',
    )

    dispatch = grocery_dispatch_pg.create_dispatch(status='scheduled')

    await stq_runner.grocery_dispatch_watchdog.call(
        task_id='dummy_task', kwargs={'dispatch_id': dispatch.dispatch_id},
    )

    state = grocery_reschedule_state_pg.get_state(
        dispatch_id=dispatch.dispatch_id,
    )
    assert state.options['dispatch_intent'] == 'pending_timeout_exceeded'

    call_data = stq.grocery_dispatch_reschedule_executor.next_call()

    await stq_runner.grocery_dispatch_reschedule_executor.call(
        task_id=call_data['id'],
        kwargs={
            'dispatch_id': dispatch.dispatch_id,
            'idempotency_token': call_data['kwargs']['idempotency_token'],
        },
    )

    assert stq.grocery_dispatch_reschedule_executor.times_called == 0

    match_tries = await exp3_recorder_priority.get_match_tries(ensure_ntries=1)
    assert (
        match_tries[0].kwargs['dispatch_intent'] == 'pending_timeout_exceeded'
    )

    match_tries = await exp3_recorder_watchdog.get_match_tries(ensure_ntries=1)
    assert match_tries[0].kwargs['is_depot_available'] == 1
    assert match_tries[0].kwargs['couriers_quantity'] == 2
