import datetime

import pytest

from simulator.core import config
from simulator.core import initializers
from simulator.core import runner
from simulator.core import structures
from simulator.core.utils import current_time

CURRENT_TIME = '2021-02-01T12:00:00'


@pytest.mark.now(CURRENT_TIME, enabled=True)
async def test_one_candidate_no_segments(dispatch_model, simulator_mocks):
    # initialize candidates online/offline events
    candidates = initializers.candidates.circle_n_generator.make_candidates(
        candidates_count=1,
        center=structures.Point(lat=55.5, lon=35.5),
        radius=100,
    )
    initializers.candidates.populate.allways_online(
        start=current_time.CurrentTime.get(), candidates=candidates,
    )

    # initialize dispatch
    initializers.dispatch.populate(
        start=current_time.CurrentTime.get(),
        planner_type='testsuite-candidates',
    )

    # run simulation until finish
    runner_ = runner.Runner()

    await runner_.run()

    # gather statistics
    runner_.print_raw_report()
    runner_.print_statistics()

    assert not runner_.is_failed

    # pre_start, online, run_planner, post_finish
    assert len(list(runner_.iter_raw_report())) == 4

    proposed_count = 0
    is_assigned_candidates = False
    for _, _, report in runner_.iter_raw_report():
        if isinstance(report, structures.DispatchOutput):
            is_assigned_candidates |= bool(report.assigned_candidates)
            proposed_count += len(report.propositions)

    assert not is_assigned_candidates
    assert proposed_count == 0


@pytest.mark.now(CURRENT_TIME, enabled=True)
async def test_no_candidates_timeout(dispatch_model, simulator_mocks):
    config.init(
        dispatch={
            'run_interval': datetime.timedelta(seconds=5),
            'total_timeout': datetime.timedelta(seconds=10),
        },
    )

    # initialize new segment events
    segments = initializers.segments.circle_n_soon_generator.make_segments(
        segments_count=1,
        center=structures.Point(lat=55.5, lon=35.5),
        radius=100,
        corp_client_id='candidates-testsuite',
        custom_context={'candidates-testsuite': {'type': 'greedy'}},
    )

    initializers.segments.populate.by_interval(
        start=current_time.CurrentTime.get(),
        end=current_time.CurrentTime.get(),
        segments=segments,
    )

    # initialize dispatch
    initializers.dispatch.populate(
        start=current_time.CurrentTime.get(),
        planner_type='testsuite-candidates',
    )

    # run simulation until finish
    runner_ = runner.Runner()

    await runner_.run()

    # gather statistics
    runner_.print_raw_report()
    runner_.print_statistics()

    assert not runner_.is_failed

    # pre_start, new_segment, run_planner,
    # run_planner, run_planner, post_finish
    assert len(list(runner_.iter_raw_report())) == 6

    proposed_count = 0
    is_assigned_candidates = False
    for _, _, report in runner_.iter_raw_report():
        if isinstance(report, structures.DispatchOutput):
            is_assigned_candidates |= bool(report.assigned_candidates)
            proposed_count += len(report.propositions)

    assert not is_assigned_candidates
    assert proposed_count == 0


@pytest.mark.now(CURRENT_TIME, enabled=True)
async def test_one_candidate_multiple_orders(dispatch_model, simulator_mocks):
    # initialize candidates online/offline events
    candidates = initializers.candidates.circle_n_generator.make_candidates(
        candidates_count=1,
        center=structures.Point(lat=55.5, lon=35.5),
        radius=100,
    )
    initializers.candidates.populate.allways_online(
        start=current_time.CurrentTime.get(), candidates=candidates,
    )

    # initialize new segment events
    segments = initializers.segments.circle_n_soon_generator.make_segments(
        segments_count=5,
        center=structures.Point(lat=55.5, lon=35.5),
        radius=100,
        corp_client_id='candidates-testsuite',
        custom_context={'candidates-testsuite': {'type': 'greedy'}},
    )

    initializers.segments.populate.by_interval(
        start=current_time.CurrentTime.get(),
        end=current_time.CurrentTime.get(),
        segments=segments,
    )

    # initialize dispatch
    initializers.dispatch.populate(
        start=current_time.CurrentTime.get(),
        planner_type='testsuite-candidates',
    )

    # run simulation until finish
    runner_ = runner.Runner()

    await runner_.run()

    # gather statistics
    runner_.print_raw_report()
    runner_.print_statistics()

    assert not runner_.is_failed

    proposed_count = 0
    is_assigned_candidates = False
    for _, _, report in runner_.iter_raw_report():
        if isinstance(report, structures.DispatchOutput):
            is_assigned_candidates |= bool(report.assigned_candidates)
            proposed_count += len(report.propositions)

    assert not is_assigned_candidates
    assert proposed_count > 1


@pytest.mark.now(CURRENT_TIME, enabled=True)
async def test_many_candidates_many_orders(dispatch_model, simulator_mocks):
    # initialize candidates online/offline events
    candidates = initializers.candidates.circle_n_generator.make_candidates(
        candidates_count=10,
        center=structures.Point(lat=55.5, lon=35.5),
        radius=100,
    )
    initializers.candidates.populate.allways_online(
        start=current_time.CurrentTime.get(), candidates=candidates,
    )

    # initialize new segment events
    segments = initializers.segments.circle_n_soon_generator.make_segments(
        segments_count=10,
        center=structures.Point(lat=55.5, lon=35.5),
        radius=100,
        corp_client_id='candidates-testsuite',
        custom_context={'candidates-testsuite': {'type': 'greedy'}},
    )

    initializers.segments.populate.by_interval(
        start=current_time.CurrentTime.get(),
        end=current_time.CurrentTime.get(),
        segments=segments,
    )

    # initialize dispatch
    initializers.dispatch.populate(
        start=current_time.CurrentTime.get(),
        planner_type='testsuite-candidates',
    )

    # run simulation until finish
    runner_ = runner.Runner()

    await runner_.run()

    # gather statistics
    runner_.print_raw_report()
    runner_.print_statistics()

    assert not runner_.is_failed

    is_proposed = False
    is_assigned_candidates = False
    for _, _, report in runner_.iter_raw_report():
        if isinstance(report, structures.DispatchOutput):
            is_assigned_candidates |= bool(report.assigned_candidates)
            is_proposed |= bool(report.propositions)

    assert not is_assigned_candidates
    assert is_proposed
