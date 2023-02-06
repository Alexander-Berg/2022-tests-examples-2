import json

from support_etl.layer.yt.ods.chatterbox_support_taxi.message_log.impl_streaming import mapper
from dmp_suite.file_utils import from_same_directory


def test_mapper():
    with open(from_same_directory(__file__, "data/raw.json")) as f:
        raw_data = json.load(f)

    actual = [row for row in mapper(raw_data)]

    with open(from_same_directory(__file__, "data/result.json")) as f:
        expected = json.load(f)

    assert actual == expected
