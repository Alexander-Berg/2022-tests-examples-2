import numpy as np

from nile.api.v1 import Record, clusters
from nile.api.v1.local import StreamSource, ListSink

from projects.autoorder.offline_exps.get_demand_by_coeffs import (
    coeffs_reducer,
    demand_mapper,
    osa_reducer,
)


def test_osa_reducer():
    test_input = [
        Record(key=1, n_units_of_sku=2, residuals=8, hour_local=7),
        Record(key=1, n_units_of_sku=0, residuals=6, hour_local=8),
        Record(key=1, n_units_of_sku=0, residuals=6, hour_local=9),
        Record(key=1, n_units_of_sku=1, residuals=6, hour_local=10),
        Record(key=1, n_units_of_sku=0, residuals=5, hour_local=11),
        Record(key=1, n_units_of_sku=0, residuals=5, hour_local=12),
        Record(key=1, n_units_of_sku=0, residuals=5, hour_local=13),
        Record(key=1, n_units_of_sku=4, residuals=5, hour_local=14),
        Record(key=1, n_units_of_sku=0, residuals=1, hour_local=15),
        Record(key=1, n_units_of_sku=1, residuals=1, hour_local=16),
        Record(key=1, n_units_of_sku=0, residuals=0, hour_local=17),
        Record(key=1, n_units_of_sku=0, residuals=0, hour_local=18),
        Record(key=1, n_units_of_sku=0, residuals=0, hour_local=19),
        Record(key=1, n_units_of_sku=0, residuals=0, hour_local=20),
        Record(key=1, n_units_of_sku=0, residuals=0, hour_local=21),
    ]

    expected_output = [
        Record(
            key=1,
            unknown_residuals=False,
            purchases_sum=8,
            instock={
                '10': (1.0, 0.0),
                '20': (1.0, 0.0),
                '30': (1.0, 0.0),
                '40': (1.0, 0.0),
                '50': (1.0, 0.125),
                '60': (0.9, 0.3),
                '70': (0.8181818181818182, 0.36363636363636365),
                '80': (0.6923076923076923, 0.46153846153846156),
                '90': (0.6428571428571429, 0.5),
            },
            purchases={
                '10': (0, 0),
                '20': (1, 0),
                '30': (1, 0),
                '40': (1, 0),
                '50': (5, 1),
                '60': (6, 5),
                '70': (6, 5),
                '80': (6, 5),
                '90': (6, 6),
            },
            full_instock=False,
            instock_prc=0.5625,
        ),
    ]
    output = []

    job = clusters.MockCluster().job()

    job.table('').label('input').groupby('key').reduce(
        osa_reducer(instock_prc_step=10, first_work_hour=8, last_work_hour=23),
    ).put('').label('output')

    job.local_run(
        sources={'input': StreamSource(test_input)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 1
    assert output[0] == expected_output[0]


def test_coeffs_reducer():
    fields = ('category', 'organization_id', 'purchases', 'purchases_sum')
    purchases = [
        {
            '10': [0, 0],
            '20': [0, 1],
            '30': [0, 1],
            '40': [1, 1],
            '50': [1, 1],
            '60': [1, 2],
            '70': [1, 2],
            '80': [2, 2],
            '90': [2, 2],
        },
        {
            '10': [1, 0],
            '20': [1, 0],
            '30': [1, 0],
            '40': [1, 0],
            '50': [1, 0],
            '60': [1, 0],
            '70': [1, 0],
            '80': [1, 0],
            '90': [1, 1],
        },
        {
            '10': [2, 1],
            '20': [2, 1],
            '30': [2, 1],
            '40': [2, 2],
            '50': [3, 3],
            '60': [4, 3],
            '70': [4, 3],
            '80': [4, 3],
            '90': [5, 5],
        },
        {
            '10': [0, 1],
            '20': [0, 1],
            '30': [0, 1],
            '40': [0, 1],
            '50': [0, 1],
            '60': [0, 1],
            '70': [0, 1],
            '80': [0, 1],
            '90': [1, 1],
        },
        {
            '10': [0, 0],
            '20': [0, 0],
            '30': [0, 0],
            '40': [0, 0],
            '50': [0, 0],
            '60': [0, 0],
            '70': [0, 0],
            '80': [0, 0],
            '90': [0, 0],
        },
    ]
    test_input = [
        Record(**dict(zip(fields, ['a', 1, purchases[0], 2]))),
        Record(**dict(zip(fields, ['a', 1, purchases[1], 1]))),
        Record(**dict(zip(fields, ['a', 1, purchases[2], 5]))),
        Record(**dict(zip(fields, ['a', 1, purchases[3], 1]))),
        Record(**dict(zip(fields, ['a', 1, purchases[4], 0]))),
    ]

    expected_output = [
        Record(
            category='a',
            coeffs={
                '10': 2.4,
                '20': 2.33,
                '30': 2.33,
                '40': 2.0,
                '50': 1.6,
                '60': 1.33,
                '70': 1.33,
                '80': 1.23,
                '90': 1.0,
            },
            organization_id=1,
            probs={
                '10': 0.67,
                '20': 0.6,
                '30': 0.6,
                '40': 0.5,
                '50': 0.5,
                '60': 0.5,
                '70': 0.5,
                '80': 0.5,
                '90': 0.0,
            },
        ),
    ]
    output = []

    job = clusters.MockCluster().job()

    job.table('').label('input').groupby('category', 'organization_id').reduce(
        coeffs_reducer(instock_prc_step=10),
    ).put('').label('output')

    job.local_run(
        sources={'input': StreamSource(test_input)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == len(expected_output)
    output = output[0].to_dict()
    expected_output = expected_output[0].to_dict()
    assert output.keys() == expected_output.keys()
    for key in output:
        if key not in {'coeffs', 'probs'}:
            assert output[key] == expected_output[key]
        else:
            assert output[key].keys() == expected_output[key].keys()
            for inner_key in output[key].keys():
                np.testing.assert_almost_equal(
                    output[key][inner_key], expected_output[key][inner_key], 2,
                )


def test_demand_mapper():
    test_input = [
        Record(
            code=1,
            organization_id=1,
            purchases_sum=[1, 1, 0, 0, 5, 2, 0, 1, 1],
            instock_prc=[0.5, 1, 0, 0.0625, 1, 0.8125, 0, 1, 0.5],
            coeffs={
                '10': 2.4,
                '20': 2.33,
                '30': 2.33,
                '40': 2.0,
                '50': 1.6,
                '60': 1.33,
                '70': 1.33,
                '80': 1.23,
                '90': 1.0,
            },
            probs={
                '10': 0.67,
                '20': 0.6,
                '30': 0.51,
                '40': 0.5,
                '50': 0.45,
                '60': 0.4,
                '70': 0.4,
                '80': 0.35,
                '90': 0.1,
            },
        ),
    ]

    expected_output = [
        Record(
            code=1,
            organization_id=1,
            lower_demand=[1, 1, 0, 0, 5, 2, 0, 1, 1],
            upper_demand=[1.6, 1, 0.67, 0.67, 5, 2.46, 0.67, 1, 1.6],
        ),
    ]
    output = []

    job = clusters.MockCluster().job()

    job.table('').label('input').map(demand_mapper(instock_prc_step=10)).put(
        '',
    ).label('output')

    job.local_run(
        sources={'input': StreamSource(test_input)},
        sinks={'output': ListSink(output)},
    )

    assert output == expected_output


if __name__ == '__main__':
    test_coeffs_reducer()
    test_osa_reducer()
    test_demand_mapper()
