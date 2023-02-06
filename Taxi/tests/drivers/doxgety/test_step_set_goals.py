import numpy as np
import pandas as pd


from projects.drivers.doxgety.objects import calc_bonuses, calc_goals
from projects.drivers.doxgety.objects.bonuses import (
    PerTripBonusExtractor,
    OldFormulaBonusExtractor,
)
from projects.drivers.doxgety.objects.goals import (
    MSEQsGoalExtractor,
    DriverTargetGoalExtractor,
    adjust_difficulty_to_aa,
)


random_np = np.random.RandomState(80085)


TEST_DRIVER_STATS = (
    pd.DataFrame(
        [
            # обычный водитель
            {
                'orders_uplift': 7.0,
                'q97': 69.0,
                'mse': 42.069,
                'quantiles': [['0.97', 69.0], ['0.98', 69.69]],
                'orders_last_week': 42,
                'currency_rate': 1,
                'orders_tariff_zone': 14214361,
                'gmv_tariff_zone': 7724288575.784416,
                'duration_days': 7,
            },
            # обычный водитель из Ташкента
            {
                'orders_uplift': 6.0,
                'q97': 69.0,
                'mse': 42.069,
                'quantiles': [['0.97', 69.0], ['0.98', 69.69]],
                'orders_last_week': 42,
                'currency_rate': 0.006949,
                'orders_tariff_zone': 4513153,
                'gmv_tariff_zone': 70458885494.5553,
                'duration_days': 7,
            },
            # нет предсказаний driver target
            {
                'orders_uplift': 5.0,
                'q97': 69.0,
                'mse': 42.069,
                'orders_last_week': 42,
                'currency_rate': 1,
                'orders_tariff_zone': 14214361,
                'gmv_tariff_zone': 7724288575.784416,
                'duration_days': 7,
            },
            # нет нужной квантили driver target
            {
                'orders_uplift': 4.0,
                'q97': 69.0,
                'quantiles': [['0.98', 69.69]],
                'mse': 42.069,
                'orders_last_week': 42,
                'currency_rate': 1,
                'orders_tariff_zone': 14214361,
                'gmv_tariff_zone': 7724288575.784416,
                'duration_days': 7,
            },
            # нет предсказаний mse_qs
            {
                'orders_uplift': 3.0,
                'quantiles': [['0.97', 69.0], ['0.98', 69.69]],
                'orders_last_week': 42,
                'currency_rate': 1,
                'orders_tariff_zone': 14214361,
                'gmv_tariff_zone': 7724288575.784416,
                'duration_days': 7,
            },
            # очень активный водитель
            {
                'orders_uplift': 2.0,
                'q97': 133.7,
                'mse': 69.69,
                'quantiles': [['0.97', 133.7], ['0.98', 420.0]],
                'orders_last_week': 69,
                'currency_rate': 1,
                'orders_tariff_zone': 14214361,
                'gmv_tariff_zone': 7724288575.784416,
                'duration_days': 7,
            },
            # неактивный водитель
            {
                'orders_uplift': 1.0,
                'q97': 1.337,
                'mse': 0.420,
                'quantiles': [['0.97', 1.337], ['0.98', 4.20]],
                'orders_last_week': 0,
                'currency_rate': 1,
                'orders_tariff_zone': 14214361,
                'gmv_tariff_zone': 7724288575.784416,
                'duration_days': 7,
            },
        ],
    ).replace([np.nan], [None])
)  # найл заменяет пропуски на None, а не на nan


MSE_QS_GOAL_EXTRACTOR = MSEQsGoalExtractor('q97', 'mse')
DRIVER_TARGET_GOAL_EXTRACTOR = DriverTargetGoalExtractor(
    'orders_last_week', 'quantiles', '0.97',
)


PER_TRIP_BONUS_EXTRACTOR = PerTripBonusExtractor(70.0)
OLD_FORMULA_BONUS_EXTRACTOR = OldFormulaBonusExtractor(
    'orders_tariff_zone', 'gmv_tariff_zone', 0.8,
)


def test_clip_goals():
    goal_params = {'min_goal': 30, 'max_goal': 100}
    goals = calc_goals(TEST_DRIVER_STATS, MSE_QS_GOAL_EXTRACTOR, goal_params)
    goals = goals[0]
    assert (goals == np.clip(goals, 10, 100)).all()


def test_adjust_difficulty_to_aa():
    stats = pd.DataFrame(
        {'aa': random_np.rand(1000), 'goals': random_np.rand(1000)},
    )
    assert (stats['goals'] > stats['aa']).mean() < 0.95
    stats['goals'] = adjust_difficulty_to_aa(
        stats['goals'].values, stats['aa'], 0.95, 0.0, 100.0, 100,
    )
    assert (stats['goals'] > stats['aa']).mean() >= 0.95


def test_mse_qs_goals():
    goal_params = {'min_goal': 1}
    goals = calc_goals(TEST_DRIVER_STATS, MSE_QS_GOAL_EXTRACTOR, goal_params)
    goals = goals[0]
    assert goals.tolist() == [69, 69, 69, 69, 1, 134, 1]


def test_driver_target_goals():
    goal_params = {'min_goal': 1}
    goals = calc_goals(
        TEST_DRIVER_STATS, DRIVER_TARGET_GOAL_EXTRACTOR, goal_params,
    )
    goals = goals[0]
    assert goals.tolist() == [69, 69, 47, 47, 69, 134, 1]


def test_capacity_plus_goals():
    goal_params = {
        'min_goal': 1,
        'capacity_plus_params': {
            'goal_coef': 0.8,
            'drivers_frac': 0.5,
            'min_quantile_column': 'orders_last_week',
            'orders_uplift_column': 'orders_uplift',
        },
    }
    goals = calc_goals(
        TEST_DRIVER_STATS, DRIVER_TARGET_GOAL_EXTRACTOR, goal_params,
    )
    goals = goals[0]
    assert goals.tolist() == [69, 69, 47, 47, 55, 107, 1]


def test_per_trip_bonus():
    goal_params = {'min_goal': 1}
    stats = TEST_DRIVER_STATS.copy()
    goals = calc_goals(TEST_DRIVER_STATS, MSE_QS_GOAL_EXTRACTOR, goal_params)
    goals = goals[0]
    stats['orders_kpi'] = goals
    bonuses = calc_bonuses(stats, PER_TRIP_BONUS_EXTRACTOR)
    assert bonuses.tolist() == [4800, 695064, 4800, 4800, 100, 9400, 100]


def test_old_formula_bonus():
    goal_params = {'min_goal': 1}
    stats = TEST_DRIVER_STATS.copy()
    goals = calc_goals(TEST_DRIVER_STATS, MSE_QS_GOAL_EXTRACTOR, goal_params)
    goals = goals[0]
    stats['orders_kpi'] = goals
    bonuses = calc_bonuses(stats, OLD_FORMULA_BONUS_EXTRACTOR)
    assert bonuses.tolist() == [6000, 335012, 6000, 6000, 400, 7800, 400]


if __name__ == '__main__':
    test_clip_goals()
    test_adjust_difficulty_to_aa()
    test_mse_qs_goals()
    test_driver_target_goals()
    test_capacity_plus_goals()
    test_per_trip_bonus()
    test_old_formula_bonus()
