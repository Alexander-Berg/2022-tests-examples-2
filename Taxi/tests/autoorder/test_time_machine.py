from nile.api.v1 import Record
from nile.api.v1 import clusters
from nile.api.v1.local import StreamSource, ListSink

from projects.autoorder.time_machine import TimeMachine


def test_time_machine():
    stream_input = [
        Record(key=1, timestamp=8, n_units_of_sku=8),
        Record(key=1, timestamp=5, n_units_of_sku=5),
        Record(key=1, timestamp=10, n_units_of_sku=10),
        Record(key=1, timestamp=1, n_units_of_sku=1),
        Record(key=1, timestamp=7, n_units_of_sku=7),
        Record(key=1, timestamp=3, n_units_of_sku=3),
        Record(key=1, timestamp=9, n_units_of_sku=9),
        Record(key=1, timestamp=12, n_units_of_sku=12),
        Record(key=1, timestamp=4, n_units_of_sku=4),
        Record(key=1, timestamp=11, n_units_of_sku=11),
        Record(key=1, timestamp=2, n_units_of_sku=2),
        Record(key=1, timestamp=0, n_units_of_sku=0),
        Record(key=1, timestamp=6, n_units_of_sku=6),
    ]
    timepoints_input = [
        Record(key=1, timestamp=5, timepoint_id='_'),
        Record(key=1, timestamp=6, timepoint_id='_'),
    ]
    expected_output_1 = [
        Record(
            key=1,
            timestamp=5,
            timepoint_id='_',
            history=[
                dict(key=1, timestamp=0, n_units_of_sku=0),
                dict(key=1, timestamp=1, n_units_of_sku=1),
                dict(key=1, timestamp=2, n_units_of_sku=2),
                dict(key=1, timestamp=3, n_units_of_sku=3),
                dict(key=1, timestamp=4, n_units_of_sku=4),
            ],
        ),
        Record(
            key=1,
            timestamp=6,
            timepoint_id='_',
            history=[
                dict(key=1, timestamp=1, n_units_of_sku=1),
                dict(key=1, timestamp=2, n_units_of_sku=2),
                dict(key=1, timestamp=3, n_units_of_sku=3),
                dict(key=1, timestamp=4, n_units_of_sku=4),
                dict(key=1, timestamp=5, n_units_of_sku=5),
            ],
        ),
    ]
    expected_output_2 = [
        Record(
            key=1,
            timestamp=6,
            timepoint_id='_',
            minus_timestamp=-6,
            history=[
                dict(
                    key=1,
                    timestamp=11,
                    n_units_of_sku=11,
                    minus_timestamp=-11,
                ),
                dict(
                    key=1,
                    timestamp=10,
                    n_units_of_sku=10,
                    minus_timestamp=-10,
                ),
                dict(key=1, timestamp=9, n_units_of_sku=9, minus_timestamp=-9),
                dict(key=1, timestamp=8, n_units_of_sku=8, minus_timestamp=-8),
                dict(key=1, timestamp=7, n_units_of_sku=7, minus_timestamp=-7),
            ],
        ),
        Record(
            key=1,
            timestamp=5,
            timepoint_id='_',
            minus_timestamp=-5,
            history=[
                dict(
                    key=1,
                    timestamp=10,
                    n_units_of_sku=10,
                    minus_timestamp=-10,
                ),
                dict(key=1, timestamp=9, n_units_of_sku=9, minus_timestamp=-9),
                dict(key=1, timestamp=8, n_units_of_sku=8, minus_timestamp=-8),
                dict(key=1, timestamp=7, n_units_of_sku=7, minus_timestamp=-7),
                dict(key=1, timestamp=6, n_units_of_sku=6, minus_timestamp=-6),
            ],
        ),
    ]
    output = []
    job = clusters.MockCluster().job()

    TimeMachine(keys=['key'], max_history_seconds=5, reverse=False).expand(
        job,
        job.table('').label('stream_input'),
        job.table('').label('timepoints_input'),
    ).put('').label('output')

    job.local_run(
        sources={
            'stream_input': StreamSource(stream_input),
            'timepoints_input': StreamSource(timepoints_input),
        },
        sinks={'output': ListSink(output)},
    )

    assert len(output) == len(expected_output_1)
    for i in range(len(output)):
        assert output[i] == expected_output_1[i]

    output = []
    job = clusters.MockCluster().job()

    TimeMachine(keys=['key'], max_history_seconds=5, reverse=True).expand(
        job,
        job.table('').label('stream_input'),
        job.table('').label('timepoints_input'),
    ).put('').label('output')

    job.local_run(
        sources={
            'stream_input': StreamSource(stream_input),
            'timepoints_input': StreamSource(timepoints_input),
        },
        sinks={'output': ListSink(output)},
    )

    assert len(output) == len(expected_output_2)
    for i in range(len(output)):
        assert output[i] == expected_output_2[i]


if __name__ == '__main__':
    test_time_machine()
