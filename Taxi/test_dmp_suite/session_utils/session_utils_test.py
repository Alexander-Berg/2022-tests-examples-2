# coding: utf-8
import pytest
from pprint import pformat
from datetime import timedelta

from nile.api.v1 import Record, MockCluster
from nile.api.v1.local import StreamSource, ListSink

from dmp_suite import datetime_utils as dtu, yt
from dmp_suite.yt import etl
from dmp_suite.yt.operation import write_yt_table, read_yt_table, get_temp_table
from dmp_suite.exceptions import DWHError
from dmp_suite.session_utils import \
    SessionBuilder, Session, DatetimeFormat, history_session_factory, \
    HistorySessionGapBuilder, PeriodCutter, PeriodCutterExtendHistory
from test_dmp_suite.yt.utils import random_yt_table

from .impl import session, DtHistorySessionTestTable, _test_history_session_loader


def test_session_build():
    class TestSession(Session):
        def __init__(self):
            super(TestSession, self).__init__()
            self.events = []

        def expand(self, record):
            super(TestSession, self).expand(record)
            self.events.append(record)

        def finish(self, record):
            if self.is_empty():
                raise DWHError('Cannot check next session for empty session. Event: {}'.format(record))
            return dtu.parse_datetime(record.utc_dttm) - dtu.parse_datetime(self.events[-1].utc_dttm) > \
                   timedelta(minutes=5)

        def build_rec(self):
            event_id_list = [event.event_id for event in self.events]
            user_id = self.events[0].user_id
            return Record(
                user_id=user_id,
                session_id=self.get_session_id([user_id] + event_id_list),
                utc_session_start=dtu.format_datetime(self.events[0].utc_dttm),
                utc_session_end=dtu.format_datetime(self.events[-1].utc_dttm),
                event_cnt=len(self.events)
            )

    class TestSessionBuilder(SessionBuilder):
        def __init__(self, session_factory, max_session_start):
            super(TestSessionBuilder, self).__init__(session_factory)
            self._max_session_start = dtu.format_datetime(max_session_start)

        def stop_session_building(self, rec):
            return rec.utc_dttm > self._max_session_start

    session_builder = TestSessionBuilder(TestSession, '2019-08-31 23:59:59')

    events = [
        Record(
            user_id='bar',
            utc_dttm='2019-08-31 23:45:00',
            event_id='200'
        ),
        Record(
            user_id='foo',
            utc_dttm='2019-08-31 23:48:00',
            event_id='100'
        ),
        Record(
            user_id='foo',
            utc_dttm='2019-08-31 23:52:00',
            event_id='101'
        ),
        Record(
            user_id='foo',
            utc_dttm='2019-08-31 23:58:00',
            event_id='102'
        ),
        Record(
            user_id='foo',
            utc_dttm='2019-09-01 00:01:00',
            event_id='103'
        ),
        Record(
            user_id='foo',
            utc_dttm='2019-09-01 00:08:00',
            event_id='104'
        )
    ]

    expected_sessions = [
        Record(
            user_id='bar',
            session_id='453516201aedef7fc6d102a995205a0a',
            utc_session_start='2019-08-31 23:45:00',
            utc_session_end='2019-08-31 23:45:00',
            event_cnt=1
        ),
        Record(
            user_id='foo',
            session_id='ce8221d1f6de874220603de8ab5bb2d8',
            utc_session_start='2019-08-31 23:48:00',
            utc_session_end='2019-08-31 23:52:00',
            event_cnt=2
        ),
        Record(
            user_id='foo',
            session_id='bbbbd3569f05604e6433340b875c7bcc',
            utc_session_start='2019-08-31 23:58:00',
            utc_session_end='2019-09-01 00:01:00',
            event_cnt=2
        )
    ]

    cluster = MockCluster()
    job = cluster.job('test_session_build')
    actual_sessions = []
    job.table('stub') \
        .label('events') \
        .groupby('user_id') \
        .sort('utc_dttm') \
        .reduce(session_builder) \
        .label('actual_sessions')
    job.local_run(
        sources={'events': StreamSource(events)},
        sinks={'actual_sessions': ListSink(actual_sessions)}
    )

    actual_sessions = sorted(actual_sessions, key=lambda rec: (rec.get('user_id'), rec.get('utc_session_start')))

    assert expected_sessions == actual_sessions, \
        'Expected sessions is different from actual:\nexpected\n{},\nactual\n{}'.format(
            pformat(expected_sessions), pformat(actual_sessions)
        )

