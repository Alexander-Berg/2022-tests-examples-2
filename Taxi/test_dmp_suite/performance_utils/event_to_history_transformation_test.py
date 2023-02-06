# coding: utf-8
from unittest import TestCase
from pprint import pformat

from nile.api.v1 import Record, MockCluster
from nile.api.v1.local import StreamSource, ListSink

from dmp_suite import datetime_utils as dtu
from dmp_suite.performance_utils import EventToHistoryTransformation


class TestEventToHistoryTransformation(TestCase):
    def test_event_to_history_transformation(self):
        event_data = [
            Record(moscow_event_dttm='2018-01-01 01:00:00', adjust_id='1', service='a', user_id='x'),
            Record(moscow_event_dttm='2018-01-01 02:00:00', adjust_id='1', service='a', user_id='y'),
            Record(moscow_event_dttm='2018-01-01 03:00:00', adjust_id='1', service='a', user_id='y'),
            Record(moscow_event_dttm='2018-01-01 04:00:00', adjust_id='1', service='a', user_id='y'),
            Record(moscow_event_dttm='2018-01-01 05:00:00', adjust_id='1', service='a', user_id='x'),
            Record(moscow_event_dttm='2018-01-01 06:00:00', adjust_id='1', service='a', user_id='x')
        ]

        expected_history_data = [
            Record(
                moscow_effective_from_dttm=dtu.MIN_DATETIME_STRING,
                moscow_effective_to_dttm='2018-01-01 00:59:59',
                adjust_id='1',
                service='a',
                user_id='x'
            ),
            Record(
                moscow_effective_from_dttm='2018-01-01 01:00:00',
                moscow_effective_to_dttm='2018-01-01 01:59:59',
                adjust_id='1',
                service='a',
                user_id='x'
            ),
            Record(
                moscow_effective_from_dttm='2018-01-01 02:00:00',
                moscow_effective_to_dttm='2018-01-01 04:59:59',
                adjust_id='1',
                service='a',
                user_id='y'
            ),
            Record(
                moscow_effective_from_dttm='2018-01-01 05:00:00',
                moscow_effective_to_dttm=dtu.MAX_DATETIME_STRING,
                adjust_id='1',
                service='a',
                user_id='x'
            )
        ]
        """
        Graphical explanation.
        Event timeline:   -------x-x-y-y-y-x-x-------
        History timeline: xxxxxxxxxxxyyyyyyxxxxxxxxxx
        """

        cluster = MockCluster()
        job = cluster.job('test_event_to_history_transformation')
        actual_history_data = []
        job.table('stub') \
            .label('event_data') \
            .call(EventToHistoryTransformation(key_names=('adjust_id', 'service'), value_name='user_id')) \
            .label('actual_history_data')
        job.local_run(
            sources={'event_data': StreamSource(event_data)},
            sinks={'actual_history_data': ListSink(actual_history_data)}
        )

        self.assertListEqual(
            expected_history_data,
            actual_history_data,
            msg='Expected data is different from actual:\nexpected\n{},\nactual\n{}'.format(
                pformat(expected_history_data), pformat(actual_history_data)
            )
        )
