import datetime

from simulator.core import initializers
from simulator.core import structures
from simulator.core.utils import current_time

CRUTCHES_PLANNER_TYPE = 'crutches'
CANDIDATES_PLANNER_TYPE = 'testsuite-candidates'
PLANNER_LAUNCH_PAUSE = datetime.timedelta(seconds=5)


async def test_single_step(
        state_initialized,
        create_candidates_segment,
        dispatch_model,
        create_simulator_candidates,
        launch_simulator_runner,
):
    """
        Check planner works in simulation.
    """
    await state_initialized()

    create_simulator_candidates()
    await launch_simulator_runner()

    # creates default 'candidates-testsuite' segment
    seg1 = create_candidates_segment('greedy')
    seg2 = create_candidates_segment('greedy')

    output = await dispatch_model.run(
        planner_type=CANDIDATES_PLANNER_TYPE,
        segments=[seg1, seg2],
        active_waybills=[],
    )

    # check 'candidates-testsuite' planner proposed waybill with candidate
    assert not output.assigned_candidates
    assert not output.passed_segment_ids
    assert not output.skipped_segment_ids
    assert len(output.propositions) == 2
    for proposition in output.propositions:
        assert proposition.candidate


async def test_live_batch(
        state_initialized,
        create_segment,
        dispatch_model,
        create_simulator_candidates,
        launch_simulator_runner,
):
    """
        Check live batch processed in simulation.
    """
    await state_initialized()

    create_simulator_candidates()

    seg1 = create_segment(crutches={'force_crutch_builder': True})
    seg2 = create_segment(crutches={'live_batch_with': seg1.id})

    initializers.segments.populate.by_interval(
        start=current_time.CurrentTime.get(),
        end=current_time.CurrentTime.get(),
        segments=[
            structures.DispatchSegment(info=seg) for seg in [seg1, seg2]
        ],
    )

    await launch_simulator_runner()

    output = await dispatch_model.run(
        planner_type=CRUTCHES_PLANNER_TYPE,
        segments=[seg1],
        active_waybills=[],
    )

    # check 'crutches' planner proposed waybill
    assert len(output.propositions) == 1
    proposition = output.propositions[0]
    proposition.info.set_performer()

    output = await dispatch_model.run(
        planner_type=CRUTCHES_PLANNER_TYPE,
        segments=[seg2],
        active_waybills=[proposition],
    )

    # check live batch proposed
    assert len(output.propositions) == 1
    seg_ids = {seg.id for seg in output.propositions[0].info.segments}
    assert seg_ids == {seg1.id, seg2.id}
    assert (
        output.propositions[0].info.update_proposition.previous_waybill_ref
        == proposition.info.id
    )


async def test_repeat_search(
        state_initialized,
        create_candidates_segment,
        dispatch_model,
        mocked_time,
        create_simulator_candidates,
        launch_simulator_runner,
):
    """
        Check repeat search in simulation.
    """
    await state_initialized()

    create_simulator_candidates()
    await launch_simulator_runner()

    # creates default 'candidates-testsuite' segment
    seg = create_candidates_segment('greedy')

    output = await dispatch_model.run(
        planner_type=CANDIDATES_PLANNER_TYPE,
        segments=[seg],
        active_waybills=[],
    )

    # check 'candidates-testsuite' planner proposed waybill with candidate
    assert len(output.propositions) == 1
    for proposition in output.propositions:
        # drop candidate for repeat search
        proposition.candidate = None

    mocked_time.sleep(PLANNER_LAUNCH_PAUSE.seconds)
    output = await dispatch_model.run(
        planner_type=CANDIDATES_PLANNER_TYPE,
        segments=[],
        active_waybills=output.propositions,
    )

    assert output.assigned_candidates
    for assigned_candidate in output.assigned_candidates:
        assert assigned_candidate.candidate
