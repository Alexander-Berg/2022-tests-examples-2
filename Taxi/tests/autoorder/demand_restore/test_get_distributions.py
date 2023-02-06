import numpy as np
import pandas as pd

from nile.api.v1 import Record

from projects.autoorder.demand_restore.distributions.get_distributions import (
    make_aggregation_dict,
    get_neighbors_agg_name,
    make_aggregations,
    get_agg_key,
    get_sorted_filtered_aggregations,
    get_stores_nonworking_hours,
    counters_to_num,
    get_winner,
    normalize_weights,
    calc_weights,
    get_distribution,
    moving_average,
)


def test_make_aggregation_dict():
    df = pd.DataFrame(
        data=[
            ['Bakery', 'Израиль', [2] * 168, [1] * 168],
            ['Напитки', 'Россия', [1] * 168, [2] * 168],
        ],
        columns=['category', 'country', 'counter_cat', 'counter_cat_cnt'],
    )

    assert make_aggregation_dict(df=df, agg_name='counter_cat') == {
        ('Bakery', 'Израиль'): ([2] * 168, [1] * 168),
        ('Напитки', 'Россия'): ([1] * 168, [2] * 168),
    }

    df = pd.DataFrame(
        data=[
            ['Израиль', [2] * 168, [1] * 168],
            ['Россия', [1] * 168, [2] * 168],
        ],
        columns=['country', 'counter_country', 'counter_country_cnt'],
    )

    assert make_aggregation_dict(df=df, agg_name='counter_country') == {
        'Израиль': ([2] * 168, [1] * 168),
        'Россия': ([1] * 168, [2] * 168),
    }

    df = pd.DataFrame(
        data=[[1, [2] * 168, [1] * 168]],
        columns=['const_field', 'counter_all', 'counter_all_cnt'],
    )

    assert make_aggregation_dict(df=df, agg_name='counter_all') == {
        1: ([2] * 168, [1] * 168),
    }


def test_get_neighbors_agg_name():
    assert get_neighbors_agg_name('counter_all') == 'org_{}'
    assert get_neighbors_agg_name('counter_org') == 'org_{}'
    assert get_neighbors_agg_name('counter_cat_org') == 'org_{}_cat'
    assert get_neighbors_agg_name('counter_subcat_org') == 'org_{}_subcat'
    assert get_neighbors_agg_name('counter_code_reg') is None
    assert get_neighbors_agg_name('counter_code') is None
    assert get_neighbors_agg_name('counter_code_org') is None
    assert get_neighbors_agg_name('counter_cat') == 'org_{}_cat'
    assert get_neighbors_agg_name('counter_reg') == 'org_{}'
    assert get_neighbors_agg_name('counter_subcat_org_past') is None


def test_get_agg_key():
    input_record = Record(
        const_field=1,
        code=111,
        organization_id=222,
        category='Напитки',
        subcategory='Вода',
        region=2,
        country='Россия',
    )
    assert get_agg_key(input_record, 'counter_all') == 1
    assert get_agg_key(input_record, 'counter_org') == 222
    assert get_agg_key(input_record, 'counter_subcat_org') == (
        222,
        'Напитки',
        'Вода',
    )


def test_make_aggregations():
    input_record = Record(
        code=1111,
        organization_id=2222,
        const_field=1,
        category='Напитки',
        subcategory='Вода',
        country='Россия',
        region=2,
        counter=[3] + [0] * 167,
        counter_cnt=[4] + [0] * 167,
        org_cnt=[5] + [0] * 167,
        org_cnt_cat=[3] + [0] * 167,
        org_cnt_subcat=[2] + [0] * 167,
        org_cnt_wo_n=[5] + [0] * 167,
        org_cnt_cat_wo_n=[3] + [0] * 167,
        org_cnt_subcat_wo_n=[2] + [0] * 167,
        org_sum=[11] + [0] * 167,
        org_sum_cat=[8] + [0] * 167,
        org_sum_subcat=[6] + [0] * 167,
        org_sum_wo_n=[13] + [0] * 167,
        org_sum_cat_wo_n=[7] + [0] * 167,
        org_sum_subcat_wo_n=[5] + [0] * 167,
        counter_past=[5] + [0] * 167,
        counter_cnt_past=[5] + [0] * 167,
    )

    agg_dct = dict(
        counter_cat={
            ('Напитки', 'Россия'): ([26] + [0] * 167, [23] + [0] * 167),
        },
        counter_all={1: ([32] + [0] * 167, [48] + [0] * 167)},
    )

    assert (
        make_aggregations(
            record=input_record,
            agg_dct=agg_dct,
            aggregations=['counter_cat', 'counter_past', 'counter_all'],
        )
        == {
            'counter_cat': ([22] + [0] * 167, [19] + [0] * 167),
            'counter_past': ([5] + [0] * 167, [5] + [0] * 167),
            'counter_all': ([31] + [0] * 167, [44] + [0] * 167),
        }
    )


def test_get_sorted_filtered_aggregations():
    input_agg_counters = {
        'counter_cat': ([65, 70] + [1] * 166, [60, 73] + [1] * 166),
        'counter_all': ([100, 200] + [1] * 166, [136, 132] + [1] * 166),
        'counter_org': ([7, 0] + [1] * 166, [16, 12] + [1] * 166),
        'counter_code': ([53, 25] + [0] * 166, [59, 50] + [0] * 166),
        'counter_code_org': ([0, 0] + [0] * 166, [21, 17] + [0] * 166),
        'counter_subcat_org': ([0, 0] + [0] * 166, [0, 0] + [1] * 166),
    }

    assert get_sorted_filtered_aggregations(input_agg_counters) == [
        'counter_all',
        'counter_cat',
        'counter_org',
    ]
    assert get_sorted_filtered_aggregations(
        input_agg_counters, min_purchases=176,
    ) == ['counter_all', 'counter_cat']


