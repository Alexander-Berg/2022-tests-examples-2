import numpy as np

from nile.api.v1 import Record, clusters
from nile.api.v1.local import StreamSource, ListSink

from projects.autoorder.demand_restore.get_demand import (
    _parse_windows,
    get_rounded_percentage,
    get_distribution,
    features_density_mapper,
    density_mapper,
    get_window_sum,
    get_promos_subset_params,
    get_parameters_for_window_sum,
)


def test_parse_windows():
    assert _parse_windows('28,28;14,0;0,14') == [(28, 28), (14, 0), (0, 14)]
    assert _parse_windows('0,14') == [(0, 14)]


def test_get_rounded_percentage():
    dist = np.asarray(
        [0] * 10
        + [0.02, 0.03, 0.03, 0.05, 0.07, 0.09, 0.06, 0.04, 0.04, 0.07]
        + [0] * 4,
    )
    resids = [0] * 5 + [2] * 10 + [0] * 9

    assert (
        get_rounded_percentage(
            thresholds=np.asarray([1 / 3, 2 / 3, 1]),
            day_dist=dist,
            residuals=resids,
        )
        == 2 / 3
    )

    assert (
        get_rounded_percentage(
            thresholds=np.asarray([1 / 2, 1]), day_dist=dist, residuals=resids,
        )
        == 0.5
    )


def test_get_distribution():
    country_distributions = {
        'Россия': [0, 0, 0.2, 0.2, 0.2, 0.2, 0.2, 0],
        'Израиль': [0, 0, 0.1, 0.3, 0.3, 0.3, 0, 0],
        'all': [0, 0, 0.1, 0.3, 0.3, 0.2, 0.1, 0],
    }

    countries_dict = {
        1: 'Россия',
        2: 'Россия',
        3: 'Израиль',
        4: 'Великобритания',
    }
    records = [
        Record(organization_id=1, distribution=[0, 0, 1, 0, 0, 0, 0, 0]),
        Record(organization_id=2),
        Record(organization_id=4),
        Record(organization_id=5),
    ]
    expected_outputs = [
        np.array([0, 0, 1, 0, 0, 0, 0, 0]),
        np.array([0, 0, 0.2, 0.2, 0.2, 0.2, 0.2, 0]),
        np.array([0, 0, 0.1, 0.3, 0.3, 0.2, 0.1, 0]),
        np.array([0, 0, 0.1, 0.3, 0.3, 0.2, 0.1, 0]),
    ]
    for rec, expected_output in zip(records, expected_outputs):
        np.testing.assert_almost_equal(
            get_distribution(rec, country_distributions, countries_dict),
            expected_output,
        )


