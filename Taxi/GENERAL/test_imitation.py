import os
from collections import namedtuple
import numpy as np
import pandas as pd
import pytest
from scipy.special import expit
from imitation import hungrian, calc_metric_dispatch_imitation
import yatest.common


FORMULAS = {
    "accident": "0.8674*score_order_accident +0.8371*score_executor_accident -9.3385",
    "injured": "1.0325*score_order_injured +0.9593*score_executor_injured -7.2890"
}


Params = namedtuple('Params', [
    'base_score',
    'test_scores',
    'slices',
    'metrics',
    'base_match_fix_keys',
    'return_change_pair_stat'
])


@pytest.fixture
def sample_data():
    return (
        pd.read_csv(
            os.path.join(yatest.common.work_path(), 'debug_sample.csv'),
            index_col=['order_id', 'dbid_uuid']
        )
        .fillna({'safety_penalty': 0})
        .fillna({'track_accidents_365_per_km': 0})
        .assign(
            prob_accident=lambda df: df.eval(FORMULAS['accident']).apply(expit),
            prob_injured=lambda df: df.eval(FORMULAS['injured']).apply(expit),
            good_driver=lambda df: df.eval('score_executor_injured <= -1.6'),
            bad_driver=lambda df: df.eval('score_executor_injured > -1.6'),
        )
    )


def test_hungrian():
    series = (
        pd.DataFrame({
            'score': [0, 1, 1, 0, 10],
            'order_id': ['o_1', 'o_1', 'o_2', 'o_2', 'o_2'],
            'dbid_uuid': ['c_1', 'c_2', 'c_1', 'c_2', 'c_3'],
        })
        .set_index(['order_id', 'dbid_uuid'], verify_integrity=True)
        .score
    )
    expected = (
        pd.DataFrame({
            'order_id': ['o_1', 'o_2'],
            'dbid_uuid': ['c_1', 'c_2'],
        })
        .set_index(['order_id', 'dbid_uuid'], verify_integrity=True)
        .index
    )
    res = hungrian(series)
    pd.testing.assert_index_equal(res, expected)


def test_big_data():
    np.random.seed(42)
    data = (
        pd.DataFrame.from_records([
            dict(
                order_id=str(order_id),
                dbid_uuid=str(dbid_uuid),
                score=np.random.randn(),
                safety_penalty=0,
                score_order_accident=np.random.randn() - 2,
                score_executor_accident=np.random.randn() - 2,
                score_order_injured=np.random.randn() - 2,
                score_executor_injured=np.random.randn() - 2,
            )
            for order_id in range(100)
            for dbid_uuid in range(110)
            if abs(order_id - dbid_uuid) < 6
        ])
        .set_index(['order_id', 'dbid_uuid'], verify_integrity=True)
    )
    hungrian(data.score)


def test_sample(sample_data):
    res = hungrian(sample_data.score)
    assert len(res) == 224


def test_calculate_metrics(sample_data):
    params = Params(
        base_score=b'score + safety_penalty',
        test_scores=[
            b'score',
            b'score + safety_penalty + 60 * (score_executor_injured > -1.6) * (track_accidents_365_per_km > 100)',
            b'score + safety_penalty + 60 * (score_executor_injured > -1.6) * (track_accidents_365_per_km > 150)',
            b'score + safety_penalty + 60 * (score_executor_injured > -1.6) * (track_accidents_365_per_km > 200)',
        ],
        slices=[
            (b''),
            (b''),
            (b'bad_driver'),
            (b'good_driver'),
        ],
        metrics=[
            b'prob_accident',
            b'prob_injured',
            b'bad_driver',
            b'good_driver',
            b'rt',
            b'score',
        ],
        base_match_fix_keys=[b'order_id', b'dbid_uuid'],
        return_change_pair_stat=True,
    )
    res = list(calc_metric_dispatch_imitation('d1', sample_data.reset_index().itertuples(), params))
    assert len(res) == (
        len(params.test_scores) * len(params.slices) * len(params.metrics)
        + len(params.test_scores) * len(params.slices)
    )


def test_one_metric(sample_data):
    result = list(calc_metric_dispatch_imitation(
        'reduce_key',
        sample_data.reset_index().itertuples(),
        Params(
            base_score=b'score + safety_penalty',
            test_scores=[b'score + safety_penalty + 60 * (score_executor_injured > -1.6) * (track_accidents_365_per_km > 200)'],
            slices=[b'bad_driver'],
            metrics=[b'plan_travel_distance_km'],
            base_match_fix_keys=[b'order_id', b'dbid_uuid'],
            return_change_pair_stat=True,
        )
    ))

    expected = [
        (
            0,
            {
                'base': {'count': 36, 'std': 8.57851172793287, 'sum': 441.39231954038144},
                'draw_id': 'reduce_key',
                'metric': 'plan_travel_distance_km',
                'score': 'score + safety_penalty + 60 * (score_executor_injured > -1.6) * '
                '(track_accidents_365_per_km > 200)',
                'slice': 'bad_driver',
                'test': {'count': 36, 'std': 9.762119196784266, 'sum': 467.9034221237897}
            }
        ),
        (
            1,
            {
                'common_pairs_count': 35,
                'draw_id': 'reduce_key',
                'pairs_count': 36,
                'score': 'score + safety_penalty + 60 * (score_executor_injured > -1.6) * '
                '(track_accidents_365_per_km > 200)',
                'slice': 'bad_driver'
            }
        )
    ]

    assert result == expected


def test_one_metric_default_slice(sample_data):
    result = list(calc_metric_dispatch_imitation(
        'reduce_key',
        sample_data.reset_index().itertuples(),
        Params(
            base_score=b'score + safety_penalty',
            test_scores=[b'score + safety_penalty + 60 * (score_executor_injured > -1.6) * (track_accidents_365_per_km > 200)'],
            slices=[b''],
            metrics=[b'plan_travel_distance_km'],
            base_match_fix_keys=[b'order_id', b'dbid_uuid'],
            return_change_pair_stat=True,
        )
    ))
    expected = [
        (
            0,
            {
                'base': {'count': 224, 'std': 11.886496842596735, 'sum': 2744.9265654798146},
                'draw_id': 'reduce_key',
                'metric': 'plan_travel_distance_km',
                'score': 'score + safety_penalty + 60 * (score_executor_injured > -1.6) * '
                '(track_accidents_365_per_km > 200)',
                'slice': '',
                'test': {'count': 224, 'std': 11.886496842596735, 'sum': 2744.9265654798146}
            }
        ),
        (
            1,
            {
                'common_pairs_count': 220,
                'draw_id': 'reduce_key',
                'pairs_count': 224,
                'score': 'score + safety_penalty + 60 * (score_executor_injured > -1.6) * '
                '(track_accidents_365_per_km > 200)',
                'slice': ''
            }
        )
    ]

    assert result == expected
