import pytest


HANDLE_URL = '/internal/tips/v1/need-hold-tips'


@pytest.mark.pgsql('tips', files=['tips.sql'])
async def test_missing_order(taxi_tips):
    order_id = 'nonexistent_order_id'
    response = await taxi_tips.post(HANDLE_URL, params={'order_id': order_id})
    assert response.status_code == 404


@pytest.mark.config(TIME_BEFORE_TAKE_TIPS=3600)
@pytest.mark.pgsql('tips', files=['tips.sql'])
@pytest.mark.parametrize(
    ['order_id', 'expected_need_hold_tips'],
    [
        ('order_1_card', True),
        ('order_2_applepay', False),
        ('order_3_card_no_billing_id', False),
        ('order_4_has_ride_only_transactions', True),
        ('order_5_has_ride_and_tips_transactions', False),
        ('order_6_zero_ride_sum_to_pay', False),
        ('order_7_ctt_false', False),
        ('order_7_2_ctt_true', True),
        ('order_8_need_accept', False),
        ('order_108_doenst_need_accept', True),
        ('order_9_need_disp_accept', False),
        ('order_109_doesnt_need_disp_accept', True),
        ('order_10_taxi_status_not_complete', False),
        ('order_11_has_zero_cost', True),
        ('order_12_has_zero_cost_and_percent_tips', False),
        ('order_13_invalid_coupon', True),
        ('order_14_unused_coupon', True),
        ('order_15_zero_percent_coupon', True),
        ('order_16_percent_coupon', False),
        ('order_17_zero_value_coupon', True),
        ('order_18_normal_value_coupon', False),
        ('order_19_empty_coupon', True),
        ('order_20_null_value_billing_id', False),
        ('order_21_percent_tips', True),
        ('order_22_real_tips_value', True),
        ('order_23_small_real_tips_value', True),
        ('order_24_zero_flat_tips', False),
        ('order_25_zero_percent_tips', False),
        ('order_26_no_creditcard_tips', True),
        ('order_27_no_creditcard_tips_and_zero_default', False),
        ('order_28_no_creditcard_tips_and_no_default', False),
        ('order_29_very_big_integers', True),
    ],
)
async def test_can_take_tips(
        taxi_tips, order_id: str, expected_need_hold_tips: bool,
):
    response = await taxi_tips.post(HANDLE_URL, params={'order_id': order_id})
    assert response.status_code == 200
    resp = response.json()
    assert resp['need_hold_tips'] == expected_need_hold_tips
    assert resp['time_before_take_tips'] == 3600
