import json
from nile.api.v1.clusters import MockCluster
from dmp_suite.data_transform import FlatMap
from dmp_suite.file_utils import from_same_directory
from test_dmp_suite.testing_utils import NileJobTestCase, JsonFileFormat
from taxi_etl.layer.yt.ods.dbprocessing.order_candidate.impl import extract_candidates, old_extract_candidates


RAW_JSON = "data/raw_order_proc.json"
ODS_JSON = "data/ods_order_candidate.json"
# note: мы знаем о существаовании отличия между релизациями по этому набору полей и
# исключаем их из тестирования новой трансформации (лучше бы из старой, но оттуда так просто не выковыришь)
EXCLUDED = (
    "utc_order_updated_dttm",
)


class TransformationTest(NileJobTestCase):
    file_format = JsonFileFormat()

    def test_old_transformation(self):
        job = MockCluster().job()
        job.table("dummy").label("input").call(old_extract_candidates).label("result")
        self.assertCorrectLocalRun(
            job,
            sources={"input": "raw_order_proc.json"},
            expected_sinks={"result": "ods_order_candidate.json"},
        )


def test_new_transformation():
    def delete_exceeding(some_list):
        return [{k: v for k, v in some_dict.items() if k not in EXCLUDED} for some_dict in some_list]

    flat_map = FlatMap(extract_candidates)
    with open(from_same_directory(__file__, RAW_JSON)) as raw,\
            open(from_same_directory(__file__, ODS_JSON)) as ods:
        raw_list = [entry["doc"] for entry in json.load(raw)]
        ods_list = json.load(ods)
        assert delete_exceeding(list(flat_map(raw_list))) == ods_list
