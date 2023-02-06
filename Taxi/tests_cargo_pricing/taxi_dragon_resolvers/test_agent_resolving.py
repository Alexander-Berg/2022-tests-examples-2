import copy

from tests_cargo_pricing.taxi_dragon_resolvers import models
from tests_cargo_pricing.taxi_dragon_resolvers import utils


async def test_yandex_go_claim_happy_path(
        v1_calc_price__driver_offer,
        v1_calc_price__driver_final,
        make_yandex_go_offer,
        cargo_claims_change_claim_order_price,
):
    segment = models.make_segment(payment_info=models.PaymentMethod.CARD)

    offer_client_resp, _ = await make_yandex_go_offer(segment)

    waybill = models.make_waybill(resolution=models.Resolution.COMPLETED)
    waybill.add_segment(segment)

    performer = models.Performer.FIRST

    offer_driver_resp, _ = await v1_calc_price__driver_offer(
        waybill, performer,
    )
    final_driver_resp, _ = await v1_calc_price__driver_final(
        waybill, performer,
    )

    final_client_resp, _ = await cargo_claims_change_claim_order_price(
        segment, performer,
    )

    assert offer_client_resp.status_code == 200
    assert offer_driver_resp.status_code == 200
    assert final_driver_resp.status_code == 200
    assert final_client_resp.status_code == 200

    offer_client_segment = offer_client_resp.json()
    final_client_segment = final_client_resp.json()
    offer_driver_segment = offer_driver_resp.json()['segments'][0]
    final_driver_segment = final_driver_resp.json()['segments'][0]

    assert utils.extract_calc_id(
        final_driver_segment['calc_for_client'],
    ) == utils.extract_calc_id(final_client_segment['calc_for_client'])
    assert utils.extract_calc_id(
        final_driver_segment['calc_for_performer'],
    ) == utils.extract_calc_id(final_client_segment['calc_for_performer'])
    assert utils.extract_previous_calc_id(
        final_driver_segment['calc_for_client'],
    ) == utils.extract_calc_id(offer_client_resp)
    assert utils.extract_previous_calc_id(
        final_driver_segment['calc_for_performer'],
    ) == utils.extract_calc_id(final_driver_segment['calc_for_client'])
    assert utils.extract_calc_id(
        offer_driver_segment['calc_for_client'],
    ) == utils.extract_calc_id(offer_client_segment)
    assert utils.extract_previous_calc_id(
        final_client_segment['calc_for_client'],
    ) == utils.extract_calc_id(offer_client_segment)


async def test_yandex_go_claim_reorder(
        v1_calc_price__driver_offer,
        v1_calc_price__driver_final,
        make_yandex_go_offer,
        cargo_claims_change_claim_order_price,
):
    segment = models.make_segment(payment_info=models.PaymentMethod.CARD)

    await make_yandex_go_offer(segment)

    waybill = models.make_waybill(resolution=models.Resolution.COMPLETED)
    waybill.add_segment(segment)

    performer = models.Performer.FIRST

    await v1_calc_price__driver_offer(waybill, performer)
    final_resp_1, _ = await v1_calc_price__driver_final(waybill, performer)

    performer = models.Performer.SECOND

    await v1_calc_price__driver_offer(waybill, performer)
    final_resp_2, _ = await v1_calc_price__driver_final(waybill, performer)

    final_client_resp, _ = await cargo_claims_change_claim_order_price(
        segment, performer,
    )

    driver_segment_1 = final_resp_1.json()['segments'][0]
    driver_segment_2 = final_resp_2.json()['segments'][0]
    client_segment = final_client_resp.json()

    assert utils.extract_calc_id(
        driver_segment_1['calc_for_client'],
    ) != utils.extract_calc_id(client_segment['calc_for_client'])
    assert utils.extract_calc_id(
        driver_segment_2['calc_for_client'],
    ) == utils.extract_calc_id(client_segment['calc_for_client'])


