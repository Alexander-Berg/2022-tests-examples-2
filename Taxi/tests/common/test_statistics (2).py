import itertools
import six
import pytest

import numpy as np
from nile.api.v1 import Record
from nile.api.v1 import clusters
from nile.api.v1.local import StreamSource, ListSink

from projects.common.statistics.mr_operations.aggregator import SumAggregator
from projects.common.statistics.objects.aggregator_keys import (
    SimpleAggregatorKey,
    SliceAggregatorKey,
    GroupAggregatorKey,
)
from projects.common.statistics.objects.metrics import (
    MetricStorage,
    ratio_function,
    create_mean_metric,
    Feature,
)
from projects.common.statistics.local_tests import (
    TTest,
    MannWhitneyUTest,
    SumBootstrapTest,
)
from projects.common.statistics.mr_operations.multi_test_calculator import (
    MultiTestCalculator,
)


def generate_input():
    result = []
    for bucket in range(5):
        for group in [b'control', b'test']:
            for defined in range(1, 5):
                for undefined in range(2):
                    for metric in itertools.repeat(1, 4):
                        result.append(
                            Record(
                                bucket=bucket,
                                group=group,
                                defined=defined,
                                undefined=undefined,
                                metric=metric,
                            ),
                        )
    return result


def generate_output():
    result = []
    for group in [b'control', b'test']:
        for bucket in range(5):
            for defined in [1, 2, 3, b'__total__']:
                for undefined in [0, 1, b'__total__']:
                    metric = 4.0
                    if defined == b'__total__' and undefined != b'__total__':
                        metric = 16.0
                    if defined != b'__total__' and undefined == b'__total__':
                        metric = 8.0
                    if defined == b'__total__' and undefined == b'__total__':
                        metric = 32.0
                    result.append(
                        Record(
                            bucket=bucket,
                            group=group,
                            defined=defined,
                            undefined=undefined,
                            metric=metric,
                        ),
                    )
    return result


def test_bucket_aggregator():
    job = clusters.MockCluster().job()
    bucket_aggregator = SumAggregator(
        feature_names=['metric'],
        keys=[
            SimpleAggregatorKey('bucket'),
            GroupAggregatorKey('group', ['control', 'test']),
            SliceAggregatorKey('defined', [1, 2, 3], True, '__total__'),
            SliceAggregatorKey(
                'undefined', unfold_total=True, total_value='__total__',
            ),
        ],
        combiner_batch_size=1000,
    )
    bucket_aggregator(job.table('').label('input')).label('output').put(
        'output_table',
    )
    output = []
    inp = generate_input()
    job.local_run(
        sources={'input': StreamSource(inp)},
        sinks={'output': ListSink(output)},
    )
    assert sorted(output) == sorted(generate_output())


def make_close_samples():
    ones = np.ones(7)
    ones_zero = np.ones(7)
    ones_zero[6] = 0
    return (
        MetricStorage(ratio_function, [ones, ones]),
        MetricStorage(ratio_function, [ones_zero, ones]),
    )


def make_equal_samples():
    ones = np.ones(7)
    return (
        MetricStorage(ratio_function, [ones, ones]),
        MetricStorage(ratio_function, [ones, ones]),
    )


@pytest.mark.filterwarnings('ignore:invalid value encountered')
def test_ttest():
    ttest = TTest(equal_var=False, confidence_level=0.05)
    result = ttest(*make_close_samples())._asdict()
    true_result = {
        'statistic': pytest.approx(1.0000000000000004),
        'pvalue': pytest.approx(0.3559176837495818),
        'control_conf_intervals': [
            pytest.approx(0.5075840216011884),
            pytest.approx(1.2067016926845258),
        ],
        'test_conf_intervals': [pytest.approx(1.0), pytest.approx(1.0)],
        'diff_conf_intervals': [
            pytest.approx(-0.2067016926845257),
            pytest.approx(0.4924159783988115),
        ],
    }
    assert result == true_result

    result = ttest(*make_equal_samples())._asdict()
    assert result['statistic'] is None
    assert result['pvalue'] is None
    assert result['diff_conf_intervals'][0] is None
    assert result['diff_conf_intervals'][1] is None
    assert result['control_conf_intervals'] == [
        pytest.approx(1.0),
        pytest.approx(1.0),
    ]
    assert result['test_conf_intervals'] == [
        pytest.approx(1.0),
        pytest.approx(1.0),
    ]