@pytest.mark.parametrize(
    'source_sessions, expected_result_sessions',
    [
        pytest.param(
            [
                session(
                    effective_from='2019-08-10',
                    effective_to='2019-08-12',
                    lightbox_flg=True,
                    sticker_flg=False
                ),
                session(
                    effective_from='2019-08-13',
                    effective_to='2019-08-14',
                    lightbox_flg=True,
                    sticker_flg=False
                ),
                session(
                    effective_from='2019-08-15',
                    effective_to='2019-08-16',
                    lightbox_flg=False,
                    sticker_flg=False
                )
            ],
            [
                session(
                    effective_from='2019-08-10',
                    effective_to='2019-08-14',
                    lightbox_flg=True,
                    sticker_flg=False
                ),
                session(
                    effective_from='2019-08-15',
                    effective_to='2019-08-16',
                    lightbox_flg=False,
                    sticker_flg=False
                )
            ],
            id='Sessions without gap'
        ),
        pytest.param(
            [
                session(
                    effective_from='2019-08-10',
                    effective_to='2019-08-12',
                    lightbox_flg=True,
                    sticker_flg=False
                ),
                session(
                    effective_from='2019-08-15',
                    effective_to='2019-08-16',
                    lightbox_flg=False,
                    sticker_flg=True
                )
            ],
            [
                session(
                    effective_from='2019-08-10',
                    effective_to='2019-08-14',
                    lightbox_flg=True,
                    sticker_flg=False
                ),
                session(
                    effective_from='2019-08-15',
                    effective_to='2019-08-16',
                    lightbox_flg=False,
                    sticker_flg=True
                )
            ],
            id='Sessions with gap'
        )
    ]
)
def test_history_session_build(source_sessions, expected_result_sessions):
    HistorySession = history_session_factory(
        history_key_fields=('car_number', 'park'),
        history_value_fields=('lightbox_flg', 'sticker_flg'),
        datetime_format=DatetimeFormat.dt
    )

    session_builder = SessionBuilder(HistorySession)

    cluster = MockCluster()
    job = cluster.job('test_session_build')
    actual_result_sessions = []
    job.table('stub') \
        .label('source_sessions') \
        .groupby('car_number', 'park') \
        .sort('utc_effective_from_dt') \
        .reduce(session_builder) \
        .label('actual_result_sessions')
    job.local_run(
        sources={'source_sessions': StreamSource(source_sessions)},
        sinks={'actual_result_sessions': ListSink(actual_result_sessions)}
    )

    actual_result_sessions = sorted(actual_result_sessions, key=lambda rec: (rec.get('user_id'), rec.get('utc_session_start')))

    assert expected_result_sessions == actual_result_sessions, \
        'Expected sessions is different from actual:\nexpected\n{},\nactual\n{}'.format(
            pformat(expected_result_sessions), pformat(actual_result_sessions)
        )


