# coding: utf-8
import mock
from nile.api.v1.clusters import MockCluster

from dmp_suite.maintenance.yt.table_diff import find_diff

from test_dmp_suite.testing_utils import NileJobTestCase


class TestTableDiff(NileJobTestCase):
    def test_diff_without_params(self):
        job = MockCluster().job()
        job.run = mock.Mock()
        with mock.patch('dmp_suite.maintenance.yt.table_diff.cu.get_job', return_value=job):
            find_diff('//dummy', '//dummy', '//dummy', keys=('id',))
            self.assertCorrectLocalRun(
                job,
                sources={
                    "table1": "table_diff/table1_in.json",
                    "table2": "table_diff/table2_in.json",
                },
                expected_sinks={
                    "diff_out": "table_diff/diff_out.json",
                    "diff_stat_out": "table_diff/diff_stat_out.json",
                }
            )

    def test_diff_wit_two_keys(self):
        job = MockCluster().job()
        job.run = mock.Mock()
        with mock.patch('dmp_suite.maintenance.yt.table_diff.cu.get_job', return_value=job):
            find_diff('//dummy', '//dummy', '//dummy', keys=('id', 'id2'))
            self.assertCorrectLocalRun(
                job,
                sources={
                    "table1": "table_diff_with_two_keys/table1_in.json",
                    "table2": "table_diff_with_two_keys/table2_in.json",
                },
                expected_sinks={
                    "diff_out": "table_diff_with_two_keys/diff_out.json",
                    "diff_stat_out": "table_diff_with_two_keys/diff_stat_out.json",
                }
            )
