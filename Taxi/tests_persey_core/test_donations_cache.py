# pylint: disable=C5521
from collections import defaultdict
from decimal import Decimal

import pytest

from tests_persey_core import utils


class _DonationsStatsHelper:
    def __init__(self):
        self.stats = defaultdict(
            lambda: defaultdict(lambda: {'count': 0, 'money': Decimal()}),
        )
        self.contributors = 0

    def add(self, app, brand, cnt, money):
        self.stats[app][brand]['count'] += cnt
        self.stats[app][brand]['money'] += Decimal(money)

    def get_stats(self):
        result = {
            'any_app': {
                'any_brand': {'count': 0, 'sum': '0'},
                'by_brand': defaultdict(lambda: {'count': 0, 'sum': '0'}),
            },
            'by_app': defaultdict(
                lambda: {
                    'any_brand': {'count': 0, 'sum': '0'},
                    'by_brand': defaultdict(lambda: {'count': 0, 'sum': '0'}),
                },
            ),
            'contributors': self.contributors,
        }
        for app, brands in self.stats.items():
            for brand, stat in brands.items():
                count = stat['count']
                money = Decimal(stat['money'])
                if stat['count'] != 0:
                    result['any_app']['any_brand']['count'] += count
                    result['any_app']['by_brand'][brand]['count'] += count
                    result['by_app'][app]['any_brand']['count'] += count
                    result['by_app'][app]['by_brand'][brand]['count'] += count
                    result['any_app']['any_brand']['sum'] = str(
                        Decimal(result['any_app']['any_brand']['sum']) + money,
                    )
                    result['any_app']['by_brand'][brand]['sum'] = str(
                        Decimal(result['any_app']['by_brand'][brand]['sum'])
                        + money,
                    )
                    result['by_app'][app]['any_brand']['sum'] = str(
                        Decimal(result['by_app'][app]['any_brand']['sum'])
                        + money,
                    )
                    result['by_app'][app]['by_brand'][brand]['sum'] = str(
                        Decimal(
                            result['by_app'][app]['by_brand'][brand]['sum'],
                        )
                        + money,
                    )
        return result


