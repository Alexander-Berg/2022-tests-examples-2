import pytest

from testsuite.utils import matching

from tests_united_dispatch.plugins import cargo_dispatch_manager


@pytest.fixture(name='processed_testpoint')
async def _processed_testpoint(testpoint):
    @testpoint('united_dispatch_waybill_reader::Process')
    def _testpoint(data):
        pass

    return _testpoint


async def test_replication(
        create_segment, state_waybill_accepted, stq_runner, get_single_waybill,
):
    """
        Check waybill event processed (external waybill info replicated).
    """
    create_segment(crutches={'force_crutch_builder': True})

    state = await state_waybill_accepted()

    await stq_runner.united_dispatch_waybill_reader.call(
        task_id='test',
        kwargs={
            'waybill_ref': state.get_proposed_waybill_ref(),
            'waybill_revision': 1,
        },
    )

    waybill = get_single_waybill()
    assert waybill['waybill']['revision'] == 1


async def test_not_processed_outdated(
        create_segment,
        state_waybill_accepted,
        stq_runner,
        processed_testpoint,
):
    """
        Check outdated stq ignored. (old revision)
    """
    create_segment(crutches={'force_crutch_builder': True})

    state = await state_waybill_accepted()

    # process with current revision
    await stq_runner.united_dispatch_waybill_reader.call(
        task_id='test',
        kwargs={
            'waybill_ref': state.get_proposed_waybill_ref(),
            'waybill_revision': 1,
        },
    )

    assert processed_testpoint.times_called == 1

    # not processed with old revision
    processed_testpoint.flush()
    await stq_runner.united_dispatch_waybill_reader.call(
        task_id='test',
        kwargs={
            'waybill_ref': state.get_proposed_waybill_ref(),
            'waybill_revision': 0,
        },
    )

    assert not processed_testpoint.times_called


async def test_repeat(
        create_segment,
        state_waybill_accepted,
        stq_runner,
        processed_testpoint,
):
    """
        Check waybill not processed for second time.
    """
    create_segment(crutches={'force_crutch_builder': True})

    state = await state_waybill_accepted()

    # process with current revision
    await stq_runner.united_dispatch_waybill_reader.call(
        task_id='test',
        kwargs={
            'waybill_ref': state.get_proposed_waybill_ref(),
            'waybill_revision': 1,
        },
    )

    assert processed_testpoint.times_called == 1

    # check do nothing on repeat
    processed_testpoint.flush()
    await stq_runner.united_dispatch_waybill_reader.call(
        task_id='test',
        kwargs={
            'waybill_ref': state.get_proposed_waybill_ref(),
            'waybill_revision': 1,
        },
    )
    assert not processed_testpoint.times_called


async def test_not_processed_resolved(
        create_segment,
        state_waybill_accepted,
        stq_runner,
        processed_testpoint,
):
    """
        Check resolved waybill ignored.
    """
    create_segment(crutches={'force_crutch_builder': True})

    await state_waybill_accepted()

    processed_testpoint.flush()
    await stq_runner.united_dispatch_waybill_reader.call(
        task_id='test',
        kwargs={
            'waybill_ref': 'united-dispatch/0/delivery/resolved_waybill',
            'waybill_revision': 1,
        },
    )

    assert not processed_testpoint.has_calls


async def test_performer_stored(
        create_segment, state_taxi_order_performer_found, get_single_waybill,
):
    """
        Check performer stored on waybill performer found.
    """
    create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_performer_found()

    waybill = get_single_waybill()
    assert waybill['waybill']['performer'] == {
        'id': matching.any_string,
        'found_ts': matching.any_string,
        'tariff_class': 'express',
    }


async def test_taxi_order_stored(
        create_segment, state_taxi_order_created, get_single_waybill,
):
    """
        Check taxi_order_id stored on waybill journal event.
    """
    create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_created()

    waybill = get_single_waybill()
    assert waybill['waybill']['taxi_order_id'] == matching.any_string


