import json
from pytest import mark
from nile.api.v1.clusters import MockCluster

from dmp_suite.file_utils import from_same_directory
from test_dmp_suite.testing_utils import NileJobTestCase, JsonFileFormat
from demand_etl.layer.yt.ods.experiments.experiment_v3_version.impl import \
    extract_fields, get_team_group_flg, get_one_mod_sha_flg, get_group_div_argument_name


@mark.parametrize(
    "func, raw_json, ods_json", (
        (get_team_group_flg, "data/raw_team_group_flg.json", "data/ods_team_group_flg.json"),
        (get_one_mod_sha_flg, "data/raw_one_mod_sha_flg.json", "data/ods_one_mod_sha_flg.json"),
        (get_group_div_argument_name, "data/raw_group_div_argument_name.json",
         "data/ods_group_div_argument_name.json"),
    ))
def test_extractor_funcs(func, raw_json, ods_json):
    with open(from_same_directory(__file__, raw_json)) as raw,\
            open(from_same_directory(__file__, ods_json)) as ods:
        actual = [func(element) for element in json.load(raw)]
        expected = json.load(ods)
        assert actual == expected


class TransformationTest(NileJobTestCase):
    file_format = JsonFileFormat()

    def test_transformation(self):
        job = MockCluster().job()
        job.table("dummy").label("input").call(extract_fields).label("result")
        self.assertCorrectLocalRun(
            job,
            sources={"input": "raw_experiment.json"},
            expected_sinks={"result": "ods_experiment.json"},
        )
