from nile.api.v1.clusters import MockCluster
from test_dmp_suite.testing_utils import NileJobTestCase, JsonFileFormat
from dmp_suite.apple_search_ads.ods.impl import calculate_result_stat


class TransformationTest(NileJobTestCase):
    file_format = JsonFileFormat()

    def test_transformation(self):
        job = MockCluster().job()
        raw_stat = job.table("dummy").label("statistics")
        raw_entity = job.table("dummy").label("entities")

        calculate_result_stat(raw_entity, raw_stat).label("result")

        self.assertCorrectLocalRun(
            job,
            sources={
                "statistics": "statistics.json",
                "entities": "entities.json"
            },
            expected_sinks={"result": "result.json"},
        )
