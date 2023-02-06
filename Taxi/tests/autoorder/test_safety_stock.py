import numpy as np

from nile.api.v1 import Record, clusters
from nile.api.v1.local import StreamSource, ListSink

from projects.autoorder.safety_stock.safety_stock import (
    get_linear_comb_of_convolved_lists,
    compute_int_weights,
    safety_stock_reducer,
    apply_constraints,
)


def test_get_linear_comb_of_convolved_lists():
    np.testing.assert_array_equal(
        get_linear_comb_of_convolved_lists(
            [[1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]],
            3,
            [1, -2, 1],
        ),
        np.array([0] * 4),
    )
    np.testing.assert_array_equal(
        get_linear_comb_of_convolved_lists(
            [[1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]],
            7,
            [1, 1, 1],
        ),
        np.array([18]),
    )
    np.testing.assert_array_equal(
        get_linear_comb_of_convolved_lists(
            [[1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]],
            1,
            [1, 1, 1],
        ),
        np.array([3] * 6),
    )
    np.testing.assert_array_equal(
        get_linear_comb_of_convolved_lists([[1], [1]], 1, [1, 2]),
        np.array([3]),
    )


def test_compute_int_weights():
    np.testing.assert_array_equal(
        compute_int_weights(10, 2), [2] * 5 + [1] * 4,
    )
    np.testing.assert_array_equal(
        compute_int_weights(28, 7), [12] * 6 + [6] * 6 + [4] * 6 + [3] * 4,
    )
    np.testing.assert_array_equal(compute_int_weights(5, 14), [1])


def test_apply_constraints():
    assert apply_constraints(5, 1, 1.5, None, None) == 0
    assert apply_constraints(5, 5, 1.5, None, None) == 2.5
    assert apply_constraints(5, 10, 1.5, None, None) == 4.5
    assert apply_constraints(10, 4, 1.5, 3, None) == 2.0
    assert apply_constraints(10, 20, 1.5, 3, None) == 3
    assert apply_constraints(10, None, 1.5, 3, None) == 0


def test_safety_stock_reducer():
    fields = (
        'minus_timestamp',
        'organization_id',
        'code',
        'date_local',
        'hour_local',
        'residuals',
        'quantity',
        'mean_prediction',
        'prediction',
    )

    def make_records(values_list, fields=fields):
        return [Record(**dict(zip(fields, values))) for values in values_list]

    test_input = make_records(
        [
            [-1, 1, 1, '2021-04-01', '09', 0, 0, 1.5, 0.2],
            [-2, 1, 1, '2021-04-01', '10', 0, 0, 1.5, 0.2],
            [-3, 1, 1, '2021-04-01', '11', 2, 1, 1.5, 0.2],
            [-4, 1, 1, '2021-04-01', '12', 1, 0, 1.5, 0.2],
            [-5, 1, 1, '2021-04-01', '13', 1, 0, 1.5, 0.2],
            [-6, 1, 1, '2021-04-02', '09', 2, 0, 1.5, 0.3],
            [-7, 1, 1, '2021-04-02', '10', 2, 1, 1.5, 0.3],
            [-8, 1, 1, '2021-04-02', '11', 1, 1, 1.5, 0.3],
            [-9, 1, 1, '2021-04-02', '12', 0, 0, 1.5, 0.3],
            [-10, 1, 1, '2021-04-03', '09', 2, 2, 1.5, 0.4],
            [-11, 1, 1, '2021-04-03', '10', 0, 0, 1.5, 0.4],
            [-12, 1, 1, '2021-04-03', '11', 0, 0, 1.5, 0.4],
            [-13, 1, 1, '2021-04-03', '12', 0, 0, 1.5, 0.4],
            [-14, 1, 1, '2021-04-03', '13', 0, 0, 1.5, 0.4],
            [-15, 1, 1, '2021-04-04', '09', 3, 0, 1.5, 0.4],
            [-16, 1, 1, '2021-04-04', '10', 3, 2, 1.5, 0.4],
            [-17, 1, 1, '2021-04-04', '11', 1, 0, 1.5, 0.4],
            [-18, 1, 1, '2021-04-04', '12', 1, 0, 1.5, 0.4],
            [-19, 1, 1, '2021-04-05', '09', 1, 0, 1.5, 0.3],
            [-20, 1, 1, '2021-04-05', '10', 1, 0, 1.5, 0.3],
        ],
    )

    expected_output = [
        Record(
            SL=0.66666,
            SSL=2.55,
            SSL_q60=3.32,
            SSL_q60_with_constraints=3.32,
            SSL_with_constraints=2.55,
            code=1,
            days_between_supply=2,
            debug={
                'target_sum': 7,
                'ssl_mean': 2.55,
                'n_days': 5,
                'days_in_history': 5,
                'mean_prediction': 1.5,
                'predictions_w_r_sum': 4.1,
                'predictions_wo_r_sum': 2.3,
                'hours_w_r': 13,
                'hours_wo_r': 7,
            },
            organization_id=1,
            shelf_life=8,
        ),
    ]
    output = []

    job = clusters.MockCluster().job()

    job.table('').label('input').groupby('code', 'organization_id').sort(
        'minus_timestamp',
    ).reduce(
        safety_stock_reducer(
            supply_windows=[2],
            days_in_history=5,
            percentiles=[60],
            shelf_life_dct={1: 8},
        ),
    ).put(
        '',
    ).label(
        'output',
    )

    job.local_run(
        sources={'input': StreamSource(test_input)},
        sinks={'output': ListSink(output)},
    )

    output_dct = output[0].to_dict()
    expected_dct = expected_output[0].to_dict()
    assert output_dct.keys() == expected_dct.keys()
    for key in output_dct.keys():
        if key != 'debug':
            np.testing.assert_almost_equal(
                output_dct[key], expected_dct[key], 5,
            )
        else:
            assert output_dct['debug'].keys() == expected_dct['debug'].keys()
            for debug_key in output_dct['debug'].keys():
                np.testing.assert_almost_equal(
                    output_dct['debug'][debug_key],
                    expected_dct['debug'][debug_key],
                    5,
                )


if __name__ == '__main__':
    test_compute_int_weights()
    test_apply_constraints()
    test_get_linear_comb_of_convolved_lists()
    test_safety_stock_reducer()
