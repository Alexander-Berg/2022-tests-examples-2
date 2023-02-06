# pylint: disable=redefined-outer-name
from tests_united_dispatch.plugins import cargo_dispatch_manager


async def test_nobatch(
        create_segment,
        state_waybill_proposed,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
):
    seg1 = create_segment()
    seg2 = create_segment()

    await state_waybill_proposed()

    assert len(propositions_manager.propositions) == 2

    segments_proposed = set()
    for proposition in propositions_manager.propositions:
        segments_proposed.add(
            frozenset(seg['segment_id'] for seg in proposition['segments']),
        )
    assert segments_proposed == {frozenset([seg1.id]), frozenset([seg2.id])}