async def test_yandex_go_claim_race_409(
        make_yandex_go_offer,
        v1_calc_price__driver_offer,
        v1_calc_price__driver_final,
        processing_state,
):
    segment = models.make_segment(payment_info=models.PaymentMethod.CARD)
    await make_yandex_go_offer(segment)

    waybill = models.make_waybill(resolution=models.Resolution.COMPLETED)
    waybill.add_segment(segment)

    performer = models.Performer.FIRST
    await v1_calc_price__driver_offer(waybill, performer)

    resp, _ = await v1_calc_price__driver_final(waybill, performer)
    assert resp.status_code == 200

    cur_events = processing_state.events_by_item_id[segment.id]
    # remove confirm-usage to avoid querying existing
    del cur_events[-1]
    cur_events[-1]['payload']['revision'] = len(cur_events)

    resp, _ = await v1_calc_price__driver_final(waybill, performer)
    assert resp.status_code == 409


async def test_yandex_go_claim_double_resolve(
        make_yandex_go_offer,
        v1_calc_price__driver_offer,
        v1_calc_price__driver_final,
):

    segment = models.make_segment(payment_info=models.PaymentMethod.CARD)
    await make_yandex_go_offer(segment)

    waybill = models.make_waybill(resolution=models.Resolution.COMPLETED)
    waybill.add_segment(segment)

    performer = models.Performer.FIRST
    await v1_calc_price__driver_offer(waybill, performer)

    final_calc_resp, _ = await v1_calc_price__driver_final(waybill, performer)
    assert final_calc_resp.status_code == 200
    final_segment = final_calc_resp.json()['segments'][0]

    final_retrieve_resp, _ = await v1_calc_price__driver_final(
        waybill, performer,
    )
    assert final_retrieve_resp.status_code == 200
    final_retrieve_segment = final_retrieve_resp.json()['segments'][0]

    client_calc = final_segment['calc_for_client']
    driver_calc = final_segment['calc_for_performer']
    retrieved_client_calc = final_retrieve_segment['calc_for_client']
    retrieved_driver_calc = final_retrieve_segment['calc_for_performer']
    assert utils.extract_calc_id(client_calc) == utils.extract_calc_id(
        retrieved_client_calc,
    )
    assert utils.extract_calc_id(driver_calc) == utils.extract_calc_id(
        retrieved_driver_calc,
    )


async def test_yandex_go_claim_ignore_race_events_on_second_call(
        make_yandex_go_offer,
        v1_calc_price__driver_offer,
        v1_calc_price__driver_final,
        processing_state,
):

    segment = models.make_segment(payment_info=models.PaymentMethod.CARD)
    await make_yandex_go_offer(segment)

    waybill = models.make_waybill(resolution=models.Resolution.COMPLETED)
    waybill.add_segment(segment)

    performer = models.Performer.FIRST
    await v1_calc_price__driver_offer(waybill, performer)

    final_calc_resp, new_events = await v1_calc_price__driver_final(
        waybill, performer,
    )
    assert final_calc_resp.status_code == 200
    final_segment = final_calc_resp.json()['segments'][0]

    race_events = copy.deepcopy(new_events)
    for i, _ in enumerate(race_events):
        race_events[i]['payload']['calc_id'] = 'cargo-pricing/v1/' + 'b' * 32
    processing_state.events_by_item_id[segment.id].extend(race_events)

    final_retrieve_resp, _ = await v1_calc_price__driver_final(
        waybill, performer,
    )
    assert final_retrieve_resp.status_code == 200
    final_retrieve_segment = final_retrieve_resp.json()['segments'][0]

    client_calc = final_segment['calc_for_client']
    driver_calc = final_segment['calc_for_performer']
    retrieved_client_calc = final_retrieve_segment['calc_for_client']
    retrieved_driver_calc = final_retrieve_segment['calc_for_performer']
    assert utils.extract_calc_id(client_calc) == utils.extract_calc_id(
        retrieved_client_calc,
    )
    assert utils.extract_calc_id(driver_calc) == utils.extract_calc_id(
        retrieved_driver_calc,
    )