async def test_waybill_resolved(
        create_segment,
        state_waybill_accepted,
        cargo_dispatch,
        get_single_waybill,
        run_waybill_reader,
):
    """
        Check waybill marked resolved.
    """
    create_segment(crutches={'force_crutch_builder': True})
    state = await state_waybill_accepted()
    waybill_ref = state.get_proposed_waybill_ref()

    cargo_dispatch.waybills.set_resolved(waybill_ref)
    await run_waybill_reader()

    waybill = get_single_waybill()
    assert 'external_resolution' in waybill


@pytest.mark.config(
    UNITED_DISPATCH_REJECTED_CANDIDATES_SETTINGS={'enabled': True},
)
async def test_waybill_resolution_failed(
        state_taxi_order_performer_found,
        cargo_dispatch,
        get_single_waybill,
        run_waybill_reader,
        get_rejected_candidates,
        make_rejected_candidates_delivery_ids,
        create_segment,
):
    """
        Check waybill marked resolved.
    """
    seg = create_segment(crutches={'force_crutch_builder': True})
    state = await state_taxi_order_performer_found()

    waybill_ref = state.get_proposed_waybill_ref()

    assert not get_rejected_candidates(segment=seg)

    cargo_dispatch.waybills.set_resolved(waybill_ref, 'failed')
    await run_waybill_reader()

    waybill = get_single_waybill()
    assert 'external_resolution' in waybill

    # check rejected candidate was stored.
    expected_ids = make_rejected_candidates_delivery_ids(segment=seg)
    assert get_rejected_candidates(segment=seg) == [
        {'delivery_id': id, 'candidate_id': matching.any_string}
        for id in expected_ids
    ]


async def test_multiple_events(
        create_segment,
        state_waybill_accepted,
        cargo_dispatch,
        get_single_waybill,
        run_waybill_reader,
):
    """
        Check multiple events processed at once.
    """
    create_segment(crutches={'force_crutch_builder': True})
    state = await state_waybill_accepted()
    waybill_ref = state.get_proposed_waybill_ref()

    cargo_dispatch.waybills.set_taxi_order(waybill_ref)
    cargo_dispatch.waybills.set_performer(waybill_ref)
    cargo_dispatch.waybills.set_resolved(waybill_ref)

    await run_waybill_reader()

    waybill = get_single_waybill()
    assert (
        waybill['waybill']['taxi_order_id'] == matching.any_string
    )  # check taxi_order_id stored
    assert waybill['waybill']['performer'] == {
        'id': matching.any_string,
        'found_ts': matching.any_string,
        'tariff_class': 'express',
    }  # check performer stored
    assert 'external_resolution' in waybill  # check resolution stored


async def test_resolved_not_processed(
        create_segment, state_waybill_resolved, stq_runner, testpoint,
):
    """
        Check resolved waybill not processed.
    """
    create_segment(crutches={'force_crutch_builder': True})
    state = await state_waybill_resolved()

    @testpoint('united_dispatch_waybill_reader::Resolved')
    def _testpoint(data):
        pass

    await stq_runner.united_dispatch_waybill_reader.call(
        task_id='test',
        kwargs={
            'waybill_ref': state.get_proposed_waybill_ref(),
            'waybill_revision': 1,
        },
    )

    assert _testpoint.times_called


async def test_points_resolution(
        create_segment,
        state_waybill_proposed,
        cargo_dispatch,
        run_waybill_reader,
        get_waybill,
        visit_order=1,
):
    """
        Check updated resolution for waybill points.
    """
    create_segment(crutches={'force_crutch_builder': True})
    state = await state_waybill_proposed()
    waybill_ref = state.get_proposed_waybill_ref()

    cargo_dispatch.waybills.set_point_resolution(
        waybill_ref=waybill_ref, visit_order=visit_order, is_visited=True,
    )
    await run_waybill_reader()

    waybill = get_waybill(waybill_ref)
    assert waybill['waybill']['path'][visit_order]['resolution'] == 'visited'