@pytest.mark.parametrize(
    'source_sessions, expected_result_sessions',
    [
        pytest.param(
            [
                session(
                    effective_from='2019-08-10',
                    effective_to='2019-08-12',
                    lightbox_flg=True,
                    sticker_flg=False
                ),
                session(
                    effective_from='2019-08-15',
                    effective_to='2019-08-16',
                    lightbox_flg=False,
                    sticker_flg=True
                )
            ],
            [
                session(
                    effective_from='2019-08-10',
                    effective_to='2019-08-12',
                    lightbox_flg=True,
                    sticker_flg=False
                ),
                session(
                    effective_from='2019-08-13',
                    effective_to='2019-08-14',
                    lightbox_flg=False,
                    sticker_flg=False
                ),
                session(
                    effective_from='2019-08-15',
                    effective_to='2019-08-16',
                    lightbox_flg=False,
                    sticker_flg=True
                )
            ],
            id='Sessions with gap without skip'
        ),
        pytest.param(
            [
                session(
                    effective_from='2019-08-10',
                    effective_to='2019-08-12',
                    lightbox_flg=True,
                    sticker_flg=False
                ),
                session(
                    effective_from='2019-08-15',
                    effective_to='2019-08-16',
                    lightbox_flg=False,
                    sticker_flg=False
                )
            ],
            [
                session(
                    effective_from='2019-08-10',
                    effective_to='2019-08-12',
                    lightbox_flg=True,
                    sticker_flg=False
                ),
                session(
                    effective_from='2019-08-13',
                    effective_to='2019-08-16',
                    lightbox_flg=False,
                    sticker_flg=False
                )
            ],
            id='Sessions with gap before skip'
        ),
        pytest.param(
            [
                session(
                    effective_from='2019-08-10',
                    effective_to='2019-08-12',
                    lightbox_flg=True,
                    sticker_flg=False
                ),
                session(
                    effective_from='2019-08-13',
                    effective_to='2019-08-14',
                    lightbox_flg=False,
                    sticker_flg=False
                ),
                session(
                    effective_from='2019-08-16',
                    effective_to='2019-08-17',
                    lightbox_flg=False,
                    sticker_flg=True
                )
            ],
            [
                session(
                    effective_from='2019-08-10',
                    effective_to='2019-08-12',
                    lightbox_flg=True,
                    sticker_flg=False
                ),
                session(
                    effective_from='2019-08-13',
                    effective_to='2019-08-15',
                    lightbox_flg=False,
                    sticker_flg=False
                ),
                session(
                    effective_from='2019-08-16',
                    effective_to='2019-08-17',
                    lightbox_flg=False,
                    sticker_flg=True
                )
            ],
            id='Sessions with gap after skip'
        ),
        pytest.param(
            [
                session(
                    effective_from='2019-08-10',
                    effective_to='2019-08-12',
                    lightbox_flg=True,
                    sticker_flg=False
                ),
                session(
                    effective_from='2019-08-13',
                    effective_to='2019-08-14',
                    lightbox_flg=False,
                    sticker_flg=False
                ),
                session(
                    effective_from='2019-08-16',
                    effective_to='2019-08-17',
                    lightbox_flg=False,
                    sticker_flg=False
                )
            ],
            [
                session(
                    effective_from='2019-08-10',
                    effective_to='2019-08-12',
                    lightbox_flg=True,
                    sticker_flg=False
                ),
                session(
                    effective_from='2019-08-13',
                    effective_to='2019-08-17',
                    lightbox_flg=False,
                    sticker_flg=False
                )
            ],
            id='Sessions with gap between skip'
        ),
        pytest.param(
            [
                session(
                    effective_from='2019-08-10',
                    effective_to='2019-08-21',
                    lightbox_flg=True,
                    sticker_flg=False
                ),
                session(
                    effective_from='2019-08-22',
                    effective_to='2019-08-30',
                    lightbox_flg=False,
                    sticker_flg=True
                )
            ],
            [
                session(
                    effective_from='2019-08-10',
                    effective_to='2019-08-21',
                    lightbox_flg=True,
                    sticker_flg=False
                ),
                session(
                    effective_from='2019-08-22',
                    effective_to='2019-08-30',
                    lightbox_flg=False,
                    sticker_flg=True
                )
            ],
            id='Distinct sessions without gap'
        ),
        pytest.param(
            [
                session(
                    effective_from='2019-08-10',
                    effective_to='2019-08-21',
                    lightbox_flg=True,
                    sticker_flg=False
                ),
                session(
                    effective_from='2019-08-22',
                    effective_to='2019-08-30',
                    lightbox_flg=True,
                    sticker_flg=False
                )
            ],
            [
                session(
                    effective_from='2019-08-10',
                    effective_to='2019-08-30',
                    lightbox_flg=True,
                    sticker_flg=False
                )
            ],
            id='Equal sessions without gap'
        )
    ]
)
def test_history_session_build_with_gap(source_sessions, expected_result_sessions):
    HistorySession = history_session_factory(
        history_key_fields=('car_number', 'park'),
        history_value_fields=('lightbox_flg', 'sticker_flg'),
        datetime_format=DatetimeFormat.dt,
        default_history_values={'lightbox_flg': False, 'sticker_flg': False}
    )

    session_builder = HistorySessionGapBuilder(HistorySession)

    cluster = MockCluster()
    job = cluster.job('test_session_build')
    actual_result_sessions = []
    job.table('stub') \
        .label('source_sessions') \
        .groupby('car_number', 'park') \
        .sort('utc_effective_from_dt') \
        .reduce(session_builder) \
        .label('actual_result_sessions')
    job.local_run(
        sources={'source_sessions': StreamSource(source_sessions)},
        sinks={'actual_result_sessions': ListSink(actual_result_sessions)}
    )

    actual_result_sessions = sorted(actual_result_sessions,
                                    key=lambda rec: (rec.get('user_id'), rec.get('utc_effective_from_dt')))

    assert expected_result_sessions == actual_result_sessions, \
        'Expected sessions is different from actual:\nexpected\n{},\nactual\n{}'.format(
            pformat(expected_result_sessions), pformat(actual_result_sessions)
            )


