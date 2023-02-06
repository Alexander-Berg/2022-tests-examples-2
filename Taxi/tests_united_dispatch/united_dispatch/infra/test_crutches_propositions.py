from tests_united_dispatch.plugins import cargo_dispatch_manager


async def test_forced_batch(
        create_segment,
        state_waybill_proposed,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
):
    seg1 = create_segment(crutches={'wait_for_batch': True})
    seg2 = create_segment(crutches={'batch_with': seg1.id})

    await state_waybill_proposed()

    assert len(propositions_manager.propositions) == 1

    segments_proposed = set()
    for proposition in propositions_manager.propositions:
        segments_proposed.add(
            frozenset(seg['segment_id'] for seg in proposition['segments']),
        )
    assert segments_proposed == {frozenset([seg1.id, seg2.id])}


async def test_forced_live_batch(
        create_segment,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
):
    """
        Check crutches planner makes live batch
        proposition for new segment.
    """
    seg1 = create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_performer_found()

    assert len(propositions_manager.propositions) == 1

    seg2 = create_segment(crutches={'live_batch_with': seg1.id})

    await state_waybill_proposed()

    assert len(propositions_manager.propositions) == 1  # still one proposed
    assert len(propositions_manager.live_propositions) == 1
    segments_proposed = set()
    for proposition in propositions_manager.live_propositions.values():
        segments_proposed.add(
            frozenset(seg['segment_id'] for seg in proposition['segments']),
        )
    assert segments_proposed == {frozenset([seg1.id, seg2.id])}


async def test_live_batch_awaited(
        create_segment,
        state_taxi_order_performer_found,
        state_waybill_proposed,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
):
    """
        Check crutches proposition awaited.
    """
    # both segments proposed at once, seg2 should await seg1
    seg1 = create_segment(crutches={'force_crutch_builder': True})
    seg2 = create_segment(crutches={'live_batch_with': seg1.id})

    await state_taxi_order_performer_found()

    assert len(propositions_manager.propositions) == 1
    assert not propositions_manager.live_propositions
    for proposition in propositions_manager.propositions:
        segments_proposed = frozenset(
            seg['segment_id'] for seg in proposition['segments']
        )
        assert segments_proposed == frozenset([seg1.id])

    # second time there is waybill for seg1, live proposition proposed
    await state_waybill_proposed()

    assert len(propositions_manager.live_propositions) == 1
    for proposition in propositions_manager.live_propositions.values():
        segments_proposed = frozenset(
            seg['segment_id'] for seg in proposition['segments']
        )
        assert segments_proposed == frozenset([seg1.id, seg2.id])


async def test_target_contractor_id(
        taxi_united_dispatch,
        create_segment,
        state_taxi_order_performer_found,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
):
    seg1 = create_segment(crutches={'target_contractor_id': 'dbid2_uuid2'})

    await state_taxi_order_performer_found()

    assert len(propositions_manager.propositions) == 1
    assert (
        propositions_manager.propositions[0]['taxi_order_requirements'][
            'lookup_extra'
        ]['performer_id']
        == 'dbid2_uuid2'
    )


async def test_target_contractor_id_in_batch(
        taxi_united_dispatch,
        create_segment,
        state_taxi_order_performer_found,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
):
    seg1 = create_segment(
        crutches={
            'target_contractor_id': 'dbid2_uuid2',
            'wait_for_batch': True,
        },
    )
    seg2 = create_segment(crutches={'batch_with': seg1.id})

    await state_taxi_order_performer_found()

    assert len(propositions_manager.propositions) == 1
    assert (
        propositions_manager.propositions[0]['taxi_order_requirements'][
            'lookup_extra'
        ]['performer_id']
        == 'dbid2_uuid2'
    )
