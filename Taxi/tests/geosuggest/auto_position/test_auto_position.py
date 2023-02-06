from nile.api.v1 import clusters, Record
from nile.api.v1.local import StreamSource, ListSink

from projects.geosuggest.auto_position.rec_sys.nile_blocks import data


order_records = [
    Record(user_id='aaa', timestamp=1700, order_id='aaa_3'),
    Record(user_id='aaa', timestamp=1100, order_id='aaa_2'),
    Record(user_id='aaa', timestamp=1000, order_id='aaa_1'),
]
request_records = [
    Record(user_id='aaa', _logfeller_timestamp=1200, is_exploration_mode=True),
    Record(
        user_id='aaa', _logfeller_timestamp=1020, is_exploration_mode=False,
    ),
    Record(user_id='aaa', _logfeller_timestamp=900, is_exploration_mode=True),
    Record(user_id='aaa', _logfeller_timestamp=880, is_exploration_mode=False),
    Record(user_id='aaa', _logfeller_timestamp=850, is_exploration_mode=False),
]
exploration_records = [
    Record(
        user_id='aaa',
        timestamp=1000,
        order_id='aaa_1',
        _logfeller_timestamp=900,
    ),
]
exploitation_records = [
    Record(
        user_id='aaa',
        _logfeller_timestamp=1020,
        timestamp=1100,
        order_id='aaa_2',
    ),
    Record(
        user_id='aaa',
        _logfeller_timestamp=850,
        timestamp=1000,
        order_id='aaa_1',
    ),
]


class TestTimestampReducer:
    def test_exploration_mode(self):
        job = clusters.MockCluster().job()
        exploration_stream = data.reduce_by_timestamp(
            orders=job.table('').label('orders'),
            requests=job.table('').label('requests'),
            exploration_mode=True,
            session_duration=300,
        )
        exploration_stream.label('exploration').put('exploration')
        output_records = []
        job.local_run(
            sources={
                'orders': StreamSource(order_records),
                'requests': StreamSource(request_records),
            },
            sinks={'exploration': ListSink(output_records)},
        )
        assert len(output_records) == len(exploration_records)
        for lhs, rhs in zip(output_records, exploration_records):
            assert lhs == rhs

    def test_exploitation_mode(self):
        job = clusters.MockCluster().job()
        exploration_stream = data.reduce_by_timestamp(
            orders=job.table('').label('orders'),
            requests=job.table('').label('requests'),
            exploration_mode=False,
            session_duration=300,
        )
        exploration_stream.label('exploration').put('exploration')
        output_records = []
        job.local_run(
            sources={
                'orders': StreamSource(order_records),
                'requests': StreamSource(request_records),
            },
            sinks={'exploration': ListSink(output_records)},
        )
        assert len(output_records) == len(exploitation_records)
        for lhs, rhs in zip(output_records, exploitation_records):
            assert lhs == rhs
