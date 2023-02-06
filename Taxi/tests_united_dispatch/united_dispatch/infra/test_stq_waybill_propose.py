# pylint: disable=invalid-name
from tests_united_dispatch.plugins import cargo_dispatch_manager


async def test_basic(
        create_segment,
        stq_runner,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
        state_waybill_created,
        get_single_waybill,
):
    create_segment(crutches={'force_crutch_builder': True})
    await state_waybill_created()

    waybill_ref = get_single_waybill()['id']

    assert not propositions_manager.propositions
    await stq_runner.united_dispatch_waybill_propose.call(
        task_id=waybill_ref, kwargs={'waybill_ref': waybill_ref},
    )
    assert len(propositions_manager.propositions) == 1

    assert get_single_waybill()['proposition_status'] == 'sent'


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


async def test_propose_error_500(
        create_segment,
        state_waybill_created,
        get_single_waybill,
        stq_runner,
        mockserver,
):
    """
        Check stq retry on /propose 500.
    """

    create_segment(crutches={'force_crutch_builder': True})

    await state_waybill_created()

    waybill_ref = get_single_waybill()['id']

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/propose')
    def mock_propose(request):
        return mockserver.make_response(status=500)

    await stq_runner.united_dispatch_waybill_propose.call(
        task_id=waybill_ref,
        kwargs={'waybill_ref': waybill_ref},
        expect_fail=True,
    )

    assert mock_propose.times_called


async def test_taxi_requirements(
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
        state_waybill_proposed,
        create_segment,
):
    create_segment(
        crutches={
            'force_crutch_builder': True,
            'forced_soon': True,
            'taxi_classes': ['foo', 'bar'],
        },
    )

    await state_waybill_proposed()

    assert len(propositions_manager.propositions) == 1
    proposition = propositions_manager.propositions[0]
    assert proposition['taxi_order_requirements'] == {
        'forced_soon': True,
        'taxi_classes': ['foo', 'bar'],
    }


async def test_segment_revision_inc_after_proposition(
        state_waybill_created,
        get_single_waybill,
        autorun_propose,
        create_segment,
        increment_segment_revision,
        get_segment,
):
    """
        Check proposition ok if segment revision increase
        after waybill_ref is set.
    """
    seg1 = create_segment(crutches={'force_crutch_builder': True})

    await state_waybill_created()

    increment_segment_revision(segment_id=seg1.id)

    await autorun_propose()

    waybill_ref = get_single_waybill()['id']
    assert get_single_waybill()['proposition_status'] == 'sent'
    assert get_segment(seg1.id)['waybill_ref'] == waybill_ref


async def test_simultaneous_regular_proposition(
        state_waybill_created,
        get_single_waybill,
        autorun_propose,
        create_segment,
        exp_delivery_configs,
        increment_segment_revision,
        get_segment,
        testpoint,
):
    """
        Check regular proposition failed if another proposition
        mark segment faster.

        batch proposition for two segments, seg1 choses
        another proposition.
    """
    seg1 = create_segment(crutches={'wait_for_batch': True})
    seg2 = create_segment(crutches={'batch_with': seg1.id})

    @testpoint('MarkSegmentPropositionsOptional')
    async def planner_interrupt(data):
        increment_segment_revision(segment_id=seg1.id)

    await exp_delivery_configs()

    await state_waybill_created()

    assert planner_interrupt.times_called
    await autorun_propose()

    assert get_single_waybill()['external_resolution'] == 'proposition_failed'
    assert get_segment(seg1.id)['waybill_ref'] is None
    assert get_segment(seg2.id)['waybill_ref'] is None


async def test_simultaneous_update_segment(
        state_taxi_order_performer_found,
        state_waybill_created,
        get_waybill_by_segment,
        get_waybill,
        autorun_propose,
        create_segment,
        increment_segment_revision,
        get_segment,
        testpoint,
        propositions_manager,
):
    """
        Check update proposition failed if another proposition
        mark segment faster.
    """
    seg1 = create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_performer_found()

    assert len(propositions_manager.propositions) == 1
    previous_waybill_ref = get_segment(seg1.id)['waybill_ref']
    assert previous_waybill_ref

    seg2 = create_segment(crutches={'live_batch_with': seg1.id})

    @testpoint('MarkSegmentPropositionsOptional')
    async def planner_interrupt(data):
        increment_segment_revision(segment_id=seg2.id)

    await state_waybill_created()

    assert planner_interrupt.times_called
    await autorun_propose()
    assert not propositions_manager.live_propositions

    assert (
        get_waybill_by_segment(seg2.id)['external_resolution']
        == 'proposition_failed'
    )
    assert get_segment(seg1.id)['waybill_ref'] == previous_waybill_ref
    assert get_waybill(previous_waybill_ref)['update_proposition_id'] is None
    assert get_segment(seg2.id)['waybill_ref'] is None


