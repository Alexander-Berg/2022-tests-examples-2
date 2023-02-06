import pytest

from tests_cargo_pricing.taxi_dragon_resolvers import models
from tests_cargo_pricing.taxi_dragon_resolvers import utils


@pytest.fixture(name='create_batch')
def _create_batch(make_yandex_go_offer):
    class Impl:
        segment_resolutions = [
            models.Resolution.COMPLETED,
            models.Resolution.COMPLETED,
        ]

        async def execute(self):
            waybill = models.make_waybill(
                resolution=models.Resolution.COMPLETED,
            )
            for resolution in self.segment_resolutions:
                segment = models.make_segment(
                    payment_info=models.PaymentMethod.CARD,
                    resolution=resolution,
                )
                await make_yandex_go_offer(segment)
                waybill.add_segment(segment)
            return waybill

    return Impl()


async def test_batch_happy_path(
        v1_calc_price__driver_offer,
        v1_calc_price__driver_final,
        create_batch,
        cargo_claims_change_claim_order_price,
):
    create_batch.segment_resolutions = [
        models.Resolution.CANCELLED_BY_CLIENT,
        models.Resolution.COMPLETED,
    ]
    waybill = await create_batch.execute()

    performer = models.Performer.FIRST

    await v1_calc_price__driver_offer(waybill, performer)
    final_driver_resp, _ = await v1_calc_price__driver_final(
        waybill, performer,
    )

    client_resp_1, _ = await cargo_claims_change_claim_order_price(
        waybill.segments[0], performer,
    )
    client_resp_2, _ = await cargo_claims_change_claim_order_price(
        waybill.segments[1], performer,
    )

    driver_segments = final_driver_resp.json()['segments']
    client_segment_1 = client_resp_1.json()
    client_segment_2 = client_resp_2.json()

    driver_result = {
        driver_segments[0]['id']: utils.extract_calc_id(
            driver_segments[0]['calc_for_client'],
        ),
        driver_segments[1]['id']: utils.extract_calc_id(
            driver_segments[1]['calc_for_client'],
        ),
    }

    clients_result = {
        waybill.segments[0].id: utils.extract_calc_id(
            client_segment_1['calc_for_client'],
        ),
        waybill.segments[1].id: utils.extract_calc_id(
            client_segment_2['calc_for_client'],
        ),
    }

    assert driver_result == clients_result
    for idx, segment in enumerate(driver_segments):
        calc_request = segment['calc_for_performer']['diagnostics'][
            'calc_request'
        ]
        assert (
            calc_request['resolution_info']
            == create_batch.segment_resolutions[idx]
        )


async def test_batch_aggregation(
        create_batch, v1_calc_price__driver_offer, v1_calc_price__driver_final,
):
    waybill = await create_batch.execute()

    performer = models.Performer.FIRST

    offer_resp, offer_new_events = await v1_calc_price__driver_offer(
        waybill, performer,
    )
    final_resp, final_new_events = await v1_calc_price__driver_final(
        waybill, performer,
    )
    for (resp, new_events) in [
            (offer_resp, offer_new_events),
            (final_resp, final_new_events),
    ]:
        aggregation = resp.json()['aggregation']
        assert aggregation['id'].startswith(
            f'cargo-pricing/aggregation/v1/{waybill.taxi_order_id}/',
        )
        sum_of_segments = 0
        segment_calc_ids = []
        for segment in resp.json()['segments']:
            sum_of_segments += float(
                segment['calc_for_performer']['prices']['total_price'],
            )
            segment_calc_ids.append(
                utils.extract_calc_id(segment['calc_for_performer']),
            )
        assert round(float(aggregation['price']), 4) == round(
            sum_of_segments, 4,
        )
        assert new_events[-1]['payload'] == {
            'kind': 'aggregation',
            'calc_id': aggregation['id'],
            'price': aggregation['price'],
            'segment_calc_ids': segment_calc_ids,
        }


async def test_batch_retrieve(
        create_batch,
        v1_calc_price__driver_offer,
        v1_calc_price__driver_final,
        v2_retrieve_waybill_pricing,
):
    waybill = await create_batch.execute()

    performer = models.Performer.FIRST

    await v1_calc_price__driver_offer(waybill, performer)
    calc_resp, _ = await v1_calc_price__driver_final(waybill, performer)
    assert calc_resp.status_code == 200

    retrieve_resp = await v2_retrieve_waybill_pricing(
        {'aggregation_calc_id': calc_resp.json()['aggregation']['id']},
    )
    assert retrieve_resp.status_code == 200

    segment_to_calc_id = {}
    for segment in calc_resp.json()['segments']:
        segment_to_calc_id[segment['id']] = utils.extract_calc_id(
            segment['calc_for_performer'],
        )

    retrieved_segment_to_calc_id = {}
    for segment in retrieve_resp.json()['segments']:
        retrieved_segment_to_calc_id[segment['id']] = utils.extract_calc_id(
            segment['calc_for_performer'],
        )

    assert segment_to_calc_id == retrieved_segment_to_calc_id


async def test_batch_confirm_usage(
        create_batch,
        v1_calc_price__driver_offer,
        v1_calc_price__driver_final,
        v2_retrieve_waybill_pricing,
        confirm_usage,
        processing_state,
        pgsql,
):
    waybill = await create_batch.execute()

    performer = models.Performer.FIRST

    await v1_calc_price__driver_offer(waybill, performer)
    calc_resp, _ = await v1_calc_price__driver_final(waybill, performer)
    assert calc_resp.status_code == 200

    aggregation_calc_id = calc_resp.json()['aggregation']['id']
    external_ref = f'taxi_order_id/{waybill.taxi_order_id}'
    await confirm_usage(aggregation_calc_id, external_ref)

    processing_events = processing_state.get_events(
        f'order/{waybill.taxi_order_id}',
    )
    assert processing_events[-1]['payload'] == {
        'calc_id': aggregation_calc_id,
        'kind': 'confirm-usage',
    }

    retrieve_resp = await v2_retrieve_waybill_pricing(
        {'aggregation_calc_id': aggregation_calc_id},
    )
    assert retrieve_resp.status_code == 200

    driver_calc_uuids = []
    for segment in calc_resp.json()['segments']:
        calc_id = utils.extract_calc_id(segment['calc_for_performer'])
        driver_calc_uuids.append(calc_id.replace('cargo-pricing/v1/', ''))

    cursor = pgsql['cargo_pricing'].conn.cursor()
    cursor.execute(
        f"""
        SELECT details_external_ref, is_confirmed
        FROM cargo_pricing.calculations WHERE id
        IN ({','.join(f"'{calc_id}'" for calc_id in driver_calc_uuids)})
        """,
    )
    for details_external_ref, is_confirmed in list(cursor):
        assert is_confirmed
        assert external_ref == details_external_ref
