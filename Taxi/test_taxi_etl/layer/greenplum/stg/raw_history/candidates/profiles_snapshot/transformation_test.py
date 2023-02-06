from nile.api.v1.clusters import MockCluster
from test_dmp_suite.testing_utils import NileJobTestCase, JsonFileFormat
from taxi_etl.layer.greenplum.stg.raw_history.candidates.profiles_snapshot.impl \
    import stream_transformation


class TransformationTest(NileJobTestCase):
    file_format = JsonFileFormat()

    def test_transformation(self):
        job = MockCluster().job()
        job.table("dummy").label("input").call(stream_transformation).label("result")
        self.assertCorrectLocalRun(
            job,
            sources={"input": "raw_data.json"},
            expected_sinks={"result": "transformed_data.json"},
        )
