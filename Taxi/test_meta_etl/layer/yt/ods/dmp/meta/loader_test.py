import pytest
from nile.api.v1.clusters import MockCluster

from test_dmp_suite.testing_utils import NileJobTestCase

from meta_etl.layer.yt.ods.dmp.meta.loader import prepare_job


@pytest.mark.skip(reason='tmp')
class TestOdsDmpTableMeta(NileJobTestCase):
    def setUp(self):
        self.job = MockCluster().job()
        prepare_job(self.job)

    def test_mapping(self):
        self.assertCorrectLocalRun(
            self.job,
            sources={
                "raw_dmp_table_meta": "raw_dmp_table_meta.json",
            },
            expected_sinks={
                "yt_table_data": "yt_table_data.json",
                "gp_table_data": "gp_table_data.json",
                "yt_field_data": "yt_field_data.json",
                "gp_field_data": "gp_field_data.json",
            }
        )
