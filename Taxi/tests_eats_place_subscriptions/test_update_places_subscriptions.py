import datetime as dt

import pytest

from tests_eats_place_subscriptions import utils


PERIODIC_NAME = 'update-places-subscriptions-periodic'


@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
@pytest.mark.config(
    EATS_PLACE_SUBSCRIPTIONS_PERIODICS={
        PERIODIC_NAME: {
            'is_enabled': True,
            'period_in_sec': 300,
            'db_chunk_size': 1,
            'sleep_time_after_iteration': 1,
        },
    },
)
@pytest.mark.experiments3(filename='tariffs.json')
@pytest.mark.parametrize(
    'current_time, db_expected_subscriptions, db_expected_change_log',
    [
        pytest.param(
            dt.datetime(2020, 4, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
            # в плейсе UTC+5
            [
                (
                    123,
                    'business',
                    None,
                    False,
                    False,
                    False,
                    dt.datetime(2020, 5, 31, 21, 0, tzinfo=utils.PG_TIMEZONE),
                    dt.datetime(2020, 4, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
                    None,
                ),
                (
                    129,
                    'business_plus',
                    None,
                    True,
                    True,
                    False,
                    dt.datetime(2020, 5, 31, 21, 0, tzinfo=utils.PG_TIMEZONE),
                    dt.datetime(2020, 4, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
                    None,
                ),
            ],
            [
                (
                    123,
                    'update-subscription',
                    'update-places-subscriptions-periodic',
                    {
                        'place_id': 123,
                        'tariff': 'business',
                        'is_trial': False,
                        'next_tariff': None,
                    },
                    {
                        'place_id': 123,
                        'tariff': 'business',
                        'is_trial': False,
                        'next_tariff': None,
                    },
                ),
                (
                    129,
                    'update-subscription',
                    'update-places-subscriptions-periodic',
                    {
                        'place_id': 129,
                        'tariff': 'business',
                        'is_trial': True,
                        'next_tariff': 'business_plus',
                        'next_is_trial': True,
                    },
                    {
                        'place_id': 129,
                        'tariff': 'business_plus',
                        'is_trial': True,
                        'next_tariff': None,
                        'next_is_trial': False,
                    },
                ),
            ],
            id='has_subscriptions_to_update_with_next',
        ),
        pytest.param(
            dt.datetime(2020, 4, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
            [],
            [],
            id='has_no_subscriptions_to_update',
        ),
    ],
)
async def test_update_places_subscriptions(
        taxi_eats_place_subscriptions,
        taxi_eats_place_subscriptions_monitor,
        testpoint,
        mocked_time,
        mockserver,
        pgsql,
        # parametrize params
        current_time,
        db_expected_subscriptions,
        db_expected_change_log,
):
    await taxi_eats_place_subscriptions.tests_control(reset_metrics=True)
    mocked_time.set(current_time)

    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    await taxi_eats_place_subscriptions.run_distlock_task(PERIODIC_NAME)

    assert periodic_finished.times_called == 1
    for exp_subscription, exp_change_log in zip(
            db_expected_subscriptions, db_expected_change_log,
    ):
        db_result = await utils.db_get_subscription(pgsql, exp_subscription[0])
        assert exp_subscription == db_result
        db_change_log = await utils.db_get_latest_change_log(
            pgsql, exp_subscription[0],
        )
        utils.check_change_log(db_change_log, exp_change_log)


@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_place_subscriptions_counters.sql'],
)
@pytest.mark.config(
    EATS_PLACE_SUBSCRIPTIONS_PERIODICS={
        PERIODIC_NAME: {
            'is_enabled': True,
            'period_in_sec': 300,
            'db_chunk_size': 1,
            'sleep_time_after_iteration': 1,
        },
    },
)
@pytest.mark.experiments3(filename='tariffs.json')
@pytest.mark.parametrize(
    'current_time, db_expected_subscriptions',
    [
        pytest.param(
            dt.datetime(2020, 1, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
            [
                (
                    111,
                    'business',
                    None,
                    False,
                    False,
                    False,
                    dt.datetime(2020, 1, 31, 21, 0, tzinfo=utils.PG_TIMEZONE),
                    dt.datetime(2020, 1, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
                    None,
                ),
            ],
            id='111_no_trial_31_orders',
        ),
        pytest.param(
            dt.datetime(2020, 2, 28, 21, 2, tzinfo=utils.PG_TIMEZONE),
            [
                (
                    222,
                    'business',
                    None,
                    False,
                    True,
                    False,
                    dt.datetime(2020, 2, 29, 21, 0, tzinfo=utils.PG_TIMEZONE),
                    dt.datetime(2020, 2, 28, 21, 2, tzinfo=utils.PG_TIMEZONE),
                    None,
                ),
            ],
            id='222_trial_29_orders',
        ),
        pytest.param(
            dt.datetime(2020, 3, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
            [
                (
                    333,
                    'business_plus',
                    None,
                    False,
                    False,
                    False,
                    dt.datetime(2020, 3, 31, 21, 0, tzinfo=utils.PG_TIMEZONE),
                    dt.datetime(2020, 3, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
                    None,
                ),
            ],
            id='333_no_trial_31_orders_and_business_plus',
        ),
        pytest.param(
            dt.datetime(2020, 4, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
            [
                (
                    444,
                    'business_plus',
                    None,
                    False,
                    False,
                    False,
                    dt.datetime(2020, 5, 31, 21, 0, tzinfo=utils.PG_TIMEZONE),
                    dt.datetime(2020, 4, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
                    None,
                ),
            ],
            id='444_no_trial_29_orders_and_business_plus',
        ),
        pytest.param(
            dt.datetime(2020, 5, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
            [
                (
                    555,
                    'business',
                    None,
                    False,
                    False,
                    False,
                    dt.datetime(2020, 5, 31, 21, 0, tzinfo=utils.PG_TIMEZONE),
                    dt.datetime(2020, 5, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
                    None,
                ),
            ],
            id='555_no_trial_31_order_and_next_tariff',
        ),
        pytest.param(
            dt.datetime(2020, 6, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
            [
                (
                    666,
                    'business',
                    None,
                    False,
                    True,
                    False,
                    dt.datetime(2020, 7, 31, 21, 0, tzinfo=utils.PG_TIMEZONE),
                    dt.datetime(2020, 6, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
                    None,
                ),
            ],
            id='666_trial_next_tariff_business_and_29_orders',
        ),
        pytest.param(
            dt.datetime(2020, 7, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
            [
                (
                    777,
                    'business_plus',
                    None,
                    False,
                    False,
                    False,
                    dt.datetime(2020, 7, 31, 21, 0, tzinfo=utils.PG_TIMEZONE),
                    dt.datetime(2020, 7, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
                    None,
                ),
            ],
            id='777_no_trial_current_and_next_tariff_business_plus_and_31_o',
        ),
        pytest.param(
            dt.datetime(2020, 8, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
            [
                (
                    888,
                    'business_plus',
                    None,
                    False,
                    False,
                    False,
                    dt.datetime(2020, 8, 31, 21, 0, tzinfo=utils.PG_TIMEZONE),
                    dt.datetime(2020, 8, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
                    None,
                ),
            ],
            id='888_no_trial_current_and_next_tariff_business_plus_and_29_o',
        ),
        pytest.param(
            dt.datetime(2020, 9, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
            [
                (
                    999,
                    'business',
                    None,
                    False,
                    True,
                    False,
                    dt.datetime(2020, 10, 31, 21, 0, tzinfo=utils.PG_TIMEZONE),
                    dt.datetime(2020, 9, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
                    None,
                ),
            ],
            id='999_trial_0_orders_and_tariff_business',
        ),
        pytest.param(
            dt.datetime(2020, 10, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
            [
                (
                    1111,
                    'business_plus',
                    None,
                    False,
                    False,
                    False,
                    dt.datetime(2020, 10, 31, 21, 0, tzinfo=utils.PG_TIMEZONE),
                    dt.datetime(2020, 10, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
                    None,
                ),
            ],
            id='1111_no_trial_0_orders_and_tariff_business_plus',
        ),
        pytest.param(
            dt.datetime(2020, 11, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
            [
                (
                    2222,
                    'business',
                    None,
                    False,
                    True,
                    False,
                    dt.datetime(2020, 12, 31, 21, 0, tzinfo=utils.PG_TIMEZONE),
                    dt.datetime(2020, 11, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
                    None,
                ),
            ],
            id='2222_trial_0_orders_and_next_tariff_business',
        ),
        pytest.param(
            dt.datetime(2020, 12, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
            [
                (
                    3333,
                    'business_plus',
                    None,
                    False,
                    False,
                    False,
                    dt.datetime(2020, 12, 31, 21, 0, tzinfo=utils.PG_TIMEZONE),
                    dt.datetime(2020, 12, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
                    None,
                ),
            ],
            id='3333_no_trial_0_orders_and_next_tariff_business_plus',
        ),
        pytest.param(
            dt.datetime(2020, 1, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
            [
                (
                    111,
                    'business',
                    None,
                    False,
                    True,
                    False,
                    dt.datetime(2020, 1, 31, 21, 0, tzinfo=utils.PG_TIMEZONE),
                    dt.datetime(2020, 1, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
                    None,
                ),
            ],
            id='111_trial_31_orders',
            marks=[
                pytest.mark.experiments3(
                    filename='tariffs_trial_counters.json',
                ),
            ],
        ),
        pytest.param(
            dt.datetime(2020, 2, 28, 21, 2, tzinfo=utils.PG_TIMEZONE),
            [
                (
                    222,
                    'business',
                    None,
                    False,
                    False,
                    False,
                    dt.datetime(2020, 2, 29, 21, 0, tzinfo=utils.PG_TIMEZONE),
                    dt.datetime(2020, 2, 28, 21, 2, tzinfo=utils.PG_TIMEZONE),
                    None,
                ),
            ],
            id='222_no_trial_29_orders',
            marks=[
                pytest.mark.experiments3(
                    filename='tariffs_trial_counters.json',
                ),
            ],
        ),
        pytest.param(
            dt.datetime(2020, 9, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
            [
                (
                    999,
                    'business',
                    None,
                    False,
                    False,
                    False,
                    dt.datetime(2020, 10, 31, 21, 0, tzinfo=utils.PG_TIMEZONE),
                    dt.datetime(2020, 9, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
                    None,
                ),
            ],
            id='999_no_trial_0_orders_and_default_exp_value',
            marks=[
                pytest.mark.experiments3(
                    filename='tariffs_trial_counters.json',
                ),
            ],
        ),
        pytest.param(
            dt.datetime(2020, 4, 30, 21, 2, tzinfo=utils.PG_TIMEZONE),
            [],
            id='has_no_subscriptions_to_update',
        ),
    ],
)
async def test_update_places_subscriptions_counters(
        taxi_eats_place_subscriptions,
        taxi_eats_place_subscriptions_monitor,
        testpoint,
        mocked_time,
        mockserver,
        pgsql,
        # parametrize params
        current_time,
        db_expected_subscriptions,
):
    await taxi_eats_place_subscriptions.tests_control(reset_metrics=True)
    mocked_time.set(current_time)

    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    await taxi_eats_place_subscriptions.run_distlock_task(PERIODIC_NAME)

    assert periodic_finished.times_called == 1
    for exp_subscription in db_expected_subscriptions:
        db_result = await utils.db_get_subscription(pgsql, exp_subscription[0])
        assert exp_subscription == db_result


@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
async def test_check_tariff_actual_metrics(
        taxi_eats_place_subscriptions,
        taxi_eats_place_subscriptions_monitor,
        testpoint,
        mocked_time,
        mockserver,
        pgsql,
):
    await taxi_eats_place_subscriptions.run_periodic_task(
        'tariffs_actual_stats_task',
    )
    metrics = await taxi_eats_place_subscriptions_monitor.get_metrics()
    assert metrics[utils.COMMON_METRICS]['tariffs_actual'] == {
        'business': 5,
        'business_plus': 4,
        'free': 6,
        'business_plus_trial': 1,
        'business_trial': 1,
    }