def test_features_density_mapper():
    country_distributions = dict()
    countries_dict = dict()

    test_input = [
        Record(
            organization_id=1111,
            code=2222,
            residuals=[10] * 16 + [5] * 8,
            n_units_of_sku=[0] * 15 + [5] + [0] * 8,
            isoweekday_local=2,
            distribution=(
                [0.0] * 30
                + [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
                + [0.0] * 128
            ),
            date_local='2021-12-01',
            timestamp=1638306000,
            sales=5,
            on_stock=True,
            promo_key='',
        ),
        Record(
            organization_id=1111,
            code=2222,
            residuals=[5] * 10 + [0] * 8,
            n_units_of_sku=[0] * 8 + [5] + [0] * 9,
            isoweekday_local=2,
            distribution=(
                [0.0] * 30
                + [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0]
                + [0.0] * 128
            ),
            date_local='2021-12-01',
            timestamp=1638306000,
            sales=5,
            on_stock=True,
            promo_key='',
        ),
    ]

    expected_output = [
        Record(
            density=1.0,
            density_bs=1.0,
            sales_bs=5,
            density_full=1.0,
            organization_id=1111,
            code=2222,
            date_local='2021-12-01',
            timestamp=1638306000,
            sales=5,
            promo_key='',
        ),
        Record(
            density=0.45,
            density_bs=0.2,
            sales_bs=0.0,
            density_full=0.9,
            organization_id=1111,
            code=2222,
            date_local='2021-12-01',
            timestamp=1638306000,
            sales=5,
            promo_key='',
        ),
    ]
    output = []
    job = clusters.MockCluster().job()

    job.table('').label('input').map(
        features_density_mapper(
            country_distributions=country_distributions,
            countries_dict=countries_dict,
            n_thresholds=2,
        ),
    ).put('').label('output')

    job.local_run(
        sources={'input': StreamSource(test_input)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == len(expected_output)
    for i in range(len(output)):
        assert output[i] == expected_output[i]


def test_density_mapper():
    country_distributions = dict()
    countries_dict = dict()

    test_input = [
        Record(
            organization_id=1111,
            code=2222,
            timepoint_id='2021-12-01_1111_2222_',
            timestamp=1638306000,
            isoweekday_local=2,
            residuals=[0] * 12 + [5] * 4 + [0] * 8,
            n_units_of_sku=[0] * 15 + [5] + [0] * 8,
            active=True,
            has_history=True,
            true_sales=10,
            true_on_stock=True,
            on_stock=True,
            uncut_sales=7,
            distribution=(
                [0.0] * 34
                + [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
                + [0.0] * 124
            ),
            date_local='2021-12-01',
            sales=5,
            future_count_w14={'': 3},
            past_count_w14={'': 5},
            past_sales_sum_w14={'': 2},
            future_sales_sum_w14={'': 1},
            past_density_sum_w14={'': 0.2},
            future_density_sum_w14={'': 0.2},
            past_sales_bs_sum_w14={'': 1},
            future_sales_bs_sum_w14={'': 0},
            past_density_bs_sum_w14={'': 0.1},
            future_density_bs_sum_w14={'': 0.1},
            past_density_full_sum_w14={'': 0.3},
            future_density_full_sum_w14={'': 0.3},
            past_weight_sum_w14={'': 2},
            future_weight_sum_w14={'': 0.5},
            replaced=True,
            promo_key='',
            promo=[],
        ),
    ]

    expected_output = [
        Record(
            code=2222,
            organization_id=1111,
            date_local='2021-12-01',
            timepoint_id='2021-12-01_1111_2222_',
            timestamp=1638306000,
            isoweekday_local=2,
            residuals=[0] * 12 + [5] * 4 + [0] * 8,
            n_units_of_sku=[0] * 15 + [5] + [0] * 8,
            active=True,
            has_history=True,
            true_sales=10,
            true_on_stock=True,
            sales=5.0,
            on_stock=True,
            uncut_sales=7.0,
            oos_density=0.4,
            full_density=1.0,
            full_oos_density=0.6,
            wo_rep_density=1.0,
            restored_sales_p14_f14=7.0,
            restored_sales_p14_f14_wo_rep=7.5,
            replaced=True,
            shelf_life=1,
            mean_sales=7.5,
            mean_sales_bs=5.0,
            mean_sales_full=5.0,
            work_on_stock=True,
            num_oos_hours=20,
            num_oos_work_hours=12,
            num_days_p14_w14=8,
            promo=[],
        ),
    ]

    output = []
    job = clusters.MockCluster().job()

    job.table('').label('input').map(
        density_mapper(
            [(14, 14)],
            country_distributions,
            countries_dict,
            shelf_life_dict={2222: 1},
            promo_alias_to_type_dct={1: 'a', 2: 'b'},
        ),
    ).put('').label('output')

    job.local_run(
        sources={'input': StreamSource(test_input)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == len(expected_output)
    for i in range(len(output)):
        x = output[i].to_frozen_dict()
        y = output[i].to_frozen_dict()
        assert x.keys() == y.keys()
        for key in x.keys():
            assert x[key] == y[key]


def test_get_window_sum():
    record = Record(
        future_sales_sum_w7={'': 2, '1': 3, '2': 2},
        past_sales_sum_w7={'': 4},
        past_only_sales_sum_w7={'': 6, '1': 2},
    )
    assert get_window_sum(record, 'sales', 7, 0, [''], 1) == 6
    assert get_window_sum(record, 'sales', 7, 0, ['', '1'], 0.5) == 7
    assert get_window_sum(record, 'sales', 7, 7, ['', '1', '2'], 1) == 11
    assert get_window_sum(record, 'sales', 7, 7, ['', '1', '2'], 0.5) == 10
    assert get_window_sum(record, 'sales', 0, 7, ['', '2'], 1) == 4
    assert get_window_sum(record, 'sales', 0, 7, ['1', '2'], 0.5) == 4

    record = Record(
        future_sales_sum_w7={'': 2},
        past_sales_sum_w7={'': 0},
        past_only_sales_sum_w7={'': 0},
    )
    assert get_window_sum(record, 'sales', 7, 0, [''], 1) == 0


def test_get_promos_subset_params():
    counter = {'': 1, '1': 3, '4': 8, '1_2': 4, '1_3': 2, '2_3_4': 3}

    output = get_promos_subset_params(counter, '2_3_4')
    expected_output = (['2_3_4', '4'], 7, 4 / 8)
    for i in range(3):
        assert output[i] == expected_output[i]

    output = get_promos_subset_params(counter, '1_3')
    expected_output = (['1_3', '1', ''], 6, 1)
    for i in range(3):
        assert output[i] == expected_output[i]


def test_get_parameters_for_window_sum():
    record = Record(
        promo_key='2',
        future_count_w7={'': 2, '1': 3, '2': 2, '1_2': 1},
        past_count_w7={'': 4},
        past_only_count_w7={'': 6, '1': 8},
    )

    output = get_parameters_for_window_sum(record, 7, 7)
    expected_output = (['2', ''], 7, 5 / 6)
    for i in range(3):
        assert output[i] == expected_output[i]

    record = record.transform(promo_key='1')
    output = get_parameters_for_window_sum(record, 7, 0)
    expected_output = (['1'], 8, 1)
    for i in range(3):
        assert output[i] == expected_output[i]

    record = record.transform(promo_key='')
    output = get_parameters_for_window_sum(record, 7, 0)
    expected_output = ([''], 6, 1)
    for i in range(3):
        assert output[i] == expected_output[i]

    record = record.transform(promo_key='1_2')
    output = get_parameters_for_window_sum(record, 0, 7)
    expected_output = (['1_2', '1', '2', ''], 7, 1 / 2)
    for i in range(3):
        assert output[i] == expected_output[i]


if __name__ == '__main__':
    test_parse_windows()
    test_get_rounded_percentage()
    test_get_distribution()
    test_features_density_mapper()
    test_get_window_sum()
    test_get_promos_subset_params()
    test_get_parameters_for_window_sum()
    test_density_mapper()
