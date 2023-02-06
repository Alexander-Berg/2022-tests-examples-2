import datetime

from nile.api.v1 import Record, clusters
from nile.api.v1.local import StreamSource, ListSink

from projects.autoorder.offline_exps.get_pred_and_safety_stock import (
    data_reducer,
)


def test_data_reducer():
    test_input = [
        Record(
            {
                'key': 1,
                'path': 'path1/2021-06',
                '_origin_name': '2021-06-01',
                '2021-06-01': 1,
                '2021-06-02': 2,
                '2021-06-03': 3,
            },
        ),
        Record(
            {
                'key': 1,
                'path': 'path1/2021-06-04',
                '2021-06-04': 4,
                '2021-06-05': 5,
                '2021-06-06': 6,
            },
        ),
        Record(
            {
                'key': 1,
                'path': 'path1/2021-06-05',
                '2021-06-05': 7,
                '2021-06-06': 8,
                '2021-06-07': 9,
            },
        ),
        Record(
            {
                'key': 1,
                'path': 'path1/2021-06-06',
                '2021-06-05': 10,
                '2021-06-06': 11,
                '2021-06-07': 12,
            },
        ),
        Record(
            {
                'key': 1,
                'path': 'path2/2021-06-05',
                '2021-06-05': 1,
                '2021-06-06': 2,
                '2021-06-07': 3,
            },
        ),
        Record(
            {
                'key': 1,
                'path': 'path2/2021-06-06',
                '2021-06-06': 4,
                '2021-06-07': 5,
                '2021-06-08': 6,
            },
        ),
        Record(
            {
                'key': 1,
                'days_between_supply': 1,
                'shelf_life': 3,
                'path': 'path3/2021-06-01',
                'q50': 1,
                'q60': 2,
                'q70': 3,
            },
        ),
        Record(
            {
                'key': 1,
                'days_between_supply': 1,
                'shelf_life': 3,
                'path': 'path3/2021-06-02',
                'q50': 4,
                'q60': 5,
                'q70': 6,
            },
        ),
        Record(
            {
                'key': 1,
                'days_between_supply': 1,
                'shelf_life': 3,
                'path': 'path3/2021-06-03',
                'q50': 7,
                'q60': 8,
                'q70': 9,
            },
        ),
        Record(
            {
                'key': 1,
                'days_between_supply': 2,
                'shelf_life': 3,
                'path': 'path3/2021-06-01',
                'q50': 10,
                'q60': 11,
                'q70': 12,
            },
        ),
        Record(
            {
                'key': 1,
                'days_between_supply': 2,
                'shelf_life': 3,
                'path': 'path3/2021-06-02',
                'q50': 13,
                'q60': 14,
                'q70': 15,
            },
        ),
        Record(
            {
                'key': 1,
                'days_between_supply': 2,
                'shelf_life': 3,
                'path': 'path3/2021-06-03',
                'q50': 16,
                'q60': 17,
                'q70': 18,
            },
        ),
        Record(
            {
                'key': 1,
                'days_between_supply': 1,
                'path': 'path4/2021-06-05',
                'q50': 19,
                'q60': 20,
                'q70': 21,
            },
        ),
    ]

    expected_output = [
        Record(
            key=1,
            pred1=[1, 0, 0, 4, 7, 8],
            pred2=[0, 0, 0, 0, 1, 2],
            stock1={'1': [3, 6, 9, 0, 0, 0], '2': [12, 15, 18, 0, 0, 0]},
            stock2={'1': [0, 0, 0, 0, 20, 0]},
        ),
    ]
    output = []

    job = clusters.MockCluster().job()

    job.table('').label('input').groupby('key').reduce(
        data_reducer(
            start_dttm=datetime.datetime.strptime('2021-06-01', '%Y-%m-%d'),
            days_num=6,
            pred_config={
                'pred1': {'paths': ['path1'], 'pred_period': 2},
                'pred2': {'paths': ['path2'], 'pred_period': 2},
            },
            sfs_config={
                'stock1': {
                    'paths': ['path3'],
                    'field_config': {1: 'q50', 2: 'q70'},
                },
                'stock2': {'paths': ['path4'], 'field_config': 'q60'},
            },
        ),
    ).put('').label('output')

    job.local_run(
        sources={'input': StreamSource(test_input)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 1
    assert output[0] == expected_output[0]


if __name__ == '__main__':
    test_data_reducer()
