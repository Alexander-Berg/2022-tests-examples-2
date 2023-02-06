import numpy as np

from nile.api.v1 import clusters
from nile.api.v1 import extractors as ne
from nile.api.v1 import Job, Record
from nile.api.v1.local import StreamSource, ListSink
from nile.api.v1.stream import Stream


from projects.gouplift.gouplift.metrics import (
    get_area_under_uplift_curve,
    get_uplift_at_k,
)


EXP_1 = []
EXP_2 = []
T = 0
for i in range(1, 101):
    for j in range(1, 101):
        treatment = (i + j) % 2 == 1
        multiplier = 1.1 if treatment else 1.0
        EXP_1.append(
            {
                'exp': 'exp_1',
                'target': i * multiplier,
                'money': j * multiplier,
                'treat': treatment,
                'i': i,
                'j': j,
            },
        )
        EXP_2.append(
            {
                'exp': 'exp_2',
                'target': i * multiplier,
                'money': j * multiplier,
                'treat': treatment,
                'i': i,
                'j': j,
            },
        )
EXP_CONCAT = EXP_1 + EXP_2


def test_uplift_at_k():
    cluster = clusters.MockCluster()
    job = cluster.job()

    experiments = _get_experiments_table(job)
    get_uplift_at_k(
        2500, experiments, 'exp', 'treat', 'score_2', 'target',
    ).label('uplift@2500')
    get_uplift_at_k(
        0.5, experiments, 'exp', 'treat', 'score_2', 'target',
    ).label('uplift@0.5')

    output_1 = []
    output_2 = []
    job.local_run(
        sources={
            'experiments': StreamSource([Record(**r) for r in EXP_CONCAT]),
        },
        sinks={
            'uplift@2500': ListSink(output_1),
            'uplift@0.5': ListSink(output_2),
        },
    )

    assert np.allclose(output_1[0]['uplift_at_k'], 37750, atol=1e-3, rtol=1e-3)
    assert np.allclose(output_2[0]['uplift_at_k'], 37750, atol=1e-3, rtol=1e-3)


def test_uplift_at_budget():
    cluster = clusters.MockCluster()
    job = cluster.job()

    experiments = _get_experiments_table(job)
    get_uplift_at_k(
        2500, experiments, 'exp', 'treat', 'score_1', 'target', 'money',
    ).label('uplift@2500')
    get_uplift_at_k(
        0.5, experiments, 'exp', 'treat', 'score_1', 'target', 'money',
    ).label('uplift@0.5')

    output_1 = []
    output_2 = []
    job.local_run(
        sources={
            'experiments': StreamSource([Record(**r) for r in EXP_CONCAT]),
        },
        sinks={
            'uplift@2500': ListSink(output_1),
            'uplift@0.5': ListSink(output_2),
        },
    )

    assert np.allclose(output_1[0]['uplift_at_k'], 18179, atol=1e-3, rtol=1e-3)
    assert np.allclose(output_2[0]['uplift_at_k'], 106, atol=1e-3, rtol=1e-3)


def _get_experiments_table(job: Job) -> Stream:
    experiments = (
        job.table('experiments')
        .label('experiments')
        .project(
            ne.all(),
            score_1=ne.custom(lambda j, i: j / i),
            score_2=ne.custom(lambda i: -i),
        )
    )
    return experiments


def test_area_under_uplift_curve():
    cluster = clusters.MockCluster()
    job = cluster.job()

    experiments = _get_experiments_table(job)
    get_area_under_uplift_curve(
        experiments, 'exp', 'treat', 'score_2', 'target',
    ).label('area_under_uplift_curve')

    output = []
    job.local_run(
        sources={
            'experiments': StreamSource([Record(**r) for r in EXP_CONCAT]),
        },
        sinks={'area_under_uplift_curve': ListSink(output)},
    )
    my_score = output[0]['area_under_uplift_curve']
    assert np.allclose(my_score, 0.665, atol=1e-3, rtol=1e-3)


def test_area_under_budget_uplift_curve():
    cluster = clusters.MockCluster()
    job = cluster.job()

    experiments = _get_experiments_table(job)
    get_area_under_uplift_curve(
        experiments, 'exp', 'treat', 'score_1', 'target', 'money',
    ).label('area_under_uplift_curve_1')
    get_area_under_uplift_curve(
        experiments, 'exp', 'treat', 'score_2', 'target', 'money',
    ).label('area_under_uplift_curve_2')

    output_1 = []
    output_2 = []
    job.local_run(
        sources={
            'experiments': StreamSource([Record(**r) for r in EXP_CONCAT]),
        },
        sinks={
            'area_under_uplift_curve_1': ListSink(output_1),
            'area_under_uplift_curve_2': ListSink(output_2),
        },
    )
    assert np.allclose(
        output_1[0]['area_under_uplift_curve'], 0.732, atol=1e-3, rtol=1e-3,
    )
    assert np.allclose(
        output_2[0]['area_under_uplift_curve'], 0.668, atol=1e-3, rtol=1e-3,
    )


if __name__ == '__main__':
    test_uplift_at_k()
    test_uplift_at_budget()
    test_area_under_uplift_curve()
    test_area_under_budget_uplift_curve()
