from nile.api.v1.clusters import MockCluster
from dmp_suite.datetime_utils import Period
from test_dmp_suite.testing_utils import NileJobTestCase, JsonFileFormat
from taxi_etl.layer.yt.cdm.crm.driver_satisfaction.fct_driver_satisfaction_pythia.impl import (
    extract_pythia_fields,
    split_stream_start_answer,
    process_pythia_stream,
)


class TransformationTest(NileJobTestCase):
    file_format = JsonFileFormat()

    def test_extract_pythia_fields(self):
        survey_ids = {'id1', 'id2', 'id4'}
        job = MockCluster().job()
        job.table("dummy").label("input").call(extract_pythia_fields, survey_ids).label("result")
        self.assertCorrectLocalRun(
            job,
            sources={"input": "raw_pythia.json"},
            expected_sinks={"result": "extracted_pythia.json"},
        )

    def test_split_stream_start_answer(self):
        job = MockCluster().job()
        start, answer = job.table("dummy").label("input").call(split_stream_start_answer)
        start.label("start")
        answer.label("answer")
        self.assertCorrectLocalRun(
            job,
            sources={"input": "extracted_pythia.json"},
            expected_sinks={
                "start": "start_pythia.json",
                "answer": "answer_pythia.json",
            },
        )

    def test_process_pythia_stream(self):
        from dmp_suite.datetime_utils import format_datetime
        period = Period(format_datetime('2018-10-01'), format_datetime('2018-10-10'))
        job = MockCluster().job()
        job.table("dummy").label("input").call(process_pythia_stream, period).label("result")
        self.assertCorrectLocalRun(
            job,
            sources={"input": "extracted_pythia.json"},
            expected_sinks={"result": "joined_pythia.json"},
        )
