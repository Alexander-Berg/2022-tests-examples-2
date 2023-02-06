import json

from taxi_etl.layer.yt.ods.clowny_quotas.quota.impl import extract_data
from dmp_suite.file_utils import from_same_directory


def test_extract_data():
    with open(from_same_directory(__file__, "data/raw_quotas.json")) as f:
        raw_data = json.load(f)

    actual = []
    for row in extract_data(raw_data):
        row['utc_business_dttm'] = '2020-01-01'
        actual.append(row)

    with open(from_same_directory(__file__, "data/result.json")) as f:
        expected = json.load(f)

    assert actual == expected
