from nile.api.v1 import Record
from nile.api.v1 import clusters
from nile.api.v1.local import StreamSource, ListSink

from projects.autoorder.apply_metrics import blackout_reducer, prices_reducer


def make_records_from_lists(fields, values_lists):
    return [Record(**dict(zip(fields, values))) for values in values_lists]


def test_blackout_reducer():
    test_input = [
        Record(key=1, sort_field=0, residuals=0, max_residuals=0),
        Record(key=1, sort_field=1, residuals=0, max_residuals=0),
        Record(key=1, sort_field=2, residuals=1, max_residuals=2),
        Record(key=1, sort_field=3, residuals=2, max_residuals=3),
        Record(key=1, sort_field=4, residuals=0, max_residuals=0),
        Record(key=1, sort_field=5, residuals=0, max_residuals=0),
        Record(key=1, sort_field=6, residuals=0, max_residuals=4),
        Record(key=1, sort_field=7, residuals=0, max_residuals=0),
    ]

    expected_output = [
        Record(key=1, sort_field=0, residuals=1, max_residuals=0),
        Record(key=1, sort_field=1, residuals=1, max_residuals=0),
        Record(key=1, sort_field=2, residuals=1, max_residuals=2),
        Record(key=1, sort_field=3, residuals=2, max_residuals=3),
        Record(key=1, sort_field=4, residuals=2, max_residuals=0),
        Record(key=1, sort_field=5, residuals=2, max_residuals=0),
        Record(key=1, sort_field=6, residuals=0, max_residuals=4),
        Record(key=1, sort_field=7, residuals=0, max_residuals=0),
    ]
    output = []

    job = clusters.MockCluster().job()

    job.table('').label('input').groupby('key').sort('sort_field').reduce(
        blackout_reducer(),
    ).put('').label('output')

    job.local_run(
        sources={'input': StreamSource(test_input)},
        sinks={'output': ListSink(output)},
    )
    assert output == expected_output


def test_prices_reducer():
    price_fields = [
        'code',
        'organization_id',
        'date',
        'sort_priority',
        'purchases_cost',
        'purchases_vat',
        'sales_quantity',
        'price_wo_vat',
        'sales_vat',
    ]

    price_values_list = [
        [1, 1, '2021-01-27', 0, 1, 1, 0, None, None],
        [1, 1, '2021-01-28', 0, 1, 1, 1, 2, 1],
        [1, 1, '2021-01-29', 0, 1, 1, 0, None, None],
        [1, 1, '2021-01-30', 0, 1, 1, 0, None, None],
        [1, 1, '2021-02-01', 0, 2, 1, 0, None, None],
        [1, 1, '2021-02-02', 0, 2, 1, 1, 2.5, 1],
        [1, 1, '2021-02-03', 0, 3, 1, 2, 5, 2],
    ]

    assortment_fields = ['code', 'organization_id', 'date', 'sort_priority']
    assortment_values_list = [
        [1, 1, '2021-01-26', 1],
        [1, 1, '2021-02-01', 1],
        [1, 1, '2021-02-02', 1],
        [1, 1, '2021-02-07', 1],
    ]

    output_fields = [
        'code',
        'organization_id',
        'date',
        'purchases_price_wo_vat',
        'purchases_price',
        'sales_price_wo_vat',
        'sales_price',
        'margin',
    ]
    output_values_list = [
        [1, 1, '2021-01-26', None, None, None, None, None],
        [1, 1, '2021-02-01', 2, 3, 2, 3, 1],
        [1, 1, '2021-02-02', 2, 3, 2.5, 3.5, 0.5],
        [1, 1, '2021-02-07', 3, 4, 2.5, 3.5, 0],
    ]

    prices_input = make_records_from_lists(price_fields, price_values_list)

    assortment_input = make_records_from_lists(
        assortment_fields, assortment_values_list,
    )

    expected_output = make_records_from_lists(
        output_fields, output_values_list,
    )
    output = []

    job = clusters.MockCluster().job()

    job.concat(
        job.table('').label('prices_input'),
        job.table('').label('assortment_input'),
    ).groupby('code', 'organization_id').sort('date', 'sort_priority').reduce(
        prices_reducer(),
    ).put(
        '',
    ).label(
        'output',
    )

    job.local_run(
        sources={
            'prices_input': StreamSource(prices_input),
            'assortment_input': StreamSource(assortment_input),
        },
        sinks={'output': ListSink(output)},
    )
    assert output == expected_output


if __name__ == '__main__':
    test_blackout_reducer()
    test_prices_reducer()
