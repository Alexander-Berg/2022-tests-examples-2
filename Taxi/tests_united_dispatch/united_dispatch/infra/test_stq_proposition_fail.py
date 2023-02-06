async def test_proposition_failed(
        create_segment,
        state_waybill_created,
        stq,
        stq_runner,
        get_single_waybill,
        mockserver,
):
    create_segment(crutches={'force_crutch_builder': True})

    await state_waybill_created()

    waybill_ref = get_single_waybill()['id']

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/propose')
    def mock_propose(request):
        return mockserver.make_response(
            status=400, json={'code': 'invalid_path', 'message': 'test error'},
        )

    stq.united_dispatch_proposition_fail.flush()
    await stq_runner.united_dispatch_waybill_propose.call(
        task_id=waybill_ref, kwargs={'waybill_ref': waybill_ref},
    )

    assert mock_propose.times_called

    assert stq.united_dispatch_proposition_fail.has_calls


async def test_planner_mark_segment_after_fail(
        state_segments_replicated,
        create_segment,
        get_segment,
        get_single_waybill,
        run_single_planner,
        autorun_propose,
        testpoint,
        mockserver,
):
    """
        Check planner does nothing after waybill fail.
    """
    segment = create_segment(crutches={'force_crutch_builder': True})

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/propose')
    async def mock_propose(request):
        return mockserver.make_response(
            status=400, json={'code': 'invalid_path', 'message': 'test error'},
        )

    @testpoint('MarkSegmentPropositionsOptional')
    async def planner_interrupt(data):
        await autorun_propose()

        assert mock_propose.times_called

        # check proposition failed, segment restarted
        assert (
            get_single_waybill()['external_resolution'] == 'proposition_failed'
        )
        pg_segment = get_segment(segment.id)
        assert pg_segment['waybill_ref'] is None

    await state_segments_replicated()

    await run_single_planner()

    assert planner_interrupt.times_called

    pg_segment = get_segment(segment.id)
    assert pg_segment['waybill_ref'] is None


async def test_planner_mark_waybill_after_fail(
        state_taxi_order_performer_found,
        state_segments_replicated,
        propositions_manager,
        create_segment,
        get_segment,
        get_waybill_by_segment,
        run_single_planner,
        autorun_propose,
        testpoint,
        mockserver,
):
    """
        Check planner does nothing after live proposition failed.
    """
    seg1 = create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_performer_found()

    assert len(propositions_manager.propositions) == 1
    previous_waybill_ref = get_segment(seg1.id)['waybill_ref']
    assert previous_waybill_ref

    seg2 = create_segment(crutches={'live_batch_with': seg1.id})

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/update-proposition')
    async def mock_propose(request):
        assert request.json['updated_waybill_ref'] == previous_waybill_ref
        return mockserver.make_response(
            status=400, json={'code': 'invalid_path', 'message': 'test error'},
        )

    @testpoint('MarkWaybillPropositionsOptional')
    async def planner_interrupt(data):
        await autorun_propose()

        assert mock_propose.times_called

        # check proposition failed, segment restarted
        assert (
            get_waybill_by_segment(seg2.id)['external_resolution']
            == 'proposition_failed'
        )
        assert get_segment(seg1.id)['waybill_ref'] == previous_waybill_ref
        assert get_segment(seg2.id)['waybill_ref'] is None

    await state_segments_replicated()

    assert len(propositions_manager.propositions) == 1  # still one proposed

    await run_single_planner()

    assert planner_interrupt.times_called

    assert get_segment(seg1.id)['waybill_ref'] == previous_waybill_ref
    assert get_segment(seg2.id)['waybill_ref'] is None


async def test_timeout_restart_segments(
        state_waybill_created,
        get_single_waybill,
        create_segment,
        get_segment,
        testpoint,
        stq_runner,
        waybill_resolution='some_resolution',
):
    """
        Check proposition is cleared succesfully if first
        try to restart segments failed finished by timeout.
    """
    seg = create_segment(crutches={'force_crutch_builder': True})

    raise_exception = True

    @testpoint('RestartSegments')
    async def injection(data):
        return {'raise_exception': raise_exception}

    await state_waybill_created()

    # first try failed to mark waybill failed, segments restarted
    waybill_ref = get_single_waybill()['id']
    await stq_runner.united_dispatch_proposition_fail.call(
        task_id='test',
        kwargs={'waybill_ref': waybill_ref, 'resolution': waybill_resolution},
    )

    assert injection.times_called
    assert get_single_waybill()['proposition_status'] == 'new'
    assert get_segment(seg.id)['waybill_ref'] is None
    assert get_single_waybill()['external_resolution'] is None

    # second try resolution set
    raise_exception = False
    await stq_runner.united_dispatch_proposition_fail.call(
        task_id='test',
        kwargs={'waybill_ref': waybill_ref, 'resolution': waybill_resolution},
    )
    assert get_single_waybill()['external_resolution'] == waybill_resolution


async def test_timeout_clean_update_proposition(
        state_taxi_order_performer_found,
        get_waybill,
        create_segment,
        get_segment,
        mockserver,
        testpoint,
        stq_runner,
        propositions_manager,
):
    """
        Check proposition is cleared succesfully if first
        try to clean live proposition finished by timeout.
    """

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/update-proposition')
    async def mock_update_proposition(request):
        return mockserver.make_response(
            status=400, json={'code': 'invalid_path', 'message': 'test error'},
        )

    raise_exception = True

    @testpoint('CleanUpdateProposition')
    async def injection(data):
        return {'raise_exception': raise_exception}

    seg1 = create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_performer_found()

    assert len(propositions_manager.propositions) == 1

    seg2 = create_segment(crutches={'live_batch_with': seg1.id})

    await state_taxi_order_performer_found()

    # first try failed to mark waybill failed
    previous_waybill_ref = get_segment(seg1.id)['waybill_ref']
    new_waybill_ref = get_segment(seg2.id)['waybill_ref']
    assert new_waybill_ref
    assert previous_waybill_ref != new_waybill_ref
    await stq_runner.united_dispatch_proposition_fail.call(
        task_id='test',
        kwargs={
            'waybill_ref': new_waybill_ref,
            'resolution': 'proposition_failed',
        },
    )

    assert injection.times_called
    assert mock_update_proposition.times_called
    # update_proposition_id cleaned, but external_resolution is not yet
    assert get_waybill(previous_waybill_ref)['update_proposition_id'] is None
    assert get_waybill(new_waybill_ref)['external_resolution'] is None

    # second try segments restarted and resolution set
    raise_exception = False
    await stq_runner.united_dispatch_proposition_fail.call(
        task_id='test',
        kwargs={
            'waybill_ref': new_waybill_ref,
            'resolution': 'proposition_failed',
        },
    )
    assert (
        get_waybill(new_waybill_ref)['external_resolution']
        == 'proposition_failed'
    )
    assert get_segment(seg2.id)['waybill_ref'] is None
