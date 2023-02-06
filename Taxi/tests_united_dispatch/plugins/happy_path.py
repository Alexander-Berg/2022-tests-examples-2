# pylint: disable=redefined-outer-name
import dataclasses

import pytest

from . import cargo_dispatch_manager


@dataclasses.dataclass
class CurrentState:
    cargo_dispatch: cargo_dispatch_manager.CargoDispatch

    def get_proposed_waybill_ref(self):
        assert len(self.cargo_dispatch.waybills.waybills) == 1
        return list(self.cargo_dispatch.waybills.waybills.keys())[0]

    def get_segment_id(self):
        assert len(self.cargo_dispatch.segments.segments) == 1
        return list(self.cargo_dispatch.segments.segments.keys())[0]


# fake state (creates State object)
@pytest.fixture(name='current_state')
async def _current_state(cargo_dispatch):
    state = CurrentState(cargo_dispatch=cargo_dispatch)

    return state


@pytest.fixture(name='state_initialized')
async def _state_initialized(
        current_state,
        united_dispatch_unit,
        cargo_corp_settings,
        exp_segment_executors_selector,
        exp_planner_shard,
        exp_delivery_generators_settings,
):
    # initialization goes before any call,
    # so it can be overwritten by other tests
    await cargo_corp_settings.add_clients(
        service_fixture=united_dispatch_unit,
        clients={
            'eats_corp_id': 'eats',
            'eats_corp_id1': 'eats',
            'eats_corp_id2': 'eats',
            'grocery_corp_id1': 'grocery',
            'food_retail_corp_id1': 'food_retail',
        },
    )
    # initialization goes before any call,
    # so it can be overwritten by other tests
    await exp_segment_executors_selector()
    await exp_planner_shard()
    await exp_delivery_generators_settings()

    async def wrapper():
        return current_state

    return wrapper


@pytest.fixture(name='state_segments_created')
async def _state_segments_created(
        state_initialized, cargo_dispatch, create_segment,
):
    async def wrapper():
        state = await state_initialized()

        if not cargo_dispatch.segments.segments:
            # create default segment
            create_segment()

        return state

    return wrapper


@pytest.fixture(name='state_segments_replicated')
async def _state_segments_replicated(
        state_segments_created, run_segments_reader, autorun_stq,
):
    async def wrapper():
        state = await state_segments_created()

        await run_segments_reader()
        await autorun_stq('united_dispatch_segment_reader')

        return state

    return wrapper


@pytest.fixture(name='state_waybill_created')
async def _state_waybill_created(
        state_segments_replicated, run_single_planner, exp_planner_settings,
):
    # initialization goes before any call,
    # so it can be overwritten by other tests
    await exp_planner_settings()

    async def wrapper():
        state = await state_segments_replicated()

        await run_single_planner()

        return state

    return wrapper


@pytest.fixture(name='state_waybill_proposed')
async def _state_waybill_proposed(state_waybill_created, autorun_stq):
    async def wrapper():
        state = await state_waybill_created()

        await autorun_stq('united_dispatch_waybill_propose')

        return state

    return wrapper


@pytest.fixture(name='state_waybill_accepted')
async def _state_waybill_accepted(state_waybill_proposed, run_waybill_reader):
    async def wrapper():
        state = await state_waybill_proposed()

        await run_waybill_reader()

        return state

    return wrapper


@pytest.fixture(name='state_taxi_order_created')
async def _state_taxi_order_created(
        state_waybill_accepted,
        mock_cargo_dispatch_waybill_ref,
        cargo_dispatch,
        run_waybill_reader,
):
    async def wrapper():
        state = await state_waybill_accepted()

        for waybill_ref in cargo_dispatch.waybills.waybills:
            cargo_dispatch.waybills.set_taxi_order(waybill_ref)

        await run_waybill_reader()

        return state

    return wrapper


@pytest.fixture(name='state_taxi_order_performer_found')
async def _state_taxi_order_performer_found(
        state_taxi_order_created,
        cargo_dispatch,
        run_waybill_reader,
        get_waybill,
):
    async def wrapper(*, performer_tariff=None):
        state = await state_taxi_order_created()

        for waybill_ref in cargo_dispatch.waybills.waybills:
            candidate_doc = get_waybill(waybill_ref)['candidate']
            performer_id = (
                candidate_doc['info']['id'] if candidate_doc else None
            )
            cargo_dispatch.waybills.set_performer(
                waybill_ref,
                performer_id=performer_id,
                performer_tariff=performer_tariff,
            )

        await run_waybill_reader()

        return state

    return wrapper


@pytest.fixture(name='state_waybill_resolved')
async def _state_waybill_resolved(
        state_taxi_order_performer_found, cargo_dispatch, run_waybill_reader,
):
    async def wrapper():
        state = await state_taxi_order_performer_found()

        for waybill_ref in cargo_dispatch.waybills.waybills:
            cargo_dispatch.waybills.set_resolved(waybill_ref)

        await run_waybill_reader()

        return state

    return wrapper
