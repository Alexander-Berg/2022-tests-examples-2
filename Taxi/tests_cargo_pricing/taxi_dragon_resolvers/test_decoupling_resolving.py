import copy

from tests_cargo_pricing.taxi_dragon_resolvers import models
from tests_cargo_pricing.taxi_dragon_resolvers import utils


async def test_decoupling_claim_happy_path(
        cargo_matcher_claim_estimating, cargo_claims_change_claim_order_price,
):
    segment = models.make_segment(payment_info=models.PaymentMethod.CORP)

    matcher_response, new_events = await cargo_matcher_claim_estimating(
        segment,
    )
    assert matcher_response.status_code == 200
    assert utils.extract_events_kinds(new_events) == set(
        ['create', 'calculation'],
    )

    final_response, new_events = await cargo_claims_change_claim_order_price(
        segment,
    )
    assert final_response.status_code == 200

    body = final_response.json()
    assert body.get('calc_for_performer') is None
    client_calc = body['calc_for_client']
    assert utils.extract_previous_calc_id(
        client_calc,
    ) == utils.extract_calc_id(matcher_response)
    assert utils.extract_events_kinds(new_events) == set(
        ['calculation', 'confirm-usage'],
    )


async def test_decoupling_corp_waybill_happy_path(
        v1_calc_price__driver_offer, v1_calc_price__driver_final,
):
    waybill = models.make_waybill(resolution=models.Resolution.COMPLETED)
    waybill.add_segment(
        models.make_segment(payment_info=models.PaymentMethod.CORP),
    )
    waybill.add_segment(
        models.make_segment(payment_info=models.PaymentMethod.CORP),
    )

    performer = models.Performer.FIRST

    offer, offer_new_events = await v1_calc_price__driver_offer(
        waybill, performer,
    )
    final, final_new_events = await v1_calc_price__driver_final(
        waybill, performer,
    )

    assert offer.status_code == 200
    assert final.status_code == 200

    offer_segments = offer.json()['segments']
    final_segments = final.json()['segments']

    offer_b2b_segment = offer_segments[0]
    final_b2b_segment = final_segments[0]
    for (b2b_segment, new_events, calc_kind) in [
            (offer_b2b_segment, offer_new_events, 'offer'),
            (final_b2b_segment, final_new_events, 'final'),
    ]:
        assert b2b_segment.get('calc_for_client') is None
        assert b2b_segment['calc_for_performer']
        assert b2b_segment['legal_scheme'] == 'decoupling_based'
        assert new_events[-2]['payload']['kind'] == 'calculation'
        assert new_events[-2]['payload']['price_for'] == 'performer'
        assert new_events[-2]['payload']['calc_kind'] == calc_kind
        assert new_events[-2]['payload']['calc_id'] == utils.extract_calc_id(
            b2b_segment['calc_for_performer'],
        )
    assert utils.extract_previous_calc_id(
        final_b2b_segment['calc_for_performer'],
    ) == utils.extract_calc_id(offer_b2b_segment['calc_for_performer'])


async def test_decoupling_double_estimation(
        cargo_matcher_claim_estimating, cargo_claims_change_claim_order_price,
):
    segment = models.make_segment(payment_info=models.PaymentMethod.CORP)

    first_estimate, _ = await cargo_matcher_claim_estimating(segment)
    second_estimate, _ = await cargo_matcher_claim_estimating(segment)

    final_calc, _ = await cargo_claims_change_claim_order_price(segment)

    assert utils.extract_previous_calc_id(
        final_calc.json()['calc_for_client'],
    ) == utils.extract_calc_id(second_estimate)
    assert utils.extract_calc_id(first_estimate) != utils.extract_calc_id(
        second_estimate,
    )


async def test_decoupling_independent_of_driver(
        cargo_matcher_claim_estimating, cargo_claims_change_claim_order_price,
):
    segment = models.make_segment(payment_info=models.PaymentMethod.CORP)

    await cargo_matcher_claim_estimating(segment)

    first_final_calc_resp, _ = await cargo_claims_change_claim_order_price(
        segment, models.Performer.FIRST,
    )
    second_final_calc_resp, second_try_events = (
        await cargo_claims_change_claim_order_price(
            segment, models.Performer.SECOND,
        )
    )

    first_calc = first_final_calc_resp.json()['calc_for_client']
    second_calc = second_final_calc_resp.json()['calc_for_client']

    assert utils.extract_calc_id(first_calc) == utils.extract_calc_id(
        second_calc,
    )
    assert not second_try_events


async def test_decoupling_race_409(
        cargo_matcher_claim_estimating,
        cargo_claims_change_claim_order_price,
        processing_state,
):
    segment = models.make_segment(payment_info=models.PaymentMethod.CORP)
    await cargo_matcher_claim_estimating(segment)

    resp, _ = await cargo_claims_change_claim_order_price(segment)
    assert resp.status_code == 200

    cur_events = processing_state.events_by_item_id[segment.id]
    # remove confirm-usage to avoid querying existing
    del cur_events[-1]
    cur_events[-1]['payload']['revision'] = len(cur_events)

    resp, _ = await cargo_claims_change_claim_order_price(segment)
    assert resp.status_code == 409


async def test_decoupling_double_resolve(
        cargo_matcher_claim_estimating, cargo_claims_change_claim_order_price,
):
    segment = models.make_segment(payment_info=models.PaymentMethod.CORP)
    await cargo_matcher_claim_estimating(segment)

    final_calc_resp, _ = await cargo_claims_change_claim_order_price(segment)
    assert final_calc_resp.status_code == 200

    final_retrieve_resp, _ = await cargo_claims_change_claim_order_price(
        segment,
    )
    assert final_retrieve_resp.status_code == 200

    calc = final_calc_resp.json()['calc_for_client']
    retrieved_calc = final_retrieve_resp.json()['calc_for_client']
    assert utils.extract_calc_id(calc) == utils.extract_calc_id(retrieved_calc)


async def test_decoupling_ignore_race_events_on_second_call(
        cargo_matcher_claim_estimating,
        cargo_claims_change_claim_order_price,
        processing_state,
):
    segment = models.make_segment(payment_info=models.PaymentMethod.CORP)
    await cargo_matcher_claim_estimating(segment)

    final_calc_resp, new_events = await cargo_claims_change_claim_order_price(
        segment,
    )
    assert final_calc_resp.status_code == 200

    race_events = copy.deepcopy(new_events)
    for i, _ in enumerate(race_events):
        race_events[i]['payload']['calc_id'] = 'cargo-pricing/v1/' + 'b' * 32
    processing_state.events_by_item_id[segment.id].extend(race_events)

    final_retrieve_resp, _ = await cargo_claims_change_claim_order_price(
        segment,
    )
    assert final_retrieve_resp.status_code == 200

    calc = final_calc_resp.json()['calc_for_client']
    retrieved_calc = final_retrieve_resp.json()['calc_for_client']
    assert utils.extract_calc_id(calc) == utils.extract_calc_id(retrieved_calc)
