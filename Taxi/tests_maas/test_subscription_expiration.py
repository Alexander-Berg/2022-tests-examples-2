import pytest


@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
async def test_subscriptions_expiration(taxi_maas, get_subscriptions):
    await taxi_maas.run_periodic_task('subscriptions_expiration')

    expired_subs = get_subscriptions('status=\'expired\'')
    for expired_sub in expired_subs:
        # correct expired coupons marked by coupon_id
        assert expired_sub.coupon_id == 'expired_coupon'

        status_history = expired_sub.status_history
        if status_history:
            last_update = status_history[-1]
            assert last_update.new_status == 'expired'
            assert last_update.reason == 'periodic_expiration'

    not_expired_subs = get_subscriptions('status!=\'expired\'')
    for not_expired_sub in not_expired_subs:
        assert not_expired_sub.coupon_id != 'expired_coupon'
        status_history = not_expired_sub.status_history
        assert not status_history


@pytest.mark.config(
    MAAS_RESERVED_CHECK_SETTINGS={
        'reserved_subscription_ttl_ms': 600000,
        'first_check_delay_ms': 2000,
        'second_check_delay_ms': 500,
    },
)
@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
async def test_subscriptions_cancellation(taxi_maas, get_subscriptions):
    await taxi_maas.run_periodic_task('subscriptions_cancellation')

    canceled_subs = get_subscriptions('status=\'canceled\'')
    for canceled_sub in canceled_subs:
        # correct canceled coupons marked by coupon_id
        assert canceled_sub.coupon_id == 'canceled_coupon'
        status_history = canceled_sub.status_history
        if status_history:
            last_update = status_history[-1]
            assert last_update.new_status == 'canceled'
            assert last_update.reason == 'periodic_cancellation'

    not_canceled_subs = get_subscriptions('status!=\'canceled\'')
    for not_canceled_sub in not_canceled_subs:
        assert not_canceled_sub.coupon_id != 'canceled_coupon'
        status_history = not_canceled_sub.status_history
        assert not status_history


@pytest.mark.config(
    MAAS_RESERVED_CHECK_SETTINGS={
        'first_check_delay_ms': 2000,
        'second_check_delay_ms': 500,
    },
)
@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
async def test_subscriptions_cancellation_disabled(
        taxi_maas, get_subscriptions,
):
    all_subscriptions_before = get_subscriptions('status IS NOT NULL')

    await taxi_maas.run_periodic_task('subscriptions_cancellation')

    all_subscriptions_after = get_subscriptions('status IS NOT NULL')

    assert all_subscriptions_before == all_subscriptions_after
