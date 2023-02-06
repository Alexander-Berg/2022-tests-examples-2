import unittest
from pprint import pformat

from nile.api.v1 import MockCluster, Record
from nile.api.v1.local import StreamSource, ListSink

from meta_etl.layer.yt.ods.greenplum.query_log.impl import PRE_EXTRACTORS, QuerySession, QuerySessionBuilder
from .impl import event


class TestCases(unittest.TestCase):
    def test_session_build(self):
        events = [
            event(
                logtime='2019-08-01 00:00:00.000000',
                logmessage='trash',
                logsession='con1',
            ),
            event(
                logtime='2019-08-01 00:00:01.000000',
                logmessage='statement: SELECT 1;',
                logsession='con1',
                logdebug='SELECT 1;',
            ),
            event(
                logtime='2019-08-01 00:00:02.000000',
                logmessage='statement: SELECT 1;',
                logsession='con1',
                logdebug='SELECT 1;',
            ),
            event(
                logtime='2019-08-01 00:00:03.000000',
                logmessage='trash',
                logsession='con1',
            ),
            event(
                logtime='2019-08-01 00:00:04.000000',
                logmessage='statement: SELECT 1;',
                logsession='con1',
                logdebug='SELECT 1;',
            ),
            event(
                logtime='2019-08-01 00:00:05.000000',
                logmessage='trash',
                logsession='con1',
            ),
            event(
                logtime='2019-08-01 00:00:06.000000',
                logmessage='trash',
                logsession='con1',
            ),
            event(
                logtime='2019-08-01 00:00:07.000000',
                logmessage='trash',
                logsession='con1',
            ),
            event(
                logtime='2019-08-01 00:00:08.000000',
                logmessage='statement: SELECT 1;',
                logsession='con1',
                logdebug='SELECT 1;',
            ),
            event(
                logtime='2019-08-01 00:00:00.000000',
                logmessage='trash',
                logsession='con2',
            ),
            event(
                logtime='2019-08-01 00:00:01.000000',
                logmessage='trash',
                logsession='con2',
            ),
            event(
                logtime='2019-08-01 00:00:00.000000',
                logmessage='statement: SELECT 3;',
                logsession='con3',
                logdebug='SELECT 3;',
            ),
            event(
                logtime='2019-08-01 00:00:03.000000',
                logmessage='trash',
                logsession='con4',
            ),
            event(
                logtime='2019-08-01 00:00:00.000000',
                logmessage='statement: SELECT 5;',
                logsession='con5',
                logdebug='SELECT 5;',
            ),
            event(
                logtime='2019-08-01 00:00:05.000000',
                logmessage='trash',
                logsession='con5',
            ),
            event(
                logtime='2019-08-01 00:00:06.000000',
                logmessage='trash',
                logsession='con5',
            ),
            event(
                logtime='2019-08-01 00:00:07.000000',
                logmessage='trash',
                logsession='con5',
            ),
            event(
                logtime='2019-08-01 00:00:08.000000',
                logmessage='statement: SELECT 5;',
                logsession='con5',
                logdebug='SELECT 5;',
            ),
        ]

        cluster = MockCluster()
        job = cluster.job('test_query_session_build')

        (job
         .table('stub')
         .label('events')
         .project(**PRE_EXTRACTORS)
         .groupby('session_id')
         .sort('utc_query_dttm')
         .reduce(QuerySessionBuilder(QuerySession))
         .label('output')
         )

        actual_output = []
        job.local_run(
            sources={'events': StreamSource(events)},
            sinks={'output': ListSink(actual_output)}
        )

        expected_output = [
            Record(database_name='database_name', host='host', log_level='LOG', message=None, process_id=123,
                   query_name='SELECT 1;', session_id=1, user_name='user_name',
                   utc_query_end_dttm='2019-07-31 21:00:01.999999', utc_query_start_dttm='2019-07-31 21:00:01.000000',
                   utc_session_start_dttm='3020-01-01 07:10:00'),
            Record(database_name='database_name', host='host', log_level='LOG', message='trash', process_id=123,
                   query_name='SELECT 1;', session_id=1, user_name='user_name',
                   utc_query_end_dttm='2019-07-31 21:00:03.999999', utc_query_start_dttm='2019-07-31 21:00:02.000000',
                   utc_session_start_dttm='3020-01-01 07:10:00'),
            Record(database_name='database_name', host='host', log_level='LOG', message='trash', process_id=123,
                   query_name='SELECT 1;', session_id=1, user_name='user_name',
                   utc_query_end_dttm='2019-07-31 21:00:07.999999', utc_query_start_dttm='2019-07-31 21:00:04.000000',
                   utc_session_start_dttm='3020-01-01 07:10:00'),
            Record(database_name='database_name', host='host', log_level='LOG', message=None, process_id=123,
                   query_name='SELECT 1;', session_id=1, user_name='user_name',
                   utc_query_end_dttm='2019-07-31 21:00:08.000000', utc_query_start_dttm='2019-07-31 21:00:08.000000',
                   utc_session_start_dttm='3020-01-01 07:10:00'),
            Record(database_name='database_name', host='host', log_level='LOG', message=None, process_id=123,
                   query_name='SELECT 3;', session_id=3, user_name='user_name',
                   utc_query_end_dttm='2019-07-31 21:00:00.000000', utc_query_start_dttm='2019-07-31 21:00:00.000000',
                   utc_session_start_dttm='3020-01-01 07:10:00'),
            Record(database_name='database_name', host='host', log_level='LOG', message='trash', process_id=123,
                   query_name='SELECT 5;', session_id=5, user_name='user_name',
                   utc_query_end_dttm='2019-07-31 21:00:07.999999', utc_query_start_dttm='2019-07-31 21:00:00.000000',
                   utc_session_start_dttm='3020-01-01 07:10:00'),
            Record(database_name='database_name', host='host', log_level='LOG', message=None, process_id=123,
                   query_name='SELECT 5;', session_id=5, user_name='user_name',
                   utc_query_end_dttm='2019-07-31 21:00:08.000000', utc_query_start_dttm='2019-07-31 21:00:08.000000',
                   utc_session_start_dttm='3020-01-01 07:10:00')
        ]

        self.assertListEqual(
            expected_output,
            actual_output,
            msg='Expected data is different from actual:\nexpected\n{},\nactual\n{}'.format(
                pformat(expected_output), pformat(actual_output)
            )
        )
