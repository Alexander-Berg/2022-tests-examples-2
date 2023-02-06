from nile.api.v1 import Record
from nile.api.v1 import clusters
from nile.api.v1.local import StreamSource, ListSink

from projects.couriers_doxgety.target import Target

SEC_IN_DAY = 60 * 60 * 24


def test_target():

    orders_input = [
        Record(courier_id=2109107, timestamp=1618531200),
        Record(courier_id=2109107, timestamp=1618531200 + SEC_IN_DAY * 7),
        Record(courier_id=2109107, timestamp=1618531200 + SEC_IN_DAY * 7 + 1),
        Record(courier_id=1111111, timestamp=1618531200 - 1),
        Record(courier_id=1111111, timestamp=1618531200),
        Record(courier_id=1111111, timestamp=1618531200 + SEC_IN_DAY * 7 - 1),
        Record(courier_id=1111111, timestamp=1618531200 + SEC_IN_DAY * 7),
    ]

    timepoints_input = [
        Record(
            courier_id=1111111,
            work_status='active',
            timestamp=1618531200,
            timepoint_id='2021-04-16_1111111',
        ),
        Record(
            courier_id=1111111,
            work_status='active',
            timestamp=1618444800,
            timepoint_id='2021-04-15_1111111',
        ),
        Record(
            courier_id=2109107,
            work_status='lost',
            timestamp=1618531200,
            timepoint_id='2021-04-16_2109107',
        ),
    ]

    expected_output = [
        Record(timepoint_id='2021-04-16_1111111', target_w7=2),
        Record(timepoint_id='2021-04-15_1111111', target_w7=2),
        Record(timepoint_id='2021-04-16_2109107', target_w7=1),
    ]
    output = []

    job = clusters.MockCluster().job()

    Target('courier_id', [7]).expand(
        job,
        job.table('').label('orders_input'),
        job.table('').label('timepoints_input'),
    ).put('').label('output')

    job.local_run(
        sources={
            'orders_input': StreamSource(orders_input),
            'timepoints_input': StreamSource(timepoints_input),
        },
        sinks={'output': ListSink(output)},
    )
    assert output == expected_output


if __name__ == '__main__':
    test_target()
