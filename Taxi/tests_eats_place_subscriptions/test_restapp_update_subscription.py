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
        'expected_response',
        'expected_db_result',
        'expected_errors_metrics',
        'expected_change_log',
    ],
    [
        (
            [
                {'place_id': 123, 'tariff': 'free'},
                {'place_id': 125, 'tariff': 'business_plus'},
            ],
            {
                'subscriptions': [
                    {
                        'activated_at': '28.04.2020',
                        'activated_at_iso': '2020-04-28T12:00:00+00:00',
                        'is_partner_updated': True,
                        'is_trial': False,
                        'need_alerting_about_finishing_trial': False,
                        'place_id': 123,
                        'tariff_info': {
                            'additional_commission': 1.44,
                            'features': ['daily_billing', 'sorry', 'boss_bot'],
                            'type': 'business',
                        },
                        'next_tariff': 'free',
                        'valid_until': '16.05.2020',
                        'valid_until_iso': '2020-05-15T21:00:00+00:00',
                        'next_tariff_info': {
                            'features': ['weekly_billing'],
                            'type': 'free',
                        },
                    },
                    {
                        'activated_at': '28.04.2020',
                        'activated_at_iso': '2020-04-28T12:00:00+00:00',
                        'is_partner_updated': True,
                        'is_trial': False,
                        'need_alerting_about_finishing_trial': False,
                        'place_id': 125,
                        'tariff_info': {
                            'features': ['weekly_billing'],
                            'type': 'free',
                        },
                        'next_tariff': 'business_plus',
                        'valid_until': '16.05.2020',
                        'valid_until_iso': '2020-05-16T03:00:00+00:00',
                        'next_tariff_info': {
                            'additional_commission': 1.44,
                            'currency': {
                                'code': 'RUB',
                                'sign': '₽',
                                'template': '$VALUE$\u2006$SIGN$$CURRENCY$',
                                'text': 'руб.',
                            },
                            'features': [
                                'daily_billing',
                                'sorry',
                                'boss_bot',
                                'personal_manager',
                            ],
                            'fix_cost_rules': {
                                'bundle_cost': 1299.0,
                                'bundle_size': 3,
                                'extra_cost': 500.0,
                            },
                            'type': 'business_plus',
                        },
                    },
                ],
            },
            [
                (
                    123,
                    'business',
                    'free',
                    True,
                    False,
                    False,
                    datetime.datetime(
                        2020, 5, 15, 21, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 4, 28, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 5, 15, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                ),
                (
                    125,
                    'free',
                    'business_plus',
                    True,
                    False,
                    False,
                    datetime.datetime(
                        2020, 5, 16, 3, 0, tzinfo=utils.PG_TIMEZONE,
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
                    'partner-1234',
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
                    'partner-1234',
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
            {
                'subscriptions': [
                    {
                        'activated_at': '28.04.2020',
                        'activated_at_iso': '2020-04-28T12:00:00+00:00',
                        'is_trial': False,
                        'need_alerting_about_finishing_trial': False,
                        'is_partner_updated': True,
                        'place_id': 123,
                        'tariff_info': {
                            'additional_commission': 1.44,
                            'features': ['daily_billing', 'sorry', 'boss_bot'],
                            'type': 'business',
                        },
                        'valid_until': '01.05.2020',
                        'valid_until_iso': '2020-04-30T21:00:00+00:00',
                    },
                ],
            },
            [
                (
                    123,
                    'business',
                    None,
                    True,
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
                    'partner-1234',
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
                {'place_id': 123, 'tariff': 'free'},
                {'place_id': 100, 'tariff': 'business_plus'},
            ],
            {
                'subscriptions': [
                    {
                        'activated_at': '28.04.2020',
                        'activated_at_iso': '2020-04-28T12:00:00+00:00',
                        'is_partner_updated': True,
                        'is_trial': False,
                        'need_alerting_about_finishing_trial': False,
                        'place_id': 123,
                        'tariff_info': {
                            'additional_commission': 1.44,
                            'features': ['daily_billing', 'sorry', 'boss_bot'],
                            'type': 'business',
                        },
                        'next_tariff': 'free',
                        'valid_until': '16.05.2020',
                        'valid_until_iso': '2020-05-15T21:00:00+00:00',
                        'next_tariff_info': {
                            'features': ['weekly_billing'],
                            'type': 'free',
                        },
                    },
                ],
            },
            [
                (
                    123,
                    'business',
                    'free',
                    True,
                    False,
                    False,
                    datetime.datetime(
                        2020, 5, 15, 21, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 4, 28, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 5, 15, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                ),
            ],
            {'not_found_in_db': 1},
            [
                (
                    123,
                    'update-subscription',
                    'partner-1234',
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
        ([], {'subscriptions': []}, {}, {'not_found_in_db': 0}, []),
    ],
    ids=[
        'green_flow',
        'same_input_type',
        'not_exist_places',
        'empty_place_ids',
    ],
)
async def test_update_subscriptions(
        taxi_eats_place_subscriptions,
        taxi_eats_place_subscriptions_monitor,
        input_places,
        expected_response,
        expected_db_result,
        expected_errors_metrics,
        expected_change_log,
        pgsql,
        mock_restapp_authorizer,
):
    await taxi_eats_place_subscriptions.tests_control(reset_metrics=True)

    response = await taxi_eats_place_subscriptions.post(
        '/4.0/restapp-front/v1/place-subscriptions/'
        'v1/place/update-subscriptions',
        headers={'X-YaEda-PartnerId': '1234'},
        json={'places': input_places},
    )

    assert response.status_code == 200
    assert response.json() == expected_response
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
        taxi_eats_place_subscriptions,
        taxi_eats_place_subscriptions_monitor,
        mock_restapp_authorizer,
):
    await taxi_eats_place_subscriptions.tests_control(reset_metrics=True)

    response = await taxi_eats_place_subscriptions.post(
        '/4.0/restapp-front/v1/place-subscriptions/'
        'v1/place/update-subscriptions',
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


@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
@pytest.mark.experiments3(filename='tariffs.json')
@pytest.mark.parametrize(
    'body, code',
    [
        (
            {
                'code': '403',
                'message': 'forbidden',
                'details': {
                    'permissions': ['permission.restaurant.functionality'],
                    'place_ids': [123],
                },
            },
            403,
        ),
        ({'code': '400', 'message': 'bad request'}, 400),
    ],
)
async def test_update_subscriptions_authorizer_errors(
        taxi_eats_place_subscriptions, body, code, mockserver,
):
    @mockserver.json_handler(
        '/eats-restapp-authorizer/' 'v1/user-access/check',
    )
    def _mock_authorizer(request):
        return mockserver.make_response(status=code, json=body)

    response = await taxi_eats_place_subscriptions.post(
        '/4.0/restapp-front/v1/place-subscriptions/v1/'
        'place/update-subscriptions',
        headers={'X-YaEda-PartnerId': '1234'},
        json={'places': [{'place_id': 123, 'tariff': 'free'}]},
    )

    assert response.status_code == code


@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
@pytest.mark.experiments3(filename='subscriptions_enabled.json')
@pytest.mark.experiments3(filename='tariffs.json')
@pytest.mark.now('2020-05-15T12:00:00+00:00')
@pytest.mark.parametrize(
    'input_places, expected_response, expected_db_result',
    [
        (
            [
                {'place_id': 133, 'tariff': 'business'},
                {'place_id': 136, 'tariff': 'free'},
            ],
            {
                'subscriptions': [
                    {
                        'activated_at': '28.04.2020',
                        'activated_at_iso': '2020-04-28T12:00:00+00:00',
                        'is_partner_updated': True,
                        'is_trial': False,
                        'need_alerting_about_finishing_trial': False,
                        'place_id': 133,
                        'tariff_info': {
                            'additional_commission': 1.44,
                            'currency': {
                                'code': 'RUB',
                                'sign': '₽',
                                'template': '$VALUE$\u2006$SIGN$$CURRENCY$',
                                'text': 'руб.',
                            },
                            'features': [
                                'daily_billing',
                                'sorry',
                                'boss_bot',
                                'personal_manager',
                            ],
                            'fix_cost_rules': {
                                'bundle_cost': 1299.0,
                                'bundle_size': 3,
                                'extra_cost': 500.0,
                            },
                            'type': 'business_plus',
                        },
                        'next_tariff': 'business',
                        'valid_until': '16.05.2020',
                        'valid_until_iso': '2020-05-15T19:00:00+00:00',
                        'next_tariff_info': {
                            'additional_commission': 1.44,
                            'features': ['daily_billing', 'sorry', 'boss_bot'],
                            'type': 'business',
                        },
                    },
                    {
                        'activated_at': '28.04.2020',
                        'activated_at_iso': '2020-04-28T12:00:00+00:00',
                        'is_partner_updated': True,
                        'is_trial': False,
                        'need_alerting_about_finishing_trial': False,
                        'place_id': 136,
                        'tariff_info': {
                            'additional_commission': 1.44,
                            'features': ['daily_billing', 'sorry', 'boss_bot'],
                            'type': 'business',
                        },
                        'next_tariff': 'free',
                        'valid_until': '16.05.2020',
                        'valid_until_iso': '2020-05-15T21:00:00+00:00',
                        'next_tariff_info': {
                            'features': ['weekly_billing'],
                            'type': 'free',
                        },
                    },
                ],
            },
            [
                (
                    133,
                    'business_plus',
                    'business',
                    True,
                    False,
                    False,
                    datetime.datetime(
                        2020, 5, 15, 19, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 4, 28, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 5, 15, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                ),
                (
                    136,
                    'business',
                    'free',
                    True,
                    False,
                    False,
                    datetime.datetime(
                        2020, 5, 15, 21, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 4, 28, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 5, 15, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                ),
            ],
        ),
        (
            [
                {'place_id': 135, 'tariff': 'business'},
                {'place_id': 138, 'tariff': 'free'},
            ],
            {
                'subscriptions': [
                    {
                        'activated_at': '28.04.2020',
                        'activated_at_iso': '2020-04-28T12:00:00+00:00',
                        'is_trial': False,
                        'need_alerting_about_finishing_trial': False,
                        'is_partner_updated': True,
                        'place_id': 135,
                        'tariff_info': {
                            'additional_commission': 1.44,
                            'currency': {
                                'code': 'RUB',
                                'sign': '₽',
                                'template': '$VALUE$\u2006$SIGN$$CURRENCY$',
                                'text': 'руб.',
                            },
                            'features': [
                                'daily_billing',
                                'sorry',
                                'boss_bot',
                                'personal_manager',
                            ],
                            'fix_cost_rules': {
                                'bundle_cost': 1299.0,
                                'bundle_size': 3,
                                'extra_cost': 500.0,
                            },
                            'type': 'business_plus',
                        },
                        'next_tariff': 'business',
                        'valid_until': '01.06.2020',
                        'valid_until_iso': '2020-05-31T19:00:00+00:00',
                        'next_tariff_info': {
                            'additional_commission': 1.44,
                            'features': ['daily_billing', 'sorry', 'boss_bot'],
                            'type': 'business',
                        },
                    },
                    {
                        'activated_at': '28.04.2020',
                        'activated_at_iso': '2020-04-28T12:00:00+00:00',
                        'is_trial': False,
                        'need_alerting_about_finishing_trial': False,
                        'is_partner_updated': True,
                        'place_id': 138,
                        'tariff_info': {
                            'additional_commission': 1.44,
                            'features': ['daily_billing', 'sorry', 'boss_bot'],
                            'type': 'business',
                        },
                        'next_tariff': 'free',
                        'valid_until': '01.06.2020',
                        'valid_until_iso': '2020-05-31T21:00:00+00:00',
                        'next_tariff_info': {
                            'features': ['weekly_billing'],
                            'type': 'free',
                        },
                    },
                ],
            },
            [
                (
                    135,
                    'business_plus',
                    'business',
                    True,
                    False,
                    False,
                    datetime.datetime(
                        2020, 5, 31, 19, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 4, 28, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 5, 15, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                ),
                (
                    138,
                    'business',
                    'free',
                    True,
                    False,
                    False,
                    datetime.datetime(
                        2020, 5, 31, 21, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 4, 28, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 5, 15, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                ),
            ],
        ),
        (
            [
                {'place_id': 134, 'tariff': 'free'},
                {'place_id': 137, 'tariff': 'free'},
            ],
            {
                'subscriptions': [
                    {
                        'activated_at': '28.04.2020',
                        'activated_at_iso': '2020-04-28T12:00:00+00:00',
                        'is_partner_updated': True,
                        'is_trial': False,
                        'need_alerting_about_finishing_trial': False,
                        'place_id': 134,
                        'tariff_info': {
                            'additional_commission': 1.44,
                            'currency': {
                                'code': 'RUB',
                                'sign': '₽',
                                'template': '$VALUE$\u2006$SIGN$$CURRENCY$',
                                'text': 'руб.',
                            },
                            'features': [
                                'daily_billing',
                                'sorry',
                                'boss_bot',
                                'personal_manager',
                            ],
                            'fix_cost_rules': {
                                'bundle_cost': 1299.0,
                                'bundle_size': 3,
                                'extra_cost': 500.0,
                            },
                            'type': 'business_plus',
                        },
                        'next_tariff': 'free',
                        'valid_until': '16.05.2020',
                        'valid_until_iso': '2020-05-15T19:00:00+00:00',
                        'next_tariff_info': {
                            'features': ['weekly_billing'],
                            'type': 'free',
                        },
                    },
                    {
                        'activated_at': '28.04.2020',
                        'activated_at_iso': '2020-04-28T12:00:00+00:00',
                        'is_partner_updated': True,
                        'is_trial': False,
                        'need_alerting_about_finishing_trial': False,
                        'place_id': 137,
                        'tariff_info': {
                            'additional_commission': 1.44,
                            'features': ['daily_billing', 'sorry', 'boss_bot'],
                            'type': 'business',
                        },
                        'next_tariff': 'free',
                        'valid_until': '16.05.2020',
                        'valid_until_iso': '2020-05-15T21:00:00+00:00',
                        'next_tariff_info': {
                            'features': ['weekly_billing'],
                            'type': 'free',
                        },
                    },
                ],
            },
            [
                (
                    134,
                    'business_plus',
                    'free',
                    True,
                    False,
                    False,
                    datetime.datetime(
                        2020, 5, 15, 19, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 4, 28, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 5, 15, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                ),
                (
                    137,
                    'business',
                    'free',
                    True,
                    False,
                    False,
                    datetime.datetime(
                        2020, 5, 15, 21, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 4, 28, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 5, 15, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                ),
            ],
        ),
        (
            [
                {'place_id': 133, 'tariff': 'business_plus'},
                {'place_id': 136, 'tariff': 'business'},
                {'place_id': 139, 'tariff': 'free'},
            ],
            {
                'subscriptions': [
                    {
                        'activated_at': '28.04.2020',
                        'activated_at_iso': '2020-04-28T12:00:00+00:00',
                        'is_partner_updated': True,
                        'is_trial': False,
                        'need_alerting_about_finishing_trial': False,
                        'place_id': 133,
                        'tariff_info': {
                            'additional_commission': 1.44,
                            'currency': {
                                'code': 'RUB',
                                'sign': '₽',
                                'template': '$VALUE$\u2006$SIGN$$CURRENCY$',
                                'text': 'руб.',
                            },
                            'features': [
                                'daily_billing',
                                'sorry',
                                'boss_bot',
                                'personal_manager',
                            ],
                            'fix_cost_rules': {
                                'bundle_cost': 1299.0,
                                'bundle_size': 3,
                                'extra_cost': 500.0,
                            },
                            'type': 'business_plus',
                        },
                        'valid_until': '01.05.2020',
                        'valid_until_iso': '2020-04-30T19:00:00+00:00',
                    },
                    {
                        'activated_at': '28.04.2020',
                        'activated_at_iso': '2020-04-28T12:00:00+00:00',
                        'is_partner_updated': True,
                        'is_trial': False,
                        'need_alerting_about_finishing_trial': False,
                        'place_id': 136,
                        'tariff_info': {
                            'additional_commission': 1.44,
                            'features': ['daily_billing', 'sorry', 'boss_bot'],
                            'type': 'business',
                        },
                        'valid_until': '01.05.2020',
                        'valid_until_iso': '2020-04-30T21:00:00+00:00',
                    },
                    {
                        'activated_at': '28.04.2020',
                        'activated_at_iso': '2020-04-28T12:00:00+00:00',
                        'is_partner_updated': True,
                        'is_trial': False,
                        'need_alerting_about_finishing_trial': False,
                        'place_id': 139,
                        'tariff_info': {
                            'features': ['weekly_billing'],
                            'type': 'free',
                        },
                        'valid_until': '01.05.2020',
                        'valid_until_iso': '2020-04-30T21:00:00+00:00',
                    },
                ],
            },
            [
                (
                    133,
                    'business_plus',
                    None,
                    True,
                    False,
                    False,
                    datetime.datetime(
                        2020, 4, 30, 19, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 4, 28, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    None,
                ),
                (
                    136,
                    'business',
                    None,
                    True,
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
                (
                    139,
                    'free',
                    None,
                    True,
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
        ),
        (
            [
                {'place_id': 136, 'tariff': 'business_plus'},
                {'place_id': 139, 'tariff': 'business'},
            ],
            {
                'subscriptions': [
                    {
                        'activated_at': '28.04.2020',
                        'activated_at_iso': '2020-04-28T12:00:00+00:00',
                        'is_partner_updated': True,
                        'is_trial': False,
                        'need_alerting_about_finishing_trial': False,
                        'place_id': 136,
                        'tariff_info': {
                            'additional_commission': 1.44,
                            'features': ['daily_billing', 'sorry', 'boss_bot'],
                            'type': 'business',
                        },
                        'next_tariff': 'business_plus',
                        'valid_until': '16.05.2020',
                        'valid_until_iso': '2020-05-15T21:00:00+00:00',
                        'next_tariff_info': {
                            'additional_commission': 1.44,
                            'currency': {
                                'code': 'RUB',
                                'sign': '₽',
                                'template': '$VALUE$\u2006$SIGN$$CURRENCY$',
                                'text': 'руб.',
                            },
                            'features': [
                                'daily_billing',
                                'sorry',
                                'boss_bot',
                                'personal_manager',
                            ],
                            'fix_cost_rules': {
                                'bundle_cost': 1299.0,
                                'bundle_size': 3,
                                'extra_cost': 500.0,
                            },
                            'type': 'business_plus',
                        },
                    },
                    {
                        'activated_at': '28.04.2020',
                        'activated_at_iso': '2020-04-28T12:00:00+00:00',
                        'is_partner_updated': True,
                        'is_trial': False,
                        'need_alerting_about_finishing_trial': False,
                        'place_id': 139,
                        'tariff_info': {
                            'features': ['weekly_billing'],
                            'type': 'free',
                        },
                        'next_tariff': 'business',
                        'valid_until': '16.05.2020',
                        'valid_until_iso': '2020-05-15T21:00:00+00:00',
                        'next_tariff_info': {
                            'additional_commission': 1.44,
                            'features': ['daily_billing', 'sorry', 'boss_bot'],
                            'type': 'business',
                        },
                    },
                ],
            },
            [
                (
                    136,
                    'business',
                    'business_plus',
                    True,
                    False,
                    False,
                    datetime.datetime(
                        2020, 5, 15, 21, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 4, 28, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    None,
                ),
                (
                    139,
                    'free',
                    'business',
                    True,
                    False,
                    False,
                    datetime.datetime(
                        2020, 5, 15, 21, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    datetime.datetime(
                        2020, 4, 28, 12, 0, tzinfo=utils.PG_TIMEZONE,
                    ),
                    None,
                ),
            ],
        ),
    ],
    ids=[
        'last_partner_downdate_time = NULL',
        'last_partner_downdate_time in current month',
        'last_partner_downdate_time in previous month',
        'new tarif is same',
        'new tarif is large',
    ],
)
async def test_update_subscriptions_check_valid_until(
        taxi_eats_place_subscriptions,
        taxi_eats_place_subscriptions_monitor,
        input_places,
        expected_response,
        expected_db_result,
        pgsql,
        mock_restapp_authorizer,
):
    await taxi_eats_place_subscriptions.tests_control(reset_metrics=True)

    response = await taxi_eats_place_subscriptions.post(
        '/4.0/restapp-front/v1/place-subscriptions/'
        'v1/place/update-subscriptions',
        headers={'X-YaEda-PartnerId': '1234'},
        json={'places': input_places},
    )

    assert response.status_code == 200
    assert response.json() == expected_response
    for subscription in expected_db_result:
        db_result = await utils.db_get_subscription(pgsql, subscription[0])
        assert subscription == db_result
