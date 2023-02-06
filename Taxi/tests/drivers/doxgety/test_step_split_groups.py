import random
import uuid

from typing import Any, Dict


import numpy as np
import pandas as pd
import scipy.stats as sps


from projects.drivers.doxgety.objects import GroupsSplitter


random_py = random.Random(1337)
random_np = np.random.RandomState(80085)


def create_test_driver(tariff_zone: str, orders_kpi: int) -> Dict[str, Any]:
    uuid_seed = random_py.getrandbits(128)
    return {
        'unique_driver_id': str(uuid.UUID(int=uuid_seed)),
        'tariff_zone': tariff_zone,
        'orders_kpi': orders_kpi,
        'quantiles': {'0.98': orders_kpi},
        'goal_params': {
            'goal_type': 'driver_target',
            'quantiles_column': 'quantiles',
            'difficulty': '0.98',
        },
        'bonus_sum': orders_kpi * 100,
        'aa_stat': random_np.standard_cauchy(),
        'aa_stat_2': random_np.standard_cauchy(),
        'currency_rate': 1.0,
    }


TEST_DRIVERS = []
for i in range(1, 11):
    TEST_DRIVERS += [create_test_driver('moscow', i) for _ in range(100)]
    TEST_DRIVERS += [create_test_driver('spb', i) for _ in range(100)]
TEST_DRIVERS = pd.DataFrame(TEST_DRIVERS)


DEFAULT_SPLIT_PARAMS = {
    'split_type': 'hash',
    'exp_frac_params': {
        'limit': 'exp_frac_by_tariff_zone',
        'exp_frac_by_tariff_zone': {'moscow': 0.8, 'spb': 0.5},
    },
}


def test_different_salts_produce_different_splits():
    splitter1 = GroupsSplitter({'split_params': DEFAULT_SPLIT_PARAMS})
    splitter2 = GroupsSplitter(
        {
            'split_params': {
                'split_type': 'hash',
                'salt': 'custom_salt',
                'exp_frac_params': {
                    'limit': 'exp_frac_by_tariff_zone',
                    'exp_frac_by_tariff_zone': {'moscow': 0.8, 'spb': 0.5},
                },
            },
        },
    )

    groups1 = splitter1.split_groups(TEST_DRIVERS)
    groups2 = splitter2.split_groups(TEST_DRIVERS)
    drivers_shuffled = TEST_DRIVERS.sample(frac=1)
    groups3 = splitter1.split_groups(drivers_shuffled)

    exp_udids1 = sorted(groups1[groups1['exp']]['unique_driver_id'])
    exp_udids2 = sorted(groups2[groups2['exp']]['unique_driver_id'])
    exp_udids3 = sorted(groups3[groups3['exp']]['unique_driver_id'])

    assert exp_udids1 != exp_udids2
    assert exp_udids1 == exp_udids3


def test_rotation_swaps_groups():
    splitter1 = GroupsSplitter(
        {
            'split_params': {
                'split_type': 'hash',
                'exp_frac_params': {
                    'limit': 'exp_frac_by_tariff_zone',
                    'exp_frac_by_tariff_zone': {'moscow': 0.5, 'spb': 0.5},
                },
            },
        },
    )
    splitter2 = GroupsSplitter(
        {
            'split_params': {
                'split_type': 'hash',
                'rotation_frac': 0.5,
                'exp_frac_params': {
                    'limit': 'exp_frac_by_tariff_zone',
                    'exp_frac_by_tariff_zone': {'moscow': 0.5, 'spb': 0.5},
                },
            },
        },
    )

    groups1 = splitter1.split_groups(TEST_DRIVERS)
    groups2 = splitter2.split_groups(TEST_DRIVERS)

    exp_udids1 = set(groups1[groups1['exp']]['unique_driver_id'])
    exp_udids2 = set(groups2[groups2['exp']]['unique_driver_id'])
    control_udids1 = set(groups1[~groups1['exp']]['unique_driver_id'])
    control_udids2 = set(groups2[~groups2['exp']]['unique_driver_id'])

    assert exp_udids1 == control_udids2
    assert exp_udids2 == control_udids1


def test_aa_control_produces_large_pvalues_in_aa():
    min_pvalue = 0.1
    splitter1 = GroupsSplitter(
        {
            'split_params': {
                'split_type': 'control_aa',
                'min_pvalue': min_pvalue,
                'aa_statistics': ['aa_stat'],
                'exp_frac_params': {
                    'limit': 'exp_frac_by_tariff_zone',
                    'exp_frac_by_tariff_zone': {'moscow': 0.8, 'spb': 0.5},
                },
            },
        },
    )
    splitter2 = GroupsSplitter({'split_params': DEFAULT_SPLIT_PARAMS})

    groups1 = splitter1.split_groups(TEST_DRIVERS)
    groups2 = splitter2.split_groups(TEST_DRIVERS)

    assert (
        sps.ttest_ind(
            groups1[groups1['exp']]['aa_stat'],
            groups1[~groups1['exp']]['aa_stat'],
        ).pvalue
        >= min_pvalue
    )
    assert (
        sps.ttest_ind(
            groups2[groups2['exp']]['aa_stat'],
            groups2[~groups2['exp']]['aa_stat'],
        ).pvalue
        < min_pvalue
    )


