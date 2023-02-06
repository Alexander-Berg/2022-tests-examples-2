from nile.api.v1.clusters import MockCluster
from test_dmp_suite.testing_utils import NileJobTestCase, JsonFileFormat
from taxi_etl.layer.yt.ods.taxi_crm.driver_satisfaction.impl import extract_fields

class TransformationTest(NileJobTestCase):
    file_format = JsonFileFormat()

    def test_transformation(self):
        job = MockCluster().job()
        job.table("dummy").label("input").call(extract_fields).label("result")
        self.assertCorrectLocalRun(
            job,
            sources={"input": "raw_driver_satisfaction.json"},
            expected_sinks={"result": "ods_driver_satisfaction.json"},
        )