def test_mannwhitneyutest():
    mannwhitneyu = MannWhitneyUTest()
    result = mannwhitneyu(*make_close_samples())._asdict()
    assert result['statistic'] == pytest.approx(28.0)
    assert result['pvalue'] == pytest.approx(0.39136593830755184)


def test_bootstrap():
    bootstrap = SumBootstrapTest(confidence_levels=0.05, iters_count=10000)
    result = bootstrap(*make_close_samples())._asdict()
    true_result = {
        'pvalue': pytest.approx(0.3452),
        'test_conf_intervals': [pytest.approx(1.0), pytest.approx(1.0)],
        'control_conf_intervals': [
            pytest.approx(0.5714285714285714),
            pytest.approx(1.0),
        ],
        'diff_conf_intervals': [
            pytest.approx(0.0),
            pytest.approx(0.4285714285714286),
        ],
        'control_distribution': None,
        'diff_distribution': None,
        'test_distribution': None,
        'warning': None,
    }
    assert result == true_result

    result = bootstrap(*make_equal_samples())._asdict()
    true_result = {
        'pvalue': pytest.approx(1.0),
        'test_conf_intervals': [pytest.approx(1.0), pytest.approx(1.0)],
        'control_conf_intervals': [pytest.approx(1.0), pytest.approx(1.0)],
        'diff_conf_intervals': [pytest.approx(0.0), pytest.approx(0.0)],
        'control_distribution': None,
        'diff_distribution': None,
        'test_distribution': None,
        'warning': None,
    }
    assert result == true_result


def generate_calculator_input():
    for i in range(1000):
        yield Record(
            key=six.ensure_binary(f'{i}'),
            groups=b'test' if i % 2 else b'control',
            numerator=i,
        )


def test_calculator():
    job = clusters.MockCluster().job()
    calculator = MultiTestCalculator(
        stat_tests={'ttest': TTest(equal_var=False, confidence_level=0.01)},
        metrics=[create_mean_metric('mean_numerator', 'numerator')],
        features=[
            Feature.make_plain('numerator'),
            Feature.make_defined('numerator'),
        ],
        n_buckets=10,
        group_column='groups',
        groups=['control', 'test'],
        group_pairs='all',
        slices=None,
        key_column='key',
        return_buckets=True,
    )
    calculator(job.table('').label('input')).label('output').put(
        'output_table',
    )
    output_records = []
    job.local_run(
        sources={'input': StreamSource(generate_calculator_input())},
        sinks={'output': ListSink(output_records)},
    )
    assert len(output_records) == 1
    result = output_records[0].to_dict()
    assert result['control_value'] == 499.0
    assert result['test_value'] == 500.0
    assert result['diff_value'] == 1.0
    assert result['relative_diff_percent'] == pytest.approx(0.2004008016032064)
    assert result['metric'] == 'mean_numerator'
    ttest_result = result['ttest']
    ttest_true_result = {
        'statistic': pytest.approx(0.32699211768708963),
        'pvalue': pytest.approx(0.7474538827476123),
        'test_conf_intervals': [
            pytest.approx(455.18346961382446),
            pytest.approx(548.2945103075754),
        ],
        'control_conf_intervals': [
            pytest.approx(450.82838178470394),
            pytest.approx(539.6985381643076),
        ],
        'diff_conf_intervals': [
            pytest.approx(-50.54152504365577),
            pytest.approx(63.49258501604406),
        ],
    }
    assert ttest_result == ttest_true_result
