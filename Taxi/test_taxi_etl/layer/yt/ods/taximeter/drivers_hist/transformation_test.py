# coding: utf-8
from nile.api.v1.clusters import MockCluster
from test_dmp_suite.testing_utils import NileJobTestCase, JsonFileFormat
from taxi_etl.layer.yt.ods.taximeter.drivers_hist.impl import extract_fields_drivers


class TransformationTest(NileJobTestCase):
    file_format = JsonFileFormat()

    def test_transformation(self):
        job = MockCluster().job()
        job.table("dummy").label("input").call(extract_fields_drivers).label("result")
        self.assertCorrectLocalRun(
            job,
            sources={"input": "raw_drivers.json"},
            expected_sinks={"result": "ods_drivers_hist.json"},
        )
