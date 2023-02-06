import datetime

from nile.api.v1 import Record, clusters
from nile.api.v1.local import StreamSource, ListSink

from projects.autoorder.offline_exps.get_demand_by_sampling import cube_reducer


def test_cube_reducer():
    def make_records(values_list, fields):
        records = []
        for values in values_list:
            values_dict = dict(zip(fields, values))
            records.append(Record(**values_dict))
        return records

    fields = ['key', 'date_local', 'hour_local', 'n_units_of_sku', 'residuals']
    values_list = [
        [1, '2021-06-01', 10, 1, 6],
        [1, '2021-06-01', 11, 2, 5],
        [1, '2021-06-01', 12, 3, 3],
        [1, '2021-06-02', 10, 4, 15],
        [1, '2021-06-02', 11, 5, 11],
        [1, '2021-06-02', 12, 6, 6],
        [1, '2021-06-03', 10, 0, 0],
        [1, '2021-06-03', 11, 0, 0],
        [1, '2021-06-03', 12, 7, 7],
        [1, '2021-06-04', 10, 8, 8],
        [1, '2021-06-04', 11, 0, 0],
        [1, '2021-06-04', 12, 0, 0],
        [1, '2021-06-05', 10, 9, 19],
        [1, '2021-06-05', 11, 10, 10],
        [1, '2021-06-05', 12, 0, 0],
        [1, '2021-06-06', 10, 0, 0],
        [1, '2021-06-06', 11, 0, 0],
        [1, '2021-06-06', 12, 0, 0],
    ]

    test_input = make_records(values_list, fields)

    expected_output = [
        Record(key=1, lower_demand=[8, 19, 0], upper_demand=[22, 19, 29]),
    ]
    output = []

    job = clusters.MockCluster().job()

    job.table('').label('input').groupby('key').reduce(
        cube_reducer(
            start_dttm=datetime.datetime.strptime('2021-06-04', '%Y-%m-%d'),
            days_num=3,
            history_days_num=3,
            first_work_hour=10,
            last_work_hour=12,
            nearby_hours_lag=1,
        ),
    ).put('').label('output')

    job.local_run(
        sources={'input': StreamSource(test_input)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 1
    assert output[0] == expected_output[0]


if __name__ == '__main__':
    test_cube_reducer()
