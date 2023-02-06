from nile.api.v1.clusters import MockCluster

from test_dmp_suite.testing_utils import NileJobTestCase, JsonFileFormat
from demand_etl.layer.yt.cdm.ab_experiment.agg_experiment_v3_revision.impl import (
    get_utc_revision_start_dttm,
    get_utc_revision_end_dttm,
    get_business_min_version_id,
)


class TransformationTest(NileJobTestCase):
    file_format = JsonFileFormat()

    def test_transformation_get_utc_revision_start_dttm(self):
        job = MockCluster().job()
        job.table("dummy").label("input").call(get_utc_revision_start_dttm).label("result")
        self.assertCorrectLocalRun(
            job,
            sources={"input": "before_get_utc_revision_start_dttm.json"},
            expected_sinks={"result": "after_get_utc_revision_start_dttm.json"},
        )

    def test_transformation_get_utc_revision_end_dttm(self):
        job = MockCluster().job()
        job.table("dummy").label("input").call(get_utc_revision_end_dttm).label("result")
        self.assertCorrectLocalRun(
            job,
            sources={"input": "after_get_utc_revision_start_dttm.json"},
            expected_sinks={"result": "after_get_utc_revision_end_dttm.json"},
        )

    def test_transformation_get_business_min_version_id(self):
        job = MockCluster().job()
        job.table("dummy").label("input").call(get_business_min_version_id).label("result")
        self.assertCorrectLocalRun(
            job,
            sources={"input": "after_get_utc_revision_end_dttm.json"},
            expected_sinks={"result": "after_get_business_min_version_id.json"}
        )
