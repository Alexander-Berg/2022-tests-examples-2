import datetime

import pytest

from tests_eats_place_subscriptions import utils


@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
@pytest.mark.experiments3(filename='subscriptions_enabled.json')
@pytest.mark.experiments3(filename='tariffs.json')
@pytest.mark.now('2020-05-15T12:00:00+00:00')
@pytest.mark.parametrize(
    [
        'input_places',
        'expected_db_result',
        'expected_errors_metrics',
        'expected_change_log',
    ],
    [
        (
            [
                {'place_id': 123, 'tariff': 'free', 'is_trial': True},
                {
                    'place_id': 125,
                    'tariff': 'business_plus',
                    'activated_at': '2020-05-15T12:30:16.663Z',
                },
            ],
            [
                (
                    123,
                    'business',
                    'free',
                    False,
                    False,
                    True,
                    datetime.datetime(
                        2020, 5, 31, 21, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 4, 28, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    None,
                ),
                (
                    125,
                    'free',
                    'business_plus',
                    True,
                    False,
                    False,
                    datetime.datetime(
                        2020, 5, 15, 13, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 4, 28, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    None,
                ),
            ],
            {'not_found_in_db': 0},
            [
                (
                    123,
                    'update-subscription',
                    'superuser',
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
                        'next_tariff': 'free',
                    },
                ),
                (
                    125,
                    'update-subscription',
                    'superuser',
                    {
                        'place_id': 125,
                        'tariff': 'free',
                        'is_trial': False,
                        'next_tariff': None,
                    },
                    {
                        'place_id': 125,
                        'tariff': 'free',
                        'is_trial': False,
                        'next_tariff': 'business_plus',
                    },
                ),
            ],
        ),
        (
            [{'place_id': 123, 'tariff': 'business'}],
            [
                (
                    123,
                    'business',
                    None,
                    False,
                    False,
                    False,
                    datetime.datetime(
                        2020, 4, 30, 21, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 4, 28, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    None,
                ),
            ],
            {'not_found_in_db': 0},
            [
                (
                    123,
                    'update-subscription',
                    'superuser',
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
            ],
        ),
        (
            [
                {
                    'place_id': 125,
                    'tariff': 'business_plus',
                    'activated_at': '2020-04-15T12:30:16.663Z',
                },
            ],
            [
                (
                    125,
                    'free',
                    'business_plus',
                    True,
                    False,
                    False,
                    datetime.datetime(
                        2020, 5, 15, 13, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 4, 28, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    None,
                ),
            ],
            {'not_found_in_db': 0},
            [
                (
                    125,
                    'update-subscription',
                    'superuser',
                    {
                        'place_id': 125,
                        'tariff': 'free',
                        'is_trial': False,
                        'next_tariff': None,
                    },
                    {
                        'place_id': 125,
                        'tariff': 'free',
                        'is_trial': False,
                        'next_tariff': 'business_plus',
                    },
                ),
            ],
        ),
        (
            [
                {'place_id': 123, 'tariff': 'free'},
                {'place_id': 100, 'tariff': 'business_plus'},
            ],
            [
                (
                    123,
                    'business',
                    'free',
                    False,
                    False,
                    False,
                    datetime.datetime(
                        2020, 5, 31, 21, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 4, 28, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    None,
                ),
            ],
            {'not_found_in_db': 1},
            [
                (
                    123,
                    'update-subscription',
                    'superuser',
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
                        'next_tariff': 'free',
                    },
                ),
            ],
        ),
        ([], [], {'not_found_in_db': 0}, []),
    ],
    ids=[
        'green_flow',
        'same_input_type',
        'activated_at_in_past',
        'not_exist_places',
        'empty_place_ids',
    ],
)
async def test_update_subscriptions(
        taxi_eats_place_subscriptions,
        taxi_eats_place_subscriptions_monitor,
        input_places,
        expected_db_result,
        expected_errors_metrics,
        expected_change_log,
        pgsql,
):
    await taxi_eats_place_subscriptions.tests_control(reset_metrics=True)

    response = await taxi_eats_place_subscriptions.post(
        '/admin/place-subscriptions/v1/subscriptions/put',
        headers={'X-Yandex-Login': 'superuser'},
        json={'places': input_places},
    )

    assert response.status_code == 200
    for subscription, change_log in zip(
            expected_db_result, expected_change_log,
    ):
        db_result = await utils.db_get_subscription(pgsql, subscription[0])
        assert subscription == db_result
        db_change_log = await utils.db_get_latest_change_log(
            pgsql, subscription[0],
        )
        utils.check_change_log(db_change_log, change_log)

    metrics = await taxi_eats_place_subscriptions_monitor.get_metrics()
    assert (
        metrics[utils.SUBSCRIPTION_ERRORS_METRICS] == expected_errors_metrics
    )


@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
@pytest.mark.experiments3(filename='subscriptions_enabled.json')
async def test_update_subscriptions_no_tariff(
        taxi_eats_place_subscriptions, taxi_eats_place_subscriptions_monitor,
):
    await taxi_eats_place_subscriptions.tests_control(reset_metrics=True)

    response = await taxi_eats_place_subscriptions.post(
        '/admin/place-subscriptions/v1/subscriptions/put',
        headers={'X-YaEda-PartnerId': '1234'},
        json={
            'places': [
                {'place_id': 123, 'tariff': 'free'},
                {'place_id': 125, 'tariff': 'business_plus'},
            ],
        },
    )
    assert response.status_code == 500

    metrics = await taxi_eats_place_subscriptions_monitor.get_metrics()
    assert metrics[utils.TARIFF_ERRORS_METRICS] == {'not_found_in_config': 1}
