from collections import Counter

from nile.api.v1 import Record, clusters
from nile.api.v1.local import StreamSource, ListSink

from projects.autoorder.demand_restore.distributions.get_aggregations import (
    _purchases_for_store_reducer,
    _neighbors_reducer,
    _count_reducer,
    _agg_reducer,
)


def test_purchases_for_store_reducer():
    codes_in_cat = {'cat_1': {1, 2, 3, 4}, 'cat_2': {5, 6, 7, 8}}
    codes_in_subcat = {
        ('cat_1', 'subcat_1'): {1, 2},
        ('cat_1', 'subcat_2'): {3, 4},
        ('cat_2', 'subcat_3'): {5, 6},
        ('cat_2', 'subcat_4'): {7, 8},
    }
    cat_dict = {
        1: 'cat_1',
        3: 'cat_1',
        4: 'cat_1',
        5: 'cat_2',
        7: 'cat_2',
        8: 'cat_2',
    }
    subcat_dict = {
        1: 'subcat_1',
        3: 'subcat_2',
        4: 'subcat_2',
        5: 'subcat_3',
        7: 'subcat_4',
        8: 'subcat_4',
    }

    test_input = [
        Record(
            key=1,
            code=3,
            category='cat_1',
            subcategory='subcat_2',
            n_units_of_sku=2,
            neighbors={'7': 2},
        ),
        Record(
            key=1,
            code=4,
            category='cat_1',
            subcategory='subcat_2',
            n_units_of_sku=0,
            neighbors=None,
        ),
        Record(
            key=1,
            code=7,
            category='cat_2',
            subcategory='subcat_4',
            n_units_of_sku=3,
            neighbors={'3': 1, '8': 1},
        ),
        Record(
            key=1,
            code=8,
            category='cat_2',
            subcategory='subcat_4',
            n_units_of_sku=3,
            neighbors={'7': 1, '1': 3, '5': 2},
        ),
        Record(
            key=1,
            code=1,
            category='cat_1',
            subcategory='subcat_1',
            n_units_of_sku=5,
            neighbors={'8': 1, '5': 2},
        ),
        Record(
            key=1,
            code=5,
            category='cat_2',
            subcategory='subcat_3',
            n_units_of_sku=2,
            neighbors={'8': 1, '1': 3},
        ),
    ]

    expected_output = [
        Record(
            key=1,
            code=3,
            category='cat_1',
            subcategory='subcat_2',
            n_units_of_sku=2,
            neighbors={'7': 2},
            org_sum=15,
            org_sum_cat=7,
            org_sum_subcat=2,
            org_sum_wo_n=13,
            org_sum_cat_wo_n=7,
            org_sum_subcat_wo_n=2,
            org_cnt=5,
            org_cnt_cat=2,
            org_cnt_subcat=1,
            org_cnt_wo_n=5,
            org_cnt_cat_wo_n=2,
            org_cnt_subcat_wo_n=1,
        ),
        Record(
            key=1,
            code=4,
            category='cat_1',
            subcategory='subcat_2',
            n_units_of_sku=0,
            neighbors=None,
            org_sum=15,
            org_sum_cat=7,
            org_sum_subcat=2,
            org_sum_wo_n=15,
            org_sum_cat_wo_n=7,
            org_sum_subcat_wo_n=2,
            org_cnt=5,
            org_cnt_cat=2,
            org_cnt_subcat=1,
            org_cnt_wo_n=5,
            org_cnt_cat_wo_n=2,
            org_cnt_subcat_wo_n=1,
        ),
        Record(
            key=1,
            code=7,
            category='cat_2',
            subcategory='subcat_4',
            n_units_of_sku=3,
            neighbors={'3': 1, '8': 1},
            org_sum=15,
            org_sum_cat=8,
            org_sum_subcat=6,
            org_sum_wo_n=13,
            org_sum_cat_wo_n=7,
            org_sum_subcat_wo_n=5,
            org_cnt=5,
            org_cnt_cat=3,
            org_cnt_subcat=2,
            org_cnt_wo_n=5,
            org_cnt_cat_wo_n=3,
            org_cnt_subcat_wo_n=2,
        ),
        Record(
            key=1,
            code=8,
            category='cat_2',
            subcategory='subcat_4',
            n_units_of_sku=3,
            neighbors={'7': 1, '1': 3, '5': 2},
            org_sum=15,
            org_sum_cat=8,
            org_sum_subcat=6,
            org_sum_wo_n=9,
            org_sum_cat_wo_n=5,
            org_sum_subcat_wo_n=5,
            org_cnt=5,
            org_cnt_cat=3,
            org_cnt_subcat=2,
            org_cnt_wo_n=4,
            org_cnt_cat_wo_n=2,
            org_cnt_subcat_wo_n=2,
        ),
        Record(
            key=1,
            code=1,
            category='cat_1',
            subcategory='subcat_1',
            n_units_of_sku=5,
            neighbors={'8': 1, '5': 2},
            org_sum=15,
            org_sum_cat=7,
            org_sum_subcat=5,
            org_sum_wo_n=12,
            org_sum_cat_wo_n=7,
            org_sum_subcat_wo_n=5,
            org_cnt=5,
            org_cnt_cat=2,
            org_cnt_subcat=1,
            org_cnt_wo_n=4,
            org_cnt_cat_wo_n=2,
            org_cnt_subcat_wo_n=1,
        ),
        Record(
            key=1,
            code=5,
            category='cat_2',
            subcategory='subcat_3',
            n_units_of_sku=2,
            neighbors={'8': 1, '1': 3},
            org_sum=15,
            org_sum_cat=8,
            org_sum_subcat=2,
            org_sum_wo_n=11,
            org_sum_cat_wo_n=7,
            org_sum_subcat_wo_n=2,
            org_cnt=5,
            org_cnt_cat=3,
            org_cnt_subcat=1,
            org_cnt_wo_n=5,
            org_cnt_cat_wo_n=3,
            org_cnt_subcat_wo_n=1,
        ),
    ]
    output = []

    job = clusters.MockCluster().job()

    job.table('').label('input').groupby('key').reduce(
        _purchases_for_store_reducer(
            codes_in_cat=codes_in_cat,
            codes_in_subcat=codes_in_subcat,
            cat_dict=cat_dict,
            subcat_dict=subcat_dict,
        ),
    ).put('').label('output')

    job.local_run(
        sources={'input': StreamSource(test_input)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == len(expected_output)
    for i in range(len(output)):
        assert output[i] == expected_output[i]


def test_neighbors_reducer():
    test_input = [
        Record(key=1, code=1, order_id=1, quantity=1),
        Record(key=1, code=1, order_id=2, quantity=3),
        Record(key=1, code=3, order_id=1, quantity=3),
        Record(key=1, code=3, order_id=3, quantity=1),
        Record(key=1, code=3, order_id=4, quantity=1),
        Record(key=1, code=4, order_id=2, quantity=1),
        Record(key=1, code=5, order_id=2, quantity=1),
    ]

    expected_output = [
        Record(key=1, code=1, neighbors=Counter({'3': 3, '4': 1, '5': 1})),
        Record(key=1, code=3, neighbors=Counter({'1': 1})),
        Record(key=1, code=4, neighbors=Counter({'1': 3, '5': 1})),
        Record(key=1, code=5, neighbors=Counter({'1': 3, '4': 1})),
    ]
    output = []

    job = clusters.MockCluster().job()

    job.table('').label('input').groupby('key').reduce(
        _neighbors_reducer(),
    ).put('').label('output')

    job.local_run(
        sources={'input': StreamSource(test_input)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == len(expected_output)
    for i in range(len(output)):
        assert output[i] == expected_output[i]


def test_count_reducer():
    test_input = [
        Record(
            key=1,
            hour_local=3,
            isoweekday_local=1,
            counter=2,
            org_sum=4,
            org_sum_cat=6,
            org_sum_subcat=8,
            org_sum_wo_n=10,
            org_sum_cat_wo_n=12,
            org_sum_subcat_wo_n=2,
            org_cnt=2,
            org_cnt_cat=3,
            org_cnt_subcat=4,
            org_cnt_wo_n=5,
            org_cnt_cat_wo_n=6,
            org_cnt_subcat_wo_n=7,
        ),
        Record(
            key=1,
            hour_local=3,
            isoweekday_local=1,
            counter=2,
            org_sum=2,
            org_sum_cat=2,
            org_sum_subcat=3,
            org_sum_wo_n=3,
            org_sum_cat_wo_n=3,
            org_sum_subcat_wo_n=3,
            org_cnt=1,
            org_cnt_cat=1,
            org_cnt_subcat=1,
            org_cnt_wo_n=1,
            org_cnt_cat_wo_n=1,
            org_cnt_subcat_wo_n=1,
        ),
    ]

    expected_output = [
        Record(
            key=1,
            const_field=1,
            counter=[0] * 3 + [4] + [0] * 164,
            counter_cnt=[0] * 3 + [2] + [0] * 164,
            org_cnt=[0] * 3 + [3] + [0] * 164,
            org_cnt_cat=[0] * 3 + [4] + [0] * 164,
            org_cnt_subcat=[0] * 3 + [5] + [0] * 164,
            org_cnt_wo_n=[0] * 3 + [6] + [0] * 164,
            org_cnt_cat_wo_n=[0] * 3 + [7] + [0] * 164,
            org_cnt_subcat_wo_n=[0] * 3 + [8] + [0] * 164,
            org_sum=[0] * 3 + [6] + [0] * 164,
            org_sum_cat=[0] * 3 + [8] + [0] * 164,
            org_sum_subcat=[0] * 3 + [11] + [0] * 164,
            org_sum_wo_n=[0] * 3 + [13] + [0] * 164,
            org_sum_cat_wo_n=[0] * 3 + [15] + [0] * 164,
            org_sum_subcat_wo_n=[0] * 3 + [5] + [0] * 164,
        ),
    ]

    fields_to_agg = [
        'counter',
        'counter_cnt',
        'org_cnt',
        'org_cnt_cat',
        'org_cnt_subcat',
        'org_cnt_wo_n',
        'org_cnt_cat_wo_n',
        'org_cnt_subcat_wo_n',
        'org_sum',
        'org_sum_cat',
        'org_sum_subcat',
        'org_sum_wo_n',
        'org_sum_cat_wo_n',
        'org_sum_subcat_wo_n',
    ]
    output = []

    job = clusters.MockCluster().job()

    job.table('').label('input').groupby('key').reduce(
        _count_reducer(fields_to_agg=fields_to_agg),
    ).put('').label('output')

    job.local_run(
        sources={'input': StreamSource(test_input)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == len(expected_output)
    for i in range(len(output)):
        assert output[i] == expected_output[i]


def test_agg_reducer():
    test_input = [
        Record(
            key=1,
            counter=[0] * 3 + [4] + [0] * 164,
            counter_cnt=[0] * 3 + [2] + [0] * 164,
        ),
        Record(
            key=1,
            counter=[0] * 3 + [3] + [0] * 164,
            counter_cnt=[0] * 3 + [2] + [0] * 164,
        ),
        Record(
            key=1,
            counter=[0] * 3 + [0] + [0] * 164,
            counter_cnt=[0] * 3 + [2] + [0] * 164,
        ),
        Record(
            key=1,
            counter=[0] * 3 + [2] + [0] * 164,
            counter_cnt=[0] * 3 + [3] + [0] * 164,
        ),
    ]

    expected_output = [
        Record(
            key=1,
            agg=[0] * 3 + [9] + [0] * 164,
            agg_cnt=[0] * 3 + [9] + [0] * 164,
        ),
    ]
    output = []

    job = clusters.MockCluster().job()

    job.table('').label('input').groupby('key').reduce(
        _agg_reducer('agg'),
    ).put('').label('output')

    job.local_run(
        sources={'input': StreamSource(test_input)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == len(expected_output)
    for i in range(len(output)):
        assert output[i] == expected_output[i]


if __name__ == '__main__':
    test_purchases_for_store_reducer()
    test_neighbors_reducer()
    test_count_reducer()
    test_agg_reducer()