@pytest.mark.parametrize('full_update', [True, False])
async def test_donations_cache(
        taxi_persey_core, persey_core_internal, pgsql, full_update,
):
    # Simple initial test:
    cursor = pgsql['persey_payments'].cursor()
    utils.fill_db(
        cursor,
        {
            'persey_payments.fund': [
                {
                    'fund_id': 'sample_fund_id',
                    'name': 'sample_name',
                    'offer_link': 'sample_offer_link',
                    'operator_uid': 'sample_operator_uid',
                    'balance_client_id': 'sample_balance_client_id',
                    'trust_partner_id': 'sample_trust_partner_id',
                    'trust_product_id': 'sample_trust_product_id',
                    'is_hidden': False,
                    'created_at': '2020-01-01T00:00:00+00:00',
                    'available_amount': '0',
                    'exclude_from_sampling': False,
                },
            ],
            'persey_payments.donation': [
                {
                    'id': 60000,
                    'fund_id': 'sample_fund_id',
                    'yandex_uid': '999',
                    'status': 'finished',
                    'created_at': '2022-02-02T10:00:00+00:00',
                    'updated_at': '2022-02-02T10:00:00+00:00',
                    'sum': '50.6',
                },
                {
                    'id': 70000,
                    'fund_id': 'sample_fund_id',
                    'yandex_uid': '100',
                    'status': 'finished',
                    'created_at': '2022-02-01T10:00:00+00:00',
                    'updated_at': '2022-02-01T10:00:00+00:00',
                    'brand': 'yataxi',
                    'application': 'go_android',
                    'sum': '5.06e1',
                },
                {
                    'id': 70100,
                    'fund_id': 'sample_fund_id',
                    'yandex_uid': '100',
                    'status': 'finished',
                    'created_at': '2022-02-02T10:00:00+00:00',
                    'updated_at': '2022-02-02T10:00:00+00:00',
                    'brand': 'yataxi',
                    'sum': '14',
                },
                {
                    'id': 70101,
                    'fund_id': 'sample_fund_id',
                    'yandex_uid': '100',
                    'status': 'started',
                    'created_at': '2022-02-02T10:00:00+00:00',
                    'updated_at': '2022-02-02T10:00:00+00:00',
                    'brand': 'yataxi',
                    'sum': '99999',
                },
                {
                    'id': 70102,
                    'fund_id': 'sample_fund_id',
                    'yandex_uid': '100',
                    'status': 'finished',
                    'created_at': '2022-02-02T10:00:00+00:00',
                    'updated_at': '2022-02-02T10:00:00+00:00',
                    'brand': 'overflow',
                    'sum': '1' * 25,
                },
                {
                    'id': 70200,
                    'fund_id': 'sample_fund_id',
                    'yandex_uid': '200',
                    'status': 'finished',
                    'created_at': '2022-02-02T10:00:00+00:00',
                    'updated_at': '2022-02-02T10:00:00+00:00',
                    'brand': 'eats',
                    'application': 'go_android',
                    'sum': '56',
                },
            ],
        },
    )
    expected_cache = defaultdict(
        lambda: {
            'donations': defaultdict(dict),
            'sum_any_brand': '0',
            'sum_by_brand': {},
        },
    )
    expected_cache.update(
        {
            '100': {
                'donations': {
                    '70000': {
                        'amount': '50.6',
                        'app': 'go_android',
                        'brand': 'yataxi',
                    },
                    '70100': {'amount': '14', 'app': '', 'brand': 'yataxi'},
                },
                'sum_any_brand': '64.6',
                'sum_by_brand': {'yataxi': '64.6'},
            },
            '200': {
                'donations': {
                    '70200': {
                        'amount': '56',
                        'app': 'go_android',
                        'brand': 'eats',
                    },
                },
                'sum_any_brand': '56',
                'sum_by_brand': {'eats': '56'},
            },
        },
    )
    expected_stats = _DonationsStatsHelper()
    expected_stats.add('go_android', 'yataxi', 1, '50.6')
    expected_stats.add('', 'yataxi', 1, '14')
    expected_stats.add('go_android', 'eats', 1, '56')
    expected_stats.contributors = 2

    await taxi_persey_core.invalidate_caches(
        clean_update=full_update, cache_names=['donations-cache'],
    )
    result = await persey_core_internal.call('GetEntireDonationsCache')
    assert result == expected_cache
    result = await persey_core_internal.call('GetDonationsCacheStats')
    assert result == expected_stats.get_stats()
    result = await persey_core_internal.call('GetDonationsCacheMaxUpdatedAt')
    assert result == '2022-02-02T10:00:00+00:00'

    # Revoke some donations
    cursor.execute(
        'ALTER TABLE persey_payments.donation DISABLE TRIGGER all; '
        'UPDATE persey_payments.donation '
        'SET status = \'not_authorized\' '
        'WHERE id in (70000, 70200)',
    )

    expected_cache['200'] = {
        'donations': {},
        'sum_any_brand': '0',
        'sum_by_brand': {},
    }
    if full_update:
        del expected_cache['100']['donations']['70000']
        expected_cache['100']['sum_any_brand'] = '14'
        expected_cache['100']['sum_by_brand']['yataxi'] = '14'
        expected_stats.add('go_android', 'yataxi', -1, '-50.6')

    expected_stats.add('go_android', 'eats', -1, '-56')
    expected_stats.contributors -= 1

    await taxi_persey_core.invalidate_caches(
        clean_update=full_update, cache_names=['donations-cache'],
    )
    result = await persey_core_internal.call('GetEntireDonationsCache')
    assert result == expected_cache
    result = await persey_core_internal.call('GetDonationsCacheStats')
    assert result == expected_stats.get_stats()
    result = await persey_core_internal.call('GetDonationsCacheMaxUpdatedAt')
    assert result == '2022-02-02T10:00:00+00:00'

    # Update a donation
    cursor.execute(
        'UPDATE persey_payments.donation '
        'SET sum = \'33\', '
        '    application = \'ios\', '
        '    updated_at = \'2022-02-03T10:00:00+00:00\' '
        'WHERE id = 70100',
    )
    expected_stats.add('', 'yataxi', -1, '-14')
    expected_stats.add('ios', 'yataxi', 1, '33')
    expected_cache['100']['donations']['70100']['amount'] = '33'
    expected_cache['100']['donations']['70100']['app'] = 'ios'
    if full_update:
        expected_cache['100']['sum_any_brand'] = '33'
        expected_cache['100']['sum_by_brand']['yataxi'] = '33'
    else:
        expected_cache['100']['sum_any_brand'] = '83.6'
        expected_cache['100']['sum_by_brand']['yataxi'] = '83.6'

    await taxi_persey_core.invalidate_caches(
        clean_update=full_update, cache_names=['donations-cache'],
    )
    result = await persey_core_internal.call('GetEntireDonationsCache')
    assert result == expected_cache
    result = await persey_core_internal.call('GetDonationsCacheStats')
    assert result == expected_stats.get_stats()
    result = await persey_core_internal.call('GetDonationsCacheMaxUpdatedAt')
    assert result == '2022-02-03T10:00:00+00:00'

    # Add a new donation
    utils.fill_db(
        cursor,
        {
            'persey_payments.donation': [
                {
                    'id': 70300,
                    'fund_id': 'sample_fund_id',
                    'yandex_uid': '300',
                    'status': 'finished',
                    'created_at': '2022-02-01T00:00:00+00:00',
                    'updated_at': '2022-02-04T10:00:00+00:00',
                    'brand': 'lavka',
                    'application': 'lavka_android',
                    'sum': '99',
                },
            ],
        },
    )
    expected_stats.add('lavka_android', 'lavka', 1, '99')
    expected_stats.contributors += 1
    expected_cache['300']['donations'] = {
        '70300': {'amount': '99', 'brand': 'lavka', 'app': 'lavka_android'},
    }
    expected_cache['300']['sum_any_brand'] = '99'
    expected_cache['300']['sum_by_brand']['lavka'] = '99'
    await taxi_persey_core.invalidate_caches(
        clean_update=full_update, cache_names=['donations-cache'],
    )
    result = await persey_core_internal.call('GetEntireDonationsCache')
    assert result == expected_cache
    result = await persey_core_internal.call('GetDonationsCacheStats')
    assert result == expected_stats.get_stats()
    result = await persey_core_internal.call('GetDonationsCacheMaxUpdatedAt')
    assert result == '2022-02-04T10:00:00+00:00'