EXTEND_HISTORY_SESSION_INITIAL_DATA = [
    {
        'utc_effective_from_dt': '1970-01-01',
        'utc_effective_to_dt': '2019-08-04',
        'user_key': '123',
        'user_value': 'foo'
    },
    {
        'utc_effective_from_dt': '2019-08-05',
        'utc_effective_to_dt': '2019-08-15',
        'user_key': '123',
        'user_value': 'foo'
    },
    {
        'utc_effective_from_dt': '2019-08-16',
        'utc_effective_to_dt': '2019-08-25',
        'user_key': '123',
        'user_value': 'bar'
    },
    {
        'utc_effective_from_dt': '2019-08-26',
        'utc_effective_to_dt': '9999-12-31',
        'user_key': '123',
        'user_value': 'bar'
    }
]
HISTORY_SESSION_INITIAL_DATA = EXTEND_HISTORY_SESSION_INITIAL_DATA[1:3]


@pytest.mark.slow
@pytest.mark.parametrize(
    'initial_data, extend_history_flg',
    [
        pytest.param(
            HISTORY_SESSION_INITIAL_DATA,
            False,
            id='Closed history session'
        ),
        pytest.param(
            EXTEND_HISTORY_SESSION_INITIAL_DATA,
            True,
            id='Extend history session'
        )
    ]
)
def test_period_cutter(initial_data, extend_history_flg):
    table = random_yt_table(DtHistorySessionTestTable)
    history_session_meta = yt.YTMeta(table)
    etl.init_target_table(history_session_meta)

    write_yt_table(
        history_session_meta.target_path(),
        initial_data
    )
    start_dt = '2019-08-10'
    end_dt = '2019-08-20'

    job = etl.cluster_job(history_session_meta)
    period_cutter = PeriodCutter if not extend_history_flg else PeriodCutterExtendHistory

    data_before_period_stream, data_after_period_stream = \
        period_cutter(job, history_session_meta, DatetimeFormat.dt)(start_dt, end_dt)
    with get_temp_table() as before_table_tmp, get_temp_table() as after_table_tmp:
        data_before_period_stream.put(before_table_tmp, merge_strategy='never')
        data_after_period_stream.put(after_table_tmp, merge_strategy='never')
        job.run()
        actual_data_before_period = list(read_yt_table(before_table_tmp))
        actual_data_after_period = list(read_yt_table(after_table_tmp))

    expected_data_before_period = [
        {
            'utc_effective_from_dt': '2019-08-05',
            'utc_effective_to_dt': '2019-08-09',
            'user_key': '123',
            'user_value': 'foo'
        }
    ]
    expected_data_after_period = [
        {
            'utc_effective_from_dt': '2019-08-21',
            'utc_effective_to_dt': '2019-08-25',
            'user_key': '123',
            'user_value': 'bar'
        }
    ]
    assert (expected_data_before_period, expected_data_after_period) == (actual_data_before_period, actual_data_after_period), \
        'Expected data is different from actual:\nexpected\n{},\nactual\n{}'.format(
            pformat((expected_data_before_period, expected_data_after_period)),
            pformat((actual_data_before_period, actual_data_after_period))
        )


