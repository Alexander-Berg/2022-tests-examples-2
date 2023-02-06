import pytest


@pytest.mark.parametrize('is_price_hidden', [True, False])
async def test_dragon_order_with_pricing(
        taxi_cargo_orders,
        default_order_id,
        my_batch_waybill_info,
        mock_cargo_pricing_calc_retrieve,
        set_order_calculations_ids,
        experiments3,
        is_price_hidden,
        call_v1_setcar_data,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_pricing_settings',
        consumers=['cargo-orders/pricing-settings'],
        clauses=[],
        default_value={'is_price_hidden': is_price_hidden},
    )
    await taxi_cargo_orders.invalidate_caches()
    set_order_calculations_ids('preset_id')
    response = await call_v1_setcar_data(
        request={
            'cargo_ref_id': f'order/{default_order_id}',
            'tariff_class': f'courier',
        },
    )
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['pricing'] == {
        'price': {'total': '827', 'surge': '48'},
        'taxi_pricing_response_parts': {
            'taximeter_meta': {
                'max_distance_from_b': 532.0,
                'show_price_in_taximeter': False,
            },
        },
        'currency': {'code': 'RUB'},
        'is_price_hidden': is_price_hidden,
    }
    assert resp_body['corp_client_ids'] == ['5e36732e2bc54e088b1466e08e31c486']
    assert resp_body['tariff_class'] == 'courier'


@pytest.fixture(name='mock_failed_cargo_pricing_calc')
def _mock_failed_cargo_pricing_calc(mockserver):
    @mockserver.json_handler('/cargo-pricing/v1/taxi/calc')
    def _cargo_pricing_calc():
        response_json = {'code': '500', 'message': 'Internal Server Error'}
        return mockserver.make_response(status=500, json=response_json)


@pytest.mark.config(CARGO_ORDERS_PRICING_SETCAR_DATA_IS_REQUIRED=False)
@pytest.mark.config(CARGO_ORDERS_CALC_OFFER_PRICE_ON_SETCAR_REQUEST=True)
async def test_dragon_order_with_failed_pricing(
        call_v1_setcar_data,
        my_batch_waybill_info,
        mock_failed_cargo_pricing_calc,
        mock_driver_tags_v1_match_profile,
):
    response = await call_v1_setcar_data()
    assert response.status_code == 200
    assert 'pricing' not in response.json()


@pytest.mark.config(CARGO_ORDERS_PRICING_SETCAR_DATA_IS_REQUIRED=True)
@pytest.mark.config(CARGO_ORDERS_CALC_OFFER_PRICE_ON_SETCAR_REQUEST=True)
async def test_dragon_order_with_failed_required_pricing(
        call_v1_setcar_data,
        my_batch_waybill_info,
        mock_failed_cargo_pricing_calc,
        mock_driver_tags_v1_match_profile,
):
    response = await call_v1_setcar_data()
    assert response.status_code == 500


@pytest.mark.config(CARGO_ORDERS_CALC_OFFER_PRICE_ON_SETCAR_REQUEST=True)
async def test_dragon_order_calc_offer_price(
        call_v1_setcar_data,
        my_batch_waybill_info,
        mock_cargo_pricing_calc,
        mock_driver_tags_v1_match_profile,
):
    response = await call_v1_setcar_data()
    assert response.status_code == 200
    assert response.json()['pricing'] == {
        'price': {'total': '933'},
        'taxi_pricing_response_parts': {
            'taximeter_meta': {
                'max_distance_from_b': 567.0,
                'show_price_in_taximeter': True,
            },
        },
    }


@pytest.mark.config(CARGO_ORDERS_CALC_OFFER_PRICE_ON_SETCAR_REQUEST=True)
async def test_dragon_order_calc_offer_price_pricing_request(
        call_v1_setcar_data,
        my_batch_waybill_info,
        mock_cargo_pricing_calc,
        mock_driver_tags_v1_match_profile,
):
    response = await call_v1_setcar_data()
    assert response.status_code == 200

    assert mock_cargo_pricing_calc.mock.times_called == 1
    pricing_request = mock_cargo_pricing_calc.request
    assert pricing_request['performer'] == {
        'driver_id': 'driver_id1',
        'park_db_id': 'park_id1',
    }
    assert pricing_request['price_for'] == 'performer'
    assert pricing_request['transport'] == 'pedestrian'
    assert pricing_request['tariff_class'] == 'courier'
    assert not pricing_request['is_usage_confirmed']
    assert pricing_request['external_ref'] == 'meta_order_id/taxi-order'
    assert pricing_request['origin_uri'] == 'cargo-orders/v1/setcar-data'
    assert (
        pricing_request['idempotency_token']
        == 'presetcar-order-taxi-order-performer-driver_id1'
    )


@pytest.mark.config(CARGO_ORDERS_CALC_OFFER_PRICE_ON_SETCAR_REQUEST=True)
async def test_dragon_order_calc_offer_price_already_exists(
        call_v1_setcar_data,
        my_batch_waybill_info,
        mock_cargo_pricing_calc,
        mock_cargo_pricing_calc_retrieve,
        mock_driver_tags_v1_match_profile,
):
    response = await call_v1_setcar_data()
    assert response.status_code == 200
    assert mock_cargo_pricing_calc.mock.times_called == 1
    assert mock_cargo_pricing_calc_retrieve.mock.times_called == 0

    response = await call_v1_setcar_data()
    assert response.status_code == 200
    assert mock_cargo_pricing_calc.mock.times_called == 1
    assert mock_cargo_pricing_calc_retrieve.mock.times_called == 1