async def test_donations_cache_dump_empty(
        taxi_persey_core, persey_core_internal,
):
    await taxi_persey_core.write_cache_dumps(names=['donations-cache'])
    await taxi_persey_core.read_cache_dumps(names=['donations-cache'])
    result = await persey_core_internal.call('GetEntireDonationsCache')
    assert result == {}
    result = await persey_core_internal.call('GetDonationsCacheMaxUpdatedAt')
    assert result == '1970-01-01T00:00:00+00:00'


async def test_donations_cache_dump(
        taxi_persey_core,
        persey_core_internal,
        pgsql,
        taxi_persey_core_monitor,
):
    cursor = pgsql['persey_payments'].cursor()
    utils.fill_db(
        cursor,
        {
            'persey_payments.fund': [
                {
                    'fund_id': 'sample_fund_id',
                    'name': 'sample_name',
                    'offer_link': 'sample_offer_link',
                    'operator_uid': 'sample_operator_uid',
                    'balance_client_id': 'sample_balance_client_id',
                    'trust_partner_id': 'sample_trust_partner_id',
                    'trust_product_id': 'sample_trust_product_id',
                    'is_hidden': False,
                    'created_at': '2020-01-01T00:00:00+00:00',
                    'available_amount': '0',
                    'exclude_from_sampling': False,
                },
            ],
            'persey_payments.donation': [
                {
                    'id': 70000,
                    'fund_id': 'sample_fund_id',
                    'yandex_uid': '100',
                    'status': 'finished',
                    'created_at': '2022-02-01T10:00:00+00:00',
                    'updated_at': '2022-02-01T10:00:00+00:00',
                    'brand': 'yataxi',
                    'application': 'go_android',
                    'sum': '50.6',
                },
                {
                    'id': 70100,
                    'fund_id': 'sample_fund_id',
                    'yandex_uid': '100',
                    'status': 'finished',
                    'created_at': '2022-02-02T10:00:00+00:00',
                    'updated_at': '2022-02-02T10:00:00+00:00',
                    'brand': 'lavka',
                    'sum': '14',
                },
                {
                    'id': 70150,
                    'fund_id': 'sample_fund_id',
                    'yandex_uid': '100',
                    'status': 'finished',
                    'created_at': '2022-02-05T10:00:00+00:00',
                    'updated_at': '2022-02-05T10:00:00+00:00',
                    'brand': 'lavka',
                    'sum': '7',
                },
                {
                    'id': 70200,
                    'fund_id': 'sample_fund_id',
                    'yandex_uid': '200',
                    'status': 'finished',
                    'created_at': '2022-02-02T10:00:00+00:00',
                    'updated_at': '2022-02-02T10:00:00+00:00',
                    'brand': 'eats',
                    'application': 'go_ios',
                    'sum': '56',
                },
            ],
        },
    )
    await taxi_persey_core.invalidate_caches(
        clean_update=True, cache_names=['donations-cache'],
    )
    await taxi_persey_core.write_cache_dumps(names=['donations-cache'])
    cursor.execute('DELETE FROM persey_payments.donation')
    await taxi_persey_core.invalidate_caches(
        clean_update=True, cache_names=['donations-cache'],
    )
    result = await persey_core_internal.call('GetEntireDonationsCache')
    assert result == {}

    await taxi_persey_core.read_cache_dumps(names=['donations-cache'])
    expected_cache = {
        '100': {
            'donations': {
                '70000': {
                    'amount': '50.6',
                    'app': 'go_android',
                    'brand': 'yataxi',
                },
                '70100': {'amount': '14', 'app': '', 'brand': 'lavka'},
                '70150': {'amount': '7', 'app': '', 'brand': 'lavka'},
            },
            'sum_any_brand': '71.6',
            'sum_by_brand': {'yataxi': '50.6', 'lavka': '21'},
        },
        '200': {
            'donations': {
                '70200': {'amount': '56', 'app': 'go_ios', 'brand': 'eats'},
            },
            'sum_any_brand': '56',
            'sum_by_brand': {'eats': '56'},
        },
    }
    expected_stats = _DonationsStatsHelper()
    expected_stats.add('go_android', 'yataxi', 1, '50.6')
    expected_stats.add('', 'lavka', 2, '21')
    expected_stats.add('go_ios', 'eats', 1, '56')
    expected_stats.contributors = 2

    result = await persey_core_internal.call('GetEntireDonationsCache')
    assert result == expected_cache
    result = await persey_core_internal.call('GetDonationsCacheStats')
    assert result == expected_stats.get_stats()
    result = await persey_core_internal.call('GetDonationsCacheMaxUpdatedAt')
    assert result == '2022-02-05T10:00:00+00:00'
    result = await taxi_persey_core_monitor.get_metric(
        'donations-cache-metrics',
    )
    assert result == {
        'contributors': 2,
        'stats': {
            '$meta': {'solomon_children_labels': 'app'},
            '__any__': {
                '$meta': {'solomon_children_labels': 'brand'},
                '__any__': {'count': 4, 'sum': 127.6},
                'eats': {'count': 1, 'sum': 56},
                'lavka': {'count': 2, 'sum': 21},
                'yataxi': {'count': 1, 'sum': 50.6},
            },
            '__null__': {
                '$meta': {'solomon_children_labels': 'brand'},
                '__any__': {'count': 2, 'sum': 21},
                'eats': {'count': 0, 'sum': 0},
                'lavka': {'count': 2, 'sum': 21},
                'yataxi': {'count': 0, 'sum': 0},
            },
            'go_android': {
                '$meta': {'solomon_children_labels': 'brand'},
                '__any__': {'count': 1, 'sum': 50.6},
                'eats': {'count': 0, 'sum': 0},
                'lavka': {'count': 0, 'sum': 0},
                'yataxi': {'count': 1, 'sum': 50.6},
            },
            'go_ios': {
                '$meta': {'solomon_children_labels': 'brand'},
                '__any__': {'count': 1, 'sum': 56},
                'eats': {'count': 1, 'sum': 56},
                'lavka': {'count': 0, 'sum': 0},
                'yataxi': {'count': 0, 'sum': 0},
            },
        },
    }
