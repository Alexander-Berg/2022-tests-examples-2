import pytest

from tests_eats_pro_orders_bdu import models


TIMERS_SETTINGS = {
    'eta': {
        'before_calculated': {'subtitle_key': 'test.before_eta_calculated'},
        'after_calculated': {'subtitle_key': 'test.after_eta_calculated'},
        'after_passed': {'subtitle_key': 'test.after_eta_passed'},
    },
    'waiting': {
        'paid': {'subtitle_key': 'test.paid_wait'},
        'free': {'subtitle_key': 'test.free_wait'},
        'paid_end': {'subtitle_key': 'test.paid_wait_end'},
    },
}


@pytest.mark.experiments3(filename='tracking_enabled.json')
@pytest.mark.experiments3(
    name='cargo_orders_taximeter_timers_settings',
    consumers=['cargo-orders/build-timer-action'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value=TIMERS_SETTINGS,
    is_config=True,
)
async def test_base_offer_set(
        taxi_eats_pro_orders_bdu,
        localizations,
        default_order_id,
        cargo,
        load_json,
        mock_driver_tags_v1_match_profile,
):
    response = await taxi_eats_pro_orders_bdu.post(
        '/driver/v1/eats-pro-orders-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    expected_timers = load_json('timer.json')
    assert (
        response.json()['state']['ui']['items'][0]['items'][0]
        == expected_timers
    )
