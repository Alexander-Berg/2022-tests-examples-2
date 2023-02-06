import json

import numpy as np
from scipy.optimize import differential_evolution

from ctaxi_pyml.discounts import optimization as cxx

from scipy.optimize._differentialevolution import DifferentialEvolutionSolver


__old_init__ = DifferentialEvolutionSolver.__init__


def __new_init__(self, *args, **kwargs):
    __old_init__(self, *args, **kwargs)

    _origin_callback = self.callback

    def _wrapped_callback(xk, convergence):
        return _origin_callback(self, xk, convergence)

    self.callback = _wrapped_callback


DifferentialEvolutionSolver.__init__ = __new_init__


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

    train_dataset = cxx.Dataset(len(true_weights))
    test_dataset = cxx.Dataset(len(true_weights))
    test_dataset.reserve(size)
    train_dataset.reserve(size)

    for features, trips, discount, is_experiment in zip(
            features_values,
            trips_values,
            discount_values,
            is_experiment_values,
    ):
        if random_gen.uniform() < 0.05:
            dataset = train_dataset
        else:
            dataset = test_dataset
        dataset.add_item(
            item=cxx.Item(
                is_experiment=is_experiment, trips=trips, discount=discount,
            ),
            features=features,
        )

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
    original_train_cxx_func = cxx.FunctionV1(config, factory, train_dataset)
    train_cxx_func = cxx.FunctionV1(config, factory, train_dataset)
    test_cxx_func = cxx.FunctionV1(config, factory, test_dataset)

    for _ in range(5):
        print(train_cxx_func(random_gen.uniform(size=len(true_weights))))
        print(test_cxx_func(random_gen.uniform(size=len(true_weights))))
        print()

    pool = cxx.EvaluationPool(8)
    bounds = [[-1, 1]] * len(true_weights)

    iter_num = 0

    def callback(solver, xk, convergence):
        global iter_num
        iter_num += 1
        if iter_num % 50 == 0:
            print(f'Iteration {iter_num}')
            print(original_train_cxx_func(xk))
            print(train_cxx_func(xk))
            print(test_cxx_func(xk))
            print()

        if iter_num % 10 == 0:
            train_cxx_func.set_seed(iter_num)
            solver.population_energies = solver._calculate_population_energies(
                solver.population,
            )

    cxx_pool_solution = differential_evolution(
        train_cxx_func,
        bounds=bounds,
        seed=42,
        workers=pool,
        tol=0.001,
        callback=callback,
        maxiter=500,
    )
    print(cxx_pool_solution)
    print(original_train_cxx_func(cxx_pool_solution.x))
    print(train_cxx_func(cxx_pool_solution.x))
    print(test_cxx_func(cxx_pool_solution.x))
