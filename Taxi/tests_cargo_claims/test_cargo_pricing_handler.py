import pytest

from testsuite.utils import matching


@pytest.mark.skip('TODO: fix in CARGODEV-11356')
@pytest.mark.config(
    CARGO_CLAIMS_PRICING_HANDLER_SETTINGS={'enabled': True, 'sleep_ms': 50},
)
async def test_cargo_pricing_handler(
        state_controller,
        run_cargo_pricing_handler,
        mock_cargo_pricing_confirm_usage,
):
    state_controller.set_options(cargo_pricing_flow=True)
    await state_controller.apply(target_status='accepted')

    result = await run_cargo_pricing_handler()
    assert result == {
        'stats': {
            'handled-claims-with-cargo-pricing-flow-count': 1,
            'processed-events-count': 4,
        },
    }
    assert mock_cargo_pricing_confirm_usage.mock.times_called == 1
    result = await run_cargo_pricing_handler()
    assert result == {
        'stats': {
            'handled-claims-with-cargo-pricing-flow-count': 0,
            'processed-events-count': 0,
        },
    }


@pytest.mark.skip('TODO: fix in CARGODEV-11356')
@pytest.mark.config(
    CARGO_CLAIMS_PRICING_HANDLER_SETTINGS={'enabled': True, 'sleep_ms': 50},
)
async def test_cargo_pricing_handler_default_flow(
        state_controller, run_cargo_pricing_handler,
):

    await state_controller.apply(target_status='accepted')

    result = await run_cargo_pricing_handler()
    assert result == {
        'stats': {
            'handled-claims-with-cargo-pricing-flow-count': 0,
            'processed-events-count': 4,
        },
    }


@pytest.mark.skip('TODO: fix in CARGODEV-11356')
@pytest.mark.config(
    CARGO_CLAIMS_PRICING_HANDLER_SETTINGS={'enabled': True, 'sleep_ms': 50},
)
async def test_cargo_pricing_handler_with_pricing_404(
        mockserver,
        state_controller,
        run_cargo_pricing_handler,
        mock_cargo_pricing_confirm_usage,
):
    mock_cargo_pricing_confirm_usage.response = mockserver.make_response(
        json={}, status=404,
    )
    state_controller.set_options(
        cargo_pricing_flow=True,
        claim_index=1,
        offer_id='taxi_offer_id_2',
        request_id='idempotency_token_2',
    )
    await state_controller.apply(target_status='accepted', claim_index=1)

    mock_cargo_pricing_confirm_usage.response = {}

    state_controller.set_options(
        cargo_pricing_flow=True,
        claim_index=0,
        offer_id='taxi_offer_id_1',
        request_id='idempotency_token_1',
    )
    await state_controller.apply(target_status='accepted', claim_index=0)

    result = await run_cargo_pricing_handler()

    assert mock_cargo_pricing_confirm_usage.request == {
        'calc_id': 'cargo-pricing/v1/taxi_offer_id_1',
        'external_ref': matching.any_string,
    }
    assert mock_cargo_pricing_confirm_usage.request['external_ref'].startswith(
        'cargo_ref_id/',
    )

    assert mock_cargo_pricing_confirm_usage.mock.times_called == 2
    assert result == {
        'stats': {
            'handled-claims-with-cargo-pricing-flow-count': 2,
            'processed-events-count': 8,
        },
    }

    result = await run_cargo_pricing_handler()

    assert result == {
        'stats': {
            'handled-claims-with-cargo-pricing-flow-count': 0,
            'processed-events-count': 0,
        },
    }
