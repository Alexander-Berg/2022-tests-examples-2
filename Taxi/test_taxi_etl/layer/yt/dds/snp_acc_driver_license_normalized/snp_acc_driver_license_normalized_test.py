# coding: utf-8
from mock import MagicMock, patch
from nile.api.v1 import MockCluster

from dmp_suite import datetime_utils as dtu
from dmp_suite.yt import YTMeta
from taxi_etl.layer.yt.dds import SnpAccDriverLicenseNormalized
from taxi_etl.layer.yt.dds.snp_acc_driver_license_normalized import loader
from test_dmp_suite.testing_utils import NileJobTestCase, JsonFileFormat


class TestSnpDriverLicenseNormalized(NileJobTestCase):
    file_format = JsonFileFormat()

    @classmethod
    def setUp(cls):
        cls.init_job = MockCluster().job()

    @patch("dmp_suite.nile.cluster_utils.range_path", MagicMock(return_value="//dummy"))
    def test_flow_with_merge(self):
        loader.prepare_transformation_flow(self.init_job, dtu.Period("2019-07-01", "2019-07-02"),
                                                YTMeta(SnpAccDriverLicenseNormalized), need_merge=True)
        self.assertCorrectLocalRun(
            self.init_job,
            sources={
                "order_stream": "dummy_order.json",
                "order_uber_stream": "dummy_uber_order.json",
                "target_to_merge": "dummy_target_to_merge.json"
            },
            expected_sinks={
                "result": "snp_acc_driver_license_normalized_result_merged.json",
            }
        )

    @patch("dmp_suite.nile.cluster_utils.range_path", MagicMock(return_value="//dummy"))
    def test_flow_without_merge(self):
        loader.prepare_transformation_flow(self.init_job, dtu.Period("2019-07-01", "2019-07-02"),
                                                YTMeta(SnpAccDriverLicenseNormalized), need_merge=False)
        self.assertCorrectLocalRun(
            self.init_job,
            sources={
                "order_stream": "dummy_order.json",
                "order_uber_stream": "dummy_uber_order.json"
            },
            expected_sinks={
                "result": "snp_acc_driver_license_normalized_result_yql.json",
            }
        )
