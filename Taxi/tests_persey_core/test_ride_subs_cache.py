# pylint: disable=C5521
from collections import defaultdict

import pytest

from tests_persey_core import utils


class _RideSubsStatsHelper:
    def __init__(self):
        self.counts = defaultdict(lambda: defaultdict(lambda: 0))
        self.participants = 0

    def add(self, sub_src, brand, cnt):
        self.counts[sub_src][brand] += cnt

    def get_stats(self):
        result = {
            'any_sub_src': {
                'any_brand': {'count': 0},
                'by_brand': defaultdict(lambda: {'count': 0}),
            },
            'by_sub_src': defaultdict(
                lambda: {
                    'any_brand': {'count': 0},
                    'by_brand': defaultdict(lambda: {'count': 0}),
                },
            ),
            'participants': self.participants,
        }
        for sub_src, brands in self.counts.items():
            for brand, count in brands.items():
                if count != 0:
                    result['any_sub_src']['any_brand']['count'] += count
                    result['any_sub_src']['by_brand'][brand]['count'] += count
                    result['by_sub_src'][sub_src]['any_brand'][
                        'count'
                    ] += count
                    result['by_sub_src'][sub_src]['by_brand'][brand][
                        'count'
                    ] += count
        return result


@pytest.mark.parametrize('proper_hidden', [True, False])
@pytest.mark.parametrize('full_update', [True, False])
async def test_ride_subs_cache(
        taxi_persey_core,
        persey_core_internal,
        pgsql,
        full_update,
        proper_hidden,
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
            'persey_payments.ride_subs': [
                {
                    'id': 90000,
                    'yandex_uid': '100',
                    'brand': 'yataxi',
                    'fund_id': 'sample_fund_id',
                    'mod': 10,
                    'created_at': '2022-02-01T10:00:00+00:00',
                    'updated_at': '2022-02-01T10:00:00+00:00',
                    'locale': 'ru',
                },
                {
                    'id': 90010,
                    'yandex_uid': '100',
                    'brand': 'eats',
                    'fund_id': 'sample_fund_id',
                    'mod': 20,
                    'created_at': '2022-02-09T10:00:00+00:00',
                    'updated_at': '2022-02-09T11:00:00+00:00',
                    'hidden_at': '2022-02-09T11:00:00+00:00',
                    'locale': 'ru',
                },
                {
                    'id': 90020,
                    'yandex_uid': '100',
                    'brand': 'eats',
                    'fund_id': 'sample_fund_id',
                    'mod': 20,
                    'created_at': '2022-02-10T10:00:00+00:00',
                    'updated_at': '2022-02-12T13:00:00+03:00',
                    'locale': 'ru',
                },
                {
                    'id': 90030,
                    'yandex_uid': '101',
                    'brand': 'market',
                    'fund_id': 'sample_fund_id',
                    'mod': 30,
                    'created_at': '2022-02-09T10:00:00+00:00',
                    'updated_at': '2022-02-11T10:00:00+00:00',
                    'locale': 'ru',
                    'subscription_source': 'go_android',
                },
                {
                    'id': 90040,
                    'yandex_uid': '102',
                    'brand': 'market',
                    'fund_id': 'sample_fund_id',
                    'mod': 50,
                    'created_at': '2022-02-11T10:00:00+00:00',
                    'updated_at': '2022-02-11T11:00:00+00:00',
                    'hidden_at': '2022-02-11T11:00:00+00:00',
                    'locale': 'ru',
                    'subscription_source': 'go_ios',
                },
            ],
        },
    )
    expected_cache = defaultdict(dict)
    expected_cache.update(
        {
            '100': {
                'yataxi': {
                    'created_at': '2022-02-01T10:00:00+00:00',
                    'mod': 10,
                    'sub_src': '',
                },
                'eats': {
                    'created_at': '2022-02-10T10:00:00+00:00',
                    'mod': 20,
                    'sub_src': '',
                },
            },
            '101': {
                'market': {
                    'created_at': '2022-02-09T10:00:00+00:00',
                    'mod': 30,
                    'sub_src': 'go_android',
                },
            },
            '102': {
                'market': {
                    'created_at': '2022-02-11T10:00:00+00:00',
                    'hidden_at': '2022-02-11T11:00:00+00:00',
                    'mod': 50,
                    'sub_src': 'go_ios',
                },
            },
        },
    )
    expected_stats = _RideSubsStatsHelper()
    expected_stats.add('', 'yataxi', 1)
    expected_stats.add('', 'eats', 1)
    expected_stats.add('go_android', 'market', 1)
    expected_stats.participants = 2

    await taxi_persey_core.invalidate_caches(
        clean_update=full_update, cache_names=['ride-subs-cache'],
    )
    result = await persey_core_internal.call('GetEntireRideSubsCache')
    assert result == expected_cache
    result = await persey_core_internal.call('GetRideSubsCacheStats')
    assert result == expected_stats.get_stats()
    result = await persey_core_internal.call('GetRideSubsCacheMaxUpdatedAt')
    assert result == '2022-02-12T10:00:00+00:00'

    # Add some subs, overriding as well some of the existing subs:
    utils.fill_db(
        cursor,
        {
            'persey_payments.ride_subs': [
                {
                    'id': 90001,
                    'yandex_uid': '100',
                    'brand': 'yataxi',
                    'fund_id': 'sample_fund_id',
                    'mod': 66,
                    'created_at': '2022-02-01T10:00:00+00:00',
                    'updated_at': '2022-02-12T10:00:00+00:00',
                    'locale': 'ru',
                    'subscription_source': 'go_android',
                },
                {
                    'id': 90050,
                    'yandex_uid': '100',
                    'brand': 'lavka',
                    'fund_id': 'sample_fund_id',
                    'mod': 90,
                    'created_at': '2022-02-19T10:00:00+00:00',
                    'updated_at': '2022-02-19T10:00:00+00:00',
                    'locale': 'ru',
                    'subscription_source': 'market_mobile',
                },
                {
                    'id': 90060,
                    'yandex_uid': '102',
                    'brand': 'lavka',
                    'fund_id': 'sample_fund_id',
                    'mod': 90,
                    'created_at': '2022-02-11T10:00:00+00:00',
                    'updated_at': '2022-02-12T09:59:59+00:00',
                    'hidden_at': '2022-02-12T09:59:59+00:00',
                    'locale': 'ru',
                },
                {
                    'id': 90070,
                    'yandex_uid': '103',
                    'brand': 'eats',
                    'fund_id': 'sample_fund_id',
                    'mod': 90,
                    'created_at': '2022-02-11T10:00:00+00:00',
                    'updated_at': '2022-02-12T09:59:55+00:00',
                    'locale': 'ru',
                    'subscription_source': 'market_desktop',
                },
                {
                    'id': 90080,
                    'yandex_uid': '104',
                    'brand': 'yataxi',
                    'fund_id': 'sample_fund_id',
                    'mod': 100,
                    'created_at': '2022-02-20T10:00:00+00:00',
                    'updated_at': '2022-02-20T10:00:00+00:00',
                    'locale': 'ru',
                },
            ],
        },
    )
    expected_cache['100'].update(
        {
            'yataxi': {
                'created_at': '2022-02-01T10:00:00+00:00',
                'mod': 66,
                'sub_src': 'go_android',
            },
            'lavka': {
                'created_at': '2022-02-19T10:00:00+00:00',
                'mod': 90,
                'sub_src': 'market_mobile',
            },
        },
    )
    expected_stats.add('', 'yataxi', -1)
    expected_stats.add('go_android', 'yataxi', 1)
    expected_stats.add('market_mobile', 'lavka', 1)

    expected_cache['102'].update(
        {
            'lavka': {
                'created_at': '2022-02-11T10:00:00+00:00',
                'hidden_at': '2022-02-12T09:59:59+00:00',
                'mod': 90,
                'sub_src': '',
            },
        },
    )

    if full_update:
        expected_cache['103'].update(
            {
                'eats': {
                    'mod': 90,
                    'created_at': '2022-02-11T10:00:00+00:00',
                    'sub_src': 'market_desktop',
                },
            },
        )
        expected_stats.add('market_desktop', 'eats', 1)
        expected_stats.participants += 1

    expected_cache['104'].update(
        {
            'yataxi': {
                'mod': 100,
                'created_at': '2022-02-20T10:00:00+00:00',
                'sub_src': '',
            },
        },
    )
    expected_stats.add('', 'yataxi', 1)
    expected_stats.participants += 1

    await taxi_persey_core.invalidate_caches(
        clean_update=full_update, cache_names=['ride-subs-cache'],
    )
    result = await persey_core_internal.call('GetEntireRideSubsCache')
    assert result == expected_cache
    result = await persey_core_internal.call('GetRideSubsCacheStats')
    assert result == expected_stats.get_stats()
    result = await persey_core_internal.call('GetRideSubsCacheMaxUpdatedAt')
    assert result == '2022-02-20T10:00:00+00:00'

    # Replace existing subs:
    cursor.execute(
        'DELETE FROM persey_payments.ride_subs '
        'WHERE id IN (90000, 90030, 90080)',
    )
    utils.fill_db(
        cursor,
        {
            'persey_payments.ride_subs': [
                {
                    'id': 90000,
                    'yandex_uid': '100',
                    'brand': 'yataxi',
                    'fund_id': 'sample_fund_id',
                    'mod': 20,
                    'created_at': '2022-02-01T10:00:00+00:00',
                    'updated_at': '2022-02-20T09:59:59+00:00',
                    'hidden_at': '2022-02-20T09:59:59+00:00',
                    'locale': 'ru',
                    'subscription_source': 'new_source',
                },
                {
                    'id': 90030,
                    'yandex_uid': '101',
                    'brand': 'market',
                    'fund_id': 'sample_fund_id',
                    'mod': 40,
                    'created_at': '2022-02-09T10:00:00+00:00',
                    'updated_at': '2022-02-20T09:59:55+00:00',
                    'hidden_at': '2022-02-20T09:59:55+00:00',
                    'locale': 'ru',
                },
                {
                    'id': 90081,
                    'yandex_uid': '104',
                    'brand': 'yataxi',
                    'fund_id': 'sample_fund_id',
                    'mod': 300,
                    'created_at': '2022-02-25T10:00:00+00:00',
                    'updated_at': '2022-02-25T10:00:00+00:00',
                    'locale': 'ru',
                },
            ],
        },
    )
    if proper_hidden:
        utils.fill_db(
            cursor,
            {
                'persey_payments.ride_subs': [
                    {
                        'id': 90080,
                        'yandex_uid': '104',
                        'brand': 'yataxi',
                        'fund_id': 'sample_fund_id',
                        'mod': 200,
                        'created_at': '2022-02-20T10:00:00+00:00',
                        'updated_at': '2022-02-21T10:00:00+00:00',
                        'hidden_at': '2022-02-21T10:00:00+00:00',
                        'locale': 'ru',
                    },
                ],
            },
        )
    expected_cache['100']['yataxi'].update(
        {
            'created_at': '2022-02-01T10:00:00+00:00',
            'hidden_at': '2022-02-20T09:59:59+00:00',
            'mod': 20,
            'sub_src': 'new_source',
        },
    )
    expected_stats.add('go_android', 'yataxi', -1)

    if full_update:
        expected_cache['101']['market'].update(
            {
                'created_at': '2022-02-09T10:00:00+00:00',
                'hidden_at': '2022-02-20T09:59:55+00:00',
                'mod': 40,
                'sub_src': '',
            },
        )
        expected_stats.add('go_android', 'market', -1)
        expected_stats.participants -= 1

    expected_cache['104']['yataxi'].update(
        {'created_at': '2022-02-25T10:00:00+00:00', 'mod': 300, 'sub_src': ''},
    )

    await taxi_persey_core.invalidate_caches(
        clean_update=full_update, cache_names=['ride-subs-cache'],
    )
    result = await persey_core_internal.call('GetEntireRideSubsCache')
    assert result == expected_cache
    result = await persey_core_internal.call('GetRideSubsCacheStats')
    assert result == expected_stats.get_stats()
    result = await persey_core_internal.call('GetRideSubsCacheMaxUpdatedAt')
    assert result == '2022-02-25T10:00:00+00:00'