async def test_simultaneous_update_proposition(
        state_taxi_order_performer_found,
        state_waybill_created,
        get_waybill_by_segment,
        autorun_propose,
        create_segment,
        increment_waybill_revision,
        get_segment,
        get_waybill,
        testpoint,
        propositions_manager,
):
    """
        Check update proposition failed if another proposition
        previous waybill faster.
    """
    seg1 = create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_performer_found()

    assert len(propositions_manager.propositions) == 1
    previous_waybill_ref = get_segment(seg1.id)['waybill_ref']
    assert previous_waybill_ref

    seg2 = create_segment(crutches={'live_batch_with': seg1.id})

    @testpoint('MarkWaybillPropositionsOptional')
    async def planner_interrupt(data):
        increment_waybill_revision(waybill_id=previous_waybill_ref)

    await state_waybill_created()

    assert planner_interrupt.times_called
    await autorun_propose()
    assert not propositions_manager.live_propositions

    assert (
        get_waybill_by_segment(seg2.id)['external_resolution']
        == 'proposition_failed'
    )
    assert get_segment(seg1.id)['waybill_ref'] == previous_waybill_ref
    assert get_waybill(previous_waybill_ref)['update_proposition_id'] is None
    assert get_segment(seg2.id)['waybill_ref'] is None


async def test_timeout_set_waybill(
        state_waybill_proposed,
        get_single_waybill,
        create_segment,
        propositions_manager,
        get_segment,
        testpoint,
        stq_runner,
):
    """
        Check stq processed success on retry if set waybill ref
        failed by timeout.
    """
    seg = create_segment(crutches={'force_crutch_builder': True})

    raise_exception = True

    @testpoint('SetRefForWaybillSegments')
    async def injection(data):
        return {'raise_exception': raise_exception}

    await state_waybill_proposed()

    # first try failed but waybill_ref was marked
    waybill_ref = get_single_waybill()['id']
    assert injection.times_called
    assert get_segment(seg.id)['waybill_ref'] == waybill_ref
    assert not propositions_manager.propositions

    # second try proposition sent
    raise_exception = False
    await stq_runner.united_dispatch_waybill_propose.call(
        task_id='test', kwargs={'waybill_ref': waybill_ref},
    )
    assert propositions_manager.propositions
    assert get_segment(seg.id)['waybill_ref'] == waybill_ref


async def test_timeout_mark_update_proposition(
        state_taxi_order_performer_found,
        state_waybill_proposed,
        get_waybill,
        create_segment,
        propositions_manager,
        get_segment,
        testpoint,
        stq_runner,
):
    """
        Check stq processed success on retry if set proposition
        for previous waybill timeouted.
    """
    seg1 = create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_performer_found()

    assert len(propositions_manager.propositions) == 1
    previous_waybill_ref = get_segment(seg1.id)['waybill_ref']
    assert previous_waybill_ref

    seg2 = create_segment(crutches={'live_batch_with': seg1.id})

    raise_exception = True

    @testpoint('SetRefForPreviousWaybill')
    async def injection(data):
        return {'raise_exception': raise_exception}

    await state_waybill_proposed()

    # first try failed but update_proposition_id was set
    update_proposition_ref = get_segment(seg2.id)['waybill_ref']
    assert update_proposition_ref
    assert (
        get_waybill(previous_waybill_ref)['update_proposition_id']
        == update_proposition_ref
    )
    assert get_waybill(update_proposition_ref)['proposition_status'] == 'new'
    assert injection.times_called
    assert not propositions_manager.live_propositions

    # second try proposition sent
    raise_exception = False
    await stq_runner.united_dispatch_waybill_propose.call(
        task_id='test', kwargs={'waybill_ref': update_proposition_ref},
    )
    assert propositions_manager.live_propositions
    assert get_segment(seg2.id)['waybill_ref'] == update_proposition_ref
    assert (
        get_waybill(previous_waybill_ref)['update_proposition_id']
        == update_proposition_ref
    )
    assert (
        get_waybill(update_proposition_ref)['proposition_status'] == 'waiting'
    )
