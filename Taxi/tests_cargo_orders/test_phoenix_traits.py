import pytest


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            id='claims_way',
            marks=pytest.mark.config(
                CARGO_ORDERS_GET_PHOENIX_TRAITS_WITH_YT=True,
            ),
        ),
        pytest.param(
            id='waybill_way',
            marks=pytest.mark.config(
                CARGO_ORDERS_GET_PHOENIX_TRAITS_WITH_YT=False,
            ),
        ),
    ],
)
async def test_not_phoenix_claims(
        taxi_cargo_orders, default_order_id, mock_admin_claims_phoenix_traits,
):
    response = await taxi_cargo_orders.post(
        '/v1/phoenix/traits',
        json={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'cargo_ref_id': f'order/{default_order_id}',
        'is_phoenix_flow': False,
        'is_cargo_finance_billing_event': False,
        'is_cargo_finance_using_cargo_pipelines': False,
        'is_cargo_finance_dry_run_for_cargo_pipelines': False,
        'is_agent_scheme': False,
        'is_phoenix_corp': False,
    }


@pytest.mark.parametrize(
    'claims_way',
    [
        pytest.param(
            True,
            id='claims_way',
            marks=pytest.mark.config(
                CARGO_ORDERS_GET_PHOENIX_TRAITS_WITH_YT=True,
            ),
        ),
        pytest.param(
            False,
            id='waybill_way',
            marks=pytest.mark.config(
                CARGO_ORDERS_GET_PHOENIX_TRAITS_WITH_YT=False,
            ),
        ),
    ],
)
async def test_phoenix_claims(
        taxi_cargo_orders,
        default_order_id,
        my_waybill_info,
        mock_admin_claims_phoenix_traits,
        claims_way,
):
    order_id = default_order_id
    claim_uuid = my_waybill_info['execution']['segments'][0]['claim_id']
    if claims_way:
        order_id = '9db1622e-582d-4091-b6fc-4cb2ffdc12c1'
        claim_uuid = 'some_id'
    else:
        my_waybill_info['execution']['segments'][0]['claim_features'] = [
            {'id': 'etc'},
            {'id': 'phoenix_claim'},
            {'id': 'agent_scheme'},
            {'id': 'phoenix_corp'},
        ]
    response = await taxi_cargo_orders.post(
        '/v1/phoenix/traits', json={'cargo_ref_id': f'order/{order_id}'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'cargo_ref_id': f'order/{order_id}',
        'claim_id': claim_uuid,
        'is_phoenix_flow': True,
        'is_agent_scheme': True,
        'is_phoenix_corp': True,
        'is_cargo_finance_billing_event': False,
        'is_cargo_finance_using_cargo_pipelines': False,
        'is_cargo_finance_dry_run_for_cargo_pipelines': False,
    }


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            id='claims_way',
            marks=pytest.mark.config(
                CARGO_ORDERS_GET_PHOENIX_TRAITS_WITH_YT=True,
            ),
        ),
        pytest.param(
            id='waybill_way',
            marks=pytest.mark.config(
                CARGO_ORDERS_GET_PHOENIX_TRAITS_WITH_YT=False,
            ),
        ),
    ],
)
async def test_not_found(taxi_cargo_orders, default_order_id, mockserver):
    @mockserver.json_handler('/cargo-claims/v2/admin/phoenix/bulk-traits')
    def _mock_phoenix_traits(request):
        return mockserver.make_response(status=200, json={'orders': []})

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _mock(request):
        return mockserver.make_response(
            status=404, json={'message': 'something', 'code': 'bad'},
        )

    response = await taxi_cargo_orders.post(
        '/v1/phoenix/traits',
        json={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'cargo_ref_id': f'order/{default_order_id}',
        'is_phoenix_flow': False,
        'is_cargo_finance_billing_event': False,
        'is_cargo_finance_using_cargo_pipelines': False,
        'is_cargo_finance_dry_run_for_cargo_pipelines': False,
        'is_agent_scheme': False,
        'is_phoenix_corp': False,
    }


@pytest.mark.parametrize(
    'claims_way',
    [
        pytest.param(
            True,
            id='claims_way',
            marks=pytest.mark.config(
                CARGO_ORDERS_GET_PHOENIX_TRAITS_WITH_YT=True,
            ),
        ),
        pytest.param(
            False,
            id='waybill_way',
            marks=pytest.mark.config(
                CARGO_ORDERS_GET_PHOENIX_TRAITS_WITH_YT=False,
            ),
        ),
    ],
)
async def test_cache_hit(
        taxi_cargo_orders,
        default_order_id,
        mockserver,
        my_waybill_info,
        mock_admin_claims_phoenix_traits,
        claims_way,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def mock_waybill_info(request):
        return mockserver.make_response(status=200, json=my_waybill_info)

    response = await taxi_cargo_orders.post(
        '/v1/phoenix/traits',
        json={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200
    if claims_way:
        assert mock_admin_claims_phoenix_traits.handler.times_called == 1
    else:
        assert mock_waybill_info.times_called == 1

    # Fetch the same order. Use cache
    response = await taxi_cargo_orders.post(
        '/v1/phoenix/traits',
        json={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200
    if claims_way:
        assert mock_admin_claims_phoenix_traits.handler.times_called == 1
    else:
        assert mock_waybill_info.times_called == 1

    # Fetch new order
    response = await taxi_cargo_orders.post(
        '/v1/phoenix/traits',
        json={'cargo_ref_id': 'order/00000000-0000-0000-0000-000000000000'},
    )
    assert response.status_code == 200
    if claims_way:
        assert mock_admin_claims_phoenix_traits.handler.times_called == 2
    else:
        assert mock_waybill_info.times_called == 2


@pytest.mark.config(CARGO_ORDERS_GET_PHOENIX_TRAITS_WITH_YT=True)
async def test_old_format_cargo_ref_id(
        taxi_cargo_orders, mock_claims_phoenix_traits,
):
    claim_uuid = 'cc0431b859b94324bb388d55a129a78e'
    response = await taxi_cargo_orders.post(
        '/v1/phoenix/traits', json={'cargo_ref_id': claim_uuid},
    )
    assert response.status_code == 200
    assert response.json() == {
        'cargo_ref_id': claim_uuid,
        'is_phoenix_flow': False,
        'is_cargo_finance_billing_event': False,
        'is_cargo_finance_using_cargo_pipelines': False,
        'is_cargo_finance_dry_run_for_cargo_pipelines': False,
        'is_agent_scheme': False,
        'is_phoenix_corp': False,
    }


async def test_invalid_cargo_ref_id(taxi_cargo_orders):
    response = await taxi_cargo_orders.post(
        '/v1/phoenix/traits',
        json={'cargo_ref_id': 'i0000000000000000000000000000000'},
    )
    assert response.status_code == 500


async def test_bulk_traits(taxi_cargo_orders, default_order_id, mockserver):
    test_order_id = '00000000-0000-0000-0000-000000000000'
    nonexistent_order_id = '00000000-0000-0000-0000-000000000001'

    @mockserver.json_handler('/cargo-claims/v2/admin/phoenix/bulk-traits')
    def mock_phoenix_traits(request):
        return mockserver.make_response(
            status=200,
            json={
                'orders': [
                    {
                        'cargo_order_id': default_order_id,
                        'claim_id': 'some_id',
                        'is_phoenix_flow': False,
                        'is_cargo_finance_billing_event': False,
                        'is_cargo_finance_using_cargo_pipelines': False,
                        'is_cargo_finance_dry_run_for_cargo_pipelines': False,
                        'is_agent_scheme': False,
                        'is_phoenix_corp': False,
                    },
                    {
                        'cargo_order_id': test_order_id,
                        'claim_id': 'some_id2',
                        'is_phoenix_flow': True,
                        'is_cargo_finance_billing_event': False,
                        'is_cargo_finance_using_cargo_pipelines': False,
                        'is_cargo_finance_dry_run_for_cargo_pipelines': False,
                        'is_agent_scheme': True,
                        'is_phoenix_corp': True,
                    },
                ],
            },
        )

    response = await taxi_cargo_orders.post(
        '/v1/phoenix/bulk-traits',
        json={
            'cargo_ref_ids': [
                f'order/{default_order_id}',
                f'order/{test_order_id}',
                f'order/{nonexistent_order_id}',
            ],
        },
    )
    expected_response = {
        'orders': [
            {
                'cargo_ref_id': f'order/{default_order_id}',
                'is_phoenix_flow': False,
                'is_cargo_finance_billing_event': False,
                'is_cargo_finance_using_cargo_pipelines': False,
                'is_cargo_finance_dry_run_for_cargo_pipelines': False,
                'is_agent_scheme': False,
                'is_phoenix_corp': False,
            },
            {
                'cargo_ref_id': f'order/{test_order_id}',
                'claim_id': 'some_id2',
                'is_phoenix_flow': True,
                'is_cargo_finance_billing_event': False,
                'is_cargo_finance_using_cargo_pipelines': False,
                'is_cargo_finance_dry_run_for_cargo_pipelines': False,
                'is_agent_scheme': True,
                'is_phoenix_corp': True,
            },
            {
                'cargo_ref_id': f'order/{nonexistent_order_id}',
                'is_phoenix_flow': False,
                'is_cargo_finance_billing_event': False,
                'is_cargo_finance_using_cargo_pipelines': False,
                'is_cargo_finance_dry_run_for_cargo_pipelines': False,
                'is_agent_scheme': False,
                'is_phoenix_corp': False,
            },
        ],
    }
    assert response.status_code == 200
    assert (
        sorted(
            response.json()['orders'], key=lambda order: order['cargo_ref_id'],
        )
        == sorted(
            expected_response['orders'],
            key=lambda order: order['cargo_ref_id'],
        )
    )
    assert mock_phoenix_traits.times_called == 1


async def test_bulk_traits_use_cache(
        taxi_cargo_orders, default_order_id, mockserver, my_waybill_info,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def mock_waybill_info(request):
        return mockserver.make_response(status=200, json=my_waybill_info)

    @mockserver.json_handler('/cargo-claims/v2/admin/phoenix/bulk-traits')
    def mock_phoenix_traits(request):
        return mockserver.make_response(
            status=200,
            json={
                'orders': [
                    {
                        'cargo_order_id': default_order_id,
                        'claim_id': 'some_id',
                        'is_phoenix_flow': False,
                        'is_cargo_finance_billing_event': False,
                        'is_cargo_finance_using_cargo_pipelines': False,
                        'is_cargo_finance_dry_run_for_cargo_pipelines': False,
                        'is_agent_scheme': False,
                        'is_phoenix_corp': False,
                    },
                ],
            },
        )

    response = await taxi_cargo_orders.post(
        '/v1/phoenix/traits',
        json={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200
    assert mock_waybill_info.times_called == 1

    response = await taxi_cargo_orders.post(
        '/v1/phoenix/bulk-traits',
        json={'cargo_ref_ids': [f'order/{default_order_id}']},
    )
    assert response.status_code == 200
    assert response.json() == {
        'orders': [
            {
                'cargo_ref_id': f'order/{default_order_id}',
                'is_phoenix_flow': False,
                'is_cargo_finance_billing_event': False,
                'is_cargo_finance_using_cargo_pipelines': False,
                'is_cargo_finance_dry_run_for_cargo_pipelines': False,
                'is_agent_scheme': False,
                'is_phoenix_corp': False,
            },
        ],
    }
    assert mock_phoenix_traits.times_called == 0


@pytest.mark.config(CARGO_ORDERS_GET_PHOENIX_TRAITS_WITH_YT=True)
async def test_bulk_traits_fill_cache(
        taxi_cargo_orders,
        default_order_id,
        mockserver,
        mock_admin_claims_phoenix_traits,
):
    response = await taxi_cargo_orders.post(
        '/v1/phoenix/bulk-traits',
        json={'cargo_ref_ids': [f'order/{default_order_id}']},
    )
    assert response.status_code == 200
    assert mock_admin_claims_phoenix_traits.handler.times_called == 1

    response = await taxi_cargo_orders.post(
        '/v1/phoenix/traits',
        json={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200
    assert mock_admin_claims_phoenix_traits.handler.times_called == 1


@pytest.mark.config(CARGO_ORDERS_GET_PHOENIX_TRAITS_WITH_YT=True)
async def test_old_format_bulk_cargo_ref_id(
        taxi_cargo_orders, mock_claims_phoenix_traits,
):
    claim_uuid = 'cc0431b859b94324bb388d55a129a78e'
    response = await taxi_cargo_orders.post(
        '/v1/phoenix/bulk-traits', json={'cargo_ref_ids': [claim_uuid]},
    )
    assert response.status_code == 200
    assert response.json() == {
        'orders': [
            {
                'cargo_ref_id': claim_uuid,
                'is_phoenix_flow': False,
                'is_cargo_finance_billing_event': False,
                'is_cargo_finance_using_cargo_pipelines': False,
                'is_cargo_finance_dry_run_for_cargo_pipelines': False,
                'is_agent_scheme': False,
                'is_phoenix_corp': False,
            },
        ],
    }


async def test_invalid_bulk_cargo_ref_id(taxi_cargo_orders):
    response = await taxi_cargo_orders.post(
        '/v1/phoenix/bulk-traits', json={'cargo_ref_ids': ['1234abcd']},
    )
    assert response.status_code == 500


async def test_provider_order_id(
        taxi_cargo_orders, my_waybill_info, mock_admin_claims_phoenix_traits,
):
    claim_uuid = my_waybill_info['execution']['segments'][0]['claim_id']
    my_waybill_info['execution']['segments'][0]['claim_features'] = [
        {'id': 'etc'},
        {'id': 'phoenix_claim'},
        {'id': 'agent_scheme'},
        {'id': 'phoenix_corp'},
    ]
    response = await taxi_cargo_orders.post(
        '/v1/phoenix/traits', json={'provider_order_id': 'taxi-order'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'claim_id': claim_uuid,
        'is_phoenix_flow': True,
        'is_cargo_finance_billing_event': False,
        'is_cargo_finance_using_cargo_pipelines': False,
        'is_cargo_finance_dry_run_for_cargo_pipelines': False,
        'is_agent_scheme': True,
        'is_phoenix_corp': True,
    }


async def test_invalid_provider_order_id(
        taxi_cargo_orders, mock_admin_claims_phoenix_traits,
):
    response = await taxi_cargo_orders.post(
        '/v1/phoenix/traits', json={'provider_order_id': 'foo123456'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'is_phoenix_flow': False,
        'is_cargo_finance_billing_event': False,
        'is_cargo_finance_using_cargo_pipelines': False,
        'is_cargo_finance_dry_run_for_cargo_pipelines': False,
        'is_agent_scheme': False,
        'is_phoenix_corp': False,
    }


async def test_invalid_request(taxi_cargo_orders):
    response = await taxi_cargo_orders.post('/v1/phoenix/traits', json={})
    assert response.status_code == 400
    assert response.json() == {
        'code': 'bad_request',
        'message': 'provider_order_id or cargo_ref_id was not found',
    }
