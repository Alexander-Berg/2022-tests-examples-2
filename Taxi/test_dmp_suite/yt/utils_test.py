# coding: utf-8
from pprint import pformat
from unittest import TestCase

from nile.api.v1 import MockCluster
from nile.local.sink import ListSink
from nile.local.source import StreamSource
from qb2.utils.record import Record

from dmp_suite.datetime_utils import timestamp2datetime
from dmp_suite.extract_utils import PathExtractor
from dmp_suite.yt.utils import DocLoader, join_sessions


class TestDocLoader(TestCase):
    def test_doc_loader(self):
        source = [
            Record(
                a=1566284500,
                b='qwe',
                c='asd'
            ),
            Record(
                b='qwe',
                c='asd'
            ),
            Record(
                a=1566284700,
                b='qwe'
            ),
            Record(
                a=1566284800,
                c='asd'
            ),
            Record()
        ]

        expected = [
            Record(
                dttm='2019-08-20 07:01:40',
                doc=dict(
                    a=1566284500,
                    b='qwe'
                )
            ),
            Record(
                dttm=None,
                doc=dict(
                    b='qwe'
                )
            ),
            Record(
                dttm='2019-08-20 07:05:00',
                doc=dict(
                    a=1566284700,
                    b='qwe'
                )
            ),
            Record(
                dttm='2019-08-20 07:06:40',
                doc=dict(
                    a=1566284800
                )
            ),
            Record(
                dttm=None,
                doc=dict()
            )
        ]

        cluster = MockCluster()
        job = cluster.job('test_doc_loader')
        actual = []
        job.table('stub') \
            .label('source') \
            .map(DocLoader(field_blacklist=('c',), extractors={'dttm': PathExtractor('a', converter=timestamp2datetime)})) \
            .label('actual')
        job.local_run(
            sources={'source': StreamSource(source)},
            sinks={'actual': ListSink(actual)}
        )

        self.assertListEqual(
            expected,
            actual,
            msg='Expected is different from actual:\nexpected\n{},\nactual\n{}'.format(
                pformat(expected), pformat(actual)
            )
        )


def test_join_sessions():
    given_left_sessions = [
        Record(start_timestamp=100, end_timestamp=299, x="a"),
        Record(start_timestamp=300, end_timestamp=499, x="b"),
        Record(start_timestamp=600, end_timestamp=799, x="c"),
    ]
    given_right_sessions = [
        Record(start_timestamp=200, end_timestamp=399, y="p"),
        Record(start_timestamp=410, end_timestamp=599, y="q"),
        Record(start_timestamp=600, end_timestamp=799, y="r"),
    ]
    expect_result = [
        Record(start_timestamp=200, end_timestamp=299, x="a", y="p"),
        Record(start_timestamp=300, end_timestamp=399, x="b", y="p"),
        Record(start_timestamp=410, end_timestamp=499, x="b", y="q"),
        Record(start_timestamp=600, end_timestamp=799, x="c", y="r"),
    ]
    assert list(join_sessions(iter(given_left_sessions), iter(given_right_sessions))) == expect_result


def test_join_sessions_does_not_squash_sessions():
    given_left_sessions = [
        Record(start_timestamp=100, end_timestamp=199, x="a"),
        Record(start_timestamp=200, end_timestamp=299, x="a"),
    ]
    given_right_sessions = [
        Record(start_timestamp=100, end_timestamp=299, y="p"),
    ]
    expect_result = [
        Record(start_timestamp=100, end_timestamp=199, x="a", y="p"),
        Record(start_timestamp=200, end_timestamp=299, x="a", y="p"),
    ]
    assert list(join_sessions(iter(given_left_sessions), iter(given_right_sessions))) == expect_result