async def test_live_proposition_accepted(
        create_segment,
        state_taxi_order_performer_found,
        state_waybill_proposed,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
        cargo_dispatch: cargo_dispatch_manager.CargoDispatch,
        get_segment,
        get_waybill,
        run_waybill_reader,
):
    """
        Check update proposition happy path.
        => live batch created
        => live batch proposition commited
        => live batch sent to cargo-dispatch
        => live batch accepted by courier
    """
    seg1 = create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_performer_found()

    assert len(propositions_manager.propositions) == 1

    seg2 = create_segment(crutches={'live_batch_with': seg1.id})

    await state_waybill_proposed()

    assert len(propositions_manager.propositions) == 1  # still 1
    assert len(propositions_manager.live_propositions) == 1
    previous_waybill_ref = propositions_manager.propositions[0]['external_ref']
    new_waybill_ref = list(propositions_manager.live_propositions.values())[0][
        'external_ref'
    ]

    await run_waybill_reader()
    # old segment have previous waybill_ref yet
    assert get_segment(seg1.id)['waybill_ref'] == previous_waybill_ref
    assert get_segment(seg2.id)['waybill_ref'] == new_waybill_ref
    assert get_waybill(new_waybill_ref)['proposition_status'] == 'waiting'

    # update proposition accepted => update waybill_ref
    cargo_dispatch.waybills.set_update_proposition_accepted(new_waybill_ref)
    await run_waybill_reader()

    # check segment's waybills updated and previous waybill resolved
    assert get_segment(seg1.id)['waybill_ref'] == new_waybill_ref
    assert get_segment(seg2.id)['waybill_ref'] == new_waybill_ref
    assert (
        get_waybill(previous_waybill_ref)['update_proposition_id']
        == new_waybill_ref
    )
    assert get_waybill(previous_waybill_ref)['external_resolution'] is None
    assert get_waybill(new_waybill_ref)['proposition_status'] == 'sent'


@pytest.mark.parametrize(
    'event, clean_waybill_on_decline',
    [
        ('not_in_dispatch', True),
        ('declined_by_dispatch', True),
        ('declined_by_dispatch', False),
    ],
)
async def test_live_proposition_declined(
        create_segment,
        exp_proposition_fail,
        state_taxi_order_performer_found,
        state_waybill_proposed,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
        cargo_dispatch: cargo_dispatch_manager.CargoDispatch,
        get_segment,
        get_waybill,
        run_waybill_reader,
        stq,
        autorun_fail,
        event: str,
        clean_waybill_on_decline: bool,
):
    """
        Check proposition declined by courier.
    """
    seg1 = create_segment(crutches={'force_crutch_builder': True})
    await exp_proposition_fail(
        clean_waybill_on_decline=clean_waybill_on_decline,
    )

    await state_taxi_order_performer_found()

    assert len(propositions_manager.propositions) == 1

    seg2 = create_segment(crutches={'live_batch_with': seg1.id})

    await state_waybill_proposed()

    assert len(propositions_manager.propositions) == 1  # still 1
    assert len(propositions_manager.live_propositions) == 1
    previous_waybill_ref = propositions_manager.propositions[0]['external_ref']
    new_waybill_ref = list(propositions_manager.live_propositions.values())[0][
        'external_ref'
    ]

    await run_waybill_reader()
    # old segment have previous waybill_ref yet
    assert get_segment(seg1.id)['waybill_ref'] == previous_waybill_ref
    assert get_segment(seg2.id)['waybill_ref'] == new_waybill_ref

    # update proposition accepted => update waybill_ref
    if event == 'not_in_dispatch':
        # this is happens sometimes due to bug, remove after fix
        cargo_dispatch.waybills.drop_update_proposition(new_waybill_ref)
    elif event == 'declined_by_dispatch':
        cargo_dispatch.waybills.set_update_proposition_declined(
            new_waybill_ref,
        )
    await run_waybill_reader()

    # old segment have previous waybill_ref yet
    assert get_segment(seg1.id)['waybill_ref'] == previous_waybill_ref
    assert get_segment(seg2.id)['waybill_ref'] == new_waybill_ref

    # check update proposition transaction rollbacked
    assert stq.united_dispatch_proposition_fail.has_calls
    await autorun_fail()

    assert get_segment(seg1.id)['waybill_ref'] == previous_waybill_ref
    assert get_segment(seg2.id)['waybill_ref'] is None
    if clean_waybill_on_decline:
        assert (
            get_waybill(previous_waybill_ref)['update_proposition_id'] is None
        )
    else:
        assert (
            get_waybill(previous_waybill_ref)['update_proposition_id']
            == new_waybill_ref
        )
    assert get_waybill(previous_waybill_ref)['external_resolution'] is None
    assert get_waybill(new_waybill_ref)['external_resolution'] == 'declined'


