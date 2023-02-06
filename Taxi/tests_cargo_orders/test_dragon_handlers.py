import pytest

from testsuite.utils import matching


@pytest.fixture(name='my_c2c_batch_waybill_info_with_segments')
def _my_c2c_batch_waybill_info_with_segments(waybill_state, mock_waybill_info):
    response = waybill_state.load_waybill(
        'cargo-dispatch/v1_waybill_info_batch_tpl_filled_segments.json',
    )
    for segment in response['execution']['segments']:
        segment['claim_features'] = [{'id': 'use_pricing_dragon_handlers'}]
        del segment['corp_client_id']
        segment['client_info']['payment_info']['type'] = 'card'
        segment['client_info']['payment_info']['method_id'].replace(
            'corp', 'card',
        )
    return response


async def test_calc_price_pricing_dragon_handlers(
        calc_price,
        calc_price_via_taximeter,
        mock_cargo_estimate_waybill,
        mock_cargo_resolve_waybill,
        mock_cargo_retrieve_waybill_pricing,
        my_c2c_batch_waybill_info_with_segments,
        resolve_waybill,
        mock_driver_tags_v1_match_profile,
        set_order_calculations_ids,
):
    set_order_calculations_ids(client_offer_calc_id='calc_id_client_offer')

    offer_calc_resp = await calc_price()
    assert offer_calc_resp.status_code == 200
    assert mock_cargo_estimate_waybill.mock.times_called == 1
    assert offer_calc_resp.json()['is_cargo_pricing']
    assert int(offer_calc_resp.json()['receipt']['total']) == int(
        mock_cargo_estimate_waybill.response['aggregation']['price'],
    )

    offer_retrieve_resp = await calc_price()
    assert offer_retrieve_resp.status_code == 200
    assert mock_cargo_retrieve_waybill_pricing.mock.times_called == 1
    assert offer_calc_resp.json() == offer_retrieve_resp.json()

    resolve_waybill(my_c2c_batch_waybill_info_with_segments)
    calc_stage = 'order_finished'
    final_calc_resp = await calc_price_via_taximeter(
        stage=calc_stage, status='complete',
    )
    assert final_calc_resp.status_code == 200
    assert mock_cargo_resolve_waybill.mock.times_called == 1
    assert int(final_calc_resp.json()['price']) == int(
        mock_cargo_resolve_waybill.response['aggregation']['price'],
    )

    final_retrieve_resp = await calc_price(source_type='requestconfirm')
    assert mock_cargo_retrieve_waybill_pricing.mock.times_called == 2
    assert int(final_calc_resp.json()['price']) == int(
        final_retrieve_resp.json()['receipt']['total'],
    )


async def test_calc_cash_pricing_dragon_handler(
        calc_cash_via_taximeter,
        mock_cargo_resolve_segment,
        waybill_info_c2c,
        set_order_calculations_ids,
):
    set_order_calculations_ids(client_offer_calc_id='calc_id_client_offer')
    segment = waybill_info_c2c['execution']['segments'][0]
    segment['claim_features'] = [{'id': 'use_pricing_dragon_handlers'}]

    response = await calc_cash_via_taximeter()
    assert response.status_code == 200
    assert mock_cargo_resolve_segment.mock.times_called == 1

    assert mock_cargo_resolve_segment.request['segment'] == {
        'id': segment['id'],
        'taxi_order_id': 'taxi-order',
        'payment_info': segment['client_info']['payment_info'],
        'resolution': {
            'resolution': 'completed',
            'resolved_at': matching.AnyString(),
        },
    }
    assert mock_cargo_resolve_segment.request['v1_request'][
        'is_usage_confirmed'
    ]

    client_calc = mock_cargo_resolve_segment.response['calc_for_client']
    assert response.json() == {
        'price': client_calc['prices']['total_price'],
        'currency_code': client_calc['details']['currency']['code'],
    }
