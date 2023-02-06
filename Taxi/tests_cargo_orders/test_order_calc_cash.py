async def test_happy_path(
        calc_price_via_taximeter,
        calc_cash_via_taximeter,
        mock_cargo_pricing_calc,
        mock_cargo_pricing_calc_retrieve,
        my_waybill_info,
        set_order_calculations_ids,
        set_point_visited,
        resolve_waybill,
        mock_driver_tags_v1_match_profile,
):
    my_waybill_info['execution']['segments'][0]['client_info']['payment_info'][
        'type'
    ] = 'cash'
    set_order_calculations_ids(client_offer_calc_id='calc_id_client_offer')
    mock_cargo_pricing_calc.substituted_client_price = '888'
    response = await calc_cash_via_taximeter()
    assert response.json() == {'currency_code': 'RUB', 'price': '888'}

    assert mock_cargo_pricing_calc.mock.times_called == 2
    assert mock_cargo_pricing_calc.request['entity_id'] == 'order/taxi-order'
    assert (
        mock_cargo_pricing_calc.request['origin_uri']
        == 'cargo-orders/driver/v1/cargo-claims/v1/cargo/calc-cash'
    )
    assert mock_cargo_pricing_calc.request['calc_kind'] == 'final'
    assert mock_cargo_pricing_calc_retrieve.mock.times_called == 0

    resolve_waybill(my_waybill_info)
    await calc_price_via_taximeter(stage='order_finished', status='complete')

    assert mock_cargo_pricing_calc.mock.times_called == 2
    assert mock_cargo_pricing_calc_retrieve.mock.times_called == 2


async def test_cash_price_on_return_point(
        calc_price_via_taximeter,
        calc_cash_via_taximeter,
        mock_cargo_pricing_calc,
        mock_cargo_pricing_calc_retrieve,
        set_order_calculations_ids,
        set_point_visited,
        mock_waybill_info,
        my_waybill_info,
        resolve_waybill,
        mock_driver_tags_v1_match_profile,
):
    waybill_exec = my_waybill_info['execution']
    waybill_exec['segments'][0]['client_info']['payment_info']['type'] = 'cash'
    waybill_exec['points'][0]['resolution']['is_visited'] = True
    waybill_exec['points'][0]['is_resolved'] = True

    set_order_calculations_ids(client_offer_calc_id='calc_id_client_offer')
    mock_cargo_pricing_calc.substituted_client_price = '888'
    response = await calc_cash_via_taximeter()
    assert response.json() == {'currency_code': 'RUB', 'price': '888'}
    assert mock_cargo_pricing_calc.mock.times_called == 2
    assert mock_cargo_pricing_calc_retrieve.mock.times_called == 0

    waybill_exec['points'][1]['resolution']['is_visited'] = True
    waybill_exec['points'][1]['is_resolved'] = True
    resolve_waybill(my_waybill_info)
    response = await calc_cash_via_taximeter()
    assert mock_cargo_pricing_calc.mock.times_called == 4
    assert mock_cargo_pricing_calc_retrieve.mock.times_called == 0

    await calc_price_via_taximeter(stage='order_finished', status='complete')
    assert mock_cargo_pricing_calc.mock.times_called == 4
    assert mock_cargo_pricing_calc_retrieve.mock.times_called == 2