@pytest.mark.config(
    UNITED_DISPATCH_REJECTED_CANDIDATES_SETTINGS={'enabled': True},
)
async def test_performer_droped(
        state_taxi_order_performer_found,
        get_waybill,
        cargo_dispatch,
        run_waybill_reader,
        get_rejected_candidates,
        make_rejected_candidates_delivery_ids,
        create_segment,
):
    """
        Check performer stored and then droped.
        Check rejection was stored.
    """
    seg = create_segment(crutches={'force_crutch_builder': True})
    state = await state_taxi_order_performer_found()

    waybill_ref = state.get_proposed_waybill_ref()
    assert get_waybill(waybill_ref)['waybill']['performer'] == {
        'id': matching.any_string,
        'found_ts': matching.any_string,
        'tariff_class': 'express',
    }

    assert not get_rejected_candidates(segment=seg)

    cargo_dispatch.waybills.drop_performer(waybill_ref)
    await run_waybill_reader()

    assert 'performer' not in get_waybill(waybill_ref)['waybill']

    # check rejected candidate was stored.
    expected_ids = make_rejected_candidates_delivery_ids(segment=seg)
    assert get_rejected_candidates(segment=seg) == [
        {'delivery_id': id, 'candidate_id': matching.any_string}
        for id in expected_ids
    ]


async def test_accept_update_proposition_accept_idempotency(
        create_segment,
        state_taxi_order_performer_found,
        state_waybill_proposed,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
        cargo_dispatch: cargo_dispatch_manager.CargoDispatch,
        get_waybill,
        run_waybill_reader,
        testpoint,
        stq_runner,
):
    """
        Check update proposition finishes if timeout happens during
        set waybill_ref on segments of previous waybill.
    """
    seg1 = create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_performer_found()

    assert len(propositions_manager.propositions) == 1

    create_segment(crutches={'live_batch_with': seg1.id})

    await state_waybill_proposed()

    assert len(propositions_manager.propositions) == 1  # still 1
    assert len(propositions_manager.live_propositions) == 1
    new_waybill_ref = list(propositions_manager.live_propositions.values())[0][
        'external_ref'
    ]

    # timeout after set waybill_ref for segments
    raise_exception = True

    @testpoint('UpdateSegmentsPropositionsStq')
    async def injection(data):
        return {'raise_exception': raise_exception}

    cargo_dispatch.waybills.set_update_proposition_accepted(new_waybill_ref)

    # check operation is not applied yet
    assert get_waybill(new_waybill_ref)['proposition_status'] == 'waiting'

    await run_waybill_reader(only_journal=True)
    kwargs = {
        'waybill_ref': new_waybill_ref,
        'waybill_revision': cargo_dispatch.get_waybill(
            waybill_ref=new_waybill_ref,
        ).revision,
    }
    await stq_runner.united_dispatch_waybill_reader.call(
        task_id='test', kwargs=kwargs, expect_fail=True,
    )
    assert injection.times_called

    # check operation is not applied yet
    assert get_waybill(new_waybill_ref)['proposition_status'] == 'waiting'

    raise_exception = False

    await stq_runner.united_dispatch_waybill_reader.call(
        task_id='test', kwargs=kwargs, expect_fail=False,
    )
    # check operation applied
    assert get_waybill(new_waybill_ref)['proposition_status'] == 'sent'
