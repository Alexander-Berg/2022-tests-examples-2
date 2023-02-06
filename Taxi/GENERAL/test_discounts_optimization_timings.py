import json
import time

import numpy as np
from scipy.optimize import differential_evolution

from ctaxi_pyml.discounts import optimization as cxx


if __name__ == '__main__':
    random_gen = np.random.RandomState(49)
    size = 1000000
    true_weights = random_gen.uniform(size=50)
    features_values = random_gen.uniform(size=(size, len(true_weights)))
    pure_trips_values = random_gen.normal(loc=5, scale=1, size=size)
    is_experiment_values = random_gen.uniform(size=size) < 0.25
    effect_values = (
        is_experiment_values
        * np.dot(features_values, true_weights)
        / np.dot(true_weights, true_weights)
    )
    trips_values = pure_trips_values * (1 + effect_values)
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

    def py_func(weights):
        result = 0
        order = np.argsort(np.dot(features_values, weights))[::-1]
        trips = trips_values[order]
        is_exp = is_experiment_values[order]
        total_len = len(order)
        trips_experiment = 0
        size_experiment = 0
        trips_control = 0
        size_control = 0
        for i, q in enumerate(np.arange(0.1, 1.1, 0.1)):
            start = int(total_len * (q - 0.1))
            end = int(total_len * q)

            is_exp_slice = is_exp[start:end]
            trips_slice = trips[start:end]

            size_experiment += is_exp_slice.sum()
            size_control += (~is_exp_slice).sum()
            trips_experiment += trips_slice[is_exp_slice].sum()
            trips_control += trips_slice[~is_exp_slice].sum()

            mean_control = trips_control / size_control
            mean_experiment = trips_experiment / size_experiment
            relative_diff = (mean_experiment - mean_control) / mean_control

            result += relative_diff * 0.97 ** i

        return -result

    config_dict = dict(
        thresholds=[
            {'percentile': x, 'weight': 0.97 ** i}
            for i, x in enumerate(np.arange(0.1, 1.1, 0.1))
        ],
        l2_coef=0,
    )
    config = cxx.FunctionV1Config.from_json_string(json.dumps(config_dict))
    factory = cxx.TripsRelativeIncreaseAggregatorFactory()

    # create cxx func
    cxx_func = cxx.FunctionV1(config, factory, dataset)

    print(py_func(true_weights))
    print(cxx_func(true_weights))
    for _ in range(5):
        print(cxx_func(random_gen.uniform(size=len(true_weights))))

    # constraint and bounds for the optimization
    bounds = [[-1, 1]] * len(true_weights)

    # check correctness of optimization
    start = time.time()
    py_solution = differential_evolution(
        py_func, bounds=bounds, seed=42, tol=0.001,
    )
    print(f'py_solution: {time.time() - start}')
    print(py_solution)
    print()

    start = time.time()
    cxx_solution = differential_evolution(
        cxx_func, bounds=bounds, seed=42, tol=0.001,
    )
    print(f'cxx_solution: {time.time() - start}')
    print(cxx_solution)
    print()

    for n_jobs in [1, 2, 4, 8, 12, 16, 32]:
        start = time.time()
        pool = cxx.EvaluationPool(n_jobs)
        cxx_pool_solution = differential_evolution(
            cxx_func, bounds=bounds, seed=42, workers=pool, tol=0.001,
        )
        print(f'cxx_pool_{n_jobs}_solution: {time.time() - start}')
        print(cxx_pool_solution)
        print()

    for n_jobs in [2, 4, 8, 12, 16, 32]:
        start = time.time()
        py_pool_solution = differential_evolution(
            py_func, bounds=bounds, seed=42, workers=n_jobs, tol=0.001,
        )
        print(f'py_pool_{n_jobs}_solution: {time.time() - start}')
        print(py_pool_solution)
        print()


