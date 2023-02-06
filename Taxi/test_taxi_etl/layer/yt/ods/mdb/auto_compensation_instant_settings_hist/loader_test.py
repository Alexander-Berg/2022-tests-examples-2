# coding: utf-8
from nile.api.v1.clusters import MockCluster

from test_dmp_suite.testing_utils import NileJobTestCase
from taxi_etl.layer.yt.ods.mdb.auto_compensation_instant_settings_hist.loader import get_records


class TestOdsAutoCompensationInstantSettingsHist(NileJobTestCase):
    def setUp(self):
        self.job = MockCluster().job()
        get_records(self.job)

    def test_filter(self):
        self.assertCorrectLocalRun(
            self.job,
            sources={
                "raw_mdb_config": "raw_mdb_config.json",
            },
            expected_sinks={
                "raw_filtered_mdb_config": "raw_filtered_mdb_config.json",
            }
        )

    def test_transform_data(self):
        self.assertCorrectLocalRun(
            self.job,
            sources={
                 "raw_filtered_mdb_config": "raw_filtered_mdb_config.json",
            },
            expected_sinks={
                "ods_transform_data": "ods_transform_data.json",
            }
        )
