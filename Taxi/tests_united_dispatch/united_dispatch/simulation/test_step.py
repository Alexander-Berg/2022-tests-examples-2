import copy

CANDIDATES_PLANNER_TYPE = 'testsuite-candidates'
CRUTCHES_PLANNER_TYPE = 'crutches'


async def test_proposition(
        simulation_step,
        state_initialized,
        create_candidates_segment,
        build_input_segments,
        create_simulator_candidates,
        launch_simulator_runner,
):
    """
        Check proposition simulation.
    """
    await state_initialized()

    create_simulator_candidates()
    await launch_simulator_runner()

    # creates default 'candidates-testsuite' segment
    seg = create_candidates_segment('greedy')

    step_output = await simulation_step(
        segments=build_input_segments([seg]),
        planner_type=CANDIDATES_PLANNER_TYPE,
    )

    # check 'delivery' planner proposed waybill with candidate
    assert not step_output['assigned_candidates']
    assert not step_output['passed_segment_ids']
    assert not step_output['skipped_segment_ids']
    assert len(step_output['propositions']) == 1
    proposition = step_output['propositions'][0]
    assert 'candidate' in proposition


async def test_repeat_search(
        simulation_step,
        state_initialized,
        create_candidates_segment,
        build_input_segments,
        create_simulator_candidates,
        launch_simulator_runner,
):
    """
        Check repeat search simulation.
    """
    await state_initialized()

    create_simulator_candidates()
    await launch_simulator_runner()

    # creates default 'candidates-testsuite' segment
    seg = create_candidates_segment('greedy')

    step_output = await simulation_step(
        segments=build_input_segments([seg]),
        planner_type=CANDIDATES_PLANNER_TYPE,
    )

    assert not step_output['assigned_candidates']
    assert not step_output['passed_segment_ids']
    assert not step_output['skipped_segment_ids']
    assert len(step_output['propositions']) == 1
    proposition = step_output['propositions'][0]
    assert 'candidate' in proposition

    initial_proposition = copy.deepcopy(proposition)
    # check repeat search
    proposition.pop('candidate')

    step_output = await simulation_step(
        segments=[],
        waybills=[proposition],
        planner_type=CANDIDATES_PLANNER_TYPE,
    )
    assert step_output['assigned_candidates'] == [initial_proposition]
    assert not step_output['passed_segment_ids']
    assert not step_output['skipped_segment_ids']
    assert not step_output['propositions']


async def test_pass(
        simulation_step,
        state_initialized,
        create_segment,
        build_input_segments,
        create_simulator_candidates,
        launch_simulator_runner,
):
    """
        Check segment pass simulation.
    """
    await state_initialized()

    create_simulator_candidates()
    await launch_simulator_runner()

    seg = create_segment(crutches={'forced_pass': True})

    step_output = await simulation_step(
        segments=build_input_segments([seg]),
        planner_type=CRUTCHES_PLANNER_TYPE,
    )

    assert not step_output['assigned_candidates']
    assert step_output['passed_segment_ids'] == [seg.id]
    assert not step_output['skipped_segment_ids']
    assert not step_output['propositions']


async def test_skip(
        simulation_step,
        state_initialized,
        create_segment,
        build_input_segments,
        create_simulator_candidates,
        launch_simulator_runner,
):
    """
        Check simulation skip simulation.
    """
    await state_initialized()

    create_simulator_candidates()
    await launch_simulator_runner()

    seg = create_segment(crutches={'forced_skip': True})

    step_output = await simulation_step(
        segments=build_input_segments([seg]),
        planner_type=CRUTCHES_PLANNER_TYPE,
    )

    assert not step_output['assigned_candidates']
    assert not step_output['passed_segment_ids']
    assert step_output['skipped_segment_ids'] == [seg.id]
    assert not step_output['propositions']


async def test_unknown_planner(
        simulation_step,
        state_initialized,
        create_segment,
        build_input_segments,
        create_simulator_candidates,
        launch_simulator_runner,
):
    """
        Check unknown planner message.
    """
    await state_initialized()

    create_simulator_candidates()
    await launch_simulator_runner()

    # creates default 'crutches' segment
    seg = create_segment(crutches={'forced_pass': True})

    await simulation_step(
        segments=build_input_segments([seg]),
        planner_type='unknown-planner',
        expected_status=400,
    )