def test_exp_frac_by_tariff_zone_is_close_to_given():
    exp_frac_by_tariff_zone = DEFAULT_SPLIT_PARAMS['exp_frac_params'][
        'exp_frac_by_tariff_zone'
    ]
    splitter = GroupsSplitter({'split_params': DEFAULT_SPLIT_PARAMS})

    groups = splitter.split_groups(TEST_DRIVERS)
    for tz, exp_frac in exp_frac_by_tariff_zone.items():
        tz_groups = groups[groups['tariff_zone'] == tz]
        assert np.isclose(tz_groups['exp'].mean(), exp_frac, atol=0.02)
        assert (tz_groups['probability'].values == exp_frac).all()


def test_budget_is_close_to_given():
    max_budget = 100000
    expected_conversion = 0.1
    splitter = GroupsSplitter(
        {
            'split_params': {
                'split_type': 'hash',
                'exp_frac_params': {
                    'limit': 'budget',
                    'max_budget': max_budget,
                    'expected_conversion': expected_conversion,
                },
            },
        },
    )

    groups = splitter.split_groups(TEST_DRIVERS)
    budget = groups[groups['exp']]['bonus_sum'].sum() * expected_conversion
    assert np.isclose(budget, max_budget, rtol=0.05)
    assert np.allclose(groups['probability'], groups['exp'].mean(), atol=0.02)


def test_filters_remove_drivers():
    splitter1 = GroupsSplitter(
        {
            'split_params': DEFAULT_SPLIT_PARAMS,
            'segment_params': {
                'remove_if_a_less_than_b_filters': [{'a': 'aa_stat', 'b': 0}],
            },
        },
    )
    splitter2 = GroupsSplitter(
        {
            'split_params': DEFAULT_SPLIT_PARAMS,
            'segment_params': {
                'remove_if_a_less_than_b_filters': [{'a': 0, 'b': 'aa_stat'}],
            },
        },
    )
    splitter3 = GroupsSplitter(
        {
            'split_params': DEFAULT_SPLIT_PARAMS,
            'segment_params': {
                'remove_if_a_less_than_b_filters': [
                    {'a': 'aa_stat', 'b': 'aa_stat_2'},
                ],
            },
        },
    )

    groups = splitter1.split_groups(TEST_DRIVERS)
    assert (groups['aa_stat'] >= 0).all()
    groups = splitter2.split_groups(TEST_DRIVERS)
    assert (groups['aa_stat'] <= 0).all()
    groups = splitter3.split_groups(TEST_DRIVERS)
    assert (groups['aa_stat'] >= groups['aa_stat_2']).all()


def test_groups_do_not_have_drivers_with_low_score():
    splitter = GroupsSplitter(
        {
            'split_params': DEFAULT_SPLIT_PARAMS,
            'segment_params': {
                'scoring_params': {
                    'type': 'score_from_column',
                    'score_column': 'aa_stat',
                    'more_is_better': True,
                    'top_size_by_tariff_zone': {'moscow': 0.5, 'spb': 0.5},
                },
            },
        },
    )

    groups = splitter.split_groups(TEST_DRIVERS)
    assert (groups['score'] == -groups['aa_stat']).all()
    for tz in 'moscow', 'spb':
        tz_groups = groups[groups['tariff_zone'] == tz]
        tz_drivers = TEST_DRIVERS[TEST_DRIVERS['tariff_zone'] == tz]
        np.isclose(tz_groups['aa_stat'].min(), tz_drivers['aa_stat'].median())


def test_groups_do_not_have_drivers_with_high_uplift_cost():
    splitter = GroupsSplitter(
        {
            'split_params': DEFAULT_SPLIT_PARAMS,
            'segment_params': {
                'scoring_params': {
                    'type': 'cost_of_extra_trip',
                    'orders_uplift_column': 'aa_stat',
                    'payment_probability_column': 'aa_stat_2',
                    'top_size_by_tariff_zone': {'moscow': 0.5, 'spb': 0.5},
                },
            },
        },
    )

    drivers = TEST_DRIVERS.copy()
    drivers['cost_of_extra_trip'] = -drivers['aa_stat'] / (
        drivers['aa_stat_2'] * (5 + drivers['orders_kpi'])
    )

    groups = splitter.split_groups(drivers)
    assert (groups['score'] == groups['cost_of_extra_trip']).all()
    for tz in 'moscow', 'spb':
        tz_groups = groups[groups['tariff_zone'] == tz]
        tz_drivers = drivers[drivers['tariff_zone'] == tz]
        np.isclose(
            tz_groups['aa_stat'].min(),
            tz_drivers['cost_of_extra_trip'].median(),
        )


if __name__ == '__main__':
    test_different_salts_produce_different_splits()
    test_rotation_swaps_groups()
    test_aa_control_produces_large_pvalues_in_aa()
    test_exp_frac_by_tariff_zone_is_close_to_given()
    test_budget_is_close_to_given()
    test_filters_remove_drivers()
    test_groups_do_not_have_drivers_with_low_score()
    test_groups_do_not_have_drivers_with_high_uplift_cost()