@pytest.mark.slow
@pytest.mark.parametrize(
    'default_history_values, increment_data, expected_data',
    [
        pytest.param(
            None,
            [
                {
                    'utc_effective_from_dt': '2019-08-13',
                    'utc_effective_to_dt': '2019-08-14',
                    'user_key': '123',
                    'user_value': 'baz'
                },
                {
                    'utc_effective_from_dt': '2019-08-16',
                    'utc_effective_to_dt': '2019-08-17',
                    'user_key': '123',
                    'user_value': 'bar'
                },
                {
                    'utc_effective_from_dt': '2019-08-18',
                    'utc_effective_to_dt': '2019-08-19',
                    'user_key': '123',
                    'user_value': 'bar'
                },
            ],
            [
                {
                    'utc_effective_from_dt': '2019-08-05',
                    'utc_effective_to_dt': '2019-08-12',
                    'user_key': '123',
                    'user_value': 'foo'
                },
                {
                    'utc_effective_from_dt': '2019-08-13',
                    'utc_effective_to_dt': '2019-08-15',
                    'user_key': '123',
                    'user_value': 'baz'
                },
                {
                    'utc_effective_from_dt': '2019-08-16',
                    'utc_effective_to_dt': '2019-08-25',
                    'user_key': '123',
                    'user_value': 'bar'
                }
            ],
            id='No-gap history sessions'
        ),
        pytest.param(
            {'user_value': '_missing_'},
            [
                {
                    'utc_effective_from_dt': '2019-08-13',
                    'utc_effective_to_dt': '2019-08-14',
                    'user_key': '123',
                    'user_value': 'baz'
                },
                {
                    'utc_effective_from_dt': '2019-08-16',
                    'utc_effective_to_dt': '2019-08-17',
                    'user_key': '123',
                    'user_value': 'bar'
                },
                {
                    'utc_effective_from_dt': '2019-08-18',
                    'utc_effective_to_dt': '2019-08-19',
                    'user_key': '123',
                    'user_value': 'bar'
                },
            ],
            [
                {
                    'utc_effective_from_dt': '2019-08-05',
                    'utc_effective_to_dt': '2019-08-09',
                    'user_key': '123',
                    'user_value': 'foo'
                },
                {
                    'utc_effective_from_dt': '2019-08-10',
                    'utc_effective_to_dt': '2019-08-12',
                    'user_key': '123',
                    'user_value': '_missing_'
                },
                {
                    'utc_effective_from_dt': '2019-08-13',
                    'utc_effective_to_dt': '2019-08-14',
                    'user_key': '123',
                    'user_value': 'baz'
                },
                {
                    'utc_effective_from_dt': '2019-08-15',
                    'utc_effective_to_dt': '2019-08-15',
                    'user_key': '123',
                    'user_value': '_missing_'
                },
                {
                    'utc_effective_from_dt': '2019-08-16',
                    'utc_effective_to_dt': '2019-08-19',
                    'user_key': '123',
                    'user_value': 'bar'
                },
                {
                    'utc_effective_from_dt': '2019-08-20',
                    'utc_effective_to_dt': '2019-08-20',
                    'user_key': '123',
                    'user_value': '_missing_'
                },
                {
                    'utc_effective_from_dt': '2019-08-21',
                    'utc_effective_to_dt': '2019-08-25',
                    'user_key': '123',
                    'user_value': 'bar'
                }
            ],
            id='Gap history sessions'
        ),
        pytest.param(
            {'user_value': '_missing_'},
            [
                {
                    'utc_effective_from_dt': '2019-08-10',
                    'utc_effective_to_dt': '2019-08-13',
                    'user_key': '123',
                    'user_value': 'foo'
                },
                {
                    'utc_effective_from_dt': '2019-08-15',
                    'utc_effective_to_dt': '2019-08-16',
                    'user_key': '123',
                    'user_value': '_missing_'
                },
                {
                    'utc_effective_from_dt': '2019-08-18',
                    'utc_effective_to_dt': '2019-08-20',
                    'user_key': '123',
                    'user_value': 'bar'
                },
            ],
            [
                {
                    'utc_effective_from_dt': '2019-08-05',
                    'utc_effective_to_dt': '2019-08-13',
                    'user_key': '123',
                    'user_value': 'foo'
                },
                {
                    'utc_effective_from_dt': '2019-08-14',
                    'utc_effective_to_dt': '2019-08-17',
                    'user_key': '123',
                    'user_value': '_missing_'
                },
                {
                    'utc_effective_from_dt': '2019-08-18',
                    'utc_effective_to_dt': '2019-08-25',
                    'user_key': '123',
                    'user_value': 'bar'
                }
            ],
            id='Gap history sessions with default value'
        )
    ]
)
def test_non_extend_history_session_loader(default_history_values, increment_data, expected_data):
    _test_history_session_loader(
        default_history_values=default_history_values,
        extend_history_flg=False,
        initial_data=HISTORY_SESSION_INITIAL_DATA,
        increment_data=increment_data,
        expected_data=expected_data,
        start_datetime='2019-08-10',
        end_datetime='2019-08-20',
        datetime_format=DatetimeFormat.dt
    )


