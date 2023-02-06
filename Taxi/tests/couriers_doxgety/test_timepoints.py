import datetime

from nile.api.v1 import Record
from nile.api.v1 import clusters
from nile.api.v1.local import StreamSource, ListSink

from projects.couriers_doxgety.timepoints import StatusRangeTimepoints


def test_status_range_timepoints():

    status_history_input = [
        Record(
            courier_id=2109107,
            new_status='active',
            old_status='inactive',
            date='2021-04-14',
            timestamp=1618411909,
        ),
        Record(
            courier_id=2109107,
            new_status='blocked',
            old_status='active',
            date='2021-04-14',
            timestamp=1618414748,
        ),
        Record(
            courier_id=2109107,
            new_status='active',
            old_status='blocked',
            date='2021-04-14',
            timestamp=1618415476,
        ),
        Record(
            courier_id=2109107,
            new_status='lost',
            old_status='active',
            date='2021-04-15',
            timestamp=1618458167,
        ),
        Record(
            courier_id=2109107,
            new_status='active',
            old_status='lost',
            date='2021-04-16',
            timestamp=1618544538,
        ),
        Record(
            courier_id=2480355,
            new_status='lost',
            old_status='active',
            date='2021-04-15',
            timestamp=1618489718,
        ),
        Record(
            courier_id=2480355,
            new_status='blocked',
            old_status='lost',
            date='2021-04-15',
            timestamp=1618544538,
        ),
        Record(
            courier_id=2480355,
            new_status='active',
            old_status='blocked',
            date='2021-04-16',
            timestamp=1618566283,
        ),
        Record(
            courier_id=2480355,
            new_status='blocked',
            old_status='active',
            date='2021-04-16',
            timestamp=1618566329,
        ),
    ]

    current_status_input = [
        Record(courier_id=2109107, work_status='active'),
        Record(courier_id=2480355, work_status='blocked'),
        Record(courier_id=1111111, work_status='active'),
    ]

    expected_output = [
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
            courier_id=1111111,
            work_status='active',
            timestamp=1618358400,
            timepoint_id='2021-04-14_1111111',
        ),
        Record(
            courier_id=2109107,
            work_status='lost',
            timestamp=1618531200,
            timepoint_id='2021-04-16_2109107',
        ),
        Record(
            courier_id=2109107,
            work_status='active',
            timestamp=1618444800,
            timepoint_id='2021-04-15_2109107',
        ),
    ]
    output = []

    job = clusters.MockCluster().job()

    StatusRangeTimepoints(
        datetime.datetime.strptime('2021-04-14', '%Y-%m-%d'),
        datetime.datetime.strptime('2021-04-16', '%Y-%m-%d'),
        'courier_id',
    ).apply(
        job,
        job.table('').label('current_status_input'),
        job.table('').label('status_history_input'),
    ).put(
        '',
    ).label(
        'output',
    )

    job.local_run(
        sources={
            'current_status_input': StreamSource(current_status_input),
            'status_history_input': StreamSource(status_history_input),
        },
        sinks={'output': ListSink(output)},
    )
    assert output == expected_output


if __name__ == '__main__':
    test_status_range_timepoints()
