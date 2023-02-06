import pytest


@pytest.fixture(name='mock_rebill_new_price')
def _mock_rebill_new_price(mockserver, mock_with_context):
    return mock_with_context(
        decorator=mockserver.json_handler(
            '/py2-delivery/rebill-new-price-set-by-operator',
        ),
        response_data={},
    )


@pytest.fixture(name='mock_pay_order_state')
def _mock_pay_order_state(mockserver, mock_with_context):
    return mock_with_context(
        decorator=mockserver.json_handler(
            '/cargo-finance/admin/cargo-finance/pay/order/state',
        ),
        response_data={
            'actions': {'change_order_sum': {'token': 'some.jwt.token'}},
            'changes_history': [],
        },
    )


@pytest.fixture(name='mock_pay_order_change_order_sum')
def _mock_pay_order_change_order_sum(mockserver, mock_with_context):
    return mock_with_context(
        decorator=mockserver.json_handler(
            '/cargo-finance/admin/cargo-finance/pay/order/change-order-sum',
        ),
        response_data={},
    )


@pytest.fixture(name='mock_v2_claims_manual_correction')
def _mock_v2_claims_manual_correction(mockserver, mock_with_context):
    return mock_with_context(
        decorator=mockserver.json_handler(
            '/cargo-claims/v2/claims/manual-price-correction',
        ),
        response_data={
            'correction_id': 'correction_id',
            'taxi_order_id': 'order_id',
        },
    )


async def test_old_c2c_nullify(
        taxi_cargo_orders,
        my_waybill_info,
        default_order_id,
        mock_rebill_new_price,
):
    for segment in my_waybill_info['execution']['segments']:
        segment['claim_features'] = [{'id': 'agent_scheme'}]

    response = await taxi_cargo_orders.post(
        '/v1/antifraud/nullify-order',
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    assert mock_rebill_new_price.request.json == {
        'driver_correction': {
            'otrs_ticket': 'CARGODEV-11973',
            'reason_code': 'OTHER',
            'sum': 0.0,
            'ticket_type': 'startrack',
        },
        'operator_login': 'toert',
        'user_correction': {
            'otrs_ticket': 'CARGODEV-11973',
            'reason_code': 'OTHER',
            'sum': 0.0,
            'ticket_type': 'startrack',
        },
    }


async def test_decoupling_strategy(
        taxi_cargo_orders,
        my_waybill_info,
        default_order_id,
        mock_v2_claims_manual_correction,
        mockserver,
        load_json,
        mock_rebill_new_price,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _mock_claims_full(request):
        return load_json('cargo-claims/default.json')

    response = await taxi_cargo_orders.post(
        '/v1/antifraud/nullify-order',
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    assert mock_v2_claims_manual_correction.request.json == {
        'claim_id': 'seg_1',
        'currency': 'RUB',
        'last_known_corrections_count': 0,
        'reason': 'CARGODEV-11973',
        'source': 'toert',
        'sum_to_pay': '0',
    }
    assert mock_rebill_new_price.request.json == {
        'driver_correction': {
            'otrs_ticket': 'CARGODEV-11973',
            'reason_code': 'OTHER',
            'sum': 0.0,
            'ticket_type': 'startrack',
        },
        'operator_login': 'toert',
    }


async def test_phoenix_strategy(
        taxi_cargo_orders,
        my_waybill_info,
        default_order_id,
        mock_pay_order_state,
        mock_pay_order_change_order_sum,
):

    for segment in my_waybill_info['execution']['segments']:
        segment['claim_features'] = [{'id': 'phoenix_claim'}]

    response = await taxi_cargo_orders.post(
        '/v1/antifraud/nullify-order',
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200
    assert mock_pay_order_change_order_sum.request.json == {
        'new_sum': '0',
        'operation_token': 'some.jwt.token',
        'reason': {'st_ticket': 'CARGODEV-11973'},
    }
