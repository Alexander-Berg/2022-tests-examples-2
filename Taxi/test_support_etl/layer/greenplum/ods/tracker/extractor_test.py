import json

from support_etl.layer.greenplum.ods.tracker.ticket_audkon_score.impl import (
    extract_data
)
from dmp_suite.file_utils import from_same_directory


def test_extract_data():
    with open(from_same_directory(__file__, "data/raw_audkon.json")) as f:
        raw_data = json.load(f)

    with open(from_same_directory(__file__, "data/result.json")) as f:
        expected = json.load(f)

    assert list(extract_data(raw_data)) == expected