@pytest.mark.slow
@pytest.mark.parametrize(
    'increment_data, start_dt, end_dt, expected_data',
    [
        pytest.param(
            [
                {
                    'utc_effective_from_dt': '2019-08-12',
                    'utc_effective_to_dt': '2019-08-18',
                    'user_key': '123',
                    'user_value': 'baz'
                },
            ],
            '2019-08-10',
            '2019-08-20',
            [
                {
                    'utc_effective_from_dt': '1970-01-01',
                    'utc_effective_to_dt': '2019-08-04',
                    'user_key': '123',
                    'user_value': 'foo'
                },
                {
                    'utc_effective_from_dt': '2019-08-05',
                    'utc_effective_to_dt': '2019-08-11',
                    'user_key': '123',
                    'user_value': 'foo'
                },
                {
                    'utc_effective_from_dt': '2019-08-12',
                    'utc_effective_to_dt': '2019-08-20',
                    'user_key': '123',
                    'user_value': 'baz'
                },
                {
                    'utc_effective_from_dt': '2019-08-21',
                    'utc_effective_to_dt': '2019-08-25',
                    'user_key': '123',
                    'user_value': 'bar'
                },
                {
                    'utc_effective_from_dt': '2019-08-26',
                    'utc_effective_to_dt': '9999-12-31',
                    'user_key': '123',
                    'user_value': 'bar'
                }
            ],
            id='History sessions'
        ),
        pytest.param(
            [
                {
                    'utc_effective_from_dt': '2019-08-12',
                    'user_key': '123',
                    'user_value': 'baz'
                },
                {
                    'utc_effective_from_dt': '2019-08-15',
                    'user_key': '123',
                    'user_value': 'baz'
                }
            ],
            '2019-08-10',
            '2019-08-30',
            [
                {
                    'utc_effective_from_dt': '1970-01-01',
                    'utc_effective_to_dt': '2019-08-04',
                    'user_key': '123',
                    'user_value': 'foo'
                },
                {
                    'utc_effective_from_dt': '2019-08-05',
                    'utc_effective_to_dt': '2019-08-11',
                    'user_key': '123',
                    'user_value': 'foo'
                },
                {
                    'utc_effective_from_dt': '2019-08-12',
                    'utc_effective_to_dt': '2019-08-15',
                    'user_key': '123',
                    'user_value': 'baz'
                },
                {
                    'utc_effective_from_dt': '2019-08-16',
                    'utc_effective_to_dt': '9999-12-31',
                    'user_key': '123',
                    'user_value': 'baz'
                }
            ],
            id='History sessions from events'
        ),
        pytest.param(
            [
                {
                    'utc_effective_from_dt': '2019-08-03',
                    'utc_effective_to_dt': '2019-08-08',
                    'user_key': '123',
                    'user_value': 'baz'
                },
            ],
            '2019-08-01',
            '2019-08-10',
            [
                {
                    'utc_effective_from_dt': '1970-01-01',
                    'utc_effective_to_dt': '2019-08-02',
                    'user_key': '123',
                    'user_value': 'baz'
                },
                {
                    'utc_effective_from_dt': '2019-08-03',
                    'utc_effective_to_dt': '2019-08-10',
                    'user_key': '123',
                    'user_value': 'baz'
                },
                {
                    'utc_effective_from_dt': '2019-08-11',
                    'utc_effective_to_dt': '2019-08-15',
                    'user_key': '123',
                    'user_value': 'foo'
                },
                {
                    'utc_effective_from_dt': '2019-08-16',
                    'utc_effective_to_dt': '2019-08-25',
                    'user_key': '123',
                    'user_value': 'bar'
                },
                {
                    'utc_effective_from_dt': '2019-08-26',
                    'utc_effective_to_dt': '9999-12-31',
                    'user_key': '123',
                    'user_value': 'bar'
                }
            ],
            id='History sessions with start update'
        ),
        pytest.param(
            [
                {
                    'utc_effective_from_dt': '2019-08-20',
                    'utc_effective_to_dt': '2019-08-27',
                    'user_key': '123',
                    'user_value': 'baz'
                },
            ],
            '2019-08-20',
            '2019-08-30',
            [
                {
                    'utc_effective_from_dt': '1970-01-01',
                    'utc_effective_to_dt': '2019-08-04',
                    'user_key': '123',
                    'user_value': 'foo'
                },
                {
                    'utc_effective_from_dt': '2019-08-05',
                    'utc_effective_to_dt': '2019-08-15',
                    'user_key': '123',
                    'user_value': 'foo'
                },
                {
                    'utc_effective_from_dt': '2019-08-16',
                    'utc_effective_to_dt': '2019-08-19',
                    'user_key': '123',
                    'user_value': 'bar'
                },
                {
                    'utc_effective_from_dt': '2019-08-20',
                    'utc_effective_to_dt': '2019-08-27',
                    'user_key': '123',
                    'user_value': 'baz'
                },
                {
                    'utc_effective_from_dt': '2019-08-28',
                    'utc_effective_to_dt': '9999-12-31',
                    'user_key': '123',
                    'user_value': 'baz'
                }
            ],
            id='History sessions with end update'
        )
    ]
)
def test_extend_history_session_loader(increment_data, start_dt, end_dt, expected_data):
    _test_history_session_loader(
        default_history_values=None,
        extend_history_flg=True,
        initial_data=EXTEND_HISTORY_SESSION_INITIAL_DATA,
        increment_data=increment_data,
        expected_data=expected_data,
        start_datetime=start_dt,
        end_datetime=end_dt,
        datetime_format=DatetimeFormat.dt
    )