def test_get_stores_nonworking_hours():
    assert get_stores_nonworking_hours(
        counter_org=[0, 0, 0, 1, 1, 0] + [1] * 162 + [0],
    ) == {0, 1, 2, 5}


def test_counters_to_num():
    input_tuple = (
        [22, 16, 10, 11, 16] + [0] * 163,
        [32, 29, 20, 28, 25] + [0] * 163,
    )
    input_org_zeros = {1, 3}

    output = counters_to_num(
        counters_tuple=input_tuple, org_zeros=input_org_zeros,
    )

    np.testing.assert_almost_equal(
        output,
        [0.376196, 0.0, 0.273597, 0.0, 0.350205] + [0] * 163,
        decimal=4,
    )


def test_get_winner():
    counter = [1, 1, 0, 0, 0, 0, 2, 0] + [0] * 160
    distributions = {
        'counter_cat': [0.5, 0.5, 0, 0, 0, 0, 0, 0] + [0] * 160,
        'counter_all': [0.33, 0.33, 0, 0, 0, 0, 0.33, 0] + [0] * 160,
        'counter_org': [0.25, 0.25, 0, 0, 0, 0, 0.5, 0] + [0] * 160,
        'counter_subcat': [0, 0, 0, 0.5, 0.5, 0, 0, 0] + [0] * 160,
        'counter_code': [0, 0, 0, 0, 0, 0.5, 0, 0.5] + [0] * 160,
    }

    assert get_winner(counter, distributions, 0) == 'counter_org'
    assert get_winner(counter, distributions, 10) is None

    counter = [0] * 168
    assert get_winner(counter, distributions, 0) is None

    counter = [1, 1, 0, 0, 0, 0, 2, 0] + [0] * 160
    distributions = {
        'counter_subcat': [0, 0, 0, 0.5, 0.5, 0, 0, 0] + [0] * 160,
        'counter_code': [0, 0, 0, 0, 0, 0.5, 0, 0.5] + [0] * 160,
    }
    assert get_winner(counter, distributions, 0) is None


def test_normalize_weights():
    assert normalize_weights({'a': 2, 'b': 7, 'c': 8}, 17, 101) == {
        'a': 11,
        'b': 41,
        'c': 47,
    }

    assert normalize_weights({'a': 51, 'b': 11, 'c': 22}, 84, 101) == {
        'a': 61,
        'b': 13,
        'c': 26,
    }


def test_calc_weights():
    weights_by_code = {'a': 2, 'b': 7, 'c': 8}
    weights_by_org = {'a': 51, 'b': 11, 'c': 22}

    assert calc_weights(
        weights_by_code, weights_by_org, norm_weights=True,
    ) == {'a': 53, 'b': 18, 'c': 30}
    assert calc_weights(
        weights_by_code, weights_by_org, norm_weights=False,
    ) == {'a': 53, 'b': 18, 'c': 30}

    weights_by_code = {'a': 602, 'b': 400, 'c': 800}
    weights_by_org = {'a': 130, 'b': 140, 'c': 205}

    assert calc_weights(
        weights_by_code, weights_by_org, norm_weights=True,
    ) == {'a': 1383, 'b': 1176, 'c': 1992}
    assert calc_weights(
        weights_by_code, weights_by_org, norm_weights=False,
    ) == {'a': 732, 'b': 540, 'c': 1005}


def test_get_distribution():
    record = Record(
        counter_cat_num=[0.25, 0.25, 0.25, 0.25] + [0] * 164,
        counter_code_num=[1, 0, 0, 0] + [0] * 164,
        counter_org_num=None,
        counter_country_num=[0.1, 0.2, 0.3, 0.4] + [0] * 164,
        counter_subcat_num=None,
        counter_past_num=None,
    )

    weights = {'counter_cat': 1, 'counter_code': 2, 'counter_org': 3}

    np.testing.assert_almost_equal(
        get_distribution(record, weights, {4, 167}, 0.5),
        [0.38461538, 0.42307692, 0.11538462, 0.07692308] + [0] * 164,
        decimal=4,
    )

    np.testing.assert_almost_equal(
        get_distribution(record, weights, {4, 167}, 0.2),
        [0.33766234, 0.33766234, 0.19480519, 0.12987013] + [0] * 164,
        decimal=4,
    )

    weights = {'counter_subcat': 3, 'counter_past': 1}
    np.testing.assert_almost_equal(
        get_distribution(record, weights, {4, 167}, 0.5),
        [0.12, 0.24, 0.36, 0.28] + [0] * 164,
        decimal=4,
    )


def test_moving_average():
    np.testing.assert_almost_equal(
        moving_average([1, 5, 2, 7, 4, 3, 7]),
        [
            4.33333333,
            2.66666667,
            4.66666667,
            4.33333333,
            4.66666667,
            4.66666667,
            3.66666667,
        ],
        decimal=2,
    )


if __name__ == '__main__':
    test_make_aggregation_dict()
    test_get_neighbors_agg_name()
    test_get_agg_key()
    test_make_aggregations()
    test_get_sorted_filtered_aggregations()
    test_get_stores_nonworking_hours()
    test_counters_to_num()
    test_get_winner()
    test_normalize_weights()
    test_calc_weights()
    test_get_distribution()
    test_moving_average()