async def test_ride_subs_cache_dump_empty(
        taxi_persey_core, persey_core_internal,
):
    await taxi_persey_core.write_cache_dumps(names=['ride-subs-cache'])
    await taxi_persey_core.read_cache_dumps(names=['ride-subs-cache'])
    result = await persey_core_internal.call('GetEntireRideSubsCache')
    assert result == {}
    result = await persey_core_internal.call('GetRideSubsCacheMaxUpdatedAt')
    assert result == '1970-01-01T00:00:00+00:00'


async def test_ride_subs_cache_dump(
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
            'persey_payments.ride_subs': [
                {
                    'id': 90000,
                    'yandex_uid': '100',
                    'brand': 'yataxi',
                    'fund_id': 'sample_fund_id',
                    'mod': 10,
                    'created_at': '2022-02-01T10:00:00+00:00',
                    'updated_at': '2022-02-01T10:00:00+00:00',
                    'locale': 'ru',
                    'subscription_source': 'src1',
                },
                {
                    'id': 90010,
                    'yandex_uid': '100',
                    'brand': 'eats',
                    'fund_id': 'sample_fund_id',
                    'mod': 20,
                    'created_at': '2022-02-09T10:00:00+00:00',
                    'updated_at': '2022-02-09T11:00:00+00:00',
                    'hidden_at': '2022-02-09T11:00:00+00:00',
                    'locale': 'ru',
                    'subscription_source': 'src2',
                },
                {
                    'id': 90020,
                    'yandex_uid': '100',
                    'brand': 'eats',
                    'fund_id': 'sample_fund_id',
                    'mod': 20,
                    'created_at': '2022-02-10T10:00:00+00:00',
                    'updated_at': '2022-02-12T13:00:00+03:00',
                    'locale': 'ru',
                },
                {
                    'id': 90030,
                    'yandex_uid': '101',
                    'brand': 'market',
                    'fund_id': 'sample_fund_id',
                    'mod': 30,
                    'created_at': '2022-02-09T10:00:00+00:00',
                    'updated_at': '2022-02-11T10:00:00+00:00',
                    'locale': 'ru',
                },
                {
                    'id': 90040,
                    'yandex_uid': '102',
                    'brand': 'market',
                    'fund_id': 'sample_fund_id',
                    'mod': 50,
                    'created_at': '2022-02-11T10:00:00+00:00',
                    'updated_at': '2022-02-11T11:00:00+00:00',
                    'hidden_at': '2022-02-11T11:00:00+00:00',
                    'locale': 'ru',
                    'subscription_source': 'src3',
                },
            ],
        },
    )
    await taxi_persey_core.invalidate_caches(
        clean_update=True, cache_names=['ride-subs-cache'],
    )
    await taxi_persey_core.write_cache_dumps(names=['ride-subs-cache'])
    cursor.execute('DELETE FROM persey_payments.ride_subs')
    await taxi_persey_core.invalidate_caches(
        clean_update=True, cache_names=['ride-subs-cache'],
    )
    result = await persey_core_internal.call('GetEntireRideSubsCache')
    assert result == {}
    await taxi_persey_core.read_cache_dumps(names=['ride-subs-cache'])
    result = await persey_core_internal.call('GetEntireRideSubsCache')
    assert result == {
        '100': {
            'yataxi': {
                'created_at': '2022-02-01T10:00:00+00:00',
                'mod': 10,
                'sub_src': 'src1',
            },
            'eats': {
                'created_at': '2022-02-10T10:00:00+00:00',
                'mod': 20,
                'sub_src': '',
            },
        },
        '101': {
            'market': {
                'created_at': '2022-02-09T10:00:00+00:00',
                'mod': 30,
                'sub_src': '',
            },
        },
        '102': {
            'market': {
                'created_at': '2022-02-11T10:00:00+00:00',
                'hidden_at': '2022-02-11T11:00:00+00:00',
                'mod': 50,
                'sub_src': 'src3',
            },
        },
    }
    expected_stats = _RideSubsStatsHelper()
    expected_stats.add('src1', 'yataxi', 1)
    expected_stats.add('', 'eats', 1)
    expected_stats.add('', 'market', 1)
    expected_stats.participants = 2
    result = await persey_core_internal.call('GetRideSubsCacheStats')
    assert result == expected_stats.get_stats()
    result = await persey_core_internal.call('GetRideSubsCacheMaxUpdatedAt')
    assert result == '2022-02-12T10:00:00+00:00'
    result = await taxi_persey_core_monitor.get_metric(
        'ride-subs-cache-metrics',
    )
    assert result == {
        'participants': 2,
        'stats': {
            '$meta': {'solomon_children_labels': 'sub_src'},
            '__any__': {
                '$meta': {'solomon_children_labels': 'brand'},
                '__any__': {'count': 3},
                'eats': {'count': 1},
                'market': {'count': 1},
                'yataxi': {'count': 1},
            },
            '__null__': {
                '$meta': {'solomon_children_labels': 'brand'},
                '__any__': {'count': 2},
                'eats': {'count': 1},
                'market': {'count': 1},
                'yataxi': {'count': 0},
            },
            'src1': {
                '$meta': {'solomon_children_labels': 'brand'},
                '__any__': {'count': 1},
                'eats': {'count': 0},
                'market': {'count': 0},
                'yataxi': {'count': 1},
            },
            'src2': {
                '$meta': {'solomon_children_labels': 'brand'},
                '__any__': {'count': 0},
                'eats': {'count': 0},
                'market': {'count': 0},
                'yataxi': {'count': 0},
            },
        },
    }
