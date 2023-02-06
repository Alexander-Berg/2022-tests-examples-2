# coding: utf-8
from nile.api.v1.clusters import MockCluster
from test_dmp_suite.testing_utils import NileJobTestCase, JsonFileFormat
from taxi_etl.layer.yt.raw.taxi_crm.driver_satisfaction.loader import _get_data


START, END = '2019-09-25', '2019-10-05'


class TransformationTest(NileJobTestCase):
    file_format = JsonFileFormat()

    def test_transformation(self):
        job = MockCluster().job()
        job.table("dummy").label("input").call(_get_data, START, END).label("result")
        self.assertCorrectLocalRun(
            job,
            sources={"input": "source.json"},
            expected_sinks={"result": "raw.json"},
        )
