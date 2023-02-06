import pytest


@pytest.mark.skip('TODO: fix in CARGODEV-11356')
@pytest.mark.config(
    CARGO_CLAIMS_DRIVER_RETURN_REASONS=[
        {'reason': 'reason_a', 'tanker_key': 'tanker_key_a'},
        {'reason': 'reason_b', 'tanker_key': 'tanker_key_b'},
    ],
)
@pytest.mark.translations(
    cargo={
        'tanker_key_a': {'ru': 'Причина А'},
        'tanker_key_b': {'ru': 'Причина Б'},
    },
)
async def test_return_reasons(
        taxi_cargo_orders, get_default_driver_auth_headers,
):
    response = await taxi_cargo_orders.get(
        'driver/v1/cargo-claims/v1/cargo/return/reasons',
        headers=get_default_driver_auth_headers,
    )
    assert response.status_code == 200
    assert response.json() == {
        'responses': [
            {'key': 'reason_a', 'text': 'Причина А'},
            {'key': 'reason_b', 'text': 'Причина Б'},
        ],
    }
