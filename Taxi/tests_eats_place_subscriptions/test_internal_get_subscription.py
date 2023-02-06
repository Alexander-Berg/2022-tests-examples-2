import pytest

from tests_eats_place_subscriptions import utils


EXPECTED_RESPONSE = {
    'subscriptions': [
        {
            'activated_at': '28.04.2020',
            'activated_at_iso': '2020-04-28T12:00:00+00:00',
            'is_partner_updated': False,
            'is_trial': True,
            'need_alerting_about_finishing_trial': True,
            'place_id': 201,
            'tariff_info': {
                'additional_commission': 1.44,
                'features': ['daily_billing', 'sorry', 'boss_bot'],
                'type': 'business',
            },
            'valid_until': '01.02.2020',
            'valid_until_iso': '2020-02-01T12:00:00+00:00',
        },
        {
            'activated_at': '28.04.2020',
            'activated_at_iso': '2020-04-28T12:00:00+00:00',
            'is_partner_updated': False,
            'is_trial': True,
            'need_alerting_about_finishing_trial': True,
            'place_id': 202,
            'tariff_info': {
                'additional_commission': 1.44,
                'features': ['daily_billing', 'sorry', 'boss_bot'],
                'type': 'business',
            },
            'valid_until': '02.02.2020',
            'valid_until_iso': '2020-02-02T12:00:00+00:00',
        },
        {
            'activated_at': '28.04.2020',
            'activated_at_iso': '2020-04-28T12:00:00+00:00',
            'is_partner_updated': False,
            'is_trial': True,
            'need_alerting_about_finishing_trial': True,
            'place_id': 203,
            'tariff_info': {
                'additional_commission': 1.44,
                'features': ['daily_billing', 'sorry', 'boss_bot'],
                'type': 'business',
            },
            'valid_until': '03.02.2020',
            'valid_until_iso': '2020-02-03T12:00:00+00:00',
        },
        {
            'activated_at': '28.04.2020',
            'activated_at_iso': '2020-04-28T12:00:00+00:00',
            'is_partner_updated': False,
            'is_trial': True,
            'need_alerting_about_finishing_trial': True,
            'place_id': 204,
            'tariff_info': {
                'additional_commission': 1.44,
                'features': ['daily_billing', 'sorry', 'boss_bot'],
                'type': 'business',
            },
            'valid_until': '04.02.2020',
            'valid_until_iso': '2020-02-04T12:00:00+00:00',
        },
        {
            'activated_at': '28.04.2020',
            'activated_at_iso': '2020-04-28T12:00:00+00:00',
            'is_partner_updated': False,
            'is_trial': True,
            'need_alerting_about_finishing_trial': True,
            'place_id': 205,
            'tariff_info': {
                'additional_commission': 1.44,
                'features': ['daily_billing', 'sorry', 'boss_bot'],
                'type': 'business',
            },
            'valid_until': '06.02.2020',
            'valid_until_iso': '2020-02-06T02:59:00+00:00',
        },
        {
            'activated_at': '28.04.2020',
            'activated_at_iso': '2020-04-28T12:00:00+00:00',
            'is_partner_updated': False,
            'is_trial': True,
            'need_alerting_about_finishing_trial': False,
            'place_id': 206,
            'tariff_info': {
                'additional_commission': 1.44,
                'features': ['daily_billing', 'sorry', 'boss_bot'],
                'type': 'business',
            },
            'valid_until': '06.02.2020',
            'valid_until_iso': '2020-02-06T03:00:01+00:00',
        },
        {
            'activated_at': '28.04.2020',
            'activated_at_iso': '2020-04-28T12:00:00+00:00',
            'is_partner_updated': False,
            'is_trial': False,
            'need_alerting_about_finishing_trial': False,
            'place_id': 207,
            'tariff_info': {
                'additional_commission': 1.44,
                'features': ['daily_billing', 'sorry', 'boss_bot'],
                'type': 'business',
            },
            'valid_until': '02.02.2020',
            'valid_until_iso': '2020-02-02T12:00:00+00:00',
        },
        {
            'activated_at': '28.04.2020',
            'activated_at_iso': '2020-04-28T12:00:00+00:00',
            'is_partner_updated': False,
            'is_trial': True,
            'need_alerting_about_finishing_trial': False,
            'place_id': 208,
            'next_tariff': 'free',
            'tariff_info': {
                'additional_commission': 1.44,
                'features': ['daily_billing', 'sorry', 'boss_bot'],
                'type': 'business',
            },
            'valid_until': '02.02.2020',
            'valid_until_iso': '2020-02-02T12:00:00+00:00',
            'next_tariff_info': {
                'features': ['weekly_billing'],
                'type': 'free',
            },
        },
        {
            'activated_at': '28.04.2020',
            'activated_at_iso': '2020-04-28T12:00:00+00:00',
            'is_partner_updated': False,
            'is_trial': True,
            'need_alerting_about_finishing_trial': True,
            'place_id': 209,
            'next_tariff': 'business_plus',
            'tariff_info': {
                'additional_commission': 1.44,
                'features': ['daily_billing', 'sorry', 'boss_bot'],
                'type': 'business',
            },
            'valid_until': '02.02.2020',
            'valid_until_iso': '2020-02-02T12:00:00+00:00',
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
}


@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
@pytest.mark.now('2020-02-02T15:00:00+0300')
@pytest.mark.experiments3(filename='tariffs.json')
@pytest.mark.experiments3(filename='subscriptions_enabled.json')
async def test_get_subscriptions(taxi_eats_place_subscriptions):
    response = await taxi_eats_place_subscriptions.post(
        '/internal/eats-place-subscriptions/v1/place/get-subscriptions?partner_id=1234',
        json={'place_ids': [201, 202, 203, 204, 205, 206, 207, 208, 209, 210]},
    )

    assert response.status_code == 200
    assert response.json() == EXPECTED_RESPONSE