@pytest.mark.slow
def test_history_session_loader_dttm():
    _test_history_session_loader(
        default_history_values=None,
        extend_history_flg=True,
        initial_data=[
            {
                'utc_effective_from_dttm': '1970-01-01 00:00:00',
                'utc_effective_to_dttm': '2019-08-15 05:00:00',
                'user_key': '123',
                'user_value': 'foo'
            },
            {
                'utc_effective_from_dttm': '2019-08-15 05:00:01',
                'utc_effective_to_dttm': '2019-08-20 15:00:00',
                'user_key': '123',
                'user_value': 'foo'
            },
            {
                'utc_effective_from_dttm': '2019-08-20 15:00:01',
                'utc_effective_to_dttm': '2019-08-22 15:00:00',
                'user_key': '123',
                'user_value': 'bar'
            },
            {
                'utc_effective_from_dttm': '2019-08-22 15:00:01',
                'utc_effective_to_dttm': '9999-12-31 23:59:59',
                'user_key': '123',
                'user_value': 'bar'
            }
        ],
        increment_data=[
            {
                'utc_effective_from_dttm': '2019-08-15 08:00:01',
                'utc_effective_to_dttm': '2019-08-23 15:00:00',
                'user_key': '123',
                'user_value': 'baz'
            },
            {
                'utc_effective_from_dttm': '2019-08-15 23:00:01',
                'utc_effective_to_dttm': '2019-08-23 01:00:00',
                'user_key': '234',
                'user_value': 'qwe'
            }
        ],
        expected_data=[
            {
                'utc_effective_from_dttm': '1970-01-01 00:00:00',
                'utc_effective_to_dttm': '2019-08-15 05:00:00',
                'user_key': '123',
                'user_value': 'foo'
            },
            {
                'utc_effective_from_dttm': '2019-08-15 05:00:01',
                'utc_effective_to_dttm': '2019-08-15 08:00:00',
                'user_key': '123',
                'user_value': 'foo'
            },
            {
                'utc_effective_from_dttm': '2019-08-15 08:00:01',
                'utc_effective_to_dttm': '2019-08-23 15:00:00',
                'user_key': '123',
                'user_value': 'baz'
            },
            {
                'utc_effective_from_dttm': '2019-08-23 15:00:01',
                'utc_effective_to_dttm': '9999-12-31 23:59:59',
                'user_key': '123',
                'user_value': 'baz'
            },
            {
                'utc_effective_from_dttm': '1970-01-01 00:00:00',
                'utc_effective_to_dttm': '2019-08-15 23:00:00',
                'user_key': '234',
                'user_value': 'qwe'
            },
            {
                'utc_effective_from_dttm': '2019-08-15 23:00:01',
                'utc_effective_to_dttm': '2019-08-23 01:00:00',
                'user_key': '234',
                'user_value': 'qwe'
            },
            {
                'utc_effective_from_dttm': '2019-08-23 01:00:01',
                'utc_effective_to_dttm': '9999-12-31 23:59:59',
                'user_key': '234',
                'user_value': 'qwe'
            }
        ],
        start_datetime='2019-08-15 08:00:01',
        end_datetime='2019-08-23 17:00:00',
        datetime_format=DatetimeFormat.dttm
    )
