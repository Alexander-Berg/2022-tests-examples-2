import json

import numpy as np
from scipy.optimize import differential_evolution
from scipy.optimize import NonlinearConstraint

from ctaxi_pyml.discounts import optimization as cxx


EPS = 1e-5
L2_COEF = 0.1


def test_function_v1():
    random_gen = np.random.RandomState(49)
    size = 10000
    true_weights = random_gen.uniform(size=5)
    features_values = random_gen.uniform(size=(size, len(true_weights)))
    pure_trips_values = random_gen.normal(loc=5, scale=1, size=size)
    is_experiment_values = random_gen.uniform(size=size) < 0.25
    effect_values = is_experiment_values * np.dot(
        features_values, true_weights,
    )
    trips_values = pure_trips_values + effect_values
    discount_values = (
        is_experiment_values
        * trips_values
        * random_gen.normal(loc=1, scale=0.1, size=size)
    )

    dataset = cxx.Dataset(len(true_weights))
    dataset.reserve(size)
    for features, trips, discount, is_experiment in zip(
            features_values,
            trips_values,
            discount_values,
            is_experiment_values,
    ):
        dataset.add_item(
            item=cxx.Item(
                is_experiment=is_experiment, trips=trips, discount=discount,
            ),
            features=features,
        )

    # implement relative trips increase of top 10 % of users
    def py_func(weights):
        indices = np.argsort(np.dot(features_values, weights))[-(size // 10) :]
        trips = trips_values[indices]
        is_exp = is_experiment_values[indices]
        return L2_COEF * abs((weights ** 2).sum() - 1) - (
            (trips[is_exp].mean() - trips[~is_exp].mean())
            / trips[~is_exp].mean()
        )

    # config and factory to relative trips increase of top 10 % of users
    config_dict = dict(
        thresholds=[{'percentile': 0.1, 'weight': 1}], l2_coef=L2_COEF,
    )
    config = cxx.FunctionV1Config.from_json_string(json.dumps(config_dict))
    factory = cxx.TripsRelativeIncreaseAggregatorFactory()

    # create cxx func
    cxx_func = cxx.FunctionV1(config, factory, dataset)

    # check correctness of the func
    for _ in range(100):
        weights = random_gen.uniform(size=len(true_weights))
        assert abs(py_func(weights) - cxx_func(weights)) < EPS

    # constraint and bounds for the optimization
    constraint = NonlinearConstraint(lambda x: np.sum(np.abs(x)), 0.9, 1.1)
    bounds = [[-1, 1]] * len(true_weights)

    # check correctness of optimization
    py_solution = differential_evolution(
        py_func, bounds=bounds, seed=42, constraints=constraint,
    )
    cxx_solution = differential_evolution(
        cxx_func, bounds=bounds, seed=42, constraints=constraint,
    )

    assert np.abs(py_solution.fun - cxx_solution.fun).sum() < EPS
    assert np.abs(cxx_func(py_solution.x) - cxx_func(cxx_solution.x)) < EPS
    assert np.abs(py_func(py_solution.x) - py_func(cxx_solution.x)) < EPS

    cxx_pool_solution = differential_evolution(
        cxx_func,
        bounds=bounds,
        seed=42,
        constraints=constraint,
        workers=cxx.EvaluationPool(4),
    )

    # check that we found the solution
    # that is not much worse than the solution without pool
    assert -cxx_pool_solution.fun >= -0.95 * cxx_solution.fun
