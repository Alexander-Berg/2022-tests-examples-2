from typing import Optional

import pytest


HANDLE_URL = '/internal/tips/v1/get-tips-sum'


@pytest.mark.pgsql('tips', files=['tips.sql'])
async def test_missing_order(taxi_tips):
    order_id = 'nonexistent_order_id'
    response = await taxi_tips.post(HANDLE_URL, params={'order_id': order_id})
    assert response.status_code == 404


@pytest.mark.config(
    TIPS_DONT_RESET_COUNTRIES=['isr'], TIME_BEFORE_TAKE_TIPS=3600,
)
@pytest.mark.tariff_settings(filename='tariff_settings.json')
@pytest.mark.pgsql('tips', files=['tips.sql'])
@pytest.mark.now('2020-10-30T12:00:00Z')
@pytest.mark.parametrize(
    ['order_id', 'expected_new_tips_sum'],
    [
        ('order_1', 600000),
        ('order_2_finish_handled_false', None),
        ('order_3_need_accept', None),
        ('order_4_need_disp_accept', None),
        ('order_5_tips_dont_reset_country_old_is_zero', 600000),
        ('order_6_tips_dont_reset_country_old_is_not_zero', None),
        ('order_6_2_old_is_not_zero_zone_not_in_ts', None),
        ('order_6_3_old_is_not_zero_zone_in_ts', 600000),
        ('order_7_has_negative_feedback', None),
        ('order_8_has_positive_feedback', 600000),
        ('order_9_tips_payment_failed', 0),
        ('order_9_2_tips_payment_failed_tips_sum_zero', 0),
        ('order_9_3_tips_payment_failed_tips_dont_reset_country', 0),
        ('order_10_same_tips', None),
        ('order_11_new_smaller_tips', 500000),
        ('order_12_ctt_false', None),  # need_hold_tips=False
        ('order_13_order_too_new', None),
        ('order_14_order_too_new_positive_feedback', 600000),
        ('order_15_order_slightly_old', 600000),
        ('order_16_tips_perc_default_int_value', 478000),
        ('order_17_tips_perc_default_real_value', 501900),
        ('order_18_tips_percent', 478000),
    ],
)
async def test_can_take_tips(
        taxi_tips, order_id: str, expected_new_tips_sum: Optional[int],
):
    response = await taxi_tips.post(HANDLE_URL, params={'order_id': order_id})
    assert response.status_code == 200
    new_tips_sum = response.json().get('new_tips_sum')
    assert new_tips_sum == expected_new_tips_sum
